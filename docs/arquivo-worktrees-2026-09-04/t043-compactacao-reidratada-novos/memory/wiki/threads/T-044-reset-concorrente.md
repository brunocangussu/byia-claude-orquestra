# T-044 — Endurecer reset concorrente do guardião de contexto

## Estado

PLANO PRONTO. Investigação e reproduções concluídas em 2026-08-13; nenhuma implementação foi feita.
O card depende do gate explícito do dono antes de tocar em `orq/`, versão, cache ou Git.

## Objetivo

Fechar duas corridas residuais do `context-guard.py` sem mudar o contrato consultivo do Codex:

1. um evento anterior não pode apagar um pedido de reset criado depois por
   `SessionStart(source="clear")`;
2. a exclusão mútua precisa ser liberada pelo sistema operacional quando o processo morre tanto em
   macOS/Linux quanto em Windows, sem depender de `lockdir` órfão.

Não entram neste card: novos limiares, mudança da máquina de estados, bloqueio de hooks, backstop de
90%, alteração do fluxo Claude, push, publicação ou update do Claude.

## Evidência de base

- Fonte investigada: `orq/scripts/context-guard.py` e `orq/scripts/test_context_guard.py` no commit
  `bbcc4cb` do worktree `feat/t043-compactacao-reidratada`.
- Baseline executada com `PYTHONDONTWRITEBYTECODE=1 python3 orq/scripts/test_context_guard.py -q`:
  **65 testes, todos verdes**.
- O teste existente `test_clear_during_lock_contention_resets_before_next_prompt` cobre um lock
  segurado sem escritor anterior. Ele não cobre o escritor que persiste depois que o `.reset` nasce.
- O teste existente `test_process_exit_releases_state_lock_without_stale_reclamation` passa no host
  atual porque usa `fcntl`; ele reprova conceitualmente no ramo `lockdir` do Windows.

### Reprodução 1 — transação anterior apaga reset posterior

Interleaving reproduzida deterministicamente em diretório temporário:

1. A adquire o lock e conserva em memória um estado antigo `recovery_required=true`.
2. B recebe `SessionStart(clear)`, cria o marcador `.reset`, apaga o JSON fora do lock e espera.
3. A chama `_persist_response()`: recria o JSON antigo e, por `_finish_pending_reset()`, apaga o
   `.reset` que pertence a B.
4. B expira após 0,75 s e falha aberto.
5. O prompt seguinte não encontra marcador e volta a aconselhar recuperação com o estado antigo.

Resultado observado:

```json
{"clear_timed_out_fail_open": true, "next_prompt_repeats_recovery": true, "reset_marker_created": true, "reset_marker_erased_by_prior_transaction": true, "stale_recovery_survived": true}
```

**Causa raiz:** `_persist_response()` trata a mera existência do marcador como autorização para
confirmá-lo. A confirmação não está vinculada nem à geração do reset nem à transação que o observou
antes de carregar o estado. Além disso, `_mark_state_reset()` altera o JSON fora do lock que deveria
serializar o read-modify-write.

### Reprodução 2 — `lockdir` órfão

Um subprocesso foi forçado ao ramo `fcntl=None`, adquiriu o `lockdir` e terminou com `os._exit(0)`.
O diretório permaneceu; a aquisição seguinte esperou 0,76 s e retornou `None`.

```json
{"child_acquired_fallback": true, "next_acquire_failed": true, "orphan_lockdir_exists_after_exit": true, "wait_seconds": 0.76}
```

**Causa raiz:** a propriedade do fallback é apenas a existência de um diretório. O kernel não o
associa ao processo, portanto não existe liberação automática na morte e também não há protocolo de
lease/owner seguro para recuperá-lo.

## Impacto confirmado

