# Frente: paridade operacional no Codex

## Card

`T-040` — transformar os atritos observados num projeto externo em comportamento padrão do plugin para qualquer repositório usado com Claude Code ou Codex.

## Evidência confirmada em 2026-08-09

- A árvore do repositório está limpa e a fonte, marketplace e cache do Codex estão em `0.20.0`.
- `codex plugin list` mostra `orq@orquestra` como `installed, enabled`.
- O Codex carrega a skill `orq`, mas não converte `orq/commands/*.md` em comandos `/orq:*`.
- A interface suportada pelo Codex é linguagem natural ou seleção por `/skills`; custom prompts com slash command são locais e estão depreciados.
- O Codex oferece `/statusline` nativa com itens fechados. A issue `openai/codex#17827` segue aberta para execução de script arbitrário, necessária para renderizar diretamente o board do Orquestra.
- O relato externo também expôs a necessidade de defaults reais por host: Manager Sol/high, Planner Sol/ultra, Implementer Terra/xhigh e painel obrigatório Opus 5 + Kimi K3.

## Escopo relacionado já existente

- `T-026`: instalação e smoke em hosts fora do Claude.
- `T-033`: template do elenco incompleto em projetos novos.
- `T-034`: consumidores não resolvem corretamente o time por host.
- `T-038`: composição não destrutiva da statusline no Claude.
- `T-039`: detecção de memória preexistente em outro formato.

`T-040` coordena a experiência Codex e os critérios de aceitação; não absorve nem reimplementa os cards acima.

## Decisão aprovada em 2026-08-09

- Linguagem natural + `/skills` formam o contrato principal no Codex.
- `/prompts:orq` pode existir somente como compatibilidade opcional, nunca como requisito nem como promessa universal do plugin.
- O desenho deve deixar explícito que `commands/` continua sendo a superfície de slash commands do Claude Code.

## Especificação

- Arquivo: `docs/superpowers/specs/2026-08-09-paridade-operacional-codex-design.md`.
- Desenho aprovado pelo dono em 2026-08-09.
- Autocrítica concluída: nenhum placeholder real, escopo de coordenação explicitado, limitações de statusline e modelos sem entitlement tratadas sem promessa falsa.
- Nenhum arquivo em `orq/` foi alterado nesta fase.

## RETOMAR AQUI

O dono revisa a especificação escrita. Com aprovação explícita, invocar `writing-plans`, escrever o plano executável e manter `orq/` intocado até o próximo gate do ciclo.
