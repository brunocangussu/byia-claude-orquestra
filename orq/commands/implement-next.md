---
description: Loop B — implementa o próximo card aprovado, com review independente e documentação, até deixá-lo pronto para você validar
argument-hint: "[T-NNN para escolher um card específico]"
---

Você é o **Manager** (leia a skill `orq`). Rode o **Loop B — Implementação**.

## 0. Pré-condições (não negociáveis)
- O card precisa estar **READY** (`[~]`) com plano **aprovado**. Se não estiver, pare e diga que
  falta passar pelo `/orq:plan-next`.
- Card que escreve código roda em **worktree isolado** (`isolation: "worktree"` no spawn) sempre que
  houver outro trabalho em andamento no repo.

> **Elenco:** antes de cada despacho, **identifique o host**, leia `## Times por host`, resolva o
> papel (`implementer`, `reviewer`, `docs`) e só então aplique `## Matriz de invocação`. Sem elenco,
> use o template completo de `ORQ_PACKAGE_ROOT/commands/elenco.md` — a skill já precisa ter
> resolvido `ORQ_PACKAGE_ROOT` para o host atual. Configurado não significa rodando: registre o
> executor real.

## 1. Implementar

Confirme primeiro que existe **worktree dedicado** ao card. Nunca execute o writer no checkout do
Manager.

- **Host Claude:** spawn fresco do `orq-implementer` no worktree, com override resolvido.
- **Host Codex:** use o modelo/effort da linha `implementer` em `## Times por host` e copie o comando
  da célula OpenAI×Codex da Matriz, com sandbox `workspace-write`, executado dentro do worktree.
  `codex exec` é o caminho padrão; a primitiva nativa só é permitida quando o `_elenco.md` registrar
  override comprovado por chamada real.
- **Host Kimi:** só escreva se o hook bloqueante estiver comprovado e o worktree existir; siga a
  Matriz. Não há fallback cross-vendor silencioso.

Sem modelo, CLI, worktree ou sandbox exigido → **não escreva**. Devolva o card com a degradação
nomeada.

O briefing inclui: o card, o **plano aprovado**, os critérios de aceite, as convenções do projeto
(build/teste) e o que está fora de escopo.

Exija de volta: o que foi feito, como testou, o que **não** conseguiu fazer, e as decisões tomadas
no caminho.

## 2. Revisar (painel independente, read-only)
Rode o **painel de revisores** (`/orq:revisar`): `orq-reviewer` (Claude) **em paralelo** com o Codex
(modelo do elenco, read-only) e demais revisores configurados. Passe a todos o **mesmo briefing**: diff,
critérios de aceite, o que está fora de escopo.

**Reconcilie** antes de agir: confirmado por 2+ = alta confiança; achado solitário você **verifica no
código** antes de aceitar; divergência **você desempata**.

Em card pequeno e de baixo risco, um revisor só basta (`--rapido`) — não gaste painel em mudança
trivial. Se o reviewer interno da tabela ativa estiver rebaixado, quem decide o painel mínimo é o
`/orq:revisar` — regra lá.

**Aplicar as correções é do implementer**, não do reviewer. Achado grave → devolva ao implementer e
revise de novo. Máximo 2 rodadas; persistindo, escale pro dono.

## 3. Documentar (sobre o código FINAL)
Só depois do review fechado, spawn do `orq-docs` — senão a documentação descreve algo que mudou.
Documentação é **atemporal**: descreve como é agora, não a história da mudança.

Atualize também a **página de tópico** da wiki afetada (é aqui que a memória se paga).

## 4. Fechar
- Commit **local** na branch atual, mensagem no padrão do projeto. **Nunca `push`** sem o dono pedir.
- Mova o card para `[?]` VALIDATE — **não** para DONE. Commit não é critério de pronto.
- Escreva no card **como o dono valida**: passos práticos de usar o produto (abrir X → clicar Y →
  observar Z). Nada de git/logs/teste automatizado — isso é trabalho do time, não dele.

## 5. Reportar
Em poucas linhas: o que mudou · o que o review pegou · o que falta o dono testar · o que ficou
pendente. Se algo precisa de decisão dele, destaque.

## Regras
- Falhou o build ou o teste → **não** feche o card. Reporte com o erro real.
- Descobriu um bug fora do escopo → card novo no BACKLOG (você decide) ou inclua se for pequeno e
  da mesma causa raiz. Registre no board de qualquer jeito.
- Nunca marque DONE sozinho, salvo se o dono tiver delegado explicitamente aquele card.
