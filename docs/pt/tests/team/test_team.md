# Testes da Página Team

**Arquivo de origem:** [`../../../../tests/team/test_team.py`](../../../../tests/team/test_team.py)

---

## Propósito

Este arquivo valida a página **Team** (`/web/team.html`) — gerenciamento de membros da equipe:

- Estrutura da tabela (colunas, linhas, contadores)
- Busca por nome e email
- Filtros por role (admin, etc.) e status (active/inactive)
- Ordenação por nome (asc/desc)
- Paginação (página 1 ↔ 2)
- Modal de convite de membro (validação, sucesso, payload API)
- Edição inline de linhas (salvar, cancelar, toast)
- Filtro da lista de frameworks

É uma suíte de **regressão funcional** densa — cobre interações de tabela, formulários modais e interceptação de requisições HTTP.

---

## Pré-requisitos

| Requisito | Descrição |
|-----------|-----------|
| Servidor local | `BASE_URL` acessível (padrão: `http://localhost:5050`). |
| Autenticação | `visit_authenticated` via API funcional. |
| Dados de equipe | Aplicação deve ter 6 membros (4 na página 1, 2 na página 2). |
| Page Object | `TeamPage` em `pages/team_page.py`. |
| Fixture JSON | `fixtures/team-member.json` com dados para convite. |

**Fixtures globais:**

- `page` — aba Playwright.
- `api_request` — cliente HTTP para autenticação.

---

## Marcadores (markers) utilizados

```python
pytestmark = pytest.mark.regression
```

Todo o módulo é **regression**. Nenhum marker adicional (`smoke`, `critical`, `api`) é aplicado individualmente.

```bash
pytest tests/team/test_team.py -v
pytest tests/team/test_team.py::TestSearch -v
pytest tests/team/test_team.py::TestInviteMemberModal::test_adds_a_new_row_after_successful_invite -v
```

---

## Conceitos PyTest e Playwright usados neste arquivo

### `visit_authenticated` vs `login_via_api`

- `login_via_api` → sempre termina no **dashboard**.
- `visit_authenticated(page, api_request, path)` → autentica e vai **direto** para o path informado (`/web/team.html`).

### `page.on("request", handler)`

Registra listener de eventos de rede. Cada requisição HTTP dispara `handler(request)`. Usado para capturar payloads POST/PUT sem `page.route` (mock).

### `Locator.evaluate_all()`

Executa JavaScript em **todos** os elementos correspondentes ao locator e retorna lista de resultados — ideal para extrair dados de múltiplas linhas de tabela.

### `Locator.count()` + loop `range(count)`

Padrão para iterar linhas dinâmicas: obtém quantidade, depois acessa `.nth(i)` para cada índice.

### Keyword-only arguments (`*`)

`fill_invite_form(*, name=..., email=...)` — força argumentos nomeados, evitando troca acidental de parâmetros.

### `re.search` em Python

Extrai número do texto `"6 row(s)"` para comparar total após convite.

---

## Imports — linha a linha

```python
import re
```

Regex para parsing de labels (`row_count`) e validação de URLs.

```python
import pytest
```

Framework de testes.

```python
from playwright.sync_api import APIRequestContext, Page, expect
```

Tipos e asserções Playwright.

```python
from pages.team_page import TeamPage
```

Page Object da página Team.

```python
from support.auth import visit_authenticated
```

Autentica via API e navega diretamente à rota desejada.

```python
from support.helpers.fixtures import read_fixture
```

Carrega JSON de `fixtures/`.

---

## Configuração do módulo

```python
pytestmark = pytest.mark.regression
```

Marca regressão em todos os testes.

```python
team_member = read_fixture("team-member.json")
```

Conteúdo de `fixtures/team-member.json`:

```json
{
  "new": {
    "name": "Grace SDET",
    "email": "grace@testflow.io"
  },
  "duplicate": {
    "name": "Alice QA",
    "email": "alice@testflow.io",
    "role": "admin"
  }
}
```

