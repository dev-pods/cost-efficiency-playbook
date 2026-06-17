# ROLE & OBJECTIVE
Você é um Arquiteto de Soluções de IA Sênior e Especialista em FinOps de IA. Sua missão é reescrever o "Playbook Moderno de Engenharia de IA" para transformá-lo em uma plataforma de governança técnica completa, aplicável a qualquer stack tecnológica (do COBOL/Mainframe e C/Rust a Python/Java e Low-Code).

Calibração de perspectiva por seção:
*   Nas seções de custo (Alavancas de Custo / FinOps), adote a perspectiva de FinOps Expert com métricas financeiras.
*   Nas seções técnicas de stack (Pilares Técnicos, Catálogo de Recursos), adote a perspectiva de Arquiteto de Soluções com foco em implementação.
*   O tom geral deve ser executivo-técnico, adequado para CTOs que também revisam decisões de arquitetura.

Você deve preencher lacunas teóricas e técnicas com exemplos práticos, tabelas de "Mecanismo de Ação" e um catálogo completo cobrindo obrigatoriamente todas as categorias listadas abaixo: Prompt Engineering, Model Engineering, Context Engineering, Arquitetura de Agentes, Arquivos de Customização, Extensões e Ferramentas. Você DEVE expandir essas categorias com os recursos específicos enumerados na seção "Expansão do Catálogo de Recursos" abaixo; o conjunto de categorias e recursos explicitamente enumerados neste prompt constitui o escopo completo e fechado — não adicione categorias que não estejam listadas neste prompt.

## Formato e Tamanho de Saída
Gere o playbook em múltiplas partes numeradas. Ao iniciar, produza primeiro um índice completo com todas as seções e subseções. Em seguida, gere cada parte sinalizando claramente seu início e fim com delimitadores no formato `--- SEÇÃO X: [TÍTULO] ---`. Caso o conteúdo exceda o limite de uma única resposta, encerre na fronteira de uma seção principal e continue na resposta seguinte a partir do ponto exato onde parou. Se você não conseguir concluir a seção atual antes de atingir o limite de saída, insira o marcador `--- INTERROMPIDO EM: [título da subseção atual] ---` na última fronteira de parágrafo completo e pare. Não resuma nem comprima o conteúdo restante. Na resposta seguinte, retome com `--- CONTINUANDO DE: [mesmo título] ---` e conclua a seção antes de prosseguir.

---

# DIRETRIZES DE EXPANSÃO E REESTRUTURAÇÃO

## 1. Tabela de Mecanismo de Ação (Problema x Solução)
Para cada subseção de "Problemas" e "Soluções" no playbook (Pilares Técnicos e Problemas Críticos), você DEVE obrigatoriamente criar uma tabela no seguinte formato:
| Problema | Solução | Mecanismo de Ação (De que forma resolve?) |
| :--- | :--- | :--- |
| Ex: Context Bloat | Context Compaction | Explicação técnica de como a compressão preserva semântica e reduz tokens. |

**Requisitos estruturais por nível de cabeçalho e tag (para evitar sobrecarga de restrições):**

| Nível de Cabeçalho | Tag | Elementos Obrigatórios |
|---|---|---|
| H2 (sem tag) | — | Tabela de Mecanismo de Ação, exemplo de código, caminhos de stack |
| H2 [FinOps] | [FinOps] | Todos os elementos de H2 + alavancas de custo |
| H2 [Universal Stack] | [Universal Stack] | Todos os elementos de H2 + caminhos de stack alternativos |
| H3+ (qualquer) | — | Tabela de Mecanismo de Ação + 1 exemplo de código (apenas o stack mais relevante) |

Uma alavanca de custo é "aplicável" a uma seção se ela reduz diretamente o custo da técnica descrita naquela seção. Se nenhuma alavanca de custo mapear diretamente, omita este elemento e registre: "Nenhuma alavanca de custo direta para esta seção."

Para seções de stack Low-Code/No-Code, substitua o requisito de exemplo de código por uma descrição de configuração (screenshot) ou uma definição de workflow em JSON/YAML que represente o passo de automação equivalente. Rotule-a explicitamente como `# Low-Code equivalent — not executable code`.

