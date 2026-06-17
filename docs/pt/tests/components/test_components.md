# Testes da Página de Componentes (Components)

**Arquivo-fonte:** [`../../../../tests/components/test_components.py`](../../../../tests/components/test_components.py)

---

## Propósito

Este módulo valida a página **Components** (`/web/components.html`), um catálogo de componentes UI reutilizáveis do sandbox TestFlow. Os testes cobrem:

- **Botões** — variantes, estados disabled/loading, toast, diálogos nativos (`alert`, `confirm`)
- **Modal** — abertura, fechamento (botões, Escape, clique no overlay), atributos ARIA
- **Tabs** — navegação, painéis, roles ARIA, foco por teclado
- **Accordion** — expandir/colapsar, múltiplos painéis abertos
- **Acessibilidade** — página inteira e modal aberto

Diferente de Settings, este arquivo interage **diretamente com locators Playwright** (`page.get_by_test_id`) em vez de um Page Object dedicado — padrão comum para páginas de demonstração/catálogo.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Ambiente | Servidor TestFlow em execução |
| Autenticação | `visit_authenticated` via fixture autouse |
| Dependências | `pytest`, `playwright`, `axe-playwright-python` |
| Constantes de TC | [`support/constants/test_cases.py`](../../../../support/constants/test_cases.py) |

```bash
pytest tests/components/test_components.py -v
pytest tests/components/test_components.py -m regression
pytest tests/components/test_components.py -m a11y
```

---

## Markers utilizados

| Marker | Onde aparece | Significado |
|--------|--------------|-------------|
| `regression` | Cada classe de teste (`@pytest.mark.regression`) | Suite de regressão |
| `a11y` | `TestComponentsAccessibility` | Testes de acessibilidade |
| `parametrize` (via TC) | `test_loading_button_shows_spinner...` | Vincula teste a ID de caso de teste (`TC-0501`) |

Não há `pytestmark` no nível do módulo — cada classe declara `@pytest.mark.regression` explicitamente.

---

## Visão geral da estrutura

```
test_components.py
├── Imports
├── Fixture autouse: components_page
├── TestButtons
├── TestModal (+ fixture autouse: open_modal)
├── TestTabs
├── TestAccordion
└── TestComponentsAccessibility
```

---

## Imports — bloco a bloco

### `import pytest`

Framework de testes — fixtures, markers, parametrização e classes de teste.

---

### `from playwright.sync_api import Page, expect`

| Símbolo | Papel |
|---------|-------|
| `Page` | Aba do navegador para interações síncronas |
| `expect` | Asserções com auto-retry do Playwright |

**Conceito:** API **sync** é ideal para iniciantes — cada ação bloqueia até completar. A variante `async_api` existe para testes assíncronos.

---

### `from conftest import check_a11y`

Executa varredura axe-core e falha em violações críticas/graves.

---

### `from support.auth import visit_authenticated`

Autentica via API e navega até o path informado — evita login manual repetido.

---

### `from support.constants.test_cases import TC, tc`

| Símbolo | Papel |
|---------|-------|
| `TC` | Classe com constantes de ID de casos de teste (ex.: `TC.COMP_LOADING_BUTTON = "TC-0501"`) |
| `tc(case_id, title)` | Formata string `"[TC-0501] loading button shows spinner..."` para relatórios |

**Conceito PyTest:** IDs de casos de teste rastreáveis em CI e integrações com Zephyr/Jira.

---

## Fixture: `components_page`

```python
@pytest.fixture(autouse=True)
def components_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/components.html")
    expect(page.get_by_test_id("page-components")).to_be_attached()
```

| Aspecto | Explicação |
|---------|------------|
| `autouse=True` | Setup automático antes de cada teste |
| `visit_authenticated` | Given: usuário logado |
| `to_be_attached()` | Elemento existe no DOM (pode estar oculto) — mais permissivo que `to_be_visible()` |

**Conceito Playwright:** `to_be_attached()` vs `to_be_visible()` — use attached quando só precisa confirmar presença no DOM.

---

## Classe `TestButtons`

```python
@pytest.mark.regression
class TestButtons:
```

Agrupa testes de botões e interações que disparam feedback (toast, diálogos).

---

### `test_all_button_variants_are_visible`

```python
def test_all_button_variants_are_visible(self, page: Page) -> None:
    for test_id in ("btn-primary", "btn-secondary", "btn-success", "btn-danger"):
        btn = page.get_by_test_id(test_id)
        expect(btn).to_be_visible()
        expect(btn).to_be_enabled()
```

| Passo | Descrição |
|-------|-----------|
| **Given** | Página Components carregada |
| **When** | Itera variantes de botão por `data-testid` |
| **Then** | Cada botão visível e habilitado |

**Conceito:** Loop em teste é válido quando valida conjunto homogêneo de elementos.

