# T-098 — dry-run local do contrato JEV

Data: 2026-09-29. **Análise efêmera, não runner de produção nem inferência.**
Contrato conferido no exemplo Choice da [API oficial](https://docs.typesafe.ai/api).

A candidata R3 mantém SHA-256
`8cc2e3b5225cb59fa869de66b466912fb607781d6ba587761e874492f7f987e1`.
Os 48 casos foram projetados em memória somente pelos campos `id`/`text`;
`gold`, `reason`, `family` e `split` não entram nessa projeção. Não foi criado
payload final, nem o gabarito foi alterado/aprovado.

## Controles observados

Um objeto de resposta inteiramente fictício, com todos os IDs e Choice,
passou nas assertions. Quinze alterações foram recusadas:

- Modelo mutável/diferente, ID ausente ou extra.
- Tipo diferente de Choice ou classe desconhecida.
- Probabilidade ausente/extra, NaN, negativa, acima de um ou soma incorreta.
- Confidence infinita ou fora de faixa.
- Uso ausente ou tokens com tipo inválido.

O controle escolheu `abster` em todos os IDs; não usou o gabarito e não foi
pontuado como classificador. Probabilidades normalizadas com tolerância
numérica de 1e-6. Confidence foi checada como número finito entre zero e um;
não houve teste de calibração ou relação estatística com probabilidades.

## Limites

Esses controles exercitam uma proposta de contrato em JavaScript no sandbox
local de análise. Não são testes de um adaptador instalado, nem comprovam
compatibilidade comportamental da API real, qualidade, economia ou autoridade
do JEV. O validador persistente/transportador deve repetir esses controles
quando seu escopo estiver aprovado; esta etapa não os implementa no produto.

Zero chamadas de rede/modelo, leituras de credencial, retries, payloads finais
congelados ou ações de release. A2 continua JEV 0/4, Luna 0/4. Próxima etapa:
revisão independente do gabarito antes de congelar e medir a classificação.
