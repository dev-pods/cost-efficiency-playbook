"""patch_applier.py — Aplicação cirúrgica e validada de uma seção nova.

Recebe arquivo, título da seção e o novo conteúdo (gerado pelo LLM). Localiza o
bloco antigo via context_slicer, valida a integridade do Markdown e substitui no
lugar. O LLM emite SÓ a seção nova; o resto do arquivo nunca passa pelo modelo
(alavanca: Tool result shaping + Input compression).
"""
from __future__ import annotations

import re
import sys

from context_slicer import Slice, _HEADER_RE, slice_file

_FENCE_RE = re.compile(r"^```", flags=re.MULTILINE)


class PatchValidationError(ValueError):
    """O conteúdo novo não satisfaz as invariantes de Markdown."""


def _first_header(content: str) -> tuple[int, str] | None:
    for line in content.splitlines():
        m = _HEADER_RE.match(line)
        if m:
            return len(m.group(1)), m.group(2).strip()
    return None


def validate(old: Slice, new_content: str) -> None:
    if not new_content.strip():
        raise PatchValidationError("Conteúdo novo vazio.")
    header = _first_header(new_content)
    if header is None:
        raise PatchValidationError("Conteúdo novo não começa com cabeçalho.")
    level, _title = header
    if level != old.level:
        raise PatchValidationError(
            f"Nível do cabeçalho mudou: era H{old.level}, veio H{level}."
        )
    if len(_FENCE_RE.findall(new_content)) % 2 != 0:
        raise PatchValidationError("Cercas de código (```) desbalanceadas na seção.")


def apply_patch(path: str, section: str, new_content: str, *, backup: bool = True) -> None:
    sl = slice_file(path, section)
    validate(sl, new_content)

    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    new_block = new_content if new_content.endswith("\n") else new_content + "\n"
    patched = "".join(lines[: sl.start] + [new_block] + lines[sl.end :])

    # Validação global: o documento inteiro deve manter cercas balanceadas.
    if len(_FENCE_RE.findall(patched)) % 2 != 0:
        raise PatchValidationError("Documento ficou com cercas de código desbalanceadas.")

    if backup:
        with open(path + ".bak", "w", encoding="utf-8") as fh:
            fh.writelines(lines)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(patched)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("uso: patch_applier.py <arquivo.md> '<seção>' <novo_conteudo.md>", file=sys.stderr)
        raise SystemExit(2)
    try:
        with open(sys.argv[3], "r", encoding="utf-8") as fh:
            apply_patch(sys.argv[1], sys.argv[2], fh.read())
    except (LookupError, FileNotFoundError, PatchValidationError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: seção {sys.argv[2]!r} atualizada em {sys.argv[1]}")
