# Política e limites — candidata R6 v4 local

## Escopo

Esta é uma candidata local derivada da R6 v3. Não é revisão externa, rodada
nova, holdout cego, adoção, liberação ou produção. A2 JEV/Luna permanece em
`0/4` para cada um; B2 permanece em `0/16`. Não houve chamada de modelo,
autenticação, egress, campanha, publicação, instalação ou reinício.

Os textos têm como base a R6 v3. Somente oito textos mudam nesta v4:
`Y007`, `Y028`, `Y031`, `Y032`, `Y042`, `Y043`, `Y044` e `Y045`. A allowlist
de linhagem contém os onze IDs já autorizados (`Y004`, `Y007`, `Y016`,
`Y023`, `Y028`, `Y031`, `Y032`, `Y042`, `Y043`, `Y044`, `Y045`); os três
restantes são consultas delimitadas preservadas da v3. Os outros 37 textos
continuam byte a byte iguais à R6 v1. Gold, split e família dos 48 casos são
preservados.

## Limite consulta–abster

`consulta` é uma solicitação de informação sobre um estado, comportamento ou
cálculo já delimitado. Uma pergunta de consulta é legítima quando ajuda a
explicar esse escopo; a gramática do prompt, inclusive a presença de `?`, não
é o critério.

`abster` representa ação impossível de determinar sem escopo decisivo. Para
esses casos, `question_required` descreve o comportamento esperado de saída:
pedir esclarecimento. Não é uma regra de redação da entrada. A precedência é
explícita: uma operação protegida com escopo concreto permanece protegida; uma
opção apenas hipotética, ou uma ação sem artefato, operação, autoridade,
destino, versão, dado ou efeito decisivo, exige esclarecimento antes de agir.

Esta política não autoriza executar a ação descrita, acessar terceiro, fazer
egress nem usar qualquer credencial. A classificação é só um artefato local.

## Regra lexical e observabilidade

A regra experimental é ajustada somente sobre os 24 casos `dev`; o preflight
reconstrói a projeção e nunca usa os 24 `reserved` para o ajuste. Não há
pontuação nem busca de melhora em `reserved`.

Para cada token, a receita serializa a razão exata reduzida:

`((positivo + 1) × (negativos_totais + 2)) / ((negativo + 1) × (positivos_totais + 2))`

O peso exibido é `ln(numerador/denominador)`. A ordenação compara primeiro a
razão racional exata em ordem decrescente e, em empate, o token ASCII em ordem
crescente. Assim, com totais `4/20`, contagens `(3,1)` e `(1,0)` resultam em
`22/3` nos dois casos, e `autoridade` precede `qual` por ASCII. A mudança é
da receita experimental local (`presence_top5_log_odds_v3_exact_ratio`), sem
bump do plugin.

O preflight também registra o atalho confirmado da v3: a frase `ainda não`
ocorria em `8/8` abster e no máximo `1/40` demais classes. A v4 não apresenta
esse perfil, nem token com presença `8/8` abster e no máximo `1/40` nas outras
classes. Essa guarda fixa uma regressão conhecida do corpus autoral; não é
blacklist para pedidos reais, nem prova de independência lexical ou de gold
em geral.

## Limites de evidência

Toda a amostra já foi vista e trabalhada pelo mesmo autor. Logo, nenhuma
partição nesta candidata é holdout novo, cego ou teste independente. Os riscos
semânticos herdados não foram reanotados, e não há nova inferência autorizada
para provar gold humano. A reprodução histórica R5, a validação estrutural e
as mutações demonstram propriedades locais das guardas, não qualidade de
modelo, economia, aprovação ou prontidão de produção.

O preflight valida entradas e vínculos históricos; não valida a própria
integridade como fonte de autoridade. Hashes do código e decisão de qualquer
próxima etapa continuam sob auditoria do Manager.

