# 视频搜索、评论与播客

For single-video reading, subtitle extraction, local transcription, frame
inspection, or video-content analysis, use [video-understanding.md](video-understanding.md).
This file covers discovery, comments, and podcast-specific routes.

## YouTube (yt-dlp)

### 获取视频元数据

```bash
yt-dlp --ignore-config --no-config-locations --no-cookies-from-browser \
  --no-exec --no-cache-dir --dump-json "URL"
```

### 获取评论

```bash
# 提取评论（best-effort，不保证完整）
yt-dlp --ignore-config --no-config-locations --no-cookies-from-browser \
  --no-exec --no-cache-dir --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# 评论在 .info.json 的 comments 字段中
```

### 搜索视频

```bash
yt-dlp --ignore-config --no-config-locations --no-cookies-from-browser \
  --no-exec --no-cache-dir --dump-json "ytsearch5:query"
```

> **评论注意**: `--write-comments` 基于网页抓取（非 YouTube Data API），部分评论可能丢失。

## B站 / Bilibili discovery

> ⚠️ **不要用 yt-dlp 读 B站**：B站风控已全面 412 拦截 yt-dlp（实测最新版、直连/代理/带 Cookie 全部无效）。yt-dlp 只用于 YouTube。

### 视频详情/搜索/热门/排行 (bili-cli，只读无需登录)

```bash
# 视频详情（标题/UP主/时长/播放互动数据/字幕可用性）
bili video BVxxx

# 搜索视频
bili search "query" --type video -n 5

# 热门视频 / 排行榜
bili hot -n 10
bili rank -n 10

# 下载音频并切分为 ASR-ready WAV（无字幕时配合 agent-reach transcribe 转写）
bili audio BVxxx
```

OpenCLI may search/read metadata. The deterministic video pipeline owns
subtitle and media fallback behavior.

If anonymous public read fails, return `AUTH_REQUIRED`. Do not bootstrap
cookies, write cookie jars, extract browser credentials, or start a login flow.

## 小宇宙播客 / Xiaoyuzhou Podcast

### Existing podcast route

```bash
# Use only when doctor reports this existing backend active.
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

Do not add `--polish` or another cloud enhancement from this Skill. Missing
podcast backends are reported; they are never installed or configured here.

### 检查状态

```bash
agent-reach doctor --json
```

> 只有 doctor 报告所需后端已经可用时才运行转录。缺少工具、登录态或
> 凭证时停止并请求单独授权；不要执行设置、登录、安装或升级。输出
> Markdown 文件默认保存到 `/tmp/`。

## 选择指南

| 场景 | 推荐工具 |
|-----|---------|
| YouTube/B站 search | yt-dlp search / bili-cli |
| Video subtitles or understanding | `video_intake.py` via video-understanding.md |
| Video comments | platform read route |
| Podcast transcription | existing doctor-reported local route |
