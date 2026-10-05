# Parecer T-144 — Medidor de progresso no Codex

**Data:** 2026-10-04 · **Natureza:** investigação e proposta, sem implementação.

**Recomendação:** manter `progress.py` como autoridade e investir primeiro em marcações fáceis, resumo nos marcos e `watch` visível. Confirmo a decisão de **não espelhar automaticamente** o ledger no plano nativo como requisito do T-144. Há, porém, duas capacidades reais que merecem distinguir dessa decisão: `update_plan` alimenta `task-progress`, e o protocolo do Codex tem eventos estruturados de Goal. Nenhuma delas equivale a uma extensão visual de plugin pronta para usar neste App.

Este parecer não autoriza mudanças no plano aprovado. A [ERRATA:10](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/docs/plano_T-144-medidor-progresso.md:10>) prevalece: fases 1–3, `watch` já na fase 1, sem ETA. A [aprovação registrada:126](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/threads/T-144-mods-claude-code.md:126>) também define este arquivo como entrega separada, sem escrita na worktree ou no board.

## Respostas diretas

| Questão | Parecer |
|---|---|
| 1. Plano nativo e `task-progress` | Espelhamento **possível como projeção parcial**, quando `update_plan` estiver exposto. Não comprovado como sincronização confiável entre CLI/App; não comporta toda a semântica do ledger. Manter a recomendação do planner para o escopo atual. |
| 2. Início/fim de Goal | Existem `thread/goal/get`, `updated` e `cleared` no protocolo. Não encontrei hook de plugin `GoalStart`/`GoalEnd`. Neste chat, `get_goal` é uma ferramenta real de leitura. |
| 3. Identidade nos hooks | `session_id` existe; `PostToolUse` tem `turn_id` e `tool_use_id`. `SessionStart` não tem ID próprio de evento. Os schemas locais são iguais nas três versões examinadas; igualdade comportamental não foi comprovada. |
| 4. Escrita em `.orq/progress` | Compatível com a política documentada se estiver dentro da raiz efetivamente gravável. Escrita real e troca atômica sob `workspace-write` permanecem não comprovadas nesta investigação somente leitura. |
| 5. MCP do plugin | Capacidade real; vale um piloto se o shell causar omissões. Não justifica substituir agora a CLI nem prometer menor consumo de tokens. |
| 6. App, notificações e painel | Há superfícies de atividade e atenção. Não comprovei painel nativo extensível que exiba continuamente o ledger. `watch` continua sendo a vista completa mais sustentada pelas evidências. |

## Host e método de verificação

Os comandos de versão saíram com código `0`:

| Executável consultado | Resultado | Evidência adicional |
|---|---|---|
| `/Users/brunocangucu/.local/bin/codex --version` | `codex-cli 0.160.0` | Primeiro do PATH; [package.json:3](/Users/brunocangucu/.local/lib/node_modules/@openai/codex/package.json:3). |
| `/usr/local/bin/codex --version` | `codex-cli 0.156.1` | [package.json:3](/usr/local/lib/node_modules/@openai/codex/package.json:3). |
| `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex --version` | `codex-cli 0.159.2` | Binário incluído no App deste host, distinto dos dois CLIs do PATH. |

`type -a codex` confirmou a precedência. O bundle local é `/Applications/ChatGPT.app`, versão **26.928.21956**, build **12404**, obtidos de `Contents/Info.plist` com `plistlib`. A inspeção de `ps -axo comm=` localizou processos nesse bundle. Isso identifica instalação/processos; não certifica a versão do backend de cada conversa já aberta.

Os dois checkouts apontavam para `4e58e7f19a8b6b51cb8ab33232862be431b3005d`; principal em `main`, implementação em `claude/t144-medidor-progresso`. Ambos tinham trabalho preexistente. A worktree estava sendo alterada pela outra janela durante a leitura: números de linha deste parecer são uma fotografia, não uma revisão final do T-144.

Foram lidos plano, thread, código/procedimentos da worktree e o Goal Meter original. Para descobrir código, usei o grafo já indexado, com `search_graph → trace_path → get_code_snippet`; para configuração, documentos e binários, leitura localizada e análise por `context-mode`. A busca oficial foi seguida de abertura das páginas e consulta das versões Markdown.

