"""Query routing for portfolio-manager context sources."""

from __future__ import annotations

import re
from typing import Any


CONTEXT_SOURCES: dict[str, dict[str, Any]] = {
    "org_context": {
        "tool": "search_org_context",
        "description": "Internal acronyms, team names, project aliases, and terminology.",
    },
    "documents": {
        "tool": "search_documents",
        "description": "Private local documents, emails, spreadsheets, notes, and reports.",
    },
    "market_data": {
        "tool": "get_jquants_daily_quote",
        "description": "Japanese security quotes and historical market data.",
    },
    "lseg_fx": {
        "tool": "plot_lseg_fx_history",
        "description": "Allowlisted LSEG FX history and FX chart generation.",
    },
    "web": {
        "tool": "google_search",
        "description": "Current public information, recent news, and external facts.",
    },
    "session_memory": {
        "tool": "search_session_memory",
        "description": "Prior conversation context or user-specific memory.",
    },
    "artifacts": {
        "tool": None,
        "description": "Uploaded or generated files attached to the current session.",
    },
}


ROUTE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "org_context": (
        "acronym",
        "alias",
        "means",
        "meaning",
        "stand for",
        "team",
        "project",
        "org",
        "internal term",
        "とは",
        "意味",
        "チーム",
        "略語",
    ),
    "documents": (
        "plan",
        "plans",
        "priority",
        "priorities",
        "risk",
        "risks",
        "status",
        "next action",
        "next step",
        "prepare",
        "budget",
        "forecast",
        "revenue",
        "finance",
        "document",
        "docs",
        "email",
        "spreadsheet",
        "notes",
        "internal",
        "準備",
        "予算",
        "見通し",
        "売上",
        "資料",
        "議事録",
    ),
    "market_data": (
        "stock",
        "security",
        "quote",
        "price",
        "close",
        "open",
        "ohlc",
        "j-quants",
        "jquants",
        "株価",
        "終値",
        "始値",
    ),
    "lseg_fx": (
        "fx",
        "foreign exchange",
        "currency",
        "exchange rate",
        "usdjpy",
        "eurjpy",
        "gbpjpy",
        "audjpy",
        "eurusd",
        "gbpusd",
        "lseg",
        "plot",
        "chart",
        "為替",
    ),
    "web": (
        "latest",
        "today",
        "current",
        "recent",
        "news",
        "public",
        "external",
        "now",
        "最新",
        "今日",
        "ニュース",
        "現在",
    ),
    "session_memory": (
        "last time",
        "earlier",
        "previous",
        "before",
        "remember",
        "we discussed",
        "we decided",
        "前回",
        "以前",
        "覚えて",
        "決めた",
    ),
    "artifacts": (
        "uploaded",
        "attached",
        "attachment",
        "file i sent",
        "this file",
        "report",
        "artifact",
        "添付",
        "アップロード",
    ),
}


def _contains_keyword(text: str, keyword: str) -> bool:
    if re.search(r"[A-Za-z0-9]", keyword):
        return keyword in text
    return keyword in text


def _has_security_code(query: str) -> bool:
    return bool(re.search(r"\b\d{4,5}\b", query))


def _has_acronym(query: str) -> bool:
    return bool(re.search(r"\b[A-Z]{2,6}\b", query))


def _has_allowed_fx_pair(query: str) -> bool:
    compact_query = re.sub(r"[^A-Za-z]", "", query).upper()
    allowed_pairs = ("USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "EURUSD", "GBPUSD")
    return any(pair in compact_query for pair in allowed_pairs)


def plan_context(query: str, max_routes: int = 4) -> dict[str, Any]:
    """
    Plan which context sources should be loaded for a user query.

    Args:
        query: Natural-language user query.
        max_routes: Maximum number of context routes to return.
    """

    normalized_query = query.strip()
    lowered_query = normalized_query.lower()
    route_scores: dict[str, int] = {}
    route_reasons: dict[str, list[str]] = {}

    for source, keywords in ROUTE_KEYWORDS.items():
        for keyword in keywords:
            if _contains_keyword(lowered_query, keyword):
                route_scores[source] = route_scores.get(source, 0) + 1
                route_reasons.setdefault(source, []).append(f"matched '{keyword}'")

    if _has_security_code(normalized_query):
        route_scores["market_data"] = route_scores.get("market_data", 0) + 3
        route_reasons.setdefault("market_data", []).append("found a 4- or 5-digit security code")

    if _has_allowed_fx_pair(normalized_query):
        route_scores["lseg_fx"] = route_scores.get("lseg_fx", 0) + 4
        route_reasons.setdefault("lseg_fx", []).append("found an allowlisted FX pair")

    if _has_acronym(normalized_query):
        route_scores["org_context"] = route_scores.get("org_context", 0) + 2
        route_reasons.setdefault("org_context", []).append("found an uppercase acronym-like term")

    if not route_scores:
        route_scores["documents"] = 1
        route_reasons["documents"] = ["default private-context route for business questions"]

    routes = []
    for source, score in sorted(
        route_scores.items(),
        key=lambda item: (-item[1], item[0]),
    )[:max_routes]:
        source_config = CONTEXT_SOURCES[source]
        priority = "high" if score >= 3 else "medium" if score == 2 else "low"
        routes.append(
            {
                "source": source,
                "priority": priority,
                "score": score,
                "tool": source_config["tool"],
                "description": source_config["description"],
                "reasons": route_reasons[source],
            }
        )

    return {
        "status": "success",
        "query": normalized_query,
        "routes": routes,
        "available_tool_routes": [route for route in routes if route["tool"]],
        "unimplemented_routes": [route for route in routes if route["tool"] is None],
    }