---

### `test_disabled_button_is_not_interactive`

```python
def test_disabled_button_is_not_interactive(self, page: Page) -> None:
    btn = page.get_by_test_id("btn-disabled")
    expect(btn).to_be_disabled()
    expect(btn).to_have_css("cursor", "not-allowed")
```

| **Then** | Botão desabilitado (`disabled`) e cursor CSS `not-allowed` |

Valida estado visual + semântico de botão inativo.

---

### `test_loading_button_shows_spinner_during_simulated_load`

```python
@pytest.mark.parametrize(
    "title",
    [tc(TC.COMP_LOADING_BUTTON, "loading button shows spinner during simulated load")],
    ids=[TC.COMP_LOADING_BUTTON],
)
def test_loading_button_shows_spinner_during_simulated_load(self, page: Page, title: str) -> None:
    del title
    page.clock.install()
    page.get_by_test_id("btn-loading").click()
    expect(page.get_by_test_id("btn-loading")).to_be_disabled()
    expect(page.locator(".spinner")).to_be_visible()
    page.clock.fast_forward(2000)
    expect(page.get_by_test_id("btn-loading")).to_be_enabled()
```

| Aspecto | Explicação |
|---------|------------|
| `@pytest.mark.parametrize` | Gera caso de teste com ID `TC-0501` no relatório |
| `del title` | Parâmetro existe só para documentação/ID — não usado no corpo |
| `page.clock.install()` | **Mock clock** do Playwright — controla timers JavaScript |
| `page.clock.fast_forward(2000)` | Avança 2 segundos sem espera real |

**Given/When/Then:**

- **Given:** Clock mockado instalado
- **When:** Clica botão loading
- **Then (imediato):** Botão desabilitado + spinner visível
- **When:** Avança 2s no clock
- **Then:** Botão habilitado novamente

**Conceito Playwright:** Clock API elimina `time.sleep` — testes rápidos e determinísticos.

---

### `test_toast_button_shows_a_toast_notification`

```python
def test_toast_button_shows_a_toast_notification(self, page: Page) -> None:
    page.get_by_test_id("btn-toast").click()
    toast = page.get_by_test_id("toast-message")
    expect(toast).to_be_visible()
    expect(toast).not_to_be_empty()
```

| **When** | Clica botão toast |
| **Then** | Toast visível com conteúdo |

---

### `test_native_alert_can_be_dismissed`

```python
def test_native_alert_can_be_dismissed(self, page: Page) -> None:
    messages: list[str] = []

    def handle_dialog(dialog) -> None:
        messages.append(dialog.message)
        dialog.accept()

    page.on("dialog", handle_dialog)
    page.get_by_test_id("btn-alert").click()
    assert messages
    assert messages[0]
```

| Conceito | Detalhe |
|----------|---------|
| `dialog.accept()` | Confirma `alert` |
| `dialog.message` | Captura texto do diálogo |
| `assert messages[0]` | Mensagem não vazia |

**Importante:** Registrar handler **antes** do clique que dispara o diálogo.

---

### `test_native_confirm_returns_true_on_accept`

```python
def test_native_confirm_returns_true_on_accept(self, page: Page) -> None:
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_test_id("btn-confirm").click()
    expect(page.get_by_test_id("dialog-result")).to_contain_text("Confirmed")
```

| **When** | Aceita confirm |
| **Then** | UI exibe `"Confirmed"` |

---

### `test_native_confirm_returns_false_on_cancel`

```python
def test_native_confirm_returns_false_on_cancel(self, page: Page) -> None:
    page.on("dialog", lambda dialog: dialog.dismiss())
    page.get_by_test_id("btn-confirm").click()
    expect(page.get_by_test_id("dialog-result")).to_contain_text("Cancelled")
```

| **When** | Cancela confirm (`dismiss`) |
| **Then** | UI exibe `"Cancelled"` |

---

## Classe `TestModal`

```python
@pytest.mark.regression
class TestModal:
    @pytest.fixture(autouse=True)
    def open_modal(self, page: Page) -> None:
        page.get_by_test_id("open-modal-btn").click()
        expect(page.get_by_test_id("modal-overlay")).to_be_visible()
```

### Fixture aninhada: `open_modal`

| Aspecto | Explicação |
|---------|------------|
| Escopo | Apenas testes dentro de `TestModal` |
| `autouse=True` | Abre modal antes de cada teste da classe |
| Ordem de execução | `components_page` (módulo) → `open_modal` (classe) → teste |

**Conceito PyTest:** Fixtures podem ser definidas **dentro de classes** — limitam setup ao grupo relevante.

---

### `test_opens_modal_and_shows_title`

```python
def test_opens_modal_and_shows_title(self, page: Page) -> None:
    expect(page.locator("#modal-title")).to_contain_text("Confirm action")
```

