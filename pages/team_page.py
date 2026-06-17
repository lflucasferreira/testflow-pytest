from playwright.sync_api import Page, expect


class TeamPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def page_root(self):
        return self.page.get_by_test_id("page-team")

    def team_summary(self):
        return self.page.get_by_test_id("team-summary")

    def invite_btn(self):
        return self.page.get_by_test_id("invite-btn")

    def search_input(self):
        return self.page.get_by_test_id("table-search")

    def role_filter(self):
        return self.page.get_by_test_id("role-filter")

    def status_filter(self):
        return self.page.get_by_test_id("status-filter")

    def sort_btn(self):
        return self.page.get_by_test_id("table-sort-name")

    def row_count(self):
        return self.page.get_by_test_id("table-row-count")

    def table(self):
        return self.page.get_by_test_id("users-table")

    def table_rows(self):
        return self.table().locator("tbody tr")

    def row(self, row_id: int):
        return self.page.get_by_test_id(f"user-row-{row_id}")

    def edit_btn(self, row_id: int):
        return self.page.get_by_test_id(f"edit-row-{row_id}")

    def save_btn(self, row_id: int):
        return self.page.get_by_test_id(f"save-row-{row_id}")

    def cancel_btn(self, row_id: int):
        return self.page.get_by_test_id(f"cancel-row-{row_id}")

    def name_cell(self, row_id: int):
        return self.page.get_by_test_id(f"cell-name-{row_id}")

    def role_cell(self, row_id: int):
        return self.page.get_by_test_id(f"cell-role-{row_id}")

    def prev_page(self):
        return self.page.get_by_test_id("prev-page")

    def next_page(self):
        return self.page.get_by_test_id("next-page")

    def page_info(self):
        return self.page.get_by_test_id("page-info")

    def invite_modal(self):
        return self.page.get_by_test_id("invite-modal")

    def invite_name(self):
        return self.page.get_by_test_id("invite-name")

    def invite_email(self):
        return self.page.get_by_test_id("invite-email")

    def invite_role(self):
        return self.page.get_by_test_id("invite-role")

    def invite_confirm(self):
        return self.page.get_by_test_id("invite-confirm")

    def invite_cancel(self):
        return self.page.get_by_test_id("invite-cancel")

    def invite_error(self):
        return self.page.get_by_test_id("invite-error")

    def edit_name_input(self, row_id: int):
        return self.page.get_by_test_id(f"edit-name-{row_id}")

    def edit_role_select(self, row_id: int):
        return self.page.get_by_test_id(f"edit-role-{row_id}")

    def framework_search(self):
        return self.page.get_by_test_id("item-search")

    def framework_list(self):
        return self.page.get_by_test_id("item-list")

    def search(self, term: str) -> "TeamPage":
        self.search_input().clear()
        self.search_input().fill(term)
        return self

    def clear_search(self) -> "TeamPage":
        self.search_input().clear()
        return self

    def filter_by_role(self, role: str) -> "TeamPage":
        self.role_filter().select_option(role)
        return self

    def filter_by_status(self, status: str) -> "TeamPage":
        self.status_filter().select_option(status)
        return self

    def sort_by_name(self) -> "TeamPage":
        self.sort_btn().click()
        return self

    def go_to_next_page(self) -> "TeamPage":
        self.next_page().click()
        return self

    def go_to_prev_page(self) -> "TeamPage":
        self.prev_page().click()
        return self

    def open_invite_modal(self) -> "TeamPage":
        self.invite_btn().click()
        expect(self.invite_modal()).to_be_visible()
        return self

    def fill_invite_form(
        self,
        *,
        name: str | None = None,
        email: str | None = None,
        role: str | None = None,
    ) -> "TeamPage":
        if name is not None:
            self.invite_name().clear()
            self.invite_name().fill(name)
        if email is not None:
            self.invite_email().clear()
            self.invite_email().fill(email)
        if role is not None:
            self.invite_role().select_option(role)
        return self

    def submit_invite(self) -> "TeamPage":
        self.invite_confirm().click()
        return self

    def cancel_invite(self) -> "TeamPage":
        self.invite_cancel().click()
        return self

    def start_edit(self, row_id: int) -> "TeamPage":
        self.edit_btn(row_id).click()
        expect(self.edit_name_input(row_id)).to_be_visible()
        return self

    def edit_name(self, row_id: int, new_name: str) -> "TeamPage":
        self.edit_name_input(row_id).clear()
        self.edit_name_input(row_id).fill(new_name)
        return self

    def edit_role(self, row_id: int, role: str) -> "TeamPage":
        self.edit_role_select(row_id).select_option(role)
        return self

    def save_edit(self, row_id: int) -> "TeamPage":
        self.save_btn(row_id).click()
        return self

    def cancel_edit(self, row_id: int) -> "TeamPage":
        self.cancel_btn(row_id).click()
        return self

    def should_have_row_count(self, n: int) -> "TeamPage":
        expect(self.table_rows()).to_have_count(n)
        return self

    def should_have_invite_modal_open(self) -> "TeamPage":
        expect(self.invite_modal()).to_be_visible()
        return self

    def should_have_invite_modal_closed(self) -> "TeamPage":
        expect(self.invite_modal()).not_to_be_visible()
        return self

    def should_show_invite_error(self, text: str) -> "TeamPage":
        expect(self.invite_error()).to_be_visible()
        expect(self.invite_error()).to_contain_text(text)
        return self

    def should_show_edit_inputs(self, row_id: int) -> "TeamPage":
        expect(self.edit_name_input(row_id)).to_be_visible()
        expect(self.edit_role_select(row_id)).to_be_visible()
        return self
