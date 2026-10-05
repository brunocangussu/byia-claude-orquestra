# T-139 — especialização verificável dos papéis centrais

## Pedido e fronteira — 2026-09-25

O dono quer continuar a viabilização do JEV e investigar se o Agency Agents pode tornar
Orquestra mais efetiva ao especializar **orquestrador/Manager, Planner e Reviewer**, com
métodos e skills próprios, em vez de trocar apenas modelo e effort. Esta etapa é
**análise arquitetural e desenho de teste**, não autorização para instalar agentes,
alterar elenco, mudar prompts do produto ou fazer novas chamadas de benchmark.
Frente: `@frente-jev-router @codex`. Trilha `sistema`, faixa `pesada`.

**Objetivo interpretado:** melhorar taxa de entregas aceitas e segurança dos gates com
menor custo *até o aceite*, não apenas reduzir tokens de uma chamada. O usuário citou
três papéis centrais; não pediu substituir o Manager humano/host nem eliminar revisão
cross-vendor. Essa preservação é uma hipótese explícita para aprovação.

## Evidência do estado atual

- A Orquestra já diferencia papéis: `orq/agents/orq-planner.md` exige causa raiz,
  aceite, escopo e handoff; `orq/agents/orq-reviewer.md` exige defeito com cenário,
  severidade e teste manual. O Manager vive na skill `orq` e é o único que move cards.
  Portanto a comparação não pode usar um baseline “LLM sem instrução”.
- A via nativa do Claude pode carregar o arquivo do agente. Na via Codex, os commands
  montam briefings e usam `codex exec`/runner; é necessário provar por recibo quais
  instruções de papel chegam ao modelo. O runner Anthropic repassa o briefing pelo
  stdin, com limite 16 KiB; não há prova automática de que o Markdown
  `orq-reviewer.md` foi incluído. Isto é um **risco de paridade**, não defeito já
  confirmado em todas as chamadas.
- O [Agency Agents fixado no T-138](https://github.com/msitarzewski/agency-agents/tree/053ddbbf392a1688fc7043d81529f47ef2cf86c8)
  é uma biblioteca de perfis/instruções Markdown. Isso não treina os pesos da LLM,
  não cria competência comprovada nem fornece ferramentas por si. O
  [Agents Orchestrator](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/specialized/agents-orchestrator.md)
  propõe pipeline autônomo, spawn e retries próprios; não pode substituir o
  Manager canônico sem quebrar autoridade, orçamento e isolamento por card.
  O [Code Reviewer](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-code-reviewer.md)
  traz priorização por correção, segurança, manutenção e testes; adaptar critérios
  úteis é diferente de importar seu workflow completo.

## Três caminhos

1. **Importar os agentes inteiros do upstream.** Menor esforço inicial, porém
   instruções extensas, autoatualização, conflito de autoridade e custo de contexto.
   Rejeitar como desenho de produção.
2. **Especialidades compactas, versionadas e escolhidas por card — recomendado.**
   Manter contratos dos três papéis e adicionar um suplemento pertinente ao domínio
   (por exemplo API, UI/acessibilidade, segurança, documentação/instruções). A seleção
   é declarada no briefing, com SHA, orçamento de tokens e exclusões. Um papel recebe
   no máximo um suplemento no piloto. O Manager conserva as decisões; JEV pode
   sugerir classe/domínio, mas nunca mover card, autorizar execução ou lançar outro
   modelo sozinho.
3. **Fine-tuning ou “treinamento” de modelo.** Só teria sentido com dados e avaliação
   suficientes depois de provar ganho do método por instruções. É caro, dependente
   de fornecedor e não é o que o catálogo Agency Agents entrega. Fora de escopo.

## Contratos candidatos — não são implementação

| Papel | Especialização útil | Limite inviolável |
|---|---|---|
| Manager | Triagem por risco/domínio, preflight de capacidade, orçamento, posse do card, handoff e escolha de *qual* skill considerar | Não vira segundo orquestrador; não delega aprovação, não aceita sugestão JEV como autorização |
| Planner | Método adequado ao domínio: contratos/invariantes para sistema, interação/acessibilidade para interface, dados/ameaças para alto risco; oráculos e instruções ao executor | Não implementa; não inventa requisitos ou amplia escopo |
| Reviewer | Checklist dependente do artefato: instruções do plugin, API, segurança, UI; procura cenário concreto, regressão e mutante que falharia | Continua independente do writer, read-only e cross-vendor; não muda teto de revisões |

O contrato base deve ser único e comprovadamente injetado nas duas vias; o suplemento é
opcional. “Skill treinada” neste desenho significa instrução e exemplos com testes de
regressão, avaliação cega e versão fixada — **não** pesos de modelo treinados.

## Ensaio proposto e dependência JEV

1. **Auditoria offline barata:** comparar os briefings realmente enviados por host com
   os contratos atuais; identificar lacunas, contradições e bytes/tokens de cada suplemento.
   Não usar contagem de palavras como tokens. Redigir fixtures sintéticas, oráculos e
   falhas sem dados reais; a bancada não move cards reais.
2. **Ablation por papel:** fixar *mesmo modelo, effort, prompt da tarefa, ferramentas,
   sandbox e limite de chamadas*; comparar Orquestra atual contra Orquestra + suplemento.
   Manager em simulação read-only; Planner em planos de cards fictícios; Reviewer em
   diffs com defeitos semeados e casos limpos. Avaliador cego ao braço. Medir aceite
   na primeira tentativa, falsos positivos/negativos, regressões, violações de
   autoridade, latência e custo total até aceite.
3. **Só depois testar seleção:** JEV vs regra congelada para sugerir classe/domínio e
   perfil elegível; as políticas de alto risco e autorização sempre prevalecem. O
   T-098/A2 atual mede seis classes de triagem, **não** seleção de skills nem qualidade
   de entregas. A R2 foi bloqueada semanticamente; JEV/Luna A2 seguem 0/4 cada.
   Redesenhar o gabarito com pré-auditoria local antes de pedir outra revisão externa,
   e investigar o uso/custo anômalo do Opus R2.
4. **Gate de adoção:** só ampliar após ganho reproduzível em tarefas distintas sem
   aumentar violação grave, falso bloqueio ou custo total. Piloto pequeno não produz
   significância estatística; resultados negativos também são resultado.

O T-138 mantém o experimento API Tester B2 como efeito de **perfil de domínio no
executor**. O T-139 isola especialização de **papéis centrais**; não misturar os dois
num único “antes/depois”. Nenhuma chamada de modelo adicional foi feita aqui.

## Direção aprovada e retomada — 2026-09-25

O dono aprovou seguir até desenvolvimento e testes, acrescentando **skills adequadas
por papel/domínio** e avaliação de qualidade, sem repetir perguntas sobre decisões
já tomadas. O Manager permanece autoridade única; Planner e Reviewer são o piloto
ativo e Manager fica em simulação read-only. Criei o worktree isolado
`/Users/brunocangucu/.codex/worktrees/t139-role-skills/byia-claude-orquestra`
no commit `a82a35f` e registrei nele `docs/plano_T-139-especializacao-papeis.md`.
O principal continua com alterações de T-098/T-131/T-138/T-139 preservadas; não
há autorização implícita para instalar, publicar ou acionar JEV sobre amostra A2
bloqueada. O próximo trabalho é implementar e testar a composição real dos
briefings, seguida de experimento sintético pareado.

### Checkpoint de recuperação — execução local

No worktree T-139 há `compose-role-briefing.py`, duas skills específicas de
instruções do plugin, testes RED/GREEN e comandos `plan-next`/`revisar` apontando
para composição explícita. O compositor emite contrato-base, no máximo uma
skill allowlisted, digest SHA-256 e tarefa; recusa erro antes de prompt parcial.
Oito testes focados, duas validações de skill e manifesto estrito passaram. O
lint/suíte completos primeiro acusaram nomes de skill confundidos com agentes;
os nomes foram corrigidos sem afrouxar o lint. Resta a trava de versão/cache,
esperada porque `orq/` mudou sem bump nesta etapa.

Casos sintéticos P-001/R-001 e rubrica foram congelados em `docs/T-139-*.md` do
worktree. A primeira chamada real do baseline Planner via `codex exec`, modelo
`gpt-6-astra`, esforço `max`, sandbox read-only, completou: cobriu 5/5 itens de
P-001 sem ação proibida. Houve uma tentativa inicial recusada pelo sandbox
antes de inicializar, seguida de uma chamada efetiva. Como o caso apresentou
teto, o braço com skill desse caso não foi disparado para evitar custo sem
discriminação. Sem chamada Claude/JEV. Próximo: caso mais difícil, ensaio
pareado e prova da via Anthropic, depois gates completos.

Atualização: P-002/A com Luna `medium` também atingiu 5/5, mas reportou
65.620 tokens de entrada (34.304 em cache) para 3.706 bytes de briefing; não
há decomposição causal desse overhead. R-001/A pelo runner Anthropic pediu
`haiku`, porém `modelUsage` indicou `claude-sonnet-5`; o runner recusou
corretamente (exit 7) sem devolver parecer e sem retry. Os recibos e limites
estão em `docs/T-139-resultados-preliminares.md` do worktree. Nove testes
focados de composição/entrega via fake runner e a suíte completa 423/423
passaram; validação das skills e manifesto estrito também. O lint de fonte
continua vermelho apenas pelo cache 0.27.10 instalado versus os comandos
modificados, até um bump/release autorizado. Manager ganhou apenas uma skill
candidata em `docs/`, não exposta como skill ativa do plugin.

Preflight R-003/A em Codex CLI, Luna `low`, com hooks/apps/remote-plugin/memories
desativados apenas para aquela execução e cwd `/private/tmp`, também falhou
como bancada: 64.271 tokens de entrada (48.384 em cache) para 3.718 bytes de
briefing, tentativa de conexão MCP global e busca read-only de caminhos locais
apesar da instrução sem ferramentas. Não houve leitura de conteúdo na busca
observada, mas o contexto externo invalida o isolamento prometido. Parei as
chamadas externas; R-003/B não foi executado. O compositor agora registra
SHA-256 do prompt completo no stderr, coberto por RED/GREEN. Para retomar o
ensaio, é obrigatório provar supressão real de ferramentas/contexto antes de
gastar chamadas pareadas. Não alterar configuração normal do usuário para isso.

Gates locais finais desta etapa: suíte por descoberta `426/426`; manifesto
estrito, validação das duas skills do pacote e `git diff --check` verdes. Lint
de coerência tem **uma** divergência esperada: fonte candidata ainda declara
0.27.10, enquanto o cache instalado 0.27.10 contém comandos antigos. Não
alterei cache, versão, configuração global, elenco, branches remotas ou main
para fazê-lo passar. A skill candidata de Manager segue somente em `docs/`.
Após revisar o risco de adoção precoce, o compositor passou a exigir
`--pilot T-139` para qualquer skill não `none`; os comandos deixam `none` como
padrão fora do ensaio sintético. Houve RED/GREEN dessa guarda e nenhum card
real ganhou suplemento automaticamente.

## Gate de direção (histórico)

**Decisão do dono:** manter o Manager atual como autoridade única e testar suplementos
compactos para os três papéis, começando por Planner/Reviewer e Manager somente em
simulação read-only? **Recomendação: sim.** Aprovar a direção permite escrever a
especificação e o plano de implementação/teste; não aprova ainda instalação, mudança
do elenco, invocação paga, release ou adoção geral.

## ⏭️ RETOMAR AQUI

Direção aprovada pelo dono e T-139 em READY no board canônico. Implementação
local isolada em andamento no worktree T-139, com plano em
`docs/plano_T-139-especializacao-papeis.md` nele. Continuar pela prova de
passagem efetiva da skill nas duas vias e por caso discriminante para o ensaio
de qualidade; os dois baselines atuais já têm efeito-teto, a tentativa
Anthropic não passou no gate de identidade do modelo e o preflight Codex
isolado não suprimiu ferramentas/contexto. T-098/A2 continua
bloqueado; T-138 B2 segue 0/16.
Não instalar, publicar ou reivindicar ganho antes das provas.

Checkpoint após compactação: a raiz instalada 0.27.10 e o board canônico
foram resolvidos novamente (`state=ok`, `exists=true`), e o worktree T-139
permanece isolado. O teste local do runner Anthropic agora confere o SHA-256
do prompt inteiro e rejeita uma mutação de um byte; os 12 testes focados
passaram. A suíte completa foi repetida: 426/426, manifesto estrito e
`git diff --check` verdes; lint somente com a divergência de cache/versionamento
já declarada. Nenhuma chamada externa nova foi feita. `codex exec --help` expõe
`--ignore-user-config`, mas isso é apenas uma possibilidade de preflight,
sem prova ainda de isolamento de ferramentas ou contexto. Detalhe e gate em
`docs/T-139-resultados-preliminares.md` do worktree.

### Checkpoint do preflight e gate de dados — 2026-09-26

Uma chamada sintética **sem código** via `codex exec --ignore-user-config`,
Luna `low` solicitado, diretório temporário vazio e sandbox read-only
respondeu ao marcador; JSONL com zero evento de ferramenta/MCP, 17.381
tokens de entrada e 10 de saída. `--ignore-user-config` é documentado e
`gpt-6-luna` consta do catálogo local; o JSONL não informa o modelo efetivo.
O contexto-base do CLI ainda é substancial. Nenhum par A/B foi executado.

R-004 foi congelado no worktree com fixture/oráculo sintéticos e detecta dois
bloqueadores, um risco de diagnóstico e um controle seguro. Ao tentar o braço
A, a revisão de permissões **rejeitou o processo antes do envio**: o prompt
composto incluiria contrato e skill internos do Orquestra, além do caso
fictício. Não houve retry nem troca de via. Sem inferência local instalada.
O resultado e hashes estão em `docs/T-139-resultados-preliminares.md`.

**Decisão externa exata pendente:** autorizar ou não até duas chamadas
Codex CLI/OpenAI (A e B condicional, Luna `low`, sem retry) que enviem
o contrato `orq/agents/orq-reviewer.md`, a skill
`orq/skills/role-review-plugin-instructions/SKILL.md` no braço B e a fixture
fictícia `docs/T-139-reviewer-caso-04.md` (4.048/5.236 bytes de prompt),
sem PII ou credenciais. Oráculo e resultados ficam locais. Se não autorizado,
manter T-139 experimental, sem alegar ganho de qualidade ou ativar a skill.

Verificação da análise inicial, antes do piloto: raiz instalada 0.27.10 e board canônico resolvidos com
`state=ok`, `exists=true`; T-139 é único no board. Suíte por descoberta
`414/414` em 48,644 s; manifesto estrito, lint de coerência e `git diff --check`
passaram. Esses checks validam o registro e o produto existente, **não** comprovam
ganho de performance dos perfis. Nenhuma chamada adicional de LLM/JEV foi feita.

### Auditoria de escopo do objetivo — 2026-09-25

Na inspeção atual do worktree T-139, `compose-role-briefing.py` possui apenas
`planner` e `reviewer` em `ROLE_FILES` e duas skills do domínio
`plugin-instructions` em `SKILL_FILES`. O teste
`test_manager_cannot_be_dispatched_by_composer` confirma que o Manager não
passa por essa via. Sua candidata `docs/T-139-manager-skill-candidate.md` é
somente uma simulação read-only, não uma skill instalada ou testada em A/B.
O opt-in `--pilot T-139` continua obrigatório; nenhuma seleção por tarefa foi
ativada no produto.

Assim, mesmo que o par R-004 prove benefício para Reviewer, **T-139 ainda não
estará completo** quanto ao pedido do dono: faltam prova discriminante de
Planner, ensaio seguro do Manager sem segunda autoridade, seleção explícita e
falha fechada de skills adequadas por domínio/tarefa e verificação
comportamental dos três papéis com qualidade, custo e violações de gate. O
piloto atual prova tubulação local e preservação de limites, não melhoria
geral. Não usar JEV para escolher skill antes do gate A2 do T-098.

O card permanece `[!]` no board canônico pelo gate de envio R-004; este
registro é auditoria read-only, sem alterar o worktree, os briefings congelados
ou a decisão externa pendente. A leitura do worktree foi pontual e read-only,
sem cópia ou escrita.

Gates locais frescos no worktree candidato: os 12 testes focados do compositor
passaram; suíte completa por descoberta com `PYTHONDONTWRITEBYTECODE=1`,
426/426 em 42,255 s; manifesto `claude plugin validate ./orq --strict`, exit0.
O lint e `git diff --check` do checkout principal também saíram exit0.
Esses resultados comprovam integridade estrutural do candidato, **não**
melhoria empírica de resolução, custo ou cobertura do Manager.

### Pré-auditoria R-004 e candidata R-005 — 2026-09-25

A R-004 não deve consumir o gate externo: o próprio enunciado explicita
quase todos os pontos do oráculo (gate do Manager, ajuda sem `--wait`, stdout
vazio em falha e controles seguros). O único raciocínio pouco guiado é a
semântica geral de `$?` depois de `printf`. Isso torna outro efeito-teto
plausível e a atribuição de ganho à skill fraca; é análise estrutural, não
resultado de modelo. A R-004 e seu oráculo permanecem intactos e a chamada
rejeitada não será repetida.

No worktree T-139 preparei R-005 fictícia, sem PII: três regressões
cross-file/host e dois controles seguros, com oráculo fechado antes de
qualquer inferência. Fixture SHA-256 `262ece1d…c930b0`; oráculo
`8f317071…89b26d91`. O compositor local retornou A/B com 4.393/5.581 bytes
e digests `211a82b0…c7880b31` / `f8db0645…7564db966`, exit0; nenhuma
chamada externa foi feita. Os arquivos completos e os hashes estão em
`docs/T-139-resultados-preliminares.md` do worktree. Se A atingir o teto,
não chamar B. O novo caso continua enviando contrato/skill internos ao
modelo externo, portanto **não elimina o gate de dados**. Sem autorização
específica, parar antes do processo, não trocar de via e não ativar o piloto.

### Gate de desenho do Manager — inspeção local

O plano aprovado limita o Manager a uma simulação read-only, enquanto o
compositor despacha somente Planner/Reviewer e o teste mantém Manager fora
de `ROLE_FILES`. A candidata do Manager ainda mora em `docs/`, não em
`orq/skills/`. O pacote publica skills pelo diretório `orq/skills/`, sem
chave de habilitação por skill no manifesto; a distribuição do Codex exige
verificar a visibilidade em `/skills` após instalação. Logo, mover a candidata
para esse diretório **não é apenas torná-la testável localmente**: há risco
de expô-la aos hosts em um release, antes de medir sua qualidade e de definir
quando ela pode ser carregada. Não foi criada ou ativada outra autoridade.

Desenho limitado proposto, ainda sem implementação: manter a candidata de
Manager fora do pacote instalado; ensaiar decisões hipotéticas com entrada,
saída e oráculo congelados, sem escrita de board, despacho ou modelo auxiliar
com poder de Manager. Somente após benefício e ausência de violações, definir
seleção manual/fail-closed de domínio e integração no skill principal, com
teste de visibilidade e comportamento nos dois hosts. A aprovação anterior
do piloto não especificou essa superfície de distribuição; o gate de desenho
permanece separado do gate externo R-005. Nenhum arquivo do produto foi
alterado nesta inspeção.

### Capacidade de descoberta de skills nos hosts — checagem documental

Após compactação, recuperei `memory/MEMORY.md`, o board canônico pelo resolver
da raiz instalada 0.27.10 (`state=ok`, `exists=true`) e esta thread. O T-139
continua `[!]` e pertencente à `@frente-jev-router @codex`; os worktrees e
arquivos sujos foram preservados.

A frase acima, “sem chave de habilitação por skill no manifesto”, se refere
ao manifesto do **plugin** e não à ausência de qualquer controle nos hosts.
A documentação oficial do Codex prevê `agents/openai.yaml` com
`policy.allow_implicit_invocation: false`: isso barra a escolha implícita, mas
**não** a invocação explícita por `$skill`. Também prevê
`[[skills.config]] enabled = false` no `~/.codex/config.toml` para uma skill
local, com restart; é configuração do host, não default distribuível do
plugin. Fonte: https://learn.chatgpt.com/docs/build-skills (seções “How
ChatGPT and Codex use skills”, “Enable or disable local Codex skills” e
“Optional metadata”).

A documentação oficial do Claude Code prevê
`disable-model-invocation: true` no frontmatter: a descrição não entra no
contexto do modelo até a invocação manual, que continua possível. Portanto
também não é uma proibição absoluta. Fonte:
https://code.claude.com/docs/en/features-overview (seção “Context cost by
feature”). Esses controles ainda **não foram testados neste plugin** nem
instalados nos hosts. A inferência prudente é manter a candidata de Manager
fora de `orq/skills/` durante o piloto; só avaliar empacotamento após ensaio
de descoberta/ativação em ambiente descartável e aprovação do desenho. O
gate R-005 de envio externo permanece separado e fechado.

### M-001 — bancada local do Manager

No worktree isolado T-139, preparei a fixture fictícia
`docs/T-139-manager-caso-01.md` e o oráculo separado
`docs/T-139-manager-rubrica-01.md` antes de qualquer inferência. Os três
cards simulados exercitam domínio adequado, posse de frente e evidência
insuficiente. Hashes completos e ressalvas estão em
`docs/T-139-resultados-preliminares.md` daquele worktree. Nada foi movido no
board; não houve despacho, chamada externa ou instalação. A pré-auditoria
identifica risco de efeito-teto porque parte das regras já consta do
contrato-base; M-001 não é prova de ganho. O gate R-005 do Reviewer continua
pendente e separado da eventual avaliação do Manager.

### P-003 — bancada local do Planner

Também no worktree T-139, preparei o caso fictício
`docs/T-139-planner-caso-03.md` e o oráculo independente
`docs/T-139-planner-rubrica-03.md`. O compositor produziu os dois briefings
locais com sucesso: A 4.577 bytes e B 5.973 bytes; hashes completos estão
em `docs/T-139-resultados-preliminares.md`. Não houve inferência nem custo de
modelo. O caso exige preservar reuso dentro do card sem contaminar outro,
mas a pré-auditoria ainda aponta risco de teto; não afirmar ganho por ter
composto prompts. A suíte local passou 426/426 após M-001; manifesto estrito
e `git diff --check` passaram. O lint do worktree continua vermelho só pela
divergência fonte/cache 0.27.10 em `commands/plan-next.md`, não resolvida por
bump ou instalação nesta etapa.

