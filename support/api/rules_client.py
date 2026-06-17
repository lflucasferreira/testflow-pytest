from playwright.sync_api import APIRequestContext, APIResponse

from support.config import SERVICE_CLIENT_ID, SERVICE_CLIENT_SECRET
from support.constants.http_status import EXPECT
from support.utilities.json_patch import extract_patch_values
from support.utilities.retry import poll_get_users_field

SERVICE_CREDENTIALS = {
    "client_id": SERVICE_CLIENT_ID,
    "client_secret": SERVICE_CLIENT_SECRET,
}


def patch_user_via_rules(
    api_request: APIRequestContext,
    auth_token: str,
    user_id: int,
    patches: list[dict],
) -> APIResponse:
    return api_request.patch(
        f"/api/users/{user_id}",
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json-patch+json",
        },
        data=patches,
    )


def get_users_via_profile(api_request: APIRequestContext, auth_token: str) -> APIResponse:
    return api_request.get(
        "/api/users",
        headers={"Authorization": f"Bearer {auth_token}"},
    )


def execute_successful_patch_flow(
    api_request: APIRequestContext,
    auth_token: str,
    user_id: int,
    patches: list[dict],
    expected_field: str,
) -> None:
    expected_values = extract_patch_values(patches)
    response = patch_user_via_rules(api_request, auth_token, user_id, patches)

    if response.status in (EXPECT.happy, EXPECT.no_content):
        expected_value = expected_values.get(expected_field)
        if expected_value is not None:
            match = poll_get_users_field(
                api_request,
                expected_field,
                str(expected_value),
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            assert match.get(expected_field) == expected_value
        return

    assert response.status in (
        EXPECT.not_found,
        EXPECT.bad_request,
        EXPECT.method_not_allowed,
        EXPECT.validation_error,
    )
