# T-071 — seção arquivada exata — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer statusline, régua de bytes e guarda de posse reconhecerem a mesma seção arquivada, sem falsos cortes e aceitando `ARQUIVADOS`.

**Architecture:** Reconhecer apenas o título H2 exato, opcionalmente precedido por `📦`, fora de cercas Markdown válidas. Os dois `awk` preservam seus locales distintos, mas usam separadores e comparação de letras ASCII determinísticos; a guarda Python aplica o mesmo contrato. Cada parser mantém marcador e comprimento da cerca, não um booleano alternado por qualquer sequência de três. Testes adversariais impedem deriva entre os consumidores.

**Tech Stack:** POSIX `sh`/`awk`, Python 3 `unittest`, Markdown.

**Spec:** `memory/wiki/threads/T-071-secao-arquivada.md` (proposta a aprovar), com evidência em `memory/wiki/threads/T-054-pareceres.md:136-138,173-183` e contrato atual em `memory/wiki/_schema.md:20-21`.

## Global Constraints

- Não implementar até o dono aprovar a proposta de títulos exatos e cerca Markdown; o card permanece `[!] @codex`.
- A `main` tem edições paralelas. Trabalho somente no worktree T-071; o T-076 também toca `kanban-status.sh` e deve ser reconciliado antes da integração.
- Não alterar o processamento em dois passos: a régua mede bytes sob `LC_ALL=C`; a renderização preserva caracteres UTF-8.
- O baseline do worktree tem 332 testes, 4 falhas anteriores ao T-071. Regressões novas são bloqueadoras; não declarar suíte global verde por extrapolação.
- Bump, commit, push, revisão externa, publicação, instalação e restart exigem gates próprios do Orquestra/dono; passos abaixo não os autorizam.

**Registro de execução (2026-09-15):** após a integração obrigatória do T-076, o baseline mudou de
332 testes/4 falhas para 374 testes/3 falhas; a falha da chave morta saiu com a documentação do
T-076, e as três restantes continuam sendo o marcador preexistente do T-081. O resultado do T-071
executou 387 testes e manteve exatamente essas três falhas nos Pythons 3.9 e 3.12.

---

### Task 1: Contrato e parser da statusline

**Files:**
- Modify: `orq/scripts/test_kanban_status.py:79-85,180-189`
- Modify: `orq/scripts/kanban-status.sh:40-52`
- Modify: `memory/wiki/_schema.md:20-21`

**Interfaces:**
- Consumes: texto de `memory/wiki/KANBAN.md` com cards no formato de marcador, ID entre crases e título.
- Produces: mesma saída da statusline, mas corte apenas após título H2 exato; os dois `awk` excluem os mesmos cards arquivados.

- [x] **Step 1: Escrever RED parametrizado.** Em `test_kanban_status.py`, usar `rodar(..., locale=...)` e `card()` existentes para verificar os dois passos sob `C` e `pt_BR.UTF-8` (ou outro UTF-8 disponível). `## Como arquivar`, `## Não arquivados`, `## Arquivados pendentes`, H3, `## ARQUİVADOS`, `##<NBSP>Arquivado`, `## arquıvados` e `## arquivadoſ` mantêm dois cards ativos e `📏1` se o segundo tem nota de 400 bytes. Os cinco títulos ASCII permitidos, caixa mista, `📦` opcional, tab e CRLF cortam no mesmo lugar nos dois passos. Asserções devem conferir simultaneamente `(done/total)` e `📏`, não só exit code.

~~~python
def test_titulos_parecidos_nao_cortam(self):
    for heading in ("## Como arquivar", "## Não arquivados", "## Arquivados pendentes", "### Arquivado"):
        with self.subTest(heading=heading):
            board = "\n".join(["# b", card(" ", "T-001", "ativo"), heading,
                               card(" ", "T-002", "longo", "x" * 400)])
            saida = rodar(board).stdout
            self.assertIn("(0/2)", saida)
            self.assertIn("📏1", saida)

