# Activity Page Tests

**Source file:** [`../../../../tests/activity/test_activity.py`](../../../../tests/activity/test_activity.py)

---

## Purpose

This module validates the **Activity** page (`/web/activity.html`), focused on advanced automation patterns:

- **API calls via UI** — buttons that trigger fetch and display results
- **Network interception** — artificial delay and response mocking
- **Local state** — counter increment/decrement/reset
- **Simulated progress** — download bar
- **Dynamic content** — asynchronous loading
- **Data fixtures** — reading JSON and CSV
- **File upload** — drag-and-drop / file input

It is a lab for concepts beyond simple clicks: network, time, files, and external data.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Environment | TestFlow server running |
| Authentication | `visit_authenticated` via autouse fixture |
| Fixtures | [`fixtures/users/empty-list.json`](../../../../fixtures/users/empty-list.json), [`fixtures/sample.csv`](../../../../fixtures/sample.csv), [`fixtures/lookups/countries.json`](../../../../fixtures/lookups/countries.json) |
| Helper | [`support/helpers/fixtures.py`](../../../../support/helpers/fixtures.py) |

```bash
pytest tests/activity/test_activity.py -v
pytest tests/activity/test_activity.py -m smoke
pytest tests/activity/test_activity.py -m api
pytest tests/activity/test_activity.py -m regression
```

---

## Markers used

| Marker | Where it appears | Meaning |
|--------|------------------|---------|
| `regression` | `TestActivity` class | Regression suite |
| `smoke` | `test_fetches_users_via_api_button` | Quick API-via-UI gate |
| `api` | `test_fetches_users_via_api_button` | Test with HTTP response validation |

---

## Structure overview

```
test_activity.py
├── Imports
├── Fixture autouse: activity_page
└── TestActivity (8 test methods)
```

---

## Imports — block by block

### `import time`

Standard library for pauses. Used in the slow route handler (`time.sleep(1.5)`) to simulate API latency.

**Note:** In UI tests we prefer `page.clock` when possible; here the delay is **in the network handler**, not in the test itself.

---

### `from pathlib import Path`

Object-oriented file path handling. Used indirectly via `FIXTURES_ROOT` (which is a `Path`).

---

### `import pytest`

Test framework.

---

### `from playwright.sync_api import Page, expect`

Playwright sync API.

---

### `from support.auth import visit_authenticated`

API authentication + navigation.

**Note:** This file does **not** import `check_a11y` — there are no accessibility tests here.

---

### `from support.helpers.fixtures import FIXTURES_ROOT, read_fixture`

| Symbol | Role |
|--------|------|
| `FIXTURES_ROOT` | Absolute `Path` to the `fixtures/` folder at project root |
| `read_fixture(relative_path)` | Reads and parses JSON relative to `FIXTURES_ROOT` |

---

## Fixture: `activity_page`

```python
@pytest.fixture(autouse=True)
def activity_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/activity.html")
    expect(page.get_by_test_id("page-activity")).to_be_attached()
```

| Aspect | Explanation |
|--------|-------------|
| Setup | API login + goto `/web/activity.html` |
| Verification | Root element `page-activity` present in DOM |

---

## Class `TestActivity`

```python
@pytest.mark.regression
class TestActivity:
```

Single class — all activity tests grouped here.

---

### `test_fetches_users_via_api_button`

```python
@pytest.mark.smoke
@pytest.mark.api
def test_fetches_users_via_api_button(self, page: Page) -> None:
    with page.expect_response("**/api/users") as response_info:
        page.get_by_test_id("fetch-users-btn").click()
    response = response_info.value
    assert response.status == 200
    expect(page.get_by_test_id("api-result")).not_to_be_empty()
```

| Step | Description |
|------|-------------|
| **Given** | Activity page loaded |
| **When** | Clicks fetch button inside `expect_response` |
| **Then (network)** | `/api/users` response with status 200 |
| **Then (UI)** | Result area not empty |

**Playwright concepts:**

| API | Usage |
|-----|-------|
| `page.expect_response("**/api/users")` | Context manager that captures response whose URL matches glob |
| `response_info.value` | `Response` object after the action |
| `response.status` | HTTP status code |

**Markers:** `smoke` + `api` — quick test validating UI ↔ API integration.

---

### `test_handles_slow_api_with_intercept_delay`

```python
def test_handles_slow_api_with_intercept_delay(self, page: Page) -> None:
    def slow_handler(route) -> None:
        time.sleep(1.5)
        route.continue_()

    page.route("**/api/slow**", slow_handler)
    with page.expect_response("**/api/slow**"):
        page.get_by_test_id("fetch-slow-btn").click()
    expect(page.get_by_test_id("api-result")).to_be_visible()
```

| Aspect | Explanation |
|--------|-------------|
| `page.route` | Registers handler for URLs matching glob |
| `slow_handler` | Waits 1.5s before continuing real request |
| `route.continue_()` | Forwards to real server (with delay) |
| Final assertion | UI displays result after slow API |

**Given/When/Then:**

- **Given:** `/api/slow` route intercepted with delay
- **When:** Clicks slow API button
- **Then:** Response received + result visible in UI

**Concept:** Tests **loading states** and latency resilience without fully mocking the response.

---

### `test_increments_and_decrements_counter`

