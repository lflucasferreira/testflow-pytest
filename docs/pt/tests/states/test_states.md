# Testes de Estados de UI — Loading, erro, sucesso, vazio e acessibilidade

**Arquivo-fonte:** [`../../../../tests/states/test_states.py`](../../../../tests/states/test_states.py)

---

## Propósito

Este módulo exercita a página **States** (`/web/states.html`), projetada para demonstrar **transições de estado** comuns em aplicações reais:

| Área | Estados cobertos |
|------|------------------|
| Skeleton loading | idle → carregando → cards carregados → reset |
| Fetch simulado | erro (falha) vs sucesso |
| Listagem | empty state (busca sem resultados) |
| Grid parcial | cards com status mistos |
| Acessibilidade | varredura axe sem violações críticas |

É material ideal para aprender **esperas explícitas**, **timeouts customizados** e integração com **axe-playwright**.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Servidor sandbox | Rodando com rotas `/web/states.html` |
| Autenticação | `visit_authenticated` via API |
| Pacote a11y | `axe-playwright-python` (função `check_a11y` em `conftest.py`) |
| Fixtures | `page`, `api_request` |

**Execução:**

```bash
pytest tests/states/test_states.py -v
pytest tests/states/test_states.py -m a11y
pytest tests/states/test_states.py -m smoke
```

---

## Markers utilizados

| Marker | Aplicação |
|--------|-----------|
| `regression` | Todas as classes de teste |
| `smoke` | `test_shows_idle_message_before_load` |
| `a11y` | Classe `TestStatesAccessibility` |

---

## Visão geral da estrutura

```
test_states.py
├── imports
├── fixture autouse: states_page
├── TestSkeletonLoading (3 testes)
├── TestErrorAndSuccessStates (2 testes)
├── TestEmptyAndPartialStates (2 testes)
└── TestStatesAccessibility (1 teste)
```

---

## Imports — bloco a bloco

### `import pytest`

Framework de testes — fixtures, markers e descoberta de classes.

---

### `from playwright.sync_api import Page, expect`

- **`Page`**: aba do navegador para interações e localizadores.
- **`expect`**: asserções com auto-retry (essencial após cliques que disparam animações ou fetch).

---

### `from conftest import check_a11y`

Importa helper **do nível raiz do projeto** (não de `support/`). Executa axe-core via `axe_playwright_python`:

- Tags WCAG 2.0/2.1 (`wcag2a`, `wcag2aa`)
- Ignora regra `color-contrast` por padrão (comum em sandboxes de demo)
- Falha se houver violações `critical` ou `serious`

**Conceito:** testes a11y complementam testes funcionais — um botão pode “funcionar” e ainda ser inacessível.

---

### `from support.auth import visit_authenticated`

Autentica via API e navega ao path informado. Mesmo padrão do módulo Advanced.

---

## Fixture: `states_page`

```python
@pytest.fixture(autouse=True)
def states_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/states.html")
    expect(page.get_by_test_id("page-states")).to_be_attached()
```

| Aspecto | Detalhe |
|---------|---------|
| Escopo | Function (padrão) — roda antes de cada teste |
| autouse | Sim — todos os testes começam na página States autenticada |
| Gate | `page-states` deve existir no DOM |

**Given global do módulo:** usuário logado em `/web/states.html`.

---

## Classe `TestSkeletonLoading`

Valida o padrão **skeleton screen**: placeholder animado enquanto dados carregam.

---

### `test_shows_idle_message_before_load`

```python
@pytest.mark.smoke
def test_shows_idle_message_before_load(self, page: Page) -> None:
    expect(page.get_by_test_id("skeleton-idle")).to_contain_text("Load cards")
```

| Fase | Descrição |
|------|-----------|
| **Given** | Página States recém-carregada, seção skeleton no estado inicial |
| **When** | Nenhuma ação |
| **Then** | Mensagem idle contém texto “Load cards” |

**Marker smoke:** verificação rápida de que a página renderizou o estado idle.

**Playwright:** `to_contain_text` faz match parcial (substring), útil para copy dinâmica.

---

### `test_loads_metric_cards_after_skeleton_delay`

```python
def test_loads_metric_cards_after_skeleton_delay(self, page: Page) -> None:
    page.get_by_test_id("skeleton-trigger").click()
    expect(page.get_by_test_id("loaded-card")).to_have_count(4, timeout=5000)
```

| Fase | Descrição |
|------|-----------|
| **Given** | Estado idle |
| **When** | Clica `skeleton-trigger` (simula fetch com delay) |
| **Then** | Exatamente 4 elementos `loaded-card` aparecem em até 5 segundos |

**Conceito Playwright — timeout:** o padrão é ~5s; aqui reforça explicitamente `timeout=5000` ms porque skeleton + delay podem exceder o default em ambientes lentos.

**Conceito UI:** skeleton → conteúdo real é assíncrono; nunca use `time.sleep` fixo — use asserções que esperam.

---

### `test_resets_skeleton_section`

