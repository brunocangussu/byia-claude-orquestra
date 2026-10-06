# MEMORY — índice da wiki

> **Leia esta página primeiro ao retomar.** Cada linha diz onde a verdade mora.
> Contexto é descartável; isto aqui não é.

**Projeto:** Orquestra (`orq`) — framework multi-host para desenvolvimento orientado a board.
**Versão:** 0.31.0 — fonte do T-149 entregue na main/local e em origin/main (`a81026f`), com elenco padrão versionado, R2 aprovada com ressalvas documentais encerradas e gates frescos verdes (870 testes, manifesto e lint). Instalação e validação prática permanecem separadas. Sem publicação, instalação ou restart nesta frente. A versão 0.27.10 foi publicada em `origin/main` no commit `df98d9c`, instalada e verificada nos hosts Claude e Codex em 2026-09-22. Processos novos carregam a versão instalada; sessões já abertas continuam no cache anterior até o próprio restart. ⚠️ **Instalado não é carregado:** cada host só roda uma versão nova depois do próprio restart · **board instalado em** 2026-07-26 · **último checkpoint:** 2026-10-06 (T-149) · **host padrão a partir de 2026-08-09: Codex**.

**T-149, 2026-10-06 — elenco padrão versionado entregue:**
- Fonte 0.31.0 em `a81026f`, integrada por fast-forward e confirmada no GitHub.
  Gates frescos no worktree e na main: 870 testes, manifesto estrito e lint exit 0.
  R2 Opus 5.5: aprovada com duas ressalvas documentais encerradas; sem retry.
- Catálogo único por host, com modelo/effort/via; adoção explícita por projeto:
  “Siga o elenco padrão desta versão do Orquestra.” Preserva Manager, papéis
  adicionais, overrides e projetos que continuem no perfil anterior.
- Card em VALIDATE: faltam ativação autorizada e teste prático dos hosts.
  Nenhuma publicação, instalação, restart ou migração de elenco ativo.
  Handoff: `../docs/handoff-T149-elenco-padrao-2026-10-06.md`.

**T-148, 2026-10-05 — conciliação entregue e ambiente organizado:**
- Fonte 0.30.0 em `d760069`; evidências/baselines em `d67cd99`. Main/GitHub incluem os
  commits originais do Claude por merges de ancestralidade `0fc58ca` e `e4a85eb`, sem
  alteração da árvore conciliada. Gates frescos: 838 testes, manifesto e lint verdes;
  bancada JEV: 31 testes e preflight verdes, sem campanha ou adoção.
- Checkouts de 8 para 2: main e T-144 com processos vivos. Cinco snapshots nativos
  recuperáveis; T-089 preservado na branch e em handoff público/backup local. Ledger
  e chave do medidor continuam privados. Nenhuma instalação ou restart por esta frente.
- Próximo ponto: validação prática dos cards em `[?]`; resumo e recuperação em
  `../docs/handoff-T148-main-organizada-2026-10-05.md`.

**T-144 / T-146, 2026-10-04 — medidor de progresso portátil (`@frente-mods`):**
- Feito a pedido do dono, que se perdia no `/goal` e no Loop B. A referência foi o Goal Meter, um
  mod só do Claude; a solução é portátil para Claude, Codex e Orca.
- Ledger por card/goal em `.orq/progress/`. A fase vem do board e o percentual dos passos do plano.
  Vistas: `show`/`watch`, hook consultivo com lembrete único e segmento na statusline do Claude.
- Fases 1 e 2 originaram a branch `claude/t144-medidor-progresso`, na worktree
  `../byia-claude-orquestra-worktrees/t144-medidor-progresso`: `ba523e9` (0.28.0) e `064e726`
  (0.29.0, versão candidata). As duas candidatas foram conciliadas na fonte
  0.30.0 pelo T-148; instalação e validação prática dos hosts continuam pendentes.
- Cards em `[?]`; fase 3 = `T-147`. A conciliação de fonte foi entregue pelo T-148, sob delegação do dono:
  `../docs/handoff-claude-T-144-T-146-conciliacao-2026-10-04.md`.
- O elenco do host Claude agora usa `gpt-6.1-sol@xhigh` no planner·sistema e no reviewer.
- Thread: `wiki/threads/T-144-mods-claude-code.md`.

**T-098 / T-131, 2026-09-24 — revisão e acesso CLI registrados:** índice, board canônico e threads
relidos após compactação. Claude CLI atualizada de 2.1.278 para 2.1.280, Opus 5.5 comprovado por
`modelUsage`. Migração local foi renomeada externamente para `t137-capacidade-modelos-runner`, sem
perda aparente dos arquivos; conciliar referência com T-131 antes de nova escrita no produto.
Sem bump/commit/push/cache; R1 autorizada executou cinco lotes Opus5.5, sem retry, com quatro grupos
de correção auditados. Codex CLI global atualizada de 0.153.4 para 0.156.1, autorizada; Sol6 e Luna6
responderam às duas sondas únicas em `low`, exit0, sem ferramentas/retry. Config, hooks e elenco
preservados; acesso comprovado não ativa papéis. Benchmark em `../docs/plano_T-098-benchmark.md`: regras e
Opus e JEV medidos; chave no Acesso às Chaves, autenticação confirmada. Uma chamada Jev 1.13.0,
24 casos fictícios, 22/24 acertos, 8/8 alto risco, sem retry; US$ 0,00025074 estimados, sem ativar
roteamento. A2 aprovada para avançar; protocolo/briefings em `../docs/experimentos/T-098-A2/`.
Autoria Terra + revisão Opus 5.5 autorizadas e executadas, 1 chamada cada; amostra reprovada.
Quatro causas-raiz da R1 em `../docs/experimentos/T-098-A2/auditoria-revisao.md`.
A amostra R2 foi corrigida localmente; revisão Opus adicional em 2026-09-25 retornou JSON
válido `BLOCKED`, por moldes de classe, dois gabaritos ambíguos e cobertura desigual de risco.
JEV/Luna A2 seguem 0/4 cada. O custo Opus R2 de tabela foi US$ 1,636352, anômalo e sem causa
provada; auditar antes de novo gate externo. Ver `../docs/experimentos/T-098-A2/auditoria-revisao-r2.md`.
T-138 avaliou Agency Agents no SHA `053ddbb`: recomendar perfis seletivos, não outro Manager;
relatório em `../docs/analise_T-138-agency-agents.md`; piloto seletivo aprovado, perfil API Tester v1
e contratos B2 em `../docs/experimentos/T-138/`, ainda sem execução, instalação ou chamadas novas. Elenco vivo e
worktrees T-096/T-123/T-125/T-128/T-130 preservados; estados nas threads T-098 e T-131.

