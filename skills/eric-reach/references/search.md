# Search routes

Use a currently available read-only search tool that can reach the required sources. A simple public lookup does not require Exa, a doctor run, or a new backend. Reuse inspected sources before searching again.

## General web search

Search narrowly in the source domain's own language and terminology. Prefer primary sources and open the selected supporting passage; snippets alone do not establish the claim. Expand queries only to resolve a material gap or disagreement.

If the verified Exa surface is already available, this is its existing discovery route:

```bash
mcporter call exa.web_search_exa query="query" numResults=5
```

Use the current tool schema for fetch parameters. The verified environment exposes `web_search_exa` and `web_fetch_exa`; the old `get_code_context_exa` example is not available here. Do not guess missing commands or install tools for a lookup.

## Code and repository search

An exact repository, file, issue, or PR should be read directly with a suitable GitHub connector or existing CLI. Search only when its location is unknown:

```bash
gh search repos "query" --limit 5
gh search code "query" --limit 10
gh search issues "query" --limit 10
```

Prefer relevance and the requested owner/project over star count. Increase a public result limit only for a justified coverage gap. Read [dev.md](dev.md) for the existing CLI routes.

## Return

Give the requested answer and source links. Preserve dates and access limitations when material. Do not create a separate retrieval report or invoke a research workflow merely because a search was used.
