# Plano T-144 — Medidor de progresso portátil

> **Origem:** planner·sistema `gpt-6-astra@xhigh` via Codex Companion, read-only (`--fresh`, sem
> `--write`), 2026-10-04 · `jobId` `task-mutuafj8-6cws86` · `threadId`
> `01a1070a-4151-7de1-8213-5420a79b1b6b` · `touchedFiles: []`. Corpo abaixo é o `rawOutput` íntegro.
>
> **Estado:** **APROVADO pelo dono em 2026-10-04**, com as recomendações do Manager. A ERRATA
> abaixo vence o corpo onde os dois divergirem.

## ERRATA — vence o corpo

1. **Escopo aprovado:** fases 1–3. Fase 4 (mod do Claude) e `T-042` ficam fora deste card.
   **Sem ETA** em nenhuma fase.
2. **Escrita simplificada.** O atrito de cada marcação é o modo de falha do medidor: se custar
   caro, o Manager pula a atualização e a barra mente.
   - O ledger é endereçável por `--root ABS --card T-NNN` (card) ou `--root ABS --run UUID`
     (goal), além de `--ledger ABS`. `--root` é a `front_root` devolvida pelo resolver.
   - `--expect-revision N` passa a ser **opcional**. Ausente: a mutação ocorre sob lock, com troca
     atômica e verificação de dono. Presente e divergente: exit `3`, sem gravar.
   - `--session-key` continua obrigatório nas mutações. É constante durante a execução, e o
     Manager grava esse valor na thread do card ao fazer o `begin`.
3. **`watch` sobe para a fase 1.** Ele usa a mesma projeção do `show`, é leitor puro e é a única
   vista contínua que vale para Claude, Codex e Orca. A fase 3 fica com o procedimento do Orca
   (`orq/skills/orq/references/progress-orca.md`) e o teste de `watch` com várias raízes.
4. **Schema** em `orq/schemas/progress-ledger-v1.json`, não em `orq/scripts/schemas/` — o
   diretório existente é `orq/schemas/` (`audit-ledger-v1.json`).
5. **Faixa revalidada:** `normal`. O desenho está fechado e o card não é Alto risco.
6. **Isolamento:** todo o trabalho fica na branch `claude/t144-medidor-progresso`, na worktree
   `/Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra-worktrees/t144-medidor-progresso`,
   fora do checkout principal: worktree aninhada quebra a suíte da `main` (`T-142`).
7. **Sem commit em `orq/` enquanto o dono não atribuir a versão.** A regra do projeto exige bump
   nos quatro lugares no mesmo commit, e o bump depende do ok dele. O implementer deixa as
   mudanças no working tree da worktree; o Manager commita no fechamento, com a versão atribuída.
   `memory/` não é tocado pelo implementer.

---

**Recomendação: implementar um núcleo portátil em Python, com ledger por execução na frente dona, sem depender de recursos de `/goal`, MCP ou mods.** A fase vem do board; a porcentagem vem dos passos verificáveis do plano. Claude, Codex e Orca consomem esse mesmo estado.

Não escrevi arquivos, não alterei configurações e não executei instalação, testes, inferência ou publicação.

## 1. Diagnóstico e decisão de desenho

### 1.1. O problema é orientação durante a execução

O Goal Meter oferece uma referência útil: tarefas ponderadas, executor por tarefa e visibilidade das alterações do plano. Seu cálculo usa S/M/L = 1/2/3; tarefas descartadas saem do denominador. A estimativa temporal usa o tempo desde o início do plano e aparece após duas conclusões. Isso está em [plan.mjs:55](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/plan.mjs:55>) e [plan.mjs:76](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/plan.mjs:76>).

O Orquestra precisa mostrar duas informações distintas:

| Informação | Fonte de autoridade | Exemplo |
|---|---|---|
| Fase do desenvolvimento | Board, complementado pela atividade declarada pelo Manager | Revisão |
| Trabalho executado dentro do plano | Ledger dos passos aprovados | 5/8 concluídos · 69% do plano |

Essa separação é necessária porque `[~]` representa READY/DEV_REVIEW e não distingue implementação, revisão e documentação. O board continua sendo a autoridade dos gates; a TaskList nativa não o substitui. Evidência: [arquitetura.md:150](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/arquitetura.md:150>) e [_schema.md:20](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/_schema.md:20>).

**Exibição proposta:**

```text
T-144 · revisão · 5/8 passos concluídos · 69% do plano
Em execução: P06 — conferir retomada · reviewer/codex
Próximos: P07 — documentar; P08 — validar integração
Plano: 7 → 8 passos
```

Usar “concluídos”, não “passo 5”, porque podem existir tarefas paralelas. A porcentagem mede trabalho declarado concluído pelo Manager após verificação; não mede probabilidade de sucesso nem aprovação do dono.

**100% dos passos nunca implica DONE.** Em VALIDATE, a vista deve dizer, por exemplo:

```text
T-144 · validação do dono · 8/8 · 100% do plano
```

Isso preserva o encerramento previsto em [implement-next.md:77](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/implement-next.md:77>).

### 1.2. Ledger semântico por execução; sessão apenas como vínculo

Recomendo este armazenamento:

```text
<FRONT_ROOT>/.orq/progress/
  .gitignore                 # conteúdo: *
  v1/
    cards/T-144.json
    goals/<run_uuid>.json
    sessions/<session_key>.json
    locks/<identificador>.lock
```

**Decisões:**

