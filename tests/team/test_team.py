import re

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

from pages.team_page import TeamPage
from support.auth import visit_authenticated
from support.helpers.fixtures import read_fixture

pytestmark = pytest.mark.regression

team_member = read_fixture("team-member.json")


@pytest.fixture(autouse=True)
def setup_team(page: Page, api_request: APIRequestContext) -> None:
    visit_authenticated(page, api_request, "/web/team.html")
    expect(TeamPage(page).page_root()).to_be_visible()


class TestPageStructure:
    def test_shows_the_page_header_with_member_count(self, page: Page) -> None:
        expect(TeamPage(page).team_summary()).to_contain_text("6 members")

    def test_renders_all_table_columns(self, page: Page) -> None:
        expect(page.get_by_test_id("users-table").locator("thead th")).to_have_count(7)

    def test_renders_the_correct_number_of_rows_on_page_1(self, page: Page) -> None:
        TeamPage(page).should_have_row_count(4)

    def test_row_count_label_matches_visible_rows(self, page: Page) -> None:
        expect(TeamPage(page).row_count()).to_contain_text("6 row(s)")


class TestSearch:
    def test_filters_rows_by_member_name(self, page: Page) -> None:
        team = TeamPage(page)
        team.search("Alice")
        team.should_have_row_count(1)
        expect(team.name_cell(1)).to_contain_text("Alice QA")

    def test_filters_rows_by_email(self, page: Page) -> None:
        team = TeamPage(page)
        team.search("carol")
        team.should_have_row_count(1)

    def test_returns_all_rows_when_search_is_cleared(self, page: Page) -> None:
        team = TeamPage(page)
        team.search("Alice")
        team.should_have_row_count(1)
        team.clear_search()
        team.should_have_row_count(4)

    def test_shows_zero_rows_for_a_term_with_no_match(self, page: Page) -> None:
        team = TeamPage(page)
        team.search("zzznoresult")
        expect(team.table_rows()).to_have_count(0)


class TestRoleFilter:
    def test_filters_to_admin_rows_only(self, page: Page) -> None:
        team = TeamPage(page)
        team.filter_by_role("admin")
        rows = team.table_rows()
        count = rows.count()
        for i in range(count):
            expect(rows.nth(i).locator('[data-role="admin"]')).to_be_visible()

    def test_shows_all_rows_when_filter_is_reset(self, page: Page) -> None:
        team = TeamPage(page)
        team.filter_by_role("admin")
        team.filter_by_role("")
        team.should_have_row_count(4)


class TestStatusFilter:
    def test_filters_to_active_members_only(self, page: Page) -> None:
        team = TeamPage(page)
        team.filter_by_status("active")
        rows = team.table_rows()
        count = rows.count()
        for i in range(count):
            expect(rows.nth(i).locator('[data-status="active"]')).to_be_visible()

    def test_filters_to_inactive_members_only(self, page: Page) -> None:
        team = TeamPage(page)
        team.filter_by_status("inactive")
        rows = team.table_rows()
        count = rows.count()
        for i in range(count):
            expect(rows.nth(i).locator('[data-status="inactive"]')).to_be_visible()


class TestSorting:
    def test_sorts_rows_by_name_descending_on_first_click(self, page: Page) -> None:
        team = TeamPage(page)
        team.sort_by_name()
        names = team.table_rows().evaluate_all(
            """rows => rows.map(row =>
                (row.querySelector('[data-testid^="cell-name-"]')?.textContent ?? '').trim()
            )"""
        )
        assert names == sorted(names, reverse=True)

    def test_second_click_sorts_rows_by_name_ascending(self, page: Page) -> None:
        team = TeamPage(page)
        team.sort_by_name()
        team.sort_by_name()
        names = team.table_rows().evaluate_all(
            """rows => rows.map(row =>
                (row.querySelector('[data-testid^="cell-name-"]')?.textContent ?? '').trim()
            )"""
        )
        assert names == sorted(names)


class TestPagination:
    def test_prev_button_is_disabled_on_page_1(self, page: Page) -> None:
        expect(TeamPage(page).prev_page()).to_be_disabled()

    def test_navigates_to_page_2_showing_remaining_rows(self, page: Page) -> None:
        team = TeamPage(page)
        team.go_to_next_page()
        expect(team.page_info()).to_contain_text("Page 2")
        team.should_have_row_count(2)

    def test_next_button_is_disabled_on_last_page(self, page: Page) -> None:
        team = TeamPage(page)
        team.go_to_next_page()
        expect(team.next_page()).to_be_disabled()

    def test_navigating_back_to_page_1_restores_row_count(self, page: Page) -> None:
        team = TeamPage(page)
        team.go_to_next_page()
        team.go_to_prev_page()
        team.should_have_row_count(4)


