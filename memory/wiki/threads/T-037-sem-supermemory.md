# T-037 — Tirar o Supermemory do sistema de desenvolvimento

> **Frente:** @sem-supermemory · **Status:** RELEASE 0.22.3 — correções finais antes do push.
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

### ⏭️ RETOMAR AQUI — SUPERADO PELAS CORREÇÕES ABAIXO

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

## ⏭️ RETOMAR AQUI — SUPERADO PELO CHECKPOINT DE RECUPERAÇÃO ABAIXO

Criar o commit combinado `0.22.3`, publicar em `origin/main`, instalar a mesma versão no Codex e no
Claude sem remover caches ainda referenciados por tasks abertas, comparar os caches, quarentenar
legados globais e rodar smokes em processos novos. Só então pedir ao dono para reabrir esta thread.

## Checkpoint de recuperação pós-compactação — 2026-08-15, Fase 5

Contexto reidratado a partir de `memory/MEMORY.md`, `memory/wiki/KANBAN.md` e desta thread. O commit
combinado já existe: `b84bc51` integra T-037 com o T-043 estável `bbcc4cb`, mantém a candidata
T-044/`0.22.2` fora e fixa a release em `0.22.3`. O backup recuperável anterior a qualquer operação
global está em `~/.codex/backups/orquestra-0.22.3-b84bc51/`. Ainda não houve push nem atualização
global nesta retomada.

A revisão final da release encontrou contratos residuais a corrigir antes da publicação: linguagem
bloqueante em `commands/stack.md`, ajuda sem distinção Codex/Claude, rastreamento durável atrasado,
documentação raiz ainda falando em quatro pontos de versão e instalação sem gate explícito de
preservação dos caches antigos. Esses achados são o escopo corrente.

### ⏭️ RETOMAR AQUI — SUPERADO PELA SEGUNDA RE-REVISÃO

Adicionar primeiro uma regressão executável para impedir semântica bloqueante no Codex; corrigir os
cinco grupos de achados; repetir suíte, validate, lint e aceites; obter re-review limpo. Só depois:
push em `origin/main`, instalação paritária `0.22.3`, restauração de qualquer cache ainda referenciado,
quarentena dos legados globais e smokes em processos novos. A frase para reabrir a thread continua
proibida até os dois hosts carregarem e validarem a mesma versão.

## Correções da revisão final — 2026-08-15

- Regressão RED→GREEN adicionada ao lint: prosa viva não pode declarar checkpoint obrigatório,
  trabalho bloqueado ou interrupção da sessão no caminho Codex.
- `commands/stack.md` passou a refletir exatamente o guardião consultivo; `commands/ajuda.md`
  distingue continuação/compactação no Codex de `/clear` no Claude.
- `commands/instalar.md` ganhou preflight, backup e restauração seletiva dos caches Codex ainda
  referenciados, sem comparar versões antigas com a release nova.
- `AGENTS.md` e `CLAUDE.md` permanecem byte-idênticos e agora documentam a suíte automatizada e os
  cinco pontos de versão. `distribuicao.md`, a T-043, o índice e o board refletem a `0.22.3`.
- Evidência: **82 testes**, `py_compile`, manifesto estrito, lint, identidade dos arquivos raiz e
  `git diff --check` verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA PRIMEIRA RE-REVISÃO

Executar os aceites mecânicos e obter re-review read-only limpo sobre o diff pós-`b84bc51`. Com o
parecer limpo, criar o commit corretivo e publicar `HEAD` em `origin/main`; só então registrar os
marketplaces no GitHub, instalar `0.22.3` nos três hosts, preservar caches, quarentenar os legados e
rodar smokes novos. Não orientar reabertura antes da validação paritária Codex/Claude.

## Re-review da release — rodada 1

Parecer: **REPROVADO** por dois cenários concretos. Uma `Directory` local ainda podia servir de fonte
de release e fazer o `diff` validar a própria fonte errada; além disso, o lint consultivo cobria só
arquivos escolhidos e não pegava “é obrigatório fazer checkpoint; pare o trabalho”.

Correções RED→GREEN: o instalador agora proíbe `Directory` em release, exige `HEAD` limpo igual ao
SHA remoto por `git ls-remote` e usa clone limpo desse SHA. O lint passou a varrer todo Markdown vivo,
acompanhar seção Codex e reconhecer ordem/paráfrases de obrigação, bloqueio e interrupção. O probe
adversarial em `commands/implement-next.md` virou teste. Resultado: **82 testes** e todos os gates
verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA TERCEIRA RE-REVISÃO

