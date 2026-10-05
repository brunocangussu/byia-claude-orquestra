# T-098 — congelamento do diagnóstico lexical local

2026-10-02. Regra ajustada somente nas 24 linhas `dev`, gravada e hasheada
**antes de pontuar a partição reserved com essa regra**. Não é o congelamento
final da campanha, nem classificação por JEV/Luna. O autor já conhece os
pedidos e o gold de ambas as partições: diagnóstico exploratório, não cego.

- Amostra candidata: 27.883 bytes; SHA-256
  `fba8c8a5f07375540369cb471c6cd8a21959564259edc7a823f2d897096ca4fb`.
- Regra: 5.423 bytes; SHA-256
  `1099ea053837a70a5e1c7a9da7b4c9d7c6f19a0b6663103fb9f74521eee9a751`.
- Projeção de treinamento: SHA-256
  `0ca1a92733cdf4d6c8f419dc8e022fdaaa4887d1d1f7dc0924a376f1380a8875`.

## Receita reproduzível, sem inferência

1. Filtrar `split=dev`, ordenar por ID, projetar `id,text,gold` nessa ordem
   e serializar JSON compacto UTF-8. O digest acima identifica o treino.
2. Para cada texto: NFKD, remover U+0300..U+036F, minúsculas e tokens
   `[a-z0-9]+` com pelo menos dois caracteres. Contar presença, não frequência.
3. Para cada classe, calcular por token
   `log((positivos+1)/6) - log((outras_classes+1)/22)`.
   Há quatro casos positivos e vinte de outras classes, com suavização +1.
4. Ordenar por peso descendente e palavra ASCII; reter cinco tokens por
   classe. Gravar contagens e pesos em `regra-lexical-congelada.json`.
5. Para predizer, somar pesos das cinco palavras presentes de cada classe;
   escolher maior soma, com desempate por classe em ordem ASCII.

Parâmetros fixos deste ensaio: presença, cinco palavras por classe, suavização
+1, sem stemming, sem otimização sobre reserved, sem ajustar a regra depois
de conhecer sua pontuação. Não extrair regex manualmente do reservado.

Resultado e matriz serão registrados separadamente após a leitura da regra
congelada. A cascata histórica é outro diagnóstico, pós-hoc; sua queda não
aprova dificuldade, independência semântica ou eficácia de um modelo.
