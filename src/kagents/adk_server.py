"""FastAPI wrappers for single ADK agents."""

from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Minimal request body for a single-turn agent run."""

    message: str = Field(..., min_length=1)
    user_id: str = "local-user"
    session_id: str | None = None


class AgentRunResponse(BaseModel):
    """Minimal response body for a single-turn agent run."""

    app_name: str
    user_id: str
    session_id: str
    text: str
    event_count: int


def _event_text(event: Any) -> list[str]:
    content = getattr(event, "content", None)
    parts = getattr(content, "parts", None)
    if not parts:
        return []

    return [
        part.text
        for part in parts
        if getattr(part, "text", None)
    ]


def create_agent_app(root_agent: Any, app_name: str | None = None) -> FastAPI:
    """Wrap an ADK root agent in a small FastAPI application."""

    resolved_app_name = app_name or getattr(root_agent, "name", "kagent")
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=resolved_app_name,
        agent=root_agent,
        session_service=session_service,
        auto_create_session=True,
    )

    app = FastAPI(
        title=f"{resolved_app_name} server",
        version="0.1.0",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "app_name": resolved_app_name}

    @app.get("/agent")
    def agent_info() -> dict[str, str]:
        return {
            "name": getattr(root_agent, "name", resolved_app_name),
            "description": getattr(root_agent, "description", ""),
        }

    @app.post("/run", response_model=AgentRunResponse)
    def run_agent(request: AgentRunRequest) -> AgentRunResponse:
        session_id = request.session_id or str(uuid4())
        session = session_service.get_session_sync(
            app_name=resolved_app_name,
            user_id=request.user_id,
            session_id=session_id,
        )
        if session is None:
            session_service.create_session_sync(
                app_name=resolved_app_name,
                user_id=request.user_id,
                session_id=session_id,
            )

        message = types.Content(
            role="user",
            parts=[types.Part(text=request.message)],
        )
        events = list(
            runner.run(
                user_id=request.user_id,
                session_id=session_id,
                new_message=message,
            )
        )
        text_parts: list[str] = []
        for event in events:
            text_parts.extend(_event_text(event))

        return AgentRunResponse(
            app_name=resolved_app_name,
            user_id=request.user_id,
            session_id=session_id,
            text="\n".join(text_parts).strip(),
            event_count=len(events),
        )

    return app


def run_app(app: FastAPI) -> None:
    """Run a FastAPI app with uvicorn."""

    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
