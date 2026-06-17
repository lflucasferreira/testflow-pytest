import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from support.auth import visit_authenticated
from support.helpers.fixtures import FIXTURES_ROOT, read_fixture


@pytest.fixture(autouse=True)
def activity_page(page: Page, api_request) -> None:
    visit_authenticated(page, api_request, "/web/activity.html")
    expect(page.get_by_test_id("page-activity")).to_be_attached()


@pytest.mark.regression
class TestActivity:
    @pytest.mark.smoke
    @pytest.mark.api
    def test_fetches_users_via_api_button(self, page: Page) -> None:
        with page.expect_response("**/api/users") as response_info:
            page.get_by_test_id("fetch-users-btn").click()
        response = response_info.value
        assert response.status == 200
        expect(page.get_by_test_id("api-result")).not_to_be_empty()

    def test_handles_slow_api_with_intercept_delay(self, page: Page) -> None:
        def slow_handler(route) -> None:
            time.sleep(1.5)
            route.continue_()

        page.route("**/api/slow**", slow_handler)
        with page.expect_response("**/api/slow**"):
            page.get_by_test_id("fetch-slow-btn").click()
        expect(page.get_by_test_id("api-result")).to_be_visible()

    def test_increments_and_decrements_counter(self, page: Page) -> None:
        page.get_by_test_id("counter-increment").click()
        page.get_by_test_id("counter-increment").click()
        expect(page.get_by_test_id("counter-value")).to_contain_text("2")
        page.get_by_test_id("counter-decrement").click()
        expect(page.get_by_test_id("counter-value")).to_contain_text("1")
        page.get_by_test_id("counter-reset").click()
        expect(page.get_by_test_id("counter-value")).to_contain_text("0")

    def test_starts_download_progress_simulation(self, page: Page) -> None:
        page.get_by_test_id("progress-start").click()
        expect(page.get_by_test_id("download-progress")).to_be_attached()

    def test_loads_dynamic_content_section(self, page: Page) -> None:
        page.get_by_test_id("load-dynamic-btn").click()
        expect(page.get_by_test_id("dynamic-content")).not_to_be_empty()

    def test_uses_mock_api_get_with_empty_users_fixture(self, page: Page) -> None:
        page.route(
            "**/api/users",
            lambda route: route.fulfill(json=read_fixture("users/empty-list.json")),
        )
        with page.expect_response("**/api/users"):
            page.get_by_test_id("fetch-users-btn").click()
        expect(page.get_by_test_id("api-result")).to_contain_text("Fetched 0 users")

    def test_read_fixture_exposes_countries_lookup_for_test_data(self) -> None:
        data = read_fixture("lookups/countries.json")
        codes = [country["code"] for country in data["countries"]]
        assert "CA" in codes

    def test_accepts_csv_file_via_drag_and_drop_on_drop_zone(self, page: Page) -> None:
        csv_path = FIXTURES_ROOT / "sample.csv"
        file_input = page.locator('[data-testid="drop-zone"] input[type="file"]')
        if file_input.count():
            file_input.set_input_files(str(csv_path))
        else:
            page.get_by_test_id("drop-zone").click()
        expect(page.get_by_test_id("page-activity")).to_be_visible()
