# T-097 — organização e integração segura dos worktrees

**Estado:** PLANNING · **frente:** `@frente-organizacao-worktrees` · **host:** `@codex`

## Objetivo

Inventariar todos os worktrees e branches locais, separar trabalho integrável, bloqueado, obsoleto
e descartável, integrar somente candidatos aprovados sem regressão e remover apenas worktrees cuja
recuperabilidade esteja comprovada.

## Por que existe

O repositório acumulou muitas frentes isoladas. A quantidade já dificulta distinguir candidato
válido de experimento antigo e aumenta o risco de integrar diff stale, apagar trabalho de outra
janela ou executar um commit amplo sobre a raiz compartilhada.

## Restrições do planejamento

- preservar integralmente a raiz suja e todo trabalho da janela Claude;
- não usar `git add .`, cherry-pick cego, reset, checkout destrutivo ou remoção recursiva ampla;
- nenhum worktree é removido só por estar antigo: antes, provar HEAD, dirty state, card, revisão,
  divergência contra `main` e existência de cópia recuperável;
- integração exige gates frescos, staging allowlisted e commit rastreável por card;
- remoção, merge, commit e push ficam fora do planejamento até aprovação explícita do dono.

## Fases

- ✅ inventário verificável de worktrees, branches, cards e sobreposições;
- ✅ classificação por destino: integrar, revisar, reconciliar, arquivar ou remover;
- ✅ plano de lotes com ordem, gates e rollback;
- ⬜ gate do dono antes de qualquer remoção ou integração.

## Inventário consolidado — 2026-09-20

- 39 worktrees, 47 branches locais, 34 checkouts sujos e 5 limpos;
- três limpos já integrados: T-001, T-071 e T-081;
- T-076 limpo com patch equivalente já integrado;
- T-044 antigo limpo, com o commit exclusivo `639a0b9` preservável pela branch;
- T-070 contradiz seu card fechado: commit exclusivo mais `_noturno.md` não commitado;
- T-095 possui consumidor vivo e está fora de qualquer remoção;
- 12 worktrees são de cards governados pelo board New ByIA, entre `VALIDATE` e `DEV_REVIEW`;
- nenhuma candidata suja será promovida por merge cego de branch.

### Manifesto pré-remoção do Lote 1

| Checkout | Branch preservada | HEAD preservado | Estado | Consumidor vivo |
|---|---|---|---|---:|
| `t001-hooks-security` | `codex/t001-hooks-security` | `7f25b6fc8ad2` | limpo, sem ignored | 0 |
| `t071-archive-heading` | `codex/root-reconcile-20260916` | `2b5ee0170089` | limpo, sem ignored | 0 |
| `t081-observation-types` | `codex/t081-observation-types` | `fd33de67bae2` | limpo; só caches de ferramentas/bytecode | 0 |
| `t076-board-root` | `codex/t076-board-root` | `d4f0f82895de` | limpo; só caches de ferramentas/bytecode | 0 |
| `t044-reset-concurrency-0223` | `codex/t044-reset-concurrency-0225` | `639a0b965777` | limpo; só caches de ferramentas | 0 |

Todas as cinco refs locais foram comprovadas antes da remoção. O conteúdo ignorado listado pelo Git
é descartável (`.code-review-graph`, `.serena`, `.ruff_cache` e `__pycache__`); não há arquivo de
produto ou artefato durável sem destino.

Plano detalhado:
`docs/superpowers/plans/2026-09-20-t097-organizacao-worktrees.md`.

## Gate do dono

Recomendação: aprovar a retirada somente dos cinco checkouts limpos, sem apagar branches; adotar o
contrato deste repositório como canônico para eventual integração das candidatas externas; e seguir
a ordem de lotes do plano, mantendo gates específicos para cada mudança de produto.

**Aprovado em 2026-09-20:** o dono autorizou o Lote 1 exatamente nos limites acima e confirmou o
contrato do Orquestra como canônico para futuras integrações. Não autorizou remoção de branches,
`--force`, merge de candidata, commit ou push.

## Resultado do Lote 1 — 2026-09-20

Os cinco checkouts foram removidos individualmente com `git worktree remove`, sem `--force`:

- `t001-hooks-security`;
- `t071-archive-heading`;
- `t081-observation-types`;
- `t076-board-root`;
- `t044-reset-concurrency-0223`.

Após cada operação, o registro do worktree desapareceu e sua branch permaneceu resolvível. O total
caiu de 39 para 34. A branch `codex/t044-reset-concurrency-0225` continua apontando para
`639a0b96577717fdfcfb9f64558445500eb61a76`; nenhum commit exclusivo foi perdido. Não houve merge,
remoção de branch, commit, push, publicação, instalação ou restart.

## Autorização do Lote 2 — 2026-09-20

O dono autorizou exclusivamente a reconciliação **read-only** de T-070 e da linhagem T-044/T-122.
O resultado deve propor o destino antes de qualquer commit, merge ou remoção; nenhuma mutação nos
worktrees candidatos está autorizada.

## Resultado da reconciliação read-only — 2026-09-20

Parecer completo:
`docs/reviews/2026-09-20-t097-lote2-reconciliacao.md`.

- T-070 já foi integrado semanticamente em `main` por `edc51c4`; não promover `caaad7c`.
- O único conteúdo exclusivo é `_noturno.md` não commitado, retrospectivo e expirado; recomendação:
  descartar esse diff com autorização específica, remover só o checkout e preservar branches/SHA.
- T-044 é a base canônica recomendada. Em prova fresca passou 115/115; T-122 passou 109/109.
- T-122 omite falhas visíveis que T-044 cobre: criação do marcador, save e consumo do snapshot. Sua
  candidata não deve ser mergeada em paralelo.
- Um cenário do T-122 merece ser portado como teste para T-044: não consumir fotografia sem
  persistência comprovada. Os bytes finais do T-044 ainda precisam de revisão independente fresca.
- T-122 continua intocada e sob autoridade do board New ByIA até handoff explícito.

## Destino executado: T-070 — 2026-09-20

O preflight confirmou que o checkout tinha exatamente um caminho modificado,
`memory/wiki/threads/_noturno.md`, e nenhum processo vivo referenciava sua raiz. O diff foi
descartado somente nesse arquivo; o checkout ficou limpo e foi removido por `git worktree remove`,
sem `--force`. A branch local e a remota continuam resolvendo para
`caaad7c754f5b82a9ab360017f4702ed85619e59`. O inventário caiu de 34 para 33 worktrees; nenhuma
branch foi removida.

## ⏭️ RETOMAR AQUI

O destino T-070 está concluído e verificável acima. Na frente dona do T-044, o cenário sem
persistência passou por RED/GREEN e a candidata fechou 116/116 focados, 409/409 completos,
manifesto e `diff --check`; o lint aponta somente o cache 0.27.8 sem bump. O T-122 não foi alterado.

A revisão fresca ficou degradada no primeiro dos quatro lotes: o runner Opus iniciou e falhou sem
parecer. O diagnóstico inicial de “Claude CLI deslogado” foi corrigido: o mesmo binário nativo
`2.1.278`, o mesmo `HOME` e o mesmo diretório de configuração funcionam no Terminal, mas
`claude auth status` devolve `loggedIn=false` quando o processo nasce da árvore
`launchd → ChatGPT.app → codex`, inclusive dentro de `zsh -il`. O runner apenas herda esse ambiente;
não faz login, logout nem altera credenciais. O quadro agora registra a condição operacional correta:
**credencial do Keychain inacessível ao subprocesso Codex/headless**, não logout comprovado da conta.

Não houve retry nem envio dos lotes 2–4. Reautenticar repetidamente deixou de ser recomendação:
antes de nova revisão, a frente precisa planejar um transporte estável para o revisor externo e um
preflight que diferencie conta realmente sem credencial de credencial indisponível ao processo host.
Até esse gate, a candidata permanece preservada, sem bump, commit, push, merge, publicação,
instalação ou restart.

## Decisão do dono: transporte exclusivamente via Claude CLI — 2026-09-20

O dono recusou broker, API key, `setup-token`, token injetado ou credencial paralela. O contrato
obrigatório é somente:
`Codex → subprocesso claude CLI → modelo solicitado → espera síncrona → resposta comprovada`.
O Orquestra não recebe, lê, copia nem armazena segredo; a autenticação continua responsabilidade do
próprio Claude CLI.

