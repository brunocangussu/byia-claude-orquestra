# T-049 Cross-Host Installation Verifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verificar, por uma única implementação estrita, que o cache instalado contém exatamente o produto fonte, descontando somente metadados comprovados do host no lado instalado.

**Architecture:** Um comparador puro enumera arquivos, diretórios e links sem seguir symlinks e devolve divergências tipadas e ordenadas. Um CLI fino traduz o resultado para saída e exit status; lint, diagnóstico e instalador consomem esse mesmo contrato, eliminando `diff -rq` como gate de produto.

**Tech Stack:** Python 3.9+ standard library, `unittest`, Markdown, `claude plugin validate`.

**Spec:** `memory/wiki/threads/T-049-verificador-instalacao.md`

## Global Constraints

- A allowlist vale somente no lado `installed`; um caminho homônimo em `source` é divergência.
- Claude permite apenas `.in_use` no topo (arquivo legado ou diretório) e `.orphaned_at` no topo (arquivo regular), se a política recomendada for aprovada.
- Codex permite apenas o diretório exato `.codex-plugin/migrated-command-skills/` e seus descendentes.
- `.DS_Store` não é metadado nominal de host e deixa de ser exceção.
- Outros extras, ausências, mudanças de tipo, symlinks inesperados e byte drift falham.
- O verificador é executado a partir de uma fonte limpa; o cache nunca se autovalida.
- Nenhum cache real, hook, instalação, commit, push ou publicação muda sem o gate correspondente.
- A candidata de release é `0.22.7`, promovida após a colisão da 0.22.6 com a T-050 e aprovada pelo dono.

---

## File Map

- Create `orq/scripts/verify_installed_cache.py`: modelo de divergência, caminhada estrita, allowlists e CLI.
- Create `orq/scripts/test_verify_installed_cache.py`: matriz unitária cross-host e contrato de exit status.
- Modify `orq/scripts/lint-coerencia.py`: remover o comparador duplicado e consumir o módulo compartilhado para o cache Claude local.
- Modify `orq/scripts/test_context_guard.py`: manter apenas os testes de integração do `main()` do lint.
- Modify `orq/commands/instalar.md` and `orq/commands/stack.md`: substituir `diff -rq` pelo CLI executado da fonte.
- Modify `README.md`, `memory/wiki/distribuicao.md`, `memory/wiki/arquitetura.md`, `AGENTS.md`, and `CLAUDE.md`: documentar o contrato atual e preservar identidade byte a byte das instruções.
- Modify the five version anchors: `orq/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md`, `memory/MEMORY.md`, and `orq/scripts/test_context_guard.py`.

### Task 1: Comparador puro e matriz RED/GREEN

**Files:**
- Create: `orq/scripts/verify_installed_cache.py`
- Create: `orq/scripts/test_verify_installed_cache.py`

**Interfaces:**
- Produces: `Divergence(kind, path, detail)` and `find_installation_divergences(source: Path, installed: Path, host: Literal["claude", "codex"]) -> list[Divergence]`.
- Produces deterministic kinds: `missing`, `extra`, `type`, `bytes`.

- [x] **Step 1: Write the failing behavior matrix**

```python
class InstallationComparatorTests(unittest.TestCase):
    def test_claude_allows_only_installed_top_level_runtime_metadata(self): ...
    def test_codex_allows_only_exact_migrated_command_skills_subtree(self): ...
    def test_source_homonyms_are_never_ignored(self): ...
    def test_wrong_host_and_prefix_lookalikes_fail(self): ...
    def test_extra_missing_type_and_byte_drift_are_sorted(self): ...
    def test_allowed_metadata_does_not_hide_real_divergence(self): ...
    def test_symlinks_are_not_followed(self): ...
```

The fixtures must include: identical trees; Claude `.in_use` as file and directory/PID; Claude `.orphaned_at` as a top-level regular file; Codex exact migrated subtree; source `.in_use`; source `.codex-plugin`; `.DS_Store`; nested `.in_use`; `.in_use-x`; Codex metadata on Claude; Claude metadata on Codex; arbitrary `.codex-plugin/other`; empty extra directory; missing manifest; byte drift; file/directory/symlink mismatches; allowed metadata plus one real extra.

