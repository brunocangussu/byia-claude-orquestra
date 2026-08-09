# Paridade Core do Codex Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer instalação, descoberta, diagnóstico e elenco do Orquestra funcionarem de forma verdadeira no Codex, sem duplicar o núcleo do Claude Code.

**Architecture:** A skill continua sendo o roteador universal e os arquivos em `commands/` continuam descrevendo as operações canônicas. O host é resolvido antes do papel; o template `_elenco.md` passa a conter a matriz e os times que os consumidores exigem. Diagnóstico e smoke distinguem instalação, habilitação, carregamento da skill e comportamento real.

**Tech Stack:** Markdown de instruções, Python 3 (`lint-coerencia.py`), manifests JSON, CLIs `codex`, `claude` e `kimi`, Git.

## Global Constraints

- Base obrigatória: commit `4d4813c`, plugin `0.20.0`. Se `main` avançar ou a versão mudar antes da execução, parar e regenerar os números deste plano.
- Release alvo deste plano: `0.21.0` nos quatro locais obrigatórios.
- Interface Codex: linguagem natural + `/skills`; `/orq:*` continua exclusivo do Claude Code.
- `/prompts:orq` é compatibilidade opcional e depreciada; nunca é escrito automaticamente.
- Manager Codex: `gpt-5.6-sol@high`; Planner: `gpt-5.6-sol@ultra`; Implementer: `gpt-5.6-terra@xhigh`; reviewers: Opus 5 + Kimi K3.
- Modelos/configuração real e elenco configurado são estados diferentes; nunca alegar execução sem evidência.
- Dados de paciente, PII, credenciais e prontuários não podem sair para modelos externos.
- Reviewer é read-only; Implementer é o único writer e trabalha em worktree dedicado.
- Não publicar, atualizar marketplace/cache global nem fazer push neste plano sem autorização separada do dono.
- **Correção de ordem descoberta na execução:** o guard de cache rejeita qualquer edição em `orq/` enquanto a versão publicada `0.20.0` continuar ativa. Por isso o bump sincronizado para `0.21.0` ocorre imediatamente após o primeiro GREEN de conteúdo, antes dos lints intermediários; a Task 4 apenas reconfirma os quatro locais.

---

## File Structure

- Modify `orq/commands/elenco.md`: gerar `_elenco.md` completo e migrar seções ausentes.
- Modify `orq/commands/init.md`: detectar memória legada, instalar o elenco completo e comunicar o host corretamente.
- Modify `orq/commands/plan-next.md`: resolver host → planner → mecanismo antes do despacho.
- Modify `orq/commands/implement-next.md`: resolver host → implementer → worktree/mecanismo.
- Modify `orq/commands/revisar.md`: montar Opus 5 + Kimi K3 no host Codex e nomear painel parcial.
- Modify `orq/skills/orq/SKILL.md`: declarar a interface oficial do Codex e a resolução por capacidade.
- Modify `orq/commands/instalar.md`: verificar plugin, skill e smoke como camadas separadas.
- Modify `orq/commands/stack.md`: diagnosticar as sete camadas sem falso “não instalado”.
- Modify `orq/scripts/lint-coerencia.py`: impedir regressão do template e promessas incorretas de slash command.
- Modify `README.md`: documentar ativação e troubleshooting por host.
- Modify `memory/wiki/arquitetura.md`: registrar a arquitetura final.
- Modify `memory/wiki/distribuicao.md`: registrar o smoke Codex e os gates de release.
- Modify `memory/MEMORY.md`: atualizar índice e versão corrente.
- Modify `memory/fixes-history.md`: registrar a mudança funcional.
- Modify `orq/.claude-plugin/plugin.json`: versão `0.21.0`.
- Modify `.claude-plugin/marketplace.json`: versão `0.21.0`.

### Task 1: Template e migração do elenco host-aware

**Files:**
- Modify: `orq/commands/elenco.md:65-170`
- Modify: `orq/commands/init.md:79-115,172-240`
- Modify: `orq/scripts/lint-coerencia.py:61-278`

**Interfaces:**
- Consumes: `memory/wiki/_elenco.md` quando existe; host atual identificado como `claude`, `codex` ou `kimi`.
- Produces: headings literais `## Matriz de invocação` e `## Times por host`; linhas `manager`, `planner`, `implementer`, `reviewer`, `docs`, `scout` por host.

