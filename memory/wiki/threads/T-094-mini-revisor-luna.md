# T-094 — Mini-revisor Luna nos dois hosts

## Estado

- 2026-09-11: AWAITING_OWNER — R6 do T-062 sem aprovação, contador 6/6; decidir R7 ou canário Luna isolado.
- Frente `@frente-gauntlet`, conduzida no Codex. Pedido: "entao vamos prosseguir - o que precisa?".
- Aprovação interpretada como execução dos itens 1–2 do plano, sem ativação global, publicação
  ou atualização de Companion. Nenhuma implementação do T-094 iniciada: a base aguarda revisão.
- Modelo desejado pelo dono: `gpt-5.6-luna@max`, auxiliar nos hosts Codex e Claude Code.
- "Cloud" foi interpretado como Claude Code pelo contexto; execução remota em nuvem não está no escopo deste plano.

## Contexto e decisões

O dono quer aproveitar pontos úteis do Gauntlet Loop sem reformar a arquitetura do Orquestra.
O primeiro teste sintético teve oito casos, quatro com erros intencionais e quatro controles:
Luna e Astra em `high` acertaram os oito. Não foi medida economia, revisão de código real,
confiabilidade geral nem paridade entre hosts.

Agora o dono pediu planejamento e sugeriu inserir erros deliberados para comparar os modelos.
Foi feita uma segunda sonda, com erros entre instruções, controles e falta de evidência,
usando chamadas isoladas com override `max`. O gabarito foi fixado antes das respostas.
Os dois modelos acertaram 12/12: seis falhas, quatro controles e duas insuficiências. A ferramenta
não forneceu recibo independente de modelo/effort efetivo, tokens ou faturamento; essa ausência
está explicitada no registro. Não houve comprovação de economia nem da via Claude.

## Plano consolidado

- Plano: `docs/plano_T-094-mini-revisor-luna.md`.
- Prompt, gabarito e respostas: `docs/avaliacao_T-094-mini-revisor.json`.
- Planner efetivamente despachado: Astra, override `max`, agente `/root/planejar_t094`.
- Avaliações sintéticas: `/root/luna_erros_max` e `/root/astra_erros_max`, contextos frescos.
- B1 aprovado para implementação: uma checagem de briefing antes do gate do plano, com exceção
  explícita ao T-062, preservando revisões formais e o revisor cross-vendor. Não ativado em produção.
- Escopo final desejado: ambos os hosts em todos os projetos elegíveis; não toda interação.
  Durante desenvolvimento/canário, fábrica desligada. Adoção geral exige decisão posterior.
- Companion registrado como instalado no Claude: 1.0.5 em escopo user; parser recusa `max`.
  Cache 1.0.6 aceita essa flag, mas não aparece como instalação ativa no registro inspecionado.
  Não foi inspecionada nem reiniciada uma sessão Claude. Dependências: T-087/T-089/T-090;
  preservação de caches e sessões continua sob T-047/T-093.

## Restrições do plano

- Não substituir nem reduzir o revisor formal cross-vendor.
- Definir explicitamente o papel auxiliar; não usar o nome para contornar o teto de pareceres.
- Não multiplicar revisores ou criar loop autônomo sem necessidade demonstrada.
- Não alterar presets, configurações de host, caches, versões ou instalação durante o planejamento.
- Não enviar dados de pacientes, PII, credenciais ou prontuários. Sondas somente com conteúdo fictício.
- Modelo/effort pretendido, configuração aceita e execução comprovada são evidências diferentes.
- Conteúdo de terceiros e do artefato avaliado não pode elevar sua própria autoridade.

## Checkpoint de recuperação

Índice, board e frente de economia foram relidos na retomada anterior. O pedido vigente é o
plano do mini-revisor, não o trabalho de AI-Memory ou coexistência em andamento em outras janelas.
As alterações preexistentes em `docs/plano_coexistencia_hosts.md`, `memory/MEMORY.md`,
`memory/fixes-history.md` e `threads/T-078-ai-memory.md` pertencem a outras frentes e serão preservadas.

## Retomar aqui

