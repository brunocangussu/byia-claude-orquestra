# T-036 — `/orq:init` apaga a statusline do dono + distribuir a barra completa

**Status:** PLANNING **v3** — a v2 foi ao painel 2 vezes e reprovou **5 de 5**; o dono recusou as
duas saídas oferecidas (só-mostrar · manter edição automática) e ditou o desenho: **compor dentro
da barra existente**. O plano v3 está no fim do arquivo; decisões pendentes: **7, 8, 10, 11, 12**.
**Frente:** @frente-statusline · **Planner:** Fable (v1 e v2 em 2026-08-07; v3 em 2026-08-08)

**O que mudou da v1 → v2** (a v1 não é preservada em separado, por instrução do Manager):
- O card vira **conserto + feature**: o plugin passa a **distribuir a statusline completa** do dono
  (novo asset `orq/scripts/statusline.sh`) e o `init` a instala no Caso C — pedido literal dele.
- **Eram DOIS projetos afetados**, não um: `IVA - App System` e
  `Prompts - Byia/prompts-byia-clientes` (neste, a chave estava **commitada** — `fa1363c`). Ambos
  revertidos à mão pelo Manager. O Risco 1 da v1 **se materializou** → legacy check vira
  **obrigatório em todo init**, não só no `--reinstalar`.
- Emenda aprovada à Decisão 2: as cópias instaladas levam **marca de versão** no topo, para o
  drift ser detectável mecanicamente.
- Novos fatos de investigação (campos documentados do stdin; teste de mesa da barra do dono).

---

## Problema (causa raiz — mantida da v1)

**Sintoma:** em 2026-08-07, após `/orq:init`, a barra degradou de rica para só `📋 …` em **dois**
projetos (IVA e prompts-byia-clientes; ambos já revertidos). Este card corrige o plugin e agora
também distribui a barra.

**Cadeia dos 5 porquês:** a barra degradou → chave `statusLine` no settings **do projeto** venceu a
global (precedência: Local > Projeto > Usuário, doc oficial) → o `init` gravou a chave achando que
"não havia statusline" → checou só o escopo do projeto → a instrução não dizia onde checar →
**o passo 4 da FASE 4 (`init.md:195-197`) tem 3 linhas para uma operação que edita settings do
usuário** — sem escopo, sem procedimento, sem formato, sem regra de caminho.

**Causas: duas.** (1) **Subespecificação do passo 4** — os defeitos (a) escopo, (b) composição,
(c) caminho, (d) redundância são quatro lacunas da mesma instrução, não quatro bugs. (2) **Lacuna
de verificação** — nada exercita o `init` contra estado pré-existente do host; o dano foi diff
`+4 -0` **aditivo**, invisível a "sobrescrevi arquivo?". Lição central, agora provada em dose
dupla: **em configuração com precedência, adicionar É sobrescrever** — e no segundo projeto o
defeito ainda foi **commitado**, pronto para contaminar quem clonasse.

## O que a investigação confirmou

Da v1 (continua valendo):
- **Precedência** (doc `settings`): Managed > CLI > Local (`.claude/settings.local.json`) >
  Projeto (`.claude/settings.json`) > Usuário (`~/.claude/settings.json`). `statusLine` não mescla.
- **`${CLAUDE_PLUGIN_ROOT}` NÃO funciona no comando da statusline**: (i) a doc de statusline só
  documenta `COLUMNS`/`LINES` como env vars do comando; (ii) o `settings.json` embarcável em plugin
  só aceita `agent` e `subagentStatusLine` — plugin não pode nem embarcar `statusLine`; (iii) o
  caminho de `${CLAUDE_PLUGIN_ROOT}` **muda a cada update** (cache por versão). → Saída: **cópias
  instaladas fora do plugin**.
- A cópia global do dono (`~/.claude/scripts/kanban-status.sh`, 45 linhas) é a **versão antiga**
  do script (sem os guardas do T-015: casa `- [.]` frouxo, sem `⚠N`).
- O `kanban-status.sh` do plugin não depende de cwd nem de jq (dir em `$1`, fallback `$PWD`).

Novos na v2:
- **Todos os campos que a barra rica usa são documentados** no stdin da statusline: `effort.level`,
  `rate_limits.five_hour.used_percentage/resets_at`, `cost.total_cost_usd`,
  `context_window.used_percentage`, `model.display_name`. **Exceção:** `.worktree.name` e
  `.worktree.original_cwd` — a doc diz que `worktree.*` só existe em sessões `--worktree`; o campo
  documentado para o caso geral é `workspace.git_worktree`, e para diretório,
  `workspace.project_dir`/`workspace.current_dir`. O asset distribuído usa os documentados.
- **Teste de mesa executado na barra do dono** (read-only): com stdin mock completo ela renderiza
  as duas linhas; com `{}` **degrada de graça** (segmentos somem, nada quebra, exit 0). A base é
  sólida para distribuição.
- **Nuance de honestidade sobre o drift:** neste board bem-formado, a cópia antiga e a estrita
  imprimem o MESMO `📋 13% (5/36) ⏳14`. A diferença só se manifesta em board malformado (a antiga
  conta checklist como card e nunca acende `⚠N`). O argumento do stamp de versão continua de pé —
  drift silencioso é exatamente o que não se vê até doer.
- **`jq`:** a barra rica faz ~12 chamadas de `jq` para parsear o stdin. O plugin hoje não tem essa
  dependência em nada. Vira ramo de degradação (Decisão 9), não pré-requisito.

## Solução (v2)

Duas entregas no mesmo card: **(A)** o conserto do passo 4 (árvore de decisão, como na v1) e
**(B)** a distribuição da barra completa como asset do plugin, instalada pelo Caso C.

### Regras invioláveis (R1-R3 mantidas; R4 emendada)

- **R1 — Escopo:** "existe statusline" = chave `statusLine` em **qualquer** um dos três arquivos:
  `.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.json` (o de maior
  precedência presente é o **efetivo**).
- **R2 — Nunca gravar por cima:** havendo statusline em qualquer escopo, **nenhuma chave é
  gravada**. Gravar chave de projeto com global existente É sobrescrever por precedência, mesmo com
  diff aditivo — o texto novo diz isso com todas as letras.
- **R3 — Caminho:** nunca gravar em settings caminho que aponte para dentro do plugin (cache ou
  repo). O executável referenciado é sempre **cópia** instalada fora do plugin.
- **R4 (emendada) — Fronteira de escrita:** o init escreve **dentro do projeto por padrão**.
  Escrever em `~/.claude/` só no Caso C, só se a Decisão 7 for aprovada, e só com **aprovação
  explícita e separada do usuário na conversa do init, nomeando os arquivos** que serão tocados.

### A tensão "R4 vs. todos os projetos" — resolvida, não contornada

*"Quero a barra completa em todos os projetos do meu computador"* tem **duas leituras com duas
respostas diferentes**:

1. **Na máquina do dono, a resposta é o Caso A funcionando.** A barra completa global **já existe**
   (`~/.claude/settings.json` → `~/.claude/statusline.sh`) e já alcança todos os projetos — o que a
   "sobrepujou" foi o init gravando chaves de projeto. O conserto (R2) **restaura e preserva** o
   alcance global. Em cada projeto dele, o init cai no Caso A ("sua statusline já mostra o board")
   e **não faz nada**. Isso é a feature, para ele.
2. **A distribuição vale para máquina nova / outro usuário**, onde não existe barra nenhuma: o
   Caso C instala a barra completa — por padrão no escopo do projeto; no escopo do usuário
   (todos os projetos da máquina) apenas via a pergunta explícita da R4 emendada (Decisão 7).

### O asset: `orq/scripts/statusline.sh` (novo arquivo do plugin)

Derivado do `~/.claude/statusline.sh` do dono (99 linhas), com estas generalizações — cada uma
remove algo específico da máquina dele:

1. **Kanban por vizinhança, não por caminho fixo:** o bloco
   `if [ -x "$HOME/.claude/scripts/kanban-status.sh" ]` vira
   `"$(dirname "$0")/kanban-status.sh"` — a barra acha o kanban **ao lado de si mesma**, onde quer
   que o par tenha sido copiado (`.claude/` do projeto ou `~/.claude/orq/`). É isso que satisfaz a
   R3 sem hardcode: settings aponta para a cópia, e a cópia acha a irmã.
2. **Campos documentados:** diretório via `.workspace.project_dir // .workspace.current_dir`
   (fallback `$PWD`); worktree via `.workspace.git_worktree // .worktree.name // empty`. O
   `.worktree.original_cwd` atual só existe em sessões `--worktree`.
3. **Guarda sem jq:** primeira linha útil — `command -v jq >/dev/null ||` → degrada executando só
  `exec sh "$(dirname "$0")/kanban-status.sh" "$PWD"`. A barra nunca quebra por falta de jq; ela
   encolhe para o board.
4. **Sem `$HOME` hardcoded, sem cruft:** remover a linha comentada do rate-limit 7d; manter a
   semântica integral da barra dele (modelo · effort · contexto % · custo · rate-limit 5h com barra
   colorida ANSI · diretório · worktree · branch com staged/modified · board), incluindo o `date -r`
   (BSD) com fallback `date -d` (GNU) que já existe.

