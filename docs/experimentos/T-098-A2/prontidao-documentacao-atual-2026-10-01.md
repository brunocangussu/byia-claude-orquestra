# T-098 — prontidão e contrato público atual do JEV

Consulta em 2026-10-01, sem inferência, acesso à chave ou requisição autenticada.
Esta nota complementa o protocolo: não aprova o gabarito, altera a rubrica,
congela payload final, implementa transportador ou ativa roteamento.

## Modelo, preço e limites atuais

A [página oficial de modelos](https://docs.typesafe.ai/models) lista
`jev-1.13.0`, preço **US$ 0,042 por milhão de tokens de entrada** e saída
gratuita. Confirma endpoint `POST /v1/systemone`, orçamento de contexto 64k
para state + todas as perguntas e 32k para state + a maior pergunta. State é
ingerido uma vez; perguntas são avaliadas separadamente contra ele.
Rate limits são dinâmicos. SDKs repetem com backoff por padrão; nosso protocolo
continua HTTP direto, sem SDK, retry, redirects ou proxies herdados.

Para o cenário teórico de quatro requisições no limite de contexto, usando
65.536 tokens por requisição como interpretação conservadora de 64k:

`4 × 65.536 × US$ 0,042 / 1.000.000 = US$ 0,011010048`.

Esse cenário fica abaixo dos US$ 0,02 propostos para JEV A2, mas **não é teto
de cobrança garantido nem tokenização medida dos payloads**. O recibo real de
uso, a disponibilidade da conta e a vigência do preço precisam ser conferidos
antes/depois da campanha. Não multiplicar o state arbitrariamente por pergunta
nem apresentar cobrança/cota de assinatura de LLM como custo equivalente.

## Vínculo de pergunta e caso: requisito concreto da montagem futura

A [API oficial](https://docs.typesafe.ai/api) informa que a chave da pergunta
não é enviada ao modelo nem usada na inferência. Portanto, `questions.Y001`
não instrui por si só qual pedido avaliar. A pergunta precisa apontar
explicitamente ao pedido Y001 em `state`, ou conter o pedido-alvo em seu
campo `instructions`, sem depender da chave de transporte.

O esquema Choice exige `criteria` como mapa de opção para descrição, não
lista arbitrária; a resposta inclui choice, probabilities e confidence.
A [especificação pública](https://api.typesafe.ai/openapi.json) confirma os
campos e GET /v1/models autenticado para catálogo por conta. Este catálogo
autenticado não foi consultado: documentação pública não prova acesso da conta.

Inspeção graph-first da candidata R4: `classifier_batches()` em
`candidata-r4/preflight.py:68` valida a amostra e projeta quatro lotes id/text.
Não monta `questions` HTTP; **não há bug de transportador demonstrado** nessa
função. A futura montagem/validação persistente deve cobrir o vínculo explícito
e sua mutação antes da inferência. O dry-run antigo é prova efêmera do contrato,
não adaptador instalado ou autorização para implementá-lo fora do plano.

Gabarito, reason, family, split, resultado de concorrente e métricas nunca
entram no material do classificador. Não ajustar consumidor/regra após abrir
respostas reservadas. Probabilidades/confidence não concedem autoridade sobre
gates, permissões ou mudanças de risco; o Manager mantém esse controle.

## O que falta para usar — sem confundir preparação com adoção

| Etapa | Evidência atual | Gate restante |
|---|---|---|
| Acesso ao revisor Claude CLI | Status novo false/none; app vivo não foi inspecionado | Uma autenticação suportada da CLI, só status persistente depois |
| Revisão independente do T-098 R4 | Pacote intacto, 51.176 bytes; 0/1 enviada | Acesso comprovado e retomada expressa da revisão |
| Consumidores A2 | Quatro lotes id/text no dry-run, 14 testes/oito mutações verdes na execução anterior | Gabarito aprovado; congelar montagem/validador, versões e estimativa |
| Comparação | JEV 0/4, Luna 0/4 | Gate de oito chamadas, sem retry, com rubrica/payloads aprovados |
| Adoção na Orquestra | Nenhum ganho/segurança de produção demonstrado | Auditar resultados e obter gate explícito de adoção |

[Jev com coding agents](https://docs.typesafe.ai/introduction/coding-agents)
confirma o desenho proposto: componente de decisão/classificação dentro do
fluxo, não substituto do LLM que escreve código. Não instalar skill adicional,
SDK ou outro Manager por causa dessa orientação.

## Retomada e auditoria da meta

As três etapas consecutivas mantiveram o mesmo bloqueio de acesso às revisões:
prova sintética falhou; diagnóstico encontrou status sem login; a continuação
reconfirmou false/none. Houve progresso local real (recibos, pacote novo,
verificações e esta consulta), mas isso não liberou revisão ou benchmark.
Nenhum processo de login/revisão foi iniciado nesta preparação; não é espera
de job vivo nem motivo para reenviar uma chamada consumida.

O protocolo operacional diz expressamente que indisponibilidade não autoriza
login, upgrade ou restart. Preparação segura disponível nesta etapa encerrada;
próxima ação necessária altera autenticação e exige autoridade específica.
Não substituir reviewer, aprovar por omissão, iniciar classificações sem
gabarito validado ou perpetuar atualizações de status como progresso.
Preservar a meta completa: o JEV **ainda não está pronto para adoção**.

Sem alteração de produto, código, dados/gabarito, credenciais, elenco ativo,
branch Claude, bump, commit, push, integração, instalação ou restart.