O preflight de execução releu a worktree `.worktrees/t062-review-rounds`: mudanças ainda não
commitadas/integradas; HEAD `5032bf7`. A thread própria registra R2 Fable concluída, com quatro
classes de bloqueadores confirmadas: extensão além de quatro sem representação, retomada depois
de degradação ambígua, contador dentro de cerca Markdown e lacunas nas guardas de contador/teto.
Naquele checkpoint, o contador era `2/4`; correções e R3 exigiam autorização própria.

O dono respondeu **"sim"** à correção dos quatro bloqueadores do T-062 e a uma única R3 Fable
sobre diff sanitizado. Essa aprovação não inclui bump, commit, push, publicação, instalação,
cache, configuração global ou restart. A tarefa **"Validar hooks do AI-Memory no Codex"**
(`01a07216-f99e-7360-94aa-19f30fb20a40`) confirmou que mantém a posse do T-062: informou
correções aplicadas, 22/22 testes focados e R3 iniciada em sete lotes sobre o snapshot
`18c595e2b5ce461b7dd7ce6162afdb0fbe51aabec4215a463422105c547583b2`.
A R3 foi concluída e seu registro durável foi conferido: sete chamadas com saída `0` e
`claude-fable-5-1`; lotes 1, 3 e 7 aprovados, 2, 4, 5 e 6 reprovados. Portanto, sem aprovação
global. O contador permanece `revisões: 3/4`. Não editar aquela worktree, duplicar despachos nem
assumir integração da base.

Na leitura de compatibilidade, o Manager encontrou uma possível ambiguidade em `revisar.md:20`
daquela worktree: “depois que qualquer lote iniciou uma chamada, todo novo despacho pertence a
uma nova revisão” pode incluir indevidamente o despacho normal do segundo lote. O cenário foi
enviado à tarefa responsável para sua auditoria consolidada, sem alterar o snapshot ou despachar
outro revisor. A tarefa responsável confirmou o problema na auditoria da R3 e corrigiu o contrato
localmente; essa observação não constituiu rodada adicional nem autorizou R4.

**Autorização recebida em 2026-09-11:** o dono respondeu “autorizo” a uma única R4 Fable sobre
o material sanitizado do T-062. A autorização foi encaminhada à tarefa responsável, que mantém
a posse, com checagem de duplicidade antes do despacho. R5, bump, commit, push, publicação,
instalação, alteração global/cache e restart permanecem fora do escopo. Não executar outra
revisão aqui. A R4 foi executada e seu resultado durável conferido: sem aprovação, com cobertura
parcial e contador `revisões: 4/4`. O saldo não pode ser zerado ou ampliado automaticamente.
**Decisão atual do dono:** autoriza extensão única de uma revisão (`+1`) para corrigir os três
bloqueadores auditados e submeter o diff sanitizado a uma única R5, somente após os testes negativos
pertinentes passarem? Essa proposta não autoriza R6, bump, commit, push, publicação, instalação,
alterações globais/cache ou restart. Até a resposta, nenhuma correção ou nova revisão deve começar.
Evidência do T-062:
`memory/wiki/threads/T-054-economia-tokens.md` e `memory/MEMORY.md` na worktree `t062-review-rounds`.

Depois da estabilização da base, implementar T-094 em worktree. Companion de usuário no Claude
foi reconferido: 1.0.5 registrado, allowlist sem `max`; sua atualização continua em gate separado.
Não alterar times formais, presets, cache, versão ou configuração global por inferência.

## Checkpoint de recuperação — 2026-09-10

Após compactação, o Manager releu integralmente o índice `memory/MEMORY.md`, o board e esta
thread, recuperando os trechos pertinentes para a retomada. O pedido atual continua sendo a
correção autorizada do T-062 seguida de uma única R3; a posse exclusiva da outra tarefa foi
confirmada por mensagem direta. A aprovação e a espera pela dependência foram refletidas no
board, sem alterar cards alheios. T-094 não foi implementado ou ativado; aguardar o resultado
auditado da revisão antes de escolher sua base de implementação.

## Atualização posterior — R3 concluída e novo gate

