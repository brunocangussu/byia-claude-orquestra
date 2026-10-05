# Host Codex

## Superfície suportada

Este contrato cobre a **TUI do Codex CLI**. Ele não configura, não diagnostica nem promete uma
statusline no **Codex Desktop**. No host Codex, o Orquestra continua sendo usado por linguagem
natural ou `/skills`; os comandos `/orq:*` pertencem ao Claude Code.

## Statusline nativa

A statusline é uma lista ordenada na chave `[tui].status_line` de
`$CODEX_HOME/config.toml`. Antes de classificar a capacidade, resolva o `CODEX_HOME` efetivo do
processo; não presuma `~/.codex` quando o host usa outra raiz.

O diagnóstico somente leitura pode processar o TOML localmente para verificar sintaxe, presença e
tipo da chave; não exibe nem persiste valores da configuração e não altera o arquivo. Ele pode
informar somente caminho efetivo, validade sintática, presença/ausência da chave e tipo estrutural.
Se o `CODEX_HOME` efetivo não puder ser resolvido, informe `INDETERMINADO` e pare sem abrir arquivos.
No Codex Desktop, informe `NÃO APLICÁVEL`; os estados abaixo são exclusivos da TUI:

- **NÃO SUPORTADA:** a versão instalada não expõe a capacidade nativa.
- **AUSENTE:** `config.toml` não existe ou o TOML válido não define `tui.status_line`; não crie o arquivo.
- **JÁ CONFIGURADA:** a chave existe; relate apenas esse estado e preserve integralmente o arquivo.
- **INVÁLIDA:** o TOML não parseia; pare no diagnóstico e não proponha mudança.

`task-progress` descreve a tarefa ou o plano da sessão Codex; **não é o board do Orquestra**. A
statusline nativa não executa scripts do plugin, não aceita shell arbitrário e não recebe conteúdo
de `KANBAN.md` ou `kanban-status.sh`.

## Identificadores e limites de prova

Os identificadores aceitos dependem da versão instalada. Descubra-os no seletor `/statusline` da
TUI quando o próprio dono estiver realizando uma alteração autorizada. Se esse seletor não puder ser
consultado, a enumeração é indisponível para automação: não grave um **ID presumido** e preserve o
estado existente.

Um parse por `tomllib` prova somente sintaxe. `codex doctor --json` pode relatar saúde geral do host,
mas não prova que um identificador será aceito ou renderizado pela barra. A prova comportamental de
uma alteração futura exige uma **nova TUI** aberta pelo dono e está fora deste contrato.

## Medidor de progresso

O medidor de progresso (`references/progress.md`) convive com este contrato sem alterá-lo: não grava
`tui.status_line` e não espelha o ledger em `task-progress`. No Codex ele registra dois hooks
consultivos próprios (`SessionStart` e `PostToolUse`), ao lado do guardião de contexto. Eles só
acrescentam contexto, saem `0` mesmo quando falham e nunca bloqueiam, negam nem interrompem o Goal; o
Codex se identifica a eles por `PLUGIN_ROOT`.

O plano nativo (`update_plan`, que alimenta o item `task-progress`) **não é espelhado**: o ledger do
medidor não escreve nele e não o lê, são duas fontes sem sincronização, e o percentual do plano do
Orquestra não aparece na statusline nativa. A decisão de um espelho opt-in (vista unidirecional e
descartável do ledger no plano nativo) é do dono e fica para a fase 3 do medidor, no card T-147. A
consulta `get_goal`, quando existe, só informa se há um Goal nativo ativo (ver `progress.md`, "Goal
avulso"); não cria nem encerra nada.

## Mudanças futuras

Instalar ou inicializar o Orquestra não autoriza alterar a statusline. Este contrato não fornece
escritor de TOML, backup, merge, rollback nem automação de configuração. Caso alguém peça modificar
`tui.status_line`, abra um card independente de alto risco, obtenha decisão explícita e valide a
mudança visualmente na nova TUI.
