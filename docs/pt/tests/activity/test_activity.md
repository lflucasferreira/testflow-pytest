# Testes da Página de Activity

**Arquivo-fonte:** [`../../../../tests/activity/test_activity.py`](../../../../tests/activity/test_activity.py)

---

## Propósito

Este módulo valida a página **Activity** (`/web/activity.html`), focada em padrões avançados de automação:

- **Chamadas API via UI** — botões que disparam fetch e exibem resultados
- **Interceptação de rede** — delay artificial e mock de respostas
- **Estado local** — contador increment/decrement/reset
- **Progresso simulado** — barra de download
- **Conteúdo dinâmico** — carregamento assíncrono
- **Fixtures de dados** — leitura de JSON e CSV
- **Upload de arquivo** — drag-and-drop / input file

É um laboratório para conceitos que vão além de cliques simples: rede, tempo, arquivos e dados externos.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Ambiente | Servidor TestFlow em execução |
| Autenticação | `visit_authenticated` via fixture autouse |
| Fixtures | [`fixtures/users/empty-list.json`](../../../../fixtures/users/empty-list.json), [`fixtures/sample.csv`](../../../../fixtures/sample.csv), [`fixtures/lookups/countries.json`](../../../../fixtures/lookups/countries.json) |
| Helper | [`support/helpers/fixtures.py`](../../../../support/helpers/fixtures.py) |

```bash
pytest tests/activity/test_activity.py -v
pytest tests/activity/test_activity.py -m smoke
pytest tests/activity/test_activity.py -m api
pytest tests/activity/test_activity.py -m regression
```

---

## Markers utilizados

| Marker | Onde aparece | Significado |
|--------|--------------|-------------|
| `regression` | Classe `TestActivity` | Suite de regressão |
| `smoke` | `test_fetches_users_via_api_button` | Gate rápido de API via UI |
| `api` | `test_fetches_users_via_api_button` | Teste com validação de resposta HTTP |

---

## Visão geral da estrutura

```
test_activity.py
├── Imports
├── Fixture autouse: activity_page
└── TestActivity (8 métodos de teste)
```

---

## Imports — bloco a bloco

### `import time`

Biblioteca padrão para pausas. Usada no handler de rota lenta (`time.sleep(1.5)`) para simular latência de API.

**Nota:** Em testes UI preferimos `page.clock` quando possível; aqui o delay está **no handler de rede**, não no teste em si.

---

### `from pathlib import Path`

Manipulação orientada a objetos de caminhos de arquivo. Usado indiretamente via `FIXTURES_ROOT` (que é um `Path`).

---

### `import pytest`

Framework de testes.

---

### `from playwright.sync_api import Page, expect`

API síncrona do Playwright.

---

### `from support.auth import visit_authenticated`

Autenticação via API + navegação.

**Nota:** Este arquivo **não** importa `check_a11y` — não há testes de acessibilidade aqui.

---

### `from support.helpers.fixtures import FIXTURES_ROOT, read_fixture`

| Símbolo | Papel |
|---------|-------|
| `FIXTURES_ROOT` | `Path` absoluto para pasta `fixtures/` na raiz do projeto |
| `read_fixture(relative_path)` | Lê e parseia JSON relativo a `FIXTURES_ROOT` |

---

## Fixture: `activity_page`

```python
@pytest.fixture(autouse=True)
def activity_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/activity.html")
    expect(page.get_by_test_id("page-activity")).to_be_attached()
```

| Aspecto | Explicação |
|---------|------------|
| Setup | Login via API + goto `/web/activity.html` |
| Verificação | Elemento raiz `page-activity` presente no DOM |

---

## Classe `TestActivity`

```python
@pytest.mark.regression
class TestActivity:
```

Única classe — todos os testes de activity agrupados aqui.

---

### `test_fetches_users_via_api_button`

