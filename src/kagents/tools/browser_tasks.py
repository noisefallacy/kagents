"""Guarded Playwright browser task tools."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from kagents.config import PROJECT_ROOT, settings


OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "browser"
ALLOWED_ACTION_TYPES = {
    "click_selector",
    "click_text",
    "extract_text",
    "fill_selector",
    "press_key",
    "screenshot",
    "wait_for_selector",
    "wait_ms",
}
ALLOWED_SELECTOR_STATES = {"attached", "detached", "hidden", "visible"}


def _resolve_project_url(value: str) -> str:
    if value.startswith("file://"):
        path_value = value.removeprefix("file://")
        candidate = Path(path_value)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        return candidate.resolve().as_uri()
    return value


def _resolve_output_dir(value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (PROJECT_ROOT / candidate).resolve()

    output_root = OUTPUT_ROOT.resolve()
    try:
        resolved.relative_to(output_root)
    except ValueError as exc:
        raise ValueError(f"Browser task output_dir must be under {output_root}") from exc

    return resolved


def _resolve_browser_artifact_path(value: str, output_dir: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (PROJECT_ROOT / candidate).resolve()

    output_root = OUTPUT_ROOT.resolve()
    try:
        resolved.relative_to(output_root)
    except ValueError as exc:
        raise ValueError(f"Browser artifact path must be under {output_root}") from exc

    try:
        resolved.relative_to(output_dir.resolve())
    except ValueError as exc:
        raise ValueError(
            f"Browser artifact path must stay under task output_dir {output_dir.resolve()}"
        ) from exc

    return resolved


def _load_task_config(tasks_path: str | None = None) -> dict[str, Any]:
    path = Path(tasks_path or settings.browser_tasks_path)
    if not path.exists():
        raise ValueError(f"Browser tasks file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("Browser tasks file must contain a tasks list.")

    return data


def _select_locator(locator: Any, action: dict[str, Any]) -> Any:
    if action.get("last", False):
        return locator.last
    if "index" in action:
        return locator.nth(action["index"])
    return locator.first


def _task_by_name(task_name: str, tasks_path: str | None = None) -> dict[str, Any]:
    requested_name = task_name.strip()
    for task in _load_task_config(tasks_path)["tasks"]:
        if isinstance(task, dict) and task.get("name") == requested_name:
            return task

    raise ValueError(f"Unknown browser task: {task_name}")


def _validated_task(task_name: str, tasks_path: str | None = None) -> dict[str, Any]:
    task = _task_by_name(task_name, tasks_path)
    start_url = task.get("start_url")
    allowed_url_prefixes = task.get("allowed_url_prefixes")
    actions = task.get("actions")
    output_dir = task.get("output_dir")

    if not isinstance(start_url, str) or not start_url:
        raise ValueError("Browser task start_url must be a non-empty string.")
    if not isinstance(allowed_url_prefixes, list) or not allowed_url_prefixes:
        raise ValueError("Browser task allowed_url_prefixes must be a non-empty list.")
    if not all(isinstance(prefix, str) and prefix for prefix in allowed_url_prefixes):
        raise ValueError("Browser task allowed_url_prefixes must contain strings.")
    if not isinstance(actions, list) or not actions:
        raise ValueError("Browser task actions must be a non-empty list.")
    if not isinstance(output_dir, str) or not output_dir:
        raise ValueError("Browser task output_dir must be a non-empty string.")

    resolved_start_url = _resolve_project_url(start_url)
    resolved_prefixes = [_resolve_project_url(prefix) for prefix in allowed_url_prefixes]
    if not any(resolved_start_url.startswith(prefix) for prefix in resolved_prefixes):
        raise ValueError("Browser task start_url is not covered by allowed_url_prefixes.")

    resolved_output_dir = _resolve_output_dir(output_dir)
    validated_actions = []
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("Browser task actions must be objects.")
        action_type = action.get("type")
        if "optional" in action and not isinstance(action["optional"], bool):
            raise ValueError("Browser task optional must be true or false when provided.")
        if "last" in action and not isinstance(action["last"], bool):
            raise ValueError("Browser task last must be true or false when provided.")
        if "index" in action and (
            not isinstance(action["index"], int) or action["index"] < 0
        ):
            raise ValueError("Browser task index must be a non-negative integer.")
        if action_type not in ALLOWED_ACTION_TYPES:
            raise ValueError(
                f"Unsupported browser action type: {action_type}. "
                f"Allowed: {sorted(ALLOWED_ACTION_TYPES)}"
            )
        if action_type == "click_text" and not isinstance(action.get("text"), str):
            raise ValueError("click_text actions require text.")
        if action_type in {"click_selector", "fill_selector", "wait_for_selector"}:
            if not isinstance(action.get("selector"), str):
                raise ValueError(f"{action_type} actions require selector.")
        if action_type == "fill_selector" and not isinstance(action.get("text"), str):
            raise ValueError("fill_selector actions require text.")
        if action_type == "press_key" and not isinstance(action.get("key"), str):
            raise ValueError("press_key actions require key.")
        if action_type == "extract_text" and not isinstance(action.get("selector"), str):
            raise ValueError("extract_text actions require selector.")
        if action_type == "wait_for_selector":
            state = action.get("state", "visible")
            if state not in ALLOWED_SELECTOR_STATES:
                raise ValueError(
                    f"wait_for_selector state must be one of {sorted(ALLOWED_SELECTOR_STATES)}"
                )
        if action_type == "wait_ms":
            milliseconds = action.get("milliseconds")
            if not isinstance(milliseconds, int) or milliseconds < 0 or milliseconds > 30000:
                raise ValueError("wait_ms actions require milliseconds between 0 and 30000.")
        if action_type == "screenshot":
            path_template = action.get("path")
            if path_template is not None and not isinstance(path_template, str):
                raise ValueError("screenshot path must be a string when provided.")
            if path_template and not path_template.endswith(".png"):
                raise ValueError("screenshot path must end in .png.")
            if path_template:
                _resolve_browser_artifact_path(
                    path_template.format(task_name=task["name"], timestamp="preview"),
                    resolved_output_dir,
                )
        validated_actions.append(action)

    return {
        "name": task["name"],
        "description": task.get("description", ""),
        "start_url": resolved_start_url,
        "allowed_url_prefixes": resolved_prefixes,
        "actions": validated_actions,
        "output_dir": resolved_output_dir,
    }


def list_browser_tasks(tasks_path: str | None = None) -> dict[str, Any]:
    """List configured browser automation tasks without running a browser."""

    try:
        tasks = _load_task_config(tasks_path)["tasks"]
    except ValueError as exc:
        return {"status": "error", "message": str(exc), "tasks": []}

    return {
        "status": "success",
        "tasks": [
            {
                "name": task.get("name"),
                "description": task.get("description", ""),
                "action_count": len(task.get("actions", [])),
            }
            for task in tasks
            if isinstance(task, dict)
        ],
    }


def _run_browser_task_in_worker(
    task: dict[str, Any],
    headless: bool,
    timeout_ms: int,
    timestamp: str,
) -> tuple[list[str], list[str], list[str]]:
    from playwright.sync_api import sync_playwright

    extracted_text: list[str] = []
    visited_urls: list[str] = []
    artifacts: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            page.set_default_timeout(timeout_ms)
            page.goto(task["start_url"])
            visited_urls.append(page.url)

            for action in task["actions"]:
                if not any(page.url.startswith(prefix) for prefix in task["allowed_url_prefixes"]):
                    raise RuntimeError(f"Navigation left allowlisted URLs: {page.url}")

                try:
                    if action["type"] == "click_text":
                        locator = page.get_by_text(
                            action["text"],
                            exact=action.get("exact", True),
                        )
                        _select_locator(locator, action).click()
                    elif action["type"] == "click_selector":
                        _select_locator(page.locator(action["selector"]), action).click()
                    elif action["type"] == "extract_text":
                        extracted_text.append(
                            _select_locator(page.locator(action["selector"]), action).inner_text()
                        )
                    elif action["type"] == "fill_selector":
                        _select_locator(page.locator(action["selector"]), action).fill(action["text"])
                    elif action["type"] == "press_key":
                        page.keyboard.press(action["key"])
                    elif action["type"] == "wait_for_selector":
                        _select_locator(page.locator(action["selector"]), action).wait_for(
                            state=action.get("state", "visible")
                        )
                    elif action["type"] == "wait_ms":
                        page.wait_for_timeout(action["milliseconds"])
                    elif action["type"] == "screenshot":
                        path_template = action.get(
                            "path",
                            str(task["output_dir"] / f"{task['name']}_{timestamp}.png"),
                        )
                        screenshot_path = _resolve_browser_artifact_path(
                            path_template.format(task_name=task["name"], timestamp=timestamp),
                            task["output_dir"],
                        )
                        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                        page.screenshot(
                            path=str(screenshot_path),
                            full_page=action.get("full_page", False),
                        )
                        artifacts.append(str(screenshot_path))
                except Exception:
                    if action.get("optional", False):
                        continue
                    raise

                if not any(page.url.startswith(prefix) for prefix in task["allowed_url_prefixes"]):
                    raise RuntimeError(f"Navigation left allowlisted URLs: {page.url}")
        finally:
            browser.close()

    return extracted_text, visited_urls, artifacts


def _run_browser_task_with_playwright(
    task: dict[str, Any],
    headless: bool,
    timeout_ms: int,
    timestamp: str,
) -> tuple[list[str], list[str], list[str]]:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return _run_browser_task_in_worker(task, headless, timeout_ms, timestamp)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            _run_browser_task_in_worker,
            task,
            headless,
            timeout_ms,
            timestamp,
        )
        return future.result()


def run_browser_task(
    task_name: str,
    headless: bool = True,
    timeout_ms: int = 30000,
    tasks_path: str | None = None,
) -> dict[str, Any]:
    """
    Run a pre-approved Playwright browser task and save extracted text artifacts.

    Args:
        task_name: Name from the configured browser tasks JSON file.
        headless: Whether Chromium should run headless.
        timeout_ms: Browser action timeout in milliseconds.
        tasks_path: Optional browser tasks JSON path, mainly for tests.
    """

    try:
        task = _validated_task(task_name, tasks_path)
    except ValueError as exc:
        return {
            "status": "error",
            "message": str(exc),
            "artifacts": [],
        }

    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return {
            "status": "error",
            "message": "Playwright is not installed. Install requirements.txt first.",
            "artifacts": [],
        }

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    try:
        extracted_text, visited_urls, browser_artifacts = _run_browser_task_with_playwright(
            task=task,
            headless=headless,
            timeout_ms=timeout_ms,
            timestamp=timestamp,
        )
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Browser task failed: {exc}",
            "artifacts": [],
            "visited_urls": [],
        }

    output_dir = task["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / f"{task['name']}_{timestamp}.txt"
    metadata_path = output_dir / f"{task['name']}_{timestamp}.json"
    text_path.write_text("\n\n".join(extracted_text), encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "task_name": task["name"],
                "start_url": task["start_url"],
                "visited_urls": visited_urls,
                "generated_at": timestamp,
                "artifact_text_path": str(text_path),
                "browser_artifacts": browser_artifacts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "status": "success",
        "task_name": task["name"],
        "artifacts": [str(text_path), str(metadata_path), *browser_artifacts],
        "visited_urls": visited_urls,
        "extracted_text_preview": "\n\n".join(extracted_text)[:1000],
    }
