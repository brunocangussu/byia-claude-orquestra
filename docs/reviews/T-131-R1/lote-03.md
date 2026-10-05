Revisão independente T-131, R1, somente texto/diff. READ-ONLY; nenhuma ferramenta, arquivo, delegação ou pesquisa. O produto são instruções: procure ambiguidade, contradição e comando inexistente com cenário concreto. Objetivo aprovado: Fable ativo -> Opus5.5; ID explícito claude-opus-5-5 exige igualdade, aliases opus/fable/sonnet/haiku conservam prefixo legado e fable não vira Opus. Catálogo passa a oferecer Sol6/Luna6, mas as sondas desta CLI/conta ChatGPT recusaram ambos: não ativar sem prova modelo+via+conta/host, nem fallback. Elenco do projeto mantém Astra/Terra; catálogo de fábrica não é elenco ativo. Nenhum bump/cache/commit/install/restart nesta fase. Lint cache divergente conhecido é gate de release, não defeito novo. Audite somente mudanças deste lote, não atribua cobertura aos outros. Defeitos antigos fora do diff não bloqueiam esta migração salvo regressão introduzida. Formato obrigatório: ## BLOQUEADORES; ## RISCOS; ## VEREDITO (APROVADO | APROVADO_COM_RESSALVAS | REPROVADO). Cada achado arquivo:linha, entrada -> erro, correção mínima. Se nenhum, diga nenhum. Não invente problema de estilo.

LOTE 3/5. Sem acesso ao repositório; cada hunk tem coordenadas Git. Snapshot local, nenhuma instalação ou integração.

diff --git a/README.md b/README.md
index d99c627..8bc4705 100644
--- a/README.md
+++ b/README.md
@@ -172,7 +172,7 @@ arquivo do agente é só o padrão de fábrica.
 
 ```bash
 /orq:elenco                    # mostra a escalação atual
-/orq:elenco planner interface fable   # host Claude — Fable 5.1; no Codex esta trilha hoje é gpt-6-astra@max
+/orq:elenco planner interface claude-opus-5-5 # host Claude — ID explícito; no Codex esta trilha hoje é gpt-6-astra@max
 /orq:elenco implementer leve haiku    # troca o degrau barato de quem escreve
 /orq:elenco codex off                 # no host Claude: fica sem revisor independente
 /orq:elenco reviewer gpt-6-astra@high # o effort mora no modelo do papel, não na via
@@ -180,7 +180,7 @@ arquivo do agente é só o padrão de fábrica.
 /orq:elenco perfil padrao      # crédito voltou: time titular de volta
 ```
 
-Ou simplesmente fale: *"quero o Fable planejando"* · *"tira o GPT da revisão"* · *"quem tá revisando?"*
+Ou simplesmente fale: *"quero o Fable planejando"* (override legado) · *"tira o GPT da revisão"* · *"quem tá revisando?"*
 
 **Perfis** — além do ajuste papel a papel, o `_elenco.md` pode ter **times nomeados** (seção
 "Perfis"): `padrao` (o titular) e `economia` (crédito Claude curto). Presets são **por host**:
@@ -197,7 +197,7 @@ tabela ativa; o host Codex tem a sua, com os modelos OpenAI equivalentes.
 | Papel | Modelo | Por quê |
 |---|---|---|
 | `manager` | *sessão principal* | definido pelo `/model` — não é spawn, não muda por aqui |
-| `planner·interface` | `fable` | trilha perceptual pensa com Anthropic — Fable 5.1 |
+| `planner·interface` | `claude-opus-5-5` | trilha perceptual usa o ID Anthropic explícito |
 | `planner·sistema` | `gpt-6-astra@max` | trilha comportamental pensa com OpenAI, read-only por CLI |
 | `implementer·pesada` | `opus` | alto risco ou decisão de desenho ainda aberta |
 | `implementer·normal` | `sonnet` | plano fechado, execução dirigida |