**Then:** Título do modal contém `"Confirm action"`.

**Conceito Playwright:** `page.locator("#modal-title")` usa seletor CSS; `get_by_test_id` é preferido quando disponível.

---

### `test_has_accessible_role_dialog`

```python
def test_has_accessible_role_dialog(self, page: Page) -> None:
    overlay = page.get_by_test_id("modal-overlay")
    expect(overlay).to_have_attribute("role", "dialog")
    expect(overlay).to_have_attribute("aria-modal", "true")
```

Valida contrato de acessibilidade para modais (WAI-ARIA).

---

### `test_closes_on_confirm_button`

```python
def test_closes_on_confirm_button(self, page: Page) -> None:
    page.get_by_test_id("modal-confirm-btn").click()
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
    expect(page.get_by_test_id("toast-message")).to_be_visible()
```

| **When** | Confirma ação |
| **Then** | Modal fecha + toast de feedback |

---

### `test_closes_on_cancel_button`

```python
def test_closes_on_cancel_button(self, page: Page) -> None:
    page.get_by_test_id("modal-cancel-btn").click()
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

Fechamento via cancelamento.

---

### `test_closes_on_close_button`

```python
def test_closes_on_close_button(self, page: Page) -> None:
    page.get_by_test_id("modal-close-btn").click()
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

Fechamento via botão X.

---

### `test_closes_on_escape_key`

```python
def test_closes_on_escape_key(self, page: Page) -> None:
    page.keyboard.press("Escape")
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

**Conceito Playwright:** `page.keyboard` simula teclas — padrão UX esperado em modais.

---

### `test_closes_on_overlay_background_click`

```python
def test_closes_on_overlay_background_click(self, page: Page) -> None:
    page.get_by_test_id("modal-overlay").click(position={"x": 5, "y": 5})
    expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
```

| Conceito | Detalhe |
|----------|---------|
| `position={"x": 5, "y": 5}` | Clica canto superior-esquerdo do overlay (fora do conteúdo central) |

Simula "clicar fora" para fechar modal.

---

### `test_aria_hidden_is_set_correctly_when_closed`

```python
def test_aria_hidden_is_set_correctly_when_closed(self, page: Page) -> None:
    page.get_by_test_id("modal-cancel-btn").click()
    expect(page.get_by_test_id("modal-overlay")).to_have_attribute("aria-hidden", "true")
```

**Then:** Após fechar, overlay marcado como oculto para leitores de tela.

---

## Classe `TestTabs`

```python
@pytest.mark.regression
class TestTabs:
```

Testes do componente de abas (tablist/tab/tabpanel).

---

### `test_overview_tab_is_active_by_default`

```python
def test_overview_tab_is_active_by_default(self, page: Page) -> None:
    expect(page.get_by_test_id("tab-overview")).to_have_attribute("aria-selected", "true")
    expect(page.get_by_test_id("tab-panel-overview")).to_be_visible()
```

Estado inicial: aba Overview selecionada e painel visível.

---

### `test_clicking_cypress_tab_activates_it_and_shows_its_panel`

```python
def test_clicking_cypress_tab_activates_it_and_shows_its_panel(self, page: Page) -> None:
    page.get_by_test_id("tab-cypress").click()
    expect(page.get_by_test_id("tab-cypress")).to_have_attribute("aria-selected", "true")
    expect(page.get_by_test_id("tab-panel-cypress")).to_be_visible()
    expect(page.get_by_test_id("tab-panel-overview")).not_to_be_visible()
```

| **When** | Clica aba Cypress |
| **Then** | Aba ativa + painel Cypress visível + painel Overview oculto |

---

### `test_clicking_playwright_tab_activates_it_and_shows_its_panel`

```python
def test_clicking_playwright_tab_activates_it_and_shows_its_panel(self, page: Page) -> None:
    page.get_by_test_id("tab-playwright").click()
    expect(page.get_by_test_id("tab-playwright")).to_have_attribute("aria-selected", "true")
    expect(page.get_by_test_id("tab-panel-playwright")).to_be_visible()
```

Mesmo padrão para aba Playwright.

---

### `test_only_one_tab_panel_is_visible_at_a_time`

```python
def test_only_one_tab_panel_is_visible_at_a_time(self, page: Page) -> None:
    page.get_by_test_id("tab-cypress").click()
    expect(page.locator(".tab-panel.active")).to_have_count(1)
```

**Then:** Exatamente um painel com classe `active` — exclusividade de visualização.

---

### `test_tabs_have_correct_role_attributes`

```python
def test_tabs_have_correct_role_attributes(self, page: Page) -> None:
    expect(page.locator('[role="tablist"]')).to_be_attached()
    expect(page.locator('[role="tab"]')).to_have_count(3)
    expect(page.locator('[role="tabpanel"]')).to_have_count(3)
