# T-052 — Reconciliar a `0.24.0` local com a `0.22.7` publicada

> **Estado: CONCLUÍDO E PUBLICADO** em 2026-09-02 — `78b0fec` (dois pais) + `bd6d3fc`. O plano
> abaixo é registro; o fechamento está no `RETOMAR AQUI` no fim do arquivo.
> **Planner:** `gpt-5.6-sol@xhigh` via `codex exec` — trilha `sistema` pelo elenco da 0.24.0. Foi a
> **primeira vez** que a via OpenAI produziu plano (antes só tinha sido exercitada como revisor);
> uma das três pendências declaradas na `0.24.0` fica assim coberta.

## O problema, em uma frase

Duas cópias do projeto cresceram separadas desde a base `008fbc91` (29/ago): a **local**, com a
`0.24.0` (`T-051` — elenco em dois eixos, revisor único, Kimi aposentado, 7 rodadas de review), e a
**remota**, com a `0.22.7` (Codex — `T-037` SuperMemory removido, `T-043` guardião consultivo,
`T-046`, `T-048`, `T-049`, `T-050`). **18 arquivos foram tocados pelos dois lados**, 29 caminhos só
existem no remoto e 8 só no local. O push foi **rejeitado**; nada se perdeu.

## Decisões do dono — 2026-09-01, todas fechadas

1. **Estratégia: reconstrução manual, arquivo por arquivo**, partindo de `origin/main`, com
   `git merge --no-ff --no-commit -s ours dcc350b` **apenas para registrar o segundo pai** — zero hunk
   importado automaticamente. *Razão que ele acatou:* o git funde silenciosamente quando as edições
   tocam linhas diferentes, e em arquivo de **instrução** isso produz texto que lê bem e ensina duas
   regras opostas, passando nos dois gates.
2. **`T-044` fica FORA.** O commit `639a0b9` vive só em `codex/t044-reset-concurrency-0225`, **não é
   ancestral de `origin/main`** — é um terceiro ramo. Replanejar sobre a `0.25.0` depois.
3. **Versão final: `0.25.0`**, nos quatro lugares canônicos. Não reaproveitar `0.24.0`: o cache é
   indexado por versão e duas árvores distintas com o mesmo rótulo são indistinguíveis.
4. **As mudanças não commitadas entram no inventário** — são o único lugar onde `T-052`, `T-053` e os
   quatro gotchas de 2026-09-01 existem, em qualquer um dos lados.
5. **Padrão de prova: os 25 bloqueadores individualizados**, sem amostragem. ✅ **Destravado**: os
   pareceres das 7 rodadas foram consolidados em `T-051-pareceres.md` (24 KB, hash por parecer) —
   antes viviam só no scratchpad volátil. Sem eles, o card teria de parar *fail-closed*: dá para
   provar preservação da árvore, não "25/25 correções preservadas".

## Mapa do conflito por dificuldade (medido, não estimado)

| Grupo | Arquivos | O que fazer |
|---|---|---|
| **Só somar** | `fixes-history.md` (+92 aqui / +304 lá) · `gotchas.md` (+44 / +8) | append-only: unir por data, **sem editar entrada existente** |
| **Item a item** | `KANBAN.md` · `MEMORY.md` · threads `T-043` e `T-048` | estado de `T-037`/`43`/`48` vem do remoto; `T-045`/`51`/`52`/`53` vêm do local |
| **Local prevalece** | `revisar.md` (+121/-123 aqui vs +3/-1 lá) · `SKILL.md` · `README.md` | base local, portando o que o remoto acrescentou (ex.: timeout 600s) |
| **União real** | `instalar.md` (−78 aqui, +68 lá) · `stack.md` · `ajuda.md` · `CLAUDE.md`/`AGENTS.md` | as duas mudanças são legítimas e precisam coexistir |
| **⚠️ O perigoso** | `lint-coerencia.py` (+356 aqui / +417 lá) | dois `main()`, guardas distintos; guarda que some **não quebra gate nenhum** |
| **Versão** | `plugin.json` · `marketplace.json` · Status do `README` · `MEMORY.md` | `0.25.0` nos quatro |

