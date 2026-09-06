# T-079 — GPT-6 Astra no elenco e Fable 5.1 documentado

**Pedido do dono em 2026-09-05:** revisar o elenco vigente, **nomear o Fable como 5.1** onde ele
aparece, e promover o **GPT-6 (Astra)** ao planejamento e à revisão.

## ✅ CARD FECHADO — 2026-09-06

**Validado pelo dono nos dois hosts.** `0.27.0` publicada (`f194acd`), instalada e verificada:
`verify_installed_cache.py` deu `ok: installed cache matches source`, exit `0`, nos dois.

**Host Codex** — respondeu `Astra @ max` nas duas trilhas de planner e `Fable 5.1` no reviewer,
citando a linha do elenco. **Host Claude** — `fable` (Fable 5.1) na trilha `interface`,
`gpt-6-astra@max` em `planner·sistema` e no `reviewer`.

**A prova que fecha o defeito central**, medida no runner **instalado** do Codex (não no do repo):

```
MODEL_ALIAS=fable · OPUS_MODEL=claude-fable-5-1 · exit 0
```

e o `revisar.md` instalado passa `--model "$REVIEWER_MODEL_ALIAS"`. O elo que fazia o Codex revisar
com Opus enquanto o elenco declarava Fable está fechado **na versão que roda**, não só na fonte.

### O que continua NÃO comprovado, de propósito registrado

- **Astra como planner nunca rodou de verdade.** O mecanismo `codex exec … -s read-only` está
  comprovado no papel de **revisor**; como planner, o primeiro Loop A de trilha `sistema` é que será
  o teste real. Não confundir "configurado" com "exercitado".
- **A trilha ainda escolhe vendor no host Claude** (Fable vs. Astra), mas **não** no Codex, onde as
  duas trilhas colapsaram em Astra e a trilha virou só cerimônia — mesma coisa que já acontecera com
  as três faixas do `implementer` no Claude em 2026-09-03.

### Incidente de release, para não repetir

A primeira publicação (`e19b877`) saiu quebrada: `orq/stack.md:113` citava `claude_mem_status.py`,
script da frente `T-075` deixado fora do commit seletivo. O Manager rodou os gates no **working
tree contaminado** (onde o script existia sem estar commitado) e declarou verde; em fonte limpa o
lint reprovava e dois testes de `test_context_guard` caíam junto, por só invocarem o lint.
Corrigido em `f194acd`. **A lição não é "rodar os gates" — é rodar no checkout detached limpo antes
do push, que é exatamente o que o protocolo deste projeto já mandava.**


## O que a pesquisa comprovou (2026-09-05)

- **Claude Fable 5.1** — lançado em 2026-09-01; ~25% mais barato que o Fable 5 em workloads
  típicos; #1 no Vals Index (67,87%), à frente do Opus 5 e do Fable 5. Id de modelo:
  `claude-fable-5-1`.
- **GPT-6 Astra** — lançado em 2026-09-03; id de API `gpt-6-astra`; efforts `low|medium|high|
  xhigh|max` (não aceita `none`); US$ 10/US$ 50 por MTok no padrão.
- **O alias `fable` já resolve 5.1 no host Claude** desde o `T-053` (CLI 2.1.258, cache
  `additionalModelOptionsCache` com entrada única `claude-fable-5-1[1m]`). O `planner·interface`
  do Claude, portanto, **já roda 5.1 hoje** — falta dizer isso por escrito.

## Decisões do gate (dono, 2026-09-05)

1. **O `reviewer` do host Codex continua Anthropic (`fable`).** O dono pediu inicialmente Astra
   nos três papéis do Codex; ao ver que isso poria OpenAI revisando trabalho OpenAI, recuou. A
   regra "o vendor do host nunca revisa a si mesmo" **fica intacta** e não precisa ser reescrita.
2. **`planner·sistema` do host Claude também vai para Astra** — mesmo papel, mesmo modelo nos
   dois hosts.
3. **O runner Anthropic passa a exigir o prefixo `claude-fable-5-1`.** Documentar "é o 5.1"
   enquanto o verificador aceita `claude-fable-5` (que casa com 5.0) seria documentação que a
   execução não honra.

## O desenho alvo

| Papel | host Claude | host Codex |
|---|---|---|
| planner·interface | `fable` (Fable 5.1) — **sem mudança de valor**, só de documentação | **`gpt-6-astra`** ← era `fable` |
| planner·sistema | **`gpt-6-astra`** ← era `gpt-5.6-sol@max` | **`gpt-6-astra`** ← era `gpt-5.6-sol@max` |
| reviewer | **`gpt-6-astra`** ← era `gpt-5.6-sol@max` | `fable` (Fable 5.1) — **sem mudança** |
| implementer (3 faixas) · docs · scout | sem mudança | sem mudança |

