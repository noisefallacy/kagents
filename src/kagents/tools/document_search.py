"""ADK-compatible tool for document search."""

from __future__ import annotations

from pathlib import Path

from kagents.config import settings
from kagents.document_store import search_directory


def search_documents(query: str, directory: str | None = None, max_results: int = 5) -> dict:
    """
    Search supported documents in a local directory and return ranked matches.

    Args:
        query: Natural-language search query.
        directory: Directory to search. Defaults to KAGENT_DOCS_DIR.
        max_results: Maximum number of results to return.
    """

    search_root = Path(directory or settings.docs_dir)

    if not search_root.exists():
        return {
            "status": "error",
            "message": f"Directory not found: {search_root}",
            "results": [],
        }

    hits = search_directory(search_root, query=query, max_results=max_results)
    return {
        "status": "success",
        "query": query,
        "directory": str(search_root),
        "results": [
            {"path": hit.path, "score": hit.score, "excerpt": hit.excerpt}
            for hit in hits
        ],
    }