```python
def test_resets_skeleton_section(self, page: Page) -> None:
    page.get_by_test_id("skeleton-trigger").click()
    expect(page.get_by_test_id("loaded-card").first).to_be_visible(timeout=5000)
    page.get_by_test_id("skeleton-reset").click()
    expect(page.get_by_test_id("skeleton-idle")).to_be_visible()
```

| Fase | Descrição |
|------|-----------|
| **Given** | Idle |
| **When** | Carrega cards → clica reset |
| **Then** | Volta ao estado idle visível |

**Fluxo completo:** load → assert intermediária → reset → assert final. Modelo de teste de **ciclo de vida** de componente.

---

## Classe `TestErrorAndSuccessStates`

Simula respostas de API bem-sucedidas e com falha na UI.

---

### `test_shows_error_state_on_failed_fetch`

```python
def test_shows_error_state_on_failed_fetch(self, page: Page) -> None:
    page.get_by_test_id("error-trigger").click()
    error = page.get_by_test_id("error-state")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Request failed")
```

| Fase | Descrição |
|------|-----------|
| **Given** | Página States |
| **When** | Dispara fetch que falha (`error-trigger`) |
| **Then** | Banner/área de erro visível com mensagem “Request failed” |

**Padrão:** reutilizar localizador em variável (`error`) para múltiplas asserções legíveis.

---

### `test_shows_success_state_on_successful_fetch`

```python
def test_shows_success_state_on_successful_fetch(self, page: Page) -> None:
    page.get_by_test_id("success-trigger").click()
    success = page.get_by_test_id("success-state")
    expect(success).to_be_visible()
    expect(success).to_contain_text("succeeded")
```

Espelho do teste de erro — valida **feedback positivo** após operação bem-sucedida.

---

## Classe `TestEmptyAndPartialStates`

Cenários de dados incompletos ou ausentes.

---

### `test_renders_empty_state_when_search_has_no_matches`

```python
def test_renders_empty_state_when_search_has_no_matches(self, page: Page) -> None:
    page.get_by_test_id("empty-search").fill("xyzno match")
    expect(page.get_by_test_id("empty-state")).to_be_visible()
    expect(page.get_by_test_id("result-list")).not_to_be_attached()
```

| Fase | Descrição |
|------|-----------|
| **Given** | Campo de busca vazio |
| **When** | Preenche termo sem correspondências |
| **Then** | Empty state visível; lista de resultados **não** está no DOM |

**Conceito:** `not_to_be_attached` confirma que a UI não renderizou lista vazia oculta — padrão empty state correto.

**Playwright:** `fill()` limpa e digita; dispara eventos de input como usuário real.

---

### `test_loads_partial_grid_with_mixed_card_statuses`

```python
def test_loads_partial_grid_with_mixed_card_statuses(self, page: Page) -> None:
    page.get_by_test_id("partial-trigger").click()
    expect(page.locator('[data-testid^="partial-card-"]')).to_have_count(6)
```

| Fase | Descrição |
|------|-----------|
| **Given** | Grid parcial não carregado |
| **When** | Clica `partial-trigger` |
| **Then** | 6 cards com `data-testid` prefixado `partial-card-` |

**Seletor CSS:** `[data-testid^="partial-card-"]` = atributo **começa com** prefixo. Alternativa Playwright: `get_by_test_id` não suporta prefix nativamente; `locator` CSS é adequado aqui.

---

## Classe `TestStatesAccessibility`

```python
@pytest.mark.regression
@pytest.mark.a11y
class TestStatesAccessibility:
    def test_states_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
```

| Fase | Descrição |
|------|-----------|
| **Given** | Página States carregada (fixture) |
| **When** | `check_a11y` executa axe na página inteira |
| **Then** | Nenhuma violação critical/serious (exceto regras desabilitadas) |

**Marker `a11y`:** permite pipeline dedicado (`pytest -m a11y`).

**Nota para estudantes:** a11y é snapshot comportamental da árvore acessível atual — alterações de copy ou ARIA podem exigir ajuste de regras desabilitadas.

---

## Conceitos PyTest e Playwright — resumo

### Espera e flakiness

- Preferir `expect(..., timeout=5000)` a sleeps fixos.
- Após cliques assíncronos, sempre asserção web-first.

### Organização

- Uma classe por **feature/estado** facilita leitura e relatórios.
- Fixture `autouse` única por módulo evita duplicar login.

### Given / When / Then

| Classe | When típico |
|--------|-------------|
| Skeleton | clique em trigger / reset |
| Error/Success | clique em triggers de fetch |
| Empty/Partial | fill / clique |
| A11y | (sem When — scan estático) |

---

## Checklist de aprendizado

- [ ] Explicar skeleton loading vs spinner tradicional
- [ ] Justificar `timeout=5000` no skeleton
- [ ] Diferenciar empty state visível vs lista vazia no DOM
- [ ] Descrever o que `check_a11y` faz internamente
- [ ] Executar `-m a11y` isoladamente
