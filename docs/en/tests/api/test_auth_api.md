# API Tests — Authentication (Login)

**Source file:** [`../../../../tests/api/test_auth_api.py`](../../../../tests/api/test_auth_api.py)

---

## Purpose

This module validates the **`POST /api/auth/login`** endpoint and related login UI flows. It combines:

1. **Pure API tests** — status, headers, JSON body, latency, token
2. **Invalid credentials and malformed payload tests**
3. **Hybrid UI + network tests** — route interception (`page.route`) and response stubbing

Reference material for students learning **APIRequestContext**, class-scoped fixtures, and **network interception** in Playwright.

---

## Prerequisites

| Item | Description |
|------|-------------|
| API | Server with `/api/auth/login` route |
| Config | `BASE_URL`, `DEMO_EMAIL`, `DEMO_PASSWORD` in `support/config.py` |
| Global fixtures | `api_request`, `playwright`, `page` |
| API-only execution | Browser not required for most tests |

```bash
pytest tests/api/test_auth_api.py -v
pytest tests/api/test_auth_api.py -m "api and smoke"
pytest tests/api/test_auth_api.py -m critical
```

---

## Markers used

| Marker | Usage |
|--------|-------|
| `api` | All REST / intercept tests |
| `regression` | Full suite |
| `smoke` | Critical happy paths (200, token) |
| `critical` | `test_body_has_token_as_non_empty_string` |

---

## Structure overview

```
test_auth_api.py
├── imports
├── constants: ENDPOINT, VALID
├── fixture: valid_login_response (scope=class)
├── TestAuthLoginValidCredentials
├── TestAuthLoginInvalidCredentials
├── TestAuthLoginMalformedRequest
└── TestAuthLoginInterceptFlow
```

---

## Imports — block by block

### `import re`

Regex for URL assertion on the login page after simulated error (`/web/login\.html`).

---

### `import time`

Latency measurement with **`time.monotonic()`** — monotonic clock, immune to system clock adjustments (prefer over `time.time()` for benchmarks).

---

### `import pytest`

Fixtures, markers, class organization.

---

### `from playwright.sync_api import APIRequestContext, Page, expect`

| Symbol | Usage in this file |
|--------|-------------------|
| `APIRequestContext` | Playwright HTTP client — POST/GET without browser |
| `Page` | Intercept tests on login UI |
| `expect` | URL and visibility assertions on UI |

**Playwright concept:** `APIRequestContext` can optionally share cookies/storage with the browser, but here uses isolated contexts for deterministic tests.

---

### `from support.config import BASE_URL, DEMO_EMAIL, DEMO_PASSWORD`

Centralizes environment and valid demo credentials.

---

## Module constants

### `ENDPOINT = "/api/auth/login"`

Relative path concatenated with `BASE_URL` in requests.

---

### `VALID = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}`

Valid login payload reused throughout the file — **single source of truth** for the happy path.

---

## Fixture: `valid_login_response`

```python
@pytest.fixture(scope="class")
def valid_login_response(playwright) -> dict:
    ctx = playwright.request.new_context(base_url=BASE_URL)
    try:
        start = time.monotonic()
        response = ctx.post(f"{BASE_URL}{ENDPOINT}", data=VALID)
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "status": response.status,
            "headers": response.headers,
            "body": response.json(),
            "duration_ms": elapsed_ms,
        }
    finally:
        ctx.dispose()
```

### PyTest concepts

| Aspect | Detail |
|--------|--------|
| `scope="class"` | Single HTTP call per test **class** using the fixture — saves time |
| `playwright` | Session fixture from pytest-playwright |
| `try/finally` + `dispose()` | Ensures HTTP context cleanup |

### Return value

Dictionary with status, headers, parsed body, and duration in ms — derived tests only **assert** without repeating POST.

**Given (for TestAuthLoginValidCredentials):** valid login response already materialized.

---

## Class `TestAuthLoginValidCredentials`

Happy-path validations with demo credentials.

---

### `test_returns_status_200`

```python
@pytest.mark.smoke
def test_returns_status_200(self, valid_login_response: dict) -> None:
    assert valid_login_response["status"] == 200
```

**Then:** HTTP 200 OK.

---

### `test_content_type_is_application_json`

