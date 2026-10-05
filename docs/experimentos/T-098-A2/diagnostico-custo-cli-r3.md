# T-098 A2 — diagnóstico local de custo e contexto da Claude CLI

Estado: **evidência histórica analisada; causa do aumento ainda não provada**.
Nenhuma inferência, retry, reautenticação ou alteração do runner foi feita nesta
auditoria. As únicas execuções novas foram consultas locais `--help`/`--version`.

## Diferença observada

Fontes: `revisao-recibo.json` (R1) e `revisao-r2-recibo.json` (R2).

| Medida | R1 | R2 |
|---|---:|---:|
| Bytes do pedido | 9.723 | 10.046 |
| Entrada sem cache | 2 | 2 |
| Entrada de criação de cache | 7.731 | 193.823 |
| Entrada de leitura de cache | 531 | 0 |
| Entrada total | 8.264 | 193.825 |
| Saída total | 4.825 | 4.288 |
| Custo de tabela reportado, US$ | 0,1584622 | 1,636352 |

Entrada total soma entrada sem cache, criação e leitura de cache. Thinking é
parte da saída reportada, não uma parcela adicional para somar novamente.
Os valores de tabela não demonstram cobrança monetária na assinatura.

O pedido cresceu 3,322%; a entrada total foi 23,454 vezes maior e o custo de
tabela 10,326 vezes maior. Portanto, **não atribuir o aumento somente aos
bytes do briefing**. Os recibos não identificam a origem de toda essa entrada.

## Limites da investigação

O runner da fonte principal envia o briefing por stdin, sem `cwd` ou `env`
explícitos no `subprocess.run`; herda o contexto do chamador. Seus argumentos
incluem `--permission-mode plan`, `--tools ""`, `--setting-sources ""`,
`--disable-slash-commands`, `--no-session-persistence` e JSON de saída. Não
incluem `--safe-mode` nem `--bare`. Isso descreve o código, não prova qual
customização entrou especificamente na R2.

A busca restrita aos dois UUIDs dos recibos não encontrou arquivos de sessão
em `~/.claude/projects`. O runner desabilita persistência; ausência de log não
prova ausência de contexto injetado nem falha de autenticação. Não houve leitura
de outros históricos de projetos ou conteúdo pessoal.

A inspeção local atual encontrou zero nomes na allowlist de variáveis de modo,
provider/proxy Anthropic; valores não foram consultados nem expostos. Esse
resultado é do subprocesso atual, não reconstrói o ambiente histórico da R2 e
não caracteriza todas as janelas do dono.

## Modo CLI não é login

Versões observadas em consultas locais: Claude CLI **2.1.280** e Codex CLI
**0.159.0**. Nenhuma atualização foi executada.

O help local e a [referência oficial da Claude CLI](https://code.claude.com/docs/en/cli-reference)
distinguem:

- `--bare`: não lê OAuth nem Keychain; autenticação Anthropic depende de API key
  ou `apiKeyHelper`. É incompatível com a via CLI/OAuth exigida pelo dono para
  este ensaio. Não usar nem pedir token manual para contornar essa diferença.
- `--safe-mode`: desabilita customizações e mantém autenticação, seleção de
  modelo e permissões; políticas administradas ainda se aplicam. É apenas uma
  **candidata a perfil diagnóstico por chamada**, sem prova comportamental
  real deste piloto. Ferramentas internas continuam sendo uma capacidade
  separada; o modo não substitui `--tools ""` nem os gates de revisão.

Não concluir que o login caiu, que `--bare` causou a anomalia histórica, ou que
`--safe-mode` já resolveu o custo. Não mudar flags, ambiente global, config ou
autenticação para executar o pacote sem o contrato correspondente.

## Próxima coleta delimitada

Antes de qualquer nova chamada autorizada, a proposta de invocação deve fixar
via, flags, diretório e nomes de variáveis relevantes, sem valores sensíveis.
Registrar versão, hash e bytes do pedido, uso/cache, modelo solicitado e
observado, custo de tabela, erro e número de chamadas no recibo. Se o isolamento
exigir alterar o runner canônico, planejar/revisar essa alteração antes de usar,
sem improvisar outro comando ou ativar um modo global.

O pacote R3 pronto localmente tem 16.115 bytes. Isso só comprova seu teto de
entrada literal no runner; não limita contexto adicional nem preço total.
Sem nova autorização delimitada, continuar apenas a preparação local, sem
inferência exploratória, retry ou envio ao Anthropic.

## Preflight de status atual — 2026-09-29

`preflight-cli-status-local.json` registra quatro consultas de status, **zero
inferências**. No context-mode, `claude auth status` e
`claude --safe-mode auth status` retornaram JSON válido, exit 1,
`loggedIn=false`, `authMethod=none`, sem stderr nem timeout.

A comparação direta por `exec_command` também retornou esse estado; uma
consulta adicional no context-mode confirmou o mesmo fingerprint do diretório
de configuração do modo normal, sem `CLAUDE_CONFIG_DIR` sobrescrito. A versão
direta é 2.1.280. Portanto, a evidência não sustenta atribuir a indisponibilidade
apenas ao subprocesso do context-mode ou apenas ao `--safe-mode`.

Não foi verificado o terminal interativo do dono nem o login de sessões Claude
vivas. Não atribuir causa a expiração, Keychain ou logout: a evidência prova só
o status destas execuções. Não foram registrados e-mail, identidade de conta,
tokens ou valores de credenciais. Não houve login, logout ou mudança de config.

O preflight de envio não está liberado, mesmo que os bytes da revisão sejam
autorizados: o acesso CLI precisa ser resolvido sem reautenticação implícita,
API key/token manual ou substituição de vendor. Esta checagem não resolve o
aumento histórico de custo e não consome nem autoriza uma revisão de modelo.
