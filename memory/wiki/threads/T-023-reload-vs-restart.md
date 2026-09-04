# Thread — T-023 · `/reload-plugins` aplica update de cache — a doc está estrita demais

**Frente:** redação precisa sobre reload vs restart, nos 5 lugares que a 0.11.0 endureceu (+2 que a
varredura achou).
**Aberta em** 2026-07-30 · **estado: IMPLEMENTADO (2026-07-31) — revisor reprovou (3 bloqueadores + 4
riscos), correções aplicadas no mesmo dia — aguarda release + validação do dono** · planner `fable`.
**As decisões 1–5 foram levadas ao dono e estão fechadas** (delegadas em 2026-07-31); `orq/`,
`README.md` e `CLAUDE.md` já foram editados — ver "Implementação" e "Correções pós-review" abaixo.

## O fato verificado (2026-07-29, sessão viva)

Depois de `claude plugin update orq@orquestra`, um `/reload-plugins` passou a servir a **skill**
0.11.0 — o parágrafo "Desempate obrigatório" apareceu sem restart. Os testes 1–3 do T-016 no board
registram "contra a 0.11.0 já ativa na sessão": a evidência foi **usada**, não só observada.
**n=1, só skill.** Comando, agente, hook e MCP: nunca testados.

## Causa raiz — por que a doc oscilou em vez de ser precisa

A doc sempre codificou uma **regra binária** em vez de **evidência por componente**:

- **Pré-0.11.0 (frouxa):** *"`/reload-plugins` basta para comandos, agentes e skills; restart só
  para hooks/MCP/PATH"* — afirmação granular **sem origem registrada** (diff `40dbc59..7545d88`).
- **0.11.0 (estrita):** quando o ciclo desconfiou e não havia como auditar de onde a afirmação veio,
  a reação foi inverter tudo: *"não está comprovado que aplique update de cache — reinicie sempre"*.
- **Agora:** o fato novo desmente a versão estrita **para skill** — e consertar virando de novo a
  regra inteira repetiria o defeito pela terceira vez.

Duas agravantes: (1) **afirmação sem procedência** — ninguém anotou *como* se soube que "basta para
comandos"; quando questionada, só restou descartá-la inteira; (2) **frase espalhada em 7 lugares sem
dono canônico** — cada correção reescreve todos no tom do momento (o mesmo defeito de vocabulário
espalhado que já ocorreu 4× numa sessão, e que nenhum gate pega).

**A correção portanto não é "afrouxar de volta":** é trocar regra binária por **três estados por
componente** (✅ comprovado que aplica · ❓ não testado · regra operacional: presuma restart), com um
lugar canônico (README "Problemas conhecidos") e espelho na página de tópico (`distribuicao.md`).
Detalhe honesto: hoje **nenhum** componente está no estado "sabidamente exige restart" — até para
hook/MCP a fonte é o `--help` da CLI ("restart required to apply"), que o fato de 2026-07-29 provou
ser **conservador** (a skill aplicou sem restart). Citação de `--help` é procedência, não prova.

**O que NÃO muda:** a regra operacional *"teste comportamental que fecha card só vale após restart +
diff vazio"* continua — enquanto comando e agente não forem testados, a sessão pós-reload pode estar
**mista** (skill nova, resto indeterminado), que é pior de diagnosticar do que qualquer dos polos.

## Inventário completo (grep de 2026-07-30 — o card citava 5; são 7 + 2 homônimos)

| Lugar | Estado hoje | Ação |
|---|---|---|
| `README.md:52` | "se um comando não aparecer, reinicie" | **manter** — já é o protocolo tentativa→fallback, não afirma nada além do testado |
| `README.md:313-314` | "reload sozinho não garante cache atualizado" | **reescrever** (passo 2) |
| `README.md:364-368` | "**não está comprovado** que aplique" | **reescrever** — é o lugar canônico (passo 3) |
| `CLAUDE.md:54-57` | só restart, reload nem citado | **acrescentar 1 frase** (passo 4) |
| `orq/stack.md:218-221` | "CLI exige reiniciar… exigência conservadora" | **reescrever** (passo 5) |
| `memory/wiki/distribuicao.md:26,41` | "exige reiniciar" seco | **reescrever** — página dona do assunto (passo 6) |
| `memory/gotchas.md:76` | "# exige reiniciar a sessão" | **opcional** (decisão 5) |
| `orq/commands/stack.md:68,73,146,170` | regra operacional de diagnóstico/instalação | **manter** — "reiniciar antes de afirmar ✓" segue correta enquanto comando/agente não testados |
| `orq/skills/orq/SKILL.md:66` | "pode reiniciar" | **NÃO TOCAR** — homônimo: é fala do dono (gatilho de checkpoint), nada a ver com plugin |

