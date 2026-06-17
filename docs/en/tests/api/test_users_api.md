# API Tests — Users, Health, and Fixture Interception

**Source file:** [`../../../../tests/api/test_users_api.py`](../../../../tests/api/test_users_api.py)

---

## Purpose

This module covers endpoints and behaviors related to **users** and **API health**, and demonstrates:

- `GET /api/users` listing with schema and email format validation
- `GET /health` endpoint with latency SLA
- Error simulation endpoints (`/api/errors/404`, `/api/errors/422`)
- **API mocking in the UI** with `page.route` + JSON fixture files
- `read_fixture` helper for reusable static data

Combines **API-only** and **E2E with network interception** tests.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Server | Routes `/api/users`, `/health`, `/api/errors/*`, page `/web/activity.html` |
| JSON fixtures | `users/empty-list.json`, `lookups/countries.json` |
| Auth | `visit_authenticated` for activity page tests |
| Helpers | `validate_schema`, `read_fixture` |

```bash
pytest tests/api/test_users_api.py -v
pytest tests/api/test_users_api.py -m smoke
```

---

## Markers used

| Marker | Where |
|--------|-------|
| `api` | All classes |
| `regression` | All except smoke combination on `TestHealth` |
| `smoke` | `TestGetUsers.test_returns_status_200`, `TestHealth` class and its status test |

---

## Structure overview

```
test_users_api.py
├── imports
├── fixture: users_list_response (scope=class)
├── TestGetUsers
├── TestHealth
├── TestErrorSimulationEndpoints
└── TestFixtureInterceptOnActivityPage
    ├── autouse fixture: activity_page
    ├── test_mock_api_get_serves_empty_users_fixture_on_fetch
    └── test_read_fixture_loads_countries_lookup
```

---

## Imports — block by block

### `import re`

Regular expression to validate email format on user objects.

---

### `import time`

Measures `duration_ms` in fixture and health test.

---

### `import pytest`

Fixtures, markers, test classes.

---

### `from playwright.sync_api import APIRequestContext, Page, expect`

| Symbol | Usage |
|--------|-------|
| `APIRequestContext` | GET health, errors, users (pure API) |
| `Page` | Activity page with intercept |
| `expect` | Text assertion on UI after fetch |

---

### `from support.auth import visit_authenticated`

Navigates authenticated to web pages — used in `activity_page` fixture.

---

### `from support.config import BASE_URL`

Base URL for building absolute paths.

---

### `from support.helpers import validate_schema`

Lightweight dict schema validator `{ field: "string" | ... }` — ensures minimum JSON types.

---

### `from support.helpers.fixtures import read_fixture`

Loads JSON files from the project fixtures directory and returns Python `dict`/`list`.

---

## Fixture: `users_list_response`

```python
@pytest.fixture(scope="class")
def users_list_response(playwright) -> dict:
    ctx = playwright.request.new_context(base_url=BASE_URL)
    try:
        start = time.monotonic()
        response = ctx.get(f"{BASE_URL}/api/users")
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "status": response.status,
            "body": response.json(),
            "duration_ms": elapsed_ms,
        }
    finally:
        ctx.dispose()
```

**Given for `TestGetUsers`:** one cached GET `/api/users` response per class.

Difference vs auth: does not capture headers; focuses on body and performance.

---

## Class `TestGetUsers`

---

### `test_returns_status_200`

```python
@pytest.mark.smoke
def test_returns_status_200(self, users_list_response: dict) -> None:
    assert users_list_response["status"] == 200
```

Smoke gate — user list accessible.

---

### `test_responds_within_2000ms`

```python
def test_responds_within_2000ms(self, users_list_response: dict) -> None:
    assert users_list_response["duration_ms"] < 2000
```

2s SLA using duration already measured in fixture (no second GET).

---

### `test_body_has_a_users_array`

```python
def test_body_has_a_users_array(self, users_list_response: dict) -> None:
    users = users_list_response["body"]["users"]
    assert isinstance(users, list)
    assert len(users) > 0
```

**Contract:** response `{ "users": [ ... ] }` with at least one item.

---

### `test_each_user_matches_json_schema`

```python
def test_each_user_matches_json_schema(self, users_list_response: dict) -> None:
    for user in users_list_response["body"]["users"]:
        validate_schema(user, {"name": "string", "email": "string", "role": "string"})
```

Iterates all users — fails on first missing `name`, `email`, or `role` as strings.

**Concept:** schema validation in contract tests prevents silent format regressions.

---

### `test_all_emails_are_valid_format`

```python
def test_all_emails_are_valid_format(self, users_list_response: dict) -> None:
    email_regex = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    for user in users_list_response["body"]["users"]:
        assert email_regex.match(user["email"])
```

Basic syntactic email validation (does not validate DNS or full RFC).

---

## Class `TestHealth`

```python
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
class TestHealth:
```