A tarefa responsável registrou correções locais para os quatro achados auditados: distinção entre
revisão/manifesto/lote; parada com decisão do dono após duas reavaliações sem progresso; cobertura
da guarda para formulações de teto como R4/R5/quarta revisão; e teste discriminante para `5/6 · +2`.
Os testes focados pós-correção constam como 22/22 no registro da tarefa; não foram reexecutados
por esta frente. O diff corrigido é posterior ao snapshot reprovado e ainda não tem aprovação
independente. T-062 está `[!] @codex`, `revisões: 3/4`, aguardando autorização própria da R4.
T-094 segue sem implementação ou ativação, e nenhuma nova revisão foi despachada por esta frente.

## Autorização da R4 — 2026-09-11

A pergunta acima foi respondida afirmativamente pelo dono. O registro de R3 (`3/4`) permanece
histórico; cabe à tarefa responsável persistir `4/4` antes da chamada efetiva, sem zerar o saldo.
Esta frente apenas encaminhou a autorização e atualizou seu próprio card/documentação. O resultado
da R4 foi recebido na atualização abaixo; o plano do Luna não precisa de nova aprovação e continua
sem implementação ou ativação global.

## Resultado da R4 e teto consumido — 2026-09-11

A tarefa responsável entregou o handoff, confirmado em sua thread durável. Snapshot sanitizado:
`8ccfdc341a2719a92bc39489512d98b28ac18a19e46b1a01faec50806dc44fc7`. Sete lotes predeclarados,
sem retry, com chamadas saindo `0` e modelo `claude-fable-5-1` comprovado. Lotes 3 e 7 aprovados;
2, 4, 5 e 6 reprovados; lote 1 inválido, sem veredito/achados/cobertura. Resultado global sem
aprovação e com cobertura parcial; contador `4/4` preservado.

Três bloqueadores confirmados pela auditoria da tarefa responsável:

1. Grafias malformadas do contador são confundidas com ausência legada e passam sem diagnóstico.
2. Algumas formulações de teto nos consumidores ainda escapam à guarda de fonte única.
3. Falta precedência conservadora entre board e evidência da thread após interrupção da chamada.

Os testes focados constam como 22/22, mas os mutantes demonstraram lacunas de cobertura. A suíte
completa teve 343 testes e quatro falhas preexistentes do T-081; manifesto e `diff --check` saíram
`0`. O lint registrou somente T-081 e a divergência esperada entre fonte local e cache instalado.
Esses resultados vêm do registro da tarefa responsável e não foram reexecutados nesta frente.

Não houve correção pós-R4 nem R5 naquele checkpoint. A responsabilidade pelo T-062 permanece com
a tarefa `01a07216-f99e-7360-94aa-19f30fb20a40`; a atualização abaixo substitui a pausa.

## Extensão +1 autorizada — 2026-09-11

O dono respondeu **“continue para corrigir esses pontos”** ao gate que propunha uma extensão única
`+1`, a correção dos três bloqueadores auditados e uma única R5 somente depois dos testes negativos
pertinentes passarem. A autorização foi encaminhada à tarefa responsável, com posse exclusiva da
worktree e instrução de conferir duplicidade antes do despacho.

O estado histórico `4/4` deve ser preservado; antes da chamada efetiva, a tarefa responsável deve
registrar a forma canônica `revisões: 5/5 · extensão: +1`, a decisão, o snapshot integral, o
manifesto fixo e a cobertura predeclarada. Não há retry automático. R6/nova extensão, bump, commit,
push, publicação, instalação, alteração de cache/configuração global e restart continuam fora do
escopo. Esta frente não edita o T-062 nem executa revisão paralela.

O handoff da R5 foi recebido e está consolidado abaixo. T-094 continua aprovado, mas sem
implementação ou ativação enquanto a base não tiver aprovação independente.

## Resultado da R5 e novo gate — 2026-09-11

A correção autorizada começou por RED com sete falhas discriminantes e voltou a 11/11 após tratar
os três bloqueadores da R4. Antes da revisão, os gates registraram 22/22 testes focados, manifesto
estrito e `diff --check` verdes. A R5 usou o snapshot sanitizado
`71ee9355ad47c50c6ec44a1ea17b54b8d1363df8bb40860f6ca470109b80d401`, com 12 arquivos e oito
lotes. As oito chamadas saíram `0`, provaram `claude-fable-5-1` e entregaram o formato completo.
Lotes 1–4, 7 e 8 aprovaram; 5 e 6 reprovaram. Não houve retry.

