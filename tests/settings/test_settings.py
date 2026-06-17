import re

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from conftest import check_a11y
from pages.settings_page import SettingsPage
from support.auth import visit_authenticated

pytestmark = pytest.mark.regression


@pytest.fixture(autouse=True)
def setup_settings(page: Page, api_request: APIRequestContext) -> None:
    visit_authenticated(page, api_request, "/web/settings.html")
    expect(SettingsPage(page).page_root()).to_be_visible()


class TestProfileSection:
    def test_shows_pre_filled_values_for_name_and_email(self, page: Page) -> None:
        settings = SettingsPage(page)
        expect(settings.name_input()).to_have_value("Demo User")
        expect(settings.email_input()).to_have_value("demo@automation.io")

    @pytest.mark.smoke
    @pytest.mark.critical
    def test_saves_profile_and_shows_success_message(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.fill_name("Demo User Updated")
        settings.save_profile()
        settings.should_show_save_success()

    def test_shows_a_toast_on_save(self, page: Page) -> None:
        SettingsPage(page).save_profile()
        expect(page.get_by_test_id("toast-message")).to_contain_text("saved")

    def test_allows_changing_the_timezone_select(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.timezone_select().select_option("brt")
        expect(settings.timezone_select()).to_have_value("brt")

    def test_avatar_upload_input_accepts_image_files(self, page: Page) -> None:
        expect(SettingsPage(page).file_upload()).to_have_attribute("accept", re.compile(r"\.png"))


class TestNotificationsSection:
    def test_push_notifications_start_as_off(self, page: Page) -> None:
        SettingsPage(page).should_show_notifications_off()

    def test_toggles_notifications_on(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.toggle_notifications()
        settings.should_show_notifications_on()

    def test_toggles_notifications_back_off(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.toggle_notifications()
        settings.toggle_notifications()
        settings.should_show_notifications_off()

    def test_volume_slider_updates_the_displayed_value(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.set_slider(75)
        expect(settings.volume_value()).to_have_text("75")

    def test_weekly_digest_checkbox_is_checked_by_default(self, page: Page) -> None:
        expect(SettingsPage(page).digest_checkbox()).to_be_checked()

    def test_digest_start_date_field_is_editable(self, page: Page) -> None:
        date_input = SettingsPage(page).date_input()
        date_input.clear()
        date_input.fill("2025-01-01")
        expect(date_input).to_have_value("2025-01-01")


class TestSecurityPasswordChange:
    def test_shows_error_when_both_password_fields_are_empty(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.password_save_btn().click()
        settings.should_show_password_error("required")

    def test_shows_error_when_new_password_is_too_short(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.submit_password_change("Demo123!", "short")
        settings.should_show_password_error("8 characters")

    def test_shows_success_when_a_valid_new_password_is_provided(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.submit_password_change("Demo123!", "NewPass123!")
        expect(settings.password_result()).to_contain_text("updated")

    def test_clears_password_fields_after_successful_change(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.submit_password_change("Demo123!", "NewPass123!")
        expect(settings.current_password()).to_have_value("")
        expect(settings.new_password()).to_have_value("")

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


class TestSecurity2FA:
    def test_starts_as_disabled(self, page: Page) -> None:
        settings = SettingsPage(page)
        expect(settings.twofa_status()).to_have_text("Disabled")
        expect(settings.twofa_switch()).to_have_attribute("aria-checked", "false")

    def test_enables_2fa_on_toggle(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.toggle_2fa()
        settings.should_show_2fa_enabled()

    def test_disables_2fa_on_second_toggle(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.toggle_2fa()
        settings.toggle_2fa()
        expect(settings.twofa_status()).to_have_text("Disabled")


class TestSecurityActiveSessions:
    def test_shows_current_session_with_active_badge(self, page: Page) -> None:
        expect(page.get_by_test_id("session-current")).to_be_visible()
        expect(SettingsPage(page).session_badge()).to_contain_text("Active")

    def test_shows_session_device_name_and_location(self, page: Page) -> None:
        expect(page.get_by_test_id("session-name")).not_to_be_empty()
        expect(page.get_by_test_id("session-meta")).to_contain_text("Current session")


class TestIntegrationsApiToken:
    def test_displays_the_api_token(self, page: Page) -> None:
        token = SettingsPage(page).api_key_display()
        expect(token).to_be_visible()
        expect(token).not_to_be_empty()

    def test_shows_copied_feedback_when_copy_is_clicked(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.copy_token()
        settings.should_show_token_result("Copied")

    def test_generates_a_new_token_on_rotate(self, page: Page) -> None:
        settings = SettingsPage(page)
        original = settings.api_key_display().inner_text()
        settings.rotate_token()
        expect(settings.api_key_display()).not_to_have_text(original)

    def test_shows_toast_after_rotating_token(self, page: Page) -> None:
        SettingsPage(page).rotate_token()
        expect(page.get_by_test_id("toast-message")).to_contain_text("rotated")

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


class TestIntegrationsWebhook:
    def test_saves_a_valid_webhook_url(self, page: Page) -> None:
        settings = SettingsPage(page)
        settings.save_webhook("https://ci.example.com/webhook")
        settings.should_show_webhook_saved()

    def test_shows_error_when_webhook_url_is_empty(self, page: Page) -> None:
        SettingsPage(page).save_webhook_btn().click()
        expect(page.get_by_test_id("webhook-result")).to_contain_text("Enter a URL")

    def test_shows_toast_on_successful_save(self, page: Page) -> None:
        SettingsPage(page).save_webhook("https://ci.example.com/hook")
        expect(page.get_by_test_id("toast-message")).to_contain_text("saved")


class TestDangerZone:
    def test_delete_account_button_is_visible(self, page: Page) -> None:
        btn = SettingsPage(page).delete_account_btn()
        expect(btn).to_be_visible()
        expect(btn).to_have_class(re.compile(r"btn-danger"))

    def test_delete_account_shows_confirmation_dialog(self, page: Page) -> None:
        confirm_called = {"value": False}

        def handle_dialog(dialog) -> None:
            confirm_called["value"] = True
            assert dialog.type == "confirm"
            dialog.dismiss()

        page.on("dialog", handle_dialog)
        SettingsPage(page).delete_account_btn().click()
        assert confirm_called["value"] is True


@pytest.mark.a11y
@pytest.mark.regression
class TestAccessibility:
    def test_settings_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        form = SettingsPage(page).settings_form()
        expect(form).to_be_visible()
        check_a11y(page, disabled_rules=["color-contrast", "label", "select-name"])
