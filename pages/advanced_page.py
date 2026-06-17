import re
from typing import Self

from playwright.sync_api import FrameLocator, Locator, Page, expect


class AdvancedPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self) -> Locator:
        return self.page.get_by_test_id("page-advanced")

    def section_shadow(self) -> Locator:
        return self.page.get_by_test_id("section-shadow")

    def shadow_host(self) -> Locator:
        return self.page.get_by_test_id("shadow-host")

    def demo_iframe(self) -> Locator:
        return self.page.get_by_test_id("demo-iframe")

    def external_link(self) -> Locator:
        return self.page.get_by_test_id("external-link")

    def iframe_result(self) -> Locator:
        return self.page.get_by_test_id("iframe-result")

    def finish_btn(self) -> Locator:
        return self.page.get_by_test_id("page-finish-btn")

    def back_btn(self) -> Locator:
        return self.page.get_by_test_id("page-back-btn")

    def shadow_content_count(self) -> int:
        return self.shadow_host().evaluate(
            """(host) => {
                const root = host.shadowRoot;
                return root ? root.querySelectorAll('*').length : 0;
            }"""
        )

    def iframe_frame(self) -> FrameLocator:
        return self.page.frame_locator('[data-testid="demo-iframe"]')

    def should_show_shadow_section(self) -> Self:
        expect(self.section_shadow()).to_be_visible()
        expect(self.shadow_host()).to_be_visible()
        return self

    def should_have_iframe_src(self) -> Self:
        expect(self.demo_iframe()).to_be_visible()
        expect(self.demo_iframe()).to_have_attribute("src", re.compile(r"."))
        return self

    def should_have_external_link(self) -> Self:
        expect(self.external_link()).to_have_attribute("href", re.compile(r"^https?://"))
        expect(self.external_link()).to_have_attribute("target", "_blank")
        return self

    def should_show_iframe_content(self) -> Self:
        frame = self.iframe_frame()
        expect(frame.locator("body")).to_be_visible(timeout=10_000)
        return self
