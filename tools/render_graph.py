#!/usr/bin/env python3
"""Render the mind-section vault graph SVG from a graphify graph.json export."""

from __future__ import annotations

import argparse
import html
import json
import math
import random
import re
import sys
from pathlib import Path


START_MARKER = "<!-- content:mind:start -->"
END_MARKER = "<!-- content:mind:end -->"

# render_section.py addresses the mind section by positional text-node index.
# The generated SVG must always emit exactly this many <text> labels or the
# "mind" SectionSpec (25 slots, 14 of them the graph labels) stops matching.
LABEL_COUNT = 14
MAX_LABEL_CHARS = 22

VIEW_W, VIEW_H = 1080, 620
MARGIN = 30
SEED = 20260725
ITERATIONS = 400

# Nodes still drawn as circles, but never chosen as one of the 14 labels.
EXCLUDE_LABELS = {"John (owner)"}

# Legend colours, matched against each community's NAME rather than its id.
# graphify renumbers communities on every rerun, so id-keyed mapping silently
# mis-colours the graph; names survive. First matching rule wins.
FALLBACK_COLOR = "var(--ink-muted)"  # "Everything else"
COLOR_RULES = (
    (("method effects",), "#99621E"),                     # Method Effects
    (("olimazi", "brand", "site"), "var(--red)"),          # Olimazi design
    (("rental", "schedule e", "tax"), "var(--olive)"),     # Schedule E & C
)


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


def load_graph(path: Path) -> tuple[list[dict], list[tuple[int, int]]]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RenderError(f"{path} is not valid JSON: {exc}") from exc

    nodes = data.get("nodes") or []
    if not nodes:
        raise RenderError(f"{path} contains no nodes")

    index = {node["id"]: i for i, node in enumerate(nodes)}
    edges: set[tuple[int, int]] = set()
    for link in data.get("links") or []:
        a, b = index.get(link.get("source")), index.get(link.get("target"))
        if a is None or b is None or a == b:
            continue
        edges.add((a, b) if a < b else (b, a))
    return nodes, sorted(edges)


def load_community_labels(path: Path) -> dict[int, str]:
    """graphify's .graphify_labels.json, keyed by community id."""
    if not path.exists():
        raise RenderError(
            f"cannot find {path}; community colours need graphify's .graphify_labels.json "
            "(pass --labels explicitly)"
        )
    try:
        raw = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise RenderError(f"{path} is not valid JSON: {exc}") from exc
    return {int(k): str(v) for k, v in raw.items()}


def community_colors(labels: dict[int, str]) -> tuple[dict[int, str], list[str]]:
    """Assign a legend colour per community by name. Returns (colours, unmatched names)."""
    colors: dict[int, str] = {}
    unmatched: list[str] = []
    for cid, name in labels.items():
        lowered = name.lower()
        for keywords, color in COLOR_RULES:
            if any(word in lowered for word in keywords):
                colors[cid] = color
                break
        else:
            colors[cid] = FALLBACK_COLOR
            unmatched.append(name)
    return colors, unmatched


def layout(count: int, edges: list[tuple[int, int]]) -> list[list[float]]:
    """Deterministic Fruchterman-Reingold, stdlib only."""
    rng = random.Random(SEED)
    pos = [[rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)] for _ in range(count)]
    k = 2.0 * math.sqrt(1.0 / count)
    temp = 0.1

    for step in range(ITERATIONS):
        disp = [[0.0, 0.0] for _ in range(count)]
        for i in range(count):
            xi, yi = pos[i]
            for j in range(i + 1, count):
                dx, dy = xi - pos[j][0], yi - pos[j][1]
                dist2 = dx * dx + dy * dy
                if dist2 < 1e-9:
                    dx, dy, dist2 = rng.uniform(-1e-3, 1e-3), rng.uniform(-1e-3, 1e-3), 1e-6
                force = (k * k) / dist2
                disp[i][0] += dx * force
                disp[i][1] += dy * force
                disp[j][0] -= dx * force
                disp[j][1] -= dy * force
        for a, b in edges:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            dist = math.hypot(dx, dy) or 1e-6
            force = dist / k
            ux, uy = dx / dist * force, dy / dist * force
            disp[a][0] -= ux
            disp[a][1] -= uy
            disp[b][0] += ux
            disp[b][1] += uy

        cooling = temp * (1.0 - step / ITERATIONS)
        for i in range(count):
            dx, dy = disp[i]
            dist = math.hypot(dx, dy) or 1e-6
            scale = min(dist, cooling) / dist
            pos[i][0] += dx * scale
            pos[i][1] += dy * scale
    return pos


def _bounds(values: list[float]) -> tuple[float, float]:
    """Percentile bounds, so a handful of flung-out isolates cannot squash the bulk."""
    ordered = sorted(values)
    lo = ordered[int(len(ordered) * 0.02)]
    hi = ordered[min(len(ordered) - 1, int(len(ordered) * 0.98))]
    return (lo, hi) if hi > lo else (min(ordered), max(ordered) or lo + 1.0)