- [x] **Step 2: Run the dedicated suite and prove RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v orq.scripts.test_verify_installed_cache`

Expected: FAIL because `verify_installed_cache` or its public API does not exist.

- [x] **Step 3: Implement the minimal typed comparator**

```python
Host = Literal["claude", "codex"]
Kind = Literal["missing", "extra", "type", "bytes"]

@dataclass(frozen=True, order=True)
class Divergence:
    kind: Kind
    path: str
    detail: str = ""

def find_installation_divergences(
    source: Path,
    installed: Path,
    host: Host,
) -> list[Divergence]:
    """Compare entry types and file bytes without following symlinks."""
```

Walk with `os.scandir()`/`lstat()`, retain empty directories, compare symlink targets rather than following them, and prune only an installed entry that matches the host policy with the expected type. Sort by `(path, kind, detail)` before returning.

- [x] **Step 4: Run the dedicated suite and prove GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v orq.scripts.test_verify_installed_cache`

Expected: all comparator tests PASS.

### Task 2: CLI determinístico e erros operacionais

**Files:**
- Modify: `orq/scripts/verify_installed_cache.py`
- Modify: `orq/scripts/test_verify_installed_cache.py`

**Interfaces:**
- Produces: `main(argv: Sequence[str] | None = None) -> int`.
- Exit `0`: árvores normalizadas iguais; `1`: divergências de produto; `2`: host inválido, raiz ausente/ilegível ou erro de travessia.

- [x] **Step 1: Add failing CLI tests**

```python
def test_cli_returns_one_and_prints_sorted_divergences(self): ...
def test_cli_returns_two_for_missing_or_unreadable_root(self): ...
def test_cli_rejects_unknown_host(self): ...
def test_cli_returns_zero_for_each_host_with_only_allowed_metadata(self): ...
```

Expected output lines for product drift are `extra: path`, `missing: path`, `type: path (source=..., installed=...)`, or `bytes: path`; operational errors start with `error:` on stderr.

- [x] **Step 2: Run the focused CLI tests and prove RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v orq.scripts.test_verify_installed_cache.InstallationVerifierCliTests`

Expected: FAIL because `main()` and the parser are absent.

- [x] **Step 3: Implement the CLI**

```python
parser.add_argument("--host", required=True, choices=("claude", "codex"))
parser.add_argument("--source", required=True, type=Path)
parser.add_argument("--installed", required=True, type=Path)
```

Catch only expected filesystem/argument failures, print a stable diagnostic, and never downgrade an I/O failure to equality.

- [x] **Step 4: Run the whole dedicated suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v orq.scripts.test_verify_installed_cache`

Expected: PASS with both comparator and CLI contracts covered.

### Task 3: Single source of truth in lint, installer, and diagnosis

**Files:**
- Modify: `orq/scripts/lint-coerencia.py`
- Modify: `orq/scripts/test_context_guard.py`
- Modify: `orq/commands/instalar.md`
- Modify: `orq/commands/stack.md`

**Interfaces:**
- Consumes: `find_installation_divergences(..., host="claude")` in lint.
- Consumes: `verify_installed_cache.py --host <host> --source <clean-source>/orq --installed <cache>` in commands.

- [x] **Step 1: Move unit cases to the dedicated suite and add failing lint integration cases**

Keep `test_main_ignores_in_use_in_installed_cache` and `test_main_reports_real_extra_alongside_in_use`; add a top-level `.orphaned_at` pass and a `.DS_Store` failure. Remove direct tests of the old `find_cache_divergences` only after equivalent dedicated cases exist.

- [x] **Step 2: Run lint integration and prove RED for the new policy**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v orq.scripts.test_context_guard.LintCoerenciaTests`

Expected: `.DS_Store` remains incorrectly ignored before integration.

- [x] **Step 3: Replace the duplicate helper and every raw cache gate**

Use the shared API in `lint-coerencia.py`. In `instalar.md` and `stack.md`, run the verifier from the resolved clean source, not from `~/.claude/...` or `~/.codex/...`; remove any second `diff -rq` requirement that could reintroduce false red.

- [x] **Step 4: Run focused and combined suites**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  orq.scripts.test_verify_installed_cache \
  orq.scripts.test_context_guard \
  orq.scripts.test_run_opus_reviewer
```

Expected: PASS; no test relies on the removed duplicate comparator.

