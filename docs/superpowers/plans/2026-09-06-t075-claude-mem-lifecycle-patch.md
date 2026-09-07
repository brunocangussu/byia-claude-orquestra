# T-075 — Claude Mem lifecycle and pool patch implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this
> plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** corrigir o `claude-mem` para que uma conversa com vários turnos persista cada evento na
sessão correta e para que o pool do Claude SDK libere o slot depois do resumo de cada turno, sem
perder mensagens já aceitas.

**Architecture:** manter o buffer em RAM durante o processamento, correlacionar cada resposta do SDK
com exatamente uma mensagem por uma FIFO de dispatch, encerrar o subprocesso somente depois do
resultado do resumo e reativar no SQLite qualquer sessão `completed` que receba um evento válido
posterior. `SessionEnd` não é requisito de correção porque o manifesto Codex não o oferece e o
`Stop` é fronteira de turno, não de sessão.

**Tech Stack:** TypeScript, Bun, SQLite, Claude Agent SDK, claude-mem 13.24.1.

**Spec:** `memory/wiki/threads/T-072-claude-mem.md`.

## Restrições globais

- O escopo deste documento é o fork local controlado do `claude-mem`. Não alterar o AI-Memory.
- Nunca ler nem imprimir conteúdo de prompt, observação, resumo ou fila; usar somente IDs, tipos,
  contagens, timestamps, status, projeto e plataforma.
- Preservar `CLAUDE_MEM_EXCLUDED_PROJECTS="*Bruno Vascular*"`; nenhum canário abre arquivos desse
  projeto. A validação clínica se limita a provar o estado `EXCLUÍDO` com metadados.
- Não editar bundles minificados nem caches instalados. Implementar em checkout isolado e gerar os
  artefatos pelo build oficial.
- Preservar o checkout do marketplace em
  `/Users/brunocangucu/.codex/.tmp/marketplaces/claude-mem-local`, inclusive o arquivo não rastreado
  `.codex-marketplace-install.json`.
- Não reiniciar o worker enquanto houver mensagem pendente somente em RAM. Antes de qualquer
  restart, capturar um snapshot metadata-only e provar drenagem ou aceitar explicitamente a perda
  do canário — nunca de dados reais.
- Instalação, restart, commit, push, publicação e comunicação com o upstream exigem gates separados.

## Evidência que orienta o desenho

- O canário Codex `session_db_id=571` persistiu 1 prompt, 1 observação e 2 resumos: a fiação do host
  está funcional.
- O canário Claude `session_db_id=574` recebeu o segundo prompt depois de já estar `completed`; a
  observação e o resumo seguintes ficaram somente no buffer em RAM.
- O gerador atual pode ocupar um slot por até três minutos de inatividade depois de `Stop`. Com três
  subprocessos legítimos, a quarta sessão espera no pool.
- O SDK pode pedir mais de uma mensagem antes de responder. Portanto, retornar ou abortar logo após
  `yield summarize` e confirmar todas as mensagens reclamadas são operações inseguras.
- Os seis arquivos de lifecycle comparados são byte a byte iguais entre o checkout 13.24.1
  (`b6e05382`) e o `main` oficial inspecionado (`3939fbb2`); não há correção pronta para transplantar.

---

## Tarefa 1 — criar a área isolada e congelar o baseline

**Arquivos:** nenhum arquivo instalado; somente um novo worktree/branch do repositório fonte.

- [ ] Confirmar que o checkout fonte continua no commit `b6e05382e2be35e29f22335f04a6890a4c0ba976`
  e que a única diferença conhecida é `.codex-marketplace-install.json` não rastreado.
- [ ] Criar um worktree isolado na branch `codex/t075-claude-mem-lifecycle` a partir desse commit.
- [ ] Registrar, sem conteúdo, PID/versão do worker, limite do pool, contagem de mensagens pendentes,
  maior ID de cada tabela e hashes dos caches Claude/Codex.
- [ ] Rodar o baseline no worktree: `bun test tests`, `npm run typecheck`,
  `npm run lint:hook-io` e `npm run lint:spawn-env`.
- [ ] Se qualquer gate já falhar no baseline, parar e separar falha preexistente de regressão antes
  de editar código.

## Tarefa 2 — escrever os testes de reativação do SQLite

**Arquivos:**

- Modificar: `tests/services/sqlite/session-store-mark-completed.test.ts`
- Criar: `tests/worker/session-lifecycle-reactivation.test.ts`

- [ ] Adicionar teste que cria uma sessão, marca como `completed`, chama a futura reativação e exige
  `status='active'`, `completed_at=NULL` e `completed_at_epoch=NULL`.
