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
3. **`--session-key`** das mutações é a **chave de dono**: 64 hexadecimais minúsculos, **constantes
   durante a execução**. O `begin` gera uma e a devolve se você omitir `--session-key`.
   A chave de dono fica somente em `owner.session_key` do ledger local ignorado.
   Na thread pública, registre só caminho, run_id e revisão; nunca a chave de dono.
   O Manager da frente dona a recupera para mutações; não a envia a workers, Git ou modelo externo.
   Toda mutação exige essa chave, e só o dono do ledger muda o
   ledger. Não a confunda com a chave da sessão nativa, que só serve ao `bind` (seção "Duas chaves").
4. **Endereço do ledger** (uma das três formas, em qualquer subcomando):
   `--root ABS --card T-NNN` (card) · `--root ABS --run UUID` (goal avulso) · `--ledger ABS`
   (caminho completo; o `begin` o devolve em `ledger_path`, já canônico). Em **mutação** (o `claim` e
   o `bind` inclusive) o caminho é canonicalizado com symlinks resolvidos e tem de ser
   `<front_root>/.orq/progress/v1/<cards|goals>/<arquivo>.json`; fora disso é exit 4 com `code`
   `destino-fora-do-layout`, porque o lock só existe nesse layout. `show` e `watch` leem qualquer caminho.

Os exemplos usam `ORQ` para abreviar `python3 "${ORQ_PACKAGE_ROOT}/scripts/progress.py"` já com o
caminho substituído, e `ENDERECO` e `CHAVE` para o endereço do ledger e a `--session-key`.

## Quando o Manager registra

| Marco | Comando |
|---|---|
| Plano aprovado, antes de despachar o primeiro worker | `begin`, depois `plan` |
| Depois do `begin` — antes ou depois do `plan`, tanto faz; o Loop B faz depois de registrar o endereço do ledger na thread —, com a chave da sessão nativa que o hook entregou no contexto | `bind --native-key` (ver "Vínculo de sessão") |
| Ao despachar um worker, nos passos que cabem a ele | `start` |
| Depois de **conferir** o resultado e a evidência do passo | `done` |
| Passo novo, descartado ou reaberto — **depois** que o ciclo normal autorizou a mudança | `add`, `drop`, `reopen` |
| Entrada em implementação, revisão ou documentação | `phase` |
| Card vai para `[?]` | `phase --value validate` e `pause` |
| Dono reprova na validação e o card volta a `[~]` | `resume` |
| Card fechou em `[x]`, ou o trabalho foi cancelado | `close` |
| Checkpoint | grave só caminho, run_id e revisão na thread, sem chave de dono (ver `/orq:checkpoint`) |

Em cada marco acima que grava (`start`, `done`, `phase`...), a linha do progresso já vem no recibo:
leia o `view` dele em vez de rodar um `show` extra (ver "Recibo").

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

# Ligar a sessão nativa do host a um ledger; não é mutação do ledger (ver "Vínculo de sessão")
ORQ bind ENDERECO --host claude|codex --session-id ID_NATIVO_DA_SESSAO

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

### Recibo: a vista compacta já vem nele

Todo `begin` e toda mutação bem-sucedida devolve, além de `ok`, `run_id`, `ledger_path`, `revision`,
`session_key` e `changed`, a **vista compacta** do que acabou de gravar:

```json
{"ok":true,"run_id":"…","ledger_path":"…","revision":4,"session_key":"…","changed":true,"view":"◎ T-146 · implementação · 2/9 · 22%","view_revision":4}
```

- `view` é a linha de `show --format segment`, pela **mesma projeção** (fase do board, passos
  concluídos e percentual); `view_revision` é a revisão que foi projetada. A projeção roda depois da
  gravação e fora do lock, sobre o ledger que acabou de ser confirmado.
- **Nos marcos, leia o `view` do recibo da marcação em vez de rodar um `show` extra.** O
  `show --format text` continua valendo quando você precisar de "Em execução", "Próximos" ou do aviso
  de fase, ou quando o dono pedir o detalhe.