```python
@pytest.mark.smoke
@pytest.mark.api
def test_fetches_users_via_api_button(self, page: Page) -> None:
    with page.expect_response("**/api/users") as response_info:
        page.get_by_test_id("fetch-users-btn").click()
    response = response_info.value
    assert response.status == 200
    expect(page.get_by_test_id("api-result")).not_to_be_empty()
```

| Passo | Descrição |
|-------|-----------|
| **Given** | Página Activity carregada |
| **When** | Clica botão fetch dentro de `expect_response` |
| **Then (rede)** | Resposta `/api/users` com status 200 |
| **Then (UI)** | Área de resultado não vazia |

**Conceitos Playwright:**

| API | Uso |
|-----|-----|
| `page.expect_response("**/api/users")` | Context manager que captura resposta cujo URL corresponde ao glob |
| `response_info.value` | Objeto `Response` após a ação |
| `response.status` | Código HTTP |

**Markers:** `smoke` + `api` — teste rápido que valida integração UI ↔ API.

---

### `test_handles_slow_api_with_intercept_delay`

```python
def test_handles_slow_api_with_intercept_delay(self, page: Page) -> None:
    def slow_handler(route) -> None:
        time.sleep(1.5)
        route.continue_()

    page.route("**/api/slow**", slow_handler)
    with page.expect_response("**/api/slow**"):
        page.get_by_test_id("fetch-slow-btn").click()
    expect(page.get_by_test_id("api-result")).to_be_visible()
```

| Aspecto | Explicação |
|---------|------------|
| `page.route` | Registra handler para URLs matching glob |
| `slow_handler` | Aguarda 1.5s antes de continuar requisição real |
| `route.continue_()` | Encaminha para servidor real (com delay) |
| Asserção final | UI exibe resultado após API lenta |

**Given/When/Then:**

- **Given:** Rota `/api/slow` interceptada com delay
- **When:** Clica botão de API lenta
- **Then:** Resposta recebida + resultado visível na UI

**Conceito:** Testa comportamento de **loading states** e resiliência a latência sem mockar resposta completa.

---

### `test_increments_and_decrements_counter`

```python
def test_increments_and_decrements_counter(self, page: Page) -> None:
    page.get_by_test_id("counter-increment").click()
    page.get_by_test_id("counter-increment").click()
    expect(page.get_by_test_id("counter-value")).to_contain_text("2")
    page.get_by_test_id("counter-decrement").click()
    expect(page.get_by_test_id("counter-value")).to_contain_text("1")
    page.get_by_test_id("counter-reset").click()
    expect(page.get_by_test_id("counter-value")).to_contain_text("0")
```

| Sequência | Valor esperado |
|-----------|----------------|
| +1, +1 | `"2"` |
| -1 | `"1"` |
| reset | `"0"` |

Testa **estado local** JavaScript — contador reativo sem envolver backend.

**Conceito:** `to_contain_text` é tolerante — funciona mesmo se o elemento tiver markup extra.

---

### `test_starts_download_progress_simulation`

```python
def test_starts_download_progress_simulation(self, page: Page) -> None:
    page.get_by_test_id("progress-start").click()
    expect(page.get_by_test_id("download-progress")).to_be_attached()
```

| **When** | Inicia simulação de download |
| **Then** | Elemento de progresso existe no DOM |

Usa `to_be_attached()` — barra pode existir antes de animação visual completar.

---

### `test_loads_dynamic_content_section`

```python
def test_loads_dynamic_content_section(self, page: Page) -> None:
    page.get_by_test_id("load-dynamic-btn").click()
    expect(page.get_by_test_id("dynamic-content")).not_to_be_empty()
```

| **When** | Clica carregar conteúdo dinâmico |
| **Then** | Seção preenchida (não vazia) |

Testa conteúdo injetado assincronamente após interação.

---

### `test_uses_mock_api_get_with_empty_users_fixture`

```python
def test_uses_mock_api_get_with_empty_users_fixture(self, page: Page) -> None:
    page.route(
        "**/api/users",
        lambda route: route.fulfill(json=read_fixture("users/empty-list.json")),
    )
    with page.expect_response("**/api/users"):
        page.get_by_test_id("fetch-users-btn").click()
    expect(page.get_by_test_id("api-result")).to_contain_text("Fetched 0 users")
```

