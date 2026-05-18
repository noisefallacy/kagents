"""ADK root agent for guarded artifact generation."""

from kagents.config import settings
from kagents.tools.charting import create_chart_png
from kagents.tools.lseg import get_lseg_fx_history, plot_lseg_fx_history

try:
    from google.adk.agents.llm_agent import Agent
except ImportError as exc:  # pragma: no cover - import guidance for first-time setup
    raise RuntimeError(
        "google-adk is not installed. Run scripts/bootstrap_venv.ps1 first."
    ) from exc


root_agent = Agent(
    model=settings.model,
    name="artifact_assistant",
    description="Creates guarded local artifacts such as PNG charts under outputs/.",
    instruction=(
        "You are an artifact-generation assistant. Use create_chart_png when the "
        "user provides chart data for a simple line, bar, or scatter chart. Use "
        "plot_lseg_fx_history when the user asks to plot an allowed FX pair such as "
        "USDJPY from LSEG. If the user asks for a visual style, pass the requested "
        "style_name when calling chart tools. Use get_lseg_fx_history when the user asks for the data "
        "without a chart. Do not execute arbitrary code or write outside the allowed "
        "outputs directory. If the user's request requires unsupported instruments, "
        "unsupported file formats, or arbitrary code execution, explain the limitation "
        "and ask for supported inputs."
    ),
    tools=[create_chart_png, get_lseg_fx_history, plot_lseg_fx_history],
)
