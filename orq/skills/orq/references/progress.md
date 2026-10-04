# Medidor de progresso

Contrato único de operação do medidor. O Manager o lê ao iniciar um goal (Loop B ou objetivo
avulso autorizado) e ao retomar trabalho em curso.

## O que o medidor é — e o que não é

- Mostra **onde a execução está**: a **fase** vem do board; o **percentual** vem dos passos
  aprovados do plano, que o Manager marca como concluídos depois de conferir a evidência.
- **Não decide nada.** Não move card, não aprova gate, não substitui o board, não substitui a lista
  de tarefas nativa do host nem a statusline nativa do Codex. Quem decide continua sendo o ciclo do
  Orquestra e o dono.
- O percentual é sempre **"do plano"**. **100% do plano não é DONE:** com o card em `[?]` a vista
  mostra "validação do dono" mesmo com 100%, e só o dono fecha o card. Também não é probabilidade
  de sucesso nem prova de que algo funciona.
- Não há estimativa de tempo (ETA), de propósito.

## Antes de qualquer chamada

1. **Comprove `ORQ_PACKAGE_ROOT`** como a skill `orq` manda ("Prova da raiz do pacote"). O script é
   `${ORQ_PACKAGE_ROOT}/scripts/progress.py`, chamado por `python3`. Fora do Claude o shell não
   conhece `${ORQ_PACKAGE_ROOT}`: escreva o caminho absoluto comprovado em **cada** chamada, porque
   variável definida numa chamada de shell não existe na seguinte.
2. **`--root` é o `front_root` do resolver** (o mesmo JSON de `--resolver`): a raiz da frente dona
   deste Manager. Nunca o worktree temporário do implementer, nunca o checkout principal quando a
   frente é outra. O ledger mora em `<front_root>/.orq/progress/v1/`, diretório que o Git ignora.
3. **`--session-key`** são 64 hexadecimais minúsculos, **constantes durante a execução**. O `begin`
   gera uma e a devolve se você omitir `--session-key`; guarde o valor devolvido e grave-o na thread
   do card. Toda mutação exige essa chave, e só o dono do ledger muda o ledger.
4. **Endereço do ledger** (uma das três formas, em qualquer subcomando):
   `--root ABS --card T-NNN` (card) · `--root ABS --run UUID` (goal avulso) · `--ledger ABS`
   (caminho completo; o `begin` o devolve em `ledger_path`, já canônico). Em **mutação** (o `claim`
   inclusive) o caminho é canonicalizado com symlinks resolvidos e tem de ser
   `<front_root>/.orq/progress/v1/<cards|goals>/<arquivo>.json`; fora disso é exit 4 com `code`
   `destino-fora-do-layout`, porque o lock só existe nesse layout. `show` e `watch` leem qualquer caminho.

Os exemplos usam `ORQ` para abreviar `python3 "${ORQ_PACKAGE_ROOT}/scripts/progress.py"` já com o
caminho substituído, e `ENDERECO` e `CHAVE` para o endereço do ledger e a `--session-key`.

## Quando o Manager registra

| Marco | Comando |
|---|---|
| Plano aprovado, antes de despachar o primeiro worker | `begin`, depois `plan` |
| Ao despachar um worker, nos passos que cabem a ele | `start` |
| Depois de **conferir** o resultado e a evidência do passo | `done` |
| Passo novo, descartado ou reaberto — **depois** que o ciclo normal autorizou a mudança | `add`, `drop`, `reopen` |
| Entrada em implementação, revisão ou documentação | `phase` |
| Card vai para `[?]` | `phase --value validate` e `pause` |
| Dono reprova na validação e o card volta a `[~]` | `resume` |
| Card fechou em `[x]`, ou o trabalho foi cancelado | `close` |
| Checkpoint | grave caminho, revisão e `session_key` na thread (ver `/orq:checkpoint`) |

**Workers nunca escrevem o ledger.** Eles devolvem resultado e a referência da evidência por ID de
passo; o Manager confere e marca. Mudança de escopo não nasce no medidor: `add`, `drop` e `reopen`
só registram o que o ciclo normal já decidiu, e mudança material do plano volta ao gate do dono.

### Comandos

