"""context_slicer.py — Extração determinística de uma seção Markdown.

Lê um arquivo Markdown e devolve apenas o bloco sob um cabeçalho H2–H6 alvo
(incluindo subseções), parando no próximo cabeçalho de nível igual ou superior.
Trabalho 100% determinístico = zero token de LLM (alavanca: Input compression).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


@dataclass
class Slice:
    header: str  # linha de cabeçalho original
    title: str   # texto do cabeçalho sem os '#'
    level: int   # 1..6
    start: int   # índice da linha do cabeçalho (0-based)
    end: int     # índice exclusivo do fim do bloco
    text: str    # conteúdo do bloco (cabeçalho + corpo)


class SectionNotFoundError(LookupError):
    """Nenhum cabeçalho casou com o alvo."""


class AmbiguousSectionError(LookupError):
    """Mais de um cabeçalho casou com o alvo."""


def _normalize(value: str) -> str:
    # Reduz a alfanumérico minúsculo p/ casar "5.4 Cost" com "5.4. Cost".
    return re.sub(r"[^0-9a-z]+", "", value.lower())


def find_slice(lines: list[str], target: str) -> Slice:
    """Localiza a seção-alvo dentro de uma lista de linhas já lida."""
    target_norm = _normalize(target)
    if not target_norm:
        raise ValueError("Alvo de seção vazio.")

    headers: list[tuple[int, int, str]] = []  # (idx, level, title)
    matches: list[int] = []
    for i, line in enumerate(lines):
        m = _HEADER_RE.match(line)
        if not m:
            continue
        title = m.group(2).strip()
        headers.append((i, len(m.group(1)), title))
        h_norm = _normalize(title)
        if h_norm == target_norm or h_norm.startswith(target_norm):
            matches.append(len(headers) - 1)

    if not matches:
        raise SectionNotFoundError(f"Seção não encontrada: {target!r}")

    # Casamento exato tem prioridade sobre 'startswith'.
    exact = [k for k in matches if _normalize(headers[k][2]) == target_norm]
    chosen = exact or matches
    if len(chosen) > 1:
        cands = ", ".join(headers[k][2] for k in chosen)
        raise AmbiguousSectionError(f"Alvo {target!r} é ambíguo: {cands}")

    start, level, title = headers[chosen[0]]
    end = len(lines)
    for idx, lvl, _ in headers[chosen[0] + 1:]:
        if lvl <= level:  # próximo cabeçalho de nível igual ou superior
            end = idx
            break

    return Slice(
        header=lines[start].rstrip("\n"),
        title=title,
        level=level,
        start=start,
        end=end,
        text="".join(lines[start:end]),
    )


def slice_file(path: str, target: str) -> Slice:
    """Abre o arquivo e devolve a seção-alvo."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Arquivo inexistente: {path}") from exc
    return find_slice(lines, target)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("uso: context_slicer.py <arquivo.md> '<seção>'", file=sys.stderr)
        raise SystemExit(2)
    try:
        sys.stdout.write(slice_file(sys.argv[1], sys.argv[2]).text)
    except (LookupError, FileNotFoundError, ValueError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        raise SystemExit(1)
