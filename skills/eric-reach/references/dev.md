# GitHub read-only acquisition

Use GitHub CLI only to search or read public repositories, code, Issues, pull
requests, checks, Actions, releases, commits, and API resources.

```bash
gh search repos "query" --sort stars --limit 10
gh search code "query" --language python --limit 20
gh search issues "query" --limit 20

gh repo view owner/repo
gh issue list -R owner/repo --state open
gh issue view 123 -R owner/repo
gh pr list -R owner/repo --state open
gh pr view 123 -R owner/repo
gh pr checks 123 --repo owner/repo

gh run list --repo owner/repo --limit 10
gh run view RUN_ID --repo owner/repo --log-failed
gh workflow list --repo owner/repo
gh release list -R owner/repo
gh api repos/owner/repo
```

## Authority boundary

Repository creation, cloning, forking or synchronization, authentication,
credential changes, Issue/PR/Release creation, merges, dispatches, comments,
and any other write action are outside Eric Reach. If the requested read
cannot proceed with the already-active GitHub state, stop, report the bounded
access failure, and request separate explicit authority. Do not provide a
setup or write-command fallback from this Skill.

For repository documentation, prefer direct public files or `gh repo view`.
Use Context7 only for supported library documentation. Return retrieved URLs
and fields; leave source ranking and synthesis to Eric Research.
