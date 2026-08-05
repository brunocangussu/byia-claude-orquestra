# Gotchas — armadilhas que já custaram tempo

> Só entra aqui o que **já** causou erro ou desperdício. Não é lista de boas intenções.

---

### Renomear o plugin não renomeia as auto-referências

A v0.2.0 trocou `orquestra` por `orq` no pacote, mas os prompts continuaram mandando rodar
`/orquestra:plan-next` e ler a skill `orquestra`. Sobreviveu a **três releases** porque
`claude plugin validate --strict` valida o *manifesto*, não a coerência entre instruções.
→ Ao renomear qualquer comando, skill ou agente, faça `grep` do nome antigo no `orq/` inteiro.

### `claude plugin validate` não testa comportamento

Ele passa com um plugin cujas instruções se contradizem ou apontam pro nada. Validação verde ≠
plugin correto. O teste real é comportamental: rodar num projeto e ver se o Claude faz o esperado.

### Cron no Claude Code é *session-scoped*

Não existe execução realmente desacompanhada dentro do CLI. O modo noturno depende da sessão
**aberta** e da máquina ligada e sem suspender. Se a máquina dormir, o trabalho pausa.
→ Nunca prometer ao dono que algo "roda sozinho de madrugada".

### O `model:` no arquivo do agente é só padrão de fábrica

Quem manda é `memory/wiki/_elenco.md`. Comando que spawna sem ler o elenco antes ignora
silenciosamente a escalação escolhida pro projeto — e ninguém percebe, porque não dá erro.

### `manager` não é configurável pelo elenco

O Manager é a sessão principal, definida pelo `/model`. Tentar trocá-lo via `/orq:elenco` não faz
sentido e confunde — não é um spawn.

### `which kimi` falhar NÃO significa que o Kimi não está instalado

O instalador põe o binário em `~/.kimi-code/bin/kimi` e adiciona o diretório ao **`.zshrc`** — o que
só alcança shell aberto **depois**. Sessão já em curso não enxerga: `which kimi` falha **enquanto o
binário está lá, funcionando**.

Isso já produziu dois erros em cascata (2026-07-28): o agente global `kimi-revisor` parava dizendo
"não instalado" (comportamento correto, diagnóstico errado), e uma sessão irmã concluiu o mesmo e foi
procurar o pacote **no npm** — onde ele nunca esteve. Os `kimi`, `kimi-cli` e `kimi-code` do npm são
homônimos sem relação; instalar um deles no papel de revisor seria risco de supply chain de verdade.
A distribuição oficial é `code.kimi.com`, binário com checksum.

→ **Detecte com fallback, nunca só pelo PATH:**
`KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")`
→ Nesta máquina há symlink em `~/.local/bin/kimi` (diretório já no PATH), então `kimi` solto resolve.
→ Igual ao Codex, o `< /dev/null` é obrigatório (sem TTY, bloqueia lendo stdin).

### O plugin do Codex não é invocável pelo modelo — só pelo dono

`codex:codex-rescue` **não aparece** como agent type disponível, e `/codex:review` tem
`disable-model-invocation: true`. Ou seja, a regra "use sempre o subagente, nunca o binário" só é
executável quando **o dono digita** o comando; de dentro de um turno do Claude, o único caminho é a
CLI (`codex exec … < /dev/null`). Verificado empiricamente em 2026-07-28.

> ⚠️ **Esta premissa venceu — não a cite como definitiva.** Desde 29/jul/2026 o
> `codex:codex-rescue` **aparece** na lista de agent types das sessões (reconfirmado em 30/jul).
> O que ficou desatualizado é só a *justificativa* do parágrafo acima, não necessariamente a
> escolha: `memory/wiki/_elenco.md` e `orq/commands/revisar.md` continuam instruindo a CLI direta,
> enquanto a regra global do dono (`~/.claude/CLAUDE.md`) manda **nunca** invocar o binário `codex`
> por Bash de dentro do Claude Code, para não perder o rastreamento de job. **Isso é decisão dele,
> não do Manager** — está registrado como card no board (`T-027`). Até ele decidir, o projeto segue
> como está, cientes de que é uma exceção à regra global, não uma impossibilidade técnica.

### Achado de revisor externo não se aplica cru — reconcilie