**T-139, 2026-09-25 — especialização dos papéis centrais:** pedido de ampliar a análise do
Agency Agents para Manager, Planner e Reviewer, sem confundir perfil de instruções com modelo
treinado. Comparação com contratos reais da Orquestra e desenho de ablation por papel em
`wiki/threads/T-139-especializacao-papeis.md`. Direção aprovada: Manager único,
skills compactas por domínio e gates preservados. Worktree isolado T-139 contém
compositor e skills de Planner/Reviewer em piloto, ainda sem instalação, mudança de
elenco ou adoção. Dois baselines sintéticos do Planner (Astra `max` e Luna
`medium`) atingiram 5/5; os casos não discriminam ganho. O runner Anthropic
recusou `haiku` ao observar `sonnet` no uso efetivo; T-098 A2 segue bloqueado e T-138 B2
não executado. Suíte 432/432; skill de domínio exige opt-in `--pilot T-139` e
os blocos de despacho fixam `none` por chamada para não herdar piloto de outro
card; lint do worktree candidato acusa apenas cache
0.27.10 divergente, sem bump/instalação. Retomar pela thread para os limites
da bancada: `--ignore-user-config` reduziu o preflight sintético a 17.381
tokens de entrada e zero evento de ferramenta, mas não deu recibo do modelo.
R-004 foi congelado; A/B rejeitado antes do envio por incluir instruções
internas do plugin. R-005 e P-003 foram retiradas por risco de efeito-teto;
M-001 só serve como smoke de autoridade. R-006 foi retirada sem chamada:
seu enunciado entregava os dois defeitos. R-007 cega foi composta localmente
com oráculo separado; a autorização pedida para R-006 está obsoleta, não
transferível. P-004 usa snapshot histórico anterior ao T-071, mas foi
rebaixada a controle local por risco alto de efeito-teto. O gate de egress
R-007/P-005 foi autorizado depois, mas o ensaio não gerou prova de ganho;
ver o checkpoint final da thread.
RED/GREEN local corrigiu a perda do LF final em `$(...)` nos dois comandos;
o recibo agora corresponde à variável shell. Novo RED/GREEN corrigiu o caminho
padrão sem `ROLE_SKILL`/`ROLE_PILOT`: ambos davam briefing vazio; agora usam
`none`, com 429/429 testes. Falta prova da sessão Codex e de qualidade A/B.
P-005 substitui P-004 como candidata Planner, com fixture/rubrica separadas
e A/B compostos apenas localmente; nenhuma inferência foi feita.
M-001 permanece smoke: seu enunciado antecipa a rubrica e o contrato-base
do Manager já excede sozinho o teto de 16 KiB do runner Anthropic.
M-002 foi congelado, mas a pré-auditoria o rebaixou a controle de autoridade
por efeito-teto provável; A/B não executado. R-007/P-005 seguem candidatos.
Em 2026-09-26, três chamadas sintéticas Luna `low` (R-007/A, R-007/B,
P-005/A) registraram erro inicial de code-mode desativado; R-007/B e
P-005/A recusaram trabalhar sem ferramentas. P-005/B não foi chamada,
sem retry. Os JSONL/saídas foram preservados no worktree T-139 e a
comparação foi invalidada, sem alegar ganho nem economia. T-139 está
em `[~]` para corrigir o protocolo local; qualquer novo envio exige
gate delimitado.
O preflight local seguinte criou os casos fictícios R-008/P-006, com
workspaces A/B e rubricas separadas, gate JSONL fail-closed e runner de
uma chamada com hashes aprovados. A bancada passou 30/30 testes e a suíte
do plugin 432/432; nenhuma inferência nova foi feita. A prova local de
sandbox não comprova a via `codex exec` nem o modelo efetivo. Hashes e
limites estão no resultado preliminar do worktree; novo A/B exige gate.
O manifesto R-008/P-006 também vincula rubrica e teto; recibos vinculam
resposta/plano e a nota A exige seis critérios com evidência antes de liberar
B. Bancada local 44/44, sem nova chamada externa ou ganho demonstrado.
Controle limpo R-009 do Reviewer preparado localmente, com patch reversível,
oráculo separado e execução file-backed dos dois consumidores. Controle
limpo P-007 do Planner confirma quatro anchors 0.4.2 e mutação detectada;
bancada 50/50. Terceiras tarefas R-010 (override de autoridade) e P-008
(thread de worktree apontando à main) também preparadas com RED/GREEN;
bancada 55/55. Pré-auditoria bloqueou B com modelo/effort diferente de A ou
recibo A sem vínculo ao snapshot; bancada 58/58. Faltam respostas para
replicação e gate novo para qualquer A/B. Seis snapshots congelados em
`../docs/T-139-preflight-freeze.json`, recomposição local 59/59.
Em 2026-09-26, testes de entrega exata dos bytes A/B ao CLI fictício elevaram a
bancada a 62/62; o runner também recusa manifesto divergente do congelamento,
mesmo com hashes novos na chamada. R-008/A foi a única chamada nova de modelo, com recibo
estrutural válido, workspace intacto, 117.347 tokens de entrada (99.840 em
cache) e nota local provisória 1/6; modelo efetivo ainda sem prova. R-009/A
foi barrada antes da CLI por revisão de permissões: instruções/patch internos
exigem autorização de egress mais específica. Nenhum retry, B ou outro caso
foi executado. Estado e recibos na thread T-139 e no worktree isolado.
Após gate específico do dono, R-009/A e R-010/A produziram recibos
estruturais válidos, ainda sem nota independente; P-006/A foi inválido
(`PLAN_MISSING`, plano vazio) por capacidade de escrita não comprovada do
perfil isolado. Na etapa seguinte, a falha de escrita foi reproduzida sem
modelo e corrigida na bancada macOS com leitura mínima das Command Line
Tools; P-007/A e P-008/A foram chamadas uma vez cada e saíram válidas.
Dos seis A, cinco têm recibo estrutural válido; P-006/A permanece inválido,
sem repetição. Bancada T-139 73/73, suíte do plugin 432/432, manifesto
estrito e Ruff verdes; lint acusa somente divergência fonte/cache 0.27.10.
Cinco briefings de nota independente foram preparados **sem envio**, com
hashes em `../docs/T-139-inventario-egress-avaliacao-A.md`. Falta gate
específico para Anthropic via Claude CLI e pontuação independente; B e
adoção não autorizados. O gate local de B agora exige indicadores booleanos
de falso achado crítico e violação de escopo na nota A, sem bloquear B por
um erro do baseline. P-009, terceiro caso sintético Planner, foi preparado e
testado somente em bancada local, fora dos seis snapshots congelados. O
gerador de nota agora recusa marcadores estruturais na resposta/plano;
cinco briefings preservaram os hashes. P-009 tem snapshot de preflight
separado `LOCAL_ONLY`, sem registro no runner nem egress; bancada 79/79,
sem chamada externa ou nota. Recibos e JSONL estão no worktree isolado;
ver a thread.
Após aprovação específica do dono, os cinco briefings A foram enviados uma
única vez cada ao Anthropic via Claude CLI `opus` (modelo comprovado
`claude-opus-5-5`), sem ferramentas nem retry. Notas auditadas: R-008 1/6,
R-009 2/6, R-010 5/6, P-007 5/6 e P-008 5/6. R-009 devolveu os dois
indicadores booleanos em objetos; a nota auditada converte apenas
`present`, preservando o parecer bruto. Hashes de pacote, recibo,
resposta/plano e rubrica conferidos nos cinco casos. P-006/A segue
inválido; P-009 segue apenas local. B, segunda avaliação cega, replicação,
custo até aceite e adoção continuam pendentes; nenhum ganho está provado.
Após novo gate do dono em 2026-09-26, cinco B congelados foram chamados uma
vez cada via `codex exec`, sem retry, e deram recibos estruturais válidos.
Cinco pacotes cegos B foram preparados localmente; a avaliação independente,
replicação e custo até aceite ainda faltam. O modelo efetivo não consta dos
recibos; não inferir ganho nem economia. O estado atual está na thread T-139.
Auditoria antes da pontuação B encontrou caminhos que revelavam A/B em
três briefings A antigos e contradição entre rubrica e memória do controle
R-009. Dez pacotes A/B v2 foram neutralizados e auditados; R-009 não vale
como controle limpo, e R-008/B tem achado alto falso verificável. Ver
`../docs/T-139-auditoria-local-B.md`; avaliação independente e adoção seguem
pendentes. R-011 substitui localmente o controle contraditório: patch
reversível e casos sucesso/falha/vazio testados, hashes A/B congelados localmente e
nenhuma nova chamada de modelo; falta gate para execução e pontuação.
Nos cinco pares A/B já executados, B somou 700.041 tokens de entrada e
11.258 de saída, contra 594.710 e 7.648 em A; os JSONL não provam o
modelo efetivo. Não alegar economia nem custo até aceite com essa amostra.
O próximo gate proposto está inventariado em
`../docs/T-139-inventario-egress-pos-B.md`: cinco pacotes fixos de
pontuação, sem retry e sem novas chamadas A/B; R-011 fica para gate próprio.
Em 2026-09-27, duas notas cegas adicionais foram enviadas uma vez cada:
R-008/A à Codex CLI (`gpt-6-astra@max` pedido, modelo efetivo não exposto) e
M-004/A à Claude CLI (`claude-opus-5-5` comprovado). R-008 recebeu 5/6 na
reauditoria local após correção RED/GREEN do validador, que rejeitava `0/1`
apesar de o briefing pedir `0/1`; o recibo original inválido foi preservado.
M-004 trouxe corpo 7/7 provisório, mas a saída cercada por Markdown viola
JSON puro e o recibo segue inválido. Sem retry, B, adoção ou prova de economia;
estado e hashes na thread T-139 e na auditoria do worktree isolado.
O dono aceitou a reauditoria R-008/A 5/6. A nota derivada vinculada às
evidências externas passou no gate local, e o preflight de R-008/B congelado
(9.537 bytes) passou sem chamada; egress de B exige gate específico.
O dono autorizou esse gate: R-008/B foi enviado uma única vez pela Claude CLI
ao `claude-opus-5-5`, sem retry. Resposta e recibo estão no worktree T-139;
o runner marcou `STRUCTURAL_ONLY`, não qualidade aprovada. O dono autorizou
em seguida a nota cega de B: uma chamada Codex CLI solicitando Astra@max,
sem retry, com zero ferramentas e parecer estrutural válido. B recebeu 5/6,
igual a A; ambos omitem a mutação explícita. B custou 18,7% mais na geração
segundo a Claude CLI. Baseline mantido; próximo desenho local exige amostra
inédita e controle sem defeito para testar uma regra curta de mutação. A CLI
não comprovou o modelo efetivo do avaliador. Não houve adoção.
Em 2026-09-28, o pacote A/B/C R-011/R-012/P-009 ganhou runner local de uma
chamada com invocação congelada por SHA e gates A→B→C; CLIs falsas testaram
as duas vias sem egress. O modelo efetivo do Codex, a nota cega e o custo
até aceite ainda faltam. Ver o checkpoint final da thread T-139; sem adoção.
O gate local de nota cega A/B/C foi acrescentado depois: pacote sanitizado,
avaliação cross-vendor com recibo/transcript vinculado e custo acumulado
até o teto cego, tudo testado com CLIs falsas. Ainda não há notas reais,
custo até aceite humano, réplica ou prova do modelo efetivo Codex; ver a
thread T-139. Nenhum egress ou adoção nesta etapa.

