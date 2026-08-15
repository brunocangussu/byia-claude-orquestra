# Orquestra SuperMemory Retirement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retirar todas as dependências e recomendações ativas do SuperMemory da Orquestra sem reescrever o histórico e sem publicar uma versão conflitante com `T-043`.

**Architecture:** O produto passa a depender somente da wiki por projeto e de mecanismos opcionais explicitamente disponíveis no host. A skill é validada por cenários de pressão antes/depois; manifesto, lint e inspeção mecânica validam o pacote. O release e a limpeza global permanecem gates posteriores à revisão da fonte.

**Tech Stack:** Markdown, Python 3 `unittest`, plugin Claude/Codex, Git worktree.

**Spec:** `docs/superpowers/specs/2026-08-15-bruno-brain-memory-architecture.md`

## Global Constraints

- Obsidian continua como interface; Dropbox continua como sincronização na primeira fase.
- SuperMemory deixa de ser dependência, recomendação ou fallback da Orquestra, Codex e Claude.
- Dados históricos são append-only; menções antigas permanecem intactas e contextualizadas.
- Não fazer bump, publicar, atualizar cache global, alterar o Claude ou fazer push antes do gate de release.
- `T-043` mantém seus próprios gates e não pode ser contornado por esta frente.
- Em host sem memória adicional, a busca degrada explicitamente para a wiki local.

---

### Task 1: Baseline comportamental da skill atual

**Files:**
- Verify: `orq/skills/orq/SKILL.md`
- Verify: `orq/commands/lembrar.md`
- Verify: `orq/commands/checkpoint.md`
- Verify: `orq/commands/stack.md`
- Verify: `orq/stack.md`
- Modify: `memory/wiki/threads/T-037-sem-supermemory.md`

**Interfaces:**
- Consumes: skill e comandos antes da remoção.
- Produces: três falhas observadas e registradas para repetir depois da edição.

- [x] **Step 1: Executar três cenários isolados sem a mudança**

Usar contextos novos e read-only:

- “lembra quando decidimos...” em host sem MCP externo;
- “faz checkpoint e termina rápido” em host sem MCP externo;
- “qual ferramenta instalar para memória entre projetos?” em projeto pequeno e multi-repo.

- [x] **Step 2: Confirmar as três falhas de baseline**

Expected:

- “lembra...” tenta `sm-search.py` e orienta configuração Claude-cêntrica;
- checkpoint ainda reserva uma etapa para o fornecedor, mesmo quando a pula;
- stack recomenda nominalmente o fornecedor para o perfil multi-projeto.

- [x] **Step 3: Registrar os resultados na thread do T-037**

Acrescentar `## Baseline comportamental — 2026-08-15` com as três observações acima e declarar que
os mesmos cenários serão repetidos depois da edição.

### Task 2: Remover a integração ativa do produto

**Files:**
- Delete: `orq/commands/lembrar.md`
- Delete: `orq/scripts/sm-search.py`
- Modify: `orq/commands/checkpoint.md`
- Modify: `orq/commands/ajuda.md`
- Modify: `orq/commands/stack.md`
- Modify: `orq/skills/orq/SKILL.md`
- Modify: `orq/stack.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: gatilhos naturais da skill e wiki local do projeto.
- Produces: produto sem provider externo obrigatório; “lembra quando...” busca wiki e usa apenas memória adicional realmente disponível no host.

- [x] **Step 1: Deletar os dois entrypoints específicos do fornecedor**

Run: `git rm orq/commands/lembrar.md orq/scripts/sm-search.py`

Expected: ambos aparecem como `D` em `git status --short`.

- [x] **Step 2: Remover a gravação externa do checkpoint**

Em `orq/commands/checkpoint.md`, excluir a seção `## 4. Supermemory`, renumerar as seções seguintes
para `## 4. Verificar ANTES de afirmar "seguro limpar"` e `## 5. Responder`, e corrigir referências
internas de `passo 6` para `passo 5` e de `passo 5` para `passo 4` onde se referem à verificação.

