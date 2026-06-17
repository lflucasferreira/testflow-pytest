# Navigation Tests (Smoke)

**Source file:** [`../../../../tests/smoke/test_navigation.py`](../../../../tests/smoke/test_navigation.py)

---

## Purpose

This file validates the fundamental flows of the TestFlow Sandbox application:

1. **Page loading** — each protected route opens without error when the user is authenticated.
2. **Sidebar navigation** — sidebar menu links lead to the correct page and highlight the active item.
3. **Logout** — ends the session and redirects to the home page.
4. **API health** — REST endpoints respond with the expected HTTP status codes.

This is the main **smoke** suite: if these tests fail, the application is likely unusable.

---

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| Local server | The application must be running at `BASE_URL` (default: `http://localhost:5050`). |
| Demo credentials | `DEMO_EMAIL` and `DEMO_PASSWORD` configured (via environment variables or defaults in `support/config.py`). |
| Playwright | Browser installed (`playwright install`). |
| PyTest | Project dependencies installed (`pip install -e .` or equivalent). |

**Global fixtures** (defined in `conftest.py` at the project root):

- `page` — Playwright `Page` instance (provided by the `pytest-playwright` plugin).
- `api_request` — HTTP `APIRequestContext` for REST calls without opening the browser.
- `auth_token` — JWT token obtained once per test session via `POST /api/auth/login`.

---

## Markers used

| Marker | Where it appears | Meaning |
|--------|------------------|---------|
| `@pytest.mark.smoke` | All classes | Smoke tests — fast execution to validate the basics. |
| `@pytest.mark.regression` | `TestPageNavigation`, `TestSidebarNavigation`, `TestApiHealth` | Part of the full regression suite. |
| `@pytest.mark.critical` | `test_tc0010_...`, `test_tc0021_...` | Critical business paths. |
| `@pytest.mark.api` | `TestApiHealth` class and individual tests | Tests that use only the HTTP API, with no visual interaction. |

To run only these tests:

```bash
pytest tests/smoke/test_navigation.py -m smoke
pytest tests/smoke/test_navigation.py -m "smoke and api"
```

---

## PyTest and Playwright concepts used in this file

### Fixtures

A **fixture** is a function that prepares data or state before a test. PyTest injects fixtures by the **parameter name** in the test signature.

- `scope="module"` — the fixture runs once per **module** (file), not per test.
- `autouse=True` — the fixture runs automatically for each test in the class, without needing to declare it as a parameter.

### `@pytest.mark.parametrize`

Runs the **same test method** multiple times with different argument sets. Each combination becomes a separate test in the report.

### `expect` (Playwright)

Assertions with **auto-retry**: Playwright repeats the check until it passes or the timeout is reached. Preferable to `assert element.is_visible()` because it waits for the UI to stabilize.

```python
expect(page.get_by_test_id("page-dashboard")).to_be_visible()
```

### `page.get_by_test_id()`

Locates elements by the `data-testid` attribute. A stable, recommended strategy for automation.

### `page.evaluate()`

Executes JavaScript in the page context. Used here to inspect `sessionStorage`.

### `APIRequestContext`

Playwright's HTTP client for testing APIs directly, sharing the same `base_url` configured in the project.

---

## Imports — line by line

```python
import re
```

Imports the **regular expressions** module. Used in assertions such as `to_have_title(re.compile(title))` and `to_have_url(re.compile(r"/web/team\.html"))`, allowing partial/flexible string matching.

```python
import pytest
```

Test framework. Provides decorators (`@pytest.fixture`, `@pytest.mark.parametrize`, `@pytest.mark.smoke`), automatic test discovery, and fixture injection.

```python
from playwright.sync_api import APIRequestContext, Page, expect
```

| Symbol | Role |
|--------|------|
| `Page` | Represents a browser tab; used to navigate, click, and locate elements. |
| `APIRequestContext` | HTTP client for REST requests (`get`, `post`, etc.). |
| `expect` | Playwright assertion API with implicit waiting. |

```python
from support.auth import get_auth_token, login_via_api, visit_with_token
```

Reusable authentication functions:

- `get_auth_token(api_request)` — returns JWT (from session cache or via API login).
- `login_via_api(page, api_request)` — authenticates via API, injects token into `sessionStorage`, and navigates to the dashboard.
- `visit_with_token(page, path, token)` — visits a protected route with a token already available.

```python
from support.config import DEMO_EMAIL, DEMO_PASSWORD
```

Default credentials for the demo account (`demo@automation.io` / `Demo123!`), configurable via environment variables.

```python
from support.constants.test_cases import TC, tc
```

- `TC` — class with test case IDs (e.g. `TC.SMOKE_DASHBOARD = "TC-0001"`).
- `tc(case_id, title)` — formats a readable ID for the PyTest report: `"[TC-0001] Dashboard page loads without error"`.

---

## `PAGES` constant

```python
PAGES = [
    {
        "path": "/web/dashboard.html",
        "test_id": "page-dashboard",
        "title": "Dashboard",
        "tc_id": TC.SMOKE_DASHBOARD,
    },
    # ... 7 more entries ...
]
```

