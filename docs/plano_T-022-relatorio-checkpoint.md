# Plano `T-022` — Relatório final do `/orq:checkpoint` fala com a pessoa errada

> Planner: Fable · 2026-07-29 · card em `memory/wiki/KANBAN.md` (`[>]`)
> Status: **aguardando aprovação do dono no gate.**

## Problema (causa raiz, não sintoma)

O passo 5 de `orq/commands/checkpoint.md` manda entregar ao **dono** a "frase de retomada"
("na próxima janela: leia `memory/MEMORY.md` → thread X") — que é instrução para o **próximo
assistente**. Pior: a próxima janela é um contexto novo que **nunca lê esta tela**, então a frase
não alcança nem a audiência declarada. O único leitor real do relatório é o dono, que a recebeu
como tarefa. Junto: o relatório afirma "seguro dar `/clear`" **sem nenhuma checagem** que sustente,
não mostra o efeito no board, não separa o que espera decisão dele, e não diz o que ficou de fora.

## Solução (e por que essa)

**Separar por audiência e por mídia.** O que é do próximo assistente já mora no disco (`⏭️ RETOMAR
AQUI` na thread + `MEMORY.md` — o passo 3 já obriga os dois); a tela fica só com o que serve ao
dono. A afirmação "seguro limpar" ganha um gate executável (o parser do board + grep do RETOMAR
AQUI) **antes** do relatório. O relatório vira um template de 6 linhas máximas com **blocos
condicionais** (linha só existe quando tem conteúdo) e a regra "um bloco = no máximo 1 linha,
agregue dentro dela". Alternativas rejeitadas: crescer o relatório (vetado pelo dono) e "curto na
tela + completo em arquivo" (vetado pelo dono).

Os três caminhos de retomada ficam assim: (1) skill lê `MEMORY.md` sozinha ao abrir sessão — disco;
(2) "onde paramos" → quadro — citado na última linha do relatório; (3) rede de segurança — a última
linha mostra o caminho `memory/MEMORY.md` como fato ("a próxima janela lê sozinha"), não como tarefa:
se tudo falhar, o dono viu onde a verdade mora, sem nunca ter recebido dever de casa.

## O desenho — 5 conteúdos em 3–6 linhas

| Linha | Conteúdo | Quando aparece |
|---|---|---|
| 1 | ⏸️ decisões que esperam o dono (agregadas numa linha) | só se houver |
| 2 | efeito no board: `📋 antes → depois` + movimentos + nascidos | se houver board |
| 3 | o que foi gravado e onde (log · páginas · thread ⏭️ ✓) | sempre |
| 4 | o que NÃO entrou (pendência · tentado-e-falhou · fora) | só se houver |
| 5 | veredito da verificação + seguro `/clear` [+ fechar janela] | sempre |
| 6 | audiência corrigida: "ao voltar, nada é seu — a próxima janela lê `memory/MEMORY.md` sozinha; na dúvida, 'onde paramos'" | sempre |

Caso cheio = 6 linhas; caso comum = 4; projeto mínimo sem board = 3. A condicionalidade é o que faz
caber: não se escreve "Não entrou: nada".

## Passos

### Passo 1 — linha em branco entre o exemplo de card e o parágrafo seguinte

- **Arquivo:** `orq/commands/checkpoint.md:19-20`
- **Atual:**
  ```
      - [ ] `T-001` Título curto — nota livre depois do travessão
  **Se o projeto NÃO tem wiki**, crie o mínimo: `memory/MEMORY.md` (índice) + `memory/fixes-history.md`
  ```
- **Proposto:** inserir uma linha em branco entre as duas.
- **Verificação:** `awk 'NR>=19 && NR<=21' orq/commands/checkpoint.md` mostra a linha do meio vazia;
  `claude plugin validate ./orq --strict` segue passando.
- **Por quê:** CommonMark exige linha em branco para fechar bloco indentado — sem ela, renderizador
  pode colar a prosa dentro do exemplo (defeito desde a 0.2.0).

### Passo 2 — capturar o "antes" do board no passo 2b

- **Arquivo:** `orq/commands/checkpoint.md:33` (após o primeiro bullet do 2b, "Releia `KANBAN.md`…")
- **Proposto (bullet novo):**
  ```
  - **Ao reler o board, rode** `sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh .` **e guarde a
    saída**: é o "antes" da linha de board do relatório final (passo 6).
  ```
