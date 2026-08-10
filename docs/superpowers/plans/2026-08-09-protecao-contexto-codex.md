# Proteção Preventiva do Contexto Codex Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer o Orquestra executar checkpoint verificável antes da saturação do contexto Codex,
bloquear trabalho novo até `/clear` e manter a compactação automática apenas como backstop em 90%.

**Architecture:** Um script Python sem dependências lê somente os eventos `token_count` mais recentes
do `transcript_path` recebido pelos hooks, mantém uma máquina de estados por `session_id` em `PLUGIN_DATA`
e emite respostas específicas para `Stop`, `UserPromptSubmit`, `PostToolUse`, `SessionStart`,
`PreCompact` e `PostCompact`. O comando de checkpoint conserva sua frase contratual como handshake;
a configuração absoluta de auto-compactação continua opt-in.

**Tech Stack:** Python 3 (`unittest`, `dataclasses`, `json`, `pathlib`), hooks JSON do Codex,
Markdown de comandos/skills, validadores `claude plugin validate` e `lint-coerencia.py`.

## Global Constraints

- Nenhuma dependência Python nova.
- Nunca persistir prompts, mensagens, tool output ou PII; estado contém somente números, faixa,
  estado e timestamps.
- Todo erro de parsing/IO falha aberto e nunca impede `PreCompact`.
- Estado isolado por `session_id`, nunca somente por `cwd`.
- `/clear` permanece manual; `/compact` não integra o fluxo normal.
- Limiar público: pré-alerta em 55%, checkpoint no primeiro valor observado `>=60%`, emergência em
  `>=70%` e compactação do núcleo em 90% como backstop.
- `model_auto_compact_token_limit` é absoluto e nunca será escrito globalmente sem aprovação.
- Release desta frente: `0.22.0`; o statusline opt-in de `T-042` passa para `0.23.0`.
- Publicação, push e mutação de `~/.codex/config.toml` ficam fora deste plano até gate próprio.

---

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `orq/scripts/context-guard.py` | parser de telemetria, estado por sessão e adaptadores de hooks |
| `orq/scripts/test_context_guard.py` | testes unitários e contratuais do guardião |
| `orq/hooks/hooks.json` | registro portátil dos seis eventos Codex |
| `orq/scripts/lint-coerencia.py` | validar comandos e arquivos citados pelos hooks |
| `orq/commands/checkpoint.md` | handshake “Seguro dar `/clear`” e comportamento guard-aware |
| `orq/commands/stack.md` | diagnóstico de hooks, telemetria e backstop opt-in |
| `orq/commands/instalar.md` | verificação de confiança/carregamento dos hooks no Codex |
| `orq/skills/orq/SKILL.md` | política natural 55/60/70 e retomada após clear/compact |
| `README.md`, `memory/wiki/arquitetura.md`, `memory/wiki/distribuicao.md` | contrato público e operacional |
| manifestos + `memory/MEMORY.md` | release coordenada `0.22.0` |

---

### Task 1: Parser limitado e máquina de estados

**Files:**
- Create: `orq/scripts/context-guard.py`
- Create: `orq/scripts/test_context_guard.py`

**Interfaces:**
- Produces: `UsageSnapshot(used_tokens: int, context_window: int)` com propriedade `percent: float`.
- Produces: `read_latest_usage(path: Path, tail_bytes: int = 4 * 1024 * 1024) -> UsageSnapshot | None`.
- Produces: `band_for(percent: float) -> str`, retornando `normal`, `pre_alert`,
  `checkpoint_required` ou `emergency`.
- Produces: `load_state(data_dir: Path, session_id: str) -> dict` e
  `save_state(data_dir: Path, session_id: str, state: dict) -> None`.

- [ ] **Step 1: escrever testes RED do parser**

Criar fixtures JSONL em `TemporaryDirectory` e cobrir:

```python
def test_read_latest_usage_uses_last_complete_token_count(self):
    write_jsonl(self.transcript, [
        token_event(540_000, 1_000_000),
        {"type": "event_msg", "payload": {"type": "other"}},
        token_event(610_000, 1_000_000),
    ])
    self.assertEqual(read_latest_usage(self.transcript).used_tokens, 610_000)

def test_read_latest_usage_ignores_partial_trailing_json(self):
    self.transcript.write_text(json.dumps(token_event(600_000, 1_000_000)) + "\n{")
    self.assertEqual(read_latest_usage(self.transcript).percent, 60.0)
```

- [ ] **Step 2: executar RED e confirmar falha por módulo ausente**

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Expected: FAIL porque `context-guard.py` ainda não existe.

- [ ] **Step 3: implementar o parser mínimo**