A auditoria confirmou dois bloqueadores:

1. A chave canônica com valor malformado ainda pode virar “legado ausente”: exemplos
   `revisões: 2 / 4`, `revisões: 2 de 4` e `revisões:` passam sem diagnóstico.
2. Os testes não impedem regressão que aceite `revisão: 2/4` e `revisões 2/4` como aliases,
   nem cobrem duplicidade mista com a chave canônica.

A R5 foi consumida sem aprovação global. O T-062 permanece na tarefa
`01a07216-f99e-7360-94aa-19f30fb20a40`, em `[!] @codex`, com
`revisões: 5/5 · extensão: +1`. A verificação final registrou 22/22 testes focados, manifesto e
`diff --check` verdes; a suíte completa manteve somente as quatro falhas preexistentes do T-081.
Não houve correção pós-R5, R6, bump, commit, push, publicação, instalação ou mudança global.

**Recomendação:** substituir a acumulação de exceções na expressão por um parser localizado em
duas etapas: primeiro reconhecer a presença da chave, independentemente do valor; depois aceitar
somente a gramática canônica e rejeitar chave vazia, espaçamento interno, `de`, aliases e
duplicidade mista. Uma tabela de mutações deve cobrir positivos e negativos com numeradores válidos,
para não confundir rejeição de sintaxe com estouro do teto.

## Parser estrito e R6 autorizados — 2026-09-11

O dono respondeu **“sim”** ao gate acima. A autorização foi encaminhada à tarefa responsável e
abrange somente o parser em duas etapas, a matriz de mutações descrita e uma única R6 Fable após
os REDs e gates locais. Antes da chamada efetiva, deve ser persistido o estado cumulativo
`revisões: 6/6 · extensão: +2`, junto da decisão, snapshot integral, manifesto fixo e cobertura
predeclarada.

Não há retry automático. R7/nova extensão, bump, commit, push, publicação, instalação,
cache/configuração global e restart continuam fora do escopo. Esta frente não edita a worktree
do T-062 nem executa revisão paralela.

O handoff da R6 foi recebido e está consolidado abaixo.

## Resultado da R6 e decisão de rumo — 2026-09-11

A correção autorizada começou por RED com quatro falhas e terminou em 13/13; a matriz passou a
matar o mutante que aceitava aliases, cobrir duplicidade mista e distinguir sintaxe de estouro.
Antes da revisão, os gates registraram 24/24 testes focados, manifesto estrito e `diff --check`
verdes; a suíte completa executou 345 testes e manteve apenas as quatro falhas preexistentes do
T-081.

A R6 usou o snapshot sanitizado
`6be03658971fa9192755be98bef547d83a1542492a84b3546a060c84ce2b1e56`, com 12 arquivos e oito
lotes. As oito chamadas saíram `0`, provaram `claude-fable-5-1` e entregaram o formato completo.
Lotes 1–7 aprovaram; o lote 8 reprovou. Não houve retry ou lote repetido. A auditoria confirmou
que os dois bloqueadores da R5 foram fechados, mas aceitou um novo bloqueador:
`memory/wiki/_schema.md` repete os números do teto enquanto `revisar.md` deveria ser a fonte
exclusiva, e o lint não trata o schema como consumidor protegido.

O T-062 permanece na tarefa `01a07216-f99e-7360-94aa-19f30fb20a40`, em `[!] @codex`, com
`revisões: 6/6 · extensão: +2`. Não houve correção pós-R6, R7, bump, commit, push, publicação,
instalação ou alteração global.

**Recomendação do Manager:** não autorizar automaticamente uma R7. Seis rodadas integrais para
chegar a uma única duplicação documental já exibem o custo e a recorrência que o T-094 pretende
reduzir. Estacionar o T-062 e avançar somente com o desenvolvimento/canário isolado permitido pelo
plano do Luna: fábrica desligada, sem alterar a regra canônica de revisões, sem ativar Claude e sem
instalação ou configuração global. O resultado seria evidência experimental, não integração.

