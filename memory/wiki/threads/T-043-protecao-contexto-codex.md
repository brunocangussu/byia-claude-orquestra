# T-043 — Proteção preventiva da janela de contexto no Codex

## Pedido do dono

Investigar se o Orquestra consegue acompanhar a ocupação da janela do Codex e sinalizar um
checkpoint ao ultrapassar 60%, antes que saltos da statusline levem a sessão diretamente para
70–80% ou para a compactação/saturação automática.

## Estado

AWAITING_OWNER. Nenhuma implementação autorizada.

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

## RETOMAR AQUI

O dono deve revisar a especificação escrita. Após aprovação, produzir o plano de implementação;
parar no gate antes de alterar o produto.
