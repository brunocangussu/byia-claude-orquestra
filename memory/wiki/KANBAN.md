# KANBAN — Orquestra (`orq`)

> Fonte da verdade do trabalho. **Só o Manager (a sessão principal) move cards.**
> Marcadores: `[ ]` backlog · `[>]` planejando · `[!]` esperando o dono · `[~]` implementando ·
> `[?]` aguardando validação · `[x]` feito.

---

## ⏸️ Esperando você

_(vazio)_

---

## 🟡 Fazendo

_(vazio)_

---

## 🟣 Validar

- [?] `T-015` Bugs de ambiente documentados e diagnosticáveis — os 6 atritos que já custaram tempo viraram seção **Problemas conhecidos** no README (plugin desatualizado · escopo errado · revisor fora do PATH · trava por stdin · statusline muda · implementa sem planejar · `--help | head` mentindo) e, mais importante, viraram **checagem executável** no `/orq:stack --verificar`, que agora diagnostica ambiente e diz o comando que corrige. Gatilho natural novo: *"não está funcionando"*, *"o revisor sumiu"*. **Como validar:** num projeto novo, diga *"parece que não conectou"* e veja se ele roda o diagnóstico em vez de chutar.
- [?] `T-014` Roteamento automático pelo ciclo — **a interface natural não funcionava.** Medi 10 frases reais do dono contra os 25 gatilhos da skill: **0 de 10**. Por isso a skill `orq` nunca foi invocada nesta sessão e tudo foi implementado direto, sem plano e sem gate — inclusive a feature do Kimi. Causa raiz: os gatilhos foram escritos imaginando como ele falaria, não observando como fala, e faltava o padrão mais comum (o **pedido de mudança**). Corrigido em dois níveis: `description` reescrita da fala real (**cobertura 0% → 100%**) e seção **ROTEAMENTO AUTOMÁTICO** no topo da skill, com escala por risco (trivial → direto · pequeno → revisor interno · normal → ciclo completo · alto risco → gate extra) e a regra "na dúvida, suba um nível". **Como validar:** numa sessão nova, diga algo como *"queria melhorar X"* e veja se ele **anuncia** que vai planejar antes (em vez de já editar arquivo, ou de perguntar se pode rodar um comando).
- [?] `T-007` Kimi como terceiro revisor do painel — **desbloqueado**: o CLI existe (`~/.kimi-code/bin/kimi`, v0.29.2, OAuth), só não estava no PATH — por isso o agente global `kimi-revisor` nunca revisou nada. Testado de ponta a ponta: 2min12s, formato exato, 5 riscos concretos, worktree intacto (read-only confirmado na prática, já que ele não tem flag de sandbox). O painel agora é **Claude + Codex + Kimi**, e "confirmado por 2+" deixou de exigir unanimidade. Adotados do prompt do dono: **formato único** (BLOQUEADORES/RISCOS/VEREDITO) e a **regra LGPD** — nenhum dado de paciente, PII ou credencial vai para revisor externo. **Como validar:** rode `/orq:revisar` numa mudança real e confira que os **três** pareceres voltam, que a reconciliação separa confirmado-por-2 de achado-solitário, e que ele avisa se algum revisor falhou.
- [?] `T-013` Protocolo de várias janelas — o dono trabalha com N janelas Claude, uma por frente, e o modelo pressupunha UM Manager: as janelas se sobrescreviam em silêncio. **Regra base:** uma janela = uma frente. **Três regras que dispensam lock:** releia antes de escrever · edite só as linhas dos seus cards (nunca reescreva o board inteiro a partir de cópia velha — é a reescrita que apaga, não a concorrência) · card em curso leva `@frente` no fim da nota. **O ganho maior não é a trava:** pendência de decisão vira card `[!]` com a pergunta exata + "RETOMAR AQUI" na thread, e aí a janela **pode fechar** — antes ela ficava viva só como memória de pendência. Escrito em `_schema.md`, no `checkpoint`, na skill e no template que o `init` gera. **Como validar:** abra duas janelas, mexa em cards diferentes nas duas, dê checkpoint nas duas e confira que nenhum movimento sumiu; depois deixe uma pendência em `[!]`, feche a janela e veja se outra retoma sem você explicar nada.
- [?] `T-011` Atritos do primeiro `/orq:init` em projeto de terceiro — 10 achados aplicados, **depois reprovados pelo painel e corrigidos de novo**. O painel (Claude + Codex) mostrou que a 0.6.0 documentou o contrato mas deixou o **parser permissivo**: item de checklist solto contava como card, `## Arquivo` não encerrava a contagem, card sem crases vazava. Corrigido na 0.6.1 endurecendo o regex e fazendo o desvio aparecer como `⚠N` — falha visível em vez de silenciosa. **Os 4 bugs de contrato:** (1) produtor e consumidor do board não compartilhavam spec, e card fora do formato deixa a statusline **muda sem erro**; (2) `checkpoint` e `wiki-lint` liam um `_schema.md` que o `init` nunca criava; (3) nenhuma regra sobre colisão entre agente local e os `orq-*` do plugin; (4) nada verificava a instalação no fim. **Correção estrutural:** o `_schema.md` virou o contrato compartilhado — o `init` cria, o `checkpoint` e o `wiki-lint` leem, e a FASE 5 exige smoke test de **três sinais** (vazio · `⚠N` · denominador ≠ contagem manual). **Como validar:** rode `/orq:init` num projeto novo e confira que o `_schema.md` nasce e que o smoke test compara a contagem, não só "saiu alguma coisa".
- [?] `T-003` Piloto end-to-end — **cumprido em 2026-07-27, e melhor do que o card pedia:** o `/orq:init` rodou em repositório de terceiro, por outra LLM, sem eu por perto. O relatório de atrito veio com 10 achados (4 bugs de contrato reais) e virou o `T-011`. Também validou o que **funciona**: a regra "este comando se ADAPTA ao projeto" cortou 6 agentes genéricos que seriam criados sem ela, e o `_stack.md` com "Dispensadas" evitou repropor ferramenta já recusada. **Como validar:** nada a testar — o card era o próprio experimento. Feche se concordar que o piloto respondeu a pergunta.
- [?] `T-008` Lint de coerência interna — `orq/scripts/lint-coerencia.py`. Confere `/orq:x`, `` `orq-agente` ``, `` skill `nome` `` e `${CLAUDE_PLUGIN_ROOT}/arquivo` contra o que existe; ignora `memory/`. Testado nos dois sentidos: passa no estado atual e pega os 4 tipos de defeito quando injetados. **Como validar:** renomeie mentalmente um comando (ou rode `python3 orq/scripts/lint-coerencia.py .` depois de editar qualquer coisa) e veja se ele aponta `arquivo:linha`. Documentado no `CLAUDE.md` como verificação obrigatória junto do `validate`.
- [?] `T-010` Painel de revisores consertado — **duas causas raiz, ambas corrigidas.** (a) `codex exec` bloqueia lendo stdin sem TTY: `< /dev/null` resolve, resposta em segundos. (b) Subagente spawnado **com `name`** vira teammate e nunca devolve resultado; sem nome, entregou em 231 s. O `/orq:revisar` foi reescrito para usar a CLI direto (era o plugin `codex:codex-rescue` com forwarder) e para proibir `name` no spawn. **Como validar:** rode `/orq:revisar` numa mudança real e confirme que **os dois** pareceres voltam e que a reconciliação separa confirmado-por-dois de achado-por-um.
- [?] `T-009` Stack complementar auto-detectada — catálogo `orq/stack.md` + comando `/orq:stack` + integração no `init` + seção no README. **Como validar:** numa sessão nova, diga *"o que falta instalar aqui?"* e veja se ele detecta sem você citar comando; depois confirme que ele **não instala nada** antes do seu ok e que respeita `_stack.md` (não repropõe a indexação já dispensada).

