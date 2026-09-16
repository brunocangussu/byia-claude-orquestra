# T-071 — reconhecimento da seção arquivada

## Evidência e escopo

O parecer em `T-054-pareceres.md:136-138,173-183` mostrou que o padrão
`/^##+ .*[Aa]rquiv/`, duplicado nos dois `awk` de `kanban-status.sh`, para em
`## Como arquivar cards` ou `## Não arquivados`, mas não em `## ARQUIVADOS`.
O parser de posse em `lint-coerencia.py` usa outra regra para a mesma fronteira;
`_schema.md:20-21` ainda descreve o contrato frouxo. Uma divergência entre
contagem, régua de 240 bytes e guarda de posse poderia esconder cards ativos.

## Proposta para aprovação

Tratar como seção arquivada **somente** um cabeçalho H2 iniciado por `##` na
coluna 1 cujo título, após separadores ASCII (espaço/tab) e um `📦` opcional,
seja exatamente `Arquivo`, `Arquivado`, `Arquivada`, `Arquivados` ou
`Arquivadas`, sem distinção entre maiúsculas e minúsculas ASCII. Preservar
`Arquivo` porque o schema vigente o promete. Não equiparar espaço Unicode a
espaço/tab nem aplicar casefold Unicode. Cabeçalho H3, sufixo como `pendentes`,
`Não arquivados`, `Como arquivar`, e cabeçalho dentro de cerca Markdown não
encerram a parte ativa.

Uma cerca Markdown abre com até três espaços de indentação e pelo menos três
crases ou tis; fecha só com o mesmo marcador, comprimento igual ou maior e
apenas espaços/tabs após o marcador. Informações de abertura são permitidas,
exceto crase em abertura por crases. Normalizar CRLF antes de avaliar a linha;
marcador trocado, fechamento mais curto ou com texto não fecham a cerca. Os
dois `awk` e o parser Python devem aplicar o mesmo estado, não alternar um
booleano a cada ocorrência de três marcadores.

Aplicar o mesmo contrato aos dois passos do statusline e à guarda de posse;
atualizar `_schema.md` e proteger com testes que comparem contagem, `📏` e
diagnóstico de host. Não trocar o desenho em dois passos (bytes sob `C` e
título sob locale do usuário). A revisão cross-vendor ocorre **após**
implementação e aprovação, com diff sanitizado; não foi solicitada agora.

Plano executável: `docs/superpowers/plans/2026-09-13-t071-secao-arquivada.md`.
O `T-076` também alterará `kanban-status.sh`; antes de implementar, reler o
estado dele e integrar as duas mudanças por hunks, sem sobrescrever o outro
worktree. O T-071 não instala release nem muda o board da `main` nesta fase.

## Evidência da preparação

Worktree `codex/t071-archive-heading`, criado de `5032bf7`, sem alteração de
código. Baseline, antes do plano: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
discover -s orq/scripts -p 'test_*.py'` executou 332 testes e reproduziu 4
falhas preexistentes (`test_elenco_perfis`, `test_observation_types_guard` e
duas em `test_write_flag_guard`). Elas não são resultado do T-071. A `main`
está suja com trabalho paralelo e não foi tocada por esta frente.

## Checkpoint de recuperação pós-compactação — 2026-09-13

O Manager releu `memory/MEMORY.md`, o quadro canônico e o `⏭️ RETOMAR AQUI`
do T-062 no worktree dele. O T-062 permanece em `7/7 · extensão: +3`, sem R8
autorizada; o T-076 permanece planejado, sem implementação autorizada. A
`main` está em `5032bf7` com alterações paralelas de Claude/T-094 e não foi
editada, restaurada nem stageada por este trabalho. Este worktree só contém
documentação do plano T-071 e a sua própria linha do card. A confirmação da
suíte de base precedeu a escrita do plano.

## Histórico — checkpoint que aguardava a integração do T-076

Checkpoint de recuperação após compactação, 2026-09-14: o Manager releu o
índice, o quadro canônico e as threads T-071/T-070. A `main` continua em
`5032bf7`, com alterações paralelas de Claude/T-094 preservadas. Dois planners
internos, read-only e sem novos chats no app, revisaram separadamente os
planos T-071 e T-070. O plano inicial T-071 recebeu NO-GO: toggle simples de
cerca escondia card ativo, e classes de espaço/casefold divergiam entre os
dois `awk` e Python. O plano e esta proposta foram corrigidos no worktree;
a rechecagem interna deu GO **para levar ao gate do dono**, sem prova de
implementação ou aprovação do dono. Nenhum código, card
da `main`, release ou cache foi alterado nesta retomada; parecer de planner
não substitui aprovação do dono.

Card `[!] @codex`, **somente planejamento**. A decisão do dono é aprovar ou
ajustar a lista exata de títulos H2 aceitos e o tratamento de cercas Markdown.
Se aprovar, primeiro reconciliar a ordem de integração com o T-076, depois
RED/implementação, testes, revisão cross-vendor e gate de release. Não inferir
aprovação para implementação, Fable, bump, commit, push, publicação, instalação
ou restart a partir deste checkpoint.

Revalidação noturna, 2026-09-15: o contrato proposto continua compatível com o
parser antigo e cobre o falso corte ainda presente. O T-076 agora tem candidato
local corrigido e também altera `kanban-status.sh`, mas aguarda uma R4 antes de
integração. Portanto a ordem segura continua sendo: concluir o gate do T-076,
integrá-lo mediante autorização própria e só então reaplicar o T-071 por hunks
sobre essa base. Implementar agora no snapshot antigo duplicaria o maior ponto
de conflito sem acelerar a entrega.

Contraprova executável repetida nessa base: `## Como arquivar` e
`### Arquivado` cortaram incorretamente o segundo card (`0/1`), enquanto o
título permitido `## ARQUIVADOS` não cortou (`0/2 📏1`). `## Arquivado` foi o
único caso do recorte que se comportou corretamente. Isso confirma o defeito e
os dois lados do contrato proposto; não é apenas revisão textual do plano.

