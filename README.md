# kagents

Custom agents built with Google ADK first, while keeping the project layout easy to adapt to an internal ADK-like interface later.

This repository is also a learning project for Google ADK. Ongoing notes are
kept in [implementation_journal.md](C:/Users/kagin/kagents/docs/implementation_journal.md).

## Current MVP

The first slice is a `doc_search` capability that can search local:

- `.txt`
- `.md`
- `.pdf`
- `.docx`
- `.xlsx`
- `.eml`

The current user-facing entrypoint is `portfolio_manager`.

## Project Layout

```text
agents/
  doc_search/
    agent.py               # specialist document-search agent
  portfolio_manager/
    agent.py               # main user-facing agent entrypoint
src/
  kagents/
    config.py
    document_store.py
    cli.py
    tools/
      document_search.py
scripts/
  bootstrap_venv.ps1
tests/
data/
  docs/
prompts/
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

## Local Usage

Put documents under `data/docs/`, then run:

```powershell
.\.venv\Scripts\python.exe -m kagents.cli "quarterly revenue"
```

Environment variables:

- `GOOGLE_API_KEY`: Gemini / ADK 用
- `JQUANTS_API_KEY`: J-Quants API V2 用
- `KAGENT_MODEL`: ADK で使うモデル名
- `KAGENT_DOCS_DIR`: 文書検索対象ディレクトリ

Saved test prompts:

- `doc_search`: [doc_search_test_prompts.md](C:/Users/kagin/kagents/prompts/doc_search_test_prompts.md)
- `portfolio_manager`: [portfolio_manager_test_prompts.md](C:/Users/kagin/kagents/prompts/portfolio_manager_test_prompts.md)

## ADK Usage

Add your API key to `.env`, then run:

```powershell
.\.venv\Scripts\adk web
```

Recommended entrypoint:

- `portfolio_manager`: main user-facing agent for natural business questions
- `doc_search`: specialist document-search agent

Example prompts for `portfolio_manager`:

- `今の優先事項を教えて`
- `finance チーム向けに何を準備する必要がありますか`
- `この案件の次のアクションをまとめて`
- `7203 の 2026-03-14 の終値を教えて`
- `今日のトヨタに関する最新ニュースを教えて`

Current tool coverage in `portfolio_manager`:

- local document search
- J-Quants daily quote lookup
- Google Search for current external information

## Next Slices

1. API tools for external data fetches
2. Document indexing and chunking
3. Safe code execution tools
4. Routing across search, API, and execution capabilities from the main agent
