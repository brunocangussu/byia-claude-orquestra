# Statusline Nativa do Codex Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Oferecer um perfil nativo e opt-in de statusline para usuários do Orquestra no Codex, preservando qualquer configuração existente e sem prometer renderização do board.

**Architecture:** O procedimento vive numa referência específica do host Codex, consumida por `init`, `stack` e pela skill. Ele descobre os itens aceitos pela versão instalada, mostra o merge proposto, cria backup e só escreve com autorização explícita. O `KANBAN.md` continua fora da statusline Codex enquanto o TUI não aceitar script arbitrário.

**Tech Stack:** Markdown de instruções, TOML (`~/.codex/config.toml`), Python 3 `tomllib`, Codex CLI `/statusline` e `doctor`, lint textual existente.

## Global Constraints

- Executar somente depois da release core `0.21.0` instalada no branch de implementação.
- Release alvo deste plano: `0.22.0`. Se a base não for `0.21.0`, parar e regenerar o plano.
- A statusline é opt-in; instalar o Orquestra não autoriza editar `~/.codex/config.toml`.
- Criar backup carimbado antes de qualquer escrita.
- Preservar campos, ordem e `status_line_use_colors` existentes.
- Consultar os identificadores aceitos pela versão Codex instalada; não gravar item desconhecido.
- `task-progress` é o plano da sessão Codex, não o board do Orquestra.
- Não instalar dependências, publicar, atualizar cache global nem fazer push sem autorização separada.

---

## File Structure

- Create `orq/skills/orq/references/hosts/codex.md`: contrato de interface, statusline e validação do host Codex.
- Modify `orq/skills/orq/SKILL.md`: apontar para a referência quando o assunto for Codex/statusline.
- Modify `orq/commands/init.md`: detectar e propor a configuração sem escrever implicitamente.
- Modify `orq/commands/stack.md`: diagnosticar statusline Codex separadamente da statusline Claude.
- Modify `orq/commands/instalar.md`: oferecer a etapa opcional depois do smoke, nunca durante instalação silenciosa.
- Modify `orq/scripts/lint-coerencia.py`: exigir backup, opt-in, preservação e limite “sem board” em quem grava `tui.status_line`.
- Modify `README.md`: documentar o perfil e seus limites.
- Modify `memory/wiki/arquitetura.md`: descrever a capacidade real atual.
- Modify `memory/wiki/distribuicao.md`: registrar validação e smoke.
- Modify `memory/MEMORY.md`, `memory/fixes-history.md`, manifests e board: release e handoff.

### Task 1: Referência de host e perfil suportado

**Files:**
- Create: `orq/skills/orq/references/hosts/codex.md`
- Modify: `orq/skills/orq/SKILL.md:60-85,300-317`

**Interfaces:**
- Consumes: versão do `codex`, `/statusline`, `~/.codex/config.toml`.
- Produces: lista recomendada filtrável e procedimento único para os consumidores.

- [ ] **Step 1: Executar probe RED da referência ausente**

```bash
python3 -c 'from pathlib import Path; p=Path("orq/skills/orq/references/hosts/codex.md"); assert p.exists(); s=p.read_text(); assert "task-progress não é o board" in s'
```

Expected: FAIL porque o arquivo não existe.

- [ ] **Step 2: Criar a referência Codex completa**

O arquivo deve conter este contrato, expandido com os comandos de validação abaixo:

```markdown
# Host Codex

## Interface

Use linguagem natural ou `/skills`. `/orq:*` pertence ao Claude Code.

## Statusline nativa

Perfil recomendado, condicionado à lista aceita pela versão instalada:
`model-with-reasoning`, `run-state`, `task-progress`, `context-used`,
`five-hour-limit`, `weekly-limit`, `current-dir`, `git-branch`,
`permissions`, `approval-mode`, `fast-mode`.

`task-progress` não é o board do Orquestra. O Codex não executa
`kanban-status.sh` na statusline; nunca prometa essa integração.

## Escrita segura

1. Leia `~/.codex/config.toml` e a configuração efetiva.
2. Consulte `/statusline` ou a referência da versão para os IDs aceitos.
3. Mostre a lista atual e o merge proposto.
4. Espere autorização explícita.
5. Crie backup carimbado.
6. Grave preservando todas as outras chaves TOML.
7. Valide com `tomllib` e `codex --strict-config doctor --json`.
8. Em falha, restaure o backup e informe a causa.
```

