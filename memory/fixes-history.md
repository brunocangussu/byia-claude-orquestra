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

**Correção do dono, na mesma sessão:** tirar os comandos de instalação do catálogo e apontar só o
repositório oficial + a importância da ferramenta. **O argumento dele é melhor que o desenho
original:** comando envelhece, repositório não — e some a assimetria de ter deixado uma ferramenta
sem comando. A IA passa a ler as instruções atuais no upstream na hora de instalar. Isso também
resolveu a pendência de procedência: o `codebase-memory-mcp` é `DeusData/codebase-memory-mcp`
(binário estático único, bate com o Mach-O de 255 MB local). Todas as 7 fontes confirmadas.

**Autocrítica antes de entregar — três brechas próprias, corrigidas:**
- `/orq:stack` passo 4 dizia "mostre o comando antes de rodar" sem definir se aquilo era um segundo
  gate. Um modelo podia mostrar e executar na mesma resposta, ou travar pedindo aprovação de novo.
  Agora está explícito: o "pode instalar" cobre a ferramenta; **voltar a perguntar só** se as
  instruções exigirem `sudo`, mexer em PATH, `curl | sh` ou dependência de sistema.
- `init.md` FASE 3: o "pode ir" genérico da instalação podia ser lido como aprovação da stack junto.
  Agora são **duas decisões separadas** — instalar arquivos no projeto é reversível, instalar
  software na máquina não é.
- `/orq:stack` passo 2 não dizia o que fazer sem `_stack.md` (comando rodando antes do `init`).

**O painel de revisores falhou por inteiro — os dois revisores.** O Codex não entregou (ver
`gotchas.md`). O `orq-reviewer` foi spawnado, respondeu três notificações de *idle* e **nunca produziu
parecer**, nem após dois pedidos de entrega parcial. Parei na terceira, em vez de insistir.

**Consequência honesta:** nenhum achado desta mudança veio de revisão independente. Todos vieram de
autocrítica do Manager. Duas contradições só apareceram na segunda passada, o que mostra o limite do
método — quem escreveu o texto é o pior leitor dele:
- `commands/stack.md:15` mandava usar a *"coluna Detectar"* do catálogo, que a reescrita eliminou (a
  detecção virou linha inline). Instrução apontando para estrutura inexistente.
- `stack.md` regra 3 dizia que a **camada 4 não se paga em projeto pequeno** — errado e contraditório
  com a própria seção da camada 4 e com os Perfis. Revisor externo se decide por **criticidade**, não
  por tamanho: script pequeno que mexe com dinheiro merece painel.

O `T-009` segue em VALIDATE, e agora a validação prática do dono é o único filtro real que restou.

---

## [2026-07-27] feat | protocolo de várias janelas (T-013, 0.7.0)

**Pergunta do dono:** ele trabalha com N janelas Claude abertas no mesmo projeto, uma por frente —
está resolvendo A, lembra de B, abre janela pra B sem largar A. Como o checkpoint não se sobrescreve?

**Não se sobrescrevia: perdia mesmo, em silêncio.** O modelo pressupõe **um** Manager. Com N janelas:
`KANBAN.md` e páginas de tópico são reescritas (last-write-wins → movimento de card some), o log é
append por ler-modificar-escrever (duas janelas simultâneas perdem uma entrada), e nada registra quem
escreveu. Mesma classe do bug do parser: **falha sem sinal**.

**O diagnóstico que mudou a solução:** a concorrência não é o problema — **a reescrita é**. Duas
janelas alterando *linhas diferentes*, cada uma relendo antes, praticamente não colidem. O que apaga
trabalho é reescrever o arquivo inteiro a partir de uma cópia velha do começo da sessão.

**Protocolo (uma janela = uma frente):**
1. releia antes de escrever — sempre, mesmo com o arquivo no contexto;
2. edite só as **linhas dos seus cards**, nunca o board inteiro;
3. card em curso leva `@frente` no fim da nota (depois do travessão, então não afeta o parser);
4. trabalho em curso mora em `threads/<frente>.md` — dono único, livre de conflito por construção.
   Isso reduz o problema de 5 arquivos disputados para **1**: o board.

