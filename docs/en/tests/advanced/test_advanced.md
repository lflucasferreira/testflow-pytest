# Advanced Tests — Shadow DOM, iframes, and viewport

**Source file:** [`../../../../tests/advanced/test_advanced.py`](../../../../tests/advanced/test_advanced.py)

---

## Purpose

This module validates the **Advanced** page (`/web/advanced.html`), which concentrates the TestFlow sandbox's more complex front-end scenarios:

- **Shadow DOM** — encapsulated content outside the main DOM tree
- **iframe** — embedded content loading
- **External links** — `href` and `target` attributes
- **Responsive viewport** — behavior at mobile vs desktop sizes
- **Navigation** — button that takes the user to another route

The tests are **UI E2E** with Playwright (sync mode) and serve as training material for locators, web-first assertions, and setup fixtures.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Environment | Sandbox server running (`BASE_URL` configured) |
| Authentication | Valid demo credentials (`DEMO_EMAIL`, `DEMO_PASSWORD`) |
| Dependencies | `pytest`, `playwright`, `pytest-playwright` plugin |
| Global fixtures | `page` (Playwright), `api_request` (defined in `conftest.py`) |
| Browser | Chromium / Firefox / WebKit per project configuration |

**Run this file only:**

```bash
pytest tests/advanced/test_advanced.py -v
```

**Filter by marker:**

```bash
pytest tests/advanced/test_advanced.py -m smoke
pytest tests/advanced/test_advanced.py -m regression
```

---

## Markers used

| Marker | Where it appears | Meaning |
|--------|------------------|---------|
| `@pytest.mark.regression` | `TestAdvanced` class | Full regression suite |
| `@pytest.mark.smoke` | `test_renders_shadow_dom_section`, `test_renders_shadow_section_at_mobile_viewport` | Fast subset for CI gate |

Markers are registered in `conftest.py` via `pytest_configure`.

---

## Structure overview

```
test_advanced.py
├── imports
├── autouse fixture: advanced_page
└── class TestAdvanced
    ├── test_renders_shadow_dom_section
    ├── test_accesses_content_inside_shadow_root
    ├── test_loads_demo_iframe
    ├── test_shows_external_link_with_target_blank
    ├── test_renders_shadow_section_at_mobile_viewport
    └── test_navigates_with_page_finish_button
```

---

## Imports — block by block

### `import re`

Python standard library for **regular expressions**. Used to validate URLs and attributes with flexible patterns (e.g. `href` starting with `http`, non-empty `src`).

**PyTest/Playwright concept:** assertions like `to_have_attribute("src", re.compile(r".+"))` accept regex from the `re` module, not just literal strings.

---

### `import pytest`

Test framework. Provides:

- `@pytest.fixture` — reusable setup/teardown
- `@pytest.mark.*` — categorization and command-line filters
- Automatic discovery of `Test*` classes and `test_*` methods

---

### `from playwright.sync_api import Page, expect`

| Symbol | Role |
|--------|------|
| `Page` | Represents a browser tab; entry point for navigation, clicks, and locators |
| `expect` | Playwright **web-first** assertion API — automatically waits until the condition is true (auto-retry) |

**Playwright concept:** prefer `expect(locator).to_be_visible()` over `assert locator.is_visible()`, because `expect` waits for UI stability.

---

### `from support.auth import visit_authenticated`

Project helper that:

1. Obtains a token via API (`fetch_auth_token`)
2. Injects the session into the browser (`inject_auth` + `sessionStorage`)
3. Navigates to the given `path` already authenticated

Avoids repeating manual login in every protected-page test.

---

### `from support.constants.viewports import DESKTOP, MOBILE`

Screen dimension constants:

| Constant | Value |
|----------|-------|
| `DESKTOP` | `{"width": 1280, "height": 800}` |
| `MOBILE` | `{"width": 375, "height": 812}` |

Used with `page.set_viewport_size(...)`.

---

## Fixture: `advanced_page`

```python
@pytest.fixture(autouse=True)
def advanced_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/advanced.html")
    expect(page.get_by_test_id("page-advanced")).to_be_attached()
```

### Parameters injected by PyTest

| Parameter | Source | Function |
|-----------|--------|----------|
| `page` | pytest-playwright fixture | Browser page instance |
| `api_request` | `conftest.py` | HTTP context for API login |

### Behavior

- **`autouse=True`**: runs automatically before **each** test in the module, without declaring the fixture name in test methods.
- **Given:** authenticated user at `/web/advanced.html`.
- **Then:** root element `page-advanced` is attached to the DOM.

**PyTest concept:** `autouse` fixtures centralize common setup and keep tests lean — each method receives a page already prepared.

---

## Class `TestAdvanced`

```python
@pytest.mark.regression
class TestAdvanced:
```

Groups tests related to the Advanced page. PyTest collects all `test_*` methods inside the class.

The `regression` marker on the class applies conceptually to the group (depending on PyTest version, class markers may need to be repeated on methods for `-m` filters; here smoke methods have their own marker).

---

### `test_renders_shadow_dom_section`

