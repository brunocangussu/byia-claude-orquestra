# Proteção de contexto Codex com compactação reidratada

**Card:** `T-043`
**Data da revisão:** 2026-08-10
**Estado:** desenho aprovado pelo dono para implementação completa

## Objetivo

Preservar o checkpoint durável do Orquestra sem impor ao Codex App um comando que ele não possui.
Cada host conserva a fronteira nativa que realmente oferece:

| Host | Depois do checkpoint verificado |
|---|---|
| Claude Code | bloquear trabalho novo até o dono executar `/clear` |
| Codex CLI e Codex App | permitir a compactação do núcleo; depois reidratar board, wiki e thread |
| Kimi | manter o fallback textual existente, sem ativar o guardião Codex |

O fluxo Codex passa a ser:

```text
trabalho → 55% pré-alerta → ≥60% checkpoint obrigatório
        → checkpoint verificado → compactação manual ou automática permitida
        → SessionStart(source=compact) → reidratação → trabalho
```

## Evidência que reprovou o desenho anterior

No teste real do dono no Codex App, o checkpoint terminou em **Seguro dar `/clear`.** e o estado
`clear_required` passou a bloquear `/CLEAR`, `continue` e `allow`. O App não expõe `/clear`; a
conversa ficou sem saída até a compactação automática.

A documentação oficial confirma:

- o App lista `/compact`, mas não `/clear`;
- `/clear` e `/new` são comandos do CLI;
- `PreCompact` e `PostCompact` distinguem `manual` de `auto`;
- depois da compactação, `SessionStart(source="compact")` roda antes da próxima chamada ao
  modelo, inclusive quando a compactação automática acontece no meio de um turno;
- `PreCompact` pode impedir a compactação com `continue: false`, portanto o guardião nunca emitirá
  esse campo.

