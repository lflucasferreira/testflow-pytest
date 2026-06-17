from support.utilities.json_patch import JsonPatchBuilder


class UserPatchFactory:
    @staticmethod
    def create_name_patch(first: str, middle: str, last: str) -> list[dict]:
        return (
            JsonPatchBuilder()
            .replace("/name", first)
            .replace("/middleName", middle)
            .replace("/lastName", last)
            .build()
        )

    @staticmethod
    def create_simple_name_patch(name: str) -> list[dict]:
        return JsonPatchBuilder().replace("/name", name).build()
