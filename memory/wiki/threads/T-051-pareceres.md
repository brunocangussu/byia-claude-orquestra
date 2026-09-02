# T-051 — Pareceres do revisor externo (recibos das 7 rodadas)

> **Por que este arquivo existe.** O plano do `T-052` (reconciliação com o ramo remoto) exige provar,
> bloqueador a bloqueador, que **nenhuma das 25 correções da `0.24.0` se perdeu na fusão**. O critério
> aprovado não é "reler com atenção": é um ledger com um recibo por bloqueador. Os pareceres viviam
> apenas no scratchpad da sessão, que é volátil — foram consolidados aqui em 2026-09-01 para virar
> evidência durável e versionada.
>
> **Revisor:** Codex/GPT (`gpt-5.6-sol`), vendor oposto ao host Claude, read-only, via
> `codex-companion.mjs adversarial-review --base main --scope branch`.
> **Alvo:** branch `feat/t051-elenco-por-tarefa`, hoje mergeada na `main` local em `dcc350b`.
> **Contagem por rodada: 5 → 8 → 4 → 5 → 2 → 1 → 0 (APROVADO).** Total: **25 bloqueadores**.
>
> ⚠️ **Os gates ficaram VERDES em todas as sete rodadas**, inclusive com os oito bloqueadores da
> rodada 2 presentes. Nenhum destes achados é detectável por `plugin validate` ou pelo lint — é a
> razão de o revisor externo existir neste projeto.

---

## Rodada 1 — 5 bloqueadores · REPROVADO

Executada pelo subagente `codex:codex-rescue` (sem arquivo de saída; transcrita do relatório).

1. **`CLAUDE.md:83-85` / `AGENTS.md:83-85`** — *"Você entra pelo `/orq:revisar`, ao lado do revisor
   interno."* Instrução viva recriando o painel proibido.
2. **`README.md:386,400-407`** — bloco de status corrente ainda prometia `/orq:instalar` para
   "Codex e Kimi" e "painel Opus 5 + Kimi K3". Não era changelog delimitado.
3. **`orq/skills/orq/SKILL.md:28,36-39`** — *"faça direto, sem cerimônia | `leve`"* contra *"A coluna
   Faixa acima decide o degrau de quem escreve"*. Duas execuções opostas justificáveis pelo mesmo arquivo.
4. **`orq/commands/revisar.md:2,118-119`** — segundo parecer "avulso" sem restrição de vendor: porta
   dos fundos para o revisor do próprio vendor do host.
5. **`orq/scripts/lint-coerencia.py:339-345`** — `count(linha_reviewer) != 1` sem ancorar no host:
   trocar as linhas entre `Host Claude` e `Host Codex` mantinha `1/1` e o lint verde, com cada host
   revisado pelo próprio vendor.

---

## Rodada 2

<sub>sha256(saída bruta, 16): `08b04d0c0a97eb04` · origem: `review2-t051.txt`</sub>

```
# Codex Adversarial Review

Target: branch diff against main
Verdict: needs-attention

VEREDITO: REPROVADO. Revisei o diff não commitado de 18 arquivos contra main — HEAD e main estão em 008fbc9. Manifesto e lint passam, e CLAUDE.md/AGENTS.md são byte-idênticos, mas restam 8 bloqueadores semânticos. RISCOS: seleção silenciosa do modelo/vendor errado, perfis sem efeito e falsa confiança produzida pelo lint verde.

Findings:
- [critical] BLOQUEADOR 1 — Há duas fontes incompatíveis para o elenco ativo (orq/commands/elenco.md:164-174)
  `orq/commands/elenco.md:164` afirma: “## Papéis (a tabela ativa — é esta que os comandos leem)”, e perfis/ajustes reescrevem essa tabela (`:133-143`). Entretanto, `plan-next`, `implement-next` e `revisar` mandam resolver o papel em `## Times por host`; o próprio template fixa outros modelos nessas tabelas (`:216-240`). Cenário: no host Codex, `perfil economia` reescreve `## Papéis`, mas o próximo spawn continua usando `## Times por host`, tornando a troca inócua. Se um consumidor escolher `## Papéis`, recebe implementers Anthropic e reviewer OpenAI, violando respectivamente escrita no vendor do host e revisão pelo vendor oposto.
  Recommendation: Definir uma única fonte ativa host-aware. Perfis e ajustes devem modificar exatamente os valores que todos os consumidores resolvem, com regra explícita de projeção por host; eliminar ou tornar derivada a tabela concorrente.
