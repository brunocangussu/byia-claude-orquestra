# Thread — T-025 · Comandos que nunca disparam sozinhos

**Frente:** cobertura de gatilho medida · superfície de descoberta · política de iniciativa do Manager.
**Aberta em** 2026-07-30 · **estado: PLANO PRONTO — aguarda gate do dono** · planner `fable`.
**Nada em `orq/` foi editado** — este arquivo é o único artefato.

## O pedido, verbatim (transcript de 2026-07-30, sessão `49b03dea`)

> "Eu também vi que o framework tem vários comandos, e às vezes nem eu lembro quais são os
> comandos. Depois eu queria revisar quais são as possibilidades. O ideal, na verdade, é que seja
> feito automaticamente. O próprio manage[r] e o próprio principal podem decidir o que fazer
> durante o desenvolvimento, o que é necessário fazer."

## A medição (método do T-014: falas reais, não imaginadas)

**Corpus:** 31 mensagens digitadas únicas do dono, extraídas dos transcripts das 4 sessões deste
projeto (`~/.claude/projects/-Users-…-byia-claude-orquestra/*.jsonl`, 26–30/jul). ~24 carregam
intenção (o resto é briefing colado ou resposta a pergunta numerada). As 10 frases do T-014 não
foram preservadas individualmente no log — este corpus foi re-extraído da fonte; os 3 fragmentos
que o log guarda ("queria acrescentar", "siga com suas recomendações", "vale a pena configurar")
batem com ele.

**Estrutural (SKILL.md hoje):** 11 dos 12 comandos têm gatilho na tabela (linhas 63–79).
`wiki-lint`: **zero menções** — confirmado por grep.

**Empírica, por intenção:**

| Intenção | Falas reais | Cobertura hoje |
|---|---|---|
| pedido de mudança | ≥8 ("queria melhorar o relatório…", "queria acrescentar…", "Seria interessante…", "precisa arrumar logo") | ✅ o T-014 consertou o grosso |
| prosseguir/aprovar | 6 ("sim pod eseguir", "pode comecar", "vamos seguir com suas recomendações", "aprova e faça…") | ✅ |
| elenco | 2 ("Quero que faça com o Fable o planejamento" ≈ gatilho listado) | ✅ |
| diagnóstico ferramental | 2 ("não consigo… conectar com o quinho [Kimi]" ≈ "não conecta com X") | ✅ |
| estado/board | 4 — **nenhuma bate literal**: "o que eu preciso fazer agora?", "o que preciso decidir??", "Eu não estou vendo card em lugar nenhum", "retomemos"/"continue de onde parou" | ⚠️ GAP — os gatilhos canônicos ("onde paramos", "cadê o board") **nunca foram digitados por ele** |
| revisar | 1 — "gostaria que validasse tambem com o plugin do codex" — stem "validar" ausente | ⚠️ GAP |
| feedback negativo pós-entrega | "Eu não gostei do formato do CheckPoint, não!" — "não gostei" ausente da description | ⚠️ GAP |
| checkpoint | 1 — "vamo fazer um checkpoint para depois eu dar um clear" — funcionou porque ele citou o nome; a palavra "checkpoint" **não está** na lista de gatilhos | ± |
| lembrar · dormir · acordar · init · **wiki-lint** | **zero falas no corpus** | sem evidência para propor gatilho — ver causa raiz |

**Amostra insuficiente, dito com todas as letras:** para `lembrar`, `dormir`, `acordar` e `init`
não há uma única fala real. **Não proponho gatilho novo para eles** — seria inventar frase, o
defeito que gerou o T-014. Ficam como estão.

## Causa raiz — são três, distintas

1. **`wiki-lint` foi desenhado com o invocador errado.** O dono nunca falou de saúde da wiki em 31
   mensagens ao longo de 4 sessões — e não vai falar: a regra global dele já diz "o Bruno só
   interage; VOCÊ organiza memória". O usuário natural do `wiki-lint` é o **Manager**, não o dono.
   Dar-lhe frase de gatilho repetiria o T-014 ao contrário. A correção é **condição** (parte 3) +
   entrada no cardápio (parte 2), não frase.
2. **Não existe superfície de descoberta.** O mapa intenção→ação vive na SKILL (para o modelo) e no
   README (para quem instala). "queria revisar quais são as possibilidades" foi dito verbatim e não
   casa com gatilho nenhum — virou este card porque foi tratado na mão.
