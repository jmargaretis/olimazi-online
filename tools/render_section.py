#!/usr/bin/env python3
"""Render a marker-bounded index.html section from Markdown fields."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path


SCHEMA = "olimazi-site-copy/v1"
HEADING_RE = re.compile(r"(?m)^# ([^\r\n]+)[ \t]*\r?$")
OPEN_TAG_RE = re.compile(
    r"<(?P<tag>[A-Za-z][\w:-]*)(?:[^\"'<>]|\"[^\"]*\"|'[^']*')*>",
    re.DOTALL,
)
INLINE_HTML = r"(?:<b>|</b>|<span[ \t\r\n]+class=(?:\"jw\"|'jw')>|</span>)"
EDITABLE_ELEMENT_RE = re.compile(
    r"<(?P<tag>[A-Za-z][\w:-]*)"
    r"(?P<attrs>(?:[^\"'<>]|\"[^\"]*\"|'[^']*')*)>"
    rf"(?P<text>(?:[^<]|{INLINE_HTML})*)</(?P=tag)\s*>",
    re.DOTALL | re.IGNORECASE,
)
DATA_C_RE = re.compile(
    r"(?<![\w:-])data-c(?![\w:-])[ \t\r\n]*=[ \t\r\n]*"
    r"(?P<quote>[\"'])(?P<name>.*?)(?P=quote)",
    re.DOTALL | re.IGNORECASE,
)
INLINE_DELIMITER_RE = re.compile(r"\*\*|\{\{|\}\}")
INLINE_HTML_RE = re.compile(INLINE_HTML, re.IGNORECASE)


class RenderError(ValueError):
    """A user-correctable content or target error."""


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


def parse_frontmatter(source: str) -> dict[str, str]:
    lines = source.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RenderError("content source must start with YAML frontmatter")
    try:
        close = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise RenderError("content source frontmatter is not closed") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:close]:
        match = re.match(r"^([a-z_]+):[ \t]*(.*)$", line)
        if match and match.group(2) not in (">", "|"):
            metadata[match.group(1)] = match.group(2).strip()

    required = ("schema", "section", "site_repo", "target", "region")
    invalid = [name for name in required if not metadata.get(name)]
    if invalid:
        raise RenderError("missing frontmatter field(s): " + ", ".join(invalid))
    if metadata["schema"] != SCHEMA:
        raise RenderError(f"unsupported schema: {metadata['schema']}")
    if metadata["section"] != metadata["region"]:
        raise RenderError("frontmatter section and region must match")
    return metadata


def parse_content(source: str) -> dict[str, str]:
    headings = list(HEADING_RE.finditer(source))
    values: dict[str, str] = {}
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if name in values:
            raise RenderError(
                f'duplicate markdown heading: {name}; keep exactly one "# {name}" block'
            )
        end = headings[index + 1].start() if index + 1 < len(headings) else len(source)
        value = source[match.end() : end].strip()
        if not value:
            raise RenderError(
                f'markdown field is empty: {name}; add a value below "# {name}"'
            )
        values[name] = value

    return values


def load_content(path: Path) -> tuple[str, None, dict[str, str]]:
    source = read_text(path)
    metadata = parse_frontmatter(source)
    values = parse_content(source)
    # Preserve the staged control-plane call shape without supplying a field list.
    return metadata["section"], None, values


def marker_bounds(target: str, section: str) -> tuple[int, int]:
    start_marker = f"<!-- content:{section}:start -->"
    end_marker = f"<!-- content:{section}:end -->"
    if target.count(start_marker) != 1 or target.count(end_marker) != 1:
        raise RenderError("target must contain exactly one start marker and one end marker")
    start = target.index(start_marker) + len(start_marker)
    end = target.index(end_marker)
    if start >= end:
        raise RenderError(f"{section} content markers are out of order or overlap")
    return start, end


def data_c_name(tag: str) -> str | None:
    matches = list(DATA_C_RE.finditer(tag))
    if not matches:
        return None
    if len(matches) > 1:
        raise RenderError("an editable element has more than one data-c attribute; keep exactly one")
    name = html.unescape(matches[0].group("name")).strip()
    if not name:
        raise RenderError('an editable element has an empty data-c name; use data-c="Field Name"')
    return name


def editable_elements(fragment: str) -> list[tuple[re.Match[str], str]]:
    named_tags = [
        (match, name)
        for match in OPEN_TAG_RE.finditer(fragment)
        if (name := data_c_name(match.group(0))) is not None
    ]
    names = [name for _, name in named_tags]

    seen: set[str] = set()
    duplicates: list[str] = []
    for name in names:
        if name in seen and name not in duplicates:
            duplicates.append(name)
        seen.add(name)
    if duplicates:
        raise RenderError(
            "duplicate data-c name(s): "
            + ", ".join(duplicates)
            + "; give each editable element a unique field name"
        )

    elements: list[tuple[re.Match[str], str]] = []
    for opening, name in named_tags:
        match = EDITABLE_ELEMENT_RE.match(fragment, opening.start())
        if match is not None:
            elements.append((match, name))
    element_names = [name for _, name in elements]
    unsupported = [name for name in names if name not in element_names]
    if unsupported:
        raise RenderError(
            "data-c element contains unsupported markup: "
            + ", ".join(unsupported)
            + "; only text, <b>, and <span class=\"jw\"> are editable"
        )
    return elements


def field_names(fragment: str) -> tuple[str, ...]:
    return tuple(name for _, name in editable_elements(fragment))


def validate_content_fields(fields: tuple[str, ...], values: dict[str, str]) -> None:
    missing = [name for name in fields if name not in values]
    if missing:
        raise RenderError(
            "data-c field(s) missing from markdown: "
            + ", ".join(missing)
            + "; add a matching \"# Field Name\" block for each"
        )
    field_set = set(fields)
    extra = [name for name in values if name not in field_set]
    if extra:
        raise RenderError(
            "markdown heading(s) missing from the marked region: "
            + ", ".join(extra)
            + "; add a matching data-c attribute or remove the heading"
        )


def render_inline(value: str, field: str) -> str:
    escaped = html.escape(value, quote=True)
    rendered: list[str] = []
    stack: list[str] = []
    cursor = 0
    for match in INLINE_DELIMITER_RE.finditer(escaped):
        token = match.group(0)
        rendered.append(escaped[cursor : match.start()])
        if token == "**":
            if stack and stack[-1] == "bold":
                stack.pop()
                rendered.append("</b>")
            elif "bold" in stack:
                raise RenderError(f'unbalanced ** delimiter in field "{field}"')
            else:
                stack.append("bold")
                rendered.append("<b>")
        elif token == "{{":
            stack.append("jw")
            rendered.append('<span class="jw">')
        elif not stack or stack[-1] != "jw":
            raise RenderError(f'unbalanced {{{{ }}}} delimiter in field "{field}"')
        else:
            stack.pop()
            rendered.append("</span>")
        cursor = match.end()
    rendered.append(escaped[cursor:])
    if stack:
        delimiter = "**" if stack[-1] == "bold" else "{{ }}"
        raise RenderError(f'unbalanced {delimiter} delimiter in field "{field}"')
    return "".join(rendered)


def read_inline(value: str, field: str) -> str:
    decoded: list[str] = []
    stack: list[str] = []
    cursor = 0
    for match in INLINE_HTML_RE.finditer(value):
        decoded.append(value[cursor : match.start()])
        token = match.group(0).lower()
        if token == "<b>":
            stack.append("bold")
            decoded.append("**")
        elif token == "</b>":
            if not stack or stack[-1] != "bold":
                raise RenderError(f'unbalanced <b> markup in field "{field}"')
            stack.pop()
            decoded.append("**")
        elif token.startswith("<span"):
            stack.append("jw")
            decoded.append("{{")
        else:
            if not stack or stack[-1] != "jw":
                raise RenderError(f'unbalanced jw span markup in field "{field}"')
            stack.pop()
            decoded.append("}}")
        cursor = match.end()
    decoded.append(value[cursor:])
    if stack:
        markup = "<b>" if stack[-1] == "bold" else "jw span"
        raise RenderError(f'unbalanced {markup} markup in field "{field}"')
    return html.unescape("".join(decoded))


def current_fields(fragment: str) -> dict[str, str]:
    return {
        name: read_inline(match.group("text").strip(), name)
        for match, name in editable_elements(fragment)
    }


def render_fragment(
    fragment: str,
    control_plane_or_values: None | dict[str, str],
    values: dict[str, str] | None = None,
) -> str:
    if values is None:
        if not isinstance(control_plane_or_values, dict):
            raise RenderError("renderer values are missing")
        values = control_plane_or_values

    elements = editable_elements(fragment)
    fields = tuple(name for _, name in elements)
    validate_content_fields(fields, values)

    rendered: list[str] = []
    cursor = 0
    for match, name in elements:
        raw = match.group("text")
        current = read_inline(raw.strip(), name)
        replacement = render_inline(values[name], name)
        rendered.append(fragment[cursor : match.start("text")])
        if current == values[name]:
            rendered.append(raw)
        else:
            leading = raw[: len(raw) - len(raw.lstrip())]
            trailing = raw[len(raw.rstrip()) :]
            rendered.append(leading + replacement + trailing)
        cursor = match.end("text")
    rendered.append(fragment[cursor:])
    return "".join(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preview", "build"))
    parser.add_argument("--target", type=Path, default=Path("index.html"))
    args = parser.parse_args()

    try:
        section, control_plane_compat, values = load_content(args.content)
        target_text = read_text(args.target)
        start, end = marker_bounds(target_text, section)
        fragment = target_text[start:end]
        current = current_fields(fragment)
        rendered = render_fragment(fragment, control_plane_compat, values)
        patched = target_text[:start] + rendered + target_text[end:]

        changed = [name for name in current if current[name] != values[name]]
        output = args.target if args.mode == "build" else args.target.with_name("index.preview.html")
        write_text(output, patched)
        if args.mode == "build":
            digest = hashlib.sha256(args.content.read_bytes()).hexdigest()
            write_text(Path(__file__).with_name(f".{section}-content-hash"), digest + "\n")

        summary = ", ".join(changed) if changed else "none"
        print(f"Rendered {output}; changed fields: {summary}")
        return 0
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
