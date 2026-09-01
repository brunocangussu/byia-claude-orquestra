# T-043 — Proteção preventiva da janela de contexto no Codex

## Pedido do dono

Investigar se o Orquestra consegue acompanhar a ocupação da janela do Codex e sinalizar um
checkpoint ao ultrapassar 60%, antes que saltos da statusline levem a sessão diretamente para
70–80% ou para a compactação/saturação automática.

## Estado

PLANNING. A validação real no Codex App reprovou a saída pós-checkpoint: o guardião exige
`/clear`, mas esse comando pertence ao CLI e não existe na lista de slash commands do App.

## Perguntas da investigação

1. Qual telemetria de contexto o Codex expõe ao modelo, ao plugin e à statusline?
2. A atualização é contínua ou acontece apenas entre eventos/turnos?
3. Um protocolo textual consegue garantir aviso antes de 70%, ou só oferecer proteção por marcos?
4. Qual combinação de limiar, sinais indiretos e checkpoint reduz melhor o risco sem interromper
   demais o trabalho?

## Evidências confirmadas

- O Orquestra já recomenda checkpoint quando o contexto passa de aproximadamente 50%, mas essa é
  uma instrução textual: o modelo não recebe o percentual exato da statusline.
- A configuração local declara janela de 1.050.000 tokens e compactação automática em 945.000.
  Os eventos desta sessão reportam janela efetiva de 997.500; portanto, a compactação configurada
  só dispara perto de 94,7% da capacidade exibida.
- A statusline calcula `context-used` a partir de `last_token_usage`, não de um contador contínuo.
  Durante uso pendente ela não tem percentual novo; quando chega outro evento de tokens, o valor
  pode saltar.
- O Codex oferece hooks `UserPromptSubmit`, `PostToolUse`, `Stop`, `PreCompact` e `PostCompact`.
  Hooks recebem `session_id` e `transcript_path`; `UserPromptSubmit` e `PostToolUse` podem injetar
  contexto visível ao modelo, e `UserPromptSubmit` pode bloquear um prompt.
- Plugins podem empacotar `hooks/hooks.json` e recebem `PLUGIN_ROOT`/`PLUGIN_DATA`, além das variáveis
  compatíveis `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`.
- O transcript contém eventos `token_count` com `last_token_usage` e `model_context_window`. O
  formato do transcript é explicitamente não estável; qualquer leitor precisa ser tolerante e
  falhar aberto.

## Abordagens

1. **Só instrução:** mudar 50% para 60%. É barata, mas não resolve a causa; o modelo continua sem
   telemetria determinística.
2. **Guardião por hooks — recomendada:** script empacotado lê o último `token_count`, deduplica por
   sessão e cria faixas. Em 60%, alerta a UI e injeta ordem de checkpoint; em 70%, pode bloquear
   trabalho novo, liberando apenas pedidos naturais de checkpoint/limpeza. `PostToolUse` reduz a
   latência dentro do turno; `UserPromptSubmit` é a barreira antes do próximo trabalho.
3. **Wrapper/app-server:** consumir `thread/tokenUsage/updated` por um cliente externo. Usa evento
   estruturado, mas exige envolver o Codex num processo adicional e foge do plugin simples.

## Defesa complementar

Baixar `model_auto_compact_token_limit` oferece reserva contra estouro, mas é opt-in e não substitui
checkpoint: compactação automática resume o chat, não grava board/wiki. Não deve ser alteração
global silenciosa do plugin.

## Pergunta ao dono

O dono esclareceu que compactação recorrente é o comportamento a evitar. O contrato desejado é:
checkpoint durável e verificado → relatório “Seguro dar `/clear`” → `/clear` manual → próxima sessão
retoma apenas de board/wiki/memória.

A documentação atual do Codex confirma que `/clear` limpa o terminal **e inicia um chat novo** na
mesma execução do CLI; não é o mesmo que `Ctrl+L`, que apenas limpa a tela e mantém o chat atual.
Portanto, o fluxo realmente separa o histórico antigo do novo contexto, como o dono precisa.

## Desenho proposto para aprovação

1. **55% observado — pré-alerta:** avisar que o bloco está próximo do fechamento; não interromper o
   trabalho atômico em curso.
