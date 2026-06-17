from typing import Self

from playwright.sync_api import Locator, Page, expect


class StatesPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self) -> Locator:
        return self.page.get_by_test_id("page-states")

    def skeleton_trigger(self) -> Locator:
        return self.page.get_by_test_id("skeleton-trigger")

    def skeleton_reset(self) -> Locator:
        return self.page.get_by_test_id("skeleton-reset")

    def skeleton_container(self) -> Locator:
        return self.page.get_by_test_id("skeleton-container")

    def skeleton_idle(self) -> Locator:
        return self.page.get_by_test_id("skeleton-idle")

    def empty_search(self) -> Locator:
        return self.page.get_by_test_id("empty-search")

    def empty_state(self) -> Locator:
        return self.page.get_by_test_id("empty-state")

    def result_list(self) -> Locator:
        return self.page.get_by_test_id("result-list")

    def error_trigger(self) -> Locator:
        return self.page.get_by_test_id("error-trigger")

    def success_trigger(self) -> Locator:
        return self.page.get_by_test_id("success-trigger")

    def error_container(self) -> Locator:
        return self.page.get_by_test_id("error-container")

    def partial_trigger(self) -> Locator:
        return self.page.get_by_test_id("partial-trigger")

    def partial_reset(self) -> Locator:
        return self.page.get_by_test_id("partial-reset")

    def partial_grid(self) -> Locator:
        return self.page.get_by_test_id("partial-grid")

    def load_skeleton_cards(self) -> Self:
        self.skeleton_trigger().click()
        return self

    def reset_skeleton(self) -> Self:
        self.skeleton_reset().click()
        return self

    def search_empty(self, term: str) -> Self:
        self.empty_search().fill(term)
        return self

    def trigger_error_fetch(self) -> Self:
        self.error_trigger().click()
        return self

    def trigger_success_fetch(self) -> Self:
        self.success_trigger().click()
        return self

    def load_partial_grid(self) -> Self:
        self.partial_trigger().click()
        return self

    def reset_partial_grid(self) -> Self:
        self.partial_reset().click()
        return self

    def should_show_skeleton_loading(self) -> Self:
        expect(self.skeleton_container()).to_be_visible()
        return self

    def should_show_empty_state(self) -> Self:
        expect(self.empty_state()).to_be_visible()
        expect(self.result_list()).not_to_be_visible()
        return self

    def should_show_error_state(self) -> Self:
        expect(self.error_container()).to_be_visible()
        expect(self.error_container()).not_to_be_empty()
        return self

    def should_show_partial_grid(self) -> Self:
        expect(self.partial_grid()).to_be_visible()
        return self
