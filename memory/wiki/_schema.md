# Schema da memória — o contrato

> Regras de formato que **outras coisas leem por parser**. Mudar aqui sem mudar o consumidor quebra
> em silêncio. O `/orq:checkpoint` e o `/orq:wiki-lint` procuram este arquivo.

## Formato do board (contrato — não improvise)

Card, exatamente assim:

    - [ ] `T-001` Título curto — nota livre depois do travessão

- o **marcador é o 4º caractere** e só pode ser um destes seis:
  `[ ]` BACKLOG · `[>]` PLANNING · `[!]` AWAITING_OWNER · `[~]` READY/DEV_REVIEW (aprovado, em
  implementação) · `[?]` VALIDATE · `[x]` DONE — os mesmos estados da máquina descrita na skill;
- o **ID vem entre crases**, imediatamente depois do marcador — **é ele que distingue card de item
  de checklist**;
- o **título vai até o primeiro travessão** `—`; o que vem depois é nota livre;
- **nada de negrito ou crase envolvendo o marcador ou o ID** — o parser lê por posição;
- **sem indentação**: card começa na coluna 0. Linha indentada é sub-item e não conta;
- uma seção cujo título case com `## …arquiv…` (Arquivado, Arquivadas, Arquivo) **encerra a
  contagem**: tudo abaixo dela é ignorado.