- [ ] Cobrir idempotência em sessão já ativa e provar que outra sessão não muda.
- [ ] Cobrir `UserPromptSubmit` válido em uma sessão completada: o mesmo row deve ser reativado antes
  de inicializar a sessão em memória.
- [ ] Cobrir prompt privado e prompt duplicado: nenhum deles pode reativar a sessão.
- [ ] Cobrir observação e resumo válidos recebidos após conclusão: ambos reativam antes de entrar na
  fila.
- [ ] Rodar apenas esses testes e confirmar que falham pela ausência do comportamento, não por erro
  de fixture.

## Tarefa 3 — implementar reativação idempotente por evento aceito

**Arquivos:**

- Modificar: `src/services/sqlite/SessionStore.ts`
- Modificar: `src/services/worker/http/routes/SessionRoutes.ts`
- Modificar: `src/services/worker/http/shared.ts` somente se o ponto comum de admissão reduzir
  duplicação sem antecipar a reativação às checagens de privacidade/exclusão

- [ ] Adicionar `SessionStore.markSessionActive(sessionDbId)` com update parametrizado de status e
  limpeza dos dois timestamps de conclusão.
- [ ] No fluxo de prompt, chamar a reativação somente depois de exclusão/privacidade e deduplicação,
  mas antes de `initializeSession`.
- [ ] Nos fluxos de observação e resumo, chamar a reativação somente depois das mesmas barreiras e
  antes de enfileirar.
- [ ] Não criar sessão nova quando a linha existente é válida: preservar o vínculo técnico da
  conversa.
- [ ] Rodar os testes da Tarefa 2 até ficarem verdes.

## Tarefa 4 — escrever os testes de confirmação individual e prefetch

**Arquivos:**

- Modificar: `tests/services/worker/session-message-buffer.test.ts`
- Criar: `tests/worker/claude-provider-turn-boundary.test.ts`

- [ ] Montar o cenário mínimo em que o SDK pede uma observação e um resumo antes de devolver a
  primeira resposta.
- [ ] Exigir que a resposta da observação confirme somente o ID da observação; o resumo permanece
  reclamado/pendente até a própria resposta.
- [ ] Exigir que resposta de `init` não confirme nenhuma mensagem persistente.
- [ ] Cobrir XML válido e prosa descartável: ambos podem resolver apenas o ID correlacionado; erro de
  quota/autenticação continua devolvendo todo o lote reclamado ao estado pendente.
- [ ] Rodar os testes novos e confirmar a falha esperada no comportamento atual de “confirmar tudo”.

## Tarefa 5 — implementar FIFO de dispatch e ACK por mensagem

**Arquivos:**

- Modificar: `src/services/worker/SessionManager.ts`
- Modificar: `src/services/worker/SessionMessageBuffer.ts` se for necessário expor confirmação por ID
- Modificar: `src/services/worker/ClaudeProvider.ts`
- Modificar: `src/services/worker/agents/ResponseProcessor.ts`

- [ ] Adicionar `confirmClaimedMessage(sessionDbId, messageId)` sem remover o reset do lote inteiro
  usado em abort, quota e autenticação.
- [ ] Criar no provider uma FIFO de dispatch com `{messageId, messageType, responseContext}`; o item
  `init` usa `messageId=null`.
- [ ] Enfileirar o descritor no mesmo instante lógico em que cada mensagem é entregue ao SDK.
- [ ] A cada resposta `assistant`, retirar exatamente um descritor e passar seu contexto e ID ao
  `ResponseProcessor`.
- [ ] Alterar os caminhos de sucesso e descarte inofensivo para confirmar somente o ID recebido.
- [ ] Manter todos os IDs recuperáveis nos caminhos de quota, autenticação, abort inesperado e erro
  antes de persistência.
- [ ] Adicionar uma asserção/erro estruturado para resposta sem descritor, sem expor conteúdo.
- [ ] Rodar os testes das Tarefas 2 e 4.

## Tarefa 6 — escrever os testes da fronteira de turno e retomada

**Arquivos:**

- Ampliar: `tests/worker/claude-provider-turn-boundary.test.ts`
- Modificar: `tests/worker/poison-respawn.test.ts`
- Modificar: `tests/supervisor/wait-for-slot.test.ts`

- [ ] Provar que `yield summarize` sozinho não encerra o gerador.
- [ ] Provar que a fronteira só é atingida depois da resposta e do `result` correspondentes ao
  resumo, com persistência/ACK concluídos.
