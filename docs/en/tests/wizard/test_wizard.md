# Multi-Step Wizard Tests

**Source file:** [`../../../../tests/wizard/test_wizard.py`](../../../../tests/wizard/test_wizard.py)

---

## Purpose

This module validates the **Wizard** (`/web/wizard.html`), a multi-step (stepper) form with three steps:

1. **Personal data** — name, email, date of birth, country
2. **Preferences** — framework, role, experience, terms, newsletter
3. **Review and completion** — summary + success message

The tests cover full flow, validation, backward navigation, restart, API interception for lookups, and accessibility.

The file uses **private helper functions** (`_` prefix) to compose long flows without duplicating code — a common pattern when there is no dedicated Page Object.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Environment | TestFlow server running |
| Authentication | `visit_authenticated` via autouse fixture |
| Factories | [`support/factories/wizard.py`](../../../../support/factories/wizard.py) — fake data with Faker |
| JSON fixtures | [`fixtures/lookups/countries.json`](../../../../fixtures/lookups/countries.json) |
| Helper | [`support/helpers/fixtures.py`](../../../../support/helpers/fixtures.py) — `read_fixture` |

```bash
pytest tests/wizard/test_wizard.py -v
pytest tests/wizard/test_wizard.py -m smoke
pytest tests/wizard/test_wizard.py -m critical
pytest tests/wizard/test_wizard.py -m a11y
```

---

## Markers used

| Marker | Where it appears | Meaning |
|--------|------------------|---------|
| `regression` | Both test classes | Regression suite |
| `smoke` | `test_shows_step_1_by_default` | Quick load verification |
| `critical` | `test_completes_all_wizard_sections` | Main end-to-end flow |
| `a11y` | `TestWizardAccessibility` | WCAG accessibility |

---

## Structure overview

```
test_wizard.py
├── Imports
├── Private helpers (_complete_wizard_step1, step2, step3, _advance, _fill_wizard_flow)
├── Fixture autouse: wizard_page
├── TestWizardMultiStepFlow
└── TestWizardAccessibility
```

---

## Imports — block by block

### `import re`

Regular expressions to validate CSS classes with word boundaries (`\bactive\b`, `\bdone\b`).

**Why `\b`?** Avoids partial matches — `"active"` does not match `"inactive"`.

---

### `import pytest`

Test framework.

---

### `from playwright.sync_api import Page, expect`

Playwright sync API for interactions and assertions.

---

### `from conftest import check_a11y`

axe-core accessibility scan.

---

### `from support.auth import visit_authenticated`

API login + authenticated navigation.

---

### `from support.factories.wizard import create_personal_step, create_preferences_step`

| Function | Returns |
|----------|---------|
| `create_personal_step(**overrides)` | `dict` with `name`, `email`, `dob`, `country` (Faker + defaults) |
| `create_preferences_step(**overrides)` | `dict` with `framework`, `role`, `experience` |

**Concept:** **Test Data Factory** — generates valid data; `**overrides` allows customizing specific fields.

---

### `from support.helpers.fixtures import read_fixture`

Loads JSON from `fixtures/` for use in tests and API mocks.

---

## Helper functions — block by block

### `_complete_wizard_step1(page, personal)`

```python
def _complete_wizard_step1(page: Page, personal: dict[str, str]) -> None:
    page.get_by_test_id("wizard-name").fill(personal["name"])
    page.get_by_test_id("wizard-email").fill(personal["email"])
    page.get_by_test_id("wizard-dob").fill(personal["dob"])
    page.get_by_test_id("wizard-country").select_option(personal["country"])
```

| Field | Action |
|-------|--------|
| `wizard-name` | Fills name |
| `wizard-email` | Fills email |
| `wizard-dob` | Fills date of birth |
| `wizard-country` | Selects country in `<select>` |

**Given/When:** Given a `personal` dict, fills all required fields in step 1.

**Concept:** `_` prefix indicates a **module-private** function — not a test, but a building block.

---

