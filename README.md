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

## Project Layout

```text
agents/
  artifact_assistant/
    agent.py
  doc_search/
    agent.py
  portfolio_manager/
    agent.py
data/
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

Recommended entrypoints:

- `portfolio_manager`: main user-facing agent
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

## Next Slices

1. ADK eval cases for context routing and tool trajectories
2. Session memory for prior portfolio-manager conversations
3. Better query reformulation for mixed Japanese and English requests
4. Broader market-data tools
5. Additional internal knowledge sources when access becomes available
