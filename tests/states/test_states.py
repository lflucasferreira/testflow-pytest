import pytest
from playwright.sync_api import Page, expect

from conftest import check_a11y
from support.auth import visit_authenticated


@pytest.fixture(autouse=True)
def states_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/states.html")
    expect(page.get_by_test_id("page-states")).to_be_attached()


@pytest.mark.regression
class TestSkeletonLoading:
    @pytest.mark.smoke
    def test_shows_idle_message_before_load(self, page: Page) -> None:
        expect(page.get_by_test_id("skeleton-idle")).to_contain_text("Load cards")

    def test_loads_metric_cards_after_skeleton_delay(self, page: Page) -> None:
        page.get_by_test_id("skeleton-trigger").click()
        expect(page.get_by_test_id("loaded-card")).to_have_count(4, timeout=5000)

    def test_resets_skeleton_section(self, page: Page) -> None:
        page.get_by_test_id("skeleton-trigger").click()
        expect(page.get_by_test_id("loaded-card").first).to_be_visible(timeout=5000)
        page.get_by_test_id("skeleton-reset").click()
        expect(page.get_by_test_id("skeleton-idle")).to_be_visible()


@pytest.mark.regression
class TestErrorAndSuccessStates:
    def test_shows_error_state_on_failed_fetch(self, page: Page) -> None:
        page.get_by_test_id("error-trigger").click()
        error = page.get_by_test_id("error-state")
        expect(error).to_be_visible()
        expect(error).to_contain_text("Request failed")

    def test_shows_success_state_on_successful_fetch(self, page: Page) -> None:
        page.get_by_test_id("success-trigger").click()
        success = page.get_by_test_id("success-state")
        expect(success).to_be_visible()
        expect(success).to_contain_text("succeeded")


@pytest.mark.regression
class TestEmptyAndPartialStates:
    def test_renders_empty_state_when_search_has_no_matches(self, page: Page) -> None:
        page.get_by_test_id("empty-search").fill("xyzno match")
        expect(page.get_by_test_id("empty-state")).to_be_visible()
        expect(page.get_by_test_id("result-list")).not_to_be_attached()

    def test_loads_partial_grid_with_mixed_card_statuses(self, page: Page) -> None:
        page.get_by_test_id("partial-trigger").click()
        expect(page.locator('[data-testid^="partial-card-"]')).to_have_count(6)


@pytest.mark.regression
@pytest.mark.a11y
class TestStatesAccessibility:
    def test_states_page_has_no_critical_a11y_violations(self, page: Page) -> None:
        check_a11y(page)
