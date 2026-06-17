# Components Page Tests

**Source file:** [`../../../../tests/components/test_components.py`](../../../../tests/components/test_components.py)

---

## Purpose

This module validates the **Components** page (`/web/components.html`), a catalog of reusable UI components in the TestFlow sandbox. The tests cover:

- **Buttons** — variants, disabled/loading states, toast, native dialogs (`alert`, `confirm`)
- **Modal** — open, close (buttons, Escape, overlay click), ARIA attributes
- **Tabs** — navigation, panels, ARIA roles, keyboard focus
- **Accordion** — expand/collapse, multiple panels open
- **Accessibility** — full page and open modal

Unlike Settings, this file interacts **directly with Playwright locators** (`page.get_by_test_id`) instead of a dedicated Page Object — a common pattern for demo/catalog pages.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Environment | TestFlow server running |
| Authentication | `visit_authenticated` via autouse fixture |
| Dependencies | `pytest`, `playwright`, `axe-playwright-python` |
| TC constants | [`support/constants/test_cases.py`](../../../../support/constants/test_cases.py) |

```bash
pytest tests/components/test_components.py -v
pytest tests/components/test_components.py -m regression
pytest tests/components/test_components.py -m a11y
```

---

## Markers used

| Marker | Where it appears | Meaning |
|--------|------------------|---------|
| `regression` | Each test class (`@pytest.mark.regression`) | Regression suite |
| `a11y` | `TestComponentsAccessibility` | Accessibility tests |
| `parametrize` (via TC) | `test_loading_button_shows_spinner...` | Links test to test case ID (`TC-0501`) |

There is no module-level `pytestmark` — each class declares `@pytest.mark.regression` explicitly.

---

## Structure overview

```
test_components.py
├── Imports
├── Fixture autouse: components_page
├── TestButtons
├── TestModal (+ fixture autouse: open_modal)
├── TestTabs
├── TestAccordion
└── TestComponentsAccessibility
```

---

## Imports — block by block

### `import pytest`

Test framework — fixtures, markers, parametrization, and test classes.

---

### `from playwright.sync_api import Page, expect`

| Symbol | Role |
|--------|------|
| `Page` | Browser tab for synchronous interactions |
| `expect` | Playwright auto-retry assertions |

**Concept:** The **sync** API is ideal for beginners — each action blocks until complete. The `async_api` variant exists for async tests.

---

### `from conftest import check_a11y`

Runs axe-core scan and fails on critical/serious violations.

---

### `from support.auth import visit_authenticated`

Authenticates via API and navigates to the given path — avoids repeated manual login.

---

### `from support.constants.test_cases import TC, tc`

| Symbol | Role |
|--------|------|
| `TC` | Class with test case ID constants (e.g., `TC.COMP_LOADING_BUTTON = "TC-0501"`) |
| `tc(case_id, title)` | Formats string `"[TC-0501] loading button shows spinner..."` for reports |

**PyTest concept:** Traceable test case IDs in CI and Zephyr/Jira integrations.

---

## Fixture: `components_page`

```python
@pytest.fixture(autouse=True)
def components_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/components.html")
    expect(page.get_by_test_id("page-components")).to_be_attached()
```

| Aspect | Explanation |
|--------|-------------|
| `autouse=True` | Automatic setup before each test |
| `visit_authenticated` | Given: logged-in user |
| `to_be_attached()` | Element exists in DOM (may be hidden) — more permissive than `to_be_visible()` |

**Playwright concept:** `to_be_attached()` vs `to_be_visible()` — use attached when you only need to confirm DOM presence.

---

## Class `TestButtons`

```python
@pytest.mark.regression
class TestButtons:
```

Groups button tests and interactions that trigger feedback (toast, dialogs).

---

### `test_all_button_variants_are_visible`

```python
def test_all_button_variants_are_visible(self, page: Page) -> None:
    for test_id in ("btn-primary", "btn-secondary", "btn-success", "btn-danger"):
        btn = page.get_by_test_id(test_id)
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()
```

| Step | Description |
|------|-------------|
| **Given** | Components page loaded |
| **When** | Iterates button variants by `data-testid` |
| **Then** | Each button visible and enabled |

**Concept:** Loops in tests are valid when validating a homogeneous set of elements.

---

### `test_disabled_button_is_not_interactive`

```python
def test_disabled_button_is_not_interactive(self, page: Page) -> None:
    btn = page.get_by_test_id("btn-disabled")
    expect(btn).to_be_disabled()
    expect(btn).to_have_css("cursor", "not-allowed")
```