- [high] BLOQUEADOR 2 — A régua canônica atribui faixa ao Trivial que a skill proíbe (orq/skills/orq/SKILL.md:28-44)
  `orq/skills/orq/SKILL.md:41-44` diz: “Onde não há spawn, não há faixa” e “A faixa só vale de Pequeno para cima”. Porém `orq/commands/elenco.md:34-35` define `leve` para resultado mecânico e cita literalmente “typo”, enquanto a linha Trivial da skill (`:28`) inclui typo e exige execução direta, sem implementer. Cenário: ao corrigir um typo, um modelo segue a régua canônica e anuncia `leve`/spawna Haiku; outro segue a tabela e o Manager escreve diretamente.
  Recommendation: Adicionar à régua canônica uma pré-condição explícita: Trivial encerra a classificação sem faixa. Remover “typo” dos exemplos de `leve` ou qualificá-lo como mudança Pequena já classificada como não trivial.
- [high] BLOQUEADOR 4 — `secao_de` não ancora headings e permite falso verde (orq/scripts/lint-coerencia.py:63-69)
  A função usa `if heading not in texto` e `texto.split(heading, 1)` (`:63-65`), portanto aceita substring em vez de heading Markdown exato. Prova executada: um template contendo apenas `### Host Codex antigo`, sem nenhuma linha exatamente igual a `### Host Codex`, passou todas as condições aplicadas pelo guarda de reviewer. Assim, renomear/remover o heading obrigatório pode deixar o lint verde e preservar uma tabela de host inválida.
  Recommendation: Localizar o heading com regex multiline ancorada e igualdade integral da linha, escapando o texto; recortar a partir do `match.end()`. Adicionar testes para heading exato, prefixado, inline, duplicado e ausente.
- [high] BLOQUEADOR 5 — A guarda do host aposentado ignora três superfícies vivas de instrução (orq/scripts/lint-coerencia.py:417-424)
  O comentário determina: “Mira só `orq/`: README, CLAUDE.md e AGENTS.md descrevem o histórico” (`:421-423`), e o loop realmente percorre apenas `plugin.rglob`. Mas CLAUDE.md e AGENTS.md governam modelos, e README.md contém instruções operacionais. Cenário: reintroduzir “use Kimi/Moonshot como revisor” nos dois arquivos idênticos mantém tanto a guarda de identidade quanto a guarda do host verdes. Isso contradiz `README.md:423`, que promete que o suporte foi removido “com guarda de regressão no lint”, e pode reabrir transferência para um terceiro vendor.
  Recommendation: Varrer também README.md, CLAUDE.md e AGENTS.md. Permitir somente ocorrências históricas exatas ou seções marcadas por uma allowlist estrutural, em vez de excluir arquivos inteiros.
- [high] BLOQUEADOR 6 — O frontmatter enfraquece “vendor oposto” para apenas “outra LLM” (orq/commands/revisar.md:2-11)
  O frontmatter diz: “todo revisor é de outra LLM que a do host” (`:2`), enquanto o corpo exige “sempre do vendor oposto ao host” (`:9-11`). As condições não são equivalentes: em host Codex/OpenAI, outro modelo OpenAI é outra LLM, mas continua sendo o vendor do host e é proibido pelo corpo. A redação fraca também aparece em `README.md:34`, `orq/commands/ajuda.md:19` e no exemplo de `orq/skills/orq/SKILL.md:50`, ampliando a rota ambígua mais saliente ao modelo.
  Recommendation: Substituir “outra LLM” por “modelo do vendor oposto ao host” no frontmatter e em todos os consumidores; reservar “outro modelo” apenas para distinguir um segundo parecer dentro desse vendor oposto.
