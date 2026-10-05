# Resultado das R4 T-131/T-098 — correção local aprovada; prioridade T-143

Data: 2026-10-02. **Duas R4 autorizadas, executadas e auditadas; 1/1 consumida cada.**

CLI/runner exit 0 nas duas, modelUsage exclusivamente claude-opus-5-5,
ferramentas desabilitadas, JSON e cobertura declarada válidos.
T-131: **NO-GO, dois bloqueadores**. T-098: **NO-GO, três bloqueadores**.
R4 encerradas sem correções/retry. Correção local aprovada depois pelo dono;
ainda não iniciada. Sem nova autenticação, chamada externa ou Git/release.

Auditorias: docs/reviews/T-131-R4-execucao-2026-10-02/auditoria-manager.md
na frente T-131; docs/experimentos/T-098-A2/revisao-r4-execucao-2026-10-02/
auditoria-manager.md na main. Próximo gate: correção delimitada dos achados
confirmados com RED/GREEN/mutações/gates locais. Revisão nova exige autoridade
própria/extensão quando aplicável. A2 JEV/Luna 0/4 cada; B2 0/16.

**Validação local final:** frente T-131 484 testes OK; main 447 testes/uma falha
por varredura de checkout histórico aninhado do Claude. Manifesto/lint/diff-check
exit 0 nos dois checkouts. Falha reproduzida e registrada, sem correção/remoção:
`docs/experimentos/T-098-A2/revisao-r4-execucao-2026-10-02/verificacao-local.md`.

Plano local consolidado: `docs/plano-correcao-local-pos-R4-T-098-T-131.md`.
Plano local aprovado em 2026-10-02; ainda não implementado. Não concede R5 ou classificação.
Prioridade máxima agora: T-143 (continuidade). T-131/T-098 seguem aprovados atrás dela.

## Histórico pré-envio — não reutilizar os gates consumidos

T-131 R3: 1/1 tentativa consumida, falhou sem parecer (CLI 1 / runner 5).
T-098 R4: 0/1, despacho suspenso. A autorização da R3 registrada abaixo é histórica:
não repetir ou reenviar com ele. A correção local do diagnóstico foi autorizada
e concluída na frente T-131: 484 testes, 16 novos, 10 mutações, manifesto e lint
verdes. Wrapper completo com CLI falsa comprovado; nenhum modelo foi chamado.
Runner novo SHA `7c1ac50d3df5bb6ec111915140b643eb056c5ee217cfb4896413fd140c215fa6`;
o pacote R3 continua histórico e byte-idêntico, não contém essa correção.

**Prova sintética autorizada e executada:** 1/1 consumida, falhou em 0,965 s,
CLI 1/runner 5; JSON de erro capturado, modelo/custo desconhecidos. Nenhum retry
ou nova autenticação. Recibo na frente T-131 em
`docs/reviews/T-131-prova-cli-sintetica-2026-10-01/resultado.json`.

## Diagnóstico read-only concluído na continuação da meta

Execução nativa do Codex/context-mode e shell zsh interativo resolvem a CLI
2.1.280, mesmo UID/HOME e presenças de variáveis verificadas. `auth status`
retorna exit 1, `loggedIn=false`, `authMethod=none`. Processos vivos do app
Claude usam a 2.1.286; um processo novo dessa folha também retorna status sem
login. Não inspecionamos a autenticação das sessões vivas do app, argumentos,
ambiente ou credenciais delas. Sem nova inferência/login/logout ou troca de CLI.
A causa da ausência de login e da falha original ainda não foi comprovada.
Recibo e limites: `docs/reviews/T-131-diagnostico-contextos-2026-10-01/`
na frente T-131. Não pedir logout ou copiar tokens por hipótese.

Bancada JEV revalidada: 14 testes OK, oito cenários de mutação detectados;
R4 permanece 0/1 e A2 JEV/Luna 0/4 cada. Suíte T-131 fresca: 484 testes OK,
manifesto estrito e lint exit 0. Nada disso aprova gabarito ou rollout.

Nova candidata **T-131 R4**, somente local: onze arquivos/41 hunks,
**138.789 bytes**, SHA `bd30519a96ace8d9d78484d4845675ce596ddb94cce90dec2e2f3d141c736f3d`.
Inclui o runner corrigido e novo módulo de diagnóstico; pacote e diff foram
recompostos/conferidos. Teto proposto 192 KiB somente para essa revisão futura,
não autorizado. Não usar o antigo teto de 128 KiB nem gate R3 consumido.

## Gate de autenticação concluído — 2026-10-02

