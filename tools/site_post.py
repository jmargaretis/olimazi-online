#!/usr/bin/env python3
"""Feed an approved post into a site section (T-004, option A).

    python tools/site_post.py --section work|learning|library \
        --title "..." --body-file caption.txt --image path1 [--image path2 ...] \
        [--deploy]

`library` and `learning` are real targets: each is backed by an append-only
list of Markdown records (`content/library/*.md` rendered by
`render_collection.py`; `content/learning/*.md` rendered by
`render_learning.py`). `work` (content/main-work.md, render_section.py) is a
fixed seven-field template tied to two hardcoded cards — there is no slot to
add a new entry, and it is refused with a specific reason before anything is
touched.

`--section learning` appends a new lesson at the next order number, using
`--title` as the headline and `--sub` (or, if omitted, the first paragraph of
`--body-file`) as the supporting line, then re-renders index.html. `--image`
is ignored for this section.

Without --deploy: writes/updates content + assets + index.html, prints one
line per file touched, and stops.

With --deploy: also `git add` the touched files, commit
"site: post to <section> — <title>", and `git push origin main`. This site's
deploy is nothing but a push — there is no build step, no GitHub Actions
workflow, and no separate deploy script in this repo; hosting picks up main
on its own once pushed.
"""

from __future__ import annotations

import argparse
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_LIBRARY = REPO_ROOT / "content" / "library"
CONTENT_LEARNING = REPO_ROOT / "content" / "learning"
ASSETS_DIR = REPO_ROOT / "assets"
INDEX_HTML = REPO_ROOT / "index.html"
RENDER_COLLECTION = REPO_ROOT / "tools" / "render_collection.py"
RENDER_LEARNING = REPO_ROOT / "tools" / "render_learning.py"
FILENAME_RE = re.compile(r"(?P<order>\d{2})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md")

DEFAULT_SUBTITLE = "posts"
DEFAULT_HEIGHT = "240px"
DEFAULT_HEIGHT_MOBILE = "150px"
DEFAULT_ASPECT = "1.333"


class SitePostError(RuntimeError):
    """A user-correctable failure. Caught at the top level, printed, exit 1."""


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        raise SitePostError(f"could not derive a slug from title: {title!r}")
    return slug


def unique_slug(base: str, existing: set[str]) -> str:
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


