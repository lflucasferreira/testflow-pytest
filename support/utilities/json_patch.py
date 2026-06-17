from typing import Any


class JsonPatchBuilder:
    def __init__(self) -> None:
        self._operations: list[dict[str, Any]] = []

    def replace(self, path: str, value: Any) -> "JsonPatchBuilder":
        self._operations.append({"op": "replace", "path": path, "value": value})
        return self

    def add(self, path: str, value: Any) -> "JsonPatchBuilder":
        self._operations.append({"op": "add", "path": path, "value": value})
        return self

    def remove(self, path: str) -> "JsonPatchBuilder":
        self._operations.append({"op": "remove", "path": path})
        return self

    def build(self) -> list[dict[str, Any]]:
        return list(self._operations)


def modify_patch_field(patches: list[dict], path: str, value: Any) -> list[dict]:
    return [{**op, "value": value} if op.get("path") == path else op for op in patches]


def extract_patch_values(patches: list[dict]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for op in patches:
        key = op["path"].split("/")[-1]
        if key:
            values[key] = op.get("value")
    return values
