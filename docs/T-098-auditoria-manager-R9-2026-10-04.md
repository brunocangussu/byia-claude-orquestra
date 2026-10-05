# T-098 — auditoria da rechecagem R9

## Decisão e limite

**GO independente registrado, sem repetir a revisão.** Uma chamada oficial
Claude CLI/Opus 5.5, 176.772 bytes sanitizados, exit 0, 86,896 s, formato
válido. B1 da R8 foi classificado CORRIGIDO; nenhum bloqueador novo no escopo.
Parecer, recibo e log estão em
`docs/reviews/T-098-R9-rechecagem-correcoes-2026-10-04/`.

A aprovação cobre a correção da bancada v6 e regressões do ajuste. Não prova
assertividade/economia do JEV, não autoriza campanha A2/B2, adoção,
integração Git, instalação ou release. A2/B2 permanecem sem novas chamadas.

## B1 e preservação conferidos pelo Manager

O teste descoberto `test_v6_integrity.py` usa symlink para arquivo regular,
controle positivo e rejeição explícita; os três mutantes exercitam as
guardas relativa, arquivo e symlink. A fixture é temporária, não altera a
candidata congelada. A prova é local/estrutural, não conduta de LLM.

Conferência pós-review: pacote intacto, 18/18 fontes externas sem mudança e
13/13 hashes da candidata iguais ao recibo local. A evidência anterior
registra amostra v6 byte-idêntica à v5, 48/48 textos iguais à v5 e 48/48
registros com gold, split, family, policy_code, facts e rationale iguais à
v1; taxonomy, policy_codes e batches também preservados. Selo local com
12 alvos, distinguido da ancoragem externa do Manager. A afirmação falsa
histórica da v5 não foi regravada nem aceita como prova.

Recibo fresco anterior ao envio:
`docs/T-098-gates-manager-pos-R8-v6-lote-545205-2026-10-04.json`.
Suíte descoberta 447 testes, bancada v6 31 testes, preflight, manifesto,
lint e diff-check: exit 0. O reviewer não executou esses comandos; o GO não
é certificação remota da execução.

## Ressalvas não bloqueantes, sem alteração após GO

- O selo interno é autocontido, não autoridade externa: mantida a
  conferência de hashes pelo Manager e o pacote congelado.
- Falha de selo não substitui discriminação comportamental: as asserções
  dirigidas cobrem os casos de caminho e os mutantes.
- Symlink requer capacidade do sistema operacional; impossibilidade deve
  falhar, não passar silenciosamente. O ambiente local é macOS.
- As limitações lexicais, Y042 e a evidência RED contra v4 permanecem
  delimitadas; não inventar execução remota ou inferência real.
- Nomes herdados `load_v5` são manutenção cosmética, não bloqueador
  demonstrado nesta rechecagem.

## Próximo passo

Review desta correção fechado. Não reabrir T-098 R9 por ausência genérica
de review. Conciliar a entrega somente com autorização correspondente;
campanhas e gate de adoção geral são etapas distintas.
