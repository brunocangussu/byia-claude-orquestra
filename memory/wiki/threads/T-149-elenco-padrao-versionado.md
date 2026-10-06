# T-149 — Elenco padrão versionado e adoção por projeto

## Objetivo e origem

O dono quer que cada versão do Orquestra tenha uma sugestão padrão de modelos e
efforts consistente, atualizada com o release, e que qualquer projeto possa
adotá-la por intenção natural, sem ajustes manuais de cada papel.

Fonte humana: mensagem do dono de 2026-10-05 nesta conversa Codex
`01a07216-f99e-7360-94aa-19f30fb20a40`, depois da confirmação das branches integradas:

> as LLM e efforts padrões do orquestra parece que nao estao bem configurados, precisamos atualizar as configuracoes padroes ppara todos os projetos...
> ideal é manter sempre atualizado como o padrao de sugestao para quando eu atualizar, apenas pedir ao projeto para seguir com o elenco padrao da versao do orquestra

O registro é transcrição da mensagem humana, não cria aprovação de um plano que
ainda não foi apresentado. O pedido cobre investigação, proposta e registro do
card; a implementação segue o gate do ciclo.

## Estado e limites

- `[!]` / `AWAITING_OWNER`; frente `elenco-padrao`, host Codex. Plano aprovado
  em 2026-10-05; implementação local verificada. Falta cobrir R1/bump/integração.
- A main começou limpa em `fbc9b2f`, fonte 0.30.0.
- Na etapa inicial de planejamento, produto e elencos estavam intactos. Agora
  o diff T-149 está apenas no worktree, com elencos ativos preservados. Sem bump,
  stage, commit, push, integração, publicação, instalação ou restart executados.
- Sem chamada de inferência externa, sonda de capacidade ou reautenticação.
- Consultas públicas à documentação e leitura local de instruções/configuração
  não são execução de modelos nem prova de disponibilidade na conta.
- O T-131 entregou candidatos de fábrica, não uma migração automática do elenco
  ativo; o T-148 preservou deliberadamente as escolhas locais das duas janelas.
- O T-144 tem checkout com processos vivos: não tocar nele nem no seu elenco.

## Investigação inicial

Leituras: índice, board canônico, skill e command `elenco` do pacote 0.30.0,
`plan-next`, elenco local completo e grafo dos testes/validador.

Observado, ainda sem mudar os valores:

- Fábrica Codex: implementer leve Luna 6/medium, normal Sol 6.1/high e pesada
  Sol 6.1/xhigh; os planners continuam Astra/max e docs/scout Sol 5.6/low.
- Elenco local Codex: planners Astra/max; implementers, docs e scout Terra
  5.6/xhigh; reviewer no alias `opus`, não no ID exato Opus 5.5.
- Fábrica Claude: planner de sistema e reviewer continuam Astra/xhigh.
- Elenco local Claude: esses dois papéis já usam Sol 6.1/xhigh, mas o preset
  `padrao` continua Astra; `perfil padrao` pode desfazer a escolha mais recente.
- A cópia global `.agents/skills/orq/SKILL.md` contém disciplina legada de painel
  e modelos fixos que diverge da skill versionada 0.30.0. O diagnóstico registra
  a concorrência das instruções, não prova qual delas venceu em outro chat.

## Checkpoint de recuperação

Checkpoint de recuperação (2026-10-05): após compactação, a raiz absoluta do
pacote 0.30.0 e `scripts/kanban-status.sh` foram comprovados; o resolver devolveu
`state: ok`, `exists: true` e o board/thread root desta main. Índice, board e
esta thread foram relidos. Continuam modificados apenas o registro do T-149 e
o board; `orq/` segue sem diff. O pedido atual permanece o padrão versionado,
não uma migração automática nem autorização de entrega.

## Plano preparado e decisão pendente

Plano: [`../../../docs/plano_T-149-elenco-padrao-versionado.md`](../../../docs/plano_T-149-elenco-padrao-versionado.md).

Proposta: catálogo distribuído único, versão derivada do manifesto (sem quinta
âncora), modelo/effort resolvidos juntos e perfil adotado com proveniência.
Intenção natural `siga o elenco padrão desta versão` distingue fábrica versionada
de preset local. Não há migração em massa, mudança do Manager, reativação de via
nem interrupção de workers vivos. Overrides explícitos sobrevivem.

