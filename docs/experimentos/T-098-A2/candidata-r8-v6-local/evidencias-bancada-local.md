# Evidências locais — candidata R8 v6

## RED/GREEN reexecutável

O RED da guarda integral foi observado antes da implementação da v6: o teste
`test_adjudicacoes_integrais_dos_48_igualam_o_baseline_v1` falhou porque
`validate_full_metadata_baseline` ainda não existia. O GREEN passa depois da
guarda que compara, para os 48 IDs, `gold`, `split`, `family`, `policy_code`,
`facts` e `rationale`, além de `policy_codes`, `taxonomy` e `batches` globais
contra o manifesto R6 v1 já ancorado.

A descoberta `test_*.py` executa `test_preflight.py`, `test_mutations.py` e
`test_v6_integrity.py`. Os dois oráculos auxiliares são chamados por testes
descobertos; não são a única cobertura declarada da candidata. O oráculo de
adjudicação registra RED somente contra o baseline histórico que não tinha a
guarda e GREEN quando a candidata rejeita a mutação, sem confundir esse
resultado com qualidade de classificação.

## Mutações cobertas

- Alterações sem reanotar em `policy_code`, `facts` e `rationale` de Y007
  falham com `metadados completos v1 divergentes: Y007`.
- Alterações de `policy_codes`, `taxonomy` e `batches` falham antes de selo,
  com a chave global nomeada.
- `_project_file` usa `TemporaryDirectory`: um arquivo regular interno é o
  controle positivo; caminho absoluto, `dir/../target.txt`, ausente, diretório
  e symlink para arquivo real interno são rejeitados. Os mutantes que removem
  `is_symlink`, a guarda relativa ou `is_file` aceitam a entrada indevida.
- A linhagem preserva os 48 textos da v5 byte a byte, os 37 textos protegidos
  em relação à v1 e os históricos R5, R6 v1-v4 e R7 v5 por SHA-256.

## Selo e limites

`selo-congelamento-r8-v6.json` cobre o runtime, todos os testes descobertos e
os documentos da v6 listados no manifesto. O selo exclui apenas o próprio
arquivo para evitar hash circular; ele registra integridade local e não é
gerado como autorização, aprovação, release ou GO.

As contagens lexicais e de pontuação são guardas estreitas contra os padrões
históricos nomeados. Elas não demonstram qualidade semântica, ausência de
atalhos, generalização, independência textual ou validade de holdout. Não há
score, ajuste em `reserved`, inferência, chamada A2/B2, rede, login, retry ou
ação externa nesta candidata.
