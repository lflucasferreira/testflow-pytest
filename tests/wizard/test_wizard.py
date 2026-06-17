import re

import pytest
from playwright.sync_api import Page, expect

from conftest import check_a11y
from support.auth import visit_authenticated
from support.factories.wizard import create_personal_step, create_preferences_step
from support.helpers.fixtures import read_fixture


def _complete_wizard_step1(page: Page, personal: dict[str, str]) -> None:
    page.get_by_test_id("wizard-name").fill(personal["name"])
    page.get_by_test_id("wizard-email").fill(personal["email"])
    page.get_by_test_id("wizard-dob").fill(personal["dob"])
    page.get_by_test_id("wizard-country").select_option(personal["country"])


def _complete_wizard_step2(page: Page, prefs: dict[str, str]) -> None:
    expect(page.get_by_test_id("wizard-panel-2")).to_have_class(re.compile(r"\bactive\b"))
    page.get_by_test_id(f"wizard-fw-{prefs['framework']}").check(force=True)
    page.get_by_test_id(f"wizard-role-{prefs['role']}").check(force=True)
    page.get_by_test_id("wizard-experience").fill(str(prefs["experience"]))
    page.get_by_test_id("wizard-terms").check(force=True)
    page.get_by_test_id("wizard-newsletter").check(force=True)


def _complete_wizard_step3(page: Page) -> None:
    expect(page.get_by_test_id("wizard-review")).to_be_visible()


def _advance_wizard(page: Page) -> None:
    page.get_by_test_id("wizard-next").click()


def _fill_wizard_flow(page: Page, personal: dict[str, str], prefs: dict[str, str]) -> None:
    _complete_wizard_step1(page, personal)
    _advance_wizard(page)
    _complete_wizard_step2(page, prefs)
    _advance_wizard(page)
    _complete_wizard_step3(page)
    _advance_wizard(page)


@pytest.fixture(autouse=True)
def wizard_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/wizard.html")
    expect(page.get_by_test_id("page-wizard")).to_be_attached()


@pytest.mark.regression
class TestWizardMultiStepFlow:
    @pytest.mark.smoke
    def test_shows_step_1_by_default(self, page: Page) -> None:
        expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()
        expect(page.get_by_test_id("wizard-step-1")).to_have_class(re.compile(r"\bactive\b"))

    def test_validates_required_fields_on_step_1(self, page: Page) -> None:
        page.get_by_test_id("wizard-next").click()
        expect(page.get_by_test_id("wizard-step1-error")).to_be_visible()

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

    def test_navigates_back_from_step_2_to_step_1(self, page: Page) -> None:
        personal = create_personal_step()
        _complete_wizard_step1(page, personal)
        _advance_wizard(page)
        page.get_by_test_id("wizard-back").click()
        expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()

    def test_restarts_wizard_after_completion(self, page: Page) -> None:
        personal = create_personal_step()
        prefs = create_preferences_step()
        _fill_wizard_flow(page, personal, prefs)
        page.get_by_test_id("wizard-restart").click()
        expect(page.get_by_test_id("wizard-panel-1")).to_be_visible()


@pytest.mark.regression
@pytest.mark.a11y
class TestWizardAccessibility:
    def test_wizard_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