Decisão do dono, 2026-09-15: o plano foi aprovado, mas a implementação só pode
começar depois da integração **autorizada** do T-076. Até lá o card está pronto,
porém bloqueado pela dependência; não há autorização para commit, push,
publicação, instalação ou restart.

## Checkpoint de recuperação e desbloqueio — 2026-09-15

O Manager releu `memory/MEMORY.md`, o quadro e esta thread após compactação.
T-076 foi integrado como 0.27.7 em `origin/main`, seguido do T-070 em commit
separado. Este worktree foi rebased sobre essa `main` sem perder os quatro
arquivos de planejamento do T-071. A dependência foi cumprida e o dono já havia
autorizado a implementação; commit, push, publicação, instalação e restart
continuam fora do escopo.

## Implementação TDD e verificação — 2026-09-15

Task 1 começou por testes que falharam nos falsos cortes, em `ARQUIVADOS` e nas
cercas; só depois os dois programas `awk` receberam o predicado H2 exato e a
máquina de estado por marcador/comprimento. Task 2 repetiu o RED na guarda de
posse e substituiu o toggle booleano pelo mesmo contrato em Python. O schema
agora nomeia os cinco títulos aceitos, espaços/tabs ASCII, `📦` opcional,
Unicode recusado e a gramática de abertura/fechamento das cercas.

Verificação localizada nos Pythons 3.9 e 3.12: statusline 35/35 e guarda 18/18.
A suíte completa executou 387 testes em cada intérprete e manteve exatamente
as três falhas basais externas causadas pelo marcador do T-081. Manifesto
estrito e `git diff --check` passaram; o lint apontou somente o mesmo T-081.
Nenhuma regressão nova foi encontrada. Não houve revisão externa, bump, commit,
push, publicação, instalação ou restart.

## Checkpoint de recuperação pós-compactação — 2026-09-15

O Manager releu `memory/MEMORY.md`, o quadro canônico e esta thread no
worktree `codex/t071-archive-heading`. O pedido ativo permanece restrito à
revisão cross-vendor do snapshot sanitizado do T-071, já autorizada pelo dono.
A implementação TDD e as verificações anteriores continuam intactas; bump,
commit, push, publicação, instalação e restart permanecem fora do gate.

## Revisão cross-vendor R1 e auditoria — 2026-09-15

Foram enviados ao runner Anthropic somente dois lotes sanitizados do T-071:
contrato/implementação (9.736 bytes) e testes (11.355 bytes). A triagem não
encontrou credenciais nem PII; os aparentes telefones eram intervalos de linhas.
O runner confirmou `OPUS_MODEL=claude-fable-5-1`. Os dois pareceres foram
`APROVADO_COM_CORRECOES`, sem bloqueadores, e confirmaram o desenho principal.

