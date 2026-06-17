from typing import Self

from playwright.sync_api import Locator, Page, expect


class ComponentsPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self) -> Locator:
        return self.page.get_by_test_id("page-components")

    def open_modal_btn(self) -> Locator:
        return self.page.get_by_test_id("open-modal-btn")

    def modal_overlay(self) -> Locator:
        return self.page.get_by_test_id("modal-overlay")

    def modal_confirm_btn(self) -> Locator:
        return self.page.get_by_test_id("modal-confirm-btn")

    def modal_cancel_btn(self) -> Locator:
        return self.page.get_by_test_id("modal-cancel-btn")

    def modal_close_btn(self) -> Locator:
        return self.page.get_by_test_id("modal-close-btn")

    def toast_message(self) -> Locator:
        return self.page.get_by_test_id("toast-message")

    def dialog_result(self) -> Locator:
        return self.page.get_by_test_id("dialog-result")

    def tab_overview(self) -> Locator:
        return self.page.get_by_test_id("tab-overview")

    def tab_cypress(self) -> Locator:
        return self.page.get_by_test_id("tab-cypress")

    def tab_playwright(self) -> Locator:
        return self.page.get_by_test_id("tab-playwright")

    def tab_panel_overview(self) -> Locator:
        return self.page.get_by_test_id("tab-panel-overview")

    def tab_panel_cypress(self) -> Locator:
        return self.page.get_by_test_id("tab-panel-cypress")

    def tab_panel_playwright(self) -> Locator:
        return self.page.get_by_test_id("tab-panel-playwright")

    def accordion_trigger(self, n: int) -> Locator:
        return self.page.get_by_test_id(f"accordion-trigger-{n}")

    def accordion_panel(self, n: int) -> Locator:
        return self.page.get_by_test_id(f"accordion-panel-{n}")

    def button(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    def open_modal(self) -> Self:
        self.open_modal_btn().click()
        expect(self.modal_overlay()).to_be_visible()
        return self

    def should_show_page(self) -> Self:
        expect(self.page_root()).to_be_visible()
        return self
