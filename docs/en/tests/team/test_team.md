# Team Page Tests

**Source file:** [`../../../../tests/team/test_team.py`](../../../../tests/team/test_team.py)

---

## Purpose

This file validates the **Team** page (`/web/team.html`) — team member management:

- Table structure (columns, rows, counters)
- Search by name and email
- Filters by role (admin, etc.) and status (active/inactive)
- Sorting by name (asc/desc)
- Pagination (page 1 ↔ 2)
- Invite member modal (validation, success, API payload)
- Inline row editing (save, cancel, toast)
- Framework list filter

This is a dense **functional regression** suite — covers table interactions, modal forms, and HTTP request interception.

---

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| Local server | `BASE_URL` accessible (default: `http://localhost:5050`). |
| Authentication | `visit_authenticated` via API functional. |
| Team data | Application must have 6 members (4 on page 1, 2 on page 2). |
| Page Object | `TeamPage` in `pages/team_page.py`. |
| JSON fixture | `fixtures/team-member.json` with invite data. |

**Global fixtures:**

- `page` — Playwright tab.
- `api_request` — HTTP client for authentication.

---

## Markers used

```python
pytestmark = pytest.mark.regression
```

The entire module is **regression**. No additional markers (`smoke`, `critical`, `api`) are applied individually.

```bash
pytest tests/team/test_team.py -v
pytest tests/team/test_team.py::TestSearch -v
pytest tests/team/test_team.py::TestInviteMemberModal::test_adds_a_new_row_after_successful_invite -v
```

---

## PyTest and Playwright concepts used in this file

### `visit_authenticated` vs `login_via_api`

- `login_via_api` → always ends on the **dashboard**.
- `visit_authenticated(page, api_request, path)` → authenticates and goes **directly** to the given path (`/web/team.html`).

### `page.on("request", handler)`

Registers a network event listener. Each HTTP request triggers `handler(request)`. Used to capture POST/PUT payloads without `page.route` (mock).

### `Locator.evaluate_all()`

Executes JavaScript on **all** elements matching the locator and returns a list of results — ideal for extracting data from multiple table rows.

### `Locator.count()` + `range(count)` loop

Pattern for iterating dynamic rows: get count, then access `.nth(i)` for each index.

### Keyword-only arguments (`*`)

`fill_invite_form(*, name=..., email=...)` — forces named arguments, preventing accidental parameter swapping.

### `re.search` in Python

Extracts number from text `"6 row(s)"` to compare total after invite.

---

## Imports — line by line

```python
import re
```

Regex for parsing labels (`row_count`) and validating URLs.

```python
import pytest
```

Test framework.

```python
from playwright.sync_api import APIRequestContext, Page, expect
```

Playwright types and assertions.

```python
from pages.team_page import TeamPage
```

Page Object for the Team page.

```python
from support.auth import visit_authenticated
```

Authenticates via API and navigates directly to the desired route.

```python
from support.helpers.fixtures import read_fixture
```

Loads JSON from `fixtures/`.

---

## Module configuration

```python
pytestmark = pytest.mark.regression
```

Marks regression on all tests.

```python
team_member = read_fixture("team-member.json")
```

Contents of `fixtures/team-member.json`:

```json
{
  "new": {
    "name": "Grace SDET",
    "email": "grace@testflow.io"
  },
  "duplicate": {
    "name": "Alice QA",
    "email": "alice@testflow.io",
    "role": "admin"
  }
}
```

Used in invite tests — centralized data, easy to change.

---

## `setup_team` fixture

```python
@pytest.fixture(autouse=True)
def setup_team(page: Page, api_request: APIRequestContext) -> None:
    visit_authenticated(page, api_request, "/web/team.html")
    expect(TeamPage(page).page_root()).to_be_visible()
```

**Before each test:**

1. Authenticates via API and opens `/web/team.html` (does not go through the dashboard).
2. Confirms `[data-testid="page-team"]` is visible.

**Implicit Given:** user logged in on the Team page with table loaded.

---

## `TeamPage` Page Object — reference

Main methods used in this file:

| Category | Method | Description |
|----------|--------|-------------|
| Structure | `team_summary()`, `table()`, `table_rows()`, `row_count()` | Table elements |
| Search | `search(term)`, `clear_search()` | `table-search` field |
| Filters | `filter_by_role(role)`, `filter_by_status(status)` | Filter selects |
| Sorting | `sort_by_name()` | Click Name header |
| Pagination | `go_to_next_page()`, `go_to_prev_page()`, `prev_page()`, `next_page()`, `page_info()` | Page controls |
| Invite | `open_invite_modal()`, `fill_invite_form()`, `submit_invite()`, `cancel_invite()` | Invite modal |
| Editing | `start_edit(id)`, `edit_name()`, `save_edit()`, `cancel_edit()` | Inline edit per row |
| Frameworks | `framework_search()`, `framework_list()` | Filterable side list |
| Assertions | `should_have_row_count(n)`, `should_show_invite_error(text)`, etc. | expect wrappers |

---

## `TestPageStructure` class

Validates initial member table layout.

### `test_shows_the_page_header_with_member_count`

```python
expect(TeamPage(page).team_summary()).to_contain_text("6 members")
```

- **Then:** header indicates 6 registered members total.

### `test_renders_all_table_columns`

```python
expect(page.get_by_test_id("users-table").locator("thead th")).to_have_count(7)
```

- **Then:** table has exactly 7 columns in `<thead>`.

### `test_renders_the_correct_number_of_rows_on_page_1`

```python
TeamPage(page).should_have_row_count(4)
```

- **Then:** 4 visible rows on page 1 (4 per page pagination, 6 total).

### `test_row_count_label_matches_visible_rows`

```python
expect(TeamPage(page).row_count()).to_contain_text("6 row(s)")
```

- **Then:** `table-row-count` label reflects global total (6), not just the current page.

---

## `TestSearch` class

Validates real-time table search filter.

### `test_filters_rows_by_member_name`

```python
team = TeamPage(page)
team.search("Alice")
team.should_have_row_count(1)
expect(team.name_cell(1)).to_contain_text("Alice QA")
```

| Step | Given/When/Then |
|------|-----------------|
| Setup | **Given** 4 rows on page 1 |
| `search("Alice")` | **When** types in search field |
| 1 row + name | **Then** filters to Alice QA |

### `test_filters_rows_by_email`

```python
team.search("carol")
team.should_have_row_count(1)
```

- **When:** searches by email fragment (case insensitive expected).
- **Then:** one row matches.

### `test_returns_all_rows_when_search_is_cleared`

```python
team.search("Alice")
team.should_have_row_count(1)
team.clear_search()
team.should_have_row_count(4)
```

- **When:** clears search after filtering.
- **Then:** restores 4 rows on page 1.

### `test_shows_zero_rows_for_a_term_with_no_match`

```python
team.search("zzznoresult")
expect(team.table_rows()).to_have_count(0)
```

- **Then:** nonexistent term → empty table.

---

## `TestRoleFilter` class

Filters rows by member role.

### `test_filters_to_admin_rows_only`

```python
team.filter_by_role("admin")
rows = team.table_rows()
count = rows.count()
for i in range(count):
    expect(rows.nth(i).locator('[data-role="admin"]')).to_be_visible()
```

- **When:** selects "admin" filter.
- **Then:** **each** visible row contains badge/element `[data-role="admin"]`.

**Iteration pattern:** `count()` gets dynamic N; loop ensures no non-admin row passed the filter.

### `test_shows_all_rows_when_filter_is_reset`

```python
team.filter_by_role("admin")
team.filter_by_role("")
team.should_have_row_count(4)
```

- **When:** resets filter (empty value = "All").
- **Then:** 4 rows again.

---

## `TestStatusFilter` class

Same pattern as role filter, for active/inactive status.

### `test_filters_to_active_members_only`

```python
team.filter_by_status("active")
# loop verifies [data-status="active"] on each row
```

### `test_filters_to_inactive_members_only`

```python
team.filter_by_status("inactive")
# loop verifies [data-status="inactive"] on each row
```

---

## `TestSorting` class

Validates clickable sorting on the Name column.

### `test_sorts_rows_by_name_descending_on_first_click`

```python
team.sort_by_name()
names = team.table_rows().evaluate_all(
    """rows => rows.map(row =>
        (row.querySelector('[data-testid^="cell-name-"]')?.textContent ?? '').trim()
    )"""
)
assert names == sorted(names, reverse=True)
```

**Flow:**

1. **When:** first click on Name header.
2. **Then:** extracts names from all rows via JS in the browser.
3. **Then:** list is in descending order (`sorted(names, reverse=True)`).

**`evaluate_all` concept:** runs JS function receiving array of DOM elements — returns Python list with texts.

### `test_second_click_sorts_rows_by_name_ascending`