3. **A política de iniciativa não existe.** "Decisões que o Manager toma sozinho" (SKILL.md:181–188)
   só cobre decisões de board. Nenhuma **condição** não-linguística dispara nada — o que não tem
   frase do dono simplesmente nunca roda. Já existe UM precedente com borda certa: "contexto >50% →
   sugira checkpoint em UMA linha, não force" (SKILL.md:88). É esse padrão que falta generalizar.

## Solução

- **Parte 1:** acrescentar à SKILL **só os gatilhos atestados** no corpus (estado, revisar,
  feedback negativo, "checkpoint", "retomemos"). Nada inventado.
- **Parte 2:** gatilho "quais as possibilidades / o que dá pra fazer" → **cardápio por situação**
  ("você diz X → acontece Y"), frases naturais em primeiro plano, comando entre parênteses.
  Recomendo materializar como comando `/orq:ajuda` (custo zero permanente — só entra sob demanda).
  Recusadas: seção fixa no `/orq:quadro` (custo recorrente de tela; ele pediu "de vez em quando",
  não "sempre") e linha no relatório do checkpoint (momento errado + mexe num formato que ele
  aprovou por mockup na 0.13.0 depois de reprovar a 0.12.0 — não re-litigar).
- **Parte 3:** política de iniciativa em **3 níveis**, na seção que já existe:
  - **N1 — age sozinho e relata** (só leitura, nada de escrita): rodar `wiki-lint` quando (a)
    fechar release/marco ou (b) um checkpoint flagrar contradição página×trabalho; relatar achados
    em **uma linha no fim da resposta em curso** — nunca turno próprio, nunca corrigir sem ok (o
    próprio `wiki-lint.md:24` já proíbe).
  - **N2 — propõe em uma linha, uma vez**: `stack` ao flagrar o mesmo atrito 2×; checkpoint com
    contexto >50% (regra existente, vira exemplo do nível). **Teto: 1 proposta não solicitada por
    bloco de trabalho.** Recusou → registra (padrão "Dispensadas" do `_stack.md` / "não re-litigar"
    da thread) e **não repropõe**.
  - **N3 — sempre pergunta**: a lista atual (instalar, irreversível, rumo, aparência) intacta.
  - Transversal: **iniciativa nunca escreve** — mudança continua entrando pelo ciclo.

## Passos (após o gate — nenhum foi executado)

1. `orq/skills/orq/SKILL.md:3-19` (description): acrescentar "não gostei" (bloco pedido de
   mudança), "valida isso" (bloco revisar), "o que preciso decidir" (bloco estado), "checkpoint"
   (bloco fechar), "retomemos"/"continue de onde parou" (bloco retomar), "quais as possibilidades"/
   "o que dá pra fazer" (novo bloco descoberta). Verificar: grep de cada frase; `validate --strict`.
2. `orq/skills/orq/SKILL.md:63,65,66,70` (tabela): mesmas variantes nas linhas de ciclo, quadro,
   checkpoint e revisar. Verificar por leitura + lint.
3. `orq/skills/orq/SKILL.md` (tabela, linha nova): descoberta → cardápio (`/orq:ajuda`). E linha
   **situacional** (como a do init em :79): "fechou release · checkpoint flagrou contradição" →
   wiki-lint por iniciativa. Verificar: lint acusa se `/orq:ajuda` não existir.
4. Criar `orq/commands/ajuda.md` — cardápio por situação; fecho: "você não precisa decorar nada —
   fale normal". Verificar por leitura contra os 13 comandos reais.
5. `orq/skills/orq/SKILL.md:181-188`: expandir para os 3 níveis com as bordas (teto 1/bloco ·
   relato no fim de resposta · recusa registrada não volta · iniciativa nunca escreve).
6. `orq/commands/wiki-lint.md`: bloco curto "quando o Manager roda por iniciativa" **apontando** a
   política da SKILL — a política mora num lugar só. ⚠️ Vocabulário: os lugares que descrevem
   iniciativa passam a ser SKILL + wiki-lint.md + README — o lint não pega divergência entre eles;
   o implementer deve `grep -rn "iniciativa\|sozinho" orq/ README.md` antes e depois.
7. `README.md`: linha do `/orq:ajuda` na tabela (~:121-132) + seção curta da política de
   iniciativa + Status/versão. Conferir se há contagem literal de comandos ("12") a atualizar.