```python
def test_content_type_is_application_json(self, valid_login_response: dict) -> None:
    assert "application/json" in valid_login_response["headers"].get("content-type", "")
```

**Then:** `content-type` header contains JSON. Using `.get(..., "")` avoids `KeyError`.

---

### `test_responds_within_2000ms`

```python
def test_responds_within_2000ms(self, api_request: APIRequestContext) -> None:
    start = time.monotonic()
    response = api_request.post(f"{BASE_URL}{ENDPOINT}", data=VALID)
    elapsed_ms = (time.monotonic() - start) * 1000
    assert response.status == 200
    assert elapsed_ms < 2000
```

**When:** fresh POST via `api_request` fixture (function scope — does not reuse class fixture cache).

**Then:** 200 and response in under 2 seconds — basic **SLA** test.

---

### `test_body_has_token_as_non_empty_string`

```python
@pytest.mark.smoke
@pytest.mark.critical
def test_body_has_token_as_non_empty_string(self, valid_login_response: dict) -> None:
    token = valid_login_response["body"]["token"]
    assert isinstance(token, str)
    assert token
```

**Then:** `token` field exists, is a non-empty string. `critical` marker for priority pipelines.

---

### `test_body_has_user_object_or_token_only_response`

```python
def test_body_has_user_object_or_token_only_response(self, valid_login_response: dict) -> None:
    body = valid_login_response["body"]
    if body.get("user"):
        assert isinstance(body["user"].get("email"), str)
        assert body["user"]["email"]
    else:
        assert isinstance(body["token"], str)
        assert body["token"]
```

**Tolerant pattern:** API may return `{ token, user }` or only `{ token }` — test accepts both contracts.

---

### `test_user_email_matches_the_login_email_when_user_is_present`

```python
def test_user_email_matches_the_login_email_when_user_is_present(
    self, valid_login_response: dict
) -> None:
    body = valid_login_response["body"]
    if body.get("user") and body["user"].get("email"):
        assert body["user"]["email"] == VALID["email"]
```

**Conditional Then:** only asserts consistency if `user.email` object exists.

---

### `test_token_can_authenticate_a_subsequent_request`

```python
def test_token_can_authenticate_a_subsequent_request(
    self, api_request: APIRequestContext, valid_login_response: dict
) -> None:
    token = valid_login_response["body"]["token"]
    response = api_request.get(
        f"{BASE_URL}/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status == 200
```

| Phase | Description |
|-------|-------------|
| **Given** | Token obtained from login |
| **When** | GET `/api/users` with Bearer header |
| **Then** | 200 — token is functional, not just present |

**OAuth/JWT concept:** `Authorization: Bearer <token>` pattern.

---

## Class `TestAuthLoginInvalidCredentials`

---

### `test_returns_401_for_wrong_password`

```python
def test_returns_401_for_wrong_password(self, api_request: APIRequestContext) -> None:
    response = api_request.post(
        f"{BASE_URL}{ENDPOINT}",
        data={"email": VALID["email"], "password": "wrongpassword"},
    )
    assert response.status == 401
```

Valid email + wrong password → **401 Unauthorized**.

---

### `test_returns_401_for_unknown_email`

```python
def test_returns_401_for_unknown_email(self, api_request: APIRequestContext) -> None:
    response = api_request.post(
        f"{BASE_URL}{ENDPOINT}",
        data={"email": "nobody@example.com", "password": VALID["password"]},
    )
    assert response.status == 401
```

Non-existent user → 401 (does not reveal whether email exists — good security practice).

---

### `test_error_response_has_a_non_empty_error_or_message_field`

```python
def test_error_response_has_a_non_empty_error_or_message_field(
    self, api_request: APIRequestContext
) -> None:
    response = api_request.post(
        f"{BASE_URL}{ENDPOINT}",
        data={"email": VALID["email"], "password": "wrong"},
    )
    body = response.json()
    err_text = body.get("message") or (body.get("error") or {}).get("message")
    assert isinstance(err_text, str)
    assert err_text
```

**Flexible error contract:** accepts top-level `message` or nested `error.message`.

---

## Class `TestAuthLoginMalformedRequest`

Input validation — expects **4xx** (400–422).

---

### `test_returns_4xx_when_body_is_empty`

