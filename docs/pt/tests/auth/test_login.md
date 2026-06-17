# Testes de Login (Autenticação)

**Arquivo de origem:** [`../../../../tests/auth/test_login.py`](../../../../tests/auth/test_login.py)

---

## Propósito

Este arquivo cobre **todos os cenários da página de login** (`/web/login.html`):

- Estrutura e atributos do formulário
- Login com credenciais válidas (UI, API toggle, tecla Enter)
- Persistência de sessão no `sessionStorage`
- Credenciais inválidas e mensagens de erro
- Validação HTML5 de campos obrigatórios
- Checkbox "Remember me"
- Redirecionamento de páginas protegidas
- Logout após login
- Acessibilidade (a11y) com axe-core

É a suíte de **regressão de autenticação** — complementa os smoke tests de navegação com cenários mais granulares.

---

## Pré-requisitos

| Requisito | Descrição |
|-----------|-----------|
| Servidor local | `BASE_URL` acessível (padrão: `http://localhost:5050`). |
| Credenciais demo | `DEMO_EMAIL` / `DEMO_PASSWORD` em `support/config.py`. |
| Fixture JSON | `fixtures/credentials.json` com pares válidos/inválidos. |
| Page Object | Classe `LoginPage` em `pages/login_page.py`. |
| Playwright + PyTest | Ambiente de testes configurado. |

**Dependências indiretas:**

- `conftest.py` — fixture `page` e função `check_a11y`.
- `support/helpers/fixtures.py` — leitor de arquivos JSON de dados de teste.

---

## Marcadores (markers) utilizados

```python
pytestmark = pytest.mark.regression
```

Esta linha aplica `@pytest.mark.regression` a **todo o módulo** — todos os testes deste arquivo são de regressão por padrão.

| Marcador | Onde | Significado |
|----------|------|-------------|
| `regression` | Módulo inteiro (`pytestmark`) | Suíte completa de regressão. |
| `smoke` | `TestValidCredentials.test_tc0101_...` | Subconjunto crítico de fumaça. |
| `critical` | `TestValidCredentials.test_tc0101_...` | Caminho crítico — login bem-sucedido. |
| `a11y` | Classe `TestAccessibility` | Testes de acessibilidade. |

**Executar exemplos:**

```bash
pytest tests/auth/test_login.py -m regression
pytest tests/auth/test_login.py -m "critical"
pytest tests/auth/test_login.py -m a11y
```

---

## Conceitos PyTest e Playwright usados neste arquivo

### Page Object Model (POM)

A classe `LoginPage` encapsula seletores e ações da página de login. Os testes chamam métodos semânticos (`login_with`, `should_show_error`) em vez de repetir seletores CSS.

### `pytestmark`

Atribuição no nível do módulo equivalente a decorar cada teste com o mesmo marker — evita repetir `@pytest.mark.regression` dezenas de vezes.

### Fixture `autouse`

A fixture `visit_login` navega à página de login **antes de cada teste**, garantindo estado inicial consistente.

### `page.expect_request()`

Context manager que **captura requisições HTTP** disparadas pela página durante uma ação. Usado para verificar que o login via API toggle faz `POST /api/auth/login`.

### `page.evaluate()`

Executa JavaScript no browser — aqui para ler e parsear `sessionStorage`.

### `Locator.press("Enter")`

Simula tecla Enter em um campo — testa submissão do formulário via teclado.

### `check_a11y(page)`

Helper do `conftest.py` que roda axe-core via `axe_playwright_python` e falha se houver violações críticas/sérias de WCAG 2.x.

---

## Imports — linha a linha

```python
import re
```

Expressões regulares para validar URLs (`to_have_url(re.compile(...))`).

```python
import pytest
```

Framework de testes e decorators.

```python
from playwright.sync_api import Page, expect
```

- `Page` — aba do navegador.
- `expect` — asserções com auto-retry.

```python
from conftest import check_a11y
```

Importa a função helper de acessibilidade definida na raiz do projeto. PyTest resolve `conftest.py` automaticamente para fixtures, mas funções auxiliares precisam ser importadas explicitamente.

```python
from pages.login_page import LoginPage
```

Page Object da tela de login.

```python
from support.config import DEMO_EMAIL, DEMO_PASSWORD
```

Credenciais padrão da conta demo.

```python
from support.helpers.fixtures import read_fixture
```

Utilitário para carregar JSON de `fixtures/` como dict Python.

---

## Configuração do módulo

```python
pytestmark = pytest.mark.regression
```