| **Then** | Button disabled and CSS cursor `not-allowed` |

Validates visual + semantic state of inactive button.

---

### `test_loading_button_shows_spinner_during_simulated_load`

```python
@pytest.mark.parametrize(
    "title",
    [tc(TC.COMP_LOADING_BUTTON, "loading button shows spinner during simulated load")],
    ids=[TC.COMP_LOADING_BUTTON],
)
def test_loading_button_shows_spinner_during_simulated_load(self, page: Page, title: str) -> None:
    del title
    page.clock.install()
    page.get_by_test_id("btn-loading").click()
    expect(page.get_by_test_id("btn-loading")).to_be_disabled()
    expect(page.locator(".spinner")).to_be_visible()
    page.clock.fast_forward(2000)
    expect(page.get_by_test_id("btn-loading")).to_be_enabled()
```

| Aspect | Explanation |
|--------|-------------|
| `@pytest.mark.parametrize` | Generates test case with ID `TC-0501` in report |
| `del title` | Parameter exists only for documentation/ID — not used in body |
| `page.clock.install()` | Playwright **mock clock** — controls JavaScript timers |
| `page.clock.fast_forward(2000)` | Advances 2 seconds without real wait |

**Given/When/Then:**

- **Given:** Mock clock installed
- **When:** Clicks loading button
- **Then (immediate):** Button disabled + spinner visible
- **When:** Advances 2s on clock
- **Then:** Button enabled again

**Playwright concept:** Clock API eliminates `time.sleep` — fast, deterministic tests.

---

### `test_toast_button_shows_a_toast_notification`

```python
def test_toast_button_shows_a_toast_notification(self, page: Page) -> None:
    page.get_by_test_id("btn-toast").click()
    toast = page.get_by_test_id("toast-message")
    expect(toast).to_be_visible()
    expect(toast).not_to_be_empty()
```

| **When** | Clicks toast button |
| **Then** | Toast visible with content |

---

### `test_native_alert_can_be_dismissed`

```python
def test_native_alert_can_be_dismissed(self, page: Page) -> None:
    messages: list[str] = []

    def handle_dialog(dialog) -> None:
        messages.append(dialog.message)
        dialog.accept()

    page.on("dialog", handle_dialog)
    page.get_by_test_id("btn-alert").click()
    assert messages
    assert messages[0]
```

| Concept | Detail |
|---------|--------|
| `dialog.accept()` | Confirms `alert` |
| `dialog.message` | Captures dialog text |
| `assert messages[0]` | Message not empty |

**Important:** Register handler **before** the click that triggers the dialog.

---

### `test_native_confirm_returns_true_on_accept`

```python
def test_native_confirm_returns_true_on_accept(self, page: Page) -> None:
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_test_id("btn-confirm").click()
    expect(page.get_by_test_id("dialog-result")).to_contain_text("Confirmed")
```

| **When** | Accepts confirm |
| **Then** | UI displays `"Confirmed"` |

---

### `test_native_confirm_returns_false_on_cancel`

```python
def test_native_confirm_returns_false_on_cancel(self, page: Page) -> None:
    page.on("dialog", lambda dialog: dialog.dismiss())
    page.get_by_test_id("btn-confirm").click()
    expect(page.get_by_test_id("dialog-result")).to_contain_text("Cancelled")
```

| **When** | Cancels confirm (`dismiss`) |
| **Then** | UI displays `"Cancelled"` |

---

## Class `TestModal`

```python
@pytest.mark.regression
class TestModal:
    @pytest.fixture(autouse=True)
    def open_modal(self, page: Page) -> None:
        page.get_by_test_id("open-modal-btn").click()
        expect(page.get_by_test_id("modal-overlay")).to_be_visible()
```

### Nested fixture: `open_modal`

| Aspect | Explanation |
|--------|-------------|
| Scope | Only tests inside `TestModal` |
| `autouse=True` | Opens modal before each test in the class |
| Execution order | `components_page` (module) → `open_modal` (class) → test |

**PyTest concept:** Fixtures can be defined **inside classes** — limiting setup to the relevant group.

---

### `test_opens_modal_and_shows_title`

```python
def test_opens_modal_and_shows_title(self, page: Page) -> None:
    expect(page.locator("#modal-title")).to_contain_text("Confirm action")
```

**Then:** Modal title contains `"Confirm action"`.

**Playwright concept:** `page.locator("#modal-title")` uses a CSS selector; `get_by_test_id` is preferred when available.

