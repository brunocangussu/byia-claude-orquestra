# Proteção preventiva da janela de contexto no Codex

**Card:** `T-043`  
**Data:** 2026-08-09  
**Estado:** design aprovado conceitualmente; especificação aguardando revisão do dono

## Objetivo

Evitar que uma sessão Codex longa dependa de compactações sucessivas. Antes da saturação, o
Orquestra deve persistir o estado do trabalho com seu checkpoint verificado, declarar que é seguro
executar `/clear` e impedir que trabalho novo continue naquela conversa.

O fluxo desejado é:

```text
trabalho → aviso preventivo → checkpoint verificado → “Seguro dar /clear” → /clear manual
        → chat novo → reidratação por board/wiki/memória
```

`/compact` não é parte do fluxo normal. A compactação automática do Codex permanece apenas como
última proteção para a sessão não falhar se todo o protocolo anterior for ultrapassado.

## Fatos confirmados

1. O contrato atual de `orq/commands/checkpoint.md` já persiste log, páginas vivas, thread, board e
   índice; depois verifica os sinais e só então pode afirmar “Seguro dar `/clear`”.
2. O Codex define `/clear` como “limpar o terminal e iniciar um chat novo”. `Ctrl+L` limpa apenas a
   tela e mantém o chat atual.
3. A statusline não é um contador contínuo. `context-used` deriva do último `token_count` concluído;
   por isso pode saltar entre dois valores.
4. Hooks Codex recebem `session_id` e `transcript_path`. `UserPromptSubmit` e `PostToolUse` podem
   adicionar developer context; `UserPromptSubmit` pode bloquear; `Stop` pode criar uma continuação
   automática; `SessionStart` distingue `clear` de `compact`.
5. Plugins podem distribuir `hooks/hooks.json`. O Codex fornece `PLUGIN_ROOT`/`PLUGIN_DATA` e as
   aliases compatíveis `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`.
6. O transcript contém eventos `token_count` com `last_token_usage` e `model_context_window`, mas a
   documentação declara que o formato do transcript não é uma interface estável.

## Limites e não objetivos

- O guardião não interrompe uma amostragem do modelo que já começou.
- Um salto pode atravessar 60% sem que um evento intermediário tenha existido. Por isso há pré-alerta
  em 55% e contingência no primeiro valor observado acima do limiar.
- O plugin não executa `/clear` sozinho. Encerrar o chat permanece uma ação visível do dono.
- O plugin não desabilita a compactação automática do núcleo e nunca bloqueia `PreCompact` perto do
  limite duro.
- O plugin não envia transcript, prompts ou dados do projeto a serviços externos.
- Esta entrega não altera a statusline nativa planejada em `T-042`.

## Arquitetura

### 1. `context-guard.py`

Novo script empacotado em `orq/scripts/context-guard.py`, chamado pelos hooks. Ele:

1. lê o JSON do hook por `stdin`;
2. usa apenas `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active` e o match
   da frase final do checkpoint;
3. busca de trás para frente o evento `token_count` mais recente, com limite rígido de bytes;
4. calcula `last_token_usage.total_tokens / model_context_window`;
5. consulta e atualiza estado pequeno por sessão em
   `${PLUGIN_DATA}/context-guard/<session_id>.json`;
6. emite JSON válido para o evento atual ou sai `0` sem saída.

O parser não carrega o transcript inteiro. Ele não armazena prompts nem mensagens; persiste somente
percentual, faixa já sinalizada, estado do checkpoint e timestamps.

### 2. Hooks empacotados

`orq/hooks/hooks.json` registra:

- **`PostToolUse`** — observa o percentual depois de ferramentas e injeta aviso/model context quando
  a telemetria já estiver atualizada;
- **`Stop`** — aplica pré-alerta e, ao primeiro valor observado em 60% ou mais, cria uma única
  continuação automática instruindo o Manager a executar o checkpoint; `stop_hook_active` e o estado
  persistido impedem loop;
- **`UserPromptSubmit`** — bloqueia trabalho novo depois que o checkpoint foi declarado seguro e, na
  contingência de 70%, aceita somente intenção de checkpoint/recuperação;
- **`SessionStart`** — em `source=clear`, injeta uma orientação curta para carregar
  `memory/MEMORY.md`, board e thread; em `source=compact`, informa que houve falha do fluxo normal e
  manda recuperar/persistir o estado antes de continuar;
- **`PreCompact`/`PostCompact`** — registram a contingência, mas não impedem o núcleo de compactar.

Hooks existentes do usuário continuam válidos; o Codex executa hooks correspondentes de múltiplas
fontes. A instalação deve explicar a revisão/confiança exigida para novos hooks.

### 3. Máquina de estados

| Estado | Condição | Comportamento |
|---|---|---|
| `NORMAL` | `<55%` | silêncio |
| `PRE_ALERT` | `55%–<60%` | um aviso por sessão; concluir apenas a unidade atômica atual |
| `CHECKPOINT_REQUIRED` | primeiro valor observado `≥60%` | uma continuação automática executa o checkpoint |
| `CHECKPOINT_RUNNING` | continuação já criada | não criar outro `Stop`; permitir correções da verificação |
| `CLEAR_REQUIRED` | resposta contém exatamente “Seguro dar `/clear`” | bloquear trabalho novo e pedir `/clear` |
| `EMERGENCY` | primeiro valor observado `≥70%` sem checkpoint seguro | bloquear trabalho novo; permitir apenas checkpoint/recuperação |
| `COMPACTED` | `PreCompact`/`PostCompact` observado | registrar falha do fluxo e reidratar antes de trabalhar |

