# Settings Page Tests

**Source file:** [`../../../../tests/settings/test_settings.py`](../../../../tests/settings/test_settings.py)

---

## Purpose

This module validates the **Settings** page (`/web/settings.html`) in the TestFlow sandbox. The tests cover:

- **Profile** section (name, email, timezone, avatar upload)
- **Notifications** section (toggle, volume slider, weekly digest, date)
- **Security** section (password change, 2FA, active sessions)
- **Integrations** section (API token, webhook)
- **Danger zone** (account deletion with native dialog)
- **Accessibility** (axe-core via Playwright)

The pattern used is **Page Object Model (POM)**: reusable interactions and assertions live in `SettingsPage`, while the tests describe business behaviors.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Environment | TestFlow server running (base URL configured in `support/config.py`) |
| Authentication | Session fixture `cache_auth_token` in `conftest.py` obtains a token via API |
| Dependencies | `pytest`, `playwright`, `axe-playwright-python` |
| Page Object | [`pages/settings_page.py`](../../../../pages/settings_page.py) |
| Demo user | Default credentials (`DEMO_EMAIL` / `DEMO_PASSWORD`) |

To run this file only:

```bash
pytest tests/settings/test_settings.py -v
```

To filter by marker:

```bash
pytest tests/settings/test_settings.py -m smoke
pytest tests/settings/test_settings.py -m critical
pytest tests/settings/test_settings.py -m a11y
```

---

## Markers used

| Marker | Where it appears | Meaning |
|--------|------------------|---------|
| `regression` | `pytestmark` (entire module) | Regression suite — all tests inherit this marker |
| `smoke` | `test_saves_profile_and_shows_success_message` | Smoke test — fast critical path |
| `critical` | `test_saves_profile_and_shows_success_message` | Critical business path |
| `a11y` | `TestAccessibility` class | Accessibility tests (WCAG 2.x) |

Markers are registered in `conftest.py` via `pytest_configure`.

---

## Structure overview

```
test_settings.py
├── Imports
├── pytestmark (regression)
├── Fixture autouse: setup_settings
├── TestProfileSection
├── TestNotificationsSection
├── TestSecurityPasswordChange
├── TestSecurity2FA
├── TestSecurityActiveSessions
├── TestIntegrationsApiToken
├── TestIntegrationsWebhook
├── TestDangerZone
└── TestAccessibility
```

---

## Imports — block by block

### `import re`

Python standard library for **regular expressions**. Used to validate attributes that contain partial patterns (e.g., file input `accept` with `.png`, CSS class `btn-danger`).

**PyTest/Playwright concept:** `expect(...).to_have_attribute("accept", re.compile(r"\.png"))` accepts any value that **contains** `.png`, without requiring an exact match.

---

### `import pytest`

Test framework. Provides:

- **Fixtures** (`@pytest.fixture`)
- **Markers** (`@pytest.mark.smoke`)
- **Test classes** (logical grouping)
- Automatic test discovery (`test_*.py`)

---

### `from playwright.sync_api import APIRequestContext, Page, expect`

| Symbol | Role |
|--------|------|
| `Page` | Represents a browser tab — UI interactions (click, fill, goto) |
| `APIRequestContext` | Playwright HTTP client for REST calls without UI |
| `expect` | Assertion API with **auto-retry** — re-evaluates until timeout if the element is not yet in the expected state |

**Playwright concept:** `expect(locator).to_be_visible()` is preferable to `assert locator.is_visible()` because it waits for DOM stabilization.

---

### `from conftest import check_a11y`

Global helper that runs **axe-core** on the page and fails if there are `critical` or `serious` violations (with optional disabled rules).

---

### `from pages.settings_page import SettingsPage`

**Page Object** that encapsulates locators (`get_by_test_id`) and actions (`fill_name`, `save_profile`) for the Settings page.

---

### `from support.auth import visit_authenticated`

Helper that:

1. Obtains a token via API (`fetch_auth_token`)
2. Injects the session into the browser's `sessionStorage`
3. Navigates authenticated to the given `path`

Avoids repeating manual login in each test.

---

