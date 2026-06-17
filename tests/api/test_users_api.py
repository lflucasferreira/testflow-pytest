import re
import time

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from support.auth import visit_authenticated
from support.config import BASE_URL
from support.helpers import validate_schema
from support.helpers.fixtures import read_fixture


@pytest.fixture(scope="class")
def users_list_response(playwright) -> dict:
    ctx = playwright.request.new_context(base_url=BASE_URL)
    try:
        start = time.monotonic()
        response = ctx.get(f"{BASE_URL}/api/users")
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "status": response.status,
            "body": response.json(),
            "duration_ms": elapsed_ms,
        }
    finally:
        ctx.dispose()


@pytest.mark.api
@pytest.mark.regression
class TestGetUsers:
    @pytest.mark.smoke
    def test_returns_status_200(self, users_list_response: dict) -> None:
        assert users_list_response["status"] == 200

    def test_responds_within_2000ms(self, users_list_response: dict) -> None:
        assert users_list_response["duration_ms"] < 2000

    def test_body_has_a_users_array(self, users_list_response: dict) -> None:
        users = users_list_response["body"]["users"]
        assert isinstance(users, list)
        assert len(users) > 0

    def test_each_user_matches_json_schema(self, users_list_response: dict) -> None:
        for user in users_list_response["body"]["users"]:
            validate_schema(user, {"name": "string", "email": "string", "role": "string"})

    def test_all_emails_are_valid_format(self, users_list_response: dict) -> None:
        email_regex = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
        for user in users_list_response["body"]["users"]:
            assert email_regex.match(user["email"])


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
class TestHealth:
    @pytest.mark.smoke
    def test_returns_status_200(self, api_request: APIRequestContext) -> None:
        response = api_request.get(f"{BASE_URL}/health")
        assert response.status == 200

    def test_responds_within_1000ms(self, api_request: APIRequestContext) -> None:
        start = time.monotonic()
        response = api_request.get(f"{BASE_URL}/health")
        elapsed_ms = (time.monotonic() - start) * 1000
        assert response.status == 200
        assert elapsed_ms < 1000


@pytest.mark.api
@pytest.mark.regression
class TestErrorSimulationEndpoints:
    def test_get_errors_404_returns_404(self, api_request: APIRequestContext) -> None:
        response = api_request.get(f"{BASE_URL}/api/errors/404")
        assert response.status == 404

    def test_get_errors_422_returns_422(self, api_request: APIRequestContext) -> None:
        response = api_request.get(f"{BASE_URL}/api/errors/422")
        assert response.status == 422

    def test_404_response_has_a_non_empty_error_or_message_field(
        self, api_request: APIRequestContext
    ) -> None:
        body = api_request.get("/api/errors/404").json()
        err_text = body.get("message") or (body.get("error") or {}).get("message")
        assert isinstance(err_text, str)
        assert err_text

    def test_422_response_has_a_non_empty_error_or_message_field(
        self, api_request: APIRequestContext
    ) -> None:
        body = api_request.get("/api/errors/422").json()
        err_text = body.get("message") or (body.get("error") or {}).get("message")
        assert isinstance(err_text, str)
        assert err_text


@pytest.mark.api
@pytest.mark.regression
class TestFixtureInterceptOnActivityPage:
    @pytest.fixture(autouse=True)
    def activity_page(self, page: Page, api_request) -> None:
        visit_authenticated(page, api_request, "/web/activity.html")

    def test_mock_api_get_serves_empty_users_fixture_on_fetch(self, page: Page) -> None:
        page.route(
            "**/api/users",
            lambda route: route.fulfill(json=read_fixture("users/empty-list.json")),
        )
        with page.expect_response("**/api/users"):
            page.get_by_test_id("fetch-users-btn").click()
        expect(page.get_by_test_id("api-result")).to_contain_text("Fetched 0 users")

    def test_read_fixture_loads_countries_lookup(self) -> None:
        data = read_fixture("lookups/countries.json")
        assert isinstance(data["countries"], list)
        assert len(data["countries"]) > 0
        assert "code" in data["countries"][0]
        assert "name" in data["countries"][0]