8. Bump **0.14.0 nos quatro lugares** (`orq/.claude-plugin/plugin.json` · README Status ·
   `memory/MEMORY.md` · `.claude-plugin/marketplace.json`).
9. Gates: `claude plugin validate ./orq --strict` + `python3 orq/scripts/lint-coerencia.py .`.
10. Release completo (`marketplace update` + `plugin update` + restart) e `diff -rq` do cache
    vazio; só então os testes do dono abaixo.
11. Pós-validação (dever de checkpoint): atualizar `arquitetura.md` (política de iniciativa é
    desenho novo), log e esta thread.

## Critérios de aceite — o dono usando o produto, pós-release + restart

1. Dizer **"queria revisar quais são as possibilidades"** (a frase real dele) → cardápio por
   situação aparece, sem comando digitado, sem despejar nomes de comando como interface.
2. Dizer **"o que preciso decidir?"** → board com a seção "esperando você" primeiro.
3. Fechar um release → o Manager roda o `wiki-lint` **sozinho**, relata em uma linha e **não
   corrige nada** sem ok.
4. **Contra-teste de intromissão:** num bloco normal sem condição disparada, **nenhuma** proposta
   não solicitada; recusar uma proposta 1× e conferir que ela não volta nos 2 blocos seguintes.
5. `/orq:wiki-lint` digitado continua funcionando (sem regressão).

## Decisões do dono (numeradas — responda "1a, 2…" que destrava tudo)

1. **Forma da descoberta:** (a) comando `/orq:ajuda` + gatilho de frase — **recomendo**: custo só
   sob demanda; (b) seção fixa no quadro — custo em toda visualização; (c) linha no checkpoint —
   re-litiga formato aprovado na 0.13.0.
2. **Nome** (se 1a): `ajuda` — **recomendo** (óbvio ao listar) — ou `possibilidades` (a palavra
   dele, porém longa).
3. **Condição do wiki-lint autônomo:** (a) a cada release fechado + contradição flagrada —
   **recomendo** (sem número mágico); (b) a cada N cards DONE (defina N).
4. **Teto de iniciativa:** 1 proposta não solicitada por bloco — **recomendo**; diga se quer mais
   frouxo ou mais apertado.
5. **Onde o achado do lint autônomo aparece:** (a) uma linha no fim da resposta corrente —
   **recomendo**; (b) seção no relatório do checkpoint — só com seu ok explícito (formato 0.13.0
   foi aprovado por mockup).
6. **Gatilhos atestados extras** (passo 1–2): aplicar? **Recomendo sim** — risco único é a
   `description` crescer (1447 chars hoje; ver Riscos).

## Riscos

- **Tamanho da `description`:** 1447 chars hoje, funciona; o limite formal não está documentado
  localmente. Mitigação: acréscimo mínimo, `validate --strict` e teste comportamental decidem.
- **Ironia do 13º comando:** `/orq:ajuda` só se justifica se a interface for a frase — o cardápio
  nunca deve ensinar o dono a digitar comando.
- **Assistente intrometido:** é o risco nomeado do card — as bordas do N2 (teto, fim de resposta,
  recusa não volta) existem exatamente para isso; o contra-teste 4 verifica.
- **Vocabulário espalhado:** a política ficará descrita em 3 arquivos; erro já aconteceu 4× numa
  sessão — por isso o grep obrigatório do passo 6.

## O que NÃO investiguei (e por quê)

- **Transcripts de outros projetos** onde o orq roda — o corpus é só deste repo; a fala dele em
  projeto-alvo pode ter padrões diferentes. Fora do alcance combinado das fontes.
- **Limite formal da description de skill** — sem documentação local; coberto por gate + teste.
- **Contexto turno-a-turno de cada fala** — classifiquei intenção pelo texto extraído por script,
  sem reler as sessões inteiras (2,5–3,8 MB cada).
- **Custo de rodar wiki-lint em wiki grande** — aqui são ~10 páginas; num projeto-alvo maior pode
  valer delegar a subagente. Se aparecer, é card novo, não escopo deste.

## Escopo — fica de fora

- Enforcement por hook (é `T-001`/`T-002`); perfis de elenco (`T-020`); host alternativo (`T-026`);
  gatilhos para `lembrar`/`dormir`/`acordar`/`init` (zero evidência); qualquer mudança no formato
  do relatório do checkpoint sem decisão 5b explícita; mover cards; editar `memory/` além desta
  thread.

## ⏭️ RETOMAR AQUI