O Kimi apontou (corretamente) que o lint exigia crases para skill e não para agente. Apliquei a
"correção" tornando as crases opcionais → **três falsos positivos na hora**, porque "skill" é palavra
comum em prosa portuguesa ("a skill **e** o comando", "skill **ou** agente"). O prefixo `orq-` não
tem esse problema: não aparece em texto corrido.
→ A assimetria era **proposital** e o revisor não tinha como saber. Diagnóstico certo, correção
errada. Sempre teste a correção antes de aceitar — e falso positivo é o que faz lint ser desligado.

### Marketplace local ≠ plugin atualizado — editar o repo NÃO basta

O marketplace `orquestra` aponta para o **diretório** deste repo, o que dá a impressão de que editar
um arquivo já vale na hora. **Não vale.** O plugin instalado é uma **cópia em cache**
(`~/.claude/plugins/cache/orquestra/orq/<versão>/`), e ela só muda com:

```bash
claude plugin marketplace update orquestra
claude plugin update orq@orquestra          # copia para o cache — teste válido só após restart
claude plugin list                          # confirma versão e escopo
```

Foi assim que a máquina do dono ficou usando a **0.4.0 em todos os outros projetos** enquanto o repo
já estava na 0.7.0 — sete releases de diferença, sem nenhum sinal. Testar comportamento sem atualizar
testa a versão errada.

### `claude plugin` TEM install/update/marketplace — não conclua por `--help | head`

Em 2026-07-27 eu rodei `claude plugin --help | head -20`, vi a lista alfabética parar em `help` e
concluí que a CLI **não tinha** `install` nem `marketplace add`. Escrevi isso como fato no
`/orq:stack` e no `init`, mandando "entregar o comando pro dono colar". **Era falso** — a lista
continuava em `install`, `list`, `marketplace`, `prune`, `tag`, `uninstall`, `update`, `validate`.
→ Nunca conclua ausência a partir de saída truncada. `head` corta; a ausência precisa ser verificada
no comando específico (`claude plugin update --help`).

### Board fora do formato = statusline muda, sem erro nenhum

`kanban-status.sh` casa `/^- \[.\]/` e lê o título **por posição** (entre a crase do ID e o travessão).
Um card escrito como `` - `[!]` **T-001 · Título** `` não casa — e o script **sai em silêncio**, sem
mensagem, sem código de erro. O board parece perfeito e o progresso simplesmente nunca aparece.

Aconteceu na primeira instalação em projeto de terceiro (2026-07-27): a LLM escreveu o board com o
marcador dentro de crases e só descobriu porque testou por conta própria — o `/orq:init` não mandava
testar. A causa é estrutural: **produtor e consumidor não compartilhavam especificação.**
→ O contrato agora vive em `memory/wiki/_schema.md`, o `init` cria esse arquivo e a FASE 5 exige
smoke test com saída não-vazia.

### Nome de agente do projeto nunca deve colidir com o do plugin

Os cinco `orq-*` vêm do plugin. Criar `.claude/agents/orq-planner.md` no projeto tem resolução
**indefinida** — pode sobrescrever, pode duplicar na lista, pode variar. Papel adicional usa nome
próprio (`dados`, `infra`, `frontend`).

### `codex exec` trava esperando stdin — sempre feche com `< /dev/null`

**Causa raiz (diagnosticada em 2026-07-26, card `T-010`).** Sem TTY — que é o caso dentro do Bash tool
do Claude Code — o `codex exec` imprime `Reading additional input from stdin...` e **bloqueia até o
timeout**, mesmo com o prompt passado como argumento. Não é lentidão, não é o modelo, não é o tamanho
do briefing: é o stdin que nunca fecha.

```bash
codex exec -s read-only "..." < /dev/null      # responde em segundos
codex exec -s read-only "..."                  # trava até o timeout
```

Custou duas tentativas de 10 e 3 minutos, e a hipótese errada de "poluição de contexto do ambiente do
Codex" — o que se via era só a sessão pendurada.

### Subagente spawnado COM `name` não devolve resultado

Com `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` no ambiente, passar `name` no spawn transforma o agente
em **teammate endereçável**: ele fica vivo emitindo `idle_notification` e **nunca retorna o parecer**.
Sem `name`, o mesmo agente com o mesmo prompt entregou em 231 s.
→ Revisor, planner, implementer e docs: **spawnar sem `name`**. Nome só para agente com quem você
realmente vai conversar em várias rodadas.

### Painel parcial nunca vira "consenso"