```python
team.sort_by_name()
team.sort_by_name()
names = team.table_rows().evaluate_all(...)
assert names == sorted(names)
```

- **When:** two clicks (toggle asc/desc).
- **Then:** alphabetical ascending order.

---

## `TestPagination` class

Validates table page navigation.

### `test_prev_button_is_disabled_on_page_1`

```python
expect(TeamPage(page).prev_page()).to_be_disabled()
```

- **Given:** page 1.
- **Then:** "Previous" button disabled.

### `test_navigates_to_page_2_showing_remaining_rows`

```python
team.go_to_next_page()
expect(team.page_info()).to_contain_text("Page 2")
team.should_have_row_count(2)
```

- **When:** advances to page 2.
- **Then:** "Page 2" indicator + 2 remaining rows (6 total − 4 on page 1).

### `test_next_button_is_disabled_on_last_page`

```python
team.go_to_next_page()
expect(team.next_page()).to_be_disabled()
```

- **Given:** last page.
- **Then:** "Next" button disabled.

### `test_navigating_back_to_page_1_restores_row_count`

```python
team.go_to_next_page()
team.go_to_prev_page()
team.should_have_row_count(4)
```

- **When:** goes to page 2 and back.
- **Then:** 4 rows on page 1 again.

---

## `TestInviteMemberModal` class

Validates new member invite modal — UX, validation, and API integration.

### `test_opens_modal_on_invite_member_click`

```python
TeamPage(page).open_invite_modal()
TeamPage(page).should_have_invite_modal_open()
```

- **When:** clicks `invite-btn`.
- **Then:** modal visible.

### `test_closes_modal_on_cancel`

```python
team.open_invite_modal()
team.cancel_invite()
team.should_have_invite_modal_closed()
```

### `test_closes_modal_on_escape_key`

```python
team.open_invite_modal()
page.keyboard.press("Escape")
team.should_have_invite_modal_closed()
```

### `test_shows_validation_error_when_name_is_empty`

```python
team.open_invite_modal()
team.fill_invite_form(email=team_member["new"]["email"])
team.submit_invite()
team.should_show_invite_error("required")
```

- **Given:** email filled, name omitted.
- **When:** submits.
- **Then:** error containing "required".

**Concept:** `fill_invite_form` uses keyword-only args — `email=` without `name=` leaves name empty.

### `test_shows_validation_error_for_invalid_email`

```python
team.fill_invite_form(name=team_member["new"]["name"], email="notanemail")
team.submit_invite()
team.should_show_invite_error("valid email")
```

- **Then:** email format validation.

### `test_adds_a_new_row_after_successful_invite`

```python
team.open_invite_modal()
team.fill_invite_form(**team_member["new"])
team.submit_invite()
team.should_have_invite_modal_closed()
expect(page.get_by_test_id("toast-message")).to_contain_text(
    team_member["new"]["email"]
)
label = team.row_count().inner_text()
row_total = int(re.search(r"\d+", label).group())
assert row_total > 6
```

| Step | Given/When/Then |
|------|-----------------|
| Fills form | **When** invites Grace SDET |
| Modal closes + toast | **Then** success with email in toast |
| Counter | **Then** total rows > 6 (was 6 before) |

`**team_member["new"]` — unpacks dict as `name="Grace SDET", email="grace@testflow.io"`.

### `test_invite_request_contains_name_and_email_in_the_payload`

```python
captured: list = []

def capture_request(req) -> None:
    if req.method == "POST" and "/api/" in req.url:
        captured.append(req)

page.on("request", capture_request)
team.open_invite_modal()
team.fill_invite_form(**team_member["new"])
team.submit_invite()
# ... UI assertions ...

invite_request = captured[0] if captured else None
if invite_request is not None:
    body = invite_request.post_data_json
    assert "name" in body and isinstance(body["name"], str)
    assert "email" in body and isinstance(body["email"], str)
    assert body["email"] == team_member["new"]["email"]
```

**Concept — passive interception with `page.on("request")`:**

1. Registers handler **before** the action.
2. Handler filters POSTs to URLs containing `/api/`.
3. After submit, inspects `post_data_json` of the captured request.

**Difference from `page.route`:** `page.on` **observes** real traffic without mocking the response — integration test.

**Note:** `if invite_request is not None` block makes payload assertions conditional — UI is still validated even if API mode is off.

---

## `TestInlineEditing` class

Validates inline member editing in the table.

### `test_shows_name_and_role_inputs_when_edit_is_clicked`