**O plano está pronto e nada foi implementado.** Próxima ação: o **Manager leva as 6 decisões
acima ao dono**. Com as respostas, o card vai a READY e o implementer executa os passos 1–11 na
ordem — os passos 4, 6 e 7 dependem das decisões 1–2; o 3 e o 5 dependem das 3–5. Sem resposta,
o card vira `[!]` com a pergunta exata: "responda as decisões 1–6 da thread T-025-gatilhos".

## Handoff do implementer (2026-08-01)

**Feito — passos 1–9 do plano, na ordem:**
1. Gatilhos atestados acrescentados na `description` da SKILL: "não gostei", "valida isso", "o que
   preciso decidir", "checkpoint", "retomemos"/"continue de onde parou", "quais as
   possibilidades"/"o que dá pra fazer" (bloco novo "descoberta").
2. Mesmas variantes nas 4 linhas da tabela (ciclo, quadro, checkpoint, revisar) — a linha de
   RETOMAR da tabela ficou **intocada**, como o próprio plano especificou (ela é por "início de
   sessão", não por frase).
3. Duas linhas novas na tabela: descoberta → `/orq:ajuda`, e uma situacional (sem aspas, no
   padrão da linha do `init`) pro `wiki-lint` autônomo.
4. Criei `orq/commands/ajuda.md` — cardápio por situação, frase antes do comando. **Corrigi um
   desvio meu próprio no meio do trabalho:** o rascunho inicial esqueceu o `wiki-lint` — a causa
   raiz #1 da thread já dizia que a correção dele é "condição + **entrada no cardápio**, não
   frase"; acrescentei uma linha situacional (sem gatilho inventado) antes de fechar. Cobre os
   **13** comandos reais, sem virar manual de sintaxe. Fecha com "você não precisa decorar nada —
   fale normal".
5. `SKILL.md:182-206` expandido pra 3 níveis. Decisão própria: **não** recategorizei os 3
   bullets pré-existentes (bug achado, limpeza/dedup, ordem da fila) dentro do N1 — eles escrevem
   no board (criar card, ordenar fila) e o N1 do card é definido como "só leitura"; misturá-los
   quebraria a própria definição. Adicionei "### Iniciativa própria — três níveis" como bloco
   novo dentro da mesma seção, e dobrei o antigo "Sempre pergunte ao dono" dentro do N3 (sem
   duplicar).
6. `orq/commands/wiki-lint.md` ganhou seção curta "Quando o Manager roda isto por iniciativa
   própria" que **aponta** pra SKILL (`Decisões que o Manager toma sozinho → N1`) — não restate
   as bordas.
7. `README.md`: linha de `/orq:ajuda` na tabela de comandos; linha nova na tabela "Você não digita
   comandos" pra "quais as possibilidades"; seção nova "## Iniciativa própria" (entre "O board" e
   "A memória (wiki)") que resume sem repetir números (não citei "1 proposta" ali, de propósito —
   número vive só na SKILL, pra não divergir depois). Não achei contagem literal de "12 comandos"
   pra corrigir (grep não achou nenhuma).
8. Bump 0.14.0 → 0.15.0 nos 4 lugares: `orq/.claude-plugin/plugin.json`,
   `.claude-plugin/marketplace.json`, `README.md` (seção Status, com os 3 itens novos anexados),
   `memory/MEMORY.md` (só a linha "**Versão:**" — não toquei no resto da página por instrução
   explícita de não mexer em `memory/` além do bump + este handoff).
9. Gates rodados 3× (2 antes do fix do item 4, 1 depois) — sempre limpo, saída literal abaixo.

**Não feito — e por quê:**
- **Passo 10 (release completo + restart + teste comportamental):** proibido pelas instruções
  desta tarefa ("não rode marketplace update, plugin update nem /reload-plugins"). Fica pro
  Manager/dono decidir quando rodar.
- **Passo 11 (pós-validação: atualizar `arquitetura.md` e o log):** não fiz — as instruções
  restringem edição de `memory/` ao bump de versão + este handoff. Deixo registrado aqui pra quem
  rodar o checkpoint depois do release.
- Critérios de aceite 1–5 da thread **não foram testados** — dependem do passo 10, que não rodei.

**Decisões próprias (além das já descritas acima):**
- Não recategorizei os 3 bullets pré-existentes de "Decisões que o Manager toma sozinho" dentro
  do framework N1/N2/N3 (ver item 5) — risco de contradizer a própria definição de N1 como
  "só leitura".
