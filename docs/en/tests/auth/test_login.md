# Login Tests (Authentication)

**Source file:** [`../../../../tests/auth/test_login.py`](../../../../tests/auth/test_login.py)

---

## Purpose

This file covers **all scenarios on the login page** (`/web/login.html`):

- Form structure and attributes
- Login with valid credentials (UI, API toggle, Enter key)
- Session persistence in `sessionStorage`
- Invalid credentials and error messages
- HTML5 validation of required fields
- "Remember me" checkbox
- Redirect from protected pages
- Logout after login
- Accessibility (a11y) with axe-core

This is the **authentication regression** suite — it complements navigation smoke tests with more granular scenarios.

---

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| Local server | `BASE_URL` accessible (default: `http://localhost:5050`). |
| Demo credentials | `DEMO_EMAIL` / `DEMO_PASSWORD` in `support/config.py`. |
| JSON fixture | `fixtures/credentials.json` with valid/invalid credential pairs. |
| Page Object | `LoginPage` class in `pages/login_page.py`. |
| Playwright + PyTest | Test environment configured. |

**Indirect dependencies:**

- `conftest.py` — `page` fixture and `check_a11y` function.
- `support/helpers/fixtures.py` — reader for JSON test data files.

---

## Markers used

```python
pytestmark = pytest.mark.regression
```

This line applies `@pytest.mark.regression` to the **entire module** — all tests in this file are regression by default.

| Marker | Where | Meaning |
|--------|-------|---------|
| `regression` | Entire module (`pytestmark`) | Full regression suite. |
| `smoke` | `TestValidCredentials.test_tc0101_...` | Critical smoke subset. |
| `critical` | `TestValidCredentials.test_tc0101_...` | Critical path — successful login. |
| `a11y` | `TestAccessibility` class | Accessibility tests. |

**Run examples:**

```bash
pytest tests/auth/test_login.py -m regression
pytest tests/auth/test_login.py -m "critical"
pytest tests/auth/test_login.py -m a11y
```

---

## PyTest and Playwright concepts used in this file

### Page Object Model (POM)

The `LoginPage` class encapsulates selectors and actions for the login page. Tests call semantic methods (`login_with`, `should_show_error`) instead of repeating CSS selectors.

### `pytestmark`

Module-level assignment equivalent to decorating each test with the same marker — avoids repeating `@pytest.mark.regression` dozens of times.

### `autouse` fixture

The `visit_login` fixture navigates to the login page **before each test**, ensuring a consistent initial state.

### `page.expect_request()`

Context manager that **captures HTTP requests** triggered by the page during an action. Used to verify that login via the API toggle makes `POST /api/auth/login`.

### `page.evaluate()`

Executes JavaScript in the browser — here to read and parse `sessionStorage`.

### `Locator.press("Enter")`

Simulates the Enter key on a field — tests form submission via keyboard.

### `check_a11y(page)`

Helper from `conftest.py` that runs axe-core via `axe_playwright_python` and fails if there are critical/serious WCAG 2.x violations.

---

## Imports — line by line

```python
import re
```

Regular expressions for validating URLs (`to_have_url(re.compile(...))`).

```python
import pytest
```

Test framework and decorators.

```python
from playwright.sync_api import Page, expect
```

- `Page` — browser tab.
- `expect` — assertions with auto-retry.

```python
from conftest import check_a11y
```

Imports the accessibility helper function defined at the project root. PyTest resolves `conftest.py` automatically for fixtures, but helper functions must be imported explicitly.

```python
from pages.login_page import LoginPage
```

Page Object for the login screen.

```python
from support.config import DEMO_EMAIL, DEMO_PASSWORD
```

Default credentials for the demo account.

```python
from support.helpers.fixtures import read_fixture
```

Utility to load JSON from `fixtures/` as a Python dict.

---

## Module configuration

```python
pytestmark = pytest.mark.regression
```

**Effect:** marks **all** tests in this file as `regression`. Appears in the report as `@pytest.mark.regression` on each test.

**PyTest concept:** `pytestmark` can be a single marker or a list: `pytestmark = [pytest.mark.regression, pytest.mark.slow]`.

```python
credentials = read_fixture("credentials.json")
```

