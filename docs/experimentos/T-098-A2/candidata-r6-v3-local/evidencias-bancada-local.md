# Evidências locais da R6 v3

## RED e GREEN

O RED executado contra a R6 v1 falhou com
`AssertionError: 8 not less than 8`: o oráculo direto confirmou 8/8
abster com `?` e 0/40 nos outros casos. O GREEN da v3 passou com 18 testes,
mantendo 2/8 e 3/40 e rejeitando o atalho original por
`formato exclusivo de abster`.

## Mutações com causa nomeada

- O texto editorial Y028 da R6 v2 morre por
  `texto do corpus divergente: Y028`.
- Trocar Y041 pelo cenário da v2 morre por
  `cenário protegido divergente: Y041` e por
  `texto do corpus divergente: Y041`.
- Trocar Y009, um dos 37 textos protegidos, morre por
  `texto do corpus divergente: Y009`.
- Inserir lacuna decisiva em Y023 morre por
  `consulta marcada com escopo ausente: Y023`.
- Projeção com texto alterado e item string morre por
  `projeção texto divergente` e
  `item de projeção não é objeto`.
- Contagem lexical negativa morre por
  `contagem fora do intervalo`.

## Mapa de cenários preservados

| Cenário R6 v1 | Cobertura v3 |
| --- | --- |
| 48 IDs, seis golds e dois splits | manifesto v1 comparado por ID |
| quatro lotes id/text em ordem | `classifier_batches` e `validate_projection` |
| consulta delimitada | Y004, Y016, Y023 e guarda de escopo |
| abstenção por escopo ausente | Y007/Y028/Y031/Y032/Y042/Y043/Y044/Y045 |
| prévia de interface | Y009 protegido |
| fonte SVG e raster PNG | Y011 protegido |
| média não vazia e vazia | Y041 protegido |
| regra dev-only e finita | recomputação e fixture tiny |
| projeção e R5 histórico | três reproduções R5 com oráculos independentes |
| R5, R6 v1 e R6 v2 imutáveis | 14, 9 e 10 hashes respectivamente |

Número de testes não substitui esse mapa: cada linha identifica a guarda e o
cenário preservado.