O “autorizo” humano mais recente aprovou somente o texto abaixo. Uma chamada
`claude auth login --claudeai` confirmou **Login successful**, processo 8681
terminado exit 0. Três processos novos — nativo Codex e context-mode na
frente/main — retornaram exit 0, `loggedIn=true`, `authMethod=claude.ai`,
`apiProvider=firstParty`, stderr vazio. Nenhuma inferência ou envio de review.
Recibo na frente T-131: `docs/reviews/T-131-autenticacao-cli-2026-10-02/`.
Uma autenticação consumida com sucesso; não repetir por esse gate.

“AUTORIZO UMA ÚNICA AUTENTICAÇÃO DA CLAUDE CLI NO CONTEXTO DO CODEX PELO
FLUXO OFICIAL DA ASSINATURA NO NAVEGADOR, SEM TOKEN MANUAL, API KEY OU LOGOUT.
DEPOIS, CONFIRA SOMENTE O STATUS SANITIZADO E SUA PERSISTÊNCIA EM PROCESSO
NOVO. SEM INFERÊNCIA, REVIEW, RETRY AUTOMÁTICO, CÓPIA DE CREDENCIAIS, MUDANÇA
DE PRODUTO, BUMP, COMMIT, PUSH, INTEGRAÇÃO, INSTALAÇÃO OU RESTART.”

O gate de acesso foi cumprido. Não comprova a causa da ausência anterior,
disponibilidade do modelo, custo ou durabilidade futura do login. Nenhuma
revisão é liberada por essa autenticação. T-131/T-098 continuam suspensos.

## Próxima decisão — duas revisões atuais, ainda não autorizadas

| Card | Pacote | Bytes exatos | Teto pontual | Chamadas |
|---|---|---:|---:|---:|
| T-131 | R4 candidata integral, 11 arquivos/41 hunks | 138.789 | 192 KiB / 196.608 bytes | 1 |
| T-098 | R4 integral candidata, 48 casos/18 famílias | 51.176 | 64 KiB / 65.536 bytes | 1 |

Total: **189.965 bytes** de código/instruções sanitizados. Caminhos:
`docs/reviews/T-131-R4-integral-candidata/pacote.txt` na frente T-131 e
`docs/experimentos/T-098-A2/revisao-r4-integral-candidata/pacote.txt` na main.
Hashes reconferidos nesta etapa: T-131 `bd30519a96ace8d9d78484d4845675ce596ddb94cce90dec2e2f3d141c736f3d`;
T-098 `0934fda33cdca92add01e4fb8f4dfbaaa8543d26470d08605e787900349e4281`.

Texto proposto ao dono:

“AUTORIZO UMA ÚNICA R4 DO T-131 E A RETOMADA EXPRESSA DE UMA ÚNICA R4 DO
T-098, VIA CLAUDE CLI DA ASSINATURA/ANTHROPIC, MODELO CLAUDE OPUS 5.5, COM
OS PACOTES SANITIZADOS ATUAIS, HASHES ACIMA, 189.965 BYTES NO TOTAL. AUTORIZO
TETOS PONTUAIS DE 192 KiB E 64 KiB, SEM MUDAR O DEFAULT. ESTOU CIENTE DE QUE
CÓDIGO E INSTRUÇÕES SAIRÃO DA MÁQUINA. SEM PII, CREDENCIAIS, FERRAMENTAS OU
RETRY. SE A PRIMEIRA FALHAR, PARE ANTES DA SEGUNDA. SEM NOVA AUTENTICAÇÃO,
TOKEN MANUAL, API KEY, LOGOUT, MUDANÇA DE PRODUTO, BUMP, COMMIT, PUSH,
INTEGRAÇÃO, PUBLICAÇÃO, INSTALAÇÃO OU RESTART.”

Só executar após autorização humana nova; login concluído não substitui esse
gate. R3/prova sintética anteriores permanecem consumidas; não as repetir.

## Proposta anterior de diagnóstico — concluída sem inferência

“AUTORIZO DIAGNÓSTICO READ-ONLY DOS CONTEXTOS DA CLAUDE CLI, COM STATUS
SANITIZADO DE AUTENTICAÇÃO E COMPARAÇÃO DE ENTRYPOINT/VERSÃO/AMBIENTE.
SEM LER OU EXPOR TOKENS, CHAVES OU CREDENCIAIS; SEM NOVA INFERÊNCIA, LOGIN,
LOGOUT, RETRY, ALTERAÇÃO NO PRODUTO, COMMIT, PUSH, INSTALAÇÃO OU RESTART.”

Objetivo cumprido parcialmente: os contextos/entrypoints e status atuais foram
comparados; a causa da perda/ausência de login continua não provada. Não
atribuir falha original a flag/modelo/login por tabela ou gastar outra chamada.

