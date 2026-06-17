# Testes do Dashboard

**Arquivo de origem:** [`../../../../tests/dashboard/test_dashboard.py`](../../../../tests/dashboard/test_dashboard.py)

---

## Propósito

Este arquivo valida a página **Dashboard** (`/web/dashboard.html`) após autenticação:

- Saudação personalizada e subtítulo
- Cards de KPI (runs, pass rate, members, issues)
- Lista de atividade recente
- Indicadores de saúde das suítes de teste
- Modal "New Test Run" (abrir, preencher, fechar, confirmar)
- Links de acesso rápido para outras páginas

Todos os testes assumem um usuário **já logado** via API — foco na UI do dashboard, não no fluxo de login.

---

## Pré-requisitos

| Requisito | Descrição |
|-----------|-----------|
| Servidor local | `BASE_URL` acessível (padrão: `http://localhost:5050`). |
| Autenticação API | Endpoint `POST /api/auth/login` funcional. |
| Page Object | `DashboardPage` em `pages/dashboard_page.py`. |
| Helper auth | `login_via_api` em `support/auth.py`. |

**Fixtures globais usadas:**

- `page` — aba Playwright.
- `api_request` — cliente HTTP para obter token de autenticação.

---

## Marcadores (markers) utilizados

```python
pytestmark = pytest.mark.regression
```

Todo o módulo é marcado como **regression**. Nenhum teste individual adiciona `smoke`, `critical` ou `api`.

```bash
pytest tests/dashboard/test_dashboard.py -m regression
pytest tests/dashboard/test_dashboard.py -v
```

---

## Conceitos PyTest e Playwright usados neste arquivo

### Fixture `autouse` de setup

`setup_dashboard` roda antes de cada teste: faz login via API e confirma que o dashboard carregou. Elimina repetição de boilerplate.

### Page Object Model

`DashboardPage` encapsula locators (`get_by_test_id`) e ações (`open_new_run_modal`, `select_suite`) — testes leem como especificações em linguagem natural.

### `expect` com regex

`to_have_text(re.compile(r"^\d+(\.\d+)?%$"))` valida formato de porcentagem sem valor exato fixo.

### `Locator.inner_text()`

Retorna texto visível do elemento — usado para extrair valor numérico do KPI.

### `page.keyboard.press("Escape")`

Simula tecla Escape — testa fechamento de modal por atalho de teclado.

### `page.go_back()`

Navega para a página anterior no histórico — usado após clicar em quick access para não afetar testes seguintes.

### `@pytest.mark.parametrize` em classe

O decorator na classe `TestQuickAccessNavigation` parametriza **todos** os métodos de teste dentro dela (neste caso, apenas um método).

### `re.escape(path)`

Escapa caracteres especiais do path para uso seguro dentro de `re.compile` na asserção de URL.

---

## Imports — linha a linha

```python
import re
```

Regex para validar formatos de texto (porcentagens, URLs, estilos CSS).

```python
import pytest
```

Framework de testes.

```python
from playwright.sync_api import APIRequestContext, Page, expect
```

| Símbolo | Uso neste arquivo |
|---------|-----------------|
| `Page` | Interação com UI do dashboard |
| `APIRequestContext` | Login via API na fixture de setup |
| `expect` | Asserções com retry |

```python
from pages.dashboard_page import DashboardPage
```

Page Object com locators e métodos do dashboard.

```python
from support.auth import login_via_api
```

Autentica via API, injeta sessão no browser e navega ao dashboard.

---

## Configuração do módulo

```python
pytestmark = pytest.mark.regression
```

Marca o arquivo inteiro como suíte de regressão.

---

## Fixture `setup_dashboard`

```python
@pytest.fixture(autouse=True)
def setup_dashboard(page: Page, api_request: APIRequestContext) -> None:
    login_via_api(page, api_request)
    DashboardPage(page).should_be_loaded()
```

**Execução (antes de cada teste):**

