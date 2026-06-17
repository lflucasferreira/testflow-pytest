import pytest
from playwright.sync_api import Page, expect

from support.auth import login_via_api, visit_authenticated
from support.constants.test_cases import TC
from support.helpers.visual import assert_locator_screenshot


def _wait_for_fonts(page: Page) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("() => document.fonts.ready")


@pytest.mark.visual
@pytest.mark.regression
class TestVisualSnapshots:
    @pytest.mark.parametrize(
        "case_id,title,snapshot_name,setup,locator_test_id",
        [
            (
                TC.VISUAL_LOGIN,
                "login form baseline",
                "login-form",
                lambda page, api_request: page.goto("/web/login.html", wait_until="networkidle"),
                "login-card",
            ),
            (
                TC.VISUAL_DASHBOARD,
                "sidebar navigation baseline",
                "sidebar-nav",
                lambda page, api_request: login_via_api(page, api_request),
                "site-sidebar",
            ),
            (
                TC.VISUAL_COMPONENTS,
                "components primary buttons baseline",
                "components-buttons",
                lambda page, api_request: visit_authenticated(
                    page, api_request, "/web/components.html"
                ),
                "section-buttons",
            ),
        ],
        ids=[TC.VISUAL_LOGIN, TC.VISUAL_DASHBOARD, TC.VISUAL_COMPONENTS],
    )
    def test_visual_baseline(
        self,
        page: Page,
        api_request,
        browser_name: str,
        update_snapshots: bool,
        case_id: str,
        title: str,
        snapshot_name: str,
        setup,
        locator_test_id: str,
    ) -> None:
        setup(page, api_request)

        target = page.get_by_test_id(locator_test_id)
        expect(target).to_be_visible()
        _wait_for_fonts(page)

        assert_locator_screenshot(
            target,
            snapshot_name,
            browser_name=browser_name,
            update=update_snapshots,
        )