## Passos (nenhum executado — texto exato por lugar)

**0. Grep de entrada** (guarda de vocabulário espalhado — rodar e guardar a saída):
```bash
grep -rn -iE "reload-plugins|reinicie|reiniciar|restart" README.md CLAUDE.md orq/ memory/wiki/distribuicao.md
```
Confere que o inventário acima ainda bate (as linhas podem ter deslocado — localizar pelo texto).

**1. `README.md:52`** — sem edição. Justificativa no inventário.

**2. `README.md:313-314`** — substituir as duas linhas por:
```
depois `/plugin marketplace update orquestra` + `/plugin update orq@orquestra`. Para iterar numa
skill, `/reload-plugins` comprovadamente aplica o update na sessão viva (verificado em 2026-07-29);
teste que fecha card exige **reiniciar** — comando, agente e hook seguem sem teste (ver "Problemas
conhecidos" abaixo).
```

**3. `README.md:364-368`** (seção "O plugin não reflete o que eu editei") — substituir o parágrafo
"Depois **reinicie a sessão** — … escopo de usuário." por:
```
O que o `/reload-plugins` aplica numa sessão viva, por componente — a doc já errou aqui nos dois
sentidos (0.10.0 afirmou demais, 0.11.0 negou demais), então o vocabulário é de evidência, não de
regra:

| Componente | `/reload-plugins` aplica o update de cache? |
|---|---|
| skill | ✅ **comprovado** — 2026-07-29: após `claude plugin update`, a sessão viva passou a servir a skill nova, sem restart |
| comando · agente | ❓ **não testado** — presuma restart até alguém repetir o teste acima com eles |
| hook · MCP server · PATH | ❓ **não testado** — presuma restart; o `claude plugin update --help` manda reiniciar, mas o caso da skill provou que esse aviso é conservador |

**A regra operacional não muda:** teste comportamental que fecha card só vale após **restart** +
`diff` vazio — enquanto comando e agente não forem testados, a sessão pós-reload pode estar mista
(skill nova, resto indeterminado). Novo dado? Atualize **uma célula** desta tabela, não a regra
inteira. Um plugin em **escopo `project`** não vale nos outros projetos: reinstale com escopo de
usuário.
```

**4. `CLAUDE.md:54-57`** — substituir o parágrafo "...seguidos de **teste comportamental**…" por:
```
...seguidos de **teste comportamental** — que só vale depois do release completo:
`claude plugin marketplace update orquestra` + `claude plugin update orq@orquestra` + **reiniciar a
sessão** + `diff -rq ~/.claude/plugins/cache/orquestra/orq/<versão>/ ./orq/` voltando **vazio**.
Só então conversar em português natural para ver se a intenção é reconhecida sem comando digitado.
Para iterar numa **skill**, `/reload-plugins` comprovadamente aplica o update na sessão viva
(2026-07-29) — serve para experimentar, **não** para fechar card: comando e agente seguem sem teste.
```

**5. `orq/stack.md:218-222`** — substituir o parágrafo "Depois de instalar: …" por:
```
Depois de instalar: rode (ou peça ao dono) `/reload-plugins` e verifique se a ferramenta responde;
se não responder, **reinicie a sessão**. O que se sabe (medido no repo do Orquestra, 2026-07-29):
o reload aplica update de cache para **skill**; comando, agente, hook e MCP seguem **sem teste** —
para eles, presuma restart, como o próprio `claude plugin update --help` recomenda. Em qualquer
caso, confirme que a ferramenta **responde** antes de dizer que está pronta. Instalado ≠ funcionando.
```

**6. `memory/wiki/distribuicao.md`** — página dona do assunto:
- linha 26, trocar o comentário: `claude plugin update orq@orquestra             # copia para o cache`
- após o bloco de código (linha 30), inserir:
```
**Reload vs restart, por componente (medido em 2026-07-29):** `/reload-plugins` na sessão viva
**aplica** o update para **skill** (a 0.11.0 foi servida sem restart). Comando, agente, hook e MCP:
**não testados** — presuma restart. Novo dado atualiza uma célula da tabela do README ("Problemas
conhecidos"), nunca vira regra binária de novo.
```
- linha 41, trocar a frase por: `**Consequência prática:** o teste comportamental que **fecha card**
  só é válido depois do update **e do restart** — reload basta para experimentar skill, não para
  validar.`