**T-044 aprovado para integração, 2026-09-21:** os seis bloqueadores confirmados da R2 foram
corrigidos com RED/GREEN e mutantes específicos; a suíte fresca passou 414/414, o manifesto estrito
e `diff --check` ficaram verdes. A R3 sanitizada saiu uma única vez em quatro lotes e três foram
aprovados. O único bloqueio alegado no lote de produção foi descartado pela auditoria do Manager:
`SessionStart(source=clear)` persiste a resposta no caminho real, e a prova direta confirmou
`additionalContext`, ausência do aviso falso, nenhum marcador pendente e estado padrão. A versão
`0.27.10` foi escolhida porque `0.27.9` está reservada ao T-095 e nenhum worktree, branch ou tag
reservava `0.27.10`. Publicação, instalação e restart permanecem fora desta etapa.

**Release e validação do `T-044`, 2026-09-22:** `origin/main` foi confirmado em `df98d9c`; os
marketplaces Git dos dois hosts resolveram a 0.27.10 e os caches passaram byte a byte contra um
checkout detached limpo desse SHA. Processos novos do Claude e do Codex responderam aos smokes
sintéticos; `/hooks` mostrou o `SessionStart` do `orq@orquestra` ativo e apontando para
`0.27.10/scripts/context-guard.py`. Os sete testes focados de runtime passaram em cada cache, e o
contrato documental passou na fonte limpa. O cache Codex 0.27.8, citado por tarefas vivas, foi
restaurado lado a lado depois de o atualizador removê-lo. Windows real permanece **não validado**.

**Fechamento administrativo do `T-097`, 2026-09-22:** os 23 checkouts sujos foram preservados em
tags anotadas e removidos sem `--force`; a raiz compartilhada ganhou um snapshot não mutante antes
da reconciliação. Após o fechamento surgiu o checkout isolado e sujo `T-096`, que foi preservado:
o estado atual correto é raiz + T-096 ativo, duas branches locais e 28 referências
`archive/t097/*`. Quatro refs remotas históricas continuam deliberadamente intactas. O estado final
da raiz está em `archive/t097/root-shared-pre-fast-forward-20260922`, e este fechamento não altera
a versão 0.27.10, os caches instalados nem o runtime dos hosts.

**Checkpoint de recuperação, 2026-09-16 — raiz reconciliada:** a `main` local estava quatro commits atrás e o fast-forward era barrado por nove alterações locais sobrepostas a `MEMORY.md`, `fixes-history.md` e `KANBAN.md`; não havia outra tarefa ativa. O estado antigo foi preservado na branch local `codex/root-recovery-20260916` (`793e1f3`), somente os conteúdos ainda válidos foram reaplicados sobre `origin/main` e publicados em `2b5ee01`. A raiz ficou limpa e sincronizada; 396/396 testes, manifesto estrito e lint passaram. O reviewer do host Codex permanece temporariamente em Opus conforme decisão do dono. Retomar pelos cards em espera `T-094`, `T-062` e `T-047`.

**Candidata 0.27.7, 2026-09-15 — `T-076`:** o dono aprovou a opção B: board operacional no
checkout principal e threads na frente proprietária. Os dois bloqueios da R5 foram corrigidos em
RED/GREEN: o checkpoint só permite handshake sem thread quando não há card ativo desta frente, e a
skill usa a thread `T-NNN.md` apontada pelo card, com a frente em `@frente-<slug>`. Contrato +
guardião fecharam 130/130 nos Pythons 3.12 e 3.9.6; a suíte executou 374 testes e manteve somente as
quatro falhas basais externas. A única R6 cobriu 240.137/240.137 bytes em 28 lotes; todos saíram `0`
e provaram `claude-fable-5-1`. Foram 6 `APROVADO` e 22 `APROVADO_COM_RESSALVAS`, sem bloqueador.
O Manager auditou as ressalvas como riscos não bloqueantes de manutenção, cobertura e clareza
histórica. O review fecha **APROVADO COM RESSALVAS**; não executar R7. Plano em
`docs/superpowers/plans/2026-09-13-t076-board-principal.md` e estado em
`wiki/threads/T-076-board-principal.md`. O contador fechou em `6/6 · extensão: +4`; a candidata
foi autorizada para bump, commit, push e integração. Publicação, instalação, restart e validação
comportamental permanecem em gates separados.

**Correção documental, 2026-09-15 — `T-070`:** a frase sobre o antigo painel de três revisores foi corrigida para o passado, preservando as três ocasiões e registrando a aposentadoria pelo T-051. A revisão Fable 5.1 foi **APROVADA**, sem bloqueadores. Evidência em `wiki/threads/T-070-painel-historico.md`.

