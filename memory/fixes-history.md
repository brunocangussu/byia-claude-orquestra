# Log de mudanças — append-only

## [2026-09-01] feat | 0.24.0 — elenco em dois eixos, revisor único cross-vendor, Kimi aposentado (T-051)

O dono pediu duas coisas na mesma conversa: retirar o Kimi (assinatura a cancelar) e redistribuir os
modelos por tipo de trabalho, a partir de uma configuração de referência que ele trouxe. Viraram **um
card só** porque batiam nos mesmos arquivos — separar seria o retrabalho que `T-023`/`T-025`/`T-020`
já pagaram.

**A leitura da referência foi corrigida pelo dono, no gate, e essa correção é o card.** O plano v1
colapsou a configuração num eixo só (dificuldade). Ele apontou: *"ou você interpretou errado ou você
viu errado?"* — e tinha razão. A referência tem **dois eixos**, e o segundo escolhe o **vendor**:
interface/experiência → Anthropic (`Frontend→Opus`, `Hard UI/UX→Fable`, `Simple UI→Sonnet`);
sistema/lógica → OpenAI (`Architecture→Sol`, `Backend→Sol`, `Normal coding→Terra`,
`Small changes→Luna`). Generalizado, o eixo **não é frontend/backend, é interface vs sistema** — CLI
é sistema, brand book é interface, e projeto sem UI só não usa a linha de cima.

**O eixo só sobrevive porque a escrita não cruza vendor.** A matriz completa exigiria um vendor
escrevendo no host do outro, o que segue **fora do desenho** (`T-021`, um writer por worktree). A
síntese que o dono aprovou: **"domínio decide quem pensa; host decide quem escreve"** — `planner` e
`reviewer` são read-only e cruzam vendor (mecanismo já comprovado: `codex exec -s read-only` e
`run-opus-reviewer.py`); `implementer`, `docs` e `scout` ficam no vendor do host.

**O painel morreu.** Regra do dono, verbatim: *"sempre tem que ser com um revisor de uma LLM
diferente; se eu estiver no Claude, o revisor tem que ser do GPT, e se eu estiver no GPT, do
Claude"*. Revisor **único, vendor oposto ao host, sem exceção** — ele escolheu a regra pura **contra
a recomendação do planner**, que propunha três exceções. Consequências assumidas e escritas no
produto: diff com dado sensível fica **sem revisor nenhum** (LGPD impede o vendor oposto, e não há
substituto interno — o Manager audita e declara a ausência); titular fora do ar → REVISÃO DEGRADADA
e o card não avança sozinho; `--rapido` vira briefing enxuto para o mesmo titular externo.
*"Confirmado por 2+"* deixou de existir.

**Sete rodadas de review externo, 25 bloqueadores.** Contagem por rodada: **5 → 8 → 4 → 5 → 2 → 1 →
0 (APROVADO)**. Os gates ficaram **verdes em todas elas** — inclusive com os oito da rodada 2
presentes. Os achados mais caros: (a) o elenco tinha **duas fontes de verdade** — `## Papéis` se
declarava ativa e era o que os perfis reescreviam, enquanto os consumidores liam `## Times por host`,
então `perfil economia` no Codex era **inócuo**; `## Papéis` foi eliminada; (b) a correção do piso de
faixa **apagou o piso de Alto risco**, deixando schema/segurança cair no implementer mais fraco; (c)
o exemplo canônico de roteamento da SKILL (*"implemento com o Sonnet e mando revisar pelo GPT"*) era
**duplamente inválido no Codex** — virou nomeação de papéis resolvidos, sem modelo concreto; (d) o
comando aceitava registrar `fable` como planner no Codex, mas o runner invoca `--model opus` fixo —
elenco declarava um modelo e executava outro, calado.

**Cobertura mecânica subiu de 2 para 5 famílias de defeito**, com 9 regressões negativas provadas.
Mas **22 dos 25 bloqueadores vieram de coerência entre superfícies**, que segue manual.

Smoke do `gpt-5.6-luna`: **passou** (`LUNA_OK`, thread `01a05e0d-309c-7a92-839c-09f6c418a974`),
liberando o degrau `implementer·leve` do Codex — **sem effort declarado**, porque o smoke provou que
o modelo responde, não quais efforts aceita nem como se comporta em `workspace-write`.

Branch `feat/t051-elenco-por-tarefa`, 18 arquivos, `0.24.0` nos quatro lugares. **Sem commit, sem
push, sem publicação** — o release aguarda ordem do dono. Estado honesto: *instalado, não validado*.

## [2026-08-29] checkpoint | @frente-auditoria-nativa · T-048 aprovado e reconciliado com a main

Após compactação, o estado foi relido e a colisão com a T-046 já publicada na 0.22.4 foi detectada.
O novo card foi renumerado para T-048 porque a main atual já possui T-047. O desenho está aprovado e
a implementação TDD seguirá no worktree isolado baseado em `origin/main`, sem tocar hooks, instalar,
publicar ou enviar ao GitHub neste gate.

## [2026-08-29] plan | @frente-auditoria-nativa · T-045 fechado e T-048 desenhado sem hooks

O dono validou “PORTAR IDEIAS”, fechando o piloto Cartographer. O follow-up T-048 propõe dois
auditores nativos, explícitos e offline: ledger de remoção e verificador de trace graph-first. A
fase 1 exclui hooks, bloqueios, captura live, rede e dependência Cartographer; aguarda aprovação.

## [2026-08-29] investig | @frente-cartographer · microbench favorece stack atual e isola uma ideia útil

Fixture sintética pré-declarada comparou Cartographer, codebase-memory e o fallback textual do stack.
O Cartographer cobriu 11/13 âncoras, contra 13/13 do stack atual, e tratou histórico como ativo; seu
verificador `adoption` distinguiu corretamente graph-first de leitura-direta-primeiro. Parecer:
portar as ideias de ledger/adoption, sem instalar ou integrar a dependência.

## [2026-08-29] investig | @frente-paridade-codex · avaliação do Cartographer recuperada após compactação

A análise read-only do `kingbootoshi/cartographer` foi recuperada após compactação sem checkpoint:
o candidato oferece grafo SQLite local, briefs delimitados, auditoria de remoção e medição de
adoção, mas sobrepõe codebase-memory/Serena. Nenhuma instalação, dependência ou mudança no produto
foi feita; a decisão de adotar continua aberta e depende do parecer comparativo desta sessão.

## [2026-08-13] incidente | @frente-protecao-contexto · T-043 bloqueou threads após checkpoint

O `/goal` coincidiu com o travamento, mas o banco local não tinha metas: o cache ativo `0.22.0`
ainda devolvia `decision: block` e reconstruía `emergency` a partir do transcript alto. Resetar só
o JSON não durava. Sete estados detectados receberam exceção `.allow` recuperável, com backup; a
sessão informada pelo dono passou smoke sem bloqueio. O hotfix é operacional. A correção permanente
ficou no gate: checkpoint consultivo, mesma conversa continua e compactação nativa permanece livre.

## [2026-08-10] instalação local | T-043 · 0.22.0 ativa no Codex

A `0.22.0` foi integrada por fast-forward em `main`, reinstalada pelo marketplace local e ficou
`installed, enabled`. Os seis hooks foram revisados e confiados na UI sem bypass. Uma sessão Codex
nova criou estado real no `PLUGIN_DATA` com `last_percent=3.19`; o estado contém somente as sete
chaves permitidas. O smoke do cache cobriu checkpoint em 60%, handshake, bloqueio até `/clear` e
reidratação. O arquivo global `~/.codex/hooks.json` ainda gera aviso por `_managedBy`, problema
pré-existente que não impediu os hooks do plugin de rodar. Sem push e sem backstop global.

## [2026-08-10] review+correção | T-043 · painel fecha sem bloqueadores

Opus 5 e Kimi K3 revisaram a candidata final sequencialmente e devolveram
`APROVADO_COM_RESSALVAS`, sem bloqueadores. Antes disso, o painel encontrou e os testes
reproduziram falso handshake de `/clear`, checkpoint falho sem retry, corrida read-modify-write,
estado inválido silencioso e lock órfão. A correção usa frase afirmativa ancorada, retry
conservador, `flock` liberado pelo SO, marcador de reset e falha aberta visível. A corrida residual
do marcador e o fallback Windows viraram `T-044`; ambos erram para over-enforcement, não bypass.

## [2026-08-09] feature local | 0.22.0 protege contexto antes do clear

O `T-043` adicionou guardião Codex por hooks: pré-alerta em 55%, checkpoint obrigatório no primeiro
valor observado ≥60%, contingência em 70% e bloqueio de trabalho novo depois da frase verificada
“Seguro dar `/clear`”. Estado é isolado por sessão em `PLUGIN_DATA`, sem conteúdo da conversa; erros
de telemetria falham abertos e compactação automática continua permitida como backstop. Release
ainda local: sem instalação, configuração global, publicação ou push neste registro.

## [2026-08-09] publicação | 0.21.0 no GitHub com runner Opus 5 comprovado

O dono autorizou o push após a validação local. `origin/main` avançou de `164387c` para `6ba462b`;
o remoto foi relido e confirmou versão `0.21.0`, referência a `run-opus-reviewer.py` no painel e o
guard `OPUS_MODEL_MISMATCH` no script distribuído. O card segue em VALIDATE até o dono repetir a
revisão no projeto real que originou o relato.

## [2026-08-09] correção de evidência | smoke externo criou metadado Serena fora do escopo

A entrada de validação abaixo diz que o workspace de teste permaneceu limpo. Escopo correto: os
arquivos do smoke não mudaram; o hook de início da sessão criou `.serena/` como untracked. Não foi
escrita do Orquestra/Opus, mas impede chamar a árvore inteira de limpa. O diretório temporário foi
descartado após a conferência.

## [2026-08-09] validação | T-041 · Opus 5 comprovado em projeto externo pelo plugin instalado

Claude e Codex receberam `orq 0.21.0`; os dois caches ficaram byte-idênticos à fonte. Uma nova
sessão Codex num projeto temporário carregou a skill do cache, passou o gate LGPD e disparou o painel
real. O runner devolveu exit 0, `OPUS_MODEL=claude-opus-5` e parecer não vazio; Kimi K3 também saiu
com exit 0 e confirmou o mesmo bloqueador. O workspace de teste permaneceu limpo. O GitHub foi
verificado separadamente e ainda entrega `0.20.0`, sem runner: push depende do gate explícito.