Loads test data from `fixtures/credentials.json`:

```json
{
  "valid": { "email": "demo@automation.io", "password": "Demo123!" },
  "invalid": { "email": "wrong@email.com", "password": "wrongpassword" },
  "emptyEmail": { "email": "", "password": "Demo123!" }
}
```

**Why use a JSON fixture?** Separates **data** from **test logic**. Invalid credentials stay centralized and reusable.

---

## `visit_login` fixture

```python
@pytest.fixture(autouse=True)
def visit_login(page: Page) -> None:
    LoginPage(page).visit()
```

| Aspect | Detail |
|--------|--------|
| `autouse=True` | Runs automatically before **each** test in the module |
| Dependency | Receives `page` from the global pytest-playwright fixture |
| Action | `LoginPage(page).visit()` → `page.goto("/web/login.html")` |

**Implicit Given:** every test starts on the login page, without needing to call `visit()` manually.

**Practical exception:** `TestRedirectAfterLogin.test_redirects_to_login_when_accessing_a_protected_page_unauthenticated` calls `page.goto("/web/team.html")` **after** setup, overriding the initial navigation — a valid pattern for testing redirects.

---

## `LoginPage` Page Object — quick reference

Tests delegate interactions to the class in `pages/login_page.py`. Methods used in this file:

| Method | What it does |
|--------|--------------|
| `visit()` | Navigates to `/web/login.html` |
| `email_input()` | Locator `[data-testid="login-email"]` |
| `password_input()` | Locator `[data-testid="login-password"]` |
| `submit_btn()` | Submit button |
| `remember_checkbox()` | "Remember me" checkbox |
| `use_api_checkbox()` | "Use API" toggle |
| `result_msg()` | Result/error message |
| `fill_email()` / `fill_password()` | Fills fields (with `clear` first) |
| `submit()` | Clicks the submit button |
| `login_with(email, password)` | Full flow: fill + submit |
| `toggle_use_api()` | Enables login via API (click via JS) |
| `toggle_remember_me()` | Toggles remember checkbox |
| `should_show_error(text)` | Assert error message visible |
| `should_redirect_to_dashboard()` | Assert dashboard visible + correct URL |

**Fluent pattern:** methods return `Self` (`return self`) for optional chaining.

---

## `TestPageStructure` class

Validates that the login form renders correctly.

### `test_tc0100_renders_all_form_elements`

```python
def test_tc0100_renders_all_form_elements(self, page: Page) -> None:
    login = LoginPage(page)
    expect(login.email_input()).to_be_visible()
    expect(login.password_input()).to_be_visible()
    expect(login.submit_btn()).to_be_visible()
    expect(login.submit_btn()).to_be_enabled()
    expect(login.remember_checkbox()).to_be_attached()
    expect(login.use_api_checkbox()).to_be_attached()
```

| Assertion | Meaning |
|-----------|---------|
| `to_be_visible()` | Element visible on screen |
| `to_be_enabled()` | Button is not disabled |
| `to_be_attached()` | Element exists in the DOM (may be hidden) — used for checkboxes |

- **Given:** login page open (`visit_login` fixture).
- **Then:** all essential controls exist and submit is enabled.

### `test_has_correct_placeholder_text_on_email_field`

```python
expect(LoginPage(page).email_input()).to_have_attribute(
    "placeholder", "demo@automation.io"
)
```

- **Then:** email placeholder guides the user with the expected demo email.

### `test_password_field_masks_input`

```python
expect(LoginPage(page).password_input()).to_have_attribute("type", "password")
```

- **Then:** password field uses `type="password"` — characters are masked.

---

## `TestValidCredentials` class

**Successful login** scenarios.

```python
@pytest.mark.smoke
@pytest.mark.critical
class TestValidCredentials:
```

Additional markers override/complement the module's `pytestmark` for critical smoke tests.

### `test_tc0101_logs_in_via_ui_and_redirects_to_dashboard`

```python
def test_tc0101_logs_in_via_ui_and_redirects_to_dashboard(self, page: Page) -> None:
    login = LoginPage(page)
    login.login_with(DEMO_EMAIL, DEMO_PASSWORD)
    login.should_redirect_to_dashboard()
```