### Auditoria do compositor — limite antes da leitura

No worktree T-139, uma entrada `--max-bytes` enorme reproduziu
`OverflowError`/traceback porque a CLI lia stdin antes de validar o limite.
Teste novo observado RED (1/13), guarda antes da leitura e GREEN (13/13);
reprodução direta passou a retornar exit 2/`LIMITE_INVALIDO`, sem prompt.
A suíte por descoberta passou 427/427 e o manifesto estrito passou. O lint
continua vermelho pela divergência já conhecida com o cache 0.27.10;
isso não valida qualidade de Planner/Reviewer/Manager nem autoriza release.
Mutation check explícito: remover temporariamente a guarda fez o teste
isolado falhar 1/1; restaurá-la fez o mesmo teste passar 1/1 e a suíte
completa repetir 427/427. A guarda está presente no estado final.

### Tamanho do baseline real do Manager

A skill-base `orq/skills/orq/SKILL.md` tem 35.484 bytes brutos / 34.705
sem frontmatter; candidata 1.405 / 1.209 bytes, e M-001 2.409 bytes.
Logo, o braço A do Manager já excede 16 KiB antes de cabeçalhos: não pode
usar sem adaptação o compositor/limite dos papéis despachados, nem trocar
o baseline por resumo e chamar isso de comparação com o Manager real.
Hashes e medição estão em `docs/T-139-resultados-preliminares.md` do
worktree. É uma restrição de capacidade medida, não custo em tokens nem
qualidade. Não houve A/B, instalação ou alteração do Manager.

### Checkpoint de recuperação — 2026-09-26

Após compactação, reli o índice, resolvi o board canônico pela raiz instalada
0.27.10 (`state=ok`, `exists=true`) e confirmei que T-139 permanece `[!]`,
com posse `@frente-jev-router @codex` e pergunta R-005 ainda sem resposta.
O worktree T-139 continua sujo e isolado; nenhuma chamada de modelo, commit,
push, instalação ou restart foi feita nesta retomada.

Auditoria da prova de entrega: `test_compose_role_briefing.py` já captura os
bytes compostos recebidos pelo runner Anthropic. Na via Codex, o comando
`plan-next.md` manda entregar `PLANNER_PROMPT` ao `codex exec`, mas não há
adaptador executável do piloto para essa entrega. Um binário falso chamado
por um shell de teste provaria o shell de teste, não que o agente seguiu a
instrução; por isso não contei a segunda via como comprovada nem acrescentei
um teste tautológico. O gate de qualidade também segue aberto: P-001/P-002
atingiram teto, P-003/M-001 só têm fixtures locais, e R-005 ainda não foi
executada. A medição de tamanho impede comparar o Manager real sob o limite
de 16 KiB de Planner/Reviewer.

### Pré-auditoria R-005 e caso substituto R-006

R-005 não foi enviada. Os contratos anexos à própria fixture entregavam
diretamente os três critérios que o oráculo pontuaria; outro teto no braço A
era provável e a skill não teria ganho atribuível. Preservei caso e oráculo
sem editar, mas retirei R-005 da fila. A pergunta antiga não autoriza outro
payload.

Preparei R-006 fictícia com dois defeitos que exigem seguir consumidores e
estado: caminho do compositor no host Codex e retomada global da task errada
após perda seletiva do vínculo `(card, papel)`. README é controle seguro.
Fixture, oráculo e hashes estão em `docs/T-139-resultados-preliminares.md` do
worktree. A/B compostos localmente (4.670/5.858 bytes) com exit 0, mas sem
modelo, custo, latência ou ganho medidos. Ainda há risco de efeito-teto;
se A fechar 2/2 sem falso positivo, B não deve ser chamado. O board agora
pergunta especificamente sobre até duas chamadas R-006; sem resposta,
nenhum envio externo. Nenhum outro gate ou instalação foi aberto.
Suíte por descoberta 427/427, manifesto estrito e `git diff --check`
passaram. Lint do worktree segue vermelho só por divergência
`bytes:commands/plan-next.md` com cache 0.27.10, sem bump/instalação.

### M-001 — prompt completo e utilidade da skill candidata

Montei localmente A/B do Manager com a skill-base inteira (sem frontmatter)
e a mesma fixture: 37.248/38.595 bytes, ambos abaixo de 64 KiB; hashes em
`docs/T-139-resultados-preliminares.md`. O compositor do produto continua
recusando `manager`; não houve chamada, segunda autoridade ou movimento de
card. O incremento de 1.347 bytes da candidata é sobretudo a política
explícita de seleção de domínio, uma skill por papel e digest/exclusões.
A base e M-001 já entregam quase todas as regras de posse, aprovação,
read-only e diferença entre hosts. M-001 vale como smoke de autoridade,
não como prova discriminativa de ganho; manter candidata fora de
`orq/skills/` e não expandir esse braço antes de uma bancada melhor.

### P-003 — pré-auditoria de discriminação

Sem chamada de modelo, retirei P-003 da fila: a própria fixture mostra
`F-031`/`F-032` com `t7`, a ausência de guarda de origem no runner, a
inexistência de slash command no Codex e a falta de recibo do vendor.
Esses são quase todos os pontos do oráculo; outro 6/6 no braço A seria
provável e não demonstraria a skill. Preservei fixture e rubrica sem
reescrever o gabarito. Um próximo teste do Planner deve exigir resolução
de tarefa com saída verificável, não comparação direta de frases.

## ⏭️ RETOMAR AQUI

1. Aguardar resposta à pergunta exata do board sobre até duas chamadas
   R-006 Codex CLI/Luna low; não enviar instruções internas do plugin sem
   esse consentimento, não fazer retry e pular B se A atingir o teto.
2. Com autorização, executar a bancada pareada congelada e auditar
   cegamente os oráculos, falsos positivos, violações de escopo, custo e
   latência. Sem autorização, avançar apenas em verificações locais honestas.
3. Antes de alegar paridade de entrega Codex/Claude, obter prova do consumidor
   real da via Codex ou desenhar um adaptador executável sob gate próprio;
   não substituir isso por teste de um binário falso isolado.
4. Para o Planner, não chamar P-003: preparar tarefa de resolução com saída
   verificável e menos resposta embutida no próprio enunciado.
5. Manter o T-098/A2 e o T-138/B2 separados; não adotar, publicar,
   instalar, bumpar ou alterar elenco a partir deste piloto.

### P-004 — caso histórico local, sem modelo

O caso P-003 foi retirado por entregar quase todo o diagnóstico. A bancada
P-004 usa o snapshot anterior à correção histórica do T-071 (`edc51c42`):
dois `awk` do statusline e a guarda Python de posse discordavam sobre a
fronteira da seção arquivada. A fixture traz o contrato de saída e trechos
anteriores à correção; a rubrica fica em arquivo separado, não no prompt.
Arquivos no worktree T-139:

- `docs/T-139-planner-caso-04.md` — 3.681 bytes, SHA-256
  `11d8b1b7b9dfe26b4df1dc3d386ce6a8ca531806e7593616ef155909cc67f5f0`.
- `docs/T-139-planner-rubrica-04.md` — 2.701 bytes, SHA-256
  `031ae9bb28a689b8306c3516c9a8f27dd1e20cbfe4a286196e8e0e7f920554b5`.

Três sintomas foram reproduzidos localmente com expressões do snapshot:
dois falsos cortes no contador e um falso corte na guarda. O compositor
produziu A/B de 5.911/7.307 bytes, com a mesma fixture uma vez e sem o
oráculo. Não houve chamada de modelo, custo, instalação ou alteração de
produto. O caso ainda pode apresentar efeito-teto; só uma execução pareada
e auditada poderá dizer se a skill muda a resolução.

Verificação fresca do worktree: 427/427 testes por descoberta, manifesto
estrito verde e `git diff --check` 0. Lint vermelho apenas por
`bytes:commands/plan-next.md` contra o cache 0.27.10, divergência já
esperada de fonte candidata não instalada; não foi encoberta.

## ⏭️ RETOMAR AQUI

1. Aguardar a resposta ao gate específico da R-006. Sem aprovação explícita,
   não enviar contrato/skill internos nem chamar o modelo; sem retry e omitir
   B se A atingir o teto.
2. P-004 está congelado apenas para ensaio local; eventual envio externo
   precisa de autorização própria, não herdada da R-006. Antes disso,
   pré-auditar o risco de efeito-teto e confirmar que o snapshot basta para
   uma pontuação justa.
3. Manager M-001 continua somente smoke de autoridade, sem papel novo no
   compositor. Não alegar ganho de qualidade, custo ou adoção sem A/B real.
4. Preservar T-098/A2, T-138/B2 e os worktrees alheios; nenhum bump,
   commit, push, instalação ou restart foi aprovado para T-139.

### Fronteira do prompt composto — RED/GREEN local

A candidata tinha um desvio real de entrega: o compositor adicionava LF
final, mas a substituição `$(...)` nos comandos Planner/Reviewer removia
esse byte antes de passar o prompt à via do modelo. O SHA-256 registrado
em stderr era dos bytes **anteriores** a essa transformação. Um teste que
executa os blocos Bash documentados falhou primeiro nos dois papéis por
um byte e passou 14/14 após sentinela de sucesso removida antes do envio.
Skill inválida continuou com exit 2 e prompt vazio; mutação sem sentinela
reproduziu a perda. O compositor e os hashes congelados de R-006/P-004
não mudaram.

Gates frescos no worktree: 428/428 testes, manifesto estrito e
`git diff --check` verdes; Ruff do teste verde sob Python 3.12.12. Lint
segue vermelho só por `bytes:commands/plan-next.md` contra o cache
instalado 0.27.10. Isto prova captura local exata, não entrega à sessão
Codex real nem ganho de qualidade.

## ⏭️ RETOMAR AQUI

1. Aguardando o consentimento específico já apresentado para R-006 com
   instruções internas; sem ele, não chamar Codex CLI nem trocar de rota.
2. A integridade de bytes até a variável shell está coberta por RED/GREEN;
   falta prova do consumidor Codex real e comparação de qualidade A/B.
3. P-004 precisa de pré-auditoria de discriminação e de gate externo próprio.
   M-001 continua somente smoke, não novo Manager operacional.
4. Não bumpar, instalar, publicar, commitar, enviar ou reiniciar T-139
   sem autorização específica. Preservar T-098/A2 e T-138/B2 separados.

### R-006 retirada antes de inferência; R-007 cega preparada

Pré-auditoria encontrou vazamento de resposta em R-006: o próprio caso
afirmava que `CLAUDE_PLUGIN_ROOT` faltava no Codex e que `--resume-last`
retomava a última task global, após mostrar a perda do vínculo de outro
card/papel. Isso entregava exatamente os dois bloqueadores do oráculo.
R-006 foi retirada **sem chamada**; a pergunta de autorização anterior
está obsoleta e eventual resposta a ela não será reaproveitada.

R-007 foi congelada no worktree como revisão fictícia do desvio de bytes
demonstrado em RED/GREEN, com fixture e oráculo separados:

- `docs/T-139-reviewer-caso-07.md`: 2.740 bytes, SHA-256
  `f815ce4b50c2d9c9fd1bf1a744aed9f7eac27c505c2d1548fbff195e791cd369`.
- `docs/T-139-rubrica-07.md`: 2.178 bytes, SHA-256
  `03c32354bab4981902951a469c775a159f7c80fe0dc6b20a7a248eaac03c608f`.

A/B locais de 4.842/6.030 bytes contêm a fixture uma vez, não o oráculo,
e cabem em 16 KiB. O enunciado não revela a semântica de `$(...)` nem a
sentinela que resolveria o problema. Ainda não há inferência, ganho,
custo ou paridade com a sessão Codex real. O board saiu de `[!]` para
`[~]`: o Manager pode avançar localmente sem aguardar a pergunta obsoleta.

## ⏭️ RETOMAR AQUI

1. R-006 está aposentada, inclusive se a autorização antiga chegar.
   R-007 requer gate novo de egress do contrato/skill internos antes de
   uma única A/B via Codex CLI; sem consentimento, só trabalho local.
2. Pré-auditar P-004 quanto a efeito-teto e preservar R-007 cega;
   não reescrever oráculos depois de inferência. M-001 segue smoke.
3. Falta prova do consumidor Codex real e qualidade de resolução A/B.
   A captura local exata do shell não substitui nenhuma dessas duas.
4. Nenhum bump, commit, push, instalação ou restart de T-139 foi
   autorizado. T-098/A2 e T-138/B2 continuam separados.

### Checkpoint de recuperação — caminho padrão de Planner/Reviewer

Após compactação, reli `memory/MEMORY.md`, o board e esta thread; comprovei
`ORQ_PACKAGE_ROOT` absoluto, existente e com `scripts/kanban-status.sh`.
O resolver retornou `state=ok`, `exists=true`, board canônico desta `main`
e `thread_root=memory/wiki`. A frente segue `@frente-jev-router @codex`.

No worktree T-139, os blocos Bash reais de Planner e Reviewer com as duas
variáveis de piloto ausentes retornavam exit 2, `SKILL_DESCONHECIDA` e
briefing vazio. A prosa prometia `none`, mas não o passava. Teste novo
RED em ambos; os comandos usam `${ROLE_SKILL:-none}` e
`${ROLE_PILOT:-none}`. Foco GREEN 15/15; remover esses defaults numa
mutação apenas em memória reconstituiu a falha. Suíte 429/429, manifesto,
Ruff e diff-check verdes. Lint da candidata exit 1 somente pela fonte
T-139 diferente do cache instalado 0.27.10 (`bytes:commands/plan-next.md`).
Detalhes em `docs/T-139-resultados-preliminares.md` do worktree.

## ⏭️ RETOMAR AQUI

1. R-007 cega e P-004 seguem locais, sem inferência; pré-auditar P-004
   quanto ao efeito-teto antes de qualquer chamada.
2. Qualidade de resolução A/B e consumidor Codex real não foram provados.
   R-007/P-004 exigem consentimento de egress específico e separado.
3. Não bumpar, commitar, enviar, instalar, publicar ou reiniciar T-139
   sem autorização; preservar os trabalhos de outras frentes.

### Pré-auditoria P-004 — evitar efeito-teto antes de egress

A comparação local da fixture com a rubrica mostrou que o enunciado já
entrega os três leitores, a tabela de títulos, as regras de cerca/linha,
LF/CRLF, bytes/locales, exemplos e arquivos afetados. A maior parte dos
seis critérios pode ser satisfeita reorganizando esses dados; não houve
resposta de modelo nem pontuação observada. P-004 fica preservada como
controle de compreensão, **não** como prova de ganho da skill. R-007 segue
cega e pronta localmente. Evidência detalhada no documento de resultados
do worktree T-139.

## ⏭️ RETOMAR AQUI

1. Preparar caso Planner mais discriminante, com rubrica independente e
   dados suficientes para avaliação justa; não enviar P-004 como A/B.
2. R-007 requer consentimento específico para egress do contrato e skill
   internos antes de A/B; a autorização antiga de R-006 não vale.
3. Falta prova do consumidor Codex real e ganho reproduzível de resolução.
   Sem bump, commit, push, publicação, instalação ou restart.

### P-005 preparada sem chamada externa

No worktree, `docs/T-139-planner-caso-05.md` e
`docs/T-139-planner-rubrica-05.md` substituem P-004 como candidata de
qualidade do Planner. A nova fixture dá sintomas, contrato mínimo e fonte,
mas não a tabela de solução nem a decomposição do oráculo. A/B compõem
4.780/6.176 bytes; o caso aparece uma vez, oráculo ausente, ambos abaixo
de 16 KiB. Hashes e ressalva de possível efeito-teto estão em
`docs/T-139-resultados-preliminares.md`. Não houve inferência nem envio.

## ⏭️ RETOMAR AQUI

1. R-007 (Reviewer) e P-005 (Planner) são candidatas locais, não resultados.
   Cada A/B exige consentimento próprio para egress de contrato/skill internos;
   se A atingir o teto, não gastar B.
2. Provar entrega ao consumidor Codex real e ganho de resolução em tarefas
   distintas antes de qualquer adoção. Manager M-001 segue smoke read-only.
3. Preservar T-098/A2 e T-138/B2; nenhum bump, commit, push, publicação,
   instalação ou restart de T-139 foi autorizado.

Checagem local complementar: os blocos de composição de Planner e Reviewer
foram executados em `bash` e `zsh`, com e sem opt-in, em oito combinações.
Todas saíram 0 e deram bytes/digest idênticos ao compositor; isso ainda
não é prova de entrega ao modelo.

### Gate externo consolidado — decisão do dono

Para medir **resolução**, e não só composição, faltam A/B reais em duas
fixtures fictícias: R-007 (Reviewer) e P-005 (Planner). A proposta de menor
custo é usar `codex exec` com `gpt-6-luna` em `low`, mesmo modelo/effort,
sandbox read-only, sem ferramentas deliberadas e mesmo limite de saída
dentro de cada par. Cada caso recebe uma chamada A sem skill; B com a skill
somente se A não atingir o teto. Limite máximo: quatro chamadas A/B no total,
zero retry. Se isolamento, via ou modelo solicitado não puderem ser
comprovados de forma suficiente, parar e rotular o resultado inválido; não
substituir modelo silenciosamente.

O envio inclui os casos fictícios e **instruções internas do Orquestra**:
contrato-base do Planner/Reviewer, skill suplementar no braço B e hashes.
Não inclui PII, dado de paciente, credenciais ou `.env`. O texto sairá da
máquina para OpenAI pelo Codex CLI. O preflight anterior sem configuração
do usuário registrou 17.381 tokens de entrada e zero evento de ferramenta,
mas não forneceu recibo inequívoco do modelo; portanto este primeiro A/B
seria exploratório e **não** provaria custo/qualidade de produção sozinho.

Decisão exata pendente: o dono autoriza separadamente os envios de R-007 e
P-005 nesse protocolo limitado? A aprovação antiga de R-006 é obsoleta.
Sem consentimento explícito, não executar nenhuma das chamadas. Nenhum
commit, push, bump, publicação, instalação ou restart está incluído.

## ⏭️ RETOMAR AQUI

1. T-139 está em `[!]` aguardando autorização específica de egress para
   R-007 e P-005; não confundir com aprovação de plano ou de R-006.
2. Se autorizado, rodar no máximo 1 A e 1 B por caso, B só sem teto;
   registrar recibos, invalidar desvios e auditar rubricas congeladas.
3. Mesmo após A/B, faltará repetição em tarefas distintas e prova da via
   de produção para adoção. Preservar T-098/A2, T-138/B2 e todo estado sujo.

### Auditoria local do Manager — não gastar chamada em M-001

O contrato-base instalado do Manager tem 35.484 bytes. Base + M-001 somam
37.893 bytes, e com a skill candidata seriam 39.298, antes de qualquer
moldura: o runner Anthropic de 16 KiB não é via viável para esse A/B.
Além disso, o caso já informa domínio, ausência de aprovação, posse de
outra frente e incerteza de causa, que são os quatro resultados centrais
da rubrica. M-001 permanece smoke de autoridade, não teste de ganho de
resolução. A skill candidata do Manager existe só em `docs/`, sem ativação.
Detalhes em `docs/T-139-resultados-preliminares.md` do worktree. O gate
R-007/P-005 acima não inclui Manager nem autoriza chamada adicional.

Sonda read-only do `codex-cli 0.156.1`: `codex exec` aceita stdin,
`--ephemeral`, `--ignore-user-config`, sandbox, modelo e JSONL, mas a ajuda
não oferece recibo de skill carregada. O ensaio Manager explícito teria
ao menos 37.893/39.298 bytes; carregar a skill implicitamente reduziria
o prompt visível sem provar paridade. Sem chamada, custo observado ou
autorização de egress para M-001.

### Checkpoint de recuperação — 2026-09-26

Após compactação, reli o índice, resolvi o board instalado com `state=ok` e
`exists=true` e confirmei T-139 em `[!] @frente-jev-router @codex`. A main
continua com alterações compartilhadas; o worktree T-139 preserva o piloto
isolado. O lint da main e `git diff --check` nos dois checkouts saíram 0 nesta
retomada. No worktree, a suíte por descoberta passou 429/429 e o manifesto
estrito passou; o lint saiu 1 apenas pela divergência esperada entre a
candidata sem bump e o cache instalado 0.27.10
(`bytes:commands/plan-next.md`). Nenhuma chamada de modelo ocorreu.

O plano aprovado permite Manager apenas em simulação read-only. M-001 informa
explicitamente as pistas centrais e permanece controle de autoridade, não
comparação discriminativa. `codex exec` oferece passagem explícita do prompt,
mas não recibo documentado de skill carregada; portanto não usar carregamento
implícito para baratear um A/B e depois afirmar paridade. Reexecutei a
composição local dos braços A/B de R-007 e P-005: os quatro hashes congelados
batem, cada fixture aparece uma vez e seu oráculo não está no prompt. Isto
valida a preparação, não a discriminação nem o resultado. O passo local
seguinte foi preparar M-002, com oráculo separado. O gate
externo de R-007/P-005 continua pendente e não se estende ao Manager. Sem
bump, commit, push, publicação, instalação ou restart.

### Manager M-002 — caso e oráculo congelados localmente

No worktree T-139, `docs/T-139-manager-caso-02.md` confronta o Manager com
domínio versus título, posse do card, teto do briefing do papel despachado,
fonte versus sessão viva, aprovação e anexo real não sanitizado **sem conter o
anexo**. `docs/T-139-manager-rubrica-02.md` é o oráculo independente. O braço
A explícito tem 37.961 bytes e o B, com skill candidata, 39.302; os hashes
reproduzíveis estão em `docs/T-139-resultados-preliminares.md`. O caso entra
uma vez por braço e o oráculo não entra em nenhum. O runner Anthropic de
16 KiB não comporta esse par; não houve inferência nem envio ao Codex CLI.
Se A fizer 6/6, B será omitido e M-002 ficará como controle, sem alegação
artificial de ganho. O gate externo de R-007/P-005 não autoriza M-002.

