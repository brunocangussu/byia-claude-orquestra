# Contexto Codex com Compactação Reidratada Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Manter o checkpoint obrigatório do Orquestra no Codex, liberar compactação manual ou automática depois da verificação, reidratar a sessão compactada e preservar sem alteração o fluxo `/clear` do Claude.

**Architecture:** `context-guard.py` ganha estado v2 e um gate nativo de host Codex. O handshake Codex muda de `clear_required` para `checkpoint_verified`; `SessionStart(source="compact")` rearma a máquina e injeta reidratação, enquanto o comando compartilhado de checkpoint escolhe a frase final conforme o host. Estados 0.22.0 são migrados sem recriar o deadlock.

**Tech Stack:** Python 3 (`unittest`, `json`, `pathlib`), hooks JSON do Codex, Markdown de comandos/skills e validadores do plugin.

## Global Constraints

- Claude instalado permanece em `0.21.0`; nenhum `claude plugin update` nesta frente.
- Codex usa compactação nativa; o guardião nunca retorna `continue: false` em `PreCompact` ou `PostCompact`.
- O script só atua quando `PLUGIN_ROOT` nativo existe; ambiente somente `CLAUDE_*` sai `0` sem stdout nem estado.
- Nenhum prompt, mensagem, tool output, PII ou dado de paciente entra no estado.
- Estado legado `clear_required=true` migra para `checkpoint_verified=true`, sem bloqueio.
- O contrato Claude continua terminando em **Seguro dar `/clear`.**.
- O contrato Codex termina em **Checkpoint verificado; compactação liberada.**.
- Release corretiva local: `0.22.1`; bump coordenado nos quatro lugares do projeto.
- `~/.codex/config.toml`, GitHub e publicação permanecem fora do escopo.
- Toda mudança de código segue RED → GREEN e roda o lint do projeto antes do commit.

---

## Estrutura de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `orq/scripts/context-guard.py` | estado v2, migração, gate Codex e decisões de compactação |
| `orq/scripts/test_context_guard.py` | regressões do App, estado legado, compactação e isolamento Claude |
| `orq/commands/checkpoint.md` | saída final por host e handshake verificável |
| `orq/skills/orq/SKILL.md` | roteamento natural Codex compactado vs. Claude limpo |
| `orq/commands/stack.md` | diagnóstico do estado/compactação Codex |
| `orq/commands/instalar.md` | smoke de host e não regressão Claude |
| `README.md` | status da 0.22.1 e contrato público |
| `memory/wiki/arquitetura.md` | arquitetura viva do guardião |
| `memory/wiki/distribuicao.md` | gates e matriz de release por host |
| `memory/MEMORY.md` | índice e versão atual |
| `memory/fixes-history.md` | registro append-only do conserto |
| `memory/wiki/threads/T-043-protecao-contexto-codex.md` | evidências e handoff da frente |
| `memory/wiki/KANBAN.md` | transição do card |
| `orq/.claude-plugin/plugin.json` | versão do pacote |
| `.claude-plugin/marketplace.json` | versão do marketplace |

---

### Task 1: Estado v2 e isolamento Codex

**Files:**
- Modify: `orq/scripts/test_context_guard.py`
- Modify: `orq/scripts/context-guard.py`

**Interfaces:**
- Consumes: `default_state() -> dict`, `load_state(data_dir: Path, session_id: str) -> dict`, `handle_event(event: dict, env: Mapping[str, str]) -> dict | None`.
- Produces: estado `state_version=2`, booleanos `checkpoint_verified`/`recovery_required` e migração de `clear_required` legado.

- [ ] **Step 1: escrever testes RED do gate de host**

Substituir o teste que aceita ambiente apenas Claude por:

```python
def test_claude_only_plugin_environment_is_ignored(self) -> None:
    env = {
        "CLAUDE_PLUGIN_ROOT": self.env["PLUGIN_ROOT"],
        "CLAUDE_PLUGIN_DATA": self.env["PLUGIN_DATA"],
    }
    result = guard.handle_event(self.event("Stop", 60.0), env)
    self.assertIsNone(result)
    self.assertFalse(any(self.data_dir.rglob("*.json")))

def test_codex_native_plugin_environment_still_runs(self) -> None:
    result = guard.handle_event(self.event("Stop", 60.0), self.env)
    self.assertEqual(result["decision"], "block")
```