def test_titulos_exatos_cortam_contagem_e_regua(self):
    for heading in ("## ARQUIVADOS", "## 📦 Arquivado", "## Arquivo"):
        with self.subTest(heading=heading):
            board = "\n".join(["# b", card(" ", "T-001", "ativo"), heading,
                               card("x", "T-900", "historico", "x" * 400)])
            saida = rodar(board).stdout
            self.assertIn("(0/1)", saida)
            self.assertNotIn("📏", saida)
~~~

Acrescentar testes de cerca com abertura de quatro crases e linha interna de três, marcador de fechamento trocado, fechamento com texto, indentação de três espaços, fechamento válido e cerca sem fechamento. Um fechamento curto/trocado/com texto mantém o estado aberto; quando houver fechamento válido posterior, um título arquivado dentro da cerca não pode cortar o card ativo posterior: `(0/2)` e `📏1`. Uma linha de quatro espaços antes de marcadores não abre cerca. Medir também o caso em que o título arquivado verdadeiro está fora da cerca e deve cortar.
- [x] **Step 2: Confirmar RED.** `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_kanban_status.py'`; os casos novos devem falhar nos falsos cortes e em `ARQUIVADOS`, enquanto os existentes permanecem verdes.
- [x] **Step 3: Implementar a menor mudança nos dois `awk`.** Em ambos, antes das regras de card, reconhecer abertura com até três espaços e uma sequência homogênea de pelo menos três crases ou tis. Guardar tipo e comprimento. Abertura por crases com informação posterior contendo crase não é cerca. Fechar somente com o mesmo marcador, sequência não menor e resto em espaço/tab; marcador trocado, linha com texto e sequência curta não fecham. Normalizar CRLF antes dessas decisões. Dentro da cerca, ignorar o conteúdo até fechamento válido ou EOF. Para o H2 do board, exigir `##` na coluna 1 seguido de espaço/tab ASCII, `📦` inicial opcional, espaços/tabs finais e **somente letras ASCII** no título. Comparar com o regex de pares ASCII abaixo, sem `tolower()`, `.*arquiv` ou classes de espaço dependentes do locale. Não casar H3 nem aceitar sufixos.

