# T-089 — reúso `card+papel` do Companion e o runtime que o suporta

Frente: `@frente-companion-runtime` · host: `@claude` · trilha `sistema` · faixa `normal`.
Origem do card: `docs/plano_coexistencia_hosts.md` (auditoria de 2026-09-08).

## Por que existe

Desde a 0.27.2 o produto manda continuar o mesmo `card+papel` com `--resume-thread <threadId>`
(`SKILL.md`, `plan-next.md`, `revisar.md`, `elenco.md`, `_elenco.md`). O Companion registrado no
Claude não conhece essa flag, e a falha é silenciosa: a continuação nasce como thread nova.

## Evidência — 2026-09-28, janela Claude (leitura + uma sonda autorizada)

- **CLI Codex desta sessão:** `~/.local/bin/codex` → `~/.local/lib/node_modules/@openai/codex`,
  `package.json` 0.158.0 (lido, sem executar o binário). Segunda instalação em
  `/usr/local/bin/codex` 0.156.1, atrás no PATH.
- **Companion registrado:** `installed_plugins.json`, escopo `user` → `codex@openai-codex` 1.0.5,
  `gitCommitSha 80c31f99570876c3ef40327838b0a2ca1ae2cd9c`, `installPath
  ~/.claude/plugins/cache/openai-codex/codex/1.0.5`, `installedAt 2026-04-03T18:51:19.359Z`,
  `lastUpdated 2026-06-26T17:31:28.729Z`. Entrada registrada aqui para rollback.
- **Escopo de projeto (não tocar):** `New ByIA Project` → 1.0.5; `prompts-byia-clientes` → 1.0.2;
  dois worktrees em `/private/tmp` → 1.0.5. Enquanto existirem, o cache 1.0.5 segue referenciado.
- **Marketplace local** `openai-codex` (`openai/codex-plugin-cc`, `lastUpdated 2026-07-18`) oferece
  1.0.6. Cache `codex/1.0.6` existe, marcado `.orphaned_at` em 2026-09-27 22:02 (local), sem
  entrada no registro. Um broker de outra frente (`Bruno Vascular - Blog`) roda scripts 1.0.6.
- **1.0.5, código:** `task` aceita `--resume-last|--resume|--fresh`; effort `none…xhigh`
  (`max` → erro explícito `Unsupported reasoning effort`). `--resume-thread` não é opção: o
  `args.mjs` empurra a flag e o valor para os posicionais, que viram texto do prompt — thread nova,
  sem erro.
- **1.0.6, código:** `--resume-thread <thread-id>` como opção de valor; exclusividade entre
  `--resume-thread`, `--resume/--resume-last` e `--fresh`; effort até `max|ultra`; o agente
  `codex-rescue` repassa `--resume-thread` e preserva `--json`.
- **Grafias:** o parser aceita traço simples em qualquer opção. `-resume` ≡ `--resume` ≡
  `--resume-last` (última thread do repositório — o que o produto proíbe). `-write` ≡ `--write`.
  No CLI do Codex, fora do Companion, retomar é o subcomando `codex resume <id>` (o Companion
  imprime essa forma); a sintaxe do CLI não foi executada.
- **`--wait`** não é opção do `task` em nenhuma das duas versões (`T-090`); o `codex-rescue` o
  descarta antes da chamada, mas chamada direta o transforma em texto do prompt.
- **Elenco:** `## Times por host` (normativo) usa `gpt-6-astra@xhigh` para planner·sistema e
  reviewer; a linha da via `codex` (`_elenco.md:67`) ainda diz `@ max` — contradição interna.
- **Sonda (uma, read-only, sem retry):** Companion 1.0.5 `task --model gpt-6-astra --json`, cwd
  fora do repo. `jobId task-mum00ssm-bf2unm`, `threadId 01a0eac8-0be2-7db1-9a1f-08f73c61ea1e`,
  `turnId 01a0eac8-0ead-7911-866c-c3276dad8bbf`, exit 0, `pwd` correto, `cli_version 0.158.0`,
  `turn_context` gpt-6-astra/xhigh/read-only. Prova só o caminho `--fresh`; não prova continuação
  nem identidade do modelo no servidor.

## Hipótese de causa raiz (Manager, antes do planner)

Duas camadas. **Ambiente:** a instalação ativa do Companion no Claude é anterior à capacidade que o
produto usa. **Produto:** as instruções presumem a capacidade sem conferir o resultado, e o 1.0.5
falha em silêncio. Corrigir só o ambiente deixa o produto quebrando em silêncio onde houver 1.0.5
em escopo de projeto; corrigir só o produto deixa o reúso indisponível aqui.

