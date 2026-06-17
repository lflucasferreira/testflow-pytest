# UI State Tests — Loading, error, success, empty, and accessibility

**Source file:** [`../../../../tests/states/test_states.py`](../../../../tests/states/test_states.py)

---

## Purpose

This module exercises the **States** page (`/web/states.html`), designed to demonstrate common **state transitions** in real applications:

| Area | States covered |
|------|----------------|
| Skeleton loading | idle → loading → cards loaded → reset |
| Simulated fetch | error (failure) vs success |
| Listing | empty state (search with no results) |
| Partial grid | cards with mixed statuses |
| Accessibility | axe scan with no critical violations |

Ideal material for learning **explicit waits**, **custom timeouts**, and integration with **axe-playwright**.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Sandbox server | Running with `/web/states.html` route |
| Authentication | `visit_authenticated` via API |
| a11y package | `axe-playwright-python` (`check_a11y` function in `conftest.py`) |
| Fixtures | `page`, `api_request` |

**Execution:**

```bash
pytest tests/states/test_states.py -v
pytest tests/states/test_states.py -m a11y
pytest tests/states/test_states.py -m smoke
```

---

## Markers used

| Marker | Application |
|--------|-------------|
| `regression` | All test classes |
| `smoke` | `test_shows_idle_message_before_load` |
| `a11y` | `TestStatesAccessibility` class |

---

## Structure overview

```
test_states.py
├── imports
├── autouse fixture: states_page
├── TestSkeletonLoading (3 tests)
├── TestErrorAndSuccessStates (2 tests)
├── TestEmptyAndPartialStates (2 tests)
└── TestStatesAccessibility (1 test)
```

---

## Imports — block by block

### `import pytest`

Test framework — fixtures, markers, and class discovery.

---

### `from playwright.sync_api import Page, expect`

- **`Page`**: browser tab for interactions and locators.
- **`expect`**: assertions with auto-retry (essential after clicks that trigger animations or fetch).

---

### `from conftest import check_a11y`

Imports helper **from the project root** (not from `support/`). Runs axe-core via `axe_playwright_python`:

- WCAG 2.0/2.1 tags (`wcag2a`, `wcag2aa`)
- Ignores `color-contrast` rule by default (common in demo sandboxes)
- Fails if there are `critical` or `serious` violations

**Concept:** a11y tests complement functional tests — a button can "work" and still be inaccessible.

---

### `from support.auth import visit_authenticated`

Authenticates via API and navigates to the given path. Same pattern as the Advanced module.

---

## Fixture: `states_page`

```python
@pytest.fixture(autouse=True)
def states_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/states.html")
    expect(page.get_by_test_id("page-states")).to_be_attached()
```

| Aspect | Detail |
|--------|--------|
| Scope | Function (default) — runs before each test |
| autouse | Yes — all tests start on the authenticated States page |
| Gate | `page-states` must exist in the DOM |

**Global Given for the module:** logged-in user at `/web/states.html`.

---

## Class `TestSkeletonLoading`

Validates the **skeleton screen** pattern: animated placeholder while data loads.

---

### `test_shows_idle_message_before_load`

```python
@pytest.mark.smoke
def test_shows_idle_message_before_load(self, page: Page) -> None:
    expect(page.get_by_test_id("skeleton-idle")).to_contain_text("Load cards")
```

| Phase | Description |
|-------|-------------|
| **Given** | States page freshly loaded, skeleton section in initial state |
| **When** | No action |
| **Then** | Idle message contains text "Load cards" |

**Smoke marker:** quick check that the page rendered the idle state.

**Playwright:** `to_contain_text` does partial match (substring), useful for dynamic copy.

---

### `test_loads_metric_cards_after_skeleton_delay`

```python
def test_loads_metric_cards_after_skeleton_delay(self, page: Page) -> None:
    page.get_by_test_id("skeleton-trigger").click()
    expect(page.get_by_test_id("loaded-card")).to_have_count(4, timeout=5000)
```

| Phase | Description |
|-------|-------------|
| **Given** | Idle state |
| **When** | Clicks `skeleton-trigger` (simulates fetch with delay) |
| **Then** | Exactly 4 `loaded-card` elements appear within 5 seconds |

**Playwright concept — timeout:** default is ~5s; here `timeout=5000` ms is explicit because skeleton + delay may exceed the default in slow environments.

**UI concept:** skeleton → real content is async; never use fixed `time.sleep` — use assertions that wait.

---

### `test_resets_skeleton_section`