Pedir nova re-revisão read-only do diff completo pós-`b84bc51`. Se aprovada, criar o commit corretivo,
confirmar novamente que `origin/main` é ancestral e publicar. Instalação global e frase de reabertura
continuam condicionadas ao GitHub no mesmo SHA e aos smokes Codex/Claude da `0.22.3`.

## Re-review da release — rodada 2

Parecer: **REPROVADO** por dois probes adicionais. A prova de SHA usava o diretório corrente do
projeto consumidor em vez do repo Orquestra; e as negações “não/nunca/jamais é obrigatório” podiam
virar falso positivo no lint.

Correções RED→GREEN: `ORQ_RELEASE_REPO` agora é um caminho nominal e todo `rev-parse`/`status` usa
`git -C`; o SHA resultante continua tendo que ser idêntico ao `main` remoto. O lint passa a avaliar
uma janela antes do match e aceita negações explícitas de obrigação/interrupção sem enfraquecer os
casos positivos. Os dois probes entraram na suíte. Resultado: **83 testes**, manifesto, lint,
identidade raiz, `py_compile` e `diff --check` verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA QUARTA RE-REVISÃO

Pedir a terceira re-revisão read-only. Só um parecer limpo autoriza o commit corretivo e o push já
aprovado; instalação global e pedido de reabertura continuam posteriores à igualdade de SHA e aos
smokes novos nos dois hosts.

## Re-review da release — rodada 3

Parecer: **REPROVADO** por uma combinação: negação válida e ordem bloqueante posterior no mesmo
parágrafo eram consumidas por um match guloso e descartadas juntas.

Correção RED→GREEN: o lint mantém o contexto Codex do bloco, mas avalia cada sentença/cláusula
separadamente. Assim, “checkpoint não é obrigatório em teste. Em produção, checkpoint é
obrigatório” acusa a segunda frase; o mesmo vale para trabalho não bloqueado seguido de trabalho
bloqueado. Os dois contraexemplos entraram na suíte. Resultado: **84 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA QUINTA RE-REVISÃO

Pedir nova re-revisão read-only. Com aprovação, commit corretivo + push; sem aprovação, nenhuma
instalação. A orientação de reabrir continua reservada ao fim dos smokes paritários.

## Re-review da release — rodada 4

Parecer: **REPROVADO** porque contrastes por vírgula/travessão ainda permitiam que uma negação do
Claude ou de ambiente de teste mascarasse uma obrigação Codex posterior.

Correções RED→GREEN: além de pontuação forte, o lint agora separa vírgula, travessão e conectores
`mas`/`porém`/`contudo`/`entretanto`, mantendo estado de host entre cláusulas. Os dois probes do
revisor e o inverso — bloqueio legítimo no Claude sem contaminar o Codex — entraram na suíte.
Resultado: **86 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA SEXTA RE-REVISÃO

Pedir re-review final read-only. Sem `APROVADO`, não commitar/pushar; com aprovação, seguir para o
commit corretivo, publicação e instalação presa ao SHA remoto. Reabertura só depois dos smokes.

## Re-review da release — rodada 5

Parecer: **REPROVADO** porque uma cláusula compartilhada “Codex e Claude” herdava somente o último
host citado e podia ocultar uma obrigação dirigida também ao Codex.

Correção RED→GREEN: quando uma cláusula cita ambos os hosts, a presença do Codex prevalece para o
gate consultivo, independentemente da ordem dos nomes. As duas ordens entraram na suíte. Resultado:
**87 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA SÉTIMA RE-REVISÃO

Pedir re-review final read-only. APROVADO → commit/push e instalação; REPROVADO → voltar ao probe.
Não orientar reabertura antes da instalação e validação paritária.

## Re-review da release — rodada 6

Parecer: **REPROVADO** porque duas regras rotuladas na mesma cláusula — `Claude: ... e Codex: ...`
ou `enquanto` — eram tratadas como sujeito compartilhado, causando falso negativo num sentido e
falso positivo no inverso.

Correção RED→GREEN: `e/enquanto` só viram separadores quando há regra rotulada por host nos dois
lados. `Codex e Claude: ...` continua compartilhado; `Claude: ... e Codex: ...` vira duas regras
independentes. Quatro combinações entraram na suíte. Resultado: **88 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA OITAVA RE-REVISÃO

Pedir re-review final read-only. Só `APROVADO` libera commit/push; a instalação e a reabertura seguem
condicionadas aos smokes da versão publicada.

## Re-review da release — rodada 7

Parecer: **REPROVADO** por dois grupos: troca de host sem `:` mascarada por negação do Claude e
checkpoint imposto como pré-condição sem usar “obrigatório” (`deve`, `só continue`, `requisito`).