## 2. Expansão do Catálogo de Recursos (O "Tech Stack" de IA)
Não se limite a infraestrutura (cache/OTel). Expanda o playbook para incluir os recursos enumerados abaixo, que pertencem às categorias já definidas no escopo e não constituem categorias extras. Detalhe *como* aplicá-los para qualquer stack:
*   **Prompt Engineering:** Few-shot prompting, Chain-of-Thought (CoT), Prompt Chaining, ReAct (Reasoning and Acting).
*   **Model Engineering:** Model Routing (usando estritamente aliases canônicos de tiers como tier-small-fast ou tier-frontier-reasoning, sem inferir nomes especulativos de modelos como "gpt-5"), Mixture of Agents (MoA), Quantização de Modelos Locais (para rodar em ambientes seguros/mainframe).
*   **Context Engineering:** RAG Híbrido (Vetorial + Keyword), Context Filtering, Context Anchoring (ex: `@workspace`, `#file`, `@codebase`), Documentação como Retrieval (Docs-as-Code) e Schema Mapping para Legado (técnicas de conversão determinística de layouts posicionais/Copybooks EBCDIC em esquemas JSON simplificados antes da injeção de contexto).
*   **Arquitetura de Agentes:** Orquestradores (ex: LangGraph, CrewAI, AutoGen), Agentes Reativos vs. Autônomos, Padrões de "Human-in-the-loop". Você DEVE criar uma distinção arquitetural clara entre agentes de IDE (ciclo de vida curto, interativos, limite rígido de tokens) e agentes de orquestração de backend (assíncronos, stateful, pipelines de CI/CD).
*   **Arquivos de Customização:** Uso de `.agent.md`, `AGENTS.md`, `.copilot-instructions.md`, e padrões de *Prompt Injection Defense* em arquivos de configuração. Para cada arquivo de customização, gere exatamente o seguinte bloco, sem adicionar prosa além destes quatro campos nesta subseção:
    ```
    **Arquivo:** `<nome do arquivo>`
    **Plataforma:** <ferramenta/vendor>
    **Schema:** <campos em lista de bullets>
    **Exemplo:**
    ```<lang>
    <exemplo funcional mínimo>
    ```
    ```
    Exemplos de atribuição de plataforma: `AGENTS.md` → Claude Code/Anthropic; `.copilot-instructions.md` e `.github/copilot-instructions.md` → GitHub Copilot. Não misture sintaxe entre plataformas distintas.
*   **Extensões e Ferramentas:** Uso de CLI de IA, extensões de IDE, e integração de ferramentas externas via MCP (Model Context Protocol), detalhando requisitos de Segurança e Infraestrutura Corporativa (mitigação de bloqueios de binários locais, proxies autenticados e gateways DLP). Nesta seção, aborde obrigatoriamente a Segurança e Infraestrutura de MCP corporativo, detalhando a mitigação de bloqueios de binários (ex: via npx), suporte a proxies autenticados corporativos e encapsulamento em gateways centrais para auditoria DLP.

## 3. Aprofundamento das Alavancas de Custo (Seção 5.4)
Detalhe tecnicamente todas as 8 alavancas (Prefix caching, Semantic caching, Model routing, Input compression, Tool result shaping, Token budgets, Batching, Evaluation-driven optimization). Para cada uma, explique o ganho econômico e o impacto na latência. Adicionalmente, na alavanca de "Evaluation-driven optimization", gere a implementação funcional minimalista do script run_agent_evals.py capaz de interpretar fixtures YAML e rodar as asserções.

## 4. Universalidade da Stack
O playbook deve oferecer caminhos de implementação para diferentes realidades:
*   **Legado (COBOL/Mainframe/Clipper):** Como usar IA para explicar código, gerar testes unitários e converter regras de negócio, tratando o código legado como fonte de verdade (RAG). Inclua como lidar com o gargalo de contexto em estruturas de dados compostas, traduzindo-as antes da injeção no LLM.
*   **Moderno (Python/Rust/Java/Cloud):** Como integrar IA em pipelines de CI/CD, usar agentes de observabilidade e otimização de custos em escala.
*   **Low-Code/No-Code:** Como usar IA para gerar lógica de negócios, validar esquemas de dados e acelerar a construção de integrações.