Pré-auditoria posterior, ainda **sem inferência**, encontrou efeito-teto
provável: os fatos de cada registro já fornecem domínio, posse, ausência
de evidência ou números do teto; a própria simulação proíbe movimentação
e chamadas. Rebaixei M-002 a controle de compreensão/autoridade e retirei-o
da bancada de ganho de qualidade. Não gastar chamada externa nele; preservar
o caso e o oráculo congelados como evidência do desenho rejeitado.

Conferi a documentação oficial do `codex exec --json`: o JSONL documenta
eventos e uso, mas não promete recibo de modelo. Uma sessão persistida local
de `codex_exec` continha `turn_context.model`, que comprova apenas a seleção
do cliente e não corresponde ao preflight efêmero deste card. Portanto o
futuro A/B R-007/P-005, se autorizado, continua exploratório enquanto não
houver prova mais forte do modelo efetivo. Evidência e link oficial no
relatório do worktree; não houve nova chamada de modelo.

### Checkpoint — opt-in isolado por chamada, 2026-09-26

Após a compactação, reli o índice, confirmei a raiz instalada 0.27.10 e
resolvi o board canônico (`state=ok`, `exists=true`). O T-139 continua
`[!] @frente-jev-router @codex`; a main e o worktree conservam suas
alterações sem commit.

Encontrei uma falha de isolamento no piloto: valores antigos de `ROLE_SKILL`
e `ROLE_PILOT` no ambiente ativavam a skill especializada mesmo em outro
card. Reproduzi com uma tarefa T-999 fictícia nos blocos Bash reais de Planner
e Reviewer; o teste RED falhou nos dois. No worktree T-139, ambos os blocos
agora fixam `none` a cada invocação, e a documentação exige substituir
explicitamente as duas atribuições somente no ensaio autorizado. O teste
GREEN em Bash/Zsh, o caminho de opt-in explícito e a suíte por descoberta passaram
**430/430**; manifesto estrito, Ruff e `git diff --check` passaram. O lint
do worktree continua vermelho só por `bytes:commands/plan-next.md` contra o
cache instalado 0.27.10 — divergência esperada de candidata sem bump.
Detalhes em `docs/T-139-resultados-preliminares.md` do worktree.

⏭️ RETOMAR AQUI: R-007/P-005 permanecem congelados e aguardam autorização
específica para enviar contrato, skill e casos fictícios em A/B externo.
Sem essa decisão, não inferir ganho, custo ou modelo efetivo. M-001/M-002
continuam controles locais, T-098/A2 e T-138/B2 são frentes distintas.
Não houve chamada de modelo, bump, commit, push, publicação, instalação
nem restart neste checkpoint.

### Checkpoint — gate do runner exercitado de ponta a ponta

No worktree T-139, executei os blocos reais de composição e despacho do
Reviewer em sequência com um runner local falso. Antes da correção, o lote
vazio produzia `BRIEFING_EMPTY`, mas o bloco seguinte ainda abria o runner
e marcava `OPUS_EXIT=0`: teste RED reproduzido. Agora a chamada só ocorre
com composição exit 0 e prompt não vazio; o caso inválido registra
`OPUS_EXIT=2` e revisão degradada sem abrir o processo. No caso válido,
o runner recebeu exatamente os bytes da composição piloto; uma mutação de
um byte no envio foi detectada. Status malformado com prompt antigo também
foi reproduzido em RED e agora falha fechado. Detalhes no relatório do worktree.

Verificações frescas: suíte por descoberta **432/432**, manifesto estrito,
Ruff e `git diff --check` verdes. Lint do candidato continua exit 1 somente
pela divergência esperada `bytes:commands/plan-next.md` versus cache 0.27.10
sem bump. Sem chamada externa, commit, push, publicação, instalação ou restart.

⏭️ RETOMAR AQUI: a integridade local de entrega está mais forte, mas a
melhoria de qualidade de Planner/Reviewer **não foi medida**. R-007 e P-005
continuam congelados, aguardando a autorização específica de egress descrita
acima; M-001/M-002 continuam controles locais inadequados para alegar ganho
do Manager. Preservar T-098/A2 e T-138/B2 separados.

### Revalidação local dos A/B congelados

Recompus R-007 A/B e P-005 A/B após os ajustes de despacho: os quatro
SHA-256 ainda batem com o relatório do worktree. O preflight verificou
mesmo contrato-base e mesma tarefa por par, caso uma vez, skill só no B,
oráculo fora do prompt e menos de 16 KiB em cada braço; exit 0, sem modelo.
Nenhum runner local foi encontrado nas vias `ollama`, `llama-cli`, `mlx_lm`
e `llama-server` deste PATH, o que não prova ausência absoluta de modelo
local. Não usar esta sessão informada pelo oráculo como avaliador cego.

⏭️ RETOMAR AQUI: os pacotes estão íntegros, mas o A/B de qualidade ainda
não ocorreu. O gate específico de egress R-007/P-005 continua pendente;
não extrapolar autorização antiga nem afirmar economia/ganho. Sem bump,
commit, push, publicação, instalação ou restart.

### Checkpoint de recuperação — Manager M-003 local

Após a compactação, reli `memory/MEMORY.md`, resolvi o board canônico pelo
pacote instalado 0.27.10 (`state=ok`, `exists=true`) e reli este card/thread.
O worktree T-139 permanece isolado. R-007/P-005 continuam congelados;
uma pergunta assíncrona de consentimento específico para até quatro envios
Codex CLI foi exibida ao dono, **sem resposta registrada até este checkpoint**.
Não tratar a aceitação da exibição como autorização de egress.

Avancei somente na bancada local do Manager: `docs/T-139-manager-caso-03.md`
e `docs/T-139-manager-rubrica-03.md` são fixture fictícia e oráculo separado.
O caso cruza patch de instruções com código, sandbox do Reviewer, limite
integral do briefing, escopo aprovado e fonte versus sessão viva. A soma
crítica exige inferência: 14.980 + 1.405 = 16.385 > 16.384. A composição
preliminar A/B em memória confirmou caso uma vez, skill só em B e oráculo
ausente; não é pacote congelado nem resposta de modelo. Há risco residual de
efeito-teto do Manager base; não chamar o caso de prova discriminante ainda.
Recibos e limites em `docs/T-139-resultados-preliminares.md` do worktree.
Na pré-auditoria do próprio autor, M-003 também se mostrou propenso a teto:
fica como controle local de segurança, não entra em A/B de ganho. Os gates
frescos do candidato foram suíte **432/432**, manifesto estrito e
`git diff --check` verdes; lint `exit 1` apenas por divergência
`bytes:commands/plan-next.md` do cache 0.27.10 sem bump.

⏭️ RETOMAR AQUI: se vier autorização específica, executar somente o protocolo
R-007/P-005 já delimitado, sem extrapolar para Manager M-003. Caso contrário,
continuar pré-auditoria local do Manager e preservar as demais frentes. Sem
bump, commit, push, publicação, instalação, restart ou chamada externa neste
checkpoint.

### Alternativa de inferência local — checagem adicional

Para evitar egress enquanto o gate R-007/P-005 está pendente, verifiquei
mais do que o `PATH`: não apareceu app Ollama, LM Studio, GPT4All ou Jan em
`/Applications`, `~/Applications` ou no Spotlight; `launchctl list` não
mostrou serviço correspondente; as APIs loopback usuais nas portas 11434,
1234 e 8080 não responderam (`HTTP 000`). `ps` foi negado pelo sandbox, então
isto **não prova ausência absoluta** de modelo local, mas não há runner
offline utilizável identificado nesta sessão. Não instalar modelo, não
trocar a via externa por outra silenciosamente e não alterar o gate do
ensaio.

### Pré-auditoria de qualidade dos pares congelados

R-007 e P-005 foram recompostos pela função real do compositor, não por
transcrição manual: os quatro hashes permanecem idênticos aos congelados,
com 4.842/6.030 bytes no Reviewer e 4.780/6.176 no Planner. O oráculo
completo não entra nos prompts. A varredura local de padrões de e-mail,
chave privada, token e caminho pessoal retornou zero nos quatro braços;
isto não substitui uma revisão humana de privacidade. As skills tampouco
contêm literalmente as respostas críticas dos casos. O baseline ainda
pode chegar ao teto, portanto não há alegação de benefício.

O plano do worktree agora pré-registra a leitura dos resultados: R-007/P-005
serão apenas exploratórios; uso limitado exigirá tarefas distintas e
controle sem defeito; adoção exigirá qualidade de resolução end-to-end,
custo até aceite, ausência de violação de gate e prova da via efetiva.
Planner/Reviewer não provam ganho do Manager. O gate específico de egress
continua fechado até resposta do dono; nenhum modelo foi chamado neste
checkpoint, nem houve bump, commit, push, publicação, instalação ou restart.

### Preparo cego da avaliação A/B

O worktree T-139 agora contém `docs/t139_blind_ab.py` e
`docs/test_t139_blind_ab.py`. A bancada conserva os bytes das duas
respostas, sorteia os rótulos candidato 1/2, guarda a chave A/B em
`sealed/` e entrega ao avaliador só `blind/`. Recusa vazamento explícito
do braço, resposta vazia/não UTF-8 e diretório preexistente; artefatos são
privados ao usuário. Cinco testes foram vistos em RED/GREEN e passaram.
Suíte do plugin **432/432**, manifesto estrito e Ruff sem cache verdes.
O lint permanece vermelho apenas pela divergência já conhecida da fonte
T-139 frente ao cache instalado 0.27.10. Nenhuma resposta real foi
produzida ou pontuada; cegamento procedimental não substitui modelo
identificado, rubrica independente nem gate de egress.

⏭️ RETOMAR AQUI: o próximo passo válido continua sendo a decisão específica
de enviar ou não os quatro prompts máximos R-007/P-005 ao Codex CLI. Se
autorizado, executar A primeiro, omitir B em efeito-teto, anonimizar saídas,
congelar notas e só então revelar o mapeamento. Sem essa decisão, não
simular qualidade; Manager segue fora do pacote e em ensaio read-only.

### Checkpoint de recuperação após compactação — 2026-09-26

Na retomada, a raiz instalada 0.27.10 e o resolvedor do board foram verificados
(`state=ok`, `exists=true`). O quadro mantém T-139 em `[!] @frente-jev-router
@codex`; o worktree isolado conserva o piloto não commitado. O último gate
local documentado é suíte 432/432, manifesto estrito e Ruff verdes, com lint
divergente apenas do cache instalado. Este turno foi de leitura e resumo ao
dono: não houve inferência, egress, bump, commit, push, instalação ou restart.
Permanece o gate específico de dados R-007/P-005; nenhuma alegação de ganho
de qualidade ou adoção foi feita.

### Gate externo autorizado, ensaio inválido — 2026-09-26

O dono respondeu `autorizo` ao gate específico de R-007/P-005. Recompus os
quatro prompts e confirmei bytes, hashes congelados e ausência dos padrões
testados de e-mail, caminho pessoal, chave privada e token; os oráculos
permaneceram fora dos briefings. Executei somente R-007/A, R-007/B e P-005/A
via Codex CLI 0.156.1, solicitando Luna `low`, configuração do usuário
ignorada, sandbox read-only, diretório temporário e ferramentas desativadas.
Não houve retry nem chamada de P-005/B.

Os três JSONL mostram um item de erro de inicialização **antes do turno**:
`Code Mode is unavailable because code-mode host is disabled`. Não há evento
de ferramenta/MCP nem recibo de modelo efetivo. R-007/A achou a falha do LF
mas inventou outro bloqueador; R-007/B recusou revisar sem workspace;
P-005/A recusou planejar sem ferramentas e citou o erro do code-mode.
Consequentemente, o par R-007 não é comparável e P-005 nem formou par.
Não pontuar ganho, economia ou adoção. Os seis artefatos originais e hashes
estão no worktree, em `docs/experimentos/T-139/`; análise detalhada em
`docs/T-139-resultados-preliminares.md`.

A causa observada atravessa duas fronteiras: desabilitar
`features.code_mode_host` gera erro visível na sessão; o ensaio sem
ferramentas conflita com contratos-base e skill que pedem verificar
consumidores reais. Ainda não foi isolado quanto cada fator afetou as
respostas, portanto não corrigir por palpite nem usar o quarto envio como
retry. T-139 passa a `[~]` para diagnóstico/preflight local de novo
protocolo. A autorização presente não cobre uma nova chamada externa.
Sem bump, commit, push, instalação, publicação ou restart.

⏭️ RETOMAR AQUI: fechar o preflight local sem chamada de modelo, definir
um snapshot sintético e via comparável sem erro de inicialização, congelar
novo caso/oráculo, então apresentar um gate externo delimitado. Qualidade
real de Planner/Reviewer e Manager continua não demonstrada.

### Recuperação após compactação — 2026-09-26

Raiz instalada 0.27.10 e `scripts/kanban-status.sh` confirmados; o resolvedor
retornou `state=ok`, `exists=true` e os caminhos canônicos do board e das
threads. Índice, quadro e esta thread foram relidos antes de continuar.
No worktree T-139, a suíte por `discover` passou (432/432), o manifesto
estrito passou e `git diff --check` passou. O lint segue vermelho apenas
pela fonte candidata diferente do cache 0.27.10 instalado em
`bytes:commands/plan-next.md`; não é evidência de falha dos testes nem
autorização para instalar. O mesmo `git diff --check` passou na main.
Nenhuma chamada externa adicional foi feita nesta retomada; P-005/B segue
omitida e o piloto permanece sem resultado comparável.

### Checkpoint local R-008/P-006 — 2026-09-26

O worktree isolado ganhou uma bancada sintética nova, sem reaproveitar o
gate consumido de R-007/P-005. `docs/t139_trial_gate.py` classificou os
três JSONL anteriores como `INVALID/STARTUP_ERROR`. R-008 fornece ao
Reviewer arquivos reais fictícios para inspeção read-only; P-006 permite
ao Planner produzir apenas um plano numa cópia temporária. Rubricas ficam
fora dos workspaces. `docs/t139_trial_setup.py` gera A/B com o compositor
real, marcador sintético, hashes e permissões privadas;
`docs/t139_trial_run.py` exige hashes aprovados e executa no máximo um braço
por invocação, sem retry, com recibo estrutural mesmo em erro.

Uma prova **local, sem inferência**, com `codex sandbox -P` confirmou leitura
somente no workspace do Reviewer e escrita somente no workspace do Planner;
não prova a aplicação do perfil no `codex exec` nem a identidade do modelo.
Os hashes completos e limites estão em
`docs/T-139-resultados-preliminares.md`. Bancada 30/30, suíte do plugin
432/432, Ruff sem cache, manifesto estrito e `git diff --check` verdes.
O lint ainda acusa apenas a fonte candidata diferente do cache 0.27.10.
Não houve chamada nova de modelo, evidência de ganho/custo, bump, commit,
push, publicação, instalação ou restart.

⏭️ RETOMAR AQUI: antes de qualquer ensaio real, obter autorização nova e
delimitada para os hashes R-008/P-006; começar por A e omitir B se A atingir
o teto. Mesmo um par válido seria exploratório. Qualidade end-to-end,
replicação em tarefas distintas por papel, controle limpo e Manager seguem
pendentes antes de adoção.

### Checkpoint da nota vinculada — 2026-09-26

No mesmo worktree T-139, o manifesto congela agora hash e teto (6) da
rubrica independente, além dos prompts e workspaces. O runner exige
aprovação explícita de rubrica, modelo e effort e recusa papel adulterado
que elevaria a permissão do Reviewer. Cada recibo registra hash da resposta
e, no Planner, dos bytes do plano. B só pode sair após nota A com seis
critérios 0/1, evidência por item e hashes coincidentes com recibo,
rubrica e plano. Os testes RED/GREEN cobriram nota velha, critério vazio,
plano alterado, rubrica/máximo adulterados e modelo/effort divergentes;
o positivo de ambos os papéis também passou. A ficha humana está em
`docs/T-139-ficha-avaliacao.md`, e os hashes novos em
`docs/T-139-resultados-preliminares.md`.

Bancada local **44/44**, suíte do plugin **432/432**, manifesto estrito,
Ruff sem cache e `git diff --check` verdes nesta etapa. O lint ainda acusa
somente a divergência fonte/cache 0.27.10 em `commands/plan-next.md`; nenhuma
resposta real foi pontuada. O gate R-008/P-006 continua fechado até
autorização específica de egress. Sem bump, commit, push, publicação,
instalação ou restart.

### Recuperação e controle limpo R-009 — 2026-09-26

Após compactação, raiz Orquestra 0.27.10 e resolvedor canônico foram
verificados (`state=ok`, `exists=true`); índice, board e esta thread foram
relidos antes da edição. No worktree T-139, o controle fictício R-009 do
Reviewer foi criado com rubrica separada. RED: caso desconhecido e compositor
ausente. GREEN: os dois consumidores recebem bytes exatos por arquivo,
inclusive LF final; falha de composição e saída vazia bloqueiam despacho;
arquivo temporário é limpo. O patch é reversível contra os arquivos mostrados.

Bancada **46/46**, suíte do plugin **432/432**, Ruff sem cache, manifesto
estrito e `git diff --check` passaram. O lint segue acusando somente
divergência esperada fonte/cache 0.27.10 em `commands/plan-next.md`.
Não houve chamada externa, bump, commit, push, publicação, instalação nem
restart. R-009 ainda não mede falsos positivos reais. Próximo trabalho local:
controle limpo do Planner; depois congelar snapshot e pedir gate delimitado
para cada A/B. Adoção continua sem evidência suficiente.

### Controle limpo P-007 e checkpoint — 2026-09-26

O Planner agora tem controle distinto: o relato fictício de versão não bate
com a fonte, pois os quatro anchors são 0.4.2. A fixture inclui índice,
board, thread, quatro anchors e verificador. RED antes da fixture; GREEN
com leitura coerente e mutação do README que faz o verificador falhar. O
runner aceita somente `docs/plano_P-007.md` para esse caso e bloqueia B se
o plano A mudar depois da nota; o positivo de B também passou no teste fake.

Bancada local **50/50**, suíte do plugin **432/432**, Ruff sem cache,
manifesto estrito e `git diff --check` verdes. O lint permanece vermelho
somente pela divergência esperada fonte/cache 0.27.10 em
`commands/plan-next.md`. Nenhuma chamada real de modelo, bump, commit,
push, publicação, instalação ou restart. R-009/P-007 são controles
preparados, não resultados de qualidade. Próxima decisão: gate delimitado
para iniciar A/B dos snapshots revisados; B só se A ficar abaixo do teto.
Antes de adoção, replicar em ao menos três tarefas distintas por papel e
medir custo até aceite, sem violar gates.

### Terceiras tarefas por papel — 2026-09-26

R-010 semeia um override de acesso no comando Reviewer: o padrão
`--readonly` é trocável por `FAROL_REVIEW_ACCESS=--write`. Teste local
executou o bloco com runner fictício e observou o efeito de escrita; o
patch reverso corresponde à fonte. P-008 semeia um resolvedor que mantém
o board canônico da main, mas calcula `thread_root` da mesma main ao operar
num worktree. O teste executou o checkpoint **somente em cópia temporária**
e confirmou escrita na thread errada. Oráculos de ambos estão fora dos
workspaces/briefings. RED/GREEN foi observado; bancada **55/55**, suíte
do plugin **432/432** e Ruff sem cache passaram.

Há agora três tarefas distintas preparadas para Planner e Reviewer, com
um controle sem defeito por papel. Isso ainda não é replicação de respostas:
nenhum dos novos casos foi enviado a modelo. O gate externo anterior de
R-007/P-005 foi consumido e não se transfere. Congelar hashes e obter
autorização específica antes de A/B; B somente se A válido abaixo do teto.
Sem bump, commit, push, publicação, instalação ou restart.

### Correção do gate de comparabilidade — 2026-09-26

Pré-auditoria local revelou que B podia sair com modelo/effort diferentes
de A, ou com recibo A adulterado quanto a caso, braço, prompt e workspace.
Três testes RED comprovaram aceitação indevida; GREEN bloqueia essas vias
antes da CLI. Bancada **58/58**. A prova é de consistência dos valores
solicitados, não de identidade do modelo efetivo. Nenhuma nova chamada de
modelo foi feita. Os seis casos seguem preparados, sem pontuação.

### Congelamento local dos seis casos — 2026-09-26

`docs/T-139-preflight-freeze.json` fixa hashes de tarefa, rubrica,
workspace e prompts A/B para R-008/R-009/R-010/P-006/P-007/P-008. Teste
recompõe os seis em diretórios temporários e compara os hashes; RED por
artefato ausente, GREEN **59/59**. `codex exec --help` na CLI 0.156.1
reconhece as flags usadas, mas não houve chamada real nem recibo do modelo
efetivo. O congelamento é candidato para autorização, não autorização.
Nenhuma chamada externa adicional, bump, commit, push, instalação ou restart.

### Checkpoint de recuperação e pausa do lote A — 2026-09-26

Após compactação, comprovei a raiz Orquestra 0.27.10 e o resolvedor canônico
(`state=ok`, `exists=true`), reli índice, board e esta thread. No worktree
isolado T-139, acrescentei teste de entrega byte a byte do prompt aprovado
à CLI fictícia. RED quando o fake não capturava stdin; uma mutação que removeu
`input=prompt` também falhou; GREEN com o runner original. A bancada passou
**60/60** e a suíte do plugin **432/432**; manifesto estrito, Ruff e
`git diff --check` passaram. O lint da fonte candidata continua divergindo
do cache instalado 0.27.10 em `commands/plan-next.md`, sem bump/instalação.

As seis cópias temporárias bateram com todos os hashes congelados. O dono
respondeu “autorizo” ao pedido de até seis chamadas A sintéticas Luna `low`,
sem PII, credenciais ou retry. **Só R-008/A executou**: recibo
`STRUCTURAL_ONLY`, exit 0, workspace inalterado, cinco eventos de ferramenta
de leitura local, 117.347 tokens de entrada (99.840 em cache), 827 de saída.
`effective_model` segue `null`. Artefatos brutos foram preservados em
`docs/experimentos/T-139/runs/R-008/A/` do worktree. Leitura provisória do
Manager: **1/6**, pois perdeu a causa do LF final em ambos os consumidores;
não é avaliação independente, nem nota selada que autorize B.

