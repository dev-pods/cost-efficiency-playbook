"""planner_preflight.py - Deterministic global preflight for playbook planning.

Builds a compact, machine-readable planning context from README.md without LLM calls.
Outputs JSON with:
- objective_macro
- candidate_sections
- declared_gaps
- cross_section_dependencies
- planning_score
- status (aguardando_usuario | pronto_para_execucao)
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

HEADER_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
WORD_RE = re.compile(r"[a-zA-Z0-9_-]+")


@dataclass
class Heading:
    level: int
    title: str
    line_no: int


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Arquivo inexistente: {path}") from exc


def _extract_headings(lines: list[str]) -> list[Heading]:
    out: list[Heading] = []
    for i, line in enumerate(lines, start=1):
        m = HEADER_RE.match(line)
        if not m:
            continue
        out.append(Heading(level=len(m.group(1)), title=m.group(2).strip(), line_no=i))
    return out


def _extract_objective_macro(text: str) -> str:
    m = re.search(r"\|\s*Objetivo\s*\|\s*(.*?)\s*\|", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s
    return "Objetivo macro nao identificado de forma deterministica."


def _section_matches(heading_title: str, instruction_tokens: set[str]) -> int:
    h_tokens = set(_tokenize(heading_title))
    if not instruction_tokens:
        return 0
    return len(h_tokens.intersection(instruction_tokens))


def _compute_dependencies(instruction: str, section: str, multi_section: bool) -> list[str]:
    deps: list[str] = []
    text = f"{instruction} {section}".lower()
    if any(k in text for k in ["sumario", "sumario", "anchor", "ancora", "ancoras"]):
        deps.append("sumario")
    if any(k in text for k in ["referencia", "referencias", "fontes"]):
        deps.append("fontes_referencias")
    if multi_section:
        deps.append("coerencia_cross_section")
    # Common operational coupling in this playbook
    if any(k in text for k in ["quick win", "quick wins", "roi", "priorizacao"]):
        deps.append("matriz_decisao_12_2")
    return sorted(set(deps))


def _detect_gaps(instruction: str, headings: list[Heading], min_match: int) -> list[str]:
    tokens = set(_tokenize(instruction))
    if not tokens:
        return ["instrucao_sem_tokens_relevantes"]
    best = 0
    for h in headings:
        best = max(best, _section_matches(h.title, tokens))
    if best >= min_match:
        return []
    return ["baixa_cobertura_semantica_nas_secoes_existentes"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic planning preflight for README updates.")
    parser.add_argument("--file", default="README.md", help="Markdown target.")
    parser.add_argument("--section", required=True, help="Target section title/number.")
    parser.add_argument("--instruction", required=True, help="Requested change.")
    parser.add_argument("--min-match", type=int, default=2, help="Minimum token overlap to consider section coverage.")
    args = parser.parse_args(argv)

    path = Path(args.file)
    text = _read_text(path)
    lines = text.splitlines()
    headings = _extract_headings(lines)

    instruction_tokens = set(_tokenize(args.instruction))
    scored = []
    for h in headings:
        score = _section_matches(h.title, instruction_tokens)
        if score > 0:
            scored.append({
                "title": h.title,
                "line": h.line_no,
                "level": h.level,
                "score": score,
            })
    scored.sort(key=lambda x: x["score"], reverse=True)

    multi_section = any(sep in args.section for sep in [",", ";", " e ", " and "])
    dependencies = _compute_dependencies(args.instruction, args.section, multi_section)
    gaps = _detect_gaps(args.instruction, headings, args.min_match)

    risk = 0.2
    if multi_section:
        risk += 0.2
    if dependencies:
        risk += min(0.3, 0.1 * len(dependencies))
    if gaps:
        risk += 0.2
    risk = min(1.0, round(risk, 2))

    coverage = 100 if not gaps else 65
    if scored:
        coverage = min(100, max(coverage, min(100, scored[0]["score"] * 20)))
    confidence = round(max(0.0, min(1.0, 1.0 - risk + 0.1)), 2)

    status = "pronto_para_execucao"
    if risk >= 0.6 or confidence < 0.8:
        status = "aguardando_usuario"

    payload = {
        "file": str(path),
        "section": args.section,
        "objective_macro": _extract_objective_macro(text),
        "candidate_sections": scored[:8],
        "declared_gaps": gaps,
        "cross_section_dependencies": dependencies,
        "planning_score": {
            "coverage_percent": int(coverage),
            "risk_score": risk,
            "confidence": confidence,
            "status": status,
        },
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError) as exc:
        print(f"erro: {exc}")
        raise SystemExit(1)
