"""Project configuration."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_project_path(path_value: str) -> str:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return str(candidate)

    return str((PROJECT_ROOT / candidate).resolve())


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("KAGENT_MODEL", "gemini-flash-latest")
    docs_dir: str = resolve_project_path(os.getenv("KAGENT_DOCS_DIR", "data/docs"))
    org_context_path: str = resolve_project_path(
        os.getenv("KAGENT_ORG_CONTEXT_PATH", "data/context/org_context.json")
    )
    session_memory_path: str = resolve_project_path(
        os.getenv("KAGENT_SESSION_MEMORY_PATH", "data/context/session_memory.json")
    )
    user_profile_path: str = resolve_project_path(
        os.getenv("KAGENT_USER_PROFILE_PATH", "data/context/user_profile.json")
    )
    operating_rules_path: str = resolve_project_path(
        os.getenv("KAGENT_OPERATING_RULES_PATH", "data/context/operating_rules.json")
    )
    tool_preferences_path: str = resolve_project_path(
        os.getenv("KAGENT_TOOL_PREFERENCES_PATH", "data/context/tool_preferences.json")
    )
    chart_styles_path: str = resolve_project_path(
        os.getenv("KAGENT_CHART_STYLES_PATH", "data/context/chart_styles.json")
    )
    jquants_api_key: str | None = os.getenv("JQUANTS_API_KEY")
    lseg_session_method: str = os.getenv("LSEG_SESSION_METHOD", "remote")
    lseg_app_key: str | None = os.getenv("LSEG_APP_KEY")
    lseg_username: str | None = os.getenv("LSEG_USERNAME")
    lseg_password: str | None = os.getenv("LSEG_PASSWORD")


settings = Settings()
