---
description: "Use when doing full playbook regeneration, structural expansion, or cross-section updates in README.md with strict FinOps and architecture constraints. Keywords: playbook update, expand catalog, regenerate sections, cost engineering, universal stack."
name: "Playbook Update Guidance"
applyTo: "README.md"
---
# Playbook Update Guidance

## Objective
Refactor or expand README.md as an executive-technical how-to manual focused on cost efficiency, context engineering, model routing, and agent governance.

## Deterministic-First Rules
- Treat README.md current state as source of truth.
- Prefer local deterministic steps (slice, route, patch, validate) before broad generation.
- Keep changes scoped to target sections and avoid unrelated rewrites.
- Preserve heading hierarchy and anchor stability when possible.

## Section Authoring Contract
- Keep conceptual rationale concise (max 3 sentences per topic).
- Prioritize implementation detail (how-to, examples, operational checklists).
- Include Mecanismo de Acao table when section discusses problem/solution pairs.
- Include direct cost lever when applicable; otherwise state that none applies.
- For uncertain API/version details, explicitly mark as unverified and point to official docs.

## Resource Coverage Contract
When expanding catalog or pillars, ensure explicit coverage for:
- Prompt Engineering: few-shot, CoT, prompt chaining, ReAct.
- Model Engineering: routing by canonical tiers, MoA, quantization paths.
- Context Engineering: hybrid RAG, filtering, anchoring, docs-as-retrieval, legacy schema mapping.
- Agent Architecture: IDE agents vs backend orchestration agents, HITL patterns.
- Customization Files: AGENTS.md, .copilot-instructions.md, .github/copilot-instructions.md, .agent.md.
- Tools and Extensions: AI CLI, IDE extensions, MCP integration and enterprise controls.

## Execution Pattern
1. Plan section targets and acceptance criteria.
2. For each section, use lightweight edit cycle:
   - use scripts/run_update.py in dry-run for scoped context
   - generate section content
   - apply via scripts/update_cycle.py for patch + feedback history
3. Validate markdown integrity and summarize risk.

## Section Template
Use scripts/templates/playbook-section.template.md as the default skeleton for new or heavily revised sections.

## Item Template Contract
- Use scripts/templates/playbook-item.template.md for H3+ items that describe operational patterns, quick wins, or point recommendations.
- Preserve the standardized suggestion blocks: Quando usar, Sugestão padronizada, Como implementar, Validação, and Alavanca de custo direta.
- Do not collapse item guidance into freeform prose when the section is an itemized recommendation; keep the template structure explicit.