- [x] **Step 1: Executar o probe RED do template atual**

```bash
python3 -c '
from pathlib import Path
s=Path("orq/commands/elenco.md").read_text()
assert "## Matriz de invocação" in s
assert "## Times por host" in s
assert "gpt-5.6-sol@ultra" in s
assert "gpt-5.6-terra@xhigh" in s
'
```

Expected: FAIL em uma das duas headings ausentes.

- [x] **Step 2: Completar o modelo canônico de `_elenco.md`**

Inserir no template de `orq/commands/elenco.md`, preservando as seções existentes:

```markdown
## Matriz de invocação

| Vendor do modelo | Host Claude | Host Codex | Host Kimi |
|---|---|---|---|
| Anthropic | spawn nativo com override | `claude -p --model <modelo> --permission-mode plan --tools '' < /dev/null` | mesma CLI Anthropic read-only |
| OpenAI | `codex exec -m <modelo> -c model_reasoning_effort=<effort> -s <sandbox> <briefing> < /dev/null` | `codex exec` obrigatório; primitiva nativa só com override comprovado e registrado | CLI Codex com sandbox explícito |
| Moonshot | `kimi -m <modelo> --output-format text -p <briefing> < /dev/null` | mesma CLI Kimi read-only | primitiva nativa somente quando a capacidade estiver comprovada |

## Times por host

### Host Codex

| Papel | Modelo | Sandbox |
|---|---|---|
| manager | `gpt-5.6-sol@high` | sessão principal |
| planner | `gpt-5.6-sol@ultra` | `read-only` |
| implementer | `gpt-5.6-terra@xhigh` | `workspace-write`, em worktree dedicado |
| reviewer 1 | `opus` (Opus 5) | read-only, sem ferramentas |
| reviewer 2 | `kimi-code/k3` | read-only, sem `--yolo`/`--auto` |
| docs | `gpt-5.6-sol@low` | read-only salvo arquivos de documentação autorizados |
| scout | `gpt-5.6-sol@low` | read-only |
```

Repetir no próprio template as tabelas completas dos hosts Claude e Kimi; não referenciar “igual acima”.

- [x] **Step 3: Tornar a migração aditiva no `init` e no `elenco`**

Adicionar a ambos os arquivos a regra operacional:

```markdown
Ao encontrar `_elenco.md` existente:
1. leia o arquivo inteiro;
2. preserve modelos, perfis e revisores escolhidos pelo projeto;
3. acrescente somente headings obrigatórias ausentes;
4. não substitua uma linha existente do host sem aprovação explícita;
5. se a seção existe mas está incompleta, mostre o diff proposto e pare no gate.
```

- [x] **Step 4: Adicionar o guard de coerência do template**

Em `lint-coerencia.py`, depois da validação AGENTS/CLAUDE, adicionar:

```python
elenco_cmd = plugin / "commands" / "elenco.md"
consumidores = [
    plugin / "skills" / "orq" / "SKILL.md",
    plugin / "commands" / "plan-next.md",
    plugin / "commands" / "implement-next.md",
    plugin / "commands" / "revisar.md",
]
txt_elenco = elenco_cmd.read_text(encoding="utf-8")
for heading in ("## Matriz de invocação", "## Times por host"):
    if any(heading in p.read_text(encoding="utf-8") for p in consumidores) and heading not in txt_elenco:
        problemas.append((elenco_cmd.relative_to(raiz), 0, f"template não gera {heading}, exigida pelos consumidores"))
```

- [x] **Step 5: Aplicar o bump sincronizado e rodar probes GREEN e lint**

Run:

```bash
python3 -c 'from pathlib import Path; s=Path("orq/commands/elenco.md").read_text(); assert all(x in s for x in ["## Matriz de invocação","## Times por host","gpt-5.6-sol@ultra","gpt-5.6-terra@xhigh","kimi-code/k3"])'
python3 -c 'import json; assert json.load(open("orq/.claude-plugin/plugin.json"))["version"]=="0.21.0"; assert json.load(open(".claude-plugin/marketplace.json"))["plugins"][0]["version"]=="0.21.0"'
python3 orq/scripts/lint-coerencia.py .
```

Expected: ambos exit `0`.

### Task 2: Resolução host → papel → executor

