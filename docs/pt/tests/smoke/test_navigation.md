# Testes de Navegação (Smoke)

**Arquivo de origem:** [`../../../../tests/smoke/test_navigation.py`](../../../../tests/smoke/test_navigation.py)

---

## Propósito

Este arquivo valida os fluxos fundamentais da aplicação TestFlow Sandbox:

1. **Carregamento de páginas** — cada rota protegida abre sem erro quando o usuário está autenticado.
2. **Navegação pela sidebar** — links do menu lateral levam à página correta e destacam o item ativo.
3. **Logout** — encerra a sessão e redireciona para a home.
4. **Saúde da API** — endpoints REST respondem com os status HTTP esperados.

É a suíte de **smoke** principal: se estes testes falharem, a aplicação provavelmente não está utilizável.

---

## Pré-requisitos

| Requisito | Descrição |
|-----------|-----------|
| Servidor local | A aplicação deve estar rodando em `BASE_URL` (padrão: `http://localhost:5050`). |
| Credenciais demo | `DEMO_EMAIL` e `DEMO_PASSWORD` configurados (via variáveis de ambiente ou defaults em `support/config.py`). |
| Playwright | Navegador instalado (`playwright install`). |
| PyTest | Dependências do projeto instaladas (`pip install -e .` ou equivalente). |

**Fixtures globais** (definidas em `conftest.py` na raiz do projeto):

- `page` — instância do Playwright `Page` (fornecida pelo plugin `pytest-playwright`).
- `api_request` — contexto HTTP `APIRequestContext` para chamadas REST sem abrir o navegador.
- `auth_token` — token JWT obtido uma vez por sessão de testes via `POST /api/auth/login`.

---

## Marcadores (markers) utilizados

| Marcador | Onde aparece | Significado |
|----------|--------------|-------------|
| `@pytest.mark.smoke` | Todas as classes | Testes de fumaça — execução rápida para validar o básico. |
| `@pytest.mark.regression` | `TestPageNavigation`, `TestSidebarNavigation`, `TestApiHealth` | Parte da suíte de regressão completa. |
| `@pytest.mark.critical` | `test_tc0010_...`, `test_tc0021_...` | Caminhos críticos de negócio. |
| `@pytest.mark.api` | Classe `TestApiHealth` e testes individuais | Testes que usam apenas a API HTTP, sem interação visual. |

Para executar apenas estes testes:

```bash
pytest tests/smoke/test_navigation.py -m smoke
pytest tests/smoke/test_navigation.py -m "smoke and api"
```

---

## Conceitos PyTest e Playwright usados neste arquivo

### Fixtures

Uma **fixture** é uma função que prepara dados ou estado antes do teste. O PyTest injeta fixtures pelo **nome do parâmetro** na assinatura do teste.

- `scope="module"` — a fixture roda uma vez por **módulo** (arquivo), não por teste.
- `autouse=True` — a fixture executa automaticamente para cada teste da classe, sem precisar declará-la como parâmetro.

### `@pytest.mark.parametrize`

Executa o **mesmo método de teste** várias vezes com conjuntos diferentes de argumentos. Cada combinação vira um teste separado no relatório.

### `expect` (Playwright)

Asserções com **auto-retry**: o Playwright repete a verificação até passar ou estourar o timeout. Preferível a `assert element.is_visible()` porque espera a UI estabilizar.

```python
expect(page.get_by_test_id("page-dashboard")).to_be_visible()
```

### `page.get_by_test_id()`

Localiza elementos pelo atributo `data-testid`. Estratégia estável e recomendada para automação.

### `page.evaluate()`

Executa JavaScript no contexto da página. Usado aqui para inspecionar `sessionStorage`.

### `APIRequestContext`

Cliente HTTP do Playwright para testar APIs diretamente, compartilhando a mesma `base_url` configurada no projeto.

---

## Imports — linha a linha

```python
import re
```

Importa o módulo de **expressões regulares**. Usado em asserções como `to_have_title(re.compile(title))` e `to_have_url(re.compile(r"/web/team\.html"))`, permitindo correspondência parcial/flexível de strings.

```python
import pytest
```