**Decisão atual do dono:** autoriza estacionar o T-062 nesse estado e avançar com esse canário
isolado do Luna? Se preferir concluir o T-062 primeiro, a alternativa exige autorização separada
para remover a duplicação de `_schema.md`, proteger esse consumidor no lint e executar uma R7
integral; nada disso está autorizado agora.

## Checkpoint de recuperação — 2026-09-12

Após compactação, o Manager releu `memory/MEMORY.md`, `memory/wiki/KANBAN.md` e esta thread. O
pedido vigente pergunta o que é “canário”, por que a implementação demorou e pede concluir as
pendências antes de novas análises. O canário é um teste operacional pequeno e controlado, sem
ativação global; as sondas sintéticas 12/12 já feitas não equivalem a ele. A demora veio de tratar
o T-062 como pré-requisito da integração, atravessando seis revisões; T-094 ainda não foi
implementado. Nenhuma autorização para R7, release ou mudança global foi inferida da pergunta.

## Transferência de frente — 2026-09-13

O dono aprovou concentrar o trabalho nesta tarefa Codex (`01a07216-f99e-7360-94aa-19f30fb20a40`).
A tarefa “Analisar Gauntlet Loop no Orquestra” foi arquivada após handoff; o card continua aberto,
agora conduzido aqui sob `@frente-gauntlet @codex`. A decisão foi estacionar o T-062 em `6/6` e
avançar com o canário isolado do T-094, sem R7 automática. O canário não autoriza integração do
contrato dependente do T-062, ativação de fábrica, instalação, restart, bump, commit, push ou
publicação. As edições de outras frentes na `main` permanecem intactas.

## Canário Codex isolado — 2026-09-13

Foi criado o worktree `codex/t094-canary` em `.worktrees/t094-canary`, separado da `main` e do
T-062. Baseline com Python 3.12: 332 testes, quatro falhas preexistentes do marcador T-081.
Os pacotes e o gabarito predeclarado estão em `docs/canario_T-094-codex-*` desse worktree.
Todos os pacotes tinham menos de 8.192 bytes e só conteúdo fictício. As chamadas usaram
`codex exec --ignore-user-config --ephemeral --sandbox read-only --model gpt-5.6-luna` com
`model_reasoning_effort="max"`; nenhuma apresentou evento de ferramenta ou alteração de arquivo.
As flags foram aceitas, mas o JSONL não comprovou de forma independente o modelo/effort efetivo.

- A (`3221e8fc…`, thread efêmera `01a09c0a-be19-78f1-968a-c29ae975901d`) achou a contradição
  `R1`/`E3`, porém omitiu `faltas` e marcou `insuficiente`: saída fora do contrato.
- B (`28b67a5e…`, `01a09c0b-c8e4-77a3-92fd-c8a57a5aa255`) revelou erro do próprio controle:
  `E3` dizia registrar em `revisar.md` sem editar esse arquivo; outros critérios não tinham oráculo
  suficiente. Não contar seus achados como falsos positivos.
- C (`ef37b54d…`, `01a09c0e-5f98-7471-8513-bf97af9c9fd2`) respondeu com lacunas plausíveis no
  briefing revisado, mas usou `cenario_concreto` no lugar do campo obrigatório `cenario`. O controle
  ainda não era limpo; D não foi chamado, sem retry de A/B/C.

As três chamadas somaram 50.895 tokens de entrada (26.880 em cache) e 10.177 de saída, dos quais
9.073 eram raciocínio, conforme o runtime. O custo monetário e a economia líquida continuam
indeterminados. Isto não valida o Loop A, o host Claude, a ausência de falsos alarmes nem a adoção
do Luna. Suspender novas chamadas até melhorar localmente o contrato do pacote e a verificação
estrutural de saída; não mudar o effort aprovado por inferência.

## Checkpoint de recuperação e autorização — 2026-09-13

Após compactação, o Manager releu `memory/MEMORY.md`, `memory/wiki/KANBAN.md` e esta thread;
confirmou o checkout compartilhado sujo e o worktree isolado `codex/t094-canary`. O pedido vigente
é a autorização explícita do dono para corrigir localmente o pacote e sua validação e então fazer
**no máximo duas novas chamadas Codex Luna@max**, em par controle/contradição fixado antes do
despacho. Não repetir A/B/C, não enviar D isolado, não executar R7 do T-062. O T-062 segue
estacionado em 6/6. Não há autorização para integração, configuração global, Claude, bump,
commit, push, publicação, instalação ou restart. O card passou a `[~] @codex` só para esta sonda.

