# KANBAN — Orquestra (`orq`)

> Fonte da verdade do trabalho. **Só o Manager (a sessão principal) move cards.**
> Marcadores: `[ ]` backlog · `[>]` planejando · `[!]` esperando o dono · `[~]` implementando ·
> `[?]` aguardando validação · `[x]` feito.

---

## ⏸️ Esperando você

- [?] `T-064` Superpowers ou a Matriz — quem vence no spawn? — decidido por você: a Matriz vence; escrito na SKILL.md · → threads/T-054-economia-tokens.md @frente-economia
- [!] `T-065` Configurações fora do plugin — effort e MCPs feitos; falta decidir claude-mem e AGENTS.md · → threads/T-054-economia-tokens.md @frente-economia
- [x] `T-066` Consolidar o ferramental empilhado — resolvido: caveman nunca esteve lá, os 2 grafos custam ~570 tok/sessão · → threads/T-054-economia-tokens.md

- [?] `T-025` Comandos que nunca disparam sozinhos — 0.15.0 entregue, aguarda seu teste: diga "quais as possibilidades" e veja se vem cardápio por situação · → threads/T-025-gatilhos.md
- [?] `T-023` `/reload-plugins` **aplica** update de cache — 0.14.0, revisado e corrigido; teste pós-restart: README "Problemas conhecidos" com data em cada ✅ · → threads/T-023-reload-vs-restart.md
- [?] `T-020` Perfis de elenco — 0.16.0 entregue, aguarda seu teste: diga *"tô com pouco crédito"* e o time inteiro tem que trocar sem comando digitado · → threads/T-020-perfis-elenco.md
- [?] `T-026` Orquestra fora do Claude Code — 0.19.0 nos três hosts; falta o smoke no Codex e sua validação prática · → threads/T-026-host-alternativo.md @release-validacao
- [?] `T-030` Correções do painel de três revisores sobre as releases 0.14.0–0.16.0 — 0.17.0 fechada; teste: "agora não" tem que repropor 1× depois · → threads/T-030-correcoes-painel.md

---

## 🟡 Fazendo
- [?] `T-051` Reestruturar o elenco por natureza da tarefa e aposentar o Kimi — 0.25.0 publicada; falta seu teste comportamental (6 critérios, seção 7) · → threads/T-051-elenco-por-tarefa.md

- [~] `T-040` Paridade operacional do Orquestra no Codex — coordena T-041, T-043 e T-042 · → threads/_notas-de-cards.md
- [?] `T-041` Paridade core do Codex — 0.21.0 instalada; aguarda sua validação no projeto real que falhava @frente-paridade-codex · → threads/_notas-de-cards.md

- [>] `T-031` Comando para listar agentes ativos — o /orq:elenco lista o time configurado, não o que está rodando agora · → threads/_notas-de-cards.md


---

## 🟣 Validar

- [?] `T-037` Tirar o SuperMemory do sistema de desenvolvimento — 0.22.3 publicada e instalada; falta sua validação prática · → threads/_notas-de-cards.md
- [?] `T-043` Proteção preventiva da janela de contexto no Codex — guardião consultivo na 0.22.3; falta sua validação em task reaberta · → threads/_notas-de-cards.md

- [?] `T-036` O `/orq:init` apaga a statusline do dono — trilha: interface · 0.20.0 publicada; teste em projeto vazio: /orq:init não pode gravar chave · → threads/T-036-statusline.md
- [?] `T-015` Diagnóstico de ambiente dá **falso all-clear** — teste: /orq:stack --verificar tem que comparar CONTEÚDO do cache, não só versão · → threads/_notas-de-cards.md
- [?] `T-016` Colisão de roteamento na skill — teste: diga "o painel de revisão não está funcionando" — tem que criar card, não fechar em "ambiente ok" · → threads/_notas-de-cards.md
- [?] `T-017` Release sem bump deixa o cache stale em silêncio — teste: edite orq/ sem bumpar e rode lint-coerencia.py — tem que falhar · → threads/_notas-de-cards.md

- [?] `T-014` Roteamento automático pelo ciclo — teste: em sessão nova diga "queria melhorar X" — tem que anunciar o plano, não editar arquivo · → threads/_notas-de-cards.md
- [?] `T-007` Kimi como terceiro revisor do painel — ⚠️ superado pelo T-051: o painel de 3 acabou, revisor é único e cross-vendor · → threads/_notas-de-cards.md
- [?] `T-013` Protocolo de várias janelas — teste: duas janelas, cards diferentes, checkpoint nas duas — nada pode sumir · → threads/_notas-de-cards.md
- [?] `T-010` Painel de revisores consertado — ⚠️ superado pelo T-051: revisor é único agora, não painel de dois · → threads/_notas-de-cards.md
- [?] `T-009` Stack complementar auto-detectada — teste: em sessão nova diga "o que falta instalar aqui?" — tem que detectar e NÃO instalar sozinho · → threads/_notas-de-cards.md
- [?] `T-022` Relatório final do `/orq:checkpoint` fala com a pessoa errada — teste: rode um checkpoint e veja se o relatório fala com VOCÊ, não com o próximo assistente · → threads/_notas-de-cards.md

