# Login-backed account safety

The default policy is `account_safety=strict`. It reduces exposure but does
not promise zero account risk. It applies before any Bilibili, Xiaohongshu, or
other login-backed OpenCLI acquisition and takes precedence over ordinary
fallback and retry guidance elsewhere in this Skill.

## Session and identity boundary

- Prefer anonymous or genuinely public read backends before considering a
  login-backed backend.
- A login-backed read may use only a session Eric already established
  voluntarily. Do not start login, extract or import browser state, refresh
  credentials, or ask for an account merely to complete acquisition.
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
  not retry any of those stages or run them concurrently.
- Read comments only when Eric explicitly asks for them, return at most 5
  top-level comments, and do not expand nested replies or reply threads.
- For ordinary content analysis, do not crawl feeds, saved items, liked items,
  history, profiles, followers, following lists, or other account surfaces.
- No batch acquisition, playlists, monitoring, polling, background jobs, or
  scheduled tasks. A login-backed V1 batch request must be refused and
  converted into an offer to process targets one at a time.
- Keep the route read-only. Never post, comment, reply, like, follow, save,
  send, upload, or otherwise interact automatically.

## Non-retry circuit breaker

Stop immediately and do not retry when any backend reports a CAPTCHA, HTTP
429, HTTP 412, "access too frequent," `SECURITY_BLOCK`, account anomaly,
login challenge, verification challenge, or equivalent access-control signal.
Do not switch backend, account, IP address, proxy, browser fingerprint, device
fingerprint, or client identity to bypass the signal.

The only retry exception is a confirmed local daemon failure where evidence
shows the request was never sent to the platform. Repairing that local daemon
may be followed by exactly one retry. If delivery is uncertain, treat the
request as sent and do not retry.

## Output disclosure

Report whether anonymous/public or logged-in access was used, the single
target and bounded fields retrieved, and any circuit-breaker limitation.
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