## Consequências a declarar no plano (não são perguntas — já decididas)

- **No host Codex, a trilha deixa de escolher vendor.** Com `planner·interface` e
  `planner·sistema` os dois em Astra, o eixo "domínio decide quem pensa" passa a medir só
  cerimônia naquele host — exatamente o que já aconteceu com as três faixas do `implementer` no
  Claude em 2026-09-03. A régua continua válida (governa o gate), mas não traga expectativa de
  modelo diferente por trilha.
- **A via `runner-opus` perde um consumidor no Codex** (`planner·interface`) e mantém o outro
  (`reviewer`). A coluna `Consumida por` em `## Revisores externos` precisa ser corrigida.
- **A via `codex` ganha o `planner·sistema` do host Claude com modelo novo** — a célula
  OpenAI × host Claude passa a citar `gpt-6-astra`.

## Pendências comprováveis (não prometer antes de rodar)

- **O CLI do Codex expõe `gpt-6-astra`?** O catálogo de lá usa nomes próprios (`gpt-5.6-sol`,
  `gpt-5.6-terra`, `gpt-5.6-luna`); que a API tenha `gpt-6-astra` **não prova** que o binário o
  aceite em `-m`. Smoke obrigatório antes de gravar o valor no elenco — o precedente é o
  `gpt-5.6-luna` (2026-09-01), que existiu no catálogo mas nunca foi medido em `workspace-write`.
- **Qual effort declarar.** A proposta é `@max`, mantendo o degrau atual do `sol`. Confirmar que
  o binário aceita `model_reasoning_effort=max` para este modelo.
- **Custo.** Astra a US$ 10/US$ 50 é o mesmo preço de tabela do Fable 5; a nota de custo do
  `## Custo` e o preset `economia` presumem números antigos e precisam ser relidos.

## Contradição viva encontrada de passagem (2026-09-05)

`orq/commands/elenco.md`, na regra "Vendor certo não basta", ainda manda **recusar `fable` na
célula Anthropic × host Codex** ("o runner só executa Opus 5"). Isso ficou falso quando o `T-077`
parametrizou o `run-opus-reviewer.py` com `--model` e o `_elenco.md` passou a registrar `fable`
como `reviewer` daquele host. **O produto contradiz a si mesmo hoje**, e o `reviewer` do Codex é
justamente o papel que este card preserva — então a correção entra neste card, não em outro.

## Prova real do alias `fable` (executada pelo planner em 2026-09-05)

Antes de qualquer mudança no verificador, o runner foi chamado de verdade contra a API:

```
python3 orq/scripts/run-opus-reviewer.py --model fable --timeout 600
exit 0 · stdout FABLE_REAL_OK
OPUS_MODEL=claude-fable-5-1
OPUS_MODEL_USAGE=claude-fable-5-1,claude-haiku-4-5-20251001
```

Isto elimina a suposição que o primeiro plano carregava. O `claude-haiku-4-5` extra no
`modelUsage` é uso auxiliar do CLI e **não** invalida a prova: o modelo atribuído foi
`claude-fable-5-1`. A documentação não deve alegar que o Fable foi o único modelo do payload.

**Ramo de falha, se um dia a sonda voltar diferente:** parar antes de editar `MODEL_ALIASES`,
registrar o `modelUsage` literal aqui e devolver ao dono. **Nunca alargar o prefixo para a sonda
passar** — seria falsificar a prova para salvar a documentação.

## Escopo retirado deste card (2026-09-05)

A guarda de lint que compara a tabela viva do host Claude com o preset `padrao` **saiu do T-079**
e virou o card `T-080`. Motivo: a divergência dos três `implementer` é de 2026-09-03, tem causa
raiz distinta e não foi introduzida por este card — regra 4 do framework ("escopo tem borda").

**O que continua aqui:** corrigir os *valores* do preset `padrao`, porque `planner·sistema` e
`reviewer` do host Claude mudam por decisão deste card e deixariam o preset incoerente de imediato.
O que saiu é apenas a *guarda automatizada* sobre a divergência pré-existente.

## Efforts do Astra — o que se sabe, e o erro que quase virou documentação (2026-09-05)

O dono viu no app do Codex o **`Ultra`** oferecido para o GPT-6 Astra e questionou a afirmação do
planner de que o modelo só aceitava `low|medium|high|xhigh|max`. Ele estava certo.

**Fonte verificada** — `~/.codex/.codex-global-state.json`, declaração do próprio host:

```
gpt-6-astra   -> low, medium, high, xhigh, max, ultra
gpt-5.6-sol   -> low, medium, high, xhigh, max, ultra
gpt-5.6-terra -> low, medium, high, xhigh, max, ultra
gpt-5.6-luna  -> low, medium, high, xhigh, max          (sem ultra)
```

