# Testes do Wizard Multi-Etapas

**Arquivo-fonte:** [`../../../../tests/wizard/test_wizard.py`](../../../../tests/wizard/test_wizard.py)

---

## Propósito

Este módulo valida o **Wizard** (`/web/wizard.html`), um formulário multi-etapas (stepper) com três passos:

1. **Dados pessoais** — nome, e-mail, data de nascimento, país
2. **Preferências** — framework, papel, experiência, termos, newsletter
3. **Revisão e conclusão** — resumo + mensagem de sucesso

Os testes cobrem fluxo completo, validação, navegação retroativa, reinício, interceptação de API para lookups e acessibilidade.

O arquivo usa **funções helper privadas** (prefixo `_`) para compor fluxos longos sem duplicar código — padrão comum quando não há Page Object dedicado.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Ambiente | Servidor TestFlow em execução |
| Autenticação | `visit_authenticated` via fixture autouse |
| Factories | [`support/factories/wizard.py`](../../../../support/factories/wizard.py) — dados fake com Faker |
| Fixtures JSON | [`fixtures/lookups/countries.json`](../../../../fixtures/lookups/countries.json) |
| Helper | [`support/helpers/fixtures.py`](../../../../support/helpers/fixtures.py) — `read_fixture` |

```bash
pytest tests/wizard/test_wizard.py -v
pytest tests/wizard/test_wizard.py -m smoke
pytest tests/wizard/test_wizard.py -m critical
pytest tests/wizard/test_wizard.py -m a11y
```

---

## Markers utilizados

| Marker | Onde aparece | Significado |
|--------|--------------|-------------|
| `regression` | Ambas as classes de teste | Suite de regressão |
| `smoke` | `test_shows_step_1_by_default` | Verificação rápida de carregamento |
| `critical` | `test_completes_all_wizard_sections` | Fluxo end-to-end principal |
| `a11y` | `TestWizardAccessibility` | Acessibilidade WCAG |

---

## Visão geral da estrutura

```
test_wizard.py
├── Imports
├── Helpers privados (_complete_wizard_step1, step2, step3, _advance, _fill_wizard_flow)
├── Fixture autouse: wizard_page
├── TestWizardMultiStepFlow
└── TestWizardAccessibility
```

---

## Imports — bloco a bloco

### `import re`

Expressões regulares para validar classes CSS com word boundaries (`\bactive\b`, `\bdone\b`).

**Por que `\b`?** Evita match parcial — `"active"` não confunde com `"inactive"`.

---

### `import pytest`

Framework de testes.

---

### `from playwright.sync_api import Page, expect`

API síncrona do Playwright para interações e asserções.

---

### `from conftest import check_a11y`

Varredura de acessibilidade axe-core.

---

### `from support.auth import visit_authenticated`

Login via API + navegação autenticada.

---

### `from support.factories.wizard import create_personal_step, create_preferences_step`

| Função | Retorno |
|--------|---------|
| `create_personal_step(**overrides)` | `dict` com `name`, `email`, `dob`, `country` (Faker + defaults) |
| `create_preferences_step(**overrides)` | `dict` com `framework`, `role`, `experience` |

**Conceito:** **Test Data Factory** — gera dados válidos; `**overrides` permite customizar campos específicos.

---

### `from support.helpers.fixtures import read_fixture`

Carrega JSON de `fixtures/` para uso em testes e mocks de API.

---

## Funções helper — bloco a bloco

### `_complete_wizard_step1(page, personal)`

```python
def _complete_wizard_step1(page: Page, personal: dict[str, str]) -> None:
    page.get_by_test_id("wizard-name").fill(personal["name"])
    page.get_by_test_id("wizard-email").fill(personal["email"])
    page.get_by_test_id("wizard-dob").fill(personal["dob"])
    page.get_by_test_id("wizard-country").select_option(personal["country"])
```

| Campo | Ação |
|-------|------|
| `wizard-name` | Preenche nome |
| `wizard-email` | Preenche e-mail |
| `wizard-dob` | Preenche data de nascimento |
| `wizard-country` | Seleciona país no `<select>` |

**Given/When:** Dado um dict `personal`, preenche todos os campos obrigatórios da etapa 1.

**Conceito:** Prefixo `_` indica função **privada do módulo** — não é teste, é building block.