def to_viewbox(pos: list[list[float]]) -> list[tuple[float, float]]:
    lox, hix = _bounds([p[0] for p in pos])
    loy, hiy = _bounds([p[1] for p in pos])
    scaled = []
    for x, y in pos:
        sx = MARGIN + (x - lox) / (hix - lox) * (VIEW_W - 2 * MARGIN)
        sy = MARGIN + (y - loy) / (hiy - loy) * (VIEW_H - 2 * MARGIN)
        sx = min(max(sx, MARGIN), VIEW_W - MARGIN)
        sy = min(max(sy, MARGIN), VIEW_H - MARGIN)
        scaled.append((round(sx, 1), round(sy, 1)))
    return scaled


def truncate(label: str) -> str:
    label = " ".join(label.split())
    if len(label) <= MAX_LABEL_CHARS:
        return label
    return label[: MAX_LABEL_CHARS - 1].rstrip() + "…"


def build_svg(
    nodes: list[dict],
    edges: list[tuple[int, int]],
    colors_by_community: dict[int, str],
    newline: str,
) -> str:
    if len(nodes) < LABEL_COUNT:
        raise RenderError(f"graph has {len(nodes)} nodes; need at least {LABEL_COUNT} to label")

    degree = [0] * len(nodes)
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
    top = max(degree) or 1

    pts = to_viewbox(layout(len(nodes), edges))
    radii = [round(3.0 + 6.0 * math.sqrt(d / top), 1) for d in degree]
    colors = [colors_by_community.get(n.get("community"), FALLBACK_COLOR) for n in nodes]

    # Smallest first so hubs paint on top, matching the hand-authored order.
    order = sorted(range(len(nodes)), key=lambda i: (degree[i], nodes[i]["id"]))
    eligible = [i for i in reversed(order) if (nodes[i].get("label") or "") not in EXCLUDE_LABELS]
    if len(eligible) < LABEL_COUNT:
        raise RenderError(f"only {len(eligible)} labellable nodes; need {LABEL_COUNT}")
    labelled = eligible[:LABEL_COUNT]

    out = [
        '<svg class="vault-graph" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg"'
        ' role="img" aria-label="Current, evolving knowledge graph of the Olimazi vault">'
        % (VIEW_W, VIEW_H),
        '<g stroke="var(--ink)" stroke-opacity="0.16" stroke-width="1">',
    ]
    for a, b in edges:
        out.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
            % (pts[a][0], pts[a][1], pts[b][0], pts[b][1])
        )
    out.append("</g>")
    out.append("<g>")
    for i in order:
        out.append(
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.88"/>'
            % (pts[i][0], pts[i][1], radii[i], colors[i])
        )
    out.append("</g>")
    out.append(
        '<g font-family="IBM Plex Mono, Consolas, monospace" font-size="11" fill="var(--ink-muted)">'
    )
    for i in labelled:
        out.append(
            '<text x="%.1f" y="%.1f">%s</text>'
            % (
                pts[i][0] + radii[i] + 4.0,
                pts[i][1] + 3.5,
                html.escape(truncate(nodes[i].get("label") or nodes[i]["id"])),
            )
        )
    out.append("</g>")
    out.append("</svg>")

    fragment = newline.join(out)
    emitted = fragment.count("<text ")
    if emitted != LABEL_COUNT:
        raise RenderError(f"emitted {emitted} labels; the mind section requires exactly {LABEL_COUNT}")
    return fragment


def splice(target_text: str, fragment: str) -> str:
    if target_text.count(START_MARKER) != 1 or target_text.count(END_MARKER) != 1:
        raise RenderError("target must contain exactly one mind start marker and one end marker")
    start = target_text.index(START_MARKER)
    end = target_text.index(END_MARKER)
    if start >= end:
        raise RenderError("mind content markers are out of order")

    region = target_text[start:end]
    match = re.search(r'<svg class="vault-graph".*?</svg>', region, re.DOTALL)
    if not match:
        raise RenderError("no <svg class=\"vault-graph\"> block found inside the mind section")
    return target_text[: start + match.start()] + fragment + target_text[start + match.end() :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True, type=Path, help="graphify graph.json export")
    parser.add_argument(
        "--labels",
        type=Path,
        help="graphify .graphify_labels.json (defaults to the sibling of --graph)",
    )
    parser.add_argument("--mode", required=True, choices=("preview", "build", "stdout"))
    parser.add_argument("--target", type=Path, default=Path("index.html"))
    args = parser.parse_args()

    try:
        nodes, edges = load_graph(args.graph)
        labels_path = args.labels or args.graph.with_name(".graphify_labels.json")
        community_labels = load_community_labels(labels_path)
        colors, unmatched = community_colors(community_labels)
        for name in unmatched:
            print(f"note: community {name!r} has no colour rule; using 'Everything else'", file=sys.stderr)

        if args.mode == "stdout":
            sys.stdout.reconfigure(encoding="utf-8")
            print(build_svg(nodes, edges, colors, "\n"))
            return 0

        target_text = read_text(args.target)
        newline = "\r\n" if "\r\n" in target_text else "\n"
        patched = splice(target_text, build_svg(nodes, edges, colors, newline))

        output = args.target if args.mode == "build" else args.target.with_name("index.preview.html")
        write_text(output, patched)
        print(f"Rendered {output}; {len(nodes)} nodes, {len(edges)} edges, {LABEL_COUNT} labels")
        return 0
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
