---
description: Health-check da wiki de memória — contradições, páginas órfãs, afirmações vencidas, pendências já resolvidas
argument-hint: "[tópico específico — opcional]"
---

Faça um **LINT da wiki de memória** deste projeto (regras em `memory/wiki/_schema.md`, se existir).
Objetivo: manter a memória confiável conforme ela cresce. Se `$ARGUMENTS` indicar um tópico,
limite o lint a ele; senão, varra a wiki inteira.

Leia `memory/MEMORY.md` (índice), as páginas de `memory/wiki/`, as threads e o topo do
`memory/fixes-history.md`. Depois procure:

1. **Contradições** — duas páginas afirmando coisas incompatíveis sobre o mesmo assunto.
2. **Afirmações vencidas** — página diz X, mas trabalho posterior (log/git/código) mudou pra Y.
   Confirme na fonte antes de acusar (use Serena/codebase-memory ou git; não presuma).
3. **Páginas órfãs** — arquivo em `memory/` que não aparece no índice, ou não é linkado por ninguém.
4. **Buracos** — assunto que aparece repetido em várias páginas/log mas não tem página própria.
5. **Threads mortas** — thread marcada 🟢 ativa mas sem movimento, ou já concluída e não arquivada.
6. **Pendências resolvidas** — item na lista de "Pendentes" do índice que o trabalho já resolveu.
7. **Inchaço** — página passando de ~150 linhas (quebrar por subtema) ou com conteúdo derivável
   (diff, lista de arquivos, schema do banco) que deveria sair.

**Entregue um relatório curto e priorizado**: o achado, o arquivo, e a correção sugerida.
**Não corrija nada ainda** — apresente e pergunte o que aplicar. Exceção: erros triviais e
inequívocos (link quebrado, página faltando no índice) pode corrigir direto e listar no fim.

Se a wiki estiver saudável, diga isso em uma linha — não invente achado pra parecer útil.
