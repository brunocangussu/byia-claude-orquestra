# Thread — desenvolvimento do próprio plugin

**Frente:** o Orquestra desenvolvendo o Orquestra (dogfooding).
**Aberta em** 2026-07-26 · **último checkpoint** 2026-07-28 · **versão** 0.10.0.

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
- ⬜ **8 cards em VALIDATE** — só testáveis depois do release da 0.11.0 + restart

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
- **CLI do Codex em vez do plugin.** O plugin não é invocável pelo modelo (`codex:codex-rescue` não
  existe como agent type; `/codex:review` tem `disable-model-invocation`). Contraria a regra global
  do dono, que só é executável quando **ele** digita o comando.

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

**Estado: 0.12.0 publicada, commitada (`7012a0f`) e com push feito.** Plugin instalado em escopo
`user` — vale em todos os projetos do dono, sem repetir nada em cada repo. `diff -rq` do cache contra
`./orq/` volta **vazio**. Working tree limpo. Board em **18% (4/22)**, 9 em VALIDATE.

Dois releases saíram no mesmo dia: **0.11.0** (diagnóstico de ambiente + parser do board + roteamento
+ guarda de bump) e **0.12.0** (relatório do checkpoint). O ciclo completo rodou nos dois — Fable
planejou, dono aprovou no gate, Sonnet implementou, review reprovou e as correções entraram.

**A primeira coisa ao voltar são os dois testes que faltam** — só o dono pode rodá-los, porque o
Manager sabe o que a instrução manda e acertaria de memória:

| Frase | Esperado |
|---|---|
| *"o painel de revisão não está funcionando"* | **cria card e planeja** — queixa sobre o produto |
| *"o Kimi sumiu do PATH"* | **diagnóstico, sem card** — queixa sobre ferramental |

O segundo é o **controle**: se os dois virarem card, ou os dois virarem diagnóstico, o desempate do
`T-016` ficou frouxo e o card volta.

**Depois, em ordem:**
1. **Validar os 9 cards em VALIDATE** — cada um tem "Como validar" próprio na nota. O `T-022` é o
   mais rápido: trabalhar um bloco, dizer *"salva aí"*, e conferir que o relatório cabe em 3–6 linhas
   com a evidência do parser na linha de verificação.
2. **`T-019`** — worktree obrigatório para revisor sem sandbox.
3. **`T-020` / `T-021`** — perfis de elenco e motor alternativo (pedidos do dono em 29/jul). O
   `T-021` tem teto técnico já escrito no card: subagente do Claude Code não roda modelo de terceiro.
4. **`T-001`** — hooks. O `T-019` provou o argumento contra o próprio repo.

⚠️ **Não rode o painel de revisores externos no repo vivo antes do `T-019`.** Só o Codex tem sandbox
(`-s read-only`); o Kimi não tem nenhum e destruiu o working tree em 28/jul. O revisor interno é
seguro e foi o que auditou a 0.12.0 sozinho.