- `ajuda.md` cita `wiki-lint` como algo que "normalmente já roda sozinho" em vez de inventar uma
  frase-gatilho pro dono — coerente com "zero falas no corpus" já registrado nesta thread.

**Verificação — saída literal:**

Antes (grep, colado no card acima): 3 hits relevantes (`stack.md`, `wiki-lint.md` inexistente
ainda, `SKILL.md:178/181-188`).

Depois:
```
$ grep -rn "iniciativa\|sozinho\|não solicitada" orq/ README.md --include="*.md"
orq/stack.md:9        ...funciona sozinho... (pré-existente, não relacionado)
orq/agents/orq-implementer.md:36   ...sozinho e o motivo. (pré-existente, não relacionado)
orq/commands/stack.md:11           ...funciona sozinho... (pré-existente, não relacionado)
orq/commands/revisar.md:42,104     ...sozinho... (pré-existente, não relacionado)
orq/commands/init.md:229           ...decida sozinho... (pré-existente, não relacionado)
orq/commands/wiki-lint.md:29,32    NOVO — aponta pra SKILL, não restate
orq/commands/implement-next.md:58  ...sozinho... (pré-existente, não relacionado)
orq/skills/orq/SKILL.md:82,83,182,194,197,203,252   política + 1 pré-existente (252)
README.md:79,259,306,353           1 nova (259, aponta pra SKILL) + 3 pré-existentes
```
Julgamento hit-a-hit: nenhuma contradição — a política mora em `SKILL.md:182-206`; `wiki-lint.md`
e `README.md` só apontam pra ela, sem restatar números (teto, exemplos).

```
$ claude plugin validate ./orq --strict
✔ Validation passed

$ python3 orq/scripts/lint-coerencia.py .
✓ coerência interna ok — 19 nomes conferidos, memory/ ignorado
```

**Achado fora de escopo:** nenhum — não mexi em `arquitetura.md`/log/KANBAN por restrição
explícita da tarefa; fica anotado acima pro passo 11 rodar depois do release.

## Correções do review REPROVADO (2026-08-01)

O revisor (Opus, read-only) reprovou a rodada acima com 4 bloqueadores, 4 riscos, 3 notas. O que
ele confirmou limpo (bump 4 lugares, 0.14.0 intacta, gates, cardápio, gatilhos da `description`)
**não foi mexido**. Correções aplicadas:

- **B1** (`SKILL.md` citava `wiki-lint.md` dizendo algo que ele não dizia): `wiki-lint.md` agora
  distingue os dois contextos — a exceção de correção trivial só vale quando o **dono pede o
  comando diretamente**; rodando por iniciativa do Manager (N1), nada se corrige, nem trivial. A
  citação na SKILL foi corrigida pra essa frase verdadeira.
- **B2** (teto do N2 matava a sugestão de checkpoint >50% pra sempre): N2 agora distingue recusa
  de **política** ("não quero X", não repropõe nunca mais) de recusa de **momento** ("agora não",
  pode voltar quando a condição piorar materialmente — ex.: recusou aos 52%, só reproponha perto
  de 75%+). `SKILL.md:92-96` (contexto >50%) foi reconciliado pra citar essa mesma regra em vez de
  mandar sugerir incondicionalmente.
- **B3** ("bloco de trabalho" nunca era definido): definido explicitamente como do início da sessão
  (ou do checkpoint anterior) até o próximo `/orq:checkpoint`, que fecha o bloco — mesma unidade
  pro contador "atrito 2×" do N2. E "quando um release fecha" (não disparava fora deste repo) virou
  "checkpoint fecha com rótulo de marco" (`$ARGUMENTS` de `/orq:checkpoint`), que existe em
  qualquer projeto, com ou sem versionamento.
- **B4** (dois gatilhos inventados — zero ocorrência no corpus): removidos `"queria revisar o que
  existe"` e `"o que você consegue fazer"` de `SKILL.md:77`. Nada substituído.
- **R1**: "iniciativa nunca escreve" precisado pra "no produto" — registrar recusa (N2) ou achado
  (N1) na memória/board é permitido e é o que os próprios níveis exigem.
- **R2**: os 3 bullets pré-existentes (bug, limpeza, ordem da fila) rotulados **N0** — decisão de
  board, escreve no board por definição, a regra dos N1-N3 não se aplica a eles.