### `_complete_wizard_step2(page, prefs)`

```python
def _complete_wizard_step2(page: Page, prefs: dict[str, str]) -> None:
    expect(page.get_by_test_id("wizard-panel-2")).to_have_class(re.compile(r"\bactive\b"))
    page.get_by_test_id(f"wizard-fw-{prefs['framework']}").check(force=True)
    page.get_by_test_id(f"wizard-role-{prefs['role']}").check(force=True)
    page.get_by_test_id("wizard-experience").fill(str(prefs["experience"]))
    page.get_by_test_id("wizard-terms").check(force=True)
    page.get_by_test_id("wizard-newsletter").check(force=True)
```

| Aspect | Explanation |
|--------|-------------|
| Initial assertion | Confirms panel 2 is active before interacting |
| `wizard-fw-{framework}` | Dynamic test ID — e.g., `wizard-fw-playwright` |
| `wizard-role-{role}` | E.g., `wizard-role-qa` |
| `check(force=True)` | Checks checkbox even if Playwright considers it not clickable |
| `str(prefs["experience"])` | Converts number to string for input |

**Playwright concept:** `force=True` on `check()` ignores actionability checks — useful when CSS hides the native input.

---

### `_complete_wizard_step3(page)`

```python
def _complete_wizard_step3(page: Page) -> None:
    expect(page.get_by_test_id("wizard-review")).to_be_visible()
```

Step 3 is **review only** — confirms the review section is visible (no fields to fill).

---

### `_advance_wizard(page)`

```python
def _advance_wizard(page: Page) -> None:
    page.get_by_test_id("wizard-next").click()
```

Clicks **Next** to advance a step.

---

### `_fill_wizard_flow(page, personal, prefs)`

```python
def _fill_wizard_flow(page: Page, personal: dict[str, str], prefs: dict[str, str]) -> None:
    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    _complete_wizard_step2(page, prefs)
    _advance_wizard(page)
    _complete_wizard_step3(page)
    _advance_wizard(page)
```

**Orchestrator** — runs the full wizard flow through step 3 (before the final success screen, depending on Next button behavior on step 3).

**Concept:** Composing helpers reduces duplication in tests that need the complete wizard.

---

## Fixture: `wizard_page`

```python
@pytest.fixture(autouse=True)
def wizard_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/wizard.html")
    expect(page.get_by_test_id("page-wizard")).to_be_attached()
```

| Aspect | Explanation |
|--------|-------------|
| Setup | Authenticates and navigates to `/web/wizard.html` |
| Verification | `page-wizard` attached in DOM |

Every test starts on the authenticated wizard page.

---

## Class `TestWizardMultiStepFlow`

```python
@pytest.mark.regression
class TestWizardMultiStepFlow:
```

Functional tests for the multi-step flow.

---

### `test_shows_step_1_by_default`

```python
@pytest.mark.smoke
def test_shows_step_1_by_default(self, page: Page) -> None:
    expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
    expect(page.get_by_test_id("wizard-step-1")).to_have_class(re.compile(r"\bactive\b"))
```

| **Given** | Freshly loaded wizard |
| **Then** | Panel 1 visible + step 1 indicator has `active` class |

**`smoke` marker:** Quick test for CI gate.

---

### `test_validates_required_fields_on_step_1`

```python
def test_validates_required_fields_on_step_1(self, page: Page) -> None:
    page.get_by_test_id("wizard-next").click()
    expect(page.get_by_test_id("wizard-step1-error")).to_be_visible()
```

| **When** | Advances without filling fields |
| **Then** | Step 1 error message visible |

Client-side validation of required fields.

---

### `test_maps_country_fixture_codes_to_wizard_select_options`

```python
def test_maps_country_fixture_codes_to_wizard_select_options(self, page: Page) -> None:
    countries = read_fixture("lookups/countries.json")["countries"]
    canada = next(c for c in countries if c["code"] == "CA")
    assert canada is not None

    page.route(
        "**/lookups/countries**",
        lambda route: route.fulfill(json=read_fixture("lookups/countries.json")),
    )
    page.get_by_test_id("wizard-country").select_option("ca")
    expect(page.get_by_test_id("wizard-country")).to_have_value("ca")
```

