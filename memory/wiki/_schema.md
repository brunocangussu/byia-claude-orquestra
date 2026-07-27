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

## Nomes de agente

Os cinco papéis do núcleo (`orq-planner`, `orq-implementer`, `orq-reviewer`, `orq-docs`, `orq-scout`)
vêm **do plugin**. Agente local em `.claude/agents/` nunca deve usar o prefixo `orq-` — colisão de
nome entre plugin e projeto tem resolução indefinida. Papel adicional usa nome próprio (`dados`,
`infra`, `frontend`).
