import re
import time

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from support.config import BASE_URL, DEMO_EMAIL, DEMO_PASSWORD


ENDPOINT = "/api/auth/login"
VALID = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}


@pytest.fixture(scope="class")
def valid_login_response(playwright) -> dict:
    ctx = playwright.request.new_context(base_url=BASE_URL)
    try:
        start = time.monotonic()
        response = ctx.post(f"{BASE_URL}{ENDPOINT}", data=VALID)
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "status": response.status,
            "headers": response.headers,
            "body": response.json(),
            "duration_ms": elapsed_ms,
        }
    finally:
        ctx.dispose()


@pytest.mark.api
@pytest.mark.regression
class TestAuthLoginValidCredentials:
    @pytest.mark.smoke
    def test_returns_status_200(self, valid_login_response: dict) -> None:
        assert valid_login_response["status"] == 200

    def test_content_type_is_application_json(self, valid_login_response: dict) -> None:
        assert "application/json" in valid_login_response["headers"].get("content-type", "")

    def test_responds_within_2000ms(self, api_request: APIRequestContext) -> None:
        start = time.monotonic()
        response = api_request.post(f"{BASE_URL}{ENDPOINT}", data=VALID)
        elapsed_ms = (time.monotonic() - start) * 1000
        assert response.status == 200
        assert elapsed_ms < 2000

    @pytest.mark.smoke
    @pytest.mark.critical
    def test_body_has_token_as_non_empty_string(self, valid_login_response: dict) -> None:
        token = valid_login_response["body"]["token"]
        assert isinstance(token, str)
        assert token

    def test_body_has_user_object_or_token_only_response(self, valid_login_response: dict) -> None:
        body = valid_login_response["body"]
        if body.get("user"):
            assert isinstance(body["user"].get("email"), str)
            assert body["user"]["email"]
        else:
            assert isinstance(body["token"], str)
            assert body["token"]

    def test_user_email_matches_the_login_email_when_user_is_present(
        self, valid_login_response: dict
    ) -> None:
        body = valid_login_response["body"]
        if body.get("user") and body["user"].get("email"):
            assert body["user"]["email"] == VALID["email"]

    def test_token_can_authenticate_a_subsequent_request(
        self, api_request: APIRequestContext, valid_login_response: dict
    ) -> None:
        token = valid_login_response["body"]["token"]
        response = api_request.get(
            f"{BASE_URL}/api/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status == 200


@pytest.mark.api
@pytest.mark.regression
class TestAuthLoginInvalidCredentials:
    def test_returns_401_for_wrong_password(self, api_request: APIRequestContext) -> None:
        response = api_request.post(
            f"{BASE_URL}{ENDPOINT}",
            data={"email": VALID["email"], "password": "wrongpassword"},
        )
        assert response.status == 401

    def test_returns_401_for_unknown_email(self, api_request: APIRequestContext) -> None:
        response = api_request.post(
            f"{BASE_URL}{ENDPOINT}",
            data={"email": "nobody@example.com", "password": VALID["password"]},
        )
        assert response.status == 401

    def test_error_response_has_a_non_empty_error_or_message_field(
        self, api_request: APIRequestContext
    ) -> None:
        response = api_request.post(
            f"{BASE_URL}{ENDPOINT}",
            data={"email": VALID["email"], "password": "wrong"},
        )
        body = response.json()
        err_text = body.get("message") or (body.get("error") or {}).get("message")
        assert isinstance(err_text, str)
        assert err_text


@pytest.mark.api
@pytest.mark.regression
class TestAuthLoginMalformedRequest:
    def test_returns_4xx_when_body_is_empty(self, api_request: APIRequestContext) -> None:
        response = api_request.post(f"{BASE_URL}{ENDPOINT}", data={})
        assert 400 <= response.status <= 422

    def test_returns_4xx_when_email_is_missing(self, api_request: APIRequestContext) -> None:
        response = api_request.post(f"{BASE_URL}{ENDPOINT}", data={"password": VALID["password"]})
        assert 400 <= response.status <= 422

    def test_returns_4xx_when_password_is_missing(self, api_request: APIRequestContext) -> None:
        response = api_request.post(f"{BASE_URL}{ENDPOINT}", data={"email": VALID["email"]})
        assert 400 <= response.status <= 422


@pytest.mark.api
@pytest.mark.regression
class TestAuthLoginInterceptFlow:
    def test_api_toggle_sends_post_with_correct_payload_and_token_response(
        self, page: Page
    ) -> None:
        captured: dict = {}

        def handle_route(route) -> None:
            post_data = route.request.post_data_json or {}
            captured["email"] = post_data.get("email")
            route.continue_()

        page.route(f"**{ENDPOINT}", handle_route)
        page.goto("/web/login.html")
        page.get_by_test_id("login-use-api").evaluate("el => el.click()")
        page.get_by_test_id("login-email").fill(VALID["email"])
        page.get_by_test_id("login-password").fill(VALID["password"])

        with page.expect_response(f"**{ENDPOINT}") as response_info:
            page.get_by_test_id("login-submit").click()

        response = response_info.value
        assert captured.get("email") == VALID["email"]
        assert response.status == 200
        body = response.json()
        assert isinstance(body.get("token"), str)
        assert body["token"]

    def test_stubbed_500_keeps_user_on_login_page_without_crashing(self, page: Page) -> None:
        page.route(
            f"**{ENDPOINT}",
            lambda route: route.fulfill(
                status=500,
                content_type="application/json",
                body='{"error":"Internal Server Error"}',
            ),
        )
        page.goto("/web/login.html")
        page.get_by_test_id("login-use-api").evaluate("el => el.click()")
        page.get_by_test_id("login-email").fill(VALID["email"])
        page.get_by_test_id("login-password").fill(VALID["password"])

        with page.expect_response(f"**{ENDPOINT}"):
            page.get_by_test_id("login-submit").click()

        expect(page).to_have_url(re.compile(r"/web/login\.html"))
        result = page.get_by_test_id("login-result")
        if result.is_visible():
            expect(result).not_to_be_empty()
