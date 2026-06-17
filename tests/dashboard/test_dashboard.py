import re

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from pages.dashboard_page import DashboardPage
from support.auth import login_via_api

pytestmark = pytest.mark.regression


@pytest.fixture(autouse=True)
def setup_dashboard(page: Page, api_request: APIRequestContext) -> None:
    login_via_api(page, api_request)
    DashboardPage(page).should_be_loaded()


class TestGreeting:
    def test_shows_time_based_greeting_with_the_user_name(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.should_show_greeting()
        expect(dashboard.greeting()).to_contain_text("Demo User")

    def test_shows_a_non_empty_subtitle(self, page: Page) -> None:
        subtitle = DashboardPage(page).subtitle()
        expect(subtitle).to_be_visible()
        expect(subtitle).not_to_be_empty()


class TestKpiCards:
    def test_renders_all_four_kpi_cards(self, page: Page) -> None:
        DashboardPage(page).should_have_all_kpi_cards()

    def test_shows_a_numeric_value_in_the_runs_card(self, page: Page) -> None:
        text = DashboardPage(page).kpi_value("runs").inner_text()
        assert int(text) > 0

    def test_shows_a_percentage_in_the_pass_rate_card(self, page: Page) -> None:
        expect(DashboardPage(page).kpi_value("passrate")).to_have_text(
            re.compile(r"^\d+(\.\d+)?%$")
        )

    def test_shows_trend_indicators_on_each_card(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        for key in ("runs", "passrate", "members", "issues"):
            expect(dashboard.kpi_trend(key)).to_be_visible()
            expect(dashboard.kpi_trend(key)).not_to_be_empty()


class TestRecentActivity:
    def test_shows_5_activity_items(self, page: Page) -> None:
        DashboardPage(page).should_have_activity_items(5)

    def test_each_activity_item_has_text_and_a_timestamp(self, page: Page) -> None:
        item = DashboardPage(page).activity_item(1)
        expect(item.locator(".activity-text")).not_to_be_empty()
        expect(item.locator(".activity-time")).not_to_be_empty()

    def test_see_all_link_navigates_to_activity_page(self, page: Page) -> None:
        DashboardPage(page).quick_action("team")
        page.get_by_test_id("activity-see-all").click()
        expect(page).to_have_url(re.compile(r"/web/activity\.html"))


class TestSuiteHealth:
    def test_shows_healthy_status_badge(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        expect(dashboard.health_status()).to_be_visible()
        expect(dashboard.health_status()).to_contain_text("Healthy")

    def test_renders_three_suite_health_bars(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        for suite in ("regression", "smoke", "e2e"):
            expect(dashboard.health_bar(suite)).to_be_visible()
            expect(dashboard.health_pct(suite)).to_have_text(re.compile(r"^\d+%$"))

    def test_regression_bar_fill_width_reflects_its_percentage(self, page: Page) -> None:
        expect(DashboardPage(page).health_bar("regression")).to_have_attribute(
            "style", re.compile(r"width:97%")
        )


class TestNewTestRunModal:
    def test_opens_modal_on_button_click(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.open_new_run_modal()
        dashboard.should_show_run_modal_open()

    def test_modal_has_suite_and_environment_selects(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.open_new_run_modal()
        expect(dashboard.run_suite_select()).to_be_visible()
        expect(dashboard.run_env_select()).to_be_visible()

    def test_closes_modal_on_cancel(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.open_new_run_modal()
        dashboard.cancel_run()
        dashboard.should_show_run_modal_closed()

    def test_closes_modal_on_escape_key(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.open_new_run_modal()
        page.keyboard.press("Escape")
        dashboard.should_show_run_modal_closed()

    def test_closes_modal_on_overlay_click(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.open_new_run_modal()
        page.get_by_test_id("run-modal-overlay").click(
            position={"x": 10, "y": 10}, force=True
        )
        dashboard.should_show_run_modal_closed()

    def test_confirms_a_run_and_shows_toast(self, page: Page) -> None:
        dashboard = DashboardPage(page)
        dashboard.open_new_run_modal()
        dashboard.select_suite("smoke")
        dashboard.select_environment("staging")
        dashboard.confirm_run()
        dashboard.should_show_run_modal_closed()
        expect(page.get_by_test_id("toast-message")).to_contain_text("smoke")


@pytest.mark.parametrize(
    "test_id,path",
    [
        ("qa-team", "/web/team.html"),
        ("qa-settings", "/web/settings.html"),
        ("qa-wizard", "/web/wizard.html"),
    ],
)
class TestQuickAccessNavigation:
    def test_quick_access_navigates(self, page: Page, test_id: str, path: str) -> None:
        page.get_by_test_id(test_id).click()
        expect(page).to_have_url(re.compile(re.escape(path)))
        page.go_back()