## Constants and module configuration

### `pytestmark = pytest.mark.regression`

Assigns the `regression` marker to **all** tests in the file without repeating `@pytest.mark.regression` on each method.

**PyTest concept:** `pytestmark` is a module convention equivalent to decorating each test individually.

---

## Fixture: `setup_settings`

```python
@pytest.fixture(autouse=True)
def setup_settings(page: Page, api_request: APIRequestContext) -> None:
    visit_authenticated(page, api_request, "/web/settings.html")
    expect(SettingsPage(page).page_root()).to_be_visible()
```

| Aspect | Explanation |
|--------|-------------|
| `autouse=True` | Runs **before each test** automatically, without needing to declare it as a parameter |
| `page` | `pytest-playwright` fixture — browser already open |
| `api_request` | `conftest.py` fixture — HTTP context for API login |
| `visit_authenticated(...)` | Given: authenticated user on the Settings page |
| `expect(...page_root()).to_be_visible()` | Then: confirms the page loaded (`data-testid="page-settings"`) |

**Implicit Given/When/Then:** Every test starts with the Settings page visible and authenticated.

---

## Class `TestProfileSection`

Groups tests for the **Profile** section of the settings form.

---

### `test_shows_pre_filled_values_for_name_and_email`

```python
def test_shows_pre_filled_values_for_name_and_email(self, page: Page) -> None:
    settings = SettingsPage(page)
    expect(settings.name_input()).to_have_value("Demo User")
    expect(settings.email_input()).to_have_value("demo@automation.io")
```

| Step | Description |
|------|-------------|
| **Given** | Settings page loaded (autouse fixture) |
| **When** | Instantiates `SettingsPage` and locates inputs |
| **Then** | Name and email display pre-filled demo user values |

**Playwright concept:** `to_have_value()` checks the `value` attribute of inputs — equivalent to what the user sees in the field.

---

### `test_saves_profile_and_shows_success_message`

```python
@pytest.mark.smoke
@pytest.mark.critical
def test_saves_profile_and_shows_success_message(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.fill_name("Demo User Updated")
    settings.save_profile()
    settings.should_show_save_success()
```

| Step | Description |
|------|-------------|
| **Given** | Profile with original name |
| **When** | Fills new name and clicks save |
| **Then** | Success message visible (via `should_show_save_success()`) |

**Markers:** `smoke` + `critical` — one of the most important tests in the Settings suite.

**POM:** `fill_name` clears and fills; `save_profile` clicks the button; `should_show_save_success` encapsulates assertions on `#form-result`.

---

### `test_shows_a_toast_on_save`

```python
def test_shows_a_toast_on_save(self, page: Page) -> None:
    SettingsPage(page).save_profile()
    expect(page.get_by_test_id("toast-message")).to_contain_text("saved")
```

| Step | Description |
|------|-------------|
| **When** | Saves profile without changing fields |
| **Then** | Global toast contains text `"saved"` |

Tests transient feedback (toast notification), not just the inline form result.

---

### `test_allows_changing_the_timezone_select`

```python
def test_allows_changing_the_timezone_select(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.timezone_select().select_option("brt")
    expect(settings.timezone_select()).to_have_value("brt")
```

| Step | Description |
|------|-------------|
| **When** | Selects option `"brt"` in the timezone `<select>` |
| **Then** | Selected value persists as `"brt"` |

**Playwright concept:** `select_option()` works on native `<select>` elements.

---

### `test_avatar_upload_input_accepts_image_files`

```python
def test_avatar_upload_input_accepts_image_files(self, page: Page) -> None:
    expect(SettingsPage(page).file_upload()).to_have_attribute("accept", re.compile(r"\.png"))
```

| Step | Description |
|------|-------------|
| **Then** | Upload input has an `accept` attribute containing `.png` |

HTML contract validation — restricts accepted file types.

---

## Class `TestNotificationsSection`

Tests for the **Notifications** section.

---

### `test_push_notifications_start_as_off`

```python
def test_push_notifications_start_as_off(self, page: Page) -> None:
    SettingsPage(page).should_show_notifications_off()
```

