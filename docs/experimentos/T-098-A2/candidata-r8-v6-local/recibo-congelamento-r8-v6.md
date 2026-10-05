# Recibo de congelamento — R8 v6 local

Data: 2026-10-04
Escopo: candidata local pós-R8 do T-098; sem efeito externo.

## Fonte e preservação

A v6 parte da R7 v5 sem alterar `amostra.json`: os 48 textos são byte a byte
idênticos. As 48 adjudicações são comparadas integralmente com a fonte R6 v1
ancorada, incluindo `gold`, `split`, `family`, `policy_code`, `facts` e
`rationale`; `policy_codes`, `taxonomy` e `batches` também são fixados contra
essa fonte. Os históricos R5, R6 v1-v4 e R7 v5 são revalidados, sem regravar
arquivos, hashes, recibos ou pacotes anteriores.

## Selo local

O manifesto declara `selo-congelamento-r8-v6.json`, que lista SHA-256 do
runtime, dos três módulos `test_*.py`, dos oráculos e da documentação v6. O
selo verifica os próprios alvos durante o preflight e exclui somente a si
mesmo, evitando digest circular. Este recibo é um dos alvos selados.

O selo é evidência de integridade local: não é autoautorização, aprovação
independente, GO, holdout, adoção, release, economia, produção ou campanha.

## Limites

As regressões RED/GREEN e mutantes demonstram apenas as guardas descritas.
Contagens lexicais ou de pontuação não provam qualidade, ausência de atalho ou
generalização. Não há score, ajuste no `reserved`, inferência, chamada A2/B2,
rede, login, retry ou ação externa.
