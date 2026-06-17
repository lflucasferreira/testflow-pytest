# Testes Avançados — Shadow DOM, iframes e viewport

**Arquivo-fonte:** [`../../../../tests/advanced/test_advanced.py`](../../../../tests/advanced/test_advanced.py)

---

## Propósito

Este módulo valida a página **Advanced** (`/web/advanced.html`), que concentra cenários de front-end mais complexos do sandbox TestFlow:

- **Shadow DOM** — conteúdo encapsulado fora da árvore DOM principal
- **iframe** — carregamento de conteúdo embutido
- **Links externos** — atributos `href` e `target`
- **Viewport responsivo** — comportamento em tamanho mobile vs desktop
- **Navegação** — botão que leva o usuário para outra rota

Os testes são **E2E de interface** com Playwright (modo síncrono) e servem como material de treinamento para localizadores, asserções web-first e fixtures de setup.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Ambiente | Servidor do sandbox em execução (variável `BASE_URL` configurada) |
| Autenticação | Credenciais demo válidas (`DEMO_EMAIL`, `DEMO_PASSWORD`) |
| Dependências | `pytest`, `playwright`, plugin `pytest-playwright` |
| Fixtures globais | `page` (Playwright), `api_request` (definidas em `conftest.py`) |
| Navegador | Chromium/ Firefox/ WebKit conforme configuração do projeto |

**Como executar apenas este arquivo:**

```bash
pytest tests/advanced/test_advanced.py -v
```

**Filtrar por marker:**

```bash
pytest tests/advanced/test_advanced.py -m smoke
pytest tests/advanced/test_advanced.py -m regression
```

---

## Markers utilizados

| Marker | Onde aparece | Significado |
|--------|--------------|-------------|
| `@pytest.mark.regression` | Classe `TestAdvanced` | Suite de regressão completa |
| `@pytest.mark.smoke` | `test_renders_shadow_dom_section`, `test_renders_shadow_section_at_mobile_viewport` | Subconjunto rápido para gate de CI |

Markers registrados em `conftest.py` via `pytest_configure`.

---

## Visão geral da estrutura

```
test_advanced.py
├── imports
├── fixture autouse: advanced_page
└── class TestAdvanced
    ├── test_renders_shadow_dom_section
    ├── test_accesses_content_inside_shadow_root
    ├── test_loads_demo_iframe
    ├── test_shows_external_link_with_target_blank
    ├── test_renders_shadow_section_at_mobile_viewport
    └── test_navigates_with_page_finish_button
```

---

## Imports — bloco a bloco

### `import re`

Biblioteca padrão do Python para **expressões regulares**. Usada para validar URLs e atributos com padrões flexíveis (ex.: `href` que começa com `http`, `src` não vazio).

**Conceito PyTest/Playwright:** asserções como `to_have_attribute("src", re.compile(r".+"))` aceitam regex do módulo `re`, não apenas strings literais.

---

### `import pytest`

Framework de testes. Fornece:

- `@pytest.fixture` — setup/teardown reutilizável
- `@pytest.mark.*` — categorização e filtros na linha de comando
- Descoberta automática de classes `Test*` e métodos `test_*`

---

### `from playwright.sync_api import Page, expect`

| Símbolo | Papel |
|---------|-------|
| `Page` | Representa uma aba do navegador; ponto de entrada para navegação, cliques e localizadores |
| `expect` | API de asserções **web-first** do Playwright — espera automaticamente até a condição ser verdadeira (auto-retry) |

**Conceito Playwright:** preferir `expect(locator).to_be_visible()` em vez de `assert locator.is_visible()`, pois `expect` aguarda estabilidade da UI.

---

### `from support.auth import visit_authenticated`

Helper do projeto que:

1. Obtém token via API (`fetch_auth_token`)
2. Injeta sessão no navegador (`inject_auth` + `sessionStorage`)
3. Navega até o `path` informado já autenticado

Evita repetir login manual em cada teste de página protegida.

---

### `from support.constants.viewports import DESKTOP, MOBILE`

Constantes de dimensão de tela:

| Constante | Valor |
|-----------|-------|
| `DESKTOP` | `{"width": 1280, "height": 800}` |
| `MOBILE` | `{"width": 375, "height": 812}` |

Usadas com `page.set_viewport_size(...)`.

---

## Fixture: `advanced_page`

```python
@pytest.fixture(autouse=True)
def advanced_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/advanced.html")
    expect(page.get_by_test_id("page-advanced")).to_be_attached()
```

### Parâmetros injetados pelo PyTest

| Parâmetro | Origem | Função |
|-----------|--------|--------|
| `page` | Fixture do pytest-playwright | Instância da página do navegador |
| `api_request` | `conftest.py` | Contexto HTTP para login via API |

### Comportamento

- **`autouse=True`**: executada automaticamente antes de **cada** teste do módulo, sem precisar declarar o nome da fixture nos métodos de teste.
- **Given (Dado):** usuário autenticado na URL `/web/advanced.html`.
- **Then (Então):** elemento raiz `page-advanced` está anexado ao DOM.

**Conceito PyTest:** fixtures `autouse` centralizam setup comum e mantêm testes enxutos — cada método recebe a página já preparada.

---

## Classe `TestAdvanced`

```python
@pytest.mark.regression
class TestAdvanced:
```

Agrupa testes relacionados à página Advanced. PyTest coleta todos os métodos `test_*` dentro da classe.

O marker `regression` na classe aplica-se conceptualmente ao grupo (dependendo da versão do PyTest, markers em classe podem precisar ser repetidos nos métodos para filtros `-m`; aqui os métodos smoke têm marker próprio).