```

Valida estrutura ARIA: 1 tablist, 3 tabs, 3 tabpanels.

---

### `test_supports_keyboard_focus_on_tab_controls`

```python
def test_supports_keyboard_focus_on_tab_controls(self, page: Page) -> None:
    expect(page.get_by_test_id("tab-overview")).to_have_attribute("aria-selected", "true")
    tab = page.get_by_test_id("tab-cypress")
    tab.focus()
    expect(tab).to_be_focused()
    tab.click()
    expect(page.get_by_test_id("tab-panel-cypress")).to_be_visible()
```

| Passo | Descrição |
|-------|-----------|
| **When** | Foca aba via teclado/programático |
| **Then** | Elemento focado |
| **When** | Ativa aba |
| **Then** | Painel correspondente visível |

**Conceito:** `locator.focus()` + `to_be_focused()` testam navegação acessível.

---

## Classe `TestAccordion`

```python
@pytest.mark.regression
class TestAccordion:
```

Testes de painéis expansíveis (accordion).

---

### `test_all_panels_are_collapsed_by_default`

```python
def test_all_panels_are_collapsed_by_default(self, page: Page) -> None:
    for n in (1, 2, 3):
        expect(page.get_by_test_id(f"accordion-trigger-{n}")).to_have_attribute(
            "aria-expanded", "false"
        )
        expect(page.get_by_test_id(f"accordion-panel-{n}")).not_to_be_visible()
```

**Then:** Três painéis colapsados (`aria-expanded="false"`, conteúdo oculto).

---

### `test_expands_first_panel_on_click`

```python
def test_expands_first_panel_on_click(self, page: Page) -> None:
    page.get_by_test_id("accordion-trigger-1").click()
    expect(page.get_by_test_id("accordion-trigger-1")).to_have_attribute("aria-expanded", "true")
    expect(page.get_by_test_id("accordion-panel-1")).to_be_visible()
```

| **When** | Clica trigger do painel 1 |
| **Then** | Expandido e visível |

---

### `test_collapses_first_panel_on_second_click`

```python
def test_collapses_first_panel_on_second_click(self, page: Page) -> None:
    trigger = page.get_by_test_id("accordion-trigger-1")
    trigger.click()
    trigger.click()
    expect(page.get_by_test_id("accordion-panel-1")).not_to_be_visible()
```

Comportamento toggle — segundo clique colapsa.

---

### `test_multiple_panels_can_be_open_simultaneously`

```python
def test_multiple_panels_can_be_open_simultaneously(self, page: Page) -> None:
    page.get_by_test_id("accordion-trigger-1").click()
    page.get_by_test_id("accordion-trigger-2").click()
    expect(page.get_by_test_id("accordion-panel-1")).to_be_visible()
    expect(page.get_by_test_id("accordion-panel-2")).to_be_visible()
```

Este accordion permite **múltiplos painéis abertos** (não exclusivo como tabs).

---

## Classe `TestComponentsAccessibility`

```python
@pytest.mark.regression
@pytest.mark.a11y
class TestComponentsAccessibility:
```

---

### `test_components_page_has_no_critical_a11y_violations`

```python
def test_components_page_has_no_critical_a11y_violations(self, page: Page) -> None:
    check_a11y(page)
```

Varredura axe na página Components inteira (regra `color-contrast` desabilitada por padrão em `check_a11y`).

---

### `test_modal_dialog_passes_a11y_when_open`

```python
def test_modal_dialog_passes_a11y_when_open(self, page: Page) -> None:
    page.get_by_test_id("open-modal-btn").click()
    expect(page.get_by_test_id("modal-overlay")).to_be_visible()
    check_a11y(page)
```

| **Given** | Modal aberto |
| **Then** | Sem violações críticas/graves com modal visível |

Testa acessibilidade em estado interativo — quando modais abertos frequentemente introduzem problemas.

---

## Resumo de conceitos aprendidos

| Conceito | Onde aparece |
|----------|--------------|
| Locators diretos | `get_by_test_id`, `locator`, seletores CSS/ARIA |
| Mock Clock | `page.clock.install()` + `fast_forward()` |
| Parametrização + TC IDs | `@pytest.mark.parametrize` com `TC`/`tc` |
| Diálogos nativos | `page.on("dialog")`, `accept()`, `dismiss()` |
| Fixture de classe | `open_modal` dentro de `TestModal` |
| Teclado | `page.keyboard.press("Escape")`, `focus()` |
| Clique com posição | `click(position={...})` |
| ARIA | `role`, `aria-selected`, `aria-expanded`, `aria-modal` |
| Acessibilidade | `check_a11y` com marker `@pytest.mark.a11y` |