def image_dimensions(path: Path) -> tuple[int, int] | None:
    """PNG/JPEG width, height without a third-party dependency. None if unknown."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        if len(data) < 24:
            return None
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                height, width = struct.unpack(">HH", data[i + 5 : i + 9])
                return width, height
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = struct.unpack(">H", data[i + 2 : i + 4])[0]
            i += 2 + seg_len
        return None
    return None


def format_aspect(width: int, height: int) -> str:
    if height <= 0:
        return DEFAULT_ASPECT
    value = width / height
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return text if text and text != "-" else DEFAULT_ASPECT


def copy_image(src: Path, dest_dir: Path, dest_stem: str) -> tuple[Path, list[str]]:
    """Copy src into dest_dir named dest_stem+ext, suffixing on any collision."""
    if not src.is_file():
        raise SitePostError(f"image not found: {src}")
    ext = src.suffix.lower()
    touched: list[str] = []
    candidate = dest_dir / f"{dest_stem}{ext}"
    n = 2
    while candidate.exists():
        candidate = dest_dir / f"{dest_stem}-{n}{ext}"
        n += 1
    shutil.copy2(src, candidate)
    touched.append(str(candidate.relative_to(REPO_ROOT)))
    return candidate, touched


def paragraphs(text: str) -> list[str]:
    parts = re.split(r"\r?\n\s*\r?\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def existing_records(content_dir: Path) -> list[tuple[int, str, Path]]:
    """[(order_int, slug, path), ...] for every NN-slug.md file in content_dir."""
    records = []
    for path in sorted(content_dir.glob("*.md")):
        match = FILENAME_RE.fullmatch(path.name)
        if match is None:
            raise SitePostError(f"unexpected file in {content_dir.relative_to(REPO_ROOT)}: {path.name}")
        records.append((int(match.group("order")), match.group("slug"), path))
    return records


def existing_library_records() -> list[tuple[int, str, Path]]:
    """[(order_int, slug, path), ...] for every content/library/NN-slug.md file."""
    return existing_records(CONTENT_LIBRARY)


def bump_library_order(records: list[tuple[int, str, Path]]) -> list[str]:
    """Shift every existing record's order prefix up by one so 01 is free.

    Renames only (never deletes). Processed highest-order first so no
    rename ever collides with a file not yet moved.
    """
    touched: list[str] = []
    for order, slug, path in sorted(records, key=lambda r: -r[0]):
        new_order = order + 1
        new_path = path.with_name(f"{new_order:02d}-{slug}.md")
        path.rename(new_path)
        touched.append(f"{path.relative_to(REPO_ROOT)} -> {new_path.relative_to(REPO_ROOT)}")
    return touched


def write_library_record(slug: str, title: str, body_text: str, image_lines: list[str], aspect: str) -> Path:
    body_paragraphs = paragraphs(body_text)
    if not body_paragraphs:
        raise SitePostError("body-file has no content")
    caption = " ".join(body_paragraphs[0].split())
    notes = body_paragraphs[1:]

    lines = [
        "---",
        "schema: olimazi-site-copy/library-item/v1",
        "status: active",
        "---",
        "",
        "# Title",
        "",
        title,
        "",
        "# Subtitle",
        "",
        DEFAULT_SUBTITLE,
        "",
        "# Caption",
        "",
        caption,
        "",
    ]
    if notes:
        lines += ["# Notes", "", "\n\n".join(notes), ""]
    lines += ["# Images", "", *image_lines, "", "# Height", "", DEFAULT_HEIGHT, "",
              "# Height Mobile", "", DEFAULT_HEIGHT_MOBILE, "", "# Aspect", "", aspect, ""]

    path = CONTENT_LIBRARY / f"01-{slug}.md"
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def write_learning_record(order: int, slug: str, headline: str, sub: str) -> Path:
    lines = [
        "---",
        "schema: olimazi-site-copy/learning-item/v1",
        "status: active",
        "---",
        "",
        "# Headline",
        "",
        headline,
        "",
        "# Sub",
        "",
        sub,
        "",
    ]
    path = CONTENT_LEARNING / f"{order:02d}-{slug}.md"
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def run_render_collection() -> str:
    result = subprocess.run(
        [sys.executable, str(RENDER_COLLECTION), "--mode", "build"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SitePostError(f"render_collection.py failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def run_render_learning() -> str:
    result = subprocess.run(
        [sys.executable, str(RENDER_LEARNING), "--mode", "build"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SitePostError(f"render_learning.py failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def deploy(section: str, title: str, touched_files: list[str]) -> None:
    add = git("add", *touched_files)
    if add.returncode != 0:
        raise SitePostError(f"git add failed: {add.stderr.strip()}")
    message = f"site: post to {section} — {title}"
    commit = git("commit", "-m", message)
    if commit.returncode != 0:
        raise SitePostError(f"git commit failed: {commit.stderr.strip() or commit.stdout.strip()}")
    push = git("push", "origin", "main")
    if push.returncode != 0:
        raise SitePostError(f"git push failed: {push.stderr.strip() or push.stdout.strip()}")


def build_learning_post(title: str, body_file: Path, sub: str | None) -> list[str]:
    if not body_file.is_file():
        raise SitePostError(f"body file not found: {body_file}")
    body_text = body_file.read_text(encoding="utf-8")

    records = existing_records(CONTENT_LEARNING)
    if not records:
        raise SitePostError("no existing content/learning records found")
    existing_slugs = {slug for _, slug, _ in records}
    slug = unique_slug(slugify(title), existing_slugs)
    next_order = max(order for order, _, _ in records) + 1

    if sub is None:
        body_paragraphs = paragraphs(body_text)
        if not body_paragraphs:
            raise SitePostError("body-file has no content")
        sub = " ".join(body_paragraphs[0].split())
    else:
        sub = sub.strip()
        if not sub:
            raise SitePostError("--sub must not be empty")

    touched: list[str] = []
    new_path = write_learning_record(next_order, slug, title.strip(), sub)
    touched.append(str(new_path.relative_to(REPO_ROOT)))

    run_render_learning()
    touched.append(str(INDEX_HTML.relative_to(REPO_ROOT)))

    return touched


def build_library_post(title: str, body_file: Path, images: list[Path]) -> list[str]:
    if not images:
        raise SitePostError("at least one --image is required")
    if not body_file.is_file():
        raise SitePostError(f"body file not found: {body_file}")
    body_text = body_file.read_text(encoding="utf-8")

    records = existing_library_records()
    existing_slugs = {slug for _, slug, _ in records}
    slug = unique_slug(slugify(title), existing_slugs)

    touched: list[str] = []

    # Copy images first (pure additions; safe to do before any rename/write).
    copied_paths: list[Path] = []
    for i, image in enumerate(images):
        stem = slug if len(images) == 1 else f"{slug}-{i + 1}"
        dest, copy_touched = copy_image(image, ASSETS_DIR, stem)
        copied_paths.append(dest)
        touched += copy_touched

    aspect = DEFAULT_ASPECT
    dims = image_dimensions(copied_paths[0])
    if dims:
        aspect = format_aspect(*dims)

    image_lines = [f"assets/{p.name}" for p in copied_paths]

    # Shift existing records up by one, then write the new 01-<slug>.md.
    touched += bump_library_order(records)
    new_path = write_library_record(slug, title, body_text, image_lines, aspect)
    touched.append(str(new_path.relative_to(REPO_ROOT)))

    render_render_out = run_render_collection()
    touched.append(str(INDEX_HTML.relative_to(REPO_ROOT)))
    hash_path = RENDER_COLLECTION.with_name(".library-content-hash")
    if hash_path.exists():
        touched.append(str(hash_path.relative_to(REPO_ROOT)))

    return touched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--section", required=True, choices=("work", "learning", "library"))
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True, type=Path)
    parser.add_argument("--image", action="append", type=Path, dest="images", default=[])
    parser.add_argument("--sub", help="learning only: the supporting line (default: body-file's first paragraph)")
    parser.add_argument("--deploy", action="store_true")
    args = parser.parse_args()

    if args.section == "work":
        print(
            "error: --section work is not supported: content/main-work.md is a fixed "
            "seven-field template tied to the two hardcoded work cards (Method Effects, "
            "Rental Manager) — render_section.py only substitutes text into named fields, "
            "it has no way to add a new entry.",
            file=sys.stderr,
        )
        return 1

    try:
        if args.section == "learning":
            touched = build_learning_post(args.title, args.body_file, args.sub)
        else:
            touched = build_library_post(args.title, args.body_file, args.images)
    except SitePostError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for line in touched:
        print(f"wrote {line}")

    if args.deploy:
        try:
            deploy(args.section, args.title, touched)
        except SitePostError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print("pushed to origin main")
    else:
        print("(no --deploy: files written, nothing committed)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