1. **`login_via_api(page, api_request)`**
   - Obtém token via `POST /api/auth/login`
   - Injeta `sessionStorage` com `inject_auth` + `_seed_session_storage`
   - Navega ao dashboard e aguarda `page-dashboard`

2. **`DashboardPage(page).should_be_loaded()`**
   - Assert: `[data-testid="page-dashboard"]` está visível

**Given implícito para todos os testes:** usuário autenticado no dashboard pronto para interação.

**Conceito PyTest:** fixture `autouse` + dependências encadeadas (`page`, `api_request`) = setup zero-linha nos métodos de teste.

---

## Page Object `DashboardPage` — referência

Métodos e locators usados neste arquivo de teste:

| Método / Locator | `data-testid` | Função |
|------------------|---------------|--------|
| `page_root()` | `page-dashboard` | Container raiz |
| `greeting()` | `dash-greeting` | Saudação time-based |
| `subtitle()` | `dash-subtitle` | Subtítulo |
| `kpi_card(name)` | `kpi-{name}` | Card KPI |
| `kpi_value(name)` | `kpi-{name}-value` | Valor numérico |
| `kpi_trend(name)` | `kpi-{name}-trend` | Indicador de tendência |
| `activity_item(n)` | `activity-item-{n}` | Item da lista |
| `health_status()` | `health-status` | Badge de saúde |
| `health_bar(suite)` | `health-{suite}` | Barra de progresso |
| `health_pct(suite)` | `health-{suite}-pct` | Texto de porcentagem |
| `open_new_run_modal()` | clica `btn-new-run` | Abre modal |
| `run_suite_select()` | `run-suite` | Select de suíte |
| `run_env_select()` | `run-env` | Select de ambiente |
| `confirm_run()` / `cancel_run()` | botões do modal | Ações do modal |
| `quick_action(name)` | `qa-{name}` | Botões de acesso rápido |

---

## Classe `TestGreeting`

Valida elementos de boas-vindas no topo do dashboard.

### `test_shows_time_based_greeting_with_the_user_name`

```python
def test_shows_time_based_greeting_with_the_user_name(self, page: Page) -> None:
    dashboard = DashboardPage(page)
    dashboard.should_show_greeting()
    expect(dashboard.greeting()).to_contain_text("Demo User")
```

**`should_show_greeting()`** (no Page Object):

```python
expect(self.greeting()).to_be_visible()
expect(self.greeting()).to_have_text(re.compile(r"Good (morning|afternoon|evening),"))
```

- **Given:** dashboard carregado.
- **Then:** saudação visível no formato "Good morning/afternoon/evening," **e** contém o nome "Demo User".

**Conceito:** asserção composta — Page Object verifica formato; teste verifica conteúdo específico do usuário demo.

### `test_shows_a_non_empty_subtitle`

```python
subtitle = DashboardPage(page).subtitle()
expect(subtitle).to_be_visible()
expect(subtitle).not_to_be_empty()
```

- **Then:** subtítulo existe, está visível e tem texto.

`not_to_be_empty()` — matcher Playwright que falha se o elemento não tiver conteúdo textual.

---

## Classe `TestKpiCards`

Valida os quatro cards de métricas principais.

### `test_renders_all_four_kpi_cards`

```python
DashboardPage(page).should_have_all_kpi_cards()
```

Page Object itera `("runs", "passrate", "members", "issues")` e verifica visibilidade + valor não vazio.

### `test_shows_a_numeric_value_in_the_runs_card`

```python
text = DashboardPage(page).kpi_value("runs").inner_text()
assert int(text) > 0
```

- **When:** lê texto do KPI "runs".
- **Then:** converte para inteiro e confirma valor > 0.

**Conceito:** combina Playwright (`inner_text()`) com assert Python nativo para lógica numérica.

### `test_shows_a_percentage_in_the_pass_rate_card`

```python
expect(DashboardPage(page).kpi_value("passrate")).to_have_text(
    re.compile(r"^\d+(\.\d+)?%$")
)
```

- **Then:** valor segue padrão como `97%` ou `97.5%`.