Usado nos testes de convite — dados centralizados e fáceis de alterar.

---

## Fixture `setup_team`

```python
@pytest.fixture(autouse=True)
def setup_team(page: Page, api_request: APIRequestContext) -> None:
    visit_authenticated(page, api_request, "/web/team.html")
    expect(TeamPage(page).page_root()).to_be_visible()
```

**Antes de cada teste:**

1. Autentica via API e abre `/web/team.html` (não passa pelo dashboard).
2. Confirma que `[data-testid="page-team"]` está visível.

**Given implícito:** usuário logado na página Team com tabela carregada.

---

## Page Object `TeamPage` — referência

Principais métodos usados neste arquivo:

| Categoria | Método | Descrição |
|-----------|--------|-----------|
| Estrutura | `team_summary()`, `table()`, `table_rows()`, `row_count()` | Elementos da tabela |
| Busca | `search(term)`, `clear_search()` | Campo `table-search` |
| Filtros | `filter_by_role(role)`, `filter_by_status(status)` | Selects de filtro |
| Ordenação | `sort_by_name()` | Clique no header Name |
| Paginação | `go_to_next_page()`, `go_to_prev_page()`, `prev_page()`, `next_page()`, `page_info()` | Controles de página |
| Convite | `open_invite_modal()`, `fill_invite_form()`, `submit_invite()`, `cancel_invite()` | Modal invite |
| Edição | `start_edit(id)`, `edit_name()`, `save_edit()`, `cancel_edit()` | Inline edit por row |
| Frameworks | `framework_search()`, `framework_list()` | Lista lateral filtrável |
| Asserções | `should_have_row_count(n)`, `should_show_invite_error(text)`, etc. | Wrappers de expect |

---

## Classe `TestPageStructure`

Valida layout inicial da tabela de membros.

### `test_shows_the_page_header_with_member_count`

```python
expect(TeamPage(page).team_summary()).to_contain_text("6 members")
```

- **Then:** cabeçalho indica total de 6 membros cadastrados.

### `test_renders_all_table_columns`

```python
expect(page.get_by_test_id("users-table").locator("thead th")).to_have_count(7)
```

- **Then:** tabela possui exatamente 7 colunas no `<thead>`.

### `test_renders_the_correct_number_of_rows_on_page_1`

```python
TeamPage(page).should_have_row_count(4)
```

- **Then:** 4 linhas visíveis na página 1 (paginação de 4 por página, 6 total).

### `test_row_count_label_matches_visible_rows`

```python
expect(TeamPage(page).row_count()).to_contain_text("6 row(s)")
```

- **Then:** label `table-row-count` reflete total global (6), não apenas página atual.

---

## Classe `TestSearch`

Valida filtro de busca em tempo real na tabela.

### `test_filters_rows_by_member_name`

```python
team = TeamPage(page)
team.search("Alice")
team.should_have_row_count(1)
expect(team.name_cell(1)).to_contain_text("Alice QA")
```

| Etapa | Given/When/Then |
|-------|-----------------|
| Setup | **Given** 4 linhas na página 1 |
| `search("Alice")` | **When** digita no campo de busca |
| 1 linha + nome | **Then** filtra para Alice QA |

### `test_filters_rows_by_email`

```python
team.search("carol")
team.should_have_row_count(1)
```

- **When:** busca por fragmento de email (case insensitive esperado).
- **Then:** uma linha corresponde.

### `test_returns_all_rows_when_search_is_cleared`

```python
team.search("Alice")
team.should_have_row_count(1)
team.clear_search()
team.should_have_row_count(4)
```

- **When:** limpa busca após filtrar.
- **Then:** restaura 4 linhas da página 1.

### `test_shows_zero_rows_for_a_term_with_no_match`

```python
team.search("zzznoresult")
expect(team.table_rows()).to_have_count(0)
```