**Como o erro nasceu:** o planner rodou um controle negativo com `model_reasoning_effort=none`, leu
a lista da mensagem de erro e tratou-a como o conjunto completo de valores aceitos. Mensagem de erro
não é catálogo. O smoke seguinte, que tentaria medir `ultra` por chamada real, morreu antes por
restrição de sandbox aninhado (`failed to initialize in-process app-server client`) — inclusive no
controle positivo, o que prova que a falha era ambiental, não do effort.

**Decisão do dono, com o `ultra` disponível na frente dele:** as quatro células Astra ficam em
**`gpt-6-astra@max`**. Não é limitação técnica — é escolha. Qualquer arquivo que justifique o `@max`
alegando indisponibilidade do `ultra` está errado.

**Efeito colateral bom:** isto valida retroativamente o preset `padrao`, que já pedia
`gpt-5.6-sol@ultra`. Aquele valor sempre foi executável; o plano supunha o contrário.

## Implementação (2026-09-05)

**Passo 1 — TDD no runner, feito primeiro.** `test_rejects_fable_5_0_when_fable_5_1_is_required`
foi escrito e visto falhar (`0 != 7`) contra o código antigo, provando que `claude-fable-5` como
prefixo aceitava `claude-fable-5-0`. Só depois `MODEL_ALIASES["fable"]` virou `"claude-fable-5-1"`
em `orq/scripts/run-opus-reviewer.py`; a asserção de `test_proof_is_per_alias_not_hardcoded_to_opus`
foi apertada para o prefixo completo. `run-opus-reviewer.py`, `DEFAULT_MODEL_ALIAS="opus"` e os
códigos `OPUS_*` **não** foram renomeados — contrato de fio preservado.

**Passo 4 — o ponto que dá valor ao card.** `orq/commands/revisar.md` passou a extrair
`REVIEWER_MODEL_ALIAS` da linha `reviewer` do elenco e a chamar o runner com `--model
"$REVIEWER_MODEL_ALIAS"`, com aviso explícito de que chamar sem a flag cai no default `opus`.

**Passos 2/3/5 — reconciliação documental.** `_elenco.md`, `orq/commands/elenco.md`, o
`SKILL.md`, o README, `arquitetura.md` e `orq/stack.md` foram atualizados: as quatro células Astra
(`@max`), Fable nomeado 5.1 nas superfícies vivas, "runner de Opus fixo" e "no Codex só aceita
opus" removidos de todo lugar vivo. O preset `padrao` foi corrigido (Astra nos dois papéis que
mudaram, os três `implementer` em `sonnet`, alinhado à tabela ativa Claude) e `economia` trocou
`gpt-5.6-sol@high` por `gpt-6-astra@high`. Preço registrado: Astra US$ 10/US$ 50 por MTok; Fable
5.1 ~25% abaixo do Fable 5, sem preço absoluto (sem fonte verificada).

**Passo 7 — lint.** `REVIEWER_CLAUDE`/`REVIEWER_CODEX`, os fragmentos de `CONTRATOS_CODEX` (elenco,
revisar.md, runner) e o `VOCABULARIO_EXTINTO` (agora proibindo "runner de Opus fixo" e "no Codex só
aceita opus" em qualquer superfície viva) foram atualizados. **Nenhuma guarda tabela↔preset foi
adicionada** — ficou para o `T-080`, aberto ao final deste card.

**Passo 8 — bump.** `0.27.0` nos quatro anchors (`orq/.claude-plugin/plugin.json`, `README.md` —
Status, `memory/MEMORY.md`, `.claude-plugin/marketplace.json`), no mesmo lote desta mudança.

**Verificação real, não simulada:**
```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'  → 232 testes, OK
claude plugin validate ./orq --strict                                                 → Validation passed
python3 orq/scripts/lint-coerencia.py .                                               → coerência interna ok
git diff --check                                                                      → exit 0
```

**Card novo aberto:** `T-080` — "Perfil padrao pode divergir da tabela ativa sem o lint detectar"
(guarda tabela↔preset que este card deliberadamente não trouxe).

**Não feito / decisões do implementador:**
- README.md não ganhou números de preço (US$/MTok) — a seção já dizia "muda a garantia, não só o
  custo" sem citar valores; os preços comprovados foram registrados em `_elenco.md` (`## Custo`),
  que é a fonte natural. Se o dono quiser os números também no README, é ajuste pontual.
- Não toquei nas menções a "201 testes"/"219 testes" em `README.md`, `memory/wiki/distribuicao.md`
  e `memory/wiki/arquitetura.md` — a suíte real agora tem 232 (232 = 201 + `test_kanban_status.py`
  já contado em 215/219 anteriores + `test_claude_mem_status.py`, que já estava no working tree
  antes deste card, sem relação com o T-079 + o teste novo deste card). Esses contadores não
  constavam da lista de arquivos do plano; ficam como achado fora de escopo.