**Files:**
- Modify: `orq/commands/plan-next.md:16-37`
- Modify: `orq/commands/implement-next.md:14-44`
- Modify: `orq/commands/revisar.md:48-104`
- Modify: `orq/skills/orq/SKILL.md:60-85,145-160`

**Interfaces:**
- Consumes: `## Times por host` e `## Matriz de invocação` produzidas na Task 1.
- Produces: resolução determinística `host -> papel -> modelo -> mecanismo`; mensagem padronizada de degradação.

- [x] **Step 1: Executar probes RED dos três consumidores**

```bash
python3 -c '
from pathlib import Path
checks={
 "orq/commands/plan-next.md":["identifique o host", "Times por host", "Matriz de invocação"],
 "orq/commands/implement-next.md":["identifique o host", "Times por host", "worktree dedicado"],
 "orq/commands/revisar.md":["Opus 5", "kimi-code/k3", "painel parcial"],
}
for f, needles in checks.items():
 s=Path(f).read_text()
 assert all(n in s for n in needles), (f, [n for n in needles if n not in s])
'
```

Expected: FAIL com os termos faltantes.

- [x] **Step 2: Substituir o despacho cego do Planner**

Em `plan-next.md`, usar o bloco completo:

```markdown
1. Identifique o host da sessão atual: Claude, Codex ou Kimi.
2. Leia `## Times por host` e selecione a linha `planner` daquele host.
3. Leia a célula vendor×host em `## Matriz de invocação`.
4. No Codex, leia modelo/effort no elenco e use a célula OpenAI×Codex com sandbox read-only. `codex exec` é o padrão; primitiva nativa só com override comprovado e registrado.
5. Se o modelo/CLI não existir, não planeje com modelo diferente em silêncio: deixe o card em PLANNING, registre a capacidade ausente e peça a escolha do fallback.
```

- [x] **Step 3: Substituir o despacho cego do Implementer**

Em `implement-next.md`, usar:

```markdown
1. Confirme que o card está READY e que existe worktree dedicado ao card.
2. Identifique o host e resolva a linha `implementer` em `## Times por host`.
3. No Codex, leia modelo/effort no elenco e use a célula OpenAI×Codex com sandbox workspace-write, dentro do worktree. Não redeclare o modelo neste consumidor.
4. Nunca execute o writer no checkout do Manager.
5. Sem modelo, CLI, worktree ou sandbox exigido, não escreva: devolva o card com a degradação nomeada.
```

- [x] **Step 4: Tornar Opus 5 + Kimi K3 obrigatórios no host Codex**

Em `revisar.md`, substituir a montagem por vendor genérico pelo contrato:

```markdown
No host Codex, dispare dois pareceres independentes e read-only:
- Opus 5: `claude -p --model opus --permission-mode plan --tools '' "<briefing sanitizado>" < /dev/null`.
- Kimi K3: `KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi"); "$KIMI" -m kimi-code/k3 --output-format text -p "<briefing sanitizado>" < /dev/null`.

O Manager Codex reconcilia os dois. Se um não rodar, escreva `PAINEL PARCIAL`, nomeie o revisor ausente e a causa (PATH, autenticação, timeout, modelo ou saída vazia). Nunca conte o próprio Manager como parecer independente.
```

- [x] **Step 5: Atualizar a skill com a ordem de resolução**

Adicionar à skill:

```markdown
Fora do Claude, antes de executar qualquer papel: identifique o host, leia `## Times por host`, resolva o papel e só então aplique a célula da `## Matriz de invocação`. “Configurado” não significa “rodando agora”. Sem executor comprovado, declare degradação e preserve o gate do card.
```

- [x] **Step 6: Rodar probes GREEN e lint**

Run os probes da Step 1 e `python3 orq/scripts/lint-coerencia.py .`.

Expected: exit `0`.

### Task 3: Onboarding, memória legada e diagnóstico do Codex

**Files:**
- Modify: `orq/skills/orq/SKILL.md:60-85,90-110`
- Modify: `orq/commands/instalar.md:53-74,136-156`
- Modify: `orq/commands/stack.md:40-130`
- Modify: `orq/commands/init.md:14-79,172-240,583-698`
- Modify: `README.md:25-60,120-140,430-470`
- Modify: `orq/scripts/lint-coerencia.py:61-278`

**Interfaces:**
- Consumes: plugin source/cache, `/plugins`, `/skills`, `memory/`, `MEMORY.md` and board paths.
- Produces: seven-layer diagnostic and four-state initialization classification.

- [x] **Step 1: Executar probe RED da interface Codex**

```bash
python3 -c '
from pathlib import Path
files=["orq/skills/orq/SKILL.md","orq/commands/instalar.md","orq/commands/stack.md","README.md"]
joined="\n".join(Path(f).read_text() for f in files)
for phrase in ["linguagem natural ou `/skills`", "instalado e habilitado", "skill carregada", "smoke comportamental"]:
 assert phrase in joined, phrase
