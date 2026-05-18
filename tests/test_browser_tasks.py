import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from kagents.tools.browser_tasks import (
    _run_browser_task_with_playwright,
    list_browser_tasks,
    run_browser_task,
)


def test_list_browser_tasks_reads_config() -> None:
    result = list_browser_tasks()

    assert result["status"] == "success"
    task_names = {task["name"] for task in result["tasks"]}
    assert "sample_portal_market_note" in task_names
    assert "tradingview_usdjpy_1h_screenshot" in task_names


def test_run_browser_task_rejects_unknown_task() -> None:
    result = run_browser_task("missing-task")

    assert result["status"] == "error"
    assert "Unknown browser task" in result["message"]


def test_run_browser_task_rejects_output_outside_browser_root(tmp_path: Path) -> None:
    tasks_path = tmp_path / "browser_tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "name": "bad_output",
                        "start_url": "file://data/browser_apps/sample_portal.html",
                        "allowed_url_prefixes": ["file://data/browser_apps/"],
                        "actions": [{"type": "extract_text", "selector": "body"}],
                        "output_dir": "outputs/not_browser",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_browser_task("bad_output", tasks_path=str(tasks_path))

    assert result["status"] == "error"
    assert "output_dir must be under" in result["message"]


def test_run_browser_task_rejects_uncovered_start_url(tmp_path: Path) -> None:
    tasks_path = tmp_path / "browser_tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "name": "bad_url",
                        "start_url": "https://example.com/app",
                        "allowed_url_prefixes": ["https://internal.example.com/"],
                        "actions": [{"type": "extract_text", "selector": "body"}],
                        "output_dir": "outputs/browser/bad_url",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_browser_task("bad_url", tasks_path=str(tasks_path))

    assert result["status"] == "error"
    assert "not covered by allowed_url_prefixes" in result["message"]


def test_run_browser_task_rejects_unsupported_action(tmp_path: Path) -> None:
    tasks_path = tmp_path / "browser_tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "name": "bad_action",
                        "start_url": "file://data/browser_apps/sample_portal.html",
                        "allowed_url_prefixes": ["file://data/browser_apps/"],
                        "actions": [{"type": "evaluate_script", "script": "alert(1)"}],
                        "output_dir": "outputs/browser/bad_action",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_browser_task("bad_action", tasks_path=str(tasks_path))

    assert result["status"] == "error"
    assert "Unsupported browser action type" in result["message"]


def test_run_browser_task_rejects_screenshot_outside_output_dir(tmp_path: Path) -> None:
    tasks_path = tmp_path / "browser_tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "name": "bad_screenshot",
                        "start_url": "file://data/browser_apps/sample_portal.html",
                        "allowed_url_prefixes": ["file://data/browser_apps/"],
                        "actions": [
                            {
                                "type": "screenshot",
                                "path": "outputs/browser/other_task/screenshot.png",
                            }
                        ],
                        "output_dir": "outputs/browser/bad_screenshot",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_browser_task("bad_screenshot", tasks_path=str(tasks_path))

    assert result["status"] == "error"
    assert "artifact path must stay under task output_dir" in result["message"]


def test_run_browser_task_allows_selector_and_screenshot_actions(tmp_path: Path) -> None:
    tasks_path = tmp_path / "browser_tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "name": "selectors",
                        "start_url": "file://data/browser_apps/sample_portal.html",
                        "allowed_url_prefixes": ["file://data/browser_apps/"],
                        "actions": [
                            {"type": "wait_for_selector", "selector": "body"},
                            {"type": "click_selector", "selector": "#market-button"},
                            {"type": "fill_selector", "selector": "input", "text": "USDJPY"},
                            {"type": "press_key", "key": "Enter"},
                            {"type": "wait_ms", "milliseconds": 100},
                            {
                                "type": "screenshot",
                                "path": "outputs/browser/selectors/screenshot_{timestamp}.png",
                            },
                        ],
                        "output_dir": "outputs/browser/selectors",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with patch(
        "kagents.tools.browser_tasks._run_browser_task_with_playwright",
        return_value=([], ["file:///sample"], ["C:/fake/screenshot.png"]),
    ):
        result = run_browser_task("selectors", tasks_path=str(tasks_path))

    assert result["status"] == "success"
    assert "C:/fake/screenshot.png" in result["artifacts"]


def test_browser_task_worker_runs_from_active_async_loop() -> None:
    task = {
        "start_url": "file:///tmp/sample.html",
        "allowed_url_prefixes": ["file:///tmp/"],
        "actions": [{"type": "extract_text", "selector": "body"}],
    }

    def fake_worker(received_task, headless, timeout_ms, timestamp):
        return (
            [received_task["start_url"], str(headless), str(timeout_ms), timestamp],
            ["visited"],
            [],
        )

    async def call_from_async_loop():
        with patch(
            "kagents.tools.browser_tasks._run_browser_task_in_worker",
            side_effect=fake_worker,
        ) as worker:
            result = _run_browser_task_with_playwright(task, True, 1234, "20260101T000000Z")
            assert worker.call_count == 1
            return result

    extracted_text, visited_urls, artifacts = asyncio.run(call_from_async_loop())

    assert extracted_text == ["file:///tmp/sample.html", "True", "1234", "20260101T000000Z"]
    assert visited_urls == ["visited"]
    assert artifacts == []