Implementar leitura binária limitada ao final do arquivo, descarte da primeira linha parcial e busca
reversa por `payload.type=token_count`, `info.last_token_usage.total_tokens` e
`info.model_context_window`. Aceitar somente inteiros positivos e retornar `None` para forma inválida.

- [ ] **Step 4: adicionar testes RED das faixas e estado**

```python
for percent, expected in [
    (54.9, "normal"), (55.0, "pre_alert"), (59.9, "pre_alert"),
    (60.0, "checkpoint_required"), (69.9, "checkpoint_required"),
    (70.0, "emergency"), (90.0, "emergency"),
]:
    with self.subTest(percent=percent):
        self.assertEqual(band_for(percent), expected)
```

Cobrir estado inexistente, gravação atômica, JSON corrompido renomeado e dois `session_id` no mesmo
diretório sem colisão.

- [ ] **Step 5: implementar estado mínimo e rodar GREEN**

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Expected: PASS nos testes do Task 1.

- [ ] **Step 6: lint após a mudança**

Run: `python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py`  
Expected: exit `0`.

- [ ] **Step 7: commit do parser**

```bash
git add orq/scripts/context-guard.py orq/scripts/test_context_guard.py
git commit -m "feat: adicionar telemetria preventiva do contexto codex"
```

---

### Task 2: Decisões dos hooks e prevenção de loops

**Files:**
- Modify: `orq/scripts/context-guard.py`
- Modify: `orq/scripts/test_context_guard.py`

**Interfaces:**
- Consumes: interfaces do Task 1.
- Produces: `handle_event(event: dict, env: Mapping[str, str]) -> dict | None`.
- Produces: `main() -> int`, stdin JSON → stdout JSON compacto.

- [ ] **Step 1: escrever testes RED de host e falha aberta**

Cobrir `PLUGIN_ROOT` ausente, stdin inválido, transcript ausente, janela zero e evento desconhecido;
todos retornam `None`/exit `0` sem bloquear.

- [ ] **Step 2: escrever testes RED do `Stop`**

```python
def test_stop_at_sixty_continues_once_with_checkpoint_instruction(self):
    result = handle_event(stop_event(percent=60, stop_hook_active=False), self.codex_env)
    self.assertEqual(result["decision"], "block")
    self.assertIn("checkpoint", result["reason"].lower())

def test_stop_hook_active_does_not_loop(self):
    result = handle_event(stop_event(percent=65, stop_hook_active=True), self.codex_env)
    self.assertNotEqual((result or {}).get("decision"), "block")
```

Cobrir pré-alerta único em 55%, salto 54→72 e deduplicação depois de `checkpoint_started=true`.

- [ ] **Step 3: executar RED**

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Expected: FAIL porque `handle_event` ainda não existe.

- [ ] **Step 4: implementar `Stop`, `PostToolUse` e handshake**

- `Stop` em 55–<60: `systemMessage`, uma vez.
- `Stop` em >=60: `decision=block` uma vez, com continuação natural para executar checkpoint.
- `stop_hook_active=true`: nunca continuar novamente.
- Se `last_assistant_message` contiver a frase contratual `Seguro dar /clear` com ou sem crases,
  marcar `clear_required=true` e exibir `systemMessage`.
- A frase negativa `NÃO afirmo que é seguro limpar` nunca marca sucesso.
- `PostToolUse` usa `hookSpecificOutput.additionalContext`, sem bloquear ferramenta.

- [ ] **Step 5: escrever testes RED de `UserPromptSubmit` e sessões**

Cobrir `test_user_prompt_is_blocked_after_safe_checkpoint`,
`test_checkpoint_prompt_is_allowed_during_emergency`,
`test_ordinary_prompt_at_sixty_injects_checkpoint_before_work`,
`test_session_start_clear_injects_memory_rehydration`,
`test_session_start_compact_marks_recovery_mode` e
`test_precompact_never_returns_continue_false`.

- [ ] **Step 6: implementar os adaptadores restantes e rodar GREEN**

Reconhecer intenção permitida de recuperação com padrões conservadores para `checkpoint`, `salva`,
`salvar`, `seguro limpar`, `corrigir verificação` e `retomar checkpoint`. `/clear` é tratado
pelo TUI e não precisa passar por `UserPromptSubmit`.

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Expected: PASS, incluindo ausência de loop.

- [ ] **Step 7: confirmar que nenhum conteúdo é persistido**

Abrir os JSON de estado e afirmar que não contêm `prompt`, `last_assistant_message`, `tool_input`,
`patient`, `message` ou conteúdo textual das fixtures.

- [ ] **Step 8: lint e commit**

Run: `python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py`  
Expected: exit `0`.