### Diagnóstico complementar

- O runner atual já satisfaz o transporte: usa `subprocess.run`, aguarda `claude -p`, lê JSON e
  valida a identidade do modelo.
- `claude auth status` retornou `loggedIn=false` no processo direto, em `zsh -il`, com ambiente
  mínimo, em PTY, via `launchctl asuser` e reproduzindo `login -pf` como o Terminal. Mesmo binário
  nativo `2.1.278`, mesmo `HOME` e mesmo `~/.claude`.
- Uma única prova externa sintética, autorizada pelo pedido do dono e sem código/PII, chamou
  diretamente `claude -p --model opus` e terminou `exit 1`, custo zero, com
  `Failed to authenticate: OAuth session expired and could not be refreshed`. Não houve retry.
- Portanto, o bloqueio não é ausência de token do Orquestra. O subprocesso está selecionando uma
  sessão OAuth expirada e não consegue renová-la; o dono relata que o Claude CLI aberto no Terminal
  continua funcional, indicando estados de credencial divergentes dentro do próprio Claude Code.

### Próximo gate proposto

Executar uma única vez `claude auth login` **pelo mesmo CLI e no mesmo contexto do subprocesso do
Codex**, deixando o próprio Claude Code conduzir o navegador e persistir sua credencial. O Orquestra
não inspeciona nenhum valor. Depois, abrir processos novos e provar: dois `auth status`, duas chamadas
sequenciais `claude -p --model opus`, identidade do modelo e preservação do login no Terminal. Se o
estado não sobreviver a processos novos, parar sem retry: será falha persistente do armazenamento do
Claude CLI, não algo corrigível pelo runner sem violar a proibição de credencial paralela.

Nenhum token foi criado, lido ou alterado pelo Orquestra nesta etapa.

## Gate executado: reautenticação CLI e prova comportamental — 2026-09-20

Com autorização nominal, o Manager executou exatamente uma vez `claude auth login` no mesmo
contexto do subprocesso Codex. O próprio Claude CLI abriu o fluxo oficial e terminou
`Login successful`; nenhum token, senha ou código foi solicitado no chat, lido ou armazenado pelo
Orquestra. Não houve logout.

Provas em processos novos e independentes:

1. `claude auth status`: `loggedIn=true`, `authMethod=claude.ai`, assinatura `max`;
2. chamada sintética 1: `exit 0`, `is_error=false`, resposta exata `CLI_REAUTH_1_OK`, identidade
   `claude-opus-5`;
3. chamada sintética 2: `exit 0`, `is_error=false`, resposta exata `CLI_REAUTH_2_OK`, identidade
   `claude-opus-5`;
4. novo `claude auth status` após ambas: continuou `loggedIn=true` por `claude.ai`.

Não houve retry, API key, token manual, commit, push, publicação, instalação ou restart. A
autorização cobria somente as duas provas sintéticas, portanto a revisão fresca do T-044 não foi
reaberta. Observação separada de custo: a segunda chamada reportou 155.004 tokens de criação de
cache mesmo com prompt mínimo; isso não afetou a prova de autenticação, mas deve ser investigado
antes de usar o runner em lotes extensos.

## Checkpoint de recuperação e inventário vivo — 2026-09-21

Após compactação, o Manager recomprovou o pacote absoluto instalado `0.27.8`, a existência de
`scripts/kanban-status.sh` e o resolver oficial com `state=ok`, `exists=true`, board e raiz de
threads canônicos. O pedido atual continua sendo concluir as candidatas úteis e reduzir a dívida de
worktrees/branches sem perder trabalho.

O inventário somente leitura, confrontado também com o `origin/main` remoto por `ls-remote`, provou:

- `HEAD`, `main`, `origin/main` local e remoto continuam no mesmo `7f25b6fc8`;
- a raiz compartilhada possui 63 caminhos sujos (20 rastreados e 43 não rastreados), sem merge,
  rebase, cherry-pick ou outra operação Git em curso;
