# Architecture Deep Dive

Everything you'd know if you built this framework from scratch — the "why" behind every decision, the dead ends explored, and the real-world constraints that shaped the design.

---

## 1. How Nykaa's API Endpoints Were Discovered

### The Problem
Nykaa doesn't publish a public API. The old endpoints referenced in community docs (`/gateway-api/search/products`, `/gateway-api/products/{id}`) return 404. Building an API test layer meant reverse-engineering working endpoints from the browser.

### The Process

**Search endpoint** — Open Chrome DevTools → Network tab → XHR filter → type "lipstick" in search bar → watch XHR fire to `/gludo/searchSuggestions?q=lipstick`. This is Nykaa's autocomplete service (Gludo is their search provider). The response contains a `products` array with `id`, `title`, `imageUrl`, and `price` fields.

**Inventory endpoint** — Navigate to any product page (PDP) → watch Network tab → see XHR to `/gateway-api/inventory/data/json/?productId=24700514`. This checks real-time stock and pricing. The response has `inventory_details` keyed by SKU ID with `quantity`, `price`, and availability flags.

**Trending searches** — Filter Network tab for XHR during homepage load → see `/search/trending` request that returns popular search terms. This fires automatically without user interaction.

### Dead Endpoints (and Why)
- `/gateway-api/search/products` → returns `{"error": "no Route matched"}` (404)
- `/gateway-api/products/{id}` → same 404 error

**Root cause**: Nykaa moved to server-side rendering (SSR). Product data is embedded in the HTML as `window.__PRELOADED_STATE__` — a Redux store serialized into a `<script>` tag. The browser doesn't need to fetch product data via XHR because it's already in the page HTML. Only dynamic data (inventory/stock) still uses API calls.

### What This Teaches
When a website's REST endpoints 404, don't assume there's no API — check if they moved to SSR. The Network tab reveals what XHR calls the frontend *actually* makes vs. what's documented. Always verify endpoints against live traffic.

---

## 2. How UI Selectors Were Chosen

### The Problem
Nykaa uses CSS-in-JS (styled-components or Emotion). Every class name looks like `css-1d0jf8e` — a hash generated at build time that **changes on every deploy**. Traditional CSS selector strategies break immediately.

### Selector Hierarchy (Most Stable → Least Stable)

**Priority 1: Name/attribute selectors**
```python
# Search input — has a stable `name` attribute
SEARCH_INPUT = (By.CSS_SELECTOR, 'input[name="search-suggestions-nykaa"]')
```
Form elements often have `name` attributes for server-side processing. These rarely change because backend code depends on them.

**Priority 2: Semantic stable classes**
```python
# Product grid wrapper — ".productWrapper" is a developer-given class
PRODUCT_CARD = (By.CSS_SELECTOR, ".product-listing .productWrapper")
```
Not all classes are hashed. Layout containers often have human-readable class names like `.productWrapper`, `.filters`, `.breadcrumb` alongside the generated ones.

**Priority 3: Tag uniqueness**
```python
# Product title — h1 (only one h1 on any PDP)
PRODUCT_TITLE = (By.CSS_SELECTOR, "h1")
```
Semantic HTML tags can be reliable selectors when the page has a single instance. Nykaa has one `h1` per product page — that won't change without breaking accessibility.

**Priority 4: XPath text match**
```python
# Add to Bag button — matched by visible text, case-insensitive
ADD_TO_BAG = (By.XPATH,
    "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
    "'abcdefghijklmnopqrstuvwxyz'),'add to bag')]")
```
When no stable attribute exists, match by visible text. The `translate()` function handles case variations ("Add to Bag" vs "ADD TO BAG"). Text-based selectors survive CSS class changes.

**Priority 5: Pattern match (last resort)**
```python
# Price element — at least the word "price" appears in class names
SELLING_PRICE = (By.CSS_SELECTOR, "[class*='price'] span:nth-child(2)")
```
`[class*='price']` matches any element whose class contains the substring "price". This is fragile but better than `css-1d0jf8e`. Combined with structural selectors (`span:nth-child(2)`), it provides reasonable stability.

