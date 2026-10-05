# T-098 A2 — recibo de congelamento local R6

Este recibo descreve a candidata R6 local após a derivação determinística da regra. Não é recibo de campanha, execução externa, inferência, revisão independente ou publicação.

| Artefato | SHA-256 |
|---|---|
| `amostra.json` | `db8ff9a874315012a9799c7794a741bc39270e30303df506cc7210c3fdae55ed` |
| `manifesto.json` | `39868f71f5f4210c0ee3320165e014fc1e0f0ab2ba5a77b00460618556dba23c` |
| `regra-lexical-dev.json` | `4178d93a8f1a7c0cd91a7c13c88df1dff106c97387913c75745c12e5713b6653` |

A amostra tem 48 textos sintéticos. O manifesto contém o selo UTF-8 de cada texto, a versão autoritativa, os lotes, a política de adjudicação e os 14 hashes históricos R4/R5. O preflight valida esses controles separadamente do digest geral e recomputa a regra a partir de `dev`.

A receita é: ordenar `dev` por ID; NFKD; remover acentos; presença por documento; tokens ASCII com dois ou mais caracteres; suavização 1; log-odds; top-5; desempate por peso descendente e token ASCII. Não há fit, predição ou métrica nova sobre `reserved`.

O snapshot não valida a semântica humana dos golds. A política local torna divergências de classe, família, split, pergunta obrigatória e fronteira de projeção detectáveis, mas não substitui revisão independente.
