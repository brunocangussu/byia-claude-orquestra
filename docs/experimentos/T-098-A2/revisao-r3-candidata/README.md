# T-098 A2 — pacote candidato da revisão R3

Estado: **revisão única concluída; NO-GO auditado**. O corpo do parecer é
`BLOCKED`; a resposta cercada por Markdown viola o JSON puro exigido. Não é
payload de classificação nem congelamento final da campanha.

`pacote.txt` contém 16.115 bytes UTF-8, abaixo do teto de 16.384 bytes do runner.
SHA-256: `a1500809c056cebdbee2953b38211fe20d33f81c0331155fdf9d287fdb1fdcf6`.
`inventario.json` vincula o pacote às fontes e registra **1/1 chamadas concluídas**,
sem retry do orquestrador. Destino: Anthropic pela Claude CLI; `modelUsage`
registrou exatamente `claude-opus-5-5`. Recibo, resposta, contrato da chamada
e auditoria estão neste diretório; modelo registrado não é prova independente
do backend nem aprovação da campanha.

## Conteúdo e integridade

Inclui os 48 casos completos: `id`, `text`, `gold`, `reason`, `family` e `split`.
O nome de família é codificado por índice em um dicionário reversível, sem abreviar
texto ou justificativa. A recomposição local dos arquivos persistidos reproduziu
exatamente esses seis campos da amostra candidata. A amostra permanece intacta.

O pacote leva as instruções do reviewer anteriores à seção de montagem do
briefing, e toda a rubrica normativa: objetivo, seis classes, regras de risco,
desambiguação e separação entre classificação e autorização de execução.
Omite somente as seções posteriores de metodologia, execução e custo; seus
documentos completos continuam nas fontes vinculadas pelo inventário.

Não inclui resultados dos classificadores, credenciais, caminhos pessoais ou
dados reais de pessoas. Os casos são fictícios. A revisão é independente do
autor, mas **não cega**: o autor conhece as duas partições e o reviewer recebe o
gabarito proposto. Não usar esse desenho para alegar validação cega.

## Gate recebido e consumido

O dono autorizou os bytes deste pacote e uma única chamada, sem retry, nesta
conversa. A chamada foi concluída uma vez, depois de reconferir hashes/tamanho,
via, versão e contrato de isolamento/autenticação. Houve uma autenticação
autorizada pela assinatura, sem token manual, API key, `--bare` ou bypass de
permissões. A análise da via e os limites
do custo estão em `../diagnostico-custo-cli-r3.md`; o tamanho do pacote não é um
teto de tokens totais nem promessa de preço da inferência.

O parecer deve ser JSON puro com `verdict`, `reviewed_count: 48`, `issues` e
`limitations`, conforme as instruções incluídas. Aprovação exige os 48 casos
avaliados, sem conflito substantivo de rubrica, gabarito ou partição. Saída
parcial, erro, recusa ou formato divergente não libera a campanha; preservar
recibo e resposta, sem repetir a chamada.

Somente após revisão aprovada e auditoria do Manager podem ser preparados os
payloads finais por allowlist `id`/`text`. Inferências JEV/Luna, B2, ativação do
roteador e adoção no Orca continuam em gates próprios. Esta preparação não
comprova assertividade, economia ou qualidade de entrega.

## Histórico de acesso e próximo passo

Em 2026-09-29, consultas de status da Claude CLI nesta sessão Codex indicaram
autenticação indisponível, inclusive na execução direta fora do context-mode.
Evidência sanitizada em `../preflight-cli-status-local.json`. Isso não prova
logout no terminal do dono nem a causa da indisponibilidade. Após o gate do dono
e a confirmação no navegador, a única autenticação terminou com exit 0; status
normal e seguro confirmaram `loggedIn=true`, `authMethod=claude.ai`.

O pacote e a amostra permanecem íntegros. `auditoria.md` confirma problemas de
partição, atalhos lexicais e ambiguidade; a campanha continua bloqueada. Próximo
passo proposto: nova candidata corrigida **localmente**, sem classificações ou
novo envio automático. Não repetir login/review nem generalizar a prova para
outros chats. JEV/Luna A2 seguem 0/4 cada; B2 0/16.