R-009/A foi recusada pela revisão de permissões **antes da CLI**: o pacote
leva instruções e patch internos do projeto a destino externo, e a
autorização foi julgada insuficientemente específica para esse conteúdo.
Não houve retry nem R-010/P-006/P-007/P-008, tampouco B, bump, commit,
push, publicação, instalação ou restart. O card fica em `[!]` com posse
`@codex` preservada. Para retomar: obter gate explícito para o payload
interno sintético e destino OpenAI via Codex CLI, submeter novamente à
revisão de permissões e só então continuar A sem refazer R-008. Após A,
pontuação independente e B somente abaixo do teto com novo gate. Não alegar
ganho de qualidade, economia ou adoção.

### Contrato local do braço B — 2026-09-26

O plano aprovado mantém o Manager somente em simulação de leitura; não foi
criada nem ativada skill operacional dele. O teste da CLI fictícia passou a
comparar também os bytes exatos do briefing **B** aprovado (com skill de
domínio), além do A. Mutação local que enviou stdin vazio apenas em B fez o
teste falhar; restaurado `input=prompt`, a bancada passou **61/61**. Não
houve nova chamada externa ou alteração dos seis snapshots congelados.
Permanece o mesmo gate de egress para os cinco A não executados; B continua
dependente de nota A independente abaixo do teto e autorização própria.

O inventário `docs/T-139-inventario-egress-A.md` no worktree lista destino,
conteúdo interno real versus arquivos fictícios, hashes e limites de cada
um dos cinco A restantes. É material para a decisão e para a revisão de
permissões, **não** autorização. Nenhuma chamada externa foi tentada nesta
etapa local.

### Guarda de snapshot no runner — 2026-09-26

RED local: alterar o prompt A e atualizar `manifest.json` mais os hashes
fornecidos na chamada permitia despachar à CLI fictícia, apesar da
divergência com `T-139-preflight-freeze.json`. GREEN: o runner compara
tarefa, rubrica, workspaces e os dois prompts com o snapshot congelado
antes de chamar a CLI. A bancada passou **62/62**; nenhum snapshot foi
modificado e não houve egress. A guarda não é assinatura de autorização:
o gate externo específico continua pendente.

### Checkpoint de recuperação e gate A consumido parcialmente — 2026-09-26

Após compactação, comprovei `ORQ_PACKAGE_ROOT` existente com
`scripts/kanban-status.sh`, resolvi o board canônico (`state=ok`,
`exists=true`) e reli índice, board e esta thread. O dono aprovou
explicitamente o inventário de egress dos cinco A restantes, com contratos
internos reais do Orquestra, workspaces fictícios congelados, destino OpenAI
via Codex CLI, Luna `low`, uma chamada por caso e sem retry. Bancada local
62/62 e hashes conferidos antes da primeira chamada; R-008/A não foi
repetido.

R-009/A e R-010/A saíram `STRUCTURAL_ONLY`, sem razões de invalidação,
workspace intacto e `effective_model: null`; R-009/A registrou 96.531
tokens de entrada (72.704 em cache), 825 de saída, e R-010/A 76.870
(61.440 em cache), 585 de saída. R-010/A identificou o override de escrita
semeado; R-009/A apontou dois supostos defeitos no controle limpo, ainda
sem auditoria de falso positivo ou nota independente.

P-006/A saiu `INVALID` por `PLAN_MISSING`: arquivo de plano com zero bytes.
O JSONL registra falhas do shell e `python3` com `xcode-select: No developer
tools` no perfil isolado. A CLI saiu 0, mas a capacidade de gravação do
Planner não foi comprovada; não pontuar esse caso como falha de raciocínio.
Foram 212.792 tokens de entrada (178.944 em cache) e 7.162 de saída.
Sem retry, P-007/A ou P-008/A; os três pacotes de evidência foram copiados
byte a byte para `docs/experimentos/T-139/runs/` do worktree T-139.

⏭️ RETOMAR AQUI: diagnosticar e provar localmente a escrita do Planner em
fixture descartável, sem novo envio nem repetição de P-006/A. Depois decidir
se os dois A ainda não usados podem seguir sob o gate existente; B continua
fora do escopo e exige nota independente válida abaixo do teto e gate
próprio. Sem bump, commit, push, publicação, instalação ou restart.

### Checkpoint de recuperação — seis A encerrados, nota pendente — 2026-09-26

Após a compactação, confirmei a raiz absoluta do pacote Orquestra, o
resolvedor com `state=ok`/`exists=true`, e reli índice, board e esta thread.
O estado anterior acima fica como histórico: a prova local do Planner foi
feita **sem modelo**. O sandbox bloqueava a leitura de
`/Library/Developer/CommandLineTools`; o perfil macOS do piloto agora
permite somente essa leitura, preservando a vedação ao tmp geral, à pasta
pessoal e à rede. O teste aninhado passou no ambiente com permissão de
sandbox; a versão sem essa permissão falha antes da execução do código.

P-007/A e P-008/A consumiram a única chamada aprovada cada, sem retry, com
recibos `STRUCTURAL_ONLY`, plano não vazio e workspace intacto. R-008/A,
R-009/A e R-010/A também têm recibos estruturais válidos. P-006/A fica
`INVALID` por plano vazio e **não** será reexecutado sob outro nome.
Os seis A somam 807.502 tokens de entrada reportados (693.760 em cache)
e 14.810 de saída; isto não mede custo em dólares nem ganho até aceite.
`effective_model` continua nulo nos recibos. Respostas, planos e JSONL
permanecem em `docs/experimentos/T-139/runs/` do worktree isolado.

Preparei localmente cinco briefings de avaliação A com rubrica, resposta e
plano quando aplicável, vinculados pelos hashes e sem rótulo do braço.
O inventário exato é `docs/T-139-inventario-egress-avaliacao-A.md`; **nada
foi enviado** ao Anthropic nesta etapa. A bancada T-139 passou 70/70 com
o teste de sandbox permitido, a suíte do plugin 432/432, manifesto estrito
e Ruff verdes. O lint do worktree continua vermelho somente pela fonte
0.27.10 candidata diferente do cache instalado em `commands/plan-next.md`.
Mutação com `braço A` e hash de recibo atualizado revelou falha de anonimato;
a guarda Unicode agora a recusa. Outra mutação com caminho pessoal também
foi recusada. Os cinco briefings permaneceram byte a byte iguais.

⏭️ RETOMAR AQUI: pedir gate específico para no máximo cinco briefings
sintéticos de hashes registrados, via Claude CLI/Anthropic alias `opus`,
uma chamada por caso, ferramentas desabilitadas, sem retry. Auditar as
notas independentes antes de qualquer B; B exigirá gate próprio e só cabe
se A ficar abaixo do teto. P-006 exige uma terceira tarefa Planner nova
para replicação, não retry. Não há prova de economia, assertividade ou
adoção. Sem bump, commit, push, publicação, instalação ou restart.

### Nota A completa antes de B — 2026-09-26

O gate local de B ignorava os indicadores separados de falso achado crítico
e violação de escopo, embora a ficha os pedisse. Testes RED mostraram que
nota com indicador ausente ou textual disparava B. GREEN exige ambos como
booleanos e mantém B possível quando A teve falso positivo: isso permite
medir se a skill corrige o baseline, sem confundir a falha de A com veto
à candidata. Nenhuma nota real foi atribuída, nenhuma chamada B ocorreu.
Bancada T-139 **73/73**, suíte do plugin **432/432**, manifesto estrito e
Ruff verdes; lint do worktree vermelho apenas pela divergência já conhecida
fonte/cache 0.27.10. Os cinco briefings e hashes da avaliação não mudaram.

⏭️ RETOMAR AQUI: aguardar resposta ao gate único, já solicitado no app,
para enviar ao Anthropic via Claude CLI alias `opus` os cinco briefings
sintéticos do inventário, uma tentativa por caso, sem ferramentas/retry.
Depois auditar e vincular as notas. B continua sem autorização e depende
de A válido abaixo do teto; adoção exige replicação e custo até aceite.

### Checkpoint de recuperação e bancada P-009 — 2026-09-26

Após a compactação, confirmei a raiz absoluta do pacote Orquestra
`0.27.10`, o resolvedor do quadro com `state=ok` e `exists=true`, e reli
índice, board e esta thread. O worktree T-139 continua isolado; a main
compartilhada tem alterações de outras frentes e nenhuma foi descartada.

P-006/A continua inválido e sem retry. Preparei no worktree P-009 como
terceiro caso sintético Planner futuro: uma sonda fictícia reproduz bypass
do teto de quatro revisões e da parada por duas reavaliações sem progresso
após retomada, além de um estado corrompido que falha aberto. Há controle
permitido e controle bloqueado. Rubrica fica separada do workspace. Testes
RED/GREEN da fixture passaram; bancada T-139 **76/76**, suíte do plugin
**432/432**, manifesto estrito e Ruff verdes. Os briefings locais A/B são
distintos (3.189/4.585 bytes) e não contêm o oráculo. O lint do candidato
segue vermelho somente pela divergência fonte/cache já conhecida de
`commands/plan-next.md`.

P-009 não foi congelado, registrado no runner nem enviado a modelo. Os
cinco briefings de avaliação A e hashes originais não mudaram. Continuam
pendentes a resposta ao gate específico de egress já solicitado no app,
a avaliação independente A e, só depois de nota válida abaixo do teto,
um gate separado para B. Sem ganho, economia ou adoção demonstrados; sem
bump, commit, push, publicação, instalação ou restart.

⏭️ RETOMAR AQUI: aguardar o gate para os cinco briefings sintéticos já
inventariados; não incluir P-009 nessa autorização. Manter P-006/A inválido
e não repetir. Auditar notas A antes de qualquer B; replicação Planner com
P-009 requer congelamento e autorização próprios.

### Guarda dos briefings de avaliação — 2026-09-26

Encontrei um bypass da fronteira entre dado e instrução no gerador de nota:
resposta ou plano com `</candidato_resposta>`/`</candidato_plano>` e recibo
atualizado eram aceitos e podiam inserir uma falsa rubrica no briefing.
Dois testes executáveis reproduziram o pacote indevido (RED). A correção
rejeita marcadores estruturais reservados nos dados candidatos antes da
montagem (GREEN). Os cinco briefings A existentes foram recompostos e
mantiveram bytes e SHA-256 do inventário.

Bancada T-139 **78/78**, suíte do plugin **432/432**, manifesto estrito,
Ruff e `git diff --check` verdes. O lint do worktree segue vermelho apenas
pela divergência fonte/cache 0.27.10 já registrada. A main compartilhada
continua suja; nada dela foi descartado. Nenhuma chamada externa, nota,
B, bump, commit, push, publicação, instalação ou restart nesta etapa.

⏭️ RETOMAR AQUI: o gate de egress dos cinco briefings de nota já foi
solicitado no app e ainda não foi atendido nesta conversa. Não incluir
P-009 no lote. Se aprovado, executar no máximo as cinco chamadas
inventariadas, uma por caso, sem retry; auditar notas e recibos antes de
pedir qualquer B. Sem prova de ganho ou custo até aceite.

### Preflight separado P-009 — 2026-09-26

Para não alterar o congelamento dos seis casos nem os cinco briefings A
pendentes de nota, registrei P-009 apenas em
`docs/T-139-P009-preflight-local.json` do worktree. O snapshot vincula
task, rubrica, fixture e prompts A/B por SHA-256; marca `LOCAL_ONLY`,
`runner_registered: false`, `egress_authorized: false` e zero chamadas.
Teste RED/GREEN de recomposição passou, e o preparador real ainda recusa
P-009 com `CASO_DESCONHECIDO`. A tentativa de mutation check por mudança
temporária do hash no arquivo foi bloqueada pelo auto-review; não contornei
o bloqueio e nenhum hash foi alterado.

Bancada T-139 **79/79**, suíte do plugin **432/432**, manifesto estrito,
Ruff e `git diff --check` verdes. Lint do candidato segue vermelho só
pela divergência fonte/cache conhecida. Nenhum modelo, nota, B, bump,
commit, push, publicação, instalação ou restart nesta etapa.

⏭️ RETOMAR AQUI: aguardar resposta ao gate específico, já solicitado no
app, para os cinco briefings A inventariados. P-009 não participa desse
lote e continua rejeitado pelo runner; eventual execução exige integração
separada, congelamento de chamada e autorização própria. Sem prova de
qualidade ou economia até aceite.

### Cinco pareceres A recebidos e auditados — 2026-09-26

O dono respondeu “aprovo” ao gate específico que nomeava os cinco
briefings sintéticos do inventário, destino Anthropic via Claude CLI alias
`opus`, uma chamada por caso, sem ferramentas e sem retry. A primeira
tentativa foi barrada pelo auto-review antes de iniciar; reapresentei a
pergunta aprovada e o hash do caso, e a permissão foi concedida. Depois
executei exatamente R-008, R-009, R-010, P-007 e P-008, uma vez cada.
O runner confirmou `claude-opus-5-5` em `modelUsage` nas cinco saídas.

Os cinco briefings mantiveram os hashes do inventário. Em cada diretório
`docs/experimentos/T-139/grading-A/<caso>/`, preservei `model-output.txt`
bruto, `model-grade.json` como devolvido e `audited-grade.json` ligado aos
hashes de pacote, recibo, resposta/plano e rubrica. Auditoria local dos
cinco vínculos e das somas dos seis critérios: **5/5**. Notas: R-008 1/6
(achado crítico fabricado), R-009 2/6 (achado crítico fabricado), R-010
5/6, P-007 5/6 e P-008 5/6; nenhuma violação de escopo indicada.

R-009 saiu com formato bruto divergente: `false_critical` e
`scope_violation` eram objetos `{present, evidence}`, não booleanos. Sem
repetir modelo, o arquivo auditado converteu exclusivamente os dois
`present` em booleanos e declara `normalization`; score, critérios e
evidências permaneceram intactos e a saída original segue preservada.
Os outros quatro pareceres já tinham formato válido. A leitura local dos
exemplos fictícios confirmou os achados principais, mas a pontuação A
isolada não demonstra ganho ou economia.

P-006/A continua inválido e sem retry. P-009 não entrou no lote. Nenhum
braço B, segundo avaliador cego, bump, commit, push, publicação,
instalação ou restart foi executado. O próximo gate é **separado**:
autorizar, ou não, os hashes de B após preflight; não reutilizar a
aprovação destas cinco notas. Só depois comparar pares, replicar e medir
custo até aceite antes de decidir adoção.

⏭️ RETOMAR AQUI: preparar preflight e inventário de B em leitura/local,
sem chamada de modelo; pedir autorização específica ao dono para o lote
B antes de egress. A nota A auditada não é licença automática para B.
Verificação desta etapa: bancada 79/79 após liberar somente o teste de
sandbox aninhado, suíte do plugin 432/432, manifesto estrito e
`git diff --check` verdes; lint da main verde. O lint da candidata ainda
aponta apenas divergência fonte/cache 0.27.10 em
`commands/plan-next.md`, não uma regressão nova desta avaliação.

### Inventário local de B — 2026-09-26

Sem executar modelo, recompus os cinco prompts B e os digests das fixtures
fictícias. Os hashes coincidem com `T-139-preflight-freeze.json` e com
`docs/T-139-inventario-egress-B.md` do worktree: cinco prompts, 20.993
bytes diretos. O documento explicita também os hashes de workspace e
rubrica, o modelo `gpt-6-luna`/`low`, o perfil isolado e que código
sintético poderá sair via saída de ferramenta local. A triagem de padrões
sensíveis em prompts/fixtures retornou zero ocorrências. Uma checagem
read-only adicional confirmou **5/5 A** com recibo `STRUCTURAL_ONLY`,
workspace intacto, modelo/effort pedidos, hashes de resposta/plano/rubrica
e nota auditada abaixo do teto. **Nenhum B foi chamado ou autorizado.**
Ainda falta reconstruir a bancada temporária e vincular as notas A
auditadas antes de cada preflight de B.

⏭️ RETOMAR AQUI: se o dono aprovar especificamente o inventário B,
reconstruir/prevalidar cada bancada e então executar no máximo uma chamada
por caso, sem retry. Não reutilizar a autorização das cinco notas A;
parar antes de egress se qualquer hash ou recibo divergir.

### Ensaio de reconstrução de B sem egress — 2026-09-26

Em `/private/tmp` criei cinco bancadas novas com o preparador local,
copiei somente os recibos, respostas, notas A auditadas e dois planos
fictícios, e confirmei **5/5** vínculos A com os manifestos. Chamei só a
função de preflight com os campos de aprovação vazios: os cinco casos
pararam exatamente em `EGRESS_NAO_AUTORIZADO`, depois das verificações
de prompt/fixture/congelamento. Não houve `codex exec` nem modelo.

A auditoria inicial encontrou dez permissões excessivas criadas pela
cópia manual (cinco diretórios `responses/` e cinco notas A). Corrigi
somente as cópias temporárias; a auditoria final mostrou **0/216**
caminhos acessíveis a grupo/outros. O inventário B agora exige `umask
077`, diretórios `0700`, arquivos `0600` e nova auditoria antes de
qualquer egress. As cinco cópias temporárias foram removidas após a
verificação; nenhum arquivo da fonte foi modificado por esse ensaio.

⏭️ RETOMAR AQUI: sem gate B, não chamar modelo. Com gate B, reconstruir
em temp privado, repetir preflight completo e permissões e parar em
qualquer drift. Não reaproveitar a aprovação A nem presumir que o ensaio
prova o comportamento externo.

### Linha de base de uso A — 2026-09-26

Os cinco recibos A somam 594.710 `input_tokens`, 514.816
`cached_input_tokens`, 7.648 `output_tokens` e 84
`reasoning_output_tokens`. São métricas de recibo, não preço; os tokens
cached são um subtipo da entrada, não parcela a somar de novo. Todos
pediram `gpt-6-luna`/`low`, mas `effective_model` permanece `null` e o
JSONL não registra o modelo. Sem prova de via/modelo efetivos e sem B,
qualquer cálculo de economia ou ganho seria prematuro. Preservar rótulo
exploratório até o gate de qualidade e custo até aceite do plano.

### Checkpoint após compactação — 2026-09-26

Relidos o índice, o board canônico (`state=ok`, `exists=true`) e esta thread
com a raiz instalada 0.27.10 validada. O T-139 permanece `[!]` em
`@frente-jev-router @codex`; os cinco pareceres A continuam auditados e
nenhum B foi chamado. O plano do worktree mantém Manager somente em
simulação read-only; M-001/M-003 são controles de autoridade sujeitos a
efeito-teto, não evidência de benefício. Sem resposta pareada B, ainda não
há teste de ganho, economia ou qualidade até aceite que justifique adoção.
O ensaio local já cobriu reconstrução, vínculos e permissões; repeti-lo
sem mudança de estado não acrescentaria evidência. Próximo gate: aprovação
específica do inventário B antes de qualquer egress. Sem bump, commit,
push, instalação, publicação ou restart neste checkpoint.

### Meta do Codex e gate B — 2026-09-26

O dono pediu continuidade sem pausas. A meta desta conversa foi marcada
`blocked` pelo agente depois de turnos repetidos sem caminho local novo;
isso é estado do Codex, **não** bloqueio do context-guard/Orquestra. O gate
material permanece: os cinco prompts B e trechos fictícios da fixture
sairiam da máquina via `codex exec`, e a aprovação anterior cobria somente
a avaliação A. Foi apresentada uma pergunta assíncrona única sobre o lote B;
a exibição da pergunta **não é autorização**. Não recomeçar o lote sem uma
resposta afirmativa específica e sem conferir novamente hashes, workspace,
permissões e recibos A. Pi foi analisado separadamente no T-140 e não serve
como via alternativa para contornar este gate.

⏭️ RETOMAR AQUI: se o dono autorizar B, executar no máximo as cinco chamadas
congeladas, uma por caso e sem retry, seguidas de nota cega e revisão dos
recibos. A continuação automática da meta depende de o estado `blocked` ser
retomado no Codex; nenhum arquivo do Orquestra consegue reativá-la.

Checkpoint de recuperação após compactação: índice, board canônico e esta
thread relidos em 2026-09-26; T-139 continua `[!]`, o estado da meta no Codex
continua `blocked` e não houve autorização nova nem chamada B.

### Controle local adicional do Manager — 2026-09-26

No worktree T-139, M-004 acrescenta um caso fictício e uma rubrica separada
para medir **falso bloqueio** e falso encaixe de domínio: um patch de
instruções já aprovado pode seguir para revisão read-only, enquanto um card
de telemetria de outra frente não deve ser capturado. Não alterei os seis
snapshots A/B congelados nem chamei modelo. É preparação de avaliação, não
prova de qualidade ou de economia. Próximo gate externo continua sendo a
autorização específica dos cinco braços B. A meta no Codex voltou a `active`
após a retomada, sem mudar esse limite de egress.

Verificação local: suíte por descoberta 432/432 e manifesto estrito verdes;
`git diff --check` do plano passou. O lint do worktree segue vermelho apenas
porque `commands/plan-next.md` da candidata 0.27.10 difere do cache instalado
0.27.10; não instalar ou bumpar para mascarar isso antes da avaliação. M-004
não teve resposta de modelo nem nota, e o card permanece `[!]`.

Auditoria da via Claude-host encontrou a dependência T-090 ainda real no
Companion Codex 1.0.6: `task` não lista `--wait` entre as opções. Uma sonda
minha, equivocadamente executada em vez de apenas inspecionar o parser,
criou a task Codex `01a0dfca-d7f7-7e90-a0df-7cfbb0475c51` com prompt literal
`--wait`; o único retorno foi “Certo. Aguardo sua próxima instrução.”, sem
código ou dados do projeto. Não era chamada B e não altera os recibos A/B.
Tentei arquivar a task concluída, mas o app respondeu `active writer` duas
vezes; não forcei exclusão. Não repetir a sonda. A paridade de entrega nos
dois hosts depende da correção T-090 e teste comportamental próprio.

Checagem local de proveniência do modelo A: o runner de T-139 usa
`codex exec --ephemeral` e o JSONL de R-008/A contém `thread_id`, mas nenhum
campo de modelo. Não encontrei sessão persistida correspondente em
`~/.codex/sessions/2026/09/26`; portanto, não há recibo retrospectivo de
modelo efetivo a extrair desses arquivos. Os cinco A continuam rotulados
como modelo **solicitado**, não efetivo. Não alterar a opção `--ephemeral`
nem criar chats novos apenas para fabricar essa prova sem desenho e gate
próprios; comparar B como exploratório se a via continuar sem recibo.