- **Falha da vista não é falha da marcação.** Se a projeção quebrar depois da gravação, o recibo
  segue `ok: true`, com o exit `0` da mutação, `view: null`, `view_revision: null` e
  `view_error` (`code` e `message`). A marcação **foi gravada**: não a repita; leia o estado com
  `show` quando precisar. Board ilegível ou ausente não é essa falha: a vista sai com "fase
  indisponível" e o percentual, igual ao `show`.
- Erros (exit `2`, `3`, `4`) continuam só em `stderr` e não trazem vista.
- O recibo sai com os acentos legíveis, com controles de terminal escapados; se o stdout do host não
  codifica acentos, sai o mesmo JSON com `\uXXXX`, e a marcação continua gravada e `ok`.

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

1. `begin --kind goal` e guarde só `run_id`, caminho e revisão no resumo da sessão; a chave fica no ledger ignorado.
2. `plan` com a lista de passos que você derivou do objetivo autorizado.
3. Atividades do goal: `planning`, `execution`, `verification`.
4. Encerramento: `close --outcome reported_complete` registra só que **o Manager encerrou a
   execução** — não é "goal check aprovado" e não altera o modo Goal do host.

Não crie card só para alimentar o medidor. Se o goal pede mudança num projeto Orquestra, o ciclo do
projeto continua valendo: o medidor não concede autorização.

**No Codex, com a ferramenta `get_goal` disponível**, o Manager PODE consultá-la (é só leitura: não
inicia, pausa nem limpa nada) para saber se há um Goal nativo ativo antes do `begin --kind goal`, e
guardar o `run_id` junto dessa constatação no resumo da sessão. Sem a ferramenta, vale o início
explícito descrito acima; não tente adivinhar o Goal pelo prompt nem pelo transcript.
- O ledger não guarda o objetivo nem um ID do Goal nativo: o vínculo é do resumo da sessão, não do
  arquivo. A API do host também não entrega um identificador portátil por Goal.
- **`goal: null` não é perda de ledger.** Diz só que não há Goal nativo agora; o ledger do card ou do
  goal segue onde estava e vale o procedimento de "Retomada". Goal nativo ativo, por sua vez, não
  implica ledger: sem `begin` explícito não há medidor.
- O estado do Goal nativo (ativo, pausado, limpo) pode informar a atividade, mas nunca fecha nada
  sozinho: o ledger só se encerra com `close`, pelo Manager.
- **Nunca feche um card nem um Goal porque o ledger chegou a 100%.** 100% do plano não é DONE: o card
  só fecha com o dono em `[x]`, e o Goal só termina pelo host.

## Duas chaves — não as confunda

| | Chave de **dono** | Chave da **sessão nativa** |
|---|---|---|
| O que é | `--session-key` do `begin` e de toda mutação; 64 hexadecimais; o `begin` a gera | `sha256(host + NUL + session_id)`; 64 hexadecimais; derivada do ID nativo da sessão no host |
| Flag | `--session-key` (begin e mutações) | `--native-key` (só no `bind`) |
| Serve para | **autorizar a escrita** do ledger: só o dono o muda | **só o vínculo** (`bind`), que o hook e a statusline usam para achar o ledger da sessão |
| Onde fica | só em `owner.session_key` do ledger local ignorado, nunca na thread pública | em `sessions/<chave>.json` e no contexto que o hook entrega (`SessionStart`, ou o primeiro `PostToolUse` da sessão que abriu o medidor) |
| Quando muda | nunca durante a execução: sobrevive a `/clear` e à compactação | quando o host abre outra sessão (`/clear` no Claude, `fork`, conversa nova) |

As flags têm nomes diferentes de propósito. `bind --native-key` recebe a chave **nativa**, a que o hook
informou; `--session-key` é sempre a de **dono** e o `bind` a recusa (exit 2). As mutações com a chave
nativa dão exit 3 (`dono-divergente`) e nada é gravado. O Manager não conhece o `session_id` bruto:
quem informa a chave nativa é o hook.

## Vínculo de sessão (`bind`)

