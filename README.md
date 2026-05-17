# kagents

Custom agents built with Google ADK first, while keeping the project layout
easy to adapt to an internal ADK-like interface later.

This repository is also a learning project for Google ADK. Ongoing notes are
kept in [implementation_journal.md](C:/Users/kagin/kagents/docs/implementation_journal.md).

## Current MVP

The current user-facing entrypoint is `portfolio_manager`.

It currently combines:

- structured org context lookup for acronyms, team names, and project aliases
- local document search across `.txt`, `.md`, `.pdf`, `.docx`, `.xlsx`, and `.eml`
- J-Quants daily quote lookup
- Google Search for current external information

## Project Layout

```text
agents/
  doc_search/
    agent.py
  portfolio_manager/
    agent.py
data/
  context/
    org_context.json
  docs/
prompts/
scripts/
src/
  kagents/
    cli.py
    config.py
    document_store.py
    tools/
tests/
```

## Virtual Environment

Create and install the local environment:

```powershell
.\scripts\bootstrap_venv.ps1
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

## Configuration

Store local settings in `.env`.

- `GOOGLE_API_KEY`: Gemini / ADK access
- `KAGENT_MODEL`: model name for the ADK agent
- `KAGENT_DOCS_DIR`: local document directory
- `KAGENT_ORG_CONTEXT_PATH`: structured internal context file
- `JQUANTS_API_KEY`: J-Quants API V2 key

## Local Usage

Search local docs from the CLI:

```powershell
.\.venv\Scripts\python.exe -m kagents.cli "quarterly revenue"
```

## ADK Usage

Run the ADK UI from the `agents` directory:

```powershell
cd .\agents
..\.venv\Scripts\adk.exe web
```

Recommended entrypoints:

- `portfolio_manager`: main user-facing agent
- `doc_search`: specialist document-search agent

Saved test prompts:

- `doc_search`: [doc_search_test_prompts.md](C:/Users/kagin/kagents/prompts/doc_search_test_prompts.md)
- `portfolio_manager`: [portfolio_manager_test_prompts.md](C:/Users/kagin/kagents/prompts/portfolio_manager_test_prompts.md)

## Next Slices

1. Broader market-data tools
2. Better query reformulation for mixed Japanese and English requests
3. Safe code execution tools
4. Additional internal knowledge sources when access becomes available