| Step | Given/When/Then |
|------|-----------------|
| Setup | **Given** empty login form |
| `login_with(...)` | **When** fills valid credentials and submits |
| `should_redirect_to_dashboard()` | **Then** dashboard visible and URL `/web/dashboard.html` |

**Critical case TC-0101** — main happy path for UI authentication.

### `test_logs_in_with_api_toggle_enabled`

```python
def test_logs_in_with_api_toggle_enabled(self, page: Page) -> None:
    login = LoginPage(page)
    with page.expect_request(
        lambda req: "/api/auth/login" in req.url and req.method == "POST"
    ) as request_info:
        login.toggle_use_api()
        login.login_with(DEMO_EMAIL, DEMO_PASSWORD)

    response = request_info.value.response()
    assert response is not None
    assert response.status == 200
    login.should_redirect_to_dashboard()
```

**Playwright concept — `page.expect_request()`:**

1. Opens a "listener" **before** the action.
2. The lambda filters requests: URL contains `/api/auth/login` and method POST.
3. Inside the `with`, runs API toggle + login.
4. `request_info.value` returns the captured `Request`.
5. `.response()` gets the associated HTTP `Response`.

- **When:** user enables "Use API" and logs in.
- **Then:** POST request was made, returned 200, and redirected to the dashboard.

### `test_sets_auth_data_in_session_storage_after_login`

```python
LoginPage(page).login_with(DEMO_EMAIL, DEMO_PASSWORD)
auth = page.evaluate(
    """() => {
        const raw = sessionStorage.getItem('sandbox-auth');
        return raw ? JSON.parse(raw) : null;
    }"""
)
assert auth is not None
assert auth["email"] == DEMO_EMAIL
```

- **When:** successful login.
- **Then:** `sessionStorage['sandbox-auth']` contains a JSON object with the correct email.

**Concept:** `page.evaluate()` with a no-argument JS function — return value serialized to Python.

### `test_shows_success_message_before_redirect`

```python
login.login_with(DEMO_EMAIL, DEMO_PASSWORD)

result = page.get_by_test_id("login-result")
if result.is_visible():
    expect(result).to_contain_text("Login successful")
login.should_redirect_to_dashboard()
```

**Defensive test:** the success message may appear briefly before redirect. Uses `is_visible()` to check conditionally — avoids failure if redirect is instant.

### `test_submits_login_form_with_enter_key`

```python
login.fill_email(DEMO_EMAIL)
login.fill_password(DEMO_PASSWORD)
login.password_input().press("Enter")
login.should_redirect_to_dashboard()
```

- **When:** submits form by pressing Enter in the password field.
- **Then:** login works the same as clicking the button.

**Playwright concept:** `Locator.press(key)` simulates keyboard events.

---

## `TestInvalidCredentials` class

**Authentication failure** scenarios.

### `test_shows_error_for_wrong_password`

```python
login.login_with(credentials["valid"]["email"], credentials["invalid"]["password"])
login.should_show_error("Invalid credentials")
```

- **Given:** valid email, wrong password (from `credentials.json`).
- **Then:** "Invalid credentials" message visible.

### `test_shows_error_for_unknown_email`

```python
login.login_with(credentials["invalid"]["email"], credentials["valid"]["password"])
login.should_show_error("Invalid credentials")
```

- **Given:** nonexistent email, correct password.
- **Then:** same generic message (good security practice — does not reveal whether the email exists).

### `test_does_not_navigate_away_on_failed_login`

```python
LoginPage(page).login_with(
    credentials["invalid"]["email"], credentials["invalid"]["password"]
)
expect(page).to_have_url(re.compile(r"/web/login\.html"))
```

- **Then:** URL stays at `/web/login.html` — user does not advance with invalid credentials.

---

## `TestFormValidation` class

### `test_requires_email_to_not_be_empty_html5_validation`

```python
login.fill_password(DEMO_PASSWORD)
login.submit()
is_valid = login.email_input().evaluate("el => el.validity.valid")
assert is_valid is False
```

- **Given:** empty email, password filled.
- **When:** attempts to submit.
- **Then:** native HTML5 validation (`constraint validation API`) reports email as invalid.

