import re
from typing import Self

from playwright.sync_api import Locator, Page, expect


class DashboardPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self) -> Locator:
        return self.page.get_by_test_id("page-dashboard")

    def greeting(self) -> Locator:
        return self.page.get_by_test_id("dash-greeting")

    def subtitle(self) -> Locator:
        return self.page.get_by_test_id("dash-subtitle")

    def kpi_grid(self) -> Locator:
        return self.page.get_by_test_id("kpi-grid")

    def kpi_card(self, name: str) -> Locator:
        return self.page.get_by_test_id(f"kpi-{name}")

    def kpi_value(self, name: str) -> Locator:
        return self.page.get_by_test_id(f"kpi-{name}-value")

    def kpi_trend(self, name: str) -> Locator:
        return self.page.get_by_test_id(f"kpi-{name}-trend")

    def activity_list(self) -> Locator:
        return self.page.get_by_test_id("activity-list")

    def activity_item(self, n: int) -> Locator:
        return self.page.get_by_test_id(f"activity-item-{n}")

    def health_status(self) -> Locator:
        return self.page.get_by_test_id("health-status")

    def health_bar(self, suite: str) -> Locator:
        return self.page.get_by_test_id(f"health-{suite}")

    def health_pct(self, suite: str) -> Locator:
        return self.page.get_by_test_id(f"health-{suite}-pct")

    def new_run_btn(self) -> Locator:
        return self.page.get_by_test_id("btn-new-run")

    def run_modal(self) -> Locator:
        return self.page.get_by_test_id("run-modal-overlay")

    def run_suite_select(self) -> Locator:
        return self.page.get_by_test_id("run-suite")

    def run_env_select(self) -> Locator:
        return self.page.get_by_test_id("run-env")

    def run_confirm_btn(self) -> Locator:
        return self.page.get_by_test_id("run-modal-confirm")

    def run_cancel_btn(self) -> Locator:
        return self.page.get_by_test_id("run-modal-cancel")

    def quick_action(self, name: str) -> Locator:
        return self.page.get_by_test_id(f"qa-{name}")

    def open_new_run_modal(self) -> Self:
        self.new_run_btn().click()
        expect(self.run_modal()).to_be_visible()
        return self

    def select_suite(self, suite: str) -> Self:
        self.run_suite_select().select_option(suite)
        return self

    def select_environment(self, env: str) -> Self:
        self.run_env_select().select_option(env)
        return self

    def confirm_run(self) -> Self:
        self.run_confirm_btn().click()
        return self

    def cancel_run(self) -> Self:
        self.run_cancel_btn().click()
        return self

    def should_be_loaded(self) -> Self:
        expect(self.page_root()).to_be_visible()
        return self

    def should_show_greeting(self) -> Self:
        expect(self.greeting()).to_be_visible()
        expect(self.greeting()).to_have_text(re.compile(r"Good (morning|afternoon|evening),"))
        return self

    def should_have_all_kpi_cards(self) -> Self:
        for key in ("runs", "passrate", "members", "issues"):
            expect(self.kpi_card(key)).to_be_visible()
            expect(self.kpi_value(key)).not_to_be_empty()
        return self

    def should_have_activity_items(self, count: int = 5) -> Self:
        expect(
            self.activity_list().locator('[data-testid^="activity-item-"]')
        ).to_have_count(count)
        return self

    def should_show_run_modal_open(self) -> Self:
        expect(self.run_modal()).to_be_visible()
        return self

    def should_show_run_modal_closed(self) -> Self:
        expect(self.run_modal()).not_to_be_visible()
        return self
