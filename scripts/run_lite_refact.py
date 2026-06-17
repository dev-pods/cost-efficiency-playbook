"""run_lite_refact.py — Orquestrador headless do pipeline lite-refact.

Fluxo determinístico (zero token fora da única chamada ao LLM):
    slice → route → build prompt → LLM → patch.

A chamada ao provedor é um adaptador plugável (call_llm). Use --dry-run para
inspecionar o prompt montado e a rota sem gastar token.
"""
from __future__ import annotations

import argparse
import os
import sys

from context_slicer import slice_file
from model_router import TaskMeta, route
from patch_applier import apply_patch
from prompt_templates import build_prompt

_TEMPLATE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "templates", "lite-refact.template.md")
)


def call_llm(prompt_text: str, *, model_alias: str, max_output_tokens: int) -> str:
    # PLACEHOLDER — conecte ao seu gateway/SDK (OpenAI, Anthropic, Azure, vLLM…).
    # Deve retornar SOMENTE o markdown da seção refatorada.
    # Consulte a documentação oficial do provedor para a sintaxe atual da API.
    raise NotImplementedError(
        f"Implemente call_llm() para o seu provedor. Mapeie o alias {model_alias!r} "
        f"para um modelo real e respeite max_output_tokens={max_output_tokens}."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refatoração cirúrgica de uma seção do playbook.")
    parser.add_argument("--file", required=True, help="Markdown alvo (ex.: README.md).")
    parser.add_argument("--section", required=True, help="Numeração + título do H2/H3.")
    parser.add_argument("--instruction", required=True, help="O que mudar na seção.")
    parser.add_argument("--class", dest="task_class", default="conteudo-tecnico",
                        choices=["texto", "conteudo-tecnico", "arquitetura"])
    parser.add_argument("--affects-summary", action="store_true",
                        help="A mudança mexe no Sumário/âncoras (força tier forte).")
    parser.add_argument("--template", default=_TEMPLATE)
    parser.add_argument("--dry-run", action="store_true",
                        help="Monta e imprime o prompt + rota, sem chamar o LLM nem gravar.")
    args = parser.parse_args(argv)

    sl = slice_file(args.file, args.section)
    chosen = route(TaskMeta(task_class=args.task_class, affects_summary=args.affects_summary))
    prompt = build_prompt(
        args.template,
        section_title=sl.title,
        section_content=sl.text,
        instruction=args.instruction,
        task_class=args.task_class,
    )

    if args.dry_run:
        sys.stdout.write(prompt.text)
        print(f"\n\n--- rota: {chosen.alias} (out<= {chosen.max_output_tokens}) ---", file=sys.stderr)
        return 0

    new_content = call_llm(prompt.text, model_alias=chosen.alias, max_output_tokens=chosen.max_output_tokens)
    apply_patch(args.file, args.section, new_content)
    print(f"OK: seção {args.section!r} refatorada via {chosen.alias}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LookupError, FileNotFoundError, ValueError, NotImplementedError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        raise SystemExit(1)