- **Verificação:** `python3 orq/scripts/lint-coerencia.py .` passa (o caminho
  `${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh` existe — mesma forma já usada em `stack.md:80` e
  `init.md:194`). Comportamental: relatório sai com par `antes → depois`.
- **Por quê:** o "antes" só existe se capturado antes das edições do passo 3 — depois, o número já
  é o "depois". O script é a mesma contagem da statusline: fonte única, sem divergência.

### Passo 3 — bullet BOARD no passo 3 (lacuna real: a skill promete, o comando não manda)

- **Arquivo:** `orq/commands/checkpoint.md:51` (inserir após o bullet **THREAD ativa**, antes de **GOTCHA**)
- **Proposto:**
  ```
  - **BOARD** (`wiki/KANBAN.md`): mova o que ESTA sessão moveu de fato e registre card que nasceu —
    formato do passo 1, regras de janelas do 2b. Guarde a lista de movimentos pro relatório.
  ```
- **Verificação:** lint passa; leitura cruzada: `SKILL.md:66` diz que o checkpoint "grava log +
  páginas + thread + **board**" — agora o comando tem a contrapartida. Comportamental: checkpoint
  numa sessão que moveu card atualiza o `KANBAN.md` editando linhas, não reescrevendo o arquivo.
- **Por quê:** sem esse bullet a linha "efeito no board" do relatório não tem fonte — o passo 3
  lista LOG/PÁGINAS/THREAD/GOTCHA/ÍNDICE/SNAPSHOT e nunca cita o board.

### Passo 4 — substituir o passo 5 por: 5 (verificar) + 6 (confirmar com template)

- **Arquivo:** `orq/commands/checkpoint.md:60-67` (a seção `## 5. Confirmar (3–6 linhas)` inteira)
- **Atual:** as 8 linhas atuais (frase de retomada entregue ao dono + "seguro dar /clear" sem
  checagem + parágrafo "Sobrou pendência…").
- **Proposto (literal):**
  ```
  ## 5. Verificar ANTES de afirmar "seguro limpar"

  "Seguro dar `/clear`" é a promessa deste comando — sustente-a antes de fazê-la. Com board: rode
  de novo `sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh .` e confira os **três sinais** (saída
  não-vazia · sem `⚠` · denominador = contagem manual dos cards). Com thread ativa: ela termina em
  **⏭️ RETOMAR AQUI**? **Falhou qualquer um → corrija e verifique de novo; não afirme "seguro" por
  cima de verificação falhando.** Falha que não é sua (outra janela)? Reporte-a no lugar da
  afirmação. O que o projeto não tem (board, thread) não se verifica — e não bloqueia.

  ## 6. Confirmar (3–6 linhas — a audiência é o DONO, não o próximo assistente)

  A instrução de retomada ("leia `memory/MEMORY.md` → thread X") é para a **próxima janela** — e ela
  **nunca lê esta tela**: o que ela lê é o `⏭️ RETOMAR AQUI` e o índice, que você acabou de escrever
  e verificar. Na tela, só o que serve ao dono. Um bloco = **no máximo 1 linha** (agregue dentro
  dela); condicional sem conteúdo não aparece:

      ⏸️ Sua decisão: <card + a pergunta exata; agregue o que espera validação>   ← só se houver
      Board: 📋 <antes → depois> · <movimentos desta sessão> · nasceram <IDs>
      Gravado: log + <páginas tocadas> + thread <nome> (⏭️ ✓)
      Não entrou: <pendência · tentado-e-falhou · deixado de fora>                ← só se houver
      Verificação ✓ — seguro dar /clear; pendência registrada no card = seguro fechar a janela também.
      Ao voltar: nada é seu — a próxima janela lê memory/MEMORY.md sozinha; na dúvida, "onde paramos".
  ```
- **Verificação:** `validate --strict` + lint passam. Comportamental (pós-release, ver passo 8):
  cenários A/B/C abaixo.
