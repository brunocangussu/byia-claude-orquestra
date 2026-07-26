---
description: Fecha o bloco de trabalho — atualiza a wiki de memória (log + páginas + thread) pra você poder /clear sem perder a linha de raciocínio
argument-hint: "[rótulo do marco — opcional; se presente, cria snapshot]"
---

Você é um **mantenedor disciplinado de wiki**, não um chatbot. Faça um **CHECKPOINT durável**:
registre o conhecimento FORA da janela, pra ela poder ser reiniciada sem perder nada.
Contexto = RAM (descartável); memória em disco = HD (durável).

## 1. Descobrir a estrutura
Procure nesta ordem: `memory/wiki/_schema.md` (regras da wiki) · `memory/MEMORY.md` (índice) ·
`memory/fixes-history.md` (log) · `memory/wiki/threads/` (trabalho em curso) · `docs/plano_*.md`.
**Se o projeto NÃO tem wiki**, crie o mínimo: `memory/MEMORY.md` (índice) + `memory/fixes-history.md`
(log) e siga — não precisa da estrutura completa num projeto pequeno.

## 2. Resumir ESTA sessão
O que foi decidido/implementado/corrigido/testado e qual o **PRÓXIMO passo**. Condensado, "o quê +
por quê" não-derivável. **Não** cole diffs nem listas de arquivos (o git já tem).

## 3. Ingerir na wiki (a parte que importa — não pule)
- **LOG** (`fixes-history.md`): append no TOPO, formato greppável
  `## [AAAA-MM-DD] <tipo> | <título>` (tipos: `feat` `fix` `plan` `investig` `decisão` `incidente` `processo`).
- **PÁGINAS DE TÓPICO** (`memory/wiki/*.md`): **atualize as afetadas** — reescreva pra refletir o
  estado ATUAL; se o trabalho contradiz o que a página afirmava, **corrija a página**. Se o assunto
  ainda não tem página e é recorrente, **crie**.
- **THREAD ativa** (`memory/wiki/threads/*.md`): status das fases (✅/🔄/⬜), decisões novas (com o
  porquê, pra não re-litigar), perguntas abertas e — obrigatório — **⏭️ RETOMAR AQUI** com a próxima
  ação concreta. Thread concluída → sintetize nas páginas de tópico e mova pra `threads/_concluidas/`.
- **GOTCHA** novo → `gotchas.md`.
- **ÍNDICE** (`MEMORY.md`): registre página/thread nova; atualize a linha de resumo do que mudou.
- **SNAPSHOT**: se `$ARGUMENTS` estiver presente (marco), crie
  `memory/snapshot-<AAAA-MM-DD>-<rótulo>.md` com o estado exato pra retomar.

## 4. Supermemory
Se a MCP `api-supermemory-ai` existir, `addMemory` com o resumo (tema + feito + próximo passo +
gotchas). Se falhar ou não existir, siga sem erro e avise que pulou.

## 5. Confirmar (3–6 linhas)
O que foi gravado e ONDE + a **frase de retomada** ("na próxima janela: leia `memory/MEMORY.md` →
thread X"). Termine avisando que **agora é seguro dar `/clear`**.

## Regras
- **NÃO** faça `git commit`/`push` sem o usuário pedir.
- **NÃO** invente: registre só o que aconteceu de fato nesta sessão.
- Sessão trivial (nada relevante)? Diga isso em vez de forçar entrada.
- Densidade > extensão. Página de tópico deve caber numa leitura (~150 linhas).