Regex explicada:
- `^` início, `\d+` dígitos, `(\.\d+)?` decimais opcionais, `%` literal, `$` fim.

### `test_shows_trend_indicators_on_each_card`

```python
dashboard = DashboardPage(page)
for key in ("runs", "passrate", "members", "issues"):
    expect(dashboard.kpi_trend(key)).to_be_visible()
    expect(dashboard.kpi_trend(key)).not_to_be_empty()
```

- **Then:** cada card tem indicador de tendência visível com texto (ex.: "↑ 12%").

---

## Classe `TestRecentActivity`

Valida a seção de atividade recente.

### `test_shows_5_activity_items`

```python
DashboardPage(page).should_have_activity_items(5)
```

Page Object conta elementos `[data-testid^="activity-item-"]` dentro de `activity-list` e espera exatamente 5.

### `test_each_activity_item_has_text_and_a_timestamp`

```python
item = DashboardPage(page).activity_item(1)
expect(item.locator(".activity-text")).not_to_be_empty()
expect(item.locator(".activity-time")).not_to_be_empty()
```

- **Then:** primeiro item tem descrição (`.activity-text`) e horário (`.activity-time`).

**Conceito Playwright:** `locator.locator(".activity-text")` — busca descendente dentro do item pai.

### `test_see_all_link_navigates_to_activity_page`

```python
DashboardPage(page).quick_action("team")
page.get_by_test_id("activity-see-all").click()
expect(page).to_have_url(re.compile(r"/web/activity\.html"))
```

**Nota:** chama `quick_action("team")` antes de clicar "See all" — possível interação prévia para garantir estado da UI (padrão do teste original).

- **When:** clica link "See all" da atividade.
- **Then:** navega para `/web/activity.html`.

---

## Classe `TestSuiteHealth`

Valida indicadores de saúde das suítes de automação.

### `test_shows_healthy_status_badge`

```python
dashboard = DashboardPage(page)
expect(dashboard.health_status()).to_be_visible()
expect(dashboard.health_status()).to_contain_text("Healthy")
```

- **Then:** badge global indica status "Healthy".

### `test_renders_three_suite_health_bars`

```python
for suite in ("regression", "smoke", "e2e"):
    expect(dashboard.health_bar(suite)).to_be_visible()
    expect(dashboard.health_pct(suite)).to_have_text(re.compile(r"^\d+%$"))
```

- **Then:** três barras (regression, smoke, e2e) visíveis com porcentagem inteira (ex.: `97%`).

### `test_regression_bar_fill_width_reflects_its_percentage`

```python
expect(DashboardPage(page).health_bar("regression")).to_have_attribute(
    "style", re.compile(r"width:97%")
)
```

- **Then:** atributo `style` inline da barra regression contém `width:97%`.

Testa que o **valor visual** da barra corresponde ao dado — CSS inline como fonte de verdade.

---

## Classe `TestNewTestRunModal`

Valida o fluxo completo do modal de nova execução de testes.

### `test_opens_modal_on_button_click`

```python
dashboard = DashboardPage(page)
dashboard.open_new_run_modal()
dashboard.should_show_run_modal_open()
```

- **When:** clica "New Run".
- **Then:** overlay do modal (`run-modal-overlay`) visível.

### `test_modal_has_suite_and_environment_selects`

```python
dashboard.open_new_run_modal()
expect(dashboard.run_suite_select()).to_be_visible()
expect(dashboard.run_env_select()).to_be_visible()
```

- **Then:** selects de suíte e ambiente presentes no modal.

### `test_closes_modal_on_cancel`

```python
dashboard.open_new_run_modal()
dashboard.cancel_run()
dashboard.should_show_run_modal_closed()
```

- **When:** clica Cancel.
- **Then:** modal não visível.

### `test_closes_modal_on_escape_key`

```python
dashboard.open_new_run_modal()
page.keyboard.press("Escape")
dashboard.should_show_run_modal_closed()
```

- **When:** pressiona Escape.
- **Then:** modal fecha (padrão UX de acessibilidade).

