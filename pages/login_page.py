import re
from typing import Self

from playwright.sync_api import Locator, Page, expect


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def email_input(self) -> Locator:
        return self.page.get_by_test_id("login-email")

    def password_input(self) -> Locator:
        return self.page.get_by_test_id("login-password")

    def remember_checkbox(self) -> Locator:
        return self.page.get_by_test_id("login-remember")

    def use_api_checkbox(self) -> Locator:
        return self.page.get_by_test_id("login-use-api")

    def submit_btn(self) -> Locator:
        return self.page.get_by_test_id("login-submit")

    def result_msg(self) -> Locator:
        return self.page.get_by_test_id("login-result")

    def visit(self) -> Self:
        self.page.goto("/web/login.html")
        return self

    def fill_email(self, email: str) -> Self:
        self.email_input().clear()
        self.email_input().fill(email)
        return self

    def fill_password(self, password: str) -> Self:
        self.password_input().clear()
        self.password_input().fill(password)
        return self

    def submit(self) -> Self:
        self.submit_btn().click()
        return self

    def login_with(self, email: str, password: str) -> Self:
        self.fill_email(email)
        self.fill_password(password)
        self.submit()
        return self

    def toggle_use_api(self) -> Self:
        self.use_api_checkbox().evaluate("el => el.click()")
        return self

    def toggle_remember_me(self) -> Self:
        self.remember_checkbox().click()
        return self

    def should_be_on_login_page(self) -> Self:
        expect(self.page).to_have_url(re.compile(r"/web/login\.html"))
        return self

    def should_show_error(self, text: str) -> Self:
        expect(self.result_msg()).to_be_visible()
        expect(self.result_msg()).to_contain_text(text)
        return self

    def should_redirect_to_dashboard(self) -> Self:
        expect(self.page.get_by_test_id("page-dashboard")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r"/web/dashboard\.html"))
        return self
