# Schema da memória — o contrato

> Regras de formato que **outras coisas leem por parser**. Mudar aqui sem mudar o consumidor quebra
> em silêncio. O `/orq:checkpoint` e o `/orq:wiki-lint` procuram este arquivo.

## Formato do board (contrato — não improvise)

Card, exatamente assim:

    - [ ] `T-001` Título curto — nota livre depois do travessão

- o **marcador é o 4º caractere**: `[ ]` backlog · `[>]` planejando · `[!]` esperando o dono ·
  `[~]` implementando · `[?]` validar · `[x]` feito;
- o **ID vem entre crases**, imediatamente depois do marcador;
- o **título vai até o travessão** `—`; o que vem depois é nota livre;
- **nada de negrito ou crase envolvendo o marcador ou o ID** — o parser lê por posição;
- uma seção cujo título case com `## …Arquivad…` **encerra a contagem** de progresso: tudo abaixo
  dela é ignorado.

⚠️ **Isto não é estilo, é contrato.** `orq/scripts/kanban-status.sh` casa `/^- \[.\]/` e extrai o
título entre a crase do ID e o travessão. Um card escrito como
`` - `[!]` **T-001 · Título** `` não casa, e a statusline fica **muda sem erro nenhum** — o board
parece perfeito e o progresso nunca aparece. Foi assim que quebrou na primeira instalação em
projeto de terceiro (2026-07-27).

**Como verificar:** `sh orq/scripts/kanban-status.sh .` — saída vazia com cards no board = formato
errado.

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

## Nomes de agente

Os cinco papéis do núcleo (`orq-planner`, `orq-implementer`, `orq-reviewer`, `orq-docs`, `orq-scout`)
vêm **do plugin**. Agente local em `.claude/agents/` nunca deve usar o prefixo `orq-` — colisão de
nome entre plugin e projeto tem resolução indefinida. Papel adicional usa nome próprio (`dados`,
`infra`, `frontend`).