**Efeito:** marca **todos** os testes deste arquivo como `regression`. Aparece no relatório como `@pytest.mark.regression` em cada teste.

**Conceito PyTest:** `pytestmark` pode ser um único marker ou uma lista: `pytestmark = [pytest.mark.regression, pytest.mark.slow]`.

```python
credentials = read_fixture("credentials.json")
```

Carrega dados de teste do arquivo `fixtures/credentials.json`:

```json
{
  "valid": { "email": "demo@automation.io", "password": "Demo123!" },
  "invalid": { "email": "wrong@email.com", "password": "wrongpassword" },
  "emptyEmail": { "email": "", "password": "Demo123!" }
}
```

**Por quê usar fixture JSON?** Separa **dados** de **lógica de teste**. Credenciais inválidas ficam centralizadas e reutilizáveis.

---

## Fixture `visit_login`

```python
@pytest.fixture(autouse=True)
def visit_login(page: Page) -> None:
    LoginPage(page).visit()
```

| Aspecto | Detalhe |
|---------|---------|
| `autouse=True` | Executa automaticamente antes de **cada** teste do módulo |
| Dependência | Recebe `page` da fixture global pytest-playwright |
| Ação | `LoginPage(page).visit()` → `page.goto("/web/login.html")` |

**Given implícito:** todo teste começa na página de login, sem precisar chamar `visit()` manualmente.

**Exceção prática:** `TestRedirectAfterLogin.test_redirects_to_login_when_accessing_a_protected_page_unauthenticated` chama `page.goto("/web/team.html")` **depois** do setup, sobrescrevendo a navegação inicial — padrão válido para testar redirecionamento.

---

## Page Object `LoginPage` — referência rápida

Os testes delegam interações à classe em `pages/login_page.py`. Métodos usados neste arquivo:

| Método | O que faz |
|--------|-----------|
| `visit()` | Navega para `/web/login.html` |
| `email_input()` | Locator `[data-testid="login-email"]` |
| `password_input()` | Locator `[data-testid="login-password"]` |
| `submit_btn()` | Botão de submit |
| `remember_checkbox()` | Checkbox "Remember me" |
| `use_api_checkbox()` | Toggle "Use API" |
| `result_msg()` | Mensagem de resultado/erro |
| `fill_email()` / `fill_password()` | Preenche campos (com `clear` antes) |
| `submit()` | Clica no botão submit |
| `login_with(email, password)` | Fluxo completo: fill + submit |
| `toggle_use_api()` | Ativa login via API (click via JS) |
| `toggle_remember_me()` | Alterna checkbox remember |
| `should_show_error(text)` | Assert mensagem de erro visível |
| `should_redirect_to_dashboard()` | Assert dashboard visível + URL correta |

**Padrão fluente:** métodos retornam `Self` (`return self`) para encadeamento opcional.

---

## Classe `TestPageStructure`

Valida que o formulário de login renderiza corretamente.

### `test_tc0100_renders_all_form_elements`

```python
def test_tc0100_renders_all_form_elements(self, page: Page) -> None:
    login = LoginPage(page)
    expect(login.email_input()).to_be_visible()
    expect(login.password_input()).to_be_visible()
    expect(login.submit_btn()).to_be_visible()
    expect(login.submit_btn()).to_be_enabled()
    expect(login.remember_checkbox()).to_be_attached()
    expect(login.use_api_checkbox()).to_be_attached()
```

| Asserção | Significado |
|----------|-------------|
| `to_be_visible()` | Elemento visível na tela |
| `to_be_enabled()` | Botão não está desabilitado |
| `to_be_attached()` | Elemento existe no DOM (pode estar oculto) — usado para checkboxes |

- **Given:** página de login aberta (fixture `visit_login`).
- **Then:** todos os controles essenciais existem e o submit está habilitado.

### `test_has_correct_placeholder_text_on_email_field`

```python
expect(LoginPage(page).email_input()).to_have_attribute(
    "placeholder", "demo@automation.io"
)
```

- **Then:** placeholder do email orienta o usuário com o email demo esperado.

### `test_password_field_masks_input`

```python
expect(LoginPage(page).password_input()).to_have_attribute("type", "password")
```

- **Then:** campo senha usa `type="password"` — caracteres mascarados.

---

## Classe `TestValidCredentials`

Cenários de **login bem-sucedido**.

```python
@pytest.mark.smoke
@pytest.mark.critical
class TestValidCredentials:
```

Markers adicionais sobrescrevem/complementam o `pytestmark` do módulo para testes críticos de fumaça.

### `test_tc0101_logs_in_via_ui_and_redirects_to_dashboard`