- [high] BLOQUEADOR 8 — O ajuste do elenco continua codificado para Claude apesar do suporte ao host Codex (orq/commands/elenco.md:68-84)
  A validação aceita como via cross-vendor somente “(`codex`)” (`:74-76`), mas o template registra também `runner Opus` (`:189-192`). Além disso, papéis de escrita aceitam apenas aliases Anthropic e um ID Claude (`:81-84`), embora `## Times por host` use modelos OpenAI para todos os implementers do Codex (`:237-239`). Cenário: no host Codex, “tira o Opus da revisão” não identifica uma via válida; e “troca o implementer normal para gpt-5.6-terra” cai como valor desconhecido, embora seja exatamente o modelo previsto pelo próprio template.
  Recommendation: Resolver primeiro o host; aceitar dinamicamente todas as vias registradas e modelos do vendor desse host. Documentar aliases para `runner Opus` e remover listas de escrita hard-coded para Claude do caminho compartilhado.
- [medium] BLOQUEADOR 3 — A linha Normal fixa uma faixa que a régua manda variar (orq/skills/orq/SKILL.md:30)
  `orq/skills/orq/SKILL.md:30` fixa Normal como faixa `normal`. A régua canônica diz que decisão de desenho restante resulta em `pesada` (`orq/commands/elenco.md:32-33`) e que resultado completamente determinado resulta em `leve` (`:34-39`), inclusive após reavaliação no gate. Cenário: uma feature Normal nasce com duas soluções defensáveis e deveria ser `pesada`; depois de um plano integralmente determinado deveria cair para `leve`. A tabela continua instruindo `normal` nos dois momentos.
  Recommendation: Trocar a célula por `pesada`, `normal` ou `leve`, conforme a régua canônica, ou declarar que a coluna representa apenas um default inicial e documentar expressamente as duas transições.
- [medium] BLOQUEADOR 7 — O fluxo permite segundo parecer e depois afirma que ele não existe (orq/commands/revisar.md:118-140)
  O corpo autoriza: “Segundo parecer só sob demanda do dono” e permite outro modelo, effort ou briefing (`:118-124`). Na auditoria, porém, afirma universalmente: “todo achado é solitário por construção” (`:136`) e “não há segundo parecer para contrapor” (`:140`). Cenário: o dono pede segunda opinião e recebe dois pareceres divergentes; o Manager não tem instrução para reconciliá-los e é simultaneamente orientado a tratar cada achado como solitário.
  Recommendation: Separar explicitamente a auditoria padrão N=1 da auditoria excepcional com segundo parecer; no segundo ramo, definir reconciliação e manter a verificação direta do Manager como desempate final.

Next steps:
- Corrigir primeiro a fonte única do elenco e as duas contradições da régua; elas afetam todo despacho.
- Endurecer `secao_de` e ampliar a guarda do host aposentado, com provas negativas automatizadas.
- Unificar o contrato de revisão em “vendor oposto” e definir o ramo de auditoria com segundo parecer.
- Reexecutar `claude plugin validate ./orq --strict` e `python3 orq/scripts/lint-coerencia.py .`; os dois estão verdes agora, mas não detectam estes bloqueadores.
```

---

## Rodada 3

<sub>sha256(saída bruta, 16): `7fb55932031fc412` · origem: `review3-t051.txt`</sub>

```
# Codex Adversarial Review

Target: branch diff against main
Verdict: needs-attention

REPROVADO: quatro regressões materiais impedem o ship, embora `plugin validate --strict` e `lint-coerencia.py` passem.

