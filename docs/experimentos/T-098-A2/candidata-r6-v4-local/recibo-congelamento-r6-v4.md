# Recibo de congelamento — R6 v4 local

Data: 2026-10-04  
Escopo: candidata local pós-R6 do T-098; nenhum efeito externo.

## Fonte e preservação

A v4 deriva da amostra R6 v3
(`c72e66afad83cf36577509c3d62723bd677f42b17f188d46f7520ee0654522b9`).
Mudam somente `Y007`, `Y028`, `Y031`, `Y032`, `Y042`, `Y043`,
`Y044` e `Y045`; a allowlist de linhagem continua contendo os onze IDs
autorizados. Os 37 textos fora dela, e gold/split/família dos 48 IDs, são
revalidados pelo preflight contra a R6 v1.

O inventário R5 é lido exclusivamente no caminho relativo à raiz do projeto
`docs/reviews/T-098-r5-gold-preparacao-local/inventario.json`, com SHA-256
`acd783acf6df30fffbb91a068b7da8530c72626228993c086374d19a1d4a8c50`.
Ele ancora 14 fontes; os mapas das R6 v1, v2 e v3 ancoram respectivamente 9,
10 e 10 fontes. Nada desses snapshots foi regravado.

## Arquivos selados desta v4

| SHA-256 | Arquivo |
| --- | --- |
| `f1f9e950d16b4ddfea14ae96ac907996045025e726405551c530ab29edc4f9fe` | `amostra.json` |
| `d7f7d6ae3aa1699c1ed4d1d9798c59691e065ce7fa116f49fe04b285ab27ba97` | `evidencias-bancada-local.md` |
| `99f2aa2286d73b8641f331b933b2e288e3d24716b01b4ec67986888ae3ebb65a` | `manifesto.json` |
| `703606ae0f46491b65ccae5354a81fbc5047ca907bfea7d6f1f65fcda57712f2` | `oraculo-red-green.py` |
| `8a789da61fa17806d2c5593accc8a8aa4709d64be221463888e17d8166de23ee` | `politica-e-limites.md` |
| `5197d1efd892f363a702990524bc720102d0dfac18139133b53a7102fb6b8a8f` | `preflight.py` |
| `9cc679299fd3ef02d578977bd922f7b3deac85e550853051eac18016e64ca6c8` | `regra-lexical-dev.json` |
| `c0007b3b938133cf7ed83e5ba32a26646383f1cdbffd88951d2742c574b8da53` | `test_mutations.py` |
| `444cfedf0de56661f3c94ea851bb3fa538795fb3331afeb8e965f3c405d4b83b` | `test_preflight.py` |

Este recibo não sela a si próprio. O JSON de evidências e hashes do lote
registra o mapa final, inclusive este recibo, sem reescrever snapshots
anteriores.

## Limites

O congelamento só identifica uma candidata local. Não é GO, aprovação
independente, score, holdout, adoção, release ou autorização de ação. Não houve
chamada A2/B2, e a regra lexical permaneceu ajustada exclusivamente em dev.

