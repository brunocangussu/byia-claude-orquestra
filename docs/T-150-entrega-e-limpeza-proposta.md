# T-150 — entrega e limpeza propostas

**Estado:** R3 terminal APROVADO_COM_RESSALVAS, auditada e sem bloqueadores;
entrega Git allowlistada e limpeza local T-144 autorizadas pelo dono na
resposta “Autorizo as duas ações”, registrada na thread dona. Publicação,
instalação e restart permanecem fora. A versão candidata livre é 0.32.0.

## Resultado já conferido

- Main local e remoto consultado por `git ls-remote` em
  `4cdbcbc9f8a54ea33292bd7cd0407a36f995bb8c`, fonte 0.31.0.
- Seis referências locais já integradas foram removidas com `branch -d`,
  sem force; checkout T-149 limpo foi arquivado nativamente, recuperável.
- Permanecem main e candidato T-150 Codex. T-144 integrada, limpa e sem
  processos com cwd no checkout foi removida com autorização, sem force;
  os dois commits continuam na main e o ledger T-146 foi preservado.
- T-150 tem diff não commitado: mesmo HEAD que a main **não** prova integração.
  Tags/snapshots históricos e referências remotas ficaram intactos.
- R1 e sete sondas consumidas continuam registradas. A R2 tem gate próprio,
  uma chamada, pacote exato 78.999 bytes; não renovou o gate anterior.
- R3 consumida 1/1: pacote 131.019 bytes, Opus 5.5/high, sem retry;
  aprovação e limitações em `docs/reviews/T-150-R3-auditoria-local.md`.
- Main fresca: 870 testes, manifesto, lint e diff-check verdes. Cache Codex
  0.31.0 corresponde à fonte limpa remota; Claude continua no cache 0.27.10.

## Sequência de entrega autorizada

1. Preservar a auditoria do resultado terminal da R3 contra seu snapshot. Nenhum parecer,
   formato inválido ou bloqueador confirmado pendente permite integração.
   Correções locais da mesma causa continuam autorizadas, não outra chamada automática.
2. Reconsultar main/remoto, diferenças e ownership; conciliar por trechos.
   Não usar a cópia de board da worktree no lugar do board canônico.
3. Versão livre **0.32.0** confirmada e bump candidato nos quatro anchors. Preservar a fábrica
   de modelos e a seção ativa Claude neste card.
4. Após o bump autorizado, repetir descoberta completa, manifesto estrito,
   coerência, Ruff e diff-check. Conservar vínculo entre R3 e produto revisto;
   mudança funcional nova não recebe aprovação por omissão.
5. Montar índice somente com allowlist/hunks próprios; conferir staged antes
   do commit. Nada de `git add .`, reescrita de commit alheio ou restauração
   destrutiva da main. Se aparecer trabalho de outra frente, preservá-lo.
6. Commit/push e integração somente conforme operações nomeadas pelo dono.
   Confirmação do SHA remoto e gates da árvore integrada vêm antes da limpeza.
7. Remover a branch própria concluída somente após prova de ancestralidade,
   checkout limpo, nenhum processo dependente e backup/arquivo recuperável.
   T-144 só foi removida sob autorização humana específica. Exclusão remota é decisão separada.

Instalação/ativação e teste comportamental nos hosts continuam posteriores.
Fonte integrada não atualiza chats vivos e não significa card DONE.

## Allowlist candidata — sujeita a reconferência

Produto revisto na R3:

- `orq/agents/orq-planner.md`
- `orq/commands/dormir.md`
- `orq/commands/implement-next.md`
- `orq/commands/plan-next.md`
- `orq/commands/revisar.md`
- `orq/references/continuidade-evidencias.md`
- `orq/scripts/planner_coordination.py`
- `orq/scripts/test_continuidade_aprovada.py`
- `orq/scripts/test_planner_coordination.py`
- `orq/scripts/test_work_evidence.py`
- `orq/scripts/work_evidence.py`
- `orq/skills/orq/SKILL.md`

Elenco: somente os oito papéis/referências próprios de Host Codex em
`memory/wiki/_elenco.md`; Manager, Claude, presets e vias desligadas intactos.

Documentação: plano/thread T-150, decisão de continuidade, adoção Codex,
auditoria R1/R2/R3 e recibos saneados dos gates finais. Em arquivos compartilhados
MEMORY/KANBAN/log, incluir somente linhas/hunks próprios após nova leitura.
Pesquisa Haiku é proposta separada somente para Host Claude, não novo modelo
ativo nem mudança de catálogo. Codex mantém OpenAI nos papéis de escrita/scout.

Anchors autorizados: `orq/.claude-plugin/plugin.json`,
Status do `README.md`, linha de versão de `memory/MEMORY.md` e
`.claude-plugin/marketplace.json`.

Excluir da entrega por padrão: wrapper com caminho privado de CLI, harnesses
locais de chamada, fingerprints de conta, diretórios temporários, ledger/chave
de progresso, logs brutos e cópias supersedidas dos pacotes. Guardar os originais
localmente; produzir recibo público saneado sem promover simulação a prova real.
Não apagar essas evidências para tornar o status artificialmente limpo.

**Próximo passo:** concluir os gates frescos, commit/push e integração
allowlistados. Não repetir a revisão nem instalar, publicar ou reiniciar.
