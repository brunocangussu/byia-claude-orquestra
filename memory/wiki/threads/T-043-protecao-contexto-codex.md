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

O redesenho aprovado está implementado no worktree `feat/t043-compactacao-reidratada`:

- estado v2 com `checkpoint_verified` e `recovery_required`;
- migração do `clear_required` legado sem recriar o deadlock;
- prompt seguinte permitido após checkpoint, inclusive acima de 70%;
- `PreCompact`/`PostCompact` nunca bloqueiam;
- `SessionStart(source=compact)` reidrata memória, board e thread, ou exige recuperação quando a
  compactação ocorreu antes do checkpoint;
- ambiente somente `CLAUDE_*` sai sem stdout nem estado; o contrato Claude continua terminando em
  `Seguro dar /clear.` e aguardando `/clear` manual.

Evidência local antes do painel: 57 testes, `py_compile`, manifesto estrito, lint de coerência e
`git diff --check` passaram.

Painel da candidata `eeb2899`:

- Opus 5 foi invocado de verdade pelo runner (`BRIEFING_BYTES=15280`), mas não devolveu parecer:
  `OPUS_TIMEOUT` após 240 s. Não contar como aprovação e não repetir automaticamente.
- Kimi K3 (`kimi-code/k3`) revisou no clone descartável `/tmp/orq-t043-kimi.Lgt8t6/repo`, exit 0,
  sessão `session_48fe1cdc-382d-436d-b1c9-4d6b51b98870`: `APROVADO_COM_RESSALVAS`, sem
  bloqueadores. Confirmou em runtime que `recovery_required` é ignorado quando o transcript ainda
  não tem `token_count`; também apontou que `checkpoint_verified` pode ficar obsoleto após muito
  trabalho novo antes da compactação. Outros riscos: startup/New chat sem reidratação explícita,
  frase Claude aceita como compatibilidade no Codex e hooks Pre/PostCompact registrados como no-op.

## Decisão do dono — guardião Codex nunca bloqueia

Em 2026-08-10, o dono substituiu explicitamente o requisito de enforcement: no framework do Codex,
nenhum hook do Orquestra pode bloquear prompt, ferramenta, `Stop` ou compactação. As faixas continuam
observando a telemetria e solicitando o checkpoint durável; depois dele, a pessoa escolhe continuar,
abrir outra conversa/task ou deixar a compactação nativa acontecer. O Claude mantém o contrato
próprio com `/clear`; esta mudança é Codex-only.

Esta decisão também resolve o risco de checkpoint obsoleto sem recriar deadlock: continuar é uma
escolha consciente e o próximo alerta/checkpoint pode rearmar de modo consultivo, nunca impeditivo.
Compactação sem checkpoint injeta recuperação, mas não bloqueia trabalho.

## Hotfix das sessões abertas

O cache executado pelas sessões existentes foi corrigido diretamente em
`~/.codex/plugins/cache/orquestra/orq/0.22.0/scripts/context-guard.py`. Antes da alteração, o arquivo
original foi preservado em `context-guard.py.bak-nonblocking-20260811` com SHA-256
`33f8f0a65381d7b1fbf287c6219462b44c238b8e14ce6d7e99bcc417e9b27551`. A salvaguarda final remove
`decision=block`/`reason` de qualquer ramo legado e converte o resultado em aviso consultivo.
`py_compile` passou; smokes de `clear_required`, prompt em 72% e `Stop` em 60% saíram sem decisão de
bloqueio. O hotfix é global para sessões que usam o cache `0.22.0`, incluindo New ByIA Project e
Bruno Vascular; não apaga estado, transcript ou memória.

Após evidência visual de que o modelo ainda insistia em `/clear`, a segunda camada também foi
corrigida: a saída do hook agora sanitiza qualquer texto legado com `/clear`; a skill instalada diz
explicitamente que a política Codex é consultiva mesmo acima de 70%; e `commands/checkpoint.md` foi
atualizado para o handshake Codex de compactação liberada. Backups separados de `SKILL.md` e
`checkpoint.md` foram criados com o sufixo `.bak-nonblocking-20260811`. `py_compile` e o teste do
sanitizador passaram, sem `decision=block` nem `/clear` na saída Codex.

A segunda tentativa visual ainda falhou porque o hotfix devolvia apenas `systemMessage`: isso remove
o bloqueio técnico, mas não injeta uma instrução prioritária no contexto do modelo, que continuava
obedecendo ao contrato antigo já carregado. A causa raiz foi corrigida no entrypoint do cache: todo
`UserPromptSubmit` agora produz `hookSpecificOutput.additionalContext` mandando atender o pedido
atual, tratar checkpoint apenas como documentação e ignorar exigências anteriores de limpeza ou
interrupção. Um smoke com estado `clear_required`, 80% e prompt “pode continuar daqui” confirmou a
saída prioritária, sem `decision=block` e sem instrução de limpeza (`LIVE_PRIORITY_OVERRIDE=PASS`).

## Checkpoint de 2026-08-13 — deriva confirmada