```bash
# Abrir (card): --root é o front_root; --front é o slug da frente; --host é claude, codex ou other
ORQ begin --kind card --root ABS --board ABS --thread-root ABS --card T-NNN --front SLUG --host HOST [--session-key CHAVE]
# Abrir (goal avulso): um UUID novo por execução
ORQ begin --kind goal --root ABS --host HOST [--session-key CHAVE]

# Registrar a semente do plano aprovado (JSON pela entrada padrão); `add` recebe reason e evidence_ref
ORQ plan ENDERECO --session-key CHAVE --input -
ORQ add ENDERECO --session-key CHAVE --input -

ORQ start ENDERECO --session-key CHAVE --task P01 --executor-host codex --executor-role implementer --executor-label normal
ORQ done ENDERECO --session-key CHAVE --task P01 --evidence-ref REF
ORQ drop ENDERECO --session-key CHAVE --task P02 --reason obsolete|duplicate|scope_change --evidence-ref REF
ORQ reopen ENDERECO --session-key CHAVE --task P01 --evidence-ref REF
ORQ phase ENDERECO --session-key CHAVE --value implementation
ORQ pause ENDERECO --session-key CHAVE
ORQ resume ENDERECO --session-key CHAVE
ORQ close ENDERECO --session-key CHAVE --outcome reported_complete|cancelled --evidence-ref REF

# Ler (somente leitura): text, json ou segment (uma linha)
ORQ show ENDERECO --format text
ORQ show --root ABS --all --format text
```

`--expect-revision N` é **opcional** em toda mutação. Ausente, a mutação vale sobre o estado atual,
sob lock, com troca atômica e verificação de dono. Presente e divergente do estado atual, termina em
exit 3 sem gravar.

Entrada de `plan`: `{"source_ref": REF, "approval_ref": REF, "tasks": [{"id": "P01", "title":
"…", "size": "S|M|L", "acceptance_ref": "A01"}]}`. Em card os dois `ref` são obrigatórios e o board
tem de marcar `[~]`; em goal podem ser `null`. Entrada de `add`: `{"reason": "scope_change",
"evidence_ref": REF, "tasks": [...]}`. Os campos são fechados: qualquer outro é rejeitado.

### Regras do plano e das transições

- Os passos vêm da **tabela do plano aprovado** (`ID | Entrega verificável | Tamanho | Critério de
  aceite`). Plano antigo sem tabela: o Manager atribui ID, tamanho e critério mantendo
  correspondência com os passos já aprovados; não troque o conteúdo do plano em silêncio.
- Pesos: `S` = 1, `M` = 2, `L` = 3 — peso relativo, não minutos. Até 200 passos.
- `start` registra o executor: `--executor-host` é o host do worker (`claude`, `codex` ou `other`),
  `--executor-role` o papel (`implementer`, `reviewer`, `docs`) e `--executor-label` um rótulo
  genérico (a faixa, por exemplo `normal`) — identificadores, nunca nome de pessoa.
- `phase --value` aceita, em card, `planning`, `gate`, `ready`, `implementation`, `review`, `docs`,
  `validate` ou `done`; em goal, `planning`, `execution` ou `verification`. O `begin` começa o card
  em `ready` e o goal em `planning`. A atividade só diz **qual** etapa de `[~]` está em curso: a
  fase exibida obedece ao board, e `phase` nunca move card. Com `[~]` e atividade `ready`, um passo
  ativo ou concluído já aparece como "implementação"; `review` e `docs` declarados valem como estão.
- `start`: pendente → ativo. `done`: ativo → concluído, **com evidência**. `drop`: pendente ou ativo →
  descartado, com motivo e referência. `reopen`: concluído → pendente. Descartado nunca é
  reutilizado: passo novo, ID novo. Nada é apagado.
- `plan` só inicializa: repetir a mesma semente não muda nada; outra semente é erro. Repetir uma
  operação já aplicada devolve `changed: false`.
- Acrescentar passo aumenta o denominador e o percentual pode cair; reabrir também.
- `close --outcome reported_complete` num card exige `[x]` no board (senão exit 2); `cancelled` não
  exige. Encerrado é terminal: nenhuma outra operação é aceita depois.
- `pause` congela as alterações de passo; só `resume`, `close` e `claim` passam enquanto pausado.
- **Evidência é referência**, não conteúdo: identificador ou caminho local, sem espaço (por exemplo
  `threads/T-144.md#validado` ou `suite:test_progress`). O medidor **não verifica** que o teste
  passou — quem verifica é o Manager, antes do `done`.