- [ ] **Step 2: escrever teste RED do estado v2**

```python
def test_default_state_uses_version_two_checkpoint_fields(self) -> None:
    state = guard.default_state()
    self.assertEqual(state["state_version"], 2)
    self.assertFalse(state["checkpoint_verified"])
    self.assertFalse(state["recovery_required"])
    self.assertNotIn("clear_required", state)
```

- [ ] **Step 3: escrever teste RED da migração 0.22.0**

Gravar no caminho real de estado um JSON v1 válido com `phase="clear_required"` e
`clear_required=true`; exigir que `load_state()` devolva `state_version=2`,
`phase="checkpoint_verified"`, `checkpoint_verified=true` e nenhuma chave `clear_required`.

- [ ] **Step 4: executar os testes focados e confirmar RED**

Run:

```bash
python3 -m unittest \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_claude_only_plugin_environment_is_ignored \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_default_state_uses_version_two_checkpoint_fields \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_legacy_clear_required_migrates_to_checkpoint_verified
```

Expected: FAIL porque o ambiente Claude ainda é aceito e o estado v2 não existe.

- [ ] **Step 5: implementar gate e migração mínimos**

- `handle_event()` e `_handle_event_unlocked()` exigem `env.get("PLUGIN_ROOT")` antes de qualquer fallback.
- `_plugin_env()` continua resolvendo aliases somente depois desse gate.
- `default_state()` retorna as oito chaves v2.
- a validação aceita um estado v1 estrito e o converte para v2; formas inválidas continuam no fluxo de corrupção atual.

- [ ] **Step 6: executar GREEN e regressão completa**

Run:

```bash
python3 -m unittest orq/scripts/test_context_guard.py
python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py
python3 orq/scripts/lint-coerencia.py .
```

Expected: todos os testes ajustados passam, compilação e lint saem `0`.

- [ ] **Step 7: commit do estado v2**

```bash
git add orq/scripts/context-guard.py orq/scripts/test_context_guard.py
git commit -m "fix: isolar guardiao codex e migrar estado"
```

---

### Task 2: Handshake Codex e compactação reidratada

**Files:**
- Modify: `orq/scripts/test_context_guard.py`
- Modify: `orq/scripts/context-guard.py`

**Interfaces:**
- Consumes: estado v2 da Task 1 e `read_latest_usage()` existente.
- Produces: handshake `checkpoint_verified`, `SessionStart(compact)` bifurcado e compactação sempre permitida.

- [ ] **Step 1: escrever teste RED do bug real do App**

```python
def test_verified_checkpoint_allows_next_prompt_in_codex_app(self) -> None:
    guard.handle_event(
        self.event(
            "Stop",
            67.1,
            last_assistant_message="Checkpoint verificado; compactação liberada.",
        ),
        self.env,
    )
    result = guard.handle_event(
        self.event("UserPromptSubmit", 67.1, prompt="continue"), self.env
    )
    self.assertNotEqual((result or {}).get("decision"), "block")
```

- [ ] **Step 2: escrever RED da frase antiga sem deadlock**

Usar `last_assistant_message="**Seguro dar `/clear`.**"`; exigir estado
`checkpoint_verified=true` e prompt seguinte não bloqueado.

- [ ] **Step 3: escrever RED da compactação verificada**

```python
def test_compact_after_verified_checkpoint_rehydrates_and_resets(self) -> None:
    state = guard.default_state()
    state.update(phase="checkpoint_verified", checkpoint_verified=True)
    guard.save_state(self.data_dir, "session-a", state)
    result = guard.handle_event(
        self.event("SessionStart", 5.0, source="compact"), self.env
    )
    self.assertIn("memory/MEMORY.md", json.dumps(result, ensure_ascii=False))
    self.assertEqual(guard.load_state(self.data_dir, "session-a")["phase"], "normal")
```

- [ ] **Step 4: escrever RED da compactação sem checkpoint**

Exigir `phase="recovery_required"`, `recovery_required=true` e contexto contendo
`checkpoint de recuperação`.

- [ ] **Step 5: escrever RED de `PreCompact`/`PostCompact`**

- `PreCompact(trigger="auto")` nunca contém `continue: false` nem `decision=block`.
- `PostCompact(trigger="auto")` não contém `additionalContext`; a orientação longa pertence ao `SessionStart(compact)`.