O host (Claude, Codex) conhece a sessão por um ID nativo. O `bind` liga essa sessão a um ledger, para
que os adaptadores consultivos (lembrete e statusline) saibam de qual execução ela fala:

```bash
# a chave NATIVA que o hook informou no contexto (o caminho normal do Manager)
ORQ bind ENDERECO --host claude|codex --native-key CHAVE_NATIVA
# alternativa, só quando você tem o ID bruto da sessão (o programa grava só o hash)
ORQ bind ENDERECO --host claude|codex --session-id ID_NATIVO_DA_SESSAO
```

- `--native-key` (a chave nativa, 64 hexadecimais) e `--session-id` são **exclusivos**: exatamente um
  (com os dois ou nenhum, exit 2). `--session-key` não existe no `bind`: é a chave de dono. Com `--session-id` o programa deriva
  `session_key = sha256(host + NUL + session_id)`; **o ID bruto nunca vai para o disco nem para a
  saída**. O vínculo mora em `<front_root>/.orq/progress/v1/sessions/<session_key>.json`, com
  `schema_version`, `session_key`, `host`, `ledger_path` canônico, `run_id` e os contadores do
  lembrete (`calls_without_plan`, `nudged`, `recent_event_ids`, no máximo 128).
- `bind` **não transfere ownership e não muda o ledger**: só liga a sessão a ele. A chave nativa não
  é a de dono das mutações; o `bind` não lê nem altera o dono. Quem escreve continua sendo o dono, e a
  transferência continua sendo o `claim`.
- Pode haver um vínculo por sessão. Mesma sessão e mesmo ledger: idempotente (`changed: false`, os
  contadores ficam). Mesma sessão e outro ledger: o vínculo daquela sessão é **substituído** e os
  contadores voltam a zero. Vínculo corrompido é refeito pelo `bind`; de `schema_version`
  desconhecida não é: exit 4 (`versao-desconhecida`), porque outro host pode estar com um plugin mais
  novo na mesma frente.
- Só `claude` e `codex` têm sessão nativa a ligar; `--host other` é erro de uso (exit 2). O ledger tem
  de existir e ser válido (senão exit 4, `ledger-ausente` ou `ledger-invalido`, sem criar nada).
- As garantias são as da gravação do ledger (veja "Códigos de saída", abaixo): realpath e contenção
  do vínculo, do lock e do diretório `sessions/`, Git ignorando o destino real (o vínculo, o lock e o
  temporário dele) e lock próprio. `sessions/` faz parte do layout: o `bind` o cria se o ledger for
  anterior a ele.
- Recibo: `ok`, `session_key`, `host`, `run_id`, `ledger_path`, `binding_path` e `changed`. Não leva
  `view`, porque o `bind` não toca no ledger.

## Lembrete consultivo (hooks)

O pacote registra dois hooks do medidor (`scripts/progress-hook.py`), no Claude e no Codex, ao lado do
guardião de contexto e sem alterá-lo. São **consultivos**: só acrescentam contexto; não bloqueiam, não
negam e não interrompem o goal. Qualquer falha (payload inválido, lock ocupado, permissão, Git
indisponível, núcleo ausente) sai com exit 0 e sem saída. Não abrem o transcript e não leem
`tool_input`, `tool_response` nem o texto do prompt. O host é reconhecido pelo ambiente nativo
(`PLUGIN_ROOT` é o Codex, `CLAUDE_PLUGIN_ROOT` o Claude); host desconhecido não faz nada.

- **`SessionStart`** (`startup`, `resume`, `clear`, `compact`, `fork`): entrega ao Manager a **chave da
  sessão nativa** e a instrução de vincular. Não cria goal, não faz `bind` sozinho, não interpreta
  prompt, não grava nada e nunca mostra o `session_id` bruto. Só fala quando existe
  `.orq/progress/v1/sessions/` na frente (no `cwd` ou acima).