Simplified **liveness/readiness** endpoint.

---

### `test_returns_status_200`

```python
@pytest.mark.smoke
def test_returns_status_200(self, api_request: APIRequestContext) -> None:
    response = api_request.get(f"{BASE_URL}/health")
    assert response.status == 200
```

Fresh request per test (function-scoped `api_request`).

---

### `test_responds_within_1000ms`

```python
def test_responds_within_1000ms(self, api_request: APIRequestContext) -> None:
    start = time.monotonic()
    response = api_request.get(f"{BASE_URL}/health")
    elapsed_ms = (time.monotonic() - start) * 1000
    assert response.status == 200
    assert elapsed_ms < 1000
```

Health should be **faster** than business endpoints — 1s SLA.

---

## Class `TestErrorSimulationEndpoints`

Sandbox exposes routes that return fixed errors for status and body assertion training.

---

### `test_get_errors_404_returns_404`

```python
def test_get_errors_404_returns_404(self, api_request: APIRequestContext) -> None:
    response = api_request.get(f"{BASE_URL}/api/errors/404")
    assert response.status == 404
```

---

### `test_get_errors_422_returns_422`

```python
def test_get_errors_422_returns_422(self, api_request: APIRequestContext) -> None:
    response = api_request.get(f"{BASE_URL}/api/errors/422")
    assert response.status == 422
```

---

### `test_404_response_has_a_non_empty_error_or_message_field`

```python
def test_404_response_has_a_non_empty_error_or_message_field(
    self, api_request: APIRequestContext
) -> None:
    body = api_request.get("/api/errors/404").json()
    err_text = body.get("message") or (body.get("error") or {}).get("message")
    assert isinstance(err_text, str)
    assert err_text
```

**Note:** uses relative path `"/api/errors/404"` — works because `api_request` was created with `base_url=BASE_URL`.

---

### `test_422_response_has_a_non_empty_error_or_message_field`

Same pattern for 422 — ensures useful message for the client.

---

## Class `TestFixtureInterceptOnActivityPage`

UI integration + backend mock.

---

### Autouse fixture: `activity_page`

```python
@pytest.fixture(autouse=True)
def activity_page(self, page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/activity.html")
```

**Scope:** defined **inside the class** — PyTest applies autouse only to tests in this class.

**Given:** authenticated user on Activity page.

---

### `test_mock_api_get_serves_empty_users_fixture_on_fetch`

```python
def test_mock_api_get_serves_empty_users_fixture_on_fetch(self, page: Page) -> None:
    page.route(
        "**/api/users",
        lambda route: route.fulfill(json=read_fixture("users/empty-list.json")),
    )
    with page.expect_response("**/api/users"):
        page.get_by_test_id("fetch-users-btn").click()
    expect(page.get_by_test_id("api-result")).to_contain_text("Fetched 0 users")
```

| Phase | Description |
|-------|-------------|
| **Given** | `/api/users` route returns static JSON from fixture |
| **When** | Click fetch users |
| **Then** | UI displays "Fetched 0 users" |

**Concepts:**

- **`route.fulfill(json=...)`** — Playwright serializes dict to response
- **`read_fixture("users/empty-list.json")`** — decouples payload from test
- **`expect_response`** — synchronizes with request triggered by click

---

### `test_read_fixture_loads_countries_lookup`

```python
def test_read_fixture_loads_countries_lookup(self) -> None:
    data = read_fixture("lookups/countries.json")
    assert isinstance(data["countries"], list)
    assert len(data["countries"]) > 0
    assert "code" in data["countries"][0]
    assert "name" in data["countries"][0]
```

**Helper unit test** — no browser or API.

Validates minimum lookup file structure (code + name).

---

## Given / When / Then — quick map

| Test | Given | When | Then |
|------|-------|------|------|
| GET users 200 | Cached fixture | — | status 200 |
| User schema | Populated list | loop | string fields |
| Health 1s | API up | GET /health | < 1000ms |
| Mock empty users | Route + activity page | click fetch | "0 users" text |
| read_fixture | JSON file | load | valid countries |

---

## Concepts for students

### APIRequestContext vs page.route

- **Pure API:** fast, no browser, ideal for contract and performance.
- **UI intercept:** validates front-end consumes API correctly and displays result.

### Class-scoped fixtures

Reusing heavy GET saves time; watch out if tests mutate shared state (not the case here — idempotent GET).

### validate_schema vs full JSON Schema

Project helper is intentionally simple — good for bootcamp; production may use `jsonschema` or Pydantic.

---

## Learning checklist

- [ ] Explain why `activity_page` is inside the class
- [ ] Compare health SLA (1s) vs users (2s)
- [ ] Describe flow `route.fulfill(json=read_fixture(...))`
- [ ] Write email regex and its limitations
- [ ] Locate files in `users/empty-list.json` and `lookups/countries.json`