Findings:
- [high] Comandos de via são reconhecidos, mas não podem ser aplicados (orq/commands/elenco.md:101-119)
  A instrução aceita “uma via cross-vendor registrada” e cita a coluna `Via`, mas o passo seguinte valida o valor exclusivamente como modelo. Assim, `codex off` ou `runner-opus off` reconhece a via e depois trata `off` como valor desconhecido; não existe passo que atualize a coluna `Estado`. O exemplo `codex xhigh` também não corresponde ao contrato `<via> on|off`. Na prática, o dono pode pedir para desligar uma transferência cross-vendor e o estado permanecer ativo.
  Recommendation: Criar um ramo explícito antes da validação de modelo: para nomes da coluna `Via`, aceitar somente `on|off`, atualizar `Estado` e confirmar o efeito. Remover ou redefinir `codex xhigh` e exigir que os consumidores recusem vias inativas.
- [high] A transição permite rebaixar cards de alto risco (orq/commands/implement-next.md:29-30)
  A frase exata é: “Se o plano aprovado fechou o desenho e a faixa ainda diz `pesada`, rebaixe-a”. Ela não preserva o piso de alto risco e contradiz a régua canônica em `orq/commands/elenco.md:53-54`, onde “O card é Alto risco ... → pesada” vem antes de qualquer outra condição. Uma migração de schema ou mudança de segurança com plano fechado pode, portanto, cair em `normal` ou `leve` e ser entregue ao implementer mais fraco.
  Recommendation: Qualificar a transição: só rebaixar quando `pesada` decorreu exclusivamente de desenho aberto; cards classificados como Alto risco permanecem `pesada` mesmo após o gate.
- [high] A migração não converte inequivocamente os presets legados (orq/commands/elenco.md:138-175)
  A migração diz “linha `planner` única → as duas trilhas” e “linha `implementer` única → as três faixas”, mas não determina explicitamente que essa expansão deve ocorrer também dentro de cada preset legado. Depois, o mesmo arquivo afirma que “Os presets têm 8 linhas ...; a tabela do host tem 9”. Um `_elenco.md` anterior, com presets de cinco linhas, pode ter apenas a antiga tabela `## Papéis` convertida e conservar presets incompatíveis; ao executar `perfil economia`, esses presets reescrevem a tabela do host com papéis ausentes ou eixos colapsados.
  Recommendation: Definir uma migração por seção: expandir e validar todas as tabelas de cada preset para as oito linhas exatas, além da tabela ativa de nove linhas. Se já existir `### Host Claude`, exigir reconciliação linha a linha no diff do gate, sem regra implícita de sobrescrita.
- [medium] A máscara de cercas ainda aceita headings falsos (orq/scripts/lint-coerencia.py:53-68)
  A implementação só alterna o estado quando a linha começa com três crases: `linha.lstrip().startswith("```")`. Ela ignora cercas `~~~` e não respeita o caractere nem o comprimento da cerca de abertura. Probes sintéticos retornaram uma seção tanto para um `### Host Codex` dentro de `~~~markdown` quanto para um heading exposto após ` ````markdown ` seguido de uma cerca curta ` ``` `. Logo, uma tabela presente apenas em exemplo cercado pode satisfazer as novas guardas e deixar o lint verde sem seção ativa real.
  Recommendation: Implementar reconhecimento CommonMark de cercas: crases ou tils, comprimento mínimo três e fechamento com mesmo caractere e comprimento suficiente. Adicionar probes negativos para `~~~` e para cercas aninhadas/de comprimentos diferentes.

Next steps:
- Corrigir os quatro bloqueadores e repetir os dois validadores obrigatórios.
- Adicionar probes comportamentais para toggles de vias, migração de presets legados, piso de alto risco e cercas Markdown.
- Submeter nova rodada adversarial sobre o diff corrigido.
```

---

## Rodada 4

<sub>sha256(saída bruta, 16): `1b528d574cfdfa99` · origem: `review4-t051.txt`</sub>

```
# Codex Adversarial Review

