# TestFlow PyTest — Documentação de Treinamento

Material didático que explica **bloco a bloco** cada arquivo de teste do projeto. Ideal para novos alunos que estão aprendendo PyTest, Playwright e automação E2E.

Cada documento aponta para o arquivo de teste correspondente com um link relativo.

**Idioma:** Português · [English](../en/README.md)

---

## Como usar este material

1. Leia o doc da suite que você vai executar ou manter.
2. Abra o [arquivo de teste](..) linkado no topo do documento.
3. Siga a explicação seção por seção enquanto lê o código.
4. Execute a suite localmente para ver o comportamento na prática:

```bash
pytest tests/smoke -v          # exemplo: smoke
pytest tests/auth/test_login.py -v  # um arquivo específico
```

---

## Índice por suite

### Smoke & Auth

| Suite | Documentação | Arquivo de teste |
|-------|--------------|------------------|
| Smoke — navegação | [test_navigation.md](tests/smoke/test_navigation.md) | [`tests/smoke/test_navigation.py`](../../tests/smoke/test_navigation.py) |
| Auth — login | [test_login.md](tests/auth/test_login.md) | [`tests/auth/test_login.py`](../../tests/auth/test_login.py) |

### Páginas autenticadas

| Suite | Documentação | Arquivo de teste |
|-------|--------------|------------------|
| Dashboard | [test_dashboard.md](tests/dashboard/test_dashboard.md) | [`tests/dashboard/test_dashboard.py`](../../tests/dashboard/test_dashboard.py) |
| Team | [test_team.md](tests/team/test_team.md) | [`tests/team/test_team.py`](../../tests/team/test_team.py) |
| Settings | [test_settings.md](tests/settings/test_settings.md) | [`tests/settings/test_settings.py`](../../tests/settings/test_settings.py) |
| Components | [test_components.md](tests/components/test_components.md) | [`tests/components/test_components.py`](../../tests/components/test_components.py) |
| Wizard | [test_wizard.md](tests/wizard/test_wizard.md) | [`tests/wizard/test_wizard.py`](../../tests/wizard/test_wizard.py) |
| Activity | [test_activity.md](tests/activity/test_activity.md) | [`tests/activity/test_activity.py`](../../tests/activity/test_activity.py) |
| Advanced | [test_advanced.md](tests/advanced/test_advanced.md) | [`tests/advanced/test_advanced.py`](../../tests/advanced/test_advanced.py) |
| UI States | [test_states.md](tests/states/test_states.md) | [`tests/states/test_states.py`](../../tests/states/test_states.py) |

### Visual & API

| Suite | Documentação | Arquivo de teste |
|-------|--------------|------------------|
| Visual regression | [test_visual.md](tests/visual/test_visual.md) | [`tests/visual/test_visual.py`](../../tests/visual/test_visual.py) |
| API — auth | [test_auth_api.md](tests/api/test_auth_api.md) | [`tests/api/test_auth_api.py`](../../tests/api/test_auth_api.py) |
| API — users & health | [test_users_api.md](tests/api/test_users_api.md) | [`tests/api/test_users_api.py`](../../tests/api/test_users_api.py) |
| API — rules / JSON Patch | [test_rules_api.md](tests/api/test_rules_api.md) | [`tests/api/test_rules_api.py`](../../tests/api/test_rules_api.py) |

---

## Conceitos transversais

Os documentos cobrem, entre outros:

- **PyTest:** markers (`@pytest.mark.smoke`), fixtures (`autouse`, escopo `module`/`class`), parametrização
- **Playwright:** `page`, `expect`, `get_by_test_id`, interceptação (`page.route`), diálogos nativos
- **Autenticação:** `login_via_api`, `visit_authenticated`, `visit_with_token`, `sessionStorage`
- **Page Object Model:** classes em `pages/`
- **Dados de teste:** fixtures JSON em `fixtures/`, factories em `support/factories/`
- **Acessibilidade:** `check_a11y` com axe-core
- **API pura:** fixture `api_request` (sem browser)

---

## Estrutura de pastas

```
docs/
├── README.md                          ← seletor de idioma
├── pytest-technical-interview-questions.md  ← banco de perguntas para entrevistas
├── pt/
│   ├── README.md                      ← índice (Português)
│   └── tests/                         ← docs em Português
└── en/
    ├── README.md                      ← index (English)
    └── tests/                         ← English docs (mirror)
```

---

## Outros recursos

| Recurso | Descrição |
|---------|-----------|
| [`pytest-technical-interview-questions.md`](../pytest-technical-interview-questions.md) | Banco de perguntas técnicas para entrevistas |
| [`slides/`](../slides/) | Apresentação Reveal.js |
