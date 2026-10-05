# Evidências da bancada local R5

## Escopo executado

Esta bancada adiciona um preflight determinístico e testes persistentes em
`candidata-r5-local/`. Ela não chama modelo, não transmite dados, não prepara
pacote externo e não altera a candidata R4, a amostra R5, a regra congelada ou
o resultado já preparado.

## RED executável

Antes de criar `preflight.py`, a descoberta da candidata R5 apontada para o
preflight R4 (somente leitura) saiu com `exit 1`: quatro `AssertionError:
ValueError not raised` para troca de gold que preserva contagens, texto antigo
em dev, texto antigo em reserved e Y006 sem contrato observável. Logo, o RED
reproduziu lacunas reais por asserção, não por erro de importação ou de
harness.

## GREEN e mutações

O preflight R5 valida os 48 IDs, os metadados `id/gold/family/split` da
referência R4, as 18 famílias, seis classes, as duas partições e os textos
congelados. Ele também produz quatro lotes de doze casos contendo somente
`id`/`text`, verifica os três selos congelados antes da pontuação e reproduz a
regra lexical sem refit.

`test_mutations.py` mata, por `ValueError`, texto antigo em dev e reserved,
Y006 sem cenário observável, troca de gold, Y038 sem rejeições contratuais,
Y047 sem isolamento de prosa, família alterada, partições cruzadas, projeção
com `gold` e os três artefatos com selo adulterado. São guardas estruturais;
não aprovam gold nem independência semântica.

## Comandos e resultados

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s docs/experimentos/T-098-A2/candidata-r5-local -p 'test_*.py'
# 16 testes, exit 0

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s docs/experimentos/T-098-A2/candidata-r4 -p 'test_*.py'
# 14 testes, exit 0

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s orq/scripts -p 'test_*.py'
# 447 testes, exit 0

claude plugin validate ./orq --strict
# exit 0

python3 orq/scripts/lint-coerencia.py .
# exit 0
```

O gate da bancada devolveu quatro lotes de 12 e os placares congelados
`dev=23/24`, `reserved=16/24`. Os hashes preservados são:

- `amostra.json`: `fba8c8a5f07375540369cb471c6cd8a21959564259edc7a823f2d897096ca4fb`
- `regra-lexical-congelada.json`: `1099ea053837a70a5e1c7a9da7b4c9d7c6f19a0b6663103fb9f74521eee9a751`
- `resultado-diagnostico-local.json`: `1bbc316515b66fa2ee0c3dc575c4aee7006b94e5d6f9567503f8ad4a2ab29b49`

## Limites e próximo passo

Auditoria complementar do Manager, em 2026-10-03: discover da candidata
16/16 em 0,050 s, histórica 14/14 em 0,048 s e plugin 447/447 em 43,141 s;
manifesto, lint, Ruff e diff-check verdes. A reprodução read-only contra o
preflight R4 matou as quatro expectativas por `AssertionError: ValueError
not raised`, com zero erros do harness. O nome de um método estava errado
na primeira tentativa de montar essa auditoria; a tentativa não executou
testes e não foi usada como evidência RED. A execução corrigida obteve os
quatro métodos existentes por descoberta antes de construir a reprodução.

O resultado continua exploratório, não cego; não demonstra qualidade do gold,
independência entre mecanismos, eficácia econômica do JEV nem capacidade de
vias reais. Revisão independente do gold e qualquer classificação R5 seguem
pendentes de autorização própria.