Referências: [Hooks](https://learn.chatgpt.com/docs/hooks),
[comandos](https://learn.chatgpt.com/docs/developer-commands) e
[projetos e chats](https://learn.chatgpt.com/docs/projects).

## Alternativas avaliadas

1. **Manter `/clear` nos dois hosts:** rejeitada porque cria um estado sem saída no Codex App.
2. **Remover o checkpoint e confiar apenas na compactação:** rejeitada porque a compactação não
   substitui board, wiki, thread e log duráveis.
3. **Checkpoint por host + compactação reidratada no Codex:** escolhida. Preserva o contrato forte
   do Claude e usa a primitiva nativa do Codex.

## Arquitetura

### 1. Isolamento de host

`hooks/hooks.json` continua sendo o bundle portátil reconhecido pelo Codex. O script só fica ativo
quando existe a variável nativa `PLUGIN_ROOT`, fornecida pelo Codex. Variáveis exclusivamente
`CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` não ativam o guardião.

Depois de confirmar que o host é Codex, o script pode aceitar as aliases `CLAUDE_*` apenas para
resolver caminhos compatíveis. Assim, uma futura instalação do mesmo pacote no Claude carrega o
bundle, mas o comando sai `0` sem stdout, sem estado e sem mudar a conversa.

### 2. Estado Codex v2

O estado por `session_id` passa a conter somente:

```text
state_version, phase, pre_alert_sent, checkpoint_started,
checkpoint_verified, recovery_required, last_percent, updated_at
```

Valores de `phase`:

| Fase | Significado |
|---|---|
| `normal` | menos de 55% |
| `pre_alert` | 55% a menos de 60% |
| `checkpoint_required` | 60% ou mais sem checkpoint iniciado |
| `emergency` | 70% ou mais sem checkpoint verificado |
| `checkpoint_verified` | artefatos duráveis verificados; compactação liberada |
| `recovery_required` | a compactação ocorreu antes de um checkpoint verificável |

Nenhum prompt, mensagem, saída de ferramenta, caminho clínico ou dado do projeto é persistido.

Estados legados sem `state_version` são migrados. `clear_required=true` vira
`checkpoint_verified=true`; nunca conserva o bloqueio antigo. Estado inválido continua sendo
renomeado para diagnóstico e recriado vazio.

### 3. Handshake por host

O comando compartilhado de checkpoint produz uma frase final conforme o host:

- Claude: **Seguro dar `/clear`.**
- Codex: **Checkpoint verificado; compactação liberada.**

O guardião Codex reconhece a frase nova e, por compatibilidade de migração, também reconhece a
frase antiga **Seguro dar `/clear`.** como checkpoint verificado — sem entrar em bloqueio.
Menções instrutivas ou negativas não completam o handshake.

### 4. Decisões por evento

#### `Stop`

- 55% a menos de 60%: pré-alerta único.
- 60% ou mais sem checkpoint: uma continuação automática executa o checkpoint.
- `stop_hook_active=true`: nunca cria segunda continuação.
- handshake verificado: grava `checkpoint_verified` e apenas informa que a compactação está
  liberada; não retorna `decision=block`.

#### `UserPromptSubmit`

- antes do checkpoint, em emergência, bloqueia trabalho que não seja checkpoint/recuperação;
- depois de `checkpoint_verified=true`, nunca bloqueia por causa do guardião, mesmo acima de 70%;
- a compactação continua sendo decisão do núcleo ou do `/compact` nativo do App.

#### `PreCompact`

- nunca retorna `continue: false`;
- não tenta executar checkpoint dentro do hook;
- quando ainda não há checkpoint verificado, pode mostrar um aviso curto de que a retomada exigirá
  checkpoint de recuperação.

#### `PostCompact`

- nunca bloqueia nem injeta uma segunda orientação longa;
- deixa a reidratação para o `SessionStart(source="compact")`, evitando contexto duplicado.

#### `SessionStart(source="compact")`

- com checkpoint verificado: reinicia a máquina em `normal` e injeta leitura de
  `memory/MEMORY.md`, `memory/wiki/KANBAN.md` e thread ativa;
- sem checkpoint verificado: reinicia em `recovery_required` e ordena a mesma leitura seguida de
  checkpoint de recuperação antes de trabalho novo;
- nunca pede `/clear`.

#### `SessionStart(source="clear")`

Mantém compatibilidade com o CLI: reinicia o estado e injeta a reidratação atual. Isso não muda o
contrato do Claude, porque o script Codex está isolado pelo gate de host.

### 5. Documentação compartilhada sem regressão

Os pontos vivos deixam explícito que a limpeza é por host:

- `orq/commands/checkpoint.md`: formato final bifurcado por host;
- `orq/skills/orq/SKILL.md`: Codex usa compactação reidratada; Claude preserva `/clear`;
- `README.md`, `memory/wiki/arquitetura.md` e `memory/wiki/distribuicao.md`: contrato operacional e
  teste dos dois hosts;
- `orq/commands/instalar.md` e `orq/commands/stack.md`: smoke Codex verifica compactação, e o
  smoke Claude verifica que o guardião não atua.

## Configuração de compactação

Esta correção usa a compactação já fornecida pelo Codex. Ela não grava silenciosamente
`model_auto_compact_token_limit` nem altera `~/.codex/config.toml`. O backstop absoluto de 90%
continua sendo configuração opt-in separada, porque depende da janela efetiva do modelo ativo.

## Testes obrigatórios

### RED/GREEN unitário

1. checkpoint verificado não bloqueia o próximo `UserPromptSubmit`;
2. a frase antiga migra para `checkpoint_verified` sem `clear_required`;
3. estado legado `clear_required=true` migra sem bloqueio;
4. `PreCompact(auto)` nunca impede a compactação;
5. `PostCompact(auto)` não duplica a orientação;
6. `SessionStart(compact)` com checkpoint reidrata e volta a `normal`;
7. `SessionStart(compact)` sem checkpoint exige recuperação;
8. ambiente somente `CLAUDE_*` retorna sem saída e não cria estado;
9. ambiente Codex com `PLUGIN_*` continua executando;
10. nenhum conteúdo da conversa aparece no JSON persistido.

### Gates do repositório

```bash
python3 -m unittest orq/scripts/test_context_guard.py
python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
git diff --check
```

### Painel e smokes

- Opus 5 e Kimi K3 revisam o diff sanitizado em read-only;
- smoke do cache Codex percorre checkpoint → prompt permitido → compact → reidratação;
- smoke Claude usa somente `CLAUDE_*` e prova ausência de stdout/estado;
- o Claude instalado permanece em `0.21.0` durante a validação desta correção;
- o Codex local recebe a versão nova e é testado em chat novo.

## Distribuição

- release corretiva: `0.22.1`;
- qualquer mudança em `orq/` atualiza os quatro lugares exigidos pelo projeto;
- o cache Codex local pode ser atualizado depois dos gates e do painel;
- o cache Claude não é atualizado nesta frente;
- push e publicação no GitHub permanecem fora desta autorização.

## Critérios de aceitação

1. Nenhum trabalho novo passa do primeiro valor observado em 60% sem checkpoint verificável.
2. Depois do checkpoint verificado, o Codex não bloqueia prompts exigindo `/clear`.
3. A compactação manual e automática nunca é impedida pelo guardião.
4. Depois da compactação, a retomada recebe board, wiki e thread antes do trabalho.
5. Compactação sem checkpoint produz recuperação durável, não um falso estado normal.
6. Estado legado instalado não consegue recriar o deadlock `clear_required`.
7. O Claude conserva o fluxo **Seguro dar `/clear`.** e o guardião Codex não atua nele.
8. Nenhum conteúdo da conversa é persistido e nenhum erro impede a compactação.
9. Testes, validadores, painel Opus 5 + Kimi K3 e smokes dos dois hosts fecham sem bloqueador.
