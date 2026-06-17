# Testes da Página de Configurações (Settings)

**Arquivo-fonte:** [`../../../../tests/settings/test_settings.py`](../../../../tests/settings/test_settings.py)

---

## Propósito

Este módulo valida a página **Settings** (`/web/settings.html`) do sandbox TestFlow. Os testes cobrem:

- Seção **Perfil** (nome, e-mail, fuso horário, upload de avatar)
- Seção **Notificações** (toggle, slider de volume, digest semanal, data)
- Seção **Segurança** (alteração de senha, 2FA, sessões ativas)
- Seção **Integrações** (token de API, webhook)
- **Zona de perigo** (exclusão de conta com diálogo nativo)
- **Acessibilidade** (axe-core via Playwright)

O padrão adotado é **Page Object Model (POM)**: interações e asserções reutilizáveis ficam em `SettingsPage`, enquanto os testes descrevem comportamentos de negócio.

---

## Pré-requisitos

| Item | Descrição |
|------|-----------|
| Ambiente | Servidor TestFlow em execução (URL base configurada em `support/config.py`) |
| Autenticação | Fixture de sessão `cache_auth_token` em `conftest.py` obtém token via API |
| Dependências | `pytest`, `playwright`, `axe-playwright-python` |
| Page Object | [`pages/settings_page.py`](../../../../pages/settings_page.py) |
| Usuário demo | Credenciais padrão (`DEMO_EMAIL` / `DEMO_PASSWORD`) |

Para executar apenas este arquivo:

```bash
pytest tests/settings/test_settings.py -v
```

Para filtrar por marker:

```bash
pytest tests/settings/test_settings.py -m smoke
pytest tests/settings/test_settings.py -m critical
pytest tests/settings/test_settings.py -m a11y
```

---

## Markers utilizados

| Marker | Onde aparece | Significado |
|--------|--------------|-------------|
| `regression` | `pytestmark` (módulo inteiro) | Suite de regressão — todos os testes herdam este marker |
| `smoke` | `test_saves_profile_and_shows_success_message` | Teste de fumaça — caminho crítico rápido |
| `critical` | `test_saves_profile_and_shows_success_message` | Caminho crítico de negócio |
| `a11y` | Classe `TestAccessibility` | Testes de acessibilidade (WCAG 2.x) |

Os markers são registrados em `conftest.py` via `pytest_configure`.

---

## Visão geral da estrutura

```
test_settings.py
├── Imports
├── pytestmark (regression)
├── Fixture autouse: setup_settings
├── TestProfileSection
├── TestNotificationsSection
├── TestSecurityPasswordChange
├── TestSecurity2FA
├── TestSecurityActiveSessions
├── TestIntegrationsApiToken
├── TestIntegrationsWebhook
├── TestDangerZone
└── TestAccessibility
```

---

## Imports — bloco a bloco

### `import re`

Biblioteca padrão do Python para **expressões regulares**. Usada para validar atributos que contêm padrões parciais (ex.: `accept` do input de arquivo com `.png`, classe CSS `btn-danger`).

**Conceito PyTest/Playwright:** `expect(...).to_have_attribute("accept", re.compile(r"\.png"))` aceita qualquer valor que **contenha** `.png`, sem exigir match exato.

---

### `import pytest`

Framework de testes. Fornece:

- **Fixtures** (`@pytest.fixture`)
- **Markers** (`@pytest.mark.smoke`)
- **Classes de teste** (agrupamento lógico)
- Descoberta automática de testes (`test_*.py`)

---

### `from playwright.sync_api import APIRequestContext, Page, expect`

| Símbolo | Papel |
|---------|-------|
| `Page` | Representa uma aba do navegador — interações UI (click, fill, goto) |
| `APIRequestContext` | Cliente HTTP do Playwright para chamadas REST sem UI |
| `expect` | API de asserções com **auto-retry** — reavalia até timeout se o elemento ainda não estiver no estado esperado |

**Conceito Playwright:** `expect(locator).to_be_visible()` é preferível a `assert locator.is_visible()` porque espera a estabilização do DOM.

---

### `from conftest import check_a11y`

Função helper global que executa **axe-core** na página e falha se houver violações `critical` ou `serious` (com regras opcionalmente desabilitadas).

---

### `from pages.settings_page import SettingsPage`

**Page Object** que encapsula locators (`get_by_test_id`) e ações (`fill_name`, `save_profile`) da página Settings.

---