### Checkpoint de recuperação — cinco braços B, 2026-09-26

O dono autorizou o inventário B congelado de cinco casos. Recompus as
bancadas em `/private/tmp`, vinculei os cinco recibos, respostas, notas A
auditadas e os dois planos A, e rodei o preflight completo: **5/5**
passaram com os hashes de prompt, fixture e rubrica aprovados, modelo
solicitado `gpt-6-luna` e effort `low`. Antes do envio, **0/227** caminhos
tinham permissões de grupo/outros e a varredura de prompt/fixture B não
encontrou PII ou credenciais.

R-008, R-009, R-010, P-007 e P-008 foram chamados **uma vez cada, sem
retry**. Os cinco recibos B são `STRUCTURAL_ONLY`, com `cli_exit=0`,
`workspace_integrity=UNCHANGED`, hashes de resposta presentes e, nos dois
Planners, hashes de plano presentes. A cópia dos artefatos gerados em
`docs/experimentos/T-139/runs/<caso>/B/` bate com os originais temporários.
O total B foi 700.041 tokens de entrada (565.504 deles em cache) e 11.258
de saída. `effective_model` continua `null` nos cinco recibos: a via/modelo
efetivos não estão provados pelo JSONL. Não converter isso em custo ou ganho.

RED/GREEN ampliou `t139_grade_packet.py` para montar pacotes de A ou B,
preservando o rótulo do braço só no recibo local. Cinco pacotes B foram
preparados em `docs/experimentos/T-139/grading-B/<caso>/`, todos abaixo do
teto de 16 KiB; P-008 tem 15.872 bytes. Bancada T-139 **82/82**, suíte do
plugin **432/432**, manifesto estrito, Ruff via Python 3.12.12 e
`git diff --check` verdes. O lint de coerência continua vermelho pela
divergência candidata/cache `bytes:commands/plan-next.md` na versão ainda
não instalada 0.27.10; não mascarar por instalação sem gate.

O guardião de contexto do Orquestra permanece consultivo. A parada anterior
da meta foi estado `blocked` aplicado pelo agente Codex quando faltava o
gate B, não falha do hook. A meta agora está `active`; chamadas longas são
aguardadas com atualizações, não interrompidas. O estudo do Pi vive no
T-140 e não muda a prova T-139.

⏭️ RETOMAR AQUI: auditar os cinco pacotes B e obter pontuação independente
somente com gate específico para novo envio ao Anthropic; enquanto isso,
prosseguir com análise local e replicação que não exija egress. P-006/A
permanece inválido, P-009 local-only, Manager sem prova externa. Não há
adoção, bump, commit, push, publicação, instalação ou restart autorizados
por este checkpoint.

### Auditoria de cegamento e oráculo — 2026-09-26

Antes de enviar qualquer pacote B para pontuação, uma inspeção local
encontrou caminhos `workspaces/A|B/` dentro das respostas. Três briefings
A já pontuados (R-009, P-007 e P-008) carregavam esse marcador; R-008/A
e R-010/A não. Nenhum pacote B de pontuação havia saído. RED/GREEN
neutralizou o prefixo temporário no texto do pacote **depois** de vincular
o hash da resposta original ao recibo; marcador remanescente falha fechado.
Dez pacotes v2 A/B foram reconstruídos e auditados: zero caminhos de braço
ou temporários, hashes íntegros e todos abaixo de 16 KiB. Os cinco B
anteriores, não enviados, ficaram em `grading-B-leaky-preaudit/`.

Outro achado é material: a rubrica de R-009 chama o caso de controle limpo
e proíbe o bloqueador de recibo, mas a memória da própria fixture exige
que o Manager compare o recibo de tamanho/SHA aos bytes recebidos; os
comandos não mostram essa comparação. O par R-009 é ambíguo e **não deve
ser usado como prova** sem novo caso congelado. Em R-008/B, o Reviewer
produziu achado alto falso: disse que o prompt vira valor de `--readonly`,
embora o comando real o passe como último argumento posicional. R-010/B
apontou o override de escrita plantado; P-007/B e P-008/B produziram planos
vinculados, mas ainda sem nota independente. Detalhes e evidências em
`../../../docs/T-139-auditoria-local-B.md`.

Verificações após a correção: bancada T-139 **83/83**, suíte do plugin
**432/432**, manifesto estrito, Ruff e `git diff --check` verdes. O lint
da candidata mantém somente o desvio fonte/cache pré-existente
`bytes:commands/plan-next.md`. A autorização para B não cobre reavaliar
A, enviar B ao Anthropic, novas tarefas/modelos nem adoção.

⏭️ RETOMAR AQUI: tratar as notas A antigas de R-009/P-007/P-008 como
evidência parcial, não cega; excluir R-009 da comparação limpa; preparar
novo controle sem contradição e orçamento/gate de avaliação independente
somente depois de fechar os pacotes. Não repetir as chamadas B. Manter
T-139 em curso e a meta do Codex ativa enquanto houver trabalho local.

### Checkpoint de recuperação e controle R-011 — 2026-09-26

Após a compactação, reli `memory/MEMORY.md`, o board canônico devolvido por
`kanban-status.sh --resolver .` (`state=ok`, `exists=true`) e esta thread.
A meta nativa do Codex está `active`. O teste do guardião do Orquestra para
`Stop` e `UserPromptSubmit` em bandas consultivas confirma que ele não
retorna `decision=block`; a pausa anterior decorreu da decisão do agente de
marcar a meta `blocked` enquanto aguardava gate de egress, não do hook.

No worktree T-139, montei R-011 como controle limpo substituto, sem alterar
R-009 congelado. A fixture não tem contrato de recibo/SHA; oráculo fica
fora do workspace. RED reproduziu caso desconhecido e fixture ausente;
GREEN exercitou em shell o comando real com runner sintético para sucesso,
falha do compositor e saída vazia. `git apply --reverse --check` validou o
patch. O preparador gerou manifesto local com A/B idênticos e prompts
distintos, `model_calls=0`; freeze local vinculada por teste, hashes e
orçamento proposto de no máximo nove
chamadas futuras, sem retry, estão em
`../../../docs/T-139-auditoria-local-B.md`. Nenhum novo envio ocorreu.

Bancada T-139 **85/85** antes da freeze e **86/86** após, suíte do plugin
**432/432**, manifesto estrito,
Ruff e `git diff --check` verdes. O lint da candidata segue vermelho
apenas pelo desvio fonte/cache conhecido `bytes:commands/plan-next.md`;
não instalar nem bumpar para mascarar. T-140/Pi segue backlog opcional,
sem acoplamento durante o experimento T-139.

⏭️ RETOMAR AQUI: auditar e congelar o R-011 antes de qualquer egress; notas
A antigas de P-007/P-008 não são cegas, R-009 fica excluído e R-008/B
já falhou localmente. O próximo gate externo precisa discriminar chamadas
de candidato e de avaliador, com teto de nove e sem retry. Enquanto isso,
continuar análise local do Manager, replicação e prova de custo/modelo, sem
pausar a meta por simples espera de gate. Nenhuma adoção, bump, commit, push,
publicação, instalação ou restart foram autorizados neste checkpoint.

### Telemetria A/B auditada sem chamada nova — 2026-09-26

Conferi os dez recibos A/B já gravados, dos cinco pares executados. A soma
de `turn.completed.usage` é A: 594.710 tokens de entrada (514.816 em cache)
e 7.648 de saída; B: 700.041 de entrada (565.504 em cache) e 11.258 de
saída. Portanto, B consumiu 105.331 tokens de entrada e 3.610 de saída
a mais no lote observado, sem que isso prove custo faturado ou qualidade.
R-009 segue excluído da comparação de qualidade. Os dez recibos têm
`effective_model=null`, e os dez JSONL não contêm campo estrutural de
`model` nem `effort`; o runner prova somente o modelo solicitado. Registrei
os números e limites em `../../../docs/T-139-auditoria-local-B.md`.

Auditoria local dos comandos candidatos confirmou que
`PLANNER_TASK_BRIEFING` e `REVIEWER_LOTE_SANITIZADO` apareciam somente no
bloco de shell, sem origem textual explícita. Esclareci que são o briefing
do card e o briefing sanitizado **deste lote**, respectivamente, e que
valor ausente não deve ser herdado. A mudança não ativa skills. Após ela,
bancada T-139 86/86, suíte 432/432, manifesto estrito, Ruff e
`git diff --check` seguem verdes; o lint mantém somente a divergência
fonte/cache 0.27.10 conhecida.

⏭️ RETOMAR AQUI: manter R-011 congelado e local, sem executar A/B; não
alegar economia ou identidade efetiva do modelo com estes recibos. Preparar
prova independente de qualidade/custo até aceite por gate próprio, sem
repetir os cinco B. A meta nativa do Codex continua `active`; novo gate
externo não torna impossível o trabalho local.

### Inventário mínimo de egress preparado — 2026-09-26

Para evitar repetir chamadas caras, congelei o próximo lote proposto em
`../../../docs/T-139-inventario-egress-pos-B.md`: cinco pacotes de pontuação
já existentes, total 51.274 bytes, com tamanho e SHA-256 conferidos no
filesystem. São R-010/B, P-007/A v2 e B, P-008/A v2 e B. O destino proposto
é Anthropic via Claude CLI, no máximo uma chamada por pacote e zero retry;
os A anteriores foram avaliados por `claude-opus-5-5`, então mudança desse
modelo invalida comparabilidade. R-011/A é um gate posterior distinto;
seu prompt tem 2.741 bytes e a fixture fictícia 2.628 bytes. Seu pacote
de avaliação ainda não existe, e B é condicional à nota A. A triagem
sensível dos cinco pacotes e R-011, com `senha` como palavra inteira para
não capturar `redesenhar`, deu zero ocorrências; ainda exige inspeção antes
de qualquer envio. **Inventário não é autorização** e nenhuma chamada nova
foi feita.

⏭️ RETOMAR AQUI: a meta segue ativa. Fazer a próxima avaliação somente
após gate explícito para os cinco hashes fixos, sem retry. Não incluir
R-009 nem R-008/B, não enviar R-011 por arrasto e não afirmar economia.
O Pi T-140 ganhou hipótese concreta de recibo de modelo/uso, mas continua
piloto isolado, não substituto de um braço já congelado.

### Checkpoint pós-compactação e pré-auditoria do Manager — 2026-09-26

Confirmei novamente o pacote instalado 0.27.10, o resolver canônico
(`state=ok`, `exists=true`), o índice, o board e esta thread. O card T-139
permanece `[~] @frente-jev-router @codex`; a meta nativa do Codex segue
ativa. Nenhum gate externo pendente foi interpretado como autorização para
nova chamada.

No worktree T-139, a candidata documental do Manager passou a pedir a
**próxima ação autorizada**, não um novo gate por padrão. Uma aprovação
existente para o mesmo card e escopo deve ser utilizada; só decisão nova ou
ampliação de escopo requer outro gate. A pré-auditoria de M-001 a M-004 está
em `../../../docs/T-139-auditoria-local-B.md`: M-001 tem efeito-teto,
M-002/M-003 mostram estados `[>]` incompatíveis com plano já aprovado e
M-004 é o controle local de falso bloqueador e falso encaixe de domínio.
As fixtures M-002/M-003 não foram reescritas. Os bytes/hashes do contrato,
candidata, caso e oráculo M-004 ficaram registrados; o contrato real do
Manager tem 35.484 bytes e excede sozinho a via Anthropic de 16 KiB. Não
truncar nem executar M-004 por essa via sem desenho e gate próprios.

⏭️ RETOMAR AQUI: continuar a bancada local T-139; pontuar os cinco pacotes
congelados somente se chegar autorização específica para os hashes do
inventário, sem retry. R-011 e M-004 continuam locais. Não alegar economia,
ganho de qualidade, modelo efetivo nem adoção geral; sem bump, commit, push,
publicação, instalação ou restart.

### Auditoria local de eficiência e qualidade dos planos — 2026-09-26

Revalidei os recibos A/B por caso e os planos P-007/P-008 contra as rubricas,
sem chamar modelo. A tabela completa está em
`../../../docs/T-139-auditoria-local-B.md`. P-007/B gastou 238.691 tokens de
entrada e 5.206 de saída, contra 121.203 e 2.200 em A; foi o principal
responsável pelo aumento bruto do lote. A nota A antiga foi 5/6 por ausência
de prova de regressão. B menciona o resultado de um anchor divergente, mas
não prescreve inequivocamente alterar um anchor numa cópia controlada;
portanto não lhe atribuí ganho por leitura local. P-008/B nomeia o mutante
`board.parent`, ainda sem pontuação cega ou teste de solução até aceite. As
fixtures já têm testes comportamentais para os defeitos semeados; não os
dupliquei. O resultado continua inconclusivo para qualidade e desfavorável
à hipótese de economia bruta nesta amostra.
Após a auditoria, os sete testes das fixtures sintéticas passaram e
`git diff --check` permaneceu limpo no worktree e na main.

⏭️ RETOMAR AQUI: preservar os pacotes e hashes congelados. Não repetir A/B
nem atribuir nota independente localmente. O próximo envio ao avaliador
externo continua dependente de autorização específica; pode-se executar
menos que o teto proposto se a auditoria justificar economia de chamadas.
R-011/M-004 permanecem locais, e a meta segue ativa.

### Integridade da tarefa no briefing composto — 2026-09-26

No worktree isolado T-139, encontrei uma perda de bytes anterior ao
despacho: os commands preservavam o LF do shell, mas o compositor removia
espaços/quebras nas bordas da tarefa com `task.strip()` e acrescentava LF
próprio. Um lote de revisão sanitizado podia, portanto, ser alterado antes
do runner. Escrevi teste de ponta a ponta do CLI com lote sintético indentado
e CRLF final: RED reproduziu a falha; GREEN preserva exatamente os bytes
recebidos após o cabeçalho do card. Não mudei seleção de skill, piloto,
permissões nem cache. Detalhes na auditoria do worktree.

Gates locais após a correção: compositor 19/19, suíte do plugin 433/433,
bancada T-139 86/86, manifesto estrito e `git diff --check` verdes. O lint
segue vermelho somente pela divergência fonte/cache 0.27.10 já conhecida.
Ruff não estava disponível no `pyenv` ativo; não o instalei. Nenhuma chamada
externa, bump, commit, push, publicação, instalação ou restart ocorreu.

⏭️ RETOMAR AQUI: continuar a verificação local da entrega exata nas duas
vias sem reescrever prompts A/B congelados. A prova de ganho reproduzível e
custo até aceite continua ausente; as cinco notas cegas externas exigem gate
específico. T-139 não está pronto para adoção.

### Checkpoint de recuperação e teste do despacho — 2026-09-26

Após compactação, reli `memory/MEMORY.md`, resolvi o board pelo pacote instalado
0.27.10 (`state=ok`, `exists=true`) e conferi o card T-139 nesta thread. A
frente segue no worktree T-139; preservei os arquivos sujos da `main` e não
interpretei o inventário de egress como autorização.

Os testes existentes já cobriam a composição nos dois comandos e a entrega do
Reviewer a um runner falso. Fortaleci o teste dos blocos de shell do Planner e
Reviewer com tarefa sintética indentada e CRLF final: os bytes entregues e o
SHA do recibo batem com o compositor. Uma mutação que remove a sentinela `X`
faz o teste divergir, provando que a guarda detecta perda dos newlines finais.
O teste focado passou. Isto ainda **não** prova entrega pelo Companion no host
Claude: a dependência T-090 (`--wait` em `task`) permanece separada. Tampouco
substitui pontuação cega, replicação ou custo até aceite.

⏭️ RETOMAR AQUI: continuar as verificações locais do piloto sem reexecutar os
braços congelados. Cinco pacotes de pontuação externos permanecem sem gate
específico; R-011 e M-004 seguem locais. Sem adoção, bump, commit, push,
publicação, instalação ou restart.

### Pré-triagem das notas pendentes — 2026-09-26

Recompus os cinco pacotes pós-B e confirmei 5/5 hashes e bytes iguais ao
inventário, sem rótulos de braço nem ocorrências na triagem automatizada de
dados sensíveis. A leitura dos oráculos e respostas mostrou que R-010/B não
pede a mutação que faltou ao A (5/6), e P-007/B não prescreve mudar um anchor
em cópia nem a prova pós-release sob gate próprio, também a lacuna do A (5/6).
Isso não é pontuação cega, mas torna injustificado gastar três avaliações
nesses casos agora; P-007/B também consumiu muito mais tokens que A.

P-008/B nomeia `board.parent` como mutante concreto, a lacuna do A. O pacote
A anterior vazava caminho de braço, então o próximo gate externo proposto
passa a abranger **somente P-008/A v2 e P-008/B**: dois hashes já congelados,
28.225 bytes no total, uma chamada por pacote, zero retry, mesmo Opus 5.5
efetivo comprovado no recibo. O inventário de cinco foi preservado como
histórico e marcado como não vigente para envio. Nenhuma chamada externa foi
feita. Ainda seriam necessários replicação, prova de solução aceita, custo
até aceite e teste de entrega real antes de adoção.

⏭️ RETOMAR AQUI: continuar trabalho local do T-139; não enviar os dois
pacotes sem gate específico, nem reativar os três descartados por arrasto.
Reviewer R-008/B tem falso crítico e precisa de nova hipótese de skill antes
de qualquer adoção. R-011 e M-004 continuam locais; sem bump, commit, push,
publicação, instalação ou restart.

O falso alto de R-008/B foi rechecado contra o comando e o teste da fixture:
`--readonly` e `"$PLANNER_PROMPT"` são argumentos separados, e o CLI falso
recebe o último argumento (teste focado verde); `< /dev/null` não elimina
argv. A hipótese de Reviewer v2 está descrita em
`../../../docs/T-139-auditoria-local-B.md`: exigir cadeia de evidência de
entrada até argv/stdin e consumidor antes de bloquear, com R-008 negativo e
R-010 positivo. Não alterei a skill congelada nem a pontuei como melhora.

### Prova local de resolução executável P-008 — 2026-09-26

Após compactação, reli o índice, resolvi o board canônico pelo pacote instalado
0.27.10 (`state=ok`, `exists=true`) e confirmei T-139 `[~] @codex` nesta
thread. A candidata permanece no worktree isolado; os arquivos compartilhados
sujos da main foram preservados.

Criei `docs/t139_p008_acceptance.py` e cinco testes. O verificador copia a
fixture sintética para diretório temporário, observa o resolvedor em main e
worktree e executa checkpoints nas duas frentes. Aceita somente board canônico
na main, `thread_root` da frente solicitante e alteração exclusiva da thread
alvo. Aceita o campo `thread_root` corrigido ou `local_thread_root` explícito,
sem favorecer uma das propostas. A fixture com `thread_root = board.parent`
reprova; a correção local em cópia passa; reintroduzir `board.parent` no
resolvedor ou no consumidor reprova. Uma thread local ausente também deve
falhar antes de qualquer append, não ser recriada silenciosamente.
O verificador não altera a candidata original. Os scripts candidatos devem
ser inspecionados antes da execução: a cópia temporária não é sandbox.

Esta é uma régua local **parcial** para uma futura implementação do plano, **não**
prova que o braço B produziu uma implementação melhor que A. A prova cega
externa de P-008/A v2 e B continua sem autorização; os dois pacotes seguem
congelados e não foram enviados. Replicação, custo até aceite, identidade
efetiva do modelo e entrega real continuam pendentes. Sem adoção, bump,
commit, push, publicação, instalação ou restart.

Gates locais após a régua: bancada T-139 91/91, suíte do plugin 433/433,
manifesto estrito, Ruff dos dois arquivos novos e `git diff --check` verdes.
O lint conserva apenas a divergência fonte/cache
0.27.10 em `commands/plan-next.md`, esperada para uma fonte em edição.

⏭️ RETOMAR AQUI: usar a régua P-008 somente para soluções executáveis e
inspecionadas; não confundir plano pontuado com resolução aceita. Aguardar
gate específico para as duas avaliações externas propostas sem tratar a
espera como falha técnica do Orquestra. Continuar o trabalho local do T-139
que tenha critério verificável, sem reexecutar braços congelados.

### Candidata Reviewer v2 isolada — 2026-09-26

O falso bloqueador alto de R-008/B foi tratado como hipótese de skill, não
como mudança do Reviewer ativo. A v2 está no worktree T-139, em
`docs/experimentos/T-139/candidates/role-review-plugin-instructions-v2/SKILL.md`,
fora de `orq/skills` e fora do catálogo do compositor. A v1 conserva SHA-256
`ab77868494ea5e435966735e9dbd2dfe3ef4770223331ff35cbdff85107da0ed`;
a v2 tem SHA-256
`1a83b9d13931494d9e33f5a7b498d77c546fad4c2d4fc0dc17c64698d1ae82cb`.
O diff é só identificação da candidata e um parágrafo que exige evidência
`entrada → argv/stdin → consumidor → efeito` antes de declarar bloqueador.

O validador da skill passou; a bancada T-139 passou 91/91, a suíte do plugin
433/433, o manifesto estrito e `git diff --check` passaram. O lint mantém
somente a divergência fonte/cache 0.27.10 em `commands/plan-next.md`.
R-008 e R-010 continuam controles negativo/positivo sustentados por fixtures,
mas a v2 **não foi executada por modelo**. Não há prova de que reduza falsos
bloqueadores sem perder achados verdadeiros; exige novo ensaio pareado e
autorização de egress própria. Nenhum braço congelado, comando ativo ou cache
foi modificado; sem bump, commit, push, publicação, instalação ou restart.

⏭️ RETOMAR AQUI: antes de considerar a v2 para o catálogo, congelar prompts
novos e medir em R-008 (sem defeito), R-010 (override real) e pelo menos mais
um caso independente; manter constantes modelo/effort/via e custo até aceite.
P-008/A v2 e B seguem com gate externo separado; não enviar por arrasto.

### Gate externo delimitado — aguardando dono