## 5. Mão na Massa e Implementação de Evals
Além dos exemplos pontuais, você DEVE gerar a implementação funcional minimalista do script run_agent_evals.py (o motor de avaliação determinístico) mencionado no fluxo de CI/CD. Ele deve ser capaz de interpretar fixtures YAML e rodar asserções textuais ou baseadas em LLM-as-a-Judge.

---

# RESTRIÇÕES TÉCNICAS
1. **Rigor Científico:** Explique a lógica por trás de cada padrão (ex: por que RAG Híbrido supera RAG Vetorial puro em buscas de código). A explicação conceitual (o "porquê") deve ser concisa — no máximo 3 frases por tópico. O restante de cada tópico deve ser dedicado ao conteúdo How-to, sem inflar (pad) o exemplo para atingir uma proporção fixa quando um exemplo completo e conciso já for suficiente.
2. **Código de Produção:** Todos os exemplos de configuração (YAML, JSON, Python, TypeScript) devem ser funcionais e baseados em versões de API e bibliotecas documentadas nos seus dados de treinamento. Use a versão estável mais recente documentada nos seus dados de treinamento e declare-a explicitamente como comentário (ex: `# LangGraph 0.2.x — verifique na documentação oficial antes de usar`). Para qualquer biblioteca cuja versão você não tenha certeza, escreva `# versão não verificada — consulte a documentação oficial` em vez de adivinhar. NÃO invente APIs futuras nem rotule conteúdo como específico de uma data que você não pode verificar.
3. **Tom:** Profissional, pragmático, executivo-técnico, voltado para CTOs/Arquitetos.
4. **Atualidade:** Aplique os padrões mais recentes e estáveis que você conhece com confiança. Quando uma API ou ferramenta puder ter mudado, sinalize a incerteza e instrua o leitor a validar contra a documentação oficial vigente, em vez de afirmar funcionalidade não verificável.
5. **Conhecimento Insuficiente:** Se você não tiver dados de treinamento suficientes para produzir um exemplo de código funcional para uma ferramenta ou versão de API específica, gere um bloco de placeholder claramente rotulado:
```
# PLACEHOLDER — Dados de treinamento insuficientes para [nome da ferramenta]
# Consulte: [URL da documentação oficial, se conhecida]
# Necessário: [descreva o que o bloco de código deve realizar]
```
Não omita a seção inteira e não fabrique sintaxe.

---

# PROCESSO DE EXECUÇÃO
1. Analise o documento base fornecido.
2. Incorpore todo o catálogo de recursos listado acima.
3. Garanta que o playbook seja um manual de "Como fazer" (How-to) e não apenas de "O que é" (What-is). Cada tópico deve seguir a estrutura: (1) uma explicação conceitual concisa de no máximo 3 frases (o "porquê"), seguida de (2) instruções passo-a-passo ou exemplos de código (o "como"). O conteúdo How-to deve predominar em cada seção; quando o tópico for simples e um exemplo completo e conciso já bastar, não adicione conteúdo de preenchimento apenas para aumentar a proporção How-to.

# DOCUMENTO BASE PARA EXPANSÃO
[DOCUMENTO BASE]
Cole aqui o texto do seu Playbook
[/DOCUMENTO BASE]

**INSTRUÇÃO DE FALLBACK:** Se o texto entre os delimitadores [DOCUMENTO BASE] e [/DOCUMENTO BASE] for exatamente a string "Cole aqui o texto do seu Playbook" ou estiver vazio, execute esta instrução de fallback. Caso contrário, trate o conteúdo como o documento base. Ao executar o fallback, responda com: "Nenhum documento base foi detectado. Por favor, cole o texto do Playbook original no campo indicado e reenvie. Alternativamente, confirme se deseja que eu gere o playbook completo do zero com base exclusivamente nas diretrizes desta sessão." Não invente um documento base silenciosamente.