## Vínculo Companion deste card

| card | papel | jobId | threadId | status |
|---|---|---|---|---|
| T-089 | planner | `task-mum17vqn-x6dfia` | `01a0eae6-b7ed-72d2-9e6b-afee5f5485bb` | `completed` (status 0) |

O `jobId` não vem no JSON do `task` em foreground (payload: `status`, `threadId`, `rawOutput`,
`touchedFiles`, `reasoningSummary`); foi lido do estado do Companion
(`$CLAUDE_PLUGIN_DATA/state/byia-claude-orquestra-47062bb90b7c38af`), com `write: false` e
`touchedFiles: []`. Cabe no `T-087` ou numa nota do contrato: o recibo JSON sozinho não fecha o
vínculo.

## Plano

Completo em `docs/plano_T-089-companion-resume.md`, com a auditoria do Manager (três ajustes:
sem pré-checagem de capacidade, checar versão do upstream antes do update, ambiente antes do
produto). Continuação do planner impossível no 1.0.5 — ajustes declarados como do Manager.

## ~~RETOMAR AQUI — 2026-09-28~~ (superado pelo de 2026-09-29, abaixo)

Gate de 2026-09-28: quatro perguntas ao dono (plano de produto, etapa de ambiente, ordem, CLI
duplicada). Respondidas em 2026-09-29 — ver a seção seguinte.

## Execução — 2026-09-29, janela Claude (PID 6267)

**Gate respondido pelo dono** (prompt colado nesta sessão, redigido na janela Codex): (1) plano de
produto aprovado, com `T-090` e `_elenco.md:67`; (2) ambiente autorizado — backup, antes/depois,
update reversível só do Companion `user` para 1.0.6, parar se a versão divergir ou se ameaçar
trabalho/cache em uso; (3) ordem ambiente → prova → produto; (4) CLI duplicada, `T-131` e troca de
modelos fora. Sem bump, commit, push ou publicação sem novo gate. A sonda `pwd` de 2026-09-28 não
conta como prova de `--resume-thread`.

### Ambiente — feito e verificado

- **Antes:** `user` → 1.0.5 `80c31f9`. Upstream `openai/codex-plugin-cc` `main` = `db52e28` = HEAD
  do catálogo local → 1.0.6 (ajuste 2 do Manager satisfeito). Cache 1.0.6 byte-idêntico ao catálogo.
- **Em uso:** seis sessões Claude com `.in_use` no 1.0.5, inclusive esta; broker órfão 57955
  (worktree do `Bruno Vascular - Blog`, pai = 1) rodando scripts 1.0.6 há um dia — só imports
  estáticos, não tocado; nenhum job não terminal em workspace algum. O broker é idêntico nas duas
  versões (diff vazio): a procedência do broker não afeta a retomada.
- **Backup:** `~/Backups/orquestra/T-089-companion-20260929T160728/` — `installed_plugins.json`,
  `known_marketplaces.json`, caches 1.0.2/1.0.5/1.0.6, catálogo e manifestos SHA-256
  antes/backup/depois (backup conferido por hash).
- **Update:** `claude plugin update codex@openai-codex --scope user --json` (CLI 2.1.280) →
  `updated`, 1.0.5 → 1.0.6, exit 0.
- **Depois:** só a entrada `user` mudou (1.0.6, `db52e28`, `installPath …/codex/1.0.6`,
  `installedAt` preservado); os quatro registros de projeto e os outros sete plugins idênticos;
  caches 1.0.2/1.0.5 idênticos; 1.0.6 idêntico salvo a remoção do `.orphaned_at`; HEAD do catálogo
  igual, só `lastUpdated` renovado; broker 57955 vivo.
- **Não investigado:** após o update, as sessões vivas mais antigas (não esta) passaram a ter
  marcador `.in_use` também no 1.0.6. Não prova que recarregaram o agente.
- **Rollback:** restaurar só a entrada `user` a partir de `antes-registros.json` do backup, sem
  reescrever o registro inteiro; caches preservados.
- **Achado de contrato (1.0.6):** o `codex-rescue` acrescenta `--write` por padrão se o pedido não
  disser explicitamente "somente leitura". A frase-âncora do produto já proíbe `--write`; o briefing
  precisa dizer "somente leitura" com todas as letras. O JSON foreground do `task` 1.0.6 traz
  `status`, `jobId`, `threadId`, `rawOutput`, `touchedFiles`, `reasoningSummary`; o `SessionEnd`
  tira os jobs da sessão da lista do estado, mas o arquivo do job permanece.

### Prova comportamental — NÃO executada