Após três rodadas de avanço local, a prova de ganho do T-139 continua
impossível sem nova execução por modelo. R-011 e M-004 já estão preparados
localmente; criar mais artefatos sem medir respostas não demonstraria qualidade.
A próxima etapa mínima proposta é pontuar cegamente só P-008/A v2
(12.390 bytes, SHA-256
`8c73bef974f0c207da0ca98381a52890a19cca0af1116b5ff7858f79ace402f6`)
e P-008/B (15.835 bytes, SHA-256
`eef668a3fccd29097e5d392a3abd57b62fe9998c3de68b95168a803849bc41b9`).
Destino: Anthropic pelo Claude CLI; uma chamada por pacote, zero retry,
ferramentas desabilitadas, inspeção sanitária antes de enviar e modelo efetivo
Opus 5.5 conferido depois. Total máximo de material: 28.225 bytes. Não incluir
os três outros pacotes históricos, R-011, M-004 ou Reviewer v2 nesta autorização.

**Decisão necessária do dono:** autoriza esse envio delimitado de código e
instruções ao Anthropic para as duas notas cegas? Sem resposta, nenhuma chamada
será feita; T-139 não pode alegar ganho, economia ou adoção. A candidata
Reviewer v2 exigirá um gate distinto depois de congelar seus próprios prompts.

### Checkpoint de recuperação — gate P-008 aprovado, 2026-09-27

O dono autorizou explicitamente **somente** os pacotes congelados P-008/A v2
(`8c73bef974f0c207da0ca98381a52890a19cca0af1116b5ff7858f79ace402f6`,
12.390 bytes) e P-008/B
(`eef668a3fccd29097e5d392a3abd57b62fe9998c3de68b95168a803849bc41b9`,
15.835 bytes) ao Anthropic via Claude CLI: duas notas cegas, uma chamada por
pacote, zero retry, total 28.225 bytes. O board passou a `[~]` em `@codex`.
O resolvedor do pacote 0.27.10 confirmou o board e a thread na main. Os dois
arquivos ainda têm bytes/hashes idênticos ao inventário; a triagem não achou
caminhos pessoais, e-mails nem padrões de credenciais; `claude --version`
respondeu 2.1.280 e não há API key no ambiente. A próxima ação é executar
exatamente essas duas chamadas, conferir `claude-opus-5-5` no recibo e auditar
os seis critérios sem extrapolar ganho ou adoção. Sem bump, commit, push,
publicação, instalação ou restart autorizados por este gate.

### Checkpoint de recuperação — duas notas P-008 concluídas, 2026-09-27

Executei **exatamente uma chamada para P-008/A v2 e uma para P-008/B**, sem
retry, com o runner local `run-opus-reviewer.py --model opus`. Ambos os pacotes
passaram nos hashes e tamanhos congelados imediatamente antes do envio, o
processo saiu 0 e o modelo efetivo foi `claude-opus-5-5` nos dois recibos.
A nota cega foi **5/6 para A v2 e 6/6 para B**; o diferencial foi o critério
5: só B nomeou o teste de mutação que reintroduz `board.parent`. Nenhum parecer
apontou falso crítico ou violação de escopo. O Manager conferiu a evidência
contra os briefings e registrou ressalvas sobre JSON malformado do resolvedor
e o formato inconsistente do retorno em
`docs/experimentos/T-139/P-008-auditoria-notas-cegas.md`. Os JSONs e recibos
ficam nas respectivas pastas de grading no worktree T-139. Os pacotes
congelados permaneceram intactos.

**Limite da conclusão:** um caso sintético não prova ganho geral nem economia;
não há autorização para novos envios, adoção da skill, bump, commit, push,
publicação, instalação ou restart. T-139 continua em investigação local
`[~] @codex`. A próxima decisão de produto deve considerar casos adicionais
e os papéis Reviewer/Manager apenas com gates próprios; não repetir P-008.

### Checkpoint de recuperação — bancada local Reviewer v2, 2026-09-27

No worktree isolado T-139, preparei a candidata Reviewer v2 sem alterar a skill
ativa. `docs/t139_trial_setup.py --reviewer-v2` compõe B com a skill candidata;
A, task, workspace e rubrica permanecem iguais ao controle. Congelei os
prompts e hashes de R-008 (falso bloqueio), R-010 (override real de autoridade)
e R-011 (controle limpo) em `docs/T-139-reviewer-v2-freeze.json`. O runner
reconhece esse manifesto apenas para Reviewer, compara o digest da candidata
e recusa variantes ou bytes divergentes **antes** da CLI. Mutation checks
locais reprovaram troca da skill e troca do prompt A; sem aprovação de egress,
os três casos pararam em `EGRESS_NAO_AUTORIZADO`, sem criar respostas ou chamar
modelo.

Verificação local: bancada T-139 98/98 após o ajuste da v2; suíte do plugin 433/433 na segunda
execução; `claude plugin validate ./orq --strict` verde; `git diff --check`
verde. A primeira execução completa teve uma falha intermitente, fora deste
patch, no teste de Git simulado do resolvedor (`git-timeout` versus
`git-indisponivel`); o teste isolado passou duas vezes. O lint de coerência
no worktree T-139 segue vermelho por divergência de bytes já existente em
`orq/commands/plan-next.md` contra o cache instalado; não declarar os gates
inteiros verdes nem alterar o cache para encobrir isso.

⏭️ RETOMAR AQUI: auditar a bancada Reviewer v2 e avançar Manager em simulação
local. Os três novos casos **não foram enviados** ao Anthropic; o gate de
P-008 foi consumido e não autoriza novos envios. Nenhum bump, commit, push,
publicação, instalação ou restart foi feito nesta etapa. Ainda não há prova
de ganho, economia ou adoção da v2.

### Checkpoint de recuperação — controle Manager M-004, 2026-09-27

Acrescentei ao worktree T-139 `docs/t139_manager_prepare.py` e seu teste. O
preparo local gera A/B privados, com o contrato-base real do Manager intacto,
a skill candidata apenas em B e o oráculo separado. Não há despacho, modelo
ou alteração do Manager ativo. O recibo e os hashes estão em
`docs/T-139-manager-M004-local-preflight.md`: A tem 36.897 bytes, B 38.546;
ambos excedem o limite **padrão** de 16.384 bytes do runner Anthropic. Um
teste com CLI falsa provou que `--max-input-bytes 38546` entrega B inteiro por
stdin, sem Anthropic; logo a via não está inviável, mas ainda exige gate
específico de egress e prova real de qualidade/custo. O caso agora explicita
que seu registro é fictício, não um board operacional, para separar a simulação
sem ferramentas da regra de resolução do board real. Uma recusa persistente
de ambos os braços ainda não provaria efeito da candidata.

Gates após essa etapa: bancada T-139 101/101, suíte do plugin 433/433,
manifesto estrito verde; lint ainda vermelho só por
`bytes:commands/plan-next.md` versus cache instalado. O ajuste adicional da
v2 eliminou a composição desnecessária da skill antiga do braço B, com teste
red/green próprio. Continuam sem bump, commit, push, publicação, instalação,
restart ou novas chamadas externas.

### Checkpoint de recuperação — custo e fronteira do próximo ensaio, 2026-09-27

Os recibos **Codex** de execução P-008/A e B registram, respectivamente,
182.759/186.045 tokens de entrada total e 3.211/3.874 de saída. A parcela
aritmética `entrada − cache` é 14.055/26.557; ela não equivale a preço.
Registrei esses números em
`docs/experimentos/T-139/P-008-auditoria-notas-cegas.md`. O braço B recebeu
6/6 contra 5/6 de A, mas não demonstrou economia; os recibos das duas notas
Anthropic não capturam contagem de tokens nem custo faturado.

Recompus os três pares Reviewer v2 (R-008, R-010 e R-011) contra o freeze:
todos os hashes bateram. O inventário em
`docs/T-139-reviewer-v2-egress-inventory.md` registra 21.663 bytes de prompts
A/B e os workspaces sintéticos acessíveis. Esse total **não limita o egress**
quando o agente pode ler arquivos; não usar como autorização tácita.

⏭️ RETOMAR AQUI: terminar a auditoria local do Manager M-004 e da bancada
Reviewer v2; depois, avaliar os novos pares só sob gate externo específico.
Persistem a divergência do lint no worktree T-139 e a ausência de prova
reproduzida de ganho/custo até aceite. Nada foi enviado, instalado ou
publicado nesta continuação; sem commit, push ou restart.

### Checkpoint de recuperação — via real do Reviewer, 2026-09-27

Após a compactação, reli o índice, resolvi o board canônico pelo pacote
Orquestra 0.27.10 (`state=ok`, `exists=true`) e conferi este card em `[~]`
com posse `@codex`. A recomposição local anterior dos pares Reviewer v2
continua válida como bancada exploratória, mas **não é prova da via de
produção do Reviewer no host Codex**: `docs/t139_trial_run.py` usa `codex
exec` (vendor OpenAI) com leitura do workspace; o elenco ativo usa `opus`
(Anthropic) via `run-opus-reviewer.py`, sem ferramentas, com conteúdo
verbatim no briefing. O plano T-139 exige entrega na via efetivamente
testada antes de qualquer adoção.

Os três pares congelados R-008/R-010/R-011 não foram enviados nesta
retomada e não devem ser apresentados como validação do Reviewer operacional.
Próximo passo local: desenhar uma faixa separada e pareada para a via Opus,
com os mesmos arquivos fictícios completos nos dois briefings, oráculo fora
do pacote e teste de entrega dos bytes com CLI falsa. Auditar tamanho,
sanitização e hashes antes de pedir gate específico; a falha antiga de
R-007 sem acesso aos arquivos não pode ser repetida. Nenhum novo envio,
adoção, bump, commit, push, publicação, instalação ou restart nesta etapa.

### Checkpoint de recuperação — bancada Reviewer Opus local, 2026-09-27

No worktree isolado T-139, criei uma faixa **separada** para o Reviewer do
host Codex na via operacional Anthropic. `docs/t139_reviewer_opus_prepare.py`
prepara R-008/R-010/R-011 com arquivos sintéticos completos e numerados no
prompt, mesma tarefa e material para A/B, skill v2 apenas em B e oráculo fora
do pacote. A saída é `LOCAL_ONLY`, sem autorização de egress. Inventário de
bytes/hashes e limites em `docs/T-139-reviewer-opus-local-preflight.md`.
Todos os prompts ficaram abaixo do limite padrão de 16 KiB. Teste com CLI
falsa comprovou `run-opus-reviewer.py --model opus`, `--tools ""`, settings
vazios e entrega íntegra por stdin; outro reconstruiu os 17 arquivos a partir
das linhas numeradas. Mutação que omitia um arquivo tornou o teste vermelho.
Não houve chamada externa nem nota de qualidade nesta faixa.

Depois acrescentei `docs/t139_reviewer_opus_run.py`: o gate exige hashes
aprovados, compara trial/fonte/freeze, recusa symlink de destino e repetição,
e só libera B com nota A abaixo do teto vinculada à resposta. Testes com CLI
falsa cobriram A e B válidos e recusas pré-egress; mutação que removia o
vínculo da nota à resposta tornou o teste vermelho. O runner Opus atual
confirma o modelo, mas não expõe tokens/custo faturado para esta bancada:
o recibo declara `usage_unavailable=true`, sem alegar economia.

Gates locais: bancada T-139 110/110, suíte do plugin 433/433, manifesto
estrito e Ruff check verdes; o lint segue vermelho somente pela divergência
preexistente `bytes:commands/plan-next.md` do worktree contra o cache
instalado. A prova local não substitui revisão cega, modelo efetivo, custo
até aceite ou replicação. ⏭️ RETOMAR AQUI: auditar o gate fail-closed e
o inventário final; qualquer A/B externo precisa autorização específica e
o Manager M-004 continua somente local. Não confundir os pares Codex antigos
com validação do Reviewer operacional.
Auditoria adicional: M-004 foi entregue integralmente a CLI falsa pelo runner
Anthropic, mas o Manager operacional deste host é a sessão Codex no modelo
escolhido pelo dono. Uma futura nota M-004 em Opus será exploratória, não
validação de produção; o limite está registrado no preflight do Manager.
Sem bump, commit, push, publicação, instalação ou restart.

### Checkpoint de recuperação — recibo numérico do Reviewer Opus, 2026-09-27

Após nova compactação, reli o índice e resolvi o board pelo pacote instalado
0.27.10 (`state=ok`, `exists=true`); T-139 segue `[~] @codex`. No worktree
isolado, o runner operacional `orq/scripts/run-opus-reviewer.py` ganhou a
opção **opt-in** `--emit-usage-json`: preserva stdout como parecer, e emite
no stderr só contadores/custo numéricos conhecidos do JSON da CLI. A bancada
`docs/t139_reviewer_opus_run.py` solicita esse recibo e grava `cli_usage` ou
`usage_unavailable=true` quando não há métricas. Campos textuais e o parecer
não entram no recibo; a saída padrão do runner não mudou. Red/green e mutação
de supressão do recibo foram exercitados com CLI falsa, sem chamada externa.
Qualquer `total_cost_usd` futuro é declaração da CLI, **não custo faturado da
assinatura**. Não há novos pares A/B reais, notas cegas ou prova de economia.

Gates locais desta continuação: T-139 111/111, plugin 434/434, manifesto
estrito e Ruff check verdes; lint permanece vermelho só pela divergência
preexistente `bytes:commands/plan-next.md` entre o worktree 0.27.10 e o cache.
A edição em `orq/` ainda não recebeu bump nem release e não pode ser tratada
como código carregado pelos hosts. ⏭️ RETOMAR AQUI: auditar o inventário
final e a prova de custo até aceite antes de propor qualquer gate externo;
nenhuma autorização anterior para P-008 cobre Reviewer Opus ou Manager M-004.
Sem commit, push, publicação, instalação ou restart.

### Checkpoint — gate local M-004 na via Codex, 2026-09-27

O caso M-004 ganhou snapshot imutável em
`docs/T-139-manager-M004-freeze.json` e um executor experimental em
`docs/t139_manager_run.py`, sempre testado com **CLI Codex falsa**. O executor
recompõe a fonte atual e compara manifesto/prompts com o freeze, exige hashes
aprovados de prompt e rubrica mais modelo/effort, usa cwd temporário vazio,
sandbox `read-only` e o perfil isolado existente (`:root` negada, rede
desligada), sem hooks, plugins ou MCP. Preserva eventos e resposta em diretório
temporário privado; reprova ferramentas, escrita, uso inválido e repetição.
B depende de nota A revisada, abaixo de 7/7 e ligada ao hash da resposta.
O recibo guarda só contadores numéricos conhecidos, não texto arbitrário do
JSONL. Red/green confirmou prompt adulterado, ausência de gate, falta de
perfil isolado, vazamento de texto de uso e symlink do diretório A e da saída
criada pela CLI; mutações
controladas mostraram que os testes detectam a remoção da recusa de ferramenta
e do vínculo da nota à resposta.

Gates finais desta etapa: bancada T-139 **120/120**, suíte do plugin
**434/434**, manifesto estrito, Ruff check/format dos arquivos novos e
`git diff --check` verdes. Lint permanece vermelho somente pelo
`bytes:commands/plan-next.md` preexistente no worktree 0.27.10. Nada foi
enviado a modelo nem integrado: `effective_model=null`, e a CLI falsa não
prova isolamento no host nem equivalência com a sessão viva do Manager.
Planner P-008 continua com benefício pontual 5/6→6/6 sem economia provada;
Reviewer Opus não tem respostas reais. ⏭️ RETOMAR AQUI: auditoria final
dos pacotes e dos riscos de execução; qualquer chamada real M-004 ou Reviewer
Opus requer gate de egress específico, distinto da autorização P-008.
Sem bump, commit, push, publicação, instalação ou restart.

### Checkpoint de recuperação — auditoria de aceite, 2026-09-27

Após compactação, reli `memory/MEMORY.md` e resolvi o board pelo pacote instalado
0.27.10 (`state=ok`, `exists=true`, caminhos absolutos); T-139 permanece
`[~] @frente-jev-router @codex`. A thread ativa foi relida. O worktree
T-139 preserva as alterações rastreadas e os experimentos não rastreados;
nenhum arquivo foi descartado ou integrado.

Pelo plano aprovado, o gate de adoção ainda não foi atingido: P-008 é um
único par com sinal 5/6→6/6 e sem economia provada; os três casos Reviewer
Opus estão congelados, porém sem respostas reais; M-004 tem somente prova
estrutural com CLI falsa, sem equivalência à sessão Manager viva. Faltam
replicação por papel, oráculos cegos, custo até aceite e teste na via
operacional. As duas chamadas Anthropic previamente autorizadas para P-008
já foram consumidas; elas não autorizam os novos lotes Reviewer ou Manager.
O trabalho local pode continuar, mas nenhuma ativação geral decorre desses
resultados. Sem chamada externa, bump, commit, push, publicação, instalação
ou restart nesta recuperação.

### Checkpoint — identidade do modelo no A/B Reviewer, 2026-09-27

Na bancada Reviewer Opus, a validação anterior aceitava qualquer
`OPUS_MODEL` não vazio. Como o runner operacional provava apenas o prefixo
`claude-opus-5`, um resultado de Opus 5.1 passava como prova estrutural do
ensaio planejado para 5.5. Além disso, B podia usar variante 5.5 diferente
de A. Três testes comportamentais com CLI falsa reproduziram os falsos
verdes antes da correção. O gate experimental agora exige a família
`claude-opus-5-5` em cada resposta e identidade efetiva exata entre A/B;
uma troca depois da chamada invalida B, sem retry nem nota de qualidade.
Não alterei o runner genérico nem o alias do host.

Verificação local: bancada T-139 **123/123**, suíte do plugin **434/434**,
manifesto estrito, Ruff check/format dos dois arquivos Python e
`git diff --check` verdes. O lint continua vermelho **somente** pela
divergência preexistente `bytes:commands/plan-next.md` entre worktree e
cache 0.27.10. `codex-cli 0.157.1` declara as flags de isolamento do M-004
e lista as nove features usadas, mas isso ainda não prova execução do perfil
ou sessão viva. O preflight de Reviewer e o de Manager registram os limites.
Faltam chamadas reais autorizadas, notas cegas, replicação e custo até
aceite; sem adoção. Sem chamada externa, bump, commit, push, publicação,
instalação ou restart nesta etapa.

### Checkpoint — quatro casos Manager congelados localmente, 2026-09-27

A lacuna de replicação estrutural do Manager foi reduzida: o preparador e o
gate `codex exec` experimental agora selecionam M-001, M-002, M-003 ou
M-004, cada qual com caso, rubrica, prompts e freeze próprios. O padrão
M-004 antigo foi preservado. Os tetos de nota são 4/6/8/7, respectivamente;
o teste M-003 mostrou RED com o gate fixo de M-004 e GREEN após aplicar o
teto e a identidade do caso. A, para cada caso novo, entregou o hash do
prompt esperado à CLI falsa; B de M-003 recusou A em 8/8 e admitiu apenas
nota íntegra 7/8. Nenhum caso foi enviado a modelo, e a CLI falsa continua
prova de encanamento, não de qualidade ou da sessão Manager viva.

Gates desta etapa: bancada T-139 **126/126**, suíte do plugin **434/434**,
manifesto estrito, Ruff check/format e `git diff --check` verdes. Lint segue
vermelho só pela divergência conhecida `bytes:commands/plan-next.md` entre
worktree e cache 0.27.10. O quadro foi atualizado apenas na linha T-139;
restam respostas reais/cegas, replicação de qualidade por papel, custo até
aceite e prova na via operacional antes de qualquer adoção. Sem chamada
externa, bump, commit, push, publicação, instalação ou restart.

### Checkpoint de recuperação — preparo local de P-009, 2026-09-27

Após compactação, reli o índice, resolvi o board pelo pacote instalado
0.27.10 (`state=ok`, `exists=true`) e reli a linha e esta thread do T-139.
O worktree isolado e as edições paralelas da main foram preservados.

P-009 agora passa pelo **preparador real** em uma lista separada
`LOCAL_ONLY_CASES`. O teste recompõe os dois workspaces idênticos e os
hashes A/B do snapshot `T-139-P009-preflight-local.json`, sem levar a
rubrica para os prompts. O caso permanece fora de `CASES`, do congelamento
original de seis casos e de qualquer pacote de egress.

Um teste RED demonstrou que um manifesto `LOCAL_ONLY` seria aceito pelo
pré-voo se alguém promovesse acidentalmente o caso e seu freeze. O gate
agora recusa `CASO_SOMENTE_LOCAL` antes da CLI; GREEN e mutation check
cobrem tanto o marcador do manifesto quanto a lista local. Nenhuma
chamada de modelo ocorreu. Bancada T-139: **128/128**; suíte do plugin:
**434/434**; manifesto estrito e Ruff check verdes. O lint segue vermelho
somente pela divergência já conhecida `bytes:commands/plan-next.md` entre
fonte candidata e cache instalado 0.27.10. Sem qualidade, economia ou
adoção nova demonstrada; sem bump, commit, push, publicação, instalação
ou restart.

⏭️ RETOMAR AQUI: preparar a decisão de gate dos ensaios ainda não
executados, sem reutilizar autorizações consumidas. P-009 continua
`LOCAL_ONLY` até congelamento de execução e autorização específica;
Reviewer Opus e Manager continuam sem respostas reais.

### Checkpoint — recibos de uso do piloto, 2026-09-27

A auditoria do gate estrutural compartilhado pelo Planner e pelo Manager
encontrou dois falsos verdes: `input_tokens: true` era aceito como inteiro
Python, e qualquer campo extra do evento `usage` era copiado ao recibo,
inclusive texto arbitrário. Com testes RED/GREEN separados, o gate agora
rejeita contadores presentes com tipo/valor inválido (obrigatórios ou
opcionais) e projeta somente `input_tokens`, `cached_input_tokens`,
`output_tokens` e `reasoning_output_tokens` numéricos. Campo desconhecido
não contamina o recibo. Os 11 JSONL históricos da bancada continuam
estruturalmente aceitos após a mudança; isso **não** revalida qualidade,
plano P-006/A nem identidade do modelo.

Verificações: bancada T-139 **131/131**, suíte do plugin **434/434**,
manifesto estrito, Ruff check e `git diff --check` verdes. O lint segue
vermelho somente pela divergência fonte/cache 0.27.10 já conhecida em
`bytes:commands/plan-next.md`. Não houve novo egress, nota de modelo,
commit, push, bump, publicação, instalação ou restart.

