import json
from pathlib import Path

from kagents.tools.org_context import search_org_context


def test_search_org_context_finds_acronym_and_team_aliases(tmp_path: Path) -> None:
    context_path = tmp_path / "org_context.json"
    context_path.write_text(
        json.dumps(
            {
                "acronyms": {
                    "FR": {
                        "meaning": "Finance Review",
                        "notes": "Monthly review process.",
                    }
                },
                "teams": {
                    "finance": {
                        "description": "Owns budget and forecast work.",
                        "aliases": ["finance team"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    result = search_org_context("finance review finance team", context_path=str(context_path))

    assert result["status"] == "success"
    names = {item["name"] for item in result["results"]}
    assert "FR" in names
    assert "finance" in names


def test_search_org_context_returns_error_for_missing_file(tmp_path: Path) -> None:
    result = search_org_context("finance", context_path=str(tmp_path / "missing.json"))

    assert result["status"] == "error"
    assert result["results"] == []