## [2026-08-09] fix+prova | T-041 · Opus 5 deixa de falhar em silêncio no Host Codex

O relato de outro projeto expôs duas causas. A instalação real ainda estava em `0.20.0`, cuja regra
do Host Codex nunca invocava Claude/Opus. Na candidata `0.21.0`, chamadas diretas comprovaram
`claude-opus-5`, mas briefings de 31–40 KB reproduziram timeout de 180–300s sem diagnóstico. Foi
adicionado um runner stdlib: limite de 16 KiB por lote, anúncio imediato, timeout de 240s, JSON obrigatório,
comprovação de `modelUsage`, saída não vazia e códigos explícitos para cada falha. Quatorze testes
RED→GREEN cobrem sucesso, modelo errado, excesso de entrada e timeout. Falta reinstalar e rodar o
smoke do plugin em projeto externo antes de publicar.

## [2026-08-09] review+correção | T-041 · painel Codex sem diagonal e despacho comprovável

Opus 5 e Kimi K3 reprovaram a primeira candidata por uma contradição concreta: a regra genérica da
diagonal podia acrescentar um terceiro parecer OpenAI ao painel Codex, embora o dono tivesse fixado
exatamente Opus 5 + Kimi K3. A correção também tornou `codex exec` o caminho padrão para Planner e
Implementer, introduziu `ORQ_PACKAGE_ROOT` e substituiu o lint permissivo por contratos por arquivo.
Na segunda rodada, ambos aprovaram com ressalvas; defaults sem elenco, alias Opus, raiz Kimi e guards
de degradação foram fechados com probes RED→GREEN. Nenhuma tentativa expirada contou como parecer.

## [2026-08-09] implementação | T-041 · paridade core do Codex candidata a 0.21.0

O produto passou a distinguir plugin instalado/habilitado, cache coerente, skill carregada e smoke
comportamental. No Codex a interface oficial é linguagem natural + `/skills`; ausência de `/orq`
não é falha. O template do elenco agora gera `Matriz de invocação` e `Times por host`, e os
consumidores resolvem host→papel→executor. Time aprovado: Manager Sol/high, Planner Sol/ultra,
Implementer Terra/xhigh, painel Opus 5 + Kimi K3. Projeto com memória preexistente sem board é
classificado como memória legada, não virgem. Candidata local aguardando painel e commit; sem
publicação, cache global ou push.

## [2026-08-09] release+processo | @frente-statusline · 0.20.0 no ar, o painel cobrou 12 pareceres, e o Codex virou host padrão

Continuação do bloco de 07→08. O card `T-036` fechou o ciclo e foi para VALIDATE.

**O que saiu na 0.20.0** (commit `164387c`, push `b62b39c..164387c`): árvore de **três folhas** com
um predicado binário (o alvo **diretamente invocado** aponta para dentro do plugin?), a folha que
não é nossa **nunca escreve**, e o asset novo `orq/scripts/statusline.sh` — a barra completa
distribuída com o plugin. Mais o tripwire do lint e o merge seguro de settings.

**O que o painel custou e o que só ele acharia** — 5 rodadas, **12 pareceres**, e o veredito foi
REPROVADO em todas até a última:

- a **verificação criada para impedir o bug não pegava o bug**: asseria sobre um arquivo que o
  comando nunca escreve, e só rodava se o próprio modelo se auto-classificasse como "instalei algo";
- o guarda `[ -x ]` num script invocado via `sh` — sem `jq`, a barra saía **inteira vazia**;
- **injeção de código** no `awk` do custo (PoC comprovado);
- `jq '…' arquivo > arquivo` **trunca para 0 byte** — e era a forma que a instrução de "mescle, não
  sobrescreva" deixava o executor escrever;
- settings **vazio** fazia a instalação falhar **em silêncio**: `jq` sem entrada devolve 0 bytes com
  exit 0, a validação aprova, o `mv` conclui, e a chave nunca é criada (provado por 2 revisores,
  cada um executando);
- e, na verificação final, a opção **"remover a chave"** — que eu tinha acrescentado porque foi ela
  que consertou o incidente real — **desfazia o próprio conserto**: copiou o critério de sucesso da
  migração (exigir o board na saída) para uma barra alheia, que não tem obrigação de mostrar board,
  e o desfecho de "falhou" era restaurar a chave defeituosa.

**Duas regressões introduzidas por correções** (o padrão que o `T-014`→`T-016` já tinha mostrado):
a de cima, e a guarda "incondicional" que reprovava o caminho feliz — **pela terceira vez** neste
card a mesma família. O que finalmente quebrou o ciclo não foi mais leitura: foi **partir o card**
(a composição saiu para o `T-038`), reduzindo a superfície.

**Erros do Manager registrados de propósito:**
1. **Varredura rasa** (1 nível) concluiu "só um projeto afetado". O dono falou em "projetos", no
   plural, e insistiu — a de 6 níveis achou o segundo, com a chave **commitada**.
2. **Emenda derrubada por 2 revisores:** propus stamp de versão nas cópias; ele faz o `diff` do
   re-sync divergir **sempre**, virando alarme crônico.
3. **All-clear falso:** reportei "resíduo limpo" com base num `grep` que voltava vazio porque o
   arquivo estava **staged no índice do git como blob vazio**. Teria entrado no commit.
4. **Afirmação exagerada no `T-039`:** escrevi que o `init` "monta a estrutura nova ao lado da
   antiga, sem migrar nem avisar" — **falso**, verificado depois no `init.md:174-187`: ele preserva
   e cria ponteiro. Corrigido no card. O defeito real é comunicar mal e entregar só o ponteiro.

**Decisões do dono neste bloco:** partir o card (`T-038` nasce) · publicar a 0.20.0 · **adotar o
Codex como host padrão**.

**Requisito de origem reafirmado por ele:** *"instalar em projetos já em andamento — acrescentar o
que existe e melhorias, não alterar"*. O princípio **estava** implementado para `CLAUDE.md`/
`AGENTS.md` (bloco delimitado, conteúdo externo preservado) e **faltou onde a destruição é
indireta**: statusline (por precedência — o `T-036`) e memória (o `T-039`). Isso reclassifica o
`T-039` de melhoria para **dívida**.