Recomendação: Sol 6.1/Luna 6 no Codex, Sonnet 5.5 para implementação/docs/scout no
Claude, Opus 5.5 para interface e revisão no Codex; review Claude continua OpenAI
Sol 6.1. Efforts por papel/faixa estão no plano; a rotina não depende de Astra,
Terra ou Fable. Isso não certifica economia nem capacidade das contas.

Lacuna adicional: `run-opus-reviewer.py` não aceita/passa effort. Frontmatters
também não o declaram. O plano inclui ajuste de chamadas e guardas, além das
tabelas. CLI local consultado sem inferência: Claude Code 2.1.290; Codex 0.160.0.

O Manager preparou o plano com investigação local e documentação pública; não
houve planner externo, revisão independente, nova inferência, prova sintética
ou autenticação. Produto e elencos ativos continuam intactos.

Decisão única: aprovar o elenco proposto e implementar localmente o T-149.
Não inclui bump, commit, push, publicação, instalação, restart, migração em
massa ou chamadas externas. Nenhuma versão reservada.

Verificação desta etapa documental: `git diff --check` e lint de coerência
com `PYTHONDONTWRITEBYTECODE=1` saíram 0; há um único card T-149 no board.
Fonte continua 0.30.0, sem diff em `orq/`, README ou marketplace. Foram alterados
somente índice, board, esta thread e o plano novo. Não são os gates completos
de implementação nem uma comprovação de funcionamento nos outros chats.

## Aprovação e execução — 2026-10-05

Fonte humana verificada diretamente nesta conversa
`01a07216-f99e-7360-94aa-19f30fb20a40`: mensagem do dono imediatamente posterior
à entrega do plano T-149, literal:

> perfeito - aprovo - pode implementar, comitar e pushar tanto local quanto pro github

Esta é transcrição, não criação de autoridade. Aprova o plano local P1–P6 e
nomeia commit/push; preparação do índice desses arquivos integra o commit.
O plano ainda exige autorização delimitada para revisão externa e bump; a
mensagem não nomeia merge, publicação, instalação ou restart. Entrega permanece
condicionada aos gates, sem simular revisão aprovada.

- Worktree: `~/.codex/worktrees/t149-elenco-padrao/byia-claude-orquestra` (registro gerenciado no host).
- Branch: `codex/t149-elenco-padrao`, criada da main `fbc9b2f`.
- Elenco ativo, caches e checkout vivo T-144 preservados.
- Gates locais: sem teto humano adicional imposto; testes/CLIs falsos sem rede.
- Gate externo T-149: nenhuma autorização de envio; limite autorizado 0,
  consumo 0. Não gastar autorizações de cards anteriores nem inferir retry.
- Gate Git: stage/commit/push do T-149 autorizados; sem execução até os gates
  obrigatórios. Bump e integração serão delimitados antes da entrega de produto.

Ruling de execução: a tabela legada continua governando o projeto e não será
ativada como efeito da implementação. O Manager executa as etapas locais nesta
sessão Codex no worktree isolado, sem declarar worker separado ou prova de
capacidade dos novos candidatos. A revisão independente não é substituída por
essa autoverificação; continua pendente de autorização própria.

Pré-flight: P1 fornece catálogo/resolvedor a P2/P3/P5; P4 recebe esforço do
mesmo perfil sem mudar os gates de identidade/zero-tools. P6 descreve o estado
final após review, não antecipa aprovação. Não há nova dependência.

Recuperação antes da implementação: raiz 0.30.0 e resolver comprovados novamente;
índice, board e thread relidos. O worktree `codex/t149-elenco-padrao` está limpo,
com base `fbc9b2f`. Mantida a autorização atual, sem nova chamada externa.

## Checkpoint de implementação e recuperação — 2026-10-05

Após nova compactação, a raiz absoluta do pacote 0.30.0 foi comprovada antes
do uso. O resolver saiu 0, com JSON válido, `state: ok`, `exists: true` e
board/thread root da main. Índice, board e esta thread foram relidos; o pedido
e a autorização de implementação/commit/push continuam os mesmos.

P1–P4 implementados no worktree: catálogo fechado com 16 perfis, resolvedor
puro de proposta por host, consumidores/agentes com modelo e effort juntos e
runner com effort explícito. O esquema não acrescenta uma quinta âncora de
versão. Adoção não é instalação, herança não é prova de capacidade, e nenhum
elenco ativo foi alterado. O T-144 vivo segue preservado.

Verificação local observada, sem inferência externa:

- Baseline: 838 testes, manifesto estrito e lint saíram 0.
- RED/GREEN: catálogo, consumidores, fronteira de escrita/provas contextuais
  e envio do effort em CLI falsa. As mutações de omissão/downgrade e de
  instruções incoerentes foram rejeitadas pelas guardas correspondentes.
- Primeira suíte completa alterada: 864 testes, duas falhas reais (diagnóstico
  maior que o teto e fixture sem a nova dependência). Ambas corrigidas e
  verificadas individualmente; não foram ignoradas nem viraram falso verde.
- Segunda suíte completa: 864 testes em 217,329 s, exit 0; manifesto estrito
  e lint também exit 0. `git diff --check` saiu 0.

Gate externo permanece autorizado 0 / consumido 0. Pacote R1 apenas preparado,
nunca enviado. A documentação final ainda precisa ser conciliada com o review;
estes gates locais não são revisão independente nem validação pós-release.
Main e origin/main seguem em `fbc9b2f`; fonte continua 0.30.0. Não houve bump,
stage, commit, push, integração, instalação ou restart nesta execução.

## Snapshot local completo e gate de entrega — 2026-10-05

P5 concluído; P6 tem rascunhos vivos de arquitetura/distribuição no pacote de
review, sem antecipar a conclusão depois da revisão independente. A atualização
inclui 23 arquivos de produto/documentação viva; os demais arquivos desta
frente são plano, registro e evidências, nunca mudanças do Claude.

Última verificação com esses rascunhos: 864 testes em 215,716 s (processo
216,109 s), manifesto estrito, lint e `git diff --check`, todos exit 0.
Recibo reproduzível e inventário por SHA-256:
`docs/reviews/T-149-gates-locais.json` no worktree. O digest agregado dos
23 arquivos é `0cc91758b9d1899f4d38fd926d069dff6c6bbdccd9743ed3630c1f17879365b1`.

Pacote R1 congelado, apenas local:

- `docs/reviews/T-149-R1-pacote-sanitizado.md` — 99.693 bytes UTF-8, teto
  proposto 128 KiB (`131072` bytes).
- SHA-256: `24ccdd9bb4343cb4027f192e85a4489abb7a7a1ba983d6a8d7f719e36b06c4ea`.
- Runner: `c753ce7992548d29ccd5673082bbac5672ab41e9a20099a1bb60d87d74ae13c4`.
- Destino proposto: Anthropic via Claude CLI, ID `claude-opus-5-5`, effort
  `high`, uma chamada fresca sem retry. Pacote sem PII, credenciais ou caminhos
  pessoais. Qualquer mudança de bytes exige novo congelamento antes do envio.
- Autorizado 0 / consumido 0; nenhuma revisão independente executada.

O pacote preliminar de 92.680 bytes foi substituído localmente para incluir
os rascunhos P6; não foi enviado, não consumiu gate e não é o alvo atual.
O elenco ativo permanece byte a byte idêntico à main. Sem configuração global,
cache ou checkout T-144 alterado. Fonte/main/origin continuam 0.30.0 / `fbc9b2f`.

Ledger local: run `e0f17b23-b5b5-4d1f-8870-9a0f8f4193eb`, revisão 15,
fase `gate`, P1–P5 concluídos, P6 ativo (conclusão pós-review), 5/6 — 91%. A chave de sessão
não sai do ledger local nem é copiada para este registro/pacote.

Só a dependência externa/de entrega está em `AWAITING_OWNER`; não há trabalho
local elegível abandonado. O Manager moveu T-149 para `[!]`, preservando posse
`@frente-elenco-padrao @codex`. Não é VALIDATE nem DONE; commit/push continuam
autorizados, sem execução antes do review e do bump obrigatório coberto.

⏭️ RETOMAR AQUI: obter uma decisão delimitada para enviar somente esta R1 e,
se aprovada, bumpar a próxima versão livre nas quatro âncoras e integrar a main
allowlistada. Revalidar hashes/estado/versão antes de executar. Commit/push já
autorizados não precisam ser pedidos de novo. Sem publicação, instalação ou
restart; não reusar saldo de outros cards nem repetir probes automaticamente.

## Autorização da R1 e recuperação — 2026-10-06

O dono respondeu **“sim - autorizo”** ao gate apresentado nesta conversa:
enviar o pacote sanitizado congelado de 99.693 bytes ao Opus 5.5/high via
Claude CLI/Anthropic, uma R1 sem retry; se aprovada, bumpar para 0.31.0 e
integrar na main. Implementação, commit e push já estavam autorizados.
Sem publicação, instalação ou restart. Não vale para pacotes de outros cards.

