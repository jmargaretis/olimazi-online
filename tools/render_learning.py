"""Generate the Olimazi homepage learning list from ordered Markdown lesson records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LEARNING_ROOT = REPO_ROOT / "content" / "learning"
SCHEMA = "olimazi-site-copy/learning-item/v1"
STATUSES = {"active", "draft"}
HEADING_RE = re.compile(r"(?m)^# ([^\r\n]+)\r?\n")
FILENAME_RE = re.compile(r"(?P<order>\d{2})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md")

REQUIRED_FIELDS = ("Headline", "Sub")


class RenderError(ValueError):
    """A user-correctable record or target error."""


@dataclass(frozen=True)
class Lesson:
    path: Path
    slug: str
    order: int
    status: str
    headline: str
    sub: str

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


def parse_record(path: Path) -> Lesson:
    metadata, body = parse_frontmatter(read_text(path), path)
    required_metadata = {"schema", "status"}
    missing_metadata = sorted(required_metadata - metadata.keys())
    if missing_metadata:
        raise RenderError(f"{path}: missing frontmatter key(s): {', '.join(missing_metadata)}")
    unknown_metadata = sorted(set(metadata) - {"schema", "status"})
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

    fields = parse_fields(body, path)
    missing_fields = [name for name in REQUIRED_FIELDS if name not in fields]
    if missing_fields:
        raise RenderError(f"{path}: missing required field(s): {', '.join(missing_fields)}")
    unknown = sorted(set(fields) - set(REQUIRED_FIELDS))
    if unknown:
        raise RenderError(f"{path}: unknown field(s): {', '.join(unknown)}")

    return Lesson(
        path=path,
        slug=slug,
        order=int(filename.group("order")),
        status=metadata["status"],
        headline=fields["Headline"],
        sub=fields["Sub"],
    )


def load_items(root: Path) -> list[Lesson]:
    if not root.is_dir():
        raise RenderError(f"learning root is not a directory: {root}")
    items = [parse_record(path) for path in sorted(root.glob("*.md"))]
    validate_items(items)
    return items


def validate_items(items: list[Lesson]) -> None:
    slugs = [item.slug for item in items]
    if len(slugs) != len(set(slugs)):
        raise RenderError("record slugs must be unique")
    orders = [item.order for item in items]
    if len(orders) != len(set(orders)):
        raise RenderError("record order prefixes must be unique")


def escape_text(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_item(lesson: Lesson) -> str:
    return (
        f'      <li class="lesson rv" data-i="{lesson.order}">'
        f'<span class="num">{lesson.order:02d}</span>'
        f"<h3>{escape_text(lesson.headline)} <em>{escape_text(lesson.sub)}</em></h3></li>"
    )


def render_learning(items: list[Lesson]) -> str:
    active = sorted((item for item in items if item.active), key=lambda item: item.order)
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("preview", "build"))
    parser.add_argument("--learning-root", type=Path, default=LEARNING_ROOT)
    args = parser.parse_args()

    try:
        items = load_items(args.learning_root)
        index_path = REPO_ROOT / "index.html"
        index_text = read_text(index_path)
        rendered_index = replace_region(index_text, "learning", render_learning(items))
        # keep the "01 of NN" counter in step with the record count
        rendered_index = re.sub(
            r'(id="lcount">\d+</span><small>of )\d+',
            lambda m: f"{m.group(1)}{len(items):02d}",
            rendered_index,
            count=1,
        )

        output = index_path if args.mode == "build" else REPO_ROOT / "index.preview.html"

        before = read_text(output) if output.exists() else None
        changed = before != rendered_index
        if changed:
            write_text(output, rendered_index)

        print(json.dumps({"mode": args.mode, "changed": {output.name: changed}}, sort_keys=True))
        return 0
    except RenderError as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