Pré-despacho: E/F v3 foram fixados no worktree, com gabarito em
`docs/canario_T-094-codex-gabarito.md`. E (controle) tem 3.671 bytes,
SHA-256 `d7d9cf3946e23f0b7115398b577f56abe5acd6805c617a5e1d372db51b887514`; F
(contradição) tem 3.680 bytes,
SHA-256 `509fca24454624ec00a9638fd7394091f1183d20d8766a7f9ac91f4435d4e2f4`.
O diff contém só card, snapshot e E3. F será despachado somente se E passar no schema e gabarito.

## Resultado do par E/F — 2026-09-13

As **duas chamadas autorizadas foram consumidas** via `codex exec --ephemeral --ignore-user-config`
em sandbox read-only, solicitando Luna@max. E passou: resposta JSON de 92 bytes com quatro chaves,
snapshot exato, `checado`, sem achados/faltas e sem evento de ferramenta. F encontrou a contradição
E3/R1/R2/K1 com cenário concreto, mas **falhou no contrato**: `snapshot_briefing` incluiu quase
todo o restante do pacote, em vez do identificador literal. Também apontou a disponibilidade de
Python 3.12, capacidade não declarada em E/F; é lacuna plausível da fixture, não falso positivo
demonstrado. O gabarito no worktree contém hashes, oráculos, formatos e métricas completos.

E/F somaram 34.016 tokens de entrada (17.920 em cache) e 12.525 de saída, com 11.602 de
raciocínio. Não há recibo independente do modelo/effort efetivo, economia líquida, teste Claude,
Loop A ou integração. O par é **inconclusivo para adoção**. Não há mais chamadas dentro desta
autorização. Três versões de pacote com falhas distintas exigem rever a representação do snapshot,
validar saída mecanicamente e declarar capacidades ambientais antes de outra sonda; não fazer
ajuste incremental com mais gasto sem decisão do dono. Os outros arquivos sujos da main continuam
intocados; sem commit, push, publicação, instalação, restart ou configuração global.

Verificação local após o par: `git diff --check` das alterações rastreadas T-094 saiu `0` e os
hashes E/F continuaram iguais aos predeclarados. `claude plugin validate ./orq --strict` saiu `0`.
A suíte completa com Python 3.12 rodou 332 testes e manteve quatro falhas preexistentes; o lint
saiu `1` pelo marcador `@codex` no card T-081 já em `[?]` (linha 14 do board), não pelo T-094.
Não corrigir o card alheio nem declarar os três verificadores verdes.

## ⏭️ RETOMAR AQUI

**Checkpoint de recuperação — 2026-09-13:** depois de compactar, reli `memory/MEMORY.md`, o board
e esta thread; mantive o pedido vigente (“autorizo, prossiga”) limitado ao redesenho local. O T-094
voltou a `[!] @frente-gauntlet @codex` após completar essa parte. O par G/H v4 em JSON, o gabarito
e o validador/testes estão no worktree `.worktrees/t094-canary/docs/`, sem mexer no produto `orq/`.
O par declara Python 3.12/permissão em K2 e isola `snapshot_briefing` como string de topo. O
`preflight` deu `exit 0`, 4.468/4.464 bytes, SHA-256
`ae0046700e57f0e486f0d6fd05fb69499d0b34c1eb43a66f9e56be4c280b7b74` /
`2c1ae9da92f8fb615bfa4d1db2e8181f1df92ef12a63539b54512d9f81e50a08` e delta só E3.
Os digests estão fixados no validador (inclusive na validação avulsa da resposta), não apenas
impressos no relatório. Há 22 testes sintéticos verdes; a mutação temporária que removia a
comparação de snapshot fez o teste específico falhar e foi restaurada antes da suíte verde.

