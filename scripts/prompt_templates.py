"""prompt_templates.py — Montagem do prompt em 'cascade' para prefix caching.

Conteúdo ESTÁVEL (regras/invariantes/contrato de saída, lido do template .prompt.md)
fica no topo → maximiza cache. Conteúdo DINÂMICO (seção + instrução) vai no fim → é
o único trecho que muda por execução (alavanca: Prefix caching).
"""
from __future__ import annotations

from dataclasses import dataclass

# Tokens-sentinela preenchidos por str.replace (NÃO usar str.format: o conteúdo
# da seção contém chaves de código/JSON que quebrariam o format).
_DYNAMIC_BLOCK = (
    "# [CONTEXTO DINÂMICO]\n"
    "- Classe da tarefa: <<TASK_CLASS>>\n"
    "- Seção-alvo: <<SECTION_TITLE>>\n"
    "- Instrução de mudança: <<INSTRUCTION>>\n\n"
    "## SEÇÃO ATUAL (fonte de verdade — reescreva APENAS esta)\n"
    "<<SECTION_CONTENT>>\n"
)


@dataclass
class Prompt:
    stable_prefix: str   # prefix-cacheável
    dynamic_suffix: str  # volátil

    @property
    def text(self) -> str:
        return f"{self.stable_prefix}\n\n{self.dynamic_suffix}"


def load_stable_prefix(template_path: str) -> str:
    try:
        with open(template_path, "r", encoding="utf-8") as fh:
            return fh.read().rstrip() + "\n"
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Template inexistente: {template_path}") from exc


def build_prompt(
    template_path: str,
    *,
    section_title: str,
    section_content: str,
    instruction: str,
    task_class: str,
) -> Prompt:
    """Monta o prompt cascade. SECTION_CONTENT é substituído por último para que
    chaves/sentinelas presentes no conteúdo não afetem as demais substituições."""
    suffix = (
        _DYNAMIC_BLOCK
        .replace("<<TASK_CLASS>>", task_class)
        .replace("<<SECTION_TITLE>>", section_title)
        .replace("<<INSTRUCTION>>", instruction)
        .replace("<<SECTION_CONTENT>>", section_content.rstrip() + "\n")
    )
    return Prompt(stable_prefix=load_stable_prefix(template_path), dynamic_suffix=suffix)
