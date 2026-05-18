# kagents

Custom agents built with Google ADK first, while keeping the project layout
easy to adapt to an internal ADK-like interface later.

This repository is also a learning project for Google ADK. Ongoing notes are
kept in [implementation_journal.md](C:/Users/kagin/kagents/docs/implementation_journal.md).
Context-management notes are kept in
[context_management.md](C:/Users/kagin/kagents/docs/context_management.md).

## Current MVP

The current user-facing entrypoint is `portfolio_manager`.

It currently combines:

- context planning to choose relevant private and external context sources
- private context bundle loading for local org context and documents
- growth context loading for user preferences, operating rules, and tool preferences
- JSON-backed session memory with search, create, list, update, and delete tools
- structured org context lookup for acronyms, team names, and project aliases
- local document search across `.txt`, `.md`, `.pdf`, `.docx`, `.xlsx`, and `.eml`
- J-Quants daily quote lookup
- Google Search for current external information
- guarded PNG chart generation under `outputs/`
- direct LSEG FX history retrieval and plotting for allowlisted pairs
- guarded Playwright browser workflows from local task definitions

## Project Layout

```text
agents/
  artifact_assistant/
    documents/
    agent.py
    server.py
  browser_assistant/
    documents/
    agent.py
    server.py
  doc_search/
    documents/
    agent.py
    server.py
  portfolio_manager/
    documents/
    agent.py
    server.py
data/
  browser_apps/
  browser_tasks/
  context/
    org_context.json
  docs/
prompts/
outputs/
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
- `KAGENT_SESSION_MEMORY_PATH`: durable local session-memory file
- `KAGENT_USER_PROFILE_PATH`: user or team preference profile
- `KAGENT_OPERATING_RULES_PATH`: data-first operating rules
- `KAGENT_TOOL_PREFERENCES_PATH`: tool usage preferences and routing hints
- `KAGENT_CHART_STYLES_PATH`: named PNG chart styles
- `KAGENT_BROWSER_TASKS_PATH`: allowlisted browser workflow definitions
- `JQUANTS_API_KEY`: J-Quants API V2 key
- `LSEG_SESSION_METHOD`: `remote` or `desktop`
- `LSEG_APP_KEY`: LSEG platform app key for remote sessions
- `LSEG_USERNAME`: LSEG username for remote sessions
- `LSEG_PASSWORD`: LSEG password for remote sessions

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

Run a single agent as a FastAPI app:

```powershell
.\.venv\Scripts\uvicorn.exe agents.portfolio_manager.server:app --host 0.0.0.0 --port 8000
```

Every agent directory follows the same runtime shape:

```text
__init__.py
agent.py
server.py
documents/
```

`server.py` wraps that folder's ADK `root_agent` in a small FastAPI app with
`/health`, `/agent`, and `/run` endpoints. `documents/` is reserved for data
that belongs to that specific agent.

Recommended entrypoints:

- `portfolio_manager`: main user-facing agent
- `browser_assistant`: guarded Playwright browser workflows
- `doc_search`: specialist document-search agent
- `artifact_assistant`: guarded PNG chart generation

Saved test prompts:

- `doc_search`: [doc_search_test_prompts.md](C:/Users/kagin/kagents/prompts/doc_search_test_prompts.md)
- `portfolio_manager`: [portfolio_manager_test_prompts.md](C:/Users/kagin/kagents/prompts/portfolio_manager_test_prompts.md)

Create a simple chart through `artifact_assistant`:

```text
Create a line chart titled Monthly Revenue with x values Jan, Feb, Mar and y values 10, 12, 15. Save it to outputs/monthly_revenue.png.
```

Use a named chart style from `data/context/chart_styles.json`:

```text
Create a line chart titled Monthly Revenue with x values Jan, Feb, Mar and y values 10, 12, 15. Use the presentation style and save it to outputs/monthly_revenue.png.
```

Plot an allowlisted FX pair through LSEG:

```text
Plot USDJPY from 2026-01-01 to 2026-03-31 using the presentation style and save it to outputs/usdjpy.png.
```

`portfolio_manager` can also route this request directly; you do not need to
switch to `artifact_assistant` for allowlisted FX plots.

Run the sample local browser workflow through `browser_assistant`:

```text
List browser tasks, then run sample_portal_market_note.
```

Browser workflows are configured in `data/browser_tasks/browser_tasks.json`.
The included sample opens `data/browser_apps/sample_portal.html`, clicks
`Show Market Note`, extracts visible page text, and saves artifacts under
`outputs/browser/`. To run Playwright locally for the first time, install the
browser binary after installing requirements:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

Take a TradingView USDJPY 1h screenshot:

```text
Run tradingview_usdjpy_1h_screenshot.
```

The browser task runner currently supports read-only workflow actions such as
`wait_for_selector`, `wait_ms`, `click_text`, `click_selector`,
`fill_selector`, `press_key`, `extract_text`, and `screenshot`. Screenshots are
restricted to that task's folder under `outputs/browser/`.

## Docker

Build the container:

```powershell
docker build -t kagents .
```

Run the default `portfolio_manager` server:

```powershell
docker run --env-file .env -p 8000:8000 kagents
```

The Dockerfile installs `requirements.txt`, the local package, and Playwright
Chromium. To serve a different agent, override the command, for example:

```powershell
docker run --env-file .env -p 8000:8000 kagents uvicorn agents.browser_assistant.server:app --host 0.0.0.0 --port 8000
```

## Next Slices

1. ADK eval cases for context routing and tool trajectories
2. Session memory for prior portfolio-manager conversations
3. Better query reformulation for mixed Japanese and English requests
4. Broader market-data tools
5. Additional internal knowledge sources when access becomes available