Target: branch diff against main
Verdict: needs-attention

REPROVADO — 5 bloqueadores. Os gates obrigatórios passam, mas não detectam estas contradições semânticas e a falsa interpretação CommonMark.

Findings:
- [high] 1. A wiki ainda permite rebaixar cards de Alto risco (memory/wiki/_elenco.md:25-27)
  `memory/wiki/_elenco.md:25-27` afirma: “Reavaliada no gate: plano fechado rebaixa a faixa.” Isso contradiz diretamente o piso canônico de `orq/commands/elenco.md:65-70`, segundo o qual Alto risco nunca deixa `pesada`. A nota do preset repete a redução em `memory/wiki/_elenco.md:255-256`, associando `pesada` apenas a desenho aberto. Cenário: ao retomar pela wiki, o Manager aprova o plano de uma mudança de schema ou segurança e a rebaixa, selecionando um implementer mais fraco apesar do risco permanecer alto.
  Recommendation: Declarar explicitamente na síntese e na nota do preset que somente `pesada` originada por desenho aberto pode rebaixar; Alto risco mantém o piso mesmo com desenho fechado.
- [high] 2. O exemplo canônico de roteamento viola o contrato no host Codex (orq/skills/orq/SKILL.md:54-55)
  A skill manda anunciar: “implemento com o Sonnet e mando revisar pelo GPT — vendor oposto ao meu.” No host Codex, Sonnet seria escrita cross-vendor, proibida pelo elenco, enquanto GPT pertence ao mesmo vendor do host e não pode ser o revisor independente. Cenário: uma tarefa `sistema · normal` iniciada no Codex segue justamente o exemplo apresentado no ponto de roteamento e escolhe os dois executores errados.
  Recommendation: Substituir modelos concretos por papéis resolvidos após identificar o host, ou fornecer exemplos separados e explicitamente rotulados para Claude e Codex.
- [high] 3. O ramo de via aceita uma via que não é cross-vendor para o host atual (orq/commands/elenco.md:112-126)
  O ramo compara qualquer primeiro token com a coluna `Via`, termina antes da validação e depois instrui: “desligar a via do vendor oposto ao host deixa o projeto sem revisor independente”. No host Codex, porém, `codex off` é aceito e altera a via OpenAI global, embora o revisor daquele host use `runner-opus`. O README também promete sem qualificação que `codex off` “fica sem revisor independente”. Cenário: executado no Codex, o comando afeta sessões Claude, mas não desliga o revisor Opus atual; o usuário recebe uma consequência ambígua ou falsa.
  Recommendation: Mapear cada via ao vendor e aos hosts consumidores antes de gravar. Informar exatamente quais hosts e papéis serão afetados, ou recusar a alteração de uma via que não seja cross-vendor para o host atual. Qualificar os exemplos do README.
- [high] 4. O init ignora a migração por seção definida pelo elenco (orq/commands/init.md:255-258)
  Para `_elenco.md` existente, o init diz apenas: “preserve modelos/perfis/vias escolhidos e acrescente somente headings obrigatórias ausentes”. Ele não manda converter todas as tabelas de 5 para 8/9 linhas, remover `## Papéis` nem reconciliar linha a linha quando `### Host Claude` já existe, como exige `orq/commands/elenco.md:167-203`. Cenário: reinstalar sobre arquivo pré-0.24 adiciona `## Times por host`, mas deixa presets antigos e duas fontes divergentes; consumidores novos passam a ignorar escolhas preservadas em `## Papéis`.
  Recommendation: Antes de acrescentar headings, encaminhar explicitamente para a migração canônica do elenco: converter tabela ativa e cada preset, validar 8/9 linhas, reconciliar conflitos e parar no gate.
