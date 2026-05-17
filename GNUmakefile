.PHONY: help activate activate-bash activate-pwsh shell-bash bootstrap test search

help:
	@echo "Available targets:"
	@echo "  make bootstrap      Create/update the local virtual environment"
	@echo "  make activate       Print the Git Bash activation command"
	@echo "  make activate-bash  Print the Git Bash activation command"
	@echo "  make activate-pwsh  Print the PowerShell activation command"
	@echo "  make shell-bash     Start a Git Bash shell with the venv activated"
	@echo "  make test           Run pytest in the venv"
	@echo "  make search QUERY='budget forecast'  Run the local CLI search"

bootstrap:
	powershell -ExecutionPolicy Bypass -File ./scripts/bootstrap_venv.ps1

activate: activate-bash

activate-bash:
	@echo "source .venv/Scripts/activate"

activate-pwsh:
	@echo ".\\.venv\\Scripts\\Activate.ps1"

shell-bash:
	@"C:/Program Files/Git/bin/bash.exe" -lc "source .venv/Scripts/activate && exec bash"

test:
	./.venv/Scripts/python.exe -m pytest

search:
	./.venv/Scripts/python.exe -m kagents.cli "$(QUERY)" --directory data/docs