Run: `rg -n "passo [0-9]|^## [0-9]" orq/commands/checkpoint.md`

Expected: somente passos/seções `1`, `2b`, `4` e `5` válidos; nenhuma seção do fornecedor.

- [x] **Step 3: Preservar a intenção de busca sem comando dedicado**

Em `orq/skills/orq/SKILL.md`, substituir o gatilho do comando removido por:

```markdown
| "lembra quando a gente…?" · "o que a gente decidiu sobre…?" | **Busca a memória disponível**: wiki do projeto primeiro; depois, somente se o host expuser uma busca de memória confiável, consulte-a. Se não houver, declare que a cobertura ficou limitada à wiki |
```

Na ordem de ferramentas, fundir decisão antiga e sessões passadas em um item provider-neutral:

```markdown
3. **Contexto de sessões passadas e decisão antiga** → wiki do projeto + memória local/confiável realmente disponível no host.
4. **Estado real** (banco, deploy) → MCP do serviço, sempre leitura primeiro.
```

Em `orq/commands/ajuda.md`, substituir a referência a `/orq:lembrar` por “busca na wiki e na memória
confiável disponível no host”.

- [x] **Step 4: Retirar o fornecedor do catálogo e da documentação pública**

Em `orq/stack.md`, remover a subseção específica, o exemplo “mínimo + Supermemory” e o perfil
“Multi-projeto”. Em `orq/commands/stack.md`, remover o filtro específico. Em `README.md`, retirar o
fornecedor da detecção, da tabela de memória e remover a linha do comando `/orq:lembrar`.

- [x] **Step 5: Repetir os três cenários com a skill editada**

Expected: “lembra...” começa pela wiki e não tenta provider ausente; checkpoint não reserva etapa
externa; stack não recomenda o fornecedor. Registrar os resultados na thread do card.

- [x] **Step 6: Executar a suíte existente**

Run: `python3 -m unittest orq.scripts.test_run_opus_reviewer orq.scripts.test_context_guard`

Expected: `Ran 63 tests` e `OK`.

- [x] **Step 7: Commitar a remoção do produto**

```bash
git add README.md orq
git commit -m "refactor: remove SuperMemory from Orquestra"
```

### Task 3: Atualizar somente a wiki viva e o estado do card

**Files:**
- Modify: `memory/wiki/_stack.md`
- Modify: `memory/wiki/distribuicao.md`
- Modify: `memory/wiki/KANBAN.md`
- Modify: `memory/wiki/threads/T-037-sem-supermemory.md`
- Modify: `memory/MEMORY.md`

**Interfaces:**
- Consumes: decisões aprovadas em 2026-08-07 e reconfirmadas em 2026-08-15.
- Produces: estado retomável do `T-037`, sem reescrever história append-only.

- [x] **Step 1: Marcar o fornecedor como dispensado**

Mover a entrada ativa de `memory/wiki/_stack.md` para “Dispensadas (não repropor)” com data
`2026-08-15` e motivo “conexão/autenticação recorrente; retirado por decisão do dono no T-037”.

- [x] **Step 2: Corrigir a árvore de distribuição**

Remover `sm-search.py` da linha de scripts em `memory/wiki/distribuicao.md`.

- [x] **Step 3: Registrar a implementação sem alterar histórico antigo**

No `T-037` do KANBAN, substituir a pergunta já respondida por estado `IMPLEMENT` e registrar:
decisões 1–4 aprovadas; remoção executada na branch `feat/t037-sem-supermemory`; release, caches
globais e limpeza da máquina continuam em gate separado. Na thread do card, acrescentar seção
`## Atualização 2026-08-15` com a arquitetura aprovada e o vínculo para a especificação.

Em `memory/MEMORY.md`, acrescentar no trabalho atual uma linha curta apontando o card, branch e
próximo gate. Não editar as entradas históricas existentes.

- [x] **Step 4: Provar preservação do histórico**

Run:

```bash
git diff --exit-code -- memory/fixes-history.md memory/gotchas.md memory/wiki/threads/T-030-correcoes-painel.md
```

Expected: exit `0`, sem diff.

- [ ] **Step 5: Commitar a atualização de governança**

```bash
git add memory/MEMORY.md memory/wiki/KANBAN.md memory/wiki/_stack.md memory/wiki/distribuicao.md memory/wiki/threads/T-037-sem-supermemory.md docs/superpowers
git commit -m "docs: record provider-neutral memory architecture"
```

### Task 4: Validar a fonte antes de pedir review

**Files:**
- Verify: `orq/`
- Verify: `README.md`
- Verify: `memory/wiki/`

**Interfaces:**
- Consumes: Tasks 1–3 concluídas.
- Produces: evidência mecânica para o painel e para o gate de release.

- [ ] **Step 1: Rodar todos os testes locais relevantes**

Run:

```bash
python3 -m unittest orq.scripts.test_run_opus_reviewer orq.scripts.test_context_guard
```

Expected: `Ran 63 tests` e `OK`.

- [ ] **Step 2: Validar manifesto e coerência**

Run:

```bash
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
```

Expected: manifesto válido. Antes do bump, o único achado tolerável é a guarda que detecta versão
já instalada com conteúdo diferente; qualquer outro achado bloqueia o review.

- [ ] **Step 3: Confirmar ausência ativa e história preservada**

Run:

```bash
rg -ni "supermemory|sm-search|/orq:lembrar" orq README.md
test ! -f orq/commands/lembrar.md
test ! -f orq/scripts/sm-search.py
rg -ni "Supermemory" memory/wiki/_stack.md
```

Expected: o primeiro comando não retorna ocorrências; os dois `test` retornam `0`; `_stack.md`
contém somente a entrada de “Dispensadas”.

- [ ] **Step 4: Revisar diff e encaminhar ao gate**

Run: `git diff --check HEAD~2..HEAD && git status --short`

Expected: sem whitespace errors e worktree limpo. Solicitar review; não fazer bump, instalar,
publicar, atualizar cache global nem push.

### Task 5: Release e limpeza global após aprovação do review

**Files:**
- Modify after gate: `orq/.claude-plugin/plugin.json`
- Modify after gate: `.claude-plugin/marketplace.json`
- Modify after gate: `README.md`
- Modify after gate: `memory/MEMORY.md`
- External after gate: `~/.codex/AGENTS.md`
- External after gate: `~/.claude/CLAUDE.md`
- External after gate: `~/.agents/skills/orq/`
- External after gate: helpers e credencial legados do SuperMemory

**Interfaces:**
- Consumes: review aprovado, ordem de release compatível com `T-043` e autorização de publicação.
- Produces: mesma versão instalada em Codex e Claude, sem referências globais ativas.

- [ ] **Step 1: Parar no gate de release**

Apresentar ao dono: resultado dos 63 testes, validação do plugin, lint, review, diff e colisões de
versão. Não escolher versão nem publicar antes da resposta.

- [ ] **Step 2: Depois do gate, instalar a mesma versão nos dois clientes**

Executar o fluxo oficial da Orquestra para release/update e comparar fonte empacotada com cada
cache por `diff -rq`, excluindo somente metadados de instalação documentados.

- [ ] **Step 3: Limpar a configuração global com backup recuperável**

Remover as instruções ativas do fornecedor de `~/.codex/AGENTS.md` e `~/.claude/CLAUDE.md`.
Mover helpers e credencial legados para uma pasta de backup com timestamp; não apagar dados da
conta remota. Confirmar que as listas MCP ativas do Codex e Claude continuam sem o fornecedor.

- [ ] **Step 4: Smoke em sessões novas e aviso ao dono**

Validar no Codex e no Claude as frases “lembra quando decidimos...” e “faça um checkpoint”. Depois
de ambos passarem, comunicar exatamente: **“reabra esta thread agora para carregar a nova versão
da Orquestra”**.
