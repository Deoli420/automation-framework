# E2E Automation Framework

![E2E Tests](https://github.com/Deoli420/automation-framework/actions/workflows/automation.yml/badge.svg)

A production-grade, end-to-end automation framework built with Python, Selenium, and PyTest — **68 tests** across UI, API, and performance layers. Demonstrates SDET-level ownership of test architecture, API validation, performance testing, Docker, and CI/CD.

**Target**: Nykaa's public e-commerce site (read-only flows, ethical usage)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Test Layer (68 tests)                  │
│  tests/ui/     — 32 Selenium UI tests (Page Object Model)│
│  tests/api/    — 36 API validation tests (schema+timing) │
├─────────────────────────────────────────────────────────┤
│                   Page Objects                           │
│  HomePage · SearchResultsPage · ProductPage · CartPage  │
├─────────────────────────────────────────────────────────┤
│                  Service Layer                           │
│  ApiClient · SearchService · ProductService              │
│  SchemaValidator                                         │
├─────────────────────────────────────────────────────────┤
│                    Core Layer                            │
│  DriverFactory · BasePage · Config · Logger · Exceptions │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure                           │
│  Docker · GitHub Actions · Allure · JMeter · Cron        │
└─────────────────────────────────────────────────────────┘
```

### Design Decisions

| Decision | Why |
|----------|-----|
| **Page Object Model** | Separates locators from test logic. When DOM changes, fix one file, not every test. |
| **Driver Factory** | Abstracts browser creation. Same code runs local Chrome, headless CI, or Selenium Grid. |
| **Pydantic Settings** | Type-safe config with env-var override. `AUTO_` prefix avoids system var collision. |
| **Function-scoped driver** | Each test gets fresh browser = zero state leakage. Slower but bulletproof. |
| **Allure reporting** | Rich visual reports with screenshots, steps, and history trends. |
| **Retry decorator** | `@retry` on `BasePage.click()` and `find_element()` handles stale DOM references. |
| **Auth auto-skip** | `pytest_collection_modifyitems` hook skips `@auth_required` tests centrally. |
| **Standalone Chrome** | Simpler than Grid for 68 tests. Upgrade path: change one env var. |

---

## Quick Start

### Local (headed Chrome)

```bash
# 1. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy config
cp .env.example .env
# Edit .env: set AUTO_HEADLESS=false for visual debugging

# 4. Run all tests
pytest -v

# 5. Run only API tests (no browser needed)
pytest tests/api/ -m api -v

# 6. Run only smoke tests
pytest -m smoke -v
```

### Docker

```bash
# Run full suite in containers (Selenium Chrome + test runner)
docker compose -f docker/docker-compose.yml up --build --abort-on-container-exit

# Watch tests live: open http://localhost:7900 (password: "secret")

# Reports: reports/report.html
```

### CI (GitHub Actions)

Push to `main` or open a PR — tests run automatically.
Manual trigger: Actions tab > "E2E Automation Tests" > Run workflow.

---

## Project Structure

```
automation-framework/
├── core/                    # Framework foundation
│   ├── config.py            # Pydantic-settings config (AUTO_ prefix)
│   ├── driver_factory.py    # Chrome/Firefox/Remote factory
│   ├── base_page.py         # BasePage with waits, clicks, @retry, screenshots
│   ├── logger.py            # JSON/text structured logging
│   └── exceptions.py        # Categorized exceptions with tags
│
├── pages/                   # Page Object Model
│   ├── home_page.py         # Search bar interaction
│   ├── search_results_page.py  # Product grid, filters
│   ├── product_page.py      # PDP: title, price, add-to-bag
│   └── cart_page.py         # Cart: items, pricing, remove
│
├── services/                # API abstraction layer
│   ├── api_client.py        # HTTP client with timing + retry
│   ├── search_service.py    # Search API wrapper
│   ├── product_service.py   # Product API wrapper
│   └── schema_validator.py  # JSON schema validation
│
├── tests/                   # Test cases
│   ├── ui/                  # Selenium tests (32 tests)
│   │   ├── test_search.py
│   │   ├── test_filters.py
│   │   ├── test_product_page.py
│   │   ├── test_cart.py          # @auth_required (auto-skipped)
│   │   ├── test_cart_pricing.py  # @auth_required (auto-skipped)
│   │   ├── test_cross_layer.py   # UI vs API price validation
│   │   ├── test_homepage.py
│   │   └── test_negative.py
│   └── api/                 # API validation tests (36 tests)
│       ├── test_search_api.py
│       ├── test_product_api.py
│       └── test_price_consistency.py
│
├── performance/             # JMeter load tests
│   ├── test_plans/          # .jmx files (≤5 users)
│   ├── run_jmeter.sh
│   └── generate_report.sh
│
├── utils/                   # Helpers
│   ├── waits.py             # Custom expected conditions
│   ├── data_generator.py    # Test data loading
│   ├── screenshot.py        # Screenshot capture
│   └── retry.py             # @retry decorator for flaky interactions
│
├── config/                  # Environment configs
│   ├── local.env
│   ├── ci.env
│   └── staging.env
│
├── fixtures/                # Static test data
│   ├── search_terms.json
│   └── expected_schemas/    # JSON Schema Draft-07
│
├── docker/                  # Containerization
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .github/workflows/
│   └── automation.yml       # 3-job CI pipeline
│
├── conftest.py              # Root fixtures + auth auto-skip hook
├── pytest.ini               # Test configuration
├── ARCHITECTURE.md          # Deep-dive design decisions
└── requirements.txt         # Python dependencies
```

---

## Test Coverage

### UI Tests (32 test cases)
- **Search** (7): Query execution, result rendering, random term validation, empty search, special chars
- **Filters** (4): Filter section presence, filter application, sort interaction
- **Product Page** (5): Title, price, image, add-to-bag button, product ID extraction
- **Cart** (4): Add item, view prices, remove item, empty cart *(auth_required — auto-skipped)*
- **Cart Pricing** (2): Cart total vs item sum, PDP price vs cart price *(auth_required — auto-skipped)*
- **Cross-Layer** (1): UI DOM price vs inventory API price comparison
- **Homepage** (4): Navigation, search bar, category links, page load
- **Negative** (5): Invalid URLs, non-existent products, boundary inputs

### API Tests (36 test cases)
- **Search API** (16): HTTP 200, response time, schema validation, special characters, empty query, pagination, boundary values, trending searches
- **Product API** (12): Inventory endpoint, response time, timeout handling, invalid IDs, schema validation
- **Price Consistency** (8): Price field presence, JSON validity, response time benchmarks, cross-endpoint comparison

### Performance Tests (JMeter)
- **Search suggestions** (`/gludo/searchSuggestions`): 5 users, 30s ramp, 60s duration
- **Product inventory** (`/gateway-api/inventory/data/json/`): 5 users, 30s ramp, 60s duration
- Metrics: avg response time, 95th percentile, error %, throughput

---

## API Endpoint Discovery

How the working Nykaa API endpoints were found:

| Endpoint | How Discovered | Status |
|----------|---------------|--------|
| `/gludo/searchSuggestions?q=...` | Chrome DevTools → Network tab → type in search bar → XHR fires | ✅ Working |
| `/gateway-api/inventory/data/json/?productId=...` | Navigate to PDP → Network tab → stock check XHR | ✅ Working |
| `/search/trending` | Network tab filtered for XHR during homepage load | ✅ Working |
| `/gateway-api/search/products` | Referenced in old docs | ❌ 404 Dead |
| `/gateway-api/products/{id}` | Referenced in old docs | ❌ 404 Dead |

**Key insight**: Nykaa moved product data to SSR via `window.__PRELOADED_STATE__` (Redux store embedded in HTML). The old REST endpoints return 404.

---

## Selector Strategy

Nykaa uses CSS-in-JS (styled-components/Emotion) — class names like `css-1d0jf8e` change every deploy. Our selector hierarchy:

| Priority | Strategy | Example | When |
|----------|----------|---------|------|
| 1 | Name/attribute | `input[name="search-suggestions-nykaa"]` | Form elements |
| 2 | Semantic stable class | `.productWrapper`, `.filters` | Layout containers |
| 3 | Tag uniqueness | `h1` (only one on PDP) | Headings |
| 4 | XPath text match | `//button[contains(text(),'Add to Bag')]` | Buttons |
| 5 | Pattern match | `[class*='price']` | Last resort |

**Why NOT `data-testid`?** Nykaa is a third-party site — we cannot add test attributes to their DOM.

---

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| **Cart requires authentication** | 6 tests auto-skipped | `@pytest.mark.auth_required` + conftest hook |
| **WAF 403 blocks** | Some API tests skip on Akamai CDN block | Graceful `pytest.skip("WAF blocked")` |
| **Single-word search redirects** | "lipstick" → `/lipstick/c/8` (category page) | Use multi-word queries: "maybelline foundation" |
| **CSS-in-JS hashed classes** | Selectors like `css-1d0jf8e` break on redeploy | Use semantic classes and attribute selectors |

---

## Scaling Path

### Phase 1 (Current): Standalone Chrome — 67 Tests
- Single `selenium/standalone-chrome` container
- pytest-xdist for parallel API test execution
- Allure reporting with Allure Report Action
- JMeter caching in CI (83MB saved per run)

### Phase 2: Selenium Grid
```yaml
# Replace standalone-chrome with:
selenium-hub:
  image: selenium/hub:4.27
chrome-node-1:
  image: selenium/node-chrome:131.0
chrome-node-2:
  image: selenium/node-chrome:131.0
```
Zero code changes. Set `AUTO_SELENIUM_REMOTE_URL=http://selenium-hub:4444/wd/hub`.

### Phase 3: Multi-Browser
DriverFactory already supports Chrome + Firefox. CI matrix:
```yaml
strategy:
  matrix:
    browser: [chrome, firefox]
env:
  AUTO_BROWSER: ${{ matrix.browser }}
```

### Phase 4: Contract Testing
Add Schemathesis or Pact tests in `tests/contract/`. Baseline schemas already exist in `fixtures/expected_schemas/`.

### Phase 5: Kubernetes
Selenium Helm chart + test runner as CronJob + reports to S3.

---

## Deployment (DigitalOcean)

### Nightly Regression
```bash
# Add cron (2:30 AM IST = 9:00 PM UTC)
crontab -e
0 21 * * * /home/deploy/automation-framework/scripts/run-nightly.sh >> /home/deploy/automation-framework/nightly.log 2>&1
```

### Report Hosting
Reports are served via nginx at `reports.adityadeoli.com` with basic auth.

---

## Interview Explanation

### 2-Minute Architecture Pitch

> "I built an end-to-end automation framework with three layers: UI tests using Selenium with Page Object Model, API validation using requests with JSON schema checking, and performance testing using JMeter — 68 tests total.
>
> At the core is a DriverFactory that abstracts browser creation — it supports local Chrome, headless mode, and remote Selenium Grid through a single environment variable. All page interactions go through a BasePage class with explicit waits, a @retry decorator for stale DOM references, structured logging, and automatic screenshot capture on failure.
>
> The API layer independently validates the same data the UI shows. A cross-layer test navigates to a product page, extracts the price from the DOM, queries the inventory API for the same product ID, and asserts they match. This catches stale caches, CDN issues, and SSR hydration mismatches that pure UI testing misses.
>
> Configuration uses pydantic-settings with an `AUTO_` prefix to avoid system var collisions. The whole thing runs in Docker — one container for Selenium Chrome, one for the test runner. GitHub Actions runs a 3-job pipeline: API tests (fast), UI tests with Selenium sidecar, and JMeter performance tests with caching."

### Tradeoffs

| Decision | Tradeoff | Why |
|----------|----------|-----|
| Standalone Chrome over Grid | No multi-node parallelism | Simpler for 68 tests; upgrade is one env var |
| Allure over pytest-html only | Needs report generation step | Rich history, screenshots, steps, trends |
| Function-scoped driver | Slower (restart per test) | Test isolation; no state leakage |
| Sync requests over httpx | No async | pytest tests are sync; no benefit |
| @retry on BasePage methods | Extra complexity | Handles stale element references transparently |

---

## Ethical Design

- Realistic Chrome User-Agent for JMeter to avoid bot detection while being transparent
- JMeter load capped at 5 users with 2-3 second think times
- No login, payment, or account creation flows
- No aggressive crawling or data scraping
- Designed as a read-only validation framework

---

## License

MIT
