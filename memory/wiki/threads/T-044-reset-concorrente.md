# T-044 — reset concorrente do guardião

## Estado

- A implementação aprovada e revisada em 2026-08-17/18 foi localizada no commit isolado `639a0b9`.
- A candidata antiga não podia ser integrada diretamente porque sua base estava 59 commits atrás.
- O port vive em `.worktrees/t044-reset-concurrency-port`, branch
  `codex/t044-reset-concurrency-port`, sobre a base atual.
- Plano reconciliado: `docs/superpowers/plans/2026-09-20-t044-reset-concorrente.md`.

## Contrato portado

- Novos clears criam gerações exclusivas `<hash>.reset.*`; o marcador fixo legado continua aceito.
- A transação consome apenas o snapshot de marcadores que observou, então um clear mais novo
  sobrevive à persistência antiga.
- macOS/Linux usam `fcntl.flock`; Windows usa `msvcrt.locking` no byte zero; não existe fallback
  `lockdir` sujeito a órfão/TOCTOU.
- Falha de criação, listagem, remoção ou backend permanece visível e fail-open, sem gravar nova
  telemetria em cima de reset incompleto.

## Evidência na base atual — 2026-09-20

- As nove funções de produção do port têm AST idêntica ao snapshot externo já revisado e aceito.
- Onze testes contratuais foram portados; o teste de morte de processo já existia na base atual sob
  nome mais específico e é semanticamente idêntico. Os quatro testes antigos de `.in_use` não foram
  duplicados porque a base atual mantém cobertura equivalente do `T-046`.
- GREEN: 114/114 testes focados e 407/407 na suíte descoberta.
- Mutation checks: 5/5 mortos — marcador fixo, ausência de lock Windows, transação antiga apagando
  geração nova, falha de reset ignorada e `ENOENT` tratado como falha.
- Manifesto estrito e `git diff --check` verdes. O lint de coerência falha somente porque uma árvore
  `orq/` modificada ainda declara `0.27.8` e diverge do cache instalado; corrigir isso exige reservar
  a próxima versão livre e alinhar os quatro anchors.
- A documentação atemporal foi portada para `arquitetura.md` e `distribuicao.md`. O smoke de morte
  de processo em Windows real permanece validação comportamental antes de release.

## Review herdado e auditado

Kimi K3 cobriu o diff histórico completo; Opus comprovou `claude-opus-5` e aprovou integralmente a
produção com ressalvas. O dono aceitou explicitamente a lacuna documental residual e autorizou o
commit local da candidata antiga. A auditoria atual confirmou equivalência estrutural da produção e
dos testes portados, sem reenviar código a terceiro.

## Pré-auditoria local — persistência antes do consumo

O port ainda violava o próprio plano: `_apply_pending_reset()` removia os marcadores fotografados
antes de `_handle_event_unlocked()` persistir o novo estado. Um `save_state=False` posterior apagava
o pedido de reset como se tivesse concluído. O RED reproduziu esse sucesso silencioso. O GREEN
separou a fotografia/preparo da finalização: o JSON antigo é removido antes do evento, mas a
fotografia só é consumida depois de uma persistência bem-sucedida; falha de save ou de remoção deixa
o marcador para retry e continua fail-open.

Evidência fresca: 115/115 testes focados e 408/408 na suíte descoberta; manifesto estrito, Ruff e
`git diff --check` verdes. O lint acusa somente a divergência esperada do cache `0.27.8`, sem bump.
Três mutantes novos morreram independentemente: consumir antes de persistir, deixar de registrar o
resultado de `save_state` e confundir falha ordinária de telemetria com reset pendente. Somados aos
cinco anteriores, são 8/8. Snapshot sanitizado dos quatro arquivos de produto: 34.072 bytes em três
lotes (máximo 13.987), SHA-256
`7bcc37484943f37dd3ca643b2fdfdf6537a16a9cd28a8cd1885e3b393336efc6`; zero PII, caminho local ou
credencial. O scanner lexical encontrou apenas o identificador de código `status_token`, auditado
como falso positivo. Nenhum payload foi enviado.

## Borda portada do T-122 — 2026-09-20

O novo RED provou uma lacuna adicional: um evento sem nenhuma persistência consumia a fotografia do
reset. O teste `test_reset_without_persistence_keeps_observed_reset_pending` falhou porque o marcador
desaparecia. O GREEN mínimo passou a exigir pelo menos um resultado de persistência e nenhum
`False` antes do consumo; sem isso, preserva o marcador e retorna aviso fail-open. O cenário de dois
clears independentes também foi exercitado (`before=2`, `after=0` depois de persistência real) e já
funcionava, por isso não recebeu teste redundante.

Provas frescas: 116/116 no módulo, 409/409 na suíte descoberta, manifesto estrito e
`git diff --check` verdes. O lint continua vermelho somente pela divergência esperada entre a fonte
modificada e o cache 0.27.8, sem bump. O mutante que remove a exigência de persistência não vazia
reproduz o RED; somado aos oito anteriores, o ledger fica em 9/9.

