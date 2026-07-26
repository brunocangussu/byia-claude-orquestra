---
description: Mostra e ajusta o elenco — qual LLM toca cada papel (planner, implementer, reviewer, docs, scout) e quais revisores externos estão ativos neste projeto
argument-hint: "[papel modelo — ex: 'planner fable' | 'reviewer opus' | 'codex off']"
---

O **elenco** define qual modelo interpreta cada papel **neste projeto**. Fica em
`memory/wiki/_elenco.md` e vale como override no momento do spawn — o `model:` do arquivo do agente
é só o padrão de fábrica.

## Sem argumento — mostrar

Leia `memory/wiki/_elenco.md` e apresente a escalação atual em tabela (papel · modelo · por quê),
mais os revisores externos ativos. Se o arquivo não existir, mostre os **padrões de fábrica** e
ofereça criá-lo.

Feche sugerindo, em uma linha, o que costuma valer a pena ajustar (ex.: *"plano difícil rende mais
com um modelo mais forte no planner"*).

## Com argumento — ajustar

`$ARGUMENTS` no formato `<papel> <valor>`. Exemplos: `planner fable` · `reviewer opus` ·
`implementer inherit` · `codex off` · `codex xhigh`.

1. Valide o papel: `manager` · `planner` · `implementer` · `reviewer` · `docs` · `scout`, ou um
   revisor externo (`codex`, ou outro registrado).
2. Valide o modelo: `opus` · `sonnet` · `haiku` · `fable` · `inherit`, ou um id específico
   (`claude-opus-5`). Valor desconhecido → **pergunte** em vez de gravar errado.
3. Grave em `memory/wiki/_elenco.md` (crie a partir do modelo abaixo se não existir).
4. Confirme o que mudou e **a partir de quando vale** (próximo spawn — não afeta agente em execução).

**`manager` é caso especial:** é a sessão principal, definida pelo `/model` do Claude Code — não dá
pra trocar por aqui. Se ele pedir, explique e sugira o `/model`.

## Modelo do arquivo

```markdown
# Elenco — quem toca cada papel

| Papel | Modelo | Por quê |
|---|---|---|
| manager (sessão principal) | opus | coordena, decide, fala com o dono — definido pelo `/model` |
| planner | opus | achar causa raiz e desenhar solução é o trabalho mais difícil |
| implementer | inherit | segue o modelo da sessão |
| reviewer (interno) | opus | revisão adversarial exige raciocínio forte |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

## Revisores externos
| Revisor | Estado | Config |
|---|---|---|
| codex | ativo | `--model gpt-5.6-sol --effort xhigh` (read-only) |
| kimi-k2 | inativo | registrar aqui quando houver CLI ou MCP |
```

## Como isso é aplicado

Ao spawnar um papel, os comandos (`plan-next`, `implement-next`, `revisar`, `init`) **leem o elenco**
e passam o modelo como override. Sem elenco, valem os padrões de fábrica dos arquivos em `agents/`.

## Orientação (quando ele pedir recomendação)

- **Planner e Reviewer** são onde modelo forte mais se paga: um erro de plano custa a implementação
  inteira; um review fraco deixa passar o que vai quebrar depois.
- **Docs e Scout** são leitura/escrita objetiva — modelo menor resolve e sai mais barato.
- **Implementer** costuma ir bem com `inherit` (acompanha o que você escolheu pra sessão).
- **Só Claude, sem GPT?** `codex off` e deixe o reviewer interno em `opus`. Você perde a diversidade
  de painel (dois modelos erram diferente), mas ganha simplicidade e um fornecedor só.
- Trocar modelo **não** troca a disciplina: as regras dos agentes valem igual.