### Why NOT `data-testid`?
In-house teams add `data-testid="add-to-cart"` attributes specifically for test automation. But Nykaa is a third-party website — we can't modify their DOM. Our framework must work with whatever selectors the production site provides.

---

## 3. Why Certain Tests Are Skipped

### Cart Tests (6 tests) — `@pytest.mark.auth_required`
Nykaa's `/checkout/cart` endpoint requires an authenticated session. Guest users get redirected to the login page. The 6 cart tests (4 in `test_cart.py`, 2 in `test_cart_pricing.py`) exist to demonstrate:
- Add-to-cart flow testing patterns
- Price consistency validation (cart total = sum of item prices)
- PDP price vs. cart price comparison

They're auto-skipped by a `pytest_collection_modifyitems` hook in `conftest.py`. To activate: provide auth cookies/credentials and remove the hook.

### WAF 403 Blocks (variable tests)
Nykaa uses Akamai CDN with Web Application Firewall rules. Some API requests get blocked with HTTP 403 despite using a realistic Chrome User-Agent. The framework handles this gracefully:
```python
if response.status_code == 403:
    pytest.skip("WAF blocked API request")
```
This keeps the test suite green while acknowledging a real limitation. The tests validate framework behavior, not just server responses.

### Single-Word Search Redirects
Searching for "lipstick" (single word) triggers a redirect to the category page `/lipstick/c/8` — a completely different DOM layout than search results. Multi-word queries like "maybelline foundation" stay on the search results page. Tests use multi-word queries to avoid this redirect.

---

## 4. Page Object Model: Why This Pattern

### What It Solves
Without POM, every test file imports Selenium directly and has hardcoded selectors:
```python
# ❌ Bad: Selector duplicated across 15 test files
driver.find_element(By.CSS_SELECTOR, "h1").text
```

With POM, selectors live in one file:
```python
# ✅ Good: Selector defined once in product_page.py
class ProductPage(BasePage):
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h1")

    def get_product_title(self) -> str:
        return self.get_text(self.PRODUCT_TITLE)
```

When Nykaa changes their DOM, fix one page object — not every test.

### BasePage Provides the Safety Net

Every page object inherits from `BasePage`, which wraps raw Selenium calls with:
- **Explicit waits**: No `time.sleep()` anywhere. Every element interaction waits for the element to be ready.
- **`@retry` decorator**: `click()` and `find_element()` retry 3 times on `StaleElementReferenceException` with 0.5s delay.
- **`dismiss_popups()`**: Nykaa shows a login modal on first visit. Three strategies (Escape key → overlay click → close button) handle it without failing.
- **`parse_price()`**: Extracts numeric value from "Rs. 1,299" or "₹1299" — shared across all pages.
- **Structured logging**: Every click and type is logged with the locator for debugging CI failures.

### Why Function-Scoped Driver?
```python
@pytest.fixture(scope="function")
def driver():
    _driver = DriverFactory.create_driver()
    yield _driver
    _driver.quit()
```

Each test gets a **fresh browser** session. This is slower (browser restart per test) but provides bulletproof isolation:
- Cart state from test A can't leak into test B
- Cookies and localStorage are clean
- No test ordering dependencies

The alternative — `session`-scoped driver shared across tests — is faster but creates hidden dependencies. A test that only passes because a previous test logged in is a ticking time bomb.

---

## 5. Config System: Pydantic-Settings with AUTO_ Prefix

### The `AUTO_` Prefix
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTO_",
        extra="ignore",
    )

    BROWSER: str = "chrome"
    HEADLESS: bool = True
    BASE_URL: str = "https://www.nykaa.com"
    SELENIUM_REMOTE_URL: str = ""
