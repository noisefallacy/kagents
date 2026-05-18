import json
from pathlib import Path

from kagents.tools.session_memory import (
    forget_session_memory,
    list_session_memory,
    remember_session_fact,
    search_session_memory,
    update_session_memory,
)


def write_memory(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "memories": [
                    {
                        "id": "mem_1",
                        "type": "decision",
                        "summary": "Finance Review should focus on forecast deltas.",
                        "details": "The team decided to compare the current forecast against last quarter.",
                        "tags": ["finance", "review", "forecast"],
                        "visibility": "private",
                        "confidence": "high",
                        "source": "user",
                        "created_at": "2026-05-18T00:00:00+00:00",
                        "updated_at": "2026-05-18T00:00:00+00:00",
                    },
                    {
                        "id": "mem_2",
                        "type": "preference",
                        "summary": "Prefer concise portfolio updates.",
                        "details": "Keep status summaries short and evidence-backed.",
                        "tags": ["style"],
                        "visibility": "private",
                        "confidence": "medium",
                        "source": "user",
                        "created_at": "2026-05-18T01:00:00+00:00",
                        "updated_at": "2026-05-18T01:00:00+00:00",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )


def test_search_session_memory_finds_prior_decisions(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"
    write_memory(memory_path)

    result = search_session_memory(
        "What did we decide about finance review forecast?",
        memory_path=str(memory_path),
    )

    assert result["status"] == "success"
    assert result["results"][0]["id"] == "mem_1"
    assert result["results"][0]["type"] == "decision"
    assert result["results"][0]["confidence"] == "high"


def test_search_session_memory_can_filter_by_type_and_boost_tags(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"
    write_memory(memory_path)

    result = search_session_memory(
        "updates",
        memory_path=str(memory_path),
        memory_type="preference",
        tags=["style"],
    )

    assert [item["id"] for item in result["results"]] == ["mem_2"]


def test_search_session_memory_returns_empty_results_for_missing_file(tmp_path: Path) -> None:
    result = search_session_memory("anything", memory_path=str(tmp_path / "missing.json"))

    assert result["status"] == "success"
    assert result["results"] == []


def test_remember_session_fact_appends_memory(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"

    result = remember_session_fact(
        summary="Use finance review as the default monthly decision forum.",
        details="The user asked to remember this for future planning questions.",
        memory_type="preference",
        tags=["finance", "review"],
        memory_path=str(memory_path),
    )

    payload = json.loads(memory_path.read_text(encoding="utf-8"))

    assert result["status"] == "success"
    assert payload["memories"][0]["type"] == "preference"
    assert payload["memories"][0]["summary"].startswith("Use finance review")
    assert payload["memories"][0]["tags"] == ["finance", "review"]
    assert payload["memories"][0]["visibility"] == "private"


def test_list_session_memory_filters_by_tag(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"
    write_memory(memory_path)

    result = list_session_memory(memory_path=str(memory_path), tags=["finance"])

    assert result["status"] == "success"
    assert [item["id"] for item in result["results"]] == ["mem_1"]


def test_update_session_memory_changes_existing_memory(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"
    write_memory(memory_path)

    result = update_session_memory(
        "mem_1",
        summary="Finance Review should focus on budget risk.",
        tags=["finance", "budget"],
        confidence="medium",
        memory_path=str(memory_path),
    )

    assert result["status"] == "success"
    assert result["memory"]["summary"] == "Finance Review should focus on budget risk."
    assert result["memory"]["tags"] == ["budget", "finance"]
    assert result["memory"]["confidence"] == "medium"


def test_forget_session_memory_deletes_existing_memory(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"
    write_memory(memory_path)

    result = forget_session_memory("mem_1", memory_path=str(memory_path))
    remaining = list_session_memory(memory_path=str(memory_path))

    assert result["status"] == "success"
    assert result["forgotten_id"] == "mem_1"
    assert {item["id"] for item in remaining["results"]} == {"mem_2"}


def test_memory_update_and_delete_return_error_for_missing_id(tmp_path: Path) -> None:
    memory_path = tmp_path / "session_memory.json"
    write_memory(memory_path)

    update_result = update_session_memory(
        "missing",
        summary="Nope",
        memory_path=str(memory_path),
    )
    forget_result = forget_session_memory("missing", memory_path=str(memory_path))

    assert update_result["status"] == "error"
    assert forget_result["status"] == "error"
