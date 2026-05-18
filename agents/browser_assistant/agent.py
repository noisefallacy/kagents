"""ADK specialist agent for guarded browser automation."""

from kagents.config import settings
from kagents.tools.browser_tasks import list_browser_tasks, run_browser_task

try:
    from google.adk.agents.llm_agent import Agent
except ImportError as exc:  # pragma: no cover - import guidance for first-time setup
    raise RuntimeError(
        "google-adk is not installed. Run scripts/bootstrap_venv.ps1 first."
    ) from exc


root_agent = Agent(
    model=settings.model,
    name="browser_assistant",
    description=(
        "Runs pre-approved Playwright browser workflows from local task definitions."
    ),
    instruction=(
        "You are a guarded browser automation assistant. Use list_browser_tasks "
        "to inspect available local workflows. Use run_browser_task only for a "
        "configured task_name from the local browser task file. Do not browse to "
        "arbitrary URLs, do not improvise clicks outside the configured workflow, "
        "and do not submit forms, upload files, purchase items, send messages, or "
        "change remote state. Browser workflows may extract visible text or save "
        "screenshots under outputs/browser/. Return extracted artifacts, visited "
        "URLs, and a short summary of what was captured."
    ),
    tools=[list_browser_tasks, run_browser_task],
)
