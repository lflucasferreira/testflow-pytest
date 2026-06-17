import pytest
from playwright.sync_api import Page, expect

from conftest import check_a11y
from support.auth import visit_authenticated
from support.constants.test_cases import TC, tc


@pytest.fixture(autouse=True)
def components_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/components.html")
    expect(page.get_by_test_id("page-components")).to_be_attached()


@pytest.mark.regression
class TestButtons:
    def test_all_button_variants_are_visible(self, page: Page) -> None:
        for test_id in ("btn-primary", "btn-secondary", "btn-success", "btn-danger"):
            btn = page.get_by_test_id(test_id)
            expect(btn).to_be_visible()
            expect(btn).to_be_enabled()

    def test_disabled_button_is_not_interactive(self, page: Page) -> None:
        btn = page.get_by_test_id("btn-disabled")
        expect(btn).to_be_disabled()
        expect(btn).to_have_css("cursor", "not-allowed")

    @pytest.mark.parametrize(
        "title",
        [tc(TC.COMP_LOADING_BUTTON, "loading button shows spinner during simulated load")],
        ids=[TC.COMP_LOADING_BUTTON],
    )
    def test_loading_button_shows_spinner_during_simulated_load(self, page: Page, title: str) -> None:
        del title
        page.clock.install()
        page.get_by_test_id("btn-loading").click()
        expect(page.get_by_test_id("btn-loading")).to_be_disabled()
        expect(page.locator(".spinner")).to_be_visible()
        page.clock.fast_forward(2000)
        expect(page.get_by_test_id("btn-loading")).to_be_enabled()

    def test_toast_button_shows_a_toast_notification(self, page: Page) -> None:
        page.get_by_test_id("btn-toast").click()
        toast = page.get_by_test_id("toast-message")
        expect(toast).to_be_visible()
        expect(toast).not_to_be_empty()

    def test_native_alert_can_be_dismissed(self, page: Page) -> None:
        messages: list[str] = []

        def handle_dialog(dialog) -> None:
            messages.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)
        page.get_by_test_id("btn-alert").click()
        assert messages
        assert messages[0]

    def test_native_confirm_returns_true_on_accept(self, page: Page) -> None:
        page.on("dialog", lambda dialog: dialog.accept())
        page.get_by_test_id("btn-confirm").click()
        expect(page.get_by_test_id("dialog-result")).to_contain_text("Confirmed")

    def test_native_confirm_returns_false_on_cancel(self, page: Page) -> None:
        page.on("dialog", lambda dialog: dialog.dismiss())
        page.get_by_test_id("btn-confirm").click()
        expect(page.get_by_test_id("dialog-result")).to_contain_text("Cancelled")


@pytest.mark.regression
class TestModal:
    @pytest.fixture(autouse=True)
    def open_modal(self, page: Page) -> None:
        page.get_by_test_id("open-modal-btn").click()
        expect(page.get_by_test_id("modal-overlay")).to_be_visible()

    def test_opens_modal_and_shows_title(self, page: Page) -> None:
        expect(page.locator("#modal-title")).to_contain_text("Confirm action")

    def test_has_accessible_role_dialog(self, page: Page) -> None:
        overlay = page.get_by_test_id("modal-overlay")
        expect(overlay).to_have_attribute("role", "dialog")
        expect(overlay).to_have_attribute("aria-modal", "true")

    def test_closes_on_confirm_button(self, page: Page) -> None:
        page.get_by_test_id("modal-confirm-btn").click()
        expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()
        expect(page.get_by_test_id("toast-message")).to_be_visible()

    def test_closes_on_cancel_button(self, page: Page) -> None:
        page.get_by_test_id("modal-cancel-btn").click()
        expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()

    def test_closes_on_close_button(self, page: Page) -> None:
        page.get_by_test_id("modal-close-btn").click()
        expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()

    def test_closes_on_escape_key(self, page: Page) -> None:
        page.keyboard.press("Escape")
        expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()

    def test_closes_on_overlay_background_click(self, page: Page) -> None:
        page.get_by_test_id("modal-overlay").click(position={"x": 5, "y": 5})
        expect(page.get_by_test_id("modal-overlay")).not_to_be_visible()

    def test_aria_hidden_is_set_correctly_when_closed(self, page: Page) -> None:
        page.get_by_test_id("modal-cancel-btn").click()
        expect(page.get_by_test_id("modal-overlay")).to_have_attribute("aria-hidden", "true")