Na `0.22.1`, o guardião Codex é consultivo e a allowlist impede respostas bloqueantes. As duas
corridas, portanto, erram para **over-enforcement recuperável**: repetição de alerta/checkpoint ou
telemetria permanentemente indisponível; não foi encontrado bypass de `decision=block`. Mesmo assim,
um reset posterior não pode ser reconhecido por uma transação anterior, e o caminho macOS/Linux não
pode regredir enquanto se corrige Windows.

## Invariantes obrigatórias

1. Toda leitura, exclusão e gravação do JSON de estado acontece sob o lock da sessão.
2. Um evento só remove pedidos de reset que já existiam quando ele entrou na seção crítica; pedido
   criado depois fica para a próxima transação.
3. Ausência do JSON equivale a `default_state()`. Depois que o JSON antigo foi removido sob lock, um
   crash antes do novo `save_state()` não ressuscita estado antigo.
4. Falha ao remover o JSON conserva o pedido de reset para retry; falha ao remover um marcador pode
   causar reset repetido, nunca falso reconhecimento do reset.
5. Marcadores não carregam prompt, transcript, caminho clínico, PII ou qualquer conteúdo de conversa.
6. Marcador fixo legado `<hash>.reset` da `0.22.1` continua reconhecido durante o upgrade.
7. macOS/Linux continuam usando `fcntl.flock(LOCK_EX|LOCK_NB)` no mesmo arquivo e no mesmo intervalo
   read → decide → write.
8. Windows usa lock de kernel de um byte por `msvcrt.locking(..., LK_NBLCK, 1)`, sempre com posição
   zero tanto no lock quanto no unlock.
9. Processo morto libera o lock de kernel pelo fechamento do descritor; não há stale-reclamation por
   PID, idade ou `rmdir` com janela TOCTOU.
10. Se nem `fcntl` nem `msvcrt` estiverem disponíveis, o hook retorna a falha aberta **visível** já
    existente e não cria um lock caseiro silenciosamente inseguro.
11. Nenhum ramo Codex introduz `decision=block`, `continue:false`, `stopReason`,
    `permissionDecision:deny` ou exigência de `/clear`.

## Desenho recomendado

### A. Reset por geração, consumido sob lock

Manter `_state_reset_path()` apenas como o caminho fixo legado. Cada novo
`_mark_state_reset()` cria, de forma exclusiva, um arquivo vazio com prefixo
`<hash>.reset.` no mesmo diretório; ele **não** apaga mais o JSON de estado.

Ao adquirir o lock, `_apply_pending_reset()`:

1. captura a lista exata formada pelo marcador legado e pelas gerações presentes naquele instante;
2. se a lista estiver vazia, não altera estado nem marcadores;
3. remove o JSON de estado sob o lock; se isso falhar, preserva todos os marcadores;
4. depois da remoção bem-sucedida, apaga somente a lista capturada.

Uma geração criada durante o passo 3 tem outro nome, não pertence ao snapshot e sobrevive. A
ausência do JSON já representa o reset durável, por isso `_persist_response()` deixa de chamar
`_finish_pending_reset()` e não confirma pedido algum por efeito colateral.

Interfaces internas alvo:

```python
def _state_reset_path(data_dir: Path, session_id: str) -> Path: ...  # legado
def _pending_state_reset_paths(data_dir: Path, session_id: str) -> list[Path]: ...
def _mark_state_reset(data_dir: Path, session_id: str) -> bool: ...
def _apply_pending_reset(data_dir: Path, session_id: str) -> bool: ...
```

Não usar PID como identidade da geração: PID é reutilizável. `tempfile.NamedTemporaryFile(...,
delete=False)` já produz nome exclusivo no diretório correto, sem dependência nova.

### B. Backend de lock por sistema operacional

Adicionar import condicional de `msvcrt` ao lado de `fcntl` e registrar o backend no próprio lock:

```python
@dataclass
class StateLock:
    path: Path
    handle: BinaryIO
    backend: str  # "fcntl" | "msvcrt"
```

`_acquire_state_lock()` tenta, nesta ordem:

