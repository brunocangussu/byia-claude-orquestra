# T-075 — claude-mem confiável no Claude Code e no Codex

> **Estado:** PLANNING — aguarda aprovação explícita do dono. Nada deste plano autoriza, por si,
> atualização, restart, edição de configuração, patch, commit, release ou push.

## Objetivo

Restabelecer a captura confiável do `claude-mem` nos dois hosts e provar o resultado pelo banco,
por sessão e por projeto — não pelo health do worker nem pela presença do plugin. Adicionar ao
Orquestra uma detecção fail-closed de memória atrasada ou parada, preservando o AI-Memory 2.0 sem
qualquer alteração.

## Diagnóstico fechado em 2026-09-05

1. O Codex está com `claude-mem@claude-mem-local` `13.24.0`, mas o bundle instalado identifica os
   próprios bytes como `13.23.1`.
2. O log local mostra o ciclo literal: mismatch de versão → worker morto por `SIGKILL` → o mesmo
   bundle obsoleto sobe novamente. O observer também perde eventos com
   `memory_session_id` nulo.
3. O upstream publicou `13.24.1` especificamente porque `13.24.0` atualizou manifestos sem
   recompilar os bundles. O cache do Claude Code já contém `13.24.1`; o do Codex continua em
   `13.24.0`.
4. Depois de o worker `13.24.1` assumir, o loop de mismatch/SIGKILL deixou de aparecer e novas
   observações voltaram a ser gravadas. Isso é evidência de recuperação parcial, não aceite final.
5. Claude e Codex ainda exibem sessões marcadas `completed` antes do último prompt/observação. Há
   também respostas não XML descartadas e fila acumulada. Portanto o Claude está capturando, mas
   não pode ser chamado de plenamente saudável.

## Limites obrigatórios

- Não ler, copiar, registrar em relatório nem usar em canário o conteúdo de prompts, observações,
  resumos ou filas. Diagnóstico consulta apenas IDs técnicos, plataforma, projeto, status,
  contagens e timestamps.
- O observer atual usa Claude/Anthropic. Logo, projeto clínico deve ficar excluído por padrão;
  `CLAUDE_MEM_EXCLUDED_PROJECTS=*Bruno Vascular*` é o mínimo fail-closed enquanto não houver
  provider realmente local ou outra base legítima definida pelo dono.
- Não tocar no daemon, banco, hooks ou configuração do AI-Memory 2.0.
- Não editar `~/.codex/hooks.json`; o arquivo é gerenciado pelo Terminals.
- Não usar `--dangerously-bypass-hook-trust` nem escrever `trusted_hash` manualmente.
- Antes de qualquer edição global, criar backup datado e conferir que o backup existe.
- Não limpar, migrar, compactar ou reescrever o banco do `claude-mem` para “fazer o teste passar”.
- Não aumentar concorrência antes de provar em qual estágio os eventos somem.

## Critério operacional

Cada canário usa duas interações na mesma sessão: prompt inofensivo → uma ferramenta somente de
leitura → `Stop`; depois novo prompt inofensivo → ferramenta somente de leitura → `Stop`.

Para cada sessão/projeto, a medição usa um watermark anterior ao canário e classifica:

- `CAPTURANDO`: prompt e observação novos aparecem associados à sessão correta; o resumo avança
  após `Stop`; não há erro estrutural novo.
- `ATRASADO`: o prompt entrou, o job está admitido e ainda está dentro do SLO de 15 minutos.
- `PARADO`: o prompt entrou e não há observação dentro de 15 minutos, ou surgiu mismatch,
  `SIGKILL`, erro `memory_session_id`/`NOT NULL` ou perda comprovada do job.
- `OCIOSO`: não houve trabalho posterior ao watermark; não autoriza concluir sucesso nem falha.
- `INDETERMINADO`: não é possível relacionar host, projeto e sessão sem ler conteúdo; falha o
  aceite e exige diagnóstico adicional.
- `EXCLUÍDO`: o projeto casa com a regra de exclusão e um canário totalmente sintético/inofensivo
  não cria prompt, observação nem resumo no banco.