Não houve chamada adicional de modelo, criação de Goal, instalação, execução de mutações do medidor, alteração de configuração ou escrita em `memory/`. A única entrega persistente produzida por este trabalho é este documento. `ctx_fetch_and_index` falhou por dependência ausente (`@mixmark-io/domino`); a leitura das páginas foi feita por `curl`/`urllib`, sem reparar ou instalar dependências.

## 1. Plano nativo: conservar a separação; espelho apenas como experimento opcional

**O que fazer.** Manter `show/watch` como projeção do ledger. Se futuramente houver interesse em espelho, permitir uma vista **unidirecional, descartável e opt-in**, derivada de uma revisão já gravada: IDs nos títulos e revisão na explicação; nunca importar a lista nativa de volta para o ledger. Não habilitar isso no T-144 atual.

**Evidência.** Nos três binários locais aparecem `update_plan` e `task-progress`. No 0.160.0, a descrição embutida de `task-progress` é **“Latest task progress from update_plan (omitted until available)”**. O contrato embutido de `update_plan` admite passos com status e **no máximo um `in_progress`**. A [documentação do App Server](https://learn.chatgpt.com/docs/app-server#turn-events) descreve `turn/plan/updated` como notificação de atualização, com `pending`, `inProgress`, `completed`; não como RPC para um plugin escrever o plano. A [configuração oficial](https://learn.chatgpt.com/docs/config-file/config-reference) define `tui.status_line` como lista de identificadores, sem entrada para executar nosso script.

O ledger admite vários passos ativos e contém pesos, executor, descartes, revisão, lifecycle e fase: [progress.py:448](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:448>). A fase deriva do board em [progress.py:420](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:420>). O [contrato local Codex:26](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/skills/orq/references/hosts/codex.md:26>) e o [plano:237](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/docs/plano_T-144-medidor-progresso.md:237>) preservam essa separação. Nesta sessão, a enumeração das ferramentas disponíveis não expôs `update_plan`; presença no executável não garante disponibilidade ao Manager deste chat.

**O que você passa a ver.** Hoje: fase, percentual ponderado e tarefas no `watch` e nos resumos. Um eventual espelho mostraria uma lista familiar de passos; não há prova de que o número exibido por `task-progress` reproduza nosso percentual ponderado. Com dois workers ativos, seria necessário perder informação ou agregá-los num único passo nativo.

**Custo.** Hoje, nenhum mecanismo novo. Espelho: transformação, chamada adicional, recuperação após compactação e teste por cliente; não há transação única entre gravar o ledger e atualizar o plano nativo.

**Risco.** Ledger atualizado e plano antigo após interrupção; lista nativa replanejada pelo modelo; contagens/percentuais diferentes; renderização distinta no App. Uma explicação com revisão ajuda a detectar divergência, mas não a elimina.

**Fase.** **1:** preservar o contrato atual. **3:** possível experimento de vista, com decisão própria e sem virar critério de aceite do núcleo. Configurar a statusline continua assunto separado de T-042.

**Confirmação/contestação do planner:** confirmo **não espelhar automaticamente** no produto atual. Contesto apenas uma leitura mais forte, “o Codex não consegue exibir progresso derivado de uma lista”: ele consegue, por `update_plan`. A capacidade existe; a equivalência e a confiabilidade exigidas aqui não estão demonstradas.

## 2. Goal: consultar estado estruturado; não confundir evento do protocolo com hook

**O que fazer.** Na boca fina do Manager, consultar `get_goal` quando disponível e houver necessidade de identificar o modo Goal. Vincular explicitamente o resultado ao `run_id` portátil. Em hosts sem essa ferramenta, conservar o início explícito previsto na skill. Para monitoramento automático, só considerar um cliente do protocolo que já tenha acesso autorizado à thread correta; um hook de plugin não deve presumir que possui essa conexão.

**Evidência.** A [documentação oficial de Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) define estado persistente por thread. O [App Server](https://learn.chatgpt.com/docs/app-server#manage-a-thread-goal) expõe `thread/goal/set`, `get`, `clear`, e notificações `thread/goal/updated`/`cleared`. Esses identificadores também existem nos três binários locais. A lista de [hooks documentados](https://learn.chatgpt.com/docs/hooks) não oferece evento específico de Goal. A sonda **real** `get_goal({})`, executada neste chat, devolveu `goal: null`, sem iniciar trabalho nem chamar modelo.

O procedimento portátil já inicia goal explicitamente e separa encerramento do medidor de Goal nativo: [progress.md:123](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/skills/orq/references/progress.md:123>). No original Claude, a captura passa por `on('command.run', { command: 'goal' }, …)`, em [register.mjs:270](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/register.mjs:270>); é API de mod do Claude, não hook portátil do Codex.

**O que você passa a ver.** Um medidor vinculado ao Goal real, sem classificar a frase do usuário. Estado nativo pode informar atividade, pausa ou encerramento; o percentual e a fase detalhada continuam vindo do ledger. `goal: null` informa ausência de Goal, não perda de um ledger de card.

**Custo.** Consulta pelo Manager: uma ferramenta nos pontos de decisão. Listener: conexão, identificação de thread, reconexão e reconciliação por `get`; só ouvir eventos perde transições ocorridas enquanto desconectado.

**Risco.** `updated` não significa exclusivamente “começou” ou “terminou”: deve-se comparar estado e vínculo anterior. A API documentada não entrega um UUID portátil para cada novo Goal. Substituir objetivo na mesma thread exige nova execução; limpar Goal não prova sucesso. Não persistir o texto integral do objetivo para tentar reconhecer identidade, nem fechar card ou Goal automaticamente porque o ledger chegou a 100%.

**Fase.** **1:** procedimento com consulta opcional e fallback explícito. **3:** listener somente como extensão futura da boca fina. **2:** os hooks continuam consultivos, sem inventar evento Goal.

## 3. Hooks: deduplicar chamadas, tornar o vínculo idempotente e validar por host

**O que fazer.** Normalizar campos conhecidos no adaptador Codex; derivar a chave opaca de `host + session_id`, conforme o plano. Em `PostToolUse`, deduplicar por `(session_id, turn_id, tool_use_id, hook_event_name)`, com memória limitada. Em `SessionStart`, fazer operação idempotente sobre vínculo existente; não fingir deduplicação por ID de evento. Conservar a chave proprietária registrada no ledger: um novo ID de host não deve causar `claim` automático.

**Evidência.** A [doc oficial de hooks](https://learn.chatgpt.com/docs/hooks#common-input-fields) especifica `session_id`; subagentes usam o ID da sessão pai. `PostToolUse` documenta `turn_id` e `tool_use_id`. Extraí, **sem gerar arquivos**, os schemas JSON embutidos nos executáveis locais e comparei seu conteúdo canônico:

| Schema | 0.156.1 | 0.160.0 | App/bundle 0.159.2 |
|---|---|---|---|
| `SessionStart` | Mesmo SHA abaixo | Mesmo SHA | Mesmo SHA |
| `PostToolUse` | Mesmo SHA abaixo | Mesmo SHA | Mesmo SHA |

- `SessionStart`: SHA-256 `f96b920ac4c05d3faaf90801ca07255fe0b5c5b8a2bd19bff3d7fdab37c547ae`; `session_id` obrigatório; sem `turn_id`, `tool_use_id` ou `event_id`. O enum local de `source` inclui `startup`, `resume`, `clear`, `compact`, **`fork`**; a tabela da doc consultada lista os quatro primeiros. Não presumir que o quinto foi exercitado.
- `PostToolUse`: SHA-256 `6b6ed2f72e3e8b7fb0d01effd48fb162772261c1a7c64dce5ccb77079a5f938d`; `session_id`, `turn_id`, `tool_use_id` obrigatórios; `agent_id` e `agent_type` opcionais; sem `event_id`.

O [plano:794](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/docs/plano_T-144-medidor-progresso.md:794>) já manda usar ID quando disponível e assumir contagem por entrega quando ausente. A retomada proíbe tomar ownership por idade/PID: [progress.md:140](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/skills/orq/references/progress.md:140>). `progress-hook.py` ainda não existia na worktree na verificação; não há adaptador novo cuja execução eu possa certificar.

**O que você passa a ver.** Um único lembrete útil de plano ausente, com vínculo retomável. Uma entrega duplicada da mesma chamada não deve adiantar o contador. O lembrete é contexto para o modelo, não uma barra contínua que o usuário necessariamente vê.

**Custo.** Baixo no desenho; fase 2 precisa de capturas sintéticas reais em cada host, cobrindo `startup/resume/compact/fork`, chamada normal, execução longa concluída por polling e subagentes. Nenhuma dessas sessões foi iniciada aqui.

**Risco.** `session_id` é identidade de sessão, não identidade exclusiva de escritor. Subagentes podem compartilhar o ID; usar os campos opcionais quando presentes e não inferir que um payload incompleto veio do Manager. Várias fontes de hooks podem coexistir, e hooks não confiados são pulados. ID de chamada não garante entrega exatamente uma vez. Um conjunto limitado a 128 IDs também não deduplica arbitrariamente todo o histórico.

**Fase.** **2**, dentro da normalização e dos testes de lembrete já previstos. O comando deve produzir somente resposta consultiva; não copiar `decision: block`, `continue: false` ou negação do mod original.

**Resposta sobre estabilidade/igualdade:** há contrato e schema para usar `session_id`; não provei sua estabilidade em todas as transições reais. A igualdade dos schemas nos três binários é comprovada. A igualdade de carregamento, confiança, ordenação, entrega e renderização no CLI/App **não é verificável por essa prova estática**.

## 4. Sandbox: manter armazenamento na frente efetivamente autorizada

**O que fazer.** Usar exatamente `front_root` do resolver e conferir que está nas raízes graváveis da sessão do **Manager**. Ler scripts do plugin/cache é distinto de escrever dados nele. Se a frente estiver fora dessas raízes, relatar o impedimento; não deslocar estado para home/cache nem ampliar permissões silenciosamente.

**Evidência.** A [política oficial](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots) permite escritas no workspace em `workspace-write`, preservando caminhos como `.git`, `.codex` e `.agents`. `.orq/progress` não é uma exceção nominal documentada. [Permission profiles](https://learn.chatgpt.com/docs/permissions) distingue `:workspace` das configurações antigas. O [Loop B:34](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/commands/implement-next.md:34>) exige a raiz da frente, não a worktree do implementer; o script prepara lock e destinos locais em [progress.py:907](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:907>) e [progress.py:1139](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:1139>).

Rodei sondas sem escrita com `codex sandbox`. A forma `sandbox macos --help` não é suportada aqui: o CLI tentou executar `macos` e saiu `71`. `sandbox --help` saiu `0`. A invocação com apenas `-c 'sandbox_mode="workspace-write"'` saiu `2`, exigindo `--permission-profile`. A forma `sandbox -P :workspace -C <checkout> /usr/bin/python3 -c <sonda>` saiu `0` nos três binários. A consulta `sandbox_check` não forneceu controle positivo discriminante: retornou o mesmo resultado em caminhos internos/externos e no baseline. **Não a interpreto como prova de permissão nem como bloqueio do medidor.**

**O que você passa a ver.** Com a raiz correta e escrita permitida, a mesma vista portátil; sem dependência de autorização para gravar no home. Se houver restrição, erro explícito em vez de progresso aparentemente atualizado.

**Custo.** Nenhum aumento de permissão inerente ao desenho. O aceite exige futuramente um ciclo sintético real de criação, lock, arquivo temporário e substituição atômica sob a política alvo.

**Risco.** Raiz de Manager diferente da raiz do worker; symlink escapando; ACL/perfil gerenciado; operação de Git que tente escrever metadados protegidos. A presença de arquivos ignorados e a ausência de pedido de aprovação nesta sessão não provam o sandbox: este chat roda com permissões diferentes de `workspace-write`.

**Fase.** **1**, aceite de persistência no Codex. A resposta é **sim, sob as condições documentadas**, com comprovação prática ainda pendente; não “já testado e garantido neste App”.

## 5. MCP: piloto para marcação, com o mesmo núcleo e sem estado global implícito

**O que fazer.** Manter a CLI como caminho obrigatório. Se o uso mostrar marcações esquecidas por atrito de shell, pilotar MCP local por STDIO: uma ferramenta de leitura e uma de operação tipada que deleguem ao núcleo existente. Exigir endereço/raiz e chave por chamada; não usar “ledger atual” global de servidor. Não implementar cálculo, ownership ou inferência de conclusão no adaptador.

**Evidência.** [Empacotamento oficial de plugins](https://developers.openai.com/plugins/build/plugins#bundled-mcp-servers-and-lifecycle-hooks) suporta MCP em plugin; formatos portátil e legado têm diferenças. A [doc MCP do Codex](https://learn.chatgpt.com/docs/extend/mcp) suporta processos STDIO, ambiente/CWD e política de aprovação por ferramenta. Neste host, servidores MCP já são ferramentas reais da sessão; isso comprova MCP no host, **não** carregamento de um futuro servidor T-144. O núcleo concentra a mutação em [progress.py:1453](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:1453>), e seu recibo contém revisão/caminho/chave em [progress.py:991](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:991>).

**O que você passa a ver.** A mesma barra, com menor probabilidade de o Manager errar quoting, caminho do script ou formato de argumentos. MCP facilita marcar; não cria automaticamente painel de progresso.

**Custo.** Inicialização/processo, protocolo, schema das ferramentas, configuração/empacotamento e testes em duas interfaces. Cada marcação continua uma chamada de ferramenta e seu resultado consome contexto. Não houve medição de tokens ou latência; reduzir o tamanho dos argumentos pode ajudar, mas isso não demonstra economia líquida. Um servidor stdlib próprio ainda precisa implementar corretamente JSON-RPC/MCP; usar SDK adicionaria dependência ao adaptador.

**Risco.** Serviço atendendo várias threads misturar execuções; cache/plugin incompatível; falha de startup; aprovações adicionais; tratar mutação como `readOnly` para evitar prompt. Não presumir que o servidor herda o sandbox da chamada de shell do Manager. O adaptador deve restringir raízes e preservar as checagens do núcleo, sem ampliar a autoridade de workers.

**Fase.** **2**, extensão opcional a planejar se o atrito for observado. Não é dependência das fases aprovadas nem motivo para atrasar o núcleo. Critério do piloto: menor taxa de marcação omitida, mesmas revisões/resultados e comportamento de erro/ownership equivalente à CLI.

## 6. Vista contínua: terminal dedicado; App e notificações como complemento

**O que fazer.** Entregar o comando de `watch` pronto com caminho absoluto da fonte instalada comprovada e endereço da execução. Se o cliente conseguir criar/operar um terminal dedicado, usá-lo para reduzir o trabalho manual; caso contrário, conservar o terminal ao lado. Não iniciar `watch` infinito na ferramenta de shell que mantém o Manager esperando.

**Evidência.** [progress.py:1519](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:1519>) lê a projeção, só imprime quando o quadro muda, redesenha em TTY e tem saída finita por `--count`. [progress.md:204](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/skills/orq/references/progress.md:204>) explica o terminal dedicado. Executei `watch --root <principal> --card T-144 --count 1`: exit `0`, quadro de indisponibilidade porque não havia ledger; não criei um.

A [documentação de notificações](https://learn.chatgpt.com/docs/notifications) descreve Activity e pet como vistas de atividade/atenção, com estados como Running/Needs input/Ready/Blocked. A [configuração avançada](https://learn.chatgpt.com/docs/config-file/config-advanced#notifications) limita `notify` atualmente a `agent-turn-complete`; as notificações TUI também atendem pedidos de aprovação. São eventos de atenção, não um feed do percentual do ledger. Neste host, `open_in_codex` permite abrir uma aba de terminal; o contrato dessa ferramenta não executa o comando nem comprova vínculo com uma sessão de `exec_command`.

**O que você passa a ver.** Fase, passos concluídos, percentual ponderado, em execução, próximos e última atualização sem pedir ao modelo. Activity/notificações podem avisar “precisa de você”; não mostram por si sós “P06 em revisão, 69% do plano”.

**Custo.** Um processo leitor, sem LLM residente, mais espaço de terminal. Frequência de leitura limitada pelo intervalo; o medidor só muda quando o Manager registra algo. Painel próprio em cliente controlado exigiria engenharia adicional de UI e poderia consumir `show --format json` sem reimplementar cálculo.

**Risco.** Abrir terminal não é iniciar monitor; anexar saída de terminal em uma resposta não garante atualização visível contínua. Não há prova aqui de uma API de plugin para inserir faixa persistente no compositor do App. Alertar a cada ferramenta/percentual causaria ruído e não corrigiria marcações ausentes.

**Fase.** **1:** `watch` individual, conforme ERRATA. **3:** procedimento Orca, múltiplas raízes e eventual conveniência do terminal integrado. Não instalar notificadores, pets ou painel como parte deste parecer.

## 7. Melhor ganho imediato: feedback curto de marcação e disciplina nos marcos

**O que fazer.** Priorizar o procedimento já aprovado: marcar `start` antes do despacho, `done` depois da evidência e `phase` na mudança de papel; mostrar `show` nos marcos. Como melhoria a deliberar, acrescentar ao recibo de mutação uma projeção compacta opcional, calculada pelo núcleo, para evitar uma chamada `show` extra. A projeção deve indicar a revisão consultada; falha de apresentação após uma mutação bem-sucedida não pode induzir retry cego da escrita.

**Evidência.** [implement-next.md:43](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/commands/implement-next.md:43>) coloca as marcações sob o Manager. [progress.py:991](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:991>) hoje devolve recibo, sem fase/percentual; [progress.py:513](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py:513>) já tem o renderizador portátil. A [ERRATA:14](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/docs/plano_T-144-medidor-progresso.md:14>) identifica o custo das marcações como modo de falha.

**O que você passa a ver.** Nos marcos, uma linha factual como `T-144 · revisão · 5/8 · 69% do plano`, acompanhada da evidência quando necessária. Com o recibo ampliado, o Manager receberia esse feedback junto da marcação e teria menos motivo para pular a leitura. É proposta, ainda não comportamento entregue.

**Custo.** Baixo para o procedimento existente; pequeno ajuste e testes de contrato para o recibo opcional. Não exige MCP, hook Goal nem alteração de configuração do Codex.

**Risco.** Uma vista perfeita pode permanecer desatualizada se ninguém marcar. Não inferir `done` de exit `0`, contagem de ferramentas, elapsed time ou término de um turno: comando bem-sucedido pode não cumprir o aceite do passo. A vista precisa conservar “100% do plano; aguarda validação”, já previsto no renderizador.

**Fase.** **1**. O procedimento já pertence ao escopo; a ampliação do recibo é sugestão nova para decisão do Manager/dono, não alteração feita por este parecer.

## Registro das sondas e reprodução

As sondas de leitura do medidor usaram a fonte em andamento, `PYTHONDONTWRITEBYTECODE=1` e `/usr/bin/python3`:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "/Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso/orq/scripts/progress.py" show --root "/Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra" --card T-144
```

Resultado: exit `4`, erro JSON `ledger-ausente`. A variante `watch` com o mesmo endereço e `--count 1` saiu `0`, mostrando `indisponível: ledger inexistente…`. Isso testa degradação sem ledger, não uma barra em execução real.

Para introspecção, foram executados `app-server --help`, `app-server generate-json-schema --help`, `sandbox --help` e `features list`. **Não executei geração de schema em diretório**. A comparação dos schemas foi feita diretamente nos bytes destes executáveis nativos:

```text
0.160.0: /Users/brunocangucu/.local/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex
0.156.1: /usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex
App:     /Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex
```

Script de leitura executado, com a lista acima em `binarios`:

```python
from pathlib import Path
import hashlib, json, re

for arquivo in binarios:
    dados = Path(arquivo).read_bytes()
    for match in re.finditer(rb'\{\s*"\$schema"\s*:', dados):
        trecho = dados[match.start():match.start() + 250000]
        try:
            schema, _ = json.JSONDecoder().raw_decode(
                trecho.decode("ascii", "replace")
            )
        except ValueError:
            continue
        campos = schema.get("properties", {})
        evento = campos.get("hook_event_name", {}).get("const")
        if evento not in ("SessionStart", "PostToolUse"):
            continue
        canonico = json.dumps(schema, sort_keys=True, separators=(",", ":"))
        print(evento, match.start(), schema.get("required"), sorted(campos),
              hashlib.sha256(canonico.encode()).hexdigest())
```

Offsets zero-based encontrados (`PostToolUse` / `SessionStart`): `182395662 / 182408723` no 0.156.1; `184925468 / 184938529` no 0.160.0; `183926812 / 183939873` no bundle 0.159.2. São offsets de binário, **não linhas de fonte**; não atribuo `arquivo:linha` fictício a executáveis. As evidências de fonte/procedimento estão vinculadas em cada sugestão.

Para a sonda de política sem escrita, executei cada CLI com `sandbox -P :workspace -C <principal> /usr/bin/python3 -c <consulta>`, além do baseline. A consulta chamou `sandbox_check` de `/usr/lib/libsandbox.dylib`, com assinatura fixa `(int, char *, int)` e argumento variádico de caminho; não chamou `open`, `mkdir`, rename ou escrita. A primeira tentativa sem assinatura fixa retornou `-1/EINVAL`; a corrigida retornou `1/errno 0` inclusive no baseline e sem distinguir os controles. Consequentemente não sustenta uma conclusão operacional sobre permissões.

Fotografia final lida de `progress.py`: SHA-256 `45a24b6a235a9f6d88da02e76529d1675b100c68edde92516b20ac6e5031851a`. O checkout compartilhado seguiu recebendo alterações da janela Claude; qualquer implementação baseada neste parecer precisa revalidar as linhas e o código final.

## O que não recomendo

- **Espelho obrigatório ou bidirecional do plano nativo.** Perde pesos, paralelismo e gates; adiciona uma segunda escrita sem transação e pode produzir duas respostas diferentes para “quanto falta”.
- **Injetar script em `tui.status_line` ou tratar `task-progress` como percentual externo.** A configuração seleciona itens nativos; não é um callback do plugin. Presença no binário não comprova a vista do App.
- **Usar `SessionStart`, `Stop`, `SessionEnd` ou `notify` como começo/fim de Goal.** Seus ciclos têm outros significados; fim de turno e fim de sessão não provam objetivo cumprido. Os eventos Goal do protocolo não viram hooks só por existirem.
- **Interpretar prompt, transcript ou banco privado do App para descobrir Goal/progresso.** Há estado estruturado onde disponível e um fallback explícito portátil; parsing desses conteúdos ampliaria fragilidade e exposição sem necessidade.
- **Usar hooks para marcar conclusão, tomar ownership ou bloquear trabalho por falta de plano.** Lembrete é consultivo; o Manager precisa conferir evidência. O modo strict do Goal Meter original não pertence ao T-144.
- **Substituir CLI por MCP agora, ou fazer o núcleo depender do servidor.** Acrescenta operação antes de provar que o shell é o atrito dominante. MCP facilita marcação; não elimina seu custo nem entrega uma UI por si só.
- **Conservar estado autoritativo em home/cache, instalar mod Claude no Codex, produzir ETA ou emitir alerta a cada passo.** Contraria portabilidade/escopo ou introduz ruído. Prefiro última atualização, fase e próximos passos.

## O que não consegui comprovar

1. Renderização de uma lista espelhada e de `task-progress` numa TUI nova de cada versão e neste App; também não medi a fórmula, persistência e recuperação da vista nativa.
2. Entrega real de `thread/goal/updated`/`cleared` a um plugin ou listener conectado à thread atual. `get_goal: null` comprova apenas a consulta neste chat.
3. Estabilidade de `session_id` e diferenças de entrega de hooks em resume/compact/fork, subagentes e execução longa nos três hosts. Schema idêntico não prova comportamento idêntico nem confiança ativa.
4. Criação, lock e troca atômica real em `.orq/progress` sob `workspace-write`. Por escopo somente leitura, nenhum ledger, fixture ou diretório foi criado para esse teste.
5. Carregamento, permissões, isolamento e economia de um MCP **T-144** empacotado. Nenhum servidor novo foi iniciado ou instalado.
6. API de plugin que mantenha um painel de ledger atualizado no App, e ligação operacional entre uma aba de terminal do App e um `watch` iniciado pela ferramenta do Manager.
7. Validação/release final do T-144, testes comportamentais pós-release ou funcionamento entre máquinas. Este parecer não substitui os gates da implementação.