- [ ] **Step 6: executar RED focado**

Run:

```bash
python3 -m unittest \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_verified_checkpoint_allows_next_prompt_in_codex_app \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_legacy_safe_clear_phrase_allows_next_prompt \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_compact_after_verified_checkpoint_rehydrates_and_resets \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_compact_without_checkpoint_requires_recovery \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_precompact_auto_never_blocks \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_postcompact_defers_rehydration_to_sessionstart
```

Expected: FAIL pelo comportamento `clear_required` atual e pelas mensagens de contingência.

- [ ] **Step 7: implementar a transição mínima**

- reconhecer a frase Codex nova e a frase legada ancorada;
- no sucesso, gravar `checkpoint_verified=true`, `checkpoint_started=false`, `phase="checkpoint_verified"`;
- em `UserPromptSubmit`, verificar `checkpoint_verified` antes das faixas e nunca bloquear nesse estado;
- `PreCompact` nunca bloquear;
- `PostCompact` retornar sem contexto duplicado;
- `SessionStart(compact)` carregar o estado anterior, escolher retomada normal ou recuperação e persistir o novo estado.

- [ ] **Step 8: executar GREEN e regressão completa**

Run:

```bash
python3 -m unittest orq/scripts/test_context_guard.py
python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py
python3 orq/scripts/lint-coerencia.py .
```

Expected: suite completa verde e nenhum erro de sintaxe/coerência.

- [ ] **Step 9: inspecionar o estado persistido**

Criar um estado em diretório temporário pelo teste CLI e exigir exatamente as oito chaves v2;
buscar `prompt|message|tool_input|patient|paciente|secret` e exigir zero ocorrências em valores.

- [ ] **Step 10: commit da compactação**

```bash
git add orq/scripts/context-guard.py orq/scripts/test_context_guard.py
git commit -m "fix: liberar compactacao apos checkpoint codex"
```

---

### Task 3: Contrato host-aware nas instruções

**Files:**
- Modify: `orq/scripts/test_context_guard.py`
- Modify: `orq/commands/checkpoint.md`
- Modify: `orq/skills/orq/SKILL.md`
- Modify: `orq/commands/stack.md`
- Modify: `orq/commands/instalar.md`

**Interfaces:**
- Consumes: frase Codex e comportamento de compactação da Task 2.
- Produces: formato final por host, diagnóstico e smoke coerentes.

- [ ] **Step 1: escrever RED do contrato documental**

O teste carrega os cinco arquivos e exige:

```python
required = {
    "commands/checkpoint.md": [
        "Checkpoint verificado; compactação liberada.",
        "Seguro dar `/clear`.",
        "Claude",
        "Codex",
    ],
    "skills/orq/SKILL.md": ["SessionStart(source=compact)", "Claude", "/clear"],
    "commands/stack.md": ["checkpoint_verified", "compact"],
    "commands/instalar.md": ["ambiente somente `CLAUDE_*`", "sem efeito"],
}
```

Também exigir ausência das frases vivas `execute /clear manualmente` e
`compactação detectada como contingência` no contrato Codex.

- [ ] **Step 2: executar RED**

Run:

```bash
python3 -m unittest \
  orq.scripts.test_context_guard.ContextGuardDocumentationContractTest
```

Expected: FAIL porque o contrato atual é `/clear` para todos.

- [ ] **Step 3: atualizar o checkpoint por host**

- manter todas as verificações atuais;
- no Claude, emitir a frase atual;
- no Codex, emitir a frase nova e informar que a compactação manual/automática está liberada;
- nunca emitir as duas frases na mesma resposta;
- falha de verificação continua sem frase de sucesso.

- [ ] **Step 4: atualizar skill, stack e instalação**

- skill: 55/60/70 permanece, mas `checkpoint_verified` libera compactação no Codex;
- stack: reportar estado v2 e distinguir compactação reidratada de recuperação;
- instalar: smoke Codex e sonda negativa Claude-only.

- [ ] **Step 5: executar GREEN e gates locais**

Run:

```bash
python3 -m unittest orq/scripts/test_context_guard.py
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
git diff --check
```

Expected: todos saem `0`.

- [ ] **Step 6: commit do contrato**

