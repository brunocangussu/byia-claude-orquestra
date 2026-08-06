# T-031 — Comando para listar agentes ativos

## Objetivo

Acrescentar uma forma natural e explícita de listar “agentes ativos” sem confundir o elenco
configurado para o próximo spawn com processos/agentes que estão executando agora.

## Contexto confirmado

- `/orq:elenco` já mostra os papéis configurados e os revisores externos ativos em
  `memory/wiki/_elenco.md`.
- A tabela ativa do elenco vale para o próximo spawn; agente em execução pode ainda usar o valor
  anterior.
- **Decisão do dono em 2026-08-05:** mostrar ambos em blocos separados — execução viva e elenco
  configurado.

## Decisões

1. **Conteúdo:** dois blocos separados: “rodando agora” e “configurado para o próximo spawn”.

## Fora de escopo até o gate

- Nenhum arquivo em `orq/` será alterado antes da aprovação do desenho e do plano.
- Não será criada telemetria persistente nem mecanismo novo de rastreamento sem necessidade
  demonstrada.

## ⏭️ RETOMAR AQUI

Verificar quais hosts expõem uma fonte viva de agentes em execução e decidir se o bloco mostra só
os que ainda rodam ou também o histórico recente. Depois, comparar as opções de estender
`/orq:elenco`, criar `/orq:agentes`, ou criar uma visão combinada por alias, e levar o desenho ao
gate antes de implementar.