List of dictionaries describing **each page** to validate in the loading smoke test.

| Field | Purpose |
|-------|---------|
| `path` | Relative URL to visit after authentication. |
| `test_id` | `data-testid` of the page root container — confirms the page rendered. |
| `title` | Expected text in the document `<title>` (partial match via regex). |
| `tc_id` | Test case ID for traceability. |

**Pages covered:** Dashboard, Team, Settings, Components, Activity, Advanced, Wizard, UI States.

Centralizing data in a list avoids duplicating eight nearly identical test methods — `@pytest.mark.parametrize` iterates over this structure.

---

## `navigation_auth_token` fixture

```python
@pytest.fixture(scope="module")
def navigation_auth_token(auth_token: str) -> str:
    return auth_token
```

**Purpose:** expose the test session authentication token to the `TestPageNavigation` class, with module scope.

**How it works:**

1. Depends on the global `auth_token` fixture (defined in `conftest.py`).
2. `auth_token` in turn comes from `cache_auth_token`, which logs in via the API **once per session** and caches the token.
3. `scope="module"` ensures the token is reused by all parametrized tests in the class, without a new login on each iteration.

**PyTest concept:** fixture chaining — a fixture can depend on another by parameter name.

---

## `TestPageNavigation` class

```python
@pytest.mark.smoke
@pytest.mark.regression
class TestPageNavigation:
```

Groups **page loading** tests. Class-level markers apply to all methods inside it (unless overridden).

### `test_page_loads_without_error` method

```python
@pytest.mark.parametrize(
    "path,test_id,title,tc_id",
    [(p["path"], p["test_id"], p["title"], p["tc_id"]) for p in PAGES],
    ids=[tc(p["tc_id"], f"{p['title']} page loads without error") for p in PAGES],
)
def test_page_loads_without_error(
    self,
    page: Page,
    navigation_auth_token: str,
    path: str,
    test_id: str,
    title: str,
    tc_id: str,
) -> None:
```

**Parametrize explained:**

- **First argument:** names of parameters to be injected.
- **Second argument:** list of tuples — one tuple per test run (8 runs, one per page).
- **`ids`:** readable labels in the PyTest report, e.g. `[TC-0001] Dashboard page loads without error`.

**Injected parameters:**

| Parameter | Source |
|-----------|--------|
| `page` | pytest-playwright fixture |
| `navigation_auth_token` | local fixture in this module |
| `path`, `test_id`, `title`, `tc_id` | values from the `PAGES` list via parametrize |

**Test body — block by block:**

```python
visit_with_token(page, path, navigation_auth_token)
```

- **Given:** user authenticated with a valid JWT token.
- **When:** navigates to `path` with session injected into `sessionStorage`.
- `visit_with_token` injects auth via `add_init_script`, passes through `/web/login.html`, and opens the desired route.

```python
expect(page.get_by_test_id(test_id)).to_be_visible()
```

- **Then:** the page root element (e.g. `page-dashboard`) is visible — the page loaded successfully.

```python
expect(page).to_have_title(re.compile(title))
```

- **Then:** the tab title contains the expected text (e.g. `"Dashboard"`). `re.compile` allows partial matching without requiring the full title.

---

## `TestSidebarNavigation` class

```python
@pytest.mark.smoke
@pytest.mark.regression
class TestSidebarNavigation:
```

Tests interaction with the sidebar menu after login.

### `setup` fixture (autouse)

```python
@pytest.fixture(autouse=True)
def setup(self, page: Page, api_request: APIRequestContext) -> None:
    login_via_api(page, api_request)
    expect(page.get_by_test_id("page-dashboard")).to_be_visible()
```

**`autouse=True`** — runs **before each test** in this class automatically.

**Flow:**

1. **Given:** `login_via_api` obtains a token, injects it into the browser, and opens the dashboard.
2. **Then (precondition):** confirms the dashboard is visible — guaranteed initial state.

**Concept:** class-level setup fixture, equivalent to Cypress `beforeEach` or JUnit `@BeforeEach`.

### `test_tc0010_navigates_from_dashboard_to_team_via_sidebar`

```python
@pytest.mark.smoke
@pytest.mark.critical
def test_tc0010_navigates_from_dashboard_to_team_via_sidebar(self, page: Page) -> None:
    page.get_by_test_id("nav-team").click()
    expect(page.get_by_test_id("page-team")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/web/team\.html"))
```

| Step | Given/When/Then |
|------|-----------------|
| Setup (fixture) | **Given** user logged in on the dashboard |
| `nav-team.click()` | **When** clicks the Team link in the sidebar |
| `page-team` visible | **Then** the Team page rendered |
| URL contains `/web/team.html` | **Then** the URL changed correctly |

`@pytest.mark.critical` marker — failure here blocks release in pipelines that respect this marker.

### `test_tc0011_highlights_the_active_nav_link`

