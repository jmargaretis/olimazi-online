"""Generate the Olimazi feature and library collections from item records."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LIBRARY_ROOT = Path(
    r"C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand"
    r"\site-copy\library"
)
REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "olimazi-site-copy/library-item/v1"
STATUSES = {"active", "draft"}
PLACEMENTS = {"feature", "library"}
HEADING_RE = re.compile(r"(?m)^# ([^\r\n]+)\r?\n")
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
DETAIL_RE = re.compile(r"Detail Item (\d+)")
SOURCE_RE = re.compile(r"Source (\d+)")

REQUIRED_FIELDS = (
    "Title",
    "Summary",
    "Dialog Chip",
    "Dialog Intro",
    "Card Image",
    "Card Image Alt",
    "Dialog Image",
    "Dialog Image Alt",
)
OPTIONAL_FIELDS = (
    "Notes Heading",
    "Notes Body",
    "Detail Heading",
    "Card Orientation",
    "Dialog Close Label",
)


class RenderError(ValueError):
    """A user-correctable record or target error."""


@dataclass(frozen=True)
class Item:
    path: Path
    slug: str
    status: str
    placement: str
    feature_slot: int | None
    order: int
    chip: str
    fields: dict[str, str]
    details: tuple[str, ...]
    sources: tuple[tuple[str, str], ...]

    @property
    def title(self) -> str:
        return self.fields["Title"]


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


def numbered_values(
    fields: dict[str, str], pattern: re.Pattern[str], label: str, path: Path
) -> tuple[str, ...]:
    numbered = sorted(
        (int(match.group(1)), value)
        for name, value in fields.items()
        if (match := pattern.fullmatch(name))
    )
    if numbered and [number for number, _ in numbered] != list(range(1, len(numbered) + 1)):
        raise RenderError(f"{path}: {label} fields must be contiguous from 1")
    return tuple(value for _, value in numbered)


def parse_record(path: Path) -> Item:
    metadata, body = parse_frontmatter(read_text(path), path)
    required_metadata = {"schema", "slug", "status", "placement", "order", "chip"}
    missing_metadata = sorted(required_metadata - metadata.keys())
    if missing_metadata:
        raise RenderError(f"{path}: missing frontmatter key(s): {', '.join(missing_metadata)}")
    if metadata["schema"] != SCHEMA:
        raise RenderError(f"{path}: unsupported schema: {metadata['schema']}")
    slug = metadata["slug"]
    if path.stem != slug:
        raise RenderError(f"{path}: filename must match slug {slug!r}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise RenderError(f"{path}: invalid slug: {slug}")
    if metadata["status"] not in STATUSES:
        raise RenderError(f"{path}: status must be active or draft")
    if metadata["placement"] not in PLACEMENTS:
        raise RenderError(f"{path}: placement must be feature or library")

    try:
        order = int(metadata["order"])
    except ValueError as exc:
        raise RenderError(f"{path}: order must be an integer") from exc

    feature_slot: int | None = None
    if metadata["placement"] == "feature":
        if "feature_slot" not in metadata:
            raise RenderError(f"{path}: feature_slot is required for feature placement")
        try:
            feature_slot = int(metadata["feature_slot"])
        except ValueError as exc:
            raise RenderError(f"{path}: feature_slot must be 1 or 2") from exc
        if feature_slot not in (1, 2):
            raise RenderError(f"{path}: feature_slot must be 1 or 2")
    elif "feature_slot" in metadata:
        raise RenderError(f"{path}: feature_slot is only valid for feature placement")

    fields = parse_fields(body, path)
    missing_fields = [name for name in REQUIRED_FIELDS if name not in fields]
    if missing_fields:
        raise RenderError(f"{path}: missing required field(s): {', '.join(missing_fields)}")
    if "CTA" in fields:
        raise RenderError(f"{path}: CTA is derived and must not be authored")

    details = numbered_values(fields, DETAIL_RE, "Detail Item", path)
    sources_raw = numbered_values(fields, SOURCE_RE, "Source", path)
    sources: list[tuple[str, str]] = []
    for value in sources_raw:
        if " | " not in value:
            raise RenderError(f"{path}: Source fields must use: Label | URL")
        label, url = value.split(" | ", 1)
        if not label.strip() or not url.strip():
            raise RenderError(f"{path}: Source label and URL must be non-empty")
        sources.append((label.strip(), url.strip()))

    known = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    unknown = sorted(
        name
        for name in fields
        if name not in known
        and DETAIL_RE.fullmatch(name) is None
        and SOURCE_RE.fullmatch(name) is None
    )
    if unknown:
        raise RenderError(f"{path}: unknown field(s): {', '.join(unknown)}")

    has_notes_heading = "Notes Heading" in fields
    has_notes_body = "Notes Body" in fields
    if has_notes_heading != has_notes_body:
        raise RenderError(f"{path}: Notes Heading and Notes Body must appear together")
    if ("Detail Heading" in fields) != bool(details):
        raise RenderError(f"{path}: Detail Heading and Detail Item fields must appear together")

    return Item(
        path=path,
        slug=slug,
        status=metadata["status"],
        placement=metadata["placement"],
        feature_slot=feature_slot,
        order=order,
        chip=metadata["chip"],
        fields=fields,
        details=details,
        sources=tuple(sources),
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
    features = [item for item in items if item.status == "active" and item.placement == "feature"]
    if len(features) > 2:
        raise RenderError("at most 2 active feature items are allowed")
    slots = [item.feature_slot for item in features]
    if len(slots) != len(set(slots)):
        raise RenderError("active feature items must use distinct feature_slot values")


def cta_label(item: Item) -> str:
    if not item.sources:
        return "Open notes →"
    recipeish = "Detail Heading" in item.fields and item.chip in {"Recipe", "Cooking"}
    return "Open notes and recipe →" if recipeish else "Open notes and sources →"


def escape_text(value: str) -> str:
    return html.escape(value, quote=False)


def escape_attr(value: str) -> str:
    return html.escape(value, quote=False).replace('"', "&quot;")


def inline_markdown(value: str) -> str:
    rendered: list[str] = []
    position = 0
    for match in INLINE_LINK_RE.finditer(value):
        rendered.append(escape_text(value[position : match.start()]))
        label = escape_text(match.group(1))
        url = escape_attr(match.group(2))
        rendered.append(f'<a href="{url}" target="_blank" rel="noopener">{label}</a>')
        position = match.end()
    rendered.append(escape_text(value[position:]))
    return "".join(rendered)


def paragraphs(value: str, indent: str) -> list[str]:
    blocks = re.split(r"\r?\n\s*\r?\n", value.strip())
    return [f"{indent}<p>{inline_markdown(block.replace(chr(10), ' '))}</p>" for block in blocks]


def render_card(item: Item, feature: bool) -> str:
    f = item.fields
    if feature:
        return "\n".join(
            (
                '            <article class="personal-card">',
                f'              <img src="{escape_attr(f["Card Image"])}" alt="{escape_attr(f["Card Image Alt"])}">',
                f'              <div class="personal-body"><span class="chip">{escape_text(item.chip)}</span><h3>{escape_text(item.title)}</h3><p>{escape_text(f["Summary"])}</p><button class="personal-open" type="button" onclick="openItem(\'{item.slug}-dialog\')">{cta_label(item)}</button></div>',
                "            </article>",
            )
        )

    orientation = f" {escape_attr(f['Card Orientation'])}" if "Card Orientation" in f else ""
    return "\n".join(
        (
            '          <article class="personal-card">',
            f'            <div class="personal-thumb{orientation}">',
            f'              <img src="{escape_attr(f["Card Image"])}" alt="{escape_attr(f["Card Image Alt"])}">',
            "            </div>",
            '            <div class="personal-body">',
            f'              <span class="chip">{escape_text(item.chip)}</span>',
            f"              <h2>{escape_text(item.title)}</h2>",
            f'              <p>{escape_text(f["Summary"])}</p>',
            f'              <button class="personal-open" type="button" aria-haspopup="dialog" onclick="openItem(\'{item.slug}-dialog\')">{cta_label(item)}</button>',
            "            </div>",
            "          </article>",
        )
    )


def render_dialog(item: Item, feature: bool) -> str:
    f = item.fields
    outer = "    " if feature else "    "
    close = f.get("Dialog Close Label", f"Close {item.title} notes")
    lines = [
        f'{outer}<dialog class="item-dialog" id="{item.slug}-dialog" aria-labelledby="{item.slug}-title">',
        f'{outer}  <div class="dialog-grid">',
        f'{outer}    <img src="{escape_attr(f["Dialog Image"])}" alt="{escape_attr(f["Dialog Image Alt"])}">',
        f'{outer}    <div class="dialog-body">',
        f'{outer}      <form method="dialog"><button class="dialog-close" aria-label="{escape_attr(close)}">✕</button></form>',
        f'{outer}      <span class="chip">{escape_text(f["Dialog Chip"])}</span>',
        f'{outer}      <h2 id="{item.slug}-title">{escape_text(item.title)}</h2>',
    ]
    lines.extend(paragraphs(f["Dialog Intro"], outer + "      "))
    if "Notes Heading" in f:
        lines.append(f'{outer}      <h3>{escape_text(f["Notes Heading"])}</h3>')
        lines.extend(paragraphs(f["Notes Body"], outer + "      "))
    if "Detail Heading" in f:
        lines.append(f'{outer}      <h3>{escape_text(f["Detail Heading"])}</h3>')
        detail_items = "".join(f"<li>{inline_markdown(value)}</li>" for value in item.details)
        lines.append(f"{outer}      <ul>{detail_items}</ul>")
    if item.sources:
        lines.append(f'{outer}      <div class="dialog-links">')
        for label, url in item.sources:
            escaped_label = escape_text(label)
            escaped_url = escape_attr(url)
            if url.startswith("mailto:"):
                lines.append(f'{outer}        <a href="{escaped_url}">{escaped_label}</a>')
            else:
                lines.append(
                    f'{outer}        <a href="{escaped_url}" target="_blank" rel="noopener">{escaped_label}</a>'
                )
        lines.append(f"{outer}      </div>")
    lines.extend((f"{outer}    </div>", f"{outer}  </div>", f"{outer}</dialog>"))
    return "\n".join(lines)


def feature_regions(items: list[Item]) -> tuple[str, str]:
    features = sorted(
        (item for item in items if item.status == "active" and item.placement == "feature"),
        key=lambda item: item.feature_slot or 0,
    )
    cards = ['          <div class="personal-grid">']
    cards.extend(render_card(item, feature=True) for item in features)
    cards.append("          </div>")
    dialogs = "\n\n".join(render_dialog(item, feature=True) for item in features)
    return "\n".join(cards), dialogs


def library_regions(items: list[Item]) -> tuple[str, str]:
    library = sorted(
        (item for item in items if item.status == "active" and item.placement == "library"),
        key=lambda item: (item.order, item.slug),
    )
    cards = ['        <div class="personal-grid">']
    for index, item in enumerate(library, 1):
        if index > 1:
            cards.append("")
        cards.append(
            f"          <!-- LIBRARY ENTRY {index:02d} — Edit the thumbnail, label, title, summary, and matching dialog together. -->"
        )
        cards.append(render_card(item, feature=False))
    cards.append("        </div>")

    dialogs: list[str] = []
    for index, item in enumerate(library, 1):
        label = item.title.removeprefix("My brother's ").replace(" classic ", " ")
        comment = f"    <!-- LIBRARY DIALOG {index:02d} — Detailed notes for the {label} entry. -->"
        dialogs.append(comment + "\n" + render_dialog(item, feature=False))
    return "\n".join(cards), "\n\n".join(dialogs)


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
    for item in sorted(items, key=lambda value: value.slug):
        digest.update(item.path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("preview", "build"))
    parser.add_argument("--library-root", type=Path, default=LIBRARY_ROOT)
    args = parser.parse_args()

    try:
        items = load_items(args.library_root)
        feature_cards, feature_dialogs = feature_regions(items)
        library_cards, library_dialogs = library_regions(items)

        index_path = REPO_ROOT / "index.html"
        library_path = REPO_ROOT / "library.html"
        index_text = read_text(index_path)
        library_text = read_text(library_path)
        rendered_index = replace_region(index_text, "library-feature", feature_cards)
        rendered_index = replace_region(
            rendered_index, "library-feature-dialogs", feature_dialogs
        )
        rendered_library = replace_region(library_text, "library", library_cards)
        rendered_library = replace_region(
            rendered_library, "library-dialogs", library_dialogs
        )

        if args.mode == "build":
            outputs = ((index_path, rendered_index), (library_path, rendered_library))
        else:
            outputs = (
                (REPO_ROOT / "index.preview.html", rendered_index),
                (REPO_ROOT / "library.preview.html", rendered_library),
            )

        changes: dict[str, bool] = {}
        for output, content in outputs:
            before = read_text(output) if output.exists() else None
            changed = before != content
            changes[output.name] = changed
            if changed:
                write_text(output, content)

        if args.mode == "build":
            receipt = Path(__file__).with_name(".library-content-hash")
            digest = collection_digest(items) + "\n"
            if not receipt.exists() or read_text(receipt) != digest:
                write_text(receipt, digest)

        print(json.dumps({"mode": args.mode, "changed": changes}, sort_keys=True))
        return 0
    except RenderError as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
