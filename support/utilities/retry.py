import time
from typing import Any

from playwright.sync_api import APIRequestContext


def poll_get_users_field(
    api_request: APIRequestContext,
    field: str,
    expected_value: str,
    *,
    headers: dict[str, str] | None = None,
    max_attempts: int = 5,
    delay_ms: int = 400,
) -> dict[str, Any]:
    last_match: dict[str, Any] = {}
    for _ in range(max_attempts):
        response = api_request.get("/api/users", headers=headers or {})
        body = response.json()
        for user in body.get("users", []):
            if str(user.get(field)) == expected_value:
                return user
            last_match = user
        time.sleep(delay_ms / 1000)
    return last_match
