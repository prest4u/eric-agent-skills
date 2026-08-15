# Search routes

Use Exa for general web discovery and GitHub CLI for repository/code search.

## General web search

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
```

- Prefer direct result URLs over snippets.
- Fetch the selected pages through their primary URL or the web route before
  treating their content as acquired evidence.
- Search in the language and terminology used by the relevant source domain.

The installed Exa surface currently exposes `web_search_exa` and
`web_fetch_exa`. Do not use the obsolete upstream example
`get_code_context_exa`; it is not available in the verified environment.

## Code and repository search

Use GitHub CLI instead of pretending Exa search is code-index access:

```bash
gh search repos "query" --sort stars --limit 10
gh search code "query" --limit 20
gh search issues "query" --limit 20
```

Read [dev.md](dev.md) for repository, issue, PR, commit, and code details.

## Retrieval boundary

Return URLs, titles, snippets or fetched fields, and access limitations. Leave
source rank, claim verification, and synthesis to Eric Research.
