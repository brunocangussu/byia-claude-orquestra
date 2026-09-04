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
8. **Card acima do teto** — linha do board passando de **240 bytes UTF-8** (`_schema.md`, "O teto da
   linha"). Meça em bytes, não em caracteres: as duas réguas discordam em board com acento e emoji.
   A correção é mover a nota para `threads/T-NNN.md` e deixar no card título, estado, como validar e
   o ponteiro — **movendo o texto íntegro, nunca resumindo**. Card acima do teto é custo cobrado em
   toda retomada e em toda compactação, porque o board é relido inteiro.
9. **Ponteiro quebrado** — card citando `threads/…` que não existe, ou thread que nenhum card cita.
   Depois que a nota passa a morar na thread, board e thread viram um par: um cherry-pick que leve
   só a linha do card deixa o ponteiro apontando para o vazio.

**Entregue um relatório curto e priorizado**: o achado, o arquivo, e a correção sugerida.
**Não corrija nada ainda** — apresente e pergunte o que aplicar. Exceção — **só quando o dono pediu
este comando**, mesmo em frase natural ("dá uma olhada na saúde da wiki", não precisa ser
`/orq:wiki-lint` digitado): erros triviais e inequívocos (link quebrado, página faltando no
índice) pode corrigir direto e listar no fim. Rodando por iniciativa própria do Manager (seção
abaixo), essa exceção **não vale** — nem o trivial se corrige sem ok.

Se a wiki estiver saudável, diga isso em uma linha — não invente achado pra parecer útil.

## Quando o Manager roda isto por iniciativa própria

Este comando também roda **sem o dono pedir** — quando, como relatar e o teto estão só na skill
`orq`, seção "Decisões que o Manager toma sozinho" → nível N1; este arquivo não repete os números
para não divergir dela.