- Card: um ledger na **frente dona**, reutilizado ao retomar o mesmo card.
- Goal avulso: um UUID por execução.
- Sessão: vínculo com o ledger, não recipiente das tarefas.
- `FRONT_ROOT`: raiz da frente do Manager, comprovada pelo resolver existente; nunca o worktree temporário do implementer.
- O Manager passa o caminho absoluto do ledger nos briefings. Workers devolvem progresso e evidência ao Manager; não escrevem o ledger.
- Outra sessão pode consumir o mesmo ledger. Para assumir a escrita, precisa realizar uma transferência explícita de ownership.
- Nenhum arquivo global `current.json` compartilhado por todas as janelas.

O resolver já fornece `front_root`, `thread_root` e board canônico separados: [kanban-status.sh:140](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/kanban-status.sh:140>). O protocolo atual exige frente e thread com dono único: [arquitetura.md:286](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/arquitetura.md:286>).

**Por que esse lugar:**

| Alternativa | Decisão |
|---|---|
| `memory/` versionado | Rejeitar para telemetria: gera alterações frequentes e disputa com documentos duráveis. |
| Home compartilhado | Rejeitar como padrão: exige escrita fora do workspace no Codex e outra convenção de permissões. |
| `PLUGIN_DATA` | Rejeitar como autoridade: pertence ao host/plugin; não garante compartilhamento entre Claude e Codex. |
| Diretório ignorado na frente | Adotar: funciona no workspace, mantém ownership e separa runtime de Git. |

O `begin` cria somente seu diretório de estado e o `.gitignore` local. Antes disso, verifica se há arquivos versionados naquele destino; havendo, recusa inicialização sem sobrescrever nada. Se o `.gitignore` já existir, preserva-o e verifica se o armazenamento está efetivamente ignorado.

**Limite assumido:** portabilidade entre hosts na mesma máquina/frente; não sincronização entre máquinas. Ao remover uma frente, o checkpoint durável deve preservar o resultado na thread. Não haverá cópia automática ao home, exportação remota ou limpeza automática.

### 1.3. Concorrência: escrita única com proteção mecânica

A disciplina de um Manager escritor será complementada por:

1. Lock de kernel por ledger, com espera limitada.
2. `revision` crescente.
3. Toda mutação exige `--expect-revision`.
4. Toda mutação exige o `session_key` proprietário.
5. Escrita em temporário no mesmo diretório, `flush`, `fsync` e `os.replace`.
6. Leituras sem criar diretórios, locks ou arquivos.

`os.replace` sozinho evita JSON parcial, mas não evita perda de atualização; por isso precisa da transação com lock e revisão.

O projeto já emprega gravação atômica em [context-guard.py:423](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/context-guard.py:423>) e documenta locks de kernel em [arquitetura.md:368](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/arquitetura.md:368>). Reaproveitar o padrão, sem refatorar o guardião neste card.

Não haverá tomada automática de ownership por idade, PID ou “sessão parece morta”. O identificador do escritor é proteção contra colisão, não credencial nem ACL.

### 1.4. Semente derivada do plano aprovado

**Adotar a ideia proposta.**

O Planner passa a produzir uma tabela estruturada dos passos:

```text
ID | Entrega verificável | Tamanho | Critério de aceite
P01 | ...               | S       | A01
P02 | ...               | L       | A02
```

Após aprovação, o Manager registra essa lista no ledger. Planejamento não gera porcentagem de implementação.

Regras:

- IDs estáveis; ordem preservada.
- S/M/L representam peso relativo, não minutos.
- `done` requer referência à evidência verificada.
- Acrescentar trabalho aumenta o denominador; a porcentagem pode cair.
- Descartar preserva a tarefa e seu motivo no ledger.
- Reabrir tarefa concluída reduz o progresso.
- O registro do plano é idempotente; não substitui silenciosamente tarefas existentes.
- Mudança de escopo continua passando pelo ciclo normal do Orquestra.
- Planos antigos podem receber IDs e pesos pelo Manager, mantendo correspondência com os passos já aprovados. Uma mudança material exige novo gate.

O Loop B já exige plano aprovado e retorno com resultado, testes e limitações: [implement-next.md:16](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/implement-next.md:16>) e [implement-next.md:50](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/implement-next.md:50>).

### 1.5. Goal avulso

Um goal sem card usa o mesmo núcleo, com:

- `kind = "goal"`;
- `card_id`, board e thread ausentes;
- título curto e genérico;
- fases `planning`, `execution` e `verification`;
- passos criados pelo modelo a partir do objetivo autorizado.

Não criar um card automaticamente apenas para alimentar o medidor. Entretanto, um goal que pede mudança em projeto Orquestra continua sujeito ao ciclo do projeto; o medidor não concede autorização.

Sem integração nativa, o encerramento será **“execução encerrada pelo Manager”**, não “goal check aprovado”.

### 1.6. CLI portátil, sem MCP na primeira implementação

Adotar `orq/scripts/progress.py`, Python stdlib, chamado pelo shell dos dois hosts.

O caminho segue o protocolo existente:

- Claude: raiz comprovada a partir de `${CLAUDE_PLUGIN_ROOT}`.
- Codex: ancestral da skill que contém `.claude-plugin/plugin.json`, com `skills/`, `commands/` e `scripts/`.
- Demais hosts: mesmo protocolo de descoberta, sem caminho fixo.
- Uma variável definida em uma chamada de shell não deve ser presumida disponível na próxima.

Evidência: [SKILL.md:17](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/skills/orq/SKILL.md:17>).

