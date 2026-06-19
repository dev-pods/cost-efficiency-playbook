---
description: "Slash command interativo: atualiza cirurgicamente UMA seção do playbook usando o Copilot como LLM e os scripts determinísticos (slice/route/patch) para economizar tokens."
agent: agent
tools: ['runCommands', 'editFiles', 'problems']
---

<!--
   /update — Driver INTERATIVO do pipeline update.
   Diferença para scripts/templates/update.template.md:
      - update.template.md = prefixo ESTÁVEL injetado pelo pipeline headless (run_update.py).
    - ESTE arquivo = slash command que usa VOCÊ (Copilot) como o LLM, delegando slice/route/patch
      aos scripts determinísticos. O trabalho determinístico roda em Python (zero token);
      você só gera a seção nova.
-->

# [OBJECTIVE]
Aplicar a instrução do usuário a **uma única seção** de `README.md` (o playbook), gerando apenas
o markdown da seção refatorada e gravando-o por patch determinístico — sem reescrever
o documento inteiro.

# [PROCESS]
1. **Montar o contexto (determinístico, sem custo de modelo).**
   Rode no terminal, a partir da raiz do repositório:
   ```bash
   python3 scripts/run_update.py \
     --file README.md \
     --section "${input:secao:Numeração + título do H2/H3 (ex.: \"5.4. Cost Engineering\")}" \
     --instruction "${input:instrucao:O que mudar na seção}" \
     --class ${input:classe:conteudo-tecnico} \
     --dry-run
   ```
   A saída é o prompt completo: `[INVARIANTES]`, `[CONTRATO DE SAÍDA]` e a `SEÇÃO ATUAL`
   já fatiada. O `stderr` mostra a rota/tier escolhida. Se o comando falhar (seção não
   encontrada/ambígua), corrija o `--section` e repita — não invente o conteúdo.

2. **Gerar a seção nova.** Seguindo **estritamente** o `[CONTRATO DE SAÍDA]` impresso:
   produza **somente** o markdown da seção refatorada, começando pelo mesmo cabeçalho
   (mesmo nível e numeração). Sem cercas externas, sem preâmbulo, sem outras seções.

3. **Gravar em arquivo temporário do sistema.** Escreva a seção gerada em um caminho
   fora do repositório, preferencialmente em `${TMPDIR:-/tmp}`, usando `mktemp` e um `trap`
   para remover o arquivo em qualquer saída do processo (somente o conteúdo da seção).

4. **Aplicar por ciclo determinístico com retroalimentação (valida e registra).**
   ```bash
   python3 scripts/update_cycle.py \
     --file README.md \
     --section "${input:secao}" \
   --new-content "<arquivo-temporario-fora-do-repo>"
   ```
   Se o ciclo reprovar (nível de cabeçalho mudou, cercas desbalanceadas),
   corrija a seção gerada e repita o passo 3–4. Não force.

5. **Validar e limpar.** Cheque `README.md` no painel de problemas (`#problems`).
   O arquivo temporário da etapa 3 deve ser removido automaticamente pelo `trap`; mantenha
   o backup `README.md.bak` criado pelo ciclo (via `patch_applier`) ou descarte-o conforme
   preferir. Consulte também o último evento em `scripts/.update-history.jsonl`.

# [OUTPUT]
Sem saudações nem preenchimento. Responda com:
- **Seção editada:** `<numeração + título>`
- **Rota/tier:** `<alias impresso no dry-run>`
- **Resumo da mudança:** 1–3 linhas.
- **Validação:** resultado do `update_cycle.py` + `#problems` (ok ou corrigido).
- **Riscos restantes:** 0–2 itens, ou "nenhum".