⏭️ RETOMAR AQUI: os recibos estão mais seguros para comparar custo, mas
Reviewer Opus e Manager ainda exigem resultados reais, pontuação cega,
replicação e custo até aceite antes de qualquer decisão de adoção.

### Checkpoint — ordem e vínculo do recibo JSONL, 2026-09-27

O gate estrutural de Planner/Manager aceitava quatro rastros falsos:
`turn.completed` anterior a `turn.started`, início de turno duplicado,
ausência de `thread.started` e mensagem final fora do turno. Também
aceitava `answer.md` diferente da última `agent_message`, apesar de ser
o arquivo submetido à pontuação. Cada caso foi reproduzido em RED antes
da correção e passou em GREEN. O gate agora exige uma sessão e um turno
ordenados, mensagens do agente dentro do turno e igualdade do texto da
última mensagem com `answer.md` (ignorando só espaço nas bordas). Não
copia o conteúdo da resposta para o recibo.

Os 11 JSONL históricos continuam `STRUCTURAL_ONLY` após a nova checagem;
isso não converte P-006/A em plano válido nem prova modelo efetivo ou
qualidade. Bancada T-139 **136/136**, suíte do plugin **434/434**,
manifesto estrito, Ruff check e `git diff --check` verdes. Lint segue
vermelho somente pelo `bytes:commands/plan-next.md` fonte/cache 0.27.10
já conhecido. Nenhuma chamada externa, bump, commit, push, publicação,
instalação ou restart.

⏭️ RETOMAR AQUI: seguir a auditoria da bancada sem confundir recibo
estrutural com benefício dos papéis. Faltam resultados reais e avaliação
cega de Reviewer Opus e Manager, replicação e custo até aceite.

### Checkpoint de recuperação — gate de ensaio externo, 2026-09-27

Após a compactação, reli `memory/MEMORY.md`, resolvi o board pelo pacote
instalado 0.27.10 (`state=ok`, `exists=true`), conferi a linha T-139 e esta
thread. O worktree isolado T-139 segue com a candidata local; as edições
paralelas na main foram preservadas. A autorização específica dos dois
pacotes P-008/A v2 e P-008/B foi consumida. Reviewer Opus e Manager ainda não
têm respostas reais, e este checkpoint não interpreta uma pergunta de status
como autorização para novo egress. Próximo passo: delimitar os pacotes
sintéticos exatos e obter um gate próprio antes de qualquer envio; sem adoção,
bump, commit, push, publicação, instalação ou restart.

### Checkpoint — anonimização e auditoria dos pacotes, 2026-09-27

A auditoria local do briefing Manager M-004 encontrou dois nomes próprios
incidentais no contrato-base. Um teste RED mostrou que ambos chegavam aos
prompts A/B; o preparador agora troca somente essas duas expressões por
referências genéricas, preserva `base_source_sha256` da fonte e vincula
`base_sha256` ao contrato anonimizado. O gate de execução compara os dois
campos com o freeze. Os quatro casos Manager foram recongelados sem alterar
`orq/skills/orq/SKILL.md` nem a candidata ativa. O teste focado passou em
GREEN e a falha anterior é o mutation check da ausência da anonimização.

Recomposição read-only: quatro casos Manager, oito prompts, **305.418 bytes**
somados; três casos Reviewer Opus, seis prompts, **44.713 bytes** somados.
Todos os hashes e comprimentos bateram com os freezes; a varredura local
dos 14 prompts não encontrou caminhos de home, e-mail, os nomes conhecidos ou
padrões de credencial testados. Isso não é garantia universal de ausência de
dado sensível: cada envio ainda requer conferência do pacote exato.

Gates: bancada T-139 **137/137**, suíte do plugin **434/434**, manifesto
estrito, Ruff check/format e `git diff --check` verdes. Lint vermelho apenas
pela divergência conhecida `bytes:commands/plan-next.md` entre a candidata e
o cache 0.27.10. Nenhuma chamada de modelo, bump, commit, push, publicação,
instalação ou restart ocorreu nesta etapa.

⏭️ RETOMAR AQUI: a evidência ainda é estrutural/local. Faltam respostas reais
cegas de Reviewer e Manager, replicação e custo até aceite. Delimitar um
gate de egress para os hashes recongelados antes de invocar as CLIs; não
reutilizar a autorização P-008 já consumida.

### Checkpoint — gate exato de duas chamadas A, 2026-09-27

O próximo lote foi reduzido a **duas chamadas**, uma por via, sem retry:
R-008/A, 7.870 bytes, SHA-256
`da2b6e28a95a2602dd0ce2361ef909da7ccf5887e8031307d4b51cf834f7203e`,
ao Claude CLI/Anthropic com alias `opus` e exigência de modelo efetivo
`claude-opus-5-5`; M-004/A, 36.880 bytes, SHA-256
`3cd30a475af4b75b8e259ce41a09012d52635eda44c36fdd1c2b4388fb45dd69`,
ao Codex CLI/OpenAI com `gpt-6-astra@max`. O dono recebeu a pergunta de
aprovação específica; **a apresentação do gate não é aprovação**.

Com os freezes atuais, os dois executores recusaram a tentativa sem hashes
aprovados: `EGRESS_NAO_AUTORIZADO`, exit 2, sem criar `responses/`. As CLIs
instaladas são `claude` 2.1.280 e `codex-cli` 0.157.1. Não houve chamada de
modelo, envio de pacote, braço B, bump, commit, push, publicação, instalação
ou restart. `claude auth status --json` informou `loggedIn=true` e
`codex login status` saiu 0, sem imprimir identidade nem credencial.
Se houver aprovação, recompor e auditar novamente o pacote exato e executar
somente as chamadas aprovadas; pontuação e eventual B exigem decisão
posterior conforme rubrica e recibo A.

### Checkpoint — falhas de teste sem despejar briefings, 2026-09-27

Uma falha real na bancada Manager havia impresso o prompt inteiro no traceback
de `assertIn`/`assertNotIn`. As asserções que recebem prompts A/B em
`test_t139_manager_prepare.py` e `test_t139_reviewer_opus_prepare.py` foram
trocadas por testes booleanos com mensagens curtas. A regra verificada é a
mesma; muda somente o diagnóstico de falha, sem expor os bytes congelados no
log. Testes focados **8/8**, bancada T-139 **137/137**, suíte do plugin
**434/434**, manifesto estrito, Ruff check/format e `git diff --check`
verdes. Lint continua vermelho apenas pela divergência conhecida
`bytes:commands/plan-next.md` fonte/cache 0.27.10. Nenhuma nova chamada de
modelo, commit, push, bump, publicação, instalação ou restart. O gate exato
de R-008/A e M-004/A continua aguardando a decisão do dono.

### Checkpoint — recibo de uso inteiro, 2026-09-27

A revisão do runner Opus encontrou contagens fracionárias de tokens aceitas
como metadado válido tanto em `run-opus-reviewer.py` quanto no leitor do gate
Reviewer. Testes RED reproduziram as duas falhas. O runner agora exclui
contagem fracionária do recibo; o gate recusa recibo adulterado com token
fracionário. Custos `costUSD`/`cost_usd` e `total_cost_usd` continuam podendo
ser decimais. GREEN e mutation check correspondem aos mesmos testes que
falharam antes da correção.

Gates atuais: bancada T-139 **139/139**, suíte do plugin **435/435**,
manifesto estrito, Ruff check/format e `git diff --check` verdes. Lint segue
vermelho apenas pelo `bytes:commands/plan-next.md` fonte/cache 0.27.10. O
parecer de custo ainda dependerá de resposta real e valor reportado pela CLI;
não é cobrança comprovada da assinatura. Nenhuma chamada de modelo, bump,
commit, push, publicação, instalação ou restart. Gate específico das duas
chamadas A ainda pendente.

### Checkpoint de recuperação — auditoria do gate de aceite, 2026-09-27

Após compactação, reli `memory/MEMORY.md`, confirmei o pacote Orquestra
instalado 0.27.10 e resolvi o board canônico (`state=ok`, `exists=true`);
T-139 continua `[~] @frente-jev-router @codex`. Reli esta thread e o plano
aprovado no worktree isolado, preservando os arquivos da main e os artefatos
experimentais não commitados.

O aceite não decorre dos gates locais: P-008 tem um único sinal 5/6→6/6,
sem economia demonstrada; Reviewer Opus e Manager têm preflight e oráculos,
mas não respostas reais nos novos pacotes. O plano exige ao menos três tarefas
distintas por papel, controle sem defeito, avaliação cega independente,
ausência de violações críticas, custo até aceite e teste na via operacional.
O próximo experimento indispensável permanece limitado a R-008/A e M-004/A
nos hashes registrados acima, com autorização específica ainda pendente;
nenhum novo envio, B, ativação, bump, commit, push, publicação, instalação
ou restart foi feito nesta recuperação.

### Checkpoint — matriz de aceite visível, 2026-09-27

O arquivo experimental `docs/T-139-resultados-preliminares.md` terminava no
lote histórico de cinco A e podia ser lido como se ainda não houvesse qualquer
B. Acrescentei uma seção datada com o par P-008/A v2–B já pontuado, as provas
que faltam para Planner, Reviewer e Manager e o gate separado dos próximos
R-008/A e M-004/A. As referências locais existem e `git diff --check` saiu
0. Isso não acrescenta chamada de modelo nem transforma 5/6→6/6 em ganho
replicado ou economia; o gate de egress continua pendente.

### Checkpoint — R-008/A e M-004/A executados, 2026-09-27

O dono respondeu `pronto - pode fazer` ao gate exato de duas chamadas A.
Recompus os pacotes no worktree isolado: R-008/A tinha 7.870 bytes e SHA-256
`da2b6e28a95a2602dd0ce2361ef909da7ccf5887e8031307d4b51cf834f7203e`;
M-004/A tinha 36.880 bytes e SHA-256
`3cd30a475af4b75b8e259ce41a09012d52635eda44c36fdd1c2b4388fb45dd69`.
A varredura de PII/credenciais definida no preflight não encontrou padrões.
Executei exatamente uma chamada por pacote, sem retry e sem B; as duas
retornaram `STRUCTURAL_ONLY`. R-008/A confirmou `claude-opus-5-5` e a CLI
declarou US$ 0,1780422, não fatura. M-004/A declarou 28.114 tokens de
entrada e 2.022 de saída, sem evento de ferramenta ou mutação; o modelo
efetivo não apareceu no JSONL, e a via não equivale à sessão Manager viva.

As respostas, JSONL, stderr, prompts, manifestos e recibos foram preservados
em `docs/experimentos/T-139/ensaios-aprovados-2026-09-27/` no worktree; a
cópia bateu byte a byte com a saída temporária. Leitura local provisória:
R-008/A encontrou a perda do LF final; seu achado adicional de patch
malformado foi confirmado por `git apply --check`, portanto não deve virar
falso positivo inventado no oráculo. M-004/A encaminhou V-046 à revisão já
autorizada e preservou V-047 na frente de telemetria. Nenhuma nota cega,
ganho, economia ou adoção foi declarada. Próximo passo: pontuação independente
de A vinculada aos hashes; B exige nota abaixo do teto e gate próprio.

### Recuperação pós-compactação e gates locais, 2026-09-27

Reli `memory/MEMORY.md`, resolvi o board canônico pelo pacote Orquestra
0.27.10 (`state=ok`, `exists=true`) e confirmei este card em `[~]` com
`@frente-jev-router @codex`. Os dois pacotes A e respostas preservadas batem
byte a byte com a saída temporária. A bancada documental T-139 passou 139/139,
a suíte completa do plugin passou 435/435, o manifesto estrito e
`git diff --check` saíram 0. O lint permanece vermelho somente pela
divergência pré-existente `bytes:commands/plan-next.md` entre a fonte
experimental 0.27.10 e o cache instalado; não mexi no cache. Nenhuma nova
chamada de modelo ocorreu nesta recuperação. Próximo gate segue sendo a
pontuação independente das respostas A, sem alegar ganho ou economia.

### Gate de pontuação cega preparado localmente, 2026-09-27

No worktree T-139, `docs/t139_role_grade_prepare.py` e seu teste novo
preparam pacotes cegos apenas para os recibos congelados R-008/A e M-004/A.
O teste inicial falhou com o preparador ausente; depois passou. Uma checagem
da ficha de avaliação revelou que o primeiro formato local (`id` e indicador
tri-state) não coincidia com o contrato (`number` e booleanos). Corrigi com
teste vermelho→verde antes do envio, retirei a composição provisória do
worktree e congelei somente o formato corrigido em
`docs/experimentos/T-139/grading-role-A-2026-09-27/`.

O briefing `candidate-reviewer` tem **7.259 bytes**, SHA-256
`15636486c3def4304d5537da1d1b69d3957f196403cf85bdffbd633ed209c6a0`;
destino proposto: Codex CLI/OpenAI `gpt-6-astra@max`, vendor oposto ao autor
Opus. O briefing `candidate-manager` tem **4.794 bytes**, SHA-256
`dbd186747fd35c24dd61b8b5bfc405b6a490c16b754d6bca797c0b80c7787c88`;
destino proposto: Claude CLI/Anthropic Opus 5.5, vendor oposto à via Codex.
Total de egress proposto: **12.053 bytes**, duas chamadas, uma por pacote,
sem retry. Só `briefing.md` sairia; recibos, prompts originais, JSONL e
workspaces ficam locais. A varredura dos briefings não encontrou os padrões
de PII, credenciais ou rótulo do braço testados; bytes e hashes bateram com
`wc -c` e `shasum -a 256`.

Gates locais após a correção: bancada T-139 **144/144**, suíte do plugin
**435/435**, Ruff e manifesto estrito verdes, `git diff --check` 0. O lint
continua vermelho somente pela divergência pré-existente de fonte/cópia
instalada 0.27.10 em `bytes:commands/plan-next.md`. Nenhuma nota, ganho,
economia, B, instalação, publicação, commit ou push ocorreu neste passo.

⏭️ RETOMAR AQUI — aguardar autorização específica do dono para enviar os
dois briefings de hashes acima aos avaliadores cross-vendor, uma chamada
por pacote e sem retry. A versão provisória não é autorizável. Depois das
respostas, validar JSON e auditar semanticamente cada 0/1, com a alegação
adicional sobre `changes.patch` adjudicada pela prova local já existente.

### Checkpoint — notas cegas R-008/A e M-004/A, 2026-09-27

O dono autorizou exatamente os dois briefings congelados (12.053 bytes), uma
chamada por pacote, sem retry e sem B. Reconfirmei os hashes, tamanhos,
ausência dos padrões sensíveis testados, diretórios de saída vazios e login
das duas CLIs. O runner local foi escrito com RED/GREEN: recusa briefing
alterado antes da CLI, recusa sobrescrever nota existente, faz uma chamada e
preserva stdout/stderr, resposta e recibo. Antes do envio, a bancada T-139
passou 149/149, a suíte do plugin 435/435, Ruff e manifesto estrito verdes.

As duas chamadas aconteceram uma vez cada, sem retry. R-008 saiu pela Codex
CLI pedindo `gpt-6-astra@max`: exit 0, zero ferramenta, 20.368 tokens de
entrada e 2.079 de saída; a CLI não expôs o modelo efetivo. M-004 saiu pela
Claude CLI, com `claude-opus-5-5` comprovado: exit 0, 192.083 tokens de
criação de cache, 2 de entrada e 2.093 de saída, US$ 1,578532 declarado
pela CLI (não fatura). Nada disso prova economia ou sessão Manager viva.

Ambos os recibos originais disseram `INVALID / GRADE_JSON_INVALID`, por
causas diferentes. Em R-008, o avaliador seguiu o briefing e usou `passed:
0/1`; meu validador local exigia booleanos. Corrigi esse erro com teste
vermelho→verde **sem repetir a chamada**; o JSON bruto agora passa na
validação estrutural, mas o recibo original foi preservado. A nota cega
auditada é 5/6: só falta a mutação explícita que retire a preservação do LF.
Os dois indicadores críticos são `false`. O achado adicional de patch
malformado permanece sustentado pelo `git apply --check` local anterior,
embora não pudesse ser verificado pelo avaliador dentro do pacote.