- **Não grave** prompt, condição integral do goal, notas livres, comandos, saída de ferramenta nem
  diff: o ledger recusa esses campos. Os títulos são genéricos (até 160 caracteres, uma linha, sem
  controles de terminal) e não carregam dado sensível.

## Goal avulso

Um pedido autorizado pelo dono que não é card (um objetivo explícito, inclusive um `/goal` do host)
usa o mesmo núcleo, sem board:

1. `begin --kind goal` e guarde `run_id` e `session_key` no resumo da sessão.
2. `plan` com a lista de passos que você derivou do objetivo autorizado.
3. Atividades do goal: `planning`, `execution`, `verification`.
4. Encerramento: `close --outcome reported_complete` registra só que **o Manager encerrou a
   execução** — não é "goal check aprovado" e não altera o modo Goal do host.

Não crie card só para alimentar o medidor. Se o goal pede mudança num projeto Orquestra, o ciclo do
projeto continua valendo: o medidor não concede autorização.

## Retomada

1. Leia `memory/MEMORY.md` e a thread do card: ali estão o caminho do ledger e a `session_key`.
2. `show` no endereço registrado. Ledger legível e `session_key` registrada: continue com ela, sem `claim`.
   `begin` de um card que já tem ledger e a mesma `--session-key` devolve o ledger existente
   (`changed: false`); outra chave é conflito (exit 3); ledger já encerrado (`close`) não é reutilizável (exit 2).
   O escopo é conferido **antes** da chave: se a frente (`--front`), o board ou a thread da chamada
   diferem dos gravados no ledger, o `begin` sai `2` com `code` `escopo-divergente` e não altera nada,
   mesmo com chave diferente. O escopo de um ledger é imutável: `claim` só transfere o dono, e trocar
   `--root` abriria outro ledger para o mesmo card. Compare a chamada com o resolver e com o `scope`
   gravado no arquivo do ledger (`ledger_path`). Chamada diferente do resolver é erro de chamada:
   corrija e repita o `begin`. Resolver diferente do gravado (frente renomeada, board movido) não é
   erro de chamada: pare e informe o dono, que decide; não recrie o ledger em silêncio nem o apague.
3. **Ledger ausente** (frente removida, estado perdido): não reconstrua em silêncio. Diga ao dono
   que o histórico do ledger se perdeu; só abra `begin` + `plan` de novo com o plano aprovado, e
   marque `done` apenas o que a thread comprova com evidência.
4. **Ownership.** O dono do ledger é a `session_key` gravada nele. Chave perdida, ou ledger
   com outro dono: **não tome a escrita por idade, PID ou "a sessão parece parada"**. Só faça `claim`
   (`claim ENDERECO --host HOST --session-key NOVA_CHAVE --expected-owner CHAVE_DO_DONO_ATUAL`,
   com a chave atual lida em `show --format json`, campo `owner.session_key`) quando o dono humano
   disser que a escrita deve passar para esta sessão. As duas chaves têm de ser **diferentes**:
   `--session-key` é a NOVA e `--expected-owner` é a anterior; chaves iguais dão exit 2 e nada transfere. Depois do `claim`, o escritor antigo perde a
   autorização (exit 3).

## Códigos de saída — o que fazer

| Exit | Significa | Ação |
|---|---|---|
| `0` | sucesso, ou repetição idempotente (`changed: false`) | siga |
| `2` | argumento, entrada ou transição inválidos (erro de uso inclusive: `code` `uso-invalido`); gravação que deixaria o ledger acima de 1 MiB (`code` `ledger-grande`) | leia a linha JSON em `stderr` (`code` e `message`), corrija a chamada; não repita igual. Em `ledger-grande` a chamada não é o defeito: nada é gravado, o ledger anterior segue íntegro e o dono é informado |
| `3` | revisão ou dono divergentes | **releia** com `show --format json`; nunca repita cegamente nem sobrescreva; dono divergente = outra sessão tem a escrita: pare e relate |
| `4` | estado indisponível: ledger ausente, corrompido, de versão desconhecida ou, na **leitura**, já acima de 1 MiB (`code` `ledger-grande`); lock ocupado; board indisponível; destino versionado, sem cobertura do Git ou fora da frente | informe a indisponibilidade ao dono com o `code`; lock ocupado admite uma nova tentativa depois de alguns segundos |

Falha do medidor **não bloqueia o trabalho — e também não vira sucesso**: se uma marcação não foi
gravada, diga que o progresso daquele marco não foi registrado.