Correções RED→GREEN: regras `no/para o <host>` agora são separadas mesmo sem `:`; o lint também
rejeita modalidades e condicionais de continuidade (`deve`, `precisa`, `necessário`, `exigido`,
`requisito`, `condição`, `só continue`, `antes de continuar`). Os quatro probes entraram na suíte.
Resultado: **90 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA NONA RE-REVISÃO

Pedir re-review final read-only. Só `APROVADO` libera o commit corretivo e a publicação autorizada;
instalação/reabertura permanecem posteriores aos smokes.

## Re-review da release — rodada 8

Parecer: **REPROVADO** por três interações: vírgula destacava o sujeito `checkpoint`, voz passiva
“só é permitido continuar” escapava e menção incidental ao Codex dentro de regra Claude mudava o
escopo.

Correções RED→GREEN: vírgula só separa regras quando há rótulos de host dos dois lados; o host passa
a vir do rótulo inicial/heading, não de menção incidental; a negação de “obrigatório” é local; e a
condicional passiva entrou no padrão. Os três probes entraram na suíte. Resultado: **93 testes** e
gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA DÉCIMA RE-REVISÃO

Pedir re-review final read-only. `APROVADO` libera commit/push; instalação e reabertura continuam
dependentes da versão publicada e dos smokes.

## Re-review da release — rodada 9

Parecer: **REPROVADO** porque negações com auxiliares (`não deve ser`, `jamais será`) viravam falso
positivo e duas regras do mesmo Codex ligadas por `e/enquanto` ainda podiam se mascarar.

Correções RED→GREEN: a negação local reconhece somente auxiliares pertinentes antes de
“obrigatório”; `e/enquanto` separam afirmações por padrão e só deixam de separar quando unem
exclusivamente os nomes do sujeito compartilhado `Codex e Claude:`. Os quatro probes entraram na
suíte. Resultado: **95 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA DÉCIMA PRIMEIRA RE-REVISÃO

Pedir re-review final read-only. APROVADO → commit/push; qualquer probe material → corrigir antes.
Instalação e reabertura seguem bloqueadas até publicação e smokes.

## Re-review da release — rodada 10

Parecer: **REPROVADO** porque sujeitos compartilhados com preposição dependiam da ordem e separar
todo `e` destacava o sujeito de um predicado composto.

Correções RED→GREEN: o sujeito compartilhado aceita `Para o/No <host> e o/no <host>` em qualquer
ordem; `e/enquanto` só separam quando ambos os lados contêm afirmação de checkpoint ou quando há
nova regra rotulada. Predicados compostos preservam o sujeito. Três probes entraram na suíte.
Resultado: **97 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA DÉCIMA SEGUNDA RE-REVISÃO

Pedir re-review final read-only. Só `APROVADO` libera o commit/push; instalação e reabertura seguem
posteriores à publicação e aos smokes.

## Re-review da release — rodada 11

Parecer: **REPROVADO** porque o sujeito implícito numa segunda obrigação do mesmo Codex ainda era
mascarado e o sujeito compartilhado com `ou` dependia da ordem.

Correções RED→GREEN: cada ocorrência de “obrigatório” agora é avaliada individualmente; apenas uma
negação auxiliar imediatamente ligada àquela ocorrência a neutraliza. O sujeito compartilhado
aceita `e/ou` em qualquer ordem. Quatro probes entraram na suíte. Resultado: **99 testes** e gates
verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA DÉCIMA TERCEIRA RE-REVISÃO

Pedir re-review final read-only. Só `APROVADO` libera commit/push e a fase de instalação.

## Re-review da release — rodada 12

Parecer: **REPROVADO** porque uma obrigação de sujeito alheio (`o backup`) na mesma cláusula era
atribuída ao checkpoint e o literal `e/ou` compartilhado dependia da ordem.

Correções RED→GREEN: após conector, sujeito nominal explícito diferente de `checkpoint` encerra a
herança; sujeito ausente mantém o checkpoint implícito. O compartilhamento aceita `e`, `ou` e
`e/ou` em qualquer ordem. Quatro probes entraram na suíte. Resultado: **101 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — SUPERADO PELA DÉCIMA QUARTA RE-REVISÃO

Pedir re-review final read-only. `APROVADO` libera commit/push; instalação e reabertura continuam
posteriores aos smokes.

## Re-review da release — rodada 13

Parecer: **REPROVADO** porque gates legítimos do dono no mesmo bloco eram tratados como bloqueio de
checkpoint e sujeitos alheios sem artigo ou em crases ainda herdavam “checkpoint”.