2. **Primeiro valor observado ≥60% — checkpoint obrigatório:** o Manager para antes de iniciar nova
   frente, executa o protocolo atual de checkpoint e verifica board, thread e memória.
3. **Depois do checkpoint:** o relatório existente termina em “Seguro dar `/clear`”. O guardião
   bloqueia trabalho novo naquela sessão; permite apenas corrigir uma verificação falhada ou repetir
   o checkpoint. O `/clear` continua manual porque o plugin não deve controlar o TUI do dono.
4. **Nova sessão após `/clear`:** `SessionStart(source=clear)` reidrata `memory/MEMORY.md`, a thread
   ativa e o board antes de qualquer trabalho.
5. **70% — contingência:** se o checkpoint ainda não terminou, o hook bloqueia qualquer prompt que
   não seja checkpoint/recuperação. Não espera 80%.
6. **Compactação automática — última falha, não fluxo:** `PreCompact` registra alerta de emergência,
   mas não tenta substituir o checkpoint por resumo compactado nem bloqueia o núcleo perto do limite.

O limiar de 55% existe porque o contador é discreto: não há garantia de observar exatamente 60%
antes de um salto. A política pública continua dizendo “checkpoint obrigatório a partir de 60%”.

**GATE:** aprovar ou ajustar esse comportamento antes da especificação e implementação.

## Especificação

Design registrado em
`docs/superpowers/specs/2026-08-09-protecao-contexto-codex-design.md`. O backstop automático de 90%
foi definido como valor absoluto calculado da janela efetiva; para `997500`, o valor é `897750` com
escopo `total`. A alteração de configuração continua opt-in.

## Implementação inline

- ✅ parser limitado, faixas e estado atômico por sessão;
- ✅ decisões dos seis eventos, handshake e prevenção de loop;
- ✅ bundle `hooks/hooks.json` e lint de referências;
- ✅ contrato natural, diagnóstico e documentação viva;
- ✅ release local identificada como `0.22.0` para evitar colisão com cache `0.21.0`.

Evidência atual: 49 testes, manifesto estrito, lint de coerência e `git diff --check` passam no
worktree `feat/t043-context-guard`. O primeiro painel real comprovou `claude-opus-5` no
`modelUsage` e encontrou falso handshake, reset inseguro no `/clear` e corrida no lock; os casos
foram reproduzidos RED e corrigidos com handshake ancorado, marcador durável de reset e `flock`
liberado pelo SO. O Kimi K3 também revisou o diff e suas ressalvas verificáveis entraram nos testes.

Na rodada final, três lotes Opus 5 começaram pelo runner, mas todos encerraram em
`OPUS_TIMEOUT` após 240 s. O Kimi encerrou com exit 1 e sem o contrato final. Pelo protocolo, não
houve retry automático. O dono autorizou uma tentativa sequencial menor em 2026-08-10:

- Opus: exit 0, `OPUS_MODEL=claude-opus-5`, `OPUS_SECONDS=205.2`, briefing 14.927 bytes,
  `APROVADO_COM_RESSALVAS`, nenhum bloqueador;
- Kimi: exit 0, sessão `session_b7c87685-862d-4dd0-81ef-5131dc282d5c`,
  `APROVADO_COM_RESSALVAS`, nenhum bloqueador;
- convergência: corrida residual do marcador pode exigir um segundo `/clear`, mas não cria bypass;
  registrada no `T-044`, junto do fallback Windows sem recuperação de lock órfão.

Instalação local concluída depois da integração em `main`:

- `orq@orquestra` aparece instalado e habilitado como `0.22.0`;
- excluindo os diretórios de metadados, o cache é idêntico à fonte; o Codex omite
  `.claude-plugin/plugin.json` e cria `.codex-plugin/migrated-command-skills`, enquanto
  `codex plugin list` confirma a versão `0.22.0` e o marketplace-fonte correto;
- seis hooks do `orq` foram revisados e confiados interativamente, sem bypass;
- uma sessão Codex nova executou o hook real e gravou estado em
  `~/.codex/plugins/data/orq-orquestra/context-guard/` com `last_percent=3.19` e somente as sete
  chaves permitidas;
