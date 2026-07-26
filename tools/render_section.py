#!/usr/bin/env python3
"""Render a marker-bounded index.html section from Markdown fields."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SCHEMA = "olimazi-site-copy/v1"
TOKEN_RE = re.compile(r"(<[^>]+>|['\"])")
HEADING_RE = re.compile(r"(?m)^# ([^\r\n]+)[ \t]*\r?$")


@dataclass(frozen=True)
class SectionSpec:
    """Ordered field names for each non-markup text slot; None is fixed UI text."""

    slots: tuple[str | None, ...]

    @property
    def fields(self) -> tuple[str, ...]:
        return tuple(name for name in self.slots if name is not None)


SECTION_SPECS = {
    "hero-spec": SectionSpec(
        (
            "Name Label",
            "Name",
            "Name Description",
            "Prior Work Label",
            "Prior Work",
            "Current Work Label",
            "Current Work",
            "Current Loop Label",
            "Current Loop",
            "Status Label",
            "Status",
        )
    ),
    "main-work": SectionSpec(
        (
            "Section Label", None, "Heading", "Intro",
            "Method Slide 01 Title", "Method Slide 01 Caption",
            "Method Slide 02 Title", "Method Slide 02 Caption",
            "Method Slide 03 Title", "Method Slide 03 Caption Lead",
            "Method Slide 03 Credit Label", "Method Slide 03 Caption Tail",
            "Method Slide 04 Title", "Method Slide 04 Caption",
            "Method Slide 05 Title", "Method Slide 05 Caption Lead",
            "Method Slide 05 Credit Label", "Method Slide 05 Caption Tail",
            "Method Slide 06 Title", "Method Slide 06 Caption",
            "Method Slide 07 Title", "Method Slide 07 Caption Lead",
            "Method Slide 07 Credit Label", "Method Slide 07 Caption Tail",
            "Method Slide 08 Title", "Method Slide 08 Caption Before Quote",
            "Method Slide 08 Quoted Word", "Method Slide 08 Caption Before Credit",
            "Method Slide 08 Credit Label", None,
            "Method Slide 09 Title", "Method Slide 09 Credit Label",
            "Method Slide 09 Caption Before Quote", "Method Slide 09 Quoted Word",
            "Method Slide 09 Caption Tail",
            "Method Slide 10 Title", "Method Slide 10 Caption",
            "Method Slide 11 Title", "Method Slide 11 Caption",
            "Method Slide 12 Title", "Method Slide 12 Caption Lead",
            "Method Slide 12 Credit Label", None,
            "Method Slide 13 Title", "Method Slide 13 Caption",
            "Method Slide 14 Title", "Method Slide 14 Caption",
            None, None, None,
            "Method Status", "Method Heading", "Method Body 1", "Method Body 2",
            "Method Period Label", "Method Period",
            "Method Built Label", "Method Built",
            "Method Reach Label", "Method Reach",
            "Method Notes Label", "Method Note 1", "Method Note 2",
            "Method Note 3", "Method Note 4", "Method Note 5",
            "Tracker Status", "Tracker Heading", "Tracker Lede",
            "Tracker Product Name", "Tracker Product Schedule", "Tracker Body",
            "Tracker Own Label", "Tracker Own Value",
            "Tracker Trust Label", "Tracker Trust Value",
            "Tracker Use Label", "Tracker Use Value",
            "Tracker Download Label", "Tracker Testing CTA", None,
            "Tracker Disclaimer Lead", "Tracker Disclaimer Tail",
            "Tracker Slide 01 Title", "Tracker Slide 01 Caption",
            "Tracker Slide 02 Title", "Tracker Slide 02 Caption",
            "Tracker Slide 03 Title", "Tracker Slide 03 Caption",
            "Tracker Slide 04 Title", "Tracker Slide 04 Caption",
            "Tracker Slide 05 Title", "Tracker Slide 05 Caption",
            None, None, None,
        )
    ),
    "method": SectionSpec(
        (
            "Section Label", None, "Heading Lead", "Heading Accent", "Lede",
            "Slide 01 Label", "Slide 01 Title", "Slide 01 Body",
            "Slide 02 Label", "Slide 02 Title", "Slide 02 Body",
            "Slide 03 Label", "Slide 03 Title", "Slide 03 Body",
            "Slide 04 Label", "Slide 04 Title", "Slide 04 Body",
            None, None, None,
        )
    ),
    "mind": SectionSpec(
        (
            "Section Label", None, "Heading", "Intro",
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None,
            "Legend Schedule E and C", "Legend Olimazi Design",
            "Legend Method Effects", "Legend Everything Else", None,
            "Practice Heading", "Practice Intro",
        )
    ),
    "dialogs": SectionSpec(
        (
            None, "Contact Chip", "Contact Heading", "Contact Intro",
            "Contact Form Label", "Contact Option Resume", "Contact Option Suggest",
            "Contact Option Explain", "Contact Option Collaborate",
            "Contact Option Business", "Contact Option General",
            "Contact CTA", None, "Contact Direct Email",
        )
    ),
    "contact": SectionSpec(
        (
            "Label", "Heading", "Intro", "Form Label",
            "Option Resume", "Option Suggest", "Option Explain",
            "Option Collaborate", "Option Business", "Option General",
            "CTA", None, "Direct Email",
        )
    ),
}


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
    if metadata["section"] not in SECTION_SPECS:
        raise RenderError(f"unsupported section: {metadata['section']}")
    return metadata


def parse_content(source: str, fields: tuple[str, ...]) -> dict[str, str]:
    headings = list(HEADING_RE.finditer(source))
    values: dict[str, str] = {}
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if name not in fields:
            continue
        if name in values:
            raise RenderError(f"duplicate field: {name}")
        end = headings[index + 1].start() if index + 1 < len(headings) else len(source)
        values[name] = source[match.end() : end].strip()

    invalid = [name for name in fields if not values.get(name)]
    if invalid:
        raise RenderError("missing or empty required field(s): " + ", ".join(invalid))
    return values


def load_content(path: Path) -> tuple[str, SectionSpec, dict[str, str]]:
    source = read_text(path)
    metadata = parse_frontmatter(source)
    section = metadata["section"]
    spec = SECTION_SPECS[section]
    return section, spec, parse_content(source, spec.fields)


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


def text_node_indices(tokens: list[str]) -> list[int]:
    return [
        index
        for index, token in enumerate(tokens)
        if token.strip() and not token.startswith("<") and token not in ("'", '"')
    ]


def current_fields(fragment: str, spec: SectionSpec) -> dict[str, str]:
    tokens = TOKEN_RE.split(fragment)
    indices = text_node_indices(tokens)
    if len(indices) != len(spec.slots):
        raise RenderError(
            f"section structure changed: expected {len(spec.slots)} text slots, found {len(indices)}"
        )
    return {
        name: html.unescape(tokens[token_index].strip())
        for token_index, name in zip(indices, spec.slots)
        if name is not None
    }


def render_fragment(fragment: str, spec: SectionSpec, values: dict[str, str]) -> str:
    tokens = TOKEN_RE.split(fragment)
    indices = text_node_indices(tokens)
    if len(indices) != len(spec.slots):
        raise RenderError(
            f"section structure changed: expected {len(spec.slots)} text slots, found {len(indices)}"
        )
    for token_index, name in zip(indices, spec.slots):
        if name is None:
            continue
        token = tokens[token_index]
        leading = token[: len(token) - len(token.lstrip())]
        trailing = token[len(token.rstrip()) :]
        tokens[token_index] = leading + html.escape(values[name], quote=True) + trailing
    return "".join(tokens)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preview", "build"))
    parser.add_argument("--target", type=Path, default=Path("index.html"))
    args = parser.parse_args()

    try:
        section, spec, values = load_content(args.content)
        target_text = read_text(args.target)
        start, end = marker_bounds(target_text, section)
        current = current_fields(target_text[start:end], spec)
        rendered = render_fragment(target_text[start:end], spec, values)
        patched = target_text[:start] + rendered + target_text[end:]

        changed = [name for name in spec.fields if current.get(name) != values[name]]
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