O snapshot completo dos quatro arquivos tem 35.096 bytes, SHA-256
`4ec0a9bf2316c7f512cf85ec2741a420741505de1110e8f285b88a1c81326c60`, com zero ocorrências nos
scanners de PII, credenciais, e-mail e caminho local. A revisão Opus iniciou no lote 1/4, de 9.903
bytes, mas o runner encerrou com `OPUS_PROCESS_FAILED: exit=1; stderr=<vazio>` e exit 5. O diagnóstico
local confirmou `claude auth status`: `loggedIn=false`, `authMethod=none`. Pelo contrato sem retry,
os lotes 2–4 não foram enviados e a revisão é **DEGRADADA**, sem parecer.

## Ponto de retomada antes da R1

## Revisão Opus fresca — 2026-09-21

Após reautenticação comprovada do Claude CLI, o dono autorizou uma única rodada com os quatro lotes
sanitizados, sem retry. Os quatro lotes comprovaram `claude-opus-5`; documentação, produção e a
segunda metade dos testes foram aprovadas. A primeira metade dos testes foi bloqueada por dois
oráculos falsamente acoplados/fracos, ambos confirmados pelo Manager:

1. o teste da falha conjunta de criação do marcador e remoção do estado aceita apenas “falhou
   aberto” + “reset”, combinação também presente na mensagem de sucesso parcial;
2. `pending_reset_markers()` promete independência, mas deriva o caminho do marcador chamando a
   própria `_state_reset_path()` de produção.

O parecer global é **BLOQUEADO**, apesar de 409/409 e da produção aprovada. O checkout temporário
T-122 já estava ausente e seu registro administrativo foi limpo no Lote 3 do T-097; a branch foi
preservada e não continha commit exclusivo.

**Próximo gate:** corrigir somente os dois oráculos com RED/GREEN e mutation checks; repetir suíte,
manifesto, lint e `diff --check`; depois pedir autorização nominal para uma nova revisão. Não houve
correção, bump, commit, push, merge, publicação, instalação ou restart.

## Checkpoint pós-compactação — 2026-09-21

A raiz absoluta instalada do Orquestra 0.27.8 foi recomprovada com
`scripts/kanban-status.sh`; o resolver devolveu `state=ok`, `exists=true`, board e `thread_root`
absolutos, e esta thread existe no caminho devolvido. O card permanece sob `@codex`.

O dono autorizou corrigir os dois oráculos da R1 com RED/GREEN e mutation checks, repetir todos os
gates locais e enviar uma única R2 sanitizada ao Claude CLI/Anthropic, sem retry. Somente um parecer
aprovado abre a reconciliação, a escolha da próxima versão livre, o commit, o push e a integração.
Publicação, instalação e restart permanecem proibidos.

## Retomada pós-compactação — executada

Provar primeiro os dois falsos-verdes em cópias temporárias, corrigir apenas
`orq/scripts/test_context_guard.py`, matar os mesmos mutantes e então executar os gates locais.

## Correção dos oráculos e R2 Opus — 2026-09-21

Os dois falsos-verdes foram reproduzidos antes da correção: substituir a resposta de falha total
pela mensagem de sucesso parcial manteve o teste verde; deslocar `_state_reset_path()` também
manteve verde o teste que deveria fixar o caminho observável. Depois da correção, os mesmos dois
mutantes falharam e os dois testes reais passaram. `pending_reset_markers()` agora calcula o digest
e o caminho legado de modo independente; a falha conjunta exige a mensagem “não foi aplicado por
completo” e rejeita “estado anterior foi removido”.

Os gates frescos passaram em 409/409, manifesto estrito e `git diff --check`. O lint manteve somente
a divergência esperada da fonte candidata contra o cache 0.27.8
(`bytes:scripts/context-guard.py`). O snapshot dos quatro arquivos ficou com 35.428 bytes e SHA-256
`084f856c3267bf2b065fdad4a8b99329bdb2e1fda2d0ab4ee021bd6b69d17dc5`; scanners deram zero para
caminho pessoal, nome do dono, e-mail, CPF, chave privada e marcadores de credencial.

A única R2 autorizada saiu em quatro lotes, uma chamada por lote e sem retry. Todos comprovaram
`claude-opus-5`; o parecer global foi **BLOQUEADO**. A auditoria contra o snapshot completo separou
seis lacunas confirmadas:

1. a garantia documental de que marcador posterior sobrevive é ampla demais para o caminho legado
   fixo: uma sessão antiga pode tocar o mesmo `<hash>.reset` depois da fotografia, e a transação
   nova ainda remove esse path;
2. `distribuicao.md` não decide se a validação Windows real é obrigatória para publicar suporte a
   Windows ou apenas dívida registrada;
3. “informa a falha aberta” não diz explicitamente se o hook aborta fail-open ou prossegue sem
   exclusão mútua;
4. se a persistência posterior ao reset falha, `handle_event()` descarta o resultado já calculado e
   devolve só `systemMessage`; a reprodução perdeu `hookSpecificOutput.additionalContext`;
5. o backend `msvcrt` repete até o deadline qualquer `OSError`, inclusive erro permanente, enquanto
   `fcntl` só repete contenção transitória;