**Then:** Notifications switch starts off (`Off`, `aria-checked="false"`).

---

### `test_toggles_notifications_on`

```python
def test_toggles_notifications_on(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_notifications()
    settings.should_show_notifications_on()
```

| Step | Description |
|------|-------------|
| **When** | Clicks the notifications switch |
| **Then** | Status `"On"` and `aria-checked="true"` |

---

### `test_toggles_notifications_back_off`

```python
def test_toggles_notifications_back_off(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_notifications()
    settings.toggle_notifications()
    settings.should_show_notifications_off()
```

Tests **bidirectional toggle**: on → off → initial state restored.

---

### `test_volume_slider_updates_the_displayed_value`

```python
def test_volume_slider_updates_the_displayed_value(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.set_slider(75)
    expect(settings.volume_value()).to_have_text("75")
```

| Step | Description |
|------|-------------|
| **When** | Sets slider to 75 via JavaScript (`evaluate`) |
| **Then** | Label displays `"75"` |

**Playwright concept:** HTML5 sliders do not always respond well to `.fill()` — `evaluate` manually fires the `input` event.

---

### `test_weekly_digest_checkbox_is_checked_by_default`

```python
def test_weekly_digest_checkbox_is_checked_by_default(self, page: Page) -> None:
    expect(SettingsPage(page).digest_checkbox()).to_be_checked()
```

**Then:** Weekly digest checkbox is checked by default.

---

### `test_digest_start_date_field_is_editable`

```python
def test_digest_start_date_field_is_editable(self, page: Page) -> None:
    date_input = SettingsPage(page).date_input()
    date_input.clear()
    date_input.fill("2025-01-01")
    expect(date_input).to_have_value("2025-01-01")
```

| Step | Description |
|------|-------------|
| **When** | Clears and fills the date field |
| **Then** | Value `"2025-01-01"` persists |

---

## Class `TestSecurityPasswordChange`

Password change tests in the **Security** section.

---

### `test_shows_error_when_both_password_fields_are_empty`

```python
def test_shows_error_when_both_password_fields_are_empty(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.password_save_btn().click()
    settings.should_show_password_error("required")
```

| Step | Description |
|------|-------------|
| **When** | Clicks save without filling passwords |
| **Then** | Error contains `"required"` |

---

### `test_shows_error_when_new_password_is_too_short`

```python
def test_shows_error_when_new_password_is_too_short(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.submit_password_change("Demo123!", "short")
    settings.should_show_password_error("8 characters")
```

Business rule validation: new password with fewer than 8 characters.

---

### `test_shows_success_when_a_valid_new_password_is_provided`

```python
def test_shows_success_when_a_valid_new_password_is_provided(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.submit_password_change("Demo123!", "NewPass123!")
    expect(settings.password_result()).to_contain_text("updated")
```

| Step | Description |
|------|-------------|
| **When** | Submits valid current password + valid new password |
| **Then** | Result contains `"updated"` |

---

### `test_clears_password_fields_after_successful_change`

```python
def test_clears_password_fields_after_successful_change(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.submit_password_change("Demo123!", "NewPass123!")
    expect(settings.current_password()).to_have_value("")
    expect(settings.new_password()).to_have_value("")
```

**Then:** After success, password fields are cleared (good security UX practice).

---

### `test_password_change_request_contains_current_password_and_new_password`

```python
def test_password_change_request_contains_current_password_and_new_password(
    self, page: Page
) -> None:
    settings = SettingsPage(page)
    password_change = None
    try:
        with page.expect_request(
            lambda req: req.method == "POST" and "/api/" in req.url, timeout=3000
        ) as request_info:
            settings.submit_password_change("Demo123!", "NewPass123!")
        password_change = request_info.value
    except Exception:
        pass

    expect(settings.password_result()).to_contain_text("updated")
    if password_change is not None:
        body = password_change.post_data_json
        assert "currentPassword" in body
        assert "newPassword" in body
        assert body["newPassword"] == "NewPass123!"
```