- [high] 5. A máscara de cercas aceita indentação que CommonMark não aceita (orq/scripts/lint-coerencia.py:53-84)
  A regex `^[ \t]*(`{3,}|~{3,})(.*)$` permite indentação ilimitada, embora o comentário declare comportamento CommonMark. Um probe com uma linha `    ``` ` entre duas headings reais `## Times por host` retornou `headings_reais=2` e `secoes_vistas_pelo_lint=1`. Em CommonMark, quatro espaços formam bloco indentado, não abertura de cerca. Assim, uma duplicata real posterior pode ser mascarada e o lint ficar verde.
  Recommendation: Aceitar no máximo três espaços antes das cercas de abertura e fechamento. Adicionar probes regressivos para 0–3 espaços, quatro espaços, tabs, tis e fechamentos menores/maiores.

Next steps:
- Corrigir os cinco bloqueadores e acrescentar probes para host Codex, migração legada e indentação de cercas.
- Reexecutar `claude plugin validate ./orq --strict` e `python3 orq/scripts/lint-coerencia.py .`.
- Fazer nova rodada adversarial; os gates atuais passaram mesmo com estes defeitos.
```

---

## Rodada 5

<sub>sha256(saída bruta, 16): `b48ff8a0800a89d3` · origem: `review5-t051.txt`</sub>

```
# Codex Adversarial Review

Target: branch diff against main
Verdict: needs-attention

REPROVADO — restam 2 BLOQUEADORES funcionais, não simples riscos de prosa. Os validadores oficiais passam, mas o novo guarda aceita uma tabela inválida e o ajuste de elenco pode registrar um modelo que o runner substitui silenciosamente por Opus.

Findings:
- [high] BLOQUEADOR — o guarda aceita papel ausente quando seu nome aparece na prosa (orq/scripts/lint-coerencia.py:508-523)
  Frase exata: `if papel_eixo not in secao`. A presença é procurada na seção inteira; as linhas da tabela são usadas apenas para contar. Em probe real, substituí a linha `implementer·leve` do Host Claude por `auditor`, preservei 9 linhas e mencionei `implementer·leve` numa nota fora da tabela: o lint terminou com exit 0. Assim, um template sem uma faixa obrigatória pode passar pelos dois validadores e gerar elencos inválidos.
  Recommendation: Extraia exatamente a primeira célula de cada linha da tabela e compare o conjunto/multiplicidade esperado: cada papel obrigatório uma vez, nenhum papel intruso e `manager` como célula exata. Adicione o probe como regressão.
- [high] BLOQUEADOR — o Codex pode registrar Fable/Sonnet, mas executar Opus (orq/commands/elenco.md:145-154)
  Frase exata: `papel read-only (...) qualquer vendor com célula na ## Matriz de invocação`. No Host Codex, qualquer modelo Anthropic satisfaz essa regra, inclusive o exemplo documentado `planner interface fable`. Porém a célula Anthropic×Codex usa `run-opus-reviewer.py`, e esse runner chama invariavelmente `--model opus` e exige `claude-opus-5`. Cenário concreto: o comando grava Fable como planner, mas o próximo Loop A executa Opus; o elenco declarado e o modelo efetivo divergem silenciosamente. O mesmo vale para `reviewer` ou outro modelo Anthropic.
  Recommendation: Valide modelo e mecanismo, não apenas vendor. Enquanto o runner for exclusivo de Opus 5, aceite no Anthropic×Codex somente `opus`/IDs comprovadamente equivalentes; alternativamente, torne o runner parametrizável e verifique que o modelo executado é exatamente o registrado.

Next steps:
- Corrigir os dois bloqueadores e adicionar probes de regressão.
- Reexecutar `claude plugin validate ./orq --strict` e `python3 orq/scripts/lint-coerencia.py .`; ambos passaram nesta rodada, mas não detectam os cenários acima.
```

---

## Rodada 6

<sub>sha256(saída bruta, 16): `fc65f0c1a79324de` · origem: `review6-t051.txt`</sub>

```
# Codex Adversarial Review