- [ ] **Step 3: Roteá-la pela skill**

Adicionar à skill:

```markdown
Quando o pedido envolver Codex, descoberta de `/orq`, modelos do host ou statusline nativa, leia `references/hosts/codex.md` antes de agir. A referência adapta o host; não replique suas regras aqui.
```

- [ ] **Step 4: Rodar probe GREEN**

Run o probe da Step 1.

Expected: exit `0`.

### Task 2: Fluxo opt-in no init, instalar e stack

**Files:**
- Modify: `orq/commands/init.md:14-79,116-170,583-698`
- Modify: `orq/commands/instalar.md:53-74,149-164`
- Modify: `orq/commands/stack.md:40-130`

**Interfaces:**
- Consumes: procedimento de `references/hosts/codex.md`.
- Produces: estados `ausente`, `padrão nativo`, `personalizada` e `inválida`, sem escrita automática.

- [ ] **Step 1: Executar probe RED de segurança**

```bash
python3 -c '
from pathlib import Path
j="\n".join(Path(f).read_text() for f in ["orq/commands/init.md","orq/commands/instalar.md","orq/commands/stack.md"])
for phrase in ["statusline Codex é opt-in", "backup carimbado", "task-progress não é o board", "codex --strict-config doctor --json"]:
 assert phrase in j, phrase
'
```

Expected: FAIL.

- [ ] **Step 2: Classificar o estado sem confundir Claude e Codex**

Adicionar aos três consumidores:

```markdown
Statusline do host Codex:
- AUSENTE: `[tui].status_line` não foi definido; o Codex usa defaults.
- NATIVA PADRÃO: contém somente os defaults conhecidos.
- PERSONALIZADA: contém seleção/ordem escolhida pelo usuário; preserve-a.
- INVÁLIDA: TOML não parseia ou o Codex rejeita IDs; não escreva antes de corrigir/restaurar.
```

- [ ] **Step 3: Tornar a proposta opt-in**

No `init`, a pergunta é separada da autorização geral:

```markdown
“Quer que eu proponha um merge não destrutivo da statusline nativa do Codex? Isso altera `~/.codex/config.toml`, não mostra o board do Orquestra e exige confirmação separada antes da escrita.”
```

No `instalar`, oferecer somente depois de plugin+skill+smoke aprovados. No `stack`, diagnosticar e sugerir uma única vez; não instalar sozinho.

- [ ] **Step 4: Fixar backup, merge e rollback**

Documentar comando de backup sem variável ampla:

```bash
cp "$HOME/.codex/config.toml" "$HOME/.codex/config.toml.bak-orq-statusline-YYYYMMDD-HHMMSS"
```

O implementador deve substituir o timestamp por `date +%Y%m%d-%H%M%S` somente no momento da execução, validar o caminho exato e nunca usar glob na restauração.

- [ ] **Step 5: Rodar probes GREEN**

Run o probe da Step 1.

Expected: exit `0`.

### Task 3: Guard de coerência e documentação

**Files:**
- Modify: `orq/scripts/lint-coerencia.py:61-278`
- Modify: `README.md:25-60,430-470`
- Modify: `memory/wiki/arquitetura.md`
- Modify: `memory/wiki/distribuicao.md`

**Interfaces:**
- Consumes: qualquer arquivo em `orq/` que grave ou proponha `status_line`.
- Produces: falha de lint quando faltar opt-in, backup, preservação ou limite do board.

- [ ] **Step 1: Adicionar fixture RED temporária para o lint**

Crie em `orq/commands/_probe-statusline-insegura.md`:

```markdown
# Codex statusline insegura

Grave `status_line = ["task-progress"]` em `~/.codex/config.toml`.
```