- existem 33 registros de worktree: 25 diretórios presentes e oito diretórios já ausentes;
- descontada a raiz, os 24 worktrees presentes contêm mudanças reais; nenhum está limpo;
- as oito entradas ausentes (`T-113`, `T-117`–`T-123`) têm branches preservadas, já ancestrais de
  `main` e sem commit exclusivo; são candidatas apenas à limpeza do registro administrativo, nunca
  a remoção de branch implícita;
- há 37 branches locais; somente quatro branches sem checkout conservam um commit não integrado:
  `backup-t049-pre-reconcile`, `root-recovery-20260916`, `t044-reset-concurrency-0225` e
  `t070-memory-truth`;
- nenhum dos snapshots sujos presentes é cópia exata de outro. Há 50 caminhos sobrepostos e até 14
  variantes concorrentes do mesmo arquivo (`lint-coerencia.py`), portanto merge em massa ou
  `git add .` perderia decisões;
- quatro worktrees presentes sem card neste board são alternativas governadas pelo New ByIA e
  precisam de reconciliação read-only com as frentes canônicas: `T-114`↔`T-031`,
  `T-125`↔`T-091`, `T-128`↔`T-042` e `T-130`↔`T-032`;
- a fonte publicada continua em `0.27.8`; os caches Claude e Codex contêm `0.27.8` com
  `kanban-status.sh` e `context-guard.py`. Isso descreve a versão já disponível, não valida as
  candidatas ainda não integradas.

Classificação operacional:

1. **limpeza administrativa segura após gate:** remover somente os oito registros de diretório
   ausente, sem `--force` e preservando todas as branches;
2. **reconciliação antes de destino:** auditar os quatro pares New ByIA acima e portar apenas
   cenários úteis para a candidata canônica antes de qualquer remoção;
3. **primeira candidata de produto:** concluir a revisão fresca do `T-044`, já em 409/409, agora que
   o Claude CLI voltou a responder; só um parecer aprovado abre o gate separado de versão e
   integração;
4. **raízes compartilhadas:** isolar e revisar separadamente `T-022` e `T-096`, hoje presentes na
   raiz suja, antes de reconciliar `T-032` e `T-042` que tocam as mesmas superfícies;
5. **não promovíveis agora:** `T-047`, `T-062` e `T-094` continuam bloqueados por revisão degradada,
   reprovação ou dependência; não entram num lote de produção por conveniência de limpeza.

Nenhum worktree, branch ou arquivo foi removido neste checkpoint. Não houve teste externo novo,
review, bump, commit, push, merge, publicação, instalação ou restart.

## Resultado do Lote 3 — 2026-09-21

O `git worktree prune --dry-run --verbose` listou exatamente as oito entradas previamente provadas
como ausentes: `T-113`, `T-117`, `T-118`, `T-119`, `T-120`, `T-121`, `T-122` e `T-123`. O prune
real removeu somente esses registros administrativos, sem `--force`. A pós-condição ficou em 25
worktrees registrados, todos com diretório existente, e 37 branches locais preservadas.

### Reconciliação read-only dos quatro pares

Todas as oito candidatas passaram a própria suíte completa, mas a execução cruzada dos contratos
provou que nenhuma alternativa é superconjunto da frente canônica:

- `T-031` 416/416 e `T-114` 406/406; sob a união dos contratos, T-031 falha em nove cenários e um
  erro da alternativa, enquanto T-114 falha em dezesseis cenários da canônica. Destino: preservar
  T-031 e portar a matriz/guarda explícita do reviewer Opus de T-114;
- `T-032` 404/404 e `T-130` 403/403; cruzados, T-032 falha em sete contratos de escrita e T-130
  produz oito erros nos contratos de concorrência. Destino: preservar T-032 e portar os cenários
  de autoria/append de T-130, reconciliando também o T-022 antes de integrar;
- `T-042` 407/407 e `T-128` 402/402; cruzados, T-042 tem uma falha e sete erros no contrato
  read-only, enquanto T-128 tem sete falhas e três erros no fluxo completo. Destino: preservar
  T-042 e portar as guardas de referência/symlink de T-128 depois do T-096;
