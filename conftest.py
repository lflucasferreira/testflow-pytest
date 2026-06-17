import pytest
from playwright.sync_api import APIRequestContext

from support.auth import fetch_auth_token
from support.config import BASE_URL
from support.session_store import write_session, write_token_cache


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: smoke gate")
    config.addinivalue_line("markers", "regression: regression suite")
    config.addinivalue_line("markers", "critical: critical paths")
    config.addinivalue_line("markers", "a11y: accessibility")
    config.addinivalue_line("markers", "api: REST tests")
    config.addinivalue_line("markers", "visual: screenshot regression")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-snapshots",
        action="store_true",
        default=False,
        help="Update visual regression baselines in tests/visual/snapshots/",
    )


@pytest.fixture
def update_snapshots(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--update-snapshots"))


@pytest.fixture(scope="session", autouse=True)
def cache_auth_token(playwright) -> str:
    api_ctx = playwright.request.new_context(base_url=BASE_URL)
    try:
        session = fetch_auth_token(api_ctx)
        write_token_cache(session["token"], session["email"])
        write_session(session["email"], session["name"], session["token"])
        return session["token"]
    finally:
        api_ctx.dispose()


@pytest.fixture(scope="session")
def auth_token(cache_auth_token: str) -> str:
    return cache_auth_token


@pytest.fixture
def api_request(playwright) -> APIRequestContext:
    ctx = playwright.request.new_context(base_url=BASE_URL)
    yield ctx
    ctx.dispose()


def check_a11y(page, *, disabled_rules: list[str] | None = None) -> None:
    from axe_playwright_python.sync_playwright import Axe

    rules = disabled_rules or ["color-contrast"]
    axe = Axe()
    results = axe.run(page, options={"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa"]}})
    violations = results.response.get("violations", [])
    violations = [v for v in violations if v.get("id") not in rules]
    critical = [v for v in violations if v.get("impact") in ("critical", "serious")]
    assert not critical, f"A11y violations: {[v['id'] for v in critical]}"