## Gate sintético anterior — consumido, não repetir

“AUTORIZO UMA ÚNICA CHAMADA SINTÉTICA VIA CLAUDE CLI, PELO RUNNER CORRIGIDO
DO T-131 E WRAPPER COM --safe-mode, PARA VERIFICAR A VIA NO CONTEXTO DO CODEX.
SEM CÓDIGO, PII, CREDENCIAIS, FERRAMENTAS OU RETRY; SEM NOVA AUTENTICAÇÃO,
BUMP, COMMIT, PUSH, INTEGRAÇÃO, PUBLICAÇÃO, INSTALAÇÃO OU RESTART.”

Se falhar, parar com recibo sanitizado; se passar, comprova apenas esse contexto
e modelo. Não comprova a causa original da falha na janela Claude e não libera
review por tabela. Nova revisão T-131 exige snapshot/pacote atualizado; R4 JEV
permanece suspensa. Relatório e hashes estão no worktree T-131 em
`docs/T-131-recibos-correcao-local.md` e `docs/T-131-recibos-snapshot-local.json`.

## Proposta histórica das revisões — não reenviar

| Card | Snapshot | Entrada exata | Exceção proposta por chamada | Chamadas |
|---|---|---:|---:|---:|
| T-131 | R3: diff completo de dez arquivos + contexto declarado | 103.081 bytes | 128 KiB / 131.072 bytes | 1 |
| T-098 | R4: sete arquivos integrais, 48 casos e rubrica | 51.176 bytes | 64 KiB / 65.536 bytes | 1 |

Total: **154.257 bytes**, duas chamadas frescas ao Anthropic pelo Claude CLI
da assinatura, modelo desejado `claude-opus-5-5`. Sem ferramentas ou retry.
Formatos inválidos, falha, timeout ou divergência de modelo não aprovam.
Não há promessa de custo cobrado, qualidade ou suporte real neste preparo.

Recomendação histórica: autorizar essas duas revisões integrais com exceção de tamanho
somente para os pacotes identificados. Um hunk T-131 tem 19.469 bytes; o limite
geral de 16 KiB não o comporta. Não alterar política/default do produto para
acomodar a rodada. A alternativa é redesenhar localmente os pacotes; cortar
conteúdo ou declarar review parcial como aprovação integral não é aceitável.

## Autorização anterior — R3 consumida, R4 suspensa

“AUTORIZO UMA ÚNICA R3 DO T-131 E UMA ÚNICA R4 DO T-098, COM OS PACOTES
INTEGRAIS PREPARADOS (154.257 BYTES NO TOTAL), AO ANTHROPIC VIA CLAUDE CLI.
AUTORIZO EXCEÇÃO PONTUAL DE ENTRADA DE 128 KiB PARA T-131 E 64 KiB PARA T-098,
SEM ALTERAR A POLÍTICA GERAL. ESTOU CIENTE DE QUE CÓDIGO E INSTRUÇÕES SAIRÃO
DA MÁQUINA. SEM PII, CREDENCIAIS, FERRAMENTAS OU RETRY; SEM BUMP, COMMIT,
PUSH, INTEGRAÇÃO, PUBLICAÇÃO, INSTALAÇÃO OU RESTART.”

T-131 pacote SHA-256:
`d4e8fbd1b1910581d59127639b1fcb5df731fbc8214414adb5a3b9dd2ea6b1d2`.
T-098 pacote SHA-256:
`0934fda33cdca92add01e4fb8f4dfbaaa8543d26470d08605e787900349e4281`.
Mudança de bytes/snapshot exige novo gate; não reutilizar autorização anterior.

## Decisões posteriores, não exigidas agora

1. Auditar os pareceres válidos. Se houver bloqueador real, propor correção
   delimitada; não abrir rodada adicional automaticamente.
2. Se T-131 ficar apto, conciliar com T-089 por trechos em frente isolada,
   preservando threadId/--wait. O snapshot final de T-089 ainda carece de
   re-review independente; sua branch não foi editada ou integrada aqui.
3. Escolher a próxima versão livre e autorizar commit/push/integração somente
   do snapshot final conciliado. Publicação/instalação/restart são outro gate.
4. Se T-098 ficar apto, congelar payloads id/text e pedir autorização separada
   para quatro chamadas JEV + quatro Luna. Medir antes de propor adoção.

O elenco ativo e os modelos em uso permanecem inalterados. O dono não precisa
classificar cada tarefa nem escolher implementer novamente; o Manager mantém
a distribuição aprovada e apresenta somente decisões que mudam autoridade.