**7. Sonda barata para os não testados** (documentar no fim da seção do README do passo 3 — 2
linhas; executar só no próximo release, não agora):
```
Sonda pendente (custo: uma invocação): no próximo release que alterar `orq/commands/*` ou
`orq/agents/*`, rodar `/reload-plugins` na sessão viva e invocar o comando/agente alterado
procurando o texto novo. Apareceu → a célula vira ✅; não apareceu → vira "exige restart".
```
O candidato natural é o release do `T-025`: ele **cria** `/orq:ajuda` — se o comando novo responder
após reload sem restart, comando está provado (célula ✅ com data).

**8. Bump 0.14.0 nos quatro lugares** (`orq/.claude-plugin/plugin.json` · README Status ·
`memory/MEMORY.md` · `.claude-plugin/marketplace.json`) — o passo 5 toca `orq/`, então é obrigatório.

**9. Gates:** `claude plugin validate ./orq --strict` + `python3 orq/scripts/lint-coerencia.py .`.

**10. Grep de saída** (mesmo comando do passo 0). Critério de aprovação, hit por hit:
- **zero** ocorrências de "não está comprovado" perto de reload, e de "basta para comandos, agentes
  e skills" (as duas frases extintas — uma de cada polo);
- nenhuma linha afirma que reload aplica **comando, agente, hook ou MCP**;
- `orq/skills/orq/SKILL.md:66` ("pode reiniciar") **intacto** — homônimo, gatilho de checkpoint;
- os 4 hits de `orq/commands/stack.md` intactos (regra operacional, segue correta).

**11. Release completo + restart + `diff -rq ~/.claude/plugins/cache/orquestra/orq/0.14.0/ ./orq/`
vazio** — só então os critérios de aceite abaixo. (Ironia assumida: este card sobre reload valida-se
com restart, porque `orq/stack.md` não é skill — é arquivo lido em runtime, categoria não testada.)

**12. Deveres de checkpoint:** log em `fixes-history.md` · esta thread · `MEMORY.md` (versão).
`arquitetura.md` não muda (o grep confirmou: zero menções lá).

## Critérios de aceite — o dono comprova usando o produto

1. Abrir README → "Problemas conhecidos" e ver a **tabela por componente** com data e os três
   estados — nenhuma frase dizendo "não está comprovado que reload aplique" nem "reload basta".
2. Rodar o grep do passo 10 e conferir os critérios hit por hit.
3. Pós-release + restart: `diff -rq` do cache 0.14.0 vazio; comportamento **inalterado** (o card é
   só redação — nenhum fluxo muda).
4. (Diferido) No release do T-025: sonda do passo 7 executada e a célula "comando" da tabela
   atualizada com data — em qualquer direção.

## Decisões do dono (numeradas — responda "1a, 2…" que destrava)

1. **Formato do lugar canônico:** (a) tabela por componente no README — **recomendo**: célula
   atualizável impede a próxima oscilação; (b) prosa corrida — mais curta, mas foi prosa que oscilou
   duas vezes.
2. **Manter "card só fecha com teste pós-restart"?** **Recomendo sim** até comando e agente terem
   célula ✅ — o custo é um restart por release; o risco de sessão mista é falso-verde em validação.
3. **Executar a sonda no release do T-025** (`/orq:ajuda` como cobaia de comando)? **Recomendo sim**
   — custo de uma invocação, fecha metade dos "não testado".
4. **Ordem:** T-023 primeiro (0.14.0), T-025 depois (0.15.0) — **recomendo**: este está pronto e
   aquele espera 6 decisões. Cruzamento real é pequeno: T-025 edita README ~:121-132 + SKILL;
   T-023 edita README :313 e :364 + stack.md — só a seção **Status** colide (bump). ⚠️ Se aprovar
   esta ordem, a thread do T-025 (passo 8) precisa renumerar "0.14.0" → "0.15.0".
5. **`memory/gotchas.md:76`** (`# exige reiniciar a sessão`): trocar por
   `# copia para o cache — teste válido só após restart`? **Recomendo sim** — uma linha, alinha o
   gotcha à regra operacional sem afirmar o não testado. (Se preferir não mexer em gotcha, o custo é
   uma divergência benigna que o grep do passo 10 vai listar para sempre.)

## Riscos

- **Reverter para o polo frouxo por engano:** o texto do passo 3 nomeia os dois erros históricos de
  propósito — quem for editar a tabela no futuro vê que regra binária já falhou duas vezes.
- **n=1:** a evidência da skill é uma ocorrência. A redação diz "comprovado — 2026-07-29" (fato
  datado), não "sempre funciona" (lei). Se um dia falhar, a célula ganha a segunda data e vira "às
  vezes" — pior caso já previsto pelo vocabulário.
- **`CLAUDE_PLUGIN_ROOT` pós-reload:** não se sabe se, após reload, arquivos lidos em runtime
  (`stack.md`, scripts) vêm do diretório da versão nova ou da velha — o cache é por versão, então
  sessão mista pode ler caminho morto. Coberto pela regra operacional (restart antes de validar).
- **Encadeamento com T-025:** os dois mexem no README. Mitigado pela decisão 4 (ordem + seções
  disjuntas + renumeração apontada).

## O que NÃO investiguei (e por quê)

- **Não reproduzi o fato** (rodar `plugin update` + `/reload-plugins`): proibido — muta o ambiente
  do dono. A evidência é o registro de 2026-07-29 no board (testes do T-016 "contra a 0.11.0 já
  ativa na sessão").
- **Comando, agente, hook, MCP:** mesma proibição — por isso a sonda documentada (passo 7), não
  executada.
- **Doc oficial do Claude Code sobre `/reload-plugins`:** não consultada. O padrão deste repo é
  comportamento observado > doc (o `--help` da própria CLI já se provou conservador); citar doc
  externa reintroduziria afirmação sem teste local.
- **De onde veio a afirmação pré-0.11.0** ("basta para comandos, agentes e skills"): o diff mostra
  que ela entrou na 0.10.0 sem procedência anotada; arqueologia além disso não muda o plano.

## Escopo — fica de fora

- Executar a sonda (é do próximo release que tocar `commands/`/`agents/`); qualquer mudança de
  **comportamento** do plugin; enforcement por hook (`T-001`/`T-002`); o conteúdo do T-025; mover
  cards; editar `memory/` além desta thread; push/publicação.

## ⏭️ RETOMAR AQUI

**Implementado em 2026-07-31; revisor (Opus, read-only) reprovou com 3 bloqueadores + 4 riscos; as
correções foram aplicadas no mesmo dia** (ver "Correções pós-review" abaixo). **As decisões 1–5 estão
fechadas** — o dono já as delegou, não repergunte. Próxima ação: o **Manager roda o passo 11** (release
completo + restart + `diff -rq` do cache 0.14.0 vazio) e cumpre o passo 12 (log em
`fixes-history.md`, checkpoint desta thread, `MEMORY.md`). Só então o card vai a VALIDATE para o dono
comprovar usando o produto (critérios de aceite acima).

## Implementação (2026-07-31) — passos 0–10 e bump executados

**Feito:** os textos exatos dos passos 2–6 foram aplicados literalmente (nenhum desvio de redação).
Também: passo 7 (sonda documentada, 3 linhas, inserida logo após o parágrafo final da tabela do
README, antes de "Um revisor sumiu do painel sem avisar"); decisão 5 (`gotchas.md` — comentário
trocado por `# copia para o cache — teste válido só após restart`); bump 0.14.0 nos quatro lugares
(`orq/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `memory/MEMORY.md` — só a
linha de versão —, e a seção Status do README, à qual acrescentei uma cláusula curta: "· reload vs
restart documentado por **evidência por componente**, não regra binária" — não havia texto sugerido
no plano para essa linha, então segui o padrão das entradas anteriores da mesma seção).

`orq/commands/stack.md` e `orq/skills/orq/SKILL.md:66` **não foram tocados**, como o plano mandava.
`README.md:52` seguiu sem edição.

**Arquivos tocados (linhas no `git diff --stat`):** `README.md` (+27/-8), `CLAUDE.md` (+2),
`orq/stack.md` (+5/-5), `memory/wiki/distribuicao.md` (+8/-3), `memory/gotchas.md` (+1/-1),
`orq/.claude-plugin/plugin.json` (+1/-1), `.claude-plugin/marketplace.json` (+1/-1),
`memory/MEMORY.md` (+1/-1). 8 arquivos, 45 inserções / 21 deleções no total.

**Verificação — os dois gates:**
```
$ claude plugin validate ./orq --strict
Validating plugin manifest: .../orq/.claude-plugin/plugin.json
✔ Validation passed

$ python3 orq/scripts/lint-coerencia.py .
✓ coerência interna ok — 18 nomes conferidos, memory/ ignorado
```
Ambos passaram sem achado.

**Grep-guarda (passos 0 e 10), antes e depois:**
- **Antes** (passo 0): bateu exatamente com o inventário do plano — 7 lugares + o homônimo do
  `SKILL.md:66` + os 4 hits de `orq/commands/stack.md`.
- **Depois** (passo 10), critérios hit por hit:
  - `grep -rn "não está comprovado" ...` → **zero** ocorrências (frase extinta do polo estrito).
  - `grep -rn -i "basta para comandos" ...` → **zero** ocorrências (frase extinta do polo frouxo).
    Nota: existe `basta para` em `distribuicao.md:47` ("reload basta para experimentar skill, não
    para validar") — é o texto literal do passo 6 do plano, escopado só a skill, não a frase extinta.
  - Nenhuma linha afirma que reload **aplica** update de cache para comando, agente, hook ou MCP —
    checado via `grep -i "aplica"`: todos os hits em componente são "skill" (comprovado) ou "seguem
    sem teste" (comando/agente/hook/MCP, corretamente não afirmado).
  - `orq/skills/orq/SKILL.md:66` — **intacto**, texto idêntico ao grep de entrada.
  - Os 4 hits de `orq/commands/stack.md` (linhas 68, 73, 146, 170) — **intactos**, texto idêntico.

**Não feito / fora do meu escopo neste card:**
- Passo 11 (release completo + restart + `diff -rq` do cache 0.14.0) — proibido para o implementer
  (mutaria o ambiente do dono); é o Manager quem roda.
- Passo 12 (deveres de checkpoint: log em `fixes-history.md`, thread, `MEMORY.md` além da versão) —
  não mexi em `fixes-history.md` nem na seção "Onde paramos"/páginas do `MEMORY.md`, por estar fora
  da autorização deste card (só a linha de versão foi meu escopo, conforme o bump obrigatório).
- Passo 4 do bloco de decisões (ordem T-023/T-025 e renumeração da thread do T-025) — decisão do
  dono via Manager, não é ação de implementação.

**Decisões que tomei sozinho:**
- Na seção Status do README, como o plano não deu texto exato para essa linha (só mandou bumpar),
  escrevi uma cláusula curta e neutra ("reload vs restart documentado por evidência por componente,
  não regra binária") seguindo o estilo das cláusulas vizinhas (separadas por `·`).
- Ao trocar a frase de `distribuicao.md:41` (decisão do passo 6), removi a frase remanescente "Antes
  disso você está testando a versão anterior e concluindo coisas erradas sobre a atual" porque o
  plano deu o texto de substituição completo para aquele parágrafo e essa frase não constava nele;
  o conteúdo equivalente já está coberto pela regra operacional na tabela do README (passo 3).

**O que falta para o card ir a VALIDATE:** passo 11 (release + restart + diff vazio do cache
0.14.0) e o passo 12 completo (log + checkpoint), que são do Manager/dono — não deste implementer.

## Nota herdada do card `T-023` (migrada em 2026-09-01)

> Texto **íntegro** que vivia na linha do card, movido para cá quando o board ganhou
> teto de 200 chars. Nada foi resumido nem descartado — só realocado.

**Título na época:** `/reload-plugins` **aplica** update de cache

a doc está estrita demais **IMPLEMENTADO, REVISADO E CORRIGIDO (2026-07-31) — aguarda seu teste** — `memory/wiki/threads/T-023-reload-vs-restart.md`. Fable planejou · Sonnet implementou (9 arquivos, bump 0.14.0) · **Opus revisou e REPROVOU** com 3 bloqueadores. O mais instrutivo: a correção **criou** contradição entre `orq/stack.md` e `orq/commands/stack.md` — o defeito que este card existe para eliminar — e reintroduziu uma procedência errada que o painel da 0.11.0 já havia corrigido. **As 7 correções foram aplicadas e verificadas** (gates verdes; catálogo e comando voltaram a concordar: CLI → restart, slash command → `/reload-plugins`; frases extintas só sobrevivem no log e na thread, descrevendo o passado). **Como validar, depois do release + restart:** (1) abra o README em "Problemas conhecidos" e confira a tabela com **data em cada ✅** e nenhuma frase dizendo "reload basta" ou "não está comprovado"; (2) diga *"instala o Serena aqui"* e **pare antes de aprovar** — tem que sair **uma** instrução sobre como aplicar, não duas alternativas sem critério; (3) pergunte *"editei só o `orq/stack.md`, preciso reiniciar?"* — a resposta certa é **sim, presuma restart**; (4) dê `/clear`, diga *"onde paramos?"* e confira que nem o board nem a thread pedem decisões já tomadas. **🔎 OBSERVAÇÃO DE 2026-07-31, a confirmar:** depois do `claude plugin update` para a 0.15.0, o comando novo `orq:ajuda` **apareceu na lista de comandos/skills da sessão viva**, sem restart explícito. Isso é evidência a favor de "reload aplica **comando**" — mas **não fecha a célula**: não dá para separar se foi o reload do plugin ou um recarregamento disparado por outra edição na mesma janela, e o card do `T-023` existe justamente porque este projeto já afirmou coisa demais a partir de evidência fina. Repetir de forma isolada antes de marcar ✅ na tabela. **Sonda diferida:** no release do `T-025`, chame `/orq:ajuda` após `/reload-plugins` sem reiniciar — respondeu, a célula "comando" vira ✅ com data; não respondeu, vira "exige restart". Plano em (planner `fable`, 2026-07-30, modo noturno). **Causa raiz achada, e não é a que o card supunha:** a doc sempre codificou **regra binária** ("reload basta" ↔ "reinicie sempre") em vez de **evidência por componente** — a 0.10.0 afirmou sem procedência, a 0.11.0 desconfiou, não teve como auditar e inverteu tudo. **Virar a regra de novo seria a terceira repetição do mesmo defeito.** A saída é vocabulário de três estados por componente (✅ comprovado com data · ❓ não testado · regra operacional: presuma restart), em tabela num lugar canônico e espelhada na `distribuicao.md` — dado novo passa a atualizar **uma célula**, não a regra. **Honestidade que o plano registra:** hoje **nada** está no estado "sabidamente exige restart" — hook e MCP são presunção do `--help`, e o fato de 2026-07-29 provou que o `--help` é conservador. **Achado além do card:** são **7 lugares + 2 homônimos**, não 5 — `orq/commands/stack.md` (4 ocorrências, **manter**: ali é regra operacional correta) e `SKILL.md:66` ("pode reiniciar" é **fala do dono** no gatilho de checkpoint — **não tocar**); `README.md:52` já está preciso. **✅ LIBERADO EM 2026-07-31 — o dono delegou as 5 decisões ("o resto você decide e eu confiro no board"), e o Manager fechou assim:** (1) **tabela** de três estados por componente, não prosa · (2) **mantém** a regra "card só fecha com teste pós-restart" — sessão pós-reload pode estar mista · (3) roda a sonda barata no release do `T-025` (o `/orq:ajuda` é a cobaia: prova se reload aplica **comando**) · (4) ordem **`T-023` = 0.14.0 antes de `T-025` = 0.15.0** · (5) ajusta a linha do `gotchas.md`. **Primeiro da fila de implementação.** Era — tabela vs prosa · manter "card só fecha com teste pós-restart" · rodar a sonda barata no release do `T-025` · ordem `T-023`=0.14.0 antes de `T-025`=0.15.0 · ajuste de uma linha no `gotchas.md:76`. — 🟢 **verificado em 2026-07-29**: depois de `claude plugin update orq@orquestra`, um `/reload-plugins` na sessão viva passou a servir a skill 0.11.0 (o parágrafo "Desempate obrigatório" apareceu). A 0.11.0 trocou o README para "reinicie sempre — não está comprovado que reload aplique update de cache"; agora está comprovado que aplica, pelo menos para **skill**. Falta saber se vale igual para comando, agente e hook. Corrigir a redação nos cinco lugares que a 0.11.0 endureceu (`README.md:52`, `:313`, `:357-358`, `CLAUDE.md:54`, `orq/stack.md:218`) **sem** voltar a afirmar mais do que foi testado: hook e MCP continuam exigindo restart, e isso não foi verificado.

