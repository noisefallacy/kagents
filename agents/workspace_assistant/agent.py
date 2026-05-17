"""ADK root agent for the main workspace assistant."""

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
    name="workspace_assistant",
    description=(
        "General-purpose workspace assistant that can answer questions about local "
        "documents and is designed to grow into API and execution capabilities."
    ),
    instruction=(
        "You are the main workspace assistant for this project. Users will usually ask "
        "natural questions without naming the data source or tool they want. When a "
        "question may depend on project documents, notes, reports, plans, or other local "
        "files, call search_documents first before answering. Base your answer on the "
        "search results, cite matched file paths when relevant, and clearly say when you "
        "could not find supporting information. Right now your available capability is "
        "document search, but your design should remain compatible with future API-fetch "
        "and code-execution tools."
    ),
    tools=[search_documents],
)