O hotfix direto não sobreviveu ao gerenciamento do cache: `codex plugin list` continua em `0.22.0`
e o `context-guard.py` ativo voltou ao SHA original bloqueante
`33f8f0a65381d7b1fbf287c6219462b44c238b8e14ce6d7e99bcc417e9b27551`. Não presumir que New ByIA
ou Bruno Vascular estão desbloqueados. A solução válida é somente release nova instalada a partir da
fonte; repetir edição do cache criaria o mesmo resultado temporário.

⏭️ RETOMAR AQUI: atualizar especificação/plano/testes para a invariável “zero `decision=block` no
host Codex”; escrever RED para 60%, 70%, recuperação sem telemetria e estado legado. Implementar
respostas consultivas na fonte `0.22.1`, rodar GREEN + gates, obter parecer Opus 5 válido,
reconciliar Kimi, integrar em `main`, instalar somente no Codex e confirmar nas sessões New ByIA e
Bruno Vascular. Não fazer push, publicação, update do Claude nem alterar o backstop de 90%.

## Checkpoint de recuperação pós-compactação — 2026-08-13

A conversa compactou antes do fluxo intencional, então o estado foi reidratado a partir de
`memory/MEMORY.md`, `KANBAN.md`, desta thread e do Git. O card não mudou de coluna. O worktree está
em `d081608` e contém oito arquivos modificados, 322 inserções e 147 remoções, sem erro em
`git diff --check`. O conteúdo do diff converge com a decisão posterior do dono: remover bloqueios
Codex, manter alertas/checkpoints consultivos e preservar o contrato Claude separado.

Essas mudanças ainda não foram validadas nesta retomada nem commitadas. Elas devem ser tratadas como
trabalho em curso possivelmente produzido por outra janela: não sobrescrever, não descartar e não
atribuir autoria sem evidência.

⏭️ RETOMAR AQUI: validar o diff existente com testes do guardião, `py_compile`, manifesto estrito,
lint de coerência, identidade `AGENTS.md`/`CLAUDE.md` e buscas por qualquer `decision=block` ou
instrução `/clear` no caminho Codex. Se passar, revisar os riscos Kimi, obter parecer Opus 5 válido e
só depois decidir integração e instalação local da `0.22.1`. Não fazer push/publicação nem alterar
o Claude.

## Validação e painel final — 2026-08-13

- recuperação sem `token_count`: reproduzida RED e corrigida antes da leitura da telemetria;
- checkpoint obsoleto: reproduzido RED e corrigido com `checkpoint_percent` e rearme consultivo após
  +10 pontos percentuais;
- defesa anti-bloqueio: teste RED provou que `continue:false`, `stopReason`, `permissionDecision:deny`
  e `reason` legado escapavam; `_persist_response` agora usa allowlist estrita;
- frase `**Checkpoint verificado; conversa continua**.`: reproduzida RED e aceita;
- Opus 5 real: `OPUS_MODEL=claude-opus-5`, 124,5 s, 6.367 bytes,
  `APROVADO_COM_RESSALVAS`, sem bloqueadores;
- Kimi K3 real: sessão `session_b48d9d4e-6539-4f6f-b599-275addecbcea`, diff completo,
  `APROVADO_COM_RESSALVAS`, sem bloqueadores;
- gates: 65 testes do guardião, 14 do runner, `py_compile`, manifesto estrito, lint, identidade
  AGENTS/CLAUDE, `git diff --check` e higiene de `__pycache__` passaram.

⏭️ RETOMAR AQUI — SUPERADO PELA RELEASE COMBINADA T-037/T-043: criar o commit estreito de T-043 no
worktree, inspecionar o `main` sujo antes de integrar, preservar mudanças concorrentes, instalar
`0.22.1` somente no Codex e executar smokes reais em New ByIA e Bruno Vascular. Não fazer
push/publicação nem atualizar o Claude.

## Integração na release `0.22.3` — 2026-08-15

O commit estável `bbcc4cb` foi integrado ao commit combinado `b84bc51` da T-037. O merge preservou o
guardião consultivo e deixou integralmente fora a candidata T-044/`0.22.2` não commitada. Por decisão
do dono, a publicação passa a ser paritária: `0.22.3` no Codex e no Claude, com caches antigos ainda
referenciados preservados; o Kimi recebe o mesmo snapshot no ciclo de instalação.

⏭️ RETOMAR AQUI: corrigir os achados finais da revisão da `0.22.3`, repetir gates e obter re-review
limpo; depois publicar, instalar nos dois hosts, comparar o cache novo, provar o fail-open no Claude
e os smokes do guardião em processo Codex novo. A validação do dono continua sendo o gate de fecho.

## Publicação e smokes finais — 2026-08-15

A `0.22.3` foi publicada em `origin/main` no commit `3bb1a24`, instalada no Codex e no Claude e
espelhada no Kimi. A suíte combinada fechou em 113 testes. Em processo Codex novo, o guardião foi
consultivo e encontrou `memory/MEMORY.md`; em ambiente somente Claude, o hook saiu fail-open sem
stdout nem estado e o contrato `/clear` permaneceu. Os caches novos bateram com a fonte remota.

⏭️ RETOMAR AQUI — VALIDATE: o dono deve reabrir a task e confirmar o comportamento real. O warning
global `_managedBy` é preexistente e continua em follow-up separado; não bloqueia esta validação.