- `T-091` e `T-125` passam 418/418 isoladamente; cruzados, T-091 tem dezessete falhas e cinco erros
  no contrato alternativo, e T-125 tem vinte e nove falhas e oito erros no contrato canônico.
  Destino: preservar T-091 e portar limites/races úteis de T-125 antes de revisar T-092.

Nenhum arquivo desses pares foi editado, portado ou removido neste lote.

### Revisão fresca do T-044

Antes do egress, a candidata foi revalidada em 409/409, manifesto estrito e `diff --check` verdes;
o lint acusou somente a divergência esperada do cache 0.27.8. O snapshot permaneceu com 35.096
bytes e SHA-256 `4ec0a9bf2316c7f512cf85ec2741a420741505de1110e8f285b88a1c81326c60`.
Scanners de caminho pessoal, nome do dono, e-mail, credenciais, chave privada, token e CPF deram
zero; “diagnóstico” apareceu uma vez em sentido técnico, sem dado clínico.

A única rodada autorizada foi dividida em quatro lotes de 5.521, 11.636, 12.373 e 12.427 bytes.
Todos saíram uma vez pelo runner oficial, sem retry, e comprovaram `claude-opus-5`:

- lote 1, documentação: **APROVADO**;
- lote 2, produção: **APROVADO**;
- lote 3, primeira metade dos testes: **BLOQUEADO** por duas lacunas de oráculo;
- lote 4, segunda metade dos testes: **APROVADO**.

O Manager confirmou os dois bloqueadores contra os bytes completos:

1. `test_clear_marker_creation_failure_warns_when_fallback_cannot_remove_state` exige apenas as
   palavras “falhou aberto” e “reset”. A mensagem do caminho de sucesso também satisfaz esse
   subconjunto, então o teste pode informar falsamente que o estado foi removido quando o arquivo
   continua no disco e nenhum marcador existe;
2. `pending_reset_markers()` declara não reutilizar a lógica de produção, mas chama
   `_state_reset_path()`. Uma regressão do caminho, inclusive quebrando compatibilidade do marcador
   legado, move simultaneamente a produção e o oráculo e pode deixar a suíte verde.

Resultado global: **T-044 não está aprovado para bump ou integração**. A próxima ação é corrigir
somente esses oráculos com RED/GREEN e mutation checks, repetir os gates locais e pedir autorização
nominal para nova revisão. Não houve correção, bump, commit, push, merge, publicação, instalação ou
restart.

## Checkpoint pós-integração do T-044 — 2026-09-22

O bloqueio descrito acima foi resolvido na frente dona: o produto entrou em `origin/main` por
`df98d9c` e a documentação/validação por `69e8805`; a versão 0.27.10 foi instalada e verificada nos
dois hosts. Este checkpoint não reabre nem altera o T-044.

O inventário vivo, exclusivamente read-only, encontrou 25/25 registros com diretório existente:

- somente `codex/t044-reset-concurrency-port` está limpo, em `69e8805`, sem commits à frente e já
  absorvido por `origin/main`;
- os outros 24 checkouts estão sujos e foram preservados integralmente;
- nenhum registro ausente reapareceu;
- quatro branches sem checkout continuam não absorvidas (`backup-t049-pre-reconcile`,
  `root-recovery-20260916`, `t044-reset-concurrency-0225` e `t070-memory-truth`) e permanecem fora de
  qualquer limpeza sem reconciliação específica.

## ⏭️ RETOMAR AQUI

O Lote 4 recomendado é estritamente administrativo: remover somente o checkout limpo
`codex/t044-reset-concurrency-port` com `git worktree remove`, sem `--force`, preservando a branch e
comprovando a pós-condição. Depois, abrir gates independentes nas frentes donas para portar os
cenários úteis dos quatro pares já reconciliados; não misturar esses produtos no lote de limpeza.

Este checkpoint não removeu worktree ou branch e não executou commit, push, merge, publicação,
instalação ou restart.

## Resultado do Lote 4 — 2026-09-22

O preflight comprovou que `codex/t044-reset-concurrency-port` estava limpo, em
`69e88058ed740a79adeb7299d87de8a532b0d7b5`, exatamente o mesmo SHA de `origin/main` e ancestral
dele. O checkout foi removido por `git worktree remove` sem `--force`.

