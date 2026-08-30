# T-048 Native Auditors Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task by task.

**Goal:** Entregar dois auditores offline e determinísticos — remoção e adoção graph-first — com o
mesmo núcleo para Claude Code, Codex e Kimi.

**Architecture:** Dois CLIs Python stdlib independentes compartilham somente contratos JSON. O
auditor de remoção produz e verifica um ledger persistente; o de adoção classifica um trace
fornecido. A skill roteia linguagem natural no Codex/Kimi e um command oferece a interface Claude.

**Tech Stack:** Python 3 stdlib (`argparse`, `json`, `pathlib`, `subprocess`, `unittest`), Markdown e
JSON Schema draft 2020-12.

**Limites do gate:** usar o worktree existente `codex/t046-auditores-nativos`; não alterar hooks nem
guardião; não instalar, publicar, commitar ou enviar ao GitHub sem autorização posterior.

---

### Task 1: Auditor de remoção — contrato RED e schema

**Files:**
- Create: `orq/scripts/test_audit_removal.py`
- Create: `orq/scripts/audit-removal.py`
- Create: `orq/schemas/audit-ledger-v1.json`

1. Escrever testes por subprocesso para scan com 13 âncoras, histórico retido, autocontaminação,
   remoção incompleta, âncora crítica ausente, recibo ausente/falho, remoção completa, Unicode e alvo
   com metacaracteres.
2. Rodar `python3 -m unittest orq/scripts/test_audit_removal.py -v` e confirmar falha RED por script
   ausente.
3. Implementar `target_variants(target)`, `scan_repository(...)`, `repository_state(...)`,
   `build_ledger(...)`, `assert_scope_matches(...)`, `verify_ledger(...)` e o parser `scan|verify`
   sem `shell=True`; o verify repete e confere o escopo externo ao ledger.
4. Definir o schema `orq.audit-removal.v1` com `target`, `repository`, `exclusions`,
   `criticalAnchors`, `requiredValidations`, `evidence`, `graphReceipts` e `verification`.
5. Rodar novamente o teste isolado até GREEN.

### Task 2: Auditor de adoção — contrato RED/GREEN

**Files:**
- Create: `orq/scripts/test_audit_adoption.py`
- Create: `orq/scripts/audit-adoption.py`

1. Escrever testes por subprocesso para traces graph-first, direct-first, busca textual antes do
   grafo, sem grafo, eventos irrelevantes, formato alternativo `data.item.command` e JSON inválido.
2. Rodar `python3 -m unittest orq/scripts/test_audit_adoption.py -v` e confirmar falha RED.
3. Implementar `event_fields(event)`, `classify_event(event)`, `audit_trace(payload)` e CLI JSON.
   As categorias são `graph`, `text-search`, `direct-read`, `mutation`, `unverified`, `other`; só
   procedência explícita de codebase-memory/Serena certifica grafo.
4. Rodar novamente o teste isolado até GREEN.

### Task 3: Interface cross-host, documentação e release candidata

**Files:**
- Create: `orq/commands/auditar.md`
- Modify: `orq/skills/orq/SKILL.md`
- Modify: `orq/commands/ajuda.md`
- Modify: `README.md`
- Modify: `orq/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `memory/MEMORY.md`

1. Documentar as frases “audite a remoção de X” e “verifique se esta sessão usou grafo primeiro”,
   parâmetros, exit codes, recibos e limites.
2. Adicionar a rota natural na skill e o command Claude sem sugerir que `/orq:*` existe no Codex.
3. Declarar explicitamente que os auditores não substituem descoberta atual nem revisão humana.
4. Coordenar a versão candidata `0.22.5` nos manifests, README e memória para o lint não aceitar um
   pacote semanticamente novo com versão antiga.

### Task 4: Gates completos e isolamento

**Files:**
- Verify only: `orq/hooks/hooks.json`
- Verify only: `orq/scripts/context-guard.py`

1. Rodar `python3 -m unittest discover -s orq/scripts -p 'test_*.py' -v`.
2. Rodar `python3 orq/scripts/lint-coerencia.py .`.
3. Rodar `claude plugin validate ./orq --strict`.
4. Comparar os dois arquivos proibidos contra `origin/main` e exigir diff vazio.
5. Inspecionar `git diff --check`, `git status --short` e o diff limitado da feature.
6. Registrar resultados no handoff da T-048, sem fechar/publicar/instalar antes do painel e do gate
   do dono.

## Execução atual

- [x] Auditor de remoção implementado e endurecido em TDD.
- [x] Auditor de adoção implementado e endurecido em TDD.
- [x] Interface cross-host, documentação e candidata 0.22.5 alinhadas.
- [x] 184 testes, Ruff, py_compile, lint, manifesto, schemas e isolamento passaram nos bytes finais.
- [x] Opus 5 retornou GO para adoção, scanner de remoção e ledger/verify.
- [x] Kimi K3 retornou GO para adoção e remoção nos bytes finais; o bloqueador de surrogate foi
  reproduzido, corrigido em TDD e revisado novamente.
- [x] Gate do dono para commit local.
- [ ] Gate separado do dono para instalação nos hosts.
- [ ] Gate separado do dono para push/publicação.