---

### `test_renders_shadow_dom_section`

```python
@pytest.mark.smoke
def test_renders_shadow_dom_section(self, page: Page) -> None:
    expect(page.get_by_test_id("section-shadow")).to_be_visible()
    expect(page.get_by_test_id("shadow-host")).to_be_attached()
```

| Fase | Ação |
|------|------|
| **Given** | Página Advanced carregada (fixture `advanced_page`) |
| **When** | (Nenhuma interação — teste de renderização estática) |
| **Then** | Seção shadow visível; host do shadow DOM anexado |

**Localizadores:** `get_by_test_id` usa o atributo `data-testid` — estratégia estável e recomendada.

**Diferença Playwright:**

- `to_be_visible()` — elemento visível para o usuário (não `display:none`, etc.)
- `to_be_attached()` — presente no DOM (pode estar oculto)

---

### `test_accesses_content_inside_shadow_root`

```python
def test_accesses_content_inside_shadow_root(self, page: Page) -> None:
    shadow_content = page.get_by_test_id("shadow-host").locator("*")
    expect(shadow_content.first).to_be_attached()
    assert shadow_content.count() >= 1
```

| Fase | Ação |
|------|------|
| **Given** | Host `shadow-host` no DOM |
| **When** | Localizador desce para filhos (`locator("*")`) |
| **Then** | Pelo menos um nó filho existe dentro do shadow root |

**Conceito Playwright:** a partir do Playwright 1.x+, localizadores atravessam **open shadow roots** automaticamente quando partem de um host conhecido.

**Mistura de estilos:** `expect(...).to_be_attached()` (web-first) + `assert shadow_content.count() >= 1` (contagem imediata). Em cenários flaky, preferir `expect(...).to_have_count(n)`.

---

### `test_loads_demo_iframe`

```python
def test_loads_demo_iframe(self, page: Page) -> None:
    iframe = page.get_by_test_id("demo-iframe")
    expect(iframe).to_be_visible()
    expect(iframe).to_have_attribute("src", re.compile(r".+"))
```

| Fase | Ação |
|------|------|
| **Given** | Página Advanced |
| **When** | Inspeciona o iframe de demonstração |
| **Then** | Iframe visível; atributo `src` preenchido (regex `.+` = um ou mais caracteres) |

**Conceito Playwright:** interagir *dentro* do iframe exigiria `page.frame_locator(...)` ou `content_frame()`; aqui só validamos o elemento `<iframe>` externo.

---

### `test_shows_external_link_with_target_blank`

```python
def test_shows_external_link_with_target_blank(self, page: Page) -> None:
    link = page.get_by_test_id("external-link")
    expect(link).to_have_attribute("href", re.compile(r"http"))
```

| Fase | Ação |
|------|------|
| **Given** | Link externo renderizado |
| **When** | Lê atributo `href` |
| **Then** | URL contém `http` (http ou https) |

Não clica no link — evita abrir nova aba/janela e flakiness em CI.

---

### `test_renders_shadow_section_at_mobile_viewport`

```python
@pytest.mark.smoke
def test_renders_shadow_section_at_mobile_viewport(self, page: Page) -> None:
    page.set_viewport_size(MOBILE)
    expect(page.get_by_test_id("section-shadow")).to_be_visible()
    page.set_viewport_size(DESKTOP)
```

| Fase | Ação |
|------|------|
| **Given** | Página em viewport desktop (padrão) |
| **When** | Redimensiona para `MOBILE` (375×812) |
| **Then** | Seção shadow continua visível |
| **Cleanup** | Restaura `DESKTOP` para não afetar testes seguintes na mesma sessão |

**Conceito Playwright:** `set_viewport_size` simula dispositivo; não emula user-agent completo (para isso, use `page.emulate(...)` ou projetos de device preset).

---

### `test_navigates_with_page_finish_button`

```python
def test_navigates_with_page_finish_button(self, page: Page) -> None:
    page.get_by_test_id("page-finish-btn").click()
    expect(page).not_to_have_url(re.compile(r"/web/advanced\.html"))
```

| Fase | Ação |
|------|------|
| **Given** | Usuário na página Advanced |
| **When** | Clica em `page-finish-btn` |
| **Then** | URL deixa de ser `/web/advanced.html` |

**Conceito Playwright:** `expect(page).not_to_have_url(...)` aguarda navegação completar — mais robusto que ler `page.url` imediatamente após o clique.

---

## Conceitos consolidados para estudantes

### PyTest

- **Fixtures** compõem dependências (`page` → `advanced_page` → teste).
- **`autouse`** elimina boilerplate nos parâmetros dos testes.
- **Markers** permitem pipelines seletivos (`-m smoke`).

### Playwright

- **`get_by_test_id`** — localizador estável.
- **`expect`** — asserções com retry integrado.
- **Viewport** — testes responsivos sem dispositivo físico.
- **Shadow DOM / iframe** — padrões comuns em design systems modernos.

### Given / When / Then neste módulo

A maioria dos testes é **renderização + asserção** (Given + Then). Apenas navegação, clique e mudança de viewport introduzem **When** explícito.

---

## Checklist de aprendizado

- [ ] Explicar por que `advanced_page` usa `autouse=True`
- [ ] Diferenciar `to_be_visible` vs `to_be_attached`
- [ ] Descrever como Playwright acessa shadow root aberto
- [ ] Executar suite com `-m smoke` e interpretar resultado
- [ ] Propor um teste novo: validar `target="_blank"` no link externo