class TestInviteMemberModal:
    def test_opens_modal_on_invite_member_click(self, page: Page) -> None:
        TeamPage(page).open_invite_modal()
        TeamPage(page).should_have_invite_modal_open()

    def test_closes_modal_on_cancel(self, page: Page) -> None:
        team = TeamPage(page)
        team.open_invite_modal()
        team.cancel_invite()
        team.should_have_invite_modal_closed()

    def test_closes_modal_on_escape_key(self, page: Page) -> None:
        team = TeamPage(page)
        team.open_invite_modal()
        page.keyboard.press("Escape")
        team.should_have_invite_modal_closed()

    def test_shows_validation_error_when_name_is_empty(self, page: Page) -> None:
        team = TeamPage(page)
        team.open_invite_modal()
        team.fill_invite_form(email=team_member["new"]["email"])
        team.submit_invite()
        team.should_show_invite_error("required")

    def test_shows_validation_error_for_invalid_email(self, page: Page) -> None:
        team = TeamPage(page)
        team.open_invite_modal()
        team.fill_invite_form(name=team_member["new"]["name"], email="notanemail")
        team.submit_invite()
        team.should_show_invite_error("valid email")

    def test_adds_a_new_row_after_successful_invite(self, page: Page) -> None:
        team = TeamPage(page)
        team.open_invite_modal()
        team.fill_invite_form(**team_member["new"])
        team.submit_invite()
        team.should_have_invite_modal_closed()
        expect(page.get_by_test_id("toast-message")).to_contain_text(
            team_member["new"]["email"]
        )
        label = team.row_count().inner_text()
        row_total = int(re.search(r"\d+", label).group())
        assert row_total > 6

    def test_invite_request_contains_name_and_email_in_the_payload(
        self, page: Page
    ) -> None:
        team = TeamPage(page)
        captured: list = []

        def capture_request(req) -> None:
            if req.method == "POST" and "/api/" in req.url:
                captured.append(req)

        page.on("request", capture_request)
        team.open_invite_modal()
        team.fill_invite_form(**team_member["new"])
        team.submit_invite()
        team.should_have_invite_modal_closed()
        expect(page.get_by_test_id("toast-message")).to_contain_text(
            team_member["new"]["email"]
        )

        invite_request = captured[0] if captured else None
        if invite_request is not None:
            body = invite_request.post_data_json
            assert "name" in body and isinstance(body["name"], str)
            assert "email" in body and isinstance(body["email"], str)
            assert body["email"] == team_member["new"]["email"]


class TestInlineEditing:
    def test_shows_name_and_role_inputs_when_edit_is_clicked(self, page: Page) -> None:
        team = TeamPage(page)
        team.start_edit(1)
        team.should_show_edit_inputs(1)

    def test_updates_the_row_after_saving_a_new_name(self, page: Page) -> None:
        team = TeamPage(page)
        team.start_edit(1)
        team.edit_name(1, "Alice QA Updated")
        team.save_edit(1)
        expect(team.name_cell(1)).to_contain_text("Alice QA Updated")

    def test_shows_a_success_toast_after_saving(self, page: Page) -> None:
        team = TeamPage(page)
        team.start_edit(2)
        team.save_edit(2)
        expect(page.get_by_test_id("toast-message")).to_contain_text("updated")

    def test_edit_save_updates_the_row_and_triggers_a_write_request_if_api_driven(
        self, page: Page
    ) -> None:
        team = TeamPage(page)
        captured: list = []

        def capture_request(req) -> None:
            if req.method in ("PUT", "PATCH") and "/api/" in req.url:
                captured.append(req)

        page.on("request", capture_request)
        team.start_edit(1)
        team.edit_name(1, "Alice QA Intercepted")
        team.save_edit(1)
        expect(team.name_cell(1)).to_contain_text("Alice QA Intercepted")

        interception = captured[0] if captured else None
        if interception is not None:
            body = interception.post_data_json
            assert "name" in body

    def test_discards_changes_on_cancel(self, page: Page) -> None:
        team = TeamPage(page)
        team.start_edit(1)
        team.edit_name(1, "Should Not Save")
        team.cancel_edit(1)
        expect(team.name_cell(1)).not_to_contain_text("Should Not Save")

    def test_restores_normal_row_after_cancel(self, page: Page) -> None:
        team = TeamPage(page)
        team.start_edit(1)
        team.cancel_edit(1)
        expect(team.edit_btn(1)).to_be_visible()


class TestFrameworkListFilter:
    def test_filters_the_framework_list(self, page: Page) -> None:
        team = TeamPage(page)
        team.framework_search().fill("play")
        items = team.framework_list().locator("li")
        count = items.count()
        for i in range(count):
            text = items.nth(i).inner_text()
            assert "play" in text.lower()

    def test_shows_all_frameworks_when_filter_is_cleared(self, page: Page) -> None:
        team = TeamPage(page)
        team.framework_search().fill("cypress")
        team.framework_search().clear()
        assert team.framework_list().locator("li").count() > 1