```bash
git add orq/commands/checkpoint.md orq/commands/stack.md orq/commands/instalar.md \
  orq/skills/orq/SKILL.md orq/scripts/test_context_guard.py
git commit -m "docs: separar checkpoint do codex e do claude"
```

---

### Task 4: Documentação viva e release 0.22.1

**Files:**
- Modify: `README.md`
- Modify: `memory/wiki/arquitetura.md`
- Modify: `memory/wiki/distribuicao.md`
- Modify: `memory/MEMORY.md`
- Modify: `memory/fixes-history.md`
- Modify: `memory/wiki/threads/T-043-protecao-contexto-codex.md`
- Modify: `orq/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: estado e contratos finais das Tasks 1–3.
- Produces: pacote `0.22.1` coerente nos quatro lugares e runbook de dois hosts.

- [ ] **Step 1: atualizar a arquitetura viva**

Substituir `CLEAR_REQUIRED` por `CHECKPOINT_VERIFIED`, documentar migração v1→v2, compactação
segura e isolamento de host.

- [ ] **Step 2: atualizar distribuição e README**

Registrar matriz de verificação:

| Superfície | Critério |
|---|---|
| Codex fonte | testes + validate + lint |
| Codex cache | diff normalizado + estado v2 |
| Codex comportamento | checkpoint → prompt permitido → compact → reidratação |
| Claude cache | permanece 0.21.0 |
| Claude comportamento | ambiente somente `CLAUDE_*` sem stdout/estado |

- [ ] **Step 3: registrar log, thread e índice**

- entrada append-only no topo de `fixes-history.md` com causa raiz e correção;
- thread com evidências RED/GREEN e próximo gate;
- `memory/MEMORY.md` com versão `0.22.1` e estado real, removendo o resumo obsoleto de `/clear` Codex.

- [ ] **Step 4: bump coordenado**

Atualizar para `0.22.1`:

- `orq/.claude-plugin/plugin.json`;
- `.claude-plugin/marketplace.json`;
- seção Status do `README.md`;
- cabeçalho de `memory/MEMORY.md`.

- [ ] **Step 5: rodar gates do pacote**

Run:

```bash
python3 -m unittest orq/scripts/test_context_guard.py
python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
git diff --check
```

Expected: todos saem `0`.

- [ ] **Step 6: commit da release candidata**

```bash
git add README.md .claude-plugin/marketplace.json orq/.claude-plugin/plugin.json \
  memory/MEMORY.md memory/fixes-history.md memory/wiki/arquitetura.md \
  memory/wiki/distribuicao.md memory/wiki/threads/T-043-protecao-contexto-codex.md
git commit -m "feat(0.22.1): reidratar contexto compactado no codex"
```

---

### Task 5: Painel Opus 5 + Kimi K3 e correções

**Files:**
- Review only first; modify only files named by confirmed findings from Tasks 1–4.

**Interfaces:**
- Consumes: diff completo desde `1057b3c` e esta especificação.
- Produces: dois pareceres independentes com modelo/exit comprovados e reconciliação do Manager.

- [ ] **Step 1: gerar briefing sanitizado**

Incluir objetivo, critérios 1–9, diff de código/instruções e saídas dos gates. Excluir qualquer
dado de paciente, credencial, transcript ou caminho de prontuário.

- [ ] **Step 2: executar Opus 5 real**

Run:

```bash
{
  printf '%s\n' \
    'Revisão read-only do T-043. Produto: instruções + guardião Python.' \
    'Verifique os 9 critérios da especificação, ambiguidades entre hosts,' \
    'deadlocks, migração de estado e testes que não provam o que afirmam.'
  git diff --no-ext-diff --unified=40 1057b3c..HEAD -- \
    orq docs/superpowers/specs/2026-08-09-protecao-contexto-codex-design.md
} | python3 orq/scripts/run-opus-reviewer.py
```

Expected: exit `0`, linha `OPUS_MODEL=claude-opus-5` e parecer não vazio.

- [ ] **Step 3: executar Kimi K3 real**

Run:

```bash
KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")
KIMI_REVIEW_DIR=$(mktemp -d /tmp/orq-t043-kimi.XXXXXX)
git clone --no-local . "$KIMI_REVIEW_DIR/repo"
git -C "$KIMI_REVIEW_DIR/repo" checkout "$(git rev-parse HEAD)"
cd "$KIMI_REVIEW_DIR/repo"
"$KIMI" -m kimi-code/k3 --output-format text -p \
  'Revisão read-only do T-043. Compare 1057b3c..HEAD. Verifique os 9 critérios da especificação, deadlocks, isolamento Codex/Claude, migração de estado e cobertura real dos testes. Não edite arquivos. Retorne achados com severidade, arquivo:linha, cenário concreto e veredito.' \
  < /dev/null
