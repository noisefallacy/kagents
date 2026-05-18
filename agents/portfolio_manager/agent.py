"""ADK root agent for the portfolio manager."""

from kagents.config import settings
from kagents.tools.context_loader import load_private_context
from kagents.tools.context_router import plan_context
from kagents.tools.document_search import search_documents
from kagents.tools.growth_context import load_growth_context
from kagents.tools.jquants import get_jquants_daily_quote
from kagents.tools.lseg import get_lseg_fx_history, plot_lseg_fx_history
from kagents.tools.org_context import search_org_context
from kagents.tools.session_memory import (
    forget_session_memory,
    list_session_memory,
    remember_session_fact,
    search_session_memory,
    update_session_memory,
)

try:
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.google_search_tool import GoogleSearchTool
except ImportError as exc:  # pragma: no cover - import guidance for first-time setup
    raise RuntimeError(
        "google-adk is not installed. Run scripts/bootstrap_venv.ps1 first."
    ) from exc

google_search = GoogleSearchTool(bypass_multi_tools_limit=True)


root_agent = Agent(
    model=settings.model,
    name="portfolio_manager",
    description=(
        "A simple portfolio manager assistant that answers business questions by "
        "loading growth context, planning relevant context, loading private context "
        "bundles, checking internal org context, searching local documents, using "
        "J-Quants market data when needed, plotting allowlisted LSEG FX history, "
        "and using web search for current external information."
    ),
    instruction=(
        "You are a portfolio manager assistant. Users will ask natural business "
        "questions without naming files or asking for document search explicitly. For "
        "most requests, use load_private_context first to plan the query and load "
        "available private context, including growth context such as user preferences, "
        "operating rules, and tool preferences. Use load_growth_context directly only "
        "when you need to inspect those growth inputs without loading detailed context. "
        "Use plan_context directly only when you need to inspect routing without "
        "loading context. Treat the plan as routing guidance, then call any dedicated "
        "external tools for selected routes before answering. "
        "If the user asks you to remember a decision, preference, or durable project "
        "fact, use remember_session_fact. If the user asks to inspect, correct, or "
        "remove remembered context, use list_session_memory, update_session_memory, "
        "or forget_session_memory. Do not invent private data; when internal context, "
        "rules, or endpoints are missing from configured data files, say what is "
        "missing and what data source would need to be updated. "
        "For acronyms, team names, project aliases, and internal terms, the private "
        "context bundle should include org context when that would help normalize "
        "the language. For most questions about plans, status, finance, priorities, "
        "risks, next steps, assumptions, or internal context, the private context "
        "bundle should include document search. Search document content rather than "
        "relying on file names. If the initial bundle is weak, call search_org_context "
        "or search_documents directly with a sharper follow-up query. If the user "
        "asks for market price data on a specific Japanese "
        "security and you have enough information to identify the code, use "
        "get_jquants_daily_quote. If the user asks for FX history or asks to plot "
        "an allowlisted FX pair such as USDJPY, EURJPY, GBPJPY, AUDJPY, EURUSD, or "
        "GBPUSD, use get_lseg_fx_history or plot_lseg_fx_history. If the user asks "
        "for a visual style, pass the requested style_name to the plotting tool. Do not use Google "
        "Search for these LSEG FX history/plot requests unless the user explicitly "
        "asks for public news or external commentary. If the user asks for current external information "
        "such as recent news, public company updates, or facts that are likely to "
        "have changed, use Google Search. If the first document search is weak, try "
        "once more with a shorter reformulation based on the user's core business "
        "terms. Answer from the evidence you found, cite file paths when useful for "
        "local documents, include source links when web search is used, and say "
        "clearly when you could not find support in the local documents, org context, "
        "API results, or web results."
    ),
    tools=[
        load_private_context,
        load_growth_context,
        plan_context,
        search_org_context,
        search_session_memory,
        remember_session_fact,
        list_session_memory,
        update_session_memory,
        forget_session_memory,
        search_documents,
        get_jquants_daily_quote,
        get_lseg_fx_history,
        plot_lseg_fx_history,
        google_search,
    ],
)