Esta sessão não consegue reiniciar a si mesma e segue com o 1.0.5 carregado. Tentei um processo
Claude novo (`claude -p` headless, workspace sintético no scratchpad) como sessão reiniciada. O
`init` dele listou `codex` em `…/codex/1.0.6` — **sessão nova carrega o 1.0.6** —, mas as duas
execuções pararam em `Not logged in` antes de qualquer inferência: a primeira por herdar
variáveis de autenticação do app desktop, a segunda, com ambiente limpo, porque o CLI de terminal
está deslogado (`claude auth status` → `loggedIn: false`). Nenhuma chamada `Agent`, nenhum `task`,
nenhum job ou broker criado, custo 0: o orçamento "uma fresca + uma retomada, sem retry" segue
intacto. **Reúso não declarado funcional.**

### Prova comportamental — EXECUTADA 2026-09-29 (Companion 1.0.6, sessão reiniciada)

Sessão Claude PID 59661: `.in_use/59661` presente em `…/codex/1.0.6`, ausente no 1.0.5. Rota real
`Agent → codex:codex-rescue → task`, foreground, "somente leitura", sem `--write`, sem retry,
`--model gpt-6-astra --effort xhigh`, marcador sintético `ZEBRA-4417-LIRIO`.

| Chamada | Flags | jobId | threadId | status | rawOutput |
|---|---|---|---|---|---|
| 1 | `--fresh --json` | `task-muna4bnu-2yaad5` | `01a0ef65-7cec-7252-be60-92d6ef9846bb` (A) | 0 | `MARCADOR REGISTRADO.` |
| 2 | `--resume-thread A --json` | `task-muna4rpv-t93o74` | `01a0ef65-7cec-7252-be60-92d6ef9846bb` (**= A**) | 0 | `ZEBRA-4417-LIRIO` |

Conferido também no arquivo de job do runtime (`…/state/byia-claude-orquestra-…/jobs/*.json`):
`status: completed`, `threadId` igual nos dois, `write: false`. **Reúso `card+papel` funcional no
1.0.6.** Vínculo **sintético**: fora da tabela de vínculos reais. Não prova o sandbox efetivo além de
`write: false` no job.

### Correção local do produto — implementada 2026-09-29, NÃO commitada

Implementer·normal (sonnet), worktree `.claude/worktrees/agent-a054e5c8dd838fcb5`, branch
`claude/t089-companion-identidade` (renomeada; base main 4e58e7f, sem commit; docs em arquitetura.md incluída, 453 OK), seção 3 do plano + `--wait` do T-090 (só envelope/runtime).
Seis arquivos: `SKILL.md` (contrato canônico), `plan-next.md`, `revisar.md`, `elenco.md`,
`memory/wiki/_elenco.md`, `test_companion_thread_reuse.py` (+6 testes). `test_write_flag_guard.py`
intacto; frase-âncora `--write` literal nas cinco superfícies; nenhuma âncora de versão tocada.

- **Rodada 1:** RED 5 falhas → GREEN; 8 mutações reprovaram a guarda certa.
- **Revisão cross-vendor** (reviewer `gpt-6-astra@xhigh`, fresco, read-only; `jobId
  task-munacjyj-g1lt7l`, `threadId 01a0ef6b-583b-7742-92b9-f37f25500825`, status 0): **NO-GO, 3 P2**,
  todos auditados pelo Manager contra o código e procedentes — (1) regra curta incompleta nos dois
  elencos; (2) guarda de identidade sem cobrir os elencos; (3) guarda de `--wait` sem cobrir
  chamadas finais de `task`.
- **Rodada 2** (última pelo teto do `revisar.md`): os três corrigidos, RED 3 falhas → GREEN, 5
  mutações reprovaram. **Verificado pelo Manager no worktree:** suíte `discover` 453 OK, `plugin
  validate --strict` exit 0, lint exit 0, `git diff --check` limpo.
- **Não há terceira revisão.** A rodada 2 não foi re-revisada pelo revisor (teto de 2): a confiança
  nela vem da verificação do Manager e das mutações, não de novo parecer.
- **Fora de escopo, registrado:** preset do host Codex com `gpt-6-astra@max` (`elenco.md` ~l.332);
  o `jobId` só sai do estado do Companion, não do JSON do `task` (nota do `T-087`).
- **Ainda não feito (gate do dono):** docs/página de tópico; próxima versão livre nas quatro âncoras
  (`0.27.11` é de outra frente); commit; release/instalação; teste comportamental pós-release.
  `T-090` fica absorvido por este card — marcar no board só quando o dono validar.

## ⏭️ RETOMAR AQUI — 2026-09-29 (passos 1–3 cumpridos, faltam os gates abaixo; ver prova e correção acima)

