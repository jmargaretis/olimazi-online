"""Generate the Olimazi homepage shelf from ordered Markdown item records."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_ROOT = REPO_ROOT / "content" / "library"
SCHEMA = "olimazi-site-copy/library-item/v1"
STATUSES = {"active", "draft"}
HEADING_RE = re.compile(r"(?m)^# ([^\r\n]+)\r?\n")
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FILENAME_RE = re.compile(r"(?P<order>\d{2})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md")

REQUIRED_FIELDS = (
    "Title",
    "Subtitle",
    "Caption",
    "Images",
    "Height",
    "Height Mobile",
    "Aspect",
)
OPTIONAL_FIELDS = ("Card Title", "Notes", "Links")


class RenderError(ValueError):
    """A user-correctable record or target error."""


@dataclass(frozen=True)
class Image:
    src: str
    title: str
    caption: str


@dataclass(frozen=True)
class Link:
    label: str
    href: str


@dataclass(frozen=True)
class Item:
    path: Path
    slug: str
    status: str
    title: str
    card_title: str
    subtitle: str
    caption: str
    notes: tuple[str, ...]
    links: tuple[Link, ...]
    images: tuple[Image, ...]
    height: str
    height_mobile: str
    aspect: str
    eager: bool = False

    @property
    def active(self) -> bool:
        return self.status == "active"


def read_text(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except OSError as exc:
        raise RenderError(f"cannot read {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    try:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content)
    except OSError as exc:
        raise RenderError(f"cannot write {path}: {exc}") from exc


def parse_frontmatter(source: str, path: Path) -> tuple[dict[str, str], str]:
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise RenderError(f"{path}: record must start with YAML frontmatter")
    try:
        close = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise RenderError(f"{path}: frontmatter is missing its closing delimiter") from exc

    metadata: dict[str, str] = {}
    for raw_line in lines[1:close]:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise RenderError(f"{path}: invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in metadata:
            raise RenderError(f"{path}: duplicate frontmatter key: {key}")
        metadata[key] = value
    return metadata, "".join(lines[close + 1 :])


def parse_fields(body: str, path: Path) -> dict[str, str]:
    headings = list(HEADING_RE.finditer(body))
    fields: dict[str, str] = {}
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if name in fields:
            raise RenderError(f"{path}: duplicate field: {name}")
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        value = body[match.end() : end].strip()
        if not value:
            raise RenderError(f"{path}: empty field: {name}")
        fields[name] = value
    return fields


def paragraphs(value: str) -> tuple[str, ...]:
    return tuple(re.split(r"\r?\n\s*\r?\n", value.strip()))


def parse_links(value: str, path: Path) -> tuple[Link, ...]:
    links: list[Link] = []
    for line in value.splitlines():
        if not line.strip():
            continue
        match = INLINE_LINK_RE.fullmatch(line.strip())
        if match is None:
            raise RenderError(f"{path}: Links lines must use [label](url)")
        links.append(Link(match.group(1), match.group(2)))
    return tuple(links)


def image_path(src: str, item_path: Path) -> Path:
    candidate = (REPO_ROOT / src).resolve()
    try:
        candidate.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise RenderError(f"{item_path}: image must stay inside the repo: {src}") from exc
    if not candidate.is_file():
        raise RenderError(f"{item_path}: image file does not exist: {src}")
    return candidate


def parse_images(value: str, title: str, caption: str, path: Path) -> tuple[Image, ...]:
    images: list[Image] = []
    for line in value.splitlines():
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(" | ")]
        if len(parts) > 3:
            raise RenderError(f"{path}: Images lines use: path | optional title | optional caption")
        src = parts[0]
        if not src:
            raise RenderError(f"{path}: image path must be non-empty")
        image_path(src, path)
        image_title = parts[1] if len(parts) > 1 and parts[1] else title
        image_caption = parts[2] if len(parts) > 2 and parts[2] else caption
        images.append(Image(src, image_title, image_caption))
    if not images:
        raise RenderError(f"{path}: Images must contain at least one image path")
    return tuple(images)


def parse_record(path: Path) -> Item:
    metadata, body = parse_frontmatter(read_text(path), path)
    required_metadata = {"schema", "status"}
    missing_metadata = sorted(required_metadata - metadata.keys())
    if missing_metadata:
        raise RenderError(f"{path}: missing frontmatter key(s): {', '.join(missing_metadata)}")
    unknown_metadata = sorted(set(metadata) - {"schema", "status", "loading"})
    if unknown_metadata:
        raise RenderError(f"{path}: unknown frontmatter key(s): {', '.join(unknown_metadata)}")
    if metadata["schema"] != SCHEMA:
        raise RenderError(f"{path}: unsupported schema: {metadata['schema']}")
    filename = FILENAME_RE.fullmatch(path.name)
    if filename is None:
        raise RenderError(f"{path}: filename must start with a two-digit order prefix")
    slug = filename.group("slug")
    if metadata["status"] not in STATUSES:
        raise RenderError(f"{path}: status must be active or draft")
    loading = metadata.get("loading", "lazy")
    if loading not in {"eager", "lazy"}:
        raise RenderError(f"{path}: loading must be eager or lazy")

    fields = parse_fields(body, path)
    missing_fields = [name for name in REQUIRED_FIELDS if name not in fields]
    if missing_fields:
        raise RenderError(f"{path}: missing required field(s): {', '.join(missing_fields)}")
    unknown = sorted(set(fields) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS))
    if unknown:
        raise RenderError(f"{path}: unknown field(s): {', '.join(unknown)}")

    title = fields["Title"]
    caption = fields["Caption"]

    return Item(
        path=path,
        slug=slug,
        status=metadata["status"],
        title=title,
        card_title=fields.get("Card Title", title),
        subtitle=fields["Subtitle"],
        caption=caption,
        notes=paragraphs(fields["Notes"]) if "Notes" in fields else (),
        links=parse_links(fields["Links"], path) if "Links" in fields else (),
        images=parse_images(fields["Images"], title, caption, path),
        height=fields["Height"],
        height_mobile=fields["Height Mobile"],
        aspect=fields["Aspect"],
        eager=loading == "eager",
    )


def load_items(root: Path) -> list[Item]:
    if not root.is_dir():
        raise RenderError(f"library root is not a directory: {root}")
    items = [parse_record(path) for path in sorted(root.glob("*.md"))]
    validate_items(items)
    return items


def validate_items(items: list[Item]) -> None:
    slugs = [item.slug for item in items]
    if len(slugs) != len(set(slugs)):
        raise RenderError("record slugs must be unique")


def escape_text(value: str) -> str:
    return html.escape(value, quote=True).replace("&#x27;", "&#39;")


def escape_double_attr(value: str) -> str:
    return html.escape(value, quote=True).replace("&#x27;", "&#39;")


def escape_single_attr(value: str) -> str:
    return html.escape(value, quote=False).replace("'", "&#39;")


def json_attr(value: object) -> str:
    return escape_double_attr(json.dumps(value, ensure_ascii=False))


def render_item(item: Item) -> str:
    first = item.images[0]
    attributes = [
        'type="button"',
        'class="shelf"',
        f'data-view="{escape_double_attr(first.src)}"',
        f'data-title="{escape_double_attr(item.title)}"',
        f'data-sub="{escape_double_attr(item.subtitle)}"',
    ]
    if len(item.images) == 1 and first.title != item.title:
        attributes.append(f'data-cap="{escape_double_attr(item.caption)}"')
    else:
        attributes.append(f"data-cap='{escape_single_attr(item.caption)}'")
    if item.notes:
        attributes.append(f"data-body='{json_attr(list(item.notes))}'")
    if item.links:
        links = [{"t": link.label, "href": link.href} for link in item.links]
        attributes.append(f"data-links='{json_attr(links)}'")
    if len(item.images) > 1:
        slides = [
            {"src": image.src, "title": image.title, "cap": image.caption}
            for image in item.images
        ]
        attributes.append(f"data-slides='{json_attr(slides)}'")
    attributes.append(
        f'style="--h:{item.height};--hm:{item.height_mobile};--ar:{item.aspect}"'
    )

    figure_class = ' class="slides"' if len(item.images) > 1 else ""
    rendered_images: list[str] = []
    for index, image in enumerate(item.images):
        active = index == 0 and (len(item.images) > 1 or image.title == item.title)
        class_attr = ' class="on"' if active else ""
        loading = "" if item.eager else ' loading="lazy"'
        rendered_images.append(
            f'<img{class_attr} src="{escape_double_attr(image.src)}" '
            f'alt="{escape_double_attr(image.title)}"{loading}>'
        )
    deck = ""
    if len(item.images) > 1:
        dots = '<b class="at"></b>' + "<b></b>" * (len(item.images) - 1)
        deck = f'<i class="deck" aria-hidden="true">{dots}</i>'
    figure = f"<figure{figure_class}>{''.join(rendered_images)}{deck}</figure>"
    caption = (
        f"<figcaption><b>{escape_text(item.card_title)}</b>"
        f"<span>{escape_text(item.subtitle)}</span></figcaption>"
    )
    return f"      <button {' '.join(attributes)}>{figure}{caption}</button>"


def render_library(items: list[Item]) -> str:
    active = sorted((item for item in items if item.active), key=lambda item: item.path.name)
    return "\n".join(render_item(item) for item in active)


def replace_region(target: str, region: str, content: str) -> str:
    start_marker = f"<!-- content:{region}:start -->"
    end_marker = f"<!-- content:{region}:end -->"
    if target.count(start_marker) != 1 or target.count(end_marker) != 1:
        raise RenderError(f"target must contain exactly one {region} start marker and end marker")
    start = target.index(start_marker) + len(start_marker)
    end = target.index(end_marker)
    if start >= end:
        raise RenderError(f"{region} content markers are out of order or overlap")
    leading = "\r\n" if target.count("\r\n") > target.count("\n") / 2 else "\n"
    marker_start = start - len(start_marker)
    start_line = target.rfind("\n", 0, marker_start) + 1
    end_indent = target[start_line:marker_start]
    return target[:start] + leading + content + leading + end_indent + target[end:]


def collection_digest(items: list[Item]) -> str:
    digest = hashlib.sha256()
    for item in sorted(items, key=lambda value: value.path.name):
        digest.update(item.path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("preview", "build"))
    parser.add_argument("--library-root", type=Path, default=LIBRARY_ROOT)
    args = parser.parse_args()

    try:
        items = load_items(args.library_root)
        index_path = REPO_ROOT / "index.html"
        index_text = read_text(index_path)
        rendered_index = replace_region(index_text, "library", render_library(items))

        if args.mode == "build":
            output = index_path
        else:
            output = REPO_ROOT / "index.preview.html"

        before = read_text(output) if output.exists() else None
        changed = before != rendered_index
        if changed:
            write_text(output, rendered_index)

        if args.mode == "build":
            receipt = Path(__file__).with_name(".library-content-hash")
            digest = collection_digest(items) + "\n"
            if not receipt.exists() or read_text(receipt) != digest:
                write_text(receipt, digest)

        print(json.dumps({"mode": args.mode, "changed": {output.name: changed}}, sort_keys=True))
        return 0
    except RenderError as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
