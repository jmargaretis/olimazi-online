#!/usr/bin/env python3
"""Sync a raw dump into its site-copy field file.

The raw file is the source of truth. A field you delete from the raw is deleted
from the field file. Nothing else touches the field file, so an edit in the raw
lane is the only edit anyone has to make.

Guard: a field the render spec requires is never deleted. If the raw drops one,
this refuses to write and tells you which.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from render_section import SECTION_SPECS

sys.stdout.reconfigure(encoding="utf-8")

VAULT_COPY = Path(
    r"C:\Users\jmarg\OneDrive\Documents\Claude OS\projects\olimazi-brand\site-copy"
)
TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*(.*)$")
STATUS_RE = re.compile(r"^Status:\s*(\S+)", re.M)
HEADING_RE = re.compile(r"^#\s+(.+?)\r?\n(.*?)(?=\n#\s|\Z)", re.S | re.M)


class SyncError(Exception):
    """A user-correctable content error."""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_raw(text: str) -> dict[str, str]:
    """Tagged fields, in file order. A value runs until the next [tag]."""
    fields: dict[str, str] = {}
    name: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if name is not None:
            fields[name] = "\n".join(buf).strip()

    for line in text.splitlines():
        match = TAG_RE.match(line)
        if match:
            flush()
            name, buf = match.group(1).strip(), [match.group(2)]
        elif name is not None:
            if line.lstrip().startswith("#"):
                flush()
                name, buf = None, []
            else:
                buf.append(line)
    flush()
    return fields


def split_field_file(text: str) -> tuple[str, dict[str, str]]:
    """Return (frontmatter block verbatim, {field: value} in file order)."""
    if not text.startswith("---"):
        raise SyncError("field file must start with YAML frontmatter")
    close = text.index("\n---", 3)
    end = text.index("\n", close + 1) + 1
    frontmatter, body = text[:end], text[end:]
    fields = {m.group(1).strip(): m.group(2).strip() for m in HEADING_RE.finditer(body)}
    return frontmatter, fields


def render_field_file(frontmatter: str, fields: dict[str, str]) -> str:
    parts = [frontmatter.rstrip("\n"), ""]
    for name, value in fields.items():
        parts += ["", f"# {name}", "", value]
    return "\n".join(parts) + "\n"


def sync(section: str, apply: bool, force: bool) -> int:
    raw_path = VAULT_COPY / "_raw" / f"{section}.md"
    field_path = VAULT_COPY / f"{section}.md"
    if not raw_path.exists():
        raise SyncError(f"no raw file: {raw_path}")
    if not field_path.exists():
        raise SyncError(f"no field file: {field_path}")

    raw_text = read(raw_path)
    status_match = STATUS_RE.search(raw_text)
    status = status_match.group(1).upper() if status_match else "MISSING"
    if status != "READY" and not force:
        print(f"{section}: Status is {status} — not processing. Flip to READY, or pass --force.")
        return 0

    raw_fields = parse_raw(raw_text)
    if not raw_fields:
        print(f"{section}: raw has no [Field] tags — untagged prose, cannot sync. Skipped.")
        return 0

    frontmatter, old = split_field_file(read(field_path))
    required = set(SECTION_SPECS[section].fields) if section in SECTION_SPECS else set()

    removed = [n for n in old if n not in raw_fields]
    added = [n for n in raw_fields if n not in old]
    changed = [n for n in raw_fields if n in old and raw_fields[n] != old[n]]

    blocked = sorted(set(removed) & required)
    if blocked:
        raise SyncError(
            "raw file is missing render-required field(s): "
            + ", ".join(blocked)
            + "\nRestore them in the raw, or remove them from SECTION_SPECS first."
        )

    # keep existing order for surviving fields; new ones append in raw order
    new = {n: raw_fields[n] for n in old if n in raw_fields}
    new.update({n: raw_fields[n] for n in added})

    print(f"{section}: raw {len(raw_fields)} fields / field file {len(old)} → {len(new)}")
    for label, names in (("changed", changed), ("added", added), ("removed", removed)):
        print(f"  {label}: {', '.join(names) if names else 'none'}")

    if not (changed or added or removed):
        return 0
    if not apply:
        print("  (check mode — nothing written)")
        return 0

    field_path.write_text(render_field_file(frontmatter, new), encoding="utf-8")
    print(f"  wrote {field_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("section", nargs="?", help="section name; omit for all")
    parser.add_argument("--apply", action="store_true", help="write; default is check only")
    parser.add_argument("--force", action="store_true", help="process even if Status is not READY")
    args = parser.parse_args()

    sections = (
        [args.section]
        if args.section
        else sorted(p.stem for p in (VAULT_COPY / "_raw").glob("*.md") if (VAULT_COPY / p.name).exists())
    )
    rc = 0
    for section in sections:
        try:
            sync(section, args.apply, args.force)
        except SyncError as exc:
            print(f"error [{section}]: {exc}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