- **Then:** termo inexistente → tabela vazia.

---

## Classe `TestRoleFilter`

Filtra linhas pelo papel (role) do membro.

### `test_filters_to_admin_rows_only`

```python
team.filter_by_role("admin")
rows = team.table_rows()
count = rows.count()
for i in range(count):
    expect(rows.nth(i).locator('[data-role="admin"]')).to_be_visible()
```

- **When:** seleciona filtro "admin".
- **Then:** **cada** linha visível contém badge/elemento `[data-role="admin"]`.

**Padrão de iteração:** `count()` obtém N dinâmico; loop garante que nenhuma linha "não-admin" passou pelo filtro.

### `test_shows_all_rows_when_filter_is_reset`

```python
team.filter_by_role("admin")
team.filter_by_role("")
team.should_have_row_count(4)
```

- **When:** reseta filtro (valor vazio = "All").
- **Then:** 4 linhas novamente.

---

## Classe `TestStatusFilter`

Mesmo padrão do filtro de role, para status active/inactive.

### `test_filters_to_active_members_only`

```python
team.filter_by_status("active")
# loop verifica [data-status="active"] em cada linha
```

### `test_filters_to_inactive_members_only`

```python
team.filter_by_status("inactive")
# loop verifica [data-status="inactive"] em cada linha
```

---

## Classe `TestSorting`

Valida ordenação clicável na coluna Name.

### `test_sorts_rows_by_name_descending_on_first_click`

```python
team.sort_by_name()
names = team.table_rows().evaluate_all(
    """rows => rows.map(row =>
        (row.querySelector('[data-testid^="cell-name-"]')?.textContent ?? '').trim()
    )"""
)
assert names == sorted(names, reverse=True)
```

**Fluxo:**

1. **When:** primeiro clique no header Name.
2. **Then:** extrai nomes de todas as linhas via JS no browser.
3. **Then:** lista está em ordem descendente (`sorted(names, reverse=True)`).

**Conceito `evaluate_all`:** executa função JS recebendo array de DOM elements — retorna lista Python com textos.

### `test_second_click_sorts_rows_by_name_ascending`

```python
team.sort_by_name()
team.sort_by_name()
names = team.table_rows().evaluate_all(...)
assert names == sorted(names)
```

- **When:** dois cliques (toggle asc/desc).
- **Then:** ordem ascendente alfabética.

---

## Classe `TestPagination`

Valida navegação entre páginas da tabela.

### `test_prev_button_is_disabled_on_page_1`

```python
expect(TeamPage(page).prev_page()).to_be_disabled()
```

- **Given:** página 1.
- **Then:** botão "Previous" desabilitado.

### `test_navigates_to_page_2_showing_remaining_rows`

```python
team.go_to_next_page()
expect(team.page_info()).to_contain_text("Page 2")
team.should_have_row_count(2)
```

- **When:** avança para página 2.
- **Then:** indicador "Page 2" + 2 linhas restantes (6 total − 4 na pág. 1).

### `test_next_button_is_disabled_on_last_page`

```python
team.go_to_next_page()
expect(team.next_page()).to_be_disabled()
```

- **Given:** última página.
- **Then:** botão "Next" desabilitado.

### `test_navigating_back_to_page_1_restores_row_count`

```python
team.go_to_next_page()
team.go_to_prev_page()
team.should_have_row_count(4)
```

- **When:** vai à pág. 2 e volta.
- **Then:** 4 linhas na página 1 novamente.

---

## Classe `TestInviteMemberModal`

Valida modal de convite de novo membro — UX, validação e integração API.

### `test_opens_modal_on_invite_member_click`

```python
TeamPage(page).open_invite_modal()
TeamPage(page).should_have_invite_modal_open()
```

- **When:** clica `invite-btn`.
- **Then:** modal visível.

### `test_closes_modal_on_cancel`