'
```

Expected: FAIL em pelo menos uma frase.

- [x] **Step 2: Fixar o contrato da interface na skill e README**

Adicionar verbatim:

```markdown
No Codex, o Orquestra é ativado por linguagem natural ou `/skills`. A pasta `commands/` não cria `/orq:*` nesse host; esses slash commands pertencem ao Claude Code. Não diagnostique a ausência de `/orq` como plugin ausente.
```

Documentar `/prompts:orq` somente em uma subseção “Compatibilidade depreciada”, com escrita manual e opt-in.

- [x] **Step 3: Separar as sete camadas em `instalar.md` e `stack.md`**

Usar a mesma ordem completa nos dois arquivos:

```markdown
1. marketplace/fonte encontrada;
2. plugin instalado;
3. plugin habilitado;
4. versão e conteúdo do cache coerentes;
5. skill visível em `/skills`;
6. estrutura do projeto e elenco resolvidos;
7. smoke comportamental em conversa nova.
```

Para cada falha, parar na camada real; não inferir as seguintes.

- [x] **Step 4: Classificar memória sem chamar projeto maduro de virgem**

Em `init.md`, declarar e usar:

```markdown
- VIRGEM: não há memória nem equivalente funcional.
- MEMÓRIA LEGADA: há `MEMORY.md`, `memory/`, `NOTES.md` ou equivalente, mas não há board Orquestra.
- ORQUESTRA PARCIAL: há ao menos um dos artefatos Orquestra, mas faltam obrigatórios.
- ORQUESTRA COMPLETO: board, índice, schema e elenco existem.
```

Mensagem obrigatória para o segundo caso: `Memória preexistente detectada em outro formato; o Orquestra ainda não foi inicializado.`

- [x] **Step 5: Definir o smoke Codex em sessão nova**

Em `instalar.md`, depois da checagem de cache:

```markdown
Abra uma conversa Codex nova. Confirme `/plugins` e `/skills`. Depois diga “onde paramos?” e verifique leitura de `memory/MEMORY.md` antes do board. Em seguida diga “quero melhorar X” num fixture sem dados reais: o Orquestra deve criar/planejar o card e parar no gate. Instalação sem esse smoke permanece `instalado, não validado`.
```

- [x] **Step 6: Adicionar guards textuais ao lint**

Adicionar:

```python
codex_docs = [
    plugin / "skills" / "orq" / "SKILL.md",
    plugin / "commands" / "instalar.md",
    raiz / "README.md",
]
for p in codex_docs:
    txt = p.read_text(encoding="utf-8")
    if "Codex" in txt and "/skills" not in txt:
        problemas.append((p.relative_to(raiz), 0, "fala da interface Codex sem documentar /skills"))
```

Não crie regex que proíba toda ocorrência de `/orq:*`; o README precisa documentar a superfície Claude.

- [x] **Step 7: Rodar probes GREEN, validate e lint**

```bash
python3 -c 'from pathlib import Path; j="\n".join(Path(f).read_text() for f in ["orq/skills/orq/SKILL.md","orq/commands/instalar.md","orq/commands/stack.md","README.md"]); assert all(x in j for x in ["linguagem natural ou `/skills`","instalado e habilitado","skill carregada","smoke comportamental"])'
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
```

Expected: todos exit `0`.

### Task 4: Documentação final, versão e commit da release local

**Files:**
- Modify: `README.md`
- Modify: `memory/wiki/arquitetura.md`
- Modify: `memory/wiki/distribuicao.md`
- Modify: `memory/MEMORY.md`
- Modify: `memory/fixes-history.md`
- Modify: `orq/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `memory/wiki/KANBAN.md`
- Modify: `memory/wiki/threads/T-040-paridade-codex.md`

