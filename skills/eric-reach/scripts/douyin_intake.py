#!/usr/bin/env python3
"""Fetch public Douyin videos in a headless browser and transcribe them locally."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from playwright.async_api import Response, async_playwright

from video_intake import final_redaction_gate, redact_sensitive_text


PAGE_HOSTS = {"douyin.com", "www.douyin.com", "v.douyin.com", "iesdouyin.com", "www.iesdouyin.com"}
MEDIA_SUFFIXES = (
    "douyinvod.com",
    "idouyinvod.com",
    "douyincdn.com",
    "pstatp.com",
    "volccdn.com",
    "bytefcdn.com",
)
BLOCK_SIGNALS = ("验证码", "访问过于频繁", "请完成验证", "安全验证", "captcha")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
MAX_BYTES = 1024 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="+", help="Public v.douyin.com or douyin.com/video URLs")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--download-only", action="store_true")
    parser.add_argument("--wait-ms", type=int, default=8000)
    parser.add_argument("--model", type=Path)
    return parser.parse_args()


def host_matches(host: str, suffixes: tuple[str, ...]) -> bool:
    return any(host == suffix or host.endswith("." + suffix) for suffix in suffixes)


def validate_page_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        raise ValueError("URL user information is not accepted")
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in PAGE_HOSTS:
        raise ValueError("Only public HTTPS Douyin video links are accepted")


def validate_media_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.username or parsed.password:
        raise ValueError("URL user information is not accepted")
    if parsed.scheme != "https" or not host_matches(host, MEDIA_SUFFIXES):
        raise ValueError(f"Unexpected media host: {host or 'missing'}")


def safe_name(value: str, max_bytes: int = 160) -> str:
    value = re.sub(r'[\\/:*?"<>|\r\n]+', "_", value)
    value = re.sub(r"\s+", " ", value).strip().rstrip(" .")
    if not value:
        return "douyin-video"
    encoded = value.encode("utf-8")
    if len(encoded) <= max_bytes:
        return value
    clipped = encoded[:max_bytes]
    while True:
        try:
            text = clipped.decode("utf-8").rstrip(" .")
            return text or "douyin-video"
        except UnicodeDecodeError:
            clipped = clipped[:-1]


def video_id_from_url(url: str) -> str:
    match = re.search(r"/(?:video|share/video)/(\d+)", url)
    return match.group(1) if match else "unknown"


def total_size(headers: dict[str, str]) -> int:
    content_range = headers.get("content-range", "")
    match = re.search(r"/(\d+)$", content_range)
    if match:
        return int(match.group(1))
    value = headers.get("content-length", "0")
    return int(value) if value.isdigit() else 0


async def capture(browser, url: str, wait_ms: int) -> dict:
    validate_page_url(url)
    context = await browser.new_context(user_agent=USER_AGENT)
    page = await context.new_page()
    media: list[dict] = []
    blocked: list[str] = []

    async def record(response: Response) -> None:
        host = (urlparse(response.url).hostname or "").lower()
        content_type = response.headers.get("content-type", "").lower()
        if response.status in {412, 429}:
            blocked.append(f"HTTP {response.status}")
        if host_matches(host, MEDIA_SUFFIXES) and ("video" in content_type or ".mp4" in response.url):
            media.append({"url": response.url, "headers": dict(response.headers), "status": response.status})

    page.on("response", record)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(wait_ms)
        if blocked:
            raise RuntimeError(f"ACCESS_BLOCK {blocked[0]}")
        final_url = page.url
        validate_page_url(final_url)
        title = (await page.title()).removesuffix(" - 抖音").strip()
        body = (await page.locator("body").inner_text(timeout=5000)).lower()
        found = next((signal for signal in BLOCK_SIGNALS if signal in body), None)
        if found and not media:
            raise RuntimeError(f"ACCESS_BLOCK {found}")
        if not media:
            raise RuntimeError("No public video response was observed")
        unique = {item["url"]: item for item in media}
        candidates = sorted(unique.values(), key=lambda item: total_size(item["headers"]), reverse=True)
        if len(candidates) > 2:
            candidates = [candidates[0], candidates[-1]]
        for candidate in candidates:
            validate_media_url(candidate["url"])
        return {
            "source_url": url,
            "resolved_url": final_url,
            "video_id": video_id_from_url(final_url),
            "title": title or video_id_from_url(final_url),
            "media_candidates": [
                {
                    "url": candidate["url"],
                    "host": (urlparse(candidate["url"]).hostname or "").lower(),
                    "expected_bytes": total_size(candidate["headers"]),
                }
                for candidate in candidates
            ],
        }
    finally:
        await context.close()


def download(url: str, destination: Path, referer: str, redirects: int = 0) -> int:
    if redirects > 4:
        raise RuntimeError("Too many media redirects")
    validate_media_url(url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    headers = {"User-Agent": USER_AGENT, "Referer": referer, "Accept": "video/*,*/*;q=0.8"}
    with requests.get(url, headers=headers, stream=True, timeout=120, allow_redirects=False) as response:
        if response.status_code in {301, 302, 303, 307, 308}:
            target = urljoin(url, response.headers.get("location", ""))
            validate_media_url(target)
            return download(target, destination, referer, redirects + 1)
        if response.status_code in {412, 429}:
            raise RuntimeError(f"ACCESS_BLOCK HTTP {response.status_code}")
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if "video" not in content_type and "octet-stream" not in content_type:
            raise RuntimeError(f"Unexpected content type: {content_type or 'missing'}")
        size = 0
        with partial.open("wb") as handle:
            for chunk in response.iter_content(1024 * 1024):
                if not chunk:
                    continue
                size += len(chunk)
                if size > MAX_BYTES:
                    raise RuntimeError("Video exceeds the 1 GiB limit")
                handle.write(chunk)
    partial.replace(destination)
    return size


def stream_types(path: Path) -> set[str]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return {item.get("codec_type", "") for item in data.get("streams", [])}


def acquire_media(metadata: dict, folder: Path) -> tuple[Path, int]:
    destination = folder / "原视频.mp4"
    if destination.is_file() and {"video", "audio"}.issubset(stream_types(destination)):
        metadata.pop("media_candidates", None)
        return destination, destination.stat().st_size

    candidates = metadata.pop("media_candidates")
    temporary: list[Path] = []
    video_stream = None
    audio_stream = None
    combined_stream = None
    try:
        for index, candidate in enumerate(candidates, 1):
            stream_path = folder / f".captured-stream-{index}.mp4"
            download(candidate["url"], stream_path, metadata["resolved_url"])
            temporary.append(stream_path)
            kinds = stream_types(stream_path)
            if {"video", "audio"}.issubset(kinds):
                combined_stream = stream_path
                break
            if "video" in kinds and video_stream is None:
                video_stream = stream_path
            if "audio" in kinds and audio_stream is None:
                audio_stream = stream_path

        if combined_stream:
            combined_stream.replace(destination)
        elif video_stream and audio_stream:
            muxed = folder / ".muxed-video.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-y",
                    "-i",
                    str(video_stream),
                    "-i",
                    str(audio_stream),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(muxed),
                ],
                check=True,
            )
            muxed.replace(destination)
        else:
            raise RuntimeError("Captured media did not provide both video and audio streams")
        return destination, destination.stat().st_size
    finally:
        for path in temporary:
            if path.exists() and path != destination:
                path.unlink()


def local_model(explicit: Path | None) -> Path:
    if explicit:
        if not explicit.is_dir():
            raise RuntimeError(f"Local Whisper model is missing: {explicit}")
        return explicit
    base = Path.home() / ".cache/huggingface/hub/models--mlx-community--whisper-large-v3-turbo/snapshots"
    matches = sorted(
        path
        for path in base.glob("*")
        if (path / "weights.npz").is_file() or (path / "weights.safetensors").is_file()
    )
    if not matches:
        raise RuntimeError("The reviewed local MLX Whisper large-v3-turbo model is not installed")
    return matches[-1]


def stamp(seconds: float, srt: bool = False) -> str:
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def transcribe(video: Path, folder: Path, metadata: dict, model: Path) -> dict:
    import mlx_whisper

    result = mlx_whisper.transcribe(
        str(video),
        path_or_hf_repo=str(model),
        language="zh",
        task="transcribe",
        verbose=False,
        condition_on_previous_text=False,
        hallucination_silence_threshold=2.0,
        initial_prompt="高考志愿填报，升学规划，院校，专业，分数，位次，出国留学。",
    )
    text = re.sub(r"\s+", "", result.get("text", "")).strip()
    segments = result.get("segments", [])
    (folder / "口播原始转写.txt").write_text(text + "\n", encoding="utf-8")
    timed = "\n".join(
        f"[{stamp(float(seg['start']))} --> {stamp(float(seg['end']))}] {seg.get('text', '').strip()}"
        for seg in segments
    )
    (folder / "口播时间轴.txt").write_text(timed + "\n", encoding="utf-8")
    srt_rows = []
    for index, seg in enumerate(segments, 1):
        srt_rows.append(
            f"{index}\n{stamp(float(seg['start']), True)} --> {stamp(float(seg['end']), True)}\n"
            f"{seg.get('text', '').strip()}\n"
        )
    (folder / "口播字幕.srt").write_text("\n".join(srt_rows), encoding="utf-8")
    md = (
        f"# {redact_sensitive_text(metadata['title'])}｜口播转写\n\n"
        f"> 来源：{redact_sensitive_text(metadata['source_url'])}\n"
        f"> 视频 ID：{metadata['video_id']}\n"
        "> 说明：本稿由本机语音识别生成，专有名词与数字需结合原片复核。\n\n"
        f"{text}\n"
    )
    (folder / "口播整理稿.md").write_text(md, encoding="utf-8")
    return {"characters": len(text), "segments": len(segments)}


async def run(args: argparse.Namespace) -> int:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model = None if args.download_only else local_model(args.model)
    statuses = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            for index, url in enumerate(args.urls, 1):
                print(f"[{index}/{len(args.urls)}] 读取公开页面", flush=True)
                try:
                    metadata = await capture(browser, url, args.wait_ms)
                    folder = args.output_dir / f"{index:02d}-{safe_name(redact_sensitive_text(metadata['title']))} [{metadata['video_id']}]"
                    folder.mkdir(parents=True, exist_ok=True)
                    video, metadata["downloaded_bytes"] = acquire_media(metadata, folder)
                    transcript_file = folder / "口播原始转写.txt"
                    timeline_file = folder / "口播时间轴.txt"
                    draft_file = folder / "口播整理稿.md"
                    if not args.download_only and all(
                        path.is_file() and path.stat().st_size > 0
                        for path in (transcript_file, timeline_file, draft_file)
                    ):
                        metadata["transcript"] = {
                            "characters": len(transcript_file.read_text(encoding="utf-8").strip()),
                            "status": "reused",
                        }
                    elif not args.download_only:
                        metadata["transcript"] = transcribe(video, folder, metadata, model)
                    (folder / "来源信息.json").write_text(
                        json.dumps(final_redaction_gate(metadata), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                    )
                    statuses.append({"url": url, "status": "ok", "folder": str(folder)})
                    print(f"[{index}/{len(args.urls)}] 完成：{folder.name}", flush=True)
                except Exception as error:
                    statuses.append({"url": url, "status": "failed", "error": redact_sensitive_text(str(error))[:300]})
                    print(f"[{index}/{len(args.urls)}] 失败：{redact_sensitive_text(str(error))[:300]}", file=sys.stderr, flush=True)
        finally:
            await browser.close()
    (args.output_dir / "处理结果.json").write_text(
        json.dumps(final_redaction_gate(statuses), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if all(item["status"] == "ok" for item in statuses) else 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run(parse_args())))