- **Por quê:** o gate executável substitui "se você não consegue afirmar com confiança, o handoff
  está fraco" (apelo à consciência) por critério de decisão; o parágrafo "Sobrou pendência…" (4
  linhas) é absorvido pela linha 5 do template — a justificativa completa já mora em
  `_schema.md` §"A pendência NÃO precisa de janela aberta" e na skill (dedup, não perda). Os três
  sinais vão inline (não só por referência ao `_schema.md`) porque instalação pré-0.6.0 não tem o
  arquivo — e a ausência dele **não** entra no gate (contradiria `checkpoint.md:11-12` e o achado
  T-015(e)).

### Passo 5 — matar a contradição nova na skill

- **Arquivo:** `orq/skills/orq/SKILL.md:66`
- **Atual (trecho):** `grava log + páginas + thread + board. **Depois** avise que é seguro dar
  \`/clear\` — e que dá pra **fechar a janela** se a pendência ficou registrada`
- **Proposto:** `grava log + páginas + thread + board, **verifica o board** e só então avisa que é
  seguro dar \`/clear\` — e que dá pra **fechar a janela** se a pendência ficou registrada`
- **Verificação:** lint passa; leitura hostil: nenhuma frase do plugin manda afirmar "seguro" sem
  condição enquanto o comando exige gate.
- **Por quê:** sem isso a skill ordena a afirmação incondicional que o comando passa a proibir —
  exatamente a classe de contradição entre arquivos que reprovou o T-015(c).

### Passo 6 — bump de versão nos QUATRO lugares (propor: 0.12.0)

- `orq/.claude-plugin/plugin.json:5` — `"version": "0.11.0"` → `"0.12.0"`
- `README.md:335` — `` `0.11.0` — board · … `` → `` `0.12.0` — board · … `` (lista de capacidades
  inalterada)
- `memory/MEMORY.md:7` — `**Versão:** 0.11.0` → `**Versão:** 0.12.0`
- `.claude-plugin/marketplace.json:12` — `"version": "0.11.0"` → `"0.12.0"`
- **Verificação:** `python3 orq/scripts/lint-coerencia.py .` (confere os quatro e tem o guarda de
  edição-sem-bump — com os passos 1-5 aplicados, ele **falha** até o bump entrar no mesmo commit).
- **Por quê:** cache é indexado por versão — sem bump, o que roda não muda e nada acusa (`5b75296`).

### Passo 7 — verificação pré-release (obrigatória, executável)

```bash
claude plugin validate ./orq --strict          # exit 0
python3 orq/scripts/lint-coerencia.py .        # exit 0
```

### Passo 8 — release + teste comportamental (só após o dono aprovar; sequência do CLAUDE.md)

`claude plugin marketplace update orquestra` → `claude plugin update orq@orquestra` → **reiniciar** →
`diff -rq ~/.claude/plugins/cache/orquestra/orq/0.12.0/ ./orq/` **vazio**. Então:

- **Cenário A (feliz):** trabalhar um bloco, dizer *"salva aí"*. Esperado: relatório 3–6 linhas;
  decisões no topo; `Board: 📋 antes → depois`; **nenhuma** frase mandando o dono ler `MEMORY.md`
  como tarefa; última linha dizendo que ele não precisa trazer nada.
- **Cenário B (gate reprova):** num branch descartável, inserir `**- [ ]** \`T-900\` teste` no
  `KANBAN.md` (vira `⚠1`) e dizer *"salva aí"*. Esperado: o checkpoint **não** afirma "seguro dar
  /clear" — aponta a linha fora do contrato e corrige ou reporta. Reverter o branch.
- **Cenário C (borda):** projeto mínimo sem `memory/wiki/KANBAN.md`. Esperado: relatório ~3 linhas,
  sem linha Board, sem travar nem acusar defeito.

## Exemplo — o relatório que ESTA sessão produziria (prova do desenho)

```
⏸️ Sua decisão: aprovar o plano do `T-022` (docs/plano_T-022-relatorio-checkpoint.md) · 8 cards em VALIDATE esperam seu teste pós-restart.
Board: 📋 20% (4/20) → 18% (4/22) · `T-022` [ ]→[>] · nasceram `T-022` `T-023`.
Gravado: log + MEMORY.md (0.11.0 publicada, commit 7545d88) + thread desenvolvimento-do-plugin (⏭️ ✓).
Não entrou: push da 0.11.0 (sem seu ok, nunca) · `T-019` `T-020` `T-021` seguem no backlog, sem plano.
Verificação ✓ (parser 4/22 = contagem manual · sem ⚠) — seguro dar /clear; e fechar a janela: o gate do T-022 está no card.
Ao voltar: nada é seu — a próxima janela lê memory/MEMORY.md sozinha; na dúvida, diga "onde paramos".
```