As verificações do projeto nesta fonte isolada foram repetidas: `claude plugin validate ./orq
--strict` e `git diff --check` saíram `0`; `lint-coerencia.py` saiu `1` pelo marcador `@codex` no
T-081 já em `[?]`, alheio a esta frente; a suíte `PYTHONDONTWRITEBYTECODE=1 python3.12 -m
unittest discover -s orq/scripts -p 'test_*.py'` executou 332 testes com as mesmas quatro falhas
de baseline (três dependem do lint do T-081 e uma aponta `memory/MEMORY.md` na guarda da chave
morta). Não corrigir arquivos de outra frente para fazer o baseline parecer verde. Os arquivos
sujos da main de Claude foram preservados, inclusive `memory/MEMORY.md`; nenhuma chamada ao Luna,
R7 do T-062, commit, push, publicação, instalação, restart ou configuração global nesta etapa.

**Resultado após o novo “prossiga” — 2026-09-13:** o dono autorizou prosseguir; delimitei antes
do despacho um par G/H, uma chamada por pacote, G primeiro e H apenas se G passasse, sem retry.
Ambos usaram `codex exec --json --ephemeral --ignore-user-config --sandbox read-only`, pedindo
Luna@max e passando o pacote fictício por stdin. G passou schema e oráculo (92 bytes, sem achados,
sem ferramenta). H respondeu com snapshot literal, um achado correto sobre E3/R1/R2/K1, sem
ferramenta, mas citou O1 como apoio adicional. O oráculo fixado aceitava apenas R1/R2/K1/E3;
`response` saiu `2` (`ORACULO`). O1 é apoio semanticamente pertinente ao mesmo achado, porém **o
gate formal não passou** e não foi alterado retroativamente. G/H consumiram 2/2 chamadas, sem
terceira tentativa. Total do runtime: 36.344 tokens de entrada (17.920 em cache), 1.541 de saída
(1.355 de raciocínio); valor monetário e identidade/effort efetivos sem recibo independente.
Respostas e adjudicação íntegras em `.worktrees/t094-canary/docs/canario_T-094-codex-gabarito.md`
e nos JSONL G/H.

**Desenvolvimento isolado aprovado:** no worktree `codex/t094-canary`, alterei somente
`orq/commands/elenco.md` (seção B1 separada, Claude/Codex `nao`, Luna@max) e
`orq/scripts/lint-coerencia.py` (guarda de seção única/completa, sem misturar override parcial com
fábrica), mais `orq/scripts/test_briefing_check_contract.py`. A função
`validate_briefing_check_contract` retorna tuplas `(Path, linha, mensagem)` e está ligada ao lint.
Houve RED antes da função, GREEN depois e mutação da ligação ao `main()` que fez o teste de
integração falhar, restaurada antes do GREEN. São 11 testes B1 focados verdes, 22 do validador
offline verdes; suíte do produto: **343 testes, 4 falhas iguais ao baseline**. Manifesto estrito
verde. Lint vermelho por T-081 alheio e por cache 0.27.6 diferente da fonte modificada — esperado
sem bump/instalação, não tratar como release validada. Ruff no teste novo verde; no arquivo lint
completo acusa só E741 preexistente na linha 182. `git diff --check` verde. Sem review cross-vendor,
bump, commit, push, publicação, instalação, restart ou ativação. Os quatro arquivos sujos de outra
frente na main continuam preservados.

**Próximo gate real:** T-062 permanece estacionado em 6/6 e impede integrar a exceção B1 em
`revisar.md`. A R6 reprovou porque `_schema.md` ainda prescreve `4`/`4 + K` e “quatro revisões”,
embora `arquitetura.md` reserve o contrato exclusivamente a `orq/commands/revisar.md`; o lint não
guardava `_schema.md` como consumidor. O dono precisa decidir se autoriza **corrigir esse
bloqueador no worktree T-062 e executar apenas uma R7 Fable de snapshot corrigido**, com extensão
delimitada própria, ou se prefere manter o card parado; esta frente não executa R7 por inferência.
Depois da base integrada, completar o consumidor B1 no Loop A, a revisão cross-vendor, a
homologação do host Claude e os testes de benefício/custo. Adoção geral e release seguem decisões
separadas. Não fechar T-094 com a sonda parcial nem com a guarda isolada.
