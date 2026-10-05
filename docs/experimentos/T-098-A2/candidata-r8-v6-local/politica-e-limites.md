# Política e limites — candidata R8 v6 local

## Escopo

Esta candidata é uma correção determinística e local do preflight. Ela não é
nova chamada, rodada externa, holdout cego, adoção, liberação, produção ou
campanha. A autorização local contínua permanece no ledger T-143; ela não é
copiada para o corpus nem ampliada por este selo.

## Preservação verificável

A amostra preserva os 48 textos da R7 v5 byte a byte. A guarda integral exige
que as 48 adjudicações correspondam à R6 v1 em `gold`, `split`, `family`,
`policy_code`, `facts` e `rationale`; exige também igualdade canônica de
`policy_codes`, `taxonomy` e `batches`. Isso impede reanotação local desses
dados, mas não substitui julgamento humano da taxonomia, dos fatos ou do gold.

Os históricos R5, R6 v1-v4 e R7 v5 são apenas lidos e validados por hash. Os
37 textos fora da allowlist histórica continuam protegidos pela linhagem. Y042
permanece com a fronteira discutível já declarada; esta v6 não altera texto,
gold, policy ou rationale.

## Regras lexicais

A regra usa somente `dev` e não calcula métrica em `reserved`. Perfis de
palavra, frase e pontuação são verificações locais de padrões históricos
específicos. Passar nelas não prova ausência de outros atalhos, qualidade,
efetividade, causalidade, generalização ou resultado em holdout.

## Limites operacionais

Não há inferência, cliente de modelo, SDK, HTTP, rede, autenticação, login,
retry, score, campanha, envio, integração, bump, commit, push, publicação,
instalação ou restart. O estado permanece `local_exploratory_not_campaign` e
não constitui GO ou autorização de próxima etapa.