6 linhas, tudo condicional presente. Nota honesta que o desenho revela: o percentual **caiu**
(20% → 18%) porque nasceram 2 cards — é informação, não bug.

## Critério de aceite

1. `validate --strict` e lint passam (exit 0) com o bump no mesmo commit.
2. Pós-release+restart, cenários A, B e C se comportam como descrito.
3. O relatório nunca instrui o dono a ler arquivo como condição de retomada.
4. Relatório entre 3 e 6 linhas nos três cenários.

## Escopo — o que fica DE FORA

- `orq/commands/quadro.md` — sem mudança: quadro mostra **estado**, checkpoint mostra **delta**;
  vocabulário do parser compartilhado, contratos distintos, sem divergência a criar.
- `dormir.md`/`acordar.md` — o relatório noturno é outro contrato.
- A questão `/reload-plugins` vs restart — já é o `T-023`.
- Enforcement de verdade (hook que bloqueie) — continua `T-001`.
- `README.md` além da linha de versão — nenhuma seção descreve a mensagem final do checkpoint
  (grep confirmou), nada a alinhar.

## Decisões do dono

1. **Tirar "`_schema.md` presente" da auto-verificação** (era candidato no card). *Recomendo:
  tirar* — `checkpoint.md:11-12` diz que a ausência não é erro, e o T-015(e) reprovou exatamente
  acusar isso como defeito. Trade-off: perde-se um check barato; ganha-se coerência.
2. **Micro-edição na `SKILL.md:66`** (passo 5). *Recomendo: sim* — 4 palavras matam uma contradição
  que o painel reprovaria. Trade-off: +1 arquivo no diff.
3. **Versão 0.12.0 (minor) vs 0.11.1 (patch).** *Recomendo: 0.12.0* — muda o contrato visível de um
  comando, não é conserto de texto. Trade-off: nenhum real.
4. **Última linha fixa em todo checkpoint** ("Ao voltar: nada é seu…"). *Recomendo: sempre* — é a
  correção de audiência em si e responde a pergunta que originou o card em qualquer projeto.
  Trade-off: 1 linha repetida por checkpoint.

## Riscos

- **"Antes" subestimado:** se o board foi editado no meio da sessão (antes do checkpoint), o
  "antes" do 2b já contém esses movimentos. Mitigação: a lista de movimentos vem do que a sessão
  sabe que fez; os números do parser são âncora, não a fonte da lista.
- **6 linhas no limite:** caso cheio encosta no teto; a regra "um bloco = 1 linha, agregue" é o que
  segura — e é instrução, não enforcement (mesma classe do T-001).
- **Gate acendendo por falha alheia** (`⚠` deixado por outra janela) bloqueia o "seguro" desta —
  desejado, mas pode surpreender; o texto manda reportar em vez de afirmar.
- **Renumeração 5→6:** nenhum arquivo do plugin referencia "passo 5" do checkpoint (grep; as
  menções em `stack.md` são ao próprio stack). O card T-022 em `memory/` cita "passo 5" — histórico,
  isento do lint por design.
- **Comportamental só vale pós-release+restart** — antes disso testa a 0.11.0 (cache por versão).

## Handoff

- **Plano:** `docs/plano_T-022-relatorio-checkpoint.md` (este arquivo).
- **Resumo:** o relatório do checkpoint falava com a audiência errada e afirmava "seguro" sem
  checar; o plano corrige em 2 arquivos (`checkpoint.md` + 1 linha da `SKILL.md`) com gate
  executável e template condicional de 3–6 linhas, mais bump 0.12.0 nos quatro lugares.
- **Pendências:** as 4 decisões acima + aprovação do plano no gate (`PLANNING → READY`).
- **Próxima ação concreta:** dono aprova (com as 4 decisões); implementer aplica os passos 1-6 num
  commit `feat(0.12.0): …`, roda o passo 7, e o release/teste (passo 8) fecha com os cenários A-C.
