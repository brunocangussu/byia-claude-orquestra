# Thread — desenvolvimento do próprio plugin

**Frente:** o Orquestra desenvolvendo o Orquestra (dogfooding).
**Aberta em** 2026-07-26 · **último checkpoint** 2026-07-29 · **versão** 0.13.0.

## Fases

- ✅ Dogfooding: board e wiki instalados no próprio repo
- ✅ Correção do namespace `/orquestra:*` → `/orq:*` (sobrevivera a 3 releases)
- ✅ Stack complementar auto-detectada, com consentimento e registro de recusa
- ✅ Painel de revisores consertado (2 causas raiz) e ampliado para 3 revisores
- ✅ Lint de coerência interna, testado nos dois sentidos
- ✅ Contrato do board (`_schema.md`) + smoke test de três sinais
- ✅ Protocolo de várias janelas
- ✅ Roteamento automático (cobertura de gatilho 0% → 100%)
- ✅ Problemas conhecidos documentados e diagnosticáveis
- ✅ **Ciclo completo rodado pela primeira vez** (0.11.0): Fable → gate → Sonnet → painel de 3
- ⬜ Hooks de segurança (`T-001`) — o único enforcement que bloqueia de verdade
- ⬜ Worktree obrigatório para revisor sem sandbox (`T-019`) — o Kimi destruiu o working tree
- ⬜ Perfis de elenco e motor alternativo (`T-020`, `T-021`) — pedido do dono em 29/jul
- ✅ Relatório do checkpoint: audiência corrigida (0.12.0) e formato legível (0.13.0)
- ⬜ **9 cards em VALIDATE** — a 0.13.0 já está instalada, então agora são testáveis

## Decisões que não devem ser re-litigadas

- **Kimi dentro do Orquestra, não como comandos globais.** Comandos globais criariam um segundo
  sistema de revisão paralelo ao `/orq:revisar`, que já tem reconciliação — mais forte que tabela
  comparativa.
- **Catálogo da stack aponta repositório, não comando.** Comando envelhece; repositório não. E some
  a assimetria de deixar uma ferramenta sem comando por falta de procedência.
- **Sem lock global no protocolo multi-janela.** Mataria o paralelismo que motiva as N janelas. A
  causa da perda é a reescrita do arquivo inteiro, não a concorrência.
- **Crases obrigatórias para skill no lint, opcionais para agente.** Assimetria proposital: "skill" é
  palavra comum em prosa portuguesa; `orq-` não aparece em texto corrido. Um revisor externo sugeriu
  uniformizar e a "correção" gerou 3 falsos positivos na hora.
- **CLI do Codex em vez do plugin.** Decidido porque o plugin não parecia invocável pelo modelo.
  ⚠️ **A premissa envelheceu:** `codex:codex-rescue` **aparece** como agent type nas sessões de
  29/jul, e a regra global do dono manda usar o subagente justamente para não perder rastreamento de
  job. A CLI funciona e é o que o `/orq:revisar` usa hoje — mas a justificativa registrada não vale
  mais. Reavaliar antes de citar esta decisão como definitiva.

## Padrão de erro que se repetiu — vigiar

**Concluir "não existe" a partir de verificação de fonte única.** Aconteceu duas vezes em dois dias:
`claude plugin --help | head` cortando lista alfabética (levou a escrever instrução falsa no plugin)
e `which kimi` respondendo sobre o PATH da sessão em vez do disco (levou outra sessão a quase
instalar pacote desnecessário). Nos dois casos a conclusão errada ia gerar ação real.

**E o irmão dele:** documentar o contrato sem endurecer o parser. A 0.6.0 escreveu a spec do board e
deixou o consumidor aceitando lixo; o painel reprovou.

## Decisões do dono em 2026-07-29 (não re-litigar)

- **Elenco padrão:** planner `fable`, implementer `sonnet`, reviewer `opus`. Ele quer poder trocar
  por perfil quando o crédito Claude estiver curto — virou `T-020`, não improvisar antes do plano.
- **Fechou** `T-003`, `T-008`, `T-011` (estruturais, já exercitados) e `T-012` (o ciclo rodou).
- **Manteve em VALIDATE** os comportamentais — eles só valem depois do release + restart.
- **Release da 0.11.0 autorizado**, incluindo o bump nos quatro lugares.

## ⏭️ RETOMAR AQUI

**Estado: 0.13.0 publicada, commitada (`e0aed12`) e com push feito.** Plugin instalado em escopo
`user` — vale em todos os projetos do dono, sem repetir nada em cada repo. `diff -rq` do cache contra
`./orq/` volta **vazio**. Board em **15% (4/26)**, 9 em VALIDATE (contagem de 2026-07-30, depois dos cards `T-024` a `T-027`;
o número muda a cada card — confira sempre com `bash orq/scripts/kanban-status.sh`).

**Três releases no mesmo dia:** 0.11.0 (diagnóstico de ambiente + parser do board + roteamento +
guarda de bump) · 0.12.0 (relatório do checkpoint: audiência e gate) · 0.13.0 (formato do relatório:
espaçamento). O ciclo completo rodou nos três, e **o review reprovou os três** — foi ele que pegou o
falso positivo do parser em prosa real, o vazamento de numeração interna para a tela, e a supressão
da autorização de `/clear` em projeto sem board.

⚠️ **Decisão de aparência sem ver renderizado é chute — custou um release.** O dono pediu relatório
"curto, 3–6 linhas"; entregue, ele reprovou a leitura (*"embolado"*). A compressão era a causa. Na
0.13.0 escolheu comparando **mockups com dados reais**. Da próxima vez que a decisão for visual,
mostre antes de construir.

**✅ Os três testes de roteamento estão cumpridos (2026-07-29/30) — não repita.**

| Frase | Esperado | O que aconteceu |
|---|---|---|
| *"queria melhorar o relatório do checkpoint"* | anuncia, cria card, para no gate | passou — virou o `T-022` |
| *"o painel de revisão não está funcionando"* | **cria card e planeja** — queixa sobre o produto | passou — virou o `T-024` |
| *"o Kimi sumiu do PATH"* | **diagnóstico, sem card** — queixa sobre ferramental | passou — ambiente ok, nada no board |

O terceiro era o **controle**, e os dois lados se comportaram diferente, que era o critério. Viés
declarado: o Manager conhece a instrução, então quem julga é o dono — `T-014` e `T-016` seguem em
VALIDATE esperando o "pode fechar" dele.

**Depois, em ordem:**
1. **Validar os 9 cards em VALIDATE** — cada um tem "Como validar" próprio na nota. O `T-022` é o
   mais rápido: trabalhar um bloco, dizer *"salva aí"*, e conferir que o relatório vem em **seções
   com título e espaçamento** (não em linhas comprimidas — isso foi reprovado), com a evidência do
   parser na seção `✅ Verificação`.
2. **`T-019`** — worktree obrigatório para revisor sem sandbox.
3. **`T-020` / `T-021`** — perfis de elenco e motor alternativo (pedidos do dono em 29/jul). O
   `T-021` tem teto técnico já escrito no card: subagente do Claude Code não roda modelo de terceiro.
4. **`T-001`** — hooks. O `T-019` provou o argumento contra o próprio repo.

⚠️ **Não rode o painel de revisores externos no repo vivo antes do `T-019`.** Só o Codex tem sandbox
(`-s read-only`); o Kimi não tem nenhum e destruiu o working tree em 28/jul. O revisor interno é
seguro e foi o que auditou a 0.12.0 sozinho.
