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

### Internal org-context layer

- Added a small structured org-context file for acronyms, team names, and
  project aliases.
- Added a `search_org_context` tool and connected it to `portfolio_manager`
  for internal terminology questions.

ADK learning:

- Not all internal context should be treated as unstructured document search.
- A small, explicit normalization layer can improve tool routing and answer
  consistency without needing a heavier knowledge system.

## 2026-05-18

### Context routing direction

- Added a deterministic `plan_context` tool that routes user questions toward
  org context, documents, market data, web search, session memory, or artifacts.
- Wired the portfolio manager to call `plan_context` before loading detailed
  context for most requests.
- Documented the context-source model and the first ADK evaluation targets.

ADK learning:

- Context routing is a useful explicit tool because ADK traces and evals can
  inspect whether the agent selected the right sources before it answered.
- Missing future capabilities such as session memory can still be represented
  as planned routes, which makes the roadmap testable before every backend is
  implemented.

### Starter ADK context-routing evals

- Added an example ADK eval set for portfolio-manager context routing.
- Covered org acronym lookup, private document lookup, J-Quants quote routing,
  current-news web routing, and the session-memory gap.
- Added a lightweight local test that validates the eval JSON shape without
  requiring ADK runtime credentials.

ADK learning:

- Eval cases are a good way to make routing expectations concrete because each
  turn can specify both final response text and expected tool trajectory.
- For early routing work, lenient response thresholds are useful while keeping
  tool trajectory expectations relatively strict.

### Private context bundle loader

- Added `load_private_context` as the normal first tool for portfolio-manager
  requests.
- The loader plans the query, loads implemented private sources such as org
  context and documents, reports unavailable private sources such as session
  memory and artifacts, and leaves external routes to dedicated tools.
- Updated the portfolio-manager instruction to use the private context bundle
  before answering or calling external tools.

ADK learning:

- A context loader can make private context management observable as one ADK
  tool call while still preserving the lower-level search tools for refinement.
- Separating private context loading from external tools keeps source freshness,
  credentials, and citation rules easier to reason about.

### Local session memory

- Added JSON-backed session-memory tools for searching prior decisions and
  remembering durable project facts or preferences.
- Added a sample memory file under `data/context/session_memory.json` and a
  `KAGENT_SESSION_MEMORY_PATH` setting.
- Wired session memory into `load_private_context` so "last time" and
  "remembered decision" questions load memory with other private context.

ADK learning:

- A local memory tool is a useful stepping stone before adopting managed ADK
  memory services because the schema and retrieval behavior stay transparent.
- Memory write operations should be explicit and user-directed at this stage;
  automatic summarization can come later once eval coverage is stronger.

### Memory governance tools and data-first architecture

- Added list, update, and delete tools for local session memory so durable
  context can be inspected and corrected.
- Added normalized memory metadata for type, tags, visibility, confidence,
  source, and timestamps.
- Added a session-memory template so real internal context can be supplied by
  replacing data rather than changing tool code.

ADK learning:

- Real-use memory needs correction and deletion paths before it becomes
  trustworthy.
- Keeping internal rules and remembered facts in data files makes the ADK tool
  architecture reusable across private deployments.

### Growth context layer

- Added data-first growth context files for user profile, operating rules, and
  tool preferences.
- Added `load_growth_context` and included it in `load_private_context` so
  preferences and operating rules are always considered before detailed context
  retrieval.
- Added templates for replacing sample growth data with real private settings
  later without changing Python code.

ADK learning:

- The "grow the tool" experience can be modeled as lightweight, always-loaded
  guidance plus route-specific context retrieval.
- Separating stable preferences/rules from session memory keeps enduring user
  taste distinct from facts learned during conversation.

### Guarded chart artifact generation

- Added a controlled `create_chart_png` tool for line, bar, and scatter charts.
- Added an `artifact_assistant` entrypoint for guarded artifact generation.
- Restricted chart output to `.png` files under `outputs/` and added validation
  for chart type, path, data lengths, numeric values, and maximum point count.

ADK learning:

- Common execution-like workflows can often be exposed as narrow tools instead
  of arbitrary code execution.
- Keeping artifact generation in a specialist agent reduces the blast radius of
  write-capable tools while still making useful local outputs possible.

### Direct LSEG FX history tools

- Added direct `lseg-data` integration inside `kagents` instead of depending on
  the sibling `kquants-py` implementation.
- Added guarded FX history and FX plotting tools for allowlisted pairs such as
  USDJPY.
- Configured remote LSEG sessions through `.env` keys while preserving a
  desktop session option for local Workspace use.
- Verified a live USDJPY sample request and switched FX history to use
  `MID_PRICE`, since `TRDPRC_1` is not supported for the `JPY=` RIC.

ADK learning:

- External market-data tools should expose narrow, domain-specific operations
  rather than unrestricted API pass-throughs.
- Combining a data-fetch tool with a guarded artifact-generation tool gives a
  useful workflow like "plot USDJPY" without arbitrary code execution.

### Portfolio-manager FX routing

- Added an explicit `lseg_fx` context route for allowlisted FX history and plot
  requests.
- Exposed LSEG FX tools directly to `portfolio_manager` so users do not need to
  switch to `artifact_assistant` for prompts such as "plot USDJPY".
- Updated routing evals to assert that FX plot requests use LSEG tools instead
  of Google Search.

ADK learning:

- Specialist tools are useful, but the main user-facing agent still needs
  enough routing capability to avoid surprising tool choices.

### Data-driven chart styles

- Added named PNG chart styles under `data/context/chart_styles.json`.
- Extended guarded chart creation and LSEG FX plotting to accept `style_name`
  while preserving output path and chart-data validation.
- Added a `KAGENT_CHART_STYLES_PATH` setting so private visual standards can be
  supplied later by replacing data instead of changing tool code.

ADK learning:

- Artifact tools can stay narrow and guarded while still becoming adaptable
  through data-driven style configuration.
- Passing style choices as explicit tool arguments makes visual behavior visible
  in ADK traces and easier to evaluate later.