```python
team.start_edit(1)
team.should_show_edit_inputs(1)
```

- **When:** clicks edit on row 1.
- **Then:** inputs `edit-name-1` and `edit-role-1` visible.

### `test_updates_the_row_after_saving_a_new_name`

```python
team.start_edit(1)
team.edit_name(1, "Alice QA Updated")
team.save_edit(1)
expect(team.name_cell(1)).to_contain_text("Alice QA Updated")
```

- **When:** changes name and saves.
- **Then:** cell reflects new value.

### `test_shows_a_success_toast_after_saving`

```python
team.start_edit(2)
team.save_edit(2)
expect(page.get_by_test_id("toast-message")).to_contain_text("updated")
```

- **Then:** toast feedback after save (even without changing data).

### `test_edit_save_updates_the_row_and_triggers_a_write_request_if_api_driven`

```python
captured: list = []

def capture_request(req) -> None:
    if req.method in ("PUT", "PATCH") and "/api/" in req.url:
        captured.append(req)

page.on("request", capture_request)
team.start_edit(1)
team.edit_name(1, "Alice QA Intercepted")
team.save_edit(1)
expect(team.name_cell(1)).to_contain_text("Alice QA Intercepted")

interception = captured[0] if captured else None
if interception is not None:
    body = interception.post_data_json
    assert "name" in body
```

- **When:** saves edit with API active.
- **Then:** UI updated **and** (if API) PUT/PATCH request contains `name` field.

### `test_discards_changes_on_cancel`

```python
team.start_edit(1)
team.edit_name(1, "Should Not Save")
team.cancel_edit(1)
expect(team.name_cell(1)).not_to_contain_text("Should Not Save")
```

- **When:** cancels after editing.
- **Then:** original value preserved.

### `test_restores_normal_row_after_cancel`

```python
team.start_edit(1)
team.cancel_edit(1)
expect(team.edit_btn(1)).to_be_visible()
```

- **Then:** normal visual mode — Edit button visible again.

---

## `TestFrameworkListFilter` class

Validates the side framework list filter.

### `test_filters_the_framework_list`

```python
team.framework_search().fill("play")
items = team.framework_list().locator("li")
count = items.count()
for i in range(count):
    text = items.nth(i).inner_text()
    assert "play" in text.lower()
```

- **When:** searches "play" in `item-search` field.
- **Then:** each visible `<li>` contains "play" (e.g. Playwright).

### `test_shows_all_frameworks_when_filter_is_cleared`

```python
team.framework_search().fill("cypress")
team.framework_search().clear()
assert team.framework_list().locator("li").count() > 1
```

- **When:** filters then clears.
- **Then:** full list restored (> 1 item).

---

## Diagram — areas tested on the Team page

```
┌─────────────────────────────────────────────────────────────┐
│  team-summary ("6 members")          [Invite Member]        │
├─────────────────────────────────────────────────────────────┤
│  [Search]  [Role ▼]  [Status ▼]                             │
├──────────────────────────────┬──────────────────────────────┤
│  users-table                 │  framework list              │
│  ├─ sort by name             │  ├─ item-search              │
│  ├─ pagination prev/next     │  └─ item-list (li...)        │
│  └─ inline edit rows         │                              │
├──────────────────────────────┴──────────────────────────────┤
│  invite-modal (name, email, role)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary for new learners

| Pattern | Example | Takeaway |
|---------|---------|----------|
| Direct route setup | `visit_authenticated(..., "/web/team.html")` | No need to go through dashboard |
| JSON data | `team_member = read_fixture(...)` | Separate data from logic |
| Dynamic iteration | `for i in range(rows.count())` | Tables with variable N |
| Bulk extraction | `evaluate_all(...)` | Read entire column via JS |
| Network listener | `page.on("request", handler)` | Validate payload without mock |
| Conditional API assert | `if captured[0] is not None` | UI + API when available |
| Pagination | prev/next disabled + row count | Control state matters |

**Suggested command — explore by class:**

```bash
# Search and filters
pytest tests/team/test_team.py::TestSearch tests/team/test_team.py::TestRoleFilter -v

# Invite modal (visual)
pytest tests/team/test_team.py::TestInviteMemberModal -v --headed
```

**Recommended study order:**

1. `TestPageStructure` — understand the baseline layout
2. `TestSearch` / `TestRoleFilter` — simple table interactions
3. `TestPagination` / `TestSorting` — multi-page state
4. `TestInviteMemberModal` / `TestInlineEditing` — forms + network