---

## 🔵 Backlog

- [ ] `T-001` Hooks de segurança — 🔴 `PreToolUse` em `Bash` negando `git push`, merge, deploy, migration e SQL de escrita. Camada 1 do roadmap#1. Autocontida: não depende de saber quem chamou. **É o que transforma as promessas do modo noturno de disciplina em garantia — sem isso o T-006 não sai do papel.**
- [ ] `T-012` Piloto dos loops A e B — o `/orq:init` já foi validado em projeto real (`T-003`), mas `/orq:plan-next` e `/orq:implement-next` **continuam sem nunca terem sido invocados de verdade** — todo o trabalho até aqui foi feito pelo Manager na mão. É o mesmo tipo de ponto cego que o `T-003` expôs no `init`: contrato entre partes que ninguém exercitou. Rodar um card do backlog pelo fluxo formal, sem atalho.
- [ ] `T-002` Hooks de processo — `PreToolUse` em `Edit`/`Write` sobre `KANBAN.md`: mover card para `[?]` sem artefato de review existente é bloqueado. Gate no **conteúdo do diff**, não em quem chamou. Camada 2 do roadmap#1. ⚠️ Verificar antes: o payload do hook distingue subagente da sessão principal? Se não, "só o Manager move cards" não é enforçável como o parecer supõe.
- [ ] `T-004` Workflows determinísticos em JS — 3 separados (plan-card / implement-card / finalize-card), nunca um só: workflow não aceita input humano no meio e há gate do dono entre as etapas. Roadmap#2. Só depois do T-003 — workflow sobre fluxo que ainda vai mudar é retrabalho garantido.
- [ ] `T-005` Worktree obrigatório em card que escreve — hoje é instrução (`isolation: "worktree"`), não imposição. Roadmap#5.
- [ ] `T-006` Implementação noturna limitada — só cards pré-aprovados, worktree próprio, commit local no máximo, sem merge/push/deploy. Roadmap#3. **Bloqueado por T-001 e T-003.**

---

## ✅ Feito

_(vazio — o board nasceu em 2026-07-26)_

---

## 📦 Arquivado

_(nada abaixo desta linha conta no progresso da statusline)_