**Release 0.27.8, 2026-09-15 — `T-071`:** publicada em `origin/main` no commit `470eba9`. O contrato de cabeçalho arquivado exato e cercas Markdown foi implementado em RED/GREEN no worktree `codex/t071-archive-heading`, reconciliado com a `main` após o T-076. A divergência entre `splitlines()`/tradução universal do Python e os `awk` foi corrigida com leitura que preserva newlines e divisão exclusiva por LF. A R2 Fable aprovou os três lotes sem bloqueadores. Testes localizados passaram nos Pythons 3.9 e 3.12; a suíte final executou 396 testes e manteve apenas as três falhas basais do T-081. Retomar em `wiki/threads/T-071-secao-arquivada.md`. Instalação, restart e validação prática permanecem em gates separados.

**Checkpoint de recuperação, 2026-09-12 — `T-094`:** após compactação, índice, board e thread foram relidos. O mini-revisor Luna segue sem implementação; a sonda sintética marcou 12/12 para Luna e Astra, sem prova de economia. A dependência `T-062` permanece em 6/6 revisões, sem aprovação, com um bloqueador documental. O dono questionou o termo “canário” e a demora e pediu priorizar a conclusão dessas tarefas. Retomar em `wiki/threads/T-094-mini-revisor-luna.md`; não inferir autorização para R7, release ou mudança global.

**Checkpoint de recuperação, 2026-09-08 — `T-078`:** os seis hooks do AI-Memory no Codex foram
reconfirmados por configuração e por ciclo real persistido; Claude e Codex continuam gravando no
SQLite local. O dono conhece a alternativa de religar o claude-mem no Codex, mas mantém por ora o
piloto isolado: AI-Memory nos dois hosts e claude-mem somente no Claude Code. A frente do Claude
avança separadamente a coexistência dos hosts (`T-085`–`T-092`); retomar o piloto em
`wiki/threads/T-078-ai-memory.md`, sem misturar as duas frentes.

**Checkpoint de recuperação, 2026-09-07:** a fila “Esperando você” foi auditada: `T-064`/`T-066`
saíram como concluídos, `T-023`/`T-026` fecharam por evidência posterior, e restaram só `T-065`
mais os testes conversacionais `T-025`/`T-020`/`T-030`. A prova técnica final do `T-075` também
apareceu no log real: com o pool `3/3`, uma quarta sessão esperou e assumiu a vaga 12 ms após a
liberação. Retomar em `wiki/threads/T-054-economia-tokens.md` e `wiki/threads/T-072-claude-mem.md`.

**Fechamento posterior, 2026-09-07:** o dono autorizou o `T-065` recomendado; os globais foram
reduzidos com backups datados e ficaram abaixo de 3 KB, preservando as regras essenciais. A frase
natural **“quais as possibilidades?”** acionou o cardápio por situação e fechou o canário do
`T-025`. Em “Esperando você” restam somente `T-020` e `T-030`. Detalhes nas threads T-054 e T-025.

**Checkpoint operacional, 2026-09-07:** após `pull --ff-only`, a 0.27.3 foi reinstalada nos dois
hosts e os dois caches passaram no verificador vindo do checkout limpo de `4229b76`. No host Codex,
`gpt-6-astra@max` foi mantido: `codex exec` aceitou o effort real via
`-c model_reasoning_effort="max"`, anunciou `reasoning effort: max` e saiu `0`. A flag literal
`--effort` não existe na CLI 0.153.4; essa é diferença de sintaxe, não recusa do effort.

## 🟢 Trabalho mais recente (2026-09-07) — `T-074` · uma camada de memória por host, e dois cards nascidos de conferência

**`T-074` (validar):** o claude-mem fica ligado **só no Claude Code**. No Codex ele foi desligado
para o piloto do `T-078` medir uma camada só — rodar as duas em paralelo contamina a comparação,
porque uma injeta memória que muda o que a outra captura. O desligamento tem **dois** pontos: o
`enabled` do plugin e um `[[hooks.UserPromptSubmit]]` escrito direto no `config.toml`, fora do
plugin. Quem parasse no primeiro seguiria capturando a cada prompt achando que desligou.

⚠️ **A decisão foi revertida por outra janela no mesmo dia e reaplicada.** A sessão que conduzia o
`T-075` leu `enabled = false`, concluiu que fora acidente do instalador e religou. Nenhuma das duas
errou: uma cumpria o card, a outra cumpria o checklist de update de plugin. O `config.toml` ganhou
**nota inline ao lado da chave**, porque quem audita config de host não lê a wiki. O protocolo de
várias janelas (`T-013`, `T-032`) cobre board e worktree — **não cobre configuração de host**.

**Dois cards nasceram de conferir em vez de aceitar:** `T-081` — a chave
`CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES` que a wiki mandava configurar é aceita pelo endpoint de
settings e **lida por ninguém**; o filtro real mora no modo e mexer nele muda a **captura**, não a
leitura. `T-082` — o lint acusou divergência de cache que era `__pycache__` da véspera; a guarda
`sys.dont_write_bytecode` impede **gerar**, não **comparar**.

Retomar em `wiki/threads/T-072-claude-mem.md`.

## 🟡 Trabalho anterior (2026-09-06) — `T-079` + `T-080` · elenco no GPT-6 Astra e a guarda que impede o preset de mentir

**`T-079` (fechado):** quatro células do elenco passam a `gpt-6-astra@max` — `planner·sistema` nos
dois hosts, `reviewer` no Claude, `planner·interface` no Codex — e o Fable é identificado como
**5.1**. O `reviewer` do host Codex **continua Anthropic**: o dono recuou de pôr Astra ali ao ver
que seria OpenAI revisando OpenAI. O defeito que dava valor ao card não estava no pedido:
`revisar.md` chamava o runner **sem `--model`** e o Codex revisava com **Opus** enquanto o elenco
declarava `fable` — provado fechado no cache instalado (`OPUS_MODEL=claude-fable-5-1`).

**`T-080` (fechado):** guarda no lint impede a tabela viva e o preset ativo de divergirem enquanto a
linha `Perfil ativo` diz "sem desvio". Compara contra o preset **ativo** e exige que os desvios
declarados sejam **exatamente** o conjunto de diferenças. Validado por demonstração.

⚠️ **`gpt-6-astra` como PLANNER nunca rodou comprovadamente.** O mecanismo `codex exec -s read-only`
só foi exercitado como revisor; nas rodadas de planejamento o runtime não expôs a variante nem o
effort. Uma das revisões rodou em `xhigh`, não no `@max` que o elenco declara. Não confundir
configurado com exercitado.

Retomar em `wiki/threads/T-079-gpt6-astra.md` (cobre os dois cards). Planos aprovados em
`docs/plano_T-079-elenco-astra.md` (ERRATA no topo vence o corpo) e `docs/plano_T-080-guarda-preset.md`.

## 🟡 Trabalho anterior (2026-09-05) — `T-078` · AI-Memory 2.0

**Uma segunda camada de memória automática entra em teste, ao lado do claude-mem.** O dono trouxe
o `AI-Memory 2.0` (akitaonrails, MIT, Rust) e pediu para rodar pelo ciclo: planner → revisor →
decisão dele. Retomar em `wiki/threads/T-078-ai-memory.md`.

**O que o ciclo produziu, e vale não re-litigar:** o planner recomendou **não** substituir a wiki
curada (*"não há causa raiz demonstrada"*), e o revisor derrubou o desenho do piloto por
esforço sem teto e critérios manipuláveis. A síntese virou **3 estágios com gate**. O Estágio 0
passou nos 4 critérios num sandbox descartável, com checksum do binário conferido.

⚠️ **Depois disso, o dono decidiu contra a recomendação:** instalar **global, capturando em todos os
projetos já** — ciente de que isso pula a validação em estágios e inclui projetos com dado de saúde.
Decisão registrada como dele, executada como pedido. **O que não muda:** `llm: disabled,
embedding: disabled` — nada do capturado sai da máquina.