**O ganho maior não é a trava.** O dono mantinha janela aberta *como memória de pendência* — "não
consigo decidir agora, então deixo a janela viva". Isso é contexto fazendo o papel do board. Agora o
`checkpoint` termina dizendo que **é seguro fechar a janela** quando a pendência virou card `[!]` com
a pergunta exata + "RETOMAR AQUI" na thread. E a instrução é explícita: **se você não consegue
afirmar isso com confiança, o handoff está fraco — melhore antes de fechar.**

**Recusado:** lock global (mata o paralelismo que motiva as N janelas) e merge por git (markdown de
prosa conflita mal, e ele não commita a cada checkpoint).

**Escrito em quatro lugares** porque cada um é lido num momento diferente: `_schema.md` (o contrato),
`checkpoint.md` (passo 2b, na hora de gravar), `SKILL.md` (a disciplina + gatilho natural para "vou
abrir outra janela") e o template que o `init` gera nos projetos novos.

---

## [2026-07-27] fix | painel REPROVOU a 0.6.0 — parser do board endurecido (0.6.1)

**Primeiro painel completo do projeto** (Claude + Codex, os dois entregando). Deu 10 achados e uma
**divergência de veredito**: Claude disse "aprovar com correções", Codex disse **REPROVAR**.
Desempatei com o Codex — o próximo `/orq:init` em projeto de terceiro repetiria a falha silenciosa.

**Confirmado pelos dois (a lição que interessa):** a 0.6.0 **documentou o contrato e esqueceu de
endurecer o parser**. Escrever a spec não impede o consumidor de aceitar lixo. Cenários provados
pelo revisor Claude rodando o script contra boards sintéticos:
- seção "Processo" com `- [x] revisor aprovou` (estrutura que o próprio CLAUDE.md global descreve)
  contava como card feito: board de 3 cards virava `📋 20% (1/5)`;
- `## 📦 Arquivo` em vez de `Arquivado` (variante natural em PT) fazia arquivados voltarem à conta;
- card sem crases no ID vazava o marcador cru para dentro da statusline.

E o mais importante: **o smoke test da 0.6.0 aprovava os quatro casos**, porque só reprovava saída
vazia.

**Correção:** o `kanban-status.sh` passou a casar `` /^- \[[ >!~?x]\] `[^`]+`/ `` — estrito. Linha
que *parece* card e não casa vira `⚠N` na saída. **A falha deixou de ser silenciosa**, que era o
defeito de fundo. O smoke test agora exige três sinais, e o terceiro é comparar o denominador com a
contagem manual de cards — "saída não-vazia" não prova nada.

**Outros aplicados:** `_stack.md` só nascia quando havia instalação, então quem **recusava** tudo
ficava sem a seção "Dispensadas" — justamente o caso em que repropor mais irrita · a pergunta 2 do
gate soldava "instalar software" com "quais revisores", e quem já tinha `codex` e recusava a stack
perdia o painel que já possuía (pior: sem `_elenco.md` o Codex é ativo por padrão, então **ter** o
arquivo deixava o dono pior do que não ter) · o `init` permitia índice fora de `memory/`, mas
`orq-planner` e `wiki-lint` exigem `memory/MEMORY.md` no caminho fixo — resolvido com ponteiro ·
`[~]` significava "implementando" no schema e READY/DEV_REVIEW na skill · `--reinstalar` não
detectava `.claude/agents/orq-*.md` legado.

**Autocrítica registrada:** o `MEMORY.md` deste repo ficou dizendo "versão 0.5.0" e "nunca rodou de
ponta a ponta" enquanto três cards já estavam em VALIDATE. O `checkpoint.md:36` manda atualizar o
índice — **o produto não seguiu a própria disciplina**, e quem retomasse pela regra "leia o
MEMORY.md primeiro" reimplementaria o lint.

---

## [2026-07-27] fix | 10 atritos do primeiro `/orq:init` em projeto de terceiro (T-011, 0.6.0)

**Origem:** outra LLM instalou o Orquestra num repositório real, sem ninguém do projeto por perto, e
devolveu relatório. É o `T-003` cumprido — e melhor do que o card pedia, porque foi em território que
ninguém aqui conhecia.

**4 bugs de contrato, todos confirmados no código:**

1. **Board fora do formato deixa a statusline muda, sem erro.** O `/orq:init` mandava "criar o
   KANBAN.md com o backlog real" e deixava o formato por conta do modelo; o `kanban-status.sh` casa
   `/^- \[.\]/` e lê por posição. A LLM escreveu o marcador dentro de crases, a saída veio vazia, e
   ela **só descobriu porque testou por conta própria**. **Causa raiz: produtor e consumidor não
   compartilhavam especificação.**
2. **`checkpoint.md:11` e `wiki-lint.md:6` liam `memory/wiki/_schema.md`, que o `init` nunca criava.**
   Todo checkpoint batia em arquivo ausente.
3. **Nenhuma regra sobre colisão de nome de agente.** O `init` mandava criar agentes em
   `.claude/agents/` e "não duplicar os que já existem" — mas os que já existem são os cinco `orq-*`
   do próprio plugin. A LLM criou com os mesmos nomes apostando que projeto vence plugin, sem poder
   validar. Resolução é indefinida.
4. **A FASE 5 mandava mostrar, não verificar.** Nada conferia se o board era legível, se o
   `CLAUDE.md` sobreviveu, se os agentes carregam.

**Correção estrutural — o `_schema.md` virou o contrato compartilhado.** Em vez de repetir o formato
em cada lugar, o `init` agora **cria** o arquivo, e `checkpoint` e `wiki-lint` **leem** dele. A FASE 5
ganhou smoke test: `kanban-status.sh` com **saída vazia é falha**, e o comando tem que corrigir antes
de declarar sucesso.

**6 lacunas de especificação, também aplicadas:** índice pré-existente em outro caminho (o projeto
tinha `MEMORY.md` na raiz — seguir ao pé da letra criaria dois índices concorrentes, exatamente o que
a wiki existe pra evitar) · custo da FASE 1 quando já se conhece o projeto (a LLM gastou 3 scouts num
repo que tinha acabado de ler; agora o comando manda usar o que já sabe e só cobrir lacunas — "num
projeto pequeno que você acabou de ler, o número certo de scouts é zero") · idempotência falava de
arquivos mas não de trabalho já feito na sessão · `--reinstalar` citado nas Regras e nunca
especificado · as decisões do gate espalhadas por três lugares, agora consolidadas num
`AskUserQuestion` de duas perguntas.

**Não é bug do plugin:** o cache com `orquestra/orquestra/0.1.0` ao lado de `orquestra/orq/0.x` é
resíduo da renomeação da 0.2.0 — todos os plugins da máquina guardam várias versões em cache.

**O que o piloto confirmou que está certo (não mexer):** a frase *"este comando se ADAPTA ao
projeto"* logo no topo — segundo o relatório, sem ela teriam nascido 6 agentes genéricos e uma wiki
de placeholders · *"menos agentes bem definidos > muitos genéricos"* · a separação entre aprovar o
Orquestra e aprovar a stack · o `_stack.md` com "Dispensadas", chamado de "melhor ideia do plugin
inteiro" · a distinção log-append × página-reescrita · scouts com escopo fechado, um dos quais
corrigiu uma premissa errada de quem os despachou.

---

## [2026-07-26] feat | lint de coerência interna (T-008)

`orq/scripts/lint-coerencia.py`. Confere que todo `/orq:x`, `` `orq-agente` ``, `` skill `nome` `` e
`${CLAUDE_PLUGIN_ROOT}/arquivo` citado **existe**. Sai com 1 e lista `arquivo:linha`.

**Por que existe:** `claude plugin validate --strict` valida o manifesto e passa com instruções que
mandam rodar comando inexistente. Foi assim que `/orquestra:*` sobreviveu a três releases.

**Ignora `memory/` de propósito** — requisito que só apareceu ao rodar o protótipo: o log é
append-only e o `gotchas.md` citam nomes extintos ao descrever bugs passados (hoje são 6 ocorrências).
Sem a exclusão, o lint acusaria falso positivo em todo checkpoint — e lint que grita à toa é lint
desligado.

**Testado nos dois sentidos**, que é o que separa lint de teatro: passa no estado atual (18 nomes) e
pega os 4 tipos de defeito quando injetados de propósito.

**Virou verificação obrigatória** no `CLAUDE.md`, ao lado do `validate`. O que nenhum dos dois cobre —
contradição semântica entre arquivos — é trabalho do painel de revisores.

---

## [2026-07-26] fix | painel de revisores consertado (T-010) + 8 achados aplicados no T-009

**Duas causas raiz, ambas achadas por experimento, ambas contra a hipótese inicial:**

1. **`codex exec` bloqueia lendo stdin quando não há TTY.** Imprime
   `Reading additional input from stdin...` e trava até o timeout — **mesmo com o prompt passado como
   argumento**. `< /dev/null` resolve: respondeu em 17 s. A hipótese anterior ("o ambiente do Codex
   injeta 2.155 linhas no lugar do briefing") estava **errada** — o que se via era a sessão pendurada.
2. **Subagente spawnado com `name` nunca devolve resultado.** Com
   `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, o `name` transforma o agente em teammate endereçável:
   emite `idle_notification` e fica vivo esperando mensagem. O **mesmo** agente, mesmo prompt, **sem
   nome**, entregou parecer completo em 231 s.