Em M-004, a resposta veio com cerca ` ```json `, contrariando “somente JSON”;
o corpo interno é válido e atribui 7/7, mas isso é **parecer provisório**,
não nota formal aprovada. A auditoria distingue essa infração de formato
da qualidade semântica. Receipts, hashes e adjudicação estão em
`docs/experimentos/T-139/grading-role-A-2026-09-27/auditoria-local.md` no
worktree isolado. Nenhum B, nova chamada, ativação, bump, commit, push,
publicação, instalação ou restart ocorreu.

⏭️ RETOMAR AQUI — decidir em gate separado como tratar a nota M-004 com
formato inválido e se autorizar B de R-008 após a reauditoria local. Mesmo
que B avance, uma réplica independente e custo até aceite ainda faltam;
não declarar ganho ou economia com este par isolado.

### Gate A aceito e B preparado somente localmente, 2026-09-27

O dono respondeu “perfeito, aceito e siga suas recomendações” à proposta de
aceitar a reauditoria R-008/A 5/6 e não repetir M-004 agora. Registrei a nota
derivada em docs/experimentos/T-139/ensaios-aprovados-2026-09-27/R-008/sealed/A-grade.json
(SHA-256 a56141b7b5075fa62aba13668a9e2f366e8f4523e11515d405aacde66f7ae544).
Ela converte apenas os seis passed: 0/1 da resposta cega em booleanos exigidos
pelo gate do runner, com evidências, resposta candidata, rubrica e hashes da
nota/recibo externos vinculados. O recibo original INVALID não foi alterado.
check_a_grade aceitou o artefato e a comparação local confirmou 5/6 e os
seis critérios quanto à pontuação; não houve nova chamada de modelo.

R-008/B já estava congelado com **9.537 bytes**, SHA-256
dbb52f50bad508e0152dfbdcd171a6bbf51ebc6be5ce4a3eca6b2892d1ce51fb;
workspace A/B idêntico no manifesto
ad3873e72daa1ca941736beac6399129be0bafc1e0a85e6cd074e838eb26bf22,
rubrica bde3eb9e84ac7d954451e06eb5d2379cbc341612ff68198d74f81a8c0bade7ea.
Os bytes/hash conferem com manifesto e congelamento. A varredura local não
encontrou /Users/, email, marcadores de chave/senha nem os nomes pessoais
testados. Em cópia temporária, preflight de B passou com os campos
hipotéticos de aprovação, sem invocar CLI/modelo. A execução real continua
dependendo de autorização específica para esses bytes saírem da máquina.

M-004 permanece sem retry: o corpo sugere 7/7, mas a saída bruta não é JSON
puro. Não há B, réplica, medida de custo até aceite nem prova de ganho ou
economia. Nenhum commit, push, publicação, instalação ou restart foi feito.

⏭️ RETOMAR AQUI — gate único e delimitado: o dono autoriza enviar somente
R-008/prompts/B.txt (9.537 bytes, SHA-256 acima) à Anthropic pela Claude CLI
Opus 5.5, uma chamada, ferramentas desligadas e sem retry, ciente de que
código e instruções sairão da máquina? Se aprovado e a resposta for válida,
preparar a pontuação cega de B para gate próprio; não executar avaliação
externa adicional nem adotar a skill sem nova aprovação.

### R-008/B enviado uma vez; checkpoint de recuperação, 2026-09-27

Após o “sim” do dono para o gate delimitado acima, reli o índice, o board e
esta thread; o resolver do pacote instalado 0.27.11 apontou para este board
canônico e confirmou `exists=true`. O pacote B ainda media **9.537 bytes** e
seu SHA-256 era
`dbb52f50bad508e0152dfbdcd171a6bbf51ebc6be5ce4a3eca6b2892d1ce51fb`,
igual ao manifesto. A varredura local não detectou `/Users/`, email,
marcadores de segredo ou nomes pessoais testados; a Claude CLI estava
autenticada. O preflight completo em cópia temporária passou, inclusive a
nota derivada de A. Uma primeira cópia no temp do sistema foi rejeitada pela
política de caminho do runner (`LOCAL_FORA_TMP`) **antes** de invocar modelo;
a cópia em `/private/tmp` passou.

Executei **uma única chamada** do runner R-008/B pela Claude CLI Opus 5.5,
com ferramentas desligadas e sem retry. Exit 0; modelo efetivo
`claude-opus-5-5`; status `STRUCTURAL_ONLY`; hash da resposta
`508c22b1382740ab9bd3a282153a8416867428bcc1e4853c26e96d1fa2eaa146`.
Os três arquivos `responses/B/answer.md`, `stderr.txt` e `receipt.json` foram
copiados byte a byte para a bancada no worktree e conferidos contra a cópia
temporária. O recibo declarou 10.098 tokens de criação de cache, 531 de
leitura de cache, 2 de entrada, 6.520 de saída e US$ 0,2112982 pela CLI
(não fatura). `quality_proven=false`: saída estrutural não é aprovação.

M-004 continua inválido no formato e não foi repetido. Nenhuma avaliação
externa adicional, adoção, bump, commit, push, publicação, instalação ou
restart ocorreu neste passo.

O pacote cego de pontuação de B foi preparado **somente localmente**, reutilizando
exatamente o cabeçalho e a rubrica do pacote A e trocando apenas a resposta
candidata. Está em
`docs/experimentos/T-139/grading-B-blind/R-008/briefing.md`, com metadados em
`packet.json`: **8.068 bytes**, SHA-256
`73f96e8bb882decc4af878df860b2126106899c047a3c5f0eb8c55be5fc8e63f`.
Os hashes da rubrica, da resposta e do recibo-fonte estão vinculados no
metadado; a conferência local confirmou tamanho/hash, uma seção de rubrica,
uma de candidato, nenhum marcador de braço e nenhum caminho pessoal. Este
pacote **não foi enviado** a nenhum modelo.

⏭️ RETOMAR AQUI — gate próprio: o dono autoriza enviar somente esse briefing
cego congelado de 8.068 bytes a um avaliador externo independente, por uma
única chamada sem retry, ciente de que a resposta candidata e a rubrica
sairão da máquina? Definir o destino/modelo no gate. Só depois comparar A/B e
custo até aceite; este par sozinho não prova ganho, economia nem comportamento
do Manager em sessão viva.

### Nota cega de B concluída e comparada com A, 2026-09-27

O dono respondeu “mudei para o astra — faça” ao gate de avaliação cega do
pacote B de 8.068 bytes. O preflight reconferiu seu hash
`73f96e8bb882decc4af878df860b2126106899c047a3c5f0eb8c55be5fc8e63f`,
a varredura de marcadores sensíveis e a ausência de uma nota B anterior.
Reaproveitei o runner de pontuação com a especificação congelada B em
memória, sem editar código ou congelamento de A.

Uma única chamada da Codex CLI 0.157.1 solicitou `gpt-6-astra@max`, como
na avaliação de A. Exit 0, zero eventos de ferramenta e workspace isolado
inalterado. Parecer JSON válido; recibo `STRUCTURAL_ONLY`, `reasons=[]`.
A CLI não expôs o modelo efetivo. Uso declarado: 21.358 tokens de entrada,
1.381 de saída, incluindo 866 de raciocínio. Não houve retry.

**Resultado auditado: B=5/6; A=5/6.** Ambos receberam zero no critério 5:
faltou a mutação que retire a preservação do LF e prove o teste vermelho.
Os dois indicadores de falha crítica/escopo ficaram `false`. A auditoria
conferiu a resposta candidata contra cada critério e manteve a nota.

Na geração, A usou 9.969 tokens totais de entrada e 5.122 de saída, com
US$ 0,1780422 declarados; B usou 10.631 e 6.520, com US$ 0,2112982.
B custou **18,6787% mais**, sem ganho de nota nesta amostra. São valores
da Claude CLI, não fatura nem custo até aceite; a pontuação externa não está
incluída. O resultado não sustenta promover a skill atual.

Saídas preservadas no worktree:
`docs/experimentos/T-139/grading-B-blind/R-008/grade/`.
Parecer SHA-256
`f0d2d9f247f6f819155f53bfcd3c400d40497ca6da6142dcbec9bc900b95d64d`;
recibo SHA-256
`54dccac642a225e9282be55711424d881c1890e1d906f71f171a34628b6236ff`.
A comparação e a proposta local estão em
`docs/experimentos/T-139/grading-B-blind/R-008/auditoria-local.md`.

Verificação final: os cinco arquivos brutos e a auditoria conferem byte a
byte com o staging; o parecer passa no validador com 5/6 e zero ferramentas.
Na main, suíte 447/447, manifesto estrito, lint e `git diff --check` passaram.

⏭️ RETOMAR AQUI — baseline mantido. Preparar o próximo desenho local com
uma regra curta que peça mutação executável, uma amostra ainda não vista e
um controle sem defeito; congelar critérios de qualidade/custo antes de
novo envio. R-008 agora é diagnóstico, não prova independente para uma regra
construída a partir dele. M-004 permanece sem retry. Nenhuma adoção, bump,
commit, push, publicação, instalação ou restart foi feito.

### Checkpoint de recuperação após compactação — 2026-09-27

O índice `memory/MEMORY.md`, o board canônico resolvido pelo pacote instalado
0.27.11 e esta thread foram relidos. O `T-139` segue em `[~]`, sob
`@frente-jev-router @codex`; a bancada isolada permanece no worktree
`t139-role-skills`. O pedido atual do dono amplia o teste da skill para o
**conjunto de cada papel**: contrato e configuração do agente, skill opcional
e resultado comportamental de Planner, Reviewer e Manager/Orquestrador (uma
única autoridade, em simulação). O A/B R-008 empatou em 5/6, com custo de
geração maior em B; é diagnóstico, não evidência de ganho. M-004 permanece
inválido, sem retry. Próximo passo seguro: inspecionar os contratos e a
bancada, definir controles inéditos e critérios congelados antes de qualquer
novo envio externo. Nenhuma adoção, bump, commit, push, publicação,
instalação ou restart foi autorizado por este pedido.

### Piloto local ampliado ao agente inteiro — 2026-09-27

No worktree T-139, o aditivo ao plano separa instrução do papel, configuração
efetiva da chamada e skill. O probe experimental
`docs/t139_role_bundle_probe.py` compõe A (agente atual), B (agente atual +
ajuste enxuto) e C (B + skill), com SHA de origem, limite de bytes e opt-in
`T-139`. Os candidatos ficam em `docs/experimentos/T-139/candidates/`, fora
do pacote ativo. RED/GREEN e mutation check capturaram ausência do braço,
troca de candidato de papel e divergência da skill Reviewer v2. A CLI local
entregou os bytes exatos em teste, sem modelo.

R-011 (Reviewer, controle limpo) recompôs A/B/C em 2.741/3.252/4.948 bytes.
P-009 (Planner, causa raiz) recompôs 3.189/3.661/5.057 bytes. O próprio
enunciado de P-009 já pede mutação; não usá-lo para alegar que o agente passou
a pedi-la espontaneamente. M-003 simulado recompôs A/B em 37.322/38.971
bytes, acima do teto Anthropic de 16.384; Manager e Orquestrador continuam
uma única autoridade, sem segundo agente. M-004 permanece inválido, sem
retry. O relatório e os hashes estão em
`docs/experimentos/T-139/ensaio-agente-inteiro-local.md` no worktree.

O pacote atual não demonstra qualidade nem economia: P-008 deu um sinal
isolado (5/6→6/6) para Planner com skill; R-008 empatou (5/6→5/6), com
18,7% mais custo de geração no braço com skill. Próximo passo: congelar
casos e runner próprios do A/B/C, incluindo um defeito novo sem dica de
mutação, e só então definir um gate de egress específico. Nada foi enviado
a modelos nesta etapa; não houve adoção, bump, commit, push, publicação,
instalação ou restart.

O preparador `docs/t139_role_bundle_setup.py` acrescentou três workspaces
idênticos por caso e manifestos com `LOCAL_ONLY`, `model_calls=0` e
`runner_ready=false`. R-011 e P-009 foram recompostos em `/private/tmp` sem
egress; repetir o mesmo destino retornou `DESTINO_EXISTE` e preservou o
manifesto. Verificação final no worktree: bancada T-139 **159/159**, suíte
do plugin **435/435**, manifesto estrito, Ruff e `git diff --check` verdes.
O lint do worktree continua vermelho **somente** pela divergência anterior
entre fonte candidata 0.27.10 e cache instalado em `commands/plan-next.md`;
o lint da raiz principal está verde. O runner A/B/C e o caso novo ainda
faltam: não tratar esses manifestos locais como pacote autorizável para
modelo, nem pedir adoção do piloto.

### Recuperação após nova compactação — 2026-09-27

O índice, o board canônico resolvido pelo pacote instalado 0.27.11 e esta
thread foram relidos. O pedido continua sendo medir o conjunto agente +
configuração de invocação + skill para Planner, Reviewer e Manager único.
No worktree isolado, a fixture sintética inédita R-012 foi criada e seu
defeito reproduzido por teste local: `exists=false` gera indevidamente
`CREATE_BOARD`, enquanto o contrato exige parar para inicialização. O patch
de mudança reverte sem conflito. Ainda falta registrá-la no preparador
A/B/C e congelar o runner antes de qualquer teste com modelo; nenhum envio
externo foi feito nesta etapa.

### R-012 e via efetiva do Reviewer — 2026-09-27

O novo caso R-012 foi registrado somente na lista `LOCAL_ONLY_CASES` e
recomposto em A/B/C: os três workspaces têm SHA
`4329caf4c3b1941602bbf70435d312d60db01092c84ebe86c32655a5e6035864`.
O enunciado não pede mutação; o defeito sintético `exists=false` →
`CREATE_BOARD` foi reproduzido localmente, sem tocar no board verdadeiro.

Auditoria da invocação revelou um erro de preparo: no host Codex o Reviewer
usa Opus por Claude CLI **sem ferramentas**, então um prompt que apenas pede
leitura de caminhos não entrega os arquivos. O preparador A/B/C passou a
embutir as fontes fictícias completas e numeradas e usar enunciados
compatíveis com a via sem ferramentas. R-011 ficou com
6.719/7.230/8.926 bytes; R-012, 7.412/7.923/9.619 bytes, todos abaixo do
teto de 16.384. O teste RED/GREEN verificou a presença do conteúdo e a
igualdade entre workspaces. Estes manifestos continuam `LOCAL_ONLY`, com
`runner_ready=false` e zero chamadas de modelo. Qualidade, economia e
configuração efetiva do CLI em uma chamada real seguem não provadas.

Os pacotes locais R-011, R-012 e P-009 foram congelados por SHA de
manifesto em `docs/T-139-role-bundle-freeze.json` e conferidos por
recomposição de fonte, prompts e workspaces. O verificador é read-only e
retorna `FROZEN_LOCAL`, nunca autorização de egress. Testes de mutação
recusaram manifesto reclassificado, prompt/workspace alterado e fonte
candidata divergente. Runner A/B/C, parâmetros da chamada, custo e
avaliação cega ainda faltam; não executar modelos com esse pacote local.

Verificação após o congelamento: bancada T-139 **166/166** (inclui RED/GREEN
e recusa de mutações do snapshot), suíte do plugin **435/435**, manifesto
estrito e Ruff verdes. `git diff --check` passou para os arquivos rastreados;
o scan dos novos encontrou só linhas de contexto válidas em `changes.patch`.
O lint da raiz principal passou. O lint do worktree candidato continua com a
mesma única divergência anterior de cache
`bytes:commands/plan-next.md` na 0.27.10 — não foi causada por este ensaio,
mas impede alegar todos os gates verdes no worktree. Nenhum arquivo de
produto `orq/` foi ativado, nem houve commit, push, publicação, instalação,
restart ou chamada de modelo.

### Checkpoint de recuperação e runner A/B/C local — 2026-09-28

Após compactação, reli `memory/MEMORY.md`, o board canônico via
`kanban-status.sh --resolver .` (`state=ok`, `exists=true`) e esta thread.
O T-139 segue em `[~]` sob `@frente-jev-router @codex`; preservei os
worktrees e as alterações de outras frentes. No worktree T-139, o runner
`docs/t139_role_bundle_run.py` agora recusa divergência dos hashes aprovados
de manifesto, prompt, workspace, rubrica e invocação antes de qualquer CLI.
O freeze de invocação fixa modelo/effort, via, ferramentas, sandbox,
contexto, timeout, comando e digests das fontes do runner/auditoria. Um
braço só pode rodar uma vez; B depende da nota válida de A, C da nota válida
de B, ambos abaixo do teto. O Reviewer exige o mesmo modelo efetivo;
o Planner escreve apenas o plano numa cópia de execução temporária, sem
alterar o workspace congelado.

RED/GREEN local: testes de timeout, hash, fonte do runner e comando mutado
recusaram a chamada antes da CLI; CLIs falsas exercitaram A/B/C nas duas vias.
Nenhuma chamada real, avaliação cega, adoção, commit, push, instalação ou
restart ocorreu nesta etapa. O primeiro manifesto tinha `runner_ready=false`;
foi substituído por novo freeze local com `runner_ready=true`, preservando os
pacotes antigos sem aceitá-los para execução. No preflight da nota cega,
R-011 e P-009 ainda descreviam o ensaio antigo de dois braços. A suíte
completa revelou que as rubricas eram compartilhadas com snapshots antigos;
preservei seus bytes e criei duas rubricas exclusivas do A/B/C, sem atribuir
skill a B nem dar a dica de parada ao avaliador. Os pacotes vigentes
R-011/R-012/P-009 em `/private/tmp/t139-role-abc.U5i98P/` passaram
`FROZEN_LOCAL`, com zero
chamadas. Esse campo não é permissão para egress. O modelo efetivo na via Codex continua
sem recibo. Próximo: construir o gate de nota
cega e custo até aceite; qualquer envio real requer autorização delimitada
do dono. Evidências em
`docs/experimentos/T-139/ensaio-agente-inteiro-local.md` do worktree.

Verificação do novo freeze: 3/3 pacotes `FROZEN_LOCAL` e 3/3 preflights
de A aceitos sem invocar modelo; bancada T-139
**178/178** (sandbox aninhado permitido), suíte do plugin **435/435**,
manifesto estrito, Ruff, lint da main e checks de whitespace verdes.
O lint do worktree candidato conserva a única divergência anterior entre
0.27.10 e cache instalado (`bytes:commands/plan-next.md`); não há release
ou instalação autorizados neste T-139.

### Recuperação após compactação — 2026-09-28

Reli `memory/MEMORY.md`, confirmei o pacote instalado 0.27.11 e resolvi o
quadro canônico com `kanban-status.sh --resolver .` (`state=ok`,
`exists=true`). Li o card T-139 em `[~]`, sob `@frente-jev-router @codex`,
e esta thread no `thread_root` devolvido. O pedido atual é prosseguir na
preparação local da nota cega para R-011/R-012/P-009, preservando os
worktrees e snapshots históricos. Nenhuma chamada de modelo, egress,
adoção, commit, push, publicação, instalação ou restart foi autorizada
nesta retomada. Próximo ponto: recibo independente de avaliação e custo
até aceite, com testes RED/GREEN antes de qualquer execução real.

### Nota cega cruzada local — 2026-09-28

No worktree T-139, `docs/t139_role_bundle_grade.py` prepara o pacote cego
sanitizado e a via oposta de avaliação: Reviewer/Opus é avaliado por
Codex/Astra; Planner/Codex, por Claude/Opus. O perfil do avaliador e o
pacote exigem SHA aprovados antes de uma única chamada, sem retry. O
Codex recebe instrução de não usar ferramentas e qualquer evento de
ferramenta invalida a nota depois da chamada; isso não desativa suas
ferramentas preventivamente. Na via Claude, elas estão desativadas. O
recibo vincula pacote, resposta original, nota lacrada, JSON bruto,
transcript, modelo solicitado/efetivo quando observável e uso. O runner
A/B/C recusa B/C sem esse recibo íntegro; nota JSON avulsa já não libera
o próximo braço. `cost_to_blind_threshold` inclui geração e avaliação até
o teto cego, mas só soma USD se todos os recibos tiverem preço. Não
atribui aceite humano nem prova de economia.

RED/GREEN: nota sem recibo, recibo alterado, nota divergente do JSON bruto,
symlink no caminho da resposta e hashes de autorização foram recusados
antes da CLI; as duas vias foram exercitadas apenas com CLIs falsas.
Nenhuma avaliação real, egress, adoção, commit, push, publicação,
instalação ou restart nesta etapa. O freeze de invocação mudou porque o
runner foi reforçado; os três pacotes de fonte continuam `FROZEN_LOCAL`.
Gates locais: bancada T-139 **191/191**, suíte do plugin **435/435**,
manifesto estrito, Ruff e três pacotes `FROZEN_LOCAL` verdes. Lint da
main verde; lint do worktree conserva a divergência fonte/cache
0.27.10 anterior (`bytes:commands/plan-next.md`).
Próximo: auditar os pacotes exatos antes de
solicitar autorização delimitada para qualquer envio. O modelo efetivo
do Codex continua sem prova.

### Checkpoint parcial — capacidade de nota cega no Codex CLI, 2026-09-28

Após a compactação, reli o índice, resolvi o board canônico pelo pacote
Orquestra instalado 0.27.11 (`state=ok`, `exists=true`) e confirmei esta
thread na raiz principal. A recuperação do worktree T-139 **não passou**:
o resolver aponta seu `thread_root` próprio, onde a thread indicada pelo
card não existe. Não criei cópia nem usei a thread da raiz como fallback
para operações no worktree.

Investigação read-only: o Codex CLI instalado é 0.157.1. O runner atual
desativa hooks/plugins/apps/browser/computer/MCP, mas ativa
`code_mode_host`; não desativa `shell_tool` nem `unified_exec`. A
documentação oficial descreve `--sandbox read-only` como política para
comandos e `features.shell_tool=false` como desativação apenas da ferramenta
shell padrão. Não foi comprovado um contrato preventivo de **zero
ferramentas** para `codex exec`; prompt e auditoria posterior não equivalem
a esse bloqueio. Nenhum pacote real foi enviado e nenhum runner foi alterado.
Próximo gate: sanar a ausência da thread no worktree e decidir se o
requisito estrito de zero ferramentas exige outra via de avaliação ou um
preflight sintético, separadamente autorizado, das flags candidatas.

### Checkpoint de recuperação e preflight sintético — 2026-09-28

Após nova compactação, reli `memory/MEMORY.md`, resolvi novamente o board
canônico pelo pacote Orquestra 0.27.11 (`state=ok`, `exists=true`), li o card
T-139 e esta thread. A thread permanece **não rastreada na raiz principal** e
ausente no `thread_root` do worktree T-139. Pelo contrato de recuperação do
Orquestra, não a copiei, dupliquei nem usei a raiz como fallback para editar
o worktree; o trabalho de produto nesse checkout permanece suspenso.

O Codex CLI observado agora é 0.158.0. Uma única chamada sintética, sem
código do projeto, usou `--sandbox read-only` e desativou hooks, plugins,
apps, MCP, shell, `unified_exec`, `code_mode_host` e `multi_agent`. Respondeu
`SEM_FERRAMENTA` sem evento de comando executado, porém o fluxo também
continha um evento `error` sem detalhe preservado; essa resposta **não prova**
ausência preventiva de ferramentas. Não houve retry nem envio dos pacotes
R-011/R-012/P-009.

Uma sondagem posterior ficou estritamente em `127.0.0.1`: provedor HTTP
fictício capturou o pedido Responses da mesma configuração candidata e o
interrompeu com HTTP 400, sem invocar modelo. O pedido continha um item
`additional_tools` com dez ferramentas: `functions` (`exec`, `wait`,
`request_user_input`, `request_user_input_async`) e `collaboration`
(`followup_task`, `interrupt_agent`, `list_agents`, `send_message`,
`spawn_agent`, `wait_agent`). Logo, as flags candidatas não satisfazem o
requisito de **zero ferramentas expostas ao avaliador**. Nenhum runner,
pacote congelado, cache ou configuração de host foi alterado; não houve
commit, push, publicação, instalação ou restart.

Próximo gate: reconciliar a thread do T-139 no worktree pela via canônica,
sem perder a versão não rastreada da main; depois escolher e provar uma via
de avaliação Codex com zero ferramentas ou rever explicitamente esse
requisito antes de qualquer egress dos pacotes reais.

### Checkpoint de recuperação — 2026-09-28 (após compactação)

Relidos o índice `memory/MEMORY.md`, o board canônico resolvido pelo pacote
Orquestra 0.27.11 (`state=ok`, `exists=true`) e esta thread. Na `main` em
`4e58e7f`, o card T-139 aparece somente no `KANBAN.md` modificado, e esta
thread continua não rastreada; nenhum dos dois existe no `HEAD`. O board
também contém alterações de outras frentes. Preservei os arquivos e não
estagiei, commitei, copiei nem editei o worktree T-139.

A documentação oficial do Codex consultada para `codex exec` e App Server
descreve controles de sandbox e de features, mas não documenta um controle
que retire todas as ferramentas do avaliador. Isso não é prova de
impossibilidade: a prova local de loopback acima é específica para as flags
candidatas na CLI 0.158.0 e mostra dez ferramentas ainda expostas. Sem via
zero-tools comprovada, os pacotes reais de A/B/C continuam bloqueados.

Foi preparado um handoff diagnóstico e read-only para uma sessão curta do
Claude testar apenas a integração Claude Code → Codex Companion na CLI
0.158.0. Esse teste não substitui o gate zero-tools do T-139. Nenhum pacote
real foi enviado, e não houve commit, push, instalação ou restart.

### Checkpoint de recuperação — 2026-09-28 (auditoria local dos pacotes)

Após a compactação, reli `memory/MEMORY.md`, resolvi o board canônico pelo
pacote Orquestra 0.27.11 (`state=ok`, `exists=true`) e reli o card e esta
thread. A thread já havia sido reconciliada, sem sobrescrita, no worktree
isolado T-139; o board principal permanece canônico.

No worktree, a bancada `test_t139_*.py` passou **191/191**. Revalidei os três
pacotes vigentes em `/private/tmp/t139-role-abc.U5i98P/` com
`t139_role_bundle_freeze.py`: P-009, R-011 e R-012 retornaram
`FROZEN_LOCAL` com exit 0 e `model_calls=0`. O status Git do worktree segue
com alterações de produto e arquivos não rastreados preservados; nenhum
bytecode novo foi detectado. Este preflight local não prova qualidade, custo
nem ausência efetiva de ferramentas no avaliador Codex. Os pacotes reais
continuam sem egress; não houve commit, push, publicação, instalação ou
restart nesta auditoria.

## ⏭️ RETOMAR AQUI — 2026-09-29, decisão do dono sobre zero-tools

O dono aprovou seguir a recomendação do T-139 **sem afrouxar** o requisito:
avaliador Codex com ausência preventiva de ferramentas, comprovada no
runtime, antes de qualquer envio dos pacotes reais. A resposta curta do
Companion 1.0.5 na CLI 0.158.0 confirma apenas a chamada read-only bem-sucedida,
não o requisito zero-tools. A documentação oficial da API permite
`tool_choice: "none"` em outra superfície, mas ainda não há ponte comprovada
desse controle para `codex exec`/Companion. Portanto P-009/R-011/R-012
permanecem `FROZEN_LOCAL`, sem egress, adoção ou alegação de economia.

A frente local pode investigar uma superfície de execução que imponha
zero-tools e preservar o pacote congelado. Não trocar o avaliador nem enviar
o material real por conveniência sem novo gate específico. O board canônico
segue no `main`; este registro não move o card nem altera o worktree isolado.

### Arquitetura e portabilidade — 2026-09-29

O dono aprovou a direção do desenho enxuto: Manager único, agentes
especializados e delegação sob demanda, com esforço proporcional. Pediu
avaliar Orca como IDE principal. A portabilidade foi separada no T-141,
com desenho próprio, para não mudar harness/modelo nos A/B/C congelados.

Orca local está pronto segundo `status`, e seus guias documentam launch
de Codex/Claude por CLI com preferências explícitas. Isso não comprova
hooks, modelo efetivo, zero-tools ou ganho. O requisito preventivo do
avaliador Codex continua intacto; P-009/R-011/R-012 sem novo egress.
T-139 não foi declarado adotado nem encerrado. Nenhuma edição do worktree
isolado, chamada externa, instalação, publicação ou restart nesta análise.