---

### `_complete_wizard_step2(page, prefs)`

```python
def _complete_wizard_step2(page: Page, prefs: dict[str, str]) -> None:
    expect(page.get_by_test_id("wizard-panel-2")).to_have_class(re.compile(r"\bactive\b"))
    page.get_by_test_id(f"wizard-fw-{prefs['framework']}").check(force=True)
    page.get_by_test_id(f"wizard-role-{prefs['role']}").check(force=True)
    page.get_by_test_id("wizard-experience").fill(str(prefs["experience"]))
    page.get_by_test_id("wizard-terms").check(force=True)
    page.get_by_test_id("wizard-newsletter").check(force=True)
```

| Aspecto | Explicação |
|---------|------------|
| Asserção inicial | Confirma que painel 2 está ativo antes de interagir |
| `wizard-fw-{framework}` | Test ID dinâmico — ex.: `wizard-fw-playwright` |
| `wizard-role-{role}` | Ex.: `wizard-role-qa` |
| `check(force=True)` | Marca checkbox mesmo se Playwright considerar não clicável |
| `str(prefs["experience"])` | Converte número para string no input |

**Conceito Playwright:** `force=True` em `check()` ignora verificações de actionability — útil quando CSS oculta o input nativo.

---

### `_complete_wizard_step3(page)`

```python
def _complete_wizard_step3(page: Page) -> None:
    expect(page.get_by_test_id("wizard-review")).to_be_visible()
```

Etapa 3 é **somente revisão** — apenas confirma que a seção de review está visível (sem campos a preencher).

---

### `_advance_wizard(page)`

```python
def _advance_wizard(page: Page) -> None:
    page.get_by_test_id("wizard-next").click()
```

Clica botão **Próximo** para avançar etapa.

---

### `_fill_wizard_flow(page, personal, prefs)`

```python
def _fill_wizard_flow(page: Page, personal: dict[str, str], prefs: dict[str, str]) -> None:
    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    _complete_wizard_step2(page, prefs)
    _advance_wizard(page)
    _complete_wizard_step3(page)
    _advance_wizard(page)
```

**Orquestrador** — executa fluxo completo do wizard até após a etapa 3 (antes da tela de sucesso final, dependendo do comportamento do botão Next na etapa 3).

**Conceito:** Composição de helpers reduz duplicação em testes que precisam do wizard completo.

---

## Fixture: `wizard_page`

```python
@pytest.fixture(autouse=True)
def wizard_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/wizard.html")
    expect(page.get_by_test_id("page-wizard")).to_be_attached()
```

| Aspecto | Explicação |
|---------|------------|
| Setup | Autentica e navega para `/web/wizard.html` |
| Verificação | `page-wizard` attached no DOM |

Todo teste começa na página do wizard autenticado.

---

## Classe `TestWizardMultiStepFlow`

```python
@pytest.mark.regression
class TestWizardMultiStepFlow:
```

Testes funcionais do fluxo multi-etapas.

---

### `test_shows_step_1_by_default`

```python
@pytest.mark.smoke
def test_shows_step_1_by_default(self, page: Page) -> None:
    expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
    expect(page.get_by_test_id("wizard-step-1")).to_have_class(re.compile(r"\bactive\b"))
```

| **Given** | Wizard recém-carregado |
| **Then** | Painel 1 visível + indicador de step 1 com classe `active` |

**Marker `smoke`:** Teste rápido para gate de CI.

---

### `test_validates_required_fields_on_step_1`

```python
def test_validates_required_fields_on_step_1(self, page: Page) -> None:
    page.get_by_test_id("wizard-next").click()
    expect(page.get_by_test_id("wizard-step1-error")).to_be_visible()
```

| **When** | Avança sem preencher campos |
| **Then** | Mensagem de erro da etapa 1 visível |

Validação client-side de campos obrigatórios.

---

### `test_maps_country_fixture_codes_to_wizard_select_options`

```python
def test_maps_country_fixture_codes_to_wizard_select_options(self, page: Page) -> None:
    countries = read_fixture("lookups/countries.json")["countries"]
    canada = next(c for c in countries if c["code"] == "CA")
    assert canada is not None

    page.route(
        "**/lookups/countries**",
        lambda route: route.fulfill(json=read_fixture("lookups/countries.json")),
    )
    page.get_by_test_id("wizard-country").select_option("ca")
    expect(page.get_by_test_id("wizard-country")).to_have_value("ca")
```