```python
@pytest.mark.smoke
def test_renders_shadow_dom_section(self, page: Page) -> None:
    expect(page.get_by_test_id("section-shadow")).to_be_visible()
    expect(page.get_by_test_id("shadow-host")).to_be_attached()
```

| Phase | Action |
|-------|--------|
| **Given** | Advanced page loaded (`advanced_page` fixture) |
| **When** | (No interaction — static rendering test) |
| **Then** | Shadow section visible; shadow DOM host attached |

**Locators:** `get_by_test_id` uses the `data-testid` attribute — a stable, recommended strategy.

**Playwright difference:**

- `to_be_visible()` — element visible to the user (not `display:none`, etc.)
- `to_be_attached()` — present in the DOM (may be hidden)

---

### `test_accesses_content_inside_shadow_root`

```python
def test_accesses_content_inside_shadow_root(self, page: Page) -> None:
    shadow_content = page.get_by_test_id("shadow-host").locator("*")
    expect(shadow_content.first).to_be_attached()
    assert shadow_content.count() >= 1
```

| Phase | Action |
|-------|--------|
| **Given** | `shadow-host` in the DOM |
| **When** | Locator descends to children (`locator("*")`) |
| **Then** | At least one child node exists inside the shadow root |

**Playwright concept:** from Playwright 1.x+, locators automatically traverse **open shadow roots** when starting from a known host.

**Mixed styles:** `expect(...).to_be_attached()` (web-first) + `assert shadow_content.count() >= 1` (immediate count). In flaky scenarios, prefer `expect(...).to_have_count(n)`.

---

### `test_loads_demo_iframe`

```python
def test_loads_demo_iframe(self, page: Page) -> None:
    iframe = page.get_by_test_id("demo-iframe")
    expect(iframe).to_be_visible()
    expect(iframe).to_have_attribute("src", re.compile(r".+"))
```

| Phase | Action |
|-------|--------|
| **Given** | Advanced page |
| **When** | Inspects the demo iframe |
| **Then** | Iframe visible; `src` attribute populated (regex `.+` = one or more characters) |

**Playwright concept:** interacting *inside* the iframe would require `page.frame_locator(...)` or `content_frame()`; here we only validate the outer `<iframe>` element.

---

### `test_shows_external_link_with_target_blank`

```python
def test_shows_external_link_with_target_blank(self, page: Page) -> None:
    link = page.get_by_test_id("external-link")
    expect(link).to_have_attribute("href", re.compile(r"http"))
```

| Phase | Action |
|-------|--------|
| **Given** | External link rendered |
| **When** | Reads `href` attribute |
| **Then** | URL contains `http` (http or https) |

Does not click the link — avoids opening a new tab/window and CI flakiness.

---

### `test_renders_shadow_section_at_mobile_viewport`

```python
@pytest.mark.smoke
def test_renders_shadow_section_at_mobile_viewport(self, page: Page) -> None:
    page.set_viewport_size(MOBILE)
    expect(page.get_by_test_id("section-shadow")).to_be_visible()
    page.set_viewport_size(DESKTOP)
```

| Phase | Action |
|-------|--------|
| **Given** | Page at desktop viewport (default) |
| **When** | Resizes to `MOBILE` (375×812) |
| **Then** | Shadow section remains visible |
| **Cleanup** | Restores `DESKTOP` so following tests in the same session are unaffected |

**Playwright concept:** `set_viewport_size` simulates device size; it does not emulate full user-agent (for that, use `page.emulate(...)` or device presets).

---

### `test_navigates_with_page_finish_button`

```python
def test_navigates_with_page_finish_button(self, page: Page) -> None:
    page.get_by_test_id("page-finish-btn").click()
    expect(page).not_to_have_url(re.compile(r"/web/advanced\.html"))
```

| Phase | Action |
|-------|--------|
| **Given** | User on Advanced page |
| **When** | Clicks `page-finish-btn` |
| **Then** | URL is no longer `/web/advanced.html` |

**Playwright concept:** `expect(page).not_to_have_url(...)` waits for navigation to complete — more robust than reading `page.url` immediately after the click.

---

## Consolidated concepts for students

### PyTest

- **Fixtures** compose dependencies (`page` → `advanced_page` → test).
- **`autouse`** eliminates boilerplate in test parameters.
- **Markers** enable selective pipelines (`-m smoke`).

### Playwright

- **`get_by_test_id`** — stable locator.
- **`expect`** — assertions with built-in retry.
- **Viewport** — responsive tests without a physical device.
- **Shadow DOM / iframe** — common patterns in modern design systems.

### Given / When / Then in this module

Most tests are **rendering + assertion** (Given + Then). Only navigation, clicks, and viewport changes introduce an explicit **When**.

---

## Learning checklist

- [ ] Explain why `advanced_page` uses `autouse=True`
- [ ] Differentiate `to_be_visible` vs `to_be_attached`
- [ ] Describe how Playwright accesses an open shadow root
- [ ] Run the suite with `-m smoke` and interpret the result
- [ ] Propose a new test: validate `target="_blank"` on the external link