@pytest.mark.regression
class TestTabs:
    def test_overview_tab_is_active_by_default(self, page: Page) -> None:
        expect(page.get_by_test_id("tab-overview")).to_have_attribute("aria-selected", "true")
        expect(page.get_by_test_id("tab-panel-overview")).to_be_visible()

    def test_clicking_cypress_tab_activates_it_and_shows_its_panel(self, page: Page) -> None:
        page.get_by_test_id("tab-cypress").click()
        expect(page.get_by_test_id("tab-cypress")).to_have_attribute("aria-selected", "true")
        expect(page.get_by_test_id("tab-panel-cypress")).to_be_visible()
        expect(page.get_by_test_id("tab-panel-overview")).not_to_be_visible()

    def test_clicking_playwright_tab_activates_it_and_shows_its_panel(self, page: Page) -> None:
        page.get_by_test_id("tab-playwright").click()
        expect(page.get_by_test_id("tab-playwright")).to_have_attribute("aria-selected", "true")
        expect(page.get_by_test_id("tab-panel-playwright")).to_be_visible()

    def test_only_one_tab_panel_is_visible_at_a_time(self, page: Page) -> None:
        page.get_by_test_id("tab-cypress").click()
        expect(page.locator(".tab-panel.active")).to_have_count(1)

    def test_tabs_have_correct_role_attributes(self, page: Page) -> None:
        expect(page.locator('[role="tablist"]')).to_be_attached()
        expect(page.locator('[role="tab"]')).to_have_count(3)
        expect(page.locator('[role="tabpanel"]')).to_have_count(3)

    def test_supports_keyboard_focus_on_tab_controls(self, page: Page) -> None:
        expect(page.get_by_test_id("tab-overview")).to_have_attribute("aria-selected", "true")
        tab = page.get_by_test_id("tab-cypress")
        tab.focus()
        expect(tab).to_be_focused()
        tab.click()
        expect(page.get_by_test_id("tab-panel-cypress")).to_be_visible()


@pytest.mark.regression
class TestAccordion:
    def test_all_panels_are_collapsed_by_default(self, page: Page) -> None:
        for n in (1, 2, 3):
            expect(page.get_by_test_id(f"accordion-trigger-{n}")).to_have_attribute(
                "aria-expanded", "false"
            )
            expect(page.get_by_test_id(f"accordion-panel-{n}")).not_to_be_visible()

    def test_expands_first_panel_on_click(self, page: Page) -> None:
        page.get_by_test_id("accordion-trigger-1").click()
        expect(page.get_by_test_id("accordion-trigger-1")).to_have_attribute("aria-expanded", "true")
        expect(page.get_by_test_id("accordion-panel-1")).to_be_visible()

    def test_collapses_first_panel_on_second_click(self, page: Page) -> None:
        trigger = page.get_by_test_id("accordion-trigger-1")
        trigger.click()
        trigger.click()
        expect(page.get_by_test_id("accordion-panel-1")).not_to_be_visible()

    def test_multiple_panels_can_be_open_simultaneously(self, page: Page) -> None:
        page.get_by_test_id("accordion-trigger-1").click()
        page.get_by_test_id("accordion-trigger-2").click()
        expect(page.get_by_test_id("accordion-panel-1")).to_be_visible()
        expect(page.get_by_test_id("accordion-panel-2")).to_be_visible()


@pytest.mark.regression
@pytest.mark.a11y
class TestComponentsAccessibility:
    def test_components_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)

    def test_modal_dialog_passes_a11y_when_open(self, page: Page) -> None:
        page.get_by_test_id("open-modal-btn").click()
        expect(page.get_by_test_id("modal-overlay")).to_be_visible()
        check_a11y(page)
