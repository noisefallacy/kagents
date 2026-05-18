from typing import Any

from kagents.tools import context_loader
from kagents.tools.context_loader import load_private_context


def test_load_private_context_loads_org_context(monkeypatch: Any) -> None:
    def fake_growth_context(**kwargs: Any) -> dict[str, Any]:
        return {"status": "success", "query": kwargs["query"], "growth_context": {}}

    def fake_org_context(**kwargs: Any) -> dict[str, Any]:
        return {
            "status": "success",
            "query": kwargs["query"],
            "results": [{"name": "FR", "details": {"meaning": "Finance Review"}}],
        }

    monkeypatch.setattr(context_loader, "load_growth_context", fake_growth_context)
    monkeypatch.setitem(
        context_loader.PRIVATE_CONTEXT_LOADERS,
        "org_context",
        fake_org_context,
    )

    result = load_private_context("What does FR mean?")

    assert result["status"] == "success"
    assert result["loaded_context"][0]["source"] == "org_context"
    assert result["loaded_context"][0]["result"]["results"][0]["name"] == "FR"


def test_load_private_context_loads_session_memory(monkeypatch: Any) -> None:
    def fake_growth_context(**kwargs: Any) -> dict[str, Any]:
        return {"status": "success", "query": kwargs["query"], "growth_context": {}}

    def fake_session_memory(**kwargs: Any) -> dict[str, Any]:
        return {
            "status": "success",
            "query": kwargs["query"],
            "results": [{"id": "mem_1", "summary": "Prior decision"}],
        }

    monkeypatch.setattr(context_loader, "load_growth_context", fake_growth_context)
    monkeypatch.setitem(
        context_loader.PRIVATE_CONTEXT_LOADERS,
        "session_memory",
        fake_session_memory,
    )

    result = load_private_context("What did we decide last time?")
    loaded_sources = {
        item["source"] for item in result["loaded_context"]
    }

    assert "session_memory" in loaded_sources


def test_load_private_context_leaves_market_data_to_dedicated_tool() -> None:
    result = load_private_context("Show me the close price for 7203.")

    external_tools = {
        item["tool"] for item in result["external_context"]
    }

    assert "get_jquants_daily_quote" in external_tools


def test_load_private_context_includes_growth_context(monkeypatch: Any) -> None:
    def fake_growth_context(**kwargs: Any) -> dict[str, Any]:
        return {
            "status": "success",
            "query": kwargs["query"],
            "growth_context": {
                "user_profile": {
                    "preferences": [{"id": "pref_1"}],
                }
            },
        }

    monkeypatch.setattr(context_loader, "load_growth_context", fake_growth_context)

    result = load_private_context("What are the risks?")

    assert result["growth_context"]["growth_context"]["user_profile"]["preferences"][0]["id"] == "pref_1"
