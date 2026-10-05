# Recibo de congelamento — R6 v3 local

Data: 2026-10-04  
Candidata: `T-098-A2-R6-v3-local`  
Estado: snapshot local; não aprovado, não enviado e sem score.

Este recibo sela as nove fontes da v3. Ele não inclui o próprio recibo para
evitar hash autorreferente. Alterar qualquer fonte exige outra candidata e
outro recibo; R5, R6 v1 e R6 v2 permanecem imutáveis.

| Arquivo | SHA-256 |
| --- | --- |
| `amostra.json` | `c72e66afad83cf36577509c3d62723bd677f42b17f188d46f7520ee0654522b9` |
| `evidencias-bancada-local.md` | `db013beb2849870d758547374282a1da6434f438e234a0003bd4ddc5c3c750fb` |
| `manifesto.json` | `41a53ca31bac12b6de9b0cbac70ddd5112ced501ea44ded01623ef78ef0ef08c` |
| `politica-e-limites.md` | `91df30957f0945ace9d3e5fead4822524996c90529f3984bf91c83ee1e7ad2ad` |
| `preflight.py` | `a9f8a7ba238f69a1e305a13c0485b2076eb6c515f8f2b79c19aecacf2273d013` |
| `regra-lexical-dev.json` | `35ea7d20548104ba04ac6cf1ed2e982b5f95c6ca3d0507cbbca606c474b5d3c6` |
| `test_mutations.py` | `af278373641dff69f68149e17b91c71914af239d92b01b69633249c5e1b347d7` |
| `test_preflight.py` | `716b271fad4c4777062305395599eba0b41d6db5aef998068d4e6b07d510c5ad` |
| `test_semantic_red.py` | `0ed08eaacb6df17ac95ea7e7c226e3c95a3bb279fa9d77af788ab44586c8a331` |

O preflight também confere 14 fontes R5, 9 fontes R6 v1 e 10 fontes R6 v2.
O recibo não equivale a holdout, revisão externa, aprovação, release ou
produção.

