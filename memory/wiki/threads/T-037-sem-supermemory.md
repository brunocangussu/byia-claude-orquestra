# T-037 — Tirar o Supermemory do sistema de desenvolvimento

> **Frente:** @sem-supermemory · **Status:** AWAITING_OWNER — gate da Fase 5.
> Pedido verbatim (2026-08-07): *"eu queria que removesse a questão de avaliação do SuperMemory do
> nosso projeto. SuperMemory está dando muito problema de conexão, e eu quero retirá-lo do sistema
> de desenvolvimento."*
> ⚠️ Frente paralela ativa: `@frente-statusline` (`T-036`) mexe em `orq/commands/init.md` — este
> plano **não toca** naquele arquivo (verificado: não precisa — ver Fase 1).

## Problema

O Supermemory está entranhado no produto em três papéis, e nenhum deles funciona de forma confiável:

1. **`/orq:lembrar` é inteiro um contorno de bug.** O comando existe porque a busca do MCP oficial
   devolve 0 resultados (o endpoint `/v3/search` ignora o header `x-sm-project`); o `sm-search.py`
   é o contorno. Não é uma feature de memória que por acaso usa Supermemory — o comando **é** o
   contorno.
2. **O `checkpoint` grava nele** (seção "## 4. Supermemory" — `addMemory` a cada checkpoint).
3. **O catálogo da stack o oferece** (`orq/stack.md`, Camada 2 + perfil "Multi-projeto"), e o
   `/orq:init` e o `/orq:stack` leem esse catálogo para propor instalação em projetos novos.

Por cima disso, o serviço dá problema de conexão recorrente — e a fonte do erro nem é o plugin:
o MCP `api-supermemory-ai` está configurado na **conta do dono** (`~/.claude.json`), então remover
só do produto não silencia os erros do cliente (isso vira recomendação, Decisão 3).

**Causa raiz do risco deste card:** as 20+ ocorrências estão espalhadas por produto, wiki viva e
histórico append-only — remover pela metade deixa o produto se contradizendo (ex.: `SKILL.md` para
de citar, `stack.md` continua oferecendo), e o gate automático **não pega** contradição em prosa.

### O que o mapeamento confirmou (2026-08-07, verificado no código)

- **Produto — 7 arquivos, não 6:** além dos 6 do card, `orq/commands/ajuda.md:22` cita
  `/orq:lembrar` (o grep original foi por "supermemory"; o `ajuda.md` só cita o comando).
- **`orq/commands/init.md` NÃO cita Supermemory** — ele lê `${CLAUDE_PLUGIN_ROOT}/stack.md` como
  catálogo (init.md:38,70-71). Removê-lo do catálogo muda o que o init oferece **sem tocar no
  arquivo do T-036**. Zero conflito de arquivos entre as frentes.
- **O histórico quase não o cita:** `memory/fixes-history.md` e `memory/gotchas.md` têm **zero**
  menções (o card supunha que o log citava — não cita). No append-only, só
  `threads/T-030-correcoes-painel.md:684` menciona `sm-search.py`. Intocável mesmo assim.
- **`orq/.claude-plugin/plugin.json` não enumera comandos** — deletar `lembrar.md` não exige
  mudança estrutural no manifesto, só o bump de release.
- **O que os gates cobrem e o que não cobrem** (lido no `lint-coerencia.py`):
  - `claude plugin validate --strict` → só o manifesto. Não nota comando deletado.
  - O lint varre `orq/**/*.md` + `README.md`/`CLAUDE.md`/`AGENTS.md` e valida `/orq:<nome>` contra
    `commands/*.md` → **se `lembrar.md` sumir, qualquer `/orq:lembrar` sobrevivente quebra o gate**
    (hoje: `SKILL.md:99`, `ajuda.md:22`, `README.md:132`). Idem
    `${CLAUDE_PLUGIN_ROOT}/scripts/sm-search.py` órfão → "não existe".
  - O lint **NÃO** pega: menção de "Supermemory" em prosa (contradição semântica) · nada em
    `memory/` (ignorado de propósito) · afirmações de fato no README. **Esses só o grep do aceite
    cobre.**
  - ⚠️ **Guarda de cache:** ao editar `orq/` sem bump, o lint vai acusar *"versão 0.19.0 já existe
    no cache com conteúdo diferente"*. É **esperado** durante o trabalho — só some no bump do
    release. Não é defeito da implementação.

