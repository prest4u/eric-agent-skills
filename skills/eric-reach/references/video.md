# 视频搜索、评论与播客

For single-video reading, subtitle extraction, local transcription, frame
inspection, or video-content analysis, use [video-understanding.md](video-understanding.md).
This file covers discovery, comments, and podcast-specific routes.

## YouTube（已连接的 Chrome / OpenCLI）

先确认 OpenCLI 扩展已连接，并使用用户已有的 Chrome 会话。单视频内容读取走
[video-understanding.md](video-understanding.md)；播放器要求登录或验证时停止。

### 获取视频元数据

```bash
opencli youtube video "URL" -f json
```

### 获取评论（仅在明确请求且 yt-dlp 可正常访问时）

```bash
# 提取评论（best-effort，不保证完整）
yt-dlp --ignore-config --no-config-locations --no-cookies-from-browser \
  --no-exec --no-cache-dir --js-runtimes node --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# 评论在 .info.json 的 comments 字段中
```

### 搜索视频

```bash
opencli youtube search "query" --limit 5 -f json
```

> **评论注意**: `--write-comments` 基于网页抓取（非 YouTube Data API），部分评论可能丢失。

## B站 / Bilibili discovery

本 Skill 的 B站视频脚本使用 OpenCLI。脚本失败后按 [账号读取规则](account-safety.md) 判断原因，可使用正常浏览器、公开正文、作者发布的字幕或其他受支持的读取方式。单独的 HTTP 412 不自动终止任务；先用正常页面判断是否可读。已获换账号授权时，可以选择另一个已有授权会话；明确的访问限制、验证码或限流不能靠轮换账号规避。不得导出 Cookie。

### 已安装 OpenCLI 的调用

先确认 `opencli doctor` 显示扩展已连接。视频详情、字幕和媒体处理使用
[video-understanding.md](video-understanding.md) 的单视频流程；仅搜索时：

```bash
opencli bilibili search "query" --limit 5 -f yaml
```

只有确认 `bili` 已安装并且 doctor 报告该后端可用时，才使用上游的 bili-cli
备选命令。当前单视频脚本使用 OpenCLI；搜索 API 可达不能说明视频或字幕可读。
浏览器扩展未连接时报告 `BROWSER_CONNECT`，不要把连接故障说成视频没有字幕。

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

> 只有 doctor 报告所需后端已经可用时才运行转录；同一任务后端状态不变时复用该结果。缺少工具、登录态或
> 凭证时停止并请求单独授权；不要执行设置、登录、安装或升级。输出
> Markdown 文件默认保存到 `/tmp/`。

## 选择指南

| 场景 | 推荐工具 |
|-----|---------|
| YouTube/B站 search | connected OpenCLI |
| Video subtitles or understanding | `video_intake.py` via video-understanding.md |
| Video comments | platform read route |
| Podcast transcription | existing doctor-reported local route |
