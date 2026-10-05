Revisão independente T-131, R1, somente texto/diff. READ-ONLY; nenhuma ferramenta, arquivo, delegação ou pesquisa. O produto são instruções: procure ambiguidade, contradição e comando inexistente com cenário concreto. Objetivo aprovado: Fable ativo -> Opus5.5; ID explícito claude-opus-5-5 exige igualdade, aliases opus/fable/sonnet/haiku conservam prefixo legado e fable não vira Opus. Catálogo passa a oferecer Sol6/Luna6, mas as sondas desta CLI/conta ChatGPT recusaram ambos: não ativar sem prova modelo+via+conta/host, nem fallback. Elenco do projeto mantém Astra/Terra; catálogo de fábrica não é elenco ativo. Nenhum bump/cache/commit/install/restart nesta fase. Lint cache divergente conhecido é gate de release, não defeito novo. Audite somente mudanças deste lote, não atribua cobertura aos outros. Defeitos antigos fora do diff não bloqueiam esta migração salvo regressão introduzida. Formato obrigatório: ## BLOQUEADORES; ## RISCOS; ## VEREDITO (APROVADO | APROVADO_COM_RESSALVAS | REPROVADO). Cada achado arquivo:linha, entrada -> erro, correção mínima. Se nenhum, diga nenhum. Não invente problema de estilo.

LOTE 1/5. Sem acesso ao repositório; cada hunk tem coordenadas Git. Snapshot local, nenhuma instalação ou integração.

diff --git a/orq/commands/elenco.md b/orq/commands/elenco.md
index bd30473..0d00436 100644
--- a/orq/commands/elenco.md
+++ b/orq/commands/elenco.md
@@ -83,7 +83,8 @@ registro → `sistema · normal`** — o default seguro. Card Trivial: `trilha:
   problema. Aceita modelo de qualquer vendor com célula na `## Matriz de invocação`, **desde que o
   mecanismo daquela célula execute aquele modelo** (a célula Anthropic×Codex é o runner Anthropic
   parametrizado por `--model <alias>`: só entra alias presente no mapa de prova do runner, e a
-  saída só vale com o prefixo daquele alias comprovado no `modelUsage`).
+  saída só vale com a prova do modelo pedido no `modelUsage`: igualdade para o ID explícito
+  `claude-opus-5-5`, prefixo para cada alias legado).
 - **`reviewer`** cruza pela **independência**, e é obrigado a cruzar: sempre o vendor **oposto** ao
   do host, com a mesma checagem de mecanismo.
 - **`implementer`, `docs` e `scout` ficam no vendor do host.** Nos dois primeiros porque **escrevem**
@@ -156,8 +157,10 @@ seção "Com argumento `perfil <nome>` — trocar o time inteiro" abaixo, em vez
      `pesada` e `leve` ficaram como estavam.
 2. Valide o modelo **contra o vendor do host resolvido no passo 0** — não contra uma lista fixa:
    - **`implementer`, `docs` e `scout`: só modelos do vendor do host.** No host Claude, `opus` ·
-     `sonnet` · `haiku` · `fable` · `inherit` ou um id (`claude-opus-5`); no host Codex, um modelo
-     OpenAI com effort opcional (`gpt-5.6-sol@xhigh`, `gpt-5.6-terra@xhigh`). Modelo de outro vendor
+     `sonnet` · `haiku` · `fable` · `inherit`, o alias legado `opus`, ou um id explícito
+     (`claude-opus-5-5`); no host Codex, um modelo OpenAI com effort opcional
+     (`gpt-5.6-terra@xhigh`; `gpt-6-sol` e `gpt-6-luna` são candidatos pendentes de capacidade).
+     Modelo de outro vendor
      aqui é **recusa com motivo**, não pergunta: nos dois primeiros porque escrita cross-vendor está
      fora do desenho; no `scout` porque leitura ampla e barata não se paga em domínio — diga isso ao
      recusar, e ofereça o modelo barato do host no lugar.