```

The `AUTO_` prefix prevents collision with system environment variables. Without it:
- `BROWSER` collides with the system's default browser setting
- `HEADLESS` could clash with display server variables
- `BASE_URL` is generic enough to conflict with other apps

With `AUTO_` prefix, you set `AUTO_BROWSER=firefox` — no ambiguity.

### Three Environment Files
- `config/local.env` — `AUTO_HEADLESS=false`, `AUTO_SELENIUM_REMOTE_URL=""` (local Chrome)
- `config/ci.env` — `AUTO_HEADLESS=true`, `AUTO_SELENIUM_REMOTE_URL=http://localhost:4444/wd/hub`
- `config/staging.env` — Same as CI but `AUTO_BASE_URL` can point to a staging server

Same test code runs everywhere. Only env vars change.

### `extra="ignore"`
Typos in env vars (like `AUTO_BROWSR=firefox`) are silently ignored instead of crashing. This prevents CI failures from mistyped environment variables — the setting just falls back to its default.

---

## 6. How Docker and CI Connect

### The Runtime Matrix

| Environment | Selenium | Config | How Driver Connects |
|-------------|----------|--------|-------------------|
| **Local** | Local Chrome binary | `local.env` | `webdriver.Chrome()` — direct |
| **Docker Compose** | `selenium-chrome` container | `ci.env` | `webdriver.Remote(url)` |
| **GitHub Actions** | `selenium/standalone-chrome` service container | CI env vars | `webdriver.Remote(url)` via Selenium Grid |

### The Single Integration Point
```python
class DriverFactory:
    @staticmethod
    def create_driver():
        if settings.SELENIUM_REMOTE_URL:
            return DriverFactory._create_remote_driver()
        return DriverFactory._create_local_driver()
```

Switching from local to Docker to CI to Grid is **one environment variable**: `AUTO_SELENIUM_REMOTE_URL`. When empty → local Chrome. When set → Remote WebDriver connecting to Selenium Grid.

### Selenium Grid in CI — Parallel Test Execution

Both UI CI jobs use `selenium/standalone-chrome` as a GitHub Actions service container. The container runs alongside the runner, exposing Selenium Grid on `localhost:4444`. Key configuration:

- **`SE_NODE_MAX_SESSIONS=3`** — Allows 3 concurrent Chrome sessions in one container
- **`--shm-size=2g`** — Chrome needs shared memory; Docker's default 64MB causes tab crashes
- **Health check** with 30s start period — Container needs time to download ChromeDriver on first boot
- **`pytest-xdist -n 3`** — Distributes tests across 3 workers, each connecting to the Grid via `webdriver.Remote()`

Each xdist worker is a separate process with its own function-scoped `driver` fixture. Worker 1 runs test A, Worker 2 runs test B, Worker 3 runs test C — all simultaneously, each with its own Chrome session in the Selenium Grid container.

### Why Selenium Grid (Not Local Chrome)

The previous approach installed Chrome directly on the runner with `browser-actions/setup-chrome@v1`. This worked but only supported **serial execution** — one Chrome instance at a time. With Nykaa page loads taking ~70s from Azure runners (US → India), serial execution meant:
- Smoke (8 tests): ~9 min of pure navigation
- Regression (26 tests): ~30 min, exceeding CI timeouts

Selenium Grid enables **parallel execution** — 3 tests running simultaneously reduces wall-clock time by ~3×. The `selenium/standalone-chrome` image bundles Chrome + ChromeDriver + Grid in one container, so there's no multi-container orchestration overhead.

### 4-Job Pipeline

1. **API Validation** (fast, ~20s) — No browser. `pytest tests/api/ -n 2` with parallel xdist workers.
2. **UI Smoke** (~5 min, every push/PR) — 8 core tests via Selenium Grid with 3 workers. Deploys Allure report to GitHub Pages.
3. **UI Regression** (~18 min, nightly + manual) — All 26 non-auth tests via Selenium Grid with 3 workers. Runs on schedule or `workflow_dispatch` with `test_suite=all|regression|ui`.
4. **Performance / JMeter** (~1 min, manual + nightly) — Search load test with JMeter caching (83MB saved per run).