- **R3**: `README.md`, `wiki-lint.md` e `ajuda.md:27` (achado que meu grep anterior tinha
  **perdido** — grep refeito e colado abaixo) pararam de restatar números/condição; agora só
  apontam pra `SKILL.md`, que é onde o teto e as condições moram.
- **R4**: `checkpoint.md` ganhou parêntese explícito — corrigir página no checkpoint não é a
  "iniciativa" que o N1 restringe, porque checkpoint só roda a pedido do dono.
- **Nota 1**: `ajuda.md` linha da "anota isso" não promete mais `/orq:plan-next` como continuação
  leve — deixa claro que planejar é ação separada, futura, só quando o dono pedir.
- **Nota 2**: acrescentadas ao cardápio as duas situações que faltavam — diagnóstico ferramental
  (`/orq:stack --verificar`) e várias janelas (`@frente`) — o cardápio se declara "por situação".
- **Nota 3**: a regra "não liste como manual" desambiguada — a tabela por situação cobrindo as 13
  está certa; o que ela proíbe é a versão comando-primeiro sem frase.

**Não feito, de novo pela mesma razão:** passo 10 (release/restart/teste comportamental) e passo 11
(atualizar `arquitetura.md`/log) continuam fora — proibidos pelas instruções desta tarefa. Critérios
de aceite 1-5 continuam não testados.

**Decisão própria:** ao reescrever `ajuda.md:40`, troquei o exemplo `` `/orq:x` `` por "nome do
comando seguido de descrição" — a forma literal `/orq:x` fazia o `lint-coerencia.py` acusar
"comando /orq:x não existe" (falso positivo do lint, que não distingue placeholder de referência
real). Resolvido trocando o texto, não o lint.

**Verificação — grep completo, hit a hit (desta vez incluindo `ajuda.md`):**
```
$ grep -rn "iniciativa\|sozinho\|não solicitada\|uma vez\|bloco de trabalho" orq/ README.md --include="*.md"
orq/stack.md:9                          "funciona sozinho" — pré-existente, não relacionado
orq/agents/orq-implementer.md:36        template de handoff, "sozinho" — pré-existente, não relacionado
orq/commands/stack.md:11                "funciona sozinho" — pré-existente, não relacionado
orq/commands/ajuda.md:29                aponta pra iniciativa do Manager, SEM restatar número — corrigido (R3)
orq/commands/revisar.md:18,42,104       "uma vez"/"sozinho" de briefing e higiene — pré-existente, não relacionado
orq/commands/init.md:229                "decida sozinho" (colisão de nome) — pré-existente, não relacionado
orq/commands/checkpoint.md:2            "bloco de trabalho" na description — mesma definição da SKILL, consistente
orq/commands/checkpoint.md:51           NOVO — aponta pra N1, distingue (R4)
orq/commands/wiki-lint.md:26,31,34      reescrito — só aponta pra SKILL, não restata números (B1+R3)
orq/commands/acordar.md:18              "uma vez" de numerar perguntas — pré-existente, não relacionado
orq/commands/implement-next.md:58       "sozinho" de marcar DONE — pré-existente, não relacionado
orq/skills/orq/SKILL.md:82              "não instale sozinho" (init) — pré-existente, não relacionado
orq/skills/orq/SKILL.md:83              linha da tabela — condição realinhada com N1 (B3)
orq/skills/orq/SKILL.md:185,189,200,209,215-217   política canônica — consistente internamente
orq/skills/orq/SKILL.md:270             "funciona sozinho" (ferramentas) — pré-existente, não relacionado
README.md:48,55                         "uma vez por máquina/projeto" (instalação) — pré-existente, não relacionado
README.md:79                             "funciona sozinho" (stack) — pré-existente, não relacionado
README.md:129                           "bloco de trabalho" na tabela de comandos — consistente com a SKILL
README.md:258                           reescrito — só aponta, sem números (R3)
README.md:305                           "push... sozinho" — pré-existente, não relacionado
README.md:352                           Status/changelog nomeando os 3 níveis — não é normativo, é registro de versão
```
Julgamento: nenhuma contradição. A política (números, condições, teto) mora só em
`SKILL.md:185-224`; todo outro arquivo aponta pra ela sem restatar.

**Gates:**
```
$ claude plugin validate ./orq --strict
✔ Validation passed

$ python3 orq/scripts/lint-coerencia.py .
✓ coerência interna ok — 19 nomes conferidos, memory/ ignorado
```
