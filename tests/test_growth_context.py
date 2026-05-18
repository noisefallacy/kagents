import json
from pathlib import Path

from kagents.tools.growth_context import load_growth_context


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_growth_context_returns_ranked_profile_rules_and_tools(tmp_path: Path) -> None:
    profile_path = tmp_path / "user_profile.json"
    rules_path = tmp_path / "operating_rules.json"
    tools_path = tmp_path / "tool_preferences.json"

    write_json(
        profile_path,
        {
            "preferences": [
                {
                    "id": "pref_evidence",
                    "summary": "Prefer concise answers with cited evidence.",
                    "tags": ["answers", "evidence"],
                    "priority": "high",
                }
            ],
            "working_style": [
                {
                    "id": "style_data_first",
                    "summary": "Keep private knowledge in data files.",
                    "tags": ["data"],
                    "priority": "high",
                }
            ],
        },
    )
    write_json(
        rules_path,
        {
            "rules": [
                {
                    "id": "rule_missing_data",
                    "summary": "Do not invent private data.",
                    "applies_to": ["all"],
                    "priority": "high",
                }
            ]
        },
    )
    write_json(
        tools_path,
        {
            "tool_preferences": [
                {
                    "id": "tool_private_first",
                    "summary": "Use private context first.",
                    "tool": "load_private_context",
                    "applies_to": ["internal_context"],
                    "priority": "high",
                }
            ]
        },
    )

    result = load_growth_context(
        "Give me an evidence-backed internal context answer.",
        user_profile_path=str(profile_path),
        operating_rules_path=str(rules_path),
        tool_preferences_path=str(tools_path),
    )

    context = result["growth_context"]
    assert result["status"] == "success"
    assert context["user_profile"]["preferences"][0]["id"] == "pref_evidence"
    assert context["operating_rules"]["rules"][0]["id"] == "rule_missing_data"
    assert context["tool_preferences"]["tool_preferences"][0]["tool"] == "load_private_context"
    assert result["missing_sources"] == []


def test_load_growth_context_reports_missing_sources(tmp_path: Path) -> None:
    result = load_growth_context(
        "anything",
        user_profile_path=str(tmp_path / "missing_profile.json"),
        operating_rules_path=str(tmp_path / "missing_rules.json"),
        tool_preferences_path=str(tmp_path / "missing_tools.json"),
    )

    missing = {item["source"] for item in result["missing_sources"]}

    assert missing == {"user_profile", "operating_rules", "tool_preferences"}
