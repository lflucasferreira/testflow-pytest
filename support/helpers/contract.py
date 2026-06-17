def expect_same_members(expected: list, actual: list) -> None:
    assert sorted(expected) == sorted(actual)
