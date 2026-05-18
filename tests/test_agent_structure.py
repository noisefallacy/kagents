from pathlib import Path


def test_agent_directories_have_standard_runtime_files() -> None:
    agents_dir = Path(__file__).resolve().parents[1] / "agents"
    agent_dirs = [
        path
        for path in agents_dir.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name != "__pycache__"
    ]

    assert agent_dirs
    for agent_dir in agent_dirs:
        assert (agent_dir / "__init__.py").exists(), agent_dir
        assert (agent_dir / "agent.py").exists(), agent_dir
        assert (agent_dir / "server.py").exists(), agent_dir
        assert (agent_dir / "documents").is_dir(), agent_dir


def test_dockerfile_defaults_to_portfolio_manager_server() -> None:
    dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"

    content = dockerfile.read_text(encoding="utf-8")

    assert "agents.portfolio_manager.server:app" in content
    assert "playwright install --with-deps chromium" in content