**Concept:** `element.validity.valid` is the browser's native API — tests client-side validation without relying on custom messages.

---

## `TestRememberMe` class

### `test_checkbox_can_be_checked_and_unchecked`

```python
expect(login.remember_checkbox()).not_to_be_checked()
login.toggle_remember_me()
expect(login.remember_checkbox()).to_be_checked()
login.toggle_remember_me()
expect(login.remember_checkbox()).not_to_be_checked()
```

- **Then:** checkbox toggles between checked and unchecked correctly.

Playwright assertions for checkboxes: `to_be_checked()` / `not_to_be_checked()`.

---

## `TestRedirectAfterLogin` class

### `test_redirects_to_login_when_accessing_a_protected_page_unauthenticated`

```python
page.goto("/web/team.html")
expect(page).to_have_url(re.compile(r"/web/login\.html"))

LoginPage(page).login_with(DEMO_EMAIL, DEMO_PASSWORD)
expect(page).not_to_have_url(re.compile(r"/web/login\.html"))
```

| Phase | Given/When/Then |
|-------|-----------------|
| 1 | **When** accesses `/web/team.html` without auth → **Then** redirects to login |
| 2 | **When** logs in → **Then** leaves the login page (goes to protected destination) |

**Note:** this test depends on the application's **route guard** behavior — protected pages require authentication.

---

## `TestLogout` class

### `test_clears_session_and_redirects_to_home_after_logout`

```python
login.login_with(DEMO_EMAIL, DEMO_PASSWORD)
login.should_redirect_to_dashboard()

page.get_by_test_id("nav-logout").click()
expect(page).to_have_url(re.compile(r"/web/index\.html"))
assert page.evaluate("() => sessionStorage.getItem('sandbox-auth')") is None
```

Complete flow:

1. **Given/When:** login via UI → dashboard.
2. **When:** clicks logout.
3. **Then:** public home + session cleared.

Mirrors `test_tc0012` in `test_navigation.py`, but uses Page Object instead of inline selectors.

---

## `TestAccessibility` class

```python
@pytest.mark.a11y
@pytest.mark.regression
class TestAccessibility:
```

Explicit class markers — `a11y` allows filtering: `pytest -m a11y`.

### `test_login_page_has_no_critical_a11y_violations`

```python
def test_login_page_has_no_critical_a11y_violations(self, page: Page) -> None:
    check_a11y(page)
```

**What `check_a11y` does** (in `conftest.py`):

1. Instantiates `Axe()` from the `axe_playwright_python` package.
2. Runs scan with WCAG 2.0/2.1 level A and AA tags.
3. Ignores the `color-contrast` rule (disabled by default — can produce false positives in demo themes).
4. Filters violations with `critical` or `serious` impact.
5. Fails the test listing violated rule IDs.

- **Given:** login page rendered.
- **Then:** no critical/serious a11y violations.

---

## Class mental map

```
test_login.py
├── TestPageStructure      → does the form UI exist?
├── TestValidCredentials   → login OK (UI, API, storage, Enter)
├── TestInvalidCredentials → wrong credentials
├── TestFormValidation     → HTML5 required
├── TestRememberMe         → checkbox works
├── TestRedirectAfterLogin → route guard
├── TestLogout             → ends session
└── TestAccessibility      → axe-core WCAG
```

---

## Summary for new learners

| Pattern | Example in this file |
|---------|---------------------|
| Page Object | `LoginPage(page).login_with(...)` |
| External data | `read_fixture("credentials.json")` |
| Automatic setup | `@pytest.fixture(autouse=True) visit_login` |
| Module marker | `pytestmark = pytest.mark.regression` |
| Intercept HTTP | `page.expect_request(lambda req: ...)` |
| Read browser state | `page.evaluate("() => sessionStorage...")` |
| Native validation | `.evaluate("el => el.validity.valid")` |
| A11y | `check_a11y(page)` + `@pytest.mark.a11y` |

**Suggested command:**

```bash
pytest tests/auth/test_login.py::TestValidCredentials -v --headed
```

Start with the `TestValidCredentials` class — it contains the most important happy path before exploring error cases.
