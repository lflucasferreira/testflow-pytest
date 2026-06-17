from playwright.sync_api import Page, expect


class SettingsPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self):
        return self.page.get_by_test_id("page-settings")

    def settings_form(self):
        return self.page.get_by_test_id("settings-form")

    def name_input(self):
        return self.page.get_by_test_id("settings-name")

    def email_input(self):
        return self.page.get_by_test_id("settings-email")

    def timezone_select(self):
        return self.page.get_by_test_id("settings-timezone")

    def save_btn(self):
        return self.page.get_by_test_id("settings-save")

    def form_result(self):
        return self.page.get_by_test_id("form-result")

    def file_upload(self):
        return self.page.get_by_test_id("file-upload")

    def notif_switch(self):
        return self.page.get_by_test_id("notifications-switch")

    def switch_status(self):
        return self.page.get_by_test_id("switch-status")

    def volume_slider(self):
        return self.page.get_by_test_id("volume-slider")

    def volume_value(self):
        return self.page.get_by_test_id("volume-value")

    def digest_checkbox(self):
        return self.page.get_by_test_id("settings-digest")

    def date_input(self):
        return self.page.get_by_test_id("settings-date")

    def current_password(self):
        return self.page.get_by_test_id("password-current")

    def new_password(self):
        return self.page.get_by_test_id("password-new")

    def password_save_btn(self):
        return self.page.get_by_test_id("password-save")

    def password_result(self):
        return self.page.get_by_test_id("password-result")

    def twofa_switch(self):
        return self.page.get_by_test_id("twofa-switch")

    def twofa_status(self):
        return self.page.get_by_test_id("twofa-status")

    def session_badge(self):
        return self.page.get_by_test_id("session-badge")

    def copy_token_btn(self):
        return self.page.get_by_test_id("copy-token-btn")

    def rotate_token_btn(self):
        return self.page.get_by_test_id("rotate-token-btn")

    def api_key_display(self):
        return self.page.get_by_test_id("api-key-display")

    def token_result(self):
        return self.page.get_by_test_id("token-result")

    def webhook_input(self):
        return self.page.get_by_test_id("webhook-url")

    def save_webhook_btn(self):
        return self.page.get_by_test_id("save-webhook-btn")

    def webhook_result(self):
        return self.page.get_by_test_id("webhook-result")

    def delete_account_btn(self):
        return self.page.get_by_test_id("delete-account-btn")

    def fill_name(self, name: str) -> "SettingsPage":
        self.name_input().clear()
        self.name_input().fill(name)
        return self

    def save_profile(self) -> "SettingsPage":
        self.save_btn().click()
        return self

    def toggle_notifications(self) -> "SettingsPage":
        self.notif_switch().click()
        return self

    def set_slider(self, value: int) -> "SettingsPage":
        self.volume_slider().evaluate(
            """(el, v) => {
                const input = el;
                input.value = String(v);
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }""",
            value,
        )
        return self

    def submit_password_change(self, current: str, new: str) -> "SettingsPage":
        self.current_password().fill(current)
        self.new_password().fill(new)
        self.password_save_btn().click()
        return self

    def toggle_2fa(self) -> "SettingsPage":
        self.twofa_switch().click()
        return self

    def copy_token(self) -> "SettingsPage":
        self.copy_token_btn().click()
        return self

    def rotate_token(self) -> "SettingsPage":
        self.rotate_token_btn().click()
        return self

    def save_webhook(self, url: str) -> "SettingsPage":
        self.webhook_input().clear()
        self.webhook_input().fill(url)
        self.save_webhook_btn().click()
        return self

    def should_show_save_success(self) -> "SettingsPage":
        expect(self.form_result()).to_be_visible()
        expect(self.form_result()).to_contain_text("saved")
        return self

    def should_show_notifications_on(self) -> "SettingsPage":
        expect(self.switch_status()).to_have_text("On")
        expect(self.notif_switch()).to_have_attribute("aria-checked", "true")
        return self

    def should_show_notifications_off(self) -> "SettingsPage":
        expect(self.switch_status()).to_have_text("Off")
        expect(self.notif_switch()).to_have_attribute("aria-checked", "false")
        return self

    def should_show_password_error(self, text: str) -> "SettingsPage":
        expect(self.password_result()).to_be_visible()
        expect(self.password_result()).to_contain_text(text)
        return self

    def should_show_2fa_enabled(self) -> "SettingsPage":
        expect(self.twofa_status()).to_have_text("Enabled")
        expect(self.twofa_switch()).to_have_attribute("aria-checked", "true")
        return self

    def should_show_token_result(self, text: str) -> "SettingsPage":
        expect(self.token_result()).to_contain_text(text)
        return self

    def should_show_webhook_saved(self) -> "SettingsPage":
        expect(self.webhook_result()).to_be_visible()
        expect(self.webhook_result()).to_contain_text("Webhook saved")
        return self
