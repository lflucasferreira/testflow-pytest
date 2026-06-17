import re

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from support.auth import get_auth_token, login_via_api, visit_with_token
from support.config import DEMO_EMAIL, DEMO_PASSWORD
from support.constants.test_cases import TC, tc

PAGES = [
    {
        "path": "/web/dashboard.html",
        "test_id": "page-dashboard",
        "title": "Dashboard",
        "tc_id": TC.SMOKE_DASHBOARD,
    },
    {
        "path": "/web/team.html",
        "test_id": "page-team",
        "title": "Team",
        "tc_id": TC.SMOKE_TEAM,
    },
    {
        "path": "/web/settings.html",
        "test_id": "page-settings",
        "title": "Settings",
        "tc_id": TC.SMOKE_SETTINGS,
    },
    {
        "path": "/web/components.html",
        "test_id": "page-components",
        "title": "Components",
        "tc_id": TC.SMOKE_COMPONENTS,
    },
    {
        "path": "/web/activity.html",
        "test_id": "page-activity",
        "title": "Activity",
        "tc_id": TC.SMOKE_ACTIVITY,
    },
    {
        "path": "/web/advanced.html",
        "test_id": "page-advanced",
        "title": "Advanced",
        "tc_id": TC.SMOKE_ADVANCED,
    },
    {
        "path": "/web/wizard.html",
        "test_id": "page-wizard",
        "title": "Wizard",
        "tc_id": TC.SMOKE_WIZARD,
    },
    {
        "path": "/web/states.html",
        "test_id": "page-states",
        "title": "UI States",
        "tc_id": TC.SMOKE_STATES,
    },
]


@pytest.fixture(scope="module")
def navigation_auth_token(auth_token: str) -> str:
    return auth_token


@pytest.mark.smoke
@pytest.mark.regression
class TestPageNavigation:
    @pytest.mark.parametrize(
        "path,test_id,title,tc_id",
        [(p["path"], p["test_id"], p["title"], p["tc_id"]) for p in PAGES],
        ids=[tc(p["tc_id"], f"{p['title']} page loads without error") for p in PAGES],
    )
    def test_page_loads_without_error(
        self,
        page: Page,
        navigation_auth_token: str,
        path: str,
        test_id: str,
        title: str,
        tc_id: str,
    ) -> None:
        visit_with_token(page, path, navigation_auth_token)
        expect(page.get_by_test_id(test_id)).to_be_visible()
        expect(page).to_have_title(re.compile(title))


@pytest.mark.smoke
@pytest.mark.regression
class TestSidebarNavigation:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, api_request: APIRequestContext) -> None:
        login_via_api(page, api_request)
        expect(page.get_by_test_id("page-dashboard")).to_be_visible()

    @pytest.mark.smoke
    @pytest.mark.critical
    def test_tc0010_navigates_from_dashboard_to_team_via_sidebar(self, page: Page) -> None:
        page.get_by_test_id("nav-team").click()
        expect(page.get_by_test_id("page-team")).to_be_visible()
        expect(page).to_have_url(re.compile(r"/web/team\.html"))

    @pytest.mark.smoke
    def test_tc0011_highlights_the_active_nav_link(self, page: Page) -> None:
        expect(page.get_by_test_id("nav-dashboard")).to_have_class(re.compile(r"active"))


@pytest.mark.smoke
class TestLogout:
    def test_tc0012_logout_clears_session_and_redirects_to_login(self, page: Page) -> None:
        page.goto("/web/login.html")
        page.get_by_test_id("login-email").fill(DEMO_EMAIL)
        page.get_by_test_id("login-password").fill(DEMO_PASSWORD)
        page.get_by_test_id("login-submit").click()
        page.get_by_test_id("page-dashboard").wait_for()

        page.get_by_test_id("nav-logout").click()
        expect(page).to_have_url(re.compile(r"/web/index\.html"))
        assert page.evaluate("() => sessionStorage.getItem('sandbox-auth')") is None


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.api
class TestApiHealth:
    @pytest.mark.smoke
    @pytest.mark.api
    def test_tc0020_get_health_returns_200(self, api_request: APIRequestContext) -> None:
        response = api_request.get("/health")
        assert response.status == 200

    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.critical
    def test_tc0021_post_auth_login_returns_token(self, api_request: APIRequestContext) -> None:
        response = api_request.post(
            "/api/auth/login",
            data={"email": DEMO_EMAIL, "password": DEMO_PASSWORD},
        )
        assert response.status == 200
        body = response.json()
        assert body["token"]
        assert body["user"]["email"] == DEMO_EMAIL

    @pytest.mark.smoke
    @pytest.mark.api
    def test_tc0022_get_users_returns_user_array(self, api_request: APIRequestContext) -> None:
        response = api_request.get("/api/users")
        assert response.status == 200
        body = response.json()
        assert isinstance(body["users"], list)
        assert len(body["users"]) > 0

    def test_tc0023_get_errors_404_returns_404_status(self, api_request: APIRequestContext) -> None:
        response = api_request.get("/api/errors/404")
        assert response.status == 404

    def test_tc0024_get_errors_422_returns_422_status(self, api_request: APIRequestContext) -> None:
        response = api_request.get("/api/errors/422")
        assert response.status == 422
