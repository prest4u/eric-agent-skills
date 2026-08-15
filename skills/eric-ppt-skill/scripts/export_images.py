#!/usr/bin/env python3
"""Export a PPTD project as page images through local editor assets for visual QA.

Reuses the localhost editor host from export_pptx.py, chooses
图片 in the export dialog, captures the images ZIP, unzips it, and stitches all pages
into a single overview image that a multimodal model can review.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from export_pptx import (
    BrowserSession,
    ExportError,
    OutputSafetyError,
    build_payload,
    default_downloads_dir,
    ensure_agent_browser,
    find_download,
    find_manifest,
    log,
    ref_by_name,
    resolve_output_target,
    serve_local_editor,
    temporary_directory,
    wait_for_export_dialog,
)

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
OVERVIEW_COLUMNS = 3
OVERVIEW_THUMB_WIDTH = 640
OVERVIEW_LABEL_HEIGHT = 32
OVERVIEW_GAP = 12
PAGE_URL_HINT = "127.0.0.1"
IMAGE_OUTPUT_MARKER = ".eric-ppt-skill-output.json"

# The export dialog's 图片 format option is a plain <div class="radio-group-item">
# without an ARIA role, so agent-browser's interactive snapshot never exposes it.
# The local editor is same-origin, so CDP Runtime.evaluate on the page works.
IMAGE_FORMAT_CLICK_JS = """
(() => {
  const items = [...document.querySelectorAll('.radio-group-item')];
  const pool = items.length
    ? items
    : [...document.querySelectorAll('div,span,label,button')].filter(
        (el) => el.children.length === 0
      );
  const target = pool.find((el) => el.textContent.trim() === '图片');
  if (!target) return null;
  target.click();
  return 'clicked';
})()
""".strip()

ACTIVE_FORMAT_JS = """
(() => {
  const active = document.querySelector('.radio-group-item.active');
  return active ? active.textContent.trim() : null;
})()
""".strip()


def ensure_pillow() -> Tuple[Any, Any, Any]:
    try:
        from PIL import Image, ImageDraw, ImageFont

        return Image, ImageDraw, ImageFont
    except ImportError:
        raise ExportError(
            "Pillow is required for stitching page previews. This script does not "
            "install packages automatically. Install the reviewed version explicitly, "
            "then retry: python3 -m pip install --user Pillow==11.1.0"
        )


def is_image_zip(path: Path) -> bool:
    if not path.is_file() or path.name.endswith(".crdownload"):
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            return any(
                Path(name).suffix.lower() in IMAGE_SUFFIXES
                for name in archive.namelist()
            )
    except (OSError, zipfile.BadZipFile):
        return False


def page_sort_key(path: Path) -> Tuple[int, str]:
    match = re.match(r"(\d+)", path.stem)
    return (int(match.group(1)) if match else sys.maxsize, path.name)


def unzip_images(archive_path: Path, pages_dir: Path) -> List[Path]:
    pages_dir.mkdir(parents=True, exist_ok=True)
    images: List[Path] = []
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            if info.is_dir() or Path(info.filename).suffix.lower() not in IMAGE_SUFFIXES:
                continue
            name = Path(info.filename).name
            if not name:
                continue
            target = pages_dir / name
            with archive.open(info) as source, target.open("wb") as out:
                shutil.copyfileobj(source, out)
            images.append(target)
    images.sort(key=page_sort_key)
    if not images:
        raise ExportError(f"no page images found in: {archive_path}")
    return images


def label_font(image_font: Any) -> Any:
    try:
        return image_font.load_default(size=18)
    except TypeError:  # older Pillow without the size argument
        return image_font.load_default()


def stitch_overview(
    images: Sequence[Path],
    output: Path,
    image_cls: Any,
    draw_cls: Any,
    image_font: Any,
) -> Path:
    thumbs: List[Tuple[str, Any]] = []
    for index, path in enumerate(images, start=1):
        with image_cls.open(path) as opened:
            frame = opened.convert("RGB")
            ratio = OVERVIEW_THUMB_WIDTH / frame.width
            thumb = frame.resize(
                (OVERVIEW_THUMB_WIDTH, max(1, round(frame.height * ratio)))
            )
        thumbs.append((f"P{index}", thumb))

    columns = OVERVIEW_COLUMNS
    rows = math.ceil(len(thumbs) / columns)
    cell_height = OVERVIEW_LABEL_HEIGHT + max(thumb.height for _, thumb in thumbs)
    width = columns * OVERVIEW_THUMB_WIDTH + (columns + 1) * OVERVIEW_GAP
    height = rows * cell_height + (rows + 1) * OVERVIEW_GAP

    overview = image_cls.new("RGB", (width, height), "#e5e7eb")
    draw = draw_cls.Draw(overview)
    font = label_font(image_font)
    for position, (label, thumb) in enumerate(thumbs):
        column = position % columns
        row = position // columns
        x = OVERVIEW_GAP + column * (OVERVIEW_THUMB_WIDTH + OVERVIEW_GAP)
        y = OVERVIEW_GAP + row * (cell_height + OVERVIEW_GAP)
        draw.rectangle(
            (x, y, x + OVERVIEW_THUMB_WIDTH, y + OVERVIEW_LABEL_HEIGHT - 4),
            fill="#111827",
        )
        draw.text((x + 8, y + 5), label, fill="#ffffff", font=font)
        overview.paste(thumb, (x, y + OVERVIEW_LABEL_HEIGHT))

    overview.save(output, "JPEG", quality=85)
    return output


def ensure_websocket() -> Any:
    try:
        import websocket

        return websocket
    except ImportError:
        raise ExportError(
            "websocket-client is required for dialog automation. This script does not "
            "install packages automatically. Install the reviewed version explicitly, "
            "then retry: python3 -m pip install --user websocket-client==1.8.0"
        )


def browser_cdp_url(browser: BrowserSession) -> str:
    process = browser.run(["get", "cdp-url"], timeout=30)
    match = re.search(r"ws://\S+", process.stdout)
    if not match:
        raise ExportError(
            f"could not determine the browser CDP URL:\n{process.stdout[-500:]}"
        )
    return match.group(0)


def evaluate_in_page(cdp_url: str, url_hint: str, expression: str) -> Any:
    websocket = ensure_websocket()

    def call(socket: Any, request_id: int, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        socket.send(json.dumps({"id": request_id, "method": method, "params": params}))
        while True:
            message = json.loads(socket.recv())
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise ExportError(f"CDP {method} failed: {message['error']}")
            return message.get("result", {})

    # websocket-client honors http_proxy env vars; the CDP endpoint is local,
    # so strip proxy settings instead of tunneling localhost through the proxy.
    proxy_env = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY")
    saved_proxy = {name: os.environ.pop(name) for name in proxy_env if name in os.environ}
    try:
        socket = websocket.create_connection(cdp_url, timeout=30, suppress_origin=True)
    finally:
        os.environ.update(saved_proxy)
    try:
        targets = call(socket, 1, "Target.getTargets", {}).get("targetInfos", [])
        page_targets = [
            item
            for item in targets
            if item.get("type") == "page" and url_hint in str(item.get("url", ""))
        ]
        target = page_targets[0] if page_targets else next(
            (item for item in targets if url_hint in str(item.get("url", ""))),
            None,
        )
        if target is None:
            visible = ", ".join(
                f"{item.get('type')}:{str(item.get('url', ''))[:80]}" for item in targets
            )
            raise ExportError(
                f"no browser target matches {url_hint!r}; observed: {visible}"
            )
        attached = call(
            socket,
            2,
            "Target.attachToTarget",
            {"targetId": target["targetId"], "flatten": True},
        )
        session_id = attached["sessionId"]
        socket.send(
            json.dumps(
                {
                    "id": 3,
                    "sessionId": session_id,
                    "method": "Runtime.evaluate",
                    "params": {"expression": expression, "returnByValue": True},
                }
            )
        )
        while True:
            message = json.loads(socket.recv())
            if message.get("id") != 3:
                continue
            if "error" in message:
                raise ExportError(f"CDP Runtime.evaluate failed: {message['error']}")
            result = message.get("result", {})
            if result.get("exceptionDetails"):
                details = result["exceptionDetails"]
                raise ExportError(f"page script failed: {details.get('text')}")
            return result.get("result", {}).get("value")
    finally:
        socket.close()


def select_image_format(browser: BrowserSession) -> None:
    cdp_url = browser_cdp_url(browser)
    value = evaluate_in_page(cdp_url, PAGE_URL_HINT, IMAGE_FORMAT_CLICK_JS)
    if value != "clicked":
        raise ExportError("could not find the 图片 option in the export dialog")
    deadline = time.monotonic() + 10
    active = None
    while time.monotonic() < deadline:
        active = evaluate_in_page(cdp_url, PAGE_URL_HINT, ACTIVE_FORMAT_JS)
        if active == "图片":
            return
        time.sleep(0.3)
    raise ExportError(f"image format was not activated; active option: {active!r}")


def expected_image_output_marker(manifest: Path) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "producer": "eric-ppt-skill",
        "artifact": "image-qa",
        "manifest": str(manifest.resolve()),
    }


def image_output_is_owned(output: Path, manifest: Path) -> bool:
    marker = output / IMAGE_OUTPUT_MARKER
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return value == expected_image_output_marker(manifest)


def ensure_image_output_replaceable(
    output: Path,
    manifest: Path,
    *,
    force: bool,
) -> Optional[Tuple[int, int]]:
    if not output.exists():
        return None
    before = output.stat(follow_symlinks=False)
    before_identity = (before.st_dev, before.st_ino)
    has_entries = any(output.iterdir())
    if not force:
        raise ExportError(
            f"output directory already exists (pass --force to replace it): {output}"
        )
    if has_entries and not image_output_is_owned(output, manifest):
        raise OutputSafetyError(
            "refusing to delete an unowned directory; choose a new output path or "
            f"remove it manually after review: {output}"
        )
    after = output.stat(follow_symlinks=False)
    after_identity = (after.st_dev, after.st_ino)
    if after_identity != before_identity:
        raise OutputSafetyError(
            "output directory identity changed during ownership validation; "
            "nothing was deleted"
        )
    return before_identity


def commit_image_output(
    staged: Path,
    output: Path,
    manifest: Path,
    *,
    force: bool,
) -> None:
    output = resolve_output_target(manifest, output, kind="directory")
    ensure_image_output_replaceable(output, manifest, force=force)
    if not force or not output.exists():
        try:
            output.mkdir()
        except FileExistsError as exc:
            raise OutputSafetyError(
                f"output directory appeared during export; refusing to replace it: {output}"
            ) from exc
        reservation = output / f".reservation-{uuid.uuid4().hex}"
        reservation.write_text("eric-ppt-skill image output reservation\n", encoding="utf-8")
        marker = staged / IMAGE_OUTPUT_MARKER
        children = [path for path in staged.iterdir() if path != marker]
        try:
            for child in children:
                child.replace(output / child.name)
            marker.replace(output / marker.name)
            reservation.unlink()
            staged.rmdir()
        except Exception:
            # Leave the reserved, unowned partial directory visible for manual
            # inspection instead of risking deletion of concurrent additions.
            raise
        return

    original_identity = ensure_image_output_replaceable(output, manifest, force=True)
    if original_identity is None:
        raise OutputSafetyError(
            "output directory disappeared during export; rerun to create it safely"
        )
    backup = output.with_name(f".{output.name}.{uuid.uuid4().hex}.backup")
    moved_existing = False
    try:
        output.replace(backup)
        moved_existing = True
        backup_stat = backup.stat(follow_symlinks=False)
        if (backup_stat.st_dev, backup_stat.st_ino) != original_identity:
            if not output.exists():
                backup.replace(output)
            raise OutputSafetyError(
                "output directory identity changed during export; no directory was deleted"
            )
        staged.replace(output)
    except Exception:
        if moved_existing and backup.exists() and not output.exists():
            backup.replace(output)
        raise
    if moved_existing:
        backup_stat = backup.stat(follow_symlinks=False)
        if (backup_stat.st_dev, backup_stat.st_ino) != original_identity:
            raise OutputSafetyError(
                f"backup identity changed; preserving it instead of deleting: {backup}"
            )
        shutil.rmtree(backup)


def export_images(
    source: Path,
    output: Path,
    keep_download: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    manifest = find_manifest(source)
    output = resolve_output_target(
        manifest,
        output,
        kind="directory",
    )
    ensure_image_output_replaceable(output, manifest, force=force)
    payload = build_payload(manifest)
    agent_browser = ensure_agent_browser()
    image_cls, draw_cls, image_font = ensure_pillow()

    log(f"manifest: {manifest}")
    with temporary_directory(prefix="eric-ppt-skill-images-") as temp_name:
        temp_dir = Path(temp_name)
        download_dir = temp_dir / "downloads"
        download_dir.mkdir()
        server, thread, url = serve_local_editor(payload)
        session = f"eric-ppt-skill-images-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        browser = BrowserSession(agent_browser, session, temp_dir, download_dir)
        downloads = default_downloads_dir()
        try:
            log("opening the local PPTD editor")
            browser.open(url)
            browser.run(
                [
                    "wait",
                    "--fn",
                    'document.documentElement.dataset.deckStatus === "ready"',
                ],
                timeout=120,
            )
            browser.run(["set", "viewport", "1280", "720"])
            snapshot = browser.snapshot()
            export_ref = ref_by_name(snapshot, "导出", "button")
            browser.run(["click", f"@{export_ref}"])
            dialog = wait_for_export_dialog(browser)

            select_image_format(browser)
            dialog = wait_for_export_dialog(browser)

            started_at = time.time() - 1.0
            download_ref = ref_by_name(dialog, "下载", "button")
            log("rendering page images in the local editor")
            browser.run(["click", f"@{download_ref}"], timeout=300)
            downloaded = find_download(
                (downloads, download_dir, temp_dir),
                timeout=240,
                accept=is_image_zip,
                since=started_at,
            )
        finally:
            browser.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        staged = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
        staged.mkdir(parents=True)
        try:
            images = unzip_images(downloaded, staged / "pages")
            if keep_download:
                shutil.copy2(downloaded, staged / "browser-raw.zip")
            overview = stitch_overview(
                images, staged / "overview.jpg", image_cls, draw_cls, image_font
            )
            (staged / IMAGE_OUTPUT_MARKER).write_text(
                json.dumps(
                    expected_image_output_marker(manifest),
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            commit_image_output(staged, output, manifest, force=force)
        finally:
            if staged.exists():
                shutil.rmtree(staged)
        try:
            if downloaded.resolve().parent == downloads.resolve():
                downloaded.unlink(missing_ok=True)
        except OSError:
            pass

        images = [output / "pages" / path.name for path in images]
        overview = output / "overview.jpg"

    page_paths = [entry["path"] for entry in payload["pages"]]
    mapping = [
        {
            "index": index,
            "image": f"pages/{path.name}",
            "page": page_paths[index - 1] if index - 1 < len(page_paths) else None,
        }
        for index, path in enumerate(images, start=1)
    ]
    return {
        "pages": len(images),
        "overview": str(overview),
        "output": str(output),
        "images": mapping,
        "exporter": "browser-local-editor",
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export a PPTD project as page images via the local PPTD editor, unzip "
            "them, and stitch an overview image for visual QA."
        )
    )
    parser.add_argument("input", type=Path, help=".pptd manifest or project directory")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="output directory (default: <project>/.qa-images)",
    )
    parser.add_argument(
        "--keep-browser-raw",
        action="store_true",
        help="also keep the downloaded images ZIP beside the overview",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output directory",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        manifest = find_manifest(args.input)
        output = args.output or manifest.parent / ".qa-images"
        summary = export_images(
            args.input,
            output,
            args.keep_browser_raw,
            args.force,
        )
    except (ExportError, OSError, subprocess.SubprocessError) as exc:
        print(f"Eric PPT Skill image export failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