- [ ] Provar que a fronteira usa abort/terminação real do subprocesso, não apenas retorno do iterador.
- [ ] Sem prompt novo e sem buffer restante: a saída finaliza e remove a sessão em memória como hoje.
- [ ] Com prompt mais novo ou mensagem restante: a saída preserva a `ActiveSession`, o buffer e
  agenda novo gerador sem duplicar mensagens.
- [ ] Cobrir corrida: novo prompt chega enquanto o resumo anterior está sendo processado.
- [ ] Cobrir regressão dos motivos existentes `quota`, `auth`, `overflow`, `idle` e erro inesperado.
- [ ] Com limite 3, provar que a quarta sessão é admitida assim que um resumo libera o slot, sem
  ultrapassar três reservas simultâneas.
- [ ] Rodar os testes e confirmar que o código atual falha somente nos novos contratos.

## Tarefa 7 — implementar liberação pós-resumo e retomada segura

**Arquivos:**

- Modificar: `src/services/worker/ClaudeProvider.ts`
- Modificar: `src/services/worker/session/GeneratorExitHandler.ts`
- Modificar: `src/services/worker/http/routes/SessionRoutes.ts`
- Modificar: `src/services/worker/SessionManager.ts` se for necessário consultar trabalho restante

- [ ] Capturar `runPromptNumber` ao iniciar cada gerador.
- [ ] Depois do `result` do resumo correlacionado, definir um motivo interno não-falho
  (`turn-complete`), abortar o controller para terminar o SDK e sair do loop.
- [ ] Não classificar `turn-complete` como falha operacional nem contaminar telemetria de abort.
- [ ] Fazer `handleGeneratorExit` devolver resultado explícito (`preserved` ou `finalized`).
- [ ] Para `turn-complete`, preservar quando `lastPromptNumber > runPromptNumber` ou houver mensagem
  no buffer; sem trabalho novo, finalizar/remover.
- [ ] Quando preservado, agendar `ensureGeneratorRunning(..., 'turn-continuation')` fora da pilha de
  cleanup para adquirir um novo slot sem recursão nem dupla reserva.
- [ ] Garantir que `finally` sempre libere a reserva e execute `ensureSdkProcessExit` quando preciso.
- [ ] Não alterar providers Gemini/OpenRouter nesta primeira correção, salvo se o contrato comum e
  os testes demonstrarem equivalência.
- [ ] Rodar toda a matriz das Tarefas 2, 4 e 6.

## Tarefa 8 — gates automatizados no código-fonte final

**Arquivos:** todos os alterados nas tarefas anteriores e artefatos gerados oficialmente.

- [ ] Rodar os testes direcionados:
  `bun test tests/services/sqlite/session-store-mark-completed.test.ts tests/worker/session-lifecycle-reactivation.test.ts tests/services/worker/session-message-buffer.test.ts tests/worker/claude-provider-turn-boundary.test.ts tests/worker/poison-respawn.test.ts tests/supervisor/wait-for-slot.test.ts`.
- [ ] Rodar `bun test tests`.
- [ ] Rodar `npm run typecheck`.
- [ ] Rodar `npm run lint:hook-io` e `npm run lint:spawn-env`.
- [ ] Rodar `npm run build` somente pelo script oficial.
- [ ] Como o build altera artefatos, repetir `bun test tests`, `npm run typecheck`,
  `npm run lint:hook-io` e `npm run lint:spawn-env` no tree final.
- [ ] Revisar o diff para confirmar ausência de conteúdo sensível, configuração global, banco,
  cache instalado e mudanças fora do lifecycle.
- [ ] Parar no gate do dono com os resultados e o rollback detalhado. Não instalar nem reiniciar.

## Tarefa 9 — gate obrigatório antes da instalação local

- [x] Obter aprovação literal do dono para instalar o build nos dois hosts e reiniciar o worker.
- [x] Verificar metadata-only se a fila em RAM drenou. Se não drenou, aguardar; não forçar restart.
- [x] Criar backups datados das configurações e dos caches que serão substituídos e provar que os
  backups existem e correspondem aos alvos.
- [x] Registrar os hashes anteriores para rollback.

## Tarefa 10 — instalar o mesmo build em Claude e Codex

- [x] Instalar pelo mecanismo local suportado do marketplace, nunca copiando um bundle isolado.
- [ ] Reiniciar uma única vez, de modo controlado, depois da prova de drenagem.
- [ ] Conferir PID/versão e igualdade de hashes do build nos caches Claude e Codex. A igualdade de
  hashes já foi provada; PID novo aguarda o restart bloqueado pela fila RAM crescente.