```bash
git add orq/scripts/context-guard.py orq/scripts/test_context_guard.py
git commit -m "feat: bloquear trabalho sem checkpoint antes do clear"
```

---

### Task 3: Empacotar hooks e validar referências

**Files:**
- Create: `orq/hooks/hooks.json`
- Modify: `orq/scripts/lint-coerencia.py`
- Modify: `orq/scripts/test_context_guard.py`

**Interfaces:**
- Consumes: CLI `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"`.
- Produces: seis grupos de hooks carregáveis por Codex.

- [ ] **Step 1: escrever teste RED do bundle**

O teste carrega `orq/hooks/hooks.json` e exige exatamente
`PostToolUse`, `Stop`, `UserPromptSubmit`, `SessionStart`, `PreCompact` e `PostCompact`.
Cada handler deve ser `type=command`, apontar para `context-guard.py`, ter timeout <=5 segundos e
`additionalContextLimit <= 300` apenas nos eventos que produzem contexto.

- [ ] **Step 2: executar RED e criar `hooks.json` mínimo**

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Expected: FAIL porque o bundle não existe; depois criar o JSON e obter GREEN.

- [ ] **Step 3: escrever teste RED para referência quebrada no lint**

Criar fixture temporária de plugin cujo hook cite
`${CLAUDE_PLUGIN_ROOT}/scripts/inexistente.py` e executar `lint-coerencia.py`; exigir exit não zero
e mensagem com o caminho ausente.

- [ ] **Step 4: estender `lint-coerencia.py`**

Analisar `hooks/hooks.json`, extrair caminhos sob `${CLAUDE_PLUGIN_ROOT}`/`${PLUGIN_ROOT}` e
validar arquivo dentro do pacote, JSON e tipos básicos dos handlers.

- [ ] **Step 5: rodar GREEN e validações**

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Run: `python3 orq/scripts/lint-coerencia.py .`  
Expected: ambos exit `0`.

- [ ] **Step 6: commit do bundle**

```bash
git add orq/hooks/hooks.json orq/scripts/lint-coerencia.py orq/scripts/test_context_guard.py
git commit -m "feat: empacotar guardiao de contexto nos hooks codex"
```

---

### Task 4: Integrar contrato natural e diagnóstico

**Files:**
- Modify: `orq/commands/checkpoint.md`
- Modify: `orq/commands/stack.md`
- Modify: `orq/commands/instalar.md`
- Modify: `orq/skills/orq/SKILL.md`
- Modify: `README.md`
- Modify: `memory/wiki/arquitetura.md`
- Modify: `memory/wiki/distribuicao.md`
- Modify: `memory/wiki/threads/T-043-protecao-contexto-codex.md`

**Interfaces:**
- Consumes: estados/mensagens do guardião.
- Produces: contrato único para 55/60/70, clear manual e backstop opt-in.

- [ ] **Step 1: escrever teste contratual RED**

Exigir as frases:
- `checkpoint.md`: `Seguro dar /clear` e `CLEAR_REQUIRED`;
- `stack.md`: `model_auto_compact_token_limit`, `90%`, `opt-in`;
- `instalar.md`: `/hooks` e confiança;
- `SKILL.md`: `55%`, `60%`, `70%` e `/clear`.

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Expected: FAIL nas frases ainda ausentes.

- [ ] **Step 2: atualizar checkpoint e skill**

Preservar o contrato atual, explicar handshake, substituir a heurística isolada de ~50% pela política
guard-aware e manter ~50% como fallback declarado para hosts sem telemetria.

- [ ] **Step 3: atualizar stack/instalação**

Diagnosticar feature hooks, bundle carregado, confiança em `/hooks`, `PLUGIN_DATA` gravável e
telemetria. Mostrar `round(model_context_window * 0.90)` — na janela efetiva atual, `997500 * 0.90 =
897750` — sem escrever config no diagnóstico.

- [ ] **Step 4: atualizar documentação viva e pública**

Documentar estados, limites do transcript, falha aberta, clear versus compact e separação de `T-042`.

- [ ] **Step 5: rodar GREEN e coerência**

Run: `python3 -m unittest orq/scripts/test_context_guard.py -v`  
Run: `python3 orq/scripts/lint-coerencia.py .`  
Expected: exit `0`.

- [ ] **Step 6: commit de contrato/docs**

```bash
git add orq/commands/checkpoint.md orq/commands/stack.md orq/commands/instalar.md \
  orq/skills/orq/SKILL.md README.md memory/wiki/arquitetura.md \
  memory/wiki/distribuicao.md memory/wiki/threads/T-043-protecao-contexto-codex.md
git commit -m "docs: definir checkpoint preventivo antes do clear"
```

---

### Task 5: Release local 0.22.0 e replanejamento do statusline

