# Log de mudanças — append-only

> Cronológico e **imutável**: cada entrada registra o que aconteceu naquele dia e por quê.
> Nunca reescrever entrada antiga. "Como funciona hoje" mora nas páginas de `wiki/`.

Formato: `## [AAAA-MM-DD] tipo | título`

---

## [2026-07-26] fix | namespace `/orquestra:*` → `/orq:*` em 6 arquivos

**Sintoma:** o plugin foi renomeado de `orquestra` para `orq` na v0.2.0, mas 9 referências internas a
`/orquestra:*` e 3 a "leia a skill `orquestra`" sobreviveram — em `SKILL.md`, `plan-next`,
`implement-next`, `init`, `quadro` e `orq-scout`.

**Impacto real (não era cosmético):** o `plan-next` terminava mandando o dono rodar
`/orquestra:implement-next`, que não existe; o `implement-next` mandava voltar pro
`/orquestra:plan-next`; três comandos mandavam ler uma skill de nome inexistente.

**Causa raiz:** a renomeação da v0.2.0 tratou o nome do pacote, não as auto-referências no corpo dos
prompts. Nenhuma verificação cobre isso — `claude plugin validate --strict` valida o manifesto, não a
coerência das instruções entre si.

**Consequência:** virou o card 🔴 `T-008` (lint de coerência interna). Um `grep` de dez linhas teria
pego o defeito em 2026-05; ele sobreviveu a três releases.

**Preservado de propósito:** o marcador HTML `<!-- orquestra:start -->` no `init.md:84` — é delimitador
de bloco no `CLAUDE.md` do projeto-alvo, não um comando.

---

## [2026-07-26] chore | instalação do Orquestra neste próprio repo (dogfooding)

Até hoje o plugin que prega *"o estado do trabalho vive no board"* era desenvolvido **sem board** — o
roadmap morava em prosa no README. Instalados: `memory/` completo, board com o roadmap convertido em
8 cards, elenco, duas páginas de tópico, `CLAUDE.md` e `AGENTS.md`.

**Decisões da instalação:**
- **Time núcleo puro**, reaproveitando os agentes do próprio plugin — nada em `.claude/agents/`.
  Cogitado um 6º papel de "crítico de prompt" (o produto aqui são instruções, não código) e
  **recusado**: a parte determinística vira lint (T-008) e o resto é briefing do reviewer.
- **Sem indexação semântica.** 24 arquivos de markdown: `grep` resolve. Registrado como decidido
  para não ser reproposto.
- **Statusline não tocada** — o dono já tem uma customizada em `~/.claude/statusline.sh`.

---

## [2026-07-26] feat | stack complementar auto-detectada (0.5.0)

**Motivação do dono:** a experiência dele com o Orquestra depende de uma stack de memória e contexto
que ele já tinha montada — e que não estava documentada em lugar nenhum. Quem instalasse o plugin
puro teria performance pior sem saber por quê. Pedido explícito: *"que uma IA leia esse repositório,
veja o que é necessário e instale tudo, mesmo que não esteja diretamente no repositório"*.

**Entregue:** `orq/stack.md` (catálogo canônico, escrito para ser lido por IA — detecção, comando
exato, custo honesto) · comando `/orq:stack` · integração nas FASES 1/2/3/4 do `init` · gatilho
natural na skill · seção no README · `memory/wiki/_stack.md` com o levantamento real desta máquina.

**Decisões:**
- **Consentimento é a espinha do desenho**, não um detalhe: nada instala sem "pode instalar", nada
  que exija chave sem o dono fornecer, e recusa registrada é **permanente** até ele reabrir.
- **`_stack.md` com seção "Dispensadas"** existe porque sem ela a mesma proposta volta toda sessão —
  o tipo de ruído que faz o dono desligar a feature.
- **Comandos levantados da máquina real**, não inventados: marketplaces, MCPs e PATH.
- **Sem comando de instalação para `codebase-memory-mcp`.** É binário local sem origem rastreável;
  recomendar um comando adivinhado a terceiros seria pior que omitir.

**Veredito sobre a dúvida do dono (Serena é redundante com codebase-memory?):** não, mas se
sobrepõem em ~20% — os dois acham símbolo por nome. Serena é LSP + **edição**; codebase-memory é
grafo de **relações**. No Orquestra a sinergia é por papel: planner/reviewer ↔ grafo, implementer ↔
LSP. Escolhendo um só: gargalo em *entender* → codebase-memory; em *editar* → Serena. Menos de ~50
arquivos → nenhum dos dois.