### `from support.auth import visit_authenticated`

Helper que:

1. Obtém token via API (`fetch_auth_token`)
2. Injeta sessão no `sessionStorage` do navegador
3. Navega autenticado até o `path` informado

Evita repetir login manual em cada teste.

---

## Constantes e configuração de módulo

### `pytestmark = pytest.mark.regression`

Atribui o marker `regression` a **todos** os testes do arquivo sem repetir `@pytest.mark.regression` em cada método.

**Conceito PyTest:** `pytestmark` é uma convenção de módulo equivalente a decorar cada teste individualmente.

---

## Fixture: `setup_settings`

```python
@pytest.fixture(autouse=True)
def setup_settings(page: Page, api_request: APIRequestContext) -> None:
    visit_authenticated(page, api_request, "/web/settings.html")
    expect(SettingsPage(page).page_root()).to_be_visible()
```

| Aspecto | Explicação |
|---------|------------|
| `autouse=True` | Executa **antes de cada teste** automaticamente, sem precisar declarar como parâmetro |
| `page` | Fixture do `pytest-playwright` — navegador já aberto |
| `api_request` | Fixture de `conftest.py` — contexto HTTP para login via API |
| `visit_authenticated(...)` | Given: usuário autenticado na página Settings |
| `expect(...page_root()).to_be_visible()` | Then: confirma que a página carregou (`data-testid="page-settings"`) |

**Given/When/Then implícito:** Todo teste começa com a página Settings visível e autenticada.

---

## Classe `TestProfileSection`

Agrupa testes da seção **Perfil** do formulário de configurações.

---

### `test_shows_pre_filled_values_for_name_and_email`

```python
def test_shows_pre_filled_values_for_name_and_email(self, page: Page) -> None:
    settings = SettingsPage(page)
    expect(settings.name_input()).to_have_value("Demo User")
    expect(settings.email_input()).to_have_value("demo@automation.io")
```

| Passo | Descrição |
|-------|-----------|
| **Given** | Página Settings carregada (fixture autouse) |
| **When** | Instancia `SettingsPage` e localiza inputs |
| **Then** | Nome e e-mail exibem valores pré-preenchidos do usuário demo |

**Conceito Playwright:** `to_have_value()` verifica o atributo `value` de inputs — equivalente ao que o usuário vê no campo.

---

### `test_saves_profile_and_shows_success_message`

```python
@pytest.mark.smoke
@pytest.mark.critical
def test_saves_profile_and_shows_success_message(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.fill_name("Demo User Updated")
    settings.save_profile()
    settings.should_show_save_success()
```

| Passo | Descrição |
|-------|-----------|
| **Given** | Perfil com nome original |
| **When** | Preenche novo nome e clica em salvar |
| **Then** | Mensagem de sucesso visível (via `should_show_save_success()`) |

**Markers:** `smoke` + `critical` — este é um dos testes mais importantes da suite Settings.

**POM:** `fill_name` limpa e preenche; `save_profile` clica no botão; `should_show_save_success` encapsula asserções no `#form-result`.

---

### `test_shows_a_toast_on_save`

```python
def test_shows_a_toast_on_save(self, page: Page) -> None:
    SettingsPage(page).save_profile()
    expect(page.get_by_test_id("toast-message")).to_contain_text("saved")
```

| Passo | Descrição |
|-------|-----------|
| **When** | Salva perfil sem alterar campos |
| **Then** | Toast global contém texto `"saved"` |

Testa feedback transiente (notificação toast), não apenas o resultado inline do formulário.

---

### `test_allows_changing_the_timezone_select`

```python
def test_allows_changing_the_timezone_select(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.timezone_select().select_option("brt")
    expect(settings.timezone_select()).to_have_value("brt")
```

| Passo | Descrição |
|-------|-----------|
| **When** | Seleciona opção `"brt"` no `<select>` de fuso horário |
| **Then** | Valor selecionado persiste como `"brt"` |

**Conceito Playwright:** `select_option()` funciona em elementos `<select>` nativos.

---

### `test_avatar_upload_input_accepts_image_files`

```python
def test_avatar_upload_input_accepts_image_files(self, page: Page) -> None:
    expect(SettingsPage(page).file_upload()).to_have_attribute("accept", re.compile(r"\.png"))
```

| Passo | Descrição |
|-------|-----------|
| **Then** | Input de upload possui atributo `accept` contendo `.png` |

Validação de contrato HTML — restringe tipos de arquivo aceitos.

