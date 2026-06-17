import re

import pytest
from playwright.sync_api import Page, expect

from conftest import check_a11y
from pages.login_page import LoginPage
from support.config import DEMO_EMAIL, DEMO_PASSWORD
from support.helpers.fixtures import read_fixture

pytestmark = pytest.mark.regression

credentials = read_fixture("credentials.json")


@pytest.fixture(autouse=True)
def visit_login(page: Page) -> None:
    LoginPage(page).visit()


class TestPageStructure:
    def test_tc0100_renders_all_form_elements(self, page: Page) -> None:
        login = LoginPage(page)
        expect(login.email_input()).to_be_visible()
        expect(login.password_input()).to_be_visible()
        expect(login.submit_btn()).to_be_visible()
        expect(login.submit_btn()).to_be_enabled()
        expect(login.remember_checkbox()).to_be_attached()
        expect(login.use_api_checkbox()).to_be_attached()

    def test_has_correct_placeholder_text_on_email_field(self, page: Page) -> None:
        expect(LoginPage(page).email_input()).to_have_attribute(
            "placeholder", "demo@automation.io"
        )

    def test_password_field_masks_input(self, page: Page) -> None:
        expect(LoginPage(page).password_input()).to_have_attribute("type", "password")


@pytest.mark.smoke
@pytest.mark.critical
class TestValidCredentials:
    def test_tc0101_logs_in_via_ui_and_redirects_to_dashboard(self, page: Page) -> None:
        login = LoginPage(page)
        login.login_with(DEMO_EMAIL, DEMO_PASSWORD)
        login.should_redirect_to_dashboard()

    def test_logs_in_with_api_toggle_enabled(self, page: Page) -> None:
        login = LoginPage(page)
        with page.expect_request(
            lambda req: "/api/auth/login" in req.url and req.method == "POST"
        ) as request_info:
            login.toggle_use_api()
            login.login_with(DEMO_EMAIL, DEMO_PASSWORD)

        response = request_info.value.response()
        assert response is not None
        assert response.status == 200
        login.should_redirect_to_dashboard()

    def test_sets_auth_data_in_session_storage_after_login(self, page: Page) -> None:
        LoginPage(page).login_with(DEMO_EMAIL, DEMO_PASSWORD)
        auth = page.evaluate(
            """() => {
                const raw = sessionStorage.getItem('sandbox-auth');
                return raw ? JSON.parse(raw) : null;
            }"""
        )
        assert auth is not None
        assert auth["email"] == DEMO_EMAIL

    def test_shows_success_message_before_redirect(self, page: Page) -> None:
        login = LoginPage(page)
        login.login_with(DEMO_EMAIL, DEMO_PASSWORD)

        result = page.get_by_test_id("login-result")
        if result.is_visible():
            expect(result).to_contain_text("Login successful")
        login.should_redirect_to_dashboard()

    def test_submits_login_form_with_enter_key(self, page: Page) -> None:
        login = LoginPage(page)
        login.fill_email(DEMO_EMAIL)
        login.fill_password(DEMO_PASSWORD)
        login.password_input().press("Enter")
        login.should_redirect_to_dashboard()


class TestInvalidCredentials:
    def test_shows_error_for_wrong_password(self, page: Page) -> None:
        login = LoginPage(page)
        login.login_with(credentials["valid"]["email"], credentials["invalid"]["password"])
        login.should_show_error("Invalid credentials")

    def test_shows_error_for_unknown_email(self, page: Page) -> None:
        login = LoginPage(page)
        login.login_with(credentials["invalid"]["email"], credentials["valid"]["password"])
        login.should_show_error("Invalid credentials")

    def test_does_not_navigate_away_on_failed_login(self, page: Page) -> None:
        LoginPage(page).login_with(
            credentials["invalid"]["email"], credentials["invalid"]["password"]
        )
        expect(page).to_have_url(re.compile(r"/web/login\.html"))


class TestFormValidation:
    def test_requires_email_to_not_be_empty_html5_validation(self, page: Page) -> None:
        login = LoginPage(page)
        login.fill_password(DEMO_PASSWORD)
        login.submit()
        is_valid = login.email_input().evaluate("el => el.validity.valid")
        assert is_valid is False


class TestRememberMe:
    def test_checkbox_can_be_checked_and_unchecked(self, page: Page) -> None:
        login = LoginPage(page)
        expect(login.remember_checkbox()).not_to_be_checked()
        login.toggle_remember_me()
        expect(login.remember_checkbox()).to_be_checked()
        login.toggle_remember_me()
        expect(login.remember_checkbox()).not_to_be_checked()


class TestRedirectAfterLogin:
    def test_redirects_to_login_when_accessing_a_protected_page_unauthenticated(
        self, page: Page
    ) -> None:
        page.goto("/web/team.html")
        expect(page).to_have_url(re.compile(r"/web/login\.html"))

        LoginPage(page).login_with(DEMO_EMAIL, DEMO_PASSWORD)
        expect(page).not_to_have_url(re.compile(r"/web/login\.html"))


class TestLogout:
    def test_clears_session_and_redirects_to_home_after_logout(self, page: Page) -> None:
        login = LoginPage(page)
        login.login_with(DEMO_EMAIL, DEMO_PASSWORD)
        login.should_redirect_to_dashboard()

        page.get_by_test_id("nav-logout").click()
        expect(page).to_have_url(re.compile(r"/web/index\.html"))
        assert page.evaluate("() => sessionStorage.getItem('sandbox-auth')") is None


@pytest.mark.a11y
@pytest.mark.regression
class TestAccessibility:
    def test_login_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
