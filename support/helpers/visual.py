import io
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import Locator

SNAPSHOTS_DIR = Path(__file__).resolve().parents[2] / "tests" / "visual" / "snapshots"


def snapshot_path(name: str, browser_name: str) -> Path:
    return SNAPSHOTS_DIR / f"{name}-{browser_name}.png"


def _diff_pixel_ratio(expected: Image.Image, actual: Image.Image) -> float:
    if expected.size != actual.size:
        raise AssertionError(
            f"Screenshot size mismatch: expected {expected.size}, got {actual.size}"
        )
    diff = ImageChops.difference(expected.convert("RGB"), actual.convert("RGB"))
    if diff.getbbox() is None:
        return 0.0
    pixels = diff.getdata()
    changed = sum(1 for pixel in pixels if pixel != (0, 0, 0))
    return changed / len(pixels)


def assert_locator_screenshot(
    locator: Locator,
    name: str,
    *,
    browser_name: str,
    update: bool = False,
    max_diff_pixel_ratio: float = 0.05,
) -> None:
    path = snapshot_path(name, browser_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    actual_bytes = locator.screenshot(type="png", animations="disabled")

    if update:
        path.write_bytes(actual_bytes)
        return

    if not path.exists():
        raise AssertionError(
            f"Missing baseline {path}. Run: pytest tests/visual --update-snapshots"
        )

    expected = Image.open(io.BytesIO(path.read_bytes()))
    actual = Image.open(io.BytesIO(actual_bytes))
    ratio = _diff_pixel_ratio(expected, actual)

    if ratio > max_diff_pixel_ratio:
        raise AssertionError(
            f"Screenshot '{name}' diff {ratio:.2%} exceeds max {max_diff_pixel_ratio:.2%} "
            f"(baseline: {path})"
        )