As pós-condições comprovaram:

- o diretório e o registro do worktree desapareceram;
- o inventário caiu de 25 para 24 worktrees, todos com diretório existente;
- a branch `codex/t044-reset-concurrency-port` continua resolvendo para `69e8805`;
- nenhum dos 24 worktrees restantes foi alterado;
- nenhuma branch foi apagada.

## Próximo lote proposto — Lote 5

Fazer somente a reconciliação read-only das quatro branches locais sem checkout e ainda não
ancestrais de `origin/main`:

1. `codex/backup-t049-pre-reconcile` (`aaf1aab`): provar se o verificador de caches e seus contratos
   já foram superados pela implementação atual;
2. `codex/root-recovery-20260916` (`793e1f3`): confrontar o checkpoint T-094/T-078 com a memória e
   documentação atuais, preservando qualquer decisão ainda exclusiva;
3. `codex/t044-reset-concurrency-0225` (`639a0b9`): provar que a implementação final 0.27.10 é
   superconjunto funcional e documental da candidata histórica;
4. `codex/t070-memory-truth` (`caaad7c`): recomprovar que o conteúdo válido já entrou em `main` pela
   linhagem posterior.

O resultado deve classificar cada branch como `preservar`, `arquivar` ou `candidata a apagar`, com
evidência por conteúdo e histórico. O Lote 5 não implementa produto, não modifica branch e não
autoriza exclusão; qualquer remoção de branch exigirá um gate posterior nominal.

## ⏭️ RETOMAR AQUI

Aguardar autorização para executar somente a reconciliação read-only do Lote 5. Não iniciar os
ports dos quatro pares de produto nem apagar branches enquanto esse gate não for aprovado.

## Resultado da reconciliação read-only do Lote 5 — 2026-09-22

Nenhuma ref, branch, worktree ou arquivo de produto foi alterado. A reconciliação examinou os
commits exclusivos, os caminhos tocados, a sobrevivência das adições em `origin/main`, a história
posterior e os contratos Python por AST.

### `codex/backup-t049-pre-reconcile` — arquivar antes de retirar a branch

- SHA preservado: `aaf1aab64d8992db57592a5a1accaea2ecd83c75`.
- A implementação vigente deriva da linhagem posterior `deabd4d`; nenhuma função antiga do
  comparador ou do lint sumiu, e a suíte atual acrescentou a normalização de bytecode e nove
  contratos específicos.
- A thread antiga existe em `origin/main` sob
  `memory/wiki/threads/_concluidas/T-049-verificador-instalacao.md`, com 117 linhas contra 100 da
  candidata; as dez linhas não idênticas são estado intermediário obsoleto de versão/gate.
- Destino: criar ref de arquivo no SHA e, somente em gate posterior, retirar a branch local.

### `codex/root-recovery-20260916` — arquivar antes de retirar a branch

- SHA preservado: `793e1f35677de2e0c65bfe9b16a525b5571fefea`.
- Os seis artefatos centrais de T-094/T-078 são byte-idênticos em `2b5ee01`/`origin/main`;
  `git diff --exit-code` retornou zero.
- Todas as adições duráveis em plano, avaliação, coexistência, elenco, fixes e threads sobrevivem.
  As únicas linhas ausentes são cabeçalho de versão e três estados transitórios do board que
  corretamente avançaram depois.
- Destino: criar ref de arquivo no SHA e, somente em gate posterior, retirar a branch local.

### `codex/t044-reset-concurrency-0225` — arquivar; não apagar diretamente

- SHA preservado: `639a0b96577717fdfcfb9f64558445500eb61a76`.
- A 0.27.10 substituiu `_apply_pending_reset()` por preparo/finalização transacionais, acrescentou
  quatorze contratos na suíte principal e preservou os comportamentos antigos sob testes atuais
  renomeados ou movidos para `test_verify_installed_cache.py`.
- A thread final e a arquitetura atuais são maiores e descrevem o contrato vigente, mas a branch
  antiga conserva evidência intermediária de revisão, versão 0.22.5 e gates que não sobrevive
  literalmente em `main`.