Se um revisor do painel não entregar, **diga ao dono que o painel foi parcial**. Nunca apresente
parecer de um revisor como se fosse a interseção de dois — o valor do painel está justamente em
confirmado-por-dois vs. achado-por-um.

### Lint de coerência não pode varrer `memory/`

O log é append-only e o `gotchas.md` citam nomes de comandos **que deixaram de existir**, de propósito,
ao descrever bugs passados. Um lint ingênuo acusa isso como referência quebrada em todo checkpoint —
e lint que dá falso positivo é lint que o dono desliga.

### Agent teams são experimentais

Mais caros e **não** isolam arquivos automaticamente. Dois agentes escrevendo no mesmo checkout dá
conflito. Tarefa que escreve → worktree próprio.

## Revisor externo sem sandbox escreve no repo vivo — e a instrução não segura

**Custou:** o working tree inteiro da 0.11.0, em 2026-07-28. Recuperado, mas com perda.

O Kimi foi spawnado como revisor **read-only**, com "não edite arquivo nenhum, apenas relate" no
prompt. No meio da revisão ele rodou `git checkout -- .` e descartou 16 arquivos de mudança não
commitada. Restaurou sozinho e avisou — mas o replay perdeu os marcadores de estado dos cards,
porque edições feitas por script não ficam no transcript de onde ele reconstruiu.

**Efeito colateral que quase virou conclusão errada:** o revisor interno, rodando em paralelo,
relatou "o working tree mudou três vezes" e "metade das correções não está em disco". Parecia
alucinação — era descrição fiel do repo sendo destruído e remontado. O Manager atribuiu a worktree
e errou. **Relato estranho de um revisor pode ser sintoma, não defeito do revisor.**

**O que dói:** `_elenco.md` e `revisar.md` **já avisavam** — "o Kimi não tem flag de sandbox como o
`-s read-only` do Codex; garantia dura só em worktree descartável". A instrução estava escrita,
estava correta, e não impediu nada. Só o Codex tem sandbox de verdade (`-s read-only`).

**Regra:** revisor externo sem flag de sandbox **não olha o repo vivo**. Worktree descartável ou
clone. Prompt não é permissão negada — é pedido educado.

## `git diff` esconde arquivo NOVO — e o painel de revisão revisa o vazio

**Pago em 2026-08-04, na 0.18.0.** O painel roda sobre um patch (`git diff > x.patch` + `git apply`
num worktree descartável). Arquivo novo é **untracked**, e `git diff` **não inclui untracked** — o
worktree do revisor externo nasceu sem `orq/commands/instalar.md`, que era **a peça central da
release**. O revisor reprovou com um bloqueador correto para o que via, e a premissa é que estava
furada.

**Sempre `git add -N .` antes de gerar o patch do painel.** Vale para toda release que cria arquivo
— e um comando novo é exatamente isso.

**Como apareceu:** o revisor foi **conferir se o arquivo existia** (`ls`, `git status -uall`) em vez
de assumir. Nenhum gate pegaria: `validate` e `lint` rodam no repo real, onde o arquivo está.

## Guarda mecânico prova ausência de STRING, não ausência de REGRA

**Pago em 2026-08-04, na 0.17.0.** O critério de aceite do A1 era `grep "Teto:" orq/` retornar 1
ocorrência — e retornou. A regra **sobreviveu mesmo assim**, em `SKILL.md:207`, escrita como
*"propõe **1×** o resto"*. O `grep` procurava uma redação; o defeito estava em outra.

Foram **cinco reincidências** do mesmo defeito, cada uma com redação diferente
(`"proponha 1× por bloco"` · `"propõe 1× o resto"` · `"(a unidade do teto do N2)"` ·
`"até o fim do bloco"` · `"insistir sem a condição ter piorado"`).

**Critério de aceite baseado em `grep` precisa vir acompanhado de leitura humana ou de revisor.**
A quinta só apareceu na releitura manual do Manager, depois de dois gates verdes e do `grep` limpo.

## Ao acrescentar cláusula a uma regra, a frase que a RESUME é sempre suspeita

**Corolário do anterior.** Toda regra tem uma frase de fecho que a resume ("o que o teto proíbe
é…"). Ao acrescentar uma cláusula nova, **essa frase foi escrita para a versão anterior** e passa a
contradizer a cláusula que você acabou de adicionar. Foi exatamente a quinta reincidência.