Framework de testes. Fornece decorators (`@pytest.fixture`, `@pytest.mark.parametrize`, `@pytest.mark.smoke`), descoberta automática de testes e injeção de fixtures.

```python
from playwright.sync_api import APIRequestContext, Page, expect
```

| Símbolo | Papel |
|---------|-------|
| `Page` | Representa uma aba do navegador; usado para navegar, clicar e localizar elementos. |
| `APIRequestContext` | Cliente HTTP para requisições REST (`get`, `post`, etc.). |
| `expect` | API de asserções do Playwright com espera implícita. |

```python
from support.auth import get_auth_token, login_via_api, visit_with_token
```

Funções de autenticação reutilizáveis:

- `get_auth_token(api_request)` — retorna JWT (do cache de sessão ou via login na API).
- `login_via_api(page, api_request)` — autentica via API, injeta token no `sessionStorage` e navega ao dashboard.
- `visit_with_token(page, path, token)` — visita uma rota protegida com token já disponível.

```python
from support.config import DEMO_EMAIL, DEMO_PASSWORD
```

Credenciais padrão da conta demo (`demo@automation.io` / `Demo123!`), configuráveis por variáveis de ambiente.

```python
from support.constants.test_cases import TC, tc
```

- `TC` — classe com IDs de casos de teste (ex.: `TC.SMOKE_DASHBOARD = "TC-0001"`).
- `tc(case_id, title)` — formata o ID legível para o relatório PyTest: `"[TC-0001] Dashboard page loads without error"`.

---

## Constante `PAGES`

```python
PAGES = [
    {
        "path": "/web/dashboard.html",
        "test_id": "page-dashboard",
        "title": "Dashboard",
        "tc_id": TC.SMOKE_DASHBOARD,
    },
    # ... mais 7 entradas ...
]
```

Lista de dicionários descrevendo **cada página** a ser validada no smoke de carregamento.

| Campo | Função |
|-------|--------|
| `path` | URL relativa a visitar após autenticação. |
| `test_id` | `data-testid` do container raiz da página — confirma que a página renderizou. |
| `title` | Texto esperado no `<title>` do documento (correspondência parcial via regex). |
| `tc_id` | ID do caso de teste para rastreabilidade. |

**Páginas cobertas:** Dashboard, Team, Settings, Components, Activity, Advanced, Wizard, UI States.

Centralizar os dados em uma lista evita duplicar oito métodos de teste quase idênticos — o `@pytest.mark.parametrize` itera sobre esta estrutura.

---

## Fixture `navigation_auth_token`

```python
@pytest.fixture(scope="module")
def navigation_auth_token(auth_token: str) -> str:
    return auth_token
```

**Propósito:** expor o token de autenticação da sessão de testes para a classe `TestPageNavigation`, com escopo de módulo.

**Como funciona:**

1. Depende da fixture global `auth_token` (definida em `conftest.py`).
2. `auth_token` por sua vez vem de `cache_auth_token`, que faz login na API **uma vez por sessão** e grava o token em cache.
3. `scope="module"` garante que o token seja reutilizado por todos os testes parametrizados da classe, sem novo login a cada iteração.

**Conceito PyTest:** encadeamento de fixtures — uma fixture pode depender de outra pelo nome do parâmetro.

---

## Classe `TestPageNavigation`

```python
@pytest.mark.smoke
@pytest.mark.regression
class TestPageNavigation:
```

Agrupa testes de **carregamento de página**. Marcadores na classe aplicam-se a todos os métodos dentro dela (a menos que sobrescritos).

### Método `test_page_loads_without_error`

```python
@pytest.mark.parametrize(
    "path,test_id,title,tc_id",
    [(p["path"], p["test_id"], p["title"], p["tc_id"]) for p in PAGES],
    ids=[tc(p["tc_id"], f"{p['title']} page loads without error") for p in PAGES],
)
def test_page_loads_without_error(
    self,
    page: Page,
    navigation_auth_token: str,
    path: str,
    test_id: str,
    title: str,
    tc_id: str,
) -> None:
```

**Parametrize explicado:**

- **Primeiro argumento:** nomes dos parâmetros que serão injetados.
- **Segundo argumento:** lista de tuplas — uma tupla por execução do teste (8 execuções, uma por página).
- **`ids`:** rótulos legíveis no relatório PyTest, ex.: `[TC-0001] Dashboard page loads without error`.

