#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import re
import shutil
from pathlib import Path

import yaml


SKILL_DIR = Path(__file__).resolve().parents[1]
STARTER = SKILL_DIR / "assets" / "starter-project"
STARTER_V2 = SKILL_DIR / "assets" / "starter-project-v2"
STARTERS = {
    "v1": STARTER,
    "v2": STARTER_V2,
}
DEFAULT_PROFILES = ["book-trim", "lesson-a4"]
PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def parse_profiles(value: str) -> list[str]:
    profiles = [item.strip() for item in value.split(",") if item.strip()]
    bad = [profile for profile in profiles if not PROFILE_NAME_RE.fullmatch(profile)]
    if bad:
        raise argparse.ArgumentTypeError(f"invalid profile names: {', '.join(bad)}")
    return profiles or list(DEFAULT_PROFILES)


def base_profile_name(profile: str) -> str:
    lowered = profile.lower()
    if "lesson-a4" in lowered or lowered.endswith("-a4") or lowered.endswith("a4"):
        return "lesson-a4"
    return "book-trim"


def answer_visibility_for_profile(profile: str) -> str | None:
    lowered = profile.lower()
    if "teacher" in lowered:
        return "teacher"
    if "student-with-answer-key" in lowered or "with-answer-key" in lowered:
        return "student-with-answer-key"
    if "student" in lowered:
        return "student"
    return None


def label_for_profile(profile: str) -> str:
    return " ".join(part.capitalize() for part in profile.replace("_", "-").split("-") if part)


def output_path_for_profile(base_spec: dict, profile: str, kind: str) -> str:
    nested = base_spec.get("outputs") or {}
    configured = base_spec.get(f"output_{kind}") or nested.get(kind)
    suffix = f".{kind}"
    if configured:
        path = Path(str(configured))
        suffix = path.suffix or suffix
        stem = path.stem
        base_name = base_profile_name(profile)
        if base_name in stem:
            stem = stem.replace(base_name, profile)
        else:
            stem = f"{stem}-{profile}"
        return str(path.with_name(stem + suffix))
    return f"outputs/textbook-template-sample-{profile}{suffix}"


def qa_without_teacher_key(data: dict) -> dict:
    qa = data.get("qa") or {}
    min_pages = int(qa.get("min_pages") or 0)
    max_pages = int(qa.get("max_pages") or min_pages)
    required_templates = [
        item
        for item in qa.get("required_templates", [])
        if item not in {"teacher-answer-key", "teacher-guide-page", "answer-key"}
    ]
    required_components = [
        item
        for item in qa.get("required_components", [])
        if item not in {"answer-key-page", "teacher-guide-page", "teacher-page-note", "teacher-answer-strip"}
    ]
    return {
        "answer_visibility": "student",
        "page_family_mode": "student-book",
        "min_pages": max(1, min_pages - 1) if min_pages else 1,
        "max_pages": max(1, max_pages - 1) if max_pages else 999,
        "required_templates": required_templates,
        "required_components": required_components,
    }


def derived_profile_spec(data: dict, profile: str) -> dict:
    profiles = data.setdefault("profiles", {})
    if profile in profiles:
        spec = copy.deepcopy(profiles[profile])
    else:
        base_name = base_profile_name(profile)
        base_spec = profiles.get(base_name) or next(iter(profiles.values()), {})
        spec = copy.deepcopy(base_spec)
        spec["label"] = label_for_profile(profile)
        spec["output_html"] = output_path_for_profile(base_spec, profile, "html")
        spec["output_pdf"] = output_path_for_profile(base_spec, profile, "pdf")

    visibility = answer_visibility_for_profile(profile)
    if visibility:
        profile_qa = copy.deepcopy(spec.get("qa") or {})
        if visibility == "student":
            profile_qa.update(qa_without_teacher_key(data))
        else:
            profile_qa["answer_visibility"] = visibility
        spec["qa"] = profile_qa
    return spec


def refuse_dangerous_target(path: Path) -> None:
    resolved = path.expanduser().resolve()
    protected = {Path.home().resolve(), Path("/").resolve(), SKILL_DIR.resolve(), STARTER.resolve(), STARTER_V2.resolve()}
    if resolved in protected:
        raise SystemExit(f"Refusing dangerous output target: {resolved}")
    try:
        resolved.relative_to(SKILL_DIR.resolve())
    except ValueError:
        return
    raise SystemExit(f"Refusing to scaffold inside the skill package: {resolved}")


def copy_starter(target: Path, starter: str) -> None:
    starter_dir = STARTERS[starter]
    ignore_generated = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        "_qa",
        "outputs",
        ".cache",
        "node_modules",
    )
    for item in starter_dir.iterdir():
        if item.name in {"_qa", "outputs", "__pycache__", ".cache", "node_modules"}:
            continue
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=ignore_generated)
        else:
            if item.name.endswith(".pyc") or item.name == ".DS_Store":
                continue
            shutil.copy2(item, dest)


def customize_book(target: Path, title: str | None, profiles: list[str]) -> None:
    book_path = target / "book.yaml"
    data = yaml.safe_load(book_path.read_text(encoding="utf-8"))
    if title:
        data["title"] = title
    data["profile_default"] = profiles[0]
    if profiles and all("a4" in profile.lower() for profile in profiles):
        qa = data.setdefault("qa", {})
        qa["output_mode"] = "a4-only"
    selected_profiles = {
        profile: derived_profile_spec(data, profile)
        for profile in profiles
    }
    data["profiles"] = selected_profiles
    book_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an Eric-designed textbook PDF project.")
    parser.add_argument("--out", required=True, type=Path, help="Output project directory.")
    parser.add_argument("--title", help="Optional book title to write into book.yaml.")
    parser.add_argument("--profiles", type=parse_profiles, default=DEFAULT_PROFILES)
    parser.add_argument("--starter", choices=sorted(STARTERS), default="v1", help="Starter scaffold: v1 core sample or v2 full-coverage gallery. Use --starter v2 for the full template matrix.")
    parser.add_argument("--include-typst", action="store_true", help="Keep the starter Typst A4 adapter.")
    parser.add_argument("--force", action="store_true", help="Replace an existing non-empty output directory.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    target = args.out.expanduser().resolve()
    refuse_dangerous_target(target)

    exists_nonempty = target.exists() and any(target.iterdir())
    if exists_nonempty and not args.force:
        raise SystemExit(f"Refusing to overwrite non-empty directory: {target}")

    if args.dry_run:
        print(target)
        return 0

    if exists_nonempty:
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    copy_starter(target, args.starter)
    customize_book(target, args.title, args.profiles)
    if not args.include_typst:
        shutil.rmtree(target / "typst-adapter", ignore_errors=True)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