```python
def test_increments_and_decrements_counter(self, page: Page) -> None:
    page.get_by_test_id("counter-increment").click()
    page.get_by_test_id("counter-increment").click()
    expect(page.get_by_test_id("counter-value")).to_contain_text("2")
    page.get_by_test_id("counter-decrement").click()
    expect(page.get_by_test_id("counter-value")).to_contain_text("1")
    page.get_by_test_id("counter-reset").click()
    expect(page.get_by_test_id("counter-value")).to_contain_text("0")
```

| Sequence | Expected value |
|----------|----------------|
| +1, +1 | `"2"` |
| -1 | `"1"` |
| reset | `"0"` |

Tests **local JavaScript state** — reactive counter without backend involvement.

**Concept:** `to_contain_text` is tolerant — works even if the element has extra markup.

---

### `test_starts_download_progress_simulation`

```python
def test_starts_download_progress_simulation(self, page: Page) -> None:
    page.get_by_test_id("progress-start").click()
    expect(page.get_by_test_id("download-progress")).to_be_attached()
```

| **When** | Starts download simulation |
| **Then** | Progress element exists in DOM |

Uses `to_be_attached()` — bar may exist before visual animation completes.

---

### `test_loads_dynamic_content_section`

```python
def test_loads_dynamic_content_section(self, page: Page) -> None:
    page.get_by_test_id("load-dynamic-btn").click()
    expect(page.get_by_test_id("dynamic-content")).not_to_be_empty()
```

| **When** | Clicks load dynamic content |
| **Then** | Section filled (not empty) |

Tests content injected asynchronously after interaction.

---

### `test_uses_mock_api_get_with_empty_users_fixture`

```python
def test_uses_mock_api_get_with_empty_users_fixture(self, page: Page) -> None:
    page.route(
        "**/api/users",
        lambda route: route.fulfill(json=read_fixture("users/empty-list.json")),
    )
    with page.expect_response("**/api/users"):
        page.get_by_test_id("fetch-users-btn").click()
    expect(page.get_by_test_id("api-result")).to_contain_text("Fetched 0 users")
```

| Aspect | Explanation |
|--------|-------------|
| `route.fulfill(json=...)` | Mocked response — does **not** call real backend |
| `read_fixture("users/empty-list.json")` | Empty list payload from disk |
| Assertion | UI reflects `"Fetched 0 users"` |

**Given/When/Then:**

- **Given:** `/api/users` API returns empty list via mock
- **When:** User clicks fetch
- **Then:** Message confirms zero users

**Concept:** API mocking enables deterministic testing of **edge cases** (empty list).

---

### `test_read_fixture_exposes_countries_lookup_for_test_data`

```python
def test_read_fixture_exposes_countries_lookup_for_test_data(self) -> None:
    data = read_fixture("lookups/countries.json")
    codes = [country["code"] for country in data["countries"]]
    assert "CA" in codes
```

| Aspect | Explanation |
|--------|-------------|
| No `page` | **Unit** test of helper — no browser needed |
| List comprehension | Extracts country codes |
| `assert "CA" in codes` | Fixture contains Canada |

**PyTest concept:** Not every test in a Playwright file needs the `page` fixture — utility tests can coexist.

---

### `test_accepts_csv_file_via_drag_and_drop_on_drop_zone`

```python
def test_accepts_csv_file_via_drag_and_drop_on_drop_zone(self, page: Page) -> None:
    csv_path = FIXTURES_ROOT / "sample.csv"
    file_input = page.locator('[data-testid="drop-zone"] input[type="file"]')
    if file_input.count():
        file_input.set_input_files(str(csv_path))
    else:
        page.get_by_test_id("drop-zone").click()
    expect(page.get_by_test_id("page-activity")).to_be_visible()
```

| Aspect | Explanation |
|--------|-------------|
| `FIXTURES_ROOT / "sample.csv"` | Absolute path to test CSV |
| `locator(... input[type="file"])` | Hidden file input inside drop zone |
| `file_input.count()` | Checks if input exists |
| `set_input_files(str(csv_path))` | Simulates file selection (equivalent to upload) |
| Fallback | If no input, clicks drop zone |
| Minimal assertion | Page remains stable/visible |

**Playwright concept:** `set_input_files()` is the reliable way to test upload — real drag-and-drop is more complex; many projects test via the underlying file input.

**`Path` concept:** `FIXTURES_ROOT / "sample.csv"` concatenates paths in a cross-platform way.

---

## Summary of concepts learned

| Concept | Where it appears |
|---------|------------------|
| Network interception | `page.route`, `route.continue_()`, `route.fulfill()` |
| Response capture | `page.expect_response` |
| Latency simulation | `time.sleep` in route handler |
| API mocking | `fulfill(json=read_fixture(...))` |
| Local UI state | Counter increment/decrement |
| Dynamic content | `not_to_be_empty()` after click |
| Data fixtures | `read_fixture`, `FIXTURES_ROOT` |
| File upload | `set_input_files()` |
| Test without browser | Method without `page` parameter |
| Markers | `smoke`, `api`, `regression` |

---

## Comparison: Activity vs other modules

| Aspect | Activity | Settings | Components | Wizard |
|--------|----------|----------|------------|--------|
| Page Object | No | Yes (`SettingsPage`) | No | Private helpers |
| API interception | Yes (heavy) | Yes (selective) | No | Yes (countries) |
| A11y | No | Yes | Yes | Yes |
| Factories | No | No | TC constants | Faker factories |
| Focus | Network, files, state | Complex forms | UI components | Multi-step flow |
