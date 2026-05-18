# Context Management

The portfolio manager should answer from the smallest useful set of context
sources for the user's query. The first implementation uses deterministic
context tools so ADK traces and evaluations can inspect both the routing
decision and the private context bundle loaded before the answer.

## Context Sources

| Source | Current tool | Purpose |
| --- | --- | --- |
| `growth_context` | `load_growth_context` | User preferences, operating rules, and tool preferences that shape most answers. |
| `org_context` | `search_org_context` | Acronyms, team names, project aliases, and internal terminology. |
| `documents` | `search_documents` | Private local notes, emails, spreadsheets, PDFs, and documents. |
| `market_data` | `get_jquants_daily_quote` | Japanese security quotes and related market data. |
| `web` | `GoogleSearchTool` | Current public facts, recent news, and external information. |
| `session_memory` | `search_session_memory`, `remember_session_fact`, `list_session_memory`, `update_session_memory`, `forget_session_memory` | Prior conversations, user preferences, and durable project memory. |
| `artifacts` | Not implemented yet | Uploaded or generated files attached to a session. |

## Current Flow

```text
User query
  -> load_private_context
     -> load_growth_context
     -> plan_context
     -> load available private sources
        -> search_org_context
        -> search_documents
        -> search_session_memory
     -> report unavailable private sources
        -> artifacts
     -> report external routes for dedicated tools
        -> get_jquants_daily_quote
        -> GoogleSearchTool
  -> answer from loaded evidence, then call external tools when needed
```

`load_private_context` is the normal first tool for portfolio-manager requests.
It always includes growth context before loading route-specific private context.
`plan_context` remains available when an eval or debugging session needs to
inspect routing without loading full context.

## Growth Context

Growth context is the "育てる" layer: stable preferences, collaboration habits,
and operating rules that make the agent feel progressively more tailored without
hard-coding private knowledge.

Configured files:

- [user_profile.json](C:/Users/kagin/kagents/data/context/user_profile.json)
- [operating_rules.json](C:/Users/kagin/kagents/data/context/operating_rules.json)
- [tool_preferences.json](C:/Users/kagin/kagents/data/context/tool_preferences.json)

Templates:

- [user_profile.template.json](C:/Users/kagin/kagents/data/context/user_profile.template.json)
- [operating_rules.template.json](C:/Users/kagin/kagents/data/context/operating_rules.template.json)
- [tool_preferences.template.json](C:/Users/kagin/kagents/data/context/tool_preferences.template.json)

Use these files for stable preferences and rules, not one-off facts. Use
session memory for remembered decisions, preferences, and project facts that are
created through conversation.

## Evaluation Direction

ADK evaluations should assert:

- the tool trajectory, such as `load_private_context` followed by a dedicated
  external tool when needed
- the internal route plan inside the loaded context bundle
- the final response, including whether the answer cites the loaded evidence

Useful early eval cases:

- acronym questions should route to `org_context`
- planning, risk, finance, and status questions should route to `documents`
- Japanese security quote questions should route to `market_data`
- current public news questions should route to `web`
- follow-up questions such as "what did we decide last time?" should surface
  `search_session_memory`

## Local Session Memory

The first memory implementation is a local JSON file configured with
`KAGENT_SESSION_MEMORY_PATH`, defaulting to
`data/context/session_memory.json`.

Use `search_session_memory` for questions about prior decisions, preferences,
or remembered facts. Use `remember_session_fact` when the user explicitly asks
the agent to remember a durable decision, preference, or project fact.

Use `list_session_memory`, `update_session_memory`, and
`forget_session_memory` when the user wants to inspect, correct, or remove
remembered context.

Memory records use stable architecture fields so private data can be swapped in
later without code changes:

- `id`: stable memory identifier
- `type`: `decision`, `preference`, `project_fact`, `follow_up`, `rule`, or `note`
- `summary`: short retrievable statement
- `details`: supporting private context
- `tags`: normalized retrieval tags
- `visibility`: `private`, `team`, or `org`
- `confidence`: `low`, `medium`, or `high`
- `source`: where the memory came from, such as `user`, `manual`, or `document`
- `created_at` / `updated_at`: ISO-8601 timestamps

This intentionally starts simpler than ADK's managed memory services. The JSON
tool makes memory behavior inspectable while the app's memory schema is still
evolving.

Data template:

- [session_memory.template.json](C:/Users/kagin/kagents/data/context/session_memory.template.json)

Starter eval assets:

- [context_routing.evalset.json](C:/Users/kagin/kagents/agents/portfolio_manager/evals/context_routing.evalset.json)
- [context_routing_config.json](C:/Users/kagin/kagents/agents/portfolio_manager/evals/context_routing_config.json)

Run them with ADK after the virtual environment is bootstrapped:

```powershell
cd C:\Users\kagin\kagents
.\.venv\Scripts\adk.exe eval .\agents\portfolio_manager .\agents\portfolio_manager\evals\context_routing.evalset.json --config_file_path .\agents\portfolio_manager\evals\context_routing_config.json --print_detailed_results
```

These examples are intentionally editable. As the context router and memory
layer mature, tighten expected tool arguments and response thresholds.
