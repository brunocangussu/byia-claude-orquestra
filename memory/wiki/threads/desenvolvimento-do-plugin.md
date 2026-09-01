# Thread — desenvolvimento do próprio plugin

**Frente:** o Orquestra desenvolvendo o Orquestra (dogfooding).
**Aberta em** 2026-07-26 · **último checkpoint** 2026-08-29 · **versão registrada nesta thread** 0.13.0.

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

**Estado: 0.16.0 publicada, commitada (`e15101d`) e com push feito** (2026-07-31). Plugin em escopo
`user` — vale em todos os projetos do dono. `diff -rq` do cache contra `./orq/` volta **vazio**.
Board em **17% (5/28)**, 12 em VALIDATE (confira sempre com `bash orq/scripts/kanban-status.sh`;
o número muda a cada card).

**Seis releases em três dias.** 0.11.0 (diagnóstico + parser + roteamento) · 0.12.0 e 0.13.0
(relatório do checkpoint: audiência, depois espaçamento) · **0.14.0** (reload×restart vira evidência
por componente) · **0.15.0** (`/orq:ajuda` + gatilhos medidos + iniciativa em três níveis) ·
**0.16.0** (perfis de elenco trocados por frase). **O review reprovou todos os seis.**

**O padrão que se repetiu nos três últimos, e é o achado de método da semana:** o review não pegou
só defeito da implementação — pegou **defeito criado pela correção anterior**. Na 0.14.0 a correção
inventou contradição entre `orq/stack.md` e `orq/commands/stack.md`; na 0.15.0 duas correções
interagiram e produziram uma exceção **inalcançável por construção**; na 0.16.0 o template definiu um
perfil como ponteiro para si mesmo, e depois a correção disso plantou o único caminho relativo do
plugin. **Corrigir é uma mudança como outra qualquer — precisa da mesma revisão que o original.**

⚠️ **Três reincidências do mesmo defeito de origem (`T-014`):** gatilho inventado em vez de medido.
Na 0.15.0 e na 0.16.0 o plano até **sabia** e marcou a frase como paráfrase — e ela entrou no produto
sem a marca. A saída adotada na 0.16.0 é a que deve virar regra: **não adivinhe a fala do dono**;
descreva a **intenção** como categoria, e faça o sistema **ensinar** a frase no momento em que ele
precisa dela.

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

**A fila aprovada acabou — nada está em curso.** Próximo, em ordem:

1. **Validar os 12 cards em VALIDATE** — cada um tem "Como validar" na própria nota. Os três mais
   novos se testam conversando: *"quais as possibilidades"* (0.15.0) · *"tô com pouco crédito"* e o
   contra-teste *"chegamos ao final do ciclo"*, que **não** pode trocar o time (0.16.0) · e
   *"instala o Serena aqui"*, que tem de sair com **uma** instrução só (0.14.0).
2. **`T-029`** — o lint é cego para caminho relativo entre arquivos do plugin. É barato e fecha o
   buraco que deixou passar o defeito do `init.md` na 0.16.0.
3. **`T-028`** — o README afirma que o Kimi não está instalado; ele é revisor ativo desde 28/jul.
4. **`T-019`** — worktree obrigatório para revisor sem sandbox. **A premissa dele mudou:** o Kimi
   **tem** hooks `PreToolUse` bloqueáveis, então a opção (c) voltou à mesa (achado do `T-026`).
5. **`T-001`** — hooks de segurança. O `T-019` provou o argumento contra o próprio repo.
6. **`T-026`** — host alternativo: plano pronto, guardado por decisão do dono. Reconferir a matriz de
   paridade antes de implementar, porque Codex e Kimi mudam rápido.

⚠️ **Não rode o painel de revisores externos no repo vivo antes do `T-019`.** Só o Codex tem sandbox
(`-s read-only`); o Kimi não tem nenhum e destruiu o working tree em 28/jul. O revisor interno é
seguro e foi o que auditou a 0.12.0 sozinho.

## ⏭️ RETOMAR AQUI — checkpoint de recuperação 2026-08-29

A sessão atual avalia, sem instalar, o repositório `kingbootoshi/cartographer` como possível apoio
ao Orquestra. A inspeção estrutural confirmou grafo SQLite local, briefs delimitados, auditoria de
remoção, verificação de frescor e adoção; a sobreposição principal é com codebase-memory e Serena.
Próxima ação concreta: entregar o parecer comparativo ao dono, recomendando ou rejeitando um piloto
opcional. Não criar card nem alterar produto antes de nova autorização explícita.