- [ ] Health confirma apenas liveness; não declarar sucesso sem os canários seguintes.

## Tarefa 11 — canários funcionais e de concorrência

- [ ] Em projeto não clínico do Claude, executar dois turnos na mesma sessão, cada um com uma leitura
  relevante, e medir apenas metadados.
- [ ] Repetir o mesmo canário no Codex.
- [ ] Exigir por sessão: prompts, observações e resumos novos; nenhum evento posterior ao timestamp
  de conclusão; nenhuma mensagem aceita perdida; status ativo enquanto há trabalho ou conclusão sem
  evento posterior.
- [ ] Abrir quatro sessões não clínicas com limite 3 e provar que a quarta começa dentro do SLO logo
  após um dos três resumos liberar o slot.
- [ ] No projeto Bruno Vascular, não abrir arquivo nem enviar conteúdo: apenas confirmar que a regra
  continua classificando como `EXCLUÍDO` e não cria linha no banco.
- [ ] Rodar o detector `orq/scripts/claude_mem_status.py` e anexar somente sua saída metadata-only à
  thread T-075.
- [ ] Se qualquer host falhar, executar rollback; não compensar com aumento adicional de pool.

## Tarefa 12 — rollback verificável

- [ ] Parar o worker corrigido somente depois de verificar novamente a fila em RAM.
- [ ] Restaurar os backups exatos da versão 13.24.1 anterior em ambos os caches e as configurações
  correspondentes.
- [ ] Reiniciar o worker original e conferir PID/versão/hash.
- [ ] Rodar um canário metadata-only não clínico para provar que o rollback restaurou o baseline.
- [ ] Preservar o branch/worktree do patch para diagnóstico; não apagar evidência.

## Tarefa 13 — fechamento e eventual contribuição upstream

- [ ] Registrar na thread os resultados automatizados, os dois canários, o teste de concorrência e
  o resultado de rollback ou permanência.
- [ ] Somente após validação autenticada do dono, mover `T-075` para `DONE`.
- [ ] Commit local, push, issue ou PR upstream continuam ações independentes; pedir autorização
  específica e remover qualquer dado/caminho identificável antes de comunicação externa.

## Critérios de aceite

1. Claude e Codex persistem os dois turnos do canário na mesma sessão com prompt, observação e
   resumo, sem `event_after_session_completion`.
2. Uma resposta do SDK confirma somente a mensagem à qual corresponde, mesmo com prefetch.
3. O subprocesso libera o slot depois do resumo e a quarta sessão entra sem oversubscription.
4. Evento válido posterior reativa atomicamente a sessão; evento privado, excluído ou duplicado não.
5. Nenhuma fila RAM é descartada durante instalação ou rollback.
6. `*Bruno Vascular*` permanece excluído e nenhum conteúdo sensível é lido ou enviado.
7. Suíte completa, typecheck, dois lints e rebuild final passam no tree que será instalado.

## Estado após implementação e revisão local — 2026-09-06

- [x] As tarefas de código e testes foram implementadas no worktree isolado
  `/private/tmp/claude-mem-t075-lifecycle`, branch `codex/t075-claude-mem-lifecycle`.
- [x] A correlação final usa UUIDs por dispatch e o `result` do SDK como fronteira; frames
  `assistant` são agregados e não confirmam o FIFO antecipadamente.
- [x] Resultado sem sucesso ou correlação declarada desconhecida devolve as mensagens à fila e
  preserva motivo neutro de pausa; `turn-complete` não sobrescreve erro/abort anterior.
- [x] A reativação ocorre somente depois de uma observação inédita entrar na fila; duplicata,
  exclusão e erro de enqueue não reativam sessão concluída.
- [x] A finalização preserva ou reativa a sessão se chegar trabalho durante a corrida de idle/finalize
  e respeita shutdown explícito.
- [x] Revisão externa delimitada foi executada em dois ciclos com Anthropic Fable 5.1. Os achados
  reproduzíveis foram corrigidos; o segundo ciclo não revisou as correções finais, conforme o limite
  de duas rodadas previsto pelo processo.
- [x] Validação final do Manager, depois do rebuild: matriz dirigida `67 pass / 0 fail`; suíte
  completa `3010 pass / 27 skip / 0 fail`; typecheck, `lint:hook-io`, `lint:spawn-env`, build e
  `git diff --check` com exit 0.
- [ ] As tarefas 9–13 continuam bloqueadas no gate do dono: nenhuma instalação, troca de cache,
  alteração de configuração/banco, reinício, commit, push ou publicação foi realizada.