```

Expected: exit `0`, parecer não vazio e clone descartável sem alterações; nunca usar `--yolo` ou
`--auto`. O diretório temporário é reportado e removido somente depois de confirmar seu caminho
explícito e que ele está sob `/tmp/orq-t043-kimi.`.

- [ ] **Step 4: reconciliar os pareceres**

Classificar cada achado como confirmado, não reproduzido ou opinião de estilo. Todo bloqueador
confirmado volta ao implementador; nenhum revisor edita arquivos.

- [ ] **Step 5: aplicar achados confirmados com novo RED/GREEN**

Para cada defeito comportamental, escrever teste que falha no commit candidato, aplicar a correção
mínima e rodar suite + gates completos.

- [ ] **Step 6: registrar e commitar a rodada de review**

Atualizar a thread com modelo, exit, resultado e reconciliação; commitar correções e registro com
assunto `fix: aplicar achados do painel da 0.22.1`.

---

### Task 6: Integração, instalação local e auditoria final

**Files:**
- Modify after evidence: `memory/wiki/KANBAN.md`
- Modify after evidence: `memory/wiki/threads/T-043-protecao-contexto-codex.md`

**Interfaces:**
- Consumes: branch revisada, pacote 0.22.1 e marketplace local existente.
- Produces: `main` integrada, Codex local atualizado, Claude preservado e T-043 em VALIDATE.

- [ ] **Step 1: rodar verificação final no worktree**

Run:

```bash
python3 -m unittest orq/scripts/test_context_guard.py
python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
git diff --check
git status --short
```

Expected: testes/gates verdes e worktree limpo.

- [ ] **Step 2: integrar na `main` sem push**

Fazer merge não interativo da branch revisada. Confirmar que somente os commits do T-043 entram e
que as mudanças paralelas da `main` permanecem.

- [ ] **Step 3: confirmar marketplace-fonte local**

Run:

```bash
codex plugin list
```

Expected: marketplace `orquestra` aponta para este repositório local.

- [ ] **Step 4: reinstalar apenas o Codex**

Run:

```bash
codex plugin add orq@orquestra
```

Não executar `claude plugin update`.

- [ ] **Step 5: comparar cache Codex com a fonte**

Comparar o cache `0.22.1` normalizando apenas metadados que o migrador Codex cria/remove. Qualquer
diferença em `scripts/`, `commands/`, `skills/` ou `hooks/` reprova a instalação.

- [ ] **Step 6: smoke direto do cache**

Executar o script instalado com fixtures temporárias e provar a sequência:

```text
Stop 60% -> decision=block para checkpoint
Stop com handshake -> checkpoint_verified=true
UserPromptSubmit 67.1% -> sem decision=block
PreCompact auto -> sem continue=false
PostCompact auto -> sem contexto duplicado
SessionStart compact -> reidrata e volta a normal
```

- [ ] **Step 7: smoke negativo Claude**

Executar o mesmo script com somente `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`; exigir exit `0`, stdout
vazio e diretório de estado ausente. Confirmar `claude plugin list` ainda em `orq 0.21.0`.

- [ ] **Step 8: pedir smoke de interface em chat novo do Codex App**

O dono abre chat novo no mesmo projeto e valida que, depois do checkpoint, `continue` não é
bloqueado e uma compactação reidrata a memória. Esse é o único critério que o Manager não pode
autovalidar sem viés da interface.

- [ ] **Step 9: mover T-043 para VALIDATE**

Somente depois dos Steps 1–7: atualizar board/thread com evidências mecânicas e deixar explícito o
teste de interface do Step 8. Não marcar DONE antes da confirmação do dono.

- [ ] **Step 10: auditoria requisito por requisito**

Reabrir os nove critérios da especificação e apontar uma evidência atual para cada um. Evidência
ausente mantém o card em DEV_REVIEW; não extrapolar de teste unitário para comportamento do App.
