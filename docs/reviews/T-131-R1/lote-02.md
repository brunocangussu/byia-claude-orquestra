Revisão independente T-131, R1, somente texto/diff. READ-ONLY; nenhuma ferramenta, arquivo, delegação ou pesquisa. O produto são instruções: procure ambiguidade, contradição e comando inexistente com cenário concreto. Objetivo aprovado: Fable ativo -> Opus5.5; ID explícito claude-opus-5-5 exige igualdade, aliases opus/fable/sonnet/haiku conservam prefixo legado e fable não vira Opus. Catálogo passa a oferecer Sol6/Luna6, mas as sondas desta CLI/conta ChatGPT recusaram ambos: não ativar sem prova modelo+via+conta/host, nem fallback. Elenco do projeto mantém Astra/Terra; catálogo de fábrica não é elenco ativo. Nenhum bump/cache/commit/install/restart nesta fase. Lint cache divergente conhecido é gate de release, não defeito novo. Audite somente mudanças deste lote, não atribua cobertura aos outros. Defeitos antigos fora do diff não bloqueiam esta migração salvo regressão introduzida. Formato obrigatório: ## BLOQUEADORES; ## RISCOS; ## VEREDITO (APROVADO | APROVADO_COM_RESSALVAS | REPROVADO). Cada achado arquivo:linha, entrada -> erro, correção mínima. Se nenhum, diga nenhum. Não invente problema de estilo.

LOTE 2/5. Sem acesso ao repositório; cada hunk tem coordenadas Git. Snapshot local, nenhuma instalação ou integração.

diff --git a/memory/wiki/_elenco.md b/memory/wiki/_elenco.md
index 15b63db..20933ff 100644
--- a/memory/wiki/_elenco.md
+++ b/memory/wiki/_elenco.md
@@ -3,7 +3,7 @@
 > **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
 > O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste papel a papel com
 > `/orq:elenco <papel> <modelo>`, ou troque o **time inteiro** com `/orq:elenco perfil <nome>` —
-> ou fale naturalmente: *"quero o Fable planejando"*, *"tô com pouco crédito"*, *"modo economia"*.
+> ou fale naturalmente: *"quero o Fable planejando"* (override legado), *"tô com pouco crédito"*, *"modo economia"*.
 
 > **Onde o modelo é resolvido — a única frase normativa:** identifique o host, leia a tabela DELE
 > em `## Times por host`, e aplique a célula da `## Matriz de invocação`. **Não existe outra tabela
@@ -39,8 +39,10 @@ réguas") — aqui ela é resumida, não redefinida.
 independência, e obrigatoriamente do vendor oposto). Aceitam qualquer vendor com célula na
 `## Matriz de invocação`, **desde que o mecanismo daquela célula execute aquele modelo** — a
 célula Anthropic×Codex é o runner Anthropic parametrizado por `--model <alias>`: só entra alias
-presente no mapa de prova do runner (`opus`·`fable`·`sonnet`·`haiku`), com o prefixo daquele alias
-comprovado no `modelUsage` antes de virar parecer. **`implementer`, `docs`
+presente no mapa de prova do runner (`claude-opus-5-5` e os aliases legados
+`opus`·`fable`·`sonnet`·`haiku`), com igualdade para o ID explícito 5.5 e prefixo para aliases
+legados comprovados no `modelUsage`
+antes de virar parecer. **`implementer`, `docs`
 e `scout` ficam no vendor do host**: os dois primeiros porque escrevem; o `scout` porque leitura
 ampla e barata não compra aptidão de domínio e ainda pagaria transferência para terceiro.
 Scout cross-vendor é recusa com motivo. A metade de **escrita** cross-vendor do `T-021` segue fora do
@@ -65,7 +67,7 @@ Regras, cada uma escrita 1×:
 | Via | Vendor | Consumida por | Estado | Registro |
 |---|---|---|---|---|
 | codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex não é via — é o vendor nativo | **ativo** | subagente `codex:codex-rescue` → `codex-companion.mjs task` · modelo `gpt-6-astra` @ `max` · `jobId` + `threadId` sustentam o reúso exato · ver **Matriz de invocação** |