A auditoria reproduziu um achado real: `texto.splitlines()` na guarda Python
trata U+2028 e outros separadores Unicode como quebra de linha, enquanto `awk`
só divide por `\n`. No probe `## Arquivado<U+2028>` seguido por `T-999` ativo,
o Python devolveu zero problemas e ocultou o card; a statusline contou `(0/1)`.
A correção mínima é iterar por `texto.split("\n")`, removendo somente `\r`
terminal, e cobrir a divergência por teste.

O achado classificado como alto sobre a régua foi refutado. O regex do primeiro
`awk` inclui cards `[x]`; uma mutação que removeu apenas o corte arquivado desse
passe produziu `📏1`, enquanto o script atual não produz régua. Logo o teste
existente distingue os dois passes. Também foi confirmado que `pt_BR.UTF-8`
existe neste host. O restante é endurecimento válido, não bloqueador: explicitar
no schema que conteúdo de cerca até EOF fica fora dos consumidores; testar CRLF
em cercas, tis com info na via `awk` e fechamentos válidos maiores/indentados;
clarificar que o H2 aceito é ATX na coluna 1, sem fecho ATX ou Setext.

Nenhum código foi corrigido nesta etapa. Não houve bump, commit, push,
publicação, instalação ou restart.

## Correções da R1 e revisão cross-vendor R2 — 2026-09-15

O RED reproduziu oito separadores que `str.splitlines()` promovia a newline
(VT, FF, FS, GS, RS, NEL, U+2028 e U+2029). A troca por `split("\n")` ficou
verde. Durante o lote 1 da R2, a auditoria encontrou a continuação da mesma
causa: `Path.read_text()` traduzia CR isolado antes do laço. Um segundo RED com
`\rtexto` comprovou o falso corte; a leitura do board passou a usar
`open(..., newline="")`, sem alterar os demais consumidores do helper.

O schema agora explicita ATX na coluna 1, rejeição de Setext/fecho ATX,
separadores ASCII e o destino de conteúdo dentro de cerca até fechamento ou
EOF. As matrizes cobrem títulos ASCII/Unicode adversariais, locale UTF-8 real,
CRLF, crase inválida na info, tis com info, fechamentos curtos/maiores,
indentados e com texto. O teste de cerca sem fechamento deixou de depender de
um heading interno que mascarava o próprio oráculo.

A única R2 usou três lotes sanitizados (10.723, 15.445 e 9.441 bytes), todos
com `OPUS_MODEL=claude-fable-5-1`. O lote de implementação voltou `APROVADO`;
guarda e statusline voltaram `CONFIRMA`; nenhum trouxe bloqueador. A checagem
do U+FE0F encontrou duas ocorrências reais, ambas fora do cabeçalho arquivado.

Verificação final: guarda 23/23 e statusline 39/39 nos Pythons 3.9 e 3.12. A
suíte descoberta executou 396 testes em cada intérprete e manteve exatamente
as três falhas basais externas do T-081. Manifesto estrito e `git diff --check`
passaram; o lint apontou somente o mesmo T-081. Não houve bump, commit, push,
publicação, instalação ou restart.

## Gate de versão e integração — 2026-09-15

O dono autorizou o T-071 a assumir a 0.27.8, com bump nos quatro anchors,
commit, push e integração allowlistados. A `main` local compartilhada permanece
fora do caminho de integração para preservar as alterações paralelas. Não há
autorização para publicação, instalação ou restart.

## Verificação do gate 0.27.8 — 2026-09-15

Na árvore exata, statusline passou 39/39 e guarda passou 23/23 nos Pythons 3.9
e 3.12. A suíte completa executou 396 testes em cada intérprete e repetiu
somente as três falhas basais provocadas pelo marcador de host ainda presente
no card T-081; manifesto estrito passou e o lint apontou somente esse mesmo
marcador. Como contraprova, a linha do T-081 foi neutralizada temporariamente
no worktree, sem entrar no escopo: 396/396 passaram nos dois Pythons, manifesto
e lint ficaram verdes. A linha foi restaurada antes do stage.

## ⏭️ RETOMAR AQUI — validar a candidata integrada

Depois de verificar o commit e a integração em `origin/main`, o próximo gate é
publicar e instalar a 0.27.8 nos dois hosts, reiniciar cada host e executar a
validação comportamental do cabeçalho arquivado. O T-047 usará a próxima versão
livre quando for retomado.