**Próximo:** o dono decide (a) aprovar/ajustar o diff no worktree, (b) versão e commit local, (c)
release. Nada disso foi feito.

*Histórico do RETOMAR anterior:*

Card em `[!]`: falta o dono reiniciar a sessão Claude deste card. Na sessão nova, nesta ordem:

1. Confirmar o carregado: `.in_use/<pid-da-sessão>` presente em `…/codex/1.0.6` e ausente no 1.0.5.
2. Prova pela ferramenta Agent → `codex:codex-rescue`, uma chamada cada, sem retry, foreground,
   com "somente leitura, NÃO adicione `--write`" explícito, marcador sintético novo:
   - 1: `--fresh --json --model gpt-6-astra --effort xhigh`, memorizar o marcador → exigir
     `status: 0`, `jobId` e `threadId=A`;
   - 2: `--resume-thread A --json --model gpt-6-astra --effort xhigh`, pedir o marcador sem
     reenviá-lo → exigir `status: 0`, `jobId` novo, **`threadId == A`**, marcador correto.
   IDs lidos do JSON do runtime; registrar aqui como vínculo **sintético**, fora da tabela de
   vínculos reais. Falhou → registrar, não declarar reúso, sem fallback nem nova tentativa.
3. Com a prova: produto em worktree isolado (implementer·normal), seção 3 do plano + `T-090`.
   Sem bump, commit, push ou publicação sem novo gate.

## ⏭️ RETOMAR AQUI — 2026-10-02: regularização documental autorizada

O dono autorizou nesta conversa a regularização somente desta thread no checkout
`claude/t089-companion-identidade`, seguida de conciliação read-only com T-131 e
com o desenho T-143. A posse `@frente-companion-runtime @claude` permanece:
esta operação documental do Manager Codex não transfere o card.

O histórico acima foi preservado da thread existente na main, SHA-256
`a078db11d01719684f10433fee6683ab738a2be90087126b69ea6f1ae215c901`,
pois o resolvedor devolve este worktree como THREAD_ROOT, mas o arquivo faltava.
Nenhuma thread, board ou arquivo da main foi alterado.

Estado reconferido: HEAD `2a879d94df86c998b401c84361603705ea1d06b6`,
base `4e58e7f`. O commit local existe e contém sete arquivos: as referências
históricas acima a produto não commitado e commit pendente estão superadas.
Não há autorização nesta etapa para integrar, publicar ou instalar esse commit.

Escopo de retomada: indicar trechos e testes que devem sobreviver à futura
conciliação. Não alterar elenco ou produto; não repetir provas Companion,
testes ou revisões; não executar chamadas externas, bump, commit, push, merge,
publicação, instalação ou restart. O desenho T-143 continua sem aprovação de
implementação; as correções locais pós-R4 do T-131 estão aprovadas, mas ainda
não aplicadas. Suíte histórica verde não aprova o snapshot reconciliado.

## Conciliação read-only — mapa verificado em 2026-10-02

Comparação do commit T-089 `2a879d9` com a candidata não commitada T-131,
ambos sobre a base `4e58e7f`, e com o desenho T-143. Nenhum merge ou patch
de produto aplicado. Os números abaixo pertencem a estes snapshots.

### Trechos que devem sobreviver

| Superfície | T-089 a preservar | Conciliação futura |
|---|---|---|
| `orq/skills/orq/SKILL.md:249–273` | Isolamento card+papel; recibo válido, sucesso, IDs presentes e igualdade exata; preservação do vínculo e ausência de retry/fallback | Manter também o gate de modelos T-131 na linha 168 da candidata. T-143 deve ter seção própria de autoridade/continuidade, sem diluir o contrato Companion. |
| `orq/commands/revisar.md:72–95` | `--wait` só no envelope; foreground sem `--background`; identidade antes de aceitar parecer | Conservar a seção Anthropic T-131, linhas 91–136 da candidata: modelo resolvido do elenco, identidade exata 5.5, aliases/default legados e sem retry. T-143 pode separar correção local autorizada de revisão externa, nunca aprovar parecer ausente. |
| `orq/commands/elenco.md:177–181,360,388–394` | Condição de identidade na capacidade, na via, na matriz e na regra curta | Combinar com os gates T-131 (`:110–138`) e a célula Anthropic (`:434` da candidata); não substituir por arquivo inteiro. A separação candidato/ativo e a ambiguidade de defaults ainda aguardam as correções pós-R4 aprovadas. |
| `orq/commands/plan-next.md:52–74` | Envelope/argumentos do runtime distintos; Planner não herda Reviewer; recibo e identidade | T-131 não altera este arquivo hoje. T-143 deve registrar aprovação local sem converter planejamento em autorização de chamada, escrita ou release. |
| `memory/wiki/_elenco.md:67,125–131` | Modelo/effort delegados ao time do host; igualdade do ID e regra curta | Não copiar o arquivo inteiro do T-089 sobre o elenco vivo. Futuramente conciliar apenas estes trechos de protocolo, preservando tabelas, presets, overrides e estado das vias. Não foi alterado nesta etapa. |
| `memory/wiki/arquitetura.md:118–128` | Documentação do vínculo e da remoção de `--wait` antes de `task` | Acrescentar depois a regra T-143 em seção distinta. As referências antigas a Fable em outras passagens não devem substituir a política de modelos da frente T-131. |
| `orq/scripts/test_companion_thread_reuse.py` | Seis testes novos, três anteriores e helpers de recorte | Transportar integralmente os mecanismos; mudanças de heading exigem ajustar recortes sem ampliar a busca para o arquivo inteiro. |

