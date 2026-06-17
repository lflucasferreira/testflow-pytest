import re

import pytest
from playwright.sync_api import Page, expect

from support.auth import visit_authenticated
from support.constants.viewports import DESKTOP, MOBILE


@pytest.fixture(autouse=True)
def advanced_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/advanced.html")
    expect(page.get_by_test_id("page-advanced")).to_be_attached()


@pytest.mark.regression
class TestAdvanced:
    @pytest.mark.smoke
    def test_renders_shadow_dom_section(self, page: Page) -> None:
        expect(page.get_by_test_id("section-shadow")).to_be_visible()
        expect(page.get_by_test_id("shadow-host")).to_be_attached()

    def test_accesses_content_inside_shadow_root(self, page: Page) -> None:
        shadow_content = page.get_by_test_id("shadow-host").locator("*")
        expect(shadow_content.first).to_be_attached()
        assert shadow_content.count() >= 1

    def test_loads_demo_iframe(self, page: Page) -> None:
        iframe = page.get_by_test_id("demo-iframe")
        expect(iframe).to_be_visible()
        expect(iframe).to_have_attribute("src", re.compile(r".+"))

    def test_shows_external_link_with_target_blank(self, page: Page) -> None:
        link = page.get_by_test_id("external-link")
        expect(link).to_have_attribute("href", re.compile(r"http"))

    @pytest.mark.smoke
    def test_renders_shadow_section_at_mobile_viewport(self, page: Page) -> None:
        page.set_viewport_size(MOBILE)
        expect(page.get_by_test_id("section-shadow")).to_be_visible()
        page.set_viewport_size(DESKTOP)

    def test_navigates_with_page_finish_button(self, page: Page) -> None:
        page.get_by_test_id("page-finish-btn").click()
        expect(page).not_to_have_url(re.compile(r"/web/advanced\.html"))
