# Handoff para a conversa Claude — T-089/T-090

2026-10-02. Destino: conversa Claude já existente da frente Companion.
Este arquivo é uma mensagem preparada para Bruno encaminhar, não uma
chamada ao modelo nem autorização emitida por outro agente.

## Mensagem para encaminhar

Retome o T-089/T-090 no checkout e branch próprios. O Codex registrou
minha aprovação das correções locais de T-131/T-098; elas ainda não
começaram, pois a prioridade máxima agora é o T-143: continuidade do
desenvolvimento aprovado sem bloqueios redundantes. O T-143 está em
desenho, não foi implementado nem instalado.

Nesta etapa, faça só preparação e conciliação read-only do T-089 com o
estado atual das outras frentes. Não repita as provas Companion/fresh/
resume nem as R4 T-131/T-098. Não faça chamadas externas, autenticação,
bump, commit, amend, push, merge, publicação, instalação ou restart.
Não modifique o elenco nem os arquivos do produto compartilhados.

Confira o commit preservado e devolva: mapa dos trechos sobrepostos,
contratos/testes que devem sobreviver e patch proposto separado (não
aplicado). Explique qualquer dúvida ou falta de revisão independente.
Pode registrar o handoff em documento novo do seu checkout, sem mudar
as fontes ou reescrever a thread/board da main. Aguarde depois a fonte
final T-131/T-143 antes da conciliação executável. Se não existir trabalho
útil permitido, registre o ponto de retomada e encerre; não invente tarefa.

## Estado reconferido pelo Codex

- main: 4e58e7f19a8b6b51cb8ab33232862be431b3005d; trabalho não commitado
  de outras frentes preservado. Não presumir main limpa, não dar checkout
  de arquivos a partir do HEAD nem usar git add .
- T-089: branch claude/t089-companion-identidade; commit
  2a879d94df86c998b401c84361603705ea1d06b6; checkout limpo no momento
  da conferência, com base 4e58e7f.
- Checkout T-089:
  /Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/.claude/worktrees/agent-a054e5c8dd838fcb5
- T-131: branch codex/t131-elenco-sol61-luna6; checkout
  /Users/brunocangucu/.codex/worktrees/t131-elenco-sol61-luna6/byia-claude-orquestra
- T-098: documentação/amostra da frente JEV na main, ainda sem R5 ou
  classificações novas. R4 1/1 consumida em cada card.
- T-143: thread memory/wiki/threads/T-143-continuidade-aprovada.md na
  main. Nenhuma modificação em orq/ feita nesta investigação.

## Contratos que a conciliação deve preservar

1. Continuação aceita somente com sucesso, JSON válido, status 0,
   jobId/threadId não vazios e threadId exatamente igual ao solicitado.
2. Divergência preserva vínculo anterior e registra IDs/runtime/motivo;
   sem rawOutput aceito como prova, fallback, nova task ou resume-last.
3. --wait pertence ao envelope codex:codex-rescue, não ao task do runtime.
4. --write permanece proibido na via read-only.
5. Elenco ativo não deve virar candidato por cópia do template; modelos,
   aliases, defaults e gate de capacidade da frente T-131 não são decididos
   pela frente Companion.
6. Continuidade T-143 não altera orçamento externo, segurança ou o
   controlador do App; não antecipe essa política antes da aprovação.

## Arquivos sobrepostos

| Arquivo | T-089 | T-131 / possível T-143 |
|---|---|---|
| orq/skills/orq/SKILL.md | Identidade/reúso | Modelo candidato / continuidade |
| orq/commands/revisar.md | Envelope --wait | Modelo/runner / continuidade |
| orq/commands/elenco.md | Capacidade/identidade | Modelos/aliases; não é alvo do T-143 |
| orq/commands/plan-next.md | Envelope --wait | Possível contrato de aprovação T-143 |
| memory/wiki/_elenco.md | Matriz/identidade | Elenco vivo protegido; não mudar |
| memory/wiki/arquitetura.md | Identidade/--wait | Documentação futura T-143, conciliar por trecho |

Os seis testes novos e a separação de --wait devem continuar cobrindo os
mesmos mecanismos após a futura conciliação. Suíte verde não substitui
parecer independente válido do snapshot final. Sem reserva de versão;
nenhuma publicação/instalação autorizada por esta mensagem.