6. `test_legacy_fixed_reset_marker_is_consumed` ainda cria e valida o fixture legado com
   `_state_reset_path()` de produção, mantendo acoplamento circular no contrato de upgrade.

Dois bloqueadores do lote final foram descartados após leitura completa: `_persist_response()` não
adquire lock nem consome marcador, portanto o teste da transação anterior não era vacuamente verde;
e reset repetido após falha de remoção do marcador é a política fail-open documentada, não regressão
nova. A observação sobre Python 3.9 também não procede porque o arquivo já usa
`from __future__ import annotations`.

Não houve bump, commit, push, integração, publicação, instalação ou restart, pois a condição
“se aprovada” não ocorreu.

## ⏭️ RETOMAR AQUI

Planejar a correção das seis lacunas confirmadas com RED/GREEN e mutations específicas. Uma nova
revisão externa exige autorização nominal; a R2 já foi consumida e não pode ser repetida.

## Correção dos seis bloqueadores e R3 auditada — 2026-09-21

As seis lacunas confirmadas da R2 foram fechadas:

1. o marcador legado fixo é reivindicado por rename atômico para um path exclusivo da transação,
   preservando um novo clear criado depois da fotografia;
2. a documentação exige smoke real no Windows antes de declarar suporte validado para Windows;
3. a política fail-open declara que a ação do host prossegue sem tocar no estado quando não há
   backend, mas sem garantia de exclusão mútua;
4. falha de persistência pós-reset preserva o `additionalContext` já calculado;
5. `msvcrt` repete somente contenção transitória e encerra imediatamente erro permanente;
6. o fixture legado deriva SHA-256 e path sem chamar `_state_reset_path()` de produção.

Os REDs reproduziram perda do clear posterior, retry indevido de `EINVAL`, perda de
`additionalContext`, contratos documentais ausentes e o acoplamento circular do fixture. Depois
da correção, sete testes focados e 414/414 completos passaram. Os mutantes de remover o claim,
descartar a resposta, repetir errno permanente, alterar o path legado e apagar cada cláusula
documental foram mortos. Manifesto estrito e `diff --check` passaram; antes do bump, o lint
acusava somente a divergência esperada contra o cache 0.27.8.

A única R3 autorizada foi enviada em quatro lotes sanitizados, sem retry, com
`OPUS_MODEL=claude-opus-5`. Documentação e as duas metades dos testes foram aprovadas. O lote de
produção alegou que `SessionStart(source=clear)` não persistiria resposta e receberia aviso falso.
A auditoria do Manager invalidou o cenário contra o snapshot integral: o handler chama
`_persist_response(default_state(), _session_context(...))`. Uma prova direta fresca confirmou
`has_additional_context=True`, `has_false_failure=False`, zero marcador pendente e estado padrão.
O único caso sem persistência é evento desconhecido, deliberadamente coberto pelo teste que mantém o
reset pendente. Sem cenário de falha concreto restante, a R3 ficou **APROVADA após auditoria**.

A versão livre escolhida é `0.27.10`: `0.27.9` está reservada ao T-095, e a varredura dos
worktrees registrados, branches e tags não encontrou reserva de `0.27.10`. O card entra em
VALIDATE após a integração; publicação, instalação, restart e teste comportamental permanecem
pendentes e não são autorizados nesta etapa.

## Release e validação comportamental — 2026-09-22

O `origin/main` público foi confirmado em `df98d9c`. Claude e Codex atualizaram seus marketplaces
Git para esse SHA e registraram `orq@orquestra` 0.27.10 habilitado. Os dois caches passaram com
exit 0 no `verify_installed_cache.py`, executado a partir de checkout detached limpo do mesmo SHA.

O primeiro `codex plugin add` ainda enxergou o snapshot antigo 0.27.8; após
`codex plugin marketplace upgrade orquestra`, o catálogo passou a 0.27.10. Durante essa troca, o
instalador removeu o cache 0.27.8 referenciado pela tarefa viva e reproduziu o ENOENT histórico do
T-047. O backup preparado antes da atualização foi restaurado imediatamente; 0.27.8 e 0.27.10
permanecem lado a lado, e o hook da tarefa viva voltou a responder.

Processos novos do Claude CLI e do `codex exec` responderam respectivamente
`ORQ_CLAUDE_02710_OK` e `ORQ_CODEX_02710_OK`. Em sessão Codex nova, `/hooks` mostrou o
`SessionStart` do `orq@orquestra` ativo, com matcher `^(clear|compact)$` e comando apontando para
`0.27.10/scripts/context-guard.py`. Os sete testes focados de runtime passaram separadamente nos
caches Claude e Codex; o teste do contrato documental passou na fonte limpa, pois `memory/wiki/`
não integra o bundle instalado.

O card está fechado nos hosts macOS validados. Suporte em Windows real continua explicitamente
**não validado**; essa ausência não bloqueia a release para as plataformas já comprovadas.

## ⏭️ RETOMAR AQUI

Nenhuma ação pendente no T-044. Reabrir somente diante de regressão comportamental ou para uma
campanha específica de validação em Windows real.
