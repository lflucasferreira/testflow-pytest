# Visual Tests — Screenshot regression

**Source file:** [`../../../../tests/visual/test_visual.py`](../../../../tests/visual/test_visual.py)

---

## Purpose

This module implements **visual regression tests** with Playwright: captures screenshots of key pages and compares them against stored **baselines**. Any difference in layout, color, font, or positioning fails the test.

Pages covered:

| Case | Page | Authentication |
|------|------|----------------|
| `TC.VISUAL_LOGIN` | `/web/login.html` | No (public) |
| `TC.VISUAL_DASHBOARD` | `/web/dashboard.html` | Yes |
| `TC.VISUAL_COMPONENTS` | `/web/components.html` | Yes |

Ideal for training **PyTest parametrization**, visual stabilization, and snapshot naming.

---

## Prerequisites

| Item | Description |
|------|-------------|
| Server | Sandbox accessible at `BASE_URL` |
| Baselines | Playwright snapshot directory (generated on first run or versioned in the repo) |
| Credentials | For dashboard and components via `visit_authenticated` |
| Markers | `visual`, `regression` |

**Execution:**

```bash
pytest tests/visual/test_visual.py -v
pytest tests/visual/test_visual.py -m visual
```

**Update baselines (when visual change is intentional):**

```bash
pytest tests/visual/test_visual.py --update-snapshots
```

(Exact flag may vary per `pytest-playwright` configuration in the project.)

---

## Markers used

| Marker | Function |
|--------|----------|
| `visual` | Identifies screenshot suite — excluded from fast API/smoke runs |
| `regression` | Part of full regression |

---

## Structure overview

```
test_visual.py
├── imports
├── helper: _wait_for_fonts
└── TestVisualSnapshots
    └── test_visual_baseline (parametrized × 3 scenarios)
```

---

## Imports — block by block

### `import pytest`

Used for `@pytest.mark` and `@pytest.mark.parametrize`.

---

### `from playwright.sync_api import Page, expect`

- **`Page`**: navigation and screenshot capture via locator.
- **`expect`**: `to_have_screenshot` integrates visual comparison with retry.

---

### `from support.auth import visit_authenticated`

API login + navigation — used for dashboard and components scenarios.

---

### `from support.config import BASE_URL`

Environment base URL (e.g. `http://localhost:3000`). Visual login uses `page.goto(f"{BASE_URL}/web/login.html")` with an absolute URL.

---

### `from support.constants.test_cases import TC`

Class with standardized test case IDs:

| Constant | ID |
|----------|-----|
| `TC.VISUAL_LOGIN` | `TC-9001` |
| `TC.VISUAL_DASHBOARD` | `TC-9002` |
| `TC.VISUAL_COMPONENTS` | `TC-9003` |

Used as `case_id` in parametrization and in the PNG filename.

---

## Helper: `_wait_for_fonts`

```python
def _wait_for_fonts(page: Page) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("() => document.fonts.ready")
```

### Why does it exist?

Flaky screenshots often come from:

1. **Web fonts** still loading (FOUT/FOIT)
2. **Animations** in motion at capture time

### Block by block

| Line | Effect |
|------|--------|
| `emulate_media(reduced_motion="reduce")` | Respects CSS `prefers-reduced-motion` — disables or reduces animations |
| `document.fonts.ready` | Browser Promise that resolves when fonts declared in `@font-face` are ready |

**Playwright concept:** `page.evaluate` runs JavaScript in the page context — here we wait for stability before the screenshot.

**Convention:** `_` prefix indicates a module-private function (not exported).

---

## Class `TestVisualSnapshots`

```python
@pytest.mark.visual
@pytest.mark.regression
class TestVisualSnapshots:
```

Groups a single parametrized method covering three baselines.

---