-| runner-opus | Anthropic | **host Codex**: `reviewer`. No host Claude não é via — é o vendor nativo | **ativo** | `orq/scripts/run-opus-reviewer.py --model <alias>` · comprova o prefixo do alias pedido · 16 KiB por lote · timeout 600s · sonda real com `--model fable` em 2026-09-05 comprovou `claude-fable-5-1` (thread `T-079`) |
+| runner-opus | Anthropic | **host Codex**: `reviewer`. No host Claude não é via — é o vendor nativo | **ativo** | `orq/scripts/run-opus-reviewer.py --model <alias-ou-id>` · igualdade para `claude-opus-5-5`, prefixo para alias legado · 16 KiB por lote · timeout 600s · registro histórico: sonda real com `--model fable` em 2026-09-05 comprovou `claude-fable-5-1` (thread `T-079`) |
 
 A coluna **Consumida por** existe para o efeito de ligar/desligar ser anunciável sem chute: a via
 só afeta os papéis listados, nos hosts listados.
@@ -121,7 +123,7 @@ uma vez, não repetido) · `não testado`.
 
 | Vendor do modelo | host Claude | host Codex |
 |---|---|---|
-| **Anthropic** | spawn nativo (Task + `model:`) — comprovado | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias>` — aliases `opus`·`fable`·`sonnet`·`haiku`, **prova o prefixo do alias pedido** (pedir `fable` e receber Opus, ou receber `claude-fable-5-0`, reprova com exit 7), limita 16 KiB/lote e aplica timeout. `opus` comprovado em 2026-08-09; `fable` habilitado no `T-077` (2026-09-04) e **comprovado com chamada real em 2026-09-05** (`OPUS_MODEL=claude-fable-5-1`, thread `T-079`) |
+| **Anthropic** | spawn nativo (Task + `model:`) — comprovado | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias-ou-id>` — aceita o ID explícito `claude-opus-5-5` e os aliases legados `opus`·`fable`·`sonnet`·`haiku`; exige **igualdade** para o ID 5.5 (receber `claude-opus-5` ou `claude-opus-5-50` reprova com exit 7) e mantém **prefixo** para aliases legados. Limita 16 KiB/lote e aplica timeout. `opus` comprovado em 2026-08-09; `fable` habilitado no `T-077` (2026-09-04) e **comprovado com chamada real em 2026-09-05** (`OPUS_MODEL=claude-fable-5-1`, thread `T-079`) |
 | **OpenAI** | **OpenAI × host Claude:** subagente `codex:codex-rescue` → `codex-companion.mjs task --model <modelo> --effort <effort>`; primeira chamada por `card+papel` usa `--fresh --json`, continuação usa `--resume-thread <threadId> --json`; persistir `rawOutput`, `jobId`, `threadId` e `status`. O modelo e o effort foram comprovados como revisor; como planner, o Loop A completo ainda é o teste real. Escrita cross-vendor: fora do desenho | a primitiva exposta na sessão não aceita override de modelo/effort; use `codex exec` com modelo, effort e sandbox explícitos |
 
 ⚠️ **Nunca acrescente `--write`.** O read-only desta chamada vem da ausência dessa flag: com ela, o sandbox do Companion vira `workspace-write` e o papel deixa de ser read-only.
@@ -139,9 +141,9 @@ time da outra.
    (pode cruzar vendor, é read-only); `implementer` e `docs` ficam no vendor do host.
 2. **O `reviewer` é único e sempre do vendor oposto ao host** — sem contingência interna, sem
    exceção. Ausência se declara, não se substitui.
-3. **A comprovação do alias do runner Anthropic** (que ele resolve para o prefixo esperado — `opus`
-   para `claude-opus-5`, `fable` para `claude-fable-5-1`) é obrigatória antes de todo parecer que
-   dependa dele; sem comprovação, trate como ausente e não troque de modelo.
+3. **A comprovação da opção do runner Anthropic** é obrigatória antes de todo parecer que dependa
+   dele: `claude-opus-5-5` exige essa identidade exata no `modelUsage`; aliases legados conservam
+   a prova por prefixo correspondente. Sem comprovação, trate como ausente e não troque de modelo.
 4. **Docs e scout seguem o vendor do host**, no degrau barato — leitura/escrita objetiva não se
    paga em domínio.
 
@@ -150,7 +152,7 @@ time da outra.
 | Papel | Modelo | Por quê |
 |---|---|---|
 | manager | modelo da sessão (`/model`) | sessão principal; **sempre escolha do dono**, em qualquer host |