### "Uma coisa só": par co-localizado, não arquivo único (Decisão 8)

Manter **dois arquivos instalados como par indivisível** (`statusline.sh` + `kanban-status.sh`,
sempre copiados juntos, resolvidos por vizinhança). Fundir num arquivo só quebraria os três usos
standalone do `kanban-status.sh` — smoke test da FASE 5, `/orq:stack --verificar` e o bloco de
composição do Caso B (statusline alheia que só quer o board) — e duplicaria o awk do contrato em
dois lugares do repo (T-015 ensinou o custo de duas cópias divergirem). "Uma coisa só" se cumpre na
experiência: **uma instalação, uma barra**.

### Marca de versão nas cópias (emenda aprovada da Decisão 2)

Ao copiar, o init insere como linha 2 (após o shebang), nas duas cópias:
`# orq v<versão> — instalado por /orq:init em <AAAA-MM-DD>; fonte: orq/scripts/<nome>. Não editar à mão; re-sync: /orq:init --reinstalar`
O `--reinstalar` compara o stamp com a versão do plugin **e** faz `diff` contra a fonte; divergiu →
propõe re-sync (não aplica sozinho). A fonte no plugin **não** leva stamp de versão (senão todo
bump exigiria editar os scripts — o stamp é escrito na cópia, no momento da cópia).

### A árvore de decisão (conteúdo do novo passo 4 da FASE 4)

1. Ler os três arquivos de settings (R1); montar a visão: qual escopo tem `statusLine`, qual é o
   efetivo. **[v2, obrigatório em TODO init]** No mesmo passe, **legacy check**: qualquer
   `statusLine` cujo comando aponte para `plugins/cache` ou para caminho contendo `orq/scripts/`
   fora do projeto → relatar como instalação defeituosa de versão antiga e **propor** migração
   para o esquema novo (não decidir sozinho).
2. **Caso A — o efetivo já integra o board** (comando ou o script que ele invoca contém
   `kanban-status` ou `KANBAN.md`; seguir o caminho e ler o arquivo): **não fazer nada**; relatar
   "sua statusline já mostra o board".
3. **Caso B — existe statusline, sem o board:** **não gravar chave** (R2). Mostrar o bloco a
   acrescentar ao script existente (modelo abaixo) + o comando de cópia do `kanban-status.sh` para
   caminho estável fora do plugin (`~/.claude/scripts/` se a statusline efetiva é global —
   recomendação, R4; `.claude/` do projeto se é do projeto). Script dentro do projeto + dono
   aprovou na conversa → aplicar (Decisão 6, aprovada); fora do projeto → só mostrar. Mencionar em
   uma linha que a barra completa do Orquestra existe como alternativa — **nunca** propor
   substituição da statusline dele.
   ```sh
   # Kanban do projeto (memory/wiki/KANBAN.md) — vazio se não houver quadro
   kanban_str=""
   if [ -x "<caminho-da-cópia>/kanban-status.sh" ]; then
     kanban_str=$(sh "<caminho-da-cópia>/kanban-status.sh" "<var-de-dir-que-o-script-já-extrai; senão $PWD>" 2>/dev/null)
   fi
   [ -n "$kanban_str" ] && kanban_str=" | ${kanban_str}"
   ```
4. **Caso C — nenhuma statusline em escopo nenhum** **[v2: instala a barra completa]**, com
   aprovação (pergunta na interação única da FASE 3, incluindo a escolha de escopo se D7 aprovada):
   - **Com `jq` na máquina** (`command -v jq`):
     - *escopo projeto (default):* copiar `${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh` **e**
       `${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh` → `.claude/` do projeto (par completo,
       `chmod +x`, stamp); gravar em `.claude/settings.local.json`:
       `{"statusLine":{"type":"command","command":"sh \"<abs-projeto>/.claude/statusline.sh\"","padding":0}}`
       (a substituição de `${CLAUDE_PLUGIN_ROOT}` funciona aqui porque `init.md` é componente de
       plugin em execução; caminho absoluto é aceitável porque o arquivo é local da máquina).
     - *escopo usuário (só com D7 aprovada + aprovação explícita e separada na conversa, nomeando
       os arquivos):* par em `~/.claude/orq/` (diretório próprio — não colide com nada do usuário);
       chave em `~/.claude/settings.json` com `command: "sh \"$HOME/.claude/orq/statusline.sh\""` —
       edição **só-adiciona** da chave `statusLine` (a pré-condição do Caso C garante que ela não
       existe; nenhuma outra chave é tocada).
   - **Sem `jq`** (Decisão 9): instalar só o ramo kanban — desenho da v1: copiar
     `kanban-status.sh` → `.claude/kanban-status.sh` (stamp) e gravar em `settings.local.json`
     `command: "sh \"<abs-projeto>/.claude/kanban-status.sh\" \"<abs-projeto>\""` (sem jq por
     desenho, argumento explícito elimina cwd). Relatar: "instale `jq` e rode
     `/orq:init --reinstalar` para a barra completa". **Nunca instalar jq por conta própria**
     (regra do `/orq:stack`: nada entra na máquina sem aprovação).
5. **Idempotência:** rodar de novo cai no Caso A (a barra instalada contém `kanban-status`) — nada
   duplica. Dizer no texto.

## Passos (cada um verificável)

1. **[v2] Criar `orq/scripts/statusline.sh`** — derivado de `~/.claude/statusline.sh` com as 4
   generalizações da seção "O asset". Verificação (teste de mesa, os três obrigatórios):
   (i) `echo '<mock JSON com model/workspace/context_window>' | sh orq/scripts/statusline.sh`
   renderiza as duas linhas com board; (ii) `echo '{}' | sh …` degrada sem erro (exit 0);
   (iii) com `jq` fora do PATH (`env PATH=/usr/bin:/bin sh -c …` num PATH sem jq ou stub), a saída
   é só o board via irmã. Nenhum `$HOME` nem caminho absoluto no fonte (`grep` volta vazio).
2. **`orq/commands/init.md`, FASE 4, passo 4 (linhas 195-197)** — substituir pela árvore v2
   (R1-R4 emendada + legacy check no passo 1 + Casos A/B/C com templates + stamp + idempotência).
   Verificação: leitura hostil não acha segunda interpretação para "onde checar", "quando gravar",
   "que caminho usar", "quando aplicar vs mostrar", "quando tocar `~/.claude/`".
3. **`orq/commands/init.md`, FASE 3** — a pergunta da statusline entra na interação única (com a
   escolha de escopo se D7 aprovada), para não contradizer "decisões em UMA interação".
   Verificação: o passo 4 não abre pergunta nova fora da FASE 3.
4. **`orq/commands/init.md`, FASE 5** — smoke de settings (v1) + teste da barra instalada:
   *(i)* `jq .statusLine` dos três escopos — nenhuma chave nova em settings do projeto se já havia
   statusline em qualquer escopo; *(ii)* nenhum comando gravado contém `plugins/cache` nem caminho
   de repo do plugin; *(iii)* se instalou: `echo '{"workspace":{"project_dir":"<abs>"}}' | sh
   <cópia-instalada>` imprime barra não-vazia. Verificação: os três são comandos, não juízo.
5. **`orq/commands/init.md`, Regras, bullet `--reinstalar`** — re-sync por stamp+diff das cópias
   instaladas (o legacy check saiu daqui para o passo 1 da árvore, que roda sempre). Verificação:
   o texto especifica o formato exato do stamp e o comando de comparação.
6. **`orq/scripts/lint-coerencia.py`** (Decisão 3, aprovada) — tripwire: arquivo de `orq/` que
   contém `statusLine` deve mencionar os três escopos (`settings.local.json`,
   `.claude/settings.json`, `~/.claude/settings.json`). Verificação: lint falha ao remover uma das
   menções do init.md; passa no repo pós-edição. (A citação do novo
   `${CLAUDE_PLUGIN_ROOT}/scripts/statusline.sh` no init.md já cai no guarda existente de
   caminhos citados → o arquivo tem que existir.)
7. **Bump 0.19.0 → 0.20.0 nos quatro lugares** (Decisão 4, aprovada) + 2-3 linhas no README sobre
   a barra distribuída (o orq-docs cuida no ciclo). Mesmo commit; push/release só com ok do dono.
