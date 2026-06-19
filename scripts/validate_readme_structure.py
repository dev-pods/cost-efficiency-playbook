"""validate_readme_structure.py - Deterministic README structure validator.

Checks:
- broken in-document anchors from Sumario section
- heading hierarchy jumps (> 1 level)
- duplicate heading anchors
- required playbook template files exist
- required playbook template references are mentioned in README

Returns JSON report. Use --strict to fail on errors.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

HEADER_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(#([^)]+)\)")
FENCE_RE = re.compile(r"^```")
REQUIRED_TEMPLATE_PATHS = [
    "scripts/templates/update.template.md",
    "scripts/templates/playbook-section.template.md",
    "scripts/templates/playbook-item.template.md",
]


@dataclass
class Heading:
    level: int
    title: str
    line_no: int
    anchor: str


def _slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9\s-]", "", ascii_text)
    ascii_text = re.sub(r"\s+", "-", ascii_text.strip())
    ascii_text = re.sub(r"-+", "-", ascii_text)
    return ascii_text


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Arquivo inexistente: {path}") from exc


def _missing_template_files(base_dir: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_TEMPLATE_PATHS if not (base_dir / rel_path).exists()]


def _missing_template_mentions(text: str) -> list[str]:
    return [rel_path for rel_path in REQUIRED_TEMPLATE_PATHS if rel_path not in text]


def _extract_headings(lines: list[str]) -> list[Heading]:
    out: list[Heading] = []
    inside_fence = False
    for i, line in enumerate(lines, start=1):
        if FENCE_RE.match(line.strip()):
            inside_fence = not inside_fence
            continue
        if inside_fence:
            continue
        m = HEADER_RE.match(line)
        if not m:
            continue
        title = m.group(2).strip()
        out.append(Heading(level=len(m.group(1)), title=title, line_no=i, anchor=_slugify(title)))
    return out


def _sumario_block(lines: list[str]) -> tuple[int, int] | None:
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## sumário") or line.strip().lower().startswith("## sumario"):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return (start, end)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate README heading and anchor structure.")
    parser.add_argument("--file", default="README.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    target_path = Path(args.file)
    text = _read(target_path)
    lines = text.splitlines()
    headings = _extract_headings(lines)
    heading_anchor_map: dict[str, list[int]] = {}
    for h in headings:
        heading_anchor_map.setdefault(h.anchor, []).append(h.line_no)

    duplicate_anchors = [
        {"anchor": a, "lines": ls}
        for a, ls in heading_anchor_map.items()
        if len(ls) > 1 and any(h.level <= 3 for h in headings if h.anchor == a)
    ]

    hierarchy_jumps = []
    prev_level = 0
    for h in headings:
        if prev_level and h.level > prev_level + 1:
            hierarchy_jumps.append({"line": h.line_no, "title": h.title, "from": prev_level, "to": h.level})
        prev_level = h.level

    broken_links = []
    block = _sumario_block(lines)
    if block:
        s, e = block
        for i in range(s + 1, e + 1):
            if i >= len(lines):
                break
            for m in MD_LINK_RE.finditer(lines[i]):
                anchor = m.group(1).strip().lower()
                if anchor not in heading_anchor_map:
                    broken_links.append({"line": i + 1, "anchor": anchor})

    errors = []
    if duplicate_anchors:
        errors.append("duplicate_anchors")
    if hierarchy_jumps:
        errors.append("hierarchy_jumps")
    if broken_links:
        errors.append("broken_sumario_links")

    missing_template_files = _missing_template_files(target_path.parent)
    missing_template_mentions = _missing_template_mentions(text)
    if missing_template_files:
        errors.append("missing_template_files")
    if missing_template_mentions:
        errors.append("missing_template_mentions")

    report = {
        "file": args.file,
        "ok": len(errors) == 0,
        "errors": errors,
        "duplicate_anchors": duplicate_anchors,
        "hierarchy_jumps": hierarchy_jumps,
        "broken_sumario_links": broken_links,
        "missing_template_files": missing_template_files,
        "missing_template_mentions": missing_template_mentions,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(f"erro: {exc}")
        raise SystemExit(1)