@@ -167,25 +170,29 @@ seção "Com argumento `perfil <nome>` — trocar o time inteiro" abaixo, em vez
    - ⛔ **Vendor certo não basta: o MECANISMO daquela célula tem que conseguir executar o modelo.**
      Leia a célula antes de aceitar, e recuse o que ela não roda:
      - **Anthropic × host Codex** — a célula é o `run-opus-reviewer.py --model <alias>`. O runner só
-       aceita alias presente no seu mapa de prova (`opus` · `fable` · `sonnet` · `haiku`) e só
-       imprime parecer se o `modelUsage` do JSON comprovar o prefixo daquele alias — pedir `fable` e
-       receber Opus, ou receber `claude-fable-5-0` quando o elenco exige 5.1, reprova com
-       `OPUS_MODEL_MISMATCH`, e alias fora do mapa é recusado **antes** de chamar o CLI. Registrar
-       aqui um alias que o runner não conhece → **recuse citando o mapa**: *"o runner não tem esse
-       alias no mapa de prova; registrar aqui gravaria um elenco que a execução não honra"*.
-       Ensinar o runner um alias novo é **card novo**, não improviso deste comando.
+       aceita a opção explícita `claude-opus-5-5` e os aliases legados do mapa (`opus` · `fable` ·
+       `sonnet` · `haiku`) e só imprime parecer se o `modelUsage` do JSON comprovar a identidade
+       exata para `claude-opus-5-5` ou o prefixo esperado para alias legado. Pedir
+       `claude-opus-5-5` e receber `claude-opus-5` ou `claude-opus-5-50` reprova com
+       `OPUS_MODEL_MISMATCH`; os aliases legados mantêm a prova por prefixo. Opção fora do mapa é
+       recusada **antes** de chamar o CLI. Registrar aqui uma opção que
+       o runner não conhece → **recuse citando o mapa**: *"o runner não tem essa opção no mapa de
+       prova; registrar aqui gravaria um elenco que a execução não honra"*.
+       Ensinar o runner uma opção nova é **card novo**, não improviso deste comando.
      - **OpenAI × host Claude** — a célula usa `codex:codex-rescue` e
-       `codex-companion.mjs task --model <modelo> --effort <effort>`; o Companion aceita o modelo
-       do catálogo e devolve `jobId` + `threadId` para reúso por `card+papel`.
-     - **OpenAI × host Codex** — a célula usa `codex exec -m <modelo>`; qualquer modelo OpenAI do
-       catálogo serve, com effort opcional.
-     **Por que isto é regra e não zelo:** sem ela o arquivo registra Fable e a execução entrega
-     Opus, calada, ou registra Fable 5.1 e a execução entrega 5.0 sem ninguém notar. Elenco que
-     mente sobre quem trabalhou é pior que elenco ausente — some a procedência, que é justamente o
-     que este arquivo existe para guardar.
+       `codex-companion.mjs task --model <modelo> --effort <effort>`; catálogo só torna um modelo
+       candidato. A capacidade precisa estar comprovada para essa via, conta e host antes da troca.
+     - **OpenAI × host Codex** — a célula usa `codex exec -m <modelo>`; catálogo também é só
+       candidatura, nunca prova de capacidade para a conta/host atual.
+     **Por que isto é regra e não zelo:** sem ela o arquivo registra Opus 5.5 e a execução entrega
+     Opus 5 ou um lookalike, calada. Elenco que mente sobre quem trabalhou é pior que elenco ausente
+     — some a procedência, que é justamente o que este arquivo existe para guardar.
    - Valor que não se encaixa em nenhuma dessas → **pergunte** em vez de gravar errado.
