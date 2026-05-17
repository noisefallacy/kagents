"""ADK root agent for the portfolio manager."""

from kagents.config import settings
from kagents.tools.document_search import search_documents
from kagents.tools.jquants import get_jquants_daily_quote

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
        "searching local documents first, using J-Quants market data when needed, "
        "and using web search for current external information."
    ),
    instruction=(
        "You are a portfolio manager assistant. Users will ask natural business "
        "questions without naming files or asking for document search explicitly. "
        "For most questions about plans, status, finance, priorities, risks, next "
        "steps, assumptions, or internal context, use search_documents first. Search "
        "document content rather than relying on file names. If the user asks for "
        "market price data on a specific Japanese security and you have enough "
        "information to identify the code, use get_jquants_daily_quote. If the user "
        "asks for current external information such as recent news, public company "
        "updates, or facts that are likely to have changed, use Google Search. If the "
        "first document search is weak, try once more with a shorter reformulation "
        "based on the user's core business terms. Answer from the evidence you found, "
        "cite file paths when useful for local documents, include source links when web "
        "search is used, and say clearly when you could not find support in the local "
        "documents, API results, or web results."
    ),
    tools=[search_documents, get_jquants_daily_quote, google_search],
)