```python
def test_tc0011_highlights_the_active_nav_link(self, page: Page) -> None:
    expect(page.get_by_test_id("nav-dashboard")).to_have_class(re.compile(r"active"))
```

- **Given:** user on the dashboard (via `setup` fixture).
- **Then:** the `nav-dashboard` link has the CSS class `active`, indicating the selected menu item.

`to_have_class(re.compile(r"active"))` checks whether **any** of the element's classes contains `active`.

---

## `TestLogout` class

```python
@pytest.mark.smoke
class TestLogout:
```

Tests session termination. **Does not use** the sidebar `setup` fixture — performs manual login via UI to isolate the logout flow.

### `test_tc0012_logout_clears_session_and_redirects_to_login`

```python
def test_tc0012_logout_clears_session_and_redirects_to_login(self, page: Page) -> None:
    page.goto("/web/login.html")
    page.get_by_test_id("login-email").fill(DEMO_EMAIL)
    page.get_by_test_id("login-password").fill(DEMO_PASSWORD)
    page.get_by_test_id("login-submit").click()
    page.get_by_test_id("page-dashboard").wait_for()
```

**Given/When — login via UI:**

1. Opens the login page.
2. Fills email and password with demo credentials.
3. Submits the form.
4. `wait_for()` waits for the dashboard to appear (explicit synchronization).

```python
    page.get_by_test_id("nav-logout").click()
    expect(page).to_have_url(re.compile(r"/web/index\.html"))
    assert page.evaluate("() => sessionStorage.getItem('sandbox-auth')") is None
```

**When/Then — logout:**

- **When:** clicks logout in the sidebar.
- **Then:** redirects to `/web/index.html` (public home).
- **Then:** `sessionStorage` no longer contains `sandbox-auth` — session cleared.

**Playwright concept:** `page.evaluate()` runs JS in the browser and returns the result to Python. Here it verifies the key was removed.

---

## `TestApiHealth` class

```python
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.api
class TestApiHealth:
```

**Pure API** tests — do not open web pages. Use only the `api_request` fixture.

### `test_tc0020_get_health_returns_200`

```python
def test_tc0020_get_health_returns_200(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/health")
    assert response.status == 200
```

- **When:** `GET /health`
- **Then:** HTTP status 200 — server is up.

### `test_tc0021_post_auth_login_returns_token`

```python
@pytest.mark.critical
def test_tc0021_post_auth_login_returns_token(self, api_request: APIRequestContext) -> None:
    response = api_request.post(
        "/api/auth/login",
        data={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert response.status == 200
    body = response.json()
    assert body["token"]
    assert body["user"]["email"] == DEMO_EMAIL
```

- **When:** login with valid credentials.
- **Then:** 200, JSON body contains non-empty `token` and correct user email.

This test validates the **authentication contract** used by `login_via_api` and `fetch_auth_token`.

### `test_tc0022_get_users_returns_user_array`

```python
def test_tc0022_get_users_returns_user_array(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/api/users")
    assert response.status == 200
    body = response.json()
    assert isinstance(body["users"], list)
    assert len(body["users"]) > 0
```

- **Then:** users endpoint returns a non-empty list.

### `test_tc0023_get_errors_404_returns_404_status`

```python
def test_tc0023_get_errors_404_returns_404_status(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/api/errors/404")
    assert response.status == 404
```

**Error simulation** endpoint — confirms the API correctly propagates HTTP 404.

### `test_tc0024_get_errors_422_returns_422_status`

```python
def test_tc0024_get_errors_422_returns_422_status(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/api/errors/422")
    assert response.status == 422
```

Same pattern for validation error (422 Unprocessable Entity).

**Note:** these last two tests **do not** have individual `@pytest.mark.smoke` markers — they inherit only the class markers (`smoke`, `regression`, `api`).

---

## Flow diagram — authentication in tests

```
┌─────────────────────────────────────────────────────────────┐
│  conftest.py (session)                                      │
│  cache_auth_token → POST /api/auth/login → stores token     │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  visit_with_token   login_via_api    login via UI
  (TestPageNav)      (TestSidebar)    (TestLogout)
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                    sessionStorage
                    ('sandbox-auth')
                           │
                           ▼
                  Protected pages /web/*.html
```

---

## Summary for new learners

| Pattern | Where it appears | Why |
|---------|------------------|-----|
| Parametrize + data list | `TestPageNavigation` | DRY — one test, eight pages |
| `autouse` fixture | `TestSidebarNavigation.setup` | Repeated setup without boilerplate |
| Login via API | Sidebar, PageNavigation | Faster and more stable than UI |
| Login via UI | TestLogout | Tests the real logout flow |
| `expect` vs `assert` | UI | Automatic retry in Playwright |
| `assert response.status` | TestApiHealth | Direct assertion in API tests |
| TC-* IDs | Parametrize `ids` | Traceability with test cases |

**Suggested command to practice:**

```bash
pytest tests/smoke/test_navigation.py -v --headed
```

The `--headed` flag opens the browser visibly — useful for following what each test does while learning.
