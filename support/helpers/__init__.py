from typing import Any

from playwright.sync_api import Page

SCHEMA_TYPES = {
    "string": str,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


def validate_schema(obj: dict[str, Any], schema: dict[str, str]) -> None:
    for key, expected_type in schema.items():
        assert key in obj, f'response body missing "{key}"'
        if expected_type == "array":
            assert isinstance(obj[key], list), f'"{key}" should be array'
        else:
            py_type = SCHEMA_TYPES[expected_type]
            assert isinstance(obj[key], py_type), f'"{key}" should be {expected_type}'


def get_table_rows(page: Page, table_test_id: str = "users-table"):
    return page.get_by_test_id(table_test_id).locator("tbody tr")


def get_cell(page: Page, row_id: int, field: str):
    return page.get_by_test_id(f"cell-{field}-{row_id}")
