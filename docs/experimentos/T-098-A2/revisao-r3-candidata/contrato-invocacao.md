# Contrato local das revisões autorizadas

O dono autorizou o pacote R3 T-098 de 16.115 bytes e os cinco lotes R2 T-131,
71.005 bytes. Uma execução CLI por pacote, sem retry do orquestrador; nenhuma
chamada sintética adicional. Código e instruções sanitizados vão à Anthropic.

Uma única autenticação `claude auth login --claudeai` terminou com exit 0.
Consultas normais e em modo seguro confirmaram `loggedIn=true` e
`authMethod=claude.ai`. Não houve logout, token manual ou API key. A causa do
estado anterior indisponível não foi demonstrada.

## Via e isolamento por chamada

- Executável: Claude CLI 2.1.280, instalação local nativa.
- Runner: candidato T-131, SHA-256
  `d0faf940ec051e094db8531ea245a7d02c170081a04ff7796dd420cd42cb7738`.
  Uso local como executor de revisão não significa instalação ou adoção.
- Modelo solicitado: `claude-opus-5-5`; aprovação exige identidade exata
  observada no `modelUsage`, não somente o nome pedido.
- Diretório vazio: `/private/tmp/orq-review-cli.n9YIQ9`.
- Argumentos do runner preservados: `-p`, modelo explícito,
  `--permission-mode plan`, `--tools ""`, `--setting-sources ""`,
  `--disable-slash-commands`, `--no-session-persistence`, JSON de saída.
- Adição explícita apenas no envelope desta execução: `--safe-mode`.
  O help local diz que desabilita CLAUDE.md, plugins, hooks, skills e MCP,
  preservando autenticação. Políticas administradas podem continuar presentes.
  Não usar `--bare` nem contorno de permissões.
- Um envelope transitório em memória observa a chamada do runner, adiciona
  esse argumento e coleta metadados de uso. Não altera o arquivo do runner,
  a configuração global, o payload congelado ou o ambiente de outra sessão.
- Sem overrides de provider/credencial na allowlist inspecionada. Somente
  `CLAUDE_BIN` identifica o executável local; nenhum valor de credencial é
  copiado ou registrado.

## Recibos e aceitação

Persistir hash/bytes do pacote, argumentos, runner, início/fim, exit,
modelo solicitado/observado, uso/cache, custo de tabela, sessão e resposta.
Custo reportado não comprova cobrança monetária na assinatura. Sem retry
do orquestrador não demonstra quantos retries internos de transporte a CLI
eventualmente fez; não afirmar essa telemetria ausente.

Erro de autenticação, capacidade ou modelo interrompe os pacotes restantes
que dependam da mesma capacidade, preservando o diagnóstico. Parecer BLOCKED
ou erro de formato não é aprovação; não repetir o mesmo pacote. Uma falha
substantiva do JEV não substitui a revisão independente do T-131.

T-089 permanece intacto. O handoff informou NO-GO da revisão e correções
posteriores sem re-revisão: não declarar o snapshot final aprovado nem
integrar como consequência destas seis chamadas. Sem commit, push, bump,
integração, publicação, instalação ou restart.
