---
description: "Use ao fazer regeneração completa do playbook, expansão estrutural ou atualizações entre seções em README.md com restrições rigorosas de FinOps e arquitetura. Palavras-chave: atualização do playbook (playbook update), expandir catálogo (expand catalog), regenerar seções (regenerate sections), engenharia de custos (cost engineering), stack universal (universal stack)."
name: "Guia de Atualização do Playbook"
applyTo: "README.md"
---
# Guia de Atualização do Playbook

## Objetivo
Refatore ou expanda o README.md como um manual executivo-técnico orientado a implementação, com foco em eficiência de custos, engenharia de contexto, roteamento de modelos e governança de agentes.

## Regras Determinísticas Primeiro
- Trate o estado atual do README.md como fonte da verdade para todas as seções existentes e para a estrutura de headings.
- Todo conteúdo em prosa gerado deve estar em inglês. Os termos em português (Mecanismo de Acao, Quando usar, Sugestão padronizada, Como implementar, Validação, Alavanca de custo direta) são identificadores de template e devem aparecer verbatim apenas como headings, sem tradução.
- Prefira etapas locais determinísticas (slice, route, patch, validate) antes de geração ampla.
- Mantenha as mudanças restritas às seções alvo e evite reescritas não relacionadas. Seções alvo são aquelas explicitamente listadas no Passo 1 da saída de planejamento do Padrão de Execução. Nenhuma seção fora dessa lista pode ser modificada.
- Preserve a hierarquia de headings e a estabilidade das âncoras sempre que possível.
- Se um ciclo determinístico não produzir novo sinal para o mesmo alvo, pare e devolva o controle em vez de repetir o mesmo passo. Ao parar por ausência de novo sinal, emita exatamente: "Cycle halted: no new signal detected for [section name]. Provide updated input, a changed planning signal, or a new target section to continue." Não encerre silenciosamente nem repita a última saída.

## Contrato de Redação de Seção
- Mantenha a justificativa conceitual concisa (máximo de 3 frases por tópico).
- Priorize detalhes de implementação (como fazer, exemplos, checklists operacionais).
- Inclua uma tabela Mecanismo de Acao quando uma seção contiver dois ou mais pares problema/solução explicitamente rotulados como sua estrutura organizacional principal.
- Inclua uma alavanca de custo direta quando a seção descrever uma técnica, ferramenta ou decisão arquitetural que tenha impacto mensurável em custos de computação, tokens ou licenciamento. Caso contrário, declare: "Cost lever: none - this section covers [concept/governance/reference] only."
- Para qualquer endpoint de API, número de versão ou flag que não seja citado diretamente da fonte da verdade README.md, marque como "[UNVERIFIED - confirm at <official doc URL>]" e não afirme como fato.

## Contrato de Cobertura de Recursos
Ao expandir catálogo ou pilares, garanta cobertura explícita para:
- Prompt Engineering: few-shot, CoT, prompt chaining, ReAct.
- Model Engineering: roteamento por tiers canônicos, MoA, caminhos de quantização.
- Context Engineering: RAG híbrido, filtragem, ancoragem, docs-as-retrieval, mapeamento de esquemas legados.
- Agent Architecture: agentes de IDE vs agentes de orquestração de backend, padrões HITL.
- Customization Files: AGENTS.md, .copilot-instructions.md, .github/copilot-instructions.md, .agent.md.
- Tools and Extensions: AI CLI, extensões de IDE, integração MCP e controles corporativos.

## Padrão de Execução
1. Planeje as seções alvo e os critérios de aceite.
2. Para cada seção, use um ciclo leve de edição:
   - 2a. Execute scripts/run_update.py --dry-run --section <target> e confirme que o contexto delimitado está correto antes de prosseguir.
   - 2b. Gere o conteúdo da seção com base nesse contexto delimitado.
   - 2c. Aplique via scripts/update_cycle.py --patch --log-feedback. Não avance para 2c se 2a produzir erros ou escopo inesperado.
   - Se qualquer script estiver indisponível ou retornar código de saída diferente de zero, interrompa o ciclo, reporte a falha com o erro exato e não prossiga para geração de conteúdo ou aplicação de patch até que o problema seja resolvido.
3. Valide a integridade do markdown e resuma o risco.
4. Não reexecute o ciclo da mesma seção sem nova entrada ou sem mudança no sinal de planejamento.

## Template de Seção
Use scripts/templates/playbook-section.template.md como esqueleto padrão para novas seções. Para seções existentes com revisão pesada, preserve a estrutura atual de headings do README.md e mapeie o conteúdo para os blocos do template sem substituir o esqueleto da seção.

## Contrato de Template de Item
- Use scripts/templates/playbook-item.template.md para itens H3+ que descrevem padrões operacionais, quick wins ou recomendações pontuais.
- Preserve os blocos padronizados de sugestão: Quando usar, Sugestão padronizada, Como implementar, Validação e Alavanca de custo direta. Todos os headings de blocos padronizados devem aparecer exatamente como escritos, independentemente do idioma do conteúdo ao redor. Não traduza esses headings.
- Não colapse a orientação de item em prosa livre quando a seção for uma recomendação em formato de lista; mantenha a estrutura do template explícita.
