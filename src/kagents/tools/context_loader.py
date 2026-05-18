"""Load private context sources selected by the context router."""

from __future__ import annotations

from typing import Any, Callable

from kagents.tools.context_router import plan_context
from kagents.tools.growth_context import load_growth_context


ContextSearch = Callable[..., dict[str, Any]]


def _search_org_context(**kwargs: Any) -> dict[str, Any]:
    from kagents.tools.org_context import search_org_context

    return search_org_context(**kwargs)


def _search_documents(**kwargs: Any) -> dict[str, Any]:
    from kagents.tools.document_search import search_documents

    return search_documents(**kwargs)


def _search_session_memory(**kwargs: Any) -> dict[str, Any]:
    from kagents.tools.session_memory import search_session_memory

    return search_session_memory(**kwargs)


PRIVATE_CONTEXT_LOADERS: dict[str, ContextSearch] = {
    "org_context": _search_org_context,
    "documents": _search_documents,
    "session_memory": _search_session_memory,
}


def load_private_context(
    query: str,
    max_routes: int = 4,
    max_results_per_source: int = 3,
) -> dict[str, Any]:
    """
    Plan and load private context sources relevant to a user query.

    Args:
        query: Natural-language user query.
        max_routes: Maximum number of planned context routes to inspect.
        max_results_per_source: Maximum number of results per loaded source.
    """

    growth_context = load_growth_context(query=query)
    plan = plan_context(query=query, max_routes=max_routes)
    loaded_context: list[dict[str, Any]] = []
    unavailable_context: list[dict[str, Any]] = []
    external_context: list[dict[str, Any]] = []

    for route in plan["routes"]:
        source = route["source"]
        loader = PRIVATE_CONTEXT_LOADERS.get(source)

        if loader:
            loaded_context.append(
                {
                    "source": source,
                    "route": route,
                    "result": loader(query=query, max_results=max_results_per_source),
                }
            )
            continue

        if route["tool"] is None:
            unavailable_context.append(
                {
                    "source": source,
                    "route": route,
                    "status": "not_implemented",
                }
            )
            continue

        external_context.append(
            {
                "source": source,
                "route": route,
                "status": "use_dedicated_tool",
                "tool": route["tool"],
            }
        )

    return {
        "status": "success",
        "query": query,
        "growth_context": growth_context,
        "plan": plan,
        "loaded_context": loaded_context,
        "unavailable_context": unavailable_context,
        "external_context": external_context,
    }