---

# Plano do Planner (íntegra)

Plano pronto. A estratégia recomendada é reconstrução manual sobre `origin/main`, preservando os dois ancestrais sem aceitar nenhum conteúdo de merge automático.

Nada foi editado. O estado continua: `main=dcc350b`, `origin/main=6fde3e3`, 3 commits à frente/27 atrás, com alterações preexistentes apenas em `memory/gotchas.md` e `memory/wiki/KANBAN.md`.

## Constatações que alteram o handoff

- Os “29 arquivos só-remoto” são, precisamente, 29 caminhos modificados apenas no remoto: 17 adições, 10 modificações e 2 remoções.
- Existem ainda 8 caminhos modificados apenas pela 0.24.0; eles também precisam entrar no inventário.
- T‑044 não está em `origin/main`: `639a0b9` vive apenas em `codex/t044-reset-concurrency-0225`, não é ancestral do remoto, e o board remoto ainda deixa T‑044 em backlog.
- O remoto introduziu um quinto pin de versão em `ContextGuardReleaseVersionTest`, contrariando a regra local dos quatro lugares.
- A prova durável dos 25 bloqueadores é incompleta: [fixes-history.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/fixes-history.md:33>) registra a contagem e quatro achados centrais, mas não enumera individualmente os 25.

## 1. Estratégia de integração

| Alternativa | Avaliação |
|---|---|
| Merge recursivo | Preserva ancestrais, mas aceita automaticamente hunks “limpos” em arquivos de instruções. É justamente o modo de perda silenciosa proibido. |
| Rebase | Reescreve os três commits locais e o golden SHA `dcc350b`; repete os mesmos conflitos sem melhorar a prova semântica. |
| Cherry-pick | `08cb879` é um commit monolítico sobre os arquivos críticos; o conflito continua opaco e ainda não representa sozinho todo o estado documental local. |
| Reconstrução manual | Escolhida. Parte do remoto publicado, importa explicitamente cada obrigação da 0.24.0 e permite provar a procedência de cada regra. |

Execução proposta, somente depois da aprovação:

1. Criar `.worktrees/t052-reconcile-0250` a partir de `origin/main`.
2. Registrar os três insumos imutáveis: remoto `6fde3e3`, golden local `dcc350b`/feature `08cb879` e hash do diff não commitado atual.
3. Abrir um merge de ancestralidade com `git merge --no-ff --no-commit -s ours dcc350b`. Como a branch parte do remoto, isso conserva integralmente a árvore remota e adiciona o segundo pai, sem importar um único hunk automaticamente.
4. Reconstruir manualmente os 18 arquivos comuns, copiar os 8 local-only e adaptar os caminhos remote-only conforme abaixo.
5. Produzir um único merge commit de produto após revisão e gates. Nada de push ou instalação nesse gate.

## 2. Tratamento dos 18 caminhos comuns

