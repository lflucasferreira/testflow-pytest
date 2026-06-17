"""Allure Report hooks — metadata, environment, Playwright artifacts on failure."""

from __future__ import annotations

import os
import platform
import re
from pathlib import Path

import allure
import pytest

from support.config import BASE_URL

TC_PATTERN = re.compile(r"TC-\d{4}")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
TEST_RESULTS_DIR = PROJECT_ROOT / "test-results"


def _suite_from_path(nodeid: str) -> str | None:
    parts = nodeid.split("::")[0].split("/")
    if "tests" in parts:
        idx = parts.index("tests")
        if idx + 1 < len(parts):
            return parts[idx + 1].replace(".py", "")
    return None


def _extract_tc_id(node: pytest.Item) -> str | None:
    if hasattr(node, "callspec") and node.callspec is not None:
        for value in node.callspec.params.values():
            text = str(value)
            match = TC_PATTERN.search(text)
            if match:
                return match.group(0)

    for source in (node.name, node.nodeid):
        match = TC_PATTERN.search(source)
        if match:
            return match.group(0)
    return None


def _attach_playwright_artifacts(node: pytest.Item) -> None:
    if "page" not in node.fixturenames:
        return

    page = node.funcargs.get("page")
    if page is None:
        return

    try:
        png = page.screenshot(full_page=True)
        allure.attach(png, name="failure-screenshot", attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass

    if not TEST_RESULTS_DIR.is_dir():
        return

    slug = re.sub(r"[^\w\-]+", "-", node.name).strip("-").lower()
    candidates: list[Path] = []
    for path in TEST_RESULTS_DIR.rglob("*"):
        if path.suffix not in {".zip", ".png", ".webm"}:
            continue
        if slug and slug in path.as_posix().lower():
            candidates.append(path)

    if not candidates:
        candidates = sorted(
            TEST_RESULTS_DIR.rglob("trace.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:1]

    for path in candidates:
        suffix = path.suffix.lower()
        if suffix == ".zip":
            allure.attach.file(
                str(path),
                name=path.name,
                attachment_type=allure.attachment_type.ZIP,
                extension="zip",
            )
        elif suffix == ".png":
            allure.attach.file(
                str(path),
                name=path.name,
                attachment_type=allure.attachment_type.PNG,
                extension="png",
            )
        elif suffix == ".webm":
            allure.attach.file(
                str(path),
                name=path.name,
                attachment_type=allure.attachment_type.WEBM,
                extension="webm",
            )


def _resolve_browser_name(item: pytest.Item) -> str:
    env = os.getenv("ALLURE_BROWSER")
    if env:
        return env

    if hasattr(item, "callspec") and item.callspec is not None:
        browser_name = item.callspec.params.get("browser_name")
        if browser_name is not None:
            return str(browser_name)

    browsers = item.config.getoption("--browser", default=None)
    if browsers:
        return browsers[0] if isinstance(browsers, (list, tuple)) else str(browsers)

    return "chromium"


def _write_environment_properties(browser: str) -> None:
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Project=testflow-pytest",
        f"Python={platform.python_version()}",
        f"Platform={platform.system()} {platform.release()}",
        f"Browser={browser}",
        f"BASE_URL={BASE_URL}",
        f"CI={os.getenv('CI', 'false')}",
    ]
    github_sha = os.getenv("GITHUB_SHA")
    if github_sha:
        lines.append(f"GitHub.SHA={github_sha[:7]}")
    github_ref = os.getenv("GITHUB_REF_NAME")
    if github_ref:
        lines.append(f"GitHub.Ref={github_ref}")

    (ALLURE_RESULTS_DIR / "environment.properties").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
    if report.when == "call" and report.failed:
        _attach_playwright_artifacts(item)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    browser = _resolve_browser_name(item)
    allure.dynamic.label("browser", browser)

    suite = _suite_from_path(item.nodeid)
    if suite:
        allure.dynamic.parent_suite("testflow-pytest")
        allure.dynamic.suite(suite)

    for marker in item.iter_markers():
        if marker.name in {"parametrize", "usefixtures"}:
            continue
        allure.dynamic.tag(marker.name)

    tc_id = _extract_tc_id(item)
    if tc_id:
        allure.dynamic.testcase(tc_id)
        allure.dynamic.label("testCase", tc_id)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if session.config.getoption("--collect-only", default=False):
        return
    browser = os.getenv("ALLURE_BROWSER")
    if not browser:
        browsers = session.config.getoption("--browser", default=None)
        if browsers:
            browser = browsers[0] if isinstance(browsers, (list, tuple)) else str(browsers)
        else:
            browser = "chromium"
    _write_environment_properties(browser)