```python
def test_tc0101_logs_in_via_ui_and_redirects_to_dashboard(self, page: Page) -> None:
    login = LoginPage(page)
    login.login_with(DEMO_EMAIL, DEMO_PASSWORD)
    login.should_redirect_to_dashboard()
```

| Etapa | Given/When/Then |
|-------|-----------------|
| Setup | **Given** formulário de login vazio |
| `login_with(...)` | **When** preenche credenciais válidas e submete |
| `should_redirect_to_dashboard()` | **Then** dashboard visível e URL `/web/dashboard.html` |

**Caso crítico TC-0101** — caminho feliz principal de autenticação via UI.

### `test_logs_in_with_api_toggle_enabled`

```python
def test_logs_in_with_api_toggle_enabled(self, page: Page) -> None:
    login = LoginPage(page)
    with page.expect_request(
        lambda req: "/api/auth/login" in req.url and req.method == "POST"
    ) as request_info:
        login.toggle_use_api()
        login.login_with(DEMO_EMAIL, DEMO_PASSWORD)

    response = request_info.value.response()
    assert response is not None
    assert response.status == 200
    login.should_redirect_to_dashboard()
```

**Conceito Playwright — `page.expect_request()`:**

1. Abre um "ouvinte" **antes** da ação.
2. O lambda filtra requisições: URL contém `/api/auth/login` e método POST.
3. Dentro do `with`, executa toggle API + login.
4. `request_info.value` retorna a `Request` capturada.
5. `.response()` obtém a `Response` HTTP associada.

- **When:** usuário ativa "Use API" e faz login.
- **Then:** requisição POST foi feita, retornou 200, e redirecionou ao dashboard.

### `test_sets_auth_data_in_session_storage_after_login`

```python
LoginPage(page).login_with(DEMO_EMAIL, DEMO_PASSWORD)
auth = page.evaluate(
    """() => {
        const raw = sessionStorage.getItem('sandbox-auth');
        return raw ? JSON.parse(raw) : null;
    }"""
)
assert auth is not None
assert auth["email"] == DEMO_EMAIL
```

- **When:** login bem-sucedido.
- **Then:** `sessionStorage['sandbox-auth']` contém objeto JSON com email correto.

**Conceito:** `page.evaluate()` com função JS sem argumentos — retorno serializado para Python.

### `test_shows_success_message_before_redirect`

```python
login.login_with(DEMO_EMAIL, DEMO_PASSWORD)

result = page.get_by_test_id("login-result")
if result.is_visible():
    expect(result).to_contain_text("Login successful")
login.should_redirect_to_dashboard()
```

Teste **defensivo:** a mensagem de sucesso pode aparecer brevemente antes do redirect. Usa `is_visible()` para verificar condicionalmente — evita falha se o redirect for instantâneo.

### `test_submits_login_form_with_enter_key`

```python
login.fill_email(DEMO_EMAIL)
login.fill_password(DEMO_PASSWORD)
login.password_input().press("Enter")
login.should_redirect_to_dashboard()
```

- **When:** submete formulário pressionando Enter no campo senha.
- **Then:** login funciona igual ao clique no botão.

**Conceito Playwright:** `Locator.press(key)` simula eventos de teclado.

---

## Classe `TestInvalidCredentials`

Cenários de **falha de autenticação**.

### `test_shows_error_for_wrong_password`

```python
login.login_with(credentials["valid"]["email"], credentials["invalid"]["password"])
login.should_show_error("Invalid credentials")
```

- **Given:** email válido, senha errada (de `credentials.json`).
- **Then:** mensagem "Invalid credentials" visível.

### `test_shows_error_for_unknown_email`

```python
login.login_with(credentials["invalid"]["email"], credentials["valid"]["password"])
login.should_show_error("Invalid credentials")
```

- **Given:** email inexistente, senha correta.
- **Then:** mesma mensagem genérica (boa prática de segurança — não revela se email existe).

### `test_does_not_navigate_away_on_failed_login`

```python
LoginPage(page).login_with(
    credentials["invalid"]["email"], credentials["invalid"]["password"]
)
expect(page).to_have_url(re.compile(r"/web/login\.html"))
```

- **Then:** URL permanece em `/web/login.html` — usuário não avança com credenciais inválidas.

---

## Classe `TestFormValidation`

### `test_requires_email_to_not_be_empty_html5_validation`

```python
login.fill_password(DEMO_PASSWORD)
login.submit()
is_valid = login.email_input().evaluate("el => el.validity.valid")
assert is_valid is False
```