## Parametrization: `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize(
    "case_id,title,setup",
    [
        (
            TC.VISUAL_LOGIN,
            "login page baseline",
            lambda page, api_request: page.goto(f"{BASE_URL}/web/login.html"),
        ),
        (
            TC.VISUAL_DASHBOARD,
            "dashboard baseline",
            lambda page, api_request: visit_authenticated(page, api_request, "/web/dashboard.html"),
        ),
        (
            TC.VISUAL_COMPONENTS,
            "components baseline",
            lambda page, api_request: visit_authenticated(page, api_request, "/web/components.html"),
        ),
    ],
    ids=[TC.VISUAL_LOGIN, TC.VISUAL_DASHBOARD, TC.VISUAL_COMPONENTS],
)
```

### Parameters

| Name | Type | Role |
|------|------|------|
| `case_id` | `str` | Case ID (`TC-9001`, etc.) |
| `title` | `str` | Human-readable description for PNG name |
| `setup` | `callable` | Lambda that navigates to the desired state |

### `ids=`

Defines short names in PyTest reports:

```
test_visual_baseline[TC-9001]
test_visual_baseline[TC-9002]
test_visual_baseline[TC-9003]
```

**PyTest concept:** parametrization avoids copy/pasting three nearly identical methods — DRY with tabular data.

**Setup lambdas:** receive `(page, api_request)` for flexibility; login uses only `page`, authenticated cases use both.

---

## Method `test_visual_baseline`

```python
def test_visual_baseline(
    self,
    page: Page,
    request,
    case_id: str,
    title: str,
    setup,
) -> None:
```

### Injected fixtures and parameters

| Parameter | Source |
|-----------|--------|
| `page` | pytest-playwright |
| `request` | PyTest — access to config, markers, node (useful for snapshot plugins) |
| `case_id`, `title`, `setup` | Parametrize |

---

### Step 1 — Page setup

```python
setup(page, api_request)
```

**When:** runs the lambda for the scenario (goto login or authenticated visit).

**Note:** `api_request` is resolved implicitly by PyTest when calling `setup(page, api_request)` — `api_request` fixture must exist in `conftest.py`.

---

### Step 2 — Readiness gate and root selection

```python
if case_id == TC.VISUAL_LOGIN:
    expect(page.get_by_test_id("login-email")).to_be_visible()
    root = page.locator("body")
elif case_id == TC.VISUAL_DASHBOARD:
    expect(page.get_by_test_id("page-dashboard")).to_be_attached()
    root = page.get_by_test_id("page-dashboard")
else:
    expect(page.get_by_test_id("page-components")).to_be_attached()
    root = page.get_by_test_id("page-components")
```

| Scenario | Gate | Captured region |
|----------|------|-----------------|
| Login | Email field visible | Full `body` (public page without authenticated shell) |
| Dashboard | `page-dashboard` attached | Main container only (excludes peripheral noise) |
| Components | `page-components` attached | Components page container |

**Visual testing concept:** cropping (`root` = specific locator) reduces false positives from dynamic header/footer.

---

### Step 3 — Stabilization

```python
_wait_for_fonts(page)
```

**Given (stabilized):** fonts loaded, motion reduced.

---

### Step 4 — Screenshot assertion

```python
expect(root).to_have_screenshot(name=f"{case_id.lower()}-{title.replace(' ', '-')}.png")
```

Example generated name: `tc-9001-login-page-baseline.png`

**Playwright concept:**

- First run: writes baseline in the test snapshot folder.
- Subsequent runs: compares pixel by pixel (with configurable threshold in the project).
- Failure: visual diff attached to the report (depending on reporter).

**Name formatting:** `case_id.lower()` + title with spaces → hyphens — portable filenames.

---

## Given / When / Then per scenario

### Login

| Phase | Action |
|-------|--------|
| Given | Clean browser |
| When | `goto` login |
| Then | Email visible → screenshot of body |

### Dashboard / Components

| Phase | Action |
|-------|--------|
| Given | Authenticated session |
| When | `visit_authenticated` to route |
| Then | Page marker present → screenshot of container |

---

## Concepts for students

### Why visual tests?

- Catch regressions functional tests miss (broken CSS, overflow, alignment).
- Cost: baselines need maintenance; environments must be consistent (OS, DPI, fonts).

### Stabilization

- Fonts, animations, dynamic data (dates, avatars) are snapshot enemies.
- This project mitigates with `_wait_for_fonts` and cropped regions.

### PyTest parametrize vs separate classes

Parametrize scales when **assert logic is identical** and only data/setup changes.

---

## Learning checklist

- [ ] Explain difference between `body` snapshot vs `page-dashboard`
- [ ] Describe the role of `document.fonts.ready`
- [ ] Run visual test and locate generated snapshot folder
- [ ] Know when to use `--update-snapshots`
- [ ] Relate `TC.VISUAL_*` to IDs in `support/constants/test_cases.py`
