# Testes de API — Usuários, Health e Interceptação de Fixtures

**Arquivo-fonte:** [`../../../../tests/api/test_users_api.py`](../../../../tests/api/test_users_api.py)

---

## Propósito

Este módulo cobre endpoints e comportamentos relacionados a **usuários** e **saúde da API**, além de demonstrar:

- Listagem `GET /api/users` com validação de schema e formato de email
- Endpoint `GET /health` com SLA de latência
- Endpoints de simulação de erro (`/api/errors/404`, `/api/errors/422`)
- **Mock de API na UI** com `page.route` + arquivos JSON de fixture
- Helper `read_fixture` para dados estáticos reutilizáveis

Combina testes **API-only** e **E2E com interceptação de rede**.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Servidor | Rotas `/api/users`, `/health`, `/api/errors/*`, página `/web/activity.html` |
| Fixtures JSON | `users/empty-list.json`, `lookups/countries.json` |
| Auth | `visit_authenticated` para testes de activity page |
| Helpers | `validate_schema`, `read_fixture` |

```bash
pytest tests/api/test_users_api.py -v
pytest tests/api/test_users_api.py -m smoke
```

---

## Markers utilizados

| Marker | Onde |
|--------|------|
| `api` | Todas as classes |
| `regression` | Todas exceto combinação smoke em `TestHealth` |
| `smoke` | `TestGetUsers.test_returns_status_200`, classe `TestHealth` e seu teste de status |

---

## Visão geral da estrutura

```
test_users_api.py
├── imports
├── fixture: users_list_response (scope=class)
├── TestGetUsers
├── TestHealth
├── TestErrorSimulationEndpoints
└── TestFixtureInterceptOnActivityPage
    ├── fixture autouse: activity_page
    ├── test_mock_api_get_serves_empty_users_fixture_on_fetch
    └── test_read_fixture_loads_countries_lookup
```

---

## Imports — bloco a bloco

### `import re`

Expressão regular para validar formato de email nos objetos user.

---

### `import time`

Medição de `duration_ms` na fixture e no teste de health.

---

### `import pytest`

Fixtures, markers, classes de teste.

---

### `from playwright.sync_api import APIRequestContext, Page, expect`

| Símbolo | Uso |
|---------|-----|
| `APIRequestContext` | GET health, errors, users (API pura) |
| `Page` | Activity page com intercept |
| `expect` | Asserção de texto na UI após fetch |

---

### `from support.auth import visit_authenticated`

Navega autenticado para páginas web — usado na fixture `activity_page`.

---

### `from support.config import BASE_URL`

URL base para montagem de paths absolutos.

---

### `from support.helpers import validate_schema`

Validador leve de schema dict `{ campo: "string" | ... }` — garante tipos mínimos no JSON.

---

### `from support.helpers.fixtures import read_fixture`

Carrega arquivos JSON do diretório de fixtures do projeto e retorna `dict`/`list` Python.

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

**Given para `TestGetUsers`:** uma resposta GET `/api/users` cacheada por classe.

Diferença vs auth: não captura headers; foco em body e performance.

---

## Classe `TestGetUsers`

---

### `test_returns_status_200`

```python
@pytest.mark.smoke
def test_returns_status_200(self, users_list_response: dict) -> None:
    assert users_list_response["status"] == 200
```

Smoke gate — lista de usuários acessível.

---

### `test_responds_within_2000ms`

```python
def test_responds_within_2000ms(self, users_list_response: dict) -> None:
    assert users_list_response["duration_ms"] < 2000
```

SLA de 2s usando duração já medida na fixture (sem segundo GET).

---

### `test_body_has_a_users_array`

```python
def test_body_has_a_users_array(self, users_list_response: dict) -> None:
    users = users_list_response["body"]["users"]
    assert isinstance(users, list)
    assert len(users) > 0
```

**Contrato:** resposta `{ "users": [ ... ] }` com pelo menos um item.

---

### `test_each_user_matches_json_schema`