-3. Grave **na tabela do host resolvido**, dentro de `## Times por host` (crie o arquivo a partir do
-   modelo abaixo se não existir). **Host sem seção `## Perfis` própria** (é o caso de fábrica fora do
+3. Grave **na tabela do host resolvido**, dentro de `## Times por host`. A **guarda de capacidade da
+   proposta de fábrica** antes da tabela vale aqui: sem prova válida para modelo + via + conta/host,
+   não grave a tabela nem acione fallback; preserve integralmente o elenco existente. Se não existe
+   elenco, pare e peça ao dono uma escolha entre opções comprovadas — não crie arquivo nem elenco
+   inoperante a partir do modelo. **Host sem seção `## Perfis` própria** (é o caso de fábrica fora do
    host Claude): grave o ajuste e diga em uma linha que este host não tem presets — não invente um.
    **Host com presets e sem a linha `Perfil ativo`**: grave-a antes do ajuste — `padrao`, data de
    hoje, sem desvio, no formato da linha do template. Semear **depois** do ajuste faria o valor
@@ -261,7 +268,8 @@ trocar por aqui. Se ele pedir, explique e sugira o `/model`.
    Grave-a também — `padrao`, com a data de hoje, sem desvio.
 1. Leia a seção **Perfis** daquele host. Perfil inexistente → liste os que existem e **pergunte**;
    não crie perfil novo sem pedido explícito.
-2. **Reescreva a tabela do host resolvido** dentro de `## Times por host`, a partir do preset
+2. **Gate de capacidade antes de mudar modelo:** exija **prova válida de capacidade para modelo + via + conta/host** de cada valor que o perfil alteraria. Catálogo, documentação e nome no preset não são prova. Recusa ou ausência de prova **preserva o elenco ativo inteiro** (sem reescrita parcial), não grava tabela nem aciona fallback, e informa a limitação da via/conta; não faça sonda automática nem declare incapacidade global de API/App.
+3. **Reescreva a tabela do host resolvido** dentro de `## Times por host`, a partir do preset
    (modelos e "Por quê"), e atualize a linha **Perfil ativo** daquela seção — nome + data, zerando
    desvios anteriores. **A linha `manager` não faz parte de preset nenhum — preserve-a como está.**
    Os presets têm 8 linhas (sem `manager`); a tabela do host tem 9. Reescrever "as 8 linhas do
@@ -270,18 +278,18 @@ trocar por aqui. Se ele pedir, explique e sugira o `/model`.
    preset declarar; preserve o que está registrado agora**, pela mesma razão do `manager`: é o que
    está de fato instalado e ativo no projeto, não uma escolha do time. A linha "Revisores externos"
    dentro de cada preset é só informativa (estado de fábrica, de leitura).
-3. Confirme mostrando o time novo, **em qual host**, **e o que se perde** — resuma a nota do preset
+4. Confirme mostrando o time novo, **em qual host**, **e o que se perde** — resuma a nota do preset
    em até 3 linhas. Havia desvio registrado na linha Perfil ativo? **Diga em uma linha que ele foi
    descartado** — sem isso, o registro só muda onde a escolha some, não o silêncio. **Anuncie, não
    pergunte**, e diga **na hora como reverter** (ex.: "quando o crédito voltar, é só dizer" ou
    `/orq:elenco perfil padrao`) — não invente nem espere que ele decore uma frase fixa de volta; o
    pedido de reverter é reconhecido como o pedido de mudança que é, na hora em que ele vier.
-4. A troca vale a partir do **próximo spawn, nas janelas daquele host** — crédito é da conta, não da
+5. A troca vale a partir do **próximo spawn, nas janelas daquele host** — crédito é da conta, não da
    frente. Agente já em execução termina no modelo antigo; não refaça nada. Se houver card `[~]`
    no board, diga em uma linha que ele termina com elenco misto, e que isso é esperado.
-5. **`manager` não muda por perfil.** Ao ativar um perfil de economia, sugira em uma linha que o
+6. **`manager` não muda por perfil.** Ao ativar um perfil de economia, sugira em uma linha que o
    dono avalie o `/model` da sessão — é onde mora o maior consumo, e só ele troca.
-6. **Perfil nunca troca o vendor do `reviewer`.** Ele rebaixa degrau/effort **dentro do mesmo
+7. **Perfil nunca troca o vendor do `reviewer`.** Ele rebaixa degrau/effort **dentro do mesmo
    vendor**: rebaixar o revisor para o vendor do host acabaria com a independência, que é a única
    coisa que ele entrega.
 
@@ -305,7 +313,7 @@ significa “rodando agora”: o Manager verifica a sessão/CLI real antes de an
 | Papel | Modelo | Sandbox / mecanismo |
 |---|---|---|
 | manager | modelo da sessão (`/model`) | sessão principal |
-| planner·interface | `fable` | spawn nativo, read-only — Fable 5.1 |
+| planner·interface | `claude-opus-5-5` | spawn nativo, read-only — ID explícito; capacidade confirmada no uso |
 | planner·sistema | `gpt-6-astra@xhigh` | Codex Companion read-only; task fresca por card+papel e retomada pelo `threadId` exato |
 | implementer·pesada | `opus` | worktree dedicado, writer único |
 | implementer·normal | `sonnet` | worktree dedicado, writer único |
@@ -326,22 +334,28 @@ continuar na lista. Ver passo 3 de "Com argumento — ajustar".)*
 
 ### Host Codex
 