## Solução

**Alternativa (a) refinada: o comando morre; a intenção sobrevive com motor trocado.**

O `/orq:lembrar` e o `sm-search.py` são deletados. O gatilho *"lembra quando a gente…?"* **não
desaparece** — a linha da tabela na skill passa a mandar buscar **na wiki (log + threads + páginas)
e, se o claude-mem estiver instalado, na busca dele** (a skill `mem-search`, que vem com o próprio
claude-mem). O Supermemory sai do catálogo da stack e entra em "Dispensadas" no `_stack.md` deste
repo, com o motivo, para nunca ser reproposto.

### Por que (a) refinada, e não (b) — divergindo da recomendação que o card carregava

O card levava (b) — "o comando sobrevive com outro motor" — como recomendação, sob o argumento de
que preserva a intenção. **O argumento tem uma falsa dicotomia: a intenção não mora no arquivo do
comando, mora na linha de gatilho da skill.** O dono não digita comando (princípio central do
produto); o que ele vê é a frase funcionando. Verificado o que o claude-mem realmente entrega
(cache instalado, v13.7.0):

- **Ele já tem uma skill própria de busca, `mem-search`**, cujos gatilhos declarados são
  exatamente a intenção deste card: *"did we already solve this?"*, *"how did we do X last time?"*.
- Ela expõe ferramentas MCP verificadas na doc da skill: `search` (com filtros de projeto, data e
  tipo), `timeline` (contexto cronológico ao redor de um achado) e `get_observations` (detalhe em
  lote), num fluxo de 3 camadas documentado.
- A captura é automática (hooks → SQLite + índice vetorial em `~/.claude-mem/`), local, sem serviço
  externo — o oposto do problema que motivou o card.

Com isso, manter um `/orq:lembrar` reescrito sobre claude-mem seria pagar quatro custos por nada:

1. **Duplicação com ambiguidade** — nosso comando e a skill `mem-search` disparariam nas mesmas
   frases; dois componentes para a mesma intenção é o tipo de defeito que o review deste repo caça.
2. **Quebra do host-agnóstico (0.19.0)** — claude-mem é plugin do Claude Code; no Codex e no Kimi
   um `/orq:lembrar` dependente dele seria instrução quebrada, pior que ausente.
3. **Acoplamento de manutenção** — nosso produto documentando a API de outro plugin (13.x muda
   rápido); apodrece sem ninguém acusar.
4. **Custa mais que (a)** — um arquivo a mais para escrever, revisar e manter.

O que se perde de verdade com (a): em host **sem** claude-mem, a busca degrada para só-wiki (a
instrução nova declara a degradação, padrão da 0.18.0); e fatos **entre projetos** deixam de ter
gravação dedicada — a wiki é por projeto. Esse era o nicho do Supermemory, e ele está inoperante de
qualquer forma. Se o multi-projeto voltar a doer, é card novo, não escopo deste.

**Nada apaga dados:** a conta Supermemory do dono e o que já foi gravado ficam intactos.

## Passos

### Fase 1 — Produto (`orq/`) — 7 arquivos