1. `fcntl` quando disponível;
2. `msvcrt` quando disponível, com `handle.seek(0)` e `LK_NBLCK` sobre um byte;
3. `None` quando nenhum backend de kernel existe.

`_release_state_lock()` despacha `LOCK_UN` ou `LK_UNLCK`, volta à posição zero no Windows e fecha o
handle em `finally`. Remover completamente o ramo `.lockdir`; não implementar lease por timestamp,
PID ou remoção oportunista. A biblioteca padrão documenta que `msvcrt.locking` tranca a região a
partir da posição atual, inclusive além do fim do arquivo, portanto não é necessário gravar byte no
arquivo de lock.

## Plano executável — RED → GREEN

### Tarefa 1 — fechar a corrida do reset

**Arquivos:**

- Modificar: `orq/scripts/test_context_guard.py`
- Modificar: `orq/scripts/context-guard.py`

**RED:** acrescentar estes testes em `ContextGuardStateTest`/
`ContextGuardHookDecisionTest`:

- `test_prior_transaction_cannot_consume_newer_clear_reset`: usar `threading.Event` para confirmar que
  B criou o reset enquanto A ainda segura o lock; persistir o estado antigo por A; forçar timeout
  curto de B; liberar A; no prompt seguinte exigir `default_state()` e ausência de conselho de
  recuperação.
- `test_reset_created_during_apply_survives_for_next_transaction`: criar geração R1, capturar/aplicar
  R1, criar R2 durante a mesma seção crítica e provar que apenas R1 é removida; a chamada seguinte
  consome R2.
- `test_legacy_fixed_reset_marker_is_consumed`: criar manualmente `<hash>.reset`, manter JSON antigo e
  exigir reset normal + remoção do legado.

Executar:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  orq.scripts.test_context_guard.ContextGuardHookDecisionTest.test_prior_transaction_cannot_consume_newer_clear_reset \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_reset_created_during_apply_survives_for_next_transaction \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_legacy_fixed_reset_marker_is_consumed
```

Esperado antes da correção: pelo menos o primeiro teste falha porque A apaga o marcador de B; o
segundo falha porque não há gerações independentes.

**GREEN:** implementar a fila de gerações, mover a exclusão do JSON para
`_apply_pending_reset()` sob lock e retirar `_finish_pending_reset()` de `_persist_response()`.
Repetir exatamente o comando acima; esperado: 3 testes verdes.

### Tarefa 2 — substituir `lockdir` pelo lock de kernel do Windows

**Arquivos:**

- Modificar: `orq/scripts/test_context_guard.py`
- Modificar: `orq/scripts/context-guard.py`

**RED:** acrescentar:

- `test_msvcrt_backend_locks_and_unlocks_same_byte`: com `fcntl=None` e `msvcrt` fake, exigir
  `LK_NBLCK`/`LK_UNLCK`, um byte, posição zero e fechamento do handle;
- `test_missing_kernel_lock_backend_fails_open_without_lockdir`: com ambos os módulos ausentes,
  exigir `None` e inexistência de qualquer `.lockdir`.

Renomear o teste de morte de processo para descrever o contrato genérico do backend e preservá-lo
sem mock: ele prova `fcntl` neste host e provará `msvcrt` quando rodado em Windows.

Executar:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_msvcrt_backend_locks_and_unlocks_same_byte \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_missing_kernel_lock_backend_fails_open_without_lockdir \
  orq.scripts.test_context_guard.ContextGuardStateTest.test_process_exit_releases_state_lock
```

Esperado antes da correção: os dois testes novos falham; o teste de processo continua verde em
macOS/Linux.

**GREEN:** implementar o backend `msvcrt`, despachar o unlock pelo campo `backend` e excluir o ramo
`lockdir`. Repetir o comando; esperado: 3 testes verdes no host atual, com o primeiro exercitado por
fake e o terceiro por `fcntl` real.

### Tarefa 3 — regressão e documentação atemporal

**Arquivos de produto/documentação:**