Contrato: SHA-256 `24ccdd9bb4343cb4027f192e85a4489abb7a7a1ba983d6a8d7f719e36b06c4ea`,
teto `131072` bytes, ID `claude-opus-5-5`, effort `high`, timeout 600 s,
limite 1, consumido 0 antes do despacho. A confirmação humana cobre esse
pacote maior que o teto geral do comando; não autoriza retry nem R2.
O runner permanece congelado em
`c753ce7992548d29ccd5673082bbac5672ab41e9a20099a1bb60d87d74ae13c4`.

Recuperação verificada: raiz absoluta 0.30.0 existente, resolver exit 0,
JSON válido, `state: ok`, `exists: true`, board/thread root da main. Índice,
quadro e thread relidos; base main/origin `fbc9b2f`, frente T-144 intacta.
O Manager reafirmou a posse e moveu somente T-149 para `[~]`.

Autenticação atual da Claude CLI: `loggedIn: true`, via `claude.ai`, sem
expor identidade ou credenciais. Não usar `--bare`: nesta CLI ele exclui
OAuth/keychain e poderia criar um falso diagnóstico de sessão deslogada.
Nenhuma reautenticação ou chamada sintética adicional é necessária.

⏭️ RETOMAR AQUI: executar uma única R1 com hashes conferidos imediatamente
antes do envio. Registrar consumo e resultado; se aprovada, concluir docs,
quatro âncoras 0.31.0, gates frescos e entrega Git allowlistada. Falha de
execução não é parecer; sem relançamento automático.

Despacho R1 reservado em 2026-10-06: autorizado 1 / consumido 1, sem retry.
Pacote/runner conferidos; envelope não acrescenta bytes ao prompt, mantém OAuth,
desliga hooks e MCP, preserva `--tools ""` e usa diretório vazio. Resultado
terminal será registrado em `docs/reviews/T-149-R1-recibo.json`; reserva e
consumo não representam parecer nem aprovação.

## R1 terminal e auditoria — 2026-10-06

Uma chamada real (1/1), sem retry: runner/CLI exit 0, 239,247 s, ID em
`OPUS_MODEL_USAGE` `claude-opus-5-5`, effort high enviado; effort do servidor
não observado. Autenticação funcionou, cwd permaneceu vazio, nenhum problema
de login. Parecer com formato válido: **REPROVADO**, não autorização de entrega.

O bloqueador foi reproduzido: comando documentado para legado mandava
`--effort ""`; argparse saiu 2 antes da chamada externa. Dois riscos também
foram reproduzidos: vias Markdown desligadas ignoradas e lista de mecanismos
candidatos inteira promovida apesar de só uma via comprovada. Correções locais
continuam dentro da implementação aprovada; nenhuma revisão adicional foi
inferida. RED/GREEN do Bash documentado, normalização host-aware, via selecionada
e revalidação de prova reutilizada por contexto concluídos. Seis mutações
válidas rejeitadas, sem erro de execução. Focados: 29 verdes.

Contratos do Manager/legado, bootstrap do init, raiz do template e briefing/
artefato do planner foram esclarecidos; agentes não tentam provar o próprio
spawn. Riscos não medidos permanecem delimitados, sem falso GO. Evidências no
worktree: `docs/reviews/T-149-R1-opus55.md`, `T-149-R1-recibo.json`,
`T-149-R1-runner.stderr.txt` e `T-149-R1-auditoria.md`.

A suíte descoberta pós-correção está em execução no handle original. Não houve
bump (fonte ainda 0.30.0), stage, commit, push, integração, publicação, instalação
ou restart. A autorização condicional de entrega não foi exercida porque a R1
não aprovou. Não relançar revisão: próximo snapshot/R2 depende de novo gate.

## Checkpoint pós-correções e próximo gate — 2026-10-06

Gates finais desta correção local: **870 testes OK em 265,088 s**, manifesto
estrito, lint e `git diff --check`, todos exit 0. A suíte emitiu dois
`ResourceWarning` de arquivo não fechado; ficaram registrados, não suprimidos,
e a origem não foi auditada. Focados 29/29; mutações válidas 6/6 rejeitadas.
Recibo pós-R1: `docs/reviews/T-149-gates-pos-R1.json` no worktree.

R2 congelada apenas para decisão humana, nunca enviada:

- Pacote: `docs/reviews/T-149-R2-pacote-sanitizado.md`.
- **126.107 bytes UTF-8**, teto proposto 128 KiB (`131072` bytes).
- SHA-256: `ee6a468b00bc93a090ed5087b454d607c60ca2bb5a710ee62ca9ae8ba39675bf`.
- Runner intacto: `c753ce7992548d29ccd5673082bbac5672ab41e9a20099a1bb60d87d74ae13c4`.
- Diff completo dos 23 arquivos, parecer R1 integral e auditoria local,
  sanitizados sem PII, credenciais ou caminhos pessoais.
- Proposta: uma R2 fresca `claude-opus-5-5`/`high` via Claude CLI/Anthropic,
  sem retry, mesmo isolamento com OAuth. R2 autorizado 0 / consumido 0.
- Se aprovada e com autorização correspondente: quatro âncoras 0.31.0,
  gates de entrega frescos, commit/push e integração allowlistados na main.
  Sem publicação, instalação ou restart. Não usar o saldo já gasto da R1.

O Manager estacionou somente a dependência de revisão/entrega em `[!]`,
preservando `@frente-elenco-padrao @codex`. Não há VALIDATE/DONE ou aprovação
por autoverificação. Main/origin ficam em `fbc9b2f`, fonte 0.30.0; elencos,
caches, configurações globais e checkout vivo do T-144 continuam intactos.

⏭️ RETOMAR AQUI: aguardar decisão para esta única R2 e entrega condicional.
Na retomada, comprovar raiz/resolver, reler índice/quadro/thread, conferir
hashes/byte count/inventário e consumo antes do despacho. Não repetir R1,
login/probe ou revisão por conta própria. Commit/push anteriores continuam
no escopo, mas a entrega requer parecer independente aprovado e seu gate.

Verificação de saída do checkpoint: pacote R2 com bytes/hash conferentes,
inventário dos 23 arquivos sem divergência, índices Git vazios nas duas raízes,
lint/diff-check exit 0 em main e worktree. Fetch confirmou main/origin em
`fbc9b2f`; T-144 segue em `064e726`. Elenco ativo permanece byte a byte igual.
Raiz/resolver reconfirmados, sem fallback. Ledger T-149 revisão 17, fase `gate`,
P6 pendente da revisão/entrega; 5/6 não significa DONE. A tentativa de fase
`implement` inválida foi recusada (exit 2), sem alterar o ledger; não houve
perda ou avanço artificial de progresso.

## Recuperação e autorização R2 — 2026-10-06

Contexto recuperado na mesma conversa: raiz instalada 0.30.0 absoluta e
existente; resolver exit 0, JSON state ok/exists true, board e THREAD_ROOT
canônicos. Índice, quadro e esta thread relidos; T-149 mantém a frente dona.
R2 não iniciada, recibo terminal ausente; R1 e suíte anteriores encerradas.
Inventário dos 23 arquivos e bytes/hash do pacote R2 reconferidos, sem divergência.
Main/origin em fbc9b2f; quatro registros Manager são desta frente e ficam
preservados. A busca de progress.md na raiz do pacote falhou localmente;
o contrato correto é skills/orq/references/progress.md, lido integralmente.
Nenhuma chamada externa decorreu dessa correção de caminho.

Fonte humana verificável: esta conversa Codex, mensagem literal do dono
**"autorizo"** imediatamente após a pergunta do Manager:
> Autoriza uma R2 de 126.107 bytes sanitizados, ao Opus 5.5/high via
> Claude CLI/Anthropic, teto de 128 KiB, sem retry, e, se aprovada,
> bump 0.31.0, commit/push e integração na main? Sem publicação,
> instalação ou restart.

A mensagem humana foi conferida no contexto da conversa; este registro é
transcrição, não cria autoridade. Modo digest congelado: somente
ee6a468b00bc93a090ed5087b454d607c60ca2bb5a710ee62ca9ae8ba39675bf,
126.107 bytes, teto 131072. Modelo claude-opus-5-5, effort solicitado high,
timeout 600 s, uma chamada fresca, sem ferramentas e sem retry. Wrapper de
isolamento acrescenta zero bytes ao prompt, desativa hooks/MCP e preserva
OAuth sem --bare, API key ou token manual. Prova contextual da R1 permanece
compatível; não há nova sonda/login. R2 autorizado 1 / consumido 0 no preparo;
reservar o consumo durável imediatamente antes de iniciar.

Entrega Git é independente e condicional à revisão aprovada: quatro âncoras
0.31.0, gates frescos, stage/commit/push/integração allowlistados. Não cobre
tag/release, instalação, restart, caches, configurações globais nem adoção
do elenco em outros projetos. R1 continua consumida e reprovada.

