**GO**

## Bloqueadores demonstrados

Nenhum. Não encontrei caminho no contrato em que uma LLM crie autoridade, saldo, escopo ou entrega Git, nem consumidor central que contradiga a política única de forma a forçar uma violação. As lacunas abaixo levam, no pior caso, a parada conservadora ou improviso que o próprio contrato já proíbe.

Linhas contadas nos arquivos reproduzidos e conferidas contra o mapa do delta. "≈" marca estimativa em trecho sem âncora no mapa.

## Ressalvas

**R1 — REALISTA. Não há meio definido para levar o resultado de A até B, ou até a integração, sem entrega Git.**
- Onde: `orq/skills/orq/SKILL.md:570`, `:579`, `:585-587`; `orq/commands/implement-next.md:116-119`, `:166-171`; `orq/agents/orq-implementer.md:43`.
- Cenário: host Claude, Git no padrão não autorizado, plano com dependência A→B entre writers. A termina no próprio checkout com mudanças não commitadas, já que worker não faz stage nem commit. B "espera A apenas no trecho dependente" e nasce em checkout isolado novo. O contrato não diz como o artefato de A entra no checkout de B ou na árvore integrada sem stage, commit, merge ou cherry-pick, que são operações de entrega.
- Saídas prováveis: o Manager improvisa uma operação Git proibida, roda B no checkout de A (contra `:386`) ou estaciona.
- Por que não bloqueia: nenhuma cláusula autoriza a violação, e o default seguro existe. A base de criação do worktree pelo host não é verificável daqui.
- Sugestão: uma frase dizendo que, sem Git autorizado, o Manager transfere por cópia ou patch sem índice, ou serializa A e B no mesmo writer e checkout.

**R2 — REALISTA. O registro de READY não lista os campos novos do acordo.**
- Onde: `orq/commands/plan-next.md:250-266` comparado com `orq/skills/orq/SKILL.md:518-527`. O §0 (`plan-next.md:48-49`) manda consolidar "no plano", não na thread.
- Cenário: o Manager segue o §6 ao pé da letra e grava só os campos T-143 (fonte, escopo, proibições, orçamento). Ficam de fora a "delegação técnica" e as "operações locais incluindo agentes". No primeiro complemento, `SKILL.md:532-533` ("Sem meta ou delegação verificável, não presuma cobertura") leva a perguntar ao dono de novo.
- Efeito: não amplia autoridade, mas frustra o objetivo do critério 1. A correção é remeter o §6 à lista completa da SKILL.

**R3 — REALISTA. O fan-out de agentes locais fica sem teto quando o acordo é silencioso.**
- Onde: `orq/skills/orq/SKILL.md:525`, `:527`, `:560-562`.
- O problema:
  - "agentes quando cobertos" não traz quantidade.
  - "capacidade comprovada" é ambíguo: pode significar capacidade do host ou orçamento.
  - "Ausência de teto não equivale a autorização ilimitada" só vale para egress.
- Cenário: o acordo diz "pode usar agentes" e o dono está em fim de ciclo de crédito. O Manager amplia entregas e consome crédito sem limite humano. A magnitude do gasto vira decisão da LLM, em tensão com o critério 1.
- Sugestão: estender a frase de não-ilimitado ao consumo local de agentes, ou exigir limite registrado no acordo.

**R4 — REALISTA (baixo). A linha "Duas análises read-only independentes podem avançar juntas" conflita com "um revisor".**
- Onde: `orq/skills/orq/SKILL.md:568` comparado com `SKILL.md:182` e `implement-next.md` §2 (≈`:180`).
- Cenário: o gate de review tem saldo 2. O Manager dispara dois revisores simultâneos no mesmo snapshot, tratando-os como "análises independentes", e consome o saldo inteiro numa rodada.
- `SKILL.md:563-564` ("independência de revisão seguem a Matriz") mitiga, mas não exclui a revisão da tabela. A regra específica provavelmente prevalece.
- Ponto TEÓRICO associado: o Planner em `workspace-read` escreve o artefato do plano (`orq-planner.md`, seção "Entrada e persistência"). Dois Planners no mesmo card poderiam disputar `docs/plano_<slug>.md`. `SKILL.md:573-575`, que exige arquivos permitidos e exclusivos no briefing, mitiga esse risco.