**Files:**
- Modify: `orq/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `memory/MEMORY.md`
- Modify: `memory/wiki/KANBAN.md`
- Modify: `docs/superpowers/plans/2026-08-09-statusline-nativa-codex.md`
- Modify: `memory/fixes-history.md`

**Interfaces:**
- Produces: pacote `0.22.0`; `T-042` replanejado para `0.23.0`.

- [ ] **Step 1: escrever teste RED de versão coordenada**

Exigir `0.22.0` nos quatro pontos obrigatórios e `0.23.0` no plano/card de statusline. Executar e
confirmar falha nas versões atuais.

- [ ] **Step 2: aplicar bump coordenado e log append-only**

Atualizar apenas pontos vivos e adicionar entrada no topo do log. `T-043` permanece em review.

- [ ] **Step 3: rodar suíte e validadores obrigatórios**

Run: `python3 -m unittest discover -s orq/scripts -p 'test_*.py' -v`  
Run: `claude plugin validate ./orq --strict`  
Run: `python3 orq/scripts/lint-coerencia.py .`  
Run: `git diff --check`  
Expected: todos exit `0`.

- [ ] **Step 4: commit da release local**

```bash
git add orq/.claude-plugin/plugin.json .claude-plugin/marketplace.json README.md \
  memory/MEMORY.md memory/wiki/KANBAN.md \
  docs/superpowers/plans/2026-08-09-statusline-nativa-codex.md memory/fixes-history.md
git commit -m "feat(0.22.0): proteger contexto antes do clear"
```

---

### Task 6: Instalação local e smoke comportamental

**Files:**
- Modify only if a defect is reproduced: files from Tasks 1–5 through a new RED test.
- Create outside repo and remove after test: temporary fixture project.

**Interfaces:**
- Consumes: pacote local `0.22.0`.
- Produces: cache idêntico e hooks carregados em sessão nova.

- [ ] **Step 1: reinstalar apenas no Codex local**

Run: `codex plugin add orq@orquestra`  
Expected: installed/enabled em `0.22.0`. Não atualizar Claude, publicar ou fazer push.

- [ ] **Step 2: comparar cache e fonte**

Run: `diff -rq <cache-codex-0.22.0> ./orq/`  
Expected: saída vazia.

- [ ] **Step 3: testar subprocesso com transcript sintético**

Executar cada evento por stdin com `PLUGIN_ROOT`, `PLUGIN_DATA` e transcript temporários. Confirmar
JSON, exit `0`, deduplicação e bloqueio após checkpoint seguro.

- [ ] **Step 4: iniciar sessão Codex descartável**

Em projeto temporário sem PII, confirmar hooks em `/hooks`, confiança, `SessionStart`, skill natural
e ausência de sucesso silencioso para hook inválido.

- [ ] **Step 5: corrigir somente defeitos reproduzidos por TDD**

Cada defeito ganha RED, correção mínima, suíte completa e commit.

---

### Task 7: Painel externo, verificação final e gate de implantação

**Files:**
- Modify: `memory/wiki/threads/T-043-protecao-contexto-codex.md`
- Modify: `memory/wiki/KANBAN.md`
- Modify only on finding: product/test file through TDD.

**Interfaces:**
- Produces: pareceres reais Opus 5 + Kimi K3, reconciliação e card em VALIDATE.

- [ ] **Step 1: preparar diff sanitizado e numerado**

Excluir PII/credencial e pedir achados concretos com severidade e arquivo:linha.

- [ ] **Step 2: executar Opus 5 real**

Usar `orq/scripts/run-opus-reviewer.py`; exigir `OPUS_STARTED`, exit `0` e
`OPUS_MODEL=claude-opus-5`.

- [ ] **Step 3: executar Kimi K3 real**

Usar Kimi não interativo com `kimi-code/k3`, sem `--yolo`/`--auto`.

- [ ] **Step 4: reconciliar e corrigir achados válidos por TDD**

Revisor não edita. Cada defeito concreto ganha RED antes da correção.

- [ ] **Step 5: executar verificação final fresca**

Run: `python3 -m unittest discover -s orq/scripts -p 'test_*.py' -v`  
Run: `python3 -m py_compile orq/scripts/context-guard.py`  
Run: `claude plugin validate ./orq --strict`  
Run: `python3 orq/scripts/lint-coerencia.py .`  
Run: `git diff --check`  
Run: `git status --short`  
Expected: zero falhas.

- [ ] **Step 6: mover para VALIDATE e listar gates restantes**

Registrar evidências, mover `T-043` para `[?]` e pedir gates separados para: config global 90%,
cache Claude, publicação/push e validação prática após `/clear` real.