1. **Deletar `orq/commands/lembrar.md`** (o comando inteiro é o contorno).
2. **Deletar `orq/scripts/sm-search.py`**.
3. **`orq/skills/orq/SKILL.md`** — 2 edições:
   - **:99** — reescrever a linha de gatilho: *"lembra quando a gente…?" · "o que a gente decidiu
     sobre…?"* → **Busca a memória**: wiki (`fixes-history.md`, threads, páginas) e, se o
     claude-mem estiver instalado, a busca dele (`mem-search`); sem claude-mem, diz que cobriu só a
     wiki. ⚠️ **Armadilha de lint:** não escrever o literal ``skill `mem-search` `` — o padrão
     `skill \`nome\`` é validado contra as skills **do orq** e falharia. Formular como *"a busca do
     claude-mem (`mem-search`)"*.
   - **:303-309** ("Ferramentas: use a mais barata que resolve") — fundir o item 4 no item 3
     (*"Contexto de sessões passadas e decisão antiga → claude-mem (automático + busca) + a
     wiki"*), apagar o item 4 do Supermemory e renumerar o 5 → 4.
4. **`orq/commands/ajuda.md:22`** — reescrever a linha: *"lembra quando a gente…"* → busca na wiki
   + claude-mem se presente (sem citar `/orq:lembrar`, que deixa de existir).
5. **`orq/commands/checkpoint.md`** — remover a seção `## 4. Supermemory` (:64-66) e renumerar
   5→4, 6→5. **Corrigir as referências cruzadas internas** (mapeadas por grep):
   - `:36` — "(passo 6)" → "(passo 5)";
   - `:141`, `:163`, `:164` — "passo 5" → "passo 4";
   - `:58` e `:168` citam "passo 1"/"passo 2b" — **não mudam**.
   Verificação do passo: `grep -n "passo [0-9]" orq/commands/checkpoint.md` sem sobra apontando
   para número inexistente. *(Não gravar nada no lugar: o claude-mem captura sozinho por hooks —
   um "grave no claude-mem" seria instrução para algo que já é automático.)*
6. **`orq/stack.md`** — 3 edições:
   - Remover a subseção `### Supermemory — fatos de longo prazo, entre projetos` inteira
     (:90-105, incluindo o gotcha da busca — morre com o motivo);
   - Perfis (:208-209): reescrever o exemplo *"cinco repositórios de 20 arquivos é 'mínimo +
     Supermemory'"* → fica só "mínimo" (não prometer que claude-mem cobre multi-projeto — não
     verificado; ver Autocrítica);
   - Perfis (:216): apagar a linha `| **Multi-projeto** | Supermemory |`.
   - Conferir que a introdução da Camada 2 (:72-75) continua fazendo sentido com uma ferramenta só.
7. **`orq/commands/stack.md:105`** — apagar a linha de filtro *"Sem repositório grande nem
   histórico longo → Supermemory é prematuro."* (era o único filtro específico dele).

### Fase 2 — README (varrido pelo lint)

8. **`README.md`** — 3 edições: `:66` (detecção do init: tirar "/ Supermemory") · `:86` (linha
   "Memória entre sessões" da tabela: fica só o claude-mem) · `:132` (apagar a linha do
   `/orq:lembrar` na tabela de comandos).

### Fase 3 — Wiki viva (reescrever para refletir o presente)

