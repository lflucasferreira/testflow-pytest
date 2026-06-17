# Dashboard Tests

**Source file:** [`../../../../tests/dashboard/test_dashboard.py`](../../../../tests/dashboard/test_dashboard.py)

---

## Purpose

This file validates the **Dashboard** page (`/web/dashboard.html`) after authentication:

- Personalized greeting and subtitle
- KPI cards (runs, pass rate, members, issues)
- Recent activity list
- Test suite health indicators
- "New Test Run" modal (open, fill, close, confirm)
- Quick access links to other pages

All tests assume a user **already logged in** via API — focus is on dashboard UI, not the login flow.

---

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| Local server | `BASE_URL` accessible (default: `http://localhost:5050`). |
| API authentication | `POST /api/auth/login` endpoint functional. |
| Page Object | `DashboardPage` in `pages/dashboard_page.py`. |
| Auth helper | `login_via_api` in `support/auth.py`. |

**Global fixtures used:**

- `page` — Playwright tab.
- `api_request` — HTTP client to obtain authentication token.

---

## Markers used

```python
pytestmark = pytest.mark.regression
```

The entire module is marked as **regression**. No individual test adds `smoke`, `critical`, or `api`.

```bash
pytest tests/dashboard/test_dashboard.py -m regression
pytest tests/dashboard/test_dashboard.py -v
```

---

## PyTest and Playwright concepts used in this file

### `autouse` setup fixture

`setup_dashboard` runs before each test: logs in via API and confirms the dashboard loaded. Eliminates repeated boilerplate.

### Page Object Model

`DashboardPage` encapsulates locators (`get_by_test_id`) and actions (`open_new_run_modal`, `select_suite`) — tests read like natural-language specifications.

### `expect` with regex

`to_have_text(re.compile(r"^\d+(\.\d+)?%$"))` validates percentage format without a fixed exact value.

### `Locator.inner_text()`

Returns visible element text — used to extract numeric KPI value.

### `page.keyboard.press("Escape")`

Simulates the Escape key — tests modal closing via keyboard shortcut.

### `page.go_back()`

Navigates to the previous page in history — used after clicking quick access so subsequent tests are not affected.

### `@pytest.mark.parametrize` on a class

The decorator on `TestQuickAccessNavigation` parametrizes **all** test methods inside it (in this case, only one method).

### `re.escape(path)`

Escapes special characters in the path for safe use inside `re.compile` in URL assertions.

---

## Imports — line by line

```python
import re
```

Regex for validating text formats (percentages, URLs, CSS styles).

```python
import pytest
```

Test framework.

```python
from playwright.sync_api import APIRequestContext, Page, expect
```

| Symbol | Use in this file |
|--------|------------------|
| `Page` | Dashboard UI interaction |
| `APIRequestContext` | API login in setup fixture |
| `expect` | Assertions with retry |

```python
from pages.dashboard_page import DashboardPage
```

Page Object with dashboard locators and methods.

```python
from support.auth import login_via_api
```

Authenticates via API, injects session into the browser, and navigates to the dashboard.

---

## Module configuration

```python
pytestmark = pytest.mark.regression
```

Marks the entire file as a regression suite.

---

## `setup_dashboard` fixture

```python
@pytest.fixture(autouse=True)
def setup_dashboard(page: Page, api_request: APIRequestContext) -> None:
    login_via_api(page, api_request)
    DashboardPage(page).should_be_loaded()
```

**Execution (before each test):**

1. **`login_via_api(page, api_request)`**
   - Obtains token via `POST /api/auth/login`
   - Injects `sessionStorage` with `inject_auth` + `_seed_session_storage`
   - Navigates to dashboard and waits for `page-dashboard`

2. **`DashboardPage(page).should_be_loaded()`**
   - Assert: `[data-testid="page-dashboard"]` is visible

**Implicit Given for all tests:** authenticated user on the dashboard ready for interaction.

**PyTest concept:** `autouse` fixture + chained dependencies (`page`, `api_request`) = zero-line setup in test methods.

---

## `DashboardPage` Page Object — reference

Methods and locators used in this test file:

| Method / Locator | `data-testid` | Function |
|------------------|---------------|----------|
| `page_root()` | `page-dashboard` | Root container |
| `greeting()` | `dash-greeting` | Time-based greeting |
| `subtitle()` | `dash-subtitle` | Subtitle |
| `kpi_card(name)` | `kpi-{name}` | KPI card |
| `kpi_value(name)` | `kpi-{name}-value` | Numeric value |
| `kpi_trend(name)` | `kpi-{name}-trend` | Trend indicator |
| `activity_item(n)` | `activity-item-{n}` | List item |
| `health_status()` | `health-status` | Health badge |
| `health_bar(suite)` | `health-{suite}` | Progress bar |
| `health_pct(suite)` | `health-{suite}-pct` | Percentage text |
| `open_new_run_modal()` | clicks `btn-new-run` | Opens modal |
| `run_suite_select()` | `run-suite` | Suite select |
| `run_env_select()` | `run-env` | Environment select |
| `confirm_run()` / `cancel_run()` | modal buttons | Modal actions |
| `quick_action(name)` | `qa-{name}` | Quick access buttons |

