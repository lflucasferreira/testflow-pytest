import json
from pathlib import Path

CACHE_DIR = Path(".pytest")
TOKEN_CACHE = CACHE_DIR / "token-cache.json"
SESSION_FILE = CACHE_DIR / "session.json"


def write_token_cache(token: str, email: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(
        json.dumps({"token": token, "email": email, "cachedAt": __import__("time").time()}),
        encoding="utf-8",
    )


def read_cached_token() -> str | None:
    try:
        data = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
        return data.get("token")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_session(email: str, name: str, token: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(
        json.dumps({"email": email, "name": name, "token": token}),
        encoding="utf-8",
    )