---

## Classe `TestNotificationsSection`

Testes da seção **Notificações**.

---

### `test_push_notifications_start_as_off`

```python
def test_push_notifications_start_as_off(self, page: Page) -> None:
    SettingsPage(page).should_show_notifications_off()
```

**Then:** Switch de notificações inicia desligado (`Off`, `aria-checked="false"`).

---

### `test_toggles_notifications_on`

```python
def test_toggles_notifications_on(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_notifications()
    settings.should_show_notifications_on()
```

| Passo | Descrição |
|-------|-----------|
| **When** | Clica no switch de notificações |
| **Then** | Status `"On"` e `aria-checked="true"` |

---

### `test_toggles_notifications_back_off`

```python
def test_toggles_notifications_back_off(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_notifications()
    settings.toggle_notifications()
    settings.should_show_notifications_off()
```

Testa **toggle bidirecional**: liga → desliga → estado inicial restaurado.

---

### `test_volume_slider_updates_the_displayed_value`

```python
def test_volume_slider_updates_the_displayed_value(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.set_slider(75)
    expect(settings.volume_value()).to_have_text("75")
```

| Passo | Descrição |
|-------|-----------|
| **When** | Define slider para 75 via JavaScript (`evaluate`) |
| **Then** | Label exibe `"75"` |

**Conceito Playwright:** Sliders HTML5 nem sempre respondem bem a `.fill()` — `evaluate` dispara evento `input` manualmente.

---

### `test_weekly_digest_checkbox_is_checked_by_default`

```python
def test_weekly_digest_checkbox_is_checked_by_default(self, page: Page) -> None:
    expect(SettingsPage(page).digest_checkbox()).to_be_checked()
```

**Then:** Checkbox de digest semanal vem marcado por padrão.

---

### `test_digest_start_date_field_is_editable`

```python
def test_digest_start_date_field_is_editable(self, page: Page) -> None:
    date_input = SettingsPage(page).date_input()
    date_input.clear()
    date_input.fill("2025-01-01")
    expect(date_input).to_have_value("2025-01-01")
```

| Passo | Descrição |
|-------|-----------|
| **When** | Limpa e preenche campo de data |
| **Then** | Valor `"2025-01-01"` persiste |

---

## Classe `TestSecurityPasswordChange`

Testes de alteração de senha na seção **Segurança**.

---

### `test_shows_error_when_both_password_fields_are_empty`

```python
def test_shows_error_when_both_password_fields_are_empty(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.password_save_btn().click()
    settings.should_show_password_error("required")
```

| Passo | Descrição |
|-------|-----------|
| **When** | Clica salvar sem preencher senhas |
| **Then** | Erro contém `"required"` |

---

### `test_shows_error_when_new_password_is_too_short`

```python
def test_shows_error_when_new_password_is_too_short(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.submit_password_change("Demo123!", "short")
    settings.should_show_password_error("8 characters")
```

Validação de regra de negócio: nova senha com menos de 8 caracteres.

---

### `test_shows_success_when_a_valid_new_password_is_provided`

```python
def test_shows_success_when_a_valid_new_password_is_provided(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.submit_password_change("Demo123!", "NewPass123!")
    expect(settings.password_result()).to_contain_text("updated")
```

| Passo | Descrição |
|-------|-----------|
| **When** | Envia senha atual válida + nova senha válida |
| **Then** | Resultado contém `"updated"` |

---

### `test_clears_password_fields_after_successful_change`

```python
def test_clears_password_fields_after_successful_change(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.submit_password_change("Demo123!", "NewPass123!")
    expect(settings.current_password()).to_have_value("")
    expect(settings.new_password()).to_have_value("")
```

**Then:** Após sucesso, campos de senha são limpos (boa prática de segurança UX).

---

### `test_password_change_request_contains_current_password_and_new_password`

```python
def test_password_change_request_contains_current_password_and_new_password(
    self, page: Page
) -> None:
    settings = SettingsPage(page)
    password_change = None
    try:
        with page.expect_request(
            lambda req: req.method == "POST" and "/api/" in req.url, timeout=3000
        ) as request_info:
            settings.submit_password_change("Demo123!", "NewPass123!")
        password_change = request_info.value
    except Exception:
        pass

    expect(settings.password_result()).to_contain_text("updated")
    if password_change is not None:
        body = password_change.post_data_json
        assert "currentPassword" in body
        assert "newPassword" in body
        assert body["newPassword"] == "NewPass123!"
```