**Fora deste repo, mapeado e não executado:** migração de memória do `Bruno Vascular`. Achado que
inverte o trabalho — **6 dos 11 snapshots de lá já são páginas vivas** (autodeclaram "como funciona
HOJE" e "esta vence a anterior"); a migração é consolidar, não extrair. Risco principal: **três
conclusões foram revogadas** por auditorias posteriores e os números velhos ainda estão nos
arquivos — consolidar por cronologia faria a wiki nova **nascer com dado errado**.
⚠️ **Regra de dados:** aquele projeto tem PII de paciente, então **a migração não pode ser feita
pelo Codex nem pelo Kimi** (transferência internacional). Fica com host Anthropic.
⚠️ Achado de segurança **fora do escopo do Orquestra**, reportado ao dono: o
`workflow_secretaria.json` de lá tem PII e token em texto puro, nunca revisado.

## [2026-08-08] bug+processo | @frente-statusline · o `/orq:init` apagou a statusline do dono em dois projetos, e o painel reprovou a correção 8×

Bloco da noite de 07 para 08. Começou com o dono notando que a barra dele tinha "ficado mais
simples" depois de um `/orq:init`.

**O bug.** O `/orq:init` gravava a chave `statusLine` no settings **do projeto** sem checar se já
havia statusline no settings **global**. Settings de projeto vencem o global por precedência → a
barra rica do dono (modelo · effort · contexto · custo · rate-limit · git · **board**) foi
**anulada** em `IVA - App System` e em `Prompts - Byia/prompts-byia-clientes`. O diff foi `+4 -0` —
**puramente aditivo**, invisível a qualquer verificação de "sobrescrevi arquivo?". A instrução tinha
a ressalva certa ("se já houver statusline customizada, não sobrescreva") mas **não dizia em que
escopo procurar**: o executor olhou o settings do projeto, viu vazio, e gravou. Os dois projetos
foram revertidos à mão; no segundo a chave estava **commitada** (`fa1363c`), então a reversão também
virou commit (`41fa1f9`).

**Erro do Manager no diagnóstico, registrado porque quase escondeu metade do problema:** a primeira
varredura desceu **1 nível** (`~/Projetos DEV - Cursor/*/`) e concluiu "só o IVA". O dono falou em
"projetos", no plural, e insistiu — a varredura de 6 níveis achou o segundo. Varredura rasa dá falso
negativo com cara de conclusão.

**O que o painel custou e o que entregou.** Três rodadas, oito pareceres (Opus · Codex · Kimi),
**oito reprovações**. Vale registrar *o que* ele pegou, porque nada disso apareceria em teste:

- a **verificação criada para impedir o bug não pegava o bug** — asseria sobre um arquivo que o
  comando nunca escreve, e só rodava se o próprio modelo se auto-classificasse como "instalei algo";
- a instrução de merge que existia para **impedir destruição de arquivo** não dava o comando, e a
  forma óbvia (`jq '…' arquivo > arquivo`) **trunca o arquivo para zero byte**;
- o guarda `[ -x ]` num script invocado via `sh` — sem `jq` e sem o bit, a barra saía **vazia**;
- **injeção de código**: o `awk` do custo interpolava o dado dentro do *programa* (PoC comprovado);
- a guarda de metacaracteres do parser de `command` não cobria `>`, `<` e `&`, e o `eval echo`
  fechava o ciclo: conteúdo de settings podia **disparar processo na fase declarada read-only**.

**A emenda do Manager que os revisores derrubaram:** propus stamp de versão nas cópias para tornar o
drift detectável. Dois revisores mostraram que isso **quebra o próprio re-sync** — a cópia ganha a
linha, a fonte não, o `diff` diverge **sempre**, e o `--reinstalar` vira alarme crônico. A ideia
estava certa; a execução se auto-sabotava.

**Três desenhos, e o terceiro veio do dono.** v1/v2 = árvore de decisão com ramos mais um "legado"
transversal; reprovada 5× porque os bloqueadores caíam nas **interseções**. Ofereci duas saídas
(simplificar para "nunca escreve" · manter edição automática) e **ele recusou as duas**: *"o script
pesquisaria se já existe uma board, veria qual é a arquitetura dessa board, e incluiria nela a parte
das tasks"*. A v3 responde a isso sem pedir juízo: **não entender o script**, mas encolher o que
precisa ser entendido até caber em checagens binárias, inserir um **bloco-sufixo no fim do fluxo**
(nunca editar linha alheia) e **provar por experimento** — a saída antiga tem que ser **prefixo
byte-a-byte** da nova, senão restaura o backup. Validada com **9 fixtures executáveis**, incluindo
uma que escreve, reprova, reverte e prova a restauração com `cmp`.

**Desfecho: card partido, por decisão do dono.** O `T-036` fica com o conserto + F1/F2/F3 + o asset
saneado; a composição (F4 + `compor-statusline.md`) virou **`T-038`**. Razão: o conserto está maduro
e resolve o problema real; a composição consumia rodada após rodada — e **na máquina do dono ela
nunca dispara**, porque a barra dele já mostra o board.

**Nada foi commitado nem publicado.** A 0.20.0 está bumpada nos quatro lugares, no working tree.

## [2026-08-07] processo | @release-validacao · a 0.19.0 no ar nos três hosts, e o painel reprovou o próprio release

Bloco da noite de 06 para 07.

**Release fechado.** A 0.19.0 saiu do limbo "commitada mas não instalada": `marketplace update` +
`plugin update` + restart (cache `0.19.0`, `diff -rq` vazio), e os três commits pendentes foram para
o GitHub (`7c14aa9..b62b39c`). O repositório é público, então **quem instalar agora recebe a 0.19.0**
— até ontem recebia a 0.18.0.

**Instalado nos outros dois hosts, o Kimi pela primeira vez.** Codex por `codex plugin add`
(installed+enabled, `diff -rq` vazio). Kimi por cópia para `~/.agents/skills/orq/` e
`~/.kimi-code/agents/`; as cinco verificações do `instalar.md` bateram.

**O `~/.kimi-code/agents/` deixou de ser hipótese** — o diretório aceitou os cinco `orq-*.md`. O que
segue **não** exercitado é o Kimi *usar* esses agentes: copiar não é invocar.

**O smoke do Kimi passou, e vale como validação SEM viés.** `kimi -m kimi-code/k3 -p "onde paramos?"`
num worktree descartável invocou a skill sozinho, leu o `MEMORY.md` antes do board e apresentou na
ordem que a skill manda; `git status` do worktree ficou vazio. Por que vale mais que um teste meu:
`T-014`/`T-016` avisam que o Manager acerta de memória porque a frase do teste está escrita no
próprio card — o Kimi não carregava essa expectativa.

**Efeito colateral revelador:** o Kimi leu o `MEMORY.md` e me devolveu "falta release e push" e
"instalar no Kimi — nunca foi feito", as duas já falsas naquele instante. Índice desatualizado não é
cosmético: ele **mente para quem retoma**, e hoje isso foi observado ao vivo em vez de suposto.

**Painel dos três sobre o diff da própria 0.19.0: REPROVADO por 3/3.** Opus interno, Codex
`gpt-5.6-sol@xhigh` e Kimi K3, independentes. Verifiquei 8 dos 10 achados no código antes de aceitar.
Convergência dos três: **procedência inflada** — a família de defeito que a 0.19.0 dizia ter
eliminado. O mais grave (2 revisores + minha verificação): o template do `_elenco.md` em
`orq/commands/elenco.md` não ganhou as seções v2, então `/orq:init` em projeto novo nasce sem a
`## Matriz de invocação` que `revisar.md:56` e `SKILL.md:85` mandam consultar.

**O achado que responde ao critério do próprio card:** o `T-026` mandava conferir que "no Codex o
painel fecha três vendors, não dois". Pelo texto atual **não fecha** — o `revisar.md` não tem passo
que invoque o revisor Anthropic pelo time do host, e a linha 63 dispara `codex exec` sempre que
`codex` estiver no PATH, o que no host Codex é sempre. Resultado: OpenAI duplicado, zero Anthropic.

**Ironia útil:** o `instalar.md:120-121` manda rodar a fumaça do Kimi sem `-m` e com `-p` primeiro —
as duas formas que a 0.19.0 acabou de declarar inseguras. Só não mordeu porque segui a Matriz, e não
o `instalar.md`; seguindo o arquivo, a instalação teria sido validada rodando o `default_model` de
terceiro.

**Validados por mim, mecanicamente e sem viés:** `T-017` (o lint acusou a edição sem bump nomeando o
arquivo; `diff -rq` pós-release vazio) · `T-007` e `T-010` (os três pareceres voltaram no formato
exigido, e a reconciliação separou confirmado-por-3, por-2 e solitário).

**Nada foi corrigido em `orq/`** — review é read-only e todo achado ali é mudança de produto, que
entra pelo ciclo. Nasceram `T-033`, `T-034` e `T-035`.

## [2026-08-05] feat | 0.19.0 — elenco host-agnostico; e o framework rodou no Codex de verdade

**O dia entregou duas coisas: a prova de que o Orquestra atravessa para outro host, e o elenco
sabendo disso.**

### O que foi provado, nao deduzido

O Codex, com o plugin instalado, passou nos **quatro** testes comportamentais: invocou a skill
sozinho por frase natural · achou e leu os `commands/` · roteou um pedido pelo ciclo e **parou no
gate** sem tocar no produto · e, mandado revisar, **declarou a degradacao** (*"este host nao oferece
override de modelo no subagente nativo"*) em vez de fingir painel — a regra da 0.18.0 indo a campo.

Fez ainda duas coisas que ninguem pediu: **cruzou o board com o `git log`** e flagrou que o
checkpoint anterior dizia "nao commitada" depois do commit; e **detectou uma edicao do Manager em
`gotchas.md` que nao era dele, excluindo-a do escopo sem sobrescrever** — o `T-013` validado entre
hosts diferentes, que era so teoria ate aqui.

### A regra do dono que simplificou o desenho

Verbatim: *"manager, planner e implementer sempre no modelo principal do host; a ideia de usar outras
LLMs e principalmente no revisor"*. Isso **dissolveu** o impasse tecnico do implementer — nenhuma
invocacao cross-vendor de **escrita** existe no desenho, so de leitura, que e o unico caminho
comprovado. O `acceptEdits` liberar Write e negar Bash deixou de importar.

### O que a implementacao ensinou sobre invocacao cross-vendor

- `claude -p` de dentro de outro agente **nao le arquivos**: trava com tools; sem tools, o Opus
  **recusa revisar** em vez de inventar `arquivo:linha` — comportamento correto.
- **Isolamento e leitura autonoma sao incompativeis**: revisor em diretorio descartavel nao enxerga
  o repo. Worktree com o patch aplicado resolve; diretorio vazio, nao.
- **A ordem das flags nao e generalizavel** e derrubou o painel **duas vezes no mesmo dia**, por
  causas opostas: o `-p` do kimi **aceita valor**; a `--tools` do claude e **variadica**.

### O padrao de metodo que se repetiu — e e o achado mais caro do dia

**Tres dos oito achados do painel eram REINCIDENCIA** da mesma familia (regra em dois lugares, um
falso), incluindo uma **generalizacao errada do proprio Manager**, escrita num gotcha e propagada
dai para o produto.

E a **setima ocorrencia** so apareceu na **releitura manual**, depois de gates verdes e do painel de
tres aprovar a rodada: a correcao tinha **ACRESCENTADO** a regra certa sem apagar a promessa falsa
ao lado, deixando duas frases vizinhas se contradizendo.

**Duas releases seguidas, o ultimo filtro que pegou o defeito foi humano, nao mecanico** (na 0.17.0
foi a quinta reincidencia, tambem so na releitura). Registrado em `gotchas.md`: corrigir afirmacao
falsa e **reescrever a afirmacao**, nunca escrever a verdade ao lado dela.

### Um criterio do Manager que o implementer recusou, com razao

O Manager exigiu `grep "-p -m"` **zero na arvore inteira**. O implementer mostrou que o `gotchas.md`
**precisa** citar a forma quebrada para ensinar qual e — o criterio, cumprido ao pe da letra,
**apagaria a licao**. E a distincao log x pagina de topico do `CLAUDE.md`, e ele estava certo em nao
obedecer.


## [2026-08-04] feat | 0.17.0 e 0.18.0 — regra duplicada vira lugar unico; Orquestra instalavel em Codex e Kimi

**0.17.0 (card `T-030`) — correcao dos 11 achados do painel sobre as releases 0.14.0–0.16.0.**
Principio: cada regra tem **um lugar normativo** e se condiciona a **propriedade real**, nunca a um
proxy (nome de perfil, argumento de comando). Tres painels, nove pareceres, convergencia
5 bloqueadores graves -> 2 -> 0. Commitada (`10ecef2`) e no GitHub. **O dono ainda nao rodou o
release na maquina** — os cards `T-020`, `T-023`, `T-025` e `T-030` seguem esperando o teste dele.

**0.18.0 (card `T-026`) — instalacao multi-host.** `AGENTS.md` = `CLAUDE.md` byte-identicos (decisao
do dono: **nao** e ponteiro), com `diff` no lint como gate mecanico; comando novo `/orq:instalar`;
`/orq:init` gravando nos dois. **NAO commitada** — esperando o ok do dono.

### Por que o dono reabriu o `T-026`, e o que a reabertura corrigiu

Motivo dele, verbatim: *"alternar as assinaturas que eu tenho… a depender de qual LLM esteja melhor
naquele momento"* — **nao e rodizio de custo, e liberdade de escolher o motor**. Cadencia: por
**ciclo de mercado** (lancamento de modelo novo), nao por semana.

A investigacao de 30/jul estava **errada em dois pontos**, e as versoes dos CLIs nao mudaram desde
la — **o que mudou foi a qualidade da investigacao**: o Codex TEM subagente (`spawn_agent`, modelo
por filho) e TEM statusline; o Kimi carrega o formato Claude Code inteiro, e o **roteamento por
intencao foi provado vivo** (`kimi -p "onde paramos?"` invocou a skill sozinho).

### A intervencao do dono que encurtou o card

O Manager desenhou um "portatil" como **copia adaptada** da `SKILL.md`, e dai nasceu toda a
complexidade (sincronizar, apodrecer, gerar no release). O dono cortou: *"Nao entendi toda essa
complexidade… isso era para funcionar em qualquer LLM, apenas adaptado aos motores de cada uma."*
**Ele estava certo: o problema era do plano, nao do dominio.** A licao: quando a solucao fica
complexa, verifique se o problema foi inventado por uma premissa sua.

Depois ele decidiu contra a proposta de ponteiro — `AGENTS.md` com o **mesmo conteudo**. Como sao
identicos por definicao, a divergencia virou verificavel por `diff`: **gate mecanico no lugar de
"dever de sincronizar"**, que e o defeito que custou cinco rodadas nesta mesma semana.

### O achado que decide se o framework realmente atravessa

Copiar arquivos **nao** entrega o framework: os comandos exigem **primitivas** (spawn de subagente
com override de modelo, worktree, `AskUserQuestion`, `/clear`). Sem tratamento, no Kimi o modelo
planejaria na propria janela e depois "devolveria ao Planner" **revisando a si mesmo** — o
isolamento de contexto e o handoff sumiriam **em silencio**. A `SKILL.md` ganhou a regra: **sem a
primitiva, nunca finja** — declare a degradacao; onde houver equivalente, invoque o papel como
**subprocesso CLI** (o mesmo padrao que o `/orq:revisar` ja pratica ha semanas).


> Cronológico e **imutável**: cada entrada registra o que aconteceu naquele dia e por quê.
> Nunca reescrever entrada antiga. "Como funciona hoje" mora nas páginas de `wiki/`.

Formato: `## [AAAA-MM-DD] tipo | título`

---

## [2026-07-26] fix | namespace `/orquestra:*` → `/orq:*` em 6 arquivos

**Sintoma:** o plugin foi renomeado de `orquestra` para `orq` na v0.2.0, mas 9 referências internas a
`/orquestra:*` e 3 a "leia a skill `orquestra`" sobreviveram — em `SKILL.md`, `plan-next`,
`implement-next`, `init`, `quadro` e `orq-scout`.

**Impacto real (não era cosmético):** o `plan-next` terminava mandando o dono rodar
`/orquestra:implement-next`, que não existe; o `implement-next` mandava voltar pro
`/orquestra:plan-next`; três comandos mandavam ler uma skill de nome inexistente.

**Causa raiz:** a renomeação da v0.2.0 tratou o nome do pacote, não as auto-referências no corpo dos
prompts. Nenhuma verificação cobre isso — `claude plugin validate --strict` valida o manifesto, não a
coerência das instruções entre si.

**Consequência:** virou o card 🔴 `T-008` (lint de coerência interna). Um `grep` de dez linhas teria
pego o defeito em 2026-05; ele sobreviveu a três releases.

**Preservado de propósito:** o marcador HTML `<!-- orquestra:start -->` no `init.md:84` — é delimitador
de bloco no `CLAUDE.md` do projeto-alvo, não um comando.

---

## [2026-07-26] chore | instalação do Orquestra neste próprio repo (dogfooding)

Até hoje o plugin que prega *"o estado do trabalho vive no board"* era desenvolvido **sem board** — o
roadmap morava em prosa no README. Instalados: `memory/` completo, board com o roadmap convertido em
8 cards, elenco, duas páginas de tópico, `CLAUDE.md` e `AGENTS.md`.

**Decisões da instalação:**
- **Time núcleo puro**, reaproveitando os agentes do próprio plugin — nada em `.claude/agents/`.
  Cogitado um 6º papel de "crítico de prompt" (o produto aqui são instruções, não código) e
  **recusado**: a parte determinística vira lint (T-008) e o resto é briefing do reviewer.
- **Sem indexação semântica.** 24 arquivos de markdown: `grep` resolve. Registrado como decidido
  para não ser reproposto.
- **Statusline não tocada** — o dono já tem uma customizada em `~/.claude/statusline.sh`.

---

## [2026-07-26] feat | stack complementar auto-detectada (0.5.0)

**Motivação do dono:** a experiência dele com o Orquestra depende de uma stack de memória e contexto
que ele já tinha montada — e que não estava documentada em lugar nenhum. Quem instalasse o plugin
puro teria performance pior sem saber por quê. Pedido explícito: *"que uma IA leia esse repositório,
veja o que é necessário e instale tudo, mesmo que não esteja diretamente no repositório"*.

**Entregue:** `orq/stack.md` (catálogo canônico, escrito para ser lido por IA — detecção, comando
exato, custo honesto) · comando `/orq:stack` · integração nas FASES 1/2/3/4 do `init` · gatilho
natural na skill · seção no README · `memory/wiki/_stack.md` com o levantamento real desta máquina.

**Decisões:**
- **Consentimento é a espinha do desenho**, não um detalhe: nada instala sem "pode instalar", nada
  que exija chave sem o dono fornecer, e recusa registrada é **permanente** até ele reabrir.
- **`_stack.md` com seção "Dispensadas"** existe porque sem ela a mesma proposta volta toda sessão —
  o tipo de ruído que faz o dono desligar a feature.
- **Comandos levantados da máquina real**, não inventados: marketplaces, MCPs e PATH.
- **Sem comando de instalação para `codebase-memory-mcp`.** É binário local sem origem rastreável;
  recomendar um comando adivinhado a terceiros seria pior que omitir.

**Correção do dono, na mesma sessão:** tirar os comandos de instalação do catálogo e apontar só o
repositório oficial + a importância da ferramenta. **O argumento dele é melhor que o desenho
original:** comando envelhece, repositório não — e some a assimetria de ter deixado uma ferramenta
sem comando. A IA passa a ler as instruções atuais no upstream na hora de instalar. Isso também
resolveu a pendência de procedência: o `codebase-memory-mcp` é `DeusData/codebase-memory-mcp`
(binário estático único, bate com o Mach-O de 255 MB local). Todas as 7 fontes confirmadas.

**Autocrítica antes de entregar — três brechas próprias, corrigidas:**
- `/orq:stack` passo 4 dizia "mostre o comando antes de rodar" sem definir se aquilo era um segundo
  gate. Um modelo podia mostrar e executar na mesma resposta, ou travar pedindo aprovação de novo.
  Agora está explícito: o "pode instalar" cobre a ferramenta; **voltar a perguntar só** se as
  instruções exigirem `sudo`, mexer em PATH, `curl | sh` ou dependência de sistema.
- `init.md` FASE 3: o "pode ir" genérico da instalação podia ser lido como aprovação da stack junto.
  Agora são **duas decisões separadas** — instalar arquivos no projeto é reversível, instalar
  software na máquina não é.
- `/orq:stack` passo 2 não dizia o que fazer sem `_stack.md` (comando rodando antes do `init`).

**O painel de revisores falhou por inteiro — os dois revisores.** O Codex não entregou (ver
`gotchas.md`). O `orq-reviewer` foi spawnado, respondeu três notificações de *idle* e **nunca produziu
parecer**, nem após dois pedidos de entrega parcial. Parei na terceira, em vez de insistir.

**Consequência honesta:** nenhum achado desta mudança veio de revisão independente. Todos vieram de
autocrítica do Manager. Duas contradições só apareceram na segunda passada, o que mostra o limite do
método — quem escreveu o texto é o pior leitor dele:
- `commands/stack.md:15` mandava usar a *"coluna Detectar"* do catálogo, que a reescrita eliminou (a
  detecção virou linha inline). Instrução apontando para estrutura inexistente.
- `stack.md` regra 3 dizia que a **camada 4 não se paga em projeto pequeno** — errado e contraditório
  com a própria seção da camada 4 e com os Perfis. Revisor externo se decide por **criticidade**, não
  por tamanho: script pequeno que mexe com dinheiro merece painel.

O `T-009` segue em VALIDATE, e agora a validação prática do dono é o único filtro real que restou.

---

## [2026-07-28] feat | problemas conhecidos documentados e diagnosticáveis (T-015, 0.10.0)

**Pedido do dono:** *"acrescentar essas possibilidades para quem instalar já conseguir funcionar sem
grandes problemas, com esses possíveis bugs já documentados"*. Os atritos que custaram tempo aqui vão
custar tempo de quem instalar — em vez de cada um redescobrir, viram documentação **e** verificação.

**README ganhou "Problemas conhecidos"** com sete itens, e o que amarra a seção é o padrão comum:
**a falha é silenciosa** — nada dá erro, a coisa só não acontece. Plugin desatualizado · escopo
`project` vs `user` · revisor fora do PATH · trava por falta de `< /dev/null` · statusline muda por
card fora do formato · implementar sem planejar · concluir ausência de `--help | head`.

**Mais importante que documentar:** `/orq:stack --verificar` virou **diagnóstico de ambiente**. Seis
checagens com sintoma e comando de correção. Doc que ninguém lê vira comando que roda — e ganhou
gatilho natural (*"não está funcionando"*, *"o revisor sumiu"*, *"não conecta"*).

**A regra de método que ficou escrita:** nunca concluir "ausente" a partir de verificação de fonte
única. Me pegou **duas vezes em dois dias** — `claude plugin --help | head` cortando lista alfabética,
e `which kimi` respondendo sobre o PATH da sessão em vez do disco. Nos dois casos a conclusão errada
ia levar a ação real (escrever instrução falsa; instalar pacote desnecessário).

---

## [2026-07-28] fix | "Kimi não instalado" era falso — PATH, não ausência (0.9.1)

**Sintoma:** outra sessão reportou `Codex ✅ · Kimi ❌`, concluiu "o binário não existe nesta máquina"
e — corretamente, dado o diagnóstico — **recusou instalar** por risco de cadeia de suprimento, já que
os pacotes `kimi` no npm são homônimos sem relação.

**O diagnóstico estava errado.** O binário existe (`~/.kimi-code/bin/kimi`, 160 MB, instalado às
13:33 do mesmo dia) e **funciona**: rodei e respondeu. A causa é que o instalador adiciona o
diretório ao `.zshrc`, o que **não alcança sessão já aberta** — o PATH foi capturado antes.
`which kimi` falha enquanto o binário está lá, operante.

**A recusa por supply chain era certa em tese e desnecessária no fato.** O `kimi-install.log` mostra
download de `https://code.kimi.com/kimi-code/binaries/0.29.2/` **com verificação de checksum** —
domínio oficial da Moonshot. O Kimi Code **não é distribuído por npm**, então procurar lá só podia
achar homônimo. Registrado no `stack.md` para ninguém repetir a busca.

**Correção:** symlink `~/.local/bin/kimi` → `~/.kimi-code/bin/kimi` (o diretório já está no PATH), o
que conserta **todos** os consumidores de uma vez — o agente global `kimi-revisor` voltou a funcionar
sem edição. E o Orquestra passou a resolver o binário com fallback
(`command -v kimi || $HOME/.kimi-code/bin/kimi`), para não depender do symlink em outra máquina.

**A lição repete a de ontem** (`claude plugin --help | head`): **ausência não se conclui de uma
verificação que só olha um lugar.** `which` responde sobre o PATH daquela sessão, não sobre o disco.

---

## [2026-07-28] fix | a interface natural não funcionava — 0% de cobertura (0.9.0)

**Observação do dono:** *"a ideia do projeto é que isso seja automático… não é pra eu ficar digitando
comando"*. Ele estava certo, e a prova é esta sessão inteira.

**Medi.** Peguei 10 frases que ele realmente usou e testei contra os 25 gatilhos declarados na
`description` da skill: **0 de 10**. Nenhuma casou. Consequência prática: **a skill `orq` não foi
invocada uma única vez** nesta sessão, os Loops A e B nunca rodaram, e tudo — inclusive a feature do
Kimi, que é uma feature inteira — foi implementado direto, sem plano, sem gate, com o painel entrando
só depois, revisando o que já estava pronto.

**Causa raiz:** os gatilhos foram escritos imaginando como o dono falaria (*"vamos planejar isso"*,
*"pode implementar"*), não observando como ele fala (*"queria acrescentar"*, *"siga com suas
recomendações"*, *"vale a pena configurar"*). E faltava o padrão mais comum de todos: **o pedido de
mudança**, que é a maioria do que ele diz e não estava coberto por nenhum gatilho.

**Duas correções, e a segunda é a que importa:**
1. `description` reescrita a partir da fala real. Cobertura medida: **0% → 100%** nas mesmas frases.
2. **Seção "ROTEAMENTO AUTOMÁTICO" no topo da skill** — porque cobertura de gatilho só faz a skill
   carregar; não diz o que fazer. Agora diz: *todo pedido de mudança entra pelo ciclo, não comece
   editando arquivo*, com **escala por risco** (trivial → direto · pequeno → revisor interno ·
   normal → ciclo completo · alto risco → gate extra) e a regra **"na dúvida, suba um nível"**.

**A instrução que faltava, em uma frase:** *anuncie o roteamento, não pergunte*. Nada de "quer que eu
rode o `/orq:plan-next`?" — o dono não precisa saber que o comando existe. Uma linha dizendo o que
vai acontecer e qual elenco toca cada papel.

**O erro nomeado no `CLAUDE.md` do projeto** para não se repetir: a feature do Kimi (0.8.0) foi
implementada direto porque o pedido chegou em linguagem natural e pareceu pequeno. É o modo de falha
típico — não é preguiça, é o pedido não se parecer com um comando.

---

## [2026-07-28] feat | Kimi como terceiro revisor do painel (T-007, 0.8.0)

**Pedido do dono**, com um prompt vindo de outra sessão que propunha comandos globais
(`kimi-review`, `kimi-adversarial`, `dupla-revisao` em `~/.claude/commands/`). **Recusado com
argumento e ele concordou:** isso criaria um segundo sistema de revisão paralelo ao `/orq:revisar`,
que já tem reconciliação — mais forte que a "tabela comparativa" proposta. O Kimi entrou **dentro do
Orquestra**, fechando o `T-007`.

**Auditoria (Fase 1) revelou dois bugs silenciosos:**
1. O `kimi` **não está no PATH** (fica em `~/.kimi-code/bin/`). O agente global `kimi-revisor`
   chamava `kimi` solto e, como ele mesmo manda "se não existir, pare", **nunca revisou nada** —
   parecia obediência à regra, era falha muda.
2. O plugin do Codex **não é invocável pelo modelo**: `codex:codex-rescue` não aparece como agent
   type e `/codex:review` tem `disable-model-invocation: true`. A regra global do dono ("use sempre
   o subagente, nunca o binário") **só é executável quando ele digita o comando** — de dentro de um
   turno, a CLI é o único caminho. Testado: o spawn falha com "Agent type not found".

**Do prompt do dono, adotados:** o **formato único** (`BLOQUEADORES / RISCOS / VEREDITO`), que o
Orquestra não tinha e sem o qual a comparação entre pareceres é frouxa; e a **regra LGPD** — nenhum
dado de paciente, PII ou credencial vai para revisor externo, com instrução de **parar e avisar** em
vez de higienizar sozinho.

**O painel provou o valor na mesma sessão.** Codex e Kimi revisaram o `lint-coerencia.py` e acharam
coisas **diferentes**: o Codex, três bloqueadores estruturais (regex aceitando `/orq:revisar2` como
válido, agente só verificado entre crases, caminho não confinado ao plugin); o Kimi, o
`read_text()` sem `encoding="utf-8"` — que **quebraria o lint em CI com locale C**, e a doc é toda
em pt-BR com acento. Nenhum dos dois viu o achado do outro.

**E o painel ensinou a não aplicar achado cru.** O Kimi apontou (corretamente) que skill exigia
crases e agente não. Apliquei a correção → **três falsos positivos na hora**, porque "skill" é
palavra comum em prosa portuguesa ("a skill **e** o comando"). A assimetria era proposital; o
revisor não tinha como saber. **Diagnóstico certo, correção errada** — revertido com o motivo no
código. Falso positivo é o que faz lint ser desligado.

**Bônus embaraçoso:** ao aplicar a correção de contenção de caminho, criei `raiz = plugin.resolve()`
dentro do loop e **sombrei a variável `raiz` externa**, quebrando o lint inteiro. Só apareceu porque
rodei o teste. Nenhum revisor pegaria — não existia quando eles revisaram.

---

## [2026-07-27] fix | a CLI `claude plugin` TEM install/update — afirmação falsa corrigida (0.7.1)

**Erro meu, de método.** Rodei `claude plugin --help | head -20`, vi a lista alfabética terminar em
`help` e concluí que a CLI **não tinha** `install` nem `marketplace add`. Escrevi isso como fato no
`/orq:stack` e no `init`, mandando "entregar o comando pro dono colar". A lista continuava logo
abaixo do corte: `install`, `list`, `marketplace`, `prune`, `tag`, `uninstall`, `update`, `validate`.

**Agravante:** essa conclusão nasceu de um achado do painel (o revisor tinha razão sobre o
`/plugin` ser comando interno do cliente), e eu "confirmei" com uma verificação truncada. Achado
correto + verificação ruim = instrução errada com aparência de bem apurada.
→ **Nunca concluir ausência a partir de saída passada por `head`.** Ausência se verifica no comando
específico: `claude plugin update --help`.

**Descoberta maior no mesmo caminho:** o marketplace aponta para o **diretório** deste repo, o que dá
a impressão de que editar já vale. **Não vale** — o plugin em uso é uma **cópia em cache**. A máquina
do dono estava rodando a **0.4.0 em todos os outros projetos** enquanto o repo já estava na 0.7.0:
sete releases de diferença, sem sinal nenhum. Todo teste comportamental feito sem `marketplace
update` + `plugin update` + restart estava testando a versão errada. Documentado em
`wiki/distribuicao.md` e em `gotchas.md`.

---

## [2026-07-27] feat | protocolo de várias janelas (T-013, 0.7.0)

**Pergunta do dono:** ele trabalha com N janelas Claude abertas no mesmo projeto, uma por frente —
está resolvendo A, lembra de B, abre janela pra B sem largar A. Como o checkpoint não se sobrescreve?

**Não se sobrescrevia: perdia mesmo, em silêncio.** O modelo pressupõe **um** Manager. Com N janelas:
`KANBAN.md` e páginas de tópico são reescritas (last-write-wins → movimento de card some), o log é
append por ler-modificar-escrever (duas janelas simultâneas perdem uma entrada), e nada registra quem
escreveu. Mesma classe do bug do parser: **falha sem sinal**.

**O diagnóstico que mudou a solução:** a concorrência não é o problema — **a reescrita é**. Duas
janelas alterando *linhas diferentes*, cada uma relendo antes, praticamente não colidem. O que apaga
trabalho é reescrever o arquivo inteiro a partir de uma cópia velha do começo da sessão.

**Protocolo (uma janela = uma frente):**
1. releia antes de escrever — sempre, mesmo com o arquivo no contexto;
2. edite só as **linhas dos seus cards**, nunca o board inteiro;
3. card em curso leva `@frente` no fim da nota (depois do travessão, então não afeta o parser);
4. trabalho em curso mora em `threads/<frente>.md` — dono único, livre de conflito por construção.
   Isso reduz o problema de 5 arquivos disputados para **1**: o board.

**O ganho maior não é a trava.** O dono mantinha janela aberta *como memória de pendência* — "não
consigo decidir agora, então deixo a janela viva". Isso é contexto fazendo o papel do board. Agora o
`checkpoint` termina dizendo que **é seguro fechar a janela** quando a pendência virou card `[!]` com
a pergunta exata + "RETOMAR AQUI" na thread. E a instrução é explícita: **se você não consegue
afirmar isso com confiança, o handoff está fraco — melhore antes de fechar.**

**Recusado:** lock global (mata o paralelismo que motiva as N janelas) e merge por git (markdown de
prosa conflita mal, e ele não commita a cada checkpoint).

**Escrito em quatro lugares** porque cada um é lido num momento diferente: `_schema.md` (o contrato),
`checkpoint.md` (passo 2b, na hora de gravar), `SKILL.md` (a disciplina + gatilho natural para "vou
abrir outra janela") e o template que o `init` gera nos projetos novos.

---

## [2026-07-27] fix | painel REPROVOU a 0.6.0 — parser do board endurecido (0.6.1)

**Primeiro painel completo do projeto** (Claude + Codex, os dois entregando). Deu 10 achados e uma
**divergência de veredito**: Claude disse "aprovar com correções", Codex disse **REPROVAR**.
Desempatei com o Codex — o próximo `/orq:init` em projeto de terceiro repetiria a falha silenciosa.

**Confirmado pelos dois (a lição que interessa):** a 0.6.0 **documentou o contrato e esqueceu de
endurecer o parser**. Escrever a spec não impede o consumidor de aceitar lixo. Cenários provados
pelo revisor Claude rodando o script contra boards sintéticos:
- seção "Processo" com `- [x] revisor aprovou` (estrutura que o próprio CLAUDE.md global descreve)
  contava como card feito: board de 3 cards virava `📋 20% (1/5)`;
- `## 📦 Arquivo` em vez de `Arquivado` (variante natural em PT) fazia arquivados voltarem à conta;
- card sem crases no ID vazava o marcador cru para dentro da statusline.

E o mais importante: **o smoke test da 0.6.0 aprovava os quatro casos**, porque só reprovava saída
vazia.

**Correção:** o `kanban-status.sh` passou a casar `` /^- \[[ >!~?x]\] `[^`]+`/ `` — estrito. Linha
que *parece* card e não casa vira `⚠N` na saída. **A falha deixou de ser silenciosa**, que era o
defeito de fundo. O smoke test agora exige três sinais, e o terceiro é comparar o denominador com a
contagem manual de cards — "saída não-vazia" não prova nada.

**Outros aplicados:** `_stack.md` só nascia quando havia instalação, então quem **recusava** tudo
ficava sem a seção "Dispensadas" — justamente o caso em que repropor mais irrita · a pergunta 2 do
gate soldava "instalar software" com "quais revisores", e quem já tinha `codex` e recusava a stack
perdia o painel que já possuía (pior: sem `_elenco.md` o Codex é ativo por padrão, então **ter** o
arquivo deixava o dono pior do que não ter) · o `init` permitia índice fora de `memory/`, mas
`orq-planner` e `wiki-lint` exigem `memory/MEMORY.md` no caminho fixo — resolvido com ponteiro ·
`[~]` significava "implementando" no schema e READY/DEV_REVIEW na skill · `--reinstalar` não
detectava `.claude/agents/orq-*.md` legado.

**Autocrítica registrada:** o `MEMORY.md` deste repo ficou dizendo "versão 0.5.0" e "nunca rodou de
ponta a ponta" enquanto três cards já estavam em VALIDATE. O `checkpoint.md:36` manda atualizar o
índice — **o produto não seguiu a própria disciplina**, e quem retomasse pela regra "leia o
MEMORY.md primeiro" reimplementaria o lint.

---

## [2026-07-27] fix | 10 atritos do primeiro `/orq:init` em projeto de terceiro (T-011, 0.6.0)

**Origem:** outra LLM instalou o Orquestra num repositório real, sem ninguém do projeto por perto, e
devolveu relatório. É o `T-003` cumprido — e melhor do que o card pedia, porque foi em território que
ninguém aqui conhecia.

**4 bugs de contrato, todos confirmados no código:**

1. **Board fora do formato deixa a statusline muda, sem erro.** O `/orq:init` mandava "criar o
   KANBAN.md com o backlog real" e deixava o formato por conta do modelo; o `kanban-status.sh` casa
   `/^- \[.\]/` e lê por posição. A LLM escreveu o marcador dentro de crases, a saída veio vazia, e
   ela **só descobriu porque testou por conta própria**. **Causa raiz: produtor e consumidor não
   compartilhavam especificação.**
2. **`checkpoint.md:11` e `wiki-lint.md:6` liam `memory/wiki/_schema.md`, que o `init` nunca criava.**
   Todo checkpoint batia em arquivo ausente.
3. **Nenhuma regra sobre colisão de nome de agente.** O `init` mandava criar agentes em
   `.claude/agents/` e "não duplicar os que já existem" — mas os que já existem são os cinco `orq-*`
   do próprio plugin. A LLM criou com os mesmos nomes apostando que projeto vence plugin, sem poder
   validar. Resolução é indefinida.
4. **A FASE 5 mandava mostrar, não verificar.** Nada conferia se o board era legível, se o
   `CLAUDE.md` sobreviveu, se os agentes carregam.

**Correção estrutural — o `_schema.md` virou o contrato compartilhado.** Em vez de repetir o formato
em cada lugar, o `init` agora **cria** o arquivo, e `checkpoint` e `wiki-lint` **leem** dele. A FASE 5
ganhou smoke test: `kanban-status.sh` com **saída vazia é falha**, e o comando tem que corrigir antes
de declarar sucesso.

**6 lacunas de especificação, também aplicadas:** índice pré-existente em outro caminho (o projeto
tinha `MEMORY.md` na raiz — seguir ao pé da letra criaria dois índices concorrentes, exatamente o que
a wiki existe pra evitar) · custo da FASE 1 quando já se conhece o projeto (a LLM gastou 3 scouts num
repo que tinha acabado de ler; agora o comando manda usar o que já sabe e só cobrir lacunas — "num
projeto pequeno que você acabou de ler, o número certo de scouts é zero") · idempotência falava de
arquivos mas não de trabalho já feito na sessão · `--reinstalar` citado nas Regras e nunca
especificado · as decisões do gate espalhadas por três lugares, agora consolidadas num
`AskUserQuestion` de duas perguntas.

**Não é bug do plugin:** o cache com `orquestra/orquestra/0.1.0` ao lado de `orquestra/orq/0.x` é
resíduo da renomeação da 0.2.0 — todos os plugins da máquina guardam várias versões em cache.

**O que o piloto confirmou que está certo (não mexer):** a frase *"este comando se ADAPTA ao
projeto"* logo no topo — segundo o relatório, sem ela teriam nascido 6 agentes genéricos e uma wiki
de placeholders · *"menos agentes bem definidos > muitos genéricos"* · a separação entre aprovar o
Orquestra e aprovar a stack · o `_stack.md` com "Dispensadas", chamado de "melhor ideia do plugin
inteiro" · a distinção log-append × página-reescrita · scouts com escopo fechado, um dos quais
corrigiu uma premissa errada de quem os despachou.

---

## [2026-07-26] feat | lint de coerência interna (T-008)

`orq/scripts/lint-coerencia.py`. Confere que todo `/orq:x`, `` `orq-agente` ``, `` skill `nome` `` e
`${CLAUDE_PLUGIN_ROOT}/arquivo` citado **existe**. Sai com 1 e lista `arquivo:linha`.

**Por que existe:** `claude plugin validate --strict` valida o manifesto e passa com instruções que
mandam rodar comando inexistente. Foi assim que `/orquestra:*` sobreviveu a três releases.

**Ignora `memory/` de propósito** — requisito que só apareceu ao rodar o protótipo: o log é
append-only e o `gotchas.md` citam nomes extintos ao descrever bugs passados (hoje são 6 ocorrências).
Sem a exclusão, o lint acusaria falso positivo em todo checkpoint — e lint que grita à toa é lint
desligado.

**Testado nos dois sentidos**, que é o que separa lint de teatro: passa no estado atual (18 nomes) e
pega os 4 tipos de defeito quando injetados de propósito.

**Virou verificação obrigatória** no `CLAUDE.md`, ao lado do `validate`. O que nenhum dos dois cobre —
contradição semântica entre arquivos — é trabalho do painel de revisores.

---

## [2026-07-26] fix | painel de revisores consertado (T-010) + 8 achados aplicados no T-009

**Duas causas raiz, ambas achadas por experimento, ambas contra a hipótese inicial:**

1. **`codex exec` bloqueia lendo stdin quando não há TTY.** Imprime
   `Reading additional input from stdin...` e trava até o timeout — **mesmo com o prompt passado como
   argumento**. `< /dev/null` resolve: respondeu em 17 s. A hipótese anterior ("o ambiente do Codex
   injeta 2.155 linhas no lugar do briefing") estava **errada** — o que se via era a sessão pendurada.
2. **Subagente spawnado com `name` nunca devolve resultado.** Com
   `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, o `name` transforma o agente em teammate endereçável:
   emite `idle_notification` e fica vivo esperando mensagem. O **mesmo** agente, mesmo prompt, **sem
   nome**, entregou parecer completo em 231 s.

**Consequência no produto:** o `/orq:revisar` usava o plugin `codex:codex-rescue` com um forwarder e
poll de bash-id. Foi trocado pela CLI direta (`codex exec … < /dev/null`), que é mais simples e agora
comprovadamente funciona. E ganhou a proibição explícita de `name` no spawn do revisor.

**O painel funcionou e pagou o investimento.** O parecer trouxe 8 achados; o mais grave eu não teria
encontrado sozinho: **3 das 7 ferramentas do catálogo se instalam por slash command** (`/plugin
marketplace add`), que o modelo **não consegue invocar** — e a CLI `claude plugin` não tem `install`
nem `marketplace add` (confirmei: só `details`, `enable`, `disable`, `eval`). Sem instrução explícita,
o caminho natural do modelo seria improvisar `git clone` para dentro de `~/.claude/plugins/` ou editar
`installed_plugins.json` na mão — mutação da máquina do dono por fora de todo gate. Agora o passo 4 do
`/orq:stack` manda **entregar o comando pra ele colar** e proíbe o equivalente improvisado.

**Outros aplicados:** `SKILL.md:163` ainda prometia "comando de instalação" (o commit anterior
esqueceu esse arquivo) · catálogo confundia o **plugin** `codex-plugin-cc` com a **CLI** `openai/codex`,
o que faria `/orq:revisar` cair para um revisor achando que tinha dois · detecção de plugin no PATH
sempre falharia (plugin não é binário) · `init` não lia a seção "Dispensadas" antes de propor, então
`--reinstalar` repropunha o recusado · perfis cumulativos arrastavam a camada 3 para quem não precisa ·
`/orq:stack` criava árvore `memory/` em projeto sem Orquestra · `dormir.md` não listava "instalar
ferramenta" entre o proibido à noite.

**Veredito sobre a dúvida do dono (Serena é redundante com codebase-memory?):** não, mas se
sobrepõem em ~20% — os dois acham símbolo por nome. Serena é LSP + **edição**; codebase-memory é
grafo de **relações**. No Orquestra a sinergia é por papel: planner/reviewer ↔ grafo, implementer ↔
LSP. Escolhendo um só: gargalo em *entender* → codebase-memory; em *editar* → Serena. Menos de ~50
arquivos → nenhum dos dois.

## [2026-07-29] feat+fix | 0.11.0 — o ciclo completo rodou e reprovou a 0.10.0

**O que motivou:** validar os cards empilhados em VALIDATE. O painel de três revisores foi rodado
sobre o commit da 0.10.0 (`40dbc59`) e **os três reprovaram**.

**Por que a 0.10.0 falhou:** ela prometia "atritos de ambiente diagnosticáveis" e o diagnóstico
errava no primeiro item. A checagem de "plugin desatualizado" comparava **versão**, mas o cache é
indexado por versão — então versão igual não prova conteúdo igual. Estava dando all-clear com o cache
divergente de verdade: o `5b75296` mudou o `lint-coerencia.py` sem bump e o cache ficou parado.

**O ciclo, na ordem em que aconteceu** (primeira vez completo):
Fable planejou 16 passos → Codex e Kimi revisaram **o plano** (os dois estouraram timeout; os
parciais renderam 3 achados reais) → dono aprovou 6 decisões → Sonnet implementou → painel revisou
o diff → 7 achados voltaram como correção.

**Achados do painel que viraram correção:**
- falso positivo da regex do board em **prosa real do repo** (linha copiada de `arquitetura.md:47`
  acendia `⚠` num board conforme) — alarme crônico é alarme ignorado, a doença que o contador cura;
- `+ [ ]` e `~~- [ ]~~` (bullet CommonMark e tachado GFM) sumiam da contagem **sem `⚠`**;
- `.orphaned_at` — a CLI escreve no cache (8 no `orq`), e sem ignorá-lo o guarda acusa edição-sem-bump
  falsa ao fazer checkout de tag antiga;
- `init.md` e `checkpoint.md` prometiam "statusline muda **sem erro nenhum**" — falso depois da
  correção do script, **no mesmo commit**;
- `stack.md` atribuía "restart required" ao `install --help`, que não menciona restart (só o `update`).

**Por que a versão vive em quatro lugares e não três:** o `.claude-plugin/marketplace.json` declara
a versão do plugin no catálogo e estava em `0.4.0` — sete releases atrás, sem ninguém notar, porque
o lint só conferia README e MEMORY.md.

**Incidente:** o Kimi rodou `git checkout -- .` numa tarefa **read-only** e destruiu o working tree.
Restaurou sozinho e avisou, mas perdeu os marcadores dos cards (edições por script não ficam no
transcript de onde ele reconstruiu). Efeito colateral: o revisor interno, em paralelo, relatou
"metade das correções não está em disco" — parecia alucinação, era descrição fiel. O Manager atribuiu
a worktree e errou. Virou `T-019` + gotcha.

**Consequência de método:** o `_elenco.md` já exigia worktree descartável para revisor sem sandbox.
A instrução existia, estava correta, e não impediu nada — o argumento do `T-001` (hooks) provado
contra o próprio repo.

**Fechados:** `T-003`, `T-008`, `T-011`, `T-012`. **Nasceram:** `T-019`, `T-020`, `T-021`.

## [2026-07-29] feat | 0.12.0 — o relatório do checkpoint falava com a pessoa errada (T-022)

**O que motivou:** o dono perguntou se *precisava dizer* o que a mensagem final do checkpoint pedia
ao voltar. Não precisava. A frase "na próxima janela: leia `memory/MEMORY.md` → thread X" era escrita
para o **próximo assistente** e entregue **a ele**, que a leu como tarefa.

**Defeito de audiência, e pior que isso — inalcançável:** a próxima janela é contexto novo e **nunca
lê aquela tela**. A frase não chegava nem ao destinatário declarado. Mover a informação para o disco
não é preferência de desenho, é a única coisa que funciona.

**O segundo defeito:** o passo afirmava "seguro dar `/clear`" **sem checagem nenhuma**. Virou gate
executável — três sinais do board, thread terminando em `⏭️ RETOMAR AQUI` — com critério de decisão
explícito: falhou, não afirme.

**O que o review pegou (revisor interno REPROVOU, 3 bloqueadores, todos verificados):**
- A linha `Verificação ✓` era **boilerplate sem slot de evidência**: indistinguível de um checkpoint
  que não rodou nada. Agora carrega os números e tem variante de falha (`Verificação ⚠`).
- O primeiro sinal virou "saída não-vazia", perdendo o qualificador **"havendo cards escritos"** que
  as outras quatro fontes têm. Board legitimamente vazio sai vazio com exit 0 — o gate acusaria
  não-defeito, a mesma classe do achado que reprovou a 0.10.0.
- "Seguro fechar a janela" não verificava nada. **Exibit da própria sessão:** o `T-022` estava em
  `[>]`, e o `/orq:quadro` só mostra `[!]` em "Esperando você" e `[?]` em "Validar" — `[>]` cai em
  "Fazendo". A pendência desapareceria do lugar onde o dono olha, logo depois de o comando garantir
  que fechar era seguro.

**Por que o relatório é curto por desenho:** o dono escolheu manter 3–6 linhas. O ganho vem de
escolher o que entra, não de escrever mais. Três regras sustentam: um bloco = uma linha (agregue
dentro dela) · até ~120 caracteres por linha · condicional sem conteúdo não aparece. O orçamento de
largura provou o valor na estreia — pegou uma linha de 121 caracteres no primeiro relatório real.

**Também:** o passo 3 ganhou bullet **BOARD** — a skill prometia que o checkpoint "grava … board" e
o comando nunca mandava tocar nele, então a linha de board do relatório não teria fonte. E o "antes →
depois" foi abandonado: o número capturado no início do checkpoint já contém o que a sessão moveu, os
dois lados sairiam iguais. O delta verdadeiro é a **lista de movimentos**; o total é só âncora.

## [2026-07-29] fix | 0.13.0 — o relatório curto era ilegível; espaçamento virou requisito (T-022)

**O que motivou:** o dono usou o formato da 0.12.0 e reprovou — *"achei os textos bem embolados…
péssima a leitura do resumo"*.

**A causa era a restrição, não a execução.** Ele havia pedido "3–6 linhas"; o desenho respondeu
comprimindo — "um bloco = uma linha, até 120 caracteres" — e 120 caracteres numa linha só é prosa
corrida. Otimizou-se para **poucas linhas** quando o requisito real era **leitura rápida**. As duas
coisas são diferentes e a primeira destrói a segunda.

**Como foi decidido:** três mockups com os dados reais da própria sessão, comparados lado a lado. Ele
escolheu o mais espaçado — seções com título — revertendo explicitamente a decisão anterior. A primeira
decisão foi tomada no escuro; a segunda com o resultado à vista. **Decidir aparência sem ver a coisa
renderizada é chute**, e o custo aqui foi um release.

**O que substitui o teto de linhas:** teto de **densidade**. Bullet de uma linha, nunca parágrafo.
Precisou de parágrafo? O item não pertence ao relatório — vira card ou já mora na thread.

**O que o review pegou (revisor interno REPROVOU, 4 bloqueadores, 2 que o Manager já tinha achado):**
- A regra guarda-chuva "seção sem conteúdo não aparece" **suprimiria a seção `✅ Verificação`** num
  projeto sem board nem thread — e com ela ia embora a linha "Seguro dar `/clear`", que é a promessa
  central do comando. O dono rodaria o checkpoint num projeto pequeno e não receberia autorização
  nenhuma. Agora `✅ Verificação` é **sempre presente**, com variante explícita para "nada a verificar".
- O placeholder `<e fechar a janela, quando o passo 5 permitir>` estava **dentro do template**, então
  vazaria numeração interna do comando para a tela do dono.
- Duas referências a "**linha** ⏸️" e "**linha** de board" sobreviveram à troca de linhas para seções —
  contradição que o lint não pega, porque ele confere nomes de comando/agente/skill/arquivo, não
  vocabulário de estrutura interna.
- A variante de falha havia perdido o "**o que corrigir**" e a frase substituta: o dono ficaria com
  checkpoint reprovado, sem ação seguinte e sem saber se podia limpar.
- O card `T-022` contradizia a si mesmo — mantinha "continua curto (3–6 linhas)" ao lado do "reprovado".
  Regra da wiki: **corrigir a afirmação vencida**, não empilhar a nova em cima.

**Padrão que se repetiu de novo:** trocar uma estrutura e não varrer as referências a ela. Foi o mesmo
erro da 0.10.0 (doc descrevendo comportamento que o script não tinha mais) e da 0.12.0 (init e checkpoint
prometendo silêncio depois de o parser passar a avisar). Três releases, três vezes.

---

## [2026-07-30] chore | modo noturno: 3 cards planejados, 4 contradições da wiki corrigidas

**Contexto:** o dono autorizou o protocolo noturno antes de dormir. Run `noturno-2026-07-30-2228`,
teto de 3 cards e 4 h, **planejamento apenas** — a v1 não implementa, e essa restrição não é dele
para dispensar sem saber o que dispensa: o `T-006` está bloqueado pelo `T-001`, que é justamente o
hook que impediria `push`/deploy/migration. Sem o hook, disciplina noturna é promessa, não garantia.

**Planejado e estacionado em `[!]`:** `T-026` (host alternativo) · `T-023` (reload vs restart) ·
`T-020` (perfis de elenco). Nenhum foi implementado; cada um tem a pergunta exata na nota do card.

**Dois planos corrigiram a premissa do próprio card — e essa é a lição da noite:**

1. O `T-026` supunha "o plugin não roda fora do Claude Code, ponto". Investigando os CLIs reais em
   modo leitura: o **Kimi 0.29.2** lê `AGENTS.md`, carrega `SKILL.md` com auto-invocação por
   description, aceita agents no formato do Claude Code e tem hooks `PreToolUse` **bloqueáveis**
   (exit 2 nega); o **Codex 0.145** já consome marketplace em formato Claude. Isso **derrubou a
   premissa escrita no `T-019`** ("o hook não alcança o Kimi") — a opção (c) daquele card voltou.
2. O `T-020` foi ao transcript e achou o pedido verbatim: o dono disse **"faço só com o Opus"**, não
   "menos Fable" como a nota do card parafraseava. A composição do perfil estava atestada na fala
   dele desde 29/jul — bastava ir olhar.

**Auditoria da wiki (read-only, 14 arquivos) — 4 contradições ativas.** A pior: `distribuicao.md`,
que é a página "como fazer release hoje", ainda dizia que a versão vive em **dois** lugares. São
quatro. Seguir aquela página ao pé da letra **reproduzia o bug que gerou o `T-017`** — o
`marketplace.json` parado em `0.4.0` por sete releases. Também: `MEMORY.md` dizia 8 cards em VALIDATE
quando são 9, e a causa era real — o `T-022` tinha marcador `[?]` mas estava fisicamente sob o
cabeçalho *Backlog*, então quem contou contou por seção visual, não por marcador. É exatamente o
desvio que o `_schema.md` manda vigiar, acontecendo dentro da wiki que descreve a regra.

**Padrão que se repetiu (quarta vez):** a informação muda num lugar e não é varrida nos outros. Desta
vez o defeito estava na própria memória, não no produto — o que é pior, porque a wiki é o que resta
quando a janela morre. As páginas foram corrigidas; o log (aqui) preserva o histórico.

**Não corrigido de propósito → `T-027`:** a regra global do dono proíbe invocar o binário `codex` por
Bash de dentro do Claude Code; `_elenco.md` e `revisar.md` instruem exatamente isso. A justificativa
registrada no `gotchas.md` venceu (o `codex:codex-rescue` aparece como agent type desde 29/jul), mas
a escolha pode continuar certa — foi o `T-010` que provou a CLI direta funcionando, e o painel
depende dela hoje. Decidir é do dono; o `gotchas.md` recebeu o aviso de premissa vencida.

---

## [2026-07-31] feat | 0.14.0 — reload vs restart vira evidência por componente

**Card `T-023`.** A documentação já tinha oscilado **duas vezes** entre "reload basta" (0.10.0, sem
procedência) e "reinicie sempre" (0.11.0, reação à desconfiança). O plano recusou virar a regra pela
terceira vez: o defeito não era o polo escolhido, era **codificar regra binária onde só existe
evidência parcial**. Agora há uma tabela de estados **por componente** — skill está `✅ observado 1×
(2026-07-29)`; comando, agente, hook, MCP, PATH e arquivo lido em runtime estão `❓ não testado,
presuma restart`. Dado novo atualiza **uma célula**, não a regra.

**A regra que sobreviveu de propósito:** card só fecha com teste **pós-restart**. Sessão pós-reload
pode estar mista, e é isso que invalidaria a validação.

**O review reprovou, e os dois bloqueadores mais caros foram autoinfligidos:**

1. A correção **criou** contradição entre `orq/stack.md` e `orq/commands/stack.md` — o texto novo
   apagou o roteamento *instalação por CLI* × *por slash command*, e o comando **ainda dependia
   dele**. O card que existe para eliminar instrução divergente produziu uma.
2. O parágrafo novo passou a citar `plugin update --help` como fonte de uma regra sobre
   **instalação**. O painel da 0.11.0 já havia corrigido exatamente isso (ver entrada de 29/jul), e a
   ressalva explícita foi apagada em silêncio. Procedência errada num card cuja causa raiz declarada é
   *afirmação sem procedência*.

**Terceiro bloqueador, de processo:** a thread ficou com cabeçalho e "RETOMAR AQUI" dizendo *"nada foi
implementado"* enquanto o rodapé descrevia a implementação. Quem retomasse re-perguntaria decisões já
delegadas, ou reimplementaria por cima de 9 arquivos.

**Lição, que é a mesma de sempre com uma volta a mais:** varrer as referências não basta se a
varredura for só textual. As duas frases que quebraram estavam **corretas isoladamente** — o que
quebrou foi a relação entre arquivos. Nenhum dos dois gates pega isso; foi o revisor humano-substituto
que pegou, lendo como leitor hostil.

**Nota de execução:** o implementer das correções morreu por erro de API no meio da verificação. As
sete correções já estavam aplicadas; o Manager mediu arquivo por arquivo antes de continuar, em vez de
relançar cego — relançar teria refeito por cima do que já estava certo.

---

## [2026-07-31] feat | 0.15.0 — descoberta por frase e política de iniciativa em três níveis

**Card `T-025`.** O dono disse que não lembra os comandos. A medição (31 mensagens reais dos
transcripts) mostrou algo pior: os gatilhos canônicos da skill — *"onde paramos"*, *"cadê o board"* —
**ele nunca digitou**. O que ele digita é *"o que preciso decidir??"* e *"não estou vendo card"*.
Entraram só os gatilhos **atestados no corpus**; para `lembrar`, `dormir`, `acordar` e `init`, que não
tinham uma única fala, **nenhum gatilho foi inventado** — a amostra foi declarada insuficiente.

**Três entregas:** `/orq:ajuda` (cardápio por situação, frase em primeiro plano e comando entre
parênteses); os gatilhos medidos; e a **política de iniciativa** que o dono escolheu com estas
palavras — *"age no que é leitura, propõe 1× o resto"*. N1 age e relata (só leitura), N2 propõe uma
vez, N3 sempre pergunta. Transversal: **iniciativa nunca escreve no produto**.

**O review reprovou duas vezes. Quatro bloqueadores na primeira, e o mais instrutivo é o segundo:**

1. A SKILL afirmava que *"o `wiki-lint.md` já proíbe corrigir"* — e o arquivo **autorizava** corrigir
   "página faltando no índice", que é exatamente o que o lint acha. A primeira execução autônoma teria
   escrito sem pedir.
2. O teto *"recusou, não repropõe"* absorveu a regra do checkpoint acima de 50% e a **desligou**: um
   "agora não" aos 52% calaria a salvaguarda até o fim da sessão. É o caminho para a sessão
   irrecuperável que a regra global do dono existe para evitar.
3. *"1 proposta por bloco de trabalho"* — e **"bloco" não estava definido em lugar nenhum**. Três
   leituras defensáveis: 1 por dia, 1 por card, 1 por assunto.
4. Dois gatilhos **inventados** entraram na tabela (zero ocorrências em 583 mensagens) — reincidência
   do defeito que gerou o `T-014`, e um deles sequestrava o pedido de *revisão* para abrir o cardápio.

**A segunda reprovação achou um defeito circular, e vale registrar como padrão:** a correção do item 2
criou a exceção *"recusou aos 52%, repropõe aos 75%"*, mas o item 3 definiu bloco como *"até o próximo
checkpoint"* — e **o que o dono recusou foi o checkpoint**. Logo os 85% caem sempre no mesmo bloco, e
*"nunca no mesmo bloco"* mandava calar. A exceção era **inalcançável por construção**: código morto
para o único caso que citava. Duas correções interagindo produziram um terceiro defeito que nenhuma
delas tinha sozinha.

**Fechado contando o teto por assunto** e permitindo repropor no mesmo bloco a cada piora material.
⚠️ Isso **mudou a semântica de uma decisão que o dono tomou pessoalmente** ("1 por bloco" → "1 por
assunto"); está no card como pendência dele, não corrigido por conta.

**O que os gates pegaram disto tudo: nada.** `validate` e `lint` passaram verdes em todas as rodadas.
Instrução que se autoanula, citação falsa sobre outro arquivo e gatilho inventado só aparecem para
quem lê o texto procurando como ele quebra.

---

## [2026-07-31] feat | 0.16.0 — perfis de elenco trocados por frase

**Card `T-020`.** O `_elenco.md` guardava um **valor** (o time de agora), não uma **escolha de
catálogo**: trocar custava 7 edições, voltar dependia de memória, e o motivo da troca ("crédito curto")
não tinha onde morar. Agora há presets nomeados — `padrao` e `economia` — e ativar um reescreve a
tabela ativa a partir do preset, registrando nome, data e desvios. **Nenhum consumidor mudou:**
`plan-next`, `implement-next`, `revisar` e `stack` seguem lendo a mesma tabela.

**A composição do `economia` não foi inventada** — o planner foi ao transcript de 29/jul e achou a fala
literal do dono: *"faço só com o Opus"*, *"uso mais o Codex e o Kimi"*. A paráfrase que estava na nota
do card ("menos Fable") estava errada, e só se descobriu isso indo à fonte.

**Escrito no preset, não só no plano:** `economia` muda **garantia**, não só custo — plano mais raso,
desempate interno rebaixado, mais peso no Kimi (que não tem sandbox, `T-019`), e os externos são
read-only, então **implementação continua queimando Claude**.

**Duas reprovações, e as duas acharam defeito que a correção anterior tinha criado:**

1. O template definia `padrao` como **ponteiro** ("a tabela acima"). Ativar `economia` fazia `padrao`
   apontar para `economia`; voltar virava no-op e o time titular **sumia do arquivo**. Era a causa raiz
   do card — *"voltar depende de memória"* — reproduzida **dentro da solução do card**.
2. A correção do item 1 deixou o `init.md` com o **único caminho relativo do plugin inteiro**
   (`orq/commands/elenco.md`). Dentro deste repo ele resolve **por acidente**, porque o repo *é* o
   plugin; em qualquer outro projeto o arquivo mora no cache e a instrução quebra. **O lint não vê
   caminho relativo** — verde no gate, quebrado no campo. É a mecânica que deixou `/orquestra:*`
   sobreviver a três releases, e virou o card `T-029`.

**Terceira reincidência do defeito do `T-014`, e desta vez o plano sabia:** foram embarcados dois
gatilhos com **zero atestação** no corpus de 36 mensagens reais — "modo economia" (marcada no plano
como paráfrase) e "volta o time normal". A mitigação que o próprio plano prescrevia — *entra marcada
como tal* — não foi implementada, e as frases apareceram no `_elenco.md` indistinguíveis das medidas.

**A solução para a volta é a parte que vale guardar:** em vez de inventar a frase de retorno, o
**anúncio da troca ensina a reverter**. O dono aprende a frase no instante em que precisa dela, e o
sistema para de adivinhar como ele fala — que é a origem do defeito nas três vezes em que apareceu.
Junto, a coluna de gatilho ganhou uma **categoria** ("sair do perfil / voltar ao time normal") em vez
de uma frase literal: descrever intenção não é fabricar fala.

**Também nesta versão:** o `_schema.md` passou a listar o `_elenco.md` como **escrita compartilhada**
entre janelas — ele é o arquivo mais fácil de perder sem perceber, porque ninguém "trabalha" nele, só
passa e troca uma linha.
## 2026-08-13 — checkpoint de recuperação durante a T-043

- A conversa foi compactada no meio do Loop B já aprovado da T-043.
- Foram relidos `memory/MEMORY.md`, `memory/wiki/KANBAN.md`, a thread da T-043 e o contrato de
  checkpoint; o board continuava com a T-043 em execução e o escopo consultivo aprovado.
- A retomada foi gravada na thread sem reabrir o gate nem abandonar o implementador em curso.
