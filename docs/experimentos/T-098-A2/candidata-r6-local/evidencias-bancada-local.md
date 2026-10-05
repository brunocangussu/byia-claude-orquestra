# T-098 A2 — evidências da bancada local R6

## RED/GREEN

- RED real: o discover da R6 falhou em test_projecao_tem_contrato_dedicado porque preflight.py não existia (FileNotFoundError).
- GREEN inicial: após criar o módulo, o mesmo teste passou.
- GREEN completo: o discover R6 executou 19 testes, exit 0.

## Mutações em memória

Os testes usam cópias em memória e não regravam R4/R5. Eles rejeitam: texto projetado adulterado com [gold=trivial]; item string antes de qualquer acesso de campo; campo gold ou reason no payload; troca de ordem; troca de gold preservando contagens pela política; troca de split/família pelos guardas de lote/taxonomia; texto por ID antes do hash geral; peso 999999 pela derivação; NaN, contagens negativas e token de um caractere pelo schema; e selo geral adulterado.

O fixture tiny calcula, sem espelhar o helper, presença, contagens, peso log(3) e desempate ASCII. O teste da regra real verifica exatamente 24 linhas dev; nenhum teste calcula score R6.

## Gates finais

- R6 discover: 19 testes, exit 0.
- discover integral do projeto: 447 testes, exit 0.
- claude plugin validate <orq> --strict: exit 0.
- lint-coerencia.py <worktree>: exit 0, 20 nomes conferidos.
- git -C <worktree> diff --check: exit 0, sem saída.
- verify_historical_r5 foi exercitado no discover R6 e conferiu 14 fontes R4/R5.

Os comandos de Git relativos executados inicialmente pelo ambiente de análise fora do worktree foram descartados; somente os comandos com git -C são evidência final.

Execuções intermediárias dentro do wrapper de análise falharam fora do worktree: uma não encontrou o pacote `orq` (422 testes, 1 erro) e outra perdeu um marcador temporário criado por `test_verify_installed_cache`. Não tocavam R6. A evidência final veio do comando obrigatório executado diretamente no worktree: 447 testes, exit 0. Isto é falha de ambiente do wrapper, não correção aplicada ao produto.

## Limites

A ausência literal de human* e contrat* é auditoria pós-hoc, não prova de independência. A política local não é revisão semântica independente. Não houve chamada de modelo, rede, login, campanha, fit/score em reserved, Git mutante, bump, instalação, restart ou publicação.