@@ -217,11 +217,22 @@ réguas ficam escritas uma única vez, em `orq/commands/elenco.md`.
 **independência** (e ele é obrigado: sempre o vendor oposto ao host). `implementer`, `docs` e
 `scout` ficam no vendor do host: os dois primeiros porque escrevem, o `scout` porque leitura ampla
 e barata não se paga em domínio. Valores aceitos nesses três dependem do host: no Claude, `opus` ·
-`sonnet` · `haiku` · `fable` · `inherit` ou um id (`claude-opus-5`); no Codex, os modelos OpenAI
-com effort (`gpt-5.6-terra@xhigh`…). Nos que cruzam, qualquer vendor com célula na Matriz de
+`sonnet` · `haiku` · `fable` · `inherit`, o alias legado `opus`, ou o id explícito
+`claude-opus-5-5`; **neste projeto**, `gpt-5.6-terra@xhigh` é o degrau ativo. `gpt-6-sol` e
+`gpt-6-luna` são apenas candidatos da **proposta global de fábrica**, pendentes de capacidade;
+não tornam Terra o default universal nem alteram o elenco do projeto. Nos que cruzam, qualquer vendor com célula na Matriz de
 invocação, **desde que o mecanismo daquela célula execute aquele modelo** (a célula Anthropic×Codex
-é o runner Anthropic parametrizado por `--model <alias>`, que só aceita os aliases do mapa de prova
-— `opus`·`fable`·`sonnet`·`haiku` — e valida o prefixo do modelo antes de aceitar a saída).
+é o runner parametrizado por `--model <alias-ou-id>`, que aceita `claude-opus-5-5` e os aliases
+legados `opus`·`fable`·`sonnet`·`haiku` e exige igualdade para o ID explícito ou prefixo para alias
+legado antes de aceitar a saída).
+
+**Gate de capacidade — perfil, ajuste papel a papel ou inicialização de elenco novo:** antes de
+mudar modelo, exija **prova válida de capacidade para modelo + via + conta/host**. Catálogo,
+documentação, template e nome de preset não provam acesso. Recusa ou ausência de prova **preserva o
+elenco ativo inteiro**, sem troca parcial: não grave a tabela nem acione fallback e informe a
+limitação daquela via/conta; se ele não existe, pare e peça ao dono uma escolha entre opções
+comprovadas, sem criar elenco inoperante. Não conclua incapacidade global de API/App nem dispare nova
+sonda.
 
 **Onde modelo forte se paga:** planner e reviewer. Um erro de plano custa a implementação inteira;
 um review fraco deixa passar o que vai quebrar depois. Docs e scout resolvem com modelo menor.
@@ -235,7 +246,7 @@ mesmo e declara a ausência. Não existe cair num revisor do mesmo fornecedor do
 ## Revisão independente
 
 Um revisor só, **sempre do fornecedor oposto ao do host**: no host Claude quem revisa é o GPT, no
-host Codex é o modelo Anthropic do elenco (hoje `fable`, Fable 5.1). A razão de existir do revisor é
+host Codex é o modelo Anthropic do elenco (hoje `claude-opus-5-5`). A razão de existir do revisor é
 ser independente de quem escreveu — um revisor do mesmo fornecedor devolveria a aparência de revisão
 sem a independência que a justifica.
 
@@ -258,14 +269,14 @@ capacidade** das vias cross-vendor, não uma composição de painel:
 | Via | Vendor | Consumida por | Estado | Registro |
 |---|---|---|---|---|
 | codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex não é via — é o vendor nativo | ativo | `--model gpt-6-astra --effort max` (read-only) |