- **Primeira execução de uma frente.** A sessão que roda o primeiro `begin` já passou do `SessionStart`
  (`sessions/` ainda não existia). Por isso o **primeiro `PostToolUse`** da sessão principal, quando
  `sessions/` existe e não há binding para a chave nativa dela, anuncia a chave **uma vez** (mesmo texto
  do `SessionStart`) e grava o marcador `sessions/.anunciada-<chave>.json`, com as mesmas garantias do
  binding (contenção, Git ignorando o destino real, lock, escrita atômica). Se a gravação falhar, fica em
  silêncio e tenta no evento seguinte. Subagente (`agent_id`) não anuncia; frente sem `.orq/progress` não
  recebe nada; com binding (ou com um arquivo de binding ruim no lugar) não anuncia.
- **Como vincular:** com a chave nativa no contexto e um medidor ativo nesta frente, rode
  `bind ENDERECO --host HOST --native-key CHAVE_NATIVA`. As mutações seguem com a chave de dono
  gravada na thread. Depois de `/clear`, `fork` ou de sessão nova a chave nativa muda: o `bind` com a
  chave nova cria **outro** binding, com os contadores **zerados** (o da chave anterior fica parado, sem
  uso). A idempotência (`changed: false`, contadores preservados) vale só para a **mesma** chave nativa e
  o mesmo ledger. Sem o `bind` com a chave nova, a statusline e o lembrete ficam sem vínculo.
- **`PostToolUse`:** só conta se a sessão está vinculada, o ledger está `active` e **sem plano**
  registrado. **Card:** conta só com o board em `[~]`; a exclusão por planejamento (`[>]`), gate (`[!]`),
  validação (`[?]`), concluído, backlog ou board ilegível vem do **board**, nunca da `activity` declarada
  no ledger. **Goal ativo** conta em **qualquer** `activity`, inclusive `planning` (o `begin` o deixa
  nela), até o plano ser registrado. Pausa e execução encerrada nunca contam, em card ou goal; chamada
  de subagente (`agent_id` presente) é ignorada. No **4º** evento elegível o hook emite UM lembrete
  curto para registrar o `plan` e grava `nudged`; não repete até um novo `bind` a outro ledger. Registrar
  o plano interrompe a condição, e a elegibilidade é conferida de novo no instante da contagem: um `plan`
  que termina entre a consulta e a contagem também impede o lembrete.
- **Contenção do ledger ligado:** o hook e a statusline só leem o `ledger_path` do binding depois de
  resolvê-lo (realpath) e provar que ele é um ledger **desta frente**, no layout
  `.orq/progress/v1/<cards|goals>/<arquivo>.json`. Binding adulterado, ou ledger trocado por symlink
  depois do `bind`, não é aberto: o hook fica em silêncio e a statusline mostra
  `◎ medidor indisponível (destino-fora-do-root)` ou `(destino-fora-do-layout)`.
- **Contagem:** a deduplicação usa hash, nunca o ID bruto: Claude por (sessão, `tool_use_id`, evento),
  Codex por (sessão, `turn_id`, `tool_use_id`, evento), numa janela de 128. Sem identificador no
  payload a contagem é **por entrega de evento**: não afirme "quatro chamadas distintas".
- O lembrete é contexto para o modelo, não uma barra visível nem prova de que falta plano: se o plano
  ainda está em aprovação, ignore o aviso.

## Statusline do Claude

A barra ganha, no fim da segunda linha, o segmento do medidor da sessão (`◎ T-146 · implementação · 2/9 ·
27%`): a mesma linha do `show --format segment`, pela mesma projeção. Quem a calcula é
`progress.py statusline --host claude --input -`, que recebe o JSON da statusline pela entrada padrão e
**só lê**: nunca escreve e sempre sai 0.

- A sessão é identificada pelo `session_id` do JSON: o programa deriva a chave nativa e procura o
  binding nas frentes do `cwd`, de `workspace.current_dir` e de `workspace.project_dir` (os próprios
  diretórios e os ancestrais). **Nunca escolhe "o ledger mais recente"** nem adivinha por horário ou
  título: sem `session_id` ou sem binding desta sessão, o segmento some.
