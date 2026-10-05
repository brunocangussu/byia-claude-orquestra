# R6 v3 local — política, linhagem e limites

## Estado

A candidata `T-098-A2-R6-v3-local` é um snapshot local corretivo de
2026-10-04. Não foi enviada a modelo, não calcula score, não usa reserved para
fit e não é holdout cego, aprovação nem produção.

A base textual é exclusivamente a R6 v1. Dos 48 textos, 37 permanecem
byte-a-byte iguais à v1; somente Y004, Y007, Y016, Y023, Y028, Y031, Y032,
Y042, Y043, Y044 e Y045 foram substituídos pelos textos autorizados do lote 3.
A R6 v2 não é fonte de texto da v3. Ela é somente baseline imutável de
integridade.

## Consulta e abstenção

Consulta é pedido de informação com escopo já delimitado: Y004, Y016 e Y023
perguntam sobre comportamento atual e proíbem alteração. Abster é pedido de
ação sem escopo decisivo: Y007, Y028, Y031, Y032, Y042, Y043, Y044 e Y045
exigem esclarecimento sobre regra, autoridade, operação, dado, evidência ou
efeito.

`question_required` permanece um fato de comportamento de saída, não uma
condição sintática do prompt. Na v3, 2/8 abster e 3/40 demais textos usam
interrogação. A guarda rejeita o perfil original da v1 (8/8 contra 0/40),
mas não classifica pedidos reais por pontuação.

## Cenários concretos preservados

- Y009 mantém a etapa de prévia na interface fictícia, com lista, navegação,
  resumo e confirmação.
- Y011 mantém `assets/roteador-legenda.svg`, a saída PNG e o limite de não
  tocar no código do roteador.
- Y041 mantém as duas saídas `[2,4] -> 3` e `[] -> null`, restringindo a
  correção ao denominador quando necessária.

Essas comparações de corpus são fixtures autorais da candidata, aplicadas
antes de seu selo. Não são blacklist de pedidos reais, detector geral de
semântica nem prova independente de gold humano.

## Taxonomia, partições e regra

Gold, split e família são os da R6 v1 para os 48 IDs. Famílias descrevem
mecanismos e podem atravessar dev/reserved; o split garante composição, ordem,
projeção e fronteira de fit, não independência semântica.

A regra lexical é recomputada deterministicamente apenas dos 24 casos dev,
com presença de token, mínimo de dois caracteres, suavização 1, top-5 e
desempate por peso decrescente/token crescente. O harness exige igualdade da
derivação, tipos e faixas finitas. Reserved não é usado para score, ajuste ou
avaliação nova.

## Limites

O corpus e seus golds não receberam revisão externa neste lote. As mutações
provam as guardas locais de formato, linhagem, projeção, cenário e regra, não
generalização, qualidade de modelo ou comportamento em produção.