**Estado real:** daemon `launchd` persistente rodando; **Claude e Codex capturam**. No Codex, a
causa era o `~/.codex/hooks.json` **gerenciado pelo app Terminals**, que reescrevia o arquivo e
apagava hooks de terceiros. Os 6 hooks do AI-Memory foram movidos para o `~/.codex/config.toml` e
aprovados pelo gate nativo. A sessão final, iniciada às 12:18, gravou no mesmo ID `session-start`,
`user-prompt`, `pre-tool-use`, `post-tool-use` e `stop`; o banco chegou a 5 sessões Codex. O teste
técnico passou; falta usar por 1–2 semanas e reavaliar o ganho real contra o claude-mem. Para
essa medição valer, o claude-mem foi **desligado no Codex** em 2026-09-07 (`T-074`): as duas
camadas em paralelo se contaminam, porque uma injeta memória que muda o que a outra captura.

## 🟢 Trabalho mais recente (2026-09-02) — @frente-economia · `T-054`…`T-075`

**A memória do Orquestra tinha crescido a ponto de ser ela quem consumia a janela.** O dono trouxe
uma análise medida (`docs/brief-economia-tokens-2026-09-02.md`) e a frente nasceu dela.
Retomar em `wiki/threads/T-054-economia-tokens.md` e `wiki/threads/T-072-claude-mem.md`.

**Entregue e verificado:**
- **Teto de 240 bytes por card + 48 cards migrados** — board de **104,7 KB → 13 KB**, de 28,4k para
  3,6k tokens. A nota foi movida **íntegra** para a thread de cada card; reconciliação byte a byte
  por ID deu **48/48**, sem órfã nem duplicata. O ganho não é disco (o texto mudou de arquivo): é
  que o board é relido em **toda** retomada e **toda** compactação — ~25k tokens poupados por leitura.
- **`test_kanban_status.py`** — o parser do board, contrato central do projeto, não tinha teste
  nenhum. Suíte 201 → **215**.
- **`T-064`**: a Matriz vence qualquer skill de spawn instalada no host (medido: 256 threads de
  sub-agente no Codex em agosto, uma por tarefa em vez de por card).
- **`T-072`/`T-073`**: o claude-mem voltou ao catálogo **com papel escrito** (rede de segurança; a
  wiki vence em conflito) e o gatilho *"lembra quando"* passou a **nomear a busca** — antes dizia
  "consulte alguma busca do host", e por isso nunca disparou em 79 sessões.

**Versão `0.26.0` bumpada nos quatro lugares. NADA commitado, publicado ou instalado — depende do
dono.** Três gates verdes: 215 testes · `validate` · lint.

**Decidido com o dono, não re-litigar:** autocompactação **recusada** (checkpoint + `/clear` já
resolve melhor) · `codebase-memory` e `serena` **ficam os dois** (~570 tok/sessão) · caveman **nunca
esteve instalado** · teto de card é **240 bytes**, não 200.

⚠️ **Incidente aberto:** o claude-mem ficou **22 h sem gravar nada, respondendo `status: ok`** — bug
do plugin (sessão marcada `completed` enquanto a conversa continua). 126 de 481 sessões têm o mesmo
padrão. **A wiki segurou tudo e nada se perdeu**, o que é a prova prática da divisão de papéis.
Virou o `T-075`: detectar memória parada pelo **carimbo do banco**, nunca por health. É o próximo a
planejar.

**2026-09-04 — elenco revisado e repositório podado.** O `manager` é **sempre escolha do dono**
(`/model`) nos dois hosts; mudança pontual de papel se pede em conversa, e o padrão é o registrado
no `_elenco.md`. O **`T-077`** destravou o Fable no host Codex: o runner Anthropic passou a aceitar
`--model` com prova por alias, então `planner·interface` e `reviewer` lá são `fable` de fato — falta
a primeira chamada real. Suíte **219**. O repositório foi de **10 worktrees para 1** e de 11 branches
para 3; preservados o `t044` (1 commit fora da main, card aberto) e o backup do `t049` (conteúdo
difere do que entrou na main). Diffs do que foi removido em `docs/arquivo-worktrees-2026-09-04/`.

⏭️ **Falta:** validação em uso de `T-056`, `T-064`, `T-072`, `T-073`; planejar o `T-075`; e o dono
decidir sobre `AGENTS.md`/`CLAUDE.md` (**nada será cortado sem ele ver linha a linha**).

**2026-09-05 — execução do `T-075`:** `claude-mem` `13.24.1` instalado nos dois hosts, Bruno
Vascular excluído e detector metadata-only com 12 testes entregue. O `UserPromptSubmit` manual
funciona, mas o Codex não dispara o hook do manifesto; fallback no `config.toml` aguarda aprovação
no gate nativo de um chat criado pela interface. Estado literal em
`wiki/threads/T-072-claude-mem.md`; plano em
`../docs/superpowers/plans/2026-09-05-t075-claude-mem-paridade.md`.

## 🟡 Trabalho anterior (2026-09-01) — @frente-elenco · `T-051` + `T-052`

**A `0.24.0` foi construída fora da linha publicada e a `T-052` a reconciliou na `0.25.0`.** Duas
cópias cresceram separadas desde `008fbc9`: a local entregou o `T-051` (`0.24.0`) e a remota chegou
à `0.22.7` pelo trabalho do Codex. O push da `0.24.0` foi **rejeitado**; nada se perdeu, e a
reconciliação é manual, arquivo a arquivo, sobre `origin/main`. Retomar em
`wiki/threads/T-052-reconciliacao.md`.

⚠️ **A `0.24.0` NUNCA foi publicada nem instalada** — quem instalar do GitHub recebe a `0.22.7`. Se
alguma página ainda disser que a `0.24.0` está no GitHub, está errada.

**O que o `T-051` trouxe para a `0.25.0`, em uma frase cada:**
- **Elenco em dois eixos** — `trilha` (`interface`|`sistema`) escolhe o **vendor de quem pensa**;
  `faixa` (`pesada`|`normal`|`leve`) escolhe o **degrau de quem escreve**. Síntese aprovada pelo
  dono: *"domínio decide quem pensa; host decide quem escreve"*.
- **Revisor único, vendor oposto ao host, SEM exceção** — decisão do dono **contra** a recomendação
  do planner. O painel acabou; *"confirmado por 2+"* não existe mais. **Diff com dado sensível fica
  sem revisor** (LGPD impede o vendor oposto): o Manager audita e **declara a ausência** — é
  proibido spawnar revisor do mesmo vendor para tapar o buraco.
- **Kimi aposentado** do produto inteiro. A limpeza na máquina do dono é **dele, depois** do release
  validado e do cancelamento da assinatura: `~/.claude/agents/kimi-revisor.md` · a seção de delegação
  do `~/.claude/CLAUDE.md` · `~/.agents/skills/orq/` · `~/.kimi-code/`.
- **`## Papéis` eliminada** — `## Times por host` é a única fonte, para ler e gravar. Antes, `perfil
  economia` no Codex reescrevia uma tabela que **nenhum consumidor lia**.
- **Custo da prova:** 7 rodadas de review externo, 25 bloqueadores (5→8→4→5→2→1→**0 APROVADO**), com
  os gates **verdes em todas elas**. Os pareceres estão em `wiki/threads/T-051-pareceres.md`.

**Estado honesto: publicada, não validada.** ✅ Commit `78b0fec` (dois pais: `6fde3e3` remoto +
`dcc350b` local) e **push feito** em 2026-09-01 — quem instalar do GitHub agora recebe a `0.25.0`.
✅ **Instalação verificada em 2026-09-02:** `marketplace update` + `plugin update` feitos pelo dono;
cache Claude (`~/.claude/plugins/cache/orquestra/orq/0.25.0/`) e cache Codex
(`~/.codex/plugins/cache/orquestra/orq/0.25.0/`) batem byte a byte com a fonte limpa. O marketplace
do Codex aponta para `bd6d3fc`. ⚠️ **Sessão Codex aberta antes do update segue com a versão antiga
em memória — só sessão nova carrega a `0.25.0`.**
⏭️ **Falta APENAS:** os 6 critérios de aceite em conversa natural (seção 7 da thread `T-051`). Retomar em `wiki/threads/T-051-elenco-por-tarefa.md`.

