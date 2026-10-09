# T-150 — auditoria da branch histórica T-144

**Pedido:** conferir o trabalho do Claude após o encerramento da conversa,
sem duplicar implementação, merge ou assumir a frente mods. Auditoria em
08/10/2026, Bahia. Nenhuma instalação ou restart.

## Conclusão

**As fases 1 e 2 estão integralmente na main e no GitHub. Não existe código
exclusivo da branch T-144 para integrar.** A limpeza local foi autorizada e
concluída conforme o complemento abaixo; validação prática é outra pendência.

## Git e preservação

- Main/local e remoto consultado: `4cdbcbc9f8a54ea33292bd7cd0407a36f995bb8c`,
  fonte 0.31.0.
- Branch `claude/t144-medidor-progresso`: `064e726`; fase 1 `ba523e9` e
  fase 2 `064e726` são ancestrais da main. Reconciliação original pelo T-148.
- `rev-list --count main..claude/t144-medidor-progresso`: 0.
- `diff --name-only main...claude/t144-medidor-progresso`: vazio.
- `merge-base --is-ancestor`: exit 0.
- Status, staged e arquivos ignorados do checkout Claude: vazios.
- Nenhum processo com cwd nesse checkout na leitura por lsof; exit 1,
  stdout/stderr vazios. Isso não equivale a matar sessões ou serviços.
- Ledger T-146 continua privado na raiz principal, pausado/validate,
  revisão 28, plano 9/9. Não foi transferido, editado ou removido.
- A thread apontada falta no THREAD_ROOT do checkout Claude. Não foi criada,
  duplicada ou substituída pela thread da main. A auditoria usa código,
  Git, board canônico e handoff público, sem retomar o Loop B dessa frente.

## Gates frescos da main

Todos executados com fonte principal atual; não representam teste de rollout.

| Gate | Resultado |
|---|---|
| `unittest discover -s orq/scripts -p 'test_*.py'` | exit 0; 870 testes, 195,224 s |
| `claude plugin validate ./orq --strict` | exit 0 |
| `lint-coerencia.py .` | exit 0 |
| `git diff --check` | exit 0 |

`PYTHONDONTWRITEBYTECODE=1` foi preservado. Interpretador observado na suíte:
Python 3.14.7. Dois ResourceWarnings de arquivo não fechado apareceram; não
há falha de teste, mas o aviso não foi escondido nem corrigido nesta auditoria.

Descoberta por módulo confirma 268 testes do medidor: núcleo 171,
procedimento 10, hooks 62, statusline 25. Cobrem ownership/chaves distintas,
contenção, fase versus percentual, 100% sem DONE, hooks consultivos, lembrete
único e preservação das seis entradas do context-guard.

## Fonte instalada versus uso real

- Codex: cache 0.31.0 existe com núcleo/hook do medidor. Verificador da
  fonte limpa detached do SHA remoto acima, status vazio antes/depois,
  confirmou cache normalizado correspondente: exit 0, stderr vazio.
  A cópia limpa foi temporária, sem criar branch/worktree no projeto.
- Claude: não existe cache 0.31.0; a única versão encontrada nesse cache
  é 0.27.10. Diretório presente não prova plugin habilitado ou carregado.
  Não foi instalado/ativado nada para corrigir isso por omissão.
- O teste real da statusline/lembrete Claude e o acompanhamento do plano
  sem tratar 100% como DONE continuam pendentes. Não afirmar paridade
  entre todos os chats a partir de testes locais ou do cache Codex.

## Destino recomendado, ainda dependente da decisão de limpeza

Remover somente o checkout limpo T-144 e a branch **local**
`claude/t144-medidor-progresso`, sem `--force`, preservando todos os commits
já alcançáveis pela main, ledger, tags, backups e referências remotas.
Não fazer merge vazio, recommit, amend, reset ou exclusão remota.

A limpeza foi apresentada ao dono em pergunta assíncrona antes da remoção.
Enquanto não houver resposta, o checkout e a branch permanecem intactos.
Repetir os checks de segurança imediatamente antes de uma remoção autorizada.

T-144/T-146 continuam em VALIDATE, sem troca silenciosa de frente. A fase 3
T-147 (Orca/watch multi-raiz e decisão do espelho Codex) não está implementada
por essa branch e permanece backlog separado. Limpar a branch não fecha cards.

## Complemento — limpeza autorizada e executada

O dono respondeu “Autorizo as duas ações” ao gate de entrega T-150 e limpeza
local T-144. Preflight repetido: branch ancestral da main, status vazio
inclusive ignorados, lsof sem processos com cwd no checkout. Executados
`git worktree remove` no checkout exato e `git branch -d
claude/t144-medidor-progresso`, sem force; ambos exit 0.
Diretório e referência local ausentes depois; ba523e9 e 064e726 continuam
ancestrais da main. Hash do ledger T-146 idêntico antes/depois:
`5e6b9f1202cebced080f2c18ca8f8eca3d55afbb0c9f8449cea72564a739c17a`.
Nenhuma alteração de frente, chave, referência remota, instalação ou restart.
A seção de destino acima registra a proposta anterior, já consumida por
este gate. T-144/T-146 permanecem VALIDATE e T-147 permanece separado.