---

## `TestGreeting` class

Validates welcome elements at the top of the dashboard.

### `test_shows_time_based_greeting_with_the_user_name`

```python
def test_shows_time_based_greeting_with_the_user_name(self, page: Page) -> None:
    dashboard = DashboardPage(page)
    dashboard.should_show_greeting()
    expect(dashboard.greeting()).to_contain_text("Demo User")
```

**`should_show_greeting()`** (in the Page Object):

```python
expect(self.greeting()).to_be_visible()
expect(self.greeting()).to_have_text(re.compile(r"Good (morning|afternoon|evening),"))
```

- **Given:** dashboard loaded.
- **Then:** greeting visible in the format "Good morning/afternoon/evening," **and** contains the name "Demo User".

**Concept:** composite assertion — Page Object verifies format; test verifies demo user-specific content.

### `test_shows_a_non_empty_subtitle`

```python
subtitle = DashboardPage(page).subtitle()
expect(subtitle).to_be_visible()
expect(subtitle).not_to_be_empty()
```

- **Then:** subtitle exists, is visible, and has text.

`not_to_be_empty()` — Playwright matcher that fails if the element has no text content.

---

## `TestKpiCards` class

Validates the four main metric cards.

### `test_renders_all_four_kpi_cards`

```python
DashboardPage(page).should_have_all_kpi_cards()
```

Page Object iterates `("runs", "passrate", "members", "issues")` and verifies visibility + non-empty value.

### `test_shows_a_numeric_value_in_the_runs_card`

```python
text = DashboardPage(page).kpi_value("runs").inner_text()
assert int(text) > 0
```

- **When:** reads text from the "runs" KPI.
- **Then:** converts to integer and confirms value > 0.

**Concept:** combines Playwright (`inner_text()`) with native Python assert for numeric logic.

### `test_shows_a_percentage_in_the_pass_rate_card`

```python
expect(DashboardPage(page).kpi_value("passrate")).to_have_text(
    re.compile(r"^\d+(\.\d+)?%$")
)
```

- **Then:** value follows a pattern like `97%` or `97.5%`.

Regex explained:
- `^` start, `\d+` digits, `(\.\d+)?` optional decimals, `%` literal, `$` end.

### `test_shows_trend_indicators_on_each_card`

```python
dashboard = DashboardPage(page)
for key in ("runs", "passrate", "members", "issues"):
    expect(dashboard.kpi_trend(key)).to_be_visible()
    expect(dashboard.kpi_trend(key)).not_to_be_empty()
```

- **Then:** each card has a visible trend indicator with text (e.g. "↑ 12%").

---

## `TestRecentActivity` class

Validates the recent activity section.

### `test_shows_5_activity_items`

```python
DashboardPage(page).should_have_activity_items(5)
```

Page Object counts elements `[data-testid^="activity-item-"]` inside `activity-list` and expects exactly 5.

### `test_each_activity_item_has_text_and_a_timestamp`

```python
item = DashboardPage(page).activity_item(1)
expect(item.locator(".activity-text")).not_to_be_empty()
expect(item.locator(".activity-time")).not_to_be_empty()
```

- **Then:** first item has description (`.activity-text`) and timestamp (`.activity-time`).

**Playwright concept:** `locator.locator(".activity-text")` — descendant search within the parent item.

### `test_see_all_link_navigates_to_activity_page`

```python
DashboardPage(page).quick_action("team")
page.get_by_test_id("activity-see-all").click()
expect(page).to_have_url(re.compile(r"/web/activity\.html"))
```

**Note:** calls `quick_action("team")` before clicking "See all" — possible prior interaction to ensure UI state (original test pattern).

- **When:** clicks the activity "See all" link.
- **Then:** navigates to `/web/activity.html`.

---

## `TestSuiteHealth` class

Validates automation suite health indicators.

### `test_shows_healthy_status_badge`

```python
dashboard = DashboardPage(page)
expect(dashboard.health_status()).to_be_visible()
expect(dashboard.health_status()).to_contain_text("Healthy")
```

- **Then:** global badge indicates "Healthy" status.

### `test_renders_three_suite_health_bars`

```python
for suite in ("regression", "smoke", "e2e"):
    expect(dashboard.health_bar(suite)).to_be_visible()
    expect(dashboard.health_pct(suite)).to_have_text(re.compile(r"^\d+%$"))
```

- **Then:** three bars (regression, smoke, e2e) visible with whole-number percentage (e.g. `97%`).

### `test_regression_bar_fill_width_reflects_its_percentage`

```python
expect(DashboardPage(page).health_bar("regression")).to_have_attribute(
    "style", re.compile(r"width:97%")
)
```