## ⚪ Trabalho anterior (2026-08-17) — @frente-protecao-contexto

**⚡ ESTADO EM 2026-08-17 — leia isto primeiro:**

- **`T-050` FECHADA — timeout de 600s validado pelo dono:** uma sonda mínima comprovou CLI,
  autenticação e `claude-opus-5` em 6,0s; o briefing real T-102 terminou em 267,1s com exit 0 quando
  executado com teto de 600s, provando que o default de 240s matava resposta válida. A candidata
  0.22.6 aumenta somente o default para 600s e preserva `--timeout`, limite de 16 KiB, kill do grupo,
  comprovação de modelo e fail-closed. Gates fecharam em 185 testes; commit `fbaff1c` chegou a
  `origin/main`; Codex e Claude registram 0.22.6 habilitada e byte-idêntica. O smoke do cache instalado
  anunciou `TIMEOUT=600s` e comprovou Opus 5. A 0.22.5 foi preservada para sessões antigas. Em
  2026-08-31, uma task Codex nova carregou naturalmente a 0.22.7, que preserva o default de 600s, e
  o dono confirmou explicitamente que a T-050 estava resolvida. Nenhuma nova chamada Opus foi feita:
  a revisão real de 267,1s e o smoke do runner instalado já cobriam o comportamento. Histórico:
  `wiki/threads/_concluidas/T-050-opus-timeout.md`.

- **`T-048` FECHADA — 0.22.5 publicada e instalada:** auditores nativos de remoção e adoção graph-first
  aprovados pelo dono. O núcleo offline comum aos três hosts está no worktree isolado; os falsos
  verdes de adoção e remoção viraram testes e a suíte chegou a 184 testes verdes. Opus 5 e Kimi K3
  fecharam GO nos dois auditores. O último achado Kimi — path com surrogate quebrando a escrita
  JSON — foi reproduzido em RED, corrigido e revisto em GO. Gates completos e a validação prática
  autorizada passaram: scan/verify e graph-first/direct-first deram os quatro resultados esperados.
  A release entrou em `origin/main` no commit `0cefa97` e foi instalada em Codex, Claude e Kimi.
  Smokes read-only em processos novos dos três hosts carregaram a skill e retomaram memória/board.
  Caches antigos foram preservados no fechamento e nenhum hook protegido mudou. Na reconciliação de
  30/ago, Codex e Claude continuavam habilitados em 0.22.5 e a cópia Kimi seguia byte-idêntica; o
  cache Codex 0.22.4 já não estava no disco, então sessão antiga que o tenha carregado deve ser
  reaberta. O único achado novo do instalador
  virou T-049: allowlist estrita para `.in_use` e `.codex-plugin`. Histórico em
  `wiki/threads/T-048-auditores-nativos.md`.

- **`T-049` FECHADA — 0.22.7 instalada e verificada em Claude/Codex:** o dono aprovou comparador compartilhado + CLI,
  `.orphaned_at` somente no cache Claude instalado, `.DS_Store` estrito e a promoção para `0.22.7`.
  Implementação TDD concluída no worktree isolado: comparador cross-host, integração no lint,
  comandos/documentação e bump nos cinco anchors. Antes da reconciliação, 200 testes, Ruff, validate,
  lint, identidade AGENTS/CLAUDE e `git diff --check` passaram. Opus 5 real deu GO final em todos os
  recortes. Duas chamadas Kimi K3 isoladas encerraram com `403 weekly usage limit`, sem veredito; o
  dono dispensou explicitamente esse parecer somente para T-049, sem registrar GO fictício. A suíte
  completa de 200 testes e todos os gates de pré-release foram repetidos com sucesso. O commit local
  foi autorizado e criado na branch `codex/t046-auditores-nativos`. Depois disso foram detectados
  caches externos `0.22.6` em Claude e Codex, ambos divergentes e sem os dois novos arquivos do
  verificador; esta task não os instalou. `origin/main` avançou com a T-050 e publicou outra 0.22.6,
  explicando os caches. O rebase sobre `origin/main` preservou a T-050, promoveu a candidata para
  0.22.7 e passou em 201 testes e todos os gates. O push fast-forward autorizado publicou `deabd4d`
  em `origin/main`. No gate pós-release, o SHA remoto final `41ed5da` foi clonado em detached com
  árvore limpa. Claude e Codex já registravam a 0.22.7 instalada e habilitada; ambos os caches reais
  passaram no verificador da fonte com `rc=0`. Cópias descartáveis com um extra inesperado foram
  rejeitadas com `rc=1`, provando o fail-closed sem tocar nos caches reais. A reinstalação redundante
  foi evitada; Kimi e restart permaneceram fora. Em 2026-08-31, uma task Codex nova carregou a skill
  0.22.7 pela frase natural *"onde paramos?"* e retomou na ordem `memory/MEMORY.md` → board →
  thread T-049. O dono delegou a conclusão da validação sem autorizar commit, push ou restart;
  o smoke Claude permanece separado e condicionado a um restart futuro explicitamente autorizado.
  Histórico: `wiki/threads/_concluidas/T-049-verificador-instalacao.md`.

- **`T-046` FECHADA — `0.22.4` publicada e instalada:** o conserto do falso positivo de
  `.in_use/<PID>` entrou em `origin/main` no commit de produto `676846a`. Claude e Codex registram
  `orq@orquestra 0.22.4` habilitado; os 29 arquivos do pacote são byte-idênticos nos dois caches e o
  lint real passou com dois marcadores `.in_use` ativos no Claude. O upgrade Codex abriu uma janela
  em que a sessão atual ainda procurava a `0.22.3`; ela foi restaurada do backup e permanece ao lado
  da `0.22.4`. Versões `0.18.0`–`0.22.2` referenciadas por sessões antigas já estavam ausentes antes
  do upgrade e viraram a T-047 — não tratá-las como recuperadas. **Próximo passo:** retomar T-044
  sobre a base publicada `0.22.4`.

- **`T-037` em VALIDATE — `0.22.3` publicada e instalada:** arquitetura provider-neutral
  reconfirmada pelo dono; remoção do SuperMemory integrada com o guardião estável da T-043 e
  publicada em `origin/main` no commit `3bb1a24`. Codex e Claude estão na mesma `0.22.3`; Kimi recebeu
  o mesmo snapshot. Não há SuperMemory, `sm-search` ou `/orq:lembrar` ativos no produto nem nas
  instruções globais; os resíduos foram preservados em backup recuperável. A suíte de 113 testes,
  gates, comparação dos caches e smokes em processos novos passaram. A candidata T-044/`0.22.2`
  permanece fora. Falta somente a validação prática do dono após reabrir a task.
- **0.22.3 PUBLICADA — `T-043` em VALIDATE:** estado v2 do guardião Codex migra o
  `clear_required` legado para `checkpoint_verified`; checkpoint libera a compactação nativa e
  `SessionStart(source=compact)` reidrata memória/board/thread. Compactação sem checkpoint exige
  recuperação. Hooks Codex nunca bloqueiam: alertam e solicitam checkpoint, após o qual a pessoa
  pode continuar, abrir task nova ou compactar. O ambiente somente Claude é ignorado e o fluxo
  Claude `/clear` permanece intacto. O commit estável `bbcc4cb` foi incorporado à release publicada;
  smoke Codex em processo novo confirmou comportamento consultivo e o smoke Claude-only confirmou
  fail-open. A task atual ainda referenciava o cache `0.22.2`; ele foi restaurado do backup sem
  alterar a `0.22.3`. Falta a validação prática do dono em task reaberta.
