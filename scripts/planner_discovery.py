"""planner_discovery.py - Deterministic discovery for planner UX.

Provides a compact JSON payload for first interaction in planning:
- alteration types (practical categories)
- available sections (H2) and subsections (H3)
- optional query correlation to suggest relevant sections/subsections
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

HEADER_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
WORD_RE = re.compile(r"[a-zA-Z0-9_-]+")
FENCE_RE = re.compile(r"^```")


@dataclass
class Heading:
    level: int
    title: str
    line_no: int


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Arquivo inexistente: {path}") from exc


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


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
        out.append(Heading(level=len(m.group(1)), title=m.group(2).strip(), line_no=i))
    return out


def _score(title: str, q_tokens: set[str]) -> int:
    if not q_tokens:
        return 0
    return len(set(_tokenize(title)).intersection(q_tokens))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic planner resource discovery for README.")
    parser.add_argument("--file", default="README.md", help="Markdown target.")
    parser.add_argument("--query", default="", help="Optional free-text query to correlate sections.")
    parser.add_argument("--top", type=int, default=8, help="Max correlated suggestions.")
    args = parser.parse_args(argv)

    path = Path(args.file)
    text = _read_text(path)
    headings = _extract_headings(text.splitlines())

    h2_list = [h for h in headings if h.level == 2]
    h3_list = [h for h in headings if h.level == 3]

    sections = [{"title": h.title, "line": h.line_no} for h in h2_list]
    subsections = [{"title": h.title, "line": h.line_no} for h in h3_list]

    q_tokens = set(_tokenize(args.query)) if args.query else set()
    correlated: list[dict] = []
    if q_tokens:
        scored = []
        for h in headings:
            if h.level not in (2, 3):
                continue
            s = _score(h.title, q_tokens)
            if s > 0:
                scored.append({
                    "title": h.title,
                    "level": h.level,
                    "line": h.line_no,
                    "score": s,
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        correlated = scored[: args.top]

    payload = {
        "file": str(path),
        "alteration_types": [
            {
                "id": "cirurgica_secao_unica",
                "label": "Ajuste cirurgico em uma secao",
                "recommended_call": "Playbook Router (fast-path)",
            },
            {
                "id": "guiada_update",
                "label": "Ajuste guiado em uma secao",
                "recommended_call": "/update",
            },
            {
                "id": "multi_secao_dependencias",
                "label": "Mudanca multi-secao com dependencias",
                "recommended_call": "Playbook Router (Planner -> Editor -> Validator)",
            },
            {
                "id": "macro_estrutural",
                "label": "Refatoracao macro/estrutural",
                "recommended_call": "Playbook Update Guidance",
            },
            {
                "id": "validacao_final",
                "label": "Validacao final",
                "recommended_call": "Playbook Validator",
            },
        ],
        "sections": sections,
        "subsections": subsections,
        "query": args.query,
        "correlated_sections": correlated,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(f"erro: {exc}")
        raise SystemExit(1)