Uma sessão que vira `completed` antes da segunda interação falha o aceite, mesmo que observações
continuem aparecendo depois: isso comprova captura intermitente, não lifecycle íntegro.

## Plano de execução

### Fase 1 — baseline, privacidade e rollback

- [x] Capturar, sem conteúdo, versões, caminhos e hashes de:
  - manifesto e bundle do cache Claude;
  - manifesto e bundle do cache Codex;
  - marketplace `claude-mem-local`;
  - worker ativo e porta;
  - `~/.claude-mem/settings.json`.
- [x] Registrar watermarks de `sdk_sessions`, `user_prompts`, `observations` e
  `session_summaries`, agrupados por `platform_source` e projeto.
- [x] Criar backup datado de `~/.claude-mem/settings.json`.
- [x] Aplicar a exclusão `*Bruno Vascular*` e validar o JSON/configuração sem exibir outros valores.
- [x] Provar o glob contra um canário sintético no caminho real; nenhuma string real de
  paciente entra no teste.
- [x] Registrar rollback: restaurar somente o backup datado da configuração e voltar ao pacote
  anterior pelo mecanismo oficial; o banco permanece intacto.

### Fase 2 — substituir o pacote quebrado do Codex pelo upstream corrigido

- [x] Executar `codex plugin marketplace upgrade claude-mem-local` — terminou sem mover o snapshot;
  foi necessário fast-forward limpo e verificável até o commit oficial `b6e05382`.
- [x] Conferir que a fonte do marketplace anuncia `13.24.1` e que o bundle foi realmente
  recompilado para `13.24.1`; versão do manifesto sozinha não basta.
- [x] Atualizar/reinstalar `claude-mem@claude-mem-local` pelo comando suportado do Codex. Se a
  atualização não trocar o cache, usar `remove` + `add` somente após confirmar que a configuração
  durável continua em `~/.claude-mem/settings.json` e que o rollback está disponível.
- [ ] Abrir uma sessão nova do Codex e deixar o dono aprovar os hooks no gate nativo, se ele surgir.
- [x] Confirmar alinhamento entre versão do plugin, versão do bundle e worker ativo. Health serve
  apenas como liveness auxiliar.
- [x] Marcar um novo watermark `t0`; não houve novo mismatch/SIGKILL estruturado na janela medida.

### Fase 3 — canários funcionais nos dois hosts

- [ ] Claude Code: executar o canário de duas interações em um projeto não clínico e conferir
  prompt, observação, resumo e lifecycle no banco.
- [ ] Codex: repetir o canário, em sessão nova, para cada projeto local salvo e não clínico:
  - `byia-orquestra`;
  - `MVP - New ByIA - Bruno`;
  - `bruno-brain`;
  - `Byia - Core - Bruno` / `New ByIA Project`.
- [x] No projeto Bruno Vascular, executar apenas um canário sintético inofensivo para provar o
  estado `EXCLUÍDO`; não abrir nem usar arquivos, prompts ou dados clínicos.
- [x] Após cada canário, consultar o banco em modo read-only e registrar somente IDs técnicos,
  contagens, status e timestamps.
- [ ] Conferir, desde `t0`, ausência de:
  - mismatch de versão e `SIGKILL` do worker;
  - `NOT NULL`/`memory_session_id`;
  - sessão encerrada antes do último evento;
  - fila que não retorna em direção ao baseline após o SLO.
- [x] Não declarar “todos os projetos funcionam” se algum projeto ficar `OCIOSO`, `ATRASADO` ou
  `INDETERMINADO`.

### Fase 4 — diagnóstico residual condicionado ao resultado da 13.24.1

Executar apenas se a Fase 3 falhar.

- [ ] Localizar o primeiro estágio ausente: hook emitido → hook recebido → job admitido → provider
  respondeu → parser aceitou → banco confirmou.
- [ ] Separar lifecycle prematuro de resposta não XML e de pressão de fila; não tratar os três como
  uma única causa.
- [ ] Reproduzir com payload sintético e abrir/atualizar issue upstream com evidência sem conteúdo.
- [ ] Se o upstream não resolver, apresentar um segundo gate ao dono para um fork/pacote fixado.
  Nunca editar bundle minificado dentro do cache instalado.