| Arquivo | Prevalência e fusão manual | Risco específico |
|---|---|---|
| `.claude-plugin/marketplace.json` | Nenhum lado: versão final `0.25.0`. | Manifestos divergirem. |
| `AGENTS.md` | União: remoto fornece compactação consultiva, suíte e verificador de cache; local fornece revisor único cross-vendor. Deve ficar idêntico a `CLAUDE.md`. | Regra antiga de painel ou “cinco bumps” sobreviver. |
| `CLAUDE.md` | Mesmo tratamento de `AGENTS.md`; preservar os dois gates oficiais e tratar a suíte como pré-gate automatizado. | Contradição operacional entre os dois arquivos-raiz. |
| `README.md` | A 0.24.0 prevalece como estrutura; portar do remoto guardião consultivo, retirada do SuperMemory, auditoria offline, timeout e validação de cache. | Ressuscitar Kimi, painel de três, `confirmado por 2+` ou `diff -rq` como prova. |
| `memory/MEMORY.md` | Reconstrução atemporal: 0.25.0/T‑051 no topo, fatos remotos de T‑037/43/48/49/50 abaixo. | A local afirma incorretamente que 0.24.0 foi publicada; a remota descreve elenco antigo. |
| `memory/fixes-history.md` | União append-only, por blocos: 92 linhas locais + 304 remotas, byte a byte, seguidas de nova entrada T‑052. | Perda, edição retroativa ou duplicação de uma entrada. |
| `memory/gotchas.md` | União append-only: 44 linhas locais + 8 remotas + as 26 linhas não commitadas atuais. | Perder os gotchas de Fable já no working tree. |
| `memory/wiki/KANBAN.md` | Status remoto prevalece para T‑037/43/48/49/50; incorporar T‑051/52/53 locais. T‑044 fica condicionado à decisão do dono. | Duplicar IDs ou regredir T‑048/49/50 para “em implementação”. |
| `threads/T-043-protecao-contexto-codex.md` | Estado final remoto prevalece; incorporar apenas cronologia/evidência local ausente. Um único `RETOMAR AQUI`, apontando para o estado atual. | Reintroduzir bloqueio/`clear_required` ou retomada vencida. |
| `threads/T-048-auditores-nativos.md` | Fechamento remoto prevalece; plano local fica como cronologia, não como estado corrente. | Thread dizer “implementando” enquanto board diz concluído. |
| `orq/.claude-plugin/plugin.json` | Nenhum lado: `0.25.0`. | Divergência com marketplace. |
| `orq/commands/ajuda.md` | Base local: revisor único e só Claude/Codex; acrescentar do remoto `/orq:auditar` e memória elegível. | Voltar a anunciar painel ou host Kimi. |
| `orq/commands/instalar.md` | Estrutura local sem Kimi; substituir o `diff -rq` pelo contrato remoto de fonte limpa + `verify_installed_cache.py`. | Usar cache/working tree como fonte ou aceitar extras arbitrários. |
| `orq/commands/revisar.md` | Arquivo local prevalece integralmente; portar apenas contrato comprovado do runner remoto, especialmente 600s. | Perder LGPD, ausência deliberada de substituto interno e `REVISÃO DEGRADADA`. |
| `orq/commands/stack.md` | União: revisor singular/local + guardião, retirada do SuperMemory e verificação de cache/remoto. | Diagnóstico sugerir Kimi, SuperMemory ou comparação bruta. |
| `orq/scripts/lint-coerencia.py` | Base estrutural local; portar `validate_codex_consultive_language`, `find_installation_divergences`, allowlists host-aware, 600s e proteção contra `__pycache__`. | Um `main()` sobrescrever o outro ou uma função existir sem ser chamada; é o conflito mais perigoso. |
| `orq/skills/orq/SKILL.md` | Base local reescrita; portar gatilho de auditoria, memória elegível e protocolo consultivo de checkpoint/compactação. | Duplicar linhas de roteamento ou reintroduzir Kimi/painel. |
| `orq/stack.md` | União: revisor único/sem Kimi da local + arquitetura provider-neutral/sem SuperMemory do remoto. | Perfis vivos contradizerem `_stack.md` ou `revisar.md`. |

No `lint-coerencia.py`, a aceitação exige simultaneamente todas as famílias locais — dois eixos, papéis únicos em `Times por host`, reviewer oposto, anti-Kimi, seções únicas e quatro âncoras de versão — e todas as remotas — linguagem consultiva, cache host-aware, timeout e import seguro. Não basta o script executar verde: cada guarda terá contraprova negativa.

## 3. Os 29 caminhos tocados apenas no remoto — e os 8 local-only

Dos 29:

- As 17 adições entram a partir do remoto: cinco planos/specs, snapshot T‑043, threads T‑046/T‑049/T‑050, `auditar.md`, schema do ledger, dois auditores, `verify_installed_cache.py` e seus cinco testes.
- As 10 modificações remotas também entram, pois a 0.24.0 não as tocou: `.gitignore`, `_stack.md`, `arquitetura.md`, `distribuicao.md`, thread T‑037, `checkpoint.md`, `context-guard.py`, `run-opus-reviewer.py` e seus dois testes. Depois:
  - `arquitetura.md`, `distribuicao.md` e `_stack.md` recebem reconciliação semântica T‑051, pois ainda descrevem Kimi/painel;
  - `test_context_guard.py` perde o pin hardcoded de versão;
  - os demais devem permanecer byte-idênticos ao remoto salvo correção exigida por teste.
- As duas remoções remotas são preservadas: `orq/commands/lembrar.md` e `orq/scripts/sm-search.py`. Não criar tombstone ativo.

Os 8 local-only também entram no inventário: `_elenco.md`, `elenco.md`, `plan-next.md`, `implement-next.md`, `init.md` e as três threads locais. As cinco superfícies vivas devem começar byte-idênticas a `dcc350b`; qualquer alteração posterior precisa citar uma obrigação remota específica.

## 4. Versão final

Recomendação: `0.25.0`. É superior ao remoto publicado e à candidata local, sem reutilizar uma versão que já designou outra árvore.

Quatro lugares canônicos:

1. `orq/.claude-plugin/plugin.json`;
2. `.claude-plugin/marketplace.json`;
3. seção Status do `README.md`;
4. cabeçalho de `memory/MEMORY.md`.

O `expected = "0.22.7"` de `ContextGuardReleaseVersionTest` deve passar a derivar `expected` do manifesto do plugin e comparar os outros três lugares contra ele. Assim o teste continua provando coordenação sem criar uma quinta fonte de verdade.

## 5. Ordem de verificação

1. Congelar SHA, inventário dos 55 caminhos e diff não commitado.
2. Construir o ledger dos 25 bloqueadores e fazê-lo passar 25/25 contra `dcc350b`.
3. Reconstruir a árvore final.
4. Rodar a suíte completa herdada do remoto, com bytecode desabilitado:
   `test_audit_adoption`, `test_audit_removal`, `test_verify_installed_cache`, `test_context_guard` e `test_run_opus_reviewer`.
5. Rodar as contraprovas T‑052 e o ledger T‑051: 25/25.
6. Gate 1: `claude plugin validate ./orq --strict`.
7. Gate 2: `python3 orq/scripts/lint-coerencia.py .`.
8. Rodar `git diff --check`, inventário de caminhos, hashes append-only e coordenação da versão.
9. Revisão externa pelo Opus, vendor oposto ao host Codex, sobre a árvore viva completa em lotes determinísticos — não apenas sobre o diff. O parecer deve citar o hash do inventário analisado.
10. Qualquer correção invalida o recibo: repetir suíte, ledger, dois gates e revisão até `APROVADO`.
11. Só então commit local. Push continua gate separado do dono.
12. Após push: clone detached limpo do SHA remoto, verificação dos caches, restart e teste comportamental.

## 6. Prova das 25 correções

O critério não será “reler com atenção”.

Antes da fusão, criar um manifesto com 25 registros:

`rodada/bloqueador → recibo original → arquivos/seções → regra positiva → regra proibida → probe → resultado esperado`.

A prova final exige:

- Os sete recibos/transcripts recuperados e hashados.
- `25/25` probes passando primeiro em `dcc350b`; isso valida o próprio manifesto.
- Seções protegidas da 0.24.0 com hash idêntico ao golden quando não precisarem de fusão.
- Toda seção diferente de `dcc350b` ligada a uma obrigação remota identificada.
- Todos os 8 caminhos local-only presentes.
- Zero strings vivas de Kimi/Moonshot no `orq/`; zero painel, maioria ou `confirmado por 2+` normativos.
- Os seis cenários comportamentais de [T-051-elenco-por-tarefa.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/threads/T-051-elenco-por-tarefa.md:298>) executados na 0.25.0 instalada.