All 4 jobs run in parallel. Fast API feedback in 20 seconds; full UI smoke in 5 minutes; complete regression + performance in ~18 minutes.

### Smoke vs Regression Split

Tests are categorized with pytest markers:

- **`@pytest.mark.smoke`** (8 tests) — Core user flows: homepage loads, search works, product page renders, XSS/404 handling. Fast feedback on every push.
- **`@pytest.mark.regression`** (remaining tests) — Parametrized searches, all filter tests, cross-layer price validation, edge cases. Full coverage on nightly schedule.
- **`@pytest.mark.auth_required`** (6 tests) — Cart tests, auto-skipped (no login fixture available).

The `ui-smoke` job runs `-m "smoke and not auth_required"`. The `ui-regression` job runs `-m "not auth_required"` (all tests including smoke).

---

## 7. What an SDET Learns Building This

### CDN WAFs Break Direct API Testing
Nykaa's Akamai CDN blocks some automated API requests with 403. Lesson: design tests to **validate framework behavior**, not just server responses. A test that gracefully skips on WAF 403 is more valuable than one that fails and blocks the pipeline.

### CSS-in-JS Makes Selectors Fragile
Hashed class names (`css-1d0jf8e`) change every build. Always prefer semantic classes over generated ones. When no stable selector exists, use text-based XPath matching — visible text changes less often than CSS classes.

### Test Isolation Is Non-Negotiable
Function-scoped browsers prevent cascading failures. When test B depends on test A's session state, a failure in A causes a cascade of false failures. The 2-3 second restart overhead per test is worth the debugging time saved.

### Config Management Compounds
The `AUTO_` prefix pattern scales to 50+ settings without collision. Starting with proper config management from day one avoids the "works on my machine" problem when you add CI, Docker, and staging environments.

### Docker Makes Tests Portable
Same Chrome version, same Python version, same dependencies everywhere. "Tests pass locally but fail in CI" is almost always an environment mismatch. Docker eliminates that class of bugs entirely.

### CI Job Separation Matters
Fast API tests (2 min) shouldn't wait for slow UI tests (15 min). Running them as separate jobs gives fast feedback on API regressions while UI tests are still running.

### Cross-Layer Testing Is the Highest-Value Test
The `test_cross_layer.py` test navigates to a PDP, reads the UI price, queries the inventory API, and compares. This single test catches:
- Cache staleness (CDN serves old page, API has new price)
- SSR hydration mismatch (server-rendered price differs from client)
- Price propagation delays between microservices
- Frontend rounding errors

It bridges two independent data sources and proves they agree — something neither UI-only nor API-only tests can verify.

### Centralized Skip Logic > Per-Test Decorators
Instead of adding `@pytest.mark.skip(reason=...)` to every cart test (6 places), a single `pytest_collection_modifyitems` hook auto-skips anything with `@pytest.mark.auth_required`. DRY principle applies to test infrastructure, not just production code.

---

## File Map

| File | Purpose | Key Decision |
|------|---------|-------------|
| `core/config.py` | Pydantic Settings | `AUTO_` prefix, `extra="ignore"` |
| `core/driver_factory.py` | Browser creation | Remote vs. local via single env var |
| `core/base_page.py` | Foundation page object | `@retry`, explicit waits, popup dismissal |
| `pages/*.py` | Page objects | Selectors verified against live DOM |
| `services/api_client.py` | HTTP client | Response timing, structured logging |
| `services/search_service.py` | Search wrapper | `/gludo/searchSuggestions` (discovered) |
| `services/product_service.py` | Product wrapper | `/gateway-api/inventory/data/json/` |
| `utils/retry.py` | Retry decorator | 3 attempts, 0.5s delay, StaleElement |
| `conftest.py` | Root fixtures | auth_required auto-skip hook |
| `fixtures/expected_schemas/` | JSON Schema Draft-07 | Required fields + nested validation |
| `.github/workflows/automation.yml` | CI pipeline | 4 jobs, Selenium Grid parallel, Allure to GitHub Pages |
