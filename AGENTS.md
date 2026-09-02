# CLAUDE.md — Orquestra (`orq`)

Este repositório **é** o plugin Orquestra. Ele também **usa** o Orquestra para se desenvolver.

<!-- orquestra:start -->

## O ciclo

```
planejar → [VOCÊ APROVA] → implementar → review → docs → [VOCÊ VALIDA] → feito
   ↑                                                          │
   └── checkpoint + compactação nativa (Codex) / /clear (Claude) ←──┘
```

O dono **não digita comandos** — ele conversa, e você reconhece a intenção. A tabela de gatilhos está
na skill `orq`. *"onde paramos"* → mostra o board · *"pode implementar"* → Loop B · *"terminamos"* →
checkpoint · *"anota isso"* → card novo.

⚠️ **Todo pedido de mudança entra pelo ciclo — não comece editando arquivo.** *"quero X"*, *"vamos
acrescentar Y"*, *"tem um problema em Z"* significam: crie o card, planeje, **pare no gate**. Só vai
direto o que for trivial (typo, ajuste de texto sem efeito). Escala completa na skill `orq`, seção
"Roteamento automático". **Anuncie o roteamento em uma linha** — não pergunte se pode.

Este erro já aconteceu aqui: a feature do Kimi (0.8.0) foi implementada direto, sem plano e sem
gate, porque o pedido chegou em linguagem natural e pareceu pequeno.

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

**Não há build.** A verificação automatizada tem três comandos, **os três obrigatórios**:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'   # suíte
claude plugin validate ./orq --strict          # manifesto
python3 orq/scripts/lint-coerencia.py .        # coerência entre as instruções
```

⚠️ **A suíte é descoberta, nunca enumerada.** A versão anterior desta linha listava três dos cinco
módulos: quem a seguia rodava 119 dos 201 testes achando que rodara tudo. `discover` acha todo
`orq/scripts/test_*.py`, então **acrescentar um módulo não exige lembrar de editar isto aqui** —
que é o modo de falha real, não a digitação.

...seguidos de **teste comportamental** — que só vale depois do release completo. `<clean-source>`
é checkout detached do SHA remoto aprovado, com `git status --porcelain` vazio; nunca cache de host
nem working tree em uso. Depois do update e restart, rode o comando do host validado:

```bash
python3 <clean-source>/orq/scripts/verify_installed_cache.py --host claude --source <clean-source>/orq --installed ~/.claude/plugins/cache/orquestra/orq/<versão>/
python3 <clean-source>/orq/scripts/verify_installed_cache.py --host codex  --source <clean-source>/orq --installed ~/.codex/plugins/cache/orquestra/orq/<versão>/
```

Cada comando executado deve sair `0`. Só então conversar em português natural para ver se a intenção
é reconhecida sem comando digitado.
Para iterar numa **skill**, `/reload-plugins` comprovadamente aplica o update na sessão viva
(2026-07-29) — serve para experimentar, **não** para fechar card: comando e agente seguem sem teste.

⚠️ **`validate` sozinho não prova correção.** Ele checa o manifesto e passa com instruções que mandam
rodar comando inexistente — foi assim que `/orquestra:*` sobreviveu a três releases depois da
renomeação para `orq`. O lint cobre esse buraco: comando, agente, skill e `${CLAUDE_PLUGIN_ROOT}/…`
citados têm que existir. Ele **ignora `memory/` por padrão** — o log é append-only e cita nomes
extintos ao descrever bugs passados. **Duas exceções nominais são varridas**, por serem instrução
viva e não registro: `memory/wiki/distribuicao.md` e `memory/wiki/arquitetura.md`. Falha nelas não é
falso positivo; `fixes-history.md`, `gotchas.md` e `threads/` continuam fora.

O verificador de cache deve vir da fonte limpa. Não crie exclusões ad hoc: as únicas normalizações
são as allowlists instaladas-only e host-aware codificadas em `verify_installed_cache.py`.

- **Commit:** `feat(0.X.0): descrição em minúscula, sem acento no assunto` — travessão pro subtítulo.
- **Versão:** mexeu em `orq/` → o mesmo commit bumpa `orq/.claude-plugin/plugin.json`, a seção
  Status do README, o `memory/MEMORY.md` **e** o `.claude-plugin/marketplace.json` (são quatro, e
  só quatro). O `ContextGuardReleaseVersionTest` **deriva** a versão do manifesto e confere os
  outros três contra ela — é guarda, não uma quinta fonte de verdade. O cache é indexado por
  versão: **editar sem bump não muda o que roda** e nada acusa — lint e suíte têm guardas pra isso.
- **Nunca** `git push`, publicar ou bumpar versão sem o ok do dono.

## O produto aqui são instruções, não código

Isso muda o que o review procura. Não há null pointer nem race condition — há **ambiguidade**,
**contradição entre arquivos** e **referência a algo que não existe**. Ao briefar o revisor deste
repo, inclua:

> Leia como um modelo hostil leria. Onde esta instrução admite duas interpretações? Ela contradiz
> alguma regra em outro arquivo do plugin? Cita comando, skill ou agente que não existe?

## Se você é o revisor entrando pelo `/orq:revisar`

Você é o **único** revisor, e é sempre de vendor oposto ao host — não há revisor interno ao seu
lado. Duas coisas:

- **Read-only.** Aponte, não corrija. Quem implementou aplica.
- **O produto são instruções, não código** — vale a mesma pergunta da seção acima ("O produto aqui
  são instruções, não código"). Um achado sem cenário de falha concreto é opinião de estilo e será
  descartado na auditoria do Manager.

## Idioma

Português-BR em tudo — commits, board, wiki, comentários e conversa. Acentuação correta obrigatória
na prosa; o assunto do commit segue sem acento por convenção do `git log` existente.