```python
team.open_invite_modal()
team.cancel_invite()
team.should_have_invite_modal_closed()
```

### `test_closes_modal_on_escape_key`

```python
team.open_invite_modal()
page.keyboard.press("Escape")
team.should_have_invite_modal_closed()
```

### `test_shows_validation_error_when_name_is_empty`

```python
team.open_invite_modal()
team.fill_invite_form(email=team_member["new"]["email"])
team.submit_invite()
team.should_show_invite_error("required")
```

- **Given:** email preenchido, nome omitido.
- **When:** submete.
- **Then:** erro contendo "required".

**Conceito:** `fill_invite_form` usa keyword-only args — `email=` sem `name=` deixa nome vazio.

### `test_shows_validation_error_for_invalid_email`

```python
team.fill_invite_form(name=team_member["new"]["name"], email="notanemail")
team.submit_invite()
team.should_show_invite_error("valid email")
```

- **Then:** validação de formato de email.

### `test_adds_a_new_row_after_successful_invite`

```python
team.open_invite_modal()
team.fill_invite_form(**team_member["new"])
team.submit_invite()
team.should_have_invite_modal_closed()
expect(page.get_by_test_id("toast-message")).to_contain_text(
    team_member["new"]["email"]
)
label = team.row_count().inner_text()
row_total = int(re.search(r"\d+", label).group())
assert row_total > 6
```

| Etapa | Given/When/Then |
|-------|-----------------|
| Preenche form | **When** convida Grace SDET |
| Modal fecha + toast | **Then** sucesso com email no toast |
| Contador | **Then** total de rows > 6 (era 6 antes) |

`**team_member["new"]` — unpack dict como `name="Grace SDET", email="grace@testflow.io"`.

### `test_invite_request_contains_name_and_email_in_the_payload`

```python
captured: list = []

def capture_request(req) -> None:
    if req.method == "POST" and "/api/" in req.url:
        captured.append(req)

page.on("request", capture_request)
team.open_invite_modal()
team.fill_invite_form(**team_member["new"])
team.submit_invite()
# ... asserções de UI ...

invite_request = captured[0] if captured else None
if invite_request is not None:
    body = invite_request.post_data_json
    assert "name" in body and isinstance(body["name"], str)
    assert "email" in body and isinstance(body["email"], str)
    assert body["email"] == team_member["new"]["email"]
```

**Conceito — interceptação passiva com `page.on("request")`:**

1. Registra handler **antes** da ação.
2. Handler filtra POSTs para URLs contendo `/api/`.
3. Após submit, inspeciona `post_data_json` da requisição capturada.

**Diferença de `page.route`:** `page.on` **observa** tráfego real sem mockar resposta — teste de integração.

**Nota:** bloco `if invite_request is not None` torna asserções de payload condicionais — UI ainda é validada mesmo se API mode estiver off.

---

## Classe `TestInlineEditing`

Valida edição inline de membros na tabela.

### `test_shows_name_and_role_inputs_when_edit_is_clicked`

```python
team.start_edit(1)
team.should_show_edit_inputs(1)
```

- **When:** clica edit na linha 1.
- **Then:** inputs `edit-name-1` e `edit-role-1` visíveis.

### `test_updates_the_row_after_saving_a_new_name`

```python
team.start_edit(1)
team.edit_name(1, "Alice QA Updated")
team.save_edit(1)
expect(team.name_cell(1)).to_contain_text("Alice QA Updated")
```

- **When:** altera nome e salva.
- **Then:** célula reflete novo valor.

### `test_shows_a_success_toast_after_saving`

```python
team.start_edit(2)
team.save_edit(2)
expect(page.get_by_test_id("toast-message")).to_contain_text("updated")
```

- **Then:** feedback toast após save (mesmo sem alterar dados).

### `test_edit_save_updates_the_row_and_triggers_a_write_request_if_api_driven`

