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
    jquants_api_key: str | None = os.getenv("JQUANTS_API_KEY")


settings = Settings()