### `test_closes_modal_on_overlay_click`

```python
page.get_by_test_id("run-modal-overlay").click(
    position={"x": 10, "y": 10}, force=True
)
dashboard.should_show_run_modal_closed()
```

- **When:** clica no overlay fora do conteúdo do modal.
- **Then:** modal fecha.

**Conceito Playwright:**
- `position={"x": 10, "y": 10}` — clique em coordenadas específicas do elemento.
- `force=True` — ignora checks de actionability (elemento pode estar parcialmente coberto).

### `test_confirms_a_run_and_shows_toast`

```python
dashboard.open_new_run_modal()
dashboard.select_suite("smoke")
dashboard.select_environment("staging")
dashboard.confirm_run()
dashboard.should_show_run_modal_closed()
expect(page.get_by_test_id("toast-message")).to_contain_text("smoke")
```

| Etapa | Given/When/Then |
|-------|-----------------|
| Abre modal | **When** inicia novo run |
| Seleciona smoke + staging | **When** preenche formulário |
| Confirma | **When** submete |
| Modal fecha + toast | **Then** feedback confirma suíte "smoke" |

**Conceito:** `select_option(value)` em `<select>` — equivalente a escolher opção no dropdown.

---

## Classe `TestQuickAccessNavigation`

```python
@pytest.mark.parametrize(
    "test_id,path",
    [
        ("qa-team", "/web/team.html"),
        ("qa-settings", "/web/settings.html"),
        ("qa-wizard", "/web/wizard.html"),
    ],
)
class TestQuickAccessNavigation:
```

**Parametrize em nível de classe** — aplica parâmetros a todos os métodos de teste da classe.

### `test_quick_access_navigates`

```python
def test_quick_access_navigates(self, page: Page, test_id: str, path: str) -> None:
    page.get_by_test_id(test_id).click()
    expect(page).to_have_url(re.compile(re.escape(path)))
    page.go_back()
```

Para cada tupla `(test_id, path)`:

| Execução | Botão | Destino |
|----------|-------|---------|
| 1 | `qa-team` | `/web/team.html` |
| 2 | `qa-settings` | `/web/settings.html` |
| 3 | `qa-wizard` | `/web/wizard.html` |

- **When:** clica botão de acesso rápido.
- **Then:** URL corresponde ao path esperado.
- **Cleanup:** `page.go_back()` retorna ao dashboard para não poluir estado dos testes seguintes (mesma sessão de browser).

---

## Fluxo de setup compartilhado

```
┌──────────────────────────────────────────┐
│  setup_dashboard (autouse, cada teste)   │
├──────────────────────────────────────────┤
│  1. login_via_api(page, api_request)     │
│     └─ POST /api/auth/login → token      │
│     └─ inject sessionStorage             │
│     └─ goto /web/dashboard.html          │
│  2. DashboardPage.should_be_loaded()     │
└──────────────────────────────────────────┘
                    │
                    ▼
         TestGreeting / TestKpiCards /
         TestRecentActivity / TestSuiteHealth /
         TestNewTestRunModal / TestQuickAccessNavigation
```

---

## Resumo para novos alunos

| Padrão | Onde | Por quê |
|--------|------|---------|
| Setup autouse | `setup_dashboard` | DRY — login uma vez por teste |
| Page Object | `DashboardPage` | Testes legíveis, seletores centralizados |
| Regex em expect | KPIs, URLs, CSS | Valida formato sem dados frágeis |
| Modal UX | Escape, overlay, cancel | Cobertura de padrões de UI |
| Parametrize na classe | Quick access | Um método, três rotas |
| `go_back()` | Quick access | Isolamento entre testes |

**Comando sugerido para explorar visualmente:**

```bash
pytest tests/dashboard/test_dashboard.py::TestNewTestRunModal -v --headed --slowmo=500
```

`--slowmo=500` adiciona pausa de 500 ms entre ações — ideal para ver modais abrindo e fechando durante o aprendizado.
