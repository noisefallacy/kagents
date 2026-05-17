"""Small local CLI for testing document search without launching ADK."""

from __future__ import annotations

import argparse
import json

from kagents.tools.document_search import search_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Search local documents.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--directory", default=None, help="Directory to search")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum results")
    args = parser.parse_args()

    result = search_documents(
        query=args.query,
        directory=args.directory,
        max_results=args.max_results,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
