import json
from pathlib import Path

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures"


def read_fixture(relative_path: str) -> dict | list:
    path = FIXTURES_ROOT / relative_path
    return json.loads(path.read_text(encoding="utf-8"))
