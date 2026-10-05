# Recibo de congelamento — R7 v5 local

Data: 2026-10-04  
Escopo: candidata local pós-R7 do T-098; sem efeito externo.

## Fonte e preservação

A v5 deriva da amostra R6 v4
(`f1f9e950d16b4ddfea14ae96ac907996045025e726405551c530ab29edc4f9fe`).
Ela altera somente `Y007`, `Y031`, `Y042` e `Y045` em relação à v4. A
allowlist permanece com onze IDs e os outros 37 textos continuam byte a byte
iguais à v1.

O preflight passa a comparar gold, split e família de todos os 48 IDs com o
manifesto v1 selado. O inventário R5 fica ancorado por
`acd783acf6df30fffbb91a068b7da8530c72626228993c086374d19a1d4a8c50`;
os mapas históricos revalidam 14 fontes R5, 9 v1, 10 v2, 10 v3 e 10 v4.
Nenhuma fonte histórica foi regravada.

## Arquivos selados desta v5

| SHA-256 | Arquivo |
| --- | --- |
| `646b985babd4f14c0545bd21060698315502bff78b8a936e5cba09617608b491` | `amostra.json` |
| `fc908527d138274f44958b9da8038b3a5956262b4bb8eff76516b6ca3657cac5` | `evidencias-bancada-local.md` |
| `6dff3fc9ea46dd2c47d68081067560882b633ba83c3c54392f9d9bfbb47454bb` | `manifesto.json` |
| `1d6402007d32fdbbda149467c10ffeb0cfac6c5b5324e68675ae301923578814` | `oraculo-adjudicacao-red-green.py` |
| `703606ae0f46491b65ccae5354a81fbc5047ca907bfea7d6f1f65fcda57712f2` | `oraculo-red-green.py` |
| `6388c83d5ac0e51b1c4207329bae8404f0076cd72f4717128c08404d4fff9805` | `politica-e-limites.md` |
| `bbb23aaa09b8a93a528c1c117633c05722f6c854cc10b5e46087d6355693f635` | `preflight.py` |
| `63f5433b75a02dd90e57bcc976b7f718a91d807b1eeb7f756ca74dc748d0a4fb` | `regra-lexical-dev.json` |
| `9699db9afd5e47141d56f109b8425b335fcc025eaa67c4fe6d72230bd0fd78b8` | `test_mutations.py` |
| `88ac047921b1d7b438569f6cd9be640619168a81646e8b64e2fa2df9a54cfcf1` | `test_preflight.py` |

Este recibo não sela a si próprio. O JSON externo de evidências inclui o mapa
final da v5, inclusive este recibo, sem reescrever snapshots anteriores.

## Limites

O recibo identifica uma candidata local, não GO, holdout, aprovação
independente, adoção, release, economia ou produção. A regra foi ajustada só
em dev; não há score em reserved, inferência, chamada A2/B2, egress ou ação.