---

### `test_has_accessible_role_dialog`

```python
def test_has_accessible_role_dialog(self, page: Page) -> None:
    overlay = page.get_by_test_id("modal-overlay")
    expect(overlay).to_have_attribute("role", "dialog")
    expect(overlay).to_have_attribute("aria-modal", "true")
```

Validates accessibility contract for modals (WAI-ARIA).

---

### `test_closes_on_confirm_button`

```python
def test_closes_on_confirm_button(self, page: Page) -> None:
    page.get_by_test_id("modal-confirm-btn").click()
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
    expect(page.get_by_test_id("toast-message")).to_be_visible()
```

| **When** | Confirms action |
| **Then** | Modal closes + feedback toast |

---

### `test_closes_on_cancel_button`

```python
def test_closes_on_cancel_button(self, page: Page) -> None:
    page.get_by_test_id("modal-cancel-btn").click()
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

Close via cancel button.

---

### `test_closes_on_close_button`

```python
def test_closes_on_close_button(self, page: Page) -> None:
    page.get_by_test_id("modal-close-btn").click()
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

Close via X button.

---

### `test_closes_on_escape_key`

```python
def test_closes_on_escape_key(self, page: Page) -> None:
    page.keyboard.press("Escape")
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

**Playwright concept:** `page.keyboard` simulates keys — expected UX pattern for modals.

---

### `test_closes_on_overlay_background_click`

```python
def test_closes_on_overlay_background_click(self, page: Page) -> None:
    page.get_by_test_id("modal-overlay").click(position={"x": 5, "y": 5})
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

| Concept | Detail |
|---------|--------|
| `position={"x": 5, "y": 5}` | Clicks top-left corner of overlay (outside central content) |

Simulates "click outside" to close modal.

---

### `test_aria_hidden_is_set_correctly_when_closed`

```python
def test_aria_hidden_is_set_correctly_when_closed(self, page: Page) -> None:
    page.get_by_test_id("modal-cancel-btn").click()
    expect(page.get_by_test_id("modal-overlay")).to_have_attribute("aria-hidden", "true")
```

**Then:** After closing, overlay marked as hidden for screen readers.

---

## Class `TestTabs`

```python
@pytest.mark.regression
class TestTabs:
```

Tests for the tab component (tablist/tab/tabpanel).

---

### `test_overview_tab_is_active_by_default`

```python
def test_overview_tab_is_active_by_default(self, page: Page) -> None:
    expect(page.get_by_test_id("tab-overview")).to_have_attribute("aria-selected", "true")
    expect(page.get_by_test_id("tab-panel-overview")).to_be_visible()
```

Initial state: Overview tab selected and panel visible.

---

### `test_clicking_cypress_tab_activates_it_and_shows_its_panel`

```python
def test_clicking_cypress_tab_activates_it_and_shows_its_panel(self, page: Page) -> None:
    page.get_by_test_id("tab-cypress").click()
    expect(page.get_by_test_id("tab-cypress")).to_have_attribute("aria-selected", "true")
    expect(page.get_by_test_id("tab-panel-cypress")).to_be_visible()
    expect(page.get_by_test_id("tab-panel-overview")).not_to_be_visible()
```

| **When** | Clicks Cypress tab |
| **Then** | Tab active + Cypress panel visible + Overview panel hidden |

---

### `test_clicking_playwright_tab_activates_it_and_shows_its_panel`

```python
def test_clicking_playwright_tab_activates_it_and_shows_its_panel(self, page: Page) -> None:
    page.get_by_test_id("tab-playwright").click()
    expect(page.get_by_test_id("tab-playwright")).to_have_attribute("aria-selected", "true")
    expect(page.get_by_test_id("tab-panel-playwright")).to_be_visible()
```

Same pattern for Playwright tab.

---

### `test_only_one_tab_panel_is_visible_at_a_time`

```python
def test_only_one_tab_panel_is_visible_at_a_time(self, page: Page) -> None:
    page.get_by_test_id("tab-cypress").click()
    expect(page.locator(".tab-panel.active")).to_have_count(1)
```

**Then:** Exactly one panel with class `active` — exclusive visibility.

---

### `test_tabs_have_correct_role_attributes`

```python
def test_tabs_have_correct_role_attributes(self, page: Page) -> None:
    expect(page.locator('[role="tablist"]')).to_be_attached()
    expect(page.locator('[role="tab"]')).to_have_count(3)
    expect(page.locator('[role="tabpanel"]')).to_have_count(3)
```