### Task 4: Living documentation, version 0.22.7, and pre-release gates

**Files:**
- Modify: `README.md`
- Modify: `memory/wiki/distribuicao.md`
- Modify: `memory/wiki/arquitetura.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `orq/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `memory/MEMORY.md`
- Modify: `orq/scripts/test_context_guard.py`

**Interfaces:**
- Preserves: `cmp -s AGENTS.md CLAUDE.md`.
- Produces: version `0.22.7` in all five anchors.

- [x] **Step 1: Replace documentation that promises a literally empty `diff -rq`**

Document equality after host normalization, the installed-only allowlist, exit statuses, the clean-source requirement, and the distinction between Claude, Codex, and Kimi selective-copy validation.

- [x] **Step 2: Update AGENTS and CLAUDE from one identical patch**

State that installed-cache verification uses the shared CLI and must not add ad-hoc exclusions. Verify immediately with `cmp -s AGENTS.md CLAUDE.md`.

- [x] **Step 3: Bump exactly the five version anchors to 0.22.7**

Do not rewrite historical occurrences of `0.22.5`; change only the active manifest, marketplace entry, README current-version line, MEMORY current-version line, and the lint version-coherence test fixture.

- [x] **Step 4: Run all pre-release gates**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  orq.scripts.test_verify_installed_cache \
  orq.scripts.test_context_guard \
  orq.scripts.test_run_opus_reviewer
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
cmp -s AGENTS.md CLAUDE.md
git diff --check
```

Expected: every command exits `0`.

- [x] **Step 5: Stop for adversarial review and the local-commit gate**

Run the real Opus 5 and Kimi K3 reviewers read-only and isolated, reconcile every blocker, repeat the gates, then present the exact diff and proposed commit. Do not commit, install, push, publish, or restart before the owner authorizes the corresponding gate.

Completion note (2026-08-30): Opus 5 real emitted GO after its blockers were reproduced and fixed.
Two isolated Kimi calls were attempted, but both ended with `403 weekly usage limit` and no verdict.
The owner explicitly authorized proceeding without Kimi for T-049. The full 200-test and pre-release
gate set was repeated successfully; the work stops at the local-commit gate.

Reconciliation note (2026-08-30): T-050 published a different 0.22.6 first. The owner approved a
rebase onto `origin/main` and promotion of T-049 to 0.22.7. The combined tree preserved T-050 and
passed 201 tests plus all pre-release gates; push and installation remain separate gates.

Publication note (2026-08-30): the owner authorized a fast-forward push and product commit
`deabd4d` reached `origin/main`. Installation remains a separate gate and must use a detached clone
of the final remote SHA.

### Task 5: Post-release validation behind separate authorization

**Files:**
- No source edits unless a validated defect returns to the cycle.

- [ ] **Step 1: From a clean checkout, verify each newly installed cache**

```bash
python3 <clean-source>/orq/scripts/verify_installed_cache.py \
  --host claude --source <clean-source>/orq \
  --installed ~/.claude/plugins/cache/orquestra/orq/0.22.7
python3 <clean-source>/orq/scripts/verify_installed_cache.py \
  --host codex --source <clean-source>/orq \
  --installed ~/.codex/plugins/cache/orquestra/orq/0.22.7
```

Expected: exit `0` with only the nominal host metadata present. Also inject one unexpected extra into disposable cache copies and prove exit `1`; never inject into real caches.

- [ ] **Step 2: Validate Kimi with its selective-copy contract**

Compare the installed commands, scripts, skills, and agents against the clean source using the existing Kimi checks; do not claim a whole-bundle cache that Kimi does not have.

- [ ] **Step 3: Record evidence and await owner validation**

Update the thread, living distribution page, append-only log, memory index, and board with exact commands/results. Move to VALIDATE only after review and real smoke evidence; DONE remains the owner’s decision.

## Self-Review

- Spec coverage: cause root, asymmetric allowlists, strict negatives, one implementation, CLI, integrations, docs, versioning, review and post-release smoke are each mapped to a task.
- Placeholder scan: angle-bracket values occur only in commands intentionally executed after concrete source/cache resolution; no implementation step is deferred implicitly.
- Type consistency: the plan uses the same `Divergence` and `find_installation_divergences` signatures in tests, lint, CLI, and docs.
