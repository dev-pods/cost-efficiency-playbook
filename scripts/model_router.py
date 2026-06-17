"""model_router.py — Roteamento declarativo de modelo por classe de tarefa.

Mapeia metadados da tarefa para um alias canônico de tier (sem nomes especulativos
de modelos) e injeta limites de token. Evita usar tier caro em tarefa trivial
(alavanca: Model routing).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    alias: str
    max_input_tokens: int
    max_output_tokens: int
    temperature: float = 0.2


# Aliases canônicos — mapeie cada um para um modelo real no seu gateway/SDK.
ROUTES: dict[str, Route] = {
    "texto": Route("tier-small-fast", max_input_tokens=8_000, max_output_tokens=2_000),
    "conteudo-tecnico": Route("tier-mid-balanced", max_input_tokens=16_000, max_output_tokens=4_000),
    "arquitetura": Route("tier-frontier-reasoning", max_input_tokens=32_000, max_output_tokens=8_000),
}
_DEFAULT = "conteudo-tecnico"


@dataclass
class TaskMeta:
    task_class: str = _DEFAULT
    failed_attempts: int = 0
    affects_summary: bool = False  # mexe no Sumário/âncoras
    multi_section: bool = False


def route(meta: TaskMeta) -> Route:
    """Devolve a rota adequada, aplicando regras de escalada de risco."""
    cls = meta.task_class if meta.task_class in ROUTES else _DEFAULT
    # Condições de alto risco forçam o tier forte.
    if meta.failed_attempts >= 2 or meta.affects_summary or meta.multi_section:
        cls = "arquitetura"
    return ROUTES[cls]


if __name__ == "__main__":
    cls = sys.argv[1] if len(sys.argv) > 1 else _DEFAULT
    print(json.dumps(route(TaskMeta(task_class=cls)).__dict__, ensure_ascii=False, indent=2))
