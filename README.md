# testflow-pytest

PyTest + Playwright automation suite for [TestFlow](https://github.com/qaschoolbr/testflow) — mirror of the Cypress suite in `testflow-cypress` and Playwright suite in `testflow-playwright`.

## Test coverage

| Suite | Module | What it covers |
|---|---|---|
| `smoke` | `tests/smoke/test_navigation.py` | All pages load, sidebar nav, logout, health API |
| `auth` | `tests/auth/test_login.py` | Login UI/API, validation, sessionStorage, redirect, logout, a11y |
| `dashboard` | `tests/dashboard/test_dashboard.py` | KPIs, activity feed, suite health, new run modal |
| `team` | `tests/team/test_team.py` | Table search, filters, sort, pagination, invite, inline edit |
| `settings` | `tests/settings/test_settings.py` | Settings form, toggles, password, 2FA, webhooks, a11y |
| `components` | `tests/components/test_components.py` | Buttons, modal, tabs, accordion, a11y |
| `wizard` | `tests/wizard/test_wizard.py` | Multi-step flow, validation, review, a11y |
| `activity` | `tests/activity/test_activity.py` | API mocks, counter, pipeline, countries fixture |
| `advanced` | `tests/advanced/test_advanced.py` | Shadow DOM, iframe, external links, mobile |
| `states` | `tests/states/test_states.py` | Skeleton, empty, error, partial loading, a11y |
| `visual` | `tests/visual/test_visual.py` | Screenshot baselines (login, sidebar, components) |
| `api` | `tests/api/*.py` | REST auth/users, golden roles, JSON Patch rules engine |

Traceable test case IDs use the `[TC-xxxx]` prefix — see `support/constants/test_cases.py`.

## Prerequisites

- Python 3.11+
- TestFlow app running locally on port `5050`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Corporate proxy (Zscaler / SSL errors)

If `playwright install chromium` fails with certificate errors:

```bash
export NODE_TLS_REJECT_UNAUTHORIZED=0
playwright install chromium
```

Or configure `NODE_EXTRA_CA_CERTS` with your corporate root CA (see `testflow-playwright` README).

### Credentials

| Field | Default | Override |
|---|---|---|
| Email | `demo@automation.io` | `DEMO_EMAIL` |
| Password | `Demo123!` | `DEMO_PASSWORD` |

## Running the app

```bash
docker run --rm -p 5050:5050 qaschool/testflow:latest
```

## Running tests

```bash
# Full suite
pytest

# By marker
pytest -m smoke
pytest -m regression
pytest -m critical
pytest -m a11y
pytest -m api
pytest -m visual

# By suite directory
pytest tests/smoke
pytest tests/auth
pytest tests/dashboard
pytest tests/team
pytest tests/settings
pytest tests/components
pytest tests/wizard
pytest tests/activity
pytest tests/advanced
pytest tests/states
pytest tests/api
pytest tests/visual

# Visual baselines (first run or update)
pytest tests/visual --update-snapshots

# Headed browser
pytest --headed

# Parallel (optional)
pytest -n auto
```

## Project structure

```
testflow-pytest/
├── conftest.py              # Session auth cache, api_request fixture, a11y helper
├── fixtures/                # JSON fixtures + schemas (mirrors Cypress)
├── pages/                   # Page Object Model
├── support/
│   ├── auth.py              # API login + sessionStorage seeding
│   ├── api/                 # Rules engine client
│   ├── constants/           # TC ids, HTTP status, viewports
│   ├── factories/           # Test data factories
│   ├── helpers/             # Schema validation, fixture loader
│   └── utilities/           # JSON Patch, retry/poll
└── tests/                   # PyTest specs by feature
```

## CI

GitHub Actions workflow runs each suite in parallel against the `qaschool/testflow:latest` Docker service.

## Slides & training docs

- **Slides (Reveal.js):** `npm install && npm run slides` → http://localhost:3336/docs/slides/
- **Guia passo a passo (HTML):** http://localhost:3336/docs/slides/guia-completo.html
- **Português:** [`docs/pt/README.md`](docs/pt/README.md) — walkthrough bloco a bloco de cada arquivo de teste
- **English:** [`docs/en/README.md`](docs/en/README.md) — same training material in English
- **Entrevistas técnicas:** [`docs/pytest-technical-interview-questions.md`](docs/pytest-technical-interview-questions.md) — 320+ perguntas `[SLIDE]` / `[EXTRA]`
- Run locally: TestFlow on port `5050`, then `pytest tests/<suite> -v`

## Technologies

- [PyTest](https://pytest.org/)
- [Playwright for Python](https://playwright.dev/python/)
- [axe-playwright-python](https://github.com/nickcolley/axe-playwright-python)
- Page Object Model with `data-testid` selectors

## License

Same as TestFlow / parent automation projects.