- Binding ou ledger que existem mas não servem (corrompido, ausente, de versão desconhecida, de outra
  execução) aparecem como `◎ medidor indisponível (<código>)`. Nunca um percentual inventado.
- O `statusline.sh` só chama o python quando há `.orq/progress/v1/sessions/` no diretório ou acima, e a
  barra fica idêntica à de antes do medidor sem `jq`, sem `python3` ou sem o `progress.py` ao lado. A
  instalação opt-in copia o trio `statusline.sh` + `kanban-status.sh` + `progress.py` (ver
  `/orq:init`); o hook do medidor não faz parte dessa cópia.
- A barra é do Claude. O Codex mantém a statusline nativa, independente (ver `hosts/codex.md`).

## Retomada

1. Leia `memory/MEMORY.md` e a thread do card: ali estão só caminho, run_id e revisão do ledger.
2. `show` no endereço registrado. Confira frente, board e thread contra o resolver antes de recuperar
   `owner.session_key` do ledger ignorado. Só o Manager da frente dona continua com ela, sem `claim`;
   não publique a chave nem encaminhe o JSON completo. O ownership não é ACL contra outro processo do mesmo usuário.
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
| `0` | sucesso, ou repetição idempotente (`changed: false`); `view_error` no recibo não muda isso | siga |
| `2` | argumento, entrada ou transição inválidos (erro de uso inclusive: `code` `uso-invalido`); gravação que deixaria o ledger acima de 1 MiB (`code` `ledger-grande`) | leia a linha JSON em `stderr` (`code` e `message`), corrija a chamada; não repita igual. Em `ledger-grande` a chamada não é o defeito: nada é gravado, o ledger anterior segue íntegro e o dono é informado |
| `3` | revisão ou dono divergentes | **releia** com `show --format json`; nunca repita cegamente nem sobrescreva; dono divergente = outra sessão tem a escrita: pare e relate |
| `4` | estado indisponível: ledger ausente, corrompido, de versão desconhecida ou, na **leitura**, já acima de 1 MiB (`code` `ledger-grande`); lock ocupado; board indisponível; destino versionado, sem cobertura do Git ou fora da frente | informe a indisponibilidade ao dono com o `code`; lock ocupado admite uma nova tentativa depois de alguns segundos |

Falha do medidor **não bloqueia o trabalho — e também não vira sucesso**: se uma marcação não foi
gravada, diga que o progresso daquele marco não foi registrado.

O `begin` confere nesta ordem. **Antes de escrever qualquer coisa** (diretório, `.gitignore`, ledger
ou lock) ele só lê: (1) se há arquivo versionado em `.orq/progress/` e (2) se `.orq`, `progress`,
`v1`, `cards`, `goals`, `sessions` e `locks` — existam ou não — resolvem para dentro da frente, sem symlink que
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
Git indisponível, a mutação também falha com exit 4 (`git-indisponivel`). O `bind` faz a mesma prova
para o vínculo: se o Git não ignora `sessions/<session_key>.json`, o lock ou o temporário dele, exit 4
(`armazenamento-nao-ignorado`) sem criar `sessions/` nem o arquivo.

## Como ler e apresentar

- `T-144 · revisão · 5/8 passos concluídos · 69% do plano`, com `Em execução`, `Próximos` e, quando o
  plano mudou, `Plano: 7 → 8 passos`. "Concluídos" conta passos, não "o passo 5": passos paralelos
  são normais.
- Sem plano registrado: **sem percentual** (nunca 0% fictício). Todos os passos descartados: "sem
  passos ativos" (nunca 100%). Enquanto restar passo não concluído o percentual não passa de 99%.
- "Fase indisponível" significa board ilegível, ausente ou ambíguo para aquele card: o percentual
  segue visível, com aviso. A atividade declarada no ledger nunca vence o board.
- Apresente um resumo nos marcos e quando o dono pedir. Nos marcos a linha `view` do recibo da
  marcação basta (ver "Recibo"); use `show --format text` para o detalhe. Em VALIDATE diga a fase
  correta ("validação do dono"), não "100% concluído".

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
