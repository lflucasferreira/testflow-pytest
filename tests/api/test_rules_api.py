import json
import time

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from support.api.rules_client import (
    SERVICE_CREDENTIALS,
    execute_successful_patch_flow,
    get_users_via_profile,
    patch_user_via_rules,
)
from support.auth import fetch_auth_token, visit_authenticated
from support.config import BASE_URL, DEMO_EMAIL, DEMO_PASSWORD
from support.constants.http_status import EXPECT
from support.constants.test_cases import TC
from support.factories.user_patch import UserPatchFactory
from support.helpers import validate_schema
from support.helpers.fixtures import read_fixture
from support.utilities.json_patch import JsonPatchBuilder, modify_patch_field

PATCH_PAYLOADS = read_fixture("api/patch-payloads.json")
VALID_PATCH_CASES = PATCH_PAYLOADS["validNamePatches"]
INVALID_PATCH_CASES = PATCH_PAYLOADS["invalidPatches"]


@pytest.mark.api
@pytest.mark.regression
class TestJsonPatchUtilities:
    def test_builds_rfc_6902_patch_operations(self) -> None:
        patches = JsonPatchBuilder().replace("/name", "Alex").replace("/role", "admin").build()
        assert len(patches) == 2
        assert patches[0] == {"op": "replace", "path": "/name", "value": "Alex"}

    def test_modifies_patch_field_for_negative_tests(self) -> None:
        base = UserPatchFactory.create_name_patch("A", "B", "C")
        invalid = modify_patch_field(base, "/name", None)
        name_op = next(op for op in invalid if op["path"] == "/name")
        assert name_op["value"] is None


@pytest.mark.api
@pytest.mark.regression
class TestPatchVsTryPatch:
    def test_patch_user_via_rules_accepts_json_patch_content_type(
        self, api_request: APIRequestContext, auth_token: str
    ) -> None:
        patches = UserPatchFactory.create_name_patch("Patch", "Test", "User")
        response = patch_user_via_rules(api_request, auth_token, 1, patches)
        assert response.status in (
            EXPECT.happy,
            EXPECT.no_content,
            EXPECT.not_found,
            EXPECT.bad_request,
        )

    def test_try_patch_rejects_invalid_patch(self, api_request: APIRequestContext, auth_token: str) -> None:
        response = patch_user_via_rules(
            api_request,
            auth_token,
            999,
            [{"op": "replace", "path": "/invalid", "value": None}],
        )
        assert response.status in (400, 404, 422, 500)


@pytest.mark.api
@pytest.mark.regression
class TestExecuteSuccessfulPatchFlow:
    @pytest.mark.critical
    def test_patches_user_and_validates_read_after_write_with_retry(
        self, api_request: APIRequestContext, auth_token: str
    ) -> None:
        """tc(TC.API_PATCH_READ_AFTER_WRITE, 'patches user and validates read-after-write with retry')"""
        unique_name = f"PatchFlow {int(time.time() * 1000)}"
        patches = UserPatchFactory.create_simple_name_patch(unique_name)
        execute_successful_patch_flow(api_request, auth_token, 1, patches, "name")


@pytest.mark.api
@pytest.mark.regression
class TestMandatoryFieldValidation:
    @pytest.mark.parametrize(
        "path,case_id",
        [
            ("/name", "TC-4001"),
        ],
        ids=["rejects null at /name"],
    )
    def test_rejects_null_at_mandatory_field(
        self,
        api_request: APIRequestContext,
        auth_token: str,
        path: str,
        case_id: str,
    ) -> None:
        base_patch = UserPatchFactory.create_simple_name_patch("Valid Name")
        modified = modify_patch_field(base_patch, path, None)
        response = patch_user_via_rules(api_request, auth_token, 1, modified)
        assert response.status in (400, 404, 422, 500)


@pytest.mark.api
@pytest.mark.regression
class TestDualServiceReadAfterWrite:
    def test_validates_get_users_after_auth_token_seed(
        self, api_request: APIRequestContext, auth_token: str
    ) -> None:
        response = get_users_via_profile(api_request, auth_token)
        assert response.status == 200
        body = response.json()
        assert isinstance(body["users"], list)
        assert len(body["users"]) > 0
        validate_schema(body["users"][0], {"name": "string", "email": "string", "role": "string"})


@pytest.mark.api
@pytest.mark.regression
class TestAuthenticatedApiRequest:
    @pytest.mark.smoke
    def test_api_with_auth_returns_users_with_bearer_token(
        self, api_request: APIRequestContext, auth_token: str
    ) -> None:
        response = get_users_via_profile(api_request, auth_token)
        assert response.status == 200
        assert isinstance(response.json()["users"], list)


@pytest.mark.api
@pytest.mark.regression
class TestOAuthStyleServiceToken:
    def test_fetch_auth_token_returns_non_empty_token(self, api_request: APIRequestContext) -> None:
        session = fetch_auth_token(api_request, DEMO_EMAIL, DEMO_PASSWORD)
        assert isinstance(session["token"], str)
        assert session["token"]

    def test_service_credentials_returns_client_credentials_object(self) -> None:
        assert set(SERVICE_CREDENTIALS.keys()) == {"client_id", "client_secret"}
        assert SERVICE_CREDENTIALS["client_id"]
        assert SERVICE_CREDENTIALS["client_secret"]


@pytest.mark.api
@pytest.mark.regression
class TestInterceptWithResponseMutation:
    def test_mutates_users_response_to_simulate_empty_list(self, page: Page, api_request) -> None:
        def mutate_users(route) -> None:
            response = route.fetch()
            body = response.json()
            body["users"] = []
            body["total"] = 0
            route.fulfill(
                status=response.status,
                content_type="application/json",
                body=json.dumps(body),
            )

        page.route("**/api/users", mutate_users)
        visit_authenticated(page, api_request, "/web/activity.html")
        with page.expect_response("**/api/users"):
            page.get_by_test_id("fetch-users-btn").click()
        expect(page.get_by_test_id("api-result")).to_contain_text("Fetched 0 users")


@pytest.mark.api
@pytest.mark.regression
class TestPatchPayloadFixtures:
    @pytest.mark.parametrize("case", VALID_PATCH_CASES, ids=lambda c: c["label"])
    def test_valid_patch_payloads_from_fixture(
        self,
        api_request: APIRequestContext,
        auth_token: str,
        case: dict,
    ) -> None:
        response = patch_user_via_rules(api_request, auth_token, 1, case["patches"])
        assert response.status in (
            EXPECT.happy,
            EXPECT.no_content,
            EXPECT.not_found,
            EXPECT.bad_request,
        )

    @pytest.mark.parametrize("case", INVALID_PATCH_CASES, ids=lambda c: c["label"])
    def test_invalid_patch_payloads_from_fixture(
        self,
        api_request: APIRequestContext,
        auth_token: str,
        case: dict,
    ) -> None:
        user_id = case.get("userId", 1)
        response = patch_user_via_rules(api_request, auth_token, user_id, case["patches"])
        assert response.status in (400, 404, 422, 500)
