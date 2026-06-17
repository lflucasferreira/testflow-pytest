from typing import Self

from playwright.sync_api import Locator, Page, expect


class ActivityPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self) -> Locator:
        return self.page.get_by_test_id("page-activity")

    def fetch_users_btn(self) -> Locator:
        return self.page.get_by_test_id("fetch-users-btn")

    def fetch_slow_btn(self) -> Locator:
        return self.page.get_by_test_id("fetch-slow-btn")

    def api_result(self) -> Locator:
        return self.page.get_by_test_id("api-result")

    def counter_value(self) -> Locator:
        return self.page.get_by_test_id("counter-value")

    def counter_increment(self) -> Locator:
        return self.page.get_by_test_id("counter-increment")

    def counter_decrement(self) -> Locator:
        return self.page.get_by_test_id("counter-decrement")

    def counter_reset(self) -> Locator:
        return self.page.get_by_test_id("counter-reset")

    def counter_badge(self) -> Locator:
        return self.page.get_by_test_id("counter-badge")

    def progress_start(self) -> Locator:
        return self.page.get_by_test_id("progress-start")

    def download_progress(self) -> Locator:
        return self.page.get_by_test_id("download-progress")

    def pipeline_pct(self) -> Locator:
        return self.page.get_by_test_id("pipeline-pct")

    def pipeline_badge(self) -> Locator:
        return self.page.get_by_test_id("pipeline-status-badge")

    def load_dynamic_btn(self) -> Locator:
        return self.page.get_by_test_id("load-dynamic-btn")

    def dynamic_content(self) -> Locator:
        return self.page.get_by_test_id("dynamic-content")

    def drop_zone(self) -> Locator:
        return self.page.get_by_test_id("drop-zone")

    def page_next_btn(self) -> Locator:
        return self.page.get_by_test_id("page-next-btn")

    def page_back_btn(self) -> Locator:
        return self.page.get_by_test_id("page-back-btn")

    def fetch_users(self) -> Self:
        self.fetch_users_btn().click()
        return self

    def increment_counter(self, times: int = 1) -> Self:
        for _ in range(times):
            self.counter_increment().click()
        return self

    def start_pipeline(self) -> Self:
        self.progress_start().click()
        return self

    def load_dynamic_content(self) -> Self:
        self.load_dynamic_btn().click()
        return self

    def should_show_api_result(self) -> Self:
        expect(self.api_result()).to_be_visible()
        expect(self.api_result()).not_to_be_empty()
        return self

    def should_show_counter(self, value: str | int) -> Self:
        expect(self.counter_value()).to_contain_text(str(value))
        return self

    def should_show_dynamic_content(self) -> Self:
        expect(self.dynamic_content()).to_be_visible()
        expect(self.dynamic_content()).not_to_be_empty()
        return self

    def should_show_pipeline_progress(self, min_pct: int = 1) -> Self:
        text = self.pipeline_pct().inner_text()
        pct = int(text.replace("%", ""))
        assert pct >= min_pct
        return self
