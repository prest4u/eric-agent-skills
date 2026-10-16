# Login-backed account safety

The default policy is `account_safety=strict`. It reduces exposure but does
not promise zero account risk. It applies before any Bilibili, Xiaohongshu, or
other login-backed acquisition. Use the failure classification below instead
of treating every failed reader as a permanent prohibition on the task.
Explicit user authorization to use another account or reading method persists
within the requested scope; do not request the same authorization again.

## Session and identity boundary

- Prefer anonymous or genuinely public read backends before considering a
  login-backed backend.
- A login-backed read may use a session Eric already established voluntarily.
  When Eric authorizes account switching, a different existing authorized
  session may be selected through supported browser/account controls for the
  requested source. If the choice of account is materially ambiguous, ask only
  which account. Do not extract/import browser state, copy credentials between
  readers, or create an account. A new login or credential entry requires its
  own applicable authority and the host's confirmation rules.
- Once an existing login-backed session is available, do not ask again for
  every link. Use it only for the requested read and disclose that logged-in
  access was used without revealing an account, profile identifier, cookie,
  token, or credential.
- Do not perform anti-detection, fingerprint spoofing, random "humanized"
  behavior, or simulated browsing. Do not claim that a frequency or delay is
  "safe."

## Strict request envelope

- One link or one exact target per request; execute serially. Never run
  login-backed commands concurrently.
- Search once, return at most 5 results, then read one exact selected result
  once. Do not broaden a direct link into search or discovery.
- For one exact video, "read once" means one serial target transaction, not
  one backend command: at most one metadata/note read, one subtitle read, and
  one media download only when local ASR or visual evidence requires it. Do
  not automatically retry any of those stages or run them concurrently.
  An agent-selected fallback follows the classification below and retrieves
  only the missing material.
- Read comments only when Eric explicitly asks for them, return at most 5
  top-level comments, and do not expand nested replies or reply threads.
- For ordinary content analysis, do not crawl feeds, saved items, liked items,
  history, profiles, followers, following lists, or other account surfaces.
- No batch acquisition, playlists, monitoring, polling, background jobs, or
  scheduled tasks. A login-backed V1 batch request must be refused and
  converted into an offer to process targets one at a time.
- Keep the route read-only. Never post, comment, reply, like, follow, save,
  send, upload, or otherwise interact automatically.

## Classify the failure and select an authorized fallback

Stop the failing automated route first. Record a sanitized signal and whether
it came from an anonymous reader, a browser session, or a local tool. Do not
erase a prior failure by starting another script invocation.

| Observed failure | Next permitted action |
|---|---|
| Empty extraction, unsupported rendering, timeout, unavailable local extension | Use a supported normal browser, public official API, existing reader, author-published transcript/cross-post, or existing local copy. Keep the source identity and retrieve only missing material. |
| HTTP 412 without an explicit rate-limit, verification, account restriction, or access-denial explanation | Treat it as an unresolved request/precondition failure. One normal-page inspection through an existing supported browser is permitted to determine actual availability. If that page is ordinarily readable, continue the requested read; otherwise classify its displayed response. A bare status code does not establish an account ban or private-content restriction. |
| Login challenge or expired session, without an account/security restriction | Use another existing authorized session when account switching is authorized. If a new login is needed, follow the host's login rules; do not export credentials. |
| HTTP 429, access too frequent, explicit account anomaly, suspension, access denial, CAPTCHA, verification challenge | Stop requests to the restricted route/account. Do not rotate accounts, IP addresses, proxies or fingerprints to evade the restriction. A challenge requires user action under the host's rules. Existing local files and independently public author-published copies remain usable. Resume the affected route only after the actual restriction is resolved. |
| SECURITY_BLOCK | Read its reason. Host validation, private-network/SSRF prevention, denied permissions and other safety controls remain enforced. An unsupported adapter may be replaced by a supported normal-browser read of a verified public URL; never weaken the adapter or fetch rejected URLs through a proxy. |

An account switch is authorized access to an available source, not a mechanism
for defeating an explicit denial or rate limit. Public alternatives must not
be leaked private copies or a service that defeats the originating restriction.
Never send authenticated or token-bearing URLs to public proxies.

For a confirmed local daemon failure where the request was never sent,
repairing that local daemon may be followed by exactly one retry. Otherwise
do not repeat an unchanged failing request. Use at most two justified alternate
routes per exact target in a task; if both fail, report the missing material.
Do not run account rotation or a retry loop.

The current intake scripts intentionally stop their own transaction and emit
`non_retryable` / `access_scope` on access signals. These fields prohibit an
automatic in-script retry; they do not implement account switching or overrule
this agent-level classification. Keep their URL validation and request limits
unchanged. Account/session selection uses supported tools outside the script.

## Output disclosure

Report whether anonymous/public or logged-in access was used, the single
target and bounded fields retrieved, any alternate route used, and remaining
limitations. Distinguish a downloaded video from a readable transcript and
from actual continuous viewing/listening.
Sanitize failure details and never disclose account identity, profile IDs,
cookies, tokens, authorization headers, or credentials.

## Evidence basis and limits (accessed 2026-07-18)

- The [Bilibili user agreement](https://www.bilibili.com/blackboard/user-rule-linux.html?night=1&padding=0)
  directs use through official routes and services, assigns responsibility for
  activity under an account, and reserves enforcement including suspension or
  termination. It is a risk boundary, not a rate-limit specification.
- [BILISRC's published standard](https://security.bilibili.com/static/docs/BILISRC_V1.3.pdf)
  includes batch crawler and automation behavior in its business-threat
  intelligence scope. This security-program document is contextual evidence;
  it does not define a safe automation allowance for ordinary users.
- The [Xiaohongshu user agreement](https://agree.xiaohongshu.com/h5/terms/ZXXY20220331001/-1)
  prohibits unauthorized third-party software and illegal scraping or
  simulated downloading, and allows account suspension or banning. Apply the
  current official terms rather than treating this summary as legal advice.
- [OpenCLI](https://github.com/jackwener/opencli) explicitly lets AI agents use
  a logged-in browser through its Browser Bridge. Its current
  [Xiaohongshu search source](https://github.com/jackwener/opencli/blob/main/clis/xiaohongshu/search.js)
  defaults to 20 results and may scroll up to 15 times; that implementation
  detail motivates Eric Reach's lower product cap but supplies no platform
  safety guarantee.
- The [2026 report on Xiaohongshu AI-managed accounts](https://www.thepaper.cn/newsDetail_forward_32741496)
  concerns AI registration, publishing, and simulated interaction. It is not
  evidence that read-only automation is safe.

The platforms publish no ban-proof request rate. `5` is Eric Reach's
conservative product ceiling, not a platform safe threshold. Strict mode
reduces but cannot eliminate account risk.