| Aspecto | Explicação |
|---------|------------|
| **Conceito Playwright** | `page.expect_request()` intercepta requisições de rede durante uma ação |
| **Lambda filter** | Captura apenas POSTs cuja URL contém `/api/` |
| **try/except** | Tolerância se a interceptação falhar — asserção UI ainda roda |
| **Then (UI)** | Sucesso visível na tela |
| **Then (API)** | Body JSON contém `currentPassword` e `newPassword` corretos |

**Given/When/Then:**

- **Given:** Formulário de senha pronto
- **When:** Submete alteração dentro do contexto `expect_request`
- **Then:** UI confirma + payload da API validado

---

## Classe `TestSecurity2FA`

Testes do toggle de **autenticação de dois fatores**.

---

### `test_starts_as_disabled`

```python
def test_starts_as_disabled(self, page: Page) -> None:
    settings = SettingsPage(page)
    expect(settings.twofa_status()).to_have_text("Disabled")
    expect(settings.twofa_switch()).to_have_attribute("aria-checked", "false")
```

Estado inicial: 2FA desabilitado.

---

### `test_enables_2fa_on_toggle`

```python
def test_enables_2fa_on_toggle(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_2fa()
    settings.should_show_2fa_enabled()
```

| **When** | Clica switch 2FA |
| **Then** | Status `"Enabled"`, `aria-checked="true"` |

---

### `test_disables_2fa_on_second_toggle`

```python
def test_disables_2fa_on_second_toggle(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.toggle_2fa()
    settings.toggle_2fa()
    expect(settings.twofa_status()).to_have_text("Disabled")
```

Toggle reversível — segundo clique restaura estado desabilitado.

---

## Classe `TestSecurityActiveSessions`

Testes da lista de **sessões ativas**.

---

### `test_shows_current_session_with_active_badge`

```python
def test_shows_current_session_with_active_badge(self, page: Page) -> None:
    expect(page.get_by_test_id("session-current")).to_be_visible()
    expect(SettingsPage(page).session_badge()).to_contain_text("Active")
```

**Then:** Sessão atual visível com badge `"Active"`.

---

### `test_shows_session_device_name_and_location`

```python
def test_shows_session_device_name_and_location(self, page: Page) -> None:
    expect(page.get_by_test_id("session-name")).not_to_be_empty()
    expect(page.get_by_test_id("session-meta")).to_contain_text("Current session")
```

Valida que metadados da sessão (nome do dispositivo, localização) são renderizados.

---

## Classe `TestIntegrationsApiToken`

Testes de **token de API** na seção Integrações.

---

### `test_displays_the_api_token`

```python
def test_displays_the_api_token(self, page: Page) -> None:
    token = SettingsPage(page).api_key_display()
    expect(token).to_be_visible()
    expect(token).not_to_be_empty()
```

**Then:** Token visível e não vazio.

---

### `test_shows_copied_feedback_when_copy_is_clicked`

```python
def test_shows_copied_feedback_when_copy_is_clicked(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.copy_token()
    settings.should_show_token_result("Copied")
```

| **When** | Clica em copiar token |
| **Then** | Feedback `"Copied"` |

---

### `test_generates_a_new_token_on_rotate`

```python
def test_generates_a_new_token_on_rotate(self, page: Page) -> None:
    settings = SettingsPage(page)
    original = settings.api_key_display().inner_text()
    settings.rotate_token()
    expect(settings.api_key_display()).not_to_have_text(original)
```

| **When** | Rotaciona token |
| **Then** | Texto exibido difere do original |

---

### `test_shows_toast_after_rotating_token`

```python
def test_shows_toast_after_rotating_token(self, page: Page) -> None:
    SettingsPage(page).rotate_token()
    expect(page.get_by_test_id("toast-message")).to_contain_text("rotated")
```

Toast confirma rotação ao usuário.

---

### `test_rotate_token_triggers_a_request_and_response_contains_new_token`

```python
def test_rotate_token_triggers_a_request_and_response_contains_new_token(
    self, page: Page
) -> None:
    settings = SettingsPage(page)
    rotate_response = None
    try:
        with page.expect_response(
            lambda res: "/api/" in res.url, timeout=3000
        ) as response_info:
            settings.rotate_token()
        rotate_response = response_info.value
    except Exception:
        pass

    expect(settings.api_key_display()).not_to_be_empty()
    if rotate_response is not None:
        assert rotate_response.status == 200
        body = rotate_response.json()
        assert isinstance(body["token"], str)
        assert len(body["token"]) > 0
```

