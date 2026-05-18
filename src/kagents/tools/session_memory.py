"""Local session-memory tools for durable portfolio-manager context."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from kagents.config import settings


ALLOWED_MEMORY_TYPES = {
    "decision",
    "preference",
    "project_fact",
    "follow_up",
    "rule",
    "note",
}
ALLOWED_VISIBILITY = {"private", "team", "org"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}


def _load_memory(memory_path: Path) -> dict[str, Any]:
    if not memory_path.exists():
        return {"memories": []}

    with memory_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        return {"memories": []}

    memories = payload.get("memories", [])
    if not isinstance(memories, list):
        payload["memories"] = []
    return payload


def _write_memory(memory_path: Path, payload: dict[str, Any]) -> None:
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    with memory_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def _memory_search_text(memory: dict[str, Any]) -> str:
    parts = [
        str(memory.get("id", "")),
        str(memory.get("type", "")),
        str(memory.get("summary", "")),
        str(memory.get("details", "")),
        str(memory.get("created_at", "")),
    ]
    tags = memory.get("tags", [])
    if isinstance(tags, list):
        parts.extend(str(tag) for tag in tags)
    return " ".join(parts).lower()


def _query_terms(query: str) -> list[str]:
    return [term for term in re.findall(r"\w+", query.lower()) if term]


def _normalize_choice(value: str, allowed: set[str], fallback: str) -> str:
    normalized = value.strip().lower()
    return normalized if normalized in allowed else fallback


def _normalize_tags(tags: list[str] | None) -> list[str]:
    if not tags:
        return []
    return sorted({tag.strip().lower() for tag in tags if tag.strip()})


def _public_memory(memory: dict[str, Any], score: int | None = None) -> dict[str, Any]:
    item = {
        "id": memory.get("id"),
        "type": memory.get("type", "note"),
        "summary": memory.get("summary", ""),
        "details": memory.get("details", ""),
        "tags": memory.get("tags", []),
        "visibility": memory.get("visibility", "private"),
        "confidence": memory.get("confidence", "medium"),
        "source": memory.get("source", "manual"),
        "created_at": memory.get("created_at"),
        "updated_at": memory.get("updated_at"),
    }
    if score is not None:
        item["score"] = score
    return item


def _find_memory(memories: list[Any], memory_id: str) -> dict[str, Any] | None:
    for memory in memories:
        if isinstance(memory, dict) and memory.get("id") == memory_id:
            return memory
    return None


def search_session_memory(
    query: str,
    memory_path: str | None = None,
    max_results: int = 5,
    memory_type: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Search durable local memories for prior decisions, preferences, and facts.

    Args:
        query: Natural-language search query.
        memory_path: Path to the local memory JSON file.
        max_results: Maximum number of results to return.
        memory_type: Optional memory type filter.
        tags: Optional tag filters. Memories matching these tags get a score boost.
    """

    source_path = Path(memory_path or settings.session_memory_path)
    payload = _load_memory(source_path)
    terms = _query_terms(query)
    normalized_type = (
        _normalize_choice(memory_type, ALLOWED_MEMORY_TYPES, "") if memory_type else None
    )
    normalized_tags = _normalize_tags(tags)
    results: list[dict[str, Any]] = []

    for memory in payload.get("memories", []):
        if not isinstance(memory, dict):
            continue
        if normalized_type and memory.get("type") != normalized_type:
            continue
        memory_tags = set(_normalize_tags(memory.get("tags", [])))
        search_text = _memory_search_text(memory)
        score = sum(1 for term in terms if term in search_text)
        score += 2 * sum(1 for tag in normalized_tags if tag in memory_tags)
        if query.lower().strip() in search_text:
            score += 3
        if score <= 0:
            continue
        results.append(_public_memory(memory, score=score))

    results.sort(
        key=lambda item: (
            item["score"],
            str(item["updated_at"] or item["created_at"] or ""),
        ),
        reverse=True,
    )

    return {
        "status": "success",
        "query": query,
        "memory_path": str(source_path),
        "results": results[:max_results],
    }