-| runner-opus | Anthropic | **host Codex**: `reviewer`. No host Claude não é via — é o vendor nativo | ativo | `scripts/run-opus-reviewer.py --model <alias>` · comprova o prefixo do alias pedido (hoje `fable` → `claude-fable-5-1`) · 16 KiB/lote · 600s |
+| runner-opus | Anthropic | **host Codex**: `reviewer`. No host Claude não é via — é o vendor nativo | ativo | `scripts/run-opus-reviewer.py --model <alias-ou-id>` · igualdade para `claude-opus-5-5`, prefixo para aliases legados · 16 KiB/lote · 600s |
 ```
 
 Aqui, ativo significa política habilitada, não saúde de runtime: CLI, autenticação, modelo e saída
 são verificados a cada parecer. O modelo Anthropic escolhido roda por
-`orq/scripts/run-opus-reviewer.py --model <alias>`: briefings acima de 16 KiB são divididos por
-arquivo/hunk sem truncamento; cada lote tem timeout e só vale se o JSON comprovar o prefixo do alias
-pedido (hoje, `fable` exige `claude-fable-5-1`).
+`orq/scripts/run-opus-reviewer.py --model <alias-ou-id>`: briefings acima de 16 KiB são divididos
+por arquivo/hunk sem truncamento; cada lote tem timeout e só vale se o JSON comprovar a identidade
+exata pedida (hoje, `claude-opus-5-5`) ou o prefixo esperado para um alias legado.
 
 **Capacidade ausente não vira substituição.** Titular fora do ar (binário, autenticação, timeout,
 saída vazia) → **REVISÃO DEGRADADA** com a causa nomeada, e o card não avança sozinho. Diff com dado
@@ -431,8 +442,9 @@ Codex, a partir da mesma fonte já registrada no Claude (`T-026`, passos 1–4)
 host-agnóstico** (`T-026`, passo 8): `## Times por host` resolve o time de cada host na leitura,
 sem preset ativável; `## Matriz de invocação` documenta o template por vendor × host com
 procedência; o template do `init` gera as duas seções e migra arquivo antigo de forma aditiva;
-consumidores resolvem host→papel→executor; no Codex, Manager Sol/high, Planner Astra/max (nas duas
-trilhas), Implementer Terra/xhigh e revisor Anthropic pelo alias do elenco (hoje `fable`, Fable 5.1);
+consumidores resolvem host→papel→executor; no Codex, Manager Astra/max (escolha declarada do dono),
+Planner Astra/max (nas duas trilhas), **no elenco deste projeto** Implementer Terra/xhigh e revisor Anthropic pelo ID explícito
+do elenco (hoje `claude-opus-5-5`);
 diagnóstico separa plugin instalado/habilitado,
 skill carregada e smoke comportamental ·
 **contratos de contexto para Claude Code e Codex** (`T-043`): no Codex, hooks empacotados observam a telemetria por

diff --git a/orq/commands/elenco.md b/orq/commands/elenco.md
index bd30473..0d00436 100644
--- a/orq/commands/elenco.md
+++ b/orq/commands/elenco.md
@@ -356,7 +370,7 @@ vendor oposto, com o que já foi comprovado e quando. O nome na coluna **Via** 
 | Via | Vendor | Consumida por | Estado | Registro |
 |---|---|---|---|---|
 | codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex **não é via** — é o vendor nativo | ativo | subagente `codex:codex-rescue` → `codex-companion.mjs task`; modelo e effort vêm da tabela, e `jobId` + `threadId` sustentam o reúso exato |
-| runner-opus | Anthropic | **host Codex**: `reviewer`. No host Claude **não é via** — é o vendor nativo | ativo | runner Anthropic `scripts/run-opus-reviewer.py --model <alias>` · comprova o prefixo do alias pedido · 16 KiB por lote · timeout 600s |
+| runner-opus | Anthropic | **host Codex**: `reviewer`. No host Claude **não é via** — é o vendor nativo | ativo | runner Anthropic `scripts/run-opus-reviewer.py --model <alias-ou-id>` · igualdade para `claude-opus-5-5`, prefixo para aliases legados · 16 KiB por lote · timeout 600s |
 
 A coluna **Consumida por** é o que torna o efeito de ligar/desligar anunciável sem chute: uma via só
 afeta os papéis listados, nos hosts listados. Via cujo vendor é o do próprio host não é via nenhuma
