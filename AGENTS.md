# AGENTS.md

Este repositório é o plugin **Orquestra** (`orq`) para Claude Code — desenvolvimento orientado a
board com agentes efêmeros, memória-wiki e gates humanos.

**Leia `CLAUDE.md` primeiro**: é lá que estão o ciclo, as convenções e onde vive o estado.
O contexto completo está em `memory/MEMORY.md` (índice) e `memory/wiki/KANBAN.md` (o board).

## Se você é o Codex sendo chamado como revisor

Você entra pelo `/orq:revisar`, como parte de um painel ao lado do revisor Claude. Duas coisas:

- **Read-only.** Aponte, não corrija. Quem implementou aplica.
- **O produto são instruções, não código.** Procure ambiguidade, contradição entre arquivos e
  referência a comando/skill/agente inexistente — não bug de runtime. Um achado sem cenário de
  falha concreto é opinião de estilo e será descartado na reconciliação.

## Verificação

```bash
claude plugin validate ./orq --strict
```

Passa com instruções contraditórias — não confunda verde com correto.

**Nunca** commitar, publicar ou bumpar versão sem o ok do dono.