**MCP de plugin é uma capacidade real do Codex**, não motivo para rejeitar a alternativa. A documentação oficial descreve servidores MCP distribuídos em plugins. No binário local 0.156.1 também encontrei referências a `.mcp.json`, `mcpServers` e parsing do manifesto. Não iniciei servidor para comprovar carregamento operacional. [Documentação oficial de empacotamento](https://developers.openai.com/plugins/build/plugins).

Ainda assim, CLI é a escolha recomendada: não adiciona servidor, transporte, inicialização nem dependência para uma operação local simples. Um eventual MCP futuro deverá apenas chamar o mesmo núcleo.

### 1.7. Lembrete consultivo

O mod de referência lembra após quatro ferramentas e pode negar edição no modo strict: [register.mjs:324](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/register.mjs:324>). Copiar somente a ideia do lembrete.

Criar um adaptador independente, `progress-hook.py`, nos eventos:

- `SessionStart`: informar como vincular/retomar o medidor e fornecer a chave opaca da sessão.
- `PostToolUse`: contar eventos da sessão vinculada quando já existe execução iniciada, mas ainda não há plano registrado.

Após quatro eventos elegíveis, emitir **um** `additionalContext` curto. Sem repetição até novo vínculo/execução.

Não adicionar hooks do medidor a `Stop`, `PreToolUse`, `PreCompact` ou `PostCompact`. Nenhuma resposta poderá conter bloqueio, negação ou continuação compulsória.

O arquivo de hooks é compartilhado, mas o guardião atual só atua quando encontra o ambiente nativo `PLUGIN_ROOT` do Codex: [context-guard.py:622](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/context-guard.py:622>). Portanto, não basta copiar seu código e alegar suporte aos dois hosts.

**Limitação explícita:** sem `begin`/vínculo, hooks genéricos não sabem com segurança que começou um goal. O início deve ser instruído pela skill e pelo Loop B. Não interpretar a frase do usuário nem varrer transcript para descobrir isso. Falta de plano durante PLANNING ou gate de aprovação não dispara cobrança de plano aprovado.

### 1.8. Vistas e capacidades comprovadas

| Superfície | Entrega recomendada | Limite |
|---|---|---|
| Qualquer host | `show` em texto/JSON e resumo do Manager nos marcos | Independente de interface nativa. |
| Claude | Segmento na statusline existente | Instalação continua opt-in; preservar configuração anterior. |
| Codex CLI | Texto do medidor; statusline nativa permanece independente | Sem injeção do ledger em `tui.status_line`. |
| Orca | Terminal com leitor local `watch` | Somente leitura, sem agente residente. |
| Mod Claude | Faixa/painel em plugin separado, posterior | Exige host compatível e aprovação própria. |

**Claude.** A barra atual encontra o script vizinho e degrada sem `jq`: [statusline.sh:13](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/statusline.sh:13>) e [statusline.sh:115](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/statusline.sh:115>).

Segmento:

```text
◎ T-144 · revisão · 5/8 · 69%
```

A instalação passará a copiar o conjunto `statusline.sh`, `kanban-status.sh` e `progress.py`, com as guardas existentes de destino, escopo e backup. Configuração não aponta para cache versionado. Evidência: [init.md:359](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/init.md:359>).

**Codex.** Há duas instalações locais:

- `/usr/local/bin/codex`: **0.156.1**, confirmado por `--version` e [package.json:3](/usr/local/lib/node_modules/@openai/codex/package.json:3).
- `codex` prioritário no PATH: **0.160.0**.

No binário 0.156.1 existem identificadores como `task-progress`, `context-remaining` e `git-branch`. Isso é evidência estática; não executei o seletor nem comprovei renderização em uma TUI nova.

O contrato local é inequívoco: `task-progress` pertence à tarefa/plano da sessão; a barra não executa scripts arbitrários nem lê o board. [codex.md:26](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/skills/orq/references/hosts/codex.md:26>). A documentação oficial também define `tui.status_line` como lista de identificadores. [Referência de configuração](https://learn.chatgpt.com/docs/config-file/config-reference).

T-042 poderá configurar itens nativos com backup, rollback e validação visual. **T-042 não cria, por si só, uma entrada para nosso percentual.** Não configurar IDs neste card e não espelhar automaticamente o ledger em uma segunda lista nativa.

**Orca.** Li os guias da instalação por `orca skills get orca-cli --json` e a referência de browser:

- Terminais: criação, leitura e acompanhamento disponíveis.
- Comentário de worktree: campo curto de status, atualizado por uma operação de escrita.
- Browser embutido: navegação por URL disponível.
- Artefatos: publicação de HTML/Markdown por conta autenticada, com link acessível a terceiros.

Consequentemente:

- Adotar terminal local com `watch`.
- Não atualizar comentários automaticamente: disputariam um campo compartilhado e introduziriam escrita no Orca.
- Não publicar artefato.
- Não prometer `file://`, atualização automática de arquivo local ou servidor local no browser: não comprovei essas propriedades.

Isso mantém o Orca como ambiente consumidor, conforme [desenho T-141:24](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/docs/superpowers/specs/2026-09-29-t141-orca-portavel-design.md:24>). Não altera seu piloto, despacho ou ownership.

**Mod separado.** A referência usa `modules` no próprio `hooks/hooks.json`: [hooks.json:1](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/hooks.json:1>). Não colocar essa chave no bundle compartilhado do Orquestra. O risco de atualização de cache em sessão Codex viva está documentado em [gotchas.md:854](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/gotchas.md:854>).

### 1.9. ETA e goal check

**Goal check: fora da fase 1 e fora da autoridade do ledger.**

A referência procura o resultado na cauda do transcript e aceita formatos não documentados: [register.mjs:183](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/register.mjs:183>) e [plan.mjs:182](</Users/brunocangucu/Downloads/nateherk-claude-code-mods/goal-meter/hooks/plan.mjs:182>).

Isso não oferece contrato portátil nem prova de conclusão. Nenhuma fase proposta precisa ler transcript.

**ETA: recomendo deixar fora das três primeiras fases.** O tempo desde o planejamento inclui aprovação, pausas, revisão e interrupções; duas tarefas concluídas não resolvem essa distorção. O medidor entrega primeiro fase, concluído, ativo, próximo e crescimento do plano. Estimar tempo deve ser uma evolução separada, depois de observar execuções reais.

## 2. Fases com passos verificáveis

### Fase 1 — Núcleo portátil e integração com os procedimentos

1. Criar schema, cálculo puro, persistência transacional e CLI.
2. Acrescentar consulta estruturada de um card ao parser existente do board.
3. Introduzir IDs, pesos e critérios de aceite no formato de plano.
4. Integrar `begin`, `plan`, atualizações e `show` ao Loop B.
5. Integrar goal avulso à skill, sem interceptação de prompt.
6. Documentar retomada, ownership, perda de estado e limites do percentual.
7. Validar tudo com fixtures sintéticas e os três gates.

Entrega: Claude e Codex atualizam e leem o mesmo ledger por shell; o Manager apresenta progresso nos marcos.

### Fase 2 — Lembretes e statusline Claude

1. Criar adaptador de hooks com normalização explícita por host.
2. Acrescentar entradas independentes de `SessionStart` e `PostToolUse`.
3. Implementar vínculo por sessão e lembrete único após quatro eventos.
4. Acrescentar segmento Claude por leitura do ledger vinculado.
5. Atualizar instalação do conjunto de scripts, guardas e rollback.
6. Validar ausência de regressões no context-guard e no contrato Codex.

Entrega: visibilidade contínua no Claude e lembrete consultivo nos dois hosts.

### Fase 3 — Vista local no Orca

1. Criar `watch`, usando exatamente a projeção de `show`.
2. Aceitar um ledger ou uma lista explícita de raízes.
3. Mostrar fase, tarefas, executor e horário da última atualização.
4. Documentar uso em terminal dedicado do Orca.
5. Validar duas execuções simultâneas e ausência de qualquer escrita pelo leitor.

Entrega: vista local da execução no Orca, sem dependência do piloto T-141.

### Fase 4 — Extensão visual Claude, opcional e separada

1. Criar card/pacote próprio após aceite do núcleo.
2. Confirmar suporte a mods na versão autorizada do Claude.
3. Implementar faixa/painel que consome `show --format json`.
4. Manter toda mutação no núcleo portátil.
5. Validar desligamento/desinstalação sem perda de progresso.
6. Instalar somente no Claude, com autorização específica.

Essa fase não condiciona o encerramento do T-144 recomendado. T-042 também permanece independente.

## 3. Riscos e o que pode quebrar

| Risco concreto | Tratamento |
|---|---|
| Duas janelas sobrescrevem o mesmo ledger | Ownership, lock, revisão esperada e substituição atômica. |
| Outro worktree cria cópia do mesmo card | Caminho da frente dona passado explicitamente; nenhum fallback para cópia local. |
| Remoção da frente apaga estado ignorado | Checkpoint durável antes da remoção; não tratar ledger como arquivo histórico. |
| Codex tenta escrever no home/cache | Estado dentro do workspace do Manager; nenhum aumento automático de permissões. |
| Codex executado por PATH diferente | Registrar executável e versão na validação; testar explicitamente 0.156.1. |
| `task-progress` diverge do ledger | Não criar sincronização nem prometer equivalência. |
| Atualização do plugin quebra hooks de sessão viva | Respeitar T-093; nenhuma instalação durante trabalho ativo sem procedimento autorizado. |
| Novo hook interfere no context-guard | Entradas separadas; preservar as seis integrações existentes e testar coexistência. |
| Board contém fences, arquivo histórico ou ID duplicado | Reutilizar o parser atual; não criar regex simplificada concorrente. |
| JSON inválido vira “0%” | Exibir indisponibilidade; nunca reconstruir sucesso silenciosamente. |
| Renderização grava arquivos ou toca em estado | `show`, `watch` e adaptador de statusline estritamente leitores. |
| Títulos contêm controles de terminal ou informações sensíveis | Títulos genéricos, limites, rejeição de controles; nenhum prompt, transcript, diff ou saída de ferramenta armazenado. |
| 100% é interpretado como aprovação | Percentual sempre qualificado como “do plano”; fase/gate continuam explícitos. |
| Artefato Orca expõe tarefas | Não utilizar publicação de artefatos para essa vista. |

**Autocrítica — o que não está comprovado:**

- Não executei uma TUI 0.156.1 para confirmar visualmente os itens nativos.
- Não capturei eventos reais dos dois hosts nesta investigação; seus payloads precisam de validação comportamental na fase 2.
- Não provei a escrita do novo diretório sob o sandbox real de um implementer; isso é aceite da fase 1.
- Não provei comportamento em Windows nem filesystem remoto. Os testes devem cobrir backends de lock; suporte não testado permanece declarado.
- Não provei integração visual do `watch` no Orca; os guias comprovam a superfície de terminal, não o novo produto.
- Não existe contrato portátil comprovado para início/veredito de goal. O desenho depende de instrução explícita ao Manager para registrar a execução.
- Locks protegem concorrência local, não sincronização distribuída.
- Evidência referenciada pelo Manager não é verificação automática de que um teste realmente passou.

Essas limitações viram critérios de aceite, não pressupostos escondidos.

## 4. Critérios de aceite verificáveis por fase

### Fase 1

- Mesma sequência de operações em Claude e Codex produz projeções equivalentes.
- Goal avulso funciona sem board.
- Card usa exclusivamente board canônico e frente dona comprovados.
- Exemplo com 11 unidades concluídas de 16 produz **69%**, com contagem de tarefas independente.
- Sem plano: percentual ausente; nunca 0% fictício.
- Todas as tarefas descartadas: “sem passos ativos”; nunca 100%.
- `add`, `drop` e `reopen` ajustam numerador/denominador corretamente.
- Plano repetido não duplica tarefas nem redefine conclusões.
- Dois processos com a mesma revisão: um vence; o outro recebe conflito, sem perda de atualização.
- Leitor durante gravação obtém snapshot anterior ou novo, nunca JSON parcial.
- Falha de gravação preserva snapshot anterior.
- `show` não altera conteúdo, timestamps de escrita nem cria arquivos.
- Criar/atualizar ledger não adiciona alterações ao Git do projeto consumidor.
- `[?]` continua VALIDATE mesmo com 100%; `[x]` não é produzido pelo medidor.
- Prática em `workspace-write` do Codex funciona sem escrita fora da raiz autorizada.

### Fase 2

- Quatro `PostToolUse` elegíveis sem plano geram um lembrete; o quinto não repete.
- Registrar plano interrompe a condição de lembrete.
- PLANNING, gate, execução pausada e sessão não vinculada não geram cobrança indevida.
- Eventos duplicados com identificador estável não contam duas vezes.
- Payload inválido, lock ocupado, falta de Python, falta de permissão e JSON corrompido não bloqueiam o host.
- Hook nunca emite `deny`, `decision: block`, `continue: false` ou instrução de interromper Goal.
- Nenhum transcript é aberto.
- Segmento Claude escolhe a sessão vinculada; não escolhe “o ledger mais recente”.
- Sem vínculo, omite o segmento; com vínculo inválido, sinaliza indisponibilidade.
- Ausência do novo script preserva a barra anterior.
- Sem `jq`, preserva a degradação atual para board.
- Configuração Codex permanece intocada.
- Teste real após release confirma lembrete e retomada nos dois hosts.

### Fase 3

- Duas janelas/hosts atualizando ledgers distintos aparecem corretamente no leitor.
- Alteração aparece até o próximo intervalo de atualização.
- Leitor não escreve ledger, binding, board, thread, comentário ou configuração.
- Encerrar o leitor não encerra worker nem sessão.
- Não há servidor, upload, link público ou chamada de modelo.
- Browser e comentários não são necessários para o funcionamento.

### Fase 4

- Desabilitar o mod preserva CLI, ledger, statusline e execução.
- Mod usa a mesma projeção e não recalcula progresso.
- Não registra ferramenta concorrente `tasks`.
- `modules` aparece somente no pacote separado.
- Nenhuma instalação ou configuração Codex recebe o mod.
- Versão mínima e comportamento visual são comprovados no host autorizado.

**Para cada fase que modificar o plugin, os três gates são obrigatórios:**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
```

Todos devem sair `0`. A descoberta nunca será substituída por lista de módulos.

Aceite comportamental definitivo ocorre somente após release autorizado, fonte detached limpa do SHA remoto aprovado, update/restart e `verify_installed_cache.py` vindo dessa fonte para cada host. Validação local não substitui esse aceite.

## 5. Decisões que precisam do dono

1. **Escopo de encerramento do T-144.**  
   Recomendo fases 1–3: núcleo, lembrete, statusline Claude e leitor Orca. Mod separado e T-042 seguem independentes.

2. **Lugar do estado.**  
   Recomendo `.orq/progress/` ignorado na frente dona, aceitando que não será sincronizado entre máquinas nem sobreviverá à remoção da frente sem checkpoint.

3. **Semântica do percentual.**  
   Recomendo pesos S/M/L = 1/2/3, sempre apresentados como progresso dos passos do plano; aprovação e conclusão do objetivo permanecem separadas.

4. **ETA.**  
   Recomendo não entregar estimativa temporal nas fases 1–3.

5. **Vista inicial no Orca.**  
   Recomendo terminal local somente leitura. Browser, comentários automáticos e publicação de artefatos ficam fora.

6. **Compatibilidade do Codex a validar.**  
   Recomendo 0.156.1 como baseline pedido, usando caminho explícito; registrar separadamente qualquer resultado no 0.160.0 do PATH.

7. **Versão e publicação.**  
   O dono precisa atribuir a versão disponível, considerando os outros worktrees. Não escolho número. Aprovação deste plano não autoriza push, publicação, instalação ou atualização do Claude.

## 6. INSTRUÇÕES AO EXECUTOR

**Executor previsto: Anthropic Sonnet.** Este é um handoff de desenho; implementação só começa após aprovação do Manager/dono e atribuição da versão. Trabalhe em worktree dedicado. Você não está sozinho no repositório: preserve alterações de outras frentes e não reverta arquivos alheios.

### 6.1. Arquivos e responsabilidade

| Fase | Arquivo | Responsabilidade |
|---|---|---|
| 1 | `orq/scripts/progress.py` — novo | Schema validado, cálculo, armazenamento, CLI e projeções. |
| 1 | `orq/scripts/schemas/progress-ledger-v1.json` — novo | Contrato documental do ledger; sem dependência de biblioteca JSON Schema no runtime. |
| 1 | `orq/scripts/kanban-status.sh` | Nova consulta estruturada de um card, reutilizando seu parser. |
| 1 | `orq/scripts/test_progress.py` — novo | Cálculo, transições, persistência, concorrência e CLI. |
| 1 | `orq/scripts/test_kanban_status.py` | Cobrir novo modo sem mudar resultados dos modos atuais. |
| 1 | `orq/skills/orq/references/progress.md` — novo | Contrato único de operação do medidor. |
| 1 | `orq/skills/orq/SKILL.md` | Encaminhamento ao contrato, início de goal e retomada. |
| 1 | `orq/commands/plan-next.md` | Exigir tabela de passos verificáveis no plano. |
| 1 | `orq/commands/implement-next.md` | Registro e atualização pelo Manager nos marcos. |
| 1 | `orq/commands/checkpoint.md` | Registrar caminho, revisão e pendências na thread; sem copiar telemetria inteira. |
| 2 | `orq/scripts/progress-hook.py` — novo | Adaptador fino dos eventos para funções do núcleo. |
| 2 | `orq/hooks/hooks.json` | Acrescentar hooks independentes, preservando os atuais. |
| 2 | `orq/scripts/statusline.sh` | Consumir segmento fornecido pelo núcleo. |
| 2 | `orq/commands/init.md` | Instalação/backup/rollback do conjunto de três scripts. |
| 2 | `orq/scripts/test_progress_hooks.py` — novo | Contrato consultivo e isolamento de sessões. |
| 2 | `orq/scripts/test_progress_statusline.py` — novo | Seleção da sessão, cópia instalada e degradações. |
| 2 | `orq/skills/orq/references/hosts/codex.md` | Explicar convivência com o medidor, preservando o contrato restritivo. |
| 3 | `orq/scripts/progress.py` | Subcomando `watch`. |
| 3 | `orq/scripts/test_progress_watch.py` — novo | Leitura contínua, interrupção e ausência de escrita. |
| 3 | `orq/skills/orq/references/progress-orca.md` — novo | Procedimento de consumo local no Orca. |

Atualizar também a arquitetura, o schema de memória onde necessário, distribuição e documentação pública. O Manager registra andamento na thread T-144 e edita somente a linha correspondente do board.

Não alterar T-141, elenco, regras de autorização, lógica de `context-guard.py` ou configurações globais.

Em cada commit de release que alterar `orq/`, coordenar **os quatro lugares**:

- `orq/.claude-plugin/plugin.json`;
- Status do `README.md`;
- `memory/MEMORY.md`;
- `.claude-plugin/marketplace.json`.

### 6.2. Contrato do ledger

Formato completo mínimo, com valores ilustrativos:

```json
{
  "schema_version": 1,
  "run_id": "UUID",
  "revision": 1,
  "kind": "card",
  "scope": {
    "front_root": "/raiz/absoluta/da/frente",
    "front": "frente-mods",
    "card_id": "T-144",
    "board_path": "/board/canonico/KANBAN.md",
    "thread_root": "/raiz/absoluta/da/frente/memory/wiki"
  },
  "owner": {
    "host": "claude",
    "session_key": "HASH_HEX_64"
  },
  "lifecycle": "active",
  "activity": "implementation",
  "plan": {
    "source_ref": "docs/plano.md#passos",
    "approval_ref": "threads/T-144.md#aprovacao",
    "seed_sha256": "HASH_HEX_64",
    "baseline_count": 1,
    "baseline_weight": 2,
    "registered_at": "2026-10-04T13:00:00Z"
  },
  "tasks": [
    {
      "id": "P01",
      "title": "Validar retomada",
      "size": "M",
      "status": "pending",
      "acceptance_ref": "A01",
      "executor": null,
      "evidence_refs": [],
      "change_reason": null,
      "created_at": "2026-10-04T13:00:00Z",
      "started_at": null,
      "finished_at": null
    }
  ],
  "created_at": "2026-10-04T13:00:00Z",
  "updated_at": "2026-10-04T13:00:00Z"
}
```

Regras de validação:

- `kind`: `card | goal`.
- Goal: campos de card, board, thread e frente podem ser `null`; `front_root` continua obrigatório.
- `host`: `claude | codex | other`.
- `lifecycle`: `active | paused | closed`.
- Card, `activity`: `planning | gate | ready | implementation | review | docs | validate | done`.
- Goal, `activity`: `planning | execution | verification`.
- `plan` pode ser `null` antes do registro.
- `status`: `pending | active | done | dropped`.
- `executor`: `null` ou objeto com `host`, `role` e `label` genéricos; sem nomes pessoais.
- Timestamps UTC gerados pelo programa.
- IDs únicos, estáveis e limitados a letras ASCII, números, `_` e `-`.
- Até 200 tarefas; título de até 160 caracteres, sem controles de terminal.
- Referências são identificadores/caminhos locais, não conteúdo de evidência.
- Sem campo de prompt, condição integral do goal, notas livres, comandos, stdout, diff ou transcript.
- Leitura limitada a 1 MiB; versão desconhecida gera erro explícito.
- `seed_sha256` é SHA-256 do JSON canônico da semente original. Não é prova criptográfica de aprovação humana.
- Tarefas nunca são removidas fisicamente.

**Binding de sessão**, separado do ledger:

```json
{
  "schema_version": 1,
  "session_key": "HASH_HEX_64",
  "host": "claude",
  "ledger_path": "/caminho/absoluto/T-144.json",
  "run_id": "UUID",
  "calls_without_plan": 0,
  "nudged": false,
  "recent_event_ids": []
}
```

`session_key = sha256(host + "\0" + session_id)` quando o host disponibilizar o ID. Nunca persistir o ID bruto. Na fase 1, sem ID disponível, `begin` gera chave local e a retorna; o Manager deve preservá-la no contexto/handoff.

A fase 2 vincula a chave nativa por `bind`; esse comando não transfere ownership.

### 6.3. CLI exata

Prefixo de todas as chamadas:

```bash
python3 "${ORQ_PACKAGE_ROOT}/scripts/progress.py"
```

Subcomandos:

```text
begin --kind card --root ABS --board ABS --thread-root ABS
      --card T-NNN --front SLUG --host HOST [--session-key KEY]

begin --kind goal --root ABS --host HOST [--session-key KEY]

bind --ledger ABS --host HOST --session-key KEY

claim --ledger ABS --host HOST --session-key KEY
      --expected-owner KEY --expect-revision N

plan --ledger ABS --session-key KEY --expect-revision N --input -

add --ledger ABS --session-key KEY --expect-revision N --input -

start --ledger ABS --session-key KEY --expect-revision N
      --task ID --executor-host HOST --executor-role ROLE
      --executor-label LABEL

done --ledger ABS --session-key KEY --expect-revision N
     --task ID --evidence-ref REF

drop --ledger ABS --session-key KEY --expect-revision N
     --task ID --reason obsolete|duplicate|scope_change
     --evidence-ref REF

reopen --ledger ABS --session-key KEY --expect-revision N
       --task ID --evidence-ref REF

phase --ledger ABS --session-key KEY --expect-revision N --value PHASE

pause --ledger ABS --session-key KEY --expect-revision N

resume --ledger ABS --session-key KEY --expect-revision N

close --ledger ABS --session-key KEY --expect-revision N
      --outcome reported_complete|cancelled --evidence-ref REF

show --ledger ABS --format text|json|segment

show --root ABS --all --format text|json

statusline --host claude --input -

watch --ledger ABS --interval 2

watch --root ABS [--root ABS ...] --interval 2
```

`watch` pertence à fase 3; `statusline` à fase 2.

**Entrada de `plan`:**

```json
{
  "source_ref": "docs/plano.md#passos",
  "approval_ref": "threads/T-144.md#aprovacao",
  "tasks": [
    {
      "id": "P01",
      "title": "Validar retomada",
      "size": "M",
      "acceptance_ref": "A01"
    }
  ]
}
```

Goal permite `approval_ref: null`. Card exige referência e estado aprovado no board para registrar a semente de execução.

`add` recebe:

```json
{
  "reason": "scope_change",
  "evidence_ref": "threads/T-144.md#ajuste-aprovado",
  "tasks": [
    {
      "id": "P02",
      "title": "Cobrir retomada interrompida",
      "size": "S",
      "acceptance_ref": "A02"
    }
  ]
}
```

Saída de mutações: JSON com `ok`, `run_id`, `ledger_path`, `revision`, `session_key` e `changed`.

Códigos:

- `0`: sucesso ou repetição idempotente.
- `2`: argumentos/schema/transição inválidos.
- `3`: revisão ou ownership conflitante.
- `4`: persistência, lock, board ou estado indisponível.

Após conflito, reler; nunca repetir cegamente nem sobrescrever.

**Exceção dos adaptadores consultivos:** `progress-hook.py` e `statusline` sempre saem `0`. Falha do medidor não pode bloquear trabalho do host. Isso não transforma falha de gravação em sucesso: o Manager deve informar a indisponibilidade.

### 6.4. Transições e cálculo

- `start`: `pending → active`.
- `done`: `active → done`, com evidência.
- `drop`: `pending|active → dropped`, com motivo e referência.
- `reopen`: `done → pending`, preservando referências anteriores.
- Tarefa descartada não é reutilizada; acrescentar nova tarefa com novo ID.
- Repetição exata de operação já aplicada: sem mudança.
- Mesmo ID com conteúdo incompatível: erro.
- `plan` só inicializa; repetição com mesma semente é idempotente.
- Alterações posteriores usam `add`, `drop` ou `reopen`.

Cálculo:

```text
ativas_no_plano = tarefas cujo status != dropped
total = soma dos pesos dessas tarefas
feito = soma dos pesos das tarefas done
percentual = arredondamento inteiro de 100 × feito / total
```

Se `total = 0`, percentual `null`. Se ainda houver tarefa não concluída, limitar a exibição a 99%; 100% exige todas as tarefas consideradas concluídas.

A fase exibida obedece ao board:

| Marcador | Fase |
|---|---|
| `[ ]` | backlog |
| `[>]` | planning; `gate` somente como indicação consultiva do Manager |
| `[!]` | gate |
| `[~]` | ready/implementation/review/docs, conforme atividade válida |
| `[?]` | validate |
| `[x]` | done |

Atividade incompatível não vence o board. Board ilegível, ausente ou ambíguo resulta em fase indisponível; percentual pode ser mostrado separado, com aviso. Nenhuma função do medidor move card.

`close --outcome reported_complete` em card exige `[x]`. Em goal, registra somente conclusão declarada pelo Manager; não altera o modo Goal nativo.

### 6.5. Consulta do board

Acrescentar:

```bash
sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" \
  --card-state T-144 --board-path "$BOARD_CANONICO"
```

Saída:

```json
{"state":"ok","card":"T-144","marker":"~"}
```

Erro:

```json
{"state":"erro","code":"card-ausente"}
```

Reutilizar a passagem existente que reconhece fences e arquivo histórico. Não duplicar uma terceira versão dessas regras em `progress.py`.

O modo novo deve:

- exigir board absoluto e ID válido;
- rejeitar ID duplicado;
- distinguir ausência de erro de leitura;
- preservar integralmente os modos existentes.

### 6.6. Assinaturas internas

Implementar funções testáveis, sem efeitos implícitos:

```python
validate_ledger(raw: object) -> dict
calculate_progress(ledger: dict) -> dict
project_phase(ledger: dict, board_state: dict | None) -> dict
apply_operation(ledger: dict, operation: dict, now: str) -> dict
read_ledger(path: Path) -> dict
mutate_ledger(
    path: Path,
    session_key: str,
    expected_revision: int,
    operation: dict,
    now: str,
) -> dict
render_text(view: dict) -> str
render_segment(view: dict) -> str
handle_hook(event: dict, env: Mapping[str, str]) -> dict | None
main(argv: list[str] | None = None) -> int
```

`apply_operation` trabalha sobre cópia e não acessa disco. `mutate_ledger` detém lock durante leitura, validação, comparação e gravação.

`show`, `statusline` e `watch` compartilham a mesma projeção; não recalculam regras em três lugares.

### 6.7. Integração dos procedimentos

**Planner:**

- Produz tabela de passos e critérios.
- Não escreve o ledger durante papel read-only.

**Manager, ao iniciar Loop B:**

1. Comprova pacote, board e frente.
2. Confirma plano aprovado.
3. Executa `begin`.
4. Registra a semente com `plan`.
5. Passa ledger e IDs relevantes ao implementer.
6. Marca início antes do despacho.
7. Confere resultado/evidência e marca conclusão.
8. Atualiza atividade nas transições de implementação, revisão e docs.
9. Apresenta resumo nos marcos e quando solicitado.
10. Em VALIDATE, mostra a fase correta e pausa a execução.
11. No checkpoint, registra caminho, revisão e pendências na thread.

Workers não recebem permissão adicional para escrever no ledger do Manager.

**Goal avulso:** mesma sequência, com plano derivado do objetivo autorizado e sem operações de board.

### 6.8. Hooks e seleção de sessão

- `SessionStart` fornece chave opaca e instrução curta; não cria goal nem interpreta prompt.
- `PostToolUse` considera somente binding existente e execução ativa.
- Para card, lembrete somente quando o board já admite execução.
- Não abrir `transcript_path`, `tool_input`, `tool_response` ou texto de prompt.
- Usar identificador do evento para deduplicação quando disponível; manter no máximo 128 IDs.
- Sem identificador, documentar que a contagem é por entrega de evento; não alegar exatamente quatro chamadas únicas.
- Payload de host desconhecido: não agir.
- Lock indisponível ou persistência falha: sair sem bloqueio.
- Criar entradas separadas no `hooks.json`; não alterar matchers nem respostas do context-guard.

A statusline usa o `session_id` do payload para procurar o binding. Sem identificação suficiente, não escolhe por horário ou proximidade de título.

### 6.9. Testes obrigatórios

Escrever testes comportamentais para:

1. Pesos, arredondamento, plano vazio, todos descartados e tarefas paralelas.
2. Idempotência e rejeição de IDs conflitantes.
3. Queda do percentual após expansão/reabertura.
4. Evidência obrigatória para conclusão.
5. Dois processos disputando a mesma revisão.
6. Leitura concorrente com gravação e falha antes de `replace`.
7. Transferência de ownership: escritor antigo perde autorização.
8. Dois hosts, sessões e cards sem contaminação cruzada.
9. Caminhos com espaço, Unicode e caracteres que não podem virar código shell.
10. Estado inválido, versão desconhecida e arquivos acima do limite.
11. `show`/`watch` sem qualquer escrita.
12. Diretório efetivamente ignorado e recusa de destino versionado.
13. Board canônico diferente do worktree; fences, arquivo histórico e ID duplicado.
14. Lembrete único, deduplicação e ausência de lembrete durante planejamento/gate.
15. Falhas dos hooks sempre consultivas.
16. Statusline sem binding, sem `jq`, sem script vizinho e com cópia instalada fora do cache.
17. Coexistência com todos os hooks do context-guard.
18. Preservação do contrato de `test_codex_statusline_contract.py`.
19. Nenhum acesso a transcript e nenhuma gravação de conteúdo de ferramenta.
20. Interrupção do `watch` sem afetar a execução observada.

### 6.10. Sequência fechada e rollback

1. Registrar baseline e preservar alterações preexistentes.
2. Implementar fase 1; executar testes focados e os três gates.
3. Obter revisão independente e corrigir achados demonstráveis.
4. Documentar somente o comportamento final.
5. Entregar fase para validação; não instalar nem publicar sem autorização.
6. Repetir o ciclo para fases 2 e 3.
7. Após release autorizado, executar verificação de cache da fonte limpa e validação prática nos hosts.

Rollback:

- Núcleo: interromper uso; manter ledgers intactos.
- Hook: remover somente entradas do medidor em release autorizado; preservar context-guard.
- Statusline: restaurar backup exato da configuração e do conjunto anterior, respeitando T-093.
- Orca: encerrar apenas o terminal leitor.
- Mod futuro: desabilitar somente o pacote separado.

Nenhum rollback apaga progresso, reescreve o board, fecha sessões reais ou remove caches utilizados por trabalho em andamento.