| Aspect | Explanation |
|--------|-------------|
| `read_fixture` | Loads country JSON from disk |
| `next(...)` | Finds Canada with code `"CA"` — proves fixture contains the data |
| `page.route` | **Intercepts** network requests |
| `route.fulfill(json=...)` | Responds with mocked JSON instead of calling real API |
| `select_option("ca")` | `<option>` value is lowercase `"ca"` |

**Given/When/Then:**

- **Given:** Countries API mocked with local fixture
- **When:** Selects Canada
- **Then:** Select value persists as `"ca"`

**Playwright concept:** Route interception decouples tests from unstable backends.

---

### `test_completes_all_wizard_sections`

```python
@pytest.mark.critical
def test_completes_all_wizard_sections(self, page: Page) -> None:
    personal = create_personal_step()
    prefs = create_preferences_step()

    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    expect(page.get_by_test_id("wizard-step-1")).to_have_class(re.compile(r"\bdone\b"))

    _complete_wizard_step2(page, prefs)
    _advance_wizard(page)
    expect(page.get_by_test_id("wizard-step-2")).to_have_class(re.compile(r"\bdone\b"))

    _complete_wizard_step3(page)
    _advance_wizard(page)

    expect(page.get_by_test_id("wizard-success")).to_be_visible()
    expect(page.get_by_test_id("wizard-success-message")).not_to_be_empty()
    expect(page.get_by_test_id("review-name")).to_contain_text(personal["name"])
```

| Step | Validation |
|------|------------|
| After step 1 | `wizard-step-1` indicator has `done` class |
| After step 2 | `wizard-step-2` indicator has `done` class |
| Final | Success screen + message + name in review |

**`critical` marker:** Main E2E test for the wizard.

**Given/When/Then:**

- **Given:** Data generated by factories
- **When:** Walks through all steps
- **Then:** Stepper marks completed steps + success displays correct data

---

### `test_navigates_back_from_step_2_to_step_1`

```python
def test_navigates_back_from_step_2_to_step_1(self, page: Page) -> None:
    personal = create_personal_step()
    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    page.get_by_test_id("wizard-back").click()
    expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
```

| **When** | Completes step 1, advances, clicks Back |
| **Then** | Returns to panel 1 |

Tests **bidirectional** stepper navigation.

---

### `test_restarts_wizard_after_completion`

```python
def test_restarts_wizard_after_completion(self, page: Page) -> None:
    personal = create_personal_step()
    prefs = create_preferences_step()
    _fill_wizard_flow(page, personal, prefs)
    page.get_by_test_id("wizard-restart").click()
    expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
```

| **When** | Completes wizard + clicks restart |
| **Then** | Returns to panel 1 (initial state) |

Validates flow reset after completion.

---

## Class `TestWizardAccessibility`

```python
@pytest.mark.regression
@pytest.mark.a11y
class TestWizardAccessibility:
    def test_wizard_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
```

| **Given** | Wizard on step 1 (default state) |
| **Then** | No critical/serious a11y violations |

Multi-step forms are prone to label and focus issues — this test ensures a WCAG baseline.

---

## Summary of concepts learned

| Concept | Where it appears |
|---------|------------------|
| Private helpers (`_`) | Composing long flows |
| Test Data Factory | `create_personal_step`, `create_preferences_step` |
| Faker | Dynamic data per run |
| Regex on CSS classes | `\bactive\b`, `\bdone\b` |
| `check(force=True)` | Styled/hidden checkboxes |
| Route interception | `page.route` + `route.fulfill` |
| JSON fixtures | `read_fixture("lookups/countries.json")` |
| Stepper UI | `wizard-step-N` indicators, `wizard-panel-N` panels |
| Markers | `smoke`, `critical`, `a11y`, `regression` |