Se os 25 recibos individuais não puderem ser recuperados, o card deve parar fail-closed: é possível provar preservação da árvore `dcc350b`, mas não afirmar honestamente “25/25 correções preservadas”.

## 7. Cache local

- Não instalar a 0.24.0 intermediária.
- Não apagar 0.22.4–0.22.7; sessões ainda podem referenciá-las e `.in_use` existe justamente para proteger cache vivo.
- Não usar nenhum cache como fonte da reconciliação.
- Após publicação autorizada da 0.25.0, atualizar marketplace/plugin separadamente em Claude e Codex, reiniciar e verificar cada cache com `verify_installed_cache.py` vindo do clone detached limpo.
- Limpeza das versões antigas vira gate posterior e explícito, apenas depois de 0.25.0 validada e sem referências vivas.

## 8. Riscos dominantes

- Regra desaparecer sem falhar em nenhum gate — principal risco; mitigado pelo ledger semântico e revisão da árvore completa.
- Reviver Kimi/painel/SuperMemory ao portar documentação remota antiga.
- Combinar os dois `main()` do lint incorretamente e deixar guardas órfãs.
- Editar memória append-only ou duplicar blocos durante a união.
- Regressar estados do board e threads para checkpoints antigos.
- Tratar o pin de teste como quinta versão canônica.
- Incorporar T‑044 como se estivesse publicado.
- Perder o diff não commitado atual ao abrir worktree/merge.
- Aceitar parecer externo e depois mudar bytes sem renovar o recibo.
- Validar cache contra working tree ou contra outro cache.

## 9. Decisões do dono

1. **Estratégia:** reconstrução manual em worktree remoto com merge `ours` apenas para registrar os dois pais.  
   **Recomendação:** aprovar.

2. **T‑044:** incorporar agora o commit isolado `639a0b9` ou mantê-lo fora.  
   **Recomendação:** manter fora de T‑052; é um terceiro ramo, não parte de `origin/main`. Depois, replanejá-lo sobre 0.25.0.

3. **Versão:** `0.25.0` e quatro fontes canônicas, refatorando o teste para derivação.  
   **Recomendação:** aprovar.

4. **Padrão de prova:** exigir os 25 recibos individualizados; se não forem recuperáveis, não declarar preservação integral.  
   **Recomendação:** obrigatório, sem redução para amostragem.

5. **Alterações não commitadas de board/gotchas:** incluí-las no inventário da reconciliação, sem mexer na `main` local atual.  
   **Recomendação:** incluir, pois contêm T‑052/T‑053 e dois gotchas que ainda não existem em nenhum commit.

Estado do card: plano concluído; deve permanecer no gate do dono, sem implementação, bump, commit, push, cache ou publicação.

---

## ⏭️ RETOMAR AQUI — *(atualizado em 2026-09-02)*

**Concluído e publicado. Não reabra.**

- **Commit `78b0fec`, dois pais** (`6fde3e3` remoto + `dcc350b` local) — a ancestralidade dos dois
  ramos ficou registrada no grafo. Depois, `bd6d3fc` com a documentação do release.
- **Como foi feito:** reconstrução manual a partir de `origin/main`, `merge -s ours` **apenas** para
  registrar os pais. Zero hunk automático — o git funde calado quando as edições tocam linhas
  diferentes, e em arquivo de instrução isso vira regra contraditória que passa nos gates.
- **Tamanho real:** 18 arquivos colididos · 29 caminhos só-remoto · 8 só-local · **52 cards** fundidos
  card a card · 5 arquivos só-remoto alterados (3 de reconciliação semântica + 2 testes).
- **Prova:** 5 ledgers em `T-052-ledgers/`, todos **discriminando** — passam na árvore fundida e
  **reprovam** na árvore que não tem a regra. `ledger_t051` 25/25 aqui e 0/25 no remoto puro;
  `ledger_remoto` 4/4 aqui e 0/4 no golden local.
