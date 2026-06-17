# TestFlow PyTest — Training Documentation

Instructional material that explains **block by block** each test file in the project. Ideal for new students learning PyTest, Playwright, and E2E automation.

Each document links to the corresponding test file with a relative path.

**Language:** English · [Português](../pt/README.md)

---

## How to use this material

1. Read the doc for the suite you will run or maintain.
2. Open the [test file](..) linked at the top of the document.
3. Follow the explanation section by section while reading the code.
4. Run the suite locally to see behavior in practice:

```bash
pytest tests/smoke -v          # example: smoke
pytest tests/auth/test_login.py -v  # a specific file
```

---

## Index by suite

### Smoke & Auth

| Suite | Documentation | Test file |
|-------|---------------|-----------|
| Smoke — navigation | [test_navigation.md](tests/smoke/test_navigation.md) | [`tests/smoke/test_navigation.py`](../../tests/smoke/test_navigation.py) |
| Auth — login | [test_login.md](tests/auth/test_login.md) | [`tests/auth/test_login.py`](../../tests/auth/test_login.py) |

### Authenticated pages

| Suite | Documentation | Test file |
|-------|---------------|-----------|
| Dashboard | [test_dashboard.md](tests/dashboard/test_dashboard.md) | [`tests/dashboard/test_dashboard.py`](../../tests/dashboard/test_dashboard.py) |
| Team | [test_team.md](tests/team/test_team.md) | [`tests/team/test_team.py`](../../tests/team/test_team.py) |
| Settings | [test_settings.md](tests/settings/test_settings.md) | [`tests/settings/test_settings.py`](../../tests/settings/test_settings.py) |
| Components | [test_components.md](tests/components/test_components.md) | [`tests/components/test_components.py`](../../tests/components/test_components.py) |
| Wizard | [test_wizard.md](tests/wizard/test_wizard.md) | [`tests/wizard/test_wizard.py`](../../tests/wizard/test_wizard.py) |
| Activity | [test_activity.md](tests/activity/test_activity.md) | [`tests/activity/test_activity.py`](../../tests/activity/test_activity.py) |
| Advanced | [test_advanced.md](tests/advanced/test_advanced.md) | [`tests/advanced/test_advanced.py`](../../tests/advanced/test_advanced.py) |
| UI States | [test_states.md](tests/states/test_states.md) | [`tests/states/test_states.py`](../../tests/states/test_states.py) |

### Visual & API

| Suite | Documentation | Test file |
|-------|---------------|-----------|
| Visual regression | [test_visual.md](tests/visual/test_visual.md) | [`tests/visual/test_visual.py`](../../tests/visual/test_visual.py) |
| API — auth | [test_auth_api.md](tests/api/test_auth_api.md) | [`tests/api/test_auth_api.py`](../../tests/api/test_auth_api.py) |
| API — users & health | [test_users_api.md](tests/api/test_users_api.md) | [`tests/api/test_users_api.py`](../../tests/api/test_users_api.py) |
| API — rules / JSON Patch | [test_rules_api.md](tests/api/test_rules_api.md) | [`tests/api/test_rules_api.py`](../../tests/api/test_rules_api.py) |

---

## Cross-cutting concepts

The documents cover, among other topics:

- **PyTest:** markers (`@pytest.mark.smoke`), fixtures (`autouse`, `module`/`class` scope), parametrization
- **Playwright:** `page`, `expect`, `get_by_test_id`, interception (`page.route`), native dialogs
- **Authentication:** `login_via_api`, `visit_authenticated`, `visit_with_token`, `sessionStorage`
- **Page Object Model:** classes in `pages/`
- **Test data:** JSON fixtures in `fixtures/`, factories in `support/factories/`
- **Accessibility:** `check_a11y` with axe-core
- **Pure API:** `api_request` fixture (no browser)

---

## Folder structure

```
docs/
├── README.md                          ← language selector
├── pt/
│   ├── README.md                      ← Portuguese index
│   └── tests/
│       ├── smoke/test_navigation.md
│       ├── auth/test_login.md
│       ├── dashboard/test_dashboard.md
│       ├── team/test_team.md
│       ├── settings/test_settings.md
│       ├── components/test_components.md
│       ├── wizard/test_wizard.md
│       ├── activity/test_activity.md
│       ├── advanced/test_advanced.md
│       ├── states/test_states.md
│       ├── visual/test_visual.md
│       └── api/
│           ├── test_auth_api.md
│           ├── test_users_api.md
│           └── test_rules_api.md
└── en/
    ├── README.md                      ← this index (English)
    └── tests/                         ← English docs (mirror)
```

Each `.md` in `docs/en/tests/` and `docs/pt/tests/` mirrors the homonymous folder under `tests/`.

---

## Other resources

| Resource | Description |
|----------|-------------|
| [`pytest-technical-interview-questions.md`](../pytest-technical-interview-questions.md) | Technical interview question bank (Portuguese) |
| [`slides/`](../slides/) | Reveal.js presentation |