```python
def test_resets_skeleton_section(self, page: Page) -> None:
    page.get_by_test_id("skeleton-trigger").click()
    expect(page.get_by_test_id("loaded-card").first).to_be_visible(timeout=5000)
    page.get_by_test_id("skeleton-reset").click()
    expect(page.get_by_test_id("skeleton-idle")).to_be_visible()
```

| Phase | Description |
|-------|-------------|
| **Given** | Idle |
| **When** | Loads cards → clicks reset |
| **Then** | Returns to visible idle state |

**Full flow:** load → intermediate assert → reset → final assert. Model for **component lifecycle** testing.

---

## Class `TestErrorAndSuccessStates`

Simulates successful and failed API responses in the UI.

---

### `test_shows_error_state_on_failed_fetch`

```python
def test_shows_error_state_on_failed_fetch(self, page: Page) -> None:
    page.get_by_test_id("error-trigger").click()
    error = page.get_by_test_id("error-state")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Request failed")
```

| Phase | Description |
|-------|-------------|
| **Given** | States page |
| **When** | Triggers failing fetch (`error-trigger`) |
| **Then** | Error banner/area visible with message "Request failed" |

**Pattern:** reuse locator in a variable (`error`) for readable multiple assertions.

---

### `test_shows_success_state_on_successful_fetch`

```python
def test_shows_success_state_on_successful_fetch(self, page: Page) -> None:
    page.get_by_test_id("success-trigger").click()
    success = page.get_by_test_id("success-state")
    expect(success).to_be_visible()
    expect(success).to_contain_text("succeeded")
```

Mirror of the error test — validates **positive feedback** after a successful operation.

---

## Class `TestEmptyAndPartialStates`

Scenarios with incomplete or missing data.

---

### `test_renders_empty_state_when_search_has_no_matches`

```python
def test_renders_empty_state_when_search_has_no_matches(self, page: Page) -> None:
    page.get_by_test_id("empty-search").fill("xyzno match")
    expect(page.get_by_test_id("empty-state")).to_be_visible()
    expect(page.get_by_test_id("result-list")).not_to_be_attached()
```

| Phase | Description |
|-------|-------------|
| **Given** | Empty search field |
| **When** | Fills term with no matches |
| **Then** | Empty state visible; result list **not** in the DOM |

**Concept:** `not_to_be_attached` confirms the UI did not render a hidden empty list — correct empty state pattern.

**Playwright:** `fill()` clears and types; fires input events like a real user.

---

### `test_loads_partial_grid_with_mixed_card_statuses`

```python
def test_loads_partial_grid_with_mixed_card_statuses(self, page: Page) -> None:
    page.get_by_test_id("partial-trigger").click()
    expect(page.locator('[data-testid^="partial-card-"]')).to_have_count(6)
```

| Phase | Description |
|-------|-------------|
| **Given** | Partial grid not loaded |
| **When** | Clicks `partial-trigger` |
| **Then** | 6 cards with `data-testid` prefixed `partial-card-` |

**CSS selector:** `[data-testid^="partial-card-"]` = attribute **starts with** prefix. Playwright alternative: `get_by_test_id` does not support prefix natively; CSS `locator` is appropriate here.

---

## Class `TestStatesAccessibility`

```python
@pytest.mark.regression
@pytest.mark.a11y
class TestStatesAccessibility:
    def test_states_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
```

| Phase | Description |
|-------|-------------|
| **Given** | States page loaded (fixture) |
| **When** | `check_a11y` runs axe on the full page |
| **Then** | No critical/serious violations (except disabled rules) |

**`a11y` marker:** enables dedicated pipeline (`pytest -m a11y`).

**Note for students:** a11y is a behavioral snapshot of the current accessible tree — copy or ARIA changes may require adjusting disabled rules.

---

## PyTest and Playwright concepts — summary

### Waiting and flakiness

- Prefer `expect(..., timeout=5000)` over fixed sleeps.
- After async clicks, always use web-first assertions.

### Organization

- One class per **feature/state** improves readability and reports.
- Single module-level `autouse` fixture avoids duplicating login.

### Given / When / Then

| Class | Typical When |
|-------|--------------|
| Skeleton | click on trigger / reset |
| Error/Success | click on fetch triggers |
| Empty/Partial | fill / click |
| A11y | (no When — static scan) |

---

## Learning checklist

- [ ] Explain skeleton loading vs traditional spinner
- [ ] Justify `timeout=5000` on skeleton
- [ ] Differentiate visible empty state vs empty list in the DOM
- [ ] Describe what `check_a11y` does internally
- [ ] Run `-m a11y` in isolation
