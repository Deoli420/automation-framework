# E2E Automation Framework

![E2E Tests](https://github.com/adityadeoli/automation-framework/actions/workflows/automation.yml/badge.svg)

A production-grade, end-to-end automation framework built with Python, Selenium, and PyTest. Demonstrates SDET-level ownership of test architecture, API validation, performance testing, Docker, and CI/CD.

**Target**: Nykaa's public e-commerce site (read-only flows, ethical usage)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Test Layer                            │
│  tests/ui/     — Selenium UI tests (Page Object Model)  │
│  tests/api/    — API validation tests (schema + timing) │
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
│  Docker · GitHub Actions · JMeter · Nginx · Cron         │
└─────────────────────────────────────────────────────────┘
```

### Design Decisions

| Decision | Why |
|----------|-----|
| **Page Object Model** | Separates locators from test logic. When DOM changes, fix one file, not every test. |
| **Driver Factory** | Abstracts browser creation. Same code runs local Chrome, headless CI, or Selenium Grid. |
| **Pydantic Settings** | Type-safe config with env-var override. `AUTO_` prefix avoids collision. |
| **Function-scoped driver** | Each test gets fresh browser = zero state leakage. Slower but bulletproof. |
| **Sync `requests`** | PyTest is sync. Using `httpx` async adds complexity for zero gain here. |
| **JSON structured logs** | Machine-parseable in CI. Human-readable in local via `AUTO_LOG_FORMAT=text`. |
| **pytest-rerunfailures** | Retries flaky tests 2x before marking failed. Reduces noise. |
| **Standalone Chrome** | Simpler than Grid for 15 tests. Upgrade path: change one env var. |

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
│   ├── base_page.py         # BasePage with waits, clicks, screenshots
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
│   ├── ui/                  # Selenium tests
│   │   ├── test_search.py
│   │   ├── test_filters.py
│   │   ├── test_product_page.py
│   │   ├── test_cart.py
│   │   └── test_cart_pricing.py
│   └── api/                 # API validation tests
│       ├── test_search_api.py
│       ├── test_product_api.py
│       └── test_price_consistency.py
│
├── performance/             # JMeter load tests
│   ├── test_plans/          # .jmx files (<=10 users)
│   ├── run_jmeter.sh
│   └── generate_report.sh
│
├── utils/                   # Helpers
│   ├── waits.py             # Custom expected conditions
│   ├── data_generator.py    # Test data loading
│   └── screenshot.py        # Screenshot capture
│
├── config/                  # Environment configs
│   ├── local.env
│   ├── ci.env
│   └── staging.env
│
├── fixtures/                # Static test data
│   ├── search_terms.json
│   └── expected_schemas/
│
├── docker/                  # Containerization
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/
│   └── run-nightly.sh       # Cron nightly runner
│
├── .github/workflows/
│   └── automation.yml       # CI pipeline
│
├── conftest.py              # Root fixtures
├── pytest.ini               # Test configuration
└── requirements.txt         # Python dependencies
```

---

## Test Coverage

### UI Tests (15 test cases)
- **Search**: Query execution, result rendering, random term validation
- **Filters**: Filter section presence, filter application
- **Product Page**: Title, price, image, add-to-bag button
- **Cart**: Add item, view prices, remove item, empty cart
- **Pricing**: Cart total vs item sum, PDP price vs cart price

### API Tests (9 test cases)
- **Search API**: HTTP 200, response time, result structure, special characters, empty query
- **Product API**: Endpoint response, response time, timeout handling
- **Price Consistency**: Price field presence, JSON validity, response time logging

### Performance Tests (JMeter)
- Search endpoint: 5 users, 30s ramp, 60s duration
- Product endpoint: 5 users, 30s ramp, 60s duration
- Metrics: avg response time, 95th percentile, error %, throughput

---

## Scaling Path

### Phase 1 (Current): Standalone Chrome
- Single `selenium/standalone-chrome` container
- pytest-xdist for parallel test execution
- Good for up to ~30 tests

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

> "I built an end-to-end automation framework with three layers: UI tests using Selenium with Page Object Model, API validation using requests with JSON schema checking, and performance testing using JMeter.
>
> At the core is a DriverFactory that abstracts browser creation — it supports local Chrome, headless mode, and remote Selenium Grid through a single environment variable. All page interactions go through a BasePage class with explicit waits, structured logging, and automatic screenshot capture on failure.
>
> The API layer independently validates the same data the UI shows. After searching in the browser, a parallel API test validates the response schema, measures response time, and cross-checks prices. This catches stale caches, CDN issues, and calculation mismatches that pure UI testing misses.
>
> Configuration uses pydantic-settings. A single `AUTO_ENVIRONMENT` flag switches between local, CI, and staging. The whole thing runs in Docker — one container for Selenium Chrome, one for the test runner. GitHub Actions orchestrates it, and on the droplet a nightly cron runs regression and publishes reports behind nginx."

### Tradeoffs

| Decision | Tradeoff | Why |
|----------|----------|-----|
| Standalone Chrome over Grid | No multi-node parallelism | Overkill for 15 tests; upgrade is one env var |
| pytest-html over Allure | Less visual | Zero server needed; self-contained HTML |
| Function-scoped driver | Slower (restart per test) | Test isolation; no state leakage |
| Sync requests over httpx | No async | pytest tests are sync; no benefit |
| CSS selectors over XPath | More fragile to DOM changes | Faster execution; more readable |

---

## Ethical Design

- Custom User-Agent identifies all traffic as automated portfolio project
- JMeter load capped at 5-10 users with 2-3 second think times
- No login, payment, or account creation flows
- No aggressive crawling or data scraping
- Designed as a read-only validation framework

---

## License

MIT