O `begin` confere nesta ordem. **Antes de escrever qualquer coisa** (diretório, `.gitignore`, ledger
ou lock) ele só lê: (1) se há arquivo versionado em `.orq/progress/` e (2) se `.orq`, `progress`,
`v1`, `cards`, `goals` e `locks` — existam ou não — resolvem para dentro da frente, sem symlink que
escape. Falhou: exit 4 (`destino-versionado` ou `destino-fora-do-root`) e a árvore fica intacta.
Passando, ele cria `.orq/progress/` e, se faltar, o `.gitignore` com `*`; um `.gitignore` já presente
é preservado, nunca alterado. **Antes de criar `v1`, o ledger ou o lock**, faz uma pré-checagem de
cobertura: o Git tem de ignorar o `.gitignore` de `.orq/progress`, o ledger e o lock com os nomes
verdadeiros e um temporário de gravação com o prefixo e o sufixo verdadeiros. Algum não ignorado:
exit 4 `armazenamento-nao-ignorado`; isso só acontece com `.gitignore` preexistente, e então nada foi
gravado. Fora de checkout Git não há conferência de cobertura.

**Gravação (`begin` e toda mutação).** O temporário de gravação é reservado com o nome verdadeiro, e o
Git é consultado sobre esse **nome exato**, antes de o JSON ser escrito nele. Não ignorado, ou o Git
sem resposta: o temporário é removido, nada é gravado, o ledger anterior fica intacto e a saída é exit 4
(`armazenamento-nao-ignorado` ou `git-indisponivel`). Num `begin` essa prova acontece depois que `v1`,
`cards`, `goals`, `locks` e o arquivo de lock já existem: podem sobrar esses diretórios vazios e o lock,
nunca um ledger nem um temporário. Qualquer falha ou interrupção durante a gravação também remove o
temporário.

**Toda mutação** repete a prova antes de gravar: o ledger e o lock canônicos ficam dentro da frente
e o Git ignora os destinos (a pré-checagem acima); senão exit 4, sem gravar. Em checkout com `.git` e
Git indisponível, a mutação também falha com exit 4 (`git-indisponivel`).

## Como ler e apresentar

- `T-144 · revisão · 5/8 passos concluídos · 69% do plano`, com `Em execução`, `Próximos` e, quando o
  plano mudou, `Plano: 7 → 8 passos`. "Concluídos" conta passos, não "o passo 5": passos paralelos
  são normais.
- Sem plano registrado: **sem percentual** (nunca 0% fictício). Todos os passos descartados: "sem
  passos ativos" (nunca 100%). Enquanto restar passo não concluído o percentual não passa de 99%.
- "Fase indisponível" significa board ilegível, ausente ou ambíguo para aquele card: o percentual
  segue visível, com aviso. A atividade declarada no ledger nunca vence o board.
- Apresente um resumo nos marcos e quando o dono pedir; use `show --format text`. Em VALIDATE diga
  a fase correta ("validação do dono"), não "100% concluído".

## Acompanhar em outro terminal (`watch`)

`watch` é um leitor local: redesenha a mesma vista do `show` a cada intervalo, não escreve nada e
encerra com Ctrl-C sem afetar a execução observada. Serve do mesmo jeito no Claude, no Codex e num
terminal do Orca:

```bash
python3 "ABS_DO_PACOTE/scripts/progress.py" watch --root ABS_DO_FRONT_ROOT --card T-NNN [--interval 2]
python3 "ABS_DO_PACOTE/scripts/progress.py" watch --ledger ABS_DO_LEDGER
```

**O Manager não roda `watch` no próprio shell:** o comando não termina e prenderia a sessão. Entregue
ao dono a linha pronta, com os caminhos absolutos já substituídos, para ele colar num terminal ao
lado (no Orca, um terminal dedicado da frente). `--count N` encerra sozinho depois de N leituras,
para quando um script precisar do comando finito. Sem ledger ainda, o quadro mostra
"indisponível" e passa a mostrar o progresso quando o `begin` acontecer.

## Limites

- Vale na mesma máquina e na mesma frente; **não sincroniza entre máquinas**. Remover a frente
  apaga o ledger: o checkpoint registra o resultado na thread antes disso.
- O lock cobre concorrência local; não foi testado em Windows nem em sistema de arquivos remoto.
- Nunca leia o transcript da sessão para descobrir o andamento: o ledger e o board são as fontes.