- **0.21.0 PUBLICADA — `T-041` em VALIDATE:** template/migração do elenco host-aware,
  resolução host→papel→executor, interface Codex por linguagem natural + `/skills`, diagnóstico em
  sete camadas e memória legada diferenciada de projeto virgem. Runner Opus 5 comprovado em nova
  sessão Codex de projeto externo; Claude/Codex instalados em `0.21.0`, caches idênticos. GitHub
  atualizado e verificado; falta o dono repetir a revisão no projeto real que originou o bug.
- **`T-042` permanece no backlog para 0.23.0:** statusline nativa Codex opt-in começa depois do
  guardião `T-043`.

- **0.20.0 RELEASADA E PUBLICADA** (commit `164387c`, push feito). Instalada e verificada no Claude
  **e** no Codex, cache idêntico ao repo nos dois. O `T-036` está em **VALIDATE**, aguardando só o
  teste do dono: projeto de rascunho → `/orq:init` → tem que dizer *"sua statusline já mostra o
  board"* e **não gravar chave nenhuma**.
- **O dono adotou o Codex como host padrão.** O time do host Codex está em `_elenco.md`,
  `## Times por host` — planner e implementer OpenAI, **revisor `opus` de fora** (a diversidade do
  painel depende disso). ⚠️ **Subagente nativo no Codex é "observado 1×", não comprovado** — se não
  funcionar, **declare a degradação**, não finja que houve painel.
- **Outras frentes preservadas:** `T-037` continua planejado/aprovado; `T-038` continua separado;
  esta janela pertence exclusivamente à paridade Codex.
- **Fora deste repo, mapeado e não executado:** a migração de memória do projeto
  `Bruno Vascular - Gestão Dados Marketing` (relatório completo do scout na conversa de 09/ago;
  6 dos 11 snapshots de lá **já são páginas vivas**; 7 páginas de tópico e 14 cards propostos).
  ⚠️ Achado de segurança **fora do escopo do Orquestra**, reportado ao dono: `workflow_secretaria.json`
  daquele projeto tem PII de paciente e token em texto puro.

**Da noite de 07→08 (frente statusline, `T-036`/`T-037`/`T-038`):**

0. **Reiniciar as sessões** do `IVA - App System` e do `prompts-byia-clientes` — é o que faz a barra
   completa voltar naqueles dois projetos. A correção já está no disco (o segundo, commitada em
   `41fa1f9`); só falta a sessão reler o settings.
1. **Tirar o conector Supermemory** em **claude.ai → Settings → Connectors**. ⚠️ Verificado em
   2026-08-08: ele **não está** em `~/.claude.json`, nem em `~/.claude/settings.json`, nem em
   `.mcp.json` de projeto algum — `claude mcp list` não o lista. É conector **da conta**, e nenhuma
   mudança no plugin alcança isso. O `T-037` tira o Supermemory do produto; **o erro de conexão que
   você vê só para aqui.**
2. **Decidir o release da 0.20.0** — está bumpada nos quatro lugares e **não commitada**. O `T-036`
   ficou com escopo reduzido (conserto + F1/F2/F3 + asset saneado); falta a rodada de correção
   terminar e um painel final antes de qualquer publicação.

**Do bloco anterior (@release-validacao, segue valendo):**



1. **Dar o de-acordo em três cards já testados** — `T-017`, `T-007` e `T-010` passaram em 07/ago,
   com a evidência escrita em cada card. São testes mecânicos, sem viés; falta só você concordar.
2. **Rodar os testes que só você pode rodar** — `T-014`, `T-016`, `T-009`, `T-022`, `T-025`, `T-020`,
   `T-023`, `T-030`. Todos dependem de **frase natural sua**: o Manager lê a frase do teste e a
   resposta esperada no próprio card, então acertaria de memória e não provaria nada. As frases:
   *"quais as possibilidades"* · *"instala o Serena aqui"* · *"tô com pouco crédito"* seguido de
   *"chegamos ao final do ciclo"* (a segunda **não** pode trocar o elenco) · *"agora não"* a uma
   sugestão de ferramenta, repetida numa sessão seguinte.
3. **Decidir os três cards que nasceram do painel de 07/ago** — `T-033` (template v2 não é gerado),
   `T-034` (painel não fecha 3 vendors fora do Claude; Loop A escolhe planner cego), `T-035`
   (procedência inflada + a fumaça do `instalar.md` na forma insegura).
4. **`T-013`** — exige duas janelas simultâneas suas; nada a fazer sozinho aqui.

**Distribuição:** 0.19.0 **instalada e no GitHub** (`b62b39c`) e presente nos **três hosts** —
Claude (cache `0.19.0`), Codex (`plugin add`, enabled) e Kimi (cópia em `~/.agents/skills/orq/`).
Quem instalar do repositório público recebe a 0.19.0.

**Commitado e no GitHub:** 0.17.0 (`10ecef2`) · 0.18.0 (`7674cab`) · 0.19.0 (`8bef7f9`) ·
board (`7c14aa9`) · `T-032` (`b62b39c`). **Nada pendente de push.**

⚠️ **O checkpoint de 07/ago tem mudanças ainda NÃO commitadas** (este índice, log, gotchas,
`_elenco.md`, board) — o dono não pediu commit.

## ✅ O que foi provado em 2026-08-05 — o framework roda fora do Claude Code

