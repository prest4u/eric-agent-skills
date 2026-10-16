# Public Douyin video intake

Use this route when Eric supplies one or more public Douyin video links and asks
to save the media, obtain a local transcript, or inspect the spoken content.

```bash
python3 ./scripts/douyin_intake.py URL [URL ...] \
  --output-dir "/absolute/output/path"
```

The adapter uses Playwright's default headless Chromium launcher, records a
public video response, downloads only from its fixed Douyin CDN allowlist, and
runs the already-installed local MLX Whisper large-v3-turbo model. It never selects a
Chrome channel, launches a Chrome app, imports cookies, starts login, plays
audio through the system, calls cloud ASR, or downloads a model.

Run targets serially. The adapter stops its transaction on CAPTCHA,
verification, HTTP 412/429, an unexpected redirect/host/content type, or missing
public media. Classify that result using [account safety](account-safety.md)
before an agent-selected alternative. A bare HTTP 412 may permit normal-page
inspection; explicit restrictions must not be evaded through account rotation.
Do not weaken the fixed-domain media validation or import browser credentials.
The JSON result distinguishes completed and failed targets; do not report a
batch as complete until each requested target has `status: ok` and its MP4 and
transcript files are non-empty.

Treat automatic speech recognition as a draft. Preserve the source link and
video ID, check names and numbers against the original media when accuracy
matters, and describe corrections rather than silently inventing words.
