# Thread — T-020 · Perfis de elenco: trocar o time inteiro por contexto de crédito

**Frente:** perfis nomeados no elenco · gatilho de crédito · o que se perde no modo economia.
**Aberta em** 2026-07-30 · **estado: PLANO PRONTO — aguarda gate do dono** · planner `fable`, modo noturno.
**Nada em `orq/` nem em `memory/` (além desta thread) foi editado** — este arquivo é o único artefato.

## O pedido, verbatim (transcript `bec00ade`, 2026-07-29)

> "Quando eu estou no final do ciclo semanal e tiver pouco crédito, pouca possibilidade de usar o
> Claude, eu diminuo a possibilidade de fazer planejamento com o Fable e **faço só com o Opus**. Eu
> **uso mais as outras, o Codex e o Kimi**, e as outras coisas. Eu queria ter essa possibilidade de
> ajustar isso conforme a necessidade, mas, **por padrão, deixar sempre essa que eu já falei**."

⚠️ **A paráfrase do card envelheceu num ponto que importa:** o card diz "menos Fable no planejamento"
e deixa a composição em aberto; o verbatim diz **planner → `opus`** no modo economia. A composição
do perfil não precisa ser inventada — está na fala dele. O terceiro bullet do mesmo pedido ("usar
outro LRM padrão ao invés do Claude, por exemplo o Codex ou direto no Kimi") **não é este card** —
é o `T-021` (motor alternativo) e o `T-026` (host alternativo), já no board.

## Causa raiz — por que trocar o time é caro hoje

O `_elenco.md` representa **um valor, não uma escolha**: guarda o time atual e nada mais. Não existe
o conceito de "time nomeado para o contexto X". Consequências, em cadeia:

1. Trocar o time = **N edições independentes** (5 papéis + 2 revisores), uma por invocação de
   `/orq:elenco <papel> <modelo>` ou na mão.
2. **Voltar é tão caro quanto ir** — e mais arriscado: nada registra qual era o time "normal".
   Depois de uma semana de economia, reconstituir o titular depende de memória (o "escolha do dono
   em 2026-07-28" na coluna Por quê é a única pista, e é prosa).
3. O **contexto** ("fim do ciclo, crédito curto") não tem onde morar: o arquivo só aceita valores
   por papel, então a intenção do dono se perde na tradução para 7 edições.

Causa raiz em uma frase: **o elenco é estado sem nome — falta o catálogo de onde o estado é
escolhido.** Não é defeito do que existe (papel a papel funciona; o Fable entrou assim); é a
demanda nova de trocar por *contexto*, que o desenho papel-a-papel nunca previu.

## Solução — perfis nomeados dentro do próprio `_elenco.md`

**Preset = tabela nomeada; ativar = reescrever a tabela ativa a partir do preset.** A tabela
"Papéis" que existe hoje continua sendo **a única coisa que os consumidores leem** (`plan-next:17`,
`implement-next:14`, `revisar:48`, `stack:32/47/93` — verificado por grep: todos leem
`_elenco.md`, nenhum precisa mudar). Uma linha nova "Perfil ativo" registra qual preset está
valendo, desde quando, e desvios manuais posteriores.

**Alternativas recusadas, e por quê:**
- **Arquivo por perfil / `_perfis.md` separado** — duas fontes de verdade sobre o time; `revisar`
  e `stack` grepam `_elenco.md` especificamente; mais um arquivo para o protocolo multi-janela.
- **"Perfil ativo" como ponteiro que os consumidores resolvem** — obrigaria a editar os 4 comandos
  + skill, e um preset malformado quebraria todo spawn. Com a tabela ativa, a falha de um preset
  ruim fica confinada ao momento da troca, e os consumidores ficam intocados.
- **Troca automática (Manager detecta crédito baixo e troca sozinho)** — o estado de crédito não é
  observável de dentro da sessão com confiabilidade, e trocar **garantia** sem fala do dono viola o
  "sempre pergunte: mudança de rumo". O gatilho é a frase dele, não uma inferência.

**Cruzamento com o `T-025` (gatilhos) — ordem que evita retrabalho:** a parte falada deste card
edita exatamente os dois lugares que o T-025 reescreve (`SKILL.md` description + tabela, passos 1–3
de lá). Recomendo **liberar o T-020 depois do T-023 e do T-025** — os dois já estão "PLANO PRONTO
esperando o dono", e este card então rebaseia sobre a SKILL nova. Se o T-025 emperrar, o T-020 pode
ir antes: o custo do rebase é pequeno (uma linha de tabela + um trecho de description), só não pode
ser simultâneo na mesma versão.

**Frases de gatilho — só as atestadas (lição do T-014/T-025: medir, não imaginar).** Léxico real do
dono no transcript: *"final do ciclo semanal"* · *"pouco crédito"* · *"acabando os créditos"*.
"Modo economia" é paráfrase do card (que ele leu), entra como o **nome de apelo** do perfil, marcada
como tal. "Volta o time normal" é frase proposta sem atestado — vai junto porque a volta precisa de
algum gatilho e o comando explícito cobre o resto.

**O que o `economia` muda na garantia, com todas as letras** (isto vai escrito no preset, não só
aqui): plano mais raso · reconciliação mais fraca (o desempatador interno rebaixado) · mais peso no
Kimi, que **não tem sandbox** (`T-019` — worktree descartável fica mais obrigatório, não menos) ·
Codex e Kimi são **read-only**: implementação continua queimando crédito Claude — o perfil reduz,
não zera. E o teto honesto: **perfil não troca o Manager** — a sessão principal é possivelmente o
maior consumo, e só o `/model` do dono a troca; o perfil no máximo sugere.

**Fora do Claude Code (achado do `T-026`):** não existe elenco multi-modelo por papel em outro
host — lá, perfil degrada para conselho em prosa no `AGENTS.md`. Mencionado; não se resolve aqui.

---

## Texto exato proposto

### A. `memory/wiki/_elenco.md` — conteúdo novo completo (substitui o arquivo)

```markdown
# Elenco — qual LLM toca cada papel

> **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
> O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste papel a papel com
> `/orq:elenco <papel> <modelo>`, ou troque o **time inteiro** com `/orq:elenco perfil <nome>` —
> ou fale naturalmente: *"quero o Fable planejando"*, *"tô com pouco crédito"*, *"modo economia"*.

**Perfil ativo:** `padrao` — desde 2026-07-28, sem desvio.
*(Trocar o perfil reescreve a tabela "Papéis" abaixo e vale a partir do **próximo spawn, em todas
as janelas** — crédito é da conta, não da frente. Agente já em execução termina no modelo antigo;
não se refaz nada. Ajuste papel a papel depois da troca é permitido: registre nesta linha como
desvio — ex.: `economia · desvio: planner→fable`.)*

## Papéis (tabela ativa — é ESTA que os comandos leem)

| Papel | Modelo | Por quê |
|---|---|---|
| `manager` | *sessão principal* | definido pelo `/model` — **não é spawn, não se configura aqui** |
| `planner` | `fable` | achar causa raiz e desenhar solução é o trabalho mais difícil — **escolha do dono em 2026-07-28** |
| `implementer` | `sonnet` | executar plano já aprovado é trabalho dirigido — **escolha do dono em 2026-07-28** |
| `reviewer` | `opus` | revisão adversarial exige raciocínio forte |
| `docs` | `sonnet` | escrita objetiva sobre código já pronto |
| `scout` | `sonnet` | leitura ampla e barata |

Valores aceitos: `opus` · `sonnet` · `haiku` · `fable` · `inherit` · ou um id específico
(`claude-opus-5`).

## Revisores externos

| Revisor | Estado | Config |
|---|---|---|
| codex | **ativo** | `codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh -s read-only "<briefing>" < /dev/null` · CLI em `/usr/local/bin/codex` |
| kimi | **ativo** | `KIMI=$(command -v kimi \|\| echo "$HOME/.kimi-code/bin/kimi")` então `"$KIMI" -p "<briefing>" --output-format text < /dev/null` · v0.29.2, OAuth · symlink em `~/.local/bin/kimi` criado em 2026-07-28 |

**Os dois exigem `< /dev/null`** — sem TTY eles bloqueiam lendo stdin e travam até o timeout.
**Nenhum dos dois recebe dado sensível** (ver a regra em `/orq:revisar`, passo 1b).

O Kimi **não tem flag de sandbox**. Não passar `-y`/`--yolo` nem `--auto`; reforçar "não edite
arquivo" no prompt. Garantia dura só em worktree descartável.

## Perfis — times nomeados por contexto de crédito

Perfil é um preset do time inteiro. Ativar = reescrever a tabela "Papéis" a partir do preset e
atualizar a linha "Perfil ativo". Os consumidores (`plan-next`, `implement-next`, `revisar`,
`stack`) não mudam: continuam lendo a tabela ativa.

**O `manager` não entra em perfil nenhum** — é a sessão principal, definida pelo `/model` do dono.
Ao ativar `economia`, sugerir em uma linha que ele avalie trocar o `/model` também: é onde mora o
maior consumo, e só ele troca.

### `padrao` — o time titular (vale por default — pedido do dono em 2026-07-29)

| Papel | Modelo | Por quê |
|---|---|---|
| planner | fable | achar causa raiz e desenhar solução é o trabalho mais difícil |
| implementer | sonnet | executar plano já aprovado é trabalho dirigido |
| reviewer | opus | revisão adversarial exige raciocínio forte |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

Revisores externos: codex **ativo** · kimi **ativo**. Painel completo em card normal; `--rapido`
em card pequeno.

### `economia` — fim do ciclo semanal, crédito Claude curto

Composição na palavra do dono (2026-07-29): *"diminuo o planejamento com o Fable e faço só com o
Opus; uso mais as outras, o Codex e o Kimi"*.

| Papel | Modelo | Por quê |
|---|---|---|
| planner | opus | escolha verbatim do dono para este contexto |
| implementer | sonnet | já era o econômico |
| reviewer | sonnet | o peso da revisão desloca para o painel externo, que não gasta crédito Claude |
| docs | haiku | escrita objetiva; rebaixar aqui custa pouco |
| scout | haiku | leitura ampla e barata |

Revisores externos: codex **ativo** · kimi **ativo** — e `--rapido` (só o interno) **deixa de ser
recomendado**: o interno é justamente o revisor rebaixado; em card pequeno, some pelo menos um
externo.

**O que se perde neste perfil — dito com todas as letras:**
- plano mais raso: card de **alto risco não se planeja em economia** — ou espera o crédito voltar,
  ou o dono aceita o risco por escrito no card;
- reconciliação mais fraca: quem desempata o painel é o reviewer interno, agora menor;
- mais peso no Kimi = mais exposição — ele não tem sandbox (`T-019`); worktree descartável vira
  **mais** obrigatório, não menos;
- Codex e Kimi são read-only: implementação continua queimando crédito Claude — o perfil **reduz,
  não zera**;
- o Manager não muda: o maior consumo é a sessão principal, e só o `/model` do dono a troca.

Quando o `T-021` (motor alternativo) fechar, este preset é o lugar de registrar o que mais o Codex
e o Kimi passam a carregar (ex.: pré-parecer read-only no planejamento). Até lá, não prometer.

## Por que o painel importa neste projeto

O produto aqui são **instruções**, não código. Onde dois modelos divergem sobre o que uma instrução
significa, **a divergência é o achado** — é sinal de ambiguidade real no texto, que um leitor futuro
também vai encontrar. O Codex tem contexto adicional: foi ele quem auditou a arquitetura original e
produziu o parecer que virou o roadmap.

Com **três** revisores (Claude · Codex · Kimi) a reconciliação fica mais forte: "confirmado por 2+"
deixa de ser unanimidade e vira **maioria**, o que separa melhor o achado sólido do palpite de um
modelo só. Três fornecedores distintos (Anthropic · OpenAI · Moonshot) erram de formas menos
correlacionadas que duas instâncias do mesmo.

Em card pequeno e de baixo risco, `--rapido` (só o revisor interno). Painel em mudança trivial é
desperdício. **Exceção: no perfil `economia`, ver a nota do preset.**
```

### B. `orq/commands/elenco.md` — três mudanças

**B1. Frontmatter** — `argument-hint` passa a:
`"[papel modelo | perfil nome — ex: 'planner fable' | 'codex off' | 'perfil economia']"`
e a `description` ganha ao final: `, e perfis nomeados para trocar o time inteiro`.

**B2. Seção nova**, inserida entre "## Com argumento — ajustar" e "## Modelo do arquivo":

```markdown
## Com argumento `perfil <nome>` — trocar o time inteiro

`$ARGUMENTS` no formato `perfil <nome>`. Exemplos: `perfil economia` · `perfil padrao`.

1. Leia a seção **Perfis** do `_elenco.md`. Perfil inexistente → liste os que existem e
   **pergunte**; não crie perfil novo sem pedido explícito.
2. Reescreva a tabela ativa **Papéis** a partir do preset (modelos e "Por quê"), aplique o estado
   dos revisores externos que o preset declarar, e atualize a linha **Perfil ativo** (nome + data,
   zerando desvios anteriores).
3. Confirme mostrando o time novo **e o que se perde** — resuma a nota do preset em até 3 linhas.
   **Anuncie, não pergunte**: a troca é reversível (`perfil padrao` desfaz).
4. A troca vale a partir do **próximo spawn, em todas as janelas** — crédito é da conta, não da
   frente. Agente já em execução termina no modelo antigo; não refaça nada. Se houver card `[~]`
   no board, diga em uma linha que ele termina com elenco misto, e que isso é esperado.
5. **`manager` não muda por perfil.** Ao ativar um perfil de economia, sugira em uma linha que o
   dono avalie o `/model` da sessão — é onde mora o maior consumo, e só ele troca.
```

**B3. Na seção "## Com argumento — ajustar"**, acrescentar ao passo 3 (depois de "Grave em
`memory/wiki/_elenco.md`…"): `Se o perfil ativo não for o 'padrao' e o ajuste divergir do preset,
registre o desvio na linha Perfil ativo (ex.: 'economia · desvio: planner→fable').`

**B4. "## Modelo do arquivo"** (o template que o `init` referencia) ganha, depois da tabela de
papéis e antes dos revisores externos, a linha `**Perfil ativo:** \`padrao\`` no topo, e ao final:

```markdown
## Perfis — times nomeados
### `padrao` — o time titular (a tabela acima)
### `economia` — crédito curto: rebaixe planner e reviewer um degrau, docs/scout para `haiku`,
mantenha os revisores externos ativos, e registre **o que se perde** — perfil de economia muda a
garantia, não só o custo. Ajuste os modelos à realidade do projeto ao criar.
```

**B5. "## Orientação"** ganha um bullet: `**Fim do ciclo de crédito?** \`perfil economia\` troca o
time inteiro — e o preset diz, com todas as letras, o que se perde. \`perfil padrao\` desfaz.`

### C. `orq/skills/orq/SKILL.md` — duas mudanças pequenas

**C1. Description** (bloco elenco, hoje `elenco ("quem tá revisando", "troca o modelo", "tira o
GPT")`) passa a: `elenco ("quem tá revisando", "troca o modelo", "tira o GPT", "pouco crédito",
"final do ciclo", "modo economia")`.

**C2. Linha da tabela** (hoje :71) passa a:

```markdown
| "quem tá revisando?" · "troca o modelo do planner" · "quero o Fable planejando" · "tira o GPT" · "tô com pouco crédito" · "final do ciclo" · "modo economia" · "volta o time normal" | **Elenco** (`/orq:elenco`) — mostra ou ajusta qual LLM toca cada papel; frase de contexto de crédito troca o **time inteiro** pelo perfil nomeado (`perfil economia` / `perfil padrao`), anunciando o que muda **e o que se perde** |
```

⚠️ Se o T-025 já tiver sido liberado, aplicar C1/C2 sobre a SKILL pós-T-025 (mesmo conteúdo, linhas
possivelmente deslocadas).

### D. `README.md` — seção "Elenco" (após os exemplos de :160-164)

```bash
/orq:elenco perfil economia    # fim do ciclo: troca o time inteiro pelo preset de crédito curto
/orq:elenco perfil padrao      # crédito voltou: time titular de volta
```

E o parágrafo, após "Ou simplesmente fale…":

```markdown
**Perfis** — além do ajuste papel a papel, o `_elenco.md` pode ter **times nomeados** (seção
"Perfis"): `padrao` (o titular) e `economia` (crédito Claude curto). Trocar o perfil reescreve a
tabela ativa; os comandos continuam lendo a mesma tabela. Honesto: perfil de economia muda a
**garantia**, não só o custo — plano mais raso, reconciliação mais fraca, mais peso em revisor sem
sandbox — e o preset lista isso com todas as letras. O `manager` nunca entra em perfil: é o
`/model` da sessão, e só o dono troca.
```

---

## Passos (após o gate — nenhum foi executado)

**Produto (`orq/` + README — bumpa versão):**
1. `orq/commands/elenco.md`: aplicar B1–B5. Verificar: leitura contra o texto exato acima.
2. `orq/skills/orq/SKILL.md`: aplicar C1–C2 (sobre a versão vigente — ver nota do T-025).
   Verificar: `grep -n "modo economia\|pouco crédito" orq/skills/orq/SKILL.md` acha description
   **e** tabela.
3. `README.md`: aplicar D + linha de Status/versão.
4. Bump nos **quatro** lugares (`orq/.claude-plugin/plugin.json` · README Status ·
   `memory/MEMORY.md` · `.claude-plugin/marketplace.json`). **Número: o próximo livre na fila** —
   T-023 propôs 0.14.0 e T-025 propôs 0.15.0; depende da ordem em que o dono aprovar (decisão 5).
5. Gates: `claude plugin validate ./orq --strict` + `python3 orq/scripts/lint-coerencia.py .`.
6. Release completo: `marketplace update` + `plugin update` + **restart** + `diff -rq` do cache
   voltando vazio. Só então os testes do dono.

**Projeto (`memory/` — sem bump; quem aplica é o Manager, não o implementer):**
7. Reescrever `memory/wiki/_elenco.md` com o texto exato da seção A.
8. `memory/wiki/_schema.md`, tabela de várias janelas: linha nova
   `| \`wiki/_elenco.md\` | qualquer janela | releia antes; troca de perfil vale para TODAS as janelas no próximo spawn — anuncie em uma linha |`.
9. Pós-validação (dever de checkpoint): `arquitetura.md` (parágrafo curto: elenco tem perfis;
   limitação "manager não configurável" ganha "nem por perfil"), `MEMORY.md` (linha do `_elenco.md`
   na tabela de páginas → "+ perfis nomeados"), log e esta thread.

## Critérios de aceite — o dono usando o produto, pós-release + restart

1. Dizer **"tô com pouco crédito, modo economia"** → o time inteiro troca **sem comando digitado**;
   a resposta anuncia em poucas linhas o que mudou **e o que se perde**; `_elenco.md` mostra
   `Perfil ativo: economia` e a tabela ativa igual ao preset.
2. Planejar um card nesse estado → o planner spawna em `opus` (o modelo aparece no anúncio de
   roteamento, como a skill já exige).
3. Dizer **"volta o time normal"** (ou `/orq:elenco perfil padrao`) → titular de volta, Fable no
   planejamento, linha Perfil ativo atualizada.
4. Com `economia` ativo, `/orq:elenco planner fable` → só o planner muda e a linha mostra
   `economia · desvio: planner→fable`.
5. **Contra-teste de falso positivo:** falar de "economia de tokens" num contexto que não é crédito
   (ex.: discutir o context-mode) → **nada troca**.
6. O anúncio da troca **nunca** afirma trocar o Manager — no máximo sugere o `/model` em uma linha.

## Decisões do dono (numeradas — responda "1a, 2a…" que destrava tudo)

1. **Quantos perfis:** (a) 2 — `padrao` + `economia` — **recomendo**: é o pedido; acrescentar um
   terceiro depois custa uma tabela; (b) +`forca-total` (tudo opus/fable, início de ciclo);
   (c) +`so-claude` (externos off — o cenário do README:186).
2. **Composição do `economia`:** (a) planner `opus` (sua palavra) · implementer `sonnet` · reviewer
   `sonnet` · docs/scout `haiku` · externos ativos — **recomendo**; (b) reviewer mantém `opus` —
   economiza menos, garante mais (você não falou do reviewer; o rebaixamento é inferência minha);
   (c) planner `sonnet` — economiza mais que o seu "só com o Opus", só se você quiser.
3. **Troca falada:** (a) sim — frases atestadas, troca imediata com anúncio honesto, sem pedir
   confirmação (é reversível) — **recomendo**; (b) só comando explícito — mais seguro contra falso
   positivo, mas trai o "modo economia" dito de passagem.
4. **`--rapido` no economia:** (a) desaconselhado — interno + pelo menos 1 externo mesmo em card
   pequeno, porque o interno é o rebaixado — **recomendo**; (b) mantém a regra atual.
5. **Ordem de release:** (a) depois de T-023 e T-025 (número = próximo livre; evita rebase da SKILL
   que o T-025 reescreve) — **recomendo**; (b) antes — rebase barato, mas duplo trabalho na SKILL.
6. **Template do `init` ganha a seção Perfis** (B4): (a) sim, genérica — **recomendo**: projeto
   novo nasce com o conceito; (b) não — perfis só neste repo, template intocado.

## Riscos

- **Drift silencioso** entre preset e tabela ativa: a linha de desvio é instrução, não enforcement —
  nada impede uma janela de editar a tabela sem registrar (mesma lição do `T-019`/`T-001`: instrução
  não segura). Aceito: o custo do drift é baixo e visível no `/orq:elenco` sem argumento.
- **Falso positivo do gatilho** ("economia" fora de contexto de crédito) — mitigado por frases
  estreitas + contra-teste 5; se falhar, a decisão 3b (só explícito) é o fallback.
- **Conflito de edição com o T-025** na SKILL — resolvido por ordem de release (decisão 5).
- **Perda de garantia no `economia` é real e é o produto** — está escrita no preset de propósito;
  o risco seria escondê-la.
- **Troca no meio de card de outra janela** → card termina com elenco misto (plano fable, review
  sonnet). Aceito e anunciado (passo 4 do B2), não bloqueado — bloquear exigiria lock, recusado no
  protocolo multi-janela.
- **`/orq:elenco` literal nunca foi invocado de verdade** (mesma ressalva do T-012 sobre os loops):
  até hoje a troca foi o Manager editando na mão. O teste comportamental 1–4 cobre.

## O que NÃO investiguei (e por quê)

- **Consumo real de crédito por modelo** (fable vs opus vs sonnet) — sem fonte local; a composição
  do `economia` segue a **palavra do dono**, não medição. Se opus não for mais barato que fable na
  prática, o preset economiza menos do que promete — corrigir é editar duas células.
- **Se `haiku` funciona bem como docs/scout neste repo** — nunca foi spawnado aqui; rebaixamento de
  menor risco do time, mas não testado.
- **Detecção automática de crédito baixo** — descartada de saída (não observável de dentro da
  sessão; e trocar garantia sem fala do dono viola a política de iniciativa em discussão no T-025).
- **Como perfil se traduz fora do Claude Code** — sem spawn com override lá (`T-026`); perfil vira
  prosa. Mencionado no plano, resolvido em lugar nenhum, de propósito.
- **T-021 (Codex/Kimi carregando papéis)** — o preset `economia` deixa o gancho escrito e não
  promete nada; o que eles podem carregar com que garantia é a pergunta daquele card.

## Escopo — fica de fora

- Migração de papéis para CLI externa (`T-021`) · host alternativo (`T-026`) · enforcement por hook
  (`T-001`/`T-002`) · qualquer mudança nos consumidores do elenco (`plan-next`, `implement-next`,
  `revisar`, `stack` — por desenho, não precisam mudar) · troca automática por detecção de crédito ·
  perfis além dos aprovados na decisão 1 · mover cards · editar `memory/` além desta thread.

## ⏭️ RETOMAR AQUI

**O plano está pronto e nada foi implementado.** Próxima ação: o **Manager leva as 6 decisões acima
ao dono**. Com as respostas, o card vai a READY e o implementer executa os passos 1–6 (produto) na
versão definida pela decisão 5; os passos 7–9 (memory/) são do Manager no fechamento. Os textos das
seções A–D são o produto — aplicar verbatim, ajustando só o que as decisões 1–4 mudarem (a
composição da tabela do `economia` depende da 2; a linha da SKILL depende da 3; a nota de `--rapido`
depende da 4; o B4 depende da 6). Sem resposta, o card vira `[!]` com a pergunta exata: "responda as
decisões 1–6 da thread T-020-perfis-elenco".