~~~awk
function is_archive_heading(line, heading) {
    heading = line
    if (!sub(/^##[ \t]+/, "", heading)) return 0
    sub(/^📦[ \t]*/, "", heading)
    sub(/[ \t]+$/, "", heading)
    return heading ~ /^[Aa][Rr][Qq][Uu][Ii][Vv]([Oo]|[Aa][Dd][OoAa][Ss]?)$/
}
~~~

O trecho acima cobre só o H2; **não** copiar o antigo toggle booleano de cerca. Repetir o predicado e a máquina de estados de cerca nos dois programas `awk`, preservando o restante; `test_card_arquivado_nao_conta_para_o_teto` e a matriz sob dois locales verificam que não divergiram.
- [x] **Step 4: Atualizar o schema.** Substituir `_schema.md:20-21` pela lista exata de H2 aceitos, `📦` opcional, espaço/tab e caixa ASCII, gramática de abertura/fechamento de cerca e rejeição de títulos parecidos ou Unicode confundível.
- [x] **Step 5: Confirmar GREEN localizado.** Repetir o comando do passo 2 e comparar casos de card acima de 240 bytes antes/depois da seção; nenhum card ativo pode sumir, nenhum histórico pode acender `📏`.

### Task 2: Guarda de posse e coerência entre consumidores

**Files:**
- Modify: `orq/scripts/test_host_marker_guard.py:216-244`
- Modify: `orq/scripts/lint-coerencia.py:1053-1057,1097-1108`

**Interfaces:**
- Consumes: o contrato H2 exato da Task 1.
- Produces: `validate_marcador_host_kanban()` ignora apenas cards abaixo da seção arquivada real; um card em curso sem host após título parecido continua produzindo diagnóstico.

- [x] **Step 1: Escrever RED.** Acrescentar fixtures com card `[~]` sem host depois de `## Como arquivar`, `## Não arquivados`, `## Arquivados pendentes`, H3 e títulos confundíveis (`İ`, `ı`, `ſ`, NBSP); cada uma deve gerar um problema. Cobrir os cinco títulos exatos, `📦` opcional, tab, caixa mista e CRLF: um card histórico após o H2 real não deve gerar problema. Para cercas, repetir os casos da Task 1 (4/3 crases, marcador trocado, fechamento com texto, indentação 3/4 e sem fechamento) e conferir o card ativo após o fechamento válido; o estado Python deve concordar com os dois `awk`.

~~~python
def test_cabecalhos_adversariais_nao_desligam_posse(self):
    for heading in ("## Como arquivar", "## Não arquivados", "## Arquivados pendentes", "### Arquivado"):
        with self.subTest(heading=heading):
            self.board.write_text(
                BOARD_BASE.replace("## Fila", f"{heading}\n- [~] `T-911` Sem host — nota\n## Fila", 1),
                encoding="utf-8",
            )
            result, output = run_lint_main(self.root, self.home)
            self.assertEqual(result, 1, output)
            self.assertIn("T-911", output)
~~~

Adicionar casos exatos e cercas com o mesmo `BOARD_BASE.replace`: após título exato fora de cerca, `T-911` não aparece no diagnóstico; após título parecido ou título arquivado ignorado dentro de cerca corretamente fechada, aparece. Esta diferença é o oráculo do teste.
- [x] **Step 2: Confirmar RED.** `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_host_marker_guard.py'`; ao menos `ARQUIVADOS` e os falsos cortes devem expor o contrato antigo.
- [x] **Step 3: Implementar predicado Python equivalente.** Trocar `_ARQUIV_HEADING_RE` por H2 exato com separadores `[ \t]`, `(?:📦[ \t]*)?`, alternativas `arquivo|arquivad[oa]s?` e `re.ASCII | re.IGNORECASE`. Substituir também o toggle baseado em `_CERCA_CODIGO_RE` em `validate_marcador_host_kanban()` por estado de marcador + comprimento e a mesma gramática de cerca da Task 1; não apenas preservar a guarda antiga. Normalizar CRLF antes de analisar a linha e manter H2 do board na coluna 1.

~~~python
_ARQUIV_HEADING_RE = re.compile(
    r"^##[ \t]+(?:📦[ \t]*)?(?:arquivo|arquivad[oa]s?)[ \t]*$",
    re.ASCII | re.IGNORECASE,
)
~~~
- [x] **Step 4: Confirmar GREEN e suíte completa.** Rodar os testes localizados e `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'`. Registrar as quatro falhas de baseline separadamente de qualquer nova falha.
- [x] **Step 5: Verificar as demais guardas.** `claude plugin validate ./orq --strict`, `python3 orq/scripts/lint-coerencia.py .` e `git diff --check`. O lint pode ainda reportar T-081/cache antigo; não reportar verde se isso ocorrer.
- [x] **Step 6: Revisão e handoff.** Depois de gate explícito, enviar somente diff sanitizado ao revisor cross-vendor; auditar achados e submeter o resultado ao dono. Fazer bump/commit/push/release apenas por autorização separada, com allowlist e verificação do staged. A R1 usou dois lotes sanitizados (9.736 e 11.355 bytes) no `claude-fable-5-1`; ambos voltaram `APROVADO_COM_CORRECOES`, sem bloqueadores. A auditoria refutou o achado alto da régua e confirmou a divergência de `splitlines()` descrita na thread.

  A correção autorizada passou por novo RED/GREEN e uma única R2 em três lotes
  sanitizados (10.723, 15.445 e 9.441 bytes). O Fable aprovou/confirmou os três
  sem bloqueadores; detalhes e auditoria estão na thread do card.
