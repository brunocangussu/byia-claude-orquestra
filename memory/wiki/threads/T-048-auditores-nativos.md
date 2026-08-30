# T-048 — auditores nativos de remoção e adoção

**Estado:** commit autorizado · aguardando instalação · **frente:** `@frente-auditoria-nativa` · **release candidata:** 0.22.5.

## Decisão aprovada

Portar as ideias úteis do piloto Cartographer sem instalar ou integrar o Cartographer. A fase 1
entrega dois CLIs Python stdlib: ledger verificável de remoção e análise de trace graph-first.
Claude, Codex e Kimi compartilham o mesmo núcleo; somente Claude ganha o slash command.

## Contratos e plano

- Desenho: `docs/superpowers/specs/2026-08-29-auditores-nativos-design.md`.
- Plano: `docs/superpowers/plans/2026-08-29-auditores-nativos.md`.
- Sem rede, LLM externa, captura viva, hook ou bloqueio.
- `orq/hooks/hooks.json` e `orq/scripts/context-guard.py` são escopo proibido nesta fase.
- Nenhum commit, push, instalação ou publicação sem gate posterior do dono.

## Evidência parcial

- Baseline da 0.22.4: 119 testes, lint e manifesto verdes.
- RED observado com scripts/schema ausentes.
- GREEN ampliado: 151 testes passam; remoção cobre 13/13 âncoras, histórico, autocontaminação,
  Unicode/UTF-16, binários, arquivo grande, symlink, ledger adulterado e argv hostil.
- O primeiro painel encontrou falsos verdes no auditor de adoção. A primeira rodada Opus foi
  corrigida e a segunda revisão Kimi voltou GO condicional. A rodada Opus mais recente continua
  NO-GO por cinco classes reproduzíveis: comando shell multilinha, redirecionamento, wrappers
  encadeados, ações de grafo sem procedência e eventos sem forma canônica reconhecida.
- Recibos de grafo entram apenas por `--graph-receipt`; o auditor não chama MCP nem shell.

## Checkpoint de recuperação — 2026-08-29

A compactação ocorreu antes de um checkpoint verificado. Memória, board e esta thread foram
reconciliados no worktree certo. O escopo continua T-048; nenhum hook, cache, instalação, commit,
push ou publicação foi alterado. A próxima ação segura é transformar os cinco bloqueios Opus em
testes RED, aplicar as correções mínimas e repetir suíte, lint, manifesto, diff proibido e painel.

## Checkpoint de recuperação pós-compactação — 2026-08-29

Memória, board, plano, diff e esta thread foram relidos no worktree isolado. Os cinco bloqueios do
auditor de adoção já foram corrigidos em TDD; a suíte chegou a 175 testes verdes e o lote B do Opus
retornou GO. Permanecem somente a reconciliação dos processos Opus A/Kimi, a revisão fatiada do
auditor de remoção e os gates frescos. O card segue em implementação; nenhum hook, cache,
instalação, commit, push ou publicação foi alterado.

## Evidência atual — 2026-08-29

- Adoção: campos canônicos inválidos, lista vazia de ferramenta e shell não tokenizável fecham sem
  falso verde; 43 testes focados passam. Opus 5 reconciliou o caminho crítico e retornou GO.
- Remoção: FIFO/especial não bloqueia, UTF-16/32 sem BOM e arquivos grandes entram na busca,
  ilegíveis falham fechado, ledger fica dentro da raiz, recibo duplicado é inválido e tombstones
  persistem. Os 22 testes focados passam; Opus 5 retornou GO para scanner e ledger/verify.
- Gates: 183 testes completos, Ruff, `py_compile`, lint de coerência, manifesto estrito, schemas,
  versão 0.22.5 e `git diff --check` passam. Os arquivos proibidos permanecem sem diff.
- Kimi K3 encontrou o último falso verde de campo canônico não-string; o repro foi confirmado e
  corrigido. Após o reset da cota, a revisão final de adoção retornou GO.
- A revisão final de remoção encontrou um crash de serialização para paths com surrogate. O achado
  foi reproduzido em teste RED, `write_json` passou a usar JSON ASCII-safe e o teste ficou GREEN.
  A nova revisão Kimi K3 sobre os bytes corrigidos retornou GO. O painel está completo.
- Nenhum cache, instalação, commit, push ou publicação foi alterado.

## Checkpoint de recuperação pós-compactação e painel — 2026-08-29

Memória, board e esta thread foram reconciliados no worktree isolado depois da compactação. A cota
do Kimi foi confirmada operacionalmente por duas invocações reais `kimi-code/k3` em diretórios
temporários: adoção GO e remoção GO após um ciclo RED/GREEN para surrogate em JSON. O estado seguro
é repetir os gates completos sobre 184 testes e, se verdes, mover T-048 para VALIDATE. Commit,
instalação, push e publicação continuam proibidos até novo gate do dono.

## Gates finais — 2026-08-29

- 184 testes completos: PASS.
- Ruff no Python 3.12.12: PASS.
- `py_compile` com cache temporário externo: PASS.
- Lint de coerência (20 nomes), manifesto estrito e schemas/versão 0.22.5: PASS.
- `git diff --check`, arquivos proibidos e `origin/main..HEAD == 0`: PASS.
- Painel real: Opus 5 GO e Kimi K3 GO nos dois auditores.

## Limites que a validação deve observar

- `--retain` e `--exclude` amplos demais são decisão explícita do operador e podem ocultar o alvo;
  a validação deve conferir o escopo gravado no ledger.
- Ledger, receipts e trace são provas locais declarativas, não artefatos autenticados contra um
  agente hostil. O auditor prova o conteúdo fornecido, não a honestidade da origem.
- Nenhum desses limites gerou falso verde não declarado no contrato atual; ambos ficam visíveis na
  saída/ledger e permanecem riscos documentados.

## Roteiro de validação prática do dono

1. Em um repositório autoral temporário, rodar `audit-removal.py scan` com um alvo presente e
   confirmar `needs-removal`/exit 1.
2. Remover o alvo, rodar `verify` com o mesmo escopo e recibo exigido e confirmar `pass`/exit 0.
3. Rodar `audit-adoption.py` sobre um trace graph-first e confirmar `pass`/exit 0.
4. Rodar o mesmo auditor sobre um trace direct-first e confirmar `fail`/exit 1.

## Validação prática executada — 2026-08-29

O dono autorizou a execução em repositório autoral temporário. Resultado: 10/10 checks passaram.

- `scan` com alvo presente: `needs-removal`, exit 1, uma evidência ativa.
- Remoção do alvo + `verify` com `unit=pass`: `pass`, exit 0, recibo persistido no ledger.
- Trace graph-first: `pass`, exit 0.
- Trace direct-first: `fail`, exit 1.

O primeiro harness procurou o recibo em `verification.receipts`, chave inexistente; o auditor já
tinha retornado `pass`. O harness foi alinhado ao contrato real `validationReceipts` e o ensaio foi
repetido do zero com zero falhas. Nenhum projeto real, cache, hook ou estado externo foi tocado.

## ⏭️ RETOMAR AQUI

A validação prática passou e o dono autorizou o commit local da candidata 0.22.5. Após criar e
verificar o commit, parar na pergunta: autoriza instalar localmente a 0.22.5 nos hosts Codex,
Claude e Kimi? Push/publicação continuam em gate separado.
