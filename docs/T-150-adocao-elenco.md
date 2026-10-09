# T-150 — adoção Codex entregue na fonte da raiz principal

**Estado atual, 08/10:** oito papéis comprovados e integrados na fonte 0.32.0;
R3 APROVADO_COM_RESSALVAS auditada, sem bloqueadores. O dono autorizou entrega
Git allowlistada e integração do T-150, registrada na thread dona. A fonte
`3cfac62` está na main e no GitHub; publicação, instalação e ativação de chats não estão
cobertas. As seções de preflight abaixo preservam os marcos históricos.

Fonte: fábrica do pacote carregado 0.31.0, digest canônico
`5996dab63533113049c15ee6778110b4b99a9248ed3b6f3beebc1b0221d70bd3`.
O elenco anterior da raiz principal ficou preservado no histórico e nos
checkpoints locais; seu SHA-256 era
`af55312bf6c2419e48c4697fde3207c55ec20e11624109fa7bff57fa8b0e7f60`.
O Host Claude, Manager, presets, desvios fora das oito linhas-alvo e vias
desligadas não foram alterados. As oito linhas e referências operacionais Codex foram aplicadas
inicialmente na worktree T-150, após prova contextual completa em 2026-10-07,
e entregues à raiz principal por fast-forward autorizado. A promoção altera
apenas notas de estado: os oito modelos/efforts/vias são os mesmos da R3.
Este registro é evidência de adoção na fonte, não outro catálogo nem ativação.

| Papel Codex | Projeção da fábrica |
|---|---|
| planner·interface | Opus 5.5 `high`, via Claude CLI |
| planner·sistema | Sol 6.1 `xhigh`, via Codex comprovada |
| implementer·leve | Luna 6 `medium`, workspace-write |
| implementer·normal | Sol 6.1 `high`, workspace-write |
| implementer·pesada | Sol 6.1 `xhigh`, workspace-write |
| reviewer | Opus 5.5 `high`, via Claude CLI sem ferramentas |
| docs | Luna 6 `low`, workspace-write |
| scout | Luna 6 `medium`, read-only |

## Resultado do preflight inicial — histórico

`preview_adoption` foi executado sem recibos autodeclarados ou contexto
fabricado: `needs-proof`, proposta `null`, oito papéis pendentes.
Isso não prova que os modelos estejam indisponíveis: prova que ainda não
há uma projeção auditada completa com identidade de conta, cliente,
via, sandbox, modelo e effort compatíveis neste contexto.

Há evidência real aproveitável no T-149 R2: Opus 5.5 observado em
`modelUsage`, `high` solicitado/enviado, processo exit 0, sem ferramentas.
Effort no servidor não foi observado; não o inventar. O recibo não traz
uma identidade contextual completa que possa ser simplesmente copiada
para os dois papéis novos. As chamadas históricas Astra/Terra ou o
catálogo de modelos do app também não provam capacidade de escrita
dos novos perfis.

Faltam: auditar os recibos existentes no contexto efetivo antes de
decidir quais provas adicionais são realmente necessárias. Não fazer
oito sondas cegas nem repetir prova compatível; nenhuma sonda está
autorizada neste gate. Uma prova read-only não certifica workspace-write.

## Decisão proposta no preflight inicial — histórico

Autorizar apenas as provas ainda ausentes, com modelo/effort/via/sandbox,
conteúdo sintético, limite de chamadas e sem retry registrados.
Quando a projeção completa for `ready`, aplicar somente as oito linhas
Codex e registrar a origem/digest/recibos. Até lá, estacionar adoção e
despachos dependentes, não toda a implementação local T-150.

## Auditoria de evidências existentes — 2026-10-06, 23:12 BRT

Inspeção local, sem chamada a modelo: 247 arquivos documentais/recibos
selecionados em `docs/` e `memory/wiki/threads/`; 11 contêm os IDs novos
OpenAI. Pacotes e lotes de código não foram considerados recibos.

| Evidência real | O que demonstra | Por que não fecha a adoção Codex |
|---|---|---|
| `docs/T-131-sondas-cli-0.156.1.json` | Luna 6 em `low`, resposta exit 0, sem ferramentas; Sol 6 anterior também respondeu | Não cobre Luna `medium`, escrita, Sol 6.1 ou identidade do cliente/contexto atual |
| `docs/reviews/T-149-R2-recibo.json` | Opus 5.5 observado em `modelUsage`, `high` solicitado/enviado, exit 0 | Sem identidade contextual completa para adoção por papel; effort efetivo no servidor não observado |
| `memory/wiki/threads/T-144-mods-claude-code.md` | Reviewer Claude em Sol 6.1 `xhigh`, por Companion, com rollout citado | Via/host diferentes do alvo Codex; leitura/revisão não prova escrita dos implementers |

Nenhum desses recibos pode ser convertido em prova completa inventando
conta, sandbox, papel ou equivalência entre Companion, CLI e chamada nativa.
O resultado permanece `needs-proof`, oito papéis lógicos pendentes; não
significa oito modelos distintos nem indisponibilidade da conta.