- **Given:** email vazio, senha preenchida.
- **When:** tenta submeter.
- **Then:** validação HTML5 nativa (`constraint validation API`) reporta email inválido.

**Conceito:** `element.validity.valid` é a API nativa do browser — testa validação client-side sem depender de mensagens customizadas.

---

## Classe `TestRememberMe`

### `test_checkbox_can_be_checked_and_unchecked`

```python
expect(login.remember_checkbox()).not_to_be_checked()
login.toggle_remember_me()
expect(login.remember_checkbox()).to_be_checked()
login.toggle_remember_me()
expect(login.remember_checkbox()).not_to_be_checked()
```

- **Then:** checkbox alterna entre marcado e desmarcado corretamente.

Asserções Playwright para checkboxes: `to_be_checked()` / `not_to_be_checked()`.

---

## Classe `TestRedirectAfterLogin`

### `test_redirects_to_login_when_accessing_a_protected_page_unauthenticated`

```python
page.goto("/web/team.html")
expect(page).to_have_url(re.compile(r"/web/login\.html"))

LoginPage(page).login_with(DEMO_EMAIL, DEMO_PASSWORD)
expect(page).not_to_have_url(re.compile(r"/web/login\.html"))
```

| Fase | Given/When/Then |
|------|-----------------|
| 1 | **When** acessa `/web/team.html` sem auth → **Then** redireciona para login |
| 2 | **When** faz login → **Then** sai da página de login (vai para destino protegido) |

**Nota:** este teste depende do comportamento de **route guard** da aplicação — páginas protegidas exigem autenticação.

---

## Classe `TestLogout`

### `test_clears_session_and_redirects_to_home_after_logout`

```python
login.login_with(DEMO_EMAIL, DEMO_PASSWORD)
login.should_redirect_to_dashboard()

page.get_by_test_id("nav-logout").click()
expect(page).to_have_url(re.compile(r"/web/index\.html"))
assert page.evaluate("() => sessionStorage.getItem('sandbox-auth')") is None
```

Fluxo completo:

1. **Given/When:** login via UI → dashboard.
2. **When:** clica logout.
3. **Then:** home pública + sessão limpa.

Espelha `test_tc0012` em `test_navigation.py`, mas usando Page Object em vez de seletores inline.

---

## Classe `TestAccessibility`

```python
@pytest.mark.a11y
@pytest.mark.regression
class TestAccessibility:
```

Markers explícitos na classe — `a11y` permite filtrar: `pytest -m a11y`.

### `test_login_page_has_no_critical_a11y_violations`

```python
def test_login_page_has_no_critical_a11y_violations(self, page: Page) -> None:
    check_a11y(page)
```

**O que `check_a11y` faz** (em `conftest.py`):

1. Instancia `Axe()` do pacote `axe_playwright_python`.
2. Executa scan com tags WCAG 2.0/2.1 nível A e AA.
3. Ignora regra `color-contrast` (desabilitada por padrão — pode gerar falsos positivos em temas demo).
4. Filtra violações com impacto `critical` ou `serious`.
5. Falha o teste listando IDs das regras violadas.

- **Given:** página de login renderizada.
- **Then:** nenhuma violação a11y crítica/séria.

---

## Mapa mental das classes

```
test_login.py
├── TestPageStructure      → UI do formulário existe?
├── TestValidCredentials   → login OK (UI, API, storage, Enter)
├── TestInvalidCredentials → credenciais erradas
├── TestFormValidation     → HTML5 required
├── TestRememberMe         → checkbox funciona
├── TestRedirectAfterLogin → guard de rotas
├── TestLogout             → encerra sessão
└── TestAccessibility      → axe-core WCAG
```

---

## Resumo para novos alunos

| Padrão | Exemplo neste arquivo |
|--------|----------------------|
| Page Object | `LoginPage(page).login_with(...)` |
| Dados externos | `read_fixture("credentials.json")` |
| Setup automático | `@pytest.fixture(autouse=True) visit_login` |
| Marker de módulo | `pytestmark = pytest.mark.regression` |
| Interceptar HTTP | `page.expect_request(lambda req: ...)` |
| Ler browser state | `page.evaluate("() => sessionStorage...")` |
| Validação nativa | `.evaluate("el => el.validity.valid")` |
| A11y | `check_a11y(page)` + `@pytest.mark.a11y` |

**Comando sugerido:**

```bash
pytest tests/auth/test_login.py::TestValidCredentials -v --headed
```

Comece pela classe `TestValidCredentials` — contém o fluxo feliz mais importante antes de explorar casos de erro.
