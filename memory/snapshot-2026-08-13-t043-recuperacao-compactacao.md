# Snapshot — T-043 após compactação inesperada

Data: 2026-08-13
Branch: `feat/t043-compactacao-reidratada`
HEAD: `d081608`

## Estado durável

- T-043 continua em implementação/review; o board não foi movido.
- Contrato aprovado: no Codex, hooks nunca bloqueiam; checkpoint documenta o progresso e a conversa
  pode continuar. No Claude, o fluxo próprio com `/clear` permanece inalterado.
- O cache instalado `0.22.0` não é fonte confiável para a correção definitiva; a solução precisa
  entrar na fonte `0.22.1` e ser instalada como nova release local.
- O worktree contém oito arquivos modificados e não commitados com 322 inserções e 147 remoções:
  `AGENTS.md`, `CLAUDE.md`, `README.md`, `memory/wiki/arquitetura.md`,
  `orq/commands/checkpoint.md`, `orq/scripts/context-guard.py`,
  `orq/scripts/test_context_guard.py` e `orq/skills/orq/SKILL.md`.
- `git diff --check` passou antes deste snapshot. A suíte completa ainda não foi rodada nesta
  retomada.
- Painel anterior: Kimi K3 aprovou com ressalvas e sem bloqueadores; a tentativa Opus 5 expirou e
  não vale como parecer.

## Próxima ação

Validar o diff preservado sem reimplementá-lo: testes unitários do guardião, `py_compile`, manifesto
estrito, lint, identidade AGENTS/CLAUDE e smokes de 60%, 70%, recuperação sem telemetria e estado
legado. Depois obter parecer Opus 5 válido, reconciliar Kimi e somente então integrar/instalar.

Não fazer push, publicação, update do Claude nem alterar o backstop de 90%.