```python
captured: list = []

def capture_request(req) -> None:
    if req.method in ("PUT", "PATCH") and "/api/" in req.url:
        captured.append(req)

page.on("request", capture_request)
team.start_edit(1)
team.edit_name(1, "Alice QA Intercepted")
team.save_edit(1)
expect(team.name_cell(1)).to_contain_text("Alice QA Intercepted")

interception = captured[0] if captured else None
if interception is not None:
    body = interception.post_data_json
    assert "name" in body
```

- **When:** salva edição com API ativa.
- **Then:** UI atualizada **e** (se API) requisição PUT/PATCH contém campo `name`.

### `test_discards_changes_on_cancel`

```python
team.start_edit(1)
team.edit_name(1, "Should Not Save")
team.cancel_edit(1)
expect(team.name_cell(1)).not_to_contain_text("Should Not Save")
```

- **When:** cancela após editar.
- **Then:** valor original preservado.

### `test_restores_normal_row_after_cancel`

```python
team.start_edit(1)
team.cancel_edit(1)
expect(team.edit_btn(1)).to_be_visible()
```

- **Then:** modo visual normal — botão Edit visível novamente.

---

## Classe `TestFrameworkListFilter`

Valida filtro da lista lateral de frameworks de teste.

### `test_filters_the_framework_list`

```python
team.framework_search().fill("play")
items = team.framework_list().locator("li")
count = items.count()
for i in range(count):
    text = items.nth(i).inner_text()
    assert "play" in text.lower()
```

- **When:** busca "play" no campo `item-search`.
- **Then:** cada `<li>` visível contém "play" (ex.: Playwright).

### `test_shows_all_frameworks_when_filter_is_cleared`

```python
team.framework_search().fill("cypress")
team.framework_search().clear()
assert team.framework_list().locator("li").count() > 1
```

- **When:** filtra e depois limpa.
- **Then:** lista completa restaurada (> 1 item).

---

## Diagrama — áreas testadas na página Team

```
┌─────────────────────────────────────────────────────────────┐
│  team-summary ("6 members")          [Invite Member]        │
├─────────────────────────────────────────────────────────────┤
│  [Search]  [Role ▼]  [Status ▼]                             │
├──────────────────────────────┬──────────────────────────────┤
│  users-table                 │  framework list              │
│  ├─ sort by name             │  ├─ item-search              │
│  ├─ pagination prev/next     │  └─ item-list (li...)        │
│  └─ inline edit rows         │                              │
├──────────────────────────────┴──────────────────────────────┤
│  invite-modal (name, email, role)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Resumo para novos alunos

| Padrão | Exemplo | Aprendizado |
|--------|---------|-------------|
| Setup direto à rota | `visit_authenticated(..., "/web/team.html")` | Não precisa passar pelo dashboard |
| Dados JSON | `team_member = read_fixture(...)` | Separar dados de lógica |
| Iteração dinâmica | `for i in range(rows.count())` | Tabelas com N variável |
| Extração em massa | `evaluate_all(...)` | Ler coluna inteira via JS |
| Listener de rede | `page.on("request", handler)` | Validar payload sem mock |
| Asserção condicional API | `if captured[0] is not None` | UI + API quando disponível |
| Paginação | prev/next disabled + row count | Estado de controles importa |

**Comando sugerido — explorar por classe:**

```bash
# Busca e filtros
pytest tests/team/test_team.py::TestSearch tests/team/test_team.py::TestRoleFilter -v

# Modal de convite (visual)
pytest tests/team/test_team.py::TestInviteMemberModal -v --headed
```

**Ordem de estudo recomendada:**

1. `TestPageStructure` — entenda o layout baseline
2. `TestSearch` / `TestRoleFilter` — interações simples na tabela
3. `TestPagination` / `TestSorting` — estado multi-página
4. `TestInviteMemberModal` / `TestInlineEditing` — formulários + rede