| Aspect | Explanation |
|--------|-------------|
| **Playwright concept** | `page.expect_request()` intercepts network requests during an action |
| **Lambda filter** | Captures only POSTs whose URL contains `/api/` |
| **try/except** | Tolerance if interception fails — UI assertion still runs |
| **Then (UI)** | Success visible on screen |
| **Then (API)** | JSON body contains correct `currentPassword` and `newPassword` |

**Given/When/Then:**

- **Given:** Password form ready
- **When:** Submits change inside `expect_request` context
- **Then:** UI confirms + API payload validated

---

## Class `TestSecurity2FA`

Tests for the **two-factor authentication** toggle.

---

### `test_starts_as_disabled`

```python
def test_starts_as_disabled(self, page: Page) -> None:
    settings = SettingsPage(page)
    expect(settings.twofa_status()).to_have_text("Disabled")
    expect(settings.twofa_switch()).to_have_attribute("aria-checked", "false")
```

Initial state: 2FA disabled.

---

### `test_enables_2fa_on_toggle`

```python
def test_enables_2fa_on_toggle(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_2fa()
    settings.should_show_2fa_enabled()
```

| **When** | Clicks 2FA switch |
| **Then** | Status `"Enabled"`, `aria-checked="true"` |

---

### `test_disables_2fa_on_second_toggle`

```python
def test_disables_2fa_on_second_toggle(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_2fa()
    settings.toggle_2fa()
    expect(settings.twofa_status()).to_have_text("Disabled")
```

Reversible toggle — second click restores disabled state.

---

## Class `TestSecurityActiveSessions`

Tests for the **active sessions** list.

---

### `test_shows_current_session_with_active_badge`

```python
def test_shows_current_session_with_active_badge(self, page: Page) -> None:
    expect(page.get_by_test_id("session-current")).to_be_visible()
    expect(SettingsPage(page).session_badge()).to_contain_text("Active")
```

**Then:** Current session visible with `"Active"` badge.

---

### `test_shows_session_device_name_and_location`

```python
def test_shows_session_device_name_and_location(self, page: Page) -> None:
    expect(page.get_by_test_id("session-name")).not_to_be_empty()
    expect(page.get_by_test_id("session-meta")).to_contain_text("Current session")
```

Validates that session metadata (device name, location) is rendered.

---

## Class `TestIntegrationsApiToken`

**API token** tests in the Integrations section.

---

### `test_displays_the_api_token`

```python
def test_displays_the_api_token(self, page: Page) -> None:
    token = SettingsPage(page).api_key_display()
    expect(token).to_be_visible()
    expect(token).not_to_be_empty()
```

**Then:** Token visible and not empty.

---

### `test_shows_copied_feedback_when_copy_is_clicked`

```python
def test_shows_copied_feedback_when_copy_is_clicked(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.copy_token()
    settings.should_show_token_result("Copied")
```

| **When** | Clicks copy token |
| **Then** | Feedback `"Copied"` |

---

### `test_generates_a_new_token_on_rotate`

```python
def test_generates_a_new_token_on_rotate(self, page: Page) -> None:
    settings = SettingsPage(page)
    original = settings.api_key_display().inner_text()
    settings.rotate_token()
    expect(settings.api_key_display()).not_to_have_text(original)
```

| **When** | Rotates token |
| **Then** | Displayed text differs from original |

---

### `test_shows_toast_after_rotating_token`

```python
def test_shows_toast_after_rotating_token(self, page: Page) -> None:
    SettingsPage(page).rotate_token()
    expect(page.get_by_test_id("toast-message")).to_contain_text("rotated")
```

Toast confirms rotation to the user.

---

### `test_rotate_token_triggers_a_request_and_response_contains_new_token`

```python
def test_rotate_token_triggers_a_request_and_response_contains_new_token(
    self, page: Page
) -> None:
    settings = SettingsPage(page)
    rotate_response = None
    try:
        with page.expect_response(
            lambda res: "/api/" in res.url, timeout=3000
        ) as response_info:
            settings.rotate_token()
        rotate_response = response_info.value
    except Exception:
        pass

    expect(settings.api_key_display()).not_to_be_empty()
    if rotate_response is not None:
        assert rotate_response.status == 200
        body = rotate_response.json()
        assert isinstance(body["token"], str)
        assert len(body["token"]) > 0
```