def remember_session_fact(
    summary: str,
    details: str = "",
    memory_type: str = "note",
    tags: list[str] | None = None,
    visibility: str = "private",
    confidence: str = "medium",
    source: str = "user",
    memory_path: str | None = None,
) -> dict[str, Any]:
    """
    Store a durable local memory for future portfolio-manager conversations.

    Args:
        summary: Short human-readable memory summary.
        details: Optional supporting details.
        memory_type: Memory category, such as decision, preference, fact, or note.
        tags: Optional tags for future retrieval.
        visibility: Intended scope, such as private, team, or org.
        confidence: Confidence level for the memory.
        source: Where the memory came from, such as user, document, or manual.
        memory_path: Path to the local memory JSON file.
    """

    source_path = Path(memory_path or settings.session_memory_path)
    payload = _load_memory(source_path)
    now = datetime.now(timezone.utc).isoformat()
    memory = {
        "id": f"mem_{uuid4().hex[:12]}",
        "type": _normalize_choice(memory_type, ALLOWED_MEMORY_TYPES, "note"),
        "summary": summary.strip(),
        "details": details.strip(),
        "tags": _normalize_tags(tags),
        "visibility": _normalize_choice(visibility, ALLOWED_VISIBILITY, "private"),
        "confidence": _normalize_choice(confidence, ALLOWED_CONFIDENCE, "medium"),
        "source": source.strip() or "user",
        "created_at": now,
        "updated_at": now,
    }
    payload.setdefault("memories", []).append(memory)
    _write_memory(source_path, payload)

    return {
        "status": "success",
        "memory_path": str(source_path),
        "memory": memory,
    }


def list_session_memory(
    memory_path: str | None = None,
    memory_type: str | None = None,
    tags: list[str] | None = None,
    max_results: int = 20,
) -> dict[str, Any]:
    """
    List local memories, optionally filtered by type or tag.

    Args:
        memory_path: Path to the local memory JSON file.
        memory_type: Optional memory type filter.
        tags: Optional tags that must be present.
        max_results: Maximum number of memories to return.
    """

    source_path = Path(memory_path or settings.session_memory_path)
    payload = _load_memory(source_path)
    normalized_type = (
        _normalize_choice(memory_type, ALLOWED_MEMORY_TYPES, "") if memory_type else None
    )
    normalized_tags = set(_normalize_tags(tags))
    memories: list[dict[str, Any]] = []

    for memory in payload.get("memories", []):
        if not isinstance(memory, dict):
            continue
        if normalized_type and memory.get("type") != normalized_type:
            continue
        memory_tags = set(_normalize_tags(memory.get("tags", [])))
        if normalized_tags and not normalized_tags.issubset(memory_tags):
            continue
        memories.append(_public_memory(memory))

    memories.sort(key=lambda item: str(item["updated_at"] or item["created_at"] or ""), reverse=True)

    return {
        "status": "success",
        "memory_path": str(source_path),
        "results": memories[:max_results],
    }


def update_session_memory(
    memory_id: str,
    summary: str | None = None,
    details: str | None = None,
    memory_type: str | None = None,
    tags: list[str] | None = None,
    visibility: str | None = None,
    confidence: str | None = None,
    source: str | None = None,
    memory_path: str | None = None,
) -> dict[str, Any]:
    """
    Update an existing local memory by id.

    Args:
        memory_id: Stable memory id to update.
        summary: Replacement summary.
        details: Replacement details.
        memory_type: Replacement memory type.
        tags: Replacement tags.
        visibility: Replacement visibility.
        confidence: Replacement confidence.
        source: Replacement source.
        memory_path: Path to the local memory JSON file.
    """

    source_path = Path(memory_path or settings.session_memory_path)
    payload = _load_memory(source_path)
    memory = _find_memory(payload.get("memories", []), memory_id)
    if memory is None:
        return {
            "status": "error",
            "message": f"Memory not found: {memory_id}",
            "memory": None,
        }

    if summary is not None:
        memory["summary"] = summary.strip()
    if details is not None:
        memory["details"] = details.strip()
    if memory_type is not None:
        memory["type"] = _normalize_choice(memory_type, ALLOWED_MEMORY_TYPES, "note")
    if tags is not None:
        memory["tags"] = _normalize_tags(tags)
    if visibility is not None:
        memory["visibility"] = _normalize_choice(visibility, ALLOWED_VISIBILITY, "private")
    if confidence is not None:
        memory["confidence"] = _normalize_choice(confidence, ALLOWED_CONFIDENCE, "medium")
    if source is not None:
        memory["source"] = source.strip() or "user"
    memory["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_memory(source_path, payload)

    return {
        "status": "success",
        "memory_path": str(source_path),
        "memory": _public_memory(memory),
    }


def forget_session_memory(
    memory_id: str,
    memory_path: str | None = None,
) -> dict[str, Any]:
    """
    Delete an existing local memory by id.

    Args:
        memory_id: Stable memory id to delete.
        memory_path: Path to the local memory JSON file.
    """

    source_path = Path(memory_path or settings.session_memory_path)
    payload = _load_memory(source_path)
    memories = payload.get("memories", [])
    kept_memories = [
        memory
        for memory in memories
        if not (isinstance(memory, dict) and memory.get("id") == memory_id)
    ]

    if len(kept_memories) == len(memories):
        return {
            "status": "error",
            "message": f"Memory not found: {memory_id}",
            "forgotten_id": None,
        }

    payload["memories"] = kept_memories
    _write_memory(source_path, payload)

    return {
        "status": "success",
        "memory_path": str(source_path),
        "forgotten_id": memory_id,
    }
