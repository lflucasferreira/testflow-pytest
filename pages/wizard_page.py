import re
from typing import Literal, Self, TypedDict

from playwright.sync_api import Locator, Page, expect


class WizardPersonalStep(TypedDict):
    name: str
    email: str
    dob: str
    country: str


class WizardPreferencesStep(TypedDict):
    framework: Literal["cypress", "playwright", "pytest", "rest-assured"]
    role: Literal["qa", "dev", "sdet", "manager"]
    experience: str


class WizardPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self) -> Locator:
        return self.page.get_by_test_id("page-wizard")

    def name_input(self) -> Locator:
        return self.page.get_by_test_id("wizard-name")

    def email_input(self) -> Locator:
        return self.page.get_by_test_id("wizard-email")

    def dob_input(self) -> Locator:
        return self.page.get_by_test_id("wizard-dob")

    def country_select(self) -> Locator:
        return self.page.get_by_test_id("wizard-country")

    def next_btn(self) -> Locator:
        return self.page.get_by_test_id("wizard-next")

    def back_btn(self) -> Locator:
        return self.page.get_by_test_id("wizard-back")

    def restart_btn(self) -> Locator:
        return self.page.get_by_test_id("wizard-restart")

    def step(self, n: Literal[1, 2, 3]) -> Locator:
        return self.page.get_by_test_id(f"wizard-step-{n}")

    def panel(self, n: Literal[1, 2, 3]) -> Locator:
        return self.page.get_by_test_id(f"wizard-panel-{n}")

    def step1_error(self) -> Locator:
        return self.page.get_by_test_id("wizard-step1-error")

    def step2_error(self) -> Locator:
        return self.page.get_by_test_id("wizard-step2-error")

    def review(self) -> Locator:
        return self.page.get_by_test_id("wizard-review")

    def success(self) -> Locator:
        return self.page.get_by_test_id("wizard-success")

    def success_message(self) -> Locator:
        return self.page.get_by_test_id("wizard-success-message")

    def review_name(self) -> Locator:
        return self.page.get_by_test_id("review-name")

    def review_email(self) -> Locator:
        return self.page.get_by_test_id("review-email")

    def experience_slider(self) -> Locator:
        return self.page.get_by_test_id("wizard-experience")

    def terms_checkbox(self) -> Locator:
        return self.page.get_by_test_id("wizard-terms")

    def newsletter_checkbox(self) -> Locator:
        return self.page.get_by_test_id("wizard-newsletter")

    def framework_radio(self, name: str) -> Locator:
        return self.page.get_by_test_id(f"wizard-fw-{name}")

    def role_radio(self, role: str) -> Locator:
        return self.page.get_by_test_id(f"wizard-role-{role}")

    def advance(self) -> Self:
        self.next_btn().click()
        return self

    def go_back(self) -> Self:
        self.back_btn().click()
        return self

    def complete_step1(self, data: WizardPersonalStep) -> Self:
        self.name_input().fill(data["name"])
        self.email_input().fill(data["email"])
        self.dob_input().fill(data["dob"])
        self.country_select().select_option(data["country"])
        return self

    def complete_step2(self, data: WizardPreferencesStep) -> Self:
        self.framework_radio(data["framework"]).check(force=True)
        self.role_radio(data["role"]).check(force=True)
        self.experience_slider().fill(data["experience"])
        self.terms_checkbox().check(force=True)
        self.newsletter_checkbox().check(force=True)
        return self

    def complete_step3(self) -> Self:
        expect(self.review()).to_be_visible()
        return self

    def complete_full_flow(
        self,
        personal: WizardPersonalStep,
        preferences: WizardPreferencesStep,
    ) -> Self:
        self.complete_step1(personal)
        self.advance()
        self.complete_step2(preferences)
        self.advance()
        self.complete_step3()
        self.advance()
        return self

    def should_show_step1_active(self) -> Self:
        expect(self.panel(1)).to_be_visible()
        expect(self.step(1)).to_have_class(re.compile(r"active"))
        return self

    def should_show_step1_error(self) -> Self:
        expect(self.step1_error()).to_be_visible()
        return self

    def should_show_step2_error(self) -> Self:
        expect(self.step2_error()).to_be_visible()
        return self

    def should_show_success(self) -> Self:
        expect(self.success()).to_be_visible()
        expect(self.success_message()).not_to_be_empty()
        return self

    def should_show_review_name(self, name: str) -> Self:
        expect(self.review_name()).to_contain_text(name)
        return self

    def should_mark_step_done(self, n: Literal[1, 2, 3]) -> Self:
        expect(self.step(n)).to_have_class(re.compile(r"done"))
        return self