| Conceito | Detalhe |
|----------|---------|
| `expect_response` | Aguarda resposta HTTP durante ação |
| Asserções condicionais | Se interceptou, valida status 200 e JSON com `token` não vazio |

---

## Classe `TestIntegrationsWebhook`

Testes de configuração de **webhook**.

---

### `test_saves_a_valid_webhook_url`

```python
def test_saves_a_valid_webhook_url(self, page: Page) -> None:
    settings = SettingsPage(page)
    settings.save_webhook("https://ci.example.com/webhook")
    settings.should_show_webhook_saved()
```

Fluxo feliz: URL válida → mensagem `"Webhook saved"`.

---

### `test_shows_error_when_webhook_url_is_empty`

```python
def test_shows_error_when_webhook_url_is_empty(self, page: Page) -> None:
    SettingsPage(page).save_webhook_btn().click()
    expect(page.get_by_test_id("webhook-result")).to_contain_text("Enter a URL")
```

Validação: salvar sem URL exibe erro.

---

### `test_shows_toast_on_successful_save`

```python
def test_shows_toast_on_successful_save(self, page: Page) -> None:
    SettingsPage(page).save_webhook("https://ci.example.com/hook")
    expect(page.get_by_test_id("toast-message")).to_contain_text("saved")
```

Feedback toast complementa resultado inline.

---

## Classe `TestDangerZone`

Testes da **zona de perigo** (exclusão de conta).

---

### `test_delete_account_button_is_visible`

```python
def test_delete_account_button_is_visible(self, page: Page) -> None:
    btn = SettingsPage(page).delete_account_btn()
    expect(btn).to_be_visible()
    expect(btn).to_have_class(re.compile(r"btn-danger"))
```

**Then:** Botão visível com classe CSS de perigo (`btn-danger`).

---

### `test_delete_account_shows_confirmation_dialog`

```python
def test_delete_account_shows_confirmation_dialog(self, page: Page) -> None:
    confirm_called = {"value": False}

    def handle_dialog(dialog) -> None:
        confirm_called["value"] = True
        assert dialog.type == "confirm"
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    SettingsPage(page).delete_account_btn().click()
    assert confirm_called["value"] is True
```

| Conceito | Explicação |
|----------|------------|
| **Diálogos nativos** | `alert`, `confirm`, `prompt` bloqueiam automação — Playwright exige handler |
| `page.on("dialog", ...)` | Registra listener antes do clique |
| `dialog.dismiss()` | Simula "Cancelar" no confirm |
| `confirm_called` | Dict mutável para verificar que o handler foi invocado |

**Given/When/Then:**

- **Given:** Handler de diálogo registrado
- **When:** Clica em excluir conta
- **Then:** Diálogo `confirm` apareceu (`confirm_called["value"] is True`)

---

## Classe `TestAccessibility`

```python
@pytest.mark.a11y
@pytest.mark.regression
class TestAccessibility:
    def test_settings_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        form = SettingsPage(page).settings_form()
        expect(form).to_be_visible()
        check_a11y(page, disabled_rules=["color-contrast", "label", "select-name"])
```

| Aspecto | Detalhe |
|---------|---------|
| Marker `a11y` | Identifica testes de acessibilidade na CI |
| `check_a11y` | Executa axe com tags WCAG 2a/2aa |
| `disabled_rules` | Ignora regras conhecidas como ruidosas neste sandbox |
| Asserção final | Falha se violações `critical` ou `serious` restantes |

**Conceito:** Acessibilidade automatizada complementa testes funcionais — detecta problemas de roles ARIA, labels, contraste, etc.

---

## Resumo de conceitos aprendidos

| Conceito | Onde aparece |
|----------|--------------|
| Page Object Model | `SettingsPage` em todos os testes |
| Fixture `autouse` | `setup_settings` — setup compartilhado |
| Autenticação via API | `visit_authenticated` |
| Asserções com retry | `expect(...)` |
| Interceptação de rede | `expect_request`, `expect_response` |
| Diálogos nativos | `page.on("dialog", ...)` |
| Regex em asserções | `re.compile` com `to_have_attribute` / `to_have_class` |
| Acessibilidade | `check_a11y` + marker `@pytest.mark.a11y` |
| Markers de pipeline | `smoke`, `critical`, `regression` |