9. **`memory/wiki/_stack.md`** — mover o Supermemory de "Ativas" (:14) para **"Dispensadas (não
   repropor)"**: `| Supermemory | 2026-08-07 | problema de conexão recorrente; o dono pediu a
   remoção do sistema de desenvolvimento (T-037). Não repropor — nem no /orq:stack, nem no init |`.
   **Este é o item que impede o pedido de ser desfeito sozinho amanhã**: `commands/stack.md:109` e
   `init.md:74` mandam ler Dispensadas antes de propor. (Em projetos **novos** a proteção é outra:
   o catálogo `orq/stack.md` simplesmente não o lista mais.)
10. **`memory/wiki/distribuicao.md:14`** — tirar `sm-search.py` da árvore de `scripts/`.

### Fase 4 — O que NÃO se toca (append-only — o defeito mais provável deste card)

- `memory/fixes-history.md` e `memory/gotchas.md` — não citam Supermemory (verificado); de todo
  modo, só recebem **append** novo no checkpoint, nunca reescrita.
- `memory/wiki/threads/T-030-correcoes-painel.md:684` — cita `sm-search.py` descrevendo um achado
  de 2026. **É história. Fica.**
- Card `T-037` no `KANBAN.md` — texto é do Manager; esta frente não o reescreve.
- `orq/commands/init.md` — é do `T-036`, e comprovadamente não precisa (lê o catálogo).

### Fase 5 — Release (Manager, após aprovação e review)

11. Bump nos **quatro** lugares (`orq/.claude-plugin/plugin.json` · seção Status do `README.md` ·
    `memory/MEMORY.md` · `.claude-plugin/marketplace.json`) — número definido na hora, conforme a
    ordem com o `T-036` (Decisão 2). `validate` + lint verdes → `marketplace update` →
    `plugin update` → restart → `diff -rq` do cache vazio → teste comportamental.

## Critério de aceite

Mecânicos (antes do release):

```bash
# 1. Ausência no produto + README (o que o lint NÃO cobre em prosa):
grep -rni "supermemory\|sm-search\|orq:lembrar" orq/ README.md AGENTS.md CLAUDE.md
#    → tem que voltar VAZIO.
# 2. Arquivos deletados de fato:
test ! -f orq/commands/lembrar.md && test ! -f orq/scripts/sm-search.py && echo ok
# 3. Wiki viva atualizada — no _stack.md ele aparece SÓ em Dispensadas:
grep -ni "supermemory" memory/wiki/_stack.md     # → apenas linha(s) da seção Dispensadas
grep -ci "sm-search" memory/wiki/distribuicao.md # → 0
# 4. História intacta (prova de que não se reescreveu o append-only):
grep -n "sm-search" memory/wiki/threads/T-030-correcoes-painel.md  # → :684 continua lá
git diff --stat -- memory/fixes-history.md memory/gotchas.md 'memory/wiki/threads/*' \
  ':(exclude)memory/wiki/threads/T-037-sem-supermemory.md'          # → sem mudança
