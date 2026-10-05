# Evidências locais da R6 v2

## RED real

Antes da implementação da v2, o teste semântico executado contra a R6 v1
imutável falhou com `AssertionError: 8 not less than 8`. O oráculo direto
confirmou o perfil: 8/8 abster continham `?` e 0/40 dos demais casos o
continham. Não foi usado módulo ausente como RED.

## GREEN e oráculos independentes

O discover da pasta da v2 executou 14 testes locais com saída 0. Eles incluem
oráculos diretos que não espelham as funções sob teste:

1. A R5 imutável aceita projeção cujo texto recebe `[gold=trivial]`; a v2
   rejeita com `projeção texto divergente`.
2. A R5 imutável acessa `.get` de um item string e levanta
   `AttributeError`; a v2 valida o tipo antes do campo e rejeita com
   `item de projeção não é objeto`.
3. A R5 imutável aceita peso 999999 e contagem negativa; a v2 rejeita regra
   com peso forjado por `derivação da regra divergente` e testa a contagem
   negativa por `contagem fora do intervalo`.

A R6 v1 é apenas lida durante essa reprodução. A v2 também revalida os
14 hashes R5 e os 9 hashes da R6 v1.

## Mutações

- Tornar 8/8 abster textos interrogativos é rejeitado por
  `formato exclusivo de abster`.
- Remover todas as interrogações fora de abster é rejeitado pelo mesmo limite.
- Acrescentar `missing_decisive_scope` à consulta Y023 é rejeitado por
  `consulta delimitada marcada como sem escopo`.
- Tornar negativa a contagem de uma feature é rejeitado antes da derivação.

A mutação que remove uma interrogação de entrada de Y031 ainda passa a
política de saída: `ask_clarifying_question` pertence ao comportamento
anotado, não à gramática da frase.

## Regra

O teste tiny usa quatro textos sintéticos e confere manualmente os pesos
log(3) e log(2), a presença por caso e o desempate. Ele testa a função pura de
derivação e não avalia a amostra reserved.