- Destino: criar ref de arquivo no SHA antes de retirar a branch; não classificar como descarte
  direto.

### `codex/t070-memory-truth` — candidata a retirar a branch local

- SHA local: `caaad7c754f5b82a9ab360017f4702ed85619e59`; a mesma ref continua no remoto.
- Todas as 82 linhas adicionadas pelo commit sobrevivem exatamente em `origin/main`; a thread
  T-070 é byte-idêntica, e a linhagem posterior `edc51c4` consolidou o estado compartilhado.
- Destino: candidata a retirar somente a branch local; a branch remota fica intacta.

## ⏭️ RETOMAR AQUI

Próximo gate recomendado, ainda administrativo: no Lote 6, criar refs locais de arquivo para os
três SHAs sem cobertura remota suficiente (`aaf1aab`, `793e1f3`, `639a0b9`) e só depois retirar as
quatro branches locais. Como Git não reconhece equivalência semântica como ancestralidade, a
remoção exigirá `git branch -D` nominal e explícito; não executar por inferência. Preservar todas as
refs remotas, os 24 worktrees e seus arquivos. Não iniciar ports de produto neste lote.

## Resultado do Lote 6 e checkpoint de recuperação — 2026-09-22

Foram criadas três tags locais de arquivo, cada uma comprovada contra o SHA de origem:

- `archive/t097/t049-pre-reconcile-aaf1aab` → `aaf1aab64d8992db57592a5a1accaea2ecd83c75`;
- `archive/t097/root-recovery-20260916-793e1f3` → `793e1f35677de2e0c65bfe9b16a525b5571fefea`;
- `archive/t097/t044-reset-0225-639a0b9` → `639a0b96577717fdfcfb9f64558445500eb61a76`.

Somente depois dessa prova, saíram as quatro branches locais reconciliadas:
`codex/backup-t049-pre-reconcile`, `codex/root-recovery-20260916`,
`codex/t044-reset-concurrency-0225` e `codex/t070-memory-truth`. A ref remota
`origin/codex/t070-memory-truth` permaneceu em `caaad7c754f5b82a9ab360017f4702ed85619e59`.
Nenhum worktree, ref remota ou arquivo de produto foi removido nesse lote.

Após compactação, o inventário foi recomposto pelo resolver canônico. Há 24 worktrees: a raiz e 23
checkouts extras, todos sujos e sem consumidor vivo detectado pelo caminho do checkout. Cada um dos
23 snapshots é único; nenhum é byte-idêntico, subconjunto exato de outro ou já absorvido por
`origin/main`. Portanto, remoção direta ou descarte por equivalência continuam proibidos.

O próximo lote administrativo preservará cada dirty snapshot em uma tag local apontando para um
objeto `stash` com tracked e untracked, comprovará os blobs antes de limpar o checkout e só então
usará `git worktree remove` sem `--force`. As branches permanecem. Ignorados são caches de
ferramenta, exceto os recibos `.superpowers/sdd` e `memory/wiki/review-journal` do T-062; nesse
checkout, o snapshot incluirá também os ignored para não perder os recibos. Não haverá integração,
feature, bump, publicação, instalação ou restart.

## ⏭️ RETOMAR AQUI

Executar primeiro o protocolo reversível em `codex/t059-partial-reads` como prova operacional. Se a
tag reproduzir todos os blobs e o checkout ficar limpo, remover somente esse worktree sem `--force`
e aplicar o mesmo protocolo aos demais checkouts extras. A raiz compartilhada não entra no lote.

## Resultado do lote reversível — 2026-09-22

O protocolo foi provado primeiro no T-059 e depois aplicado aos outros 22 checkouts. Para cada
worktree, o processo:

1. registrou branch, HEAD, conjunto tracked/untracked e SHA-256 do snapshot;
2. criou um objeto `stash`, conferiu seu primeiro parent contra o HEAD e comparou cada blob e modo
   de arquivo com os bytes ainda no checkout;
3. criou uma tag anotada `archive/t097/worktree/<slug>-20260922` com branch, HEAD, digest e comando
   de restauração;
4. removeu o `stash` transitório somente depois de a tag resolver para o mesmo objeto;
5. removeu o checkout com `git worktree remove`, sem `--force`, e comprovou que a branch não se
   moveu.

