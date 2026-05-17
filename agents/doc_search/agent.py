"""ADK root agent for the document-search MVP."""

from kagents.config import settings
from kagents.tools.document_search import search_documents

try:
    from google.adk.agents.llm_agent import Agent
except ImportError as exc:  # pragma: no cover - import guidance for first-time setup
    raise RuntimeError(
        "google-adk is not installed. Run scripts/bootstrap_venv.ps1 first."
    ) from exc


root_agent = Agent(
    model=settings.model,
    name="doc_search_agent",
    description="Searches local documents and returns relevant excerpts.",
    instruction=(
        "You are a document search assistant. Use the search_documents tool whenever "
        "the user asks questions that depend on local files. Cite the matched file path "
        "and excerpt in your answer. If nothing relevant is found, say so clearly."
    ),
    tools=[search_documents],
)
