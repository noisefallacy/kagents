from pathlib import Path

from openpyxl import Workbook

from kagents.config import resolve_project_path
from kagents.document_store import search_directory
from kagents.tools.document_search import search_documents
from kagents.tools.jquants import normalize_security_code


def test_search_directory_ranks_matching_documents(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "alpha.txt").write_text("budget forecast and revenue planning", encoding="utf-8")
    (docs_dir / "beta.md").write_text("engineering roadmap and agent work", encoding="utf-8")

    results = search_directory(docs_dir, query="budget revenue", max_results=5)

    assert len(results) == 1
    assert results[0].path.endswith("alpha.txt")
    assert results[0].score >= 2


def test_search_documents_returns_error_for_missing_directory(tmp_path: Path) -> None:
    result = search_documents("anything", directory=str(tmp_path / "missing"))

    assert result["status"] == "error"
    assert result["results"] == []


def test_resolve_project_path_makes_relative_paths_absolute() -> None:
    resolved = Path(resolve_project_path("data/docs"))

    assert resolved.is_absolute()
    assert resolved.name == "docs"


def test_search_directory_reads_email_and_spreadsheet_content(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    email_file = docs_dir / "team_update.eml"
    email_file.write_text(
        "\n".join(
            [
                "From: pm@example.com",
                "To: team@example.com",
                "Subject: Tuesday sync",
                "",
                "Please review the budget forecast before the client meeting.",
            ]
        ),
        encoding="utf-8",
    )

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Pipeline"
    sheet.append(["Topic", "Value"])
    sheet.append(["Revenue planning", "Priority"])
    workbook.save(docs_dir / "numbers.xlsx")

    results = search_directory(docs_dir, query="budget forecast revenue planning", max_results=5)

    returned_paths = {Path(result.path).name for result in results}
    assert "team_update.eml" in returned_paths
    assert "numbers.xlsx" in returned_paths


def test_normalize_security_code_appends_zero_for_four_digit_codes() -> None:
    assert normalize_security_code("7203") == "72030"
    assert normalize_security_code("72030") == "72030"