**Parâmetros injetados:**

| Parâmetro | Origem |
|-----------|--------|
| `page` | Fixture do pytest-playwright |
| `navigation_auth_token` | Fixture local deste módulo |
| `path`, `test_id`, `title`, `tc_id` | Valores da lista `PAGES` via parametrize |

**Corpo do teste — bloco a bloco:**

```python
visit_with_token(page, path, navigation_auth_token)
```

- **Given:** usuário autenticado com token JWT válido.
- **When:** navega para `path` com sessão injetada no `sessionStorage`.
- `visit_with_token` injeta auth via `add_init_script`, passa por `/web/login.html` e abre a rota desejada.

```python
expect(page.get_by_test_id(test_id)).to_be_visible()
```

- **Then:** o elemento raiz da página (ex.: `page-dashboard`) está visível — a página carregou com sucesso.

```python
expect(page).to_have_title(re.compile(title))
```

- **Then:** o título da aba contém o texto esperado (ex.: `"Dashboard"`). `re.compile` permite match parcial sem exigir o título completo.

---

## Classe `TestSidebarNavigation`

```python
@pytest.mark.smoke
@pytest.mark.regression
class TestSidebarNavigation:
```

Testa interação com o menu lateral após login.

### Fixture `setup` (autouse)

```python
@pytest.fixture(autouse=True)
def setup(self, page: Page, api_request: APIRequestContext) -> None:
    login_via_api(page, api_request)
    expect(page.get_by_test_id("page-dashboard")).to_be_visible()
```

**`autouse=True`** — roda **antes de cada teste** desta classe automaticamente.

**Fluxo:**

1. **Given:** `login_via_api` obtém token, injeta no navegador e abre o dashboard.
2. **Then (pré-condição):** confirma que o dashboard está visível — estado inicial garantido.

**Conceito:** fixture de setup por classe, equivalente ao `beforeEach` do Cypress ou `@BeforeEach` do JUnit.

### `test_tc0010_navigates_from_dashboard_to_team_via_sidebar`

```python
@pytest.mark.smoke
@pytest.mark.critical
def test_tc0010_navigates_from_dashboard_to_team_via_sidebar(self, page: Page) -> None:
    page.get_by_test_id("nav-team").click()
    expect(page.get_by_test_id("page-team")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/web/team\.html"))
```

| Etapa | Given/When/Then |
|-------|-----------------|
| Setup (fixture) | **Given** usuário logado no dashboard |
| `nav-team.click()` | **When** clica no link Team na sidebar |
| `page-team` visível | **Then** a página Team renderizou |
| URL contém `/web/team.html` | **Then** a URL mudou corretamente |

Marcador `@pytest.mark.critical` — falha aqui bloqueia release em pipelines que respeitam este marker.

### `test_tc0011_highlights_the_active_nav_link`

```python
def test_tc0011_highlights_the_active_nav_link(self, page: Page) -> None:
    expect(page.get_by_test_id("nav-dashboard")).to_have_class(re.compile(r"active"))
```

- **Given:** usuário no dashboard (via fixture `setup`).
- **Then:** o link `nav-dashboard` possui a classe CSS `active`, indicando item selecionado no menu.

`to_have_class(re.compile(r"active"))` verifica se **alguma** das classes do elemento contém `active`.

---

## Classe `TestLogout`

```python
@pytest.mark.smoke
class TestLogout:
```

Testa encerramento de sessão. **Não usa** a fixture `setup` de sidebar — faz login manual via UI para isolar o fluxo de logout.

### `test_tc0012_logout_clears_session_and_redirects_to_login`

```python
def test_tc0012_logout_clears_session_and_redirects_to_login(self, page: Page) -> None:
    page.goto("/web/login.html")
    page.get_by_test_id("login-email").fill(DEMO_EMAIL)
    page.get_by_test_id("login-password").fill(DEMO_PASSWORD)
    page.get_by_test_id("login-submit").click()
    page.get_by_test_id("page-dashboard").wait_for()
```

**Given/When — login via UI:**

1. Abre a página de login.
2. Preenche email e senha com credenciais demo.
3. Submete o formulário.
4. `wait_for()` aguarda o dashboard aparecer (sincronização explícita).