# 5. Gates:
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
#    → antes do bump, o ÚNICO achado tolerado é o guarda de cache ("0.19.0 já existe no cache");
#      depois do bump do release, zero achados.
# 6. Nenhuma referência interna de passo quebrada no checkpoint:
grep -n "passo [0-9]" orq/commands/checkpoint.md   # → só passos que existem (1, 2b, 4, 5)
```

Comportamentais (só valem após release completo + restart + `diff -rq` do cache vazio):

- *"lembra quando a gente decidiu sobre o painel?"* → busca wiki (+ claude-mem se presente), **sem**
  tentar `sm-search.py` e **sem** citar Supermemory.
- *"que ferramenta ajudaria?"* → o `/orq:stack` propõe a partir do catálogo **sem** Supermemory, e
  a seção Dispensadas segura qualquer reproposição neste repo.
- O card fecha em VALIDATE **quando o dono confirma** — commit não é critério de pronto.

## Escopo

**Dentro:** os 7 arquivos do produto, README, `_stack.md`, `distribuicao.md`, esta thread, e o
release (Fase 5, pelo Manager, com ok do dono).

**Fora (explícito):**
- **A máquina do dono** — `~/.claude.json` (MCP `api-supermemory-ai`), `~/.claude/CLAUDE.md` global
  e `~/.claude/scripts/sm-search.py`. Vira a Decisão 3, nunca edição nossa.
- A conta/os dados no Supermemory — nada é apagado nem exportado.
- Log, gotchas e threads antigas (append-only).
- `T-036` e `orq/commands/init.md`.
- Qualquer substituto para o nicho "fatos entre projetos" — se doer, é card novo.

## Riscos

1. **Remoção pela metade → produto se contradiz** (ex.: README mantém a oferta que o `stack.md`
   removeu). O lint não pega prosa — o grep nº 1 do aceite é o gate real. Mitigação: rodá-lo antes
   e depois do review.
2. **Reproposição futura** — `/orq:stack`/`--reinstalar`/init reoferecendo o Supermemory. Mitigado
   em duas camadas: fora do catálogo (todos os projetos) + Dispensadas no `_stack.md` (este repo).
3. **Renumeração do `checkpoint.md`** quebrar referência cruzada interna ("passo 5"/"passo 6") —
   as 4 linhas exatas estão no passo 5 do plano; o grep nº 6 do aceite prova.
4. **Armadilha do lint no texto novo**: escrever ``skill `mem-search` `` faz o gate falhar (universo
   de skills é o do orq). A formulação segura está no passo 3.
5. **Guarda de cache do lint** acusando "edição sem bump" durante o trabalho — esperado; não
   "corrigir" bumpando sem ok do dono (regra da casa).
6. **A dor do dono não some só com este card**: os erros de conexão nascem do MCP configurado na
   conta dele. Sem a Decisão 3, ele continua vendo erro — e pode achar que o card falhou.
7. **Degradação em host sem claude-mem** (Codex/Kimi): "lembra quando…" vira só-wiki. A instrução
   nova declara a degradação em vez de fingir — padrão já estabelecido na 0.18.0.
8. **Conflito de release com o `T-036`** — os dois bumpam os mesmos 4 arquivos. Tratado na
   Decisão 2 (sequenciamento pelo Manager, que é quem commita).

## Decisões do dono

1. **(a) refinada ou (b)?** — **Recomendo (a) refinada**: `/orq:lembrar` morre; o gatilho "lembra
   quando…" aponta para wiki + busca do claude-mem quando presente. *Trade-off:* sem comando
   dedicado, e em host sem claude-mem a busca degrada para só-wiki; em troca, zero duplicação com a
   skill `mem-search`, zero acoplamento à API de outro plugin, e custa menos que (b).
2. **Release junto ou separado do `T-036`?** — **Recomendo separado e sequencial** (quem ficar
   pronto primeiro sai primeiro; o segundo pega o número seguinte). É o padrão da casa (0.14–0.16
   saíram como três releases no mesmo dia), o teste comportamental valida uma mudança por vez, e
   uma reprovação no painel não prende a outra frente. *Trade-off:* dois ciclos completos de
   release/teste em vez de um.
3. **Sua máquina (recomendação — não editamos nada):** remover ou desabilitar o MCP
   `api-supermemory-ai` do `~/.claude.json` — **é lá que nasce o erro de conexão**, e este card não
   o alcança — e atualizar a seção Supermemory do seu `~/.claude/CLAUDE.md` global (que hoje manda
   buscar via `~/.claude/scripts/sm-search.py`). *Trade-off:* perde a gravação de fatos entre
   projetos; os dados já gravados ficam intactos na sua conta, recuperáveis se um dia quiser.
4. **Confirmar a entrada em Dispensadas** com o motivo "problema de conexão recorrente
   (2026-08-07)". **Recomendo sim** — é o que impede o `/orq:stack` de reoferecer amanhã.
   *Trade-off:* para readotar um dia, será preciso remover a linha de propósito (e é esse o ponto).

## Autocrítica — o que estou assumindo sem ter verificado

1. **Não exercitei a busca do claude-mem ao vivo.** Verifiquei o instalado (v13.7.0 no cache): a
   skill `mem-search` existe, documenta `search`/`timeline`/`get_observations`, e o
   `mcp-server.cjs` está lá — mas não rodei uma busca. Se ela depender do worker HTTP
   (`localhost:37777`) e ele estiver off, o primeiro uso pode falhar; a nota global do dono diz que
   o worker é on-demand, mas não provei. **Teste comportamental do aceite cobre isso.**
2. **Não sei se o `search` do claude-mem funciona sem filtro de projeto** (busca entre projetos) —
   a doc da skill não marca o parâmetro como opcional. Por isso o plano **não promete** substituto
   para o nicho multi-projeto em lugar nenhum do produto.
3. Assumo que o `T-036` não vai tocar `SKILL.md` nem `README.md`; se tocar, a conciliação é do
   Manager (protocolo de várias janelas).
4. Assumo que as cópias nos outros hosts (Codex via `plugin add`, Kimi em `~/.agents/skills/orq/`)
   serão re-sincronizadas pelo fluxo normal de release/`/orq:instalar` — não verifiquei o mecanismo
   de update de cada host.
5. O mapeamento foi por grep case-insensitive de `supermemory|sm-search|lembrar` em `.md/.py/.json`
   — menção com grafia exótica ("super memory") ou em outro tipo de arquivo teria escapado.

## ⏭️ RETOMAR AQUI — SUPERADO EM 2026-08-15

**Próxima ação:** levar as 4 decisões ao dono (gate `PLANNING → READY`). Aprovado o desenho, o
implementer executa as Fases 1–3 na ordem, roda os aceites 1–6 (tolerando só o guarda de cache no
lint), e devolve para review do painel. Release (Fase 5) só depois do review e da ordem do dono,
coordenado com o `T-036` conforme a Decisão 2.

## Atualização — 2026-08-15

O dono reconfirmou as decisões 1–4 e aprovou a arquitetura provider-neutral descrita em
`docs/superpowers/specs/2026-08-15-bruno-brain-memory-architecture.md`.

Correção de estado atual: o MCP não está ativo nem no Codex nem no Claude. Permanecem instruções,
helpers e uma credencial legada na máquina, além das referências no produto. A limpeza global será
feita somente depois do review, do release e da instalação da mesma versão nos dois clientes.

### Baseline comportamental — 2026-08-15

Três cenários read-only foram executados contra a skill anterior à mudança:

1. **“Lembra quando decidimos...” em host sem o MCP:** a skill acionou `/orq:lembrar`, tentou
   `sm-search.py` e orientou uma recuperação centrada no `~/.claude.json`; comportamento reprovado.
2. **“Faz checkpoint e termina rápido” sem o MCP:** o checkpoint preservou os gates locais, mas
   ainda reservou uma etapa ao fornecedor para então informar que a pulou; acoplamento desnecessário.
3. **“Qual ferramenta instalar para memória entre projetos?” em projeto pequeno multi-repo:** o
   catálogo recomendou nominalmente SuperMemory; comportamento contraditório com a decisão do dono.

Os mesmos cenários serão repetidos depois da edição. Aceite: wiki primeiro; nenhuma etapa externa no
checkpoint; nenhuma recomendação do fornecedor no stack.

### Resultado GREEN — 2026-08-15

Os três cenários foram repetidos em contextos novos e read-only:

1. **“Lembra quando decidimos...”** começou por `memory/MEMORY.md` e pela wiki, não tentou provider
   ausente e declarou que a cobertura ficou limitada ao projeto.
2. **Checkpoint rápido** preservou releitura, board, thread e handshake, sem etapa ou tentativa de
   gravação externa.
3. **Stack multi-projeto pequeno** permaneceu no perfil mínimo, não recomendou provider externo e
   declarou que não oferece memória semântica agregada entre repositórios.

Resultado: GREEN nos três comportamentos que falharam no baseline.

## ⏭️ RETOMAR AQUI — SUPERADO PELO CHECKPOINT ABAIXO

Executar a remoção na branch `feat/t037-sem-supermemory`, repetir os três cenários, rodar os gates e
parar antes de bump, publicação, cache global, alteração do Claude ou push.

## Checkpoint de recuperação pós-compactação — 2026-08-15

Contexto reidratado a partir de `memory/MEMORY.md`, `memory/wiki/KANBAN.md` e desta thread. A
implementação e a documentação estão commitadas em `103b4f7`, `1cfdec2` e `df856c8`; o worktree
estava limpo antes deste checkpoint. Os três cenários comportamentais ficaram GREEN, os 63 testes
passaram, `claude plugin validate ./orq --strict` e `lint-coerencia.py` passaram, o aceite mecânico
ficou limpo e o histórico append-only permaneceu intacto.

### ⏭️ RETOMAR AQUI — checkpoint atual

Solicitar review read-only do intervalo `008fbc9..HEAD` e corrigir somente achados concretos.
Depois do review, parar no gate do dono: **sem bump, publicação, push, alteração global, atualização
dos caches Codex/Claude ou orientação para reabrir a thread**. A reabertura só será pedida depois de
uma versão nova ser instalada e validada nos hosts.

## Revisão — rodada 1

- Revisor interno: quatro achados importantes sobre compatibilidade por host, provider dispensado,
  separação entre gateway read-only e fila mutável, e rastreamento desatualizado.
- Kimi K3: `APROVADO_COM_RESSALVAS`; confirmou remoção, 63 testes e gates, e encontrou resíduos de
  prosa/estado no README, plano e thread.
- Opus 5: chamada iniciada no modelo correto, mas sem parecer final no formato contratado; painel
  registrado como **PARCIAL**, sem retry automático.

Correções em andamento. Após aplicá-las: repetir o cenário “provider exposto, mas Dispensado”,
rodar novamente testes, validate, lint e aceites mecânicos; então pedir re-review read-only. Release
e alterações globais continuam proibidos.

### Resultado das correções e rodada 2

- O cenário “provider exposto, mas Dispensado” ficou GREEN: wiki primeiro, nenhuma consulta ou
  sugestão do provider e declaração de cobertura limitada ao conteúdo elegível.
- Os 63 testes passaram novamente; manifesto, lint, ausência ativa, arquivos deletados,
  `git diff --check` e preservação do histórico ficaram verdes.
- A rodada 2 do revisor não encontrou achado técnico restante. O único ajuste pedido foi encerrar
  esta thread com o estado atual, feito neste bloco.
- O painel externo continua **PARCIAL**: Kimi concluiu; Opus iniciou no modelo correto, mas não
  entregou parecer final. Pela regra do painel, não houve retry automático.

## ⏭️ RETOMAR AQUI — SUPERADO PELA AUTORIZAÇÃO DA FASE 5

Apresentar ao dono o resultado e pedir autorização explícita para a Fase 5: definir a nova versão,
fazer bump/commit/push, instalar a mesma versão no Codex e no Claude, comparar os caches e remover
as instruções globais legadas de forma recuperável. **Ainda não pedir para reabrir a thread**; isso
só acontece depois da instalação paritária e da validação dos hosts.

## Fase 5 — integração e release autorizado

O dono autorizou versão, push, instalação paritária e limpeza global recuperável. A auditoria
encontrou três linhas concorrentes: T-037 sobre `0.22.0`, T-043 estável em `bbcc4cb`/`0.22.1` e a
candidata T-044/`0.22.2` não commitada, ainda com corrida apontada pelo Opus.

**Ruling:** publicar `0.22.3` combinando T-037 com o commit estável T-043 e deixar todo o working
tree T-044 fora. Custo se errado: o Codex deixa de executar a candidata experimental `0.22.2`, mas
preserva o guardião estável e não publica trabalho sem gate.

O merge teve conflitos somente em `README.md`, `memory/MEMORY.md` e
`orq/commands/checkpoint.md`; foram conciliados preservando o handshake por host e removendo toda
gravação/referência ativa ao SuperMemory. O teste de coordenação revelou um quinto ponto de versão
(`ContextGuardReleaseVersionTest`), atualizado e documentado. Resultado pré-commit: **79 testes
verdes**, manifesto válido, lint verde, `py_compile` verde e ausência ativa confirmada.

## ⏭️ RETOMAR AQUI

Criar o commit combinado `0.22.3`, publicar em `origin/main`, instalar a mesma versão no Codex e no
Claude sem remover caches ainda referenciados por tasks abertas, comparar os caches, quarentenar
legados globais e rodar smokes em processos novos. Só então pedir ao dono para reabrir esta thread.
