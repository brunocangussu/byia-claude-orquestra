# Plano T-081 — `OBSERVATION_TYPES` sem efeito silencioso

**Data:** 2026-09-08
**Host responsável:** Codex
**Trilha / faixa:** sistema / normal
**Estado:** opção A aprovada e implementada na fonte 0.27.6; publicação, instalação e restart aguardam novo gate do dono

## Problema comprovado

`CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES` é aceita e persistida pelo endpoint de settings do
claude-mem, mas não é consumida pelo gerador de contexto. O filtro efetivo vem de
`getActiveMode().observation_types`. Esses mesmos tipos também compõem o `type_guidance` do
observer; portanto, removê-los por modo derivado reduz o que é capturado, não apenas o que é
injetado. Isso contaminaria a comparação isolada do `T-078`.

## Opções

### A — corrigir o contrato do Orquestra, sem alterar captura (recomendada)

1. Remover das instruções vivas a recomendação de configurar
   `CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES` como filtro de injeção.
2. Manter `CLAUDE_MEM_CONTEXT_OBSERVATIONS=25` e
   `CLAUDE_MEM_CONTEXT_SESSION_COUNT=5`, que são chaves efetivas e independentes.
3. Acrescentar uma guarda automatizada que falhe se a chave morta voltar a ser prescrita como
   configuração funcional nas superfícies vivas do plugin.
4. Preservar as menções históricas, explicitamente marcadas como diagnóstico de chave morta.
5. Não criar modo local e não alterar `~/.claude-mem`, hooks ou ativação por host.

**Efeito:** elimina o falso all-clear sem mudar a captura nem a janela comparativa.

### B — criar modo derivado removendo tipos

Criar um override persistente em `~/.claude-mem/modes/`. É tecnicamente suportado, mas altera o
vocabulário do observer e faz tipos sumirem do banco. **Não recomendado durante o `T-078`.**

### C — implementar filtro apenas de injeção no claude-mem

Alterar o upstream para separar `context_observation_types` de `observation_types`. É o desenho
semanticamente correto para filtrar somente a leitura, porém está fora do repositório Orquestra e
exige uma frente própria, com patch/release do claude-mem. Não deve ser improvisado no cache.

## Escopo da opção A

- Corrigir as superfícies prescritivas vivas que ainda tratam a chave como funcional.
- Adicionar teste/guarda focado na prescrição, sem proibir textos históricos que documentam o bug.
- Atualizar board, thread, índice e log ao concluir.
- Bump da fonte para 0.27.6 nos quatro anchors exigidos pelo repositório, depois de reconciliar a
  `origin/main` atual.

## Fora de escopo

- Religar o claude-mem no Codex.
- Modificar os seis hooks do AI-Memory.
- Criar ou ativar modo derivado.
- Patch direto em cache instalado.
- Publicação, instalação ou restart sem autorização específica.

## Critérios de aceite

1. Nenhuma superfície viva afirma que `CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES` filtra a injeção.
2. A guarda falha diante de uma prescrição funcional reintroduzida e aceita menção histórica clara.
3. As duas chaves de contagem continuam documentadas como efetivas.
4. O estado local permanece: AI-Memory ativo nos dois hosts; claude-mem ativo no Claude Code e
   desligado nos dois pontos do Codex durante o `T-078`.
5. Passam os três comandos obrigatórios: suíte completa com `PYTHONDONTWRITEBYTECODE=1`, validação
   estrita do manifesto e lint de coerência.
6. Se houver mudança em `orq/`, caches e comportamento só serão validados após release autorizado,
   instalação a partir de fonte limpa e restart de cada host.

## Execução da opção A

1. A worktree foi atualizada a partir da `origin/main` publicada pela frente Claude e os conflitos
   foram reauditados.
2. A guarda nasceu com teste vermelho real e depois passou com a correção.
3. Somente as superfícies prescritivas do escopo foram corrigidas.
4. Suíte completa, manifesto estrito e lint passaram na fonte 0.27.6.
5. A documentação canônica e a revisão independente foram concluídas; a promoção para os caches
   permanece separada.

## Próximo gate do dono

Autorizar, em etapa separada, a publicação da 0.27.6, a instalação nos hosts Claude e Codex e o
restart necessário para validar os caches e o comportamento carregado.