-| planner·interface | `fable` | spawn nativo, read-only — Fable 5.1 (id `claude-fable-5-1`), comprovado |
+| planner·interface | `claude-opus-5-5` | spawn nativo, read-only — ID explícito; capacidade confirmada no uso |
 | planner·sistema | `gpt-6-astra@xhigh` | Codex Companion read-only; task fresca por card+papel e retomada pelo `threadId` exato |
 | implementer·pesada | `sonnet` | worktree dedicado, writer único |
 | implementer·normal | `sonnet` | worktree dedicado, writer único |
@@ -185,13 +187,13 @@ Motor: a sessão Codex. A linha `manager` é expectativa verificável, não coma
 
 | Papel | Modelo | Por quê |
 |---|---|---|
-| manager | modelo da sessão (`/model`) | sessão principal; **sempre escolha do dono** — verificar o modelo real antes de anunciar |
+| manager | `gpt-6-astra@max` | decisão declarada do dono; verificar o modelo real antes de anunciar, sem troca silenciosa |
 | planner·interface | `gpt-6-astra@max` | decisão do dono em 2026-09-05 (`T-079`); `max` comprovado no `codex exec` em 2026-09-07 (`T-083`), read-only |
 | planner·sistema | `gpt-6-astra@max` | mesma prova do `T-083`; read-only |
 | implementer·pesada | `gpt-5.6-terra@xhigh` | `workspace-write`, writer único em worktree |
 | implementer·normal | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-08-09; writer único em worktree |
 | implementer·leve | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-09-03: as três faixas no mesmo modelo. O smoke do `gpt-5.6-luna` fica no histórico, mas o degrau não o usa mais |
-| reviewer | `opus` | vendor oposto ao host; runner Anthropic, read-only, sem ferramentas. Invocar com `--model opus`; a prova exige o prefixo `claude-opus-5` no `modelUsage`, comprovado em 2026-08-09 |
+| reviewer | `claude-opus-5-5` | vendor oposto ao host; runner Anthropic, read-only, sem ferramentas. Invocar com `--model claude-opus-5-5`; a prova exige essa identidade exata no `modelUsage` antes de aceitar parecer |
 | docs | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-09-03 |
 | scout | `gpt-5.6-terra@xhigh` | decisão do dono em 2026-09-03 |
 
@@ -208,6 +210,13 @@ aplicam aqui: trariam modelos Anthropic para `implementer`/`docs`, que só aceit
 
 ### Pendências comprováveis (não prometer antes de rodar)
 
+- **Sol 6 e Luna 6 no host Codex** — são candidatos, não elenco ativo. Em uma única chamada
+  read-only sintética por `codex exec` 0.153.4, com conta ChatGPT e effort `low`, `gpt-6-sol` e
+  `gpt-6-luna` receberam HTTP 400: o modelo não é suportado ao usar Codex com essa conta. A prova
+  de capacidade para **modelo + via + conta/host** está pendente; isso não declara incapacidade
+  global de API/App. Astra e Terra permanecem ativos. Antes de aplicar perfil que mudaria modelo,
+  ausência ou recusa de prova preserva o elenco ativo inteiro, sem troca parcial, e informa essa
+  limitação.
 - **Astra (`gpt-6-astra`) como planner e reviewer** — o modelo e os efforts `low|medium|high|xhigh|
   max` estão comprovados via CLI Codex. Em 2026-09-07 (`T-083`), a sonda real
   `codex exec -c 'model_reasoning_effort="max"' --model gpt-6-astra --sandbox read-only` anunciou
@@ -248,8 +257,8 @@ nenhum arquivo deste projeto deriva um.
 
 `economia` é perfil de **crédito e esforço**, não garantia de menor custo total: o Astra cai de
 `@max` para `@high` (mesmo modelo, effort menor), `implementer·leve`, `docs` e `scout` usam degraus
-mais baratos, e `planner·interface` continua trocando de Fable 5.1 para Opus — decisão anterior do
-dono, preservada aqui.
+mais baratos. `planner·interface` permanece em `claude-opus-5-5`, igual ao padrão: este perfil não
+promete economia inexistente nesse papel.
 
 ## Perfis — times nomeados por contexto de crédito (host Claude)
 
@@ -278,7 +287,7 @@ o vendor do host acabaria com a única coisa que ele entrega.
 
 | Papel | Modelo | Por quê |
 |---|---|---|
