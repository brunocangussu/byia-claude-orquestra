# T-098 — handoff local pós-R8 v6

## Resultado

A candidata nova `docs/experimentos/T-098-A2/candidata-r8-v6-local/` fecha a
correção local do B1 da R8 e mantém estado `local_exploratory_not_campaign`.
Ela não é GO, avaliação de qualidade, holdout, campanha, pacote externo ou
autorização de ação seguinte.

## Correções verificadas

- Os 48 textos da v6 são byte a byte idênticos aos da R7 v5; os 37 textos
  protegidos continuam iguais à R6 v1.
- A guarda integral confronta os 48 IDs com R6 v1 em `gold`, `split`,
  `family`, `policy_code`, `facts` e `rationale`, e confronta também
  `policy_codes`, `taxonomy` e `batches` por JSON canônico.
- O histórico da R7 v5 entra no manifesto e é revalidado junto de R5 e R6
  v1-v4; nenhum snapshot antigo foi regravado. O complemento externo da v5
  permanece fora da candidata e preservado.
- A regressão de `_project_file` agora usa arquivo regular e symlink para
  arquivo real, ambos sintéticos em `TemporaryDirectory`, com controle
  positivo. Ela mata remoções de `is_symlink`, da guarda relativa e de
  `is_file`; não cria fixture no diretório congelado.
- O selo da v6 abrange runtime, três módulos `test_*.py`, oráculos e
  documentação v6. O único excluído é o próprio selo, para evitar hash
  circular; o recibo declara que isso não é autoautorização.

## RED/GREEN e gates

| Verificação | Resultado |
| --- | --- |
| RED da guarda integral antes de implementá-la | 1 teste, saída `AttributeError` de `validate_full_metadata_baseline`, exit 1 |
| GREEN da guarda integral | 6 testes, exit 0 |
| RED da saída do preflight sem `r7_v5` | 12 testes, saída `KeyError: 'r7_v5'`, exit 1 |
| GREEN da saída com `r7_v5` | 12 testes, exit 0 |
| Descoberta final v6 | 31 testes, exit 0 |
| Preflight final v6 | exit 0; R5=14, R6 v1=9, v2=10, v3=10, v4=10, R7 v5=11; `scores=not_evaluated` |
| Suíte obrigatória `orq/scripts` | 447 testes, exit 0 |
| `claude plugin validate ./orq --strict` | exit 0 |
| `python3 orq/scripts/lint-coerencia.py .` | exit 0 |

O JSON de evidências adjacente contém os comandos, todos os hashes da v6,
mutantes executados e os limites. A auditoria local também confirmou que não
há `__pycache__` na candidata.

O `git diff --no-index --check` não encontrou espaço terminal nos 14 novos
artefatos de código, teste, selo e handoff. `amostra.json` mantém a linha em
branco final herdada da v5: ela foi preservada intencionalmente junto do
snapshot textual, em vez de reformatar o corpus para satisfazer um check
estético.

## Limites e próximo gate

Atalhos lexicais e pontuação continuam apenas guardas estreitas de padrões
históricos: não provam qualidade, ausência de atalho, generalização ou
holdout. Não houve inferência, score, chamada A2/B2, rede, login, retry,
Git, bump, release, instalação ou restart.

Próxima ação: auditoria local e gates frescos do Manager sobre a candidata e
suas evidências. Uma revisão externa do novo snapshot só pode ser pedida após
novo gate humano. Não mover board nem promover sem esses gates e a validação
do dono.
