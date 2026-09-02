# T-048 — auditores nativos de remoção e adoção

**Estado:** concluído · **frente:** `@frente-auditoria-nativa` · **release:** 0.22.5.

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

## Desenho original — do ramo local, incorporado na reconciliação `T-052`

⚠️ **Cronologia, não estado corrente.** Estas seções nasceram no ramo da `0.24.0` como o desenho
aprovado no gate de 2026-08-29 e **já foram implementadas e publicadas na `0.22.5`**. Ficam aqui
porque registram *por que* o desenho é este e o que foi recusado — o resto do arquivo diz como
terminou. O ponteiro de retomada daquele ramo ("implementar os dois auditores offline com TDD")
está **cumprido**; o marcador vivo é o do fim deste arquivo.

## Origem

O T-045 provou duas coisas diferentes: o Cartographer não melhora a cobertura de descoberta frente
ao stack atual, mas os conceitos de ledger de remoção e prova da ordem graph-first são úteis. O
dono validou o parecer **PORTAR IDEIAS**; este card desenha a versão nativa sem copiar código nem
adicionar a dependência.

## Abordagens consideradas

1. **Instalar ou envolver Cartographer:** rejeitada pela cobertura 11/13, histórico falso-ativo,
   ambiguidade de licença e sobreposição com codebase-memory/Serena.
2. **Dois auditores explícitos e offline — recomendada:** scripts puros, um comando natural comum e
   recibos JSON; nenhuma integração com hooks na fase 1.
3. **Observador automático em PostToolUse:** poderia medir sessões ao vivo, mas amplia a superfície
   do guardião de contexto e arrisca regressão/bloqueio. Diferido para outro card, se ainda fizer
   sentido depois do uso offline.

## Desenho recomendado

Uma entrada natural `/orq:auditar` oferece dois modos independentes. No Codex, a skill reconhece a
mesma intenção e chama o script; no Claude, o slash command é apenas a interface. O núcleo e o schema
são os mesmos nos dois hosts.

### `auditar remocao <alvo>`

- Descobre candidatos por variantes literal, kebab-case, snake_case, UPPER_SNAKE, imports e símbolos.
- O Manager adiciona ao ledger os recibos de codebase-memory/Serena; o script não tenta chamar MCP.
- Cada evidência fica em `active`, `retained-historical`, `removed` ou `ambiguous`, com caminho,
  linha, classe, consulta e timestamp.
- O ledger registra root, commit, dirty state, alvo, exclusões, comandos de validação e resultado.
- O próprio ledger, `.git`, dependências e artefatos gerados são excluídos por padrão.
- A verificação falha se houver `active`/`ambiguous`, se faltar âncora crítica declarada ou se um
  comando obrigatório não tiver recibo; histórico retido não bloqueia.

### `auditar adocao <trace.json>`

- Consome eventos normalizados fornecidos explicitamente; não captura a sessão na fase 1.
- Classifica ferramentas de grafo, busca textual, leitura direta de fonte e mutação.
- Passa quando o primeiro acesso relevante é grafo/índice e nenhuma leitura direta o antecede.
- Saída distingue `not-observed`, `pass`, `fail` e `invalid-trace`; nunca transforma ausência de
  telemetria em sucesso.
- Exit codes: `0` conforme, `1` política não cumprida, `2` entrada/schema inválido.

## Artefatos propostos

- `orq/scripts/audit-removal.py` e testes com a fixture autoral do T-045.
- `orq/scripts/audit-adoption.py` e traces graph-first/direct-first/sem-grafo/inválido.
- `orq/commands/auditar.md` como interface Claude; roteamento equivalente na skill para Codex.
- Schema versionado `orq/schemas/audit-ledger-v1.json`.
- Ledgers gerados somente quando solicitado, em `memory/audits/`; a thread guarda o resumo e link.

## Regras que evitam regressão entre hosts

- Nenhuma alteração em `context-guard.py` ou `hooks.json` na fase 1.
- Nenhum `decision: block`; auditores são comandos explícitos e read-only, salvo o ledger pedido.
- Claude e Codex usam o mesmo core; adapters de captura ao vivo, se existirem, serão módulos separados.
- Zero rede, zero LLM externo, zero PII/credencial e nenhuma dependência Python adicional.
- Falha de ferramenta gera recibo incompleto e exit não-verde; nunca falso “auditoria passou”.

## Critérios de aceitação

1. Fixture do T-045: 13/13 âncoras, histórico em `retained`, zero autocontaminação do ledger.
2. Mutação controlada: remoção incompleta falha; remoção completa com recibos passa.
3. Traces: graph-first passa; direct-first falha; sem grafo retorna `not-observed`; JSON inválido sai 2.
4. Testes Linux/macOS e paths com espaço/Unicode; nenhum shell injection pelo alvo.
5. Diff de `hooks.json` e `context-guard.py` obrigatoriamente vazio.
6. Documentação deixa explícito que o audit não substitui review humano nem o stack de descoberta.

## Fora da fase 1

- Captura automática de eventos em sessões vivas.
- Bloqueio por hook, enforcement durante prompts ou alteração do guardião de contexto.
- Instalação/integração do Cartographer e teste em repositório de produção.

## Fechamento — 2026-08-29/30 (registro, não pendência)

T-048 concluída. A 0.22.5 entrou em `origin/main` no commit `0cefa97`. Smokes read-only em processos
novos carregaram a skill e retomaram o estado. O achado não bloqueante sobre `.in_use`/`.codex-plugin`
virou T-049; não foi corrigido fora do card.

Checkpoint de recuperação em 2026-08-30: `origin/main` e o worktree estavam em `986a45d`, com Codex e
Claude habilitados em 0.22.5. O cache Codex 0.22.4 já não estava no disco; reabrir somente eventual
sessão antiga que ainda referencie esse caminho. ⚠️ **Topologia de hosts vencida:** aquele ciclo
também espelhou a release num terceiro host, que **saiu do produto na `0.24.0`** (`T-051`) — a
paridade descrita aqui é histórica e não deve ser reproduzida.

## ⏭️ RETOMAR AQUI

**Nada pendente nesta thread — ela está encerrada.** O `T-048` está `[x]` no board, e o `T-049`, que
era o ponteiro seguinte deste arquivo, **também já foi concluído e publicado** (`0.22.7`). Se você
chegou aqui procurando trabalho, o board é a fonte: `memory/wiki/KANBAN.md`. Não reabra o `T-049` e
não trate a paridade de três hosts descrita acima como estado corrente.
