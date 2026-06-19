---
name: playbook-script-update
description: "Atualizacao cirurgica e script-first do README com assertions deterministicas. Use para editar secao, patch seguro, scope guard, validacao estrutural, changed/char_delta gate, baixo consumo de contexto."
argument-hint: "--file README.md --section \"6.6.1 CLI de IA\" --new-content /tmp/secao.md"
user-invocable: true
---

# Playbook Script Update

Skill para atualizar secoes do playbook com fluxo deterministic-first e assertions explicitas.
Este wrapper e o recurso preferencial quando o fluxo agentico selecionar `resource_recommendation=skill-wrapper`.

## Quando usar
- Mudanca cirurgica em uma secao do README.
- Necessidade de evidencias objetivas (changed, char_delta, scope_guard, estrutura).
- Prioridade em baixo custo de contexto e baixa variacao de execucao.

## Nao usar
- Refatoracao ampla multi-secao sem planejamento previo.
- Pedido ambigiuo sem secao alvo definida.

## Procedimento
1. (Opcional fora do Router) Rodar preflight para risco/cobertura:
   - `python3 scripts/planner_preflight.py --file README.md --section "<secao>" --instruction "<instrucao>"`
2. Se `planning_score.status` for `aguardando_usuario`, interromper e coletar esclarecimentos.
3. Preparar conteudo final da secao em arquivo local (ex.: `/tmp/new-section.md`).
4. Executar pipeline com assertions:
   - [update_with_assertions.sh](./scripts/update_with_assertions.sh)
5. Se o mesmo input nao produzir novo delta valido, parar o ciclo e devolver controle ao Planner/Router em vez de repetir.
6. Retornar apenas evidencias compactas:
   - secoes alteradas
   - changed/char_delta
   - scope_guard
   - validate_readme_structure

### Regra de limpeza
- Sempre criar o conteudo temporario fora do repositório com `mktemp`.
- Sempre usar `trap` para apagar o temporario em `EXIT`, `INT`, `TERM`, `HUP` e `ERR`.
- Nunca deixar temporario sobrar no workspace ou em `scripts/`.

## Assertions obrigatorias
- `changed == true` para alteracao esperada.
- `scope_guard.strict == OK` (sem alteracao colateral fora da secao).
- `validate_readme_structure --strict == OK`.
- Em falha de assertion: abortar ciclo e retornar causa objetiva.
- Em repeticao sem novo delta ou novo input: nao rodar o mesmo ciclo novamente.

## Comando recomendado
- `bash .github/skills/playbook-script-update/scripts/update_with_assertions.sh --file README.md --section "<secao>" --new-content "/tmp/new-section.md"`

## Validacao final (sem skill separada)
- `python3 scripts/validate_readme_structure.py --file README.md --strict`
- `tail -n 1 scripts/.update-history.jsonl`