O Codex, com o plugin instalado, passou nos quatro testes comportamentais: **invocou a skill sozinho**
por frase natural · **achou e leu os `commands/`** · roteou um pedido pelo ciclo e **parou no gate**
sem tocar no produto · e, ao ser mandado revisar, **declarou a degradação** (*"este host não oferece
override de modelo no subagente nativo"*) em vez de fingir painel — a regra escrita na 0.18.0 indo a
campo. Ele ainda **cruzou o board com o `git log`** e flagrou dois defeitos do checkpoint anterior.

**O protocolo de várias janelas (`T-013`) foi validado entre hosts diferentes:** o Codex detectou uma
edição do Manager em `gotchas.md` que não era dele, e a excluiu do escopo sem sobrescrever.

## Onde paramos

**O que já foi provado em uso real:**
- O `/orq:init` rodou em **projeto de terceiro** (outra LLM, sem ninguém daqui) e voltou com 10
  atritos — 4 bugs de contrato. Fechou o `T-003`, gerou o `T-011`.
- O antigo **painel de três revisores** (Claude · Codex · Kimi) funcionou e se pagou três vezes:
  achou a brecha de instalação por slash command, o parser permissivo do board, e — na mesma rodada —
  Codex e Kimi acharam bugs **diferentes** no mesmo arquivo. **Esse painel foi aposentado pelo T-051;
  o contrato atual é revisor único, de vendor oposto ao host.**
- O ciclo de release está fechado: `validate` → `lint` → `marketplace update` → `plugin update`.

- **O ciclo inteiro rodou pela primeira vez** (0.11.0, 29/jul): Fable planejou 16 passos → dono
  aprovou no gate → Sonnet implementou → Claude+Codex+Kimi revisaram → 7 achados voltaram como
  correção. **Achou defeito que `validate` e `lint` não pegam.** Fechou o `T-012`.

**O que o ciclo revelou, e é o achado mais consequente até aqui:** o cache do plugin é indexado por
**versão**. Editar sem bumpar não muda o que roda, e `claude plugin list` segue dizendo que está tudo
certo. Aconteceu no `5b75296` e **invalidou retroativamente** todo teste comportamental feito depois.
Agora há guarda no lint. A versão vive em **quatro** lugares — o `marketplace.json` estava em `0.4.0`,
sete releases atrás.

**A lição de método:** instrução não é enforcement. O `_elenco.md` **já dizia** que o Kimi não tem
sandbox e exigia worktree descartável; o Kimi rodou `git checkout -- .` numa revisão read-only e
destruiu o working tree (`T-019`). É o argumento do `T-001` provado contra o próprio repo.

**O que continua sem teste:** os comandos `/orq:plan-next` e `/orq:implement-next` literais (o fluxo
foi provado, os comandos não). As 9 regras invioláveis seguem sendo texto — nenhum hook (`T-001`,
`T-002`).

⚠️ **12 cards em VALIDATE** (0.14.0, 0.15.0 e 0.16.0 entraram em 2026-07-31). Card fecha quando o dono confirma, não quando o commit passa. Os
comportamentais só são testáveis **depois do release e do restart** — antes disso testam a versão
anterior, pelo motivo acima.

Ver `wiki/KANBAN.md` para o estado exato de cada card.

## Páginas

| Página | Responde |
|---|---|
| [`wiki/KANBAN.md`](wiki/KANBAN.md) | **O board.** Onde cada card está e o que espera o dono |
| [`wiki/arquitetura.md`](wiki/arquitetura.md) | Como o Orquestra funciona hoje e **por que** cada recusa de desenho |
| [`wiki/distribuicao.md`](wiki/distribuicao.md) | Como empacotar, validar, testar e publicar o plugin |
| [`wiki/_schema.md`](wiki/_schema.md) | **O contrato**: formato do board (lido por parser) e regras da wiki |
| [`wiki/_elenco.md`](wiki/_elenco.md) | Qual LLM toca cada papel + revisores externos ativos |
| [`wiki/_stack.md`](wiki/_stack.md) | Ferramentas ativas aqui + **o que o dono dispensou** (não repropor) |
| [`fixes-history.md`](fixes-history.md) | **Log** cronológico, append-only — "o que aconteceu naquele dia" |
| [`gotchas.md`](gotchas.md) | Armadilhas que já custaram tempo |
| [`wiki/threads/desenvolvimento-do-plugin.md`](wiki/threads/desenvolvimento-do-plugin.md) | **Thread ativa** — fases, decisões a não re-litigar e **⏭️ RETOMAR AQUI** |
| [`wiki/threads/T-025-gatilhos.md`](wiki/threads/T-025-gatilhos.md) | **Implementado na 0.15.0** — descoberta (`/orq:ajuda`), gatilhos atestados e a política de iniciativa em três níveis |
| [`wiki/threads/T-026-host-alternativo.md`](wiki/threads/T-026-host-alternativo.md) | **Ativo** — o Orquestra rodando fora do Claude Code. Instalação multi-host (0.18.0, provada no Codex) e elenco host-agnóstico (0.19.0 — **liberada, instalada nos três hosts e revisada pelo painel em 07/ago; reprovada 3/3, achados em `T-033`/`T-034`/`T-035`**). **A thread é longa: o `⏭️ RETOMAR AQUI` vivo é o último do arquivo** — os anteriores estão marcados como superados |
| [`wiki/threads/T-023-reload-vs-restart.md`](wiki/threads/T-023-reload-vs-restart.md) | **Implementado na 0.14.0**, reprovado no review e corrigido — evidência por componente no lugar de regra binária |
| [`wiki/threads/T-020-perfis-elenco.md`](wiki/threads/T-020-perfis-elenco.md) | **Entregue na 0.16.0** — perfis de elenco (`padrao` · `economia`) trocados por frase |
| [`wiki/threads/T-051-elenco-por-tarefa.md`](wiki/threads/T-051-elenco-por-tarefa.md) | **Entregue na 0.24.0, reconciliado na 0.25.0** — elenco em dois eixos, revisor único cross-vendor, Kimi aposentado; traz os 6 critérios de aceite comportamental |
| [`wiki/threads/T-051-pareceres.md`](wiki/threads/T-051-pareceres.md) | **Evidência durável** — os 25 bloqueadores das 7 rodadas de review externo, com hash por parecer |
| [`wiki/threads/T-052-reconciliacao.md`](wiki/threads/T-052-reconciliacao.md) | **Thread ativa** — o plano e as 5 decisões da reconciliação `0.24.0` local × `0.22.7` publicada |
| [`wiki/threads/T-054-economia-tokens.md`](wiki/threads/T-054-economia-tokens.md) | **Thread ativa** — a frente de economia de tokens: o diagnóstico, o baseline medido, o que o parecer mudou e o **⏭️ RETOMAR AQUI** |
| [`wiki/threads/T-054-pareceres.md`](wiki/threads/T-054-pareceres.md) | **Evidência durável** — o parecer cross-vendor íntegro e a auditoria do Manager, que corrigiu um achado e confirmou outro |
| [`wiki/threads/T-148-consolidacao-main.md`](wiki/threads/T-148-consolidacao-main.md) | **Entregue, validar organização** — conciliação 0.30.0, evidências, ancestralidade Claude e limpeza recuperável; main pronta, T-144 vivo preservado |
| [`wiki/threads/T-149-elenco-padrao-versionado.md`](wiki/threads/T-149-elenco-padrao-versionado.md) | **Fonte 0.31.0 entregue na main/GitHub** — `a81026f`, R2 aprovada/auditada, gates frescos 870 verdes nas duas árvores. Em VALIDATE: ativação e uso prático separados. Sem publicação, instalação, restart ou migração do elenco ativo |
| [`wiki/threads/T-144-mods-claude-code.md`](wiki/threads/T-144-mods-claude-code.md) | **Fonte 0.30.0 entregue, validação prática pendente (`@frente-mods`)** — medidor portátil, fases 1–2 conciliadas; branch/ledger T-146 e sessão viva preservados |
| [`wiki/threads/T-072-claude-mem.md`](wiki/threads/T-072-claude-mem.md) | **No gate** — o papel do claude-mem, a fiação de busca que nunca existiu, e a correção de uma medição minha que estava 4,4× errada |
| [`wiki/threads/T-078-ai-memory.md`](wiki/threads/T-078-ai-memory.md) | **Ativa** — o AI-Memory 2.0: parecer do planner, revisão que derrubou o piloto, os 3 estágios, a decisão do dono contra a recomendação, e o root cause do Codex não capturar |
| [`wiki/threads/_notas-de-cards.md`](wiki/threads/_notas-de-cards.md) | As notas longas que saíram do board na migração do `T-056`, íntegras, por ID de card. **Não é thread** — não tem RETOMAR AQUI |
| [`wiki/threads/T-053-fable-51.md`](wiki/threads/T-053-fable-51.md) | O Fable 5.1 no elenco — thread criada na migração, porque o card era o único dos seis maiores sem uma |
| [`wiki/threads/T-052-ledgers/`](wiki/threads/T-052-ledgers/README.md) | **Prova executável** da reconciliação — três ledgers que reprovam onde a regra não existe (25/25 · 4/4 · 12/12) |
| [`wiki/threads/_noturno.md`](wiki/threads/_noturno.md) | Manifesto **expirado** + relatório do modo noturno de 2026-07-30 — não abrir run novo a partir dele |
| [`snapshot-2026-07-31-releases-0.14-0.16.md`](snapshot-2026-07-31-releases-0.14-0.16.md) | **Marco**: estado exato ao fim das três entregas do dia + as três lições de método |

## A distinção que faz isto funcionar

O **log** é imutável e responde *"o que aconteceu em tal dia"*. A **página de tópico** é reescrita e
responde *"como funciona hoje"*. Sem a página, a segunda pergunta vira arqueologia no log.

Nunca guarde aqui o que é **derivável** (diff, `git log`, lista de arquivos, o código atual) — a fonte
já tem. Guarde o *porquê* e as *consequências*.
