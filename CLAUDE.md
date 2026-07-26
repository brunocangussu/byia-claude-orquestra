# CLAUDE.md — Orquestra (`orq`)

Este repositório **é** o plugin Orquestra. Ele também **usa** o Orquestra para se desenvolver.

<!-- orquestra:start -->

## O ciclo

```
planejar → [VOCÊ APROVA] → implementar → review → docs → [VOCÊ VALIDA] → feito
   ↑                                                          │
   └──────────────  checkpoint + /clear  ←────────────────────┘
```

O dono **não digita comandos** — ele conversa, e você reconhece a intenção. A tabela de gatilhos está
na skill `orq`. *"onde paramos"* → mostra o board · *"pode implementar"* → Loop B · *"terminamos"* →
checkpoint · *"anota isso"* → card novo.

## Onde vive o estado

| Arquivo | Papel |
|---|---|
| `memory/MEMORY.md` | **índice — leia primeiro ao retomar** |
| `memory/wiki/KANBAN.md` | o board (fonte da verdade do trabalho) |
| `memory/wiki/arquitetura.md` | como o plugin funciona hoje e o que foi recusado |
| `memory/wiki/distribuicao.md` | empacotar, validar, publicar |
| `memory/wiki/_elenco.md` | qual LLM toca cada papel — **ler antes de spawnar** |
| `memory/fixes-history.md` | log append-only |
| `memory/gotchas.md` | armadilhas já pagas |

**Só o Manager (a sessão principal) move cards.** Worker que quiser mover, pede.
`PLANNING → READY` exige aprovação explícita do dono. **Commit não é critério de pronto** — o card
fecha em VALIDATE e o dono confirma usando o produto.

<!-- orquestra:end -->

## Convenções deste projeto

**Não há build nem teste automatizado.** A verificação é:

```bash
claude plugin validate ./orq --strict     # tem que passar
```

...seguida de **teste comportamental**: `/plugin marketplace update orquestra` + `/reload-plugins`,
e então conversar em português natural para ver se a intenção é reconhecida sem comando digitado.

⚠️ **`validate` não prova correção.** Ele checa o manifesto, não a coerência das instruções entre si.
Foi assim que `/orquestra:*` sobreviveu a três releases depois da renomeação para `orq`.
**Ao renomear qualquer comando, skill ou agente, faça `grep` do nome antigo no `orq/` inteiro.**

- **Commit:** `feat(0.X.0): descrição em minúscula, sem acento no assunto` — travessão pro subtítulo.
- **Versão:** `orq/.claude-plugin/plugin.json` **e** a seção Status do README andam juntos.
- **Nunca** `git push`, publicar ou bumpar versão sem o ok do dono.

## O produto aqui são instruções, não código

Isso muda o que o review procura. Não há null pointer nem race condition — há **ambiguidade**,
**contradição entre arquivos** e **referência a algo que não existe**. Ao spawnar o `orq-reviewer`
neste repo, inclua no briefing:

> Leia como um modelo hostil leria. Onde esta instrução admite duas interpretações? Ela contradiz
> alguma regra em outro arquivo do plugin? Cita comando, skill ou agente que não existe?

## Idioma

Português-BR em tudo — commits, board, wiki, comentários e conversa. Acentuação correta obrigatória
na prosa; o assunto do commit segue sem acento por convenção do `git log` existente.