```python
def test_each_user_matches_json_schema(self, users_list_response: dict) -> None:
    for user in users_list_response["body"]["users"]:
        validate_schema(user, {"name": "string", "email": "string", "role": "string"})
```

Itera todos os usuários — falha no primeiro que não tiver `name`, `email`, `role` como strings.

**Conceito:** schema validation em testes de contrato impede regressões silenciosas de formato.

---

### `test_all_emails_are_valid_format`

```python
def test_all_emails_are_valid_format(self, users_list_response: dict) -> None:
    email_regex = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    for user in users_list_response["body"]["users"]:
        assert email_regex.match(user["email"])
```

Validação sintática básica de email (não valida DNS ou RFC completo).

---

## Classe `TestHealth`

```python
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
class TestHealth:
```

Endpoint de **liveness/readiness** simplificado.

---

### `test_returns_status_200`

```python
@pytest.mark.smoke
def test_returns_status_200(self, api_request: APIRequestContext) -> None:
    response = api_request.get(f"{BASE_URL}/health")
    assert response.status == 200
```

Request fresco por teste (function-scoped `api_request`).

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

Health deve ser **mais rápido** que endpoints de negócio — SLA 1s.

---

## Classe `TestErrorSimulationEndpoints`

Sandbox expõe rotas que retornam erros fixos para treinar assert de status e corpo.

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

**Nota:** usa path relativo `"/api/errors/404"` — funciona porque `api_request` foi criado com `base_url=BASE_URL`.

---

### `test_422_response_has_a_non_empty_error_or_message_field`

Mesmo padrão para 422 — garante mensagem útil ao cliente.

---

## Classe `TestFixtureInterceptOnActivityPage`

Integração UI + mock de backend.

---

### Fixture autouse: `activity_page`

```python
@pytest.fixture(autouse=True)
def activity_page(self, page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/activity.html")
```

**Escopo:** definida **dentro da classe** — PyTest aplica autouse só aos testes desta classe.

**Given:** usuário autenticado na página Activity.

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

| Fase | Descrição |
|------|-----------|
| **Given** | Rota `/api/users` retorna JSON estático da fixture |
| **When** | Clique em buscar usuários |
| **Then** | UI exibe “Fetched 0 users” |

**Conceitos:**

- **`route.fulfill(json=...)`** — Playwright serializa dict para response
- **`read_fixture("users/empty-list.json")`** — desacopla payload do teste
- **`expect_response`** — sincroniza com request disparado pelo clique

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

Teste **unitário do helper** — não usa browser nem API.

Valida estrutura mínima do arquivo de lookup (code + name).

---

## Given / When / Then — mapa rápido

| Teste | Given | When | Then |
|-------|-------|------|------|
| GET users 200 | Fixture cache | — | status 200 |
| Schema users | Lista populada | loop | campos string |
| Health 1s | API up | GET /health | < 1000ms |
| Mock empty users | Route + activity page | click fetch | texto 0 users |
| read_fixture | arquivo JSON | load | countries válidos |

---

## Conceitos para estudantes

### APIRequestContext vs page.route

- **API pura:** rápida, sem browser, ideal para contrato e performance.
- **Intercept UI:** valida que front-end consome API corretamente e exibe resultado.

### Fixtures class-scoped

Reutilizar GET pesado economiza tempo; cuidado se testes alterarem estado compartilhado (não é o caso aqui — GET idempotente).

### validate_schema vs JSON Schema completo

Helper do projeto é intencionalmente simples — bom para bootcamp; produção pode usar `jsonschema` ou Pydantic.

---

## Checklist de aprendizado

- [ ] Explicar por que `activity_page` está dentro da classe
- [ ] Comparar SLA health (1s) vs users (2s)
- [ ] Descrever fluxo `route.fulfill(json=read_fixture(...))`
- [ ] Escrever regex de email e limitações
- [ ] Localizar arquivos em `users/empty-list.json` e `lookups/countries.json`
