"""Tooling for lightweight internal organization context."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kagents.config import settings


def _load_org_context(context_path: Path) -> dict[str, Any]:
    with context_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _entry_search_text(category: str, name: str, entry: dict[str, Any]) -> str:
    parts = [category, name]
    for key, value in entry.items():
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        else:
            parts.append(str(value))
    return " ".join(parts).lower()


def search_org_context(
    query: str, context_path: str | None = None, max_results: int = 5
) -> dict[str, Any]:
    """
    Search lightweight internal org context such as acronyms and team names.

    Args:
        query: Natural-language search query.
        context_path: Path to the org context JSON file.
        max_results: Maximum number of results to return.
    """

    source_path = Path(context_path or settings.org_context_path)
    if not source_path.exists():
        return {
            "status": "error",
            "message": f"Context file not found: {source_path}",
            "results": [],
        }

    payload = _load_org_context(source_path)
    terms = [term.lower() for term in query.split() if term.strip()]
    results: list[dict[str, Any]] = []

    for category, entries in payload.items():
        if not isinstance(entries, dict):
            continue
        for name, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            search_text = _entry_search_text(category, name, entry)
            score = sum(1 for term in terms if term in search_text)
            if score <= 0:
                continue
            results.append(
                {
                    "category": category,
                    "name": name,
                    "score": score,
                    "details": entry,
                }
            )

    results.sort(key=lambda item: (-item["score"], item["category"], item["name"]))

    return {
        "status": "success",
        "query": query,
        "context_path": str(source_path),
        "results": results[:max_results],
    }