- smoke sintético diretamente do cache passou em Stop 60%, handshake, bloqueio até `/clear`,
  reidratação e retomada aberta.

Não houve configuração global do backstop de 90%, publicação ou push. O startup ainda aponta um
erro pré-existente e separado: `~/.codex/hooks.json` contém `_managedBy`, campo que o Codex 0.147.0
não aceita; isso não impediu os seis hooks confiados do plugin de rodarem.

## RETOMAR AQUI

### Incidente recorrente — 2026-08-13

O dono decidiu a pendência anterior: depois do checkpoint, a **mesma conversa deve continuar**;
ela não pode ficar bloqueada, inclusive durante `/goal`. O incidente reproduziu em threads de
desenvolvimento importantes. O banco local `~/.codex/sqlite/goals_1.sqlite` tinha zero metas, então
o `/goal` não era o bloqueio persistido: ele apenas continuava tentando executar enquanto o hook
recusava os prompts.

Causa comprovada no cache ativo `0.22.0`: o `context-guard.py` ainda tinha três saídas
`decision: block`. Um reset simples do estado não funciona para transcript já alto: na sessão
`019fee80-f689-7640-bde7-9b807a85d29e`, o próximo evento releu 90,2% e recriou `emergency`.

Contenção operacional aplicada, sem apagar conversas: backup em
`~/.codex/plugins/data/orq-orquestra/context-guard-backup-20260813-incident/`; os 7 estados que
estavam em `clear_required`, `checkpoint_required` ou `emergency` receberam marcador `.allow`.
O cache instalado ganhou ramo restrito por sessão antes do cálculo da faixa. Smoke direto da
sessão informada retornou `decision:block = 0` e uma instrução prioritária para atender e continuar.
Isso é hotfix recuperável do ambiente, não implementação do produto nem release.

### Plano permanente no gate

1. Criar testes RED para continuação em `clear_required`, `emergency` e Goal mode, inclusive
   transcript acima de 90%; nenhum `UserPromptSubmit` ou `Stop` pode devolver `decision: block`.
2. Tornar 55/60/70 consultivos: preservar telemetria, deduplicação e checkpoint durável, mas emitir
   apenas contexto prioritário que conclui o checkpoint e continua o pedido atual.
3. Depois do checkpoint, limpar o latch de execução e permitir a mesma conversa; compactação nativa
   substitui a obrigação de `/clear`. Remover texto vivo que manda abandonar/bloquear a sessão.
4. Tratar `/goal` como continuidade normal: meta ativa não muda a política e nunca vira requisito
   para desbloqueio; teste não depende do banco privado do App.
5. Atualizar `checkpoint.md`, a skill, arquitetura e testes para um único contrato consultivo.
6. Rodar testes do guardião, `claude plugin validate ./orq --strict` e
   `python3 orq/scripts/lint-coerencia.py .`; depois fazer smoke em sessão real já acima do limiar.

Riscos: alerta consultivo pode ser ignorado e levar a compactação antes de um checkpoint completo;
por isso o checkpoint continua automático/durável, mas nunca ganha poder de negar o pedido. O
marcador `.allow` emergencial precisa ser retirado quando a versão corrigida estiver comprovada,
para não virar estado paralelo permanente.

Critérios de aceite: `pode continuar` passa na mesma conversa após checkpoint; `/goal` segue; 0
respostas `decision:block`; board/thread sobrevivem à compactação; hooks do Orquestra não alteram
o Claude. Publicação, push, cache global, backstop de 90% e update do Claude seguem fora do gate.

## RETOMAR AQUI

Plano consultivo aprovado pelo dono em 2026-08-13. Uma compactação ocorreu durante o Loop B; o
checkpoint de recuperação releu `memory/MEMORY.md`, o board e esta thread e confirmou que o gate
continua válido. Retomar o implementador já iniciado no worktree
`feat/t043-compactacao-reidratada`, começando pelos testes RED. Depois: verificação independente,
painel Opus 5 + Kimi K3, documentação e movimento para VALIDATE. Não publicar, dar push, atualizar
o Claude nem substituir caches globais sem novo ok.
