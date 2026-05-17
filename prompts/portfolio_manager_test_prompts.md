# Portfolio Manager Test Prompts

Use these prompts to test the current `portfolio_manager` behavior.

Sample local sources:

- [sample_notes.md](C:/Users/kagin/kagents/data/docs/sample_notes.md)
- [quarterly_numbers.xlsx](C:/Users/kagin/kagents/data/docs/quarterly_numbers.xlsx)
- [inbox_update.eml](C:/Users/kagin/kagents/data/docs/inbox_update.eml)
- [org_context.json](C:/Users/kagin/kagents/data/context/org_context.json)

## Org Context

```text
What does FR mean?
```

Expected:
- resolves `FR` from org context

```text
What does the finance team do?
```

Expected:
- returns the internal team description from org context

## Document Search

```text
What are the current priorities?
```

Expected:
- uses local documents
- mentions next steps from `sample_notes.md`

```text
What should we prepare for the finance team?
```

Expected:
- searches content rather than file names
- can use both org context and local docs

```text
Summarize the next actions for this project.
```

Expected:
- summarizes action items from local documents or email content

## J-Quants API

```text
Show me the close price for 7203 on 2026-02-20.
```

Expected:
- uses `get_jquants_daily_quote`
- returns OHLC-related data when available

## Web Search

```text
Tell me the latest news about Toyota today.
```

Expected:
- uses Google Search
- includes web sources for current information

## Miss Cases

```text
What does the internal acronym XYZ mean?
```

Expected:
- says it could not confirm the term from org context or local documents