```python
def test_returns_4xx_when_body_is_empty(self, api_request: APIRequestContext) -> None:
    response = api_request.post(f"{BASE_URL}{ENDPOINT}", data={})
    assert 400 <= response.status <= 422
```

---

### `test_returns_4xx_when_email_is_missing`

```python
def test_returns_4xx_when_email_is_missing(self, api_request: APIRequestContext) -> None:
    response = api_request.post(f"{BASE_URL}{ENDPOINT}", data={"password": VALID["password"]})
    assert 400 <= response.status <= 422
```

---

### `test_returns_4xx_when_password_is_missing`

```python
def test_returns_4xx_when_password_is_missing(self, api_request: APIRequestContext) -> None:
    response = api_request.post(f"{BASE_URL}{ENDPOINT}", data={"email": VALID["email"]})
    assert 400 <= response.status <= 422
```

**400–422 range:** covers Bad Request, Unprocessable Entity per sandbox implementation.

---

## Class `TestAuthLoginInterceptFlow`

**Browser + network** tests — not API-only.

---

### `test_api_toggle_sends_post_with_correct_payload_and_token_response`

```python
def test_api_toggle_sends_post_with_correct_payload_and_token_response(
    self, page: Page
) -> None:
    captured: dict = {}

    def handle_route(route) -> None:
        post_data = route.request.post_data_json or {}
        captured["email"] = post_data.get("email")
        route.continue_()

    page.route(f"**{ENDPOINT}", handle_route)
    page.goto("/web/login.html")
    page.get_by_test_id("login-use-api").evaluate("el => el.click()")
    page.get_by_test_id("login-email").fill(VALID["email"])
    page.get_by_test_id("login-password").fill(VALID["password"])

    with page.expect_response(f"**{ENDPOINT}") as response_info:
        page.get_by_test_id("login-submit").click()

    response = response_info.value
    assert captured.get("email") == VALID["email"]
    assert response.status == 200
    body = response.json()
    assert isinstance(body.get("token"), str)
    assert body["token"]
```

| Phase | Description |
|-------|-------------|
| **Given** | Handler records POST email without blocking (`continue_`) |
| **When** | Login UI with API mode enabled |
| **Then** | Correct payload; real 200 response with token |

**Playwright concepts:**

- **`page.route`**: intercepts requests matching pattern `**/api/auth/login`
- **`post_data_json`**: parsed JSON body of the request
- **`page.expect_response`**: context manager that captures response after action
- **`evaluate("el => el.click()")`**: JS click when normal click fails (hidden checkbox/toggle)

---

### `test_stubbed_500_keeps_user_on_login_page_without_crashing`

```python
def test_stubbed_500_keeps_user_on_login_page_without_crashing(self, page: Page) -> None:
    page.route(
        f"**{ENDPOINT}",
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body='{"error":"Internal Server Error"}',
        ),
    )
    page.goto("/web/login.html")
    page.get_by_test_id("login-use-api").evaluate("el => el.click()")
    page.get_by_test_id("login-email").fill(VALID["email"])
    page.get_by_test_id("login-password").fill(VALID["password"])

    with page.expect_response(f"**{ENDPOINT}"):
        page.get_by_test_id("login-submit").click()

    expect(page).to_have_url(re.compile(r"/web/login\.html"))
    result = page.get_by_test_id("login-result")
    if result.is_visible():
        expect(result).not_to_be_empty()
```

| Phase | Description |
|-------|-------------|
| **Given** | Login API always returns simulated 500 |
| **When** | Form submit |
| **Then** | Stays on login; if result message appears, it is not empty |

**Concept:** `route.fulfill` **replaces** the response — UI resilience test for backend failure.

---

## Summary table — test types

| Class | Layer | Main fixture |
|-------|-------|--------------|
| ValidCredentials | API | `valid_login_response` |
| InvalidCredentials | API | `api_request` |
| MalformedRequest | API | `api_request` |
| InterceptFlow | UI + Network | `page` |

---

## Learning checklist

- [ ] Explain `scope="class"` vs function scope for HTTP fixtures
- [ ] Differentiate `route.continue_()` vs `route.fulfill()`
- [ ] Describe Bearer header on authenticated request
- [ ] Justify `400 <= status <= 422` range
- [ ] Run `-m "api and critical"` and interpret the result
