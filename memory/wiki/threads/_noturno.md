# Modo noturno — manifesto

> A corrida anterior (`noturno-2026-07-30-2228`) está **encerrada e expirada**, com relatório
> próprio — recuperável em `git show bf9a6dc:memory/wiki/threads/_noturno.md`. Este arquivo é
> sobrescrito a cada corrida; o histórico mora no git, não aqui.

```
run_id: noturno-2026-09-07-2130
cards_max: 3
horas_max: 4
expira_em: 2026-09-08 01:30
modo: PLANEJAMENTO (nenhuma implementação)
cards: T-085 · T-086 · T-087
```

## Por que estes três, e por que planejados JUNTOS

Os três são o **mesmo problema com três sintomas**: a coexistência de dois hosts (Claude e Codex) no
mesmo repositório, cada um com seu runtime, escrevendo nos mesmos arquivos e chamando um ao outro.

- `T-085` — cada chamada do Claude ao Codex deixa uma thread visível lá; o inverso não deixa.
- `T-086` — o board não diz qual host pegou o card, e as janelas colidem em silêncio.
- `T-087` — o subagente que monta a chamada cross-host omite flags pedidas.

A regra de escopo do Orquestra permite tratar junto o que tem **a mesma causa raiz e o mesmo
subsistema**. Planejá-los separado produziria três planos que se contradizem na fronteira. Isso
também reduz de três para uma as threads criadas no Codex durante o planejamento — que, dado o
`T-085`, seria irônico ignorar.

## Achado que já muda o desenho do `T-085` (medido antes de dormir)

- O runner Anthropic (Codex → Claude) passa `--no-session-persistence`: por isso **o inverso não
  polui**. A assimetria não é do Codex, é de quem monta cada chamada.
- O runtime do Codex **tem** o mecanismo: `lib/codex.mjs:1117` resolve
  `ephemeral: options.persistThread ? false : true`.
- `codex-companion.mjs:493` passa `persistThread: true` **fixo** no subcomando `task`. Por isso
  `review`/`adversarial-review` não sujam a tela e `task` suja.

**Conclusão: não é limitação do Codex — é uma capacidade existente que o plugin não expõe no `task`.**
O trade-off real a resolver no plano: `ephemeral` mata o `--resume-thread`, que é o reúso
`card+papel` do `T-081`. Papel de rodada única não precisa de retomada; papel que recheca, precisa.

## Limites desta corrida

Nenhuma implementação · nenhum push · nenhuma instalação · nenhuma decisão no lugar do dono.
Card que exigir escolha dele termina em `[!]` com a pergunta exata escrita.

## Relatório — encerrada às 22h05, ~35 min de 4h

**Fila esgotada por conclusão, não por limite.** Os três cards escolhidos foram planejados juntos,
como previsto, e o planejamento produziu mais trabalho do que consumiu: três cards novos nasceram da
auditoria do plano.

### Planejado

`T-085`, `T-086` e `T-087` — plano único em `docs/plano_coexistencia_hosts.md`, escrito pelo
`planner·sistema` (`gpt-6-astra@xhigh`) e **auditado pelo Manager contra o código instalado** antes
de virar veredito. Os três terminam em `[!]`, com a pergunta exata no card.

### Estacionado — quatro decisões esperando o dono

1. Persistir a thread do Codex **só quando houver rechecada prevista**, com arquivamento reversível
   ao encerrar o papel?
2. Substituir o encaminhamento pelo `codex:codex-rescue` por um **adaptador determinístico** que
   monte os argumentos por código?
3. Migrar o estado para **um arquivo por card**, com o `KANBAN.md` virando visão gerada?
4. **Um único Manager/integrador**, e worktrees distintos quando os dois hosts escreverem em
   paralelo?

### O que a auditoria mudou — e um dos derrubados era meu

- 🔴 **`T-089` (novo, grave):** `--resume-thread` não existe no cache `1.0.5` do Companion, que é o
  que o subagente escolhe. **O reúso `card+papel` da `0.27.2` não está funcionando**, em silêncio.
- **`T-090` (novo):** o produto manda passar `--wait` ao `task`, que não é opção dele.
- **`T-087` reescrito:** minha premissa ("o subagente omitiu uma flag pedida") estava **errada** —
  a skill do plugin manda remover esse token justamente. O defeito real é a divergência entre três
  contratos de flags, sem ninguém verificar o que chegou.
- **Ressalva ao `T-019`**, que validei ontem: o JSON do `task` não devolve o sandbox efetivo, então
  a evidência é do que foi lançado, não do que o runtime reconheceu.

### Não verificado, deliberadamente

O planner cita `thread/archive` na documentação oficial do App Server. É fonte externa, os `--help`
locais não expõem arquivamento, e eu não confirmei — fica como hipótese a testar com canário, nunca
como capacidade assumida.

### Pulado

Nenhum card foi pulado por risco. Nada foi implementado, instalado, publicado ou decidido no lugar
do dono. **Nenhum push** — os commits são locais e esperam ele acordar.