Target: branch diff against main
Verdict: needs-attention

REPROVADO: 1 bloqueador funcional e 1 risco. Manifesto e lint passam, mas não detectam essas inconsistências.

Findings:
- [high] BLOQUEADOR — `scout` recebe políticas incompatíveis de vendor (orq/commands/elenco.md:152-170)
  A frase exata é: “papel read-only (`planner`, `reviewer`, `scout`): qualquer vendor”. Isso obriga aceitar, por exemplo, `scout gpt-5.6-sol` no host Claude. Porém a via `codex` declara em `Consumida por` somente `planner·sistema` e `reviewer` (linhas 331-336), enquanto `memory/wiki/_elenco.md:135` afirma “Docs e scout seguem o vendor do host”. Cenário concreto: configure o scout cross-vendor e depois execute `codex off`; o comando deriva o efeito exclusivamente de `Consumida por`, omite o scout, e o `/orq:init` despacha scouts sem verificar o estado da via. O resultado pode ser transferência por uma via desligada pelo dono ou falha sem degradação prevista.
  Recommendation: Escolher uma regra única. Se scout deve permanecer no vendor do host, removê-lo da permissão cross-vendor e recusar o ajuste. Se deve cruzar vendor, atualizar `Consumida por` quando o papel mudar, exigir Estado/capacidade em todo consumidor de scout e alinhar `_elenco.md` e a seção de custo. Adicionar probe `scout cross-vendor → via off → despacho bloqueado`.
- [medium] RISCO — guarda de versão aceita dois blocos `## Status` conflitantes (orq/scripts/lint-coerencia.py:281-284)
  O helper documenta que heading duplicado é ambíguo e deve reprovar, mas o consumidor faz `"\n".join(trechos)`. A sonda com um primeiro `## Status` em 0.23.0 e um segundo em 0.24.0 retornou `sections=2`, `guard_passes=True` e `first_is_stale=True`. Assim, o lint fica verde enquanto o bloco lido primeiro pelo usuário anuncia versão antiga.
  Recommendation: Exigir exatamente um `## Status`: zero usa o fallback declarado; mais de um deve falhar por ambiguidade; somente um pode ser validado. Aplicar a mesma regra de unicidade aos demais chamadores de `secoes_de`.

Next steps:
- Corrigir a política de `scout` e sua relação com as vias cross-vendor.
- Endurecer a multiplicidade das headings no lint.
- Reexecutar `claude plugin validate ./orq --strict`, `python3 orq/scripts/lint-coerencia.py .` e os probes negativos.
```

---

## Rodada 7

<sub>sha256(saída bruta, 16): `bc800562a7d91255` · origem: `review7-t051.txt`</sub>

```
# Codex Adversarial Review

Target: branch diff against main
Verdict: approve

APROVADO. Nenhuma regressão material nas duas correções: o scout permanece no vendor do host em todas as superfícies, não aparece em `Consumida por` nem no impacto de `codex off`, e os quatro chamadores tratam ausência/duplicidade sem falso positivo legítimo identificado. Lint e validação estrita passaram.

No material findings.

Next steps:
- Prosseguir para a validação comportamental pós-release exigida pelo projeto.
```

---

## Smoke do `gpt-5.6-luna` (2026-09-01)

<sub>sha256: `aef5dbc7c9e4744d`</sub>

```
[codex] Starting Codex task thread.
[codex] Thread ready (01a05e0d-309c-7a92-839c-09f6c418a974).
[codex] Turn started (01a05e0d-38be-7aa3-a1a2-1e22c0fa4671).
[codex] Assistant message captured: LUNA_OK
[codex] Turn completion inferred after the main thread finished and subagent work drained.
LUNA_OK
```

**Comprovou:** o modelo existe, está autenticado e responde a `--model gpt-5.6-luna`.
**Não comprovou:** efforts aceitos, nem comportamento em `-s workspace-write` — o smoke foi read-only.