**Interfaces:**
- Consumes: produto final das Tasks 1-3.
- Produces: documentação atemporal, versão `0.21.0`, commit local validado e handoff para painel.

- [x] **Step 1: Atualizar documentação atemporal**

Registrar em `arquitetura.md`: núcleo compartilhado, interface por host e ordem host→papel→executor. Registrar em `distribuicao.md`: quatro estados do Codex e smoke em conversa nova. Atualizar README sem frases históricas.

- [x] **Step 2: Registrar histórico e handoff**

No topo de `fixes-history.md`, adicionar entrada datada com causa raiz, arquivos afetados e validações. Na thread `T-040`, registrar objetivo, decisões, limitações, evidência e próximo gate.

- [x] **Step 3: Reconfirmar o bump sincronizado para `0.21.0` aplicado na Task 1**

Atualizar:

```text
orq/.claude-plugin/plugin.json -> 0.21.0
.claude-plugin/marketplace.json -> 0.21.0
README.md Status -> 0.21.0
memory/MEMORY.md -> 0.21.0
```

- [x] **Step 4: Executar verificação completa local**

```bash
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
git diff --check
python3 -c 'import json; assert json.load(open("orq/.claude-plugin/plugin.json"))["version"]=="0.21.0"; assert json.load(open(".claude-plugin/marketplace.json"))["plugins"][0]["version"]=="0.21.0"'
```

Expected: todos exit `0`.

- [x] **Step 5: Revisar o diff como produto de instruções**

Confirmar manualmente: nenhuma instrução admite duas interpretações; nenhuma cita comando/skill/agente inexistente; nenhum caminho depende da máquina do dono; nenhum exemplo envia PII.

- [x] **Step 6: Executar painel read-only antes do commit**

Enviar o mesmo diff sanitizado para Opus 5 e Kimi K3. Exigir achados com arquivo:linha, cenário de
falha e veredito. O Manager reconcilia; reviewer não edita.

- [x] **Step 7: Aplicar correções e repetir a verificação completa**

Para cada achado confirmado, escrever primeiro um probe que falha, aplicar a correção mínima e
repetir validate, lint, `git diff --check` e probes de requisitos. Painel com bloqueador aberto não
vira commit.

- [x] **Step 8: Criar commit local único da release**

```bash
git add orq README.md .claude-plugin/marketplace.json memory/MEMORY.md memory/wiki/arquitetura.md memory/wiki/distribuicao.md memory/fixes-history.md memory/wiki/KANBAN.md memory/wiki/threads/T-040-paridade-codex.md
git commit -m "feat(0.21.0): paridade operacional do codex — interface e elenco por host"
```

- [x] **Step 9: Parar antes de instalar/publicar**

Não rodar marketplace update, plugin update, push ou smoke contra cache global. Entregar commit,
validações e pedido explícito de autorização para instalação local da release.

### Task 5: Fechar o silêncio do Opus 5 descoberto na validação

- [x] Reproduzir separadamente CLI, versão instalada e comportamento da candidata.
- [x] Comprovar por JSON que o alias local resolve para `claude-opus-5` em repo e projeto externo.
- [x] Criar runner stdin-only com anúncio imediato, orçamento, timeout e falha explícita.
- [x] Cobrir sucesso e falhas com testes RED→GREEN stdlib.
- [x] Integrar runner à Matriz, ao painel Codex/Kimi e ao lint.
- [x] Rodar Opus 5 real como revisor sobre o runner em lotes abaixo de 16 KiB.
- [x] Reconciliar Opus/Kimi: refutar flags inexistentes e descendente sobrevivente com chamadas reais
  e cinco repetições; aplicar os achados confirmados de privacidade, diagnóstico e cobertura.
- [ ] Reinstalar `0.21.0` em Claude/Codex e executar smoke numa conversa Codex nova em projeto externo.
- [ ] Confirmar o estado do GitHub e obter gate explícito antes de push/publicação.

## Plan Self-Review Checklist

- [x] Cada requisito da spec core está coberto por uma Task.
- [x] Nenhuma Step contém marcador pendente, atalho para outra Task ou erro genérico.
- [x] Headings e modelos consumidos nas Tasks 2-3 são produzidos na Task 1.
- [x] O commit toca `orq/` e inclui os quatro bumps exigidos.
- [x] O plano termina antes de publicação/push/cache global.
