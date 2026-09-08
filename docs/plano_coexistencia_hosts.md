# Plano — coexistência Claude + Codex no mesmo repositório (`T-085`, `T-086`, `T-087`)

> Planejado na corrida `noturno-2026-09-07-2130` pelo `planner·sistema` (`gpt-6-astra@xhigh`,
> read-only, thread `01a07ed2-b605-7ad1-b250-5063191edd81`). **Os achados abaixo foram auditados
> pelo Manager contra o código instalado** — o que passou, o que caiu e o que ficou sem prova está
> marcado. Nada foi implementado.

## O que a auditoria confirmou, negou e não pôde provar

### 🔴 CONFIRMADO — e é mais grave que os três cards originais

**O reúso `card+papel` da `0.27.2` está quebrado em silêncio.** `--resume-thread` **não existe** no
cache `codex/1.0.5` do Companion (`grep -c` devolve `0`; no `1.0.6` devolve `6`). E o subagente
`codex:codex-rescue` escolheu o `1.0.5` nas **duas** chamadas observadas nesta sessão, com três
caches instalados (`1.0.2`, `1.0.5`, `1.0.6`).

Consequência: onde `revisar.md`, `plan-next.md`, `SKILL.md` e o `_elenco.md` mandam continuar com
`--resume-thread <threadId>`, o parser do `1.0.5` não reconhece a flag — ela **vira texto do
briefing** e a chamada nasce nova. A feature que a `0.27.2` entregou não está funcionando, e nada
acusa. Isso é card próprio (`T-089`).

### ✅ CONFIRMADO — `--wait` não é opção de `task`

`handleTask` aceita `model, effort, cwd, prompt-file, resume-thread` e os booleanos
`json, write, resume-last, resume, fresh, background`. **`wait` não está lá** — ele pertence ao
`handleReviewCommand`. O Orquestra manda passar `--wait` em três arquivos. Ou vira texto do
briefing, ou é removido pela skill do plugin antes da chamada.

### ❌ NEGADO — o `T-087` partia de premissa errada, e o card era meu

Eu registrei que o subagente "omitiu uma flag pedida" ao não passar `--fresh`. **Ele estava certo.**
`codex-cli-runtime/SKILL.md:34` manda *strip* do token, e `codex-rescue.md:39` define `--fresh` como
controle de roteamento do lado Claude — "não adicione `--resume-last`" —, não como flag a repassar.

O defeito real é outro, e continua existindo: **três contratos divergem sobre as mesmas flags.** O
Orquestra documenta uma linha de comando; a skill do plugin manda transformá-la; o parser do runtime
aceita um terceiro conjunto (e ele aceita `fresh`, que a skill remove). Ninguém verifica o que
chegou de fato. O `T-087` precisa ser reescrito para esse defeito.

### ⚠️ SEM PROVA — arquivamento de thread

O planner cita `thread/archive` e `thread/unarchive` na documentação oficial do App Server. **Não
verifiquei** (é fonte externa) e os `--help` locais de `1.0.5` e `1.0.6` não expõem arquivamento.
Fica como hipótese a testar com canário, nunca como capacidade assumida.

## `T-085` — as threads que se acumulam no Codex

Mecanismo já provado: `persistThread: true` é fixo no `task`; o runtime tem `ephemeral`; o sentido
inverso não polui porque o runner Anthropic passa `--no-session-persistence`.

| Opção | Ganho | Custo |
|---|---|---|
| **Híbrida** — efêmera quando a execução é única, persistente quando haverá rechecada | corta a maioria das threads sem perder retomada | `task` ainda não expõe a capacidade; se surgir continuação inesperada, exige briefing novo |
| Persistir e arquivar ao encerrar o papel | preserva contexto e limpa a lista | depende de arquivamento **não comprovado** |
| Trocar por `review`/`adversarial-review` | já são efêmeros | perde briefing sob medida e controle de effort |
| Manter e só organizar por card/papel | mudança mínima | reduz desordem, não quantidade |
| Pedir a flag upstream | expõe a capacidade sem gambiarra | sem prazo |

**Recomendação do planner, que endosso:** política híbrida como destino, pedido upstream em
paralelo, e enquanto a capacidade não estiver homologada, manter o reúso persistente **explícito**.

Ele também aponta que a expressão "estado terminal" na `SKILL.md:236` é ambígua: fim de um job não é
fim do papel — um parecer com correções encerra a chamada e inaugura a necessidade de rechecada.

## `T-086` — quem é o dono do card

| Família | Resolve | Não resolve |
|---|---|---|
| **A** — host na linha do card + guarda no lint | torna o responsável visível | duas escritas concorrentes deixam só a última marca, e o lint vê estado "válido"; não protege os outros arquivos compartilhados |
| **B** — um arquivo por card, com posse controlada | elimina a disputa em vez de sinalizá-la | nome de arquivo **não** dá unicidade: precisa de mecanismo de posse |

**Recomendação:** B como destino, A como sinalização transitória. O desenho proposto usa
`memory/wiki/cards/T-NNN.json` com host, sessão, geração de posse e revisão; `KANBAN.md` vira
**projeção gerada**. Isso muda um contrato central do plugin — e o próprio planner diz que a faixa
do card precisa ser reavaliada antes de implementar.

⚠️ **Duas afirmações vigentes do plugin caem com isso**, e ele mostrou onde: "só o board é disputado"
(`SKILL.md:350`) é falso — `MEMORY.md`, `_elenco.md`, log e manifesto de versão também são; e a
premissa de que qualquer lock mataria o paralelismo também não se sustenta, porque o lock proposto
cobre só a operação de metadados, nunca a chamada de LLM.

## `T-087` (reescrito) — o que chega ao runtime não é o que o produto documenta

**Recomendação:** um adaptador determinístico do Orquestra que monte os argumentos por código e
continue chamando `codex-companion.mjs task`. O briefing continua sendo trabalho do modelo; **os
argumentos deixam de ser**. Antes do spawn ele valida campos, resolve uma instalação **homologada
por caminho e capacidade** (em vez de "a mais nova que achar"), exige `--json`/modelo/effort, emite
`--fresh` ou `--resume-thread` de forma exclusiva, e recusa qualquer forma da opção de escrita —
aliases, duplicatas e valores inline.

⚠️ **Limitação que o contrato tem que declarar:** o JSON do `task` **não devolve** argumentos,
modelo, effort nem sandbox efetivo. O recibo local prova o que foi *lançado*, não o que o runtime
*reconheceu*. Isso vale inclusive para a validação que fiz do `T-019`: `write: false` solicitado e
ausência de arquivos tocados **não são prova equivalente** de confinamento.

## Divisão de trabalho entre os dois hosts

- **Um Manager/integrador por repositório.** As duas janelas seguem produtivas: uma planeja ou
  revisa enquanto a outra implementa.
- **Dois escritores simultâneos só em worktrees distintos.** O checkout mutável fica com um.
- Reviewer segue único e do vendor oposto ao host que implementou.
- Arquivos compartilhados e integração Git passam pelo integrador, com commit por allowlist **e
  conferência do conteúdo staged** — um arquivo permitido pode carregar alteração de outro trabalho,
  como aconteceu nesta sessão.
- **Não** eleger "Claude só para prosa" nem trocar elenco neste lote. O ganho vem de trabalho
  independente sobreposto, medido por tempo até aceite e retrabalho — não por número de agentes.

## Fora de escopo

Limpeza em massa de threads antigas, deleção de sessões, edição manual do estado do Codex, patch em
cache do Companion, instalações, troca de modelos e implementação dos hooks globais de segurança.