---

## 🔵 Backlog

- [?] `T-077` Runner Anthropic fixa --model opus e barra o Fable no host Codex — feito: --model por alias, prova por prefixo · → threads/T-054-economia-tokens.md

- [ ] `T-076` Board resolvido pelo checkout principal, para sobreviver a worktree por frente · trilha: sistema · faixa: normal · → threads/T-076-board-worktree.md

- [ ] `T-075` Memória de sessão pode parar de gravar sem ninguém notar — detectar no diagnóstico e no checkpoint · trilha: sistema · faixa: normal · → threads/T-072-claude-mem.md @frente-economia

- [?] `T-072` claude-mem volta ao catálogo com o papel escrito — feito em SKILL.md, stack.md e _stack.md · → threads/T-072-claude-mem.md
- [?] `T-073` O gatilho "lembra quando" nunca chama busca nenhuma — agora nomeia a busca; teste: diga a frase · → threads/T-072-claude-mem.md
- [!] `T-074` Avaliar instalar o claude-mem no Codex — plano e custo prontos; falta sua decisão de instalar · → threads/T-072-claude-mem.md

- [ ] `T-071` O regex de secao arquivada aceita demais e recusa ARQUIVADOS — revisao cross-vendor · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia

- [ ] `T-070` MEMORY.md afirma no presente que o painel de 3 revisores funciona — wiki-lint N1 · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia

- [ ] `T-068` Sequência alto uso → checkpoint → compactação → retomada não tem teste ponta a ponta — parecer · trilha: sistema · faixa: normal · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-069` Conteúdo de thread injetado pelo hook é promoção de confiança — parecer · trilha: sistema · faixa: pesada · → threads/T-054-economia-tokens.md @frente-economia

- [ ] `T-054` Guardião funciona no Claude Code, com faixas em tokens — p7 · trilha: sistema · faixa: normal · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-055` Pós-compactação injeta estado, não ordem de releitura — p8 · trilha: sistema · faixa: normal · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-056` Card do board com teto: a nota longa vai para a thread — p12 · trilha: sistema · faixa: normal · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-057` MEMORY.md volta a ser índice, com teto de linhas — p13 · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-058` Thread com teto e um único RETOMAR AQUI vivo — p14 · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-059` Leitura parcial por padrão em quadro e checkpoint — p15 · trilha: sistema · faixa: normal · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-060` Worker devolve resumo com teto, não transcrição — p16 · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-061` Escala de cerimônia dimensiona o ciclo de cada card — p17 · trilha: sistema · faixa: normal · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-062` Teto de rodadas de revisão com contador no card — p11 · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-063` Writer do Codex por subprocesso, para matar o polling — p9 · trilha: sistema · faixa: pesada · → threads/T-054-economia-tokens.md @frente-economia
- [ ] `T-067` A Matriz manda rodar codex exec por Bash; a regra do dono proíbe — achado · trilha: sistema · faixa: leve · → threads/T-054-economia-tokens.md @frente-economia

- [?] `T-052` Reconciliar a `0.24.0` com as `0.22.1`–`0.22.7` publicadas no GitHub — 0.25.0 reconciliada e publicada; teste comportamental compartilhado com o T-051 · → threads/T-052-reconciliacao.md

- [ ] `T-053` Incorporar o Fable 5.1 no elenco — trilha: sistema · faixa: normal · próximo: claude update 2.1.255+, reiniciar, reler additionalModelOptionsCache · → threads/T-053-fable-51.md

- [ ] `T-047` Compatibilidade de sessões antigas após upgrades — sessões antigas apontam para caches já ausentes · → threads/_notas-de-cards.md
- [ ] `T-044` Endurecer reset concorrente do guardião de contexto — reset concorrente pode apagar o marcador .reset do SessionStart(clear) · → threads/_notas-de-cards.md

- [ ] `T-042` Statusline nativa do Codex — release alvo 0.23.0 · perfil opt-in com backup e rollback · → threads/_notas-de-cards.md

- [ ] `T-032` O protocolo de várias janelas ficou incompleto onde o projeto cresceu depois dele — o T-013 funciona; falta cobrir o que cresceu depois dele · → threads/_notas-de-cards.md

- [ ] `T-033` O template do `_elenco.md` não ganhou as seções da 0.19.0 — template do _elenco.md sem as seções da 0.19.0; projeto novo nasce vazio · → threads/_notas-de-cards.md
- [ ] `T-034` Os consumidores não resolvem o time por host — bloqueador: a falha é silenciosa — consumidor não resolve o time por host · → threads/_notas-de-cards.md
- [ ] `T-035` Procedência inflada e a fumaça do `instalar.md` usando a forma que a 0.19.0 declarou insegura — três achados do painel de 2026-08-07 · → threads/_notas-de-cards.md