+**Proposta de fábrica, não elenco ativo.** Esta tabela só oferece candidatos para inicializar um
+elenco novo; ela não substitui a tabela já registrada em `memory/wiki/_elenco.md`. `gpt-6-sol` e
+`gpt-6-luna` dependem de capacidade real comprovada para **modelo + via + conta/host**. Documentação,
+catálogo e esta própria proposta não são prova. A guarda vale para perfil, ajuste papel a papel ou
+inicialização de elenco novo: sem prova não grave a tabela nem acione fallback; preserve
+integralmente o elenco existente; se ele não existe, pare e peça ao dono uma escolha entre opções
+comprovadas, sem criar elenco inoperante.
+
 | Papel | Modelo | Sandbox / mecanismo |
 |---|---|---|
-| manager | `gpt-5.6-sol@high` | sessão principal; verificar, não trocar silenciosamente |
+| manager | modelo da sessão (`/model`) | sessão principal; escolha do dono, verificar sem trocar silenciosamente |
 | planner·interface | `gpt-6-astra@max` | `codex exec … -s read-only` — vendor nativo do host |
 | planner·sistema | `gpt-6-astra@max` | `read-only` |
-| implementer·pesada | `gpt-5.6-sol@xhigh` | `workspace-write`, em worktree dedicado |
+| implementer·pesada | `gpt-6-sol@xhigh` | `workspace-write`, em worktree dedicado |
 | implementer·normal | `gpt-5.6-terra@xhigh` | `workspace-write`, em worktree dedicado |
-| implementer·leve | `gpt-5.6-luna` (sem effort declarado — ver nota) | `workspace-write`, em worktree dedicado |
-| reviewer | `fable` (exigir comprovação de que o alias resolve para `claude-fable-5-1`) | runner Anthropic, read-only, sem ferramentas — invocar com `--model fable` |
-| docs | `gpt-5.6-sol@low` | arquivos de documentação autorizados |
-| scout | `gpt-5.6-sol@low` | read-only |
+| implementer·leve | `gpt-6-luna` (sem effort declarado — ver nota) | `workspace-write`, em worktree dedicado |
+| reviewer | `claude-opus-5-5` (exigir comprovação da identidade exata `claude-opus-5-5`) | runner Anthropic, read-only, sem ferramentas — invocar com `--model claude-opus-5-5` |
+| docs | `gpt-6-sol@low` | arquivos de documentação autorizados |
+| scout | `gpt-6-sol@low` | read-only |
 
-**Nota do `implementer·leve`:** o degrau vai **sem effort declarado** de propósito — o smoke que
-liberou o modelo provou que ele responde quando endereçado, não quais reasoning efforts aceita nem
-como se comporta em `workspace-write`. Declarar um effort aqui seria inventar procedência. Registre
-a medição no `_elenco.md` do projeto quando ela existir.
+**Candidatos pendentes:** `gpt-6-sol` e `gpt-6-luna` só entram depois de prova válida para
+modelo + via + conta/host; não os ative por aparecerem no catálogo ou neste template.
 
 **Perfil ativo:** — este host não tem presets de fábrica; ajuste papel a papel. Criar um `## Perfis`
 para ele é pedido do dono, não iniciativa.