| Aspecto | Explicação |
|---------|------------|
| `route.fulfill(json=...)` | Resposta mockada — **não** chama backend real |
| `read_fixture("users/empty-list.json")` | Payload de lista vazia do disco |
| Asserção | UI reflete `"Fetched 0 users"` |

**Given/When/Then:**

- **Given:** API `/api/users` retorna lista vazia via mock
- **When:** Usuário clica fetch
- **Then:** Mensagem confirma zero usuários

**Conceito:** Mock de API permite testar **edge cases** (lista vazia) de forma determinística.

---

### `test_read_fixture_exposes_countries_lookup_for_test_data`

```python
def test_read_fixture_exposes_countries_lookup_for_test_data(self) -> None:
    data = read_fixture("lookups/countries.json")
    codes = [country["code"] for country in data["countries"]]
    assert "CA" in codes
```

| Aspecto | Explicação |
|---------|------------|
| Sem `page` | Teste **unitário** do helper — não precisa de navegador |
| List comprehension | Extrai códigos de país |
| `assert "CA" in codes` | Fixture contém Canadá |

**Conceito PyTest:** Nem todo teste em arquivo Playwright precisa da fixture `page` — testes de utilitários podem coexistir.

---

### `test_accepts_csv_file_via_drag_and_drop_on_drop_zone`

```python
def test_accepts_csv_file_via_drag_and_drop_on_drop_zone(self, page: Page) -> None:
    csv_path = FIXTURES_ROOT / "sample.csv"
    file_input = page.locator('[data-testid="drop-zone"] input[type="file"]')
    if file_input.count():
        file_input.set_input_files(str(csv_path))
    else:
        page.get_by_test_id("drop-zone").click()
    expect(page.get_by_test_id("page-activity")).to_be_visible()
```

| Aspecto | Explicação |
|---------|------------|
| `FIXTURES_ROOT / "sample.csv"` | Caminho absoluto para CSV de teste |
| `locator(... input[type="file"])` | Input file oculto dentro da drop zone |
| `file_input.count()` | Verifica se input existe |
| `set_input_files(str(csv_path))` | Simula seleção de arquivo (equivale a upload) |
| Fallback | Se não houver input, clica na drop zone |
| Asserção mínima | Página permanece estável/visível |

**Conceito Playwright:** `set_input_files()` é a forma confiável de testar upload — drag-and-drop real é mais complexo; muitos projetos testam via input file subjacente.

**Conceito `Path`:** `FIXTURES_ROOT / "sample.csv"` concatena caminhos de forma cross-platform.

---

## Resumo de conceitos aprendidos

| Conceito | Onde aparece |
|----------|--------------|
| Interceptação de rede | `page.route`, `route.continue_()`, `route.fulfill()` |
| Captura de resposta | `page.expect_response` |
| Simulação de latência | `time.sleep` em route handler |
| Mock de API | `fulfill(json=read_fixture(...))` |
| Estado local UI | Contador increment/decrement |
| Conteúdo dinâmico | `not_to_be_empty()` após click |
| Fixtures de dados | `read_fixture`, `FIXTURES_ROOT` |
| Upload de arquivo | `set_input_files()` |
| Teste sem browser | Método sem parâmetro `page` |
| Markers | `smoke`, `api`, `regression` |

---

## Comparativo: Activity vs outros módulos

| Aspecto | Activity | Settings | Components | Wizard |
|---------|----------|----------|------------|--------|
| Page Object | Não | Sim (`SettingsPage`) | Não | Helpers privados |
| Interceptação API | Sim (forte) | Sim (pontual) | Não | Sim (countries) |
| A11y | Não | Sim | Sim | Sim |
| Factories | Não | Não | TC constants | Faker factories |
| Foco | Rede, arquivos, estado | Formulários complexos | Componentes UI | Fluxo multi-step |
