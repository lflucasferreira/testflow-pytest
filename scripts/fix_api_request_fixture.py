"""One-off: rename pytest request fixture conflicts to api_request."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
replacements = [
    ("request: APIRequestContext", "api_request: APIRequestContext"),
    ("login_via_api(page, request)", "login_via_api(page, api_request)"),
    ("visit_authenticated(page, request", "visit_authenticated(page, api_request"),
    ("get_auth_token(request)", "get_auth_token(api_request)"),
    ("fetch_auth_token(request", "fetch_auth_token(api_request"),
    ("def navigation_auth_token(request:", "def navigation_auth_token(api_request:"),
    ("return get_auth_token(request)", "return get_auth_token(api_request)"),
    ("response = request.", "response = api_request."),
    ("await request.", "await api_request."),
    ("page, request)", "page, api_request)"),
    ("page, request,", "page, api_request,"),
    ("lambda page, request:", "lambda page, api_request:"),
    ("patch_user_via_rules(request,", "patch_user_via_rules(api_request,"),
    ("get_users_via_profile(request,", "get_users_via_profile(api_request,"),
    ("execute_successful_patch_flow(request,", "execute_successful_patch_flow(api_request,"),
    ("poll_get_users_field(request,", "poll_get_users_field(api_request,"),
]

for path in ROOT.glob("tests/**/*.py"):
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"updated {path.relative_to(ROOT)}")