O T-031 tinha `orq/scripts/test_elenco_runtime_contract.py` em `intent-to-add`, condição que o
`git stash` recusa. O índice foi normalizado somente depois de registrar essa intenção; a tag do
T-031 contém `intent_to_add=...` e o passo `git add -N` necessário para reconstruí-la. O T-062 usou
captura com ignored: 31 blobs no terceiro parent, dos quais 22 são recibos de `.superpowers/sdd` e
`memory/wiki/review-journal`; caches também ficaram preservados nesse único snapshot.

As 23 tags passaram a prova tag → stash → primeiro parent → HEAD, sem divergência. Depois foram
retiradas as 23 branches locais correspondentes, pois a tag conserva tanto a base quanto o estado
sujo integral. Também saíram nove ponteiros locais sem checkout, todos ancestrais de `origin/main`
e sem commit exclusivo. Nenhuma ref remota foi alterada.

Pós-condição:

- um único worktree permanece: a raiz compartilhada;
- a única branch local é `main`;
- 26 tags `archive/t097/*` preservam três SHAs históricos e 23 dirty snapshots;
- o stash preexistente `wip-t052-pre-merge` continua intacto;
- quatro refs remotas históricas permanecem: T-044 e T-071 já ancestrais da main, T-070 e T-076
  com um commit remoto exclusivo cada;
- não houve feature, integração de produto, bump, push, publicação, instalação ou restart.

A raiz compartilhada não foi submetida a `stash/apply`: processos do host mantêm esse diretório
como `cwd`, e uma mutação temporária criaria risco de corrida com trabalho paralelo. Ela permaneceu
byte a byte no estado original; a limpeza atuou somente nos checkouts extras e nas refs locais já
preservadas.

Para restaurar um snapshot, crie um worktree/branch no primeiro parent da tag e aplique a própria
tag com `git stash apply --index`. A mensagem anotada da tag informa branch, HEAD, digest e o comando
exato; a tag do T-031 acrescenta a restauração do `intent-to-add`.

## Fechamento administrativo e reconciliação da raiz — 2026-09-22

O dono validou a organização e autorizou concluir a reconciliação. Antes de limpar a raiz
compartilhada, o Manager construiu um snapshot **sem alterar worktree nem índice real** com um índice
Git temporário e comparou todos os 63 caminhos modificados/não rastreados, inclusive modo e bytes:

- tag anotada: `archive/t097/root-shared-pre-reconcile-20260922`;
- commit do snapshot: `182e39afd9fbe378134ccd8632c12b9a6373da65`;
- SHA-256 do inventário: `82a67bf6c668de4f33104aea6ba20d95e9097f383db5d5a2cdb8a77fd3c93015`;
- HEAD original preservado: `7f25b6fc8ad28da0548aa7d63a1cffaa5cc1b82b`.

Uma edição concorrente posterior em `memory/gotchas.md` foi detectada antes da limpeza. Em vez de
perdê-la, o Manager repetiu a captura sobre o estado final e provou novamente os 63 caminhos:

- tag final: `archive/t097/root-shared-pre-fast-forward-20260922`;
- commit final: `9b452f9c25bc92e7127dc70d269b08d49944e94c`;
- SHA-256 do inventário final: `ac356e72405d42fbf08918ec517c5c323d2d6eb3b114c7b8252ec7d817372e82`.

Com essas referências, os dois estados da raiz podem ser reconstruídos sem mantê-la suja. O
fechamento deixa como pós-condição:

- um único worktree e somente a branch local `main`;
- 28 referências locais `archive/t097/*`: 23 snapshots de worktree, três SHAs históricos e dois
  snapshots sucessivos da raiz;
- o stash preexistente `wip-t052-pre-merge` preservado;
- as quatro refs remotas históricas mantidas deliberadamente, sem exclusão remota;
- fonte local reconciliada com `origin/main`, mantendo a versão 0.27.10;
- nenhuma alteração de produto, publicação de plugin, instalação ou restart.

O card fecha como trabalho administrativo validado. Qualquer limpeza das quatro refs remotas exige
outro gate explícito; não faz parte do T-097.