Checkpoint de recuperação registrado; a conversa e o pedido continuam.
⏭️ RETOMAR AQUI: conferir recibo/consumo da R2 antes de iniciar ou observar
somente seu handle se já iniciado. Nunca relançar após interrupção.

R2 iniciada em 2026-10-06T17:36:02.741Z, handle local exec 6484.
Autorizado 1 / consumido 1, sem retry. O recibo durável no worktree guarda
o despacho; o próximo passo é observar este handle até o estado terminal,
nunca abrir uma segunda chamada se a observação for interrompida.

## R2 terminal, auditoria e recuperação — 2026-10-06

O handle 6484 terminou; não deve ser observado nem relançado. R2 consumiu
exatamente 1/1 chamada autorizada, sem retry, de 17:36:02.741Z a
17:40:34.744Z: runner/CLI exit 0, formato válido, veredito literal
`APROVADO_COM_RESSALVAS`, sem bloqueadores. Identidade observada pelo runner:
`claude-opus-5-5`; effort high solicitado/transmitido, sem observação do
effort no servidor ou custo informado.

As duas condições pré-commit foram encerradas: cabeçalho do revisor não
obriga effort no legado comprovado; combinação nova só com modelo não herda
exceção histórica nem é gravada/despachada sem decisão/gate do dono. Outros
riscos foram auditados; o helper é projeção dos oito papéis, não reescritor
da seção inteira. Manager/papéis adicionais/overrides ficam fora dela.

Pacote e runner preservaram os hashes congelados. Parecer, recibo terminal
e auditoria: `docs/reviews/T-149-R2-{opus55.md,recibo.json,auditoria.md}`
na frente dona. Clarificações limitadas a dois comandos, docstring do
helper e reforço do teste Bash, sem mudança algorítmica e sem nova chamada.
Foco 29/29 verde; duas mutações reprovadas por asserção correta. O erro de
seletor inicial não foi contado como RED.

Após compactação, raiz instalada 0.30.0 e resolvedor foram comprovados;
índice, board e esta thread relidos. Main/origin em `fbc9b2f`, versão
0.31.0 livre, frente Claude T-144 e elenco ativo preservados. Checkpoint de
recuperação registrado, mantendo o pedido atual. Bump das quatro âncoras
na frente T-149; gates finais antes da entrega Git allowlistada autorizada.

⏭️ RETOMAR AQUI: observar somente a suíte local em curso se houver handle,
concluir gates frescos, commit/push e integração autorizados. Não fazer
outra rodada externa, publicação, instalação, restart ou adoção automática.

## Gates finais 0.31.0 — 2026-10-06

Handle local 74137 terminal, exit 0: suíte por discover 870/870 em
273,057 s, manifesto estrito exit 0 e lint de coerência exit 0. Recibo
durável em `docs/reviews/T-149-gates-pos-R2-0.31.0.json`. Dois avisos
ResourceWarning de arquivo não fechado foram registrados, sem falhas e sem
afirmar causa preexistente não auditada. O erro de escape do invólucro local
antes desse handle não chegou a executar testes nem qualquer chamada externa.

As quatro âncoras conferem 0.31.0. O delta posterior ao pacote R2 contém
as clarificações auditadas e o cabeçalho de arquitetura atualizado pelo
bump. O runner e o pacote congelado mantêm seus digests; elenco ativo
byte a byte preservado. Plano e thread têm caminhos locais portáveis,
sem nomes pessoais nos novos artefatos de envio.

⏭️ RETOMAR AQUI: fazer pull --rebase sem perder o trabalho próprio,
conferir staged por allowlist, commitar e integrar/pushar a fonte.
Repetir gates na main integrada e só então registrar a entrega efetiva.
Não relançar os handles terminais 6484/74137 nem revisões externas.

Conferência do staged: 45 arquivos allowlistados, nenhum `_elenco.md`
ativo, arquivo do T-144 ou ledger/chave privada. Check de espaços global
exit 2 apenas nos três snapshots congelados R1/parecer/R2 (1+70+75
ocorrências). Check de todos os arquivos vivos/editáveis exit 0,
excluindo só essas três evidências imutáveis, sem mudar seus bytes/hashes
nem configurar exclusões globais. Detalhes na auditoria R2.
Pull --rebase na frente T-149: já atualizado em `fbc9b2f`, digests
de todos os 45 arquivos preservados.