Run:

```bash
python3 orq/scripts/lint-coerencia.py .
```

Expected: inicialmente PASS, provando que o guard ainda não existe. Remova o probe somente depois da Step 3.

- [ ] **Step 2: Implementar o guard de statusline Codex**

Adicionar em `lint-coerencia.py`:

```python
GRAVA_CODEX_STATUS_RE = re.compile(r"(?:tui\.)?status_line\s*=|status_line\s*:")
REQUISITOS_CODEX_STATUS = (
    "opt-in",
    "backup",
    "preserv",
    "task-progress não é o board",
)
for arq in plugin.rglob("*.md"):
    txt = arq.read_text(encoding="utf-8")
    if GRAVA_CODEX_STATUS_RE.search(txt) and "Codex" in txt:
        faltando = [r for r in REQUISITOS_CODEX_STATUS if r.lower() not in txt.lower()]
        if faltando:
            problemas.append((arq.relative_to(raiz), 0, f"propõe statusline Codex sem requisitos {faltando}"))
```

- [ ] **Step 3: Verificar RED real e remover fixture**

Run `python3 orq/scripts/lint-coerencia.py .`.

Expected: FAIL apontando `_probe-statusline-insegura.md`. Depois remova somente esse arquivo e rode novamente; Expected: PASS.

- [ ] **Step 4: Documentar limites e recuperação**

README e arquitetura devem dizer explicitamente:

```markdown
A statusline do Codex é nativa e usa uma lista fechada de campos. Ela pode mostrar o progresso do plano da sessão, mas não executa o script do board do Orquestra. O perfil é opcional e qualquer configuração existente é preservada.
```

Distribuição deve exigir parse TOML, `doctor --strict-config` e nova sessão.

### Task 4: Versão, validação e commit local

**Files:**
- Modify: `orq/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `memory/MEMORY.md`
- Modify: `memory/fixes-history.md`
- Modify: `memory/wiki/KANBAN.md`
- Modify: `memory/wiki/threads/T-040-paridade-codex.md`

**Interfaces:**
- Consumes: Tasks 1-3 finalizadas.
- Produces: release local `0.22.0`, validada e parada antes de instalação/publicação.

- [ ] **Step 1: Atualizar os quatro locais de versão para `0.22.0`**

```text
orq/.claude-plugin/plugin.json
.claude-plugin/marketplace.json
README.md Status
memory/MEMORY.md
```

- [ ] **Step 2: Registrar histórico e handoff**

Adicionar entrada atemporal nas páginas vivas, entrada datada no topo de `fixes-history.md` e evidência/limitações na thread `T-040`.

- [ ] **Step 3: Executar validação completa**

```bash
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
git diff --check
python3 -c 'import json; assert json.load(open("orq/.claude-plugin/plugin.json"))["version"]=="0.22.0"; assert json.load(open(".claude-plugin/marketplace.json"))["plugins"][0]["version"]=="0.22.0"'
```

Expected: todos exit `0`.

- [ ] **Step 4: Criar commit local**

```bash
git add orq README.md .claude-plugin/marketplace.json memory/MEMORY.md memory/wiki/arquitetura.md memory/wiki/distribuicao.md memory/fixes-history.md memory/wiki/KANBAN.md memory/wiki/threads/T-040-paridade-codex.md
git commit -m "feat(0.22.0): statusline nativa do codex — perfil opt-in e seguro"
```

- [ ] **Step 5: Parar no gate de instalação**

Não editar `~/.codex/config.toml`, não atualizar plugin/cache e não publicar. Entregar o backup/merge proposto como próximo gate do dono.

## Plan Self-Review Checklist

- [ ] Cada escrita de statusline exige opt-in, backup, preservação e rollback.
- [ ] Nenhuma etapa promete o board na statusline do Codex.
- [ ] `task-progress` está identificado como plano da sessão.
- [ ] O plano não instala dependências nem toca config global durante a implementação.
- [ ] A release inclui os quatro bumps sincronizados.