```python
    page.get_by_test_id("nav-logout").click()
    expect(page).to_have_url(re.compile(r"/web/index\.html"))
    assert page.evaluate("() => sessionStorage.getItem('sandbox-auth')") is None
```

**When/Then — logout:**

- **When:** clica em logout na sidebar.
- **Then:** redireciona para `/web/index.html` (home pública).
- **Then:** `sessionStorage` não contém mais `sandbox-auth` — sessão limpa.

**Conceito Playwright:** `page.evaluate()` executa JS no browser e retorna o resultado para Python. Aqui verifica que a chave foi removida.

---

## Classe `TestApiHealth`

```python
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.api
class TestApiHealth:
```

Testes **puramente de API** — não abrem páginas web. Usam apenas a fixture `api_request`.

### `test_tc0020_get_health_returns_200`

```python
def test_tc0020_get_health_returns_200(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/health")
    assert response.status == 200
```

- **When:** `GET /health`
- **Then:** status HTTP 200 — servidor está no ar.

### `test_tc0021_post_auth_login_returns_token`

```python
@pytest.mark.critical
def test_tc0021_post_auth_login_returns_token(self, api_request: APIRequestContext) -> None:
    response = api_request.post(
        "/api/auth/login",
        data={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    assert response.status == 200
    body = response.json()
    assert body["token"]
    assert body["user"]["email"] == DEMO_EMAIL
```

- **When:** login com credenciais válidas.
- **Then:** 200, corpo JSON contém `token` não vazio e email do usuário correto.

Este teste valida o **contrato de autenticação** usado por `login_via_api` e `fetch_auth_token`.

### `test_tc0022_get_users_returns_user_array`

```python
def test_tc0022_get_users_returns_user_array(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/api/users")
    assert response.status == 200
    body = response.json()
    assert isinstance(body["users"], list)
    assert len(body["users"]) > 0
```

- **Then:** endpoint de usuários retorna lista não vazia.

### `test_tc0023_get_errors_404_returns_404_status`

```python
def test_tc0023_get_errors_404_returns_404_status(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/api/errors/404")
    assert response.status == 404
```

Endpoint de **simulação de erro** — confirma que a API propaga corretamente HTTP 404.

### `test_tc0024_get_errors_422_returns_422_status`

```python
def test_tc0024_get_errors_422_returns_422_status(self, api_request: APIRequestContext) -> None:
    response = api_request.get("/api/errors/422")
    assert response.status == 422
```

Mesmo padrão para erro de validação (422 Unprocessable Entity).

**Nota:** estes dois últimos testes **não** têm `@pytest.mark.smoke` individual — herdam apenas os markers da classe (`smoke`, `regression`, `api`).

---

## Diagrama de fluxo — autenticação nos testes

```
┌─────────────────────────────────────────────────────────────┐
│  conftest.py (sessão)                                       │
│  cache_auth_token → POST /api/auth/login → grava token      │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  visit_with_token   login_via_api    login via UI
  (TestPageNav)      (TestSidebar)    (TestLogout)
         │                 │                 │
         └─────────────────┴─────────────────┘
                           │
                    sessionStorage
                    ('sandbox-auth')
                           │
                           ▼
                  Páginas protegidas /web/*.html
```

---

## Resumo para novos alunos

| Padrão | Onde aparece | Por quê |
|--------|--------------|---------|
| Parametrize + lista de dados | `TestPageNavigation` | DRY — um teste, oito páginas |
| Fixture `autouse` | `TestSidebarNavigation.setup` | Setup repetido sem boilerplate |
| Login via API | Sidebar, PageNavigation | Mais rápido e estável que UI |
| Login via UI | TestLogout | Testa o fluxo real de logout |
| `expect` vs `assert` | UI | Retry automático no Playwright |
| `assert response.status` | TestApiHealth | Asserção direta em testes de API |
| IDs TC-* | Parametrize `ids` | Rastreabilidade com casos de teste |

**Comando sugerido para praticar:**

```bash
pytest tests/smoke/test_navigation.py -v --headed
```

O flag `--headed` abre o navegador visível — útil para acompanhar o que cada teste faz durante o aprendizado.