8. **Memória (checkpoint pós-implementação):** gotcha novo ("settings de projeto vencem o global:
   diff aditivo desliga comportamento global sem tocar arquivo" + "varredura rasa dá falso
   negativo: a de 1 nível não achou o segundo projeto afetado"); log; board; página
   `arquitetura.md` ganha o asset novo.

## Como verificar sem quebrar de novo

**Com todas as letras (mantido da v1): `claude plugin validate --strict` e `lint-coerencia.py` NÃO
pegam este bug** — o defeito vive na interação instrução × estado do host. O que faz o papel deles:

1. **Tripwire do lint** (passo 6) — pega a regressão textual (escopo sumir da instrução).
2. **Testes de mesa do asset** (passo 1) — mecânicos, rodáveis no repo, sem release.
3. **Teste comportamental pós-release, cenário A (o que teria pego o incidente):** na máquina do
   dono (que TEM statusline global), projeto scratch (`git init` em dir temporário) → `/orq:init` →
   o init relata Caso A; `jq .statusLine` nos settings do scratch retorna `null` nos dois; a barra
   do dono continua rica no scratch. **[v2]** E o legacy check: plantar no scratch um
   `.claude/settings.json` com `statusLine` apontando para `plugins/cache/...` → o init acusa e
   propõe migração.
4. **Cenário C (máquina virgem) não é testável nesta máquina** — a global do dono existe. Cobrir
   por leitura hostil no review + os testes de mesa do passo 1, e registrar como limitação.

## Critério de aceite

- [ ] `claude plugin validate ./orq --strict` e `python3 orq/scripts/lint-coerencia.py .` passam.
- [ ] `orq/scripts/statusline.sh` existe e passa os três testes de mesa do passo 1; `grep` de
      `$HOME`/caminho absoluto no fonte volta vazio.
- [ ] O novo passo 4 cumpre a checklist da v1 (escopos enumerados; "existe" = qualquer escopo;
      proibições R2/R3; Casos A/B/C; fronteira R4 emendada; idempotência) **+** stamp de versão
      **+** legacy check no passo que roda em todo init.
- [ ] FASE 3 contém a pergunta (interação única); FASE 5 tem o smoke com os três itens executáveis.
- [ ] Review hostil não encontra dupla interpretação; painel confirma.
- [ ] Pós-release + restart: cenário A passa (Caso A relatado, `statusLine` nulo no scratch, barra
      rica intacta) e o legacy check plantado é acusado.
- [ ] O dono valida usando o produto (card fecha em VALIDATE, não no commit).

## Escopo

**Dentro:** `orq/commands/init.md` (FASES 3, 4, 5, Regras) · **novo** `orq/scripts/statusline.sh` ·
`orq/scripts/lint-coerencia.py` (tripwire) · bump quádruplo + README · memória.
**Fora:** IVA e prompts-byia-clientes (revertidos; sobra **uma pendência de verificação** — ver
Riscos 8) · T-029 (gate geral de caminhos; o tripwire daqui é estreito e não o substitui) ·
redesenho do `kanban-status.sh` · **qualquer edição em `~/.claude/` nesta tarefa** (a atualização
da cópia antiga dele é a Decisão 5, aprovada, mas quem aplica é ele) · statusline para hosts
não-Claude (Codex/Kimi não têm statusLine).

## Riscos

Mantidos da v1: **(1)** projetos legados fora das varreduras — agora com mitigação forte (legacy
check em todo init); **(2)** Caso B aplicado errado — binário: só script dentro do projeto + 
aprovação; **(3)** drift das cópias — agora detectável (stamp + diff no `--reinstalar`);
**(4)** caminho absoluto em `settings.local.json` quebra se o projeto mudar de pasta — local da
máquina, smoke acusa; **(5)** tripwire é heurística — custo baixo; **(6)** init.md cresce —
mitigado pela pergunta na FASE 3.

Novos na v2:
7. **Dependência de `jq` na barra completa.** Mitigada em duas camadas: ramo de instalação sem jq
   (Caso C degrada para kanban-only) e guarda em runtime no próprio script (jq some depois → a
   barra encolhe para o board em vez de quebrar). Resíduo: máquina sem jq não ganha a barra
   completa até instalar e re-rodar.
8. **Asset derivado da máquina do dono.** O fonte usa `.worktree.original_cwd`/`.worktree.name`,
   que a doc restringe a sessões `--worktree` — na máquina dele "funciona" possivelmente por efeito
   colateral (fallback de `cd ""` para o cwd). A generalização troca pelos campos documentados;
   risco de comportamento visual levemente diferente do que ele tem hoje (ex.: worktree via
   `workspace.git_worktree`) — o VALIDATE dele pega. E **pendência fora deste repo:** confirmar que
   a reversão no `prompts-byia-clientes` foi **commitada** — a chave entrou por commit (`fa1363c`);
   reverter só o working tree deixa o defeito no histórico pronto para voltar num clone/reset.
9. **Escrita em `~/.claude/settings.json` no escopo usuário (se D7 aprovada):** editar JSON global
   de terceiros é o passo mais delicado do plano — mitigação: pré-condição "nenhuma statusline em
   escopo nenhum", edição só-adiciona da chave, aprovação nomeando o arquivo, e o dono desta
   máquina nunca cai nesse ramo (Caso A).
10. **A barra distribuída vira produto** — todo ajuste futuro nela exige bump + re-sync das cópias
    instaladas (é o custo da emenda da Decisão 2; o stamp torna o custo visível em vez de
    silencioso).

## Decisões do dono

### Aprovadas (1-6, em 2026-08-07 — não re-perguntar)

1. ✅ Chave do Caso C em `.claude/settings.local.json` (não no compartilhado).
2. ✅ Cópia do script como caminho canônico — **com a emenda do Manager:** stamp de versão na
   cópia, drift detectável (incorporada nos passos 1, 5 e na seção "Marca de versão").
3. ✅ Tripwire no `lint-coerencia.py`.
4. ✅ Bump 0.20.0 + release nos quatro lugares (push/publicação continuam exigindo o ok final).
5. ✅ Atualizar `~/.claude/scripts/kanban-status.sh` com a versão do plugin — **ele aplica**, não
   nós. Nota v2: a antiga só diverge em board malformado; ainda assim vale, pelos guardas `⚠N`.
6. ✅ Caso B com script do projeto: aplicar com aprovação explícita na conversa.

### Novas (7-9 — precisam de resposta)

7. **Alcance do Caso C — oferecer escopo de usuário?** Em máquina sem statusline nenhuma, o init
   pergunta "só neste projeto (default) ou para todos os projetos desta máquina?"; o escopo usuário
   grava `~/.claude/settings.json` + par em `~/.claude/orq/`, sempre com aprovação explícita e
   separada, nomeando os arquivos. *Rec.:* **sim, oferecer com default projeto** — é a única
   leitura que cumpre "todos os projetos" numa máquina nova; a tripla guarda (pré-condição Caso C +
   pergunta separada + diretório próprio `~/.claude/orq/`) contém o risco. Trade-off: o init passa
   a poder escrever fora do projeto — a R4 emendada existe para isso ser exceção nomeada, nunca
   padrão. *(Na máquina do dono este ramo nunca dispara — a global dele existe → Caso A.)*
8. **"Uma coisa só": par co-localizado vs arquivo único.** *Rec.:* **par co-localizado**
   (`statusline.sh` + `kanban-status.sh` sempre copiados juntos, resolução por vizinhança) — fundir
   quebraria os três usos standalone do kanban (smoke FASE 5, `/orq:stack`, composição Caso B) e
   duplicaria o awk do contrato (T-015 já cobrou o preço de duas cópias). Trade-off: "uma coisa só"
   vira experiência (uma instalação, uma barra), não um único arquivo no disco.
9. **Política de `jq`.** *Rec.:* **degradar sem instalar** — sem jq, o Caso C instala só o ramo
   kanban e informa como obter a completa; o script ainda carrega guarda de runtime. Nunca instalar
   jq automaticamente (fere a regra do stack: nada entra na máquina sem aprovação). Trade-off:
   máquina sem jq fica com a barra mínima até o usuário agir. Alternativas rejeitadas: exigir jq
   (init falharia por um luxo) e reescrever o parse sem jq (JSON em shell puro é armadilha
   conhecida; 12 campos em awk/sed é dívida certa).

## Autocrítica — o que estou assumindo sem ter verificado

1. **`${CLAUDE_PLUGIN_ROOT}` ausente no runtime da statusline** — três evidências de doc, zero
   teste empírico (teste de 1 linha descrito na v1 segue disponível). O desenho é robusto às duas
   hipóteses.
2. **cwd do processo da statusline** — não documentado; nada no desenho depende dele.
3. **O asset generalizado não existe ainda** — os três testes de mesa do passo 1 são a prova; o
   que testei foi o fonte do dono (mock cheio e `{}`), não a derivação.
4. **Mecanismo exato do `{}` funcionar na barra dele** — o dir correto apareceu provavelmente por
   `cd ""` cair no cwd; não rastreei por shell. A generalização não herda essa dependência.
5. **Varredura de legado ainda pode estar incompleta** — a v1 assumiu completa e errou (1 nível);
   a de 6 níveis pode não cobrir projetos fora de `~` ou mais fundos. Por isso o legacy check roda
   em **todo** init, para sempre.
6. **Reversão do `prompts-byia-clientes` commitada?** Não verifiquei — pendência nomeada (Risco 8).
7. **`.claude/settings.local.json` auto-gitignored pelo Claude Code** — comportamento conhecido,
   não re-verificado na doc; se falso, o Caso C projeto precisa gravar `.gitignore` junto (uma
   linha no passo 2 resolve; o incidente do prompts-byia-clientes prova que settings de projeto
   **vão** parar no git).
8. **Campos `rate_limits`/`cost` presentes em qualquer instalação** — documentados, mas podem vir
   vazios (plano API vs assinatura); a barra já degrada segmento a segmento (`// empty`), o mock
   `{}` provou.

---

## RETOMAR AQUI *(SUPERADO — o vivo é o último do arquivo)*

v2 pronta, não implementada. Decisões 1-6 aprovadas (emenda da 2 incorporada). Próxima ação:
**dono responde as Decisões 7-9** (recomendações dadas) → card READY → `/orq:implement-next`
executa os passos 1-8 na ordem (o 1 antes do 2: o init.md cita o asset; o 7 só com ok do bump) →
review hostil com o briefing do CLAUDE.md → release 0.20.0 → teste comportamental cenário A +
legacy check plantado → VALIDATE do dono. Pendência paralela para o Manager: confirmar reversão
**commitada** no `prompts-byia-clientes` (Risco 8).

---

## 🔴 2026-08-07 — DUAS RODADAS DE PAINEL, CINCO REPROVAÇÕES. O desenho é a causa.

**Rodada 1** (Kimi · Codex · interno): 3/3 REPROVADO — 3 bloqueadores, 9 riscos. Corrigidos todos.
**Rodada 2** (Codex · interno): 2/2 REPROVADO — **bloqueadores novos, criados pelas correções**.

**O padrão, e é ele que importa:** os bloqueadores das duas rodadas caem em **interseções de ramos**
e em **guardas que tratam sintoma**. Criou-se o "Caso A-legado" na rodada 1; a rodada 2 achou o
mesmo buraco um ramo adiante (estado que é Caso B **e** legado ao mesmo tempo, sem ramo). Uma árvore
com 4 ramos + um "legado" transversal produz interseções mais rápido do que se consegue cobrir.

**Achados da rodada 2 que independem do desenho** (corrigir de qualquer forma):
1. 🔴 **`statusline.sh`: o guarda `[ -x ]` está errado** — a irmã é invocada via `sh`, o bit de
   execução é **irrelevante**. Pior: o `init.md` documentou o defeito como lei da natureza e criou
   um item de smoke para o sintoma. Correção: `[ -r ]`, e o smoke de `chmod` deixa de precisar
   existir. Sem `jq` + irmã sem `+x` = **barra totalmente vazia**, exit 0.
2. 🔴 **O merge (B3) não dá o comando, e o comando óbvio destrói o arquivo:** `jq '.statusLine = …'
   arquivo > arquivo` trunca para 0 byte (o shell abre o redirect antes do `jq` ler) — **é
   literalmente o dano que o B3 existe para impedir**. Falta a forma segura (`> tmp && mv`).
3. 🔴 **O smoke incondicional (B2) fica vermelho no caminho feliz** e exige um snapshot "antes" que
   manda capturar **na FASE 5**, depois de a FASE 4 já ter gravado. Impossível de cumprir como
   escrito. Reintroduziu o alarme crônico que o próprio card curou em outro lugar.
4. 🔴 **O ramo "sem `jq`" é um beco sem saída:** ele instala kanban-only e manda "instale `jq` e rode
   `--reinstalar`" — mas o `--reinstalar` classifica Caso A e não faz nada. A receita escrita no
   arquivo é **no-op**. E contradiz a regra "o par, sempre junto, nunca um sem o outro" — sendo que
   o `statusline.sh` **já degrada sozinho** sem `jq`, tornando o ramo inteiro redundante.
5. 🟠 **Caso B com statusline inline** (`command` sem arquivo de script) não tem resposta: o critério
   é "onde mora o ARQUIVO", e não há arquivo. Uma das leituras reescreve o `command` do dono.
6. 🟠 **Tripwire:** o implementer tinha razão contra o revisor na regex (comprovado por teste), mas a
   dele conta `$HOME/.claude/settings.json` como escopo de projeto → um `init.md` que **pare de
   nomear o escopo de projeto** passa verde. E `jq '.statusLine |= …'` e `. + {statusLine:…}` — as
   duas formas canônicas de merge em `jq` — não disparam.
7. 🟠 **Caso C é definido pela ausência da CHAVE, não dos ARQUIVOS:** `.claude/*.sh` são versionados;
   um colega que clona e roda o init sobrescreve arquivos **rastreados** sem aviso.
8. 🟡 **Segurança:** `awk "BEGIN { printf \"%.2f\", $total_cost }"` interpola dado no **código** do
   awk — execução arbitrária a cada render (provado com PoC; exige host comprometido, daí baixo).
   Correção de uma linha: `awk -v c="$total_cost" 'BEGIN { printf "%.2f", c+0 }'`.

**RETOMAR AQUI (substitui o anterior — SUPERADO em 2026-08-08: o dono RECUSOU esta simplificação;
ver o plano v3 abaixo):** proposta de **simplificação radical** aguardando o dono —
regra única "existe statusline em qualquer escopo → o init NUNCA escreve, só relata e mostra";
instalar só quando não há nada; legado vira relato, nunca migração automática; o ramo sem `jq`
morre (o script já degrada sozinho). Isso apaga os ramos A-legado, B-legado, o critério
"aplicar vs mostrar" e o beco sem saída — as quatro fontes dos bloqueadores das duas rodadas.
**Custo a declarar ao dono:** a Decisão 6 (aplicar a composição com aprovação) vira "só mostrar".

---

# PLANO v3 (2026-08-08) — compor dentro da barra existente

**Planner:** Fable. Substitui o Caso B da v2 **e** a proposta de simplificação radical. As Decisões
1-6 aprovadas continuam valendo; a **9 é substituída pela 12** (abaixo, com a política preservada).

## Problema (o que a v3 ataca — além da causa raiz, que não mudou)

A causa raiz do incidente segue a mesma (chave de projeto vence a global; o passo 4 era
subespecificado). O que a v3 ataca de novo é **a causa das cinco reprovações**: a v2 pedia **juízo
em interseções** — "de quem é o script?", "onde mora o arquivo?", "aplicar ou mostrar?", "é legado
E Caso B ao mesmo tempo?" — e cada correção criava a interseção seguinte. E o dono recusou as duas
saídas que levei, com argumento:

> *"Quando pedir por script, já editar automaticamente dá o erro que apagou o que já existia.
> Mostrar o trecho para a pessoa preencher — a pessoa às vezes vai fazer errado. O ideal seria que
> o script pesquisasse se já existisse uma board, ver qual é a arquitetura dessa board, e incluir
> nela a parte das tasks."*

**Premissa corrigida com ele:** o dano do incidente veio de **gravar a chave no settings do
projeto** (precedência), nunca de editar script — o produto jamais editou o `~/.claude/statusline.sh`
dele. Compor dentro de um script existente é operação **nova**, e é diferente do "aplicar" que o
painel derrubou: aquele exigia *classificar de quem é o script* para decidir se podia mexer; este
exige *provar que a edição preservou tudo* — e prova é verificável, classificação não.

⚠️ **Na máquina do dono, nada disto dispara.** A barra dele já mostra o board (chama
`~/.claude/scripts/kanban-status.sh` e concatena) → cai na folha F3 ("já tem") e o init não faz
nada. A composição vale para **máquina nova, outra pessoa, barra sem board**. Que ninguém prometa a
ele um efeito visível na barra dele — o que ele valida é o cenário de teste (abaixo), não a barra
dele mudando.

## Solução — a tese em uma frase

**Trocar juízo por propriedade verificável.** Onde a v2 pedia classificação, a v3 pede: (a) uma
árvore de **4 folhas mutuamente exclusivas**, decididas por duas perguntas em sequência, sem
modificador transversal; (b) um procedimento de composição cuja "compreensão do script" encolhe até
caber em **checagens binárias** (T1-T6); (c) uma **prova experimental** no lugar de confiança na
leitura — executar antes×depois com entrada fixa e exigir que a saída antiga seja **prefixo
byte-a-byte** da nova. Se o entendimento estiver errado, o experimento reprova e a reversão
automática desfaz — o erro custa um backup restaurado, nunca uma barra quebrada.

Alternativas recusadas: *só mostrar* (recusada pelo dono — a pessoa erra ao aplicar) · *editar o
`printf` existente* (ver Decisão 11 — é a classe de erro que o painel puniu duas vezes) · *manter a
árvore da v2 com mais um remendo* (a segunda rodada provou que remendo cria a interseção seguinte).

### O que muda da v2 → v3

| v2 | v3 |
|---|---|
| Caso B: mostrar o bloco; aplicar só se o script mora no projeto | **Compor dentro do script** (qualquer localização), com as 5 travas; "mostrar" vira **só** o fallback de erro, sempre com o motivo dito |
| "Caso A-legado" transversal — a fonte dos bloqueadores das 2 rodadas | Legado vira **folha própria (F2), avaliada antes** de A/B; sem modificador transversal, sem interseção |
| "Onde mora o arquivo" decide aplicar vs mostrar | Localização decide só **destino da cópia** e **tipo de aprovação** (projeto = pergunta 4 normal; fora = aprovação nominal, D10) |
| Caso C sem `jq` instala kanban-only (beco sem saída, achado 4) | **O ramo morre**: o par é instalado sempre; o `statusline.sh` degrada sozinho sem `jq` e se completa **sozinho** quando `jq` aparecer — sem re-run |
| Smoke da FASE 5 com "antes" impossível + item de `chmod` | "Antes" = **registro feito na FASE 1**; itens condicionais à folha executada; o item de `chmod` morre (achado 1) |
| Bloco de composição com `[ -x ]` | Bloco novo (P3): sem guarda de bit, compatível com `set -e`, exit 0 nos dois ramos — **verificado em mesa em 2026-08-08** |

**Continua da v2 (aproveitado):** o asset `orq/scripts/statusline.sh` (com 2 correções) · R1 e R3 ·
a mecânica do Caso C (merge + stamp + escopos, com 2 correções) · o re-sync do `--reinstalar` · o
tripwire do lint (com 2 correções) · o bump 0.20.0 já feito nos quatro lugares.

### Regras invioláveis v3

- **R1 (mantida)** — "existe statusline" = chave em qualquer dos três arquivos; o de maior
  precedência presente é o efetivo.
- **R2 (emendada)** — havendo statusline em qualquer escopo, **nenhuma chave é ADICIONADA em
  escopo nenhum**. A única escrita de settings permitida com statusline existente é **substituir o
  valor** da chave efetiva **no mesmo arquivo**, exclusivamente na folha F2 (instalação nossa
  defeituosa), com aprovação nominal. Compor (F4) **nunca** toca settings.
- **R3 (mantida)** — nunca gravar em settings caminho para dentro do plugin; sempre cópia estável.
- **R4 (v3)** — o init escreve dentro do projeto por padrão. `~/.claude/` só em **dois ramos
  nomeados**, sempre com aprovação nominal citando cada arquivo: (a) Caso C escopo usuário (D7);
  (b) composição cujo alvo real mora fora do projeto (D10).
- **R5 (nova — as 5 travas, como regra, não como boa prática)** — nenhuma edição de script sem:
  backup carimbado **antes** · análise T1-T6 verde · validação por experimento **depois** ·
  reversão automática em qualquer falha, com o motivo dito.

## A árvore v3 — quatro folhas, duas perguntas, zero interseção

Ler os três escopos (R1); montar a visão (efetivo + sombreados) e **registrá-la no relatório da
FASE 1** — esse registro é o "antes" que a FASE 5 compara (conserta o achado 3). Então, **na
ordem, parando na primeira folha que casar**:

- **F1 — Não há chave em escopo nenhum → INSTALAR** (o Caso C da v2, com as correções dos achados
  2 e 7 e sem o ramo `jq` — ver "Correções ao Caso C").
- **F2 — A chave EFETIVA aponta para dentro do plugin** (`plugins/cache` ou `orq/scripts/` fora
  deste projeto) **→ INSTALAÇÃO NOSSA, DEFEITUOSA**: propor **reinstalação** — copiar o par para o
  destino do mesmo escopo da chave (`.claude/` do projeto ou `~/.claude/orq/`), com stamp, e
  **substituir** o `command` da chave existente **naquele mesmo arquivo** (R2 emendada). Só com
  aprovação nominal (pergunta 4 da FASE 3); recusado → relata o risco e não toca. *Mostrar o board
  ou não é irrelevante aqui: a barra é nossa e quebra no próximo update — não há o que "compor" num
  script que é o nosso próprio `kanban-status.sh` do cache.*
- **F3 — A barra efetiva mostra o board** (o comando, ou o script que ele invoca, contém
  `kanban-status` ou lê `KANBAN.md`; seguir o caminho e ler) **→ NADA**. Relatar "sua statusline já
  mostra o board". É a folha do dono, em todos os projetos dele.
- **F4 — Existe barra efetiva, do usuário, sem o board → COMPOR** (o procedimento abaixo). O
  fallback interno do procedimento é **total**: qualquer estado que F4 não saiba tratar termina em
  "mostrar o bloco + motivo", nunca em estado sem resposta.

**Chaves sombreadas** (escopo de menor precedência também tem chave): **relato, nunca ação** — nem
compor nem substituir um script que não está valendo. Sombreada apontando para o plugin → relatar
como pendência com o comando manual de conserto. Isso fecha a interseção "legado que não é o
efetivo", que a rodada 2 encontraria.

**Totalidade (o argumento, para o painel):** F1 cobre "sem chave"; com chave, F2/F3/F4 particionam
por dois predicados binários avaliados em ordem (procedência → board). Estado com chave e script
inexistente/ilegível: não é F2 (procedência ok), não é F3 (não dá pra confirmar board) → F4 → T2
falha → fallback com motivo ("o comando aponta para arquivo que não existe"). Nenhum estado fica
sem folha; nenhuma folha depende de outra.

## A pergunta central — como o init prova que entendeu, ANTES de escrever

**Ele não prova que "entendeu a arquitetura" lendo — ele encolhe o que precisa entender até caber
no que dá para verificar, e prova o resto por experimento.** Três camadas:

1. **A estratégia de inserção exige compreensão mínima por construção.** O bloco entra **no fim do
   fluxo** (EOF, ou antes de um `exit` final) e emite um **sufixo** na saída — não edita nenhuma
   linha existente, não precisa achar o `printf`, não precisa entender como a barra é montada.
   (A barra do dono tem **dois** `printf` finais em if/else — até o caso real mais simples já
   quebraria "achar A linha que imprime". Ver Decisão 11.)
2. **O que precisa ser verdade vira checagem binária (T1-T6, abaixo).** Cada uma tem resposta
   sim/não; cada "não" nomeia o motivo do fallback. Não existe "o modelo lê e se vira": ou o
   estado passa nas seis, ou o init **diz por que desistiu** e mostra o bloco.
3. **A prova final é o experimento, não a leitura.** Rodar o script original 2× com stdin fixo
   (T6, que também captura o "antes"); depois da inserção, rodar de novo e exigir: saída antiga é
   **prefixo byte-a-byte** da nova + o sufixo contém o board (`📋` ou `⚠`) no mock rico + exit 0.
   Se a leitura enganou (um `exec` no meio, `exit` escondido nos ramos, montagem exótica), o bloco
   não executa, o sufixo não aparece, a validação reprova e a trava 5 reverte.

**"Reconhecer que NÃO entendeu"** = qualquer T falhar **ou** o experimento reprovar. O procedimento
não pede juízo em interseção nenhuma — pede propriedades em sequência. É exatamente o que as duas
rodadas de painel cobraram e a v2 não tinha.

## O procedimento de composição — novo arquivo `orq/compor-statusline.md`

Mora em arquivo próprio do plugin (mesmo padrão do `stack.md`: o init manda ler
`${CLAUDE_PLUGIN_ROOT}/compor-statusline.md` na hora de executar F4 — o lint já garante que
citação de caminho existe). O `init.md` fica com a árvore + as travas em resumo; a regra
operacional vive num lugar só, sem duplicação. **P0-P2 rodam na FASE 1 (read-only)** — é o que
permite a pergunta 4 da FASE 3 já mostrar o bloco exato e os arquivos nomeados; **P3-P7 só rodam
na FASE 4, depois da aprovação**.

**P0 — Resolver e qualificar o alvo (read-only; T1-T6):**
- **T1** `statusLine.type == "command"`. Outro tipo → fallback (motivo: tipo não suportado).
- **T2** Tokenizar o `command`: descartar prefixos `NOME=valor`; reconhecer interpretador inicial
  (`sh`/`bash`/`zsh`, com ou sem caminho); o token seguinte deve resolver (expandindo `~` e
  `$HOME`) para **arquivo existente e legível**. Symlink → `realpath`; o alvo é o arquivo real, e é
  **ele** que a aprovação nominal nomeia. Zero ou mais de um candidato, ou pipe/`&&`/subshell no
  nível de cima, ou **comando inline sem arquivo** (achado 5) → fallback (motivo: "não consigo
  isolar um único arquivo de script").
- **T3** O alvo é shell: shebang `#!/…/(sh|bash|zsh)` (ou `env` deles), ou sem shebang com
  interpretador shell no T2. Python/Node/binário (byte NUL no arquivo) → fallback (motivo: "só sei
  compor shell; para <linguagem>, o trecho a adaptar é este").
- **T4** O alvo é gravável (`[ -w ]`). Não → fallback (motivo: permissão).
- **T5** Escolher o ponto: a última linha não-vazia e não-comentário é `exit`/`exit N` em coluna
  0 → inserir **antes** dela; senão → **EOF**. *De propósito, T5 não tenta provar que o fluxo
  chega lá* (exec no meio, exit nos ramos): esse é o papel do experimento (P5) — análise estática
  de fluxo em shell alheio é o juízo que este desenho existe para não fazer.
- **T6** Determinismo + captura do "antes": rodar o original **2× por mock** (mock rico — com
  `workspace.project_dir` apontando para o projeto atual — e `{}`), mesmo cwd (o projeto). As duas
  execuções de um mesmo mock diferem entre si → fallback (motivo: "sua barra não é reprodutível
  com entrada fixa; não consigo validar uma edição sem risco"). Iguais → a saída é o "antes".
- **Colisão de nome:** `grep -c 'orq_kanban'` no alvo > 0 → fallback (regra fechada; na prática
  não ocorre).

**P1 — Variável de diretório (nunca causa fallback):** procurar no alvo **exatamente uma** linha
casando `NOME=$(… (jq|grep|sed) … (project_dir|current_dir|cwd) …)`. Achou → o bloco usa
`"$NOME"`; senão → `"$PWD"`. Os dois degradam com segurança (pior caso: board vazio ou do
diretório errado — visível e reversível; nunca barra quebrada). `$PWD` como cwd do render é
empírico, não documentado — declarado na autocrítica.

**P2 — Cópia do `kanban-status.sh`** (a fonte no plugin não serve — R3): alvo dentro do projeto →
`.claude/kanban-status.sh`; fora → `~/.claude/orq/kanban-status.sh` (R4/D10). Stamp na linha 2
(formato da Decisão 2). **Guarda do achado 7:** destino já existe **sem** o nosso stamp → parar e
relatar (não sobrescrever arquivo que não é nosso); com stamp → recopiar é re-sync legítimo. Se o
destino é rastreado pelo git do projeto (`git ls-files --error-unmatch`), dizer na proposta que um
arquivo versionado será alterado.

**P3 — O bloco (exato, com sentinelas):**
```sh
# >>> orq: kanban no fim da barra (v<versão>, /orq:init <AAAA-MM-DD>) — para desfazer, apague daqui até '<<< orq'
orq_kanban=$(sh "<caminho-absoluto-da-cópia>/kanban-status.sh" "<"$VAR" de P1, senão "$PWD">" 2>/dev/null) || orq_kanban=""
[ -z "$orq_kanban" ] || printf " | %s" "$orq_kanban"
# <<< orq
```
Três propriedades, **verificadas em mesa em 2026-08-08** (fixtures no scratchpad): sob `set -e`
com a cópia ausente, a barra sai intacta e exit 0 (o `|| orq_kanban=""` protege a atribuição; a
forma `[ -z … ] || printf` retorna 0 nos dois ramos — `[ -n … ] && printf` retornaria 1 com board
vazio e derrubaria script com `set -e`); com a cópia presente, o board concatena na mesma linha; e
`sh -n`/`zsh -n` aceitam. Sem `[ -x ]`/`[ -r ]`: cópia ausente/ilegível já degrada a vazio pelo
`2>/dev/null` + `||`.

**P4 — Escrita (travas 1 e 3):** backup `cp -p <alvo> <alvo>.orq-bak.AAAAMMDD-HHMMSS` no mesmo
diretório (o backup **nunca** é apagado por nós). Ponto = EOF → append em **uma** chamada (`>>`,
preserva inode/modo/dono); ponto = antes do `exit` final → conteúdo novo em arquivo temporário
**no mesmo diretório**, modo espelhado do original, e `mv` (rename atômico — o host pode invocar a
barra no meio da edição; o arquivo nunca fica meio-escrito).

**P5 — Validação (trava 4):** (i) sintaxe com o interpretador do shebang (`sh -n`/`bash -n`/
`zsh -n`); (ii) executar o composto com os dois mocks de T6, mesmo cwd: **prefixo byte-a-byte**
do "antes" correspondente + exit 0 nos dois + no mock rico o sufixo contém `📋` ou `⚠` (a FASE 4
já criou o board do projeto no passo 1, então o sufixo é exigível; no `{}` exige-se só prefixo +
exit 0). Qualquer falha → P6.

**P6 — Reversão (trava 5):** `cp -p` do backup de volta + `cmp` backup×alvo provando restauração
byte-idêntica; relatar **o motivo exato** da falha; cair para "mostrar o bloco". Se a própria
restauração falhar (disco, permissão): **parar tudo**, dar o caminho do backup e o comando de
restauração — nunca tentar de novo por conta.

**P7 — Relato:** o que foi editado (arquivo real), o caminho do backup, como desfazer (apagar
entre as sentinelas), e — alvo fora do projeto — o aviso: "isto muda a barra de **todos** os
projetos desta máquina; em projeto sem board o bloco não imprime nada".

**Mapa travas → passos:** trava 1 = P4 (backup) · trava 2 = folha F3 + sentinelas (script composto
contém `kanban-status` → próximo init cai em F3; nada duplica) · trava 3 = T5 + P3/P4 (redefinida —
ver Decisão 11) · trava 4 = P5 · trava 5 = P6.

## A tensão do `~/.claude/` — de frente

A v2 dizia "o init só escreve dentro do projeto; `~/.claude/` só no Caso C com D7". Mas **o caso
comum de barra sem board é a barra global** — é onde a do dono mora (`~/.claude/statusline.sh`), e
é a configuração que faz a barra valer em todos os projetos, que é o pedido dele desde o começo.
Restringir a composição ao projeto tornaria F4 **letra morta** exatamente no cenário para o qual
ela existe.

**Proposta (Decisão 10):** composição com alvo fora do projeto é o **segundo ramo nomeado** da R4
v3 — permitida, exigindo **aprovação nominal** na pergunta 4 da FASE 3, que nomeia: o arquivo real
a editar (symlink resolvido) · o bloco exato · o destino da cópia (`~/.claude/orq/kanban-status.sh`)
· o caminho do backup que será criado. Alvo dentro do projeto → a aprovação entra na pergunta 4
normal, sem cerimônia extra. **Não há terceira via**: ou o dono da máquina aprovou nomeando, ou é
fallback mostrar. (Settings continuam intocados na composição — a exceção de settings fora do
projeto segue sendo só o Caso C escopo usuário, D7.)

## Correções ao Caso C (folha F1) — achados 2, 4 e 7

- **Merge seguro escrito com todas as letras (achado 2):** nunca `jq … arquivo > arquivo` (trunca
  para 0 byte). Forma obrigatória no texto: `jq '. + {statusLine: …}' arquivo > arquivo.tmp &&
  jq . arquivo.tmp >/dev/null && mv arquivo.tmp arquivo` — valida o JSON resultante **antes** do
  `mv`; arquivo inexistente → criar com o objeto; JSON existente inválido → abortar e relatar, não
  escrever.
- **O ramo "sem `jq`" morre (achado 4; Decisão 12):** F1 instala **sempre** o par completo e grava
  a chave apontando para `statusline.sh`. Sem `jq` na máquina, o próprio script degrada para
  board-only (primeiro bloco dele, que extrai `project_dir` sem jq) e **se completa sozinho** quando
  `jq` aparecer — sem `--reinstalar`, sem receita no-op, sem violar "o par, sempre junto". Para a
  escrita do settings sem `jq`: o arquivo-alvo não existe → gravar o objeto completo direto;
  existe → **não editar JSON sem `jq`** — mostrar a chave a acrescentar e relatar (fallback
  honesto, mesmo padrão de F4). A política da Decisão 9 fica preservada: **nunca instalar `jq`**.
- **Destino ocupado (achado 7):** antes de copiar, se `.claude/statusline.sh` ou
  `.claude/kanban-status.sh` já existem **sem** o nosso stamp → parar e relatar (são arquivos de
  alguém — Caso C é ausência da CHAVE, não dos arquivos); com stamp → re-sync legítimo. Arquivo
  rastreado pelo git → dizer na proposta.

## Os 8 achados do painel — onde cada um entra

| # | Achado | Correção | Onde |
|---|---|---|---|
| 1 | 🔴 `[ -x ]` com invocação via `sh` | `[ -r ]` nas linhas 14 e 111 do asset; item de `chmod` sai do smoke | Passos 1 e 6 |
| 2 | 🔴 merge `> arquivo` trunca | forma `> tmp && jq . tmp && mv` obrigatória no texto | Passo 3 |
| 3 | 🔴 smoke com "antes" impossível | o "antes" é o registro da FASE 1; itens condicionais à folha | Passos 4 e 6 |
| 4 | 🔴 ramo sem `jq` = beco sem saída | o ramo morre; o script degrada e se completa sozinho | Passo 3 (D12) |
| 5 | 🟠 statusline inline sem arquivo | T2 → fallback com motivo (regra fechada, sem reescrever `command`) | Passo 2 |
| 6 | 🟠 tripwire: `$HOME/…` conta como projeto; `\|=` e `{statusLine:}` não disparam | lookbehind duplo `(?<!~/)(?<!\$HOME/)` + gatilho ampliado — **regex verificada em 2026-08-08, 11/11 probes** | Passo 7 |
| 7 | 🟠 Caso C ignora arquivos pré-existentes | guarda de destino por stamp + aviso de arquivo rastreado | Passo 3 |
| 8 | 🟡 injeção via awk interpolado | `awk -v c="$total_cost" 'BEGIN { printf "%.2f", c+0 }'` (linha 65) | Passo 1 |

## O que aproveita e o que joga fora (working tree da v2, não commitado)

**Aproveita (fica, com correção pontual):** `orq/scripts/statusline.sh` (achados 1 e 8) · FASE 1
lendo os três escopos (reescreve a classificação para F1-F4 + registro do "antes") · FASE 3 com a
pergunta na interação única (reescreve o conteúdo da pergunta 4) · mecânica do Caso C (achados 2 e
7; sem o ramo jq) · Regras/`--reinstalar` com stamp+`sed '2d'`+diff · tripwire do lint (achado 6) ·
bump 0.20.0 nos quatro lugares.

**Joga fora (reescreve):** o "Caso A-legado" da FASE 3/FASE 4 (vira folha F2) · o critério "onde
mora o arquivo" como decisor aplicar/mostrar (vira decisor de destino+aprovação) · o bloco template
do Caso B com `[ -x ]` (vira P3) · o ramo "sem jq" do Caso C · o item de `chmod` e o smoke
incondicional da FASE 5.

## Passos (ordenados; cada um verificável)

1. **`orq/scripts/statusline.sh`** — achado 1 (`[ -x ]` → `[ -r ]`, linhas 14 e 111) e achado 8
   (`awk -v`, linha 65). Verificação: os 3 testes de mesa da v2 **+ 2 novos**: (iv) irmã sem `+x`,
   com e sem `jq` no PATH → o board sai mesmo assim; (v) mock com
   `"total_cost_usd": "0;system(\"id\")"` → imprime `$0.00`-equivalente, nada executa.
2. **Criar `orq/compor-statusline.md`** — P0-P7/T1-T6 completos, com o bloco exato, os dois mocks
   inline e os comandos de backup/validação/reversão. Verificação: a bateria do passo 9 exercita
   cada regra; o lint confirma que a citação `${CLAUDE_PLUGIN_ROOT}/compor-statusline.md` no
   init.md resolve.
3. **`orq/commands/init.md`, FASE 4, passo 4** (hoje linhas ~225-316) — a árvore F1-F4 no lugar da
   atual: sai Caso A-legado, sai o ramo sem `jq`, entra R2-emendada/R5, F1 com merge seguro e
   guarda de destino, F4 delegando ao arquivo do passo 2. Verificação: leitura hostil — todo estado
   cai em exatamente uma folha; `grep -F '[ -x' orq/commands/init.md` volta vazio; `grep -c
   'sem .jq.' ` só sobrevive onde descreve a degradação do script, não instalação parcial.
4. **`orq/commands/init.md`, FASE 1** (hoje linhas ~43-52) — classificação F1-F4 + P0-P2 read-only
   + **registrar a visão dos três escopos como o "antes" da FASE 5**. Verificação: nenhuma escrita
   descrita na FASE 1.
5. **`orq/commands/init.md`, FASE 3, pergunta 4** (hoje linhas ~108-126) — reescrever: F2 nominal ·
   F4 dentro do projeto (aprovação na pergunta) vs fora (nominal, D10, nomeando arquivo real +
   cópia + backup) · Caso C com escolha de escopo (D7) · fallback já decidido = relato, não
   pergunta. Verificação: cada escrita da FASE 4 tem aprovação correspondente na FASE 3; nenhuma
   pergunta nova fora da FASE 3.
6. **`orq/commands/init.md`, FASE 5, item 5** (hoje linhas ~350-373) — reescrever: comparação
   contra o registro da FASE 1 (achado 3) · itens por folha executada · sai o gate de `chmod` ·
   entram os itens de composição: backup existe; `diff` backup×alvo mostra **só** o bloco;
   sentinela aparece exatamente 1×; resultado da validação P5 relatado. Verificação: nenhum item
   exige dado que não foi mandado capturar antes dele.
7. **`orq/scripts/lint-coerencia.py`** — achado 6: `ESCOPO_PROJETO_RE =
   re.compile(r"(?<!~/)(?<!\$HOME/)\.claude/settings\.json")` e `GRAVA_STATUSLINE_RE =
   re.compile(r'"statusLine"\s*:|\.statusLine\s*(\|=|=)(?!=)|\{\s*statusLine\s*:')`; probes dos
   comentários atualizados com as formas novas. Verificação: os 11 probes (rodados em 2026-08-08,
   todos OK) reproduzidos como teste de mesa; lint passa no repo pós-edição e falha se uma menção
   de escopo sumir do init.md.
8. **`orq/commands/init.md`, Regras/`--reinstalar`** — o re-sync passa a cobrir também a cópia
   solitária de composição (`.claude/kanban-status.sh` ou `~/.claude/orq/kanban-status.sh` sem a
   irmã); remoção de qualquer referência ao ramo sem `jq`. Verificação: o texto lista os três
   layouts possíveis de cópia (par no projeto · par no usuário · solitária de composição).
9. **Bateria de fixtures (pré-release, no scratchpad)** — 9 alvos: (a) réplica da barra do dono
   (2 `printf` em if/else); (b) acumuladora com `printf` único; (c) termina em `exit 0`; (d) com
   `set -e`; (e) shebang `zsh`; (f) Python; (g) inline sem arquivo; (h) não-determinística
   (`date +%s` na saída); (i) fluxo termina em `exec` no meio (o bloco nunca roda). Esperado:
   a-e compõem e passam prefixo+sufixo; f-h caem em fallback **antes de escrever**, com o motivo
   certo; **i compõe, reprova em P5, reverte, e `cmp` prova restauração byte-idêntica** — é o
   teste do caminho de reversão. Verificação: tabela de resultados colada nesta thread.
10. **Gates** — `claude plugin validate ./orq --strict` + `python3 orq/scripts/lint-coerencia.py .`;
    conferir que o bump 0.20.0 segue coerente nos quatro lugares (já está no working tree).
11. **(pós-ok do dono) Release + restart + comportamentais** — ver "Como testar" abaixo.
12. **Memória** — gotchas novos (`jq … arquivo > arquivo` trunca · `[ -x ]` é irrelevante quando a
    invocação é via `sh` · "validar edição por experimento antes×depois, não por leitura") · log ·
    board · `arquitetura.md` (asset + compor-statusline + a tese "juízo → propriedade verificável").

## Como testar sem uma máquina virgem

1. **Fixtures do passo 9** — todo o procedimento de composição (inclusive reversão) roda em mesa,
   no scratchpad, sem release e sem tocar nada real. É a cobertura principal de F4.
2. **Composição de verdade, nesta máquina, sem tocar `~/.claude/`:** projeto scratch (`git init`
   em dir temporário) com `.claude/settings.local.json` apontando para uma barra fake **local do
   scratch** sem board → a precedência Local blinda a global do dono → `/orq:init` → F4 compõe
   **dentro do scratch**: conferir backup, `diff` só-bloco, prefixo, board no sufixo. Variante com
   a fixture (h) plantada → fallback com motivo + barra intacta.
3. **Cenário A (o que teria pego o incidente):** scratch sem settings próprios → o init relata F3
   (a global do dono mostra board), `jq .statusLine` nos settings do scratch volta `null`, a barra
   dele segue rica. **Legado plantado:** scratch com chave para `plugins/cache/...` → F2 proposto,
   nada escrito sem aprovação.
4. **Limite declarado:** F1 (Caso C) comportamental **continua não testável nesta máquina** — a
   global do dono existe e não vamos removê-la. Cobertura: a mecânica (merge seguro, cópia, stamp,
   guarda de destino) roda em mesa no scratchpad com arquivos fake; o resto é leitura hostil no
   review. Mesma limitação da v2, agora com a parte mecânica coberta.

## Critério de aceite

- [ ] Gates verdes (`validate --strict` + lint).
- [ ] `orq/scripts/statusline.sh`: 5 testes de mesa passam; `grep -F '[ -x' ` e `grep 'awk "BEGIN'`
      no fonte voltam vazios.
- [ ] `orq/compor-statusline.md` existe; leitura hostil não acha estado de F4 sem resposta nem T
      com duas interpretações; todo fallback nomeia o motivo.
- [ ] Árvore F1-F4 no init.md: todo estado (com/sem chave × procedência × board × sombreadas) cai
      em exatamente uma folha; nenhuma escrita sem aprovação correspondente na FASE 3.
- [ ] Fixtures: 9/9 com o resultado esperado, **incluindo a reversão da fixture (i) provada por
      `cmp`** — tabela na thread.
- [ ] Lint: 11 probes do tripwire OK; falha ao remover menção de escopo do init.md.
- [ ] Pós-release + restart: os 3 cenários comportamentais do "Como testar" (composição no scratch ·
      fallback não-determinístico · F3/legado) passam.
- [ ] Painel (rodada 3): **nenhum bloqueador em interseção de ramos** — é a métrica deste card,
      dado o histórico 5/5.
- [ ] O dono valida usando o produto (card fecha em VALIDATE, não no commit).

## Escopo

**Dentro:** `orq/commands/init.md` (FASES 1, 3, 4, 5, Regras) · **novo** `orq/compor-statusline.md` ·
`orq/scripts/statusline.sh` (2 correções) · `orq/scripts/lint-coerencia.py` (2 correções) · bump
0.20.0 (já no working tree) + README · fixtures · memória.
**Fora:** editar `~/.claude/statusline.sh` do dono (na máquina dele nada dispara — F3; a Decisão 5
segue sendo dele aplicar) · composição em Python/Node/inline (fallback declarado; se houver
demanda real, é card novo) · T-029 (gate geral de caminhos) · a pendência do commit de reversão no
`prompts-byia-clientes` (do Manager, fora deste repo) · statusline para Codex/Kimi (hosts sem
`statusLine`) · qualquer mudança de settings na composição (F4 nunca toca settings, por regra).

## Riscos

1. **Editar arquivo do usuário é classe nova de escrita.** Contida por R5 (as 5 travas), aprovação
   nominal fora do projeto, backup nunca apagado e sentinelas removíveis à mão. O pior caso
   realista é "reprovou e reverteu" — barra intacta, um `.orq-bak` sobrando.
2. **Alvo global composto muda todos os projetos da máquina.** Por desenho, degrada a vazio onde
   não há board; ainda assim o aviso é obrigatório na aprovação nominal (P7).
3. **Determinismo dá falso-negativo em barra legítima** (relógio na saída) → composição recusada
   com motivo. Custo aceito: fallback honesto em vez de validação que não prova nada.
4. **Corrida com o render do host durante a escrita** — mitigada: append em uma chamada / tmp+`mv`
   atômico no mesmo diretório.
5. **A validação executa o script do usuário 6× com stdin fake.** Script com efeito colateral
   (log, cache) roda a mais — mesma classe de risco de qualquer render da barra; declarado.
6. **Dois arquivos normativos** (init.md + compor-statusline.md) = superfície de contradição entre
   arquivos. Mitigação: o init.md só resume as travas e delega; o review hostil lê os dois lado a
   lado; o lint garante a citação.
7. **O histórico é 5/5 contra.** O desenho minimiza juízo, mas quem decide é a rodada 3 do painel —
   por isso o critério de aceite tem a métrica explícita "nenhum bloqueador em interseção".

## Decisões do dono (pendentes — respondem no gate)

*1-6 aprovadas em 2026-08-07, não re-perguntar. A 9 é substituída pela 12 (política preservada).*

7. **Caso C: oferecer escopo de usuário?** (mantida da v2, sem mudança) *Rec.:* **sim, com default
   projeto** — única leitura que cumpre "todos os projetos" numa máquina nova; tripla guarda
   (pré-condição F1 + pergunta nominal + `~/.claude/orq/`). Trade-off: o init ganha um ramo que
   escreve fora do projeto, sempre nominal.
8. **"Uma coisa só": par co-localizado vs arquivo único.** (mantida da v2) *Rec.:* **par** — fundir
   quebraria os usos standalone do `kanban-status.sh` e duplicaria o awk do contrato (preço já pago
   no T-015). Trade-off: "uma coisa só" é a experiência, não o disco.
9. ~~Política de `jq`~~ — **substituída pela 12**; a política aprovada ("nunca instalar `jq`")
   permanece intacta.
10. **Composição com alvo fora do projeto, mediante aprovação nominal.** *Rec.:* **sim** — o caso
    comum de barra sem board é a global; sem este ramo, a composição que você pediu vira letra
    morta exatamente onde ela importa. Trade-off: o init passa a poder editar um script em
    `~/.claude/` — sempre nomeando o arquivo real, com backup e reversão automática.
11. **Estratégia de inserção: bloco no fim do fluxo emitindo sufixo (E1), em vez de editar o
    `printf` existente (E2).** *Rec.:* **E1** — não edita linha alheia, é validável por prefixo
    byte-a-byte, e E2 é a classe de erro que o painel puniu (sua própria barra tem dois `printf`
    finais; "achar A linha" já falha nela). Trade-off: o board entra sempre **no fim da última
    linha** da barra (numa barra que termina com quebra de linha, ele aparece em linha própria) —
    sem controle fino de posição.
12. **Matar o ramo "sem `jq`" do Caso C.** *Rec.:* **sim** — instalar sempre o par; a barra degrada
    para board-only sem `jq` e se completa **sozinha** quando `jq` aparecer (o guarda já está no
    script); elimina o beco sem saída do achado 4 e a contradição com "o par, sempre junto".
    Trade-off: nenhum identificado — o comportamento visível sem `jq` é o mesmo do ramo antigo, sem
    a receita no-op.

## Autocrítica — onde a v3 ainda pode reprovar

1. **T5 é deliberadamente fraco** (não prova que o fluxo chega ao fim — delega ao experimento).
   Custo: em script com `exec` no meio, o usuário recebe "compus, reprovou, reverti" em vez de um
   diagnóstico fino antes de tocar. Aceito de propósito: análise de fluxo é o juízo que reprovou
   duas vezes. Um revisor pode ler isso como "escreve sem ter certeza" — a resposta é que a
   incerteza é limitada por backup + prefixo + reversão provada por `cmp`.
2. **Propriedade de prefixo pressupõe estado externo parado** entre as execuções (git counts,
   board). Duas execuções encadeadas em repo parado — não verificado sob hook/daemon que mexa no
   repo no meio. Falha vira falso fallback, nunca dano.
3. **`$PWD` como cwd do render é empírico** (a barra antiga do dono funciona por esse caminho com
   `original_cwd` vazio), não documentado. P1 prefere a variável identificada; pior caso é board
   vazio/errado — visível, reversível.
4. **Detecção de F3 por `grep kanban-status|KANBAN.md` herda o falso-A da v2** (um comentário no
   script casaria). Consequência é inação — segura — mas o board não entra numa barra que só
   *menciona* o kanban. Não corrigido; declarado.
5. **Fixture (e) cobre `zsh -n` mas não uma barra zsh idiomática** (arrays, `print -P`); o bloco
   P3 é POSIX válido em zsh, e `zsh -n` foi verificado — mas não testei compor numa barra zsh real.
6. **A pergunta 4 mostrando o bloco para APROVAÇÃO não é o mesmo que a v2 mostrando para a PESSOA
   APLICAR** — assumo que isso cumpre o que o dono pediu ("o script pesquisa e inclui"): nós
   aplicamos, ele só consente. Se ele quiser zero pergunta, é mudança do contrato de aprovação do
   init inteiro — não está neste card.
7. **Os mocks usam os campos documentados** do stdin; um host futuro com stdin diferente pode
   renderizar diferente do validado. O stdin real do render não é capturável no momento do init.
8. **`orq/compor-statusline.md` como arquivo novo** segue o precedente do `stack.md`, mas é o
   primeiro arquivo normativo citado pelo init fora dele desde o T-029 — se o padrão "instrução
   dividida" incomodar o painel, a alternativa é embutir no init.md (custa ~100 linhas e a
   legibilidade; a regra não muda).
9. **Não verifiquei se as Decisões 7-8 foram respondidas** entre a v2 e a recusa das duas saídas —
   o board diz "faltam as 7-9"; a v3 as re-lista como pendentes. Se o dono já respondeu em conversa
   não registrada, o Manager corrige no gate.

---

## ⏭️ RETOMAR AQUI (v3 — o vivo)

Plano v3 pronto, não implementado. A implementação da v2 **segue no working tree, não commitada** —
a v3 aproveita a maior parte (ver "O que aproveita e o que joga fora"). Próxima ação: **dono
responde as Decisões 7, 8, 10, 11 e 12** (recomendações dadas) → card READY → implementar os passos
1-10 na ordem (o 2 antes do 3: o init.md cita `compor-statusline.md`; o lint exige que exista) →
review hostil (briefing do CLAUDE.md + "leia init.md e compor-statusline.md lado a lado; procure
estado de F4 sem resposta e juízo disfarçado de checagem") → **painel rodada 3** (métrica: zero
bloqueador em interseção de ramos) → release 0.20.0 com ok do dono → comportamentais do "Como
testar" → VALIDATE do dono. Pendências paralelas do Manager: confirmar reversão **commitada** no
`prompts-byia-clientes`; conferir se 7-8 já foram respondidas em conversa.

---

## ⏭️ RETOMAR AQUI (2026-08-08, fim do dia — substitui todos os anteriores)

**O card foi PARTIDO por decisão do dono** (*"siga sua recomendação"*), depois de **3 rodadas de
painel · 8 pareceres · 8 reprovações**.

- **`T-036` (este card) fica com:** o conserto do bug · o asset `orq/scripts/statusline.sh` já
  saneado (`[ -r ]` no lugar de `[ -x ]`; injeção do `awk` fechada) · as folhas **F1** (instalar em
  máquina limpa) · **F2** (consertar instalação nossa antiga) · **F3** (já mostra o board → não
  mexer) · o tripwire do lint · o bump 0.20.0.
- **`T-038` leva:** a folha **F4** (compor dentro de barra alheia) e o `orq/compor-statusline.md`
  inteiro, com os achados abertos da rodada 3 listados no card.

**Estado real do disco:** tudo no working tree, **nada commitado, nada publicado**. Uma rodada de
correção dos achados da rodada 3 (C1-C9 + D1-D5) **estava em execução** quando o card foi partido —
ela toca os dois escopos e **não é desperdício**: o que for de F4 migra para o `T-038`.

**Próxima ação, em ordem:**
1. Conferir o handoff da correção em curso (achados C1-C9/D1-D5) quando ele chegar.
2. **Recortar o escopo**: tirar F4 e a citação de `compor-statusline.md` do `init.md`, deixando
   "barra alheia sem board → relate e mostre, sem prometer composição". ⚠️ O lint exige que caminho
   citado exista — se `compor-statusline.md` sair do `init.md`, decidir se o arquivo fica no repo
   (órfão, para o `T-038`) ou sai junto.
3. Painel final **só sobre o escopo reduzido**.
4. Release 0.20.0 **com o ok do dono** + teste comportamental na máquina dele (ele cai em **F3**:
   o init deve dizer "sua statusline já mostra o board" e **não gravar nada**).

**Não repetir:** varredura rasa (a de 1 nível deu falso negativo e escondeu o 2º projeto) · stamp de
versão comparado por `diff` cru (vira alarme crônico) · guarda `[ -x ]` para script lido por `sh` ·
`jq '…' arquivo > arquivo` (trunca) · interpolar dado no programa do `awk`.