- **4 rodadas de revisão externa** (3+2 → 3+2 → 1 → 1). Os gates ficaram **verdes em todas**.

**O que este card ensinou, e está no `gotchas.md`:** a classe de defeito dominante numa fusão de
instruções não é contradição, é **ausência** — obrigação que existe num ramo e some do texto do
outro. Contradição tem string para procurar; ausência não. Foi assim que a suíte de 201 testes ficou
fora do guia de release e o bump sumiu do procedimento do README.

**Seguimento natural, se algum dia incomodar:** o `T-044` (reset concorrente) continua num terceiro
ramo (`codex/t044-reset-concurrency-0225`), fora de `origin/main` — decisão do dono de deixá-lo fora
desta reconciliação. Replanejar sobre a `0.25.0`, com card próprio.

## Nota herdada do card `T-052` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** Reconciliar a `0.24.0` com as `0.22.1`–`0.22.7` publicadas no GitHub

🔴 **descoberto em 2026-09-01, no momento do push, que foi REJEITADO.** A `main` remota está **27 commits à frente** da local, em **`0.22.7`**: o trabalho do Codex (`T-044` reset concorrente · `T-046`/`T-048` auditores nativos · `T-049` install-validation · `T-050` opus-timeout) foi publicado enquanto a `0.24.0` era construída a partir de `008fbc9` (29/ago). **Isto é o desalinhamento que o relatório de abertura desta sessão apontou** — a `main` estava atrás dos worktrees, e o dono optou (legitimamente) por seguir com o `T-051` primeiro. **Tamanho medido:** **18 arquivos tocados pelos dois lados**, incluindo os que a `0.24.0` reescreveu por inteiro em 7 rodadas de review — `revisar.md`, `SKILL.md`, `lint-coerencia.py`, `instalar.md`, `stack.md`, `ajuda.md`, `README.md`, `CLAUDE.md`/`AGENTS.md` e a memória; mais **29 arquivos que só existem no remoto**. **Numerações divergiram:** local `0.22.0→0.24.0`, remoto `0.22.0→0.22.7`. **Decisão do dono (2026-09-01): reconciliar com card próprio e revisão**, não `git pull` cru — *"nenhuma das 25 correções se perde num merge automático"*. **O plano precisa:** mapear o que cada versão remota mudou nos 18 arquivos colididos · integrar conflito a conflito com o mesmo rigor de review (o produto são instruções: merge automático perde regra sem avisar) · decidir a numeração final (provável `0.25.0`) · rodar os dois gates **e** o revisor externo sobre o resultado · só então publicar. ⚠️ **Efeito colateral já causado e declarado:** o `claude plugin marketplace update orquestra` rodou antes da descoberta, e o cache local recebeu `0.22.4`–`0.22.7` **do GitHub** — a `0.24.0` **não está instalada**; nada quebrou, mas o Claude está rodando o ramo remoto, e o Codex também. **A `0.24.0` está segura**: commitada na `main` local (`dcc350b`), gates verdes, nada perdido. 📊 **AUDITORIA DOS DOIS BOARDS, medida em 2026-09-01 — insumo obrigatório do plano:** os dois têm **48 cards**, mas os **conjuntos são diferentes**. **(a) Três cards avançaram no remoto e o board local não sabe:** `T-037` implementando→**VALIDATE** (SuperMemory removido, `0.22.3` publicada) · `T-043` implementando→**VALIDATE** (guardião consultivo) · `T-048` implementando→**FEITO** (`0.22.5` publicada). **(b) Quatro cards existem só no remoto:** `T-046` FEITO (lint separa `.in_use/<PID>` de divergência real, `0.22.4`) · `T-047` backlog (compatibilidade de sessões antigas após upgrade) · `T-049` FEITO (instalador rejeitava cache correto por artefato do host) · `T-050` FEITO (timeout do runner Opus matava parecer válido). **(c) Quatro existem só no local:** `T-045` (Cartographer, FEITO), `T-051`, `T-052`, `T-053`. **(d) Colisão de numeração confirmada:** o local criou `T-045` e o remoto criou `T-046`–`T-050` a partir da mesma base — a união são **52 cards**, e a renumeração tem que ser decidida no plano. **(e) A fila de validação do dono é maior do que o board local mostra:** 16 em VALIDATE aqui, **18 no remoto**. ⚠️ **Consequência de método:** fundir o `KANBAN.md` escolhendo um lado **apaga trabalho concluído de verdade** — os estados corretos de `T-037`/`T-043`/`T-048` só existem no remoto, e `T-045`/`T-051`+ só existem aqui. O board tem que ser fundido **card a card**, como os arquivos de produto. ✅ **PLANO APROVADO E DECISÕES FECHADAS (dono, 2026-09-01)** — plano em `memory/wiki/threads/T-052-reconciliacao.md`, escrito pelo **planner OpenAI** (`gpt-5.6-sol@xhigh` via `codex exec`, trilha `sistema`) — **primeira vez que a via produziu plano**, cobrindo uma das três pendências declaradas na 0.24.0. **(1) Reconstrução manual arquivo a arquivo** a partir de `origin/main`, com `merge -s ours` só para registrar ancestralidade — zero hunk automático, porque o git funde calado quando as edições tocam linhas diferentes e, em arquivo de instrução, isso vira regra contraditória que passa nos dois gates. **(2) `T-044` FICA FORA** — `639a0b9` não é ancestral do remoto, é um terceiro ramo; replanejar sobre a 0.25.0. **(3) Versão `0.25.0`** nos quatro lugares (cache é indexado por versão: reusar `0.24.0` criaria duas árvores com o mesmo rótulo). **(4) O não-commitado entra no inventário** — é o único lugar onde `T-052`, `T-053` e os 4 gotchas de hoje existem. **(5) Prova por 25 recibos individualizados, sem amostragem** — ✅ destravada: os pareceres das 7 rodadas foram consolidados em `memory/wiki/threads/T-051-pareceres.md` (24 KB, hash por parecer); antes viviam só no scratchpad volátil, e sem eles o card pararia *fail-closed*. ✅ **CONCLUÍDO E PUBLICADO (2026-09-02):** reconciliação manual arquivo a arquivo sobre `origin/main`, `merge -s ours` só para ancestralidade (**zero hunk automático**). Commit `78b0fec` com **dois pais** (`6fde3e3` remoto + `dcc350b` local) e push feito. **18 arquivos colididos, 52 cards fundidos card a card, 5 arquivos só-remoto alterados** (3 de reconciliação semântica + 2 testes). **Prova executável, não declarada:** 5 ledgers em `wiki/threads/T-052-ledgers/` que **discriminam** — 25/25 e 4/4 na árvore fundida, **0/25** no remoto puro, **0/4** no golden local. **4 rodadas de revisão externa** (3+2 → 3+2 → 1 → 1 achados), e os gates ficaram verdes em todas. **Seis defeitos viraram guarda mecânico**: papel por célula, heading ancorado, host aposentado nas páginas vivas, teto do runner derivado da fonte, vocabulário extinto e bump como passo do procedimento. ⏭️ Falta só o teste comportamental do dono, compartilhado com o `T-051`. ‖ **Contexto do trabalho:** ⚠️ **O arquivo mais perigoso era `orq/scripts/lint-coerencia.py`**: +356 linhas aqui e +417 lá, dois `main()`, guardas diferentes — **guarda que some não quebra gate nenhum**. 📌 **Achado do planner que corrige o card:** o remoto criou um **quinto** pin de versão (`ContextGuardReleaseVersionTest`), violando a regra dos quatro lugares — o teste passa a **derivar** a versão do manifesto. @frente-elenco