- **Then:** inline `style` attribute on the regression bar contains `width:97%`.

Tests that the **visual value** of the bar matches the data — inline CSS as source of truth.

---

## `TestNewTestRunModal` class

Validates the full new test run modal flow.

### `test_opens_modal_on_button_click`

```python
dashboard = DashboardPage(page)
dashboard.open_new_run_modal()
dashboard.should_show_run_modal_open()
```

- **When:** clicks "New Run".
- **Then:** modal overlay (`run-modal-overlay`) visible.

### `test_modal_has_suite_and_environment_selects`

```python
dashboard.open_new_run_modal()
expect(dashboard.run_suite_select()).to_be_visible()
expect(dashboard.run_env_select()).to_be_visible()
```

- **Then:** suite and environment selects present in the modal.

### `test_closes_modal_on_cancel`

```python
dashboard.open_new_run_modal()
dashboard.cancel_run()
dashboard.should_show_run_modal_closed()
```

- **When:** clicks Cancel.
- **Then:** modal not visible.

### `test_closes_modal_on_escape_key`

```python
dashboard.open_new_run_modal()
page.keyboard.press("Escape")
dashboard.should_show_run_modal_closed()
```

- **When:** presses Escape.
- **Then:** modal closes (accessibility UX pattern).

### `test_closes_modal_on_overlay_click`

```python
page.get_by_test_id("run-modal-overlay").click(
    position={"x": 10, "y": 10}, force=True
)
dashboard.should_show_run_modal_closed()
```

- **When:** clicks the overlay outside the modal content.
- **Then:** modal closes.

**Playwright concepts:**
- `position={"x": 10, "y": 10}` — click at specific coordinates on the element.
- `force=True` — ignores actionability checks (element may be partially covered).

### `test_confirms_a_run_and_shows_toast`

```python
dashboard.open_new_run_modal()
dashboard.select_suite("smoke")
dashboard.select_environment("staging")
dashboard.confirm_run()
dashboard.should_show_run_modal_closed()
expect(page.get_by_test_id("toast-message")).to_contain_text("smoke")
```

| Step | Given/When/Then |
|------|-----------------|
| Opens modal | **When** starts new run |
| Selects smoke + staging | **When** fills form |
| Confirms | **When** submits |
| Modal closes + toast | **Then** feedback confirms "smoke" suite |

**Concept:** `select_option(value)` on `<select>` — equivalent to choosing an option in a dropdown.

---

## `TestQuickAccessNavigation` class

```python
@pytest.mark.parametrize(
    "test_id,path",
    [
        ("qa-team", "/web/team.html"),
        ("qa-settings", "/web/settings.html"),
        ("qa-wizard", "/web/wizard.html"),
    ],
)
class TestQuickAccessNavigation:
```

**Class-level parametrize** — applies parameters to all test methods in the class.

### `test_quick_access_navigates`

```python
def test_quick_access_navigates(self, page: Page, test_id: str, path: str) -> None:
    page.get_by_test_id(test_id).click()
    expect(page).to_have_url(re.compile(re.escape(path)))
    page.go_back()
```

For each `(test_id, path)` tuple:

| Run | Button | Destination |
|-----|--------|-------------|
| 1 | `qa-team` | `/web/team.html` |
| 2 | `qa-settings` | `/web/settings.html` |
| 3 | `qa-wizard` | `/web/wizard.html` |

- **When:** clicks quick access button.
- **Then:** URL matches expected path.
- **Cleanup:** `page.go_back()` returns to dashboard so subsequent tests are not polluted (same browser session).

---

## Shared setup flow

```
┌──────────────────────────────────────────┐
│  setup_dashboard (autouse, each test)    │
├──────────────────────────────────────────┤
│  1. login_via_api(page, api_request)     │
│     └─ POST /api/auth/login → token      │
│     └─ inject sessionStorage             │
│     └─ goto /web/dashboard.html          │
│  2. DashboardPage.should_be_loaded()     │
└──────────────────────────────────────────┘
                    │
                    ▼
         TestGreeting / TestKpiCards /
         TestRecentActivity / TestSuiteHealth /
         TestNewTestRunModal / TestQuickAccessNavigation
```

---

## Summary for new learners

| Pattern | Where | Why |
|---------|-------|-----|
| Autouse setup | `setup_dashboard` | DRY — login once per test |
| Page Object | `DashboardPage` | Readable tests, centralized selectors |
| Regex in expect | KPIs, URLs, CSS | Validates format without fragile data |
| Modal UX | Escape, overlay, cancel | UI pattern coverage |
| Class parametrize | Quick access | One method, three routes |
| `go_back()` | Quick access | Isolation between tests |

**Suggested command to explore visually:**

```bash
pytest tests/dashboard/test_dashboard.py::TestNewTestRunModal -v --headed --slowmo=500
```

`--slowmo=500` adds a 500 ms pause between actions — ideal for watching modals open and close while learning.