- [ ] `T-038` Compor o board dentro de uma statusline alheia (a folha F4, extraída do `T-036`) — tese validada; falta o acabamento das bordas · → threads/_notas-de-cards.md

- [ ] `T-039` Projeto com memória preexistente em OUTRO formato é tratado como virgem — o init já protege o caso; o defeito real é a FASE 1 anunciar "não inicializado" · → threads/_notas-de-cards.md

- [ ] `T-028` `README.md` afirma que o Kimi não está instalado — ⚠️ o card virou obsoleto: o T-051 aposentou o Kimi do produto · → threads/_notas-de-cards.md
- [ ] `T-029` O lint não enxerga caminho relativo entre arquivos do plugin — o lint não valida caminho relativo entre arquivos do plugin · → threads/_notas-de-cards.md
- [ ] `T-027` CLI do Codex direto vs subagente `codex:codex-rescue` — decisão sua, não minha — a CLI direta é o caminho que o T-010 provou · → threads/_notas-de-cards.md
- [ ] `T-021` Motor alternativo quando o Claude está no limite — teto técnico: subagente do Claude só aceita modelo Claude · → threads/_notas-de-cards.md

- [ ] `T-019` 🔴 **O Kimi rodou `git checkout -- .` numa tarefa read-only e destruiu o working tree** — hook que barra escrita em worker read-only · → threads/_notas-de-cards.md
- [ ] `T-001` Hooks de segurança — PreToolUse em Bash negando push, merge, deploy e SQL de escrita · → threads/_notas-de-cards.md
- [ ] `T-002` Hooks de processo — PreToolUse sobre o KANBAN: mover para [?] sem review existente é bloqueado · → threads/_notas-de-cards.md
- [ ] `T-004` Workflows determinísticos em JS — três workflows separados: plan-card, implement-card, finalize-card · → threads/_notas-de-cards.md
- [ ] `T-005` Worktree obrigatório em card que escreve — hoje é instrução (`isolation: "worktree"`), não imposição. Roadmap#5.
- [ ] `T-006` Implementação noturna limitada — só cards pré-aprovados, worktree próprio, commit local no máximo, sem merge/push/deploy. Roadmap#3. **Bloqueado por T-001 e T-003.**

---

## ✅ Feito

- [x] `T-045` Piloto Cartographer — fechado; decisão: portar ideias, sem instalar o Cartographer · → threads/_notas-de-cards.md

- [x] `T-050` Timeout padrão do runner Opus mata parecer válido — **resolvida e validada pelo dono
  em 2026-08-31.** A revisão real terminou em 267,1s com o novo teto padrão de 600s, e o smoke do
  runner instalado comprovou `TIMEOUT=600s` e `claude-opus-5`. Uma task Codex nova carregou
  naturalmente a 0.22.7, que preserva a correção; o dono confirmou o fechamento. Nenhuma chamada
  Opus foi repetida. Histórico em `memory/wiki/threads/_concluidas/T-050-opus-timeout.md`.
  @frente-opus-timeout

- [x] `T-049` Instalador rejeita caches corretos por artefatos gerados pelo host — **validado pelo
  dono em 2026-08-31 numa task Codex nova.** A skill 0.22.7 foi carregada pela frase natural
  *"onde paramos?"* e a retomada foi confirmada na ordem `memory/MEMORY.md` → board → thread
  T-049. Verificação fresca repetiu `rc=0` nos caches reais Codex e Claude, ambos habilitados em
  0.22.7, contra o pacote limpo no SHA `41ed5da`. A reinstalação redundante foi evitada; Kimi,
  commit, push e restart permaneceram fora. O smoke Claude continua separado e só pode ocorrer
  depois de um restart autorizado. @frente-auditoria-nativa
- [x] `T-048` Auditores nativos de remoção e adoção graph-first — fechado; 0.22.5 publicada e instalada · → threads/_notas-de-cards.md
- [x] `T-046` Lint de coerência separa `.in_use/<PID>` de divergência real — fechado; 0.22.4 publicada e instalada nos dois hosts · → threads/_notas-de-cards.md
- [x] `T-024` O painel de revisão não está funcionando — fechado; a causa raiz foi para o T-010 · → threads/_notas-de-cards.md
- [x] `T-003` Piloto end-to-end — fechado; o card era o próprio experimento, nada a testar · → threads/_notas-de-cards.md
- [x] `T-008` Lint de coerência interna — fechado; teste: edite algo em orq/ e rode lint-coerencia.py · → threads/_notas-de-cards.md
- [x] `T-011` Atritos do primeiro `/orq:init` em projeto de terceiro — fechado; teste: /orq:init em projeto novo tem que criar o _schema.md · → threads/_notas-de-cards.md
- [x] `T-012` Piloto dos loops A e B — fechado; o ciclo inteiro rodou pela primeira vez na 0.11.0 · → threads/_notas-de-cards.md

_(vazio — o board nasceu em 2026-07-26)_

---

## 📦 Arquivado

_(nada abaixo desta linha conta no progresso da statusline)_
