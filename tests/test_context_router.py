from kagents.tools.context_router import plan_context


def route_sources(query: str) -> list[str]:
    result = plan_context(query)
    return [route["source"] for route in result["routes"]]


def test_plan_context_routes_acronym_questions_to_org_context() -> None:
    result = plan_context("What does FR mean?")

    assert result["status"] == "success"
    assert result["routes"][0]["source"] == "org_context"
    assert result["routes"][0]["tool"] == "search_org_context"


def test_plan_context_routes_private_business_questions_to_documents() -> None:
    sources = route_sources("What are the current project risks and next steps?")

    assert "documents" in sources


def test_plan_context_routes_security_codes_to_market_data() -> None:
    result = plan_context("Show me the close price for 7203 on 2026-02-20.")

    assert result["routes"][0]["source"] == "market_data"
    assert result["routes"][0]["tool"] == "get_jquants_daily_quote"


def test_plan_context_routes_current_public_questions_to_web() -> None:
    sources = route_sources("Tell me the latest public news about Toyota today.")

    assert "web" in sources


def test_plan_context_routes_fx_plot_requests_to_lseg() -> None:
    result = plan_context("Plot USDJPY from 2024-05-01 to 2024-05-03.")

    assert result["routes"][0]["source"] == "lseg_fx"
    assert result["routes"][0]["tool"] == "plot_lseg_fx_history"


def test_plan_context_identifies_session_memory_needs() -> None:
    result = plan_context("What did we decide last time about the finance review?")

    sources = route_sources("What did we decide last time about the finance review?")

    assert "session_memory" in sources
    memory_routes = [
        route for route in result["available_tool_routes"] if route["source"] == "session_memory"
    ]
    assert memory_routes[0]["tool"] == "search_session_memory"
