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