⚠️ **Isto não é estilo, é contrato.** `orq/scripts/kanban-status.sh` casa
`` /^- \[[ >!~?x]\] `[^`]+`/ `` — estrito de propósito.

### O teto da linha — 240 bytes

**A linha inteira do card cabe em 240 bytes UTF-8.** O que não couber vai para a thread do card, e o
card guarda um ponteiro para ela.

**A unidade é byte UTF-8, não "caractere"** — e isto não é preciosismo. Neste board, contando *code
points*, 17 cards passavam de 200; contando *bytes*, 21. Quatro cards ficavam de lados opostos da
mesma régua. `wc -c` conta bytes, `wc -m` conta caracteres, `awk` depende do locale e `len()` do
Python conta code points: sem a unidade fixada, o mesmo board passa numa máquina e falha noutra.
Byte UTF-8 é a única régua que não depende de locale nem de implementação — e é a mais próxima do
custo real em tokens, que é o motivo do teto existir.

**Orçamento por componente**, porque esticar só o total apenas adia o aperto:

| Componente | Teto | Observação |
|---|---|---|
| marcador + ID | ~14 B | fixo pelo contrato |
| título | **80 B** | até o primeiro travessão |
| ponteiro de thread | **50 B** | `→ threads/T-NNN-nome.md` |
| nota (estado, `trilha:`, `faixa:`, como validar, `@frente`) | o que sobrar | ~96 B |

**Por que 240 e não 200.** A migração de 2026-09-02 mediu: com teto de 200, **três dos nove
primeiros cards estouraram** e tiveram o "como validar" reescrito até caber — perda que não aparece
em contagem nenhuma. A causa é sempre título longo somado a ponteiro longo. 240 dá a folga sem
devolver a nota-ensaio.

⚠️ **A nota continua sendo lida por parser semântico.** `trilha: … · faixa: …` é procurado dentro
dela por `/orq:plan-next`, `/orq:implement-next` e `/orq:elenco`. O teto **não** pode espremer isso
para fora: é metadado obrigatório, não prosa.

### Onde a nota vai morar, e como achá-la depois

| Situação do card | Destino da nota |
|---|---|
| tem frente/thread própria | a thread dele, `threads/T-NNN-nome.md` |
| não tem | `threads/_notas-de-cards.md`, seção própria |

**O endereço é sempre o ID, nunca a posição.** A seção se chama exatamente
`` ## Nota herdada do card `T-NNN` `` — procure por essa linha. Assim o endereço sobrevive a
reordenação, a renomeação de título e a notas novas inseridas no meio, que é o que faria um ponteiro
por posição apodrecer em semanas. O `_notas-de-cards.md` mantém um índice de IDs no topo.

**Por que um arquivo coletivo e não uma thread por card:** trinta threads de um parágrafo trocariam
um inchaço por outro, e o `wiki-lint` acusaria trinta páginas órfãs — com razão. O coletivo **não é
thread**: não tem `RETOMAR AQUI` e não representa frente de trabalho. Card que voltar a ser
trabalhado ganha thread de verdade, e a nota migra para lá.

### O que NUNCA migra para a thread

O board tem **consumidores automáticos** que só leem ele. O que eles procuram na linha do card é
metadado, não nota — e migrar isso quebra o consumidor em silêncio.

| Fica no card, sempre | Quem lê |
|---|---|
| `trilha: … · faixa: …` | `/orq:plan-next`, `/orq:implement-next`, `/orq:elenco` |
| **release alvo** (`0.23.0`) em card que tem uma | `ContextGuardReleaseVersionTest` |
| `@frente` | o protocolo de várias janelas |
| o ponteiro `→ threads/…` | quem precisa achar o resto |

⚠️ **Isto não é teoria — aconteceu na migração de 2026-09-02.** A nota do `T-042` citava a release
alvo `0.23.0`; ela foi para a thread junto com o resto, e a suíte caiu na hora
(`test_release_version_is_coordinated`). O teste é um consumidor que lê **só** o board, e a
informação sumiu do lugar onde ele olha. **Antes de migrar a nota de um card, pergunte quem mais lê
aquela linha** — a resposta não é sempre "uma pessoa".

⚠️ **O que a thread precisa carregar depois da migração.** Mover a nota para a thread cria um risco
específico: a recuperação pós-compactação injeta o card curto e o `RETOMAR AQUI`, não a nota velha.
Se a nota continha uma **restrição** ("não fazer deploy") ou os **critérios de aceite**, eles somem
da recuperação. Por isso a thread guarda esses dois como **campos**, não como prosa solta — e é a
thread, não o board, que responde "o que não pode ser feito neste card".

**Só card usa `- [` na coluna 0.** Se você escrever uma seção de processo com itens soltos
(`- [x] revisor aprovou`), eles **não** entram na contagem por não terem ID entre crases — mas
aparecem como `⚠N` na statusline, para o desvio não passar despercebido.

**Como verificar:** `sh <raiz-do-plugin>/scripts/kanban-status.sh .` — e confira **os três sinais**:

| Sinal | Significa |
|---|---|
| saída vazia com cards no board | formato errado, nenhum card reconhecido |
| `⚠N` no fim | N linhas parecem card e não casam o contrato |
| denominador ≠ nº de cards que você escreveu | alguma linha entrou ou ficou de fora |

O terceiro é o que pega o erro sutil: **saída não-vazia não prova que está certo.**

## Regras da wiki

| Arquivo | Natureza | Responde |
|---|---|---|
| `fixes-history.md` | **append-only**, nunca reescrito | "o que aconteceu naquele dia" |
| `wiki/<tópico>.md` | **reescrita** para refletir o presente | "como funciona hoje" |
| `wiki/threads/<nome>.md` | vivo, com "RETOMAR AQUI" no fim | "onde eu estava" |
| `wiki/KANBAN.md` | o board | "o que falta" |
| `gotchas.md` | append, só o que já causou erro | "onde eu já me queimei" |

**A distinção que faz funcionar:** sem a página de tópico, responder *"como isso funciona hoje"* exige
reconstruir a verdade lendo N entradas do log.

**Não guarde o derivável** — diff, `git log`, lista de arquivos, schema do banco, o código atual. A
fonte já tem. Guarde o **porquê** e as **consequências**.

## Trabalho em VÁRIAS JANELAS ao mesmo tempo

O modelo do Orquestra pressupõe **um Manager**. Com N janelas abertas no mesmo projeto há N
Managers, e sem disciplina eles se sobrescrevem **em silêncio** — a janela B grava por cima do
movimento de card da A, e ninguém percebe.

**A regra base: uma janela = uma FRENTE.** Nunca duas janelas na mesma frente.

| Arquivo | Quem escreve | Regra |
|---|---|---|
| `wiki/threads/<frente>.md` | só a janela dona | livre — ninguém mais toca |
| `wiki/KANBAN.md` | todas | **o único ponto de disputa real** — ver as 3 regras |
| `fixes-history.md` | todas | append **no fim**, relendo antes; entrada carimbada com a frente |
| `wiki/<tópico>.md` | quem fechou o card | reler antes de reescrever |
| `wiki/_elenco.md` | todas | **estado compartilhado** — o perfil ativo vale para **todas** as janelas no próximo spawn. Releia **imediatamente antes** de gravar. Ajuste de um papel: edite **só aquela linha**. **Exceção — trocar de perfil** (`/orq:elenco perfil <nome>`): aí a tabela ativa **é** reescrita inteira a partir do preset, preservando a linha do `manager` — o que continua proibido é reescrever a partir da **cópia velha do seu contexto** em vez de reler o disco |

⚠️ **O `_elenco.md` é o mais fácil de perder sem perceber**, porque ninguém "trabalha" nele — só passa
e troca uma linha. Cenário real: a janela A ativa o perfil `economia`; a janela B, com uma cópia velha
no contexto, ajusta um papel e regrava a tabela inteira — a troca de A desaparece **em silêncio**, e a
B segue spawnando com o time errado achando que está tudo certo.

### As três regras que evitam a colisão

1. **Releia antes de escrever.** Sempre. O arquivo em disco pode ter mudado desde que você o leu —
   outra janela trabalhou nesse meio-tempo. Não confie na cópia que está no seu contexto.
2. **Edite a linha, nunca o arquivo.** Altere **apenas as linhas dos seus cards**. Reescrever o
   `KANBAN.md` inteiro a partir de uma cópia velha é o que apaga o trabalho das outras janelas —
   é a causa da perda, não a concorrência em si.
3. **Card em curso leva a marca da frente**, no fim da nota: `@auth`, `@billing`. Uma janela **não
   pega** card marcado com frente alheia. Card sem marca é livre.

```
- [~] `T-042` Rotacionar o token — bloqueado no rate limit @auth
```

A marca vai depois do travessão, então não interfere no parser (o título termina no primeiro `—`).

**Encontrou conflito mesmo assim?** (o card mudou de estado entre a sua leitura e a sua escrita)
**Não sobrescreva.** Releia, entenda o que a outra janela fez, e decida — se não der para conciliar,
registre no card e leve ao dono. Perda silenciosa é sempre pior que a pergunta.

### A pendência NÃO precisa de janela aberta

Deixar uma janela viva só para "não esquecer que isso está pendente" é usar contexto como memória —
exatamente o que o board existe para substituir. Se algo depende de decisão do dono:

1. mova o card para `[!]` **com a pergunta exata escrita nele**, e a sua recomendação;
2. grave o estado na thread da frente, terminando com **"RETOMAR AQUI"**;
3. **pode fechar a janela.**

Qualquer janela — inclusive uma aberta amanhã — retoma pelo card e pela thread. Se você precisa
manter a janela aberta para não perder o fio, **o handoff foi mal escrito**: é aí que está o defeito,
não na sua memória.

## Nomes de agente

Os cinco papéis do núcleo (`orq-planner`, `orq-implementer`, `orq-reviewer`, `orq-docs`, `orq-scout`)
vêm **do plugin**. Agente local — em `.claude/agents/` do projeto **ou** em `~/.claude/agents/`
(escopo usuário) — nunca deve usar o prefixo `orq-` — colisão de nome entre plugin e projeto tem
resolução indefinida. Papel adicional usa nome próprio (`dados`, `infra`, `frontend`).