Correções RED→GREEN: bloqueio/interrupção só são acusados quando a própria cláusula contém
`checkpoint`; após conector, qualquer sujeito explícito fora das preposições/adverbiais conhecidas
encerra a herança, inclusive `backup` e ``git status``. Quatro probes entraram na suíte. Resultado:
**103 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir re-review final read-only. APROVADO → commit/push; instalação/reabertura só depois dos smokes.

## Re-review da release — rodada 14

Parecer: **REPROVADO** porque “mesma cláusula” ainda não provava causalidade, adjunto adverbial
ocultava sujeito alheio e “isso” não retomava checkpoint.

Correções RED→GREEN: bloqueio/interrupção exigem ligação temporal explícita com checkpoint;
adjuntos iniciais são removidos antes de classificar sujeito; `isso/isto/essa regra/esta regra`
preservam a retomada. O rótulo de host também é removido antes da análise de sujeito. Quatro probes
entraram na suíte. Resultado: **106 testes** e gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir re-review final read-only. Só `APROVADO` libera commit/push; instalação e reabertura continuam
depois da publicação e dos smokes.

## Checkpoint de recuperação pós-compactação — 2026-08-15

Contexto reidratado a partir de `memory/MEMORY.md`, `memory/wiki/KANBAN.md` e desta thread, sem
alterar o escopo autorizado. A release continua sendo `0.22.3` = T-037 + commit estável T-043
`bbcc4cb`; T-044 permanece excluída. O último ponto técnico é a rodada 15: dois probes foram
adicionados para correferência por `concluí-lo` e para não confundir narrativa passada do dono com
política ativa. A correção do linter já está no worktree, mas ainda precisa passar RED→GREEN, suíte
completa, gates e novo parecer adversarial antes de commit/push. Instalação global e aviso para
reabrir a task permanecem posteriores à publicação e aos smokes novos em Codex e Claude.

### ⏭️ RETOMAR AQUI — checkpoint de recuperação atual

Rodar os dois probes da rodada 15; depois suíte/gates completos. Registrar a rodada e solicitar
novo re-review read-only. Somente `APROVADO` libera commit/push e instalação paritária.

## Re-review da release — rodada 15

Parecer: **REPROVADO** porque a correferência por `concluí-lo` rompia o vínculo causal do
checkpoint, enquanto uma narrativa passada — `foi bloqueado pelo dono` — era confundida com uma
política ativa do Codex.

Correções RED→GREEN: o vínculo temporal reconhece `checkpoint`, `concluí-lo` e `concluir o
checkpoint`; bloqueio declarativo exige estado ou ordem ativa (`fica`, `está`, `permanece`, `será`
ou imperativo), sem acusar relato passado incidental. Os dois probes entraram na suíte. Resultado:
**108 testes** e todos os gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir novo re-review final read-only. Somente `APROVADO` libera commit/push; instalação e aviso de
reabertura continuam posteriores à publicação e aos smokes novos em Codex e Claude.

## Re-review da release — rodada 21

Parecer: **REPROVADO** porque `backup do checkpoint` ainda era classificado pela presença do
adjunto, ações coordenadas escondiam o objeto mais recente e a narrativa dependia de uma whitelist
incompleta de verbos comunicativos.

Correções RED→GREEN: sujeito e objeto agora classificam o núcleo antes de adjunto preposicional;
coordenação encerra o primeiro objeto para que ações posteriores também sejam candidatas; a
exceção narrativa deixou de enumerar verbos e compara diretamente a posição da relação temporal
com o verbo de bloqueio, aceitando como causal a relação anterior ao bloqueio ou terminal. Quatro
probes novos foram incorporados aos testes existentes. Resultado: **113 testes** e todos os gates
verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir parecer final read-only sobre o diff vivo e o corpus representativo. `APROVADO` libera
commit/push; instalação e aviso de reabertura continuam posteriores à publicação e aos smokes.

## Parecer final da release — APROVADO

O revisor adversarial aprovou o diff vivo e o corpus representativo: classe consultiva 34/34,
suíte 113/113, lint, manifesto estrito, `git diff --check` e identidade AGENTS/CLAUDE verdes. Não
restou contradição Codex/Claude nem violação material de fonte/SHA/caches, cinco pontos de versão,
exclusão T-044 ou remoção do SuperMemory.

### ⏭️ RETOMAR AQUI — gate de publicação aberto

Repetir verificação fresca, commit das correções, confirmar `origin/main` como ancestral imutável e
publicar `HEAD:main`. Depois instalar e validar `0.22.3` em Codex/Claude/Kimi, quarentenar resíduos
globais do SuperMemory e executar smokes novos antes de avisar a reabertura.

