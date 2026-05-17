# Implementation Journal

This log captures both project progress and what we are learning about Google
ADK while building the app.

## 2026-05-17

### Initial project scaffold and document-search MVP

- Created the project skeleton around Google ADK with a structure that can be
  adapted later to an internal ADK-like interface.
- Added a document-search MVP that can search local `.txt`, `.md`, `.pdf`,
  `.docx`, `.xlsx`, and `.eml` files.
- Added CLI usage, tests, sample documents, and bootstrap scripts for the local
  virtual environment.

ADK learning:

- A minimal ADK app can stay very small when the agent delegates real work to
  plain Python tools.
- It is useful to keep tool logic outside the ADK agent file so the app remains
  testable without running the full ADK UI.

### Main entrypoint shifted to portfolio_manager

- Replaced the earlier `workspace_assistant` direction with a simpler
  `portfolio_manager` entrypoint while keeping `doc_search` as a specialist
  agent.
- Strengthened the agent instructions so users do not need to explicitly say
  "search docs" for document-backed questions.

ADK learning:

- A single main agent with a small toolset is a good early shape before moving
  into a more complex multi-agent design.
- Prompting and tool routing behavior can be improved materially just by
  tightening the agent instruction.

### Web search and J-Quants integration

- Added `GoogleSearchTool` to the main agent for current external information.
- Added a minimal direct J-Quants REST tool for daily quotes using API key
  authentication.
- Kept the J-Quants integration thin instead of introducing a heavier client
  dependency.

ADK learning:

- ADK can mix built-in tools and custom Python functions cleanly in a single
  agent.
- For an MVP, direct API tools can be easier to stabilize than a larger client
  library or external abstraction layer.

### MCP direction clarified

- Confirmed that ADK supports MCP integration through `McpToolset`.
- Identified the practical split between Codex-side MCP for development support
  and ADK-side MCP for runtime agent capabilities.

ADK learning:

- In ADK, MCP is best treated as another tool transport layer rather than as a
  separate agent architecture.
- `McpToolset` gives a clear extension path for future integrations such as
  J-Quants MCP without forcing an immediate rewrite of existing tools.
