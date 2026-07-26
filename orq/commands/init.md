---
description: Instala o Orquestra neste projeto — inspeciona o código, detecta as ferramentas disponíveis, propõe o time de agentes sob medida e monta a memória. Funciona em projeto novo ou já em andamento.
argument-hint: "[--reinstalar para refazer a análise]"
---

Você vai instalar o **Orquestra** neste projeto. Leia a skill `orquestra` primeiro (a disciplina).

**Regra de ouro: este comando se ADAPTA ao projeto.** Não despeje uma estrutura genérica — investigue,
decida o que faz sentido *aqui*, e só então proponha. Um script Python de 200 linhas não precisa do
mesmo time que um monorepo com backend, CRM e workflows.

---

## FASE 1 — Investigar (paralelo, read-only)

Dispare agentes `orq-scout` **em paralelo** (um por frente) e, enquanto isso, olhe você mesmo a raiz.
Não leia arquivos inteiros: use busca semântica e amostragem.

Levante:

1. **Stack e forma** — linguagens, frameworks, gerenciadores de pacote, monorepo vs único, onde
   ficam código/testes/migrations/infra. Tamanho (arquivos, LOC aproximado).
2. **Domínio** — do que o projeto TRATA (README, docs, nomes de módulos, modelos). Isso define os
   papéis: um projeto com banco e multi-tenant pede agente de dados; um site estático não.
3. **Como se trabalha aqui** — `CLAUDE.md`/`AGENTS.md` existentes, convenções, comando de build e
   de teste, o que **quebra o deploy** (regras de CI), estilo de commit no `git log` recente.
4. **Memória e docs que já existem** — `memory/`, `docs/`, `NOTES.md`, `TODO.md`, `ROADMAP.md`,
   snapshots, planos. **Tudo isso é matéria-prima** — a wiki nasce com a verdade que já existe.
5. **Trabalho em aberto** — TODO/FIXME no código, issues, itens não concluídos nos docs, testes
   quebrados. Vira o backlog inicial (com IDs `T-NNN`).
6. **Ferramental disponível** (checar de verdade, não presumir):
   - MCPs conectados (banco, deploy, observabilidade, design…)
   - Plugins ativos: claude-mem, context-mode, codex, superpowers…
   - Busca semântica: Serena e/ou codebase-memory — **e se o repo já está indexado**
   - Memória de longo prazo (Supermemory) configurada?
   - Subagentes que o projeto **já** tem em `.claude/agents/`

## FASE 2 — Decidir (o julgamento)

**Time.** Comece pelo núcleo — Planner · Implementer · Reviewer · Docs — e só adicione papel com
justificativa concreta *deste* projeto (ex.: "tem 90 migrations e RLS → vale um agente de dados";
"tem UI e mockups → vale um de frontend"). **Menos agentes bem definidos > muitos genéricos.**
Se o projeto já tem agentes bons, **reaproveite**: mapeie-os aos papéis em vez de duplicar.

Para cada papel decida:
- `model` — trabalho difícil (plano, review) pede modelo forte; tarefa mecânica, um menor.
- `tools` — **mínimo necessário**. Reviewer é **read-only** (sem Edit/Write). Só quem implementa escreve.
- quando é chamado e o que entrega.

**Estratégia de leitura** (o que economiza contexto neste projeto):
- Repo grande → busca semântica primeiro; indexar se ainda não estiver.
- Saída volumosa (testes, logs, git) → context-mode.
- Se faltar ferramenta útil, **registre como sugestão** — não instale nada sozinho.

**Páginas de wiki iniciais:** 1 a 3 dos subsistemas mais quentes. Não faça backfill especulativo —
a wiki cresce com o uso.

## FASE 3 — Propor e ESPERAR

Apresente ao dono, curto e escaneável:
- o que você entendeu do projeto (2–3 linhas — ele corrige se você errou);
- o **time proposto** (papel · modelo · por que existe aqui);
- o que será criado/alterado (com destaque para o que **altera arquivo existente**);
- backlog inicial que você encontrou;
- sugestões de ferramenta que ele pode querer ligar.

**PARE e espere aprovação.** Se ele ajustar o time, incorpore. Nada é escrito antes do "pode ir".

## FASE 4 — Instalar

1. **Memória** (só o que faltar — nunca sobrescrever o que existe):
   `memory/MEMORY.md` (índice) · `memory/fixes-history.md` (log) · `memory/gotchas.md` ·
   `memory/wiki/KANBAN.md` (board, com o backlog real que você achou) · `memory/wiki/threads/` ·
   as páginas de tópico aprovadas.
   Se já houver memória, **integre**: aproveite o conteúdo, não recomece.
2. **Agentes** em `.claude/agents/` — só os aprovados, com `model`/`tools` decididos. Não duplique
   os que já existem; complemente.
3. **`CLAUDE.md`** — adicione (ou atualize) um bloco `<!-- orquestra:start -->…<!-- orquestra:end -->`
   com: o ciclo, onde vive a memória, quem move o board, e as convenções do projeto que você
   descobriu (build, teste, o que quebra o deploy). **Preserve todo o resto do arquivo.**
4. **`AGENTS.md`** — se existir, ponteiro equivalente de poucas linhas (o Codex lê esse). Se não
   existir, só crie se o projeto usar Codex.
5. **Statusline** (opcional, perguntar): garantir `~/.claude/scripts/kanban-status.sh` e apontar o
   `statusLine` do settings pra ele. Se já houver statusline customizada, **não sobrescreva** —
   mostre a linha a acrescentar.

## FASE 5 — Confirmar

Mostre: o que foi criado vs alterado · o board inicial (`/orquestra:quadro`) · e o ciclo em 3 linhas:

> `/orquestra:plan-next` planeja o próximo card → você aprova → `/orquestra:implement-next`
> implementa com review → `/checkpoint` grava → `/clear` limpa a janela.

Registre a instalação no log (`fixes-history.md`).

---

## Regras

- **Idempotente.** Rodar de novo não destrói nada: detecta o que existe, completa o que falta,
  relata o que ignorou. Com `--reinstalar`, refaz a análise e propõe atualizações (ainda pedindo ok).
- **Nunca** `git commit`/`push`. Nunca instalar dependência. Nunca tocar em código de produção.
- **Nunca** inventar estado: se não sabe se algo funciona, põe em VALIDATE, não em DONE.
- Projeto pequeno merece estrutura pequena — `MEMORY.md` + `fixes-history.md` + board já bastam.
