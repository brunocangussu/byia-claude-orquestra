# Handoff — T-150, fonte 0.32.0 entregue

## O que foi entregue

Fonte em `3cfac6291b22d380c5631326f98ab74eb74ac4ce`, main/local e GitHub,
integração fast-forward. Commit de 39 arquivos allowlistados; checkpoint
documental subsequente não altera o produto revisado. Quatro anchors 0.32.0.

- Elenco Codex: Opus 5.5/high em planner interface e reviewer; Sol 6.1/xhigh
  em planner sistema e implementer pesada; Sol 6.1/high em normal; Luna 6/
  medium em leve e scout, Luna 6/low em docs. Manager é escolha da sessão.
  Host Claude, presets e vias desligadas preservados.
- Sem teto global de duas revisões. Duas sem progresso exigem diagnóstico
  e estratégia diferente, não encerramento automático da meta. Gates
  humanos, saldo externo e orçamento continuam obrigatórios.
- Coordenação técnica opt-in no mesmo Planner, não um sexto agente.
- Helper de evidências/JEV offline e consultivo. API e campanha A2/B2 não
  executadas; qualidade/economia comparativas continuam sem prova.
- Haiku 5.5 é proposta de piloto exclusivamente no Host Claude. Nenhum
  trigger, writer/docs/scout Anthropic foi inserido no Host Codex.

## Evidências

R3 Opus 5.5 via Claude CLI: APROVADO_COM_RESSALVAS, sem bloqueadores após
auditoria; uma chamada, sem retry. Modelo observado 5.5, high enviado;
effort no servidor não observado. Snapshot funcional preservado e oito
configurações do elenco inalteradas na promoção documental.

916 testes na candidata e na main, manifesto estrito/lint/Ruff/diff-check
exit 0. Main: Python 3.14.7, 238,205 s, dois ResourceWarnings registrados.
Recibos públicos: `docs/T-150-verificacoes-entrega.json` e
`docs/T-150-R3-recibo-publico.json`. Originais com conta/path/keys continuam
privados na worktree T-150; nenhuma nova chamada externa nesta entrega.

## T-144 e organização

Fases 1/2 já estavam integralmente na main; não havia patch exclusivo.
Checkout e branch local `claude/t144-medidor-progresso` removidos com
autorização, sem force. Commits ba523e9/064e726 continuam na main; ledger
T-146 idêntico. Não houve merge vazio, reset, amend ou exclusão remota.
T-144/T-146 seguem VALIDATE; T-147/fase 3 não foi implementada.

## O que não foi feito

Sem publicação, instalação ou restart. Diretórios observados: Codex 0.31.0;
Claude 0.27.10/0.31.0; nenhum cache 0.32.0. Presença no cache não prova
habilitação, integridade ou carga em chats. Não afirmar que todos os chats
já executam a política nova.

Próximo gate: autorizar separadamente ativação e validar comportamento a
partir da fonte remota limpa, seguindo o procedimento do projeto. Até lá,
T-150 permanece VALIDATE, e os saldos R1/R2/R3 não são renovados.

Verificação final do checkpoint: 916 testes, 277,321 s, Python 3.14.7;
manifesto/lint/Ruff/diff-check exit 0, dois ResourceWarnings. Nenhuma mudança
funcional depois da R3; as nove linhas Codex (Manager + oito papéis) permanecem
iguais à fonte entregue. O checkpoint subsequente é documental e allowlistado.