- Modificar: `memory/wiki/arquitetura.md` — registrar reset geracional e locks de kernel por host;
- Modificar: `memory/wiki/distribuicao.md` — acrescentar o smoke de morte de processo por backend;
- Atualizar após o código final: `memory/wiki/threads/T-044-reset-concorrente.md` e append em
  `memory/fixes-history.md`;
- O Manager, não o implementer, move a linha do `T-044` em `memory/wiki/KANBAN.md`.

Não alterar `hooks/hooks.json`, comandos, skill nem contrato público: o evento e a resposta do hook
não mudam.

Rodar regressão completa:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 orq/scripts/test_context_guard.py -q
python3 -m py_compile orq/scripts/context-guard.py orq/scripts/test_context_guard.py
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
cmp -s AGENTS.md CLAUDE.md
git diff --check
test -z "$(find orq -type d -name __pycache__ -print -quit)"
```

Baseline: 65 testes. Com os cinco RED novos, esperado GREEN local: **70 testes** e nenhum
`__pycache__` no pacote.

### Tarefa 4 — release estreita e painel

Como `orq/` muda e o cache é indexado por versão, não reutilizar nem reescrever `0.22.1`. Criar uma
release local `0.22.2` em commit novo sobre `bbcc4cb`, atualizando juntos:

- `orq/.claude-plugin/plugin.json`;
- `.claude-plugin/marketplace.json`;
- seção `Status` do `README.md`;
- linha de versão de `memory/MEMORY.md`;
- constante esperada em `ContextGuardReleaseVersionTest`.

Depois dos gates locais, rodar painel read-only real conforme `_elenco.md`: Opus 5 + Kimi K3 em
clone/worktree descartável, briefing sem PII, reconciliação pelo Manager. Bloqueador devolve ao
implementer; não há retry automático de reviewer.

Não fazer amend de `bbcc4cb`, merge, push, publicação, update do Claude ou remoção do shim `0.22.0`
sem autorização separada.

### Tarefa 5 — validação de runtime

Após aprovação específica para instalação local, instalar `0.22.2` somente no Codex e exigir:

1. seis arquivos críticos byte-idênticos entre fonte e cache;
2. suíte do cache verde, excluindo apenas os testes repo-level já conhecidos;
3. reprodução da corrida do reset verde contra o arquivo instalado;
4. processo filho morto liberando `flock` no macOS/Linux;
5. processo filho morto liberando `msvcrt` em **Windows real**.

Sem o passo 5, é permitido integrar a correção POSIX e a seleção unitária de `msvcrt`, mas não
declarar comprovada a recuperação Windows nem fechar o card como validado.

## Riscos e contenções

- **Marcadores acumulados:** um reset sem evento posterior deixa arquivo vazio por desenho; a próxima
  transação limpa todas as gerações capturadas. O teste não aceita conteúdo nem nomes derivados de
  prompt.
- **Reset repetido após falha de cleanup:** é over-enforcement; preservar o marcador é mais seguro do
  que reconhecer reset que não conseguiu remover o estado antigo.
- **Regressão POSIX:** o ramo `fcntl` deve permanecer byte-equivalente em semântica e coberto pelo
  subprocesso real; nenhum fallback pode antecipá-lo.
- **Semântica do `msvcrt`:** lock/unlock dependem da posição atual; `seek(0)` é invariável testada,
  não detalhe implícito.
- **Plataforma exótica:** sem backend de kernel, falha aberta visível; não fingir serialização.
- **Upgrade com artefato antigo:** o marcador fixo `.reset` precisa ser consumido junto das novas
  gerações.
- **Concorrência com T-043:** não reescrever commit nem memória concorrente; antes de cada edição,
  reler o arquivo e manter um writer por arquivo.

## Gates

1. **Gate do dono:** aprovação explícita deste plano.
2. **Gate RED:** cinco testes novos falham pelas causas descritas, não por import/nome incorreto.
3. **Gate GREEN local:** 70 testes + `py_compile` + manifesto + lint + identidade AGENTS/CLAUDE +
   `diff --check` verdes.
4. **Gate de segurança:** busca no diff e testes confirmam zero campo bloqueante e zero conteúdo de
   conversa persistido.
5. **Gate de painel:** Opus 5 e Kimi K3 sem bloqueador, ou painel parcial declarado ao dono.
6. **Gate de cache:** versão `0.22.2`, fonte/cache idênticos e suíte de runtime verde.
7. **Gate Windows:** subprocesso real prova liberação após morte; sem isso, compatibilidade fica
   explicitamente não comprovada.
8. **Gate operacional:** nada de push/publicação/update do Claude sem autorização nova.

## Pergunta exata ao dono

**Posso implementar o `T-044` como um novo commit sobre `bbcc4cb`, em release local `0.22.2`, usando
reset por gerações e `msvcrt.locking` no Windows, sem push, publicação ou update do Claude?**

⏭️ RETOMAR AQUI

## Retomada de implementação e painel — 2026-08-14

O dono aprovou a implementação local, sem push, publicação, instalação no cache ou update do
Claude. A candidata `0.22.2` foi implementada no worktree sobre `bbcc4cb`:

- reset por gerações com marcador exclusivo e consumo apenas do snapshot capturado sob lock;
- `fcntl.flock` preservado em POSIX e `msvcrt.locking` adicionado para Windows;
- fallback consultivo quando criação, enumeração ou aplicação do reset falha;
- ausência de `decision:block` e preservação do fluxo Claude/limiares;
- coerência de versão em manifesto, marketplace, README e memória.

Três rodadas TDD responderam aos achados do painel:

1. retorno ignorado na criação/aplicação do reset — corrigido com saída consultiva sem persistência;
2. erro de enumeração confundido com lista vazia e clear perdido em `ENOSPC` — corrigidos com
   tri-state e fallback de unlink sob lock;
3. `Path.is_file()` ocultando erro de `stat` — substituído por `iterdir()` único sem stat por entrada.

Verificação independente após a terceira rodada: **75 testes**, `py_compile`, manifesto estrito,
lint de coerência, identidade AGENTS/CLAUDE, ausência de campos bloqueantes e `diff --check` verdes.
Kimi K3 devolveu `APROVADO`. Opus 5 real (`claude-opus-5`) retirou a objeção ao retry deliberado,
mas encontrou um bloqueador arquitetural novo e reproduzível: o early return de
`PreCompact`/`PostCompact` chama `_handle_event_unlocked()` antes do lock. Um compact concorrente
pode ler o JSON pré-clear, o clear remover JSON+marcador sob lock, e o compact gravar o estado antigo
de volta depois — falso reconhecimento do clear. Os docs confirmam que compact events recebem
`session_id`/`PLUGIN_DATA`; a isenção nasceu para garantir que nunca bloqueiem, mas não há teste de
concorrência compact×clear.

Após três correções, não empilhar uma quarta sem novo gate. Direção recomendada: serializar também
`PreCompact`/`PostCompact` pelo mesmo lock de sessão, mantendo timeout curto e resposta fail-open sem
campos bloqueantes; antes de editar, criar reprodução determinística do interleaving acima e provar
que os testes `test_precompact_auto_never_blocks` e
`test_postcompact_defers_rehydration_to_sessionstart` continuam verdes.

### Pergunta exata ao dono

**Você aprova ampliar o `T-044` para colocar `PreCompact`/`PostCompact` no mesmo lock de sessão,
com TDD da corrida compact×clear e preservação explícita de fail-open/zero bloqueio, antes de um novo
painel?**

Nada foi commitado, instalado ou publicado. O cache ativo continua `0.22.1`; o arquivo ausente que
causou loop no Stop hook foi restaurado byte a byte a partir de `bbcc4cb`.

⏭️ RETOMAR AQUI