@@ -382,7 +396,7 @@ nunca leva dado de paciente, PII, prontuário ou credencial.
 
 | Vendor do modelo | Host Claude | Host Codex |
 |---|---|---|
-| Anthropic | spawn nativo com override | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias>` — limite 16 KiB/lote, timeout e comprovação do prefixo do alias pedido no `modelUsage`; alias fora do mapa de prova (`opus`·`fable`·`sonnet`·`haiku`) é recusado antes da chamada |
+| Anthropic | spawn nativo com override | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias-ou-id>` — limite 16 KiB/lote, timeout e igualdade para `claude-opus-5-5` ou prefixo para alias legado no `modelUsage`; aceita `claude-opus-5-5` e os aliases legados `opus`·`fable`·`sonnet`·`haiku`, recusando opção fora do mapa antes da chamada |
 | OpenAI | **OpenAI × host Claude:** subagente `codex:codex-rescue` → `codex-companion.mjs task --model <modelo> --effort <effort>`; primeira chamada por `card+papel` usa `--fresh --json`, continuação usa `--resume-thread <threadId> --json`; briefing declara read-only, e o handoff persiste `rawOutput`, `jobId`, `threadId` e `status` | **Host Codex: `codex exec` é obrigatório**; primitiva nativa só quando `_elenco.md` registrar override comprovado por chamada real |
 
 ⚠️ **Nunca acrescente `--write`.** O read-only desta chamada vem da ausência dessa flag: com ela, o sandbox do Companion vira `workspace-write` e o papel deixa de ser read-only.
@@ -401,7 +415,7 @@ perfil os toca, e aplicar um preset **preserva a linha `manager` e a seção "Re
 
 | Papel | Modelo | Por quê |
 |---|---|---|
-| planner·interface | fable | trilha perceptual pensa com Anthropic — Fable 5.1 |
+| planner·interface | claude-opus-5-5 | trilha perceptual usa o ID Anthropic explícito |
 | planner·sistema | gpt-6-astra@xhigh | trilha comportamental pensa com OpenAI |
 | implementer·pesada | opus | alto risco ou decisão de desenho ainda aberta |
 | implementer·normal | sonnet | plano fechado, execução dirigida |
@@ -411,13 +425,13 @@ perfil os toca, e aplicar um preset **preserva a linha `manager` e a seção "Re
 | scout | sonnet | leitura ampla e barata |
 
 Revisores externos: via `codex` ativa · via `runner-opus` ativa — estado de fábrica, informativo: o
-perfil não aplica isto (ver passo 2 de "Com argumento `perfil <nome>`"), vale o que está registrado.
+perfil não aplica isto (ver passo 3 de "Com argumento `perfil <nome>`"), vale o que está registrado.
 
 ### `economia` — crédito curto
 
 | Papel | Modelo | Por quê |
 |---|---|---|
-| planner·interface | opus | um planner só de Anthropic, sem o degrau extra de raciocínio |
+| planner·interface | claude-opus-5-5 | mesmo modelo do padrão; economia não promete rebaixamento inexistente neste papel |
 | planner·sistema | gpt-6-astra@high | effort rebaixado dentro do mesmo vendor |
 | implementer·pesada | sonnet | rebaixado um degrau — evita herdar o modelo caro da sessão |
 | implementer·normal | sonnet | já era o degrau econômico |
@@ -427,7 +441,7 @@ perfil não aplica isto (ver passo 2 de "Com argumento `perfil <nome>`"), vale o
 | scout | haiku | leitura ampla e barata |
 
 Revisores externos: via `codex` ativa · via `runner-opus` ativa — mesmo estado de fábrica do preset
-`padrao`, também informativo, não aplicado pelo perfil (ver passo 2 acima). Quem decide o briefing
+`padrao`, também informativo, não aplicado pelo perfil (ver passo 3 acima). Quem decide o briefing
 enxuto do `--rapido` é o `/orq:revisar` — regra lá.
 
 **O que se perde — registre com todas as letras ao criar este perfil neste projeto:** o parecer