**Consequência no produto:** o `/orq:revisar` usava o plugin `codex:codex-rescue` com um forwarder e
poll de bash-id. Foi trocado pela CLI direta (`codex exec … < /dev/null`), que é mais simples e agora
comprovadamente funciona. E ganhou a proibição explícita de `name` no spawn do revisor.

**O painel funcionou e pagou o investimento.** O parecer trouxe 8 achados; o mais grave eu não teria
encontrado sozinho: **3 das 7 ferramentas do catálogo se instalam por slash command** (`/plugin
marketplace add`), que o modelo **não consegue invocar** — e a CLI `claude plugin` não tem `install`
nem `marketplace add` (confirmei: só `details`, `enable`, `disable`, `eval`). Sem instrução explícita,
o caminho natural do modelo seria improvisar `git clone` para dentro de `~/.claude/plugins/` ou editar
`installed_plugins.json` na mão — mutação da máquina do dono por fora de todo gate. Agora o passo 4 do
`/orq:stack` manda **entregar o comando pra ele colar** e proíbe o equivalente improvisado.

**Outros aplicados:** `SKILL.md:163` ainda prometia "comando de instalação" (o commit anterior
esqueceu esse arquivo) · catálogo confundia o **plugin** `codex-plugin-cc` com a **CLI** `openai/codex`,
o que faria `/orq:revisar` cair para um revisor achando que tinha dois · detecção de plugin no PATH
sempre falharia (plugin não é binário) · `init` não lia a seção "Dispensadas" antes de propor, então
`--reinstalar` repropunha o recusado · perfis cumulativos arrastavam a camada 3 para quem não precisa ·
`/orq:stack` criava árvore `memory/` em projeto sem Orquestra · `dormir.md` não listava "instalar
ferramenta" entre o proibido à noite.

**Veredito sobre a dúvida do dono (Serena é redundante com codebase-memory?):** não, mas se
sobrepõem em ~20% — os dois acham símbolo por nome. Serena é LSP + **edição**; codebase-memory é
grafo de **relações**. No Orquestra a sinergia é por papel: planner/reviewer ↔ grafo, implementer ↔
LSP. Escolhendo um só: gargalo em *entender* → codebase-memory; em *editar* → Serena. Menos de ~50
arquivos → nenhum dos dois.