Validates ARIA structure: 1 tablist, 3 tabs, 3 tabpanels.

---

### `test_supports_keyboard_focus_on_tab_controls`

```python
def test_supports_keyboard_focus_on_tab_controls(self, page: Page) -> None:
    expect(page.get_by_test_id("tab-overview")).to_have_attribute("aria-selected", "true")
    tab = page.get_by_test_id("tab-cypress")
    tab.focus()
    expect(tab).to_be_focused()
    tab.click()
    expect(page.get_by_test_id("tab-panel-cypress")).to_be_visible()
```

| Step | Description |
|------|-------------|
| **When** | Focuses tab via keyboard/programmatic call |
| **Then** | Element focused |
| **When** | Activates tab |
| **Then** | Corresponding panel visible |

**Concept:** `locator.focus()` + `to_be_focused()` test accessible navigation.

---

## Class `TestAccordion`

```python
@pytest.mark.regression
class TestAccordion:
```

Tests for expandable panels (accordion).

---

### `test_all_panels_are_collapsed_by_default`

```python
def test_all_panels_are_collapsed_by_default(self, page: Page) -> None:
    for n in (1, 2, 3):
        expect(page.get_by_test_id(f"accordion-trigger-{n}")).to_have_attribute(
            "aria-expanded", "false"
        )
        expect(page.get_by_test_id(f"accordion-panel-{n}")).not_to_be_visible()
```

**Then:** Three panels collapsed (`aria-expanded="false"`, content hidden).

---

### `test_expands_first_panel_on_click`

```python
def test_expands_first_panel_on_click(self, page: Page) -> None:
    page.get_by_test_id("accordion-trigger-1").click()
    expect(page.get_by_test_id("accordion-trigger-1")).to_have_attribute("aria-expanded", "true")
    expect(page.get_by_test_id("accordion-panel-1")).to_be_visible()
```

| **When** | Clicks panel 1 trigger |
| **Then** | Expanded and visible |

---

### `test_collapses_first_panel_on_second_click`

```python
def test_collapses_first_panel_on_second_click(self, page: Page) -> None:
    trigger = page.get_by_test_id("accordion-trigger-1")
    trigger.click()
    trigger.click()
    expect(page.get_by_test_id("accordion-panel-1")).not_to_be_visible()
```

Toggle behavior — second click collapses.

---

### `test_multiple_panels_can_be_open_simultaneously`

```python
def test_multiple_panels_can_be_open_simultaneously(self, page: Page) -> None:
    page.get_by_test_id("accordion-trigger-1").click()
    page.get_by_test_id("accordion-trigger-2").click()
    expect(page.get_by_test_id("accordion-panel-1")).to_be_visible()
    expect(page.get_by_test_id("accordion-panel-2")).to_be_visible()
```

This accordion allows **multiple panels open** (not exclusive like tabs).

---

## Class `TestComponentsAccessibility`

```python
@pytest.mark.regression
@pytest.mark.a11y
class TestComponentsAccessibility:
```

---

### `test_components_page_has_no_critical_a11y_violations`

```python
def test_components_page_has_no_critical_a11y_violations(self, page: Page) -> None:
    check_a11y(page)
```

Axe scan on the entire Components page (`color-contrast` rule disabled by default in `check_a11y`).

---

### `test_modal_dialog_passes_a11y_when_open`

```python
def test_modal_dialog_passes_a11y_when_open(self, page: Page) -> None:
    page.get_by_test_id("open-modal-btn").click()
    expect(page.get_by_test_id("modal-overlay")).to_be_visible()
    check_a11y(page)
```

| **Given** | Modal open |
| **Then** | No critical/serious violations with modal visible |

Tests accessibility in interactive state — open modals often introduce problems.

---

## Summary of concepts learned

| Concept | Where it appears |
|---------|------------------|
| Direct locators | `get_by_test_id`, `locator`, CSS/ARIA selectors |
| Mock Clock | `page.clock.install()` + `fast_forward()` |
| Parametrization + TC IDs | `@pytest.mark.parametrize` with `TC`/`tc` |
| Native dialogs | `page.on("dialog")`, `accept()`, `dismiss()` |
| Class fixture | `open_modal` inside `TestModal` |
| Keyboard | `page.keyboard.press("Escape")`, `focus()` |
| Positioned click | `click(position={...})` |
| ARIA | `role`, `aria-selected`, `aria-expanded`, `aria-modal` |
| Accessibility | `check_a11y` with `@pytest.mark.a11y` |