**R5 — REALISTA (baixo). Na colisão do Companion, a análise serializada deixa de ser independente.**
- Onde: `orq/skills/orq/SKILL.md:≈294-296` (mesmo card e papel reutilizam a task), `:576-578`.
- O critério 4 é cumprido literalmente. Mas, no host Claude, duas análises OpenAI do mesmo papel no mesmo card fazem a segunda retomar a thread da primeira.
- A exceção "nasce fresca" só existe para o Reviewer (`:≈305-307`). Nada manda declarar que a segunda análise perdeu a independência.
- Detalhe: o "Scout" do plano não é papel do elenco, então não resolve linha em `## Times por host`.

**R6 — TEÓRICO. A instrução "entregue o apontamento ao mesmo worker" não tem primitiva nativa no Claude.**
- Onde: `orq/commands/implement-next.md:163-164`.
- O spawn sem `name` é efêmero. Com `name`, o subagente trava em idle, como a própria SKILL avisa.
- A regra de degradação ("Sem a primitiva, nunca finja") cobre o caso, mas um modelo pode tentar `name` para cumprir "mesmo worker".

**R7 — TEÓRICO. A regra 7 é genérica demais.**
- Onde: `orq/skills/orq/SKILL.md:386-387` ("Escrita roda em checkout isolado por writer").
- Ela convive com três escritas fora de checkout isolado: o Trivial escrito pelo Manager na sessão, o spawn do `orq-docs` sem isolamento declarado (`implement-next.md` §3) e as escritas de board e thread.
- Leitura hostil: Docs num worktree novo, que não contém o código integrado não commitado. Liga-se a R1.

**R8 — TEÓRICO. A frase sobre resultado terminal admite leitura que trava correções.**
- Onde: `orq/skills/orq/SKILL.md:588-589` ("resultado terminal ou timeout não autoriza nova chamada").
- Lida literalmente, bloqueia rodadas de correção. `implement-next.md:163-164` ("quando a continuação estiver coberta") e o §2 resolvem a dúvida: o resultado terminal não é autorização, mas a cobertura é.

**R9 — TEÓRICO. Pequenas imprecisões em `orq/agents/orq-implementer.md`.**
- `:43` lista "stage, commit, push ou integração" e omite merge, tag e publicação da lista canônica. O título "Entrega Git é do Manager" cobre o caso.
- `:24` diz "não relance a chamada cegamente" a um worker que não tem chamada a relançar. É ambíguo, mas inócuo diante de `:45`.
- `:47` "não execute como complemento" tem redação condicional. Mesmo assim, `:48` devolve ao Manager.

**R10 — TEÓRICO. Limites dos testes.**
- `orq/scripts/test_work_evidence.py:25` e `orq/scripts/test_implementer_worker_boundary.py:29` usam `parents[2]` com `AGENTS.md` e `orq/...`, ou seja, caminhos relativos ao repositório. Quebram fora dele, por exemplo no cache instalado. O `PolicyConsumersTest`, preexistente, usa `parents[1]`.
- Se a suíte é executada fora do repositório não é verificável daqui.
- As guardas checam presença de substring. Uma cláusula contraditória acrescentada em outro trecho passaria. Isso já foi reconhecido como "não é prova comportamental".

## Não verificável daqui

- **Medidor:** se `references/progress.md` aceita vários `start` simultâneos com executores distintos. Isso decide se o medidor existente suporta writers paralelos, ligado aos critérios 4 e 5.
- **Arquivos não reproduzidos:** `revisar.md`, `elenco.md`, `orq-docs`, `orq-reviewer` e a coerência do lint sobre eles.
- **Números da evidência:** as mutações visíveis somam 31 (17 + 14). As "10 Manager" não estão no pacote. Os 936 testes e o exit 0 são alegações.
- **Host:** o comportamento de `isolation: "worktree"` quanto ao commit-base.

## Gates pendentes

Nenhum é dispensado pela candidata:

- O bump de quatro arquivos segue exigido (`AGENTS.md`, "Versão"). A candidata está em 0.32.0 sem bump, então não pode ser commitada como está.
- Git continua não autorizado por padrão.
- O teste comportamental só vale após o release.
- O review externo depende de cobertura (P05).

A imprecisão de C01 é da sonda, não da candidata.

---
*Nota: o briefing pediu trabalho sem ferramentas nem arquivos. Por isso não criei o arquivo de plano nem chamei ExitPlanMode; o parecer vai só como texto.*