Os três arquivos compartilhados por T-089/T-131 são skill, revisar e elenco.
Seus intervalos editados na base não se intersectam neste snapshot. Isso é
evidência textual de separação, não prova de merge limpo nem de runtime.
T-143 ainda não possui implementação/diff de produto a conciliar.

### Testes inspecionados, não executados

Seis novos testes T-089 que devem sobreviver, em
`orq/scripts/test_companion_thread_reuse.py`:

- `:130` `test_continuacao_exige_identidade_do_thread_id`
- `:142` `test_tabela_de_vias_condiciona_o_reuso_a_identidade`
- `:150` `test_recibo_exige_sucesso_e_ids_presentes`
- `:160` `test_divergencia_preserva_vinculo_e_proibe_retry`
- `:176` `test_wait_e_controle_do_envelope_nao_do_task`
- `:210` `test_via_codex_delega_modelo_ao_time_do_host`

O último contém o literal `gpt-6-astra@xhigh`. Uma troca futura de modelo,
aprovada pela frente dona, exige conciliar esse literal; não remover a
delegação a Times por host nem a guarda que recusa `@max` nesta via.
Hoje os times não foram alterados. Os três testes anteriores sobre vínculo,
consumidores e matriz também devem permanecer.

`test_write_flag_guard.py` permanece intacto: conservar a frase-âncora nas
cinco superfícies, a rejeição de `--write`/`-write` fora dela e a distinção
entre o sandbox nativo `workspace-write` e a via Companion read-only.

No T-131, preservar os mecanismos de `T131ContratoTest` em
`test_elenco_perfis.py:266–377`: snapshot por host/papel, mutações de todos
os papéis, atualização deliberada do snapshot, ausência de ativação por
candidato, composição de fábrica e gate delimitado. O plano pós-R4 exige
fortalecer a separação template copiável/ativo e a cobertura da etapa 2b de
init; não declarar a cobertura atual suficiente por haver testes escritos.
Preservar também em `test_run_opus_reviewer.py` os testes de default legado
(`:190`), identidade exata 5.5 (`:196`) e prefixos dos aliases (`:212`).

No T-143 não há testes novos implementados. Seus critérios propostos exigem
guardar: aprovação humana/escopo local, orçamento externo independente,
proibição de retry ou revisão por omissão, respeito à frente dona e retomada
sem relançar execução. Descrever estes casos não equivale a executá-los.

### Limites, posse e próxima ação

- T-089: R1 independente foi NO-GO; correções da R2 têm verificação histórica
  do Manager, mas não novo parecer independente. Não declarar GO do snapshot
  final por transportar testes ou por ter commit local.
- T-131: R4 auditada permanece NO-GO, com dois bloqueadores; correções locais
  já aprovadas, ainda não aplicadas. Não renovar a R4 nem enviar R5 aqui.
- T-143: desenho ainda aguardando aprovação de implementação. A autorização
  para regularizar esta thread não aprova política, novo runner ou release.
- T-090: absorção técnica documentada; fechamento do board depende da
  validação do dono. Nenhum card foi movido nesta etapa.
- Próxima conciliação executável: usar as fontes finais das frentes donas,
  portar somente os trechos acima e manter as guardas. Verificações/revisão
  do novo snapshot, versão, Git e release dependem dos gates próprios.

Checkpoint de recuperação: análise read-only concluída. Única escrita nesta
etapa: esta thread documental, autorizada pelo dono. Main, candidata T-131,
elenco e fontes/testes do T-089 preservados; nenhum teste, prova Companion,
parecer, chamada externa, bump, commit, push, instalação ou restart repetido.
