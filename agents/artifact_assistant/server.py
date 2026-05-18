"""FastAPI server entrypoint for artifact_assistant."""

from kagents.adk_server import create_agent_app, run_app

from .agent import root_agent


app = create_agent_app(root_agent)


if __name__ == "__main__":
    run_app(app)
