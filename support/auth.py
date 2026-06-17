import json

from playwright.sync_api import APIRequestContext, Page

from support.config import DEMO_EMAIL, DEMO_PASSWORD
from support.session_store import read_cached_token


def fetch_auth_token(
    api_request: APIRequestContext,
    email: str = DEMO_EMAIL,
    password: str = DEMO_PASSWORD,
) -> dict[str, str]:
    response = api_request.post(
        "/api/auth/login",
        data={"email": email, "password": password},
    )
    if response.status != 200:
        raise RuntimeError(
            f"Auth login failed with status {response.status}: {response.text()}"
        )
    body = response.json()
    token = body.get("token")
    if not token:
        raise RuntimeError(
            f"Token not found in auth response (status {response.status}): {body}"
        )
    return {
        "email": email,
        "name": body.get("user", {}).get("name", "Demo User"),
        "token": token,
    }


def _seed_session_storage(page: Page, session: dict[str, str]) -> None:
    page.evaluate(
        """(auth) => {
            sessionStorage.setItem('sandbox-auth', JSON.stringify(auth));
            sessionStorage.setItem('sandbox-token', auth.token);
        }""",
        session,
    )


def inject_auth(page: Page, session: dict[str, str]) -> None:
    payload = json.dumps(session)
    page.context.add_init_script(
        f"""() => {{
            const auth = {payload};
            sessionStorage.setItem('sandbox-auth', JSON.stringify(auth));
            sessionStorage.setItem('sandbox-token', auth.token);
        }}"""
    )


def login_via_api(
    page: Page,
    api_request: APIRequestContext,
    email: str = DEMO_EMAIL,
    password: str = DEMO_PASSWORD,
) -> None:
    session = fetch_auth_token(api_request, email, password)
    inject_auth(page, session)
    page.goto("/web/login.html", wait_until="domcontentloaded")
    _seed_session_storage(page, session)
    page.goto("/web/dashboard.html")
    page.get_by_test_id("page-dashboard").wait_for()


def visit_authenticated(page: Page, api_request: APIRequestContext, path: str) -> None:
    session = fetch_auth_token(api_request)
    inject_auth(page, session)
    page.goto("/web/login.html", wait_until="domcontentloaded")
    _seed_session_storage(page, session)
    page.goto(path, wait_until="domcontentloaded")


def login_via_ui(
    page: Page,
    email: str = DEMO_EMAIL,
    password: str = DEMO_PASSWORD,
) -> None:
    page.goto("/web/login.html")
    page.get_by_test_id("login-email").fill(email)
    page.get_by_test_id("login-password").fill(password)
    page.get_by_test_id("login-submit").click()
    page.get_by_test_id("page-dashboard").wait_for()


def get_auth_token(api_request: APIRequestContext) -> str:
    cached = read_cached_token()
    if cached:
        return cached
    return fetch_auth_token(api_request)["token"]


def visit_with_token(
    page: Page,
    path: str,
    token: str,
    email: str = DEMO_EMAIL,
) -> None:
    session = {"email": email, "name": "Demo User", "token": token}
    inject_auth(page, session)
    page.goto("/web/login.html", wait_until="domcontentloaded")
    _seed_session_storage(page, session)
    page.goto(path)