| Aspecto | Explicação |
|---------|------------|
| `read_fixture` | Carrega JSON de países do disco |
| `next(...)` | Encontra Canadá com código `"CA"` — prova que fixture contém o dado |
| `page.route` | **Intercepta** requisições de rede |
| `route.fulfill(json=...)` | Responde com JSON mockado em vez de chamar API real |
| `select_option("ca")` | Valor do `<option>` é lowercase `"ca"` |

**Given/When/Then:**

- **Given:** API de countries mockada com fixture local
- **When:** Seleciona Canadá
- **Then:** Valor do select persiste como `"ca"`

**Conceito Playwright:** Route interception desacopla testes de backend instável.

---

### `test_completes_all_wizard_sections`

```python
@pytest.mark.critical
def test_completes_all_wizard_sections(self, page: Page) -> None:
    personal = create_personal_step()
    prefs = create_preferences_step()

    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    expect(page.get_by_test_id("wizard-step-1")).to_have_class(re.compile(r"\bdone\b"))

    _complete_wizard_step2(page, prefs)
    _advance_wizard(page)
    expect(page.get_by_test_id("wizard-step-2")).to_have_class(re.compile(r"\bdone\b"))

    _complete_wizard_step3(page)
    _advance_wizard(page)

    expect(page.get_by_test_id("wizard-success")).to_be_visible()
    expect(page.get_by_test_id("wizard-success-message")).not_to_be_empty()
    expect(page.get_by_test_id("review-name")).to_contain_text(personal["name"])
```

| Etapa | Validação |
|-------|-----------|
| Após step 1 | Indicador `wizard-step-1` com classe `done` |
| Após step 2 | Indicador `wizard-step-2` com classe `done` |
| Final | Tela de sucesso + mensagem + nome na revisão |

**Marker `critical`:** Teste E2E principal do wizard.

**Given/When/Then:**

- **Given:** Dados gerados por factories
- **When:** Percorre todas as etapas
- **Then:** Stepper marca etapas concluídas + sucesso exibe dados corretos

---

### `test_navigates_back_from_step_2_to_step_1`

```python
def test_navigates_back_from_step_2_to_step_1(self, page: Page) -> None:
    personal = create_personal_step()
    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    page.get_by_test_id("wizard-back").click()
    expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
```

| **When** | Completa step 1, avança, clica Voltar |
| **Then** | Retorna ao painel 1 |

Testa navegação **bidirecional** do stepper.

---

### `test_restarts_wizard_after_completion`

```python
def test_restarts_wizard_after_completion(self, page: Page) -> None:
    personal = create_personal_step()
    prefs = create_preferences_step()
    _fill_wizard_flow(page, personal, prefs)
    page.get_by_test_id("wizard-restart").click()
    expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
```

| **When** | Completa wizard + clica reiniciar |
| **Then** | Volta ao painel 1 (estado inicial) |

Valida reset do fluxo após conclusão.

---

## Classe `TestWizardAccessibility`

```python
@pytest.mark.regression
@pytest.mark.a11y
class TestWizardAccessibility:
    def test_wizard_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
```

| **Given** | Wizard na etapa 1 (estado padrão) |
| **Then** | Sem violações a11y críticas/graves |

Formulários multi-etapas são propensos a problemas de labels e foco — este teste garante baseline WCAG.

---

## Resumo de conceitos aprendidos

| Conceito | Onde aparece |
|----------|--------------|
| Helpers privados (`_`) | Composição de fluxos longos |
| Test Data Factory | `create_personal_step`, `create_preferences_step` |
| Faker | Dados dinâmicos por execução |
| Regex em classes CSS | `\bactive\b`, `\bdone\b` |
| `check(force=True)` | Checkboxes estilizados/ocultos |
| Route interception | `page.route` + `route.fulfill` |
| Fixtures JSON | `read_fixture("lookups/countries.json")` |
| Stepper UI | Indicadores `wizard-step-N`, painéis `wizard-panel-N` |
| Markers | `smoke`, `critical`, `a11y`, `regression` |