Próximo gate proposto: até oito chamadas sintéticas, uma por papel ainda
sem prova compatível, sem retry. Registrar identidade contextual real e
modelo/effort enviado/observado; escrita somente em diretório descartável
isolado, nunca no produto. Se uma prova compatível for localizada antes
do despacho, reduzir o lote; não consumir chamada por obrigação numérica.
Nenhuma dessas chamadas foi feita ou autorizada neste gate local.

## Provas autorizadas e executadas — 2026-10-07

Gate humano conferido na conversa: até oito sondas ainda necessárias, uma por papel, e uma R1 Opus 5.5 high, sem retry. As seis sondas Codex passaram na CLI 0.160.1: Sol 6.1 xhigh/read-only, Luna 6 medium/workspace-write, Sol 6.1 high/workspace-write, Sol 6.1 xhigh/workspace-write, Luna 6 low/workspace-write e Luna 6 medium/read-only. As quatro provas de escrita geraram o arquivo sintético exato no diretório descartável, sem editar o produto.

Modelo, effort e sandbox OpenAI foram observados no `turn_context` do cliente; isso não é medição do modelo interno do servidor. O account context é somente um fingerprint local não sensível, sem login/token. Os recibos reais estão em `docs/reviews/T-150-codex-[1-6]-2026-10-07-recibo.json`.

A sonda planner·interface respondeu por Claude CLI 2.1.290, modelo `claude-opus-5-5` observado em `modelUsage`, high solicitado/enviado e effort no servidor não exposto. OAuth manteve-se autenticado; nenhum login foi executado. Envelope desliga customizações/MCP e ferramentas; cwd vazio antes/depois. Recibo `docs/reviews/T-150-interface-2026-10-07-recibo.json`.

Consumo até este marco: sondas 7/8, R1 1/1 em execução. Oitava sonda não é obrigatória: a chamada R1 pode fornecer prova contextual real do reviewer. `T-150-preview-adocao.py` retorna needs-proof somente para reviewer; nenhum trecho do elenco foi ativado parcialmente. Nem os smokes nem a adoção comprovam qualidade, economia ou ativação de todos os chats.

## Adoção candidata após conclusão das provas — 2026-10-07

R1 terminou com exit 0 e parecer **REPROVADO**. Isso comprova capacidade
contextual do reviewer, não aprovação técnica. Projeção completa `ready`, oito
papéis comprovados, zero papel pendente; sete sondas + uma R1, sem retry.

Aplicado o diff aprovado em `memory/wiki/_elenco.md` somente na worktree
`codex/t150-alinhamento-operacional`, derivado da fábrica 0.31.0, incluindo
modelo **e** effort. Fonte canônica carregada conferida antes da consulta,
com `kanban-status.sh` existente. Prova CLI não autoriza native spawn/Companion.
Não alterei Manager, seção Claude, presets, overrides fora das oito linhas-alvo nem vias desligadas;
a referência `runner-opus` volta a incluir `planner·interface` neste host.
Presets Codex continuam ausentes. Não migrei a main ou outros projetos/chats.

Snapshot anterior recuperável: objeto Git de `memory/wiki/_elenco.md` em
`4cdbcbc9f8a54ea33292bd7cd0407a36f995bb8c`, SHA-256 acima. A reversão exige
intenção do dono e aplicação apenas dos trechos próprios, nunca checkout do
arquivo compartilhado. Arquivo candidato após aplicação:
`d0880c83cdfde9f6a425b951a931038cda477c839d4c1680d7dc5433323c669c`.
Seção Claude preservada byte a byte, SHA-256
`4ab4146e8370d218a005fa4344aa493aa0b9b9e1b83007f8caa15c55515d92ce`.

Effort Anthropic solicitado/enviado `high`; observação no servidor ausente.
Modelo Anthropic observado em `modelUsage`. OpenAI observado em `turn_context`
do cliente. Nenhuma prova de inferência interna, economia ou qualidade geral.
Recebimento da R1 reprovada mantém a revisão independente corretiva pendente.

## Decisões anteriores e autoridade da substituição candidata

As linhas antigas não eram acidente: registravam decisões humanas sobre Astra
nos planners (T-079/T-083), Terra na faixa normal (`2026-08-09`),
três implementers/docs/scout em Terra
(`2026-09-03`) e o reviewer Opus legado (`2026-08-09`). A referência Git acima
preserva exatamente os trechos e justificativas anteriores.

A aprovação local do T-150 cobre avaliar e aplicar a projeção candidata somente
na sua worktree após as provas contextuais. Fonte humana literal e ponteiro
verificável na thread dona `memory/wiki/threads/T-150-alinhamento.md`, seção
“Recuperação e autorização R2”: aprovação da continuidade com as recomendações
e chamada delimitada. Isso **não** é autorização para integrar o novo elenco
na main, ativar chats ou descartar decisões anteriores. A substituição final
das oito linhas ainda depende de review/validação e do gate de entrega/adoção
do dono. Nenhum override adicional ao conjunto-alvo foi descartado.

Os marcos acima são históricos; R2 terminou **REPROVADO** e não é prova de
aprovação do candidato. Sua auditoria em
`docs/reviews/T-150-R2-auditoria-local.md` separa recibos de capacidade de
aceite técnico. Documentos de prova/rollback devem acompanhar o candidato
na futura integração allowlistada; não dependem da permanência do checkout.