Um chat novo após `/clear` recebe outro `session_id`; portanto, começa novamente em `NORMAL`.

### 4. Reconhecimento do checkpoint concluído

O `Stop` hook não tenta inferir mudanças de arquivos. Ele marca `CLEAR_REQUIRED` somente quando a
última resposta contém a frase contratual exata **“Seguro dar `/clear`”**, que o comando checkpoint
só pode emitir depois de verificar board/thread/memória.

Se a resposta disser “Gravado, mas NÃO afirmo que é seguro limpar”, o estado permanece
`CHECKPOINT_RUNNING` e o guardião permite apenas a correção da verificação.

## Compactação automática como backstop

As chaves corretas são:

```toml
model_auto_compact_token_limit = 897750
model_auto_compact_token_limit_scope = "total"
```

Para a janela efetiva atual de `997500`, `897750` representa 90%. `700000` representaria
aproximadamente 70,2% e poderia competir com o checkpoint obrigatório iniciado em 60%.

O valor é absoluto, não percentual. Como modelos diferentes têm janelas diferentes, o plugin não
deve gravar `897750` silenciosamente para todos. O diagnóstico/instalação deve:

1. descobrir a janela efetiva do modelo ativo;
2. calcular 90%;
3. mostrar o valor e o arquivo que seria alterado;
4. aplicar somente com aprovação explícita e backup;
5. alertar quando uma troca de modelo tornar o valor incompatível.

`model_auto_compact_token_limit_scope = "total"` é o padrão atual, mas será escrito explicitamente
quando o usuário aprovar a configuração, para o contrato não depender de default implícito.

## Falhas seguras

- Transcript ausente, truncado, alterado ou JSON inválido: sair `0`, não bloquear trabalho e mostrar
  no máximo um aviso de “telemetria indisponível” por sessão.
- `model_context_window` ausente/zero: não calcular percentual.
- `PLUGIN_DATA` não gravável: manter aviso em memória apenas naquela execução e nunca falhar o hook.
- Estado corrompido: renomear o arquivo de estado para diagnóstico e recriar vazio.
- Dois chats no mesmo projeto: isolamento obrigatório por `session_id`, nunca apenas por `cwd`.
- Claude/Kimi: o guardião detecta o host/schema; nesta primeira entrega, comportamento Codex é ativo
  e hosts não suportados saem `0` sem efeito.
- Nenhum caminho de erro pode impedir `PreCompact` do núcleo.

## Testes

### Unidade

- parser encontra o último `token_count` sem ler o transcript inteiro;
- limites em 54,9%, 55%, 59,9%, 60%, 69,9%, 70%, 89,9% e 90%;
- salto direto de 54% para 72%;
- deduplicação de pré-alerta e continuação de checkpoint;
- `stop_hook_active=true` não cria loop;
- frase “Seguro dar `/clear`” marca `CLEAR_REQUIRED`;
- verificação falhada não marca `CLEAR_REQUIRED`;
- transcript ausente, JSON parcial, evento desconhecido e estado corrompido falham abertos;
- sessões diferentes no mesmo `cwd` não compartilham estado;
- nenhum conteúdo de prompt/transcript é persistido.

### Integração

- validar `hooks/hooks.json` e comandos resolvidos via `PLUGIN_ROOT`;
- provar que hooks globais existentes continuam executando;
- instalar cache novo do plugin e aprovar os hooks;
- numa sessão Codex descartável, usar fixtures para forçar cada faixa e observar mensagens/decisões;
- provar que o checkpoint verificado leva a `CLEAR_REQUIRED`;
- executar `/clear` e provar novo `session_id` + reidratação de memória;
- confirmar que `PreCompact` continua permitido;
- validar Claude sem regressão e Kimi sem ativação acidental.

## Distribuição e escopo

- A entrega deve sair em release própria depois da `0.21.0`; não será misturada silenciosamente com
  a configuração de statusline de `T-042`.
- Modificar `orq/` exige bump coordenado de manifesto, marketplace, README e `memory/MEMORY.md`.
- Publicação, atualização global do cache, alteração de `~/.codex/config.toml` e push permanecem em
  gates separados do dono.
- O guardião vem habilitado pelo plugin para Codex, mas a alteração do limite automático em
  `config.toml` permanece opt-in.

## Critérios de aceitação

1. Em uso normal, uma sessão não inicia trabalho novo após o primeiro valor observado `≥60%` sem
   antes produzir checkpoint verificável.
2. Após “Seguro dar `/clear`”, qualquer prompt de trabalho é bloqueado até o `/clear`.
3. `/clear` cria chat novo e a retomada acontece apenas pelos artefatos duráveis.
4. Saltos acima de 70% entram em contingência imediatamente.
5. Erro de telemetria nunca trava o Codex nem desabilita sua compactação de segurança.
6. O plugin não persiste conteúdo da conversa e não altera configuração global sem aprovação.
