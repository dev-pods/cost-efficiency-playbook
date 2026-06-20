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
- Se o pedido for ambiguo ou nao tiver secao alvo, responda com: "Esta skill requer um argumento --section especifico. Forneca o titulo exato da secao a ser atualizada." Nao prosseguir.

## Procedimento
1. Rodar preflight para risco/cobertura:
   - `python3 scripts/planner_preflight.py --file README.md --section "<secao>" --instruction "<instrucao>"`
2. Se `planning_score.status` for `aguardando_usuario`, interromper e coletar esclarecimentos.
3. Preparar conteudo final da secao em arquivo local (ex.: `/tmp/new-section.md`).
4. Se `--file` nao existir no caminho especificado, abortar imediatamente e retornar erro: "Arquivo nao encontrado: <path>. Nenhuma alteracao foi feita."
5. Executar pipeline com assertions:
   - [update_with_assertions.sh](./scripts/update_with_assertions.sh)
6. Se executar novamente o script com os mesmos argumentos `--file`, `--section` e `--new-content` produzir `char_delta` igual a 0 (nenhuma mudanca detectada), parar o ciclo e devolver controle ao Planner/Router.
7. Retornar um unico objeto JSON contendo exatamente estas chaves: `sections_changed` (array com nomes de secoes), `changed` (bool), `char_delta` (int), `scope_guard` (string: OK ou FAIL), `validate_readme_structure` (string: OK ou FAIL).

### Regra de limpeza
- Sempre criar o conteudo temporario fora do repositório com `mktemp`.
- Se `mktemp` falhar, abortar imediatamente com exit code 1 e retornar erro: "Falha ao criar arquivo temporario - verifique espaco em disco e permissoes. Nenhuma alteracao foi feita."
- Sempre usar `trap` para apagar o temporario em `EXIT`, `INT`, `TERM`, `HUP` e `ERR`.
- Nunca deixar temporario sobrar no workspace ou em `scripts/`.

## Assertions obrigatorias
- `changed == true` para alteracao esperada.
- `scope_guard.strict == OK` (sem alteracao colateral fora da secao).
- Se `scope_guard.strict` nao produzir saida ou retornar valor nao reconhecido, tratar como FAIL e abortar com erro: "A assertion scope_guard retornou saida inesperada: <raw output>."
- `validate_readme_structure --strict == OK`.
- Verificar assertions nesta ordem: (1) `changed`, (2) `scope_guard.strict`, (3) `validate_readme_structure`. Na primeira falha, abortar e retornar essa causa especifica. Nao verificar as assertions restantes apos uma falha.
- Em repeticao sem novo delta ou novo input: nao rodar o mesmo ciclo novamente.

## Comando recomendado
- `bash .github/skills/playbook-script-update/scripts/update_with_assertions.sh --file README.md --section "<secao>" --new-content "/tmp/new-section.md"`

## Validacao final (sem skill separada)
- `python3 scripts/validate_readme_structure.py --file README.md --strict`
- `tail -n 1 scripts/.update-history.jsonl`
