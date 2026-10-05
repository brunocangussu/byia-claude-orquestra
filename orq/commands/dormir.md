---
description: Modo noturno — adianta PLANEJAMENTO dos cards do backlog enquanto você dorme, estacionando o que precisar de decisão sua. Com limites, orçamento e sem tocar em produção.
argument-hint: "[quantos cards, ex: 3] [--horas N]"
---

O dono vai dormir. Você vai **adiantar planejamento** — nunca implementação — dentro de limites duros.

Antes do manifesto, comprove `ORQ_PACKAGE_ROOT` e use o mesmo resolver canônico;
não reinvente o resolver: `sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" --resolver .`.
Use somente `board` e `thread_root` absolutos devolvidos, na frente atual. A
marca de host não transfere a propriedade da frente. Card de outra frente ou
thread ausente da frente dona interrompe somente aquela frente; não crie,
duplique, troque de frente ou faça fallback.

## ⚠️ Diga isto a ele ANTES de começar (uma linha, honesta)

A sessão do Claude Code **precisa ficar aberta** (máquina ligada, sem suspender). Não existe execução
realmente desacompanhada dentro do CLI. Se a máquina dormir, o trabalho pausa e retoma quando voltar.

## 1. Manifesto (escreva antes de qualquer trabalho)

Grave em `THREAD_ROOT/threads/_noturno.md`:

```
run_id: noturno-<AAAA-MM-DD-HHMM>
cards_max: 3          (default; $ARGUMENTS pode mudar)
horas_max: 4          (default)
expira_em: <hora>
modo: PLANEJAMENTO (nenhuma implementação)
cards: [IDs escolhidos]
```

Se já existir um manifesto **não expirado**, não abra outro — retome aquele.

## 2. Escolher os cards

Do BACKLOG, **em ordem**, no máximo `cards_max`. **Pule** qualquer card que envolva:
schema/migration · segurança/permissão · dependência nova · **instalar ferramenta na máquina**
(inclusive a stack complementar do `/orq:stack` — ela é opcional para o Orquestra, mas instalá-la
altera a máquina do dono do mesmo jeito) · deploy/infra · mudança de rumo do produto · qualquer coisa
irreversível. Esses **exigem o dono acordado** — deixe no backlog com nota.

Se sobrar nenhum card seguro, diga isso e **não invente trabalho**.

## 3. Trabalhar (um card por vez)

Para cada card: marque `[>]`, spawn **fresco** do `orq-planner` (contexto isolado), e no prompt inclua:

> "Modo noturno ativo — o dono está dormindo e **não vai responder**. Se surgir dúvida ou algo que
> precise da aprovação dele, **não pare esperando**: escreva no plano o que já foi decidido, onde
> você parou, e a **pergunta exata** que falta responder. Salve o plano e reporte."

Ao receber o plano:
- **Precisa de decisão dele** → card vira `[!]` AWAITING_OWNER, com a **pergunta exata escrita no
  card** + caminho do plano. **Nunca decida no lugar dele.**
- **Plano completo e sem pendência** → card vira `[!]` AWAITING_OWNER, com o caminho do
  plano e a pergunta exata **Você aprova este plano?**. Modo noturno não transforma plano
  em aprovação nem cria READY falsamente aprovado.

Depois de cada card: grave no board e siga pro próximo. **Uma tarefa travada nunca trava a fila.**

## 4. Parar (qualquer uma destas encerra o modo)

- Atingiu `cards_max` ou `horas_max`
- **Duas rodadas seguidas sem progresso verificável**
- Erro repetido no mesmo card (1 retry, não mais)
- O dono mandou parar

Ao encerrar, escreva o **relatório** no manifesto: o que planejou · o que estacionou (com as
perguntas) · o que pulou e por quê · quanto tempo levou.

## 🚫 Proibições absolutas (não negociáveis)

Nada disto, em hipótese alguma, com o dono dormindo:

- **Implementar código** (isto é modo planejamento — a v1 não implementa)
- `git push`, merge, deploy, publish
- Migration, SQL de escrita, qualquer mutação em banco
- Ler/mover/expor segredo ou credencial
- Instalar dependência
- Mensagem pra fora (e-mail, WhatsApp, webhook, API de terceiro que escreve)
- `rm -rf`, mover/apagar arquivo fora do que o card previa
- **Decidir no lugar do dono** qualquer coisa da lista do passo 2

Na dúvida sobre se algo é permitido: **não faça**, estacione o card e registre a dúvida.

## Continuidade de execução aprovada

Consulte o `Contrato de continuidade aprovada` em
`ORQ_PACKAGE_ROOT/skills/orq/SKILL.md`.
Modo noturno não transforma plano em aprovação e não é Goal: ele pode estacionar
um card sem bloquear outra ação permitida da frente dona, mas nunca implementa
ou libera card sem a evidência humana exigida.

## Cancelar

O dono manda parar (ou `/orq:dormir off`) → encerre imediatamente, grave o relatório parcial e
marque o manifesto como expirado.
