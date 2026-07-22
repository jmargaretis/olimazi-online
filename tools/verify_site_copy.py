#!/usr/bin/env python3
"""Verify staged site copy against the pristine packet 12-C snapshot."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import render_section


SECTIONS = ("hero-spec", "main-work", "method", "mind", "contact", "dialogs")
MARKER_LINE_RE = re.compile(
    rb"^[ \t]*<!-- content:(?:hero-spec|main-work|method|mind|contact|dialogs):"
    rb"(?:start|end) -->\r?\n",
    re.MULTILINE,
)


def strip_new_markers(content: bytes) -> bytes:
    """Remove only the marker lines introduced by packet 12-C."""

    return MARKER_LINE_RE.sub(b"", content)


def main() -> int:
    tools_dir = Path(__file__).resolve().parent
    repo = tools_dir.parent
    renderer = tools_dir / "render_section.py"
    pristine_path = tools_dir / ".index.pre-migration.html"
    marked_path = repo / "index.html"
    staging_dir = tools_dir / "site-copy-staging"

    pristine = pristine_path.read_bytes()
    marked = marked_path.read_bytes()
    if strip_new_markers(marked) != pristine:
        print("error: index.html differs from the pristine snapshot beyond packet markers", file=sys.stderr)
        return 1

    staged_names = {path.stem for path in staging_dir.glob("*.md")}
    if staged_names != set(SECTIONS):
        missing = sorted(set(SECTIONS) - staged_names)
        extra = sorted(staged_names - set(SECTIONS))
        print(f"error: staged section mismatch; missing={missing}, extra={extra}", file=sys.stderr)
        return 1

    results: list[tuple[str, bool, bool, str]] = []
    scratch_paths: list[Path] = []
    try:
        for section in SECTIONS:
            source_path = staging_dir / f"{section}.md"
            scratch = tools_dir / f".site-copy-verify-{os.getpid()}-{section}.html"
            scratch_paths.append(scratch)
            if scratch.exists():
                print(f"error: refusing to overwrite scratch path {scratch}", file=sys.stderr)
                return 1

            # This is the pristine snapshot plus the marker lines already proven above.
            scratch.write_bytes(marked)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(renderer),
                    "--content",
                    str(source_path),
                    "--mode",
                    "build",
                    "--target",
                    str(scratch),
                ],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout).strip()
                results.append((section, False, False, detail))
                continue

            rendered_bytes = scratch.read_bytes()
            byte_pass = strip_new_markers(rendered_bytes) == pristine

            parsed_section, spec, source_values = render_section.load_content(source_path)
            rendered_text = render_section.read_text(scratch)
            start, end = render_section.marker_bounds(rendered_text, parsed_section)
            reparsed_values = render_section.current_fields(rendered_text[start:end], spec)
            round_trip_pass = source_values == reparsed_values
            detail = completed.stdout.strip()
            results.append((section, byte_pass, round_trip_pass, detail))
    finally:
        for scratch in scratch_paths:
            try:
                scratch.unlink(missing_ok=True)
            except OSError as exc:
                print(f"warning: could not remove scratch file {scratch}: {exc}", file=sys.stderr)

    print("SECTION      BYTE-PRESERVATION  ROUND-TRIP  RESULT")
    for section, byte_pass, round_trip_pass, _detail in results:
        overall = byte_pass and round_trip_pass
        print(
            f"{section:<12} {'PASS' if byte_pass else 'FAIL':<18} "
            f"{'PASS' if round_trip_pass else 'FAIL':<11} {'PASS' if overall else 'FAIL'}"
        )

    failures = [item for item in results if not (item[1] and item[2])]
    if failures:
        for section, _byte_pass, _round_trip_pass, detail in failures:
            print(f"{section}: {detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
