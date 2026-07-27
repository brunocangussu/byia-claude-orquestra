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
vêm **do plugin**. Agente local em `.claude/agents/` nunca deve usar o prefixo `orq-` — colisão de
nome entre plugin e projeto tem resolução indefinida. Papel adicional usa nome próprio (`dados`,
`infra`, `frontend`).