- [ ] O patch candidato deve impedir que saída transitória/ociosa do generator finalize a sessão
  enquanto o host ainda a usa, e deve preservar os tratamentos específicos de quota, autenticação e
  overflow.
- [ ] Adicionar testes de regressão para segunda interação na mesma sessão, resposta não XML,
  reciclagem do worker e duas sessões concorrentes.

### Fase 5 — detector fail-closed no Orquestra

- [x] Criar `orq/scripts/claude_mem_status.py`, somente leitura, abrindo o SQLite com `mode=ro` e
  devolvendo os estados definidos neste plano por host/projeto.
- [x] Não usar texto do banco como saída; apenas metadados e a razão técnica da classificação.
- [x] Criar `orq/scripts/test_claude_mem_status.py` com banco temporário e casos:
  `CAPTURANDO`, `ATRASADO`, `PARADO`, `OCIOSO`, `INDETERMINADO` e `EXCLUÍDO`.
- [x] Integrar a leitura em `orq/commands/stack.md` e `orq/commands/checkpoint.md`: health verde sem
  avanço do watermark deve aparecer como degradado, nunca como saudável.
- [x] Atualizar `orq/stack.md` e `memory/wiki/_stack.md` para distinguir plugin instalado, worker
  vivo, captura confirmada e projeto excluído.
- [ ] Qualquer mudança em `orq/` exige, no mesmo commit autorizado, bump nas quatro fontes de
  versão do projeto. Não bumpar, commitar, publicar ou instalar sem gate específico do dono.

### Fase 6 — gates e documentação

- [x] Rodar a suíte completa por descoberta:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'`.
- [x] Rodar `claude plugin validate ./orq --strict`.
- [x] Rodar `python3 orq/scripts/lint-coerencia.py .`.
- [ ] Rodar `git diff --check` e revisar somente os arquivos do T-075.
- [ ] Atualizar esta thread, `memory/MEMORY.md` e `memory/fixes-history.md` com resultado literal,
  incluindo projetos aprovados, excluídos e ainda indeterminados.
- [ ] Encaminhar para revisão hostil/cross-vendor e depois para validação do dono. Commit, release,
  instalação do Orquestra e push permanecem decisões separadas.

## Gate solicitado ao dono

A recomendação é aprovar agora:

1. exclusão fail-closed de `*Bruno Vascular*` no `claude-mem`;
2. atualização controlada do Codex para `13.24.1`, com backup, sessão nova e restart apenas do que
   o procedimento oficial exigir;
3. canários metadata-only no Claude e em todos os projetos Codex salvos, com o projeto clínico
   validado apenas como `EXCLUÍDO`;
4. implementação do detector no Orquestra após a captura estar estável.

Um patch/fork do `claude-mem` **não** está pré-aprovado: se `13.24.1` ainda falhar, volta ao dono
com a reprodução e um segundo gate.

## Resultado parcial da execução

- O empacotamento quebrado foi removido: Codex e Claude agora usam `13.24.1` com bundle idêntico.
- A exclusão clínica passou inclusive após `PostToolUse`: zero sessão e zero prompt.
- Os quatro canários Codex anteriores ao fallback ficaram `PARADO`; o canário Claude ficou
  `ATRASADO`. Logo, versão alinhada não equivale a captura saudável.
- O log estruturado pós-baseline tem zero mismatch, zero `SIGKILL` e zero `NOT NULL`, mas 11 falhas
  reais de autenticação do SDK em menos de um minuto; busca bruta sem filtrar nível produz falso
  positivo porque o próprio texto diagnóstico aparece nos metadados do log.
- O hook manual `UserPromptSubmit` funciona; o mesmo evento do manifesto do plugin não foi chamado
  pelo host Codex. O fallback mínimo foi adicionado ao `config.toml` após backup.
- Próximo gate: o dono cria chat novo pela interface e aprova “Recording prompt in claude-mem”.
  Nenhum hash de confiança foi escrito manualmente.
- Detector: 12 testes próprios; suíte completa 232/232; manifesto estrito e lint verdes.
