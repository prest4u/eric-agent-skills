# Social and community read-only acquisition

Use only an already-active backend reported by `agent-reach doctor --json`.
The commands below search or read public material; they do not authorize
account, credential, setup, or write actions.

Before any Bilibili, Xiaohongshu, or other login-backed OpenCLI command, read
[account-safety.md](account-safety.md) completely and apply
`account_safety=strict`. Its serial, single-target, five-result, and
non-retry circuit-breaker rules override ordinary fallback guidance. For every
platform below, use search once → exact read once; when Eric supplies an exact
URL or ID, skip search.

## 小红书 / Xiaohongshu

Use the reported active backend. When discovery is needed, search once so the
result carries the required one-time read locator, then read one exact result once.

```bash
opencli xiaohongshu search "query" --limit 5 -f yaml
opencli xiaohongshu note "NOTE_URL_FROM_SEARCH" -f yaml
opencli xiaohongshu comments NOTE_ID_FROM_SEARCH --limit 5 --with-replies false -f yaml
```

Run the comments command only when Eric explicitly requests comments. Read
at most 5 top-level comments and never expand nested replies or reply threads.

Do not attempt a QR flow, browser-state change, or token extraction. If no
read-capable backend is already active, stop and request separate authority.

## X / Twitter

```bash
opencli twitter search "query" --limit 5 -f yaml
```

Choose one already-active read backend before sending the request. Do not
switch backends after a login, rate-limit, or security signal. Do not upgrade a
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

If the reported active OpenCLI backend cannot read, stop and request separate
authority. Do not install a backend, initiate authentication, write Cookies,
or request API credentials.

## Facebook and Instagram

Use OpenCLI only when doctor reports an already-active read backend.

```bash
opencli facebook search "query" --limit 5 -f yaml

opencli instagram search "query" --limit 5 -f yaml
```

Ordinary content analysis does not authorize feed, profile, history, saved,
liked, group, follower, or other account-surface crawling. If the public read
is blocked by login state, stop and request separate authority.

## Universal authority boundary

Posting, replying, commenting as the user, liking, following, saving, sending,
uploading, account changes, setup, login, credential handling, installation,
and upgrades are outside Eric Reach. Never turn a failed read into one of
those actions. Report the platform, backend, sanitized failure fingerprint,
and the explicit authority that would be needed.

For every other login-backed platform, apply the same strict generic rule:
one target, serial execution, search at most 5 results, exact read once, no
ordinary feed/profile/history/saved/liked crawling, and no retry or backend
switching after a risk signal.
