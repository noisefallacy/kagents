"""Always-on growth context for user preferences and operating rules."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from kagents.config import settings


def _load_json(path: Path, fallback: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return fallback, "missing"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        return fallback, "invalid"
    return payload, "loaded"


def _query_terms(query: str) -> list[str]:
    return [term for term in re.findall(r"\w+", query.lower()) if term]


def _item_text(item: dict[str, Any]) -> str:
    parts = [
        str(item.get("id", "")),
        str(item.get("summary", "")),
        str(item.get("tool", "")),
        str(item.get("priority", "")),
    ]
    for key in ("tags", "applies_to"):
        values = item.get(key, [])
        if isinstance(values, list):
            parts.extend(str(value) for value in values)
    return " ".join(parts).lower()


def _priority_score(item: dict[str, Any]) -> int:
    priority = str(item.get("priority", "medium")).lower()
    return {"high": 3, "medium": 2, "low": 1}.get(priority, 2)


def _rank_items(items: list[Any], query: str, always_include_high: bool) -> list[dict[str, Any]]:
    terms = _query_terms(query)
    ranked: list[dict[str, Any]] = []

    for item in items:
        if not isinstance(item, dict):
            continue
        text = _item_text(item)
        score = _priority_score(item)
        score += sum(1 for term in terms if term in text)
        if always_include_high and str(item.get("priority", "")).lower() == "high":
            score += 2
        if score <= 0:
            continue
        public_item = dict(item)
        public_item["score"] = score
        ranked.append(public_item)

    ranked.sort(key=lambda item: (-item["score"], str(item.get("id", ""))))
    return ranked


def load_growth_context(
    query: str,
    user_profile_path: str | None = None,
    operating_rules_path: str | None = None,
    tool_preferences_path: str | None = None,
    max_items_per_source: int = 5,
) -> dict[str, Any]:
    """
    Load lightweight user, rule, and tool preference context for a query.

    Args:
        query: Natural-language user query.
        user_profile_path: Path to the user profile JSON file.
        operating_rules_path: Path to the operating rules JSON file.
        tool_preferences_path: Path to the tool preferences JSON file.
        max_items_per_source: Maximum ranked items per source.
    """

    profile_path = Path(user_profile_path or settings.user_profile_path)
    rules_path = Path(operating_rules_path or settings.operating_rules_path)
    preferences_path = Path(tool_preferences_path or settings.tool_preferences_path)

    profile, profile_status = _load_json(profile_path, {"preferences": [], "working_style": []})
    rules, rules_status = _load_json(rules_path, {"rules": []})
    tool_preferences, tool_status = _load_json(preferences_path, {"tool_preferences": []})

    missing_sources = []
    for source, path, status in (
        ("user_profile", profile_path, profile_status),
        ("operating_rules", rules_path, rules_status),
        ("tool_preferences", preferences_path, tool_status),
    ):
        if status != "loaded":
            missing_sources.append(
                {
                    "source": source,
                    "path": str(path),
                    "status": status,
                }
            )

    preferences = _rank_items(profile.get("preferences", []), query, always_include_high=True)
    working_style = _rank_items(profile.get("working_style", []), query, always_include_high=True)
    selected_rules = _rank_items(rules.get("rules", []), query, always_include_high=True)
    selected_tool_preferences = _rank_items(
        tool_preferences.get("tool_preferences", []),
        query,
        always_include_high=True,
    )

    return {
        "status": "success",
        "query": query,
        "growth_context": {
            "user_profile": {
                "path": str(profile_path),
                "preferences": preferences[:max_items_per_source],
                "working_style": working_style[:max_items_per_source],
            },
            "operating_rules": {
                "path": str(rules_path),
                "rules": selected_rules[:max_items_per_source],
            },
            "tool_preferences": {
                "path": str(preferences_path),
                "tool_preferences": selected_tool_preferences[:max_items_per_source],
            },
        },
        "missing_sources": missing_sources,
    }