-| planner·interface | fable | trilha perceptual pensa com Anthropic — Fable 5.1 |
+| planner·interface | claude-opus-5-5 | trilha perceptual usa a identidade Anthropic explícita |
 | planner·sistema | gpt-6-astra@xhigh | trilha comportamental pensa com OpenAI |
 | implementer·pesada | sonnet | executar plano já aprovado é trabalho dirigido — reconciliado com a tabela ativa |
 | implementer·normal | sonnet | executar plano já aprovado é trabalho dirigido |
@@ -298,7 +307,7 @@ com o Opus"* — relida para os dois eixos.
 
 | Papel | Modelo | Por quê |
 |---|---|---|
-| planner·interface | opus | escolha verbatim do dono para este contexto |
+| planner·interface | claude-opus-5-5 | mesmo modelo do padrão; economia não promete rebaixamento inexistente neste papel |
 | planner·sistema | gpt-6-astra@high | effort rebaixado dentro do mesmo vendor |
 | implementer·pesada | sonnet | rebaixado um degrau — evita herdar Opus no perfil de economia |
 | implementer·normal | sonnet | já era o econômico |

diff --git a/orq/scripts/run-opus-reviewer.py b/orq/scripts/run-opus-reviewer.py
index 64a13af..b022b63 100644
--- a/orq/scripts/run-opus-reviewer.py
+++ b/orq/scripts/run-opus-reviewer.py
@@ -21,12 +21,14 @@ import time
 
 DEFAULT_MAX_INPUT_BYTES = 16_384
 DEFAULT_TIMEOUT_SECONDS = 600.0
-DEFAULT_MODEL_ALIAS = "opus"
+DEFAULT_MODEL_ALIAS = "claude-opus-5-5"
 
-# alias do CLI → prefixo que o `modelUsage` da resposta TEM que exibir.
-# É o mapa que sustenta a prova: sem prefixo conhecido, a saída não pode ser
-# atribuída a modelo nenhum, e o runner recusa antes de chamar o CLI.
+# Alias/modelo pedido ao CLI → prefixo esperado no `modelUsage`. O novo ID
+# explícito é a exceção deliberada: ele exige igualdade, para não aceitar
+# `claude-opus-5` nem o lookalike `claude-opus-5-50`; aliases legados mantêm
+# a prova por prefixo já compatível com os sufixos de release da CLI.
 MODEL_ALIASES = {
+    "claude-opus-5-5": "claude-opus-5-5",
     "opus": "claude-opus-5",
     "fable": "claude-fable-5-1",
     "sonnet": "claude-sonnet-5",
@@ -72,9 +74,9 @@ def main() -> int:
     if args.timeout <= 0 or args.max_input_bytes <= 0:
         return fail(2, "OPUS_INVALID_LIMITS: timeout e max-input-bytes devem ser positivos")
 
-    # Fail-closed ANTES de qualquer efeito: alias sem prefixo conhecido não roda.
-    expected_prefix = MODEL_ALIASES.get(args.model)
-    if expected_prefix is None:
+    # Fail-closed ANTES de qualquer efeito: alias/modelo sem prova conhecida não roda.
+    expected_model = MODEL_ALIASES.get(args.model)
+    if expected_model is None:
         return fail(
             2,
             f"MODEL_ALIAS_DESCONHECIDO: {args.model!r} não está no mapa de prova; "
@@ -155,10 +157,13 @@ def main() -> int:
 
     model_usage = payload.get("modelUsage") or payload.get("model_usage") or {}
     model_names = list(model_usage) if isinstance(model_usage, dict) else []
-    opus_models = [name for name in model_names if name.startswith(expected_prefix)]
+    if args.model == "claude-opus-5-5":
+        opus_models = [name for name in model_names if name == expected_model]
+    else:
+        opus_models = [name for name in model_names if name.startswith(expected_model)]
     if not opus_models:
         observed = ",".join(model_names) if model_names else "<ausente>"
-        return fail(7, f"OPUS_MODEL_MISMATCH: esperado {expected_prefix}; observado {observed}")
+        return fail(7, f"OPUS_MODEL_MISMATCH: esperado {expected_model}; observado {observed}")
 
     result = payload.get("result")
     if not isinstance(result, str) or not result.strip():

