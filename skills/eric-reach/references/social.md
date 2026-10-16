# Social and community read-only acquisition

Use an existing read-capable backend and reuse its verified status while
platform/backend/session state is unchanged. `active_backend` is a routing hint,
not a prerequisite for an anonymous normal-browser read. A conservative doctor
may leave it empty because platform access has not been tested. Apply
[reader recovery](reader-recovery.md) before classifying that as a failure.
This does not relax any per-request account rule or access stop condition.
The commands below search or read public material; they do not authorize
account, credential, setup, or write actions.

Before any Bilibili, Xiaohongshu, or other login-backed OpenCLI command, read
[account-safety.md](account-safety.md) completely and apply
`account_safety=strict`. Its serial, single-target, five-result, and
failure-classification rules override ordinary fallback guidance. For every
platform below, use search once → exact read once; when Eric supplies an exact
URL or ID, skip search.

## 小红书 / Xiaohongshu

Use the existing ready backend under the checks above. When discovery is needed, search once so the
result carries the required one-time read locator, then read one exact result once.

```bash
opencli xiaohongshu search "query" --limit 5 -f yaml
opencli xiaohongshu note "NOTE_URL_FROM_SEARCH" -f yaml
opencli xiaohongshu comments "NOTE_URL_FROM_SEARCH" --limit 5 --with-replies false -f yaml
```

The installed comments adapter requires the full search-result note URL, including its short-lived read locator, just like `note`; a bare note ID is insufficient. Keep that locator out of reports, durable ledgers and public reader proxies.

Run the comments command only when Eric explicitly requests comments. Read
at most 5 top-level comments and never expand nested replies or reply threads.

Do not attempt a QR flow, browser-state change, or token extraction. If no
read-capable backend is already active, stop and request separate authority.

## X / Twitter

For one exact public post, prefer the normal Chrome page through a supported
browser. Record visible original text, author, displayed date and metrics. A
login prompt for replies does not erase a readable original. Read reply/quote
context only where actually visible and within the requested bound; Reply and
Quote compose controls are not readers.

Inspected OpenCLI 1.8.7 `twitter search` and `twitter thread` both read cookies
into Node; do not invoke either under the current no-export contract. Search
with `--limit 5` requests `count=15` on its first request and may paginate before
trimming the output; thread can paginate five times before applying its limit.
A small output limit does not establish a bounded acquisition. Do not treat
search as an approved alternative to thread, or invent `twitter read/replies/quotes`
commands. No CLI discovery route for X is verified under the current rules;
if no permitted discovery reader is available, report the missing source link
instead of logging in, exporting credentials or switching backends to obtain it.

Check any other supported reader's implementation before selecting it; a ready
bridge or doctor result alone does not authorize that reader. Classify a
failed read under [account safety](account-safety.md); supported public alternatives
and an authorized existing account switch may be used where that policy permits. Do not upgrade a
client, export browser state, set credential variables, or change account
state. Ordinary content analysis does not authorize user-post or profile
crawling.

## B站 / Bilibili

```bash
opencli bilibili search "query" --limit 5 -f yaml
opencli bilibili subtitle BV_ID
```

See [video.md](video.md) for subtitle and transcription routes.

## V2EX

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

## Reddit

Use only the `active_backend` reported by doctor.

```bash
opencli reddit search "query" --limit 5 -f yaml
opencli reddit read POST_ID -f yaml
```

If the active OpenCLI backend cannot read, stop that route and apply account
safety before choosing an already-supported alternative. Existing authorization
for session selection persists. Installing a backend, initiating a new login,
or handling credentials requires the applicable separate authority.

## Facebook and Instagram

Use OpenCLI only when doctor reports an already-active read backend.

```bash
opencli facebook search "query" --limit 5 -f yaml

opencli instagram search "query" --limit 5 -f yaml
```

Ordinary content analysis does not authorize feed, profile, history, saved,
liked, group, follower, or other account-surface crawling. If the public read
fails because of login state, apply account safety: an existing authorized
session may be selected; a new login requires the applicable authority.

## Universal authority boundary

Posting, replying, commenting as the user, liking, following, saving, sending,
and uploading remain outside the read-only task. Changes to account settings,
setup, new login, credential handling, installation and upgrades require their
applicable authority. Selecting an existing authorized session follows account
safety and is permitted when already authorized. Never infer authority for
other account mutations from a failed read. Report the platform, backend,
sanitized failure and any specifically missing authorization.

For every other login-backed platform, apply the same strict generic rule:
one target, serial execution, search at most 5 results, exact read once, no
ordinary feed/profile/history/saved/liked crawling. Use account safety to distinguish
a reader failure from an explicit access restriction before any alternate route.
