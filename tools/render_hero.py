#!/usr/bin/env python3
"""Render the home-page hero from its Markdown content source."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path


FIELDS = (
    "Kicker",
    "Headline Lead",
    "Headline Accent",
    "Sub",
    "CTA Label",
    "CTA Href",
)
START_MARKER = "<!-- content:home-hero:start -->"
END_MARKER = "<!-- content:home-hero:end -->"


class RenderError(ValueError):
    """A user-correctable content or target error."""


def read_text(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except OSError as exc:
        raise RenderError(f"cannot read {path}: {exc}") from exc


def parse_content(source: str) -> dict[str, str]:
    headings = list(re.finditer(r"(?m)^# ([^\r\n]+)[ \t]*\r?$", source))
    values: dict[str, str] = {}
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if name not in FIELDS:
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else len(source)
        values[name] = source[match.end() : end].strip()

    invalid = [name for name in FIELDS if not values.get(name)]
    if invalid:
        raise RenderError("missing or empty required field(s): " + ", ".join(invalid))
    return values


def marker_bounds(target: str) -> tuple[int, int]:
    if target.count(START_MARKER) != 1 or target.count(END_MARKER) != 1:
        raise RenderError("target must contain exactly one start marker and one end marker")
    start = target.index(START_MARKER) + len(START_MARKER)
    end = target.index(END_MARKER)
    if start >= end:
        raise RenderError("hero content markers are out of order or overlap")
    return start, end


def render_fragment(values: dict[str, str], newline: str) -> str:
    escaped = {name: html.escape(value, quote=True) for name, value in values.items()}
    lines = (
        f'          <div class="hero-kicker">{escaped["Kicker"]}</div>',
        f'          <h1>{escaped["Headline Lead"]} <span class="accent">{escaped["Headline Accent"]}</span></h1>',
        f'          <p class="hero-sub">{escaped["Sub"]}</p>',
        f'          <a class="btn" href="{escaped["CTA Href"]}">{escaped["CTA Label"]} <span class="arr" aria-hidden="true">→</span></a>',
    )
    return newline + newline.join(lines) + newline + "          "


def current_fields(fragment: str) -> dict[str, str]:
    patterns = {
        "Kicker": r'<div class="hero-kicker">(.*?)</div>',
        "Headline Lead": r"<h1>(.*?) <span class=\"accent\">",
        "Headline Accent": r'<span class="accent">(.*?)</span></h1>',
        "Sub": r'<p class="hero-sub">(.*?)</p>',
        "CTA Label": r'<a class="btn" href=".*?">(.*?) <span class="arr"',
        "CTA Href": r'<a class="btn" href="(.*?)">',
    }
    current: dict[str, str] = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, fragment, re.DOTALL)
        if match:
            current[name] = html.unescape(match.group(1))
    return current


def write_text(path: Path, content: str) -> None:
    try:
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content)
    except OSError as exc:
        raise RenderError(f"cannot write {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preview", "build"))
    parser.add_argument("--target", type=Path, default=Path("index.html"))
    args = parser.parse_args()

    try:
        source = read_text(args.content)
        values = parse_content(source)
        target_text = read_text(args.target)
        start, end = marker_bounds(target_text)
        current = current_fields(target_text[start:end])
        newline = "\r\n" if "\r\n" in target_text[start:end] else "\n"
        patched = target_text[:start] + render_fragment(values, newline) + target_text[end:]

        changed = [name for name in FIELDS if current.get(name) != values[name]]
        output = args.target if args.mode == "build" else args.target.with_name("index.preview.html")
        write_text(output, patched)
        if args.mode == "build":
            digest = hashlib.sha256(args.content.read_bytes()).hexdigest()
            write_text(Path(__file__).with_name(".hero-content-hash"), digest + "\n")

        summary = ", ".join(changed) if changed else "none"
        print(f"Rendered {output}; changed fields: {summary}")
        return 0
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