## Re-review da release — rodada 20

Parecer: **REPROVADO** porque um adjunto temporal dentro do complemento fazia `checkpoint`
sobrescrever o núcleo `backup`; além disso, `depois do checkpoint, informe...` era lido como duração
do bloqueio narrado.

Correções RED→GREEN: objetos de ação agora capturam somente o núcleo nominal antes de adjuntos e
a presença literal de checkpoint só vale como fallback quando não há candidato semântico mais
específico. Relações temporais seguidas por verbo comunicativo são classificadas como ação
posterior, não como causa do bloqueio. Dois probes novos foram incorporados aos testes existentes.
Resultado: **113 testes** e todos os gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir novo re-review final read-only. Somente `APROVADO` libera commit/push; instalação e aviso de
reabertura continuam posteriores à publicação e aos smokes novos em Codex e Claude.

## Re-review da release — rodada 19

Parecer: **REPROVADO** porque objetos recentes introduzidos por imperativo (`faça o backup`,
`inicie a revisão`) ainda não substituíam o antecedente checkpoint; a exceção narrativa também
ignorava relação temporal colocada entre `explique por que` e o verbo de bloqueio.

Correções RED→GREEN: o tracker agora escolhe o candidato semântico mais recente por posição,
incluindo sujeitos com cópula/modal e objetos de ações executáveis; cláusulas comunicativas
incidentais continuam sem apagar o antecedente. A exceção narrativa procura causalidade temporal
depois do verbo explicador, cobrindo tanto a posição anterior quanto posterior ao bloqueio. Três
probes novos foram incorporados aos testes existentes. Resultado: **113 testes** e todos os gates
verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir novo re-review final read-only. Somente `APROVADO` libera commit/push; instalação e aviso de
reabertura continuam posteriores à publicação e aos smokes novos em Codex e Claude.

## Re-review da release — rodada 18

Parecer: **REPROVADO** porque uma cláusula incidental apagava o antecedente checkpoint, o sujeito
mais recente dentro da mesma cláusula não o substituía e a exceção narrativa ainda escondia uma
causa temporal posta depois do bloqueio.

Correções RED→GREEN: o antecedente persiste por cláusulas sem novo sujeito explícito; o último
sujeito nominal com predicado vence dentro da cláusula; a exceção narrativa só neutraliza o alerta
quando não existe relação temporal com checkpoint depois do verbo de bloqueio. Três probes novos
foram incorporados. Resultado: **113 testes** e todos os gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir novo re-review final read-only. Somente `APROVADO` libera commit/push; instalação e aviso de
reabertura continuam posteriores à publicação e aos smokes novos em Codex e Claude.

## Re-review da release — rodada 17

Parecer: **REPROVADO** porque a exceção ampla para `bloqueado pelo dono` ocultava causalidade
explícita do checkpoint e as elipses novas retomavam qualquer antecedente, inclusive revisão e
backup.

Correções RED→GREEN: elipse agora só retoma checkpoint da cláusula imediatamente anterior;
`concluir` sem objeto só é correferência quando termina antes de pontuação; cláusula intermediária
sem checkpoint quebra a retomada. A exceção do dono foi estreitada para linguagem narrativa
explícita (`explique/descreva/registre/documente/informe por que`), mantendo detectável
`até concluir o checkpoint, o trabalho fica bloqueado pelo dono`. Cinco probes materiais ficam
cobertos. Resultado: **111 testes** e todos os gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir novo re-review final read-only. Somente `APROVADO` libera commit/push; instalação e aviso de
reabertura continuam posteriores à publicação e aos smokes novos em Codex e Claude.

## Re-review da release — rodada 16

Parecer: **REPROVADO** porque `até concluir` e `até fazê-lo` ainda rompiam a correferência natural
com o checkpoint; além disso, `está bloqueado pelo dono` era confundido com bloqueio causado pelo
checkpoint.

Correções RED→GREEN: as duas retomadas elípticas passaram a integrar o vínculo causal quando o
bloco já estabelece checkpoint; bloqueio atribuído explicitamente ao dono é tratado como gate do
dono, não como política do guardião. Três probes materiais foram cobertos em dois testes. Resultado:
**109 testes** e todos os gates verdes.

### ⏭️ RETOMAR AQUI — checkpoint atual

Pedir novo re-review final read-only. Somente `APROVADO` libera commit/push; instalação e aviso de
reabertura continuam posteriores à publicação e aos smokes novos em Codex e Claude.