| Concept | Detail |
|---------|--------|
| `expect_response` | Waits for HTTP response during action |
| Conditional assertions | If intercepted, validates status 200 and JSON with non-empty `token` |

---

## Class `TestIntegrationsWebhook`

**Webhook** configuration tests.

---

### `test_saves_a_valid_webhook_url`

```python
def test_saves_a_valid_webhook_url(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.save_webhook("https://ci.example.com/webhook")
    settings.should_show_webhook_saved()
```

Happy path: valid URL → `"Webhook saved"` message.

---

### `test_shows_error_when_webhook_url_is_empty`

```python
def test_shows_error_when_webhook_url_is_empty(self, page: Page) -> None:
    SettingsPage(page).save_webhook_btn().click()
    expect(page.get_by_test_id("webhook-result")).to_contain_text("Enter a URL")
```

Validation: saving without URL shows error.

---

### `test_shows_toast_on_successful_save`

```python
def test_shows_toast_on_successful_save(self, page: Page) -> None:
    SettingsPage(page).save_webhook("https://ci.example.com/hook")
    expect(page.get_by_test_id("toast-message")).to_contain_text("saved")
```

Toast feedback complements inline result.

---

## Class `TestDangerZone`

**Danger zone** tests (account deletion).

---

### `test_delete_account_button_is_visible`

```python
def test_delete_account_button_is_visible(self, page: Page) -> None:
    btn = SettingsPage(page).delete_account_btn()
    expect(btn).to_be_visible()
    expect(btn).to_have_class(re.compile(r"btn-danger"))
```

**Then:** Button visible with danger CSS class (`btn-danger`).

---

### `test_delete_account_shows_confirmation_dialog`

```python
def test_delete_account_shows_confirmation_dialog(self, page: Page) -> None:
    confirm_called = {"value": False}

    def handle_dialog(dialog) -> None:
        confirm_called["value"] = True
        assert dialog.type == "confirm"
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    SettingsPage(page).delete_account_btn().click()
    assert confirm_called["value"] is True
```

| Concept | Explanation |
|---------|-------------|
| **Native dialogs** | `alert`, `confirm`, `prompt` block automation — Playwright requires a handler |
| `page.on("dialog", ...)` | Registers listener before the click |
| `dialog.dismiss()` | Simulates "Cancel" on confirm |
| `confirm_called` | Mutable dict to verify the handler was invoked |

**Given/When/Then:**

- **Given:** Dialog handler registered
- **When:** Clicks delete account
- **Then:** `confirm` dialog appeared (`confirm_called["value"] is True`)

---

## Class `TestAccessibility`

```python
@pytest.mark.a11y
@pytest.mark.regression
class TestAccessibility:
    def test_settings_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        form = SettingsPage(page).settings_form()
        expect(form).to_be_visible()
        check_a11y(page, disabled_rules=["color-contrast", "label", "select-name"])
```

| Aspect | Detail |
|--------|--------|
| `a11y` marker | Identifies accessibility tests in CI |
| `check_a11y` | Runs axe with WCAG 2a/2aa tags |
| `disabled_rules` | Ignores rules known to be noisy in this sandbox |
| Final assertion | Fails if remaining `critical` or `serious` violations |

**Concept:** Automated accessibility complements functional tests — detects ARIA role, label, contrast issues, etc.

---

## Summary of concepts learned

| Concept | Where it appears |
|---------|------------------|
| Page Object Model | `SettingsPage` in all tests |
| `autouse` fixture | `setup_settings` — shared setup |
| API authentication | `visit_authenticated` |
| Retry assertions | `expect(...)` |
| Network interception | `expect_request`, `expect_response` |
| Native dialogs | `page.on("dialog", ...)` |
| Regex in assertions | `re.compile` with `to_have_attribute` / `to_have_class` |
| Accessibility | `check_a11y` + `@pytest.mark.a11y` |
| Pipeline markers | `smoke`, `critical`, `regression` |
