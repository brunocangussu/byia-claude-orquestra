# T-051 — Elenco em dois eixos (trilha × faixa) + aposentadoria do Kimi

> **Status:** PLANO v2 — revisado em 2026-09-01 após correção do dono no gate. As quatro decisões
> estão **fechadas** (seção 8); resta **um** ponto de confirmação. Nada em `orq/` foi tocado.
> Versão-alvo proposta: **0.24.0** — o board reserva `0.23.0` para o `T-042` (statusline Codex,
> `KANBAN.md:23,54`); quem sair primeiro leva o menor número livre, e os quatro lugares do bump
> andam juntos de qualquer forma.

---

## 1. Diagnóstico — e a correção de leitura do dono

O elenco de hoje tem **um modelo fixo por papel de processo** (`_elenco.md:31-35`); a única
variação é o perfil de crédito (`padrao`/`economia`). A escala de roteamento
(`skills/orq/SKILL.md:26-31`) e o `--rapido` (`revisar.md:156-170`) modulam *processo*, nunca
*modelo*: um typo e uma refatoração de contrato pagam o mesmo `sonnet`.

**A v1 deste plano leu a referência errado — o dono corrigiu.** A configuração dele tem **dois
eixos**, e o desenho anterior colapsou tudo em um (dificuldade). Relida com atenção ao vendor:

- `Frontend → Opus 5` · `Hard UI/UX → Fable 5` · `Simple UI → Sonnet 5` — tudo **Anthropic**;
- `Architecture → Sol` · `Backend → Sol` · `Normal coding → Terra` · `Small changes → Luna` — tudo
  **OpenAI**.

Ou seja: **o domínio da tarefa escolhe o vendor; a dificuldade escolhe o degrau dentro dele.**
Interface/experiência pensa com Anthropic; sistema/lógica/dados pensa com OpenAI; planejamento puro
com Fable. A generalização que ele pediu (*"nem sempre tem front-end"*) cai naturalmente quando o
eixo deixa de ser camada de stack: não é frontend/backend, é **interface vs sistema** — um CLI é
sistema, um brand book é interface, uma migração de banco é sistema. Projeto sem UI só não usa a
linha de interface; o eixo vale em qualquer stack.

O limite duro continua o mesmo (`T-021`): escrita cross-vendor está **fora do desenho** — subagente
nativo do Claude só spawna modelo Claude, e a regra do dono é um writer por worktree, no vendor do
host. A síntese que ele aprovou: **"domínio decide quem pensa; host decide quem escreve."**

## 2. O desenho — dois eixos, cada um com régua objetiva

### Eixo 1 — trilha (`interface` | `sistema`): escolhe o VENDOR de quem pensa

| Trilha | Critério (aplicável por modelo lendo o card, sem o dono no meio) | Vendor que pensa |
|---|---|---|
| **`interface`** | o critério de aceite do card é **perceptual**: o dono valida olhando/usando — aparência, texto voltado a humano, fluxo de interação, experiência, marca | **Anthropic** |
| **`sistema`** | o critério de aceite é **comportamental**: valida-se verificando — lógica, dados, contrato, infra, CLI, build, desempenho | **OpenAI** |

**Régua de desempate:** card misto ou ambíguo → `sistema` (é a trilha default da própria referência
— "Normal coding" mora no lado OpenAI); `interface` exige critério de aceite perceptual explícito.

### Eixo 2 — faixa (`pesada` | `normal` | `leve`): escolhe o DEGRAU de quem escreve

Sobrevive da v1, intacta. Três perguntas, na ordem:

1. O card é **Alto risco** na escala de roteamento, **ou** resta decisão de desenho por tomar
   (mais de uma solução defensável)? → **`pesada`**
2. Senão: o resultado está **completamente determinado** e a verificação é mecânica (typo, rename,
   aplicar diff pronto, doc de código pronto)? → **`leve`**
3. Senão → **`normal`**

Na dúvida, sobe uma faixa (mesma regra da escala, `SKILL.md:33`, citada e não reescrita). A faixa
da *implementação* se reavalia no gate do Loop A: plano aprovado que determina tudo rebaixa a faixa.
⛔ **Corrigido em 2026-09-01, no review da implementação (rodada 4): a reavaliação tem PISO.**
Card **Alto risco** continua `pesada` mesmo com o plano fechado — o plano muda a incerteza, não a
consequência do erro; sem o piso, uma migração de schema com plano aprovado cairia para o
implementer mais fraco. Só rebaixa a `pesada` que veio **exclusivamente** de desenho aberto.

**Registro:** o Manager grava `trilha: … · faixa: …` na nota do card (na criação e revalidado no
gate). Card sem registro → `sistema · normal` (default seguro, é o comportamento de hoje).
**Definição canônica das duas réguas em `commands/elenco.md`**; `SKILL.md`, `plan-next.md` e
`implement-next.md` referenciam — regra escrita 1× (`gotchas.md:231`).

## 3. Cruzamento com os papéis — cada eixo modula um papel diferente

**Os cinco papéis + manager ficam** (as garantias do desenho moram neles; ~124 citações
preservadas; os `agents/orq-*.md` e a migração aditiva dos `_elenco.md` instalados sobrevivem).
A modulação:

| Papel | Modulado por | Regra |
|---|---|---|
| `planner` | **trilha** | `interface` → Anthropic · `sistema` → OpenAI — **nos dois hosts** (é read-only: cross-vendor por CLI/runner é barato e já praticado) |
| `implementer` | **faixa** | sempre **vendor do host** (regra do dono: host decide quem escreve), em três degraus |
| `reviewer` | **nenhum dos dois** | único, sempre **vendor oposto ao host** — ver seção 5 |
| `docs` / `scout` | — | vendor do host, degrau barato (domínio não se paga em leitura/escrita objetiva) |
| `manager` | — | sessão principal, fora do elenco |

**Conflito trilha × revisor, resolvido como regra:** para card de interface no host Claude, o eixo
de domínio pediria revisor Anthropic — mas **a independência ganha, sempre**. A razão de existir do
revisor é ser independente de quem escreveu, não ser apto no domínio; o domínio modula o *planner*
(e, quando útil, a ênfase do briefing do revisor), **nunca o vendor do revisor**. Isso vira texto
normativo em `revisar.md`.

**Consequência estrutural na tabela ativa:** hoje `_elenco.md:37-40` proíbe modelo de outro vendor
na tabela `## Papéis` ("é o T-021, ainda não decidido"). Este card **decide a metade read-only**:
papéis que não escrevem (`planner`, `reviewer`, `scout`) aceitam modelo de qualquer vendor,
resolvido pela Matriz de invocação; papéis de escrita só aceitam o vendor do host. A metade de
escrita do `T-021` continua fora do desenho.
⚠️ **Corrigido em 2026-09-01, no review da implementação (rodada 6): o `scout` NÃO cruza vendor.**
Esta frase contradizia a própria seção 3 (*"`docs`/`scout` — vendor do host, degrau barato,
domínio não se paga em leitura/escrita objetiva"*), e foi ela que a implementação seguiu.
Cruzam vendor **só `planner` (domínio) e `reviewer` (independência)**; `implementer`, `docs` e
`scout` ficam no vendor do host. Motivo do `scout`: leitura ampla e barata não compra aptidão de
domínio, e cruzar ali pagaria transferência a terceiro por nada — além de deixar o papel fora da
coluna `Consumida por` das vias, e portanto fora do cálculo de impacto ao desligar uma via.

**A costura que não dá para engolir (ponto fraco declarado):** no host Claude, um card `sistema ·
pesada` é *pensado* por GPT e *escrito* por Claude (e o simétrico no Codex). Risco real: plano cujo
estilo/premissas o writer de outro vendor executa mal. Mitigação em três pontos, todos no plano de
execução: (a) **handoff reforçado em plano de trilha cruzada** — o `plan-next.md` passa a exigir,
quando vendor do planner ≠ vendor do writer, uma seção "instruções ao executor" com passos fechados
(arquivos, assinaturas, testes, critérios verificáveis), sem depender de contexto implícito do
vendor; (b) **o gate confere executabilidade** — o Manager devolve ao planner plano que exigiria o
writer re-decidir desenho; (c) a **faixa é reavaliada após o plano** — plano fechado rebaixa a
faixa e reduz o espaço de erro do writer, **exceto em card Alto risco, que tem piso `pesada`**
(ver a correção do piso na seção 2). Não há mudança de gate: o que muda é o critério de
qualidade que o Manager já aplica ao avaliar o plano (`plan-next.md:41-48`).

## 4. Times por host — sem Kimi, mecanismo por célula

### Host Claude

| Papel · eixo | Modelo | Mecanismo |
|---|---|---|
| manager | `/model` da sessão | sessão principal — não se configura no elenco |
| planner · interface | `fable` | spawn nativo (Task + override) — comprovado |
| planner · sistema | `gpt-5.6-sol@ultra` | `codex exec -m … -s read-only "<briefing>" < /dev/null` — **mecanismo comprovado no papel de revisor; como planner, não exercitado** |
| implementer · pesada | `opus` | spawn nativo, worktree dedicado |
| implementer · normal | `sonnet` | spawn nativo, worktree dedicado |
| implementer · leve | `haiku` | spawn nativo (worktree se houver trabalho paralelo) |
| reviewer | `gpt-5.6-sol@xhigh` | `codex exec … -s read-only` — comprovado no painel. **Único. Sem contingência interna** (decisão do dono, 2026-09-01) |
| docs · scout | `sonnet` | spawn nativo |

### Host Codex

| Papel · eixo | Modelo | Mecanismo |
|---|---|---|
| manager | `gpt-5.6-sol@high` | sessão principal (verificar o modelo real antes de anunciar) |
| planner · interface | `opus` (comprovar Opus 5) | runner `scripts/run-opus-reviewer.py` via stdin — **limitação declarada: o runner só comprova `claude-opus-5`; `fable` cross-host não tem via comprovada, então a trilha interface no Codex pensa com Opus, não Fable** |
| planner · sistema | `gpt-5.6-sol@ultra` | `codex exec … -s read-only` (aprovado pelo dono em 2026-08-09) |
| implementer · pesada | `gpt-5.6-sol@xhigh` | `codex exec … -s workspace-write`, dentro do worktree |
| implementer · normal | `gpt-5.6-terra@xhigh` | idem (aprovado pelo dono em 2026-08-09) |
| implementer · leve | `gpt-5.6-luna` **sem effort declarado** | idem; **smoke passou em 2026-09-01** — o condicional caiu, ver a procedência abaixo |
| reviewer | `opus` (comprovar Opus 5) | runner `run-opus-reviewer.py` — comprovado 2026-08-09. **Único. Sem contingência interna** (decisão do dono, 2026-09-01) |
| docs · scout | `gpt-5.6-sol@low` | própria sessão ou `codex exec` low |

**Procedência do `gpt-5.6-luna` — atualizada em 2026-09-01, com o smoke feito:** existe no catálogo
do Codex (`~/.codex/models_cache.json`, slug `gpt-5.6-luna`, "Fast and affordable agentic coding
model", janela 272k, sucessor declarado do GPT-5.4 Mini; `~/.codex/config.toml:362`). **Comprovado
pelo smoke:** o modelo está autenticado nesta máquina e responde quando endereçado por
`--model gpt-5.6-luna` — chamada trivial pelo runtime do Codex (`codex-companion.mjs task --model
gpt-5.6-luna`, prompt *"responda somente LUNA_OK"*) devolveu `LUNA_OK`, thread
`01a05e0d-309c-7a92-839c-09f6c418a974`, sem leitura de arquivo e sem execução de comando.
**Segue NÃO comprovado:** (a) quais reasoning efforts ele aceita — catálogo não expõe, smoke não
testou, e por isso o degrau fica **sem effort declarado**; (b) o comportamento em
`-s workspace-write`, o modo real do implementer — o smoke foi read-only. Responder a uma chamada
trivial não é escrever código confiável em worktree. A tabela Host Kimi
(`_elenco.md:154-168`) sai inteira.

## 5. A revisão vira parecer único (N=1) — o painel deixa de existir

**Regra do dono, verbatim:** *"não precisa ser os dois, mas sempre tem que ser com um revisor de
uma LLM diferente. Se eu estiver usando o Claude, o revisor idealmente tem que ser do GPT, e
vice-versa."* Titular: **um revisor, sempre do vendor oposto ao host**. A diagonal OpenAI da v1
está **descartada**; o revisor interno do mesmo vendor **sai do fluxo padrão**.

**O que morre e o que entra no lugar — com todas as letras:**

- **"Confirmado por 2+" deixa de existir.** Todo achado é solitário **por construção**. O
  protocolo que era a exceção (`revisar.md:177-178`: achado solitário → o Manager verifica no
  código antes de repassar) vira **o protocolo inteiro**: o Manager audita cada achado contra o
  código, descarta o que não tem cenário de falha concreto, e entrega veredito + achados
  verificados. O formato `BLOQUEADORES/RISCOS/VEREDITO` fica.
- **"PAINEL PARCIAL" morre como conceito** (pressupõe N≥2) e vira **"REVISÃO DEGRADADA"**: titular
  indisponível (binário, autenticação, timeout, saída vazia) → entra a **contingência interna do
  host**, com a perda de independência **nomeada** — nunca substituição silenciosa.
- **SEM contingência interna — nenhuma exceção.** ✅ **Decidido pelo dono em 2026-09-01**, contra a
  recomendação do planner (que propunha três exceções): **o revisor é sempre do vendor oposto ao
  host, e ponto.** Não existe cair no revisor interno. As três consequências, que o Manager tem que
  declarar em vez de contornar:
  1. **Dado sensível → não há revisor nenhum.** A regra LGPD do dono (global,
     `~/.claude/CLAUDE.md`) proíbe mandar PII/prontuário/credencial para modelo de terceiro, e do
     ponto de vista de cada host **o vendor oposto é terceiro**. Sem exceção, o revisor titular
     fica impedido e nenhum outro o substitui. O que resta é o **Manager auditando o diff ele
     mesmo** — o que ele já faz na reconciliação — e **declarando** "sem revisão independente por
     restrição de dados". Isso não é revisor interno: é ausência de revisor, nomeada. **Nunca**
     spawnar revisor do mesmo vendor para tapar esse buraco.
  2. **Titular indisponível → a revisão não acontece.** Binário fora do ar, autenticação vencida,
     timeout, saída vazia: o Manager declara **REVISÃO DEGRADADA — sem parecer** e o card **não
     avança sozinho**; seguir sem revisão é decisão do dono, pedida na hora.
  3. **`--rapido` perde a razão de existir como estava.** Ele rebaixava o painel a um revisor só —
     e um revisor só já é o padrão. Vira **briefing enxuto para o mesmo titular externo**, nunca
     troca de vendor. A linha "Pequeno → implemente + revisor interno" da escala (`SKILL.md:29`)
     **precisa ser reescrita** por este card: ou o revisor é o externo, ou não há revisor.
  **Segundo parecer só sob demanda do dono** — nunca padrão; pedir "quero uma segunda opinião"
  adiciona um parecer avulso sem ressuscitar o painel.
- **A honestidade de `_elenco.md:75-78`** ("o interno não conta como outra LLM") migra para a
  contingência: parecer de contingência não entrega independência de vendor, e o texto diz isso.

**Nome do comando:** `/orq:revisar` **fica** — renomear quebraria `SKILL.md:99`, `ajuda.md:19`,
`implement-next.md:43`, o README e o hábito do dono. O corpo é reescrito: de "painel de revisores
reconciliado" para "**parecer independente + auditoria do Manager**".

**O que quebra em `revisar.md`, verificado linha a linha (bem mais que na v1):**

- linha 2 (frontmatter): "Painel de revisores independentes (Claude + Codex + Kimi…)";
- linhas 6-11: a justificativa inteira ("revisores diferentes erram diferente… interseção…
  divergência") — é o racional do painel, não do parecer único;
- linhas 18-22: briefing "pra todos" / formato "de todos" — plural sem referente;
- **seção 2 inteira (linhas 46-170)** é reescrita: o título "Disparar os revisores EM PARALELO"
  perde o objeto; o bloco do `orq-reviewer` interno (56-66) vira a contingência; o bloco "Host
  Codex — painel obrigatório Opus 5 + Kimi K3" (68-103) vira só o titular Opus via runner; o bloco
  "Se o Codex estiver ATIVO…" (105-117) vira o titular do host Claude; o bloco Kimi (119-140) sai;
  "Outros revisores ativos" (142-146, com "não acrescente a diagonal OpenAI" travada pelo
  `lint:281`) sai; "revisor que falhar" (148-150) vira REVISÃO DEGRADADA; toda a lógica de
  rebaixamento do `--rapido` (152-170) dissolve — comparava o *interno* ao preset, e o titular
  agora é externo por definição;
- linhas 172-184 (reconciliação): vira o protocolo de auditoria de parecer único;
- linhas 186-192 (entrega): "quem apontou (Claude / Codex / …)" perde sentido com N=1;
- linhas 196-199 (regras): sobrevivem como estão.

**Consequência em `elenco.md`/`_elenco.md`:** a seção "Revisores externos" muda de *composição de
painel* para **registro de capacidade das vias cross-vendor** (CLI `codex` · runner Opus): binário,
modelo, comprovações e data. A frase-contrato "política habilitada, não capacidade comprovada"
(travada pelo lint em `revisar.md` e `elenco.md`) **sobrevive** com o mesmo sentido. O `reviewer`
passa a ser linha do time por host, não tabela à parte. A orientação "Só Claude, sem GPT? `codex
off`…" (`elenco.md:229-230`) é reescrita: sem a via externa, **toda** revisão é degradada — dito
assim.

## 6. Plano de execução — passos verificáveis, na ordem

`G0` = `grep -ci "kimi\|moonshot\|kimi-code" <arquivo>` retorna **0**. Worktree dedicado, writer
único. Passos 1-7 no **mesmo commit** (travam strings uns dos outros).

1. **`orq/commands/elenco.md`** — template em dois eixos: réguas canônicas de trilha e faixa;
   tabela `## Papéis` com `planner·interface`, `planner·sistema`, `implementer·pesada/normal/leve`,
   `reviewer` único; regra "papel read-only aceita qualquer vendor; escrita só vendor do host";
   regra "independência ganha do domínio no reviewer"; "Revisores externos" → registro de
   capacidade; times por host da seção 4 com mecanismo; Matriz 2 vendors × 2 hosts; validação de
   argumento (`planner <modelo>` sem sufixo aplica às duas trilhas e avisa; `implementer` sem
   sufixo ajusta a `normal` e avisa); migração de legado (tabela antiga: `planner` único → as duas
   trilhas naquele modelo; `implementer` único → as três faixas; linha `kimi` → aposentadoria
   proposta **com gate**); presets `padrao`/`economia` no formato novo (economia rebaixa degrau/
   effort dentro do mesmo vendor). *Prova:* G0; template contém 2 trilhas + 3 degraus + reviewer
   único.
2. **`orq/commands/revisar.md`** — a reescrita da seção 5: parecer único oposto ao host,
   contingência em três exceções, REVISÃO DEGRADADA, auditoria do Manager, formato mantido, LGPD
   com precedência intacta. *Prova:* G0; sem as palavras "painel"/"PAINEL PARCIAL" em sentido
   normativo; strings novas batem com o passo 7.
3. **`orq/commands/plan-next.md`** — resolve o planner pela **trilha** do card; grava
   `trilha · faixa` no card no gate; exige a seção "instruções ao executor" quando trilha cruzada
   (vendor do planner ≠ vendor do writer); remove o ramo Host Kimi (linha 28) e "Claude, Codex ou
   Kimi" (linha 18). **`orq/commands/implement-next.md`** — resolve o implementer pela **faixa**;
   remove Host Kimi (30-31); reescreve o passo 2 (43-52): sai "painel independente"/"confirmado
   por 2+", entra o parecer único + auditoria. Sem redeclarar modelo (o lint proíbe,
   `lint:344-360`). *Prova:* G0 nos dois; citam as réguas por referência.
4. **`orq/skills/orq/SKILL.md`** — escala de roteamento ganha o mapa para faixa (por referência);
   anúncio de roteamento nomeia trilha e faixa; linha 99 ("revisor interno + externos ativos") →
   parecer único oposto; exemplo do anúncio (linha 39, "Codex + Kimi") reescrito; parágrafo
   `ORQ_PACKAGE_ROOT` (57-71) sem o ramo Kimi; gatilho de instalação (105) sem "no Kimi".
   *Prova:* G0.
5. **`orq/commands/instalar.md`** — `description`/`argument-hint` sem kimi; seção "## Kimi"
   (97-156) removida; gotcha dos três hosts vira dois. **`orq/stack.md`** — camada 4: seção kimi
   (156-179) sai; intro reescrita (revisor único cross-vendor; some "dois externos… maioria").
   **`orq/commands/init.md:272`** e **`orq/commands/ajuda.md:19,25`** — ajustes pontuais ("Claude +
   externos ativos" → parecer oposto ao host; "no Codex/no Kimi" → "no Codex"). *Prova:* G0 nos
   quatro.
6. **`orq/commands/stack.md`** — revalidar "Revisor externo: quem testar" no singular (já é G0).
7. **`orq/scripts/lint-coerencia.py`** — a mudança é maior que na v1: **substituir** em
   CONTRATOS_CODEX/revisar as strings "Host Codex é exceção", "exatamente Opus 5 + Kimi K3",
   "Codex ativo e Kimi K3 ativo", "não acrescente a diagonal OpenAI", "PAINEL PARCIAL" (→
   "REVISÃO DEGRADADA") e "Sem elenco, valem os padrões de fábrica: reviewer `opus`," (fábrica
   nova: titular oposto ao host) pelas equivalentes novas; **manter** "política habilitada, não
   capacidade comprovada" e todos os contratos do runner (`OPUS_*`, 16 KiB, 240s — o runner segue
   titular no host Codex e via da trilha interface); em `elenco_cmd`, substituir as linhas
   "reviewer 1/reviewer 2" pelo reviewer único e **trocar o guarda `count == 2`** (`lint:333-341`)
   por: linha do reviewer oposto presente 1× em cada tabela de host + comprovação do alias Opus na
   tabela Codex; **guardas novos**: (a) ocorrência case-insensitive de `kimi|moonshot` em `orq/` =
   problema (só `orq/` — README/CLAUDE/AGENTS têm menção histórica legítima); (b) template contém
   as 2 trilhas do planner e os 3 degraus do implementer. *Prova:*
   `python3 orq/scripts/lint-coerencia.py .` **verde** — antes deste passo reprova, e é esperado.
8. **`README.md`** — menções vivas (34, 99, 134, 232-247, 376…): revisor único cross-vendor no
   pitch e na seção de revisores; histórico de versões pode citar Kimi. *Prova:* nenhuma promessa
   viva de painel; lint verde.
9. **Bump `0.24.0` nos quatro lugares** (`orq/.claude-plugin/plugin.json`, README Status,
   `memory/MEMORY.md`, `.claude-plugin/marketplace.json`) — salvo se este card sair antes do
   `T-042`, caso em que o Manager decide no release quem leva `0.23.0`. *Prova:* guarda de versão
   do lint.
10. **Gates — são TRÊS, nesta ordem** (atualizado em 2026-09-01 pelo `T-052`: a suíte veio do ramo
    remoto e este handoff foi escrito antes de ela existir): `PYTHONDONTWRITEBYTECODE=1 python3 -m
    unittest discover -s orq/scripts -p 'test_*.py'` · `claude plugin validate ./orq --strict` ·
    `python3 orq/scripts/lint-coerencia.py .` — os três verdes. **A suíte vem primeiro**: os outros
    dois leem texto e manifesto, então regressão no verificador, no runner ou no guardião passa
    inteira por eles.
11. **`memory/wiki/_elenco.md` deste projeto** (página viva, fora do lint): formato novo — dois
    eixos, reviewer único, registro de capacidade, sem Kimi; o porquê vai no `fixes-history.md`.
12. **Release + teste comportamental** (fecha o card): `claude plugin marketplace update orquestra`
    + `claude plugin update orq@orquestra` + restart + verificação do cache com
    `python3 orq/scripts/verify_installed_cache.py` a partir de **fonte limpa** (clone detached do
    SHA publicado) + critérios da seção 7. ⚠️ **`diff -rq` NÃO serve mais como prova** (corrigido em
    2026-09-01 pelo `T-052`): comparação bruta reprova cache válido por artefato instalado-only
    legítimo — `.in_use`, `.orphaned_at`, migrated-command-skills — que é o bug do `T-049`. ✅ **Smoke do luna feito em 2026-09-01**
    (`LUNA_OK`, thread `01a05e0d-309c-7a92-839c-09f6c418a974`); resultado e os dois limites
    registrados no `_elenco.md`.
13. **Board e memória (Manager, no checkpoint):** anotar encerramento em `T-007` (Kimi 3º revisor)
    e no braço Kimi de `T-026`; anotar em `T-021` que a metade read-only foi decidida aqui;
    atualizar `arquitetura.md` e o índice; checklist da Decisão 4 entregue ao dono.

## 7. Critérios de aceite — o dono exercita conversando

1. **"quem tá revisando?"** → um revisor só, do vendor oposto ao host, com a regra dita ("revisor é
   sempre de outra LLM") e as exceções nomeadas.
2. **Eixo de domínio, no mesmo host:** *"deixa o texto desse aviso mais claro pro usuário"* e
   depois *"otimiza a leitura do board no script"* → os dois anúncios de roteamento nomeiam
   **planners de vendors diferentes** (interface → Anthropic; sistema → OpenAI).
3. **"ajusta a mensagem desse erro em `x.py`"** (card **Pequeno** — 1 arquivo, sem decisão de
   desenho) → o anúncio nomeia a faixa (`leve`) **e** o modelo barato do host, que é quem escreve.
   ⚠️ **Corrigido em 2026-09-01, no review da implementação:** o exemplo anterior era *"corrige esse
   typo no README"*, que é **Trivial** na escala — e em Trivial não há implementer spawnado, o
   Manager escreve na sessão. Exigir ali "o modelo barato escreve" contradizia a escala. A regra
   ficou: **a escala mede cerimônia, a faixa mede a capacidade de quem foi spawnado; onde não há
   spawn, não há faixa** (Trivial exibe `—`).
4. **"tem um comando pra instalar o Orquestra no Kimi?"** → resposta: suporte aposentado; não
   oferece instalar.
5. **"tô com pouco crédito, modo economia"** → perfil troca o time no formato novo (duas trilhas,
   três degraus), sem citar Kimi.
6. **"revisa isso"** num diff com dado sensível → a resposta diz que **não haverá revisor** (LGPD
   impede o vendor oposto, e não existe substituto interno), que o Manager audita ele mesmo, e
   pergunta se o dono quer seguir assim. **Não pode** aparecer revisor do mesmo vendor do host.

## 8. Decisões — fechadas pelo dono em 2026-09-01

1. **REFORMULADA — "domínio decide quem pensa; host decide quem escreve":** o `planner` (por
   domínio) e o `reviewer` (por independência) podem cruzar vendor; a escrita fica no vendor do
   host, modulada pela faixa (Claude `opus`/`sonnet`/`haiku`; Codex
   `sol@xhigh`/`terra@xhigh`/`luna`). ✅ ⚠️ **O `scout` saiu da lista em 2026-09-01 (rodada 6 do
   review):** ele é read-only, mas segue o vendor do host — ver a correção na seção 3.
2. **Revisor único, sempre do vendor oposto ao host** (verbatim: *"sempre tem que ser com um
   revisor de uma LLM diferente"*). Diagonal descartada; interno sai do fluxo padrão. A
   independência ganha do domínio, sempre. ✅
3. **`gpt-5.6-luna` como implementer·leve no Codex** — condicional **cumprido**: smoke passou em
   2026-09-01 (`LUNA_OK`). O degrau entra **sem effort declarado**, e effort suportado +
   comportamento em `workspace-write` seguem sem medição, escritos como pendência. ✅
4. **Limpeza dos artefatos Kimi da máquina: DEPOIS** do release validado e do cancelamento efetivo
   — o card entrega o checklist (`~/.claude/agents/kimi-revisor.md` · seção de delegação do
   `~/.claude/CLAUDE.md` · `~/.agents/skills/orq/` · `~/.kimi-code/`), o dono aplica. ✅

5. **SEM exceções à regra do revisor oposto** — ✅ **decidido pelo dono em 2026-09-01, contra a
   recomendação do planner.** Ele leu o custo (diff com dado sensível fica sem revisor nenhum) e
   escolheu a regra pura. As três consequências estão escritas na seção 5 e **são de execução
   obrigatória**: dado sensível → ausência de revisor declarada + auditoria do Manager (nunca
   revisor do mesmo vendor); titular fora do ar → REVISÃO DEGRADADA, card não avança sozinho;
   `--rapido` → briefing enxuto para o mesmo titular externo, e a linha "Pequeno → implemente +
   revisor interno" de `SKILL.md:29` **é reescrita por este card**.

**Nenhuma decisão pendente. O card está READY.**

## 9. Riscos

- **Plano de um vendor, execução de outro** (a costura da Decisão 1): plano GPT escrito por Claude
  (e o simétrico) pode carregar premissas que o writer executa mal. Mitigação na seção 3 (handoff
  fechado em trilha cruzada + gate confere executabilidade + faixa reavaliada pós-plano). Resíduo
  declarado: não zera — o primeiro card cruzado real é o teste, e reprovar plano inexecutável é
  função do gate.
- **Reviewer correlacionado ao planner em trilha cruzada:** host Claude + card `sistema` → planner
  GPT, writer Claude, reviewer GPT — o parecer é independente **do writer**, não do planner. O
  Manager audita os achados também contra o plano, e o texto de `revisar.md` declara essa natureza.
- **N=1 perde a checagem cruzada:** sem interseção, erro do revisor único não tem contrapeso — a
  auditoria do Manager contra o código é a única defesa, e "segundo parecer sob demanda" existe
  como válvula, nunca como padrão. Dito com todas as letras na página.
- **Contradição entre arquivos segue o modo de falha nº 1:** `revisar.md` × `elenco.md` ×
  `SKILL.md` × lint travam strings uns dos outros — inclusive as novas ("REVISÃO DEGRADADA",
  fábrica do reviewer). Passos 1-7 no mesmo commit; guarda anti-kimi vira regressão permanente.
- **Correção que acrescenta em vez de substituir** (gotcha 2026-08-05): promessas vivas de
  "painel"/"três revisores"/"confirmado por 2+" sobrando em `README.md:376`, `_elenco.md:250-253`,
  `implement-next.md:47-48` ou na prosa do `revisar.md`. Mitigação: G0 + releitura dirigida por
  "painel|parecer|2+|maioria|interseção".
- **Guarda mecânico prova ausência de string, não de regra** (`gotchas.md:218`): G0 e lint verdes
  não provam a composição nova coerente — o fecho é o teste comportamental do passo 12.
- **Migração dos `_elenco.md` instalados:** "Revisores externos" muda de semântica (painel →
  capacidade) e a tabela ativa ganha sufixos; arquivo legado sem migração continua funcionando
  pelos defaults (`sistema · normal`, implementer único = três faixas), e a migração real é
  proposta com gate — nunca reescrita silenciosa.
- **Runner só comprova Opus:** a trilha interface no host Codex pensa com Opus, não Fable —
  limitação declarada; estender o runner a outro modelo Anthropic é card futuro, não este.
- **Cópia Kimi órfã na máquina** até a Decisão 4 ser executada: quem abrir o Kimi CLI roda a
  0.22.0 com painel de três. Risco baixo (assinatura a cancelar), registrado no checklist.

**Suposições que não pude confirmar:** (a) `codex exec -s read-only` **produzindo plano** — o
mecanismo é comprovado como revisor; como planner, não exercitado (primeiro Loop A `sistema` no
host Claude é o teste real). (b) Reasoning efforts e custo do `gpt-5.6-luna` — o smoke de 2026-09-01 provou
que o modelo responde, **não** os efforts nem a escrita em `workspace-write`; segue sem medição. (c) `haiku` na faixa leve — precedente indireto (docs/scout no `economia`), sem
medição; ajuste de uma linha se incomodar.

**Fora do escopo (card novo, não engorda este):** execução da limpeza Kimi na máquina (Decisão 4)
· `docs/superpowers/` (histórico, fora do lint) · metade de **escrita** do `T-021` · perfil
`economia` do host Codex (sob demanda) · runner Anthropic parametrizado (Fable cross-host) ·
faixa/trilha retroativa nos cards antigos.

---

## ⏭️ RETOMAR AQUI

**Próxima ação exata:** o Manager apresenta ao dono **só o ponto único da seção 8** (as três
exceções da contingência interna — recomendação: confirmar como está) e a proposta de versão
(**0.24.0**, `0.23.0` reservado ao `T-042`). Confirmado, mover `T-051` de `[>]` para `[~]` READY e
despachar o implementer (host Codex, `gpt-5.6-terra@xhigh`, worktree dedicado) com os passos 1-10
da seção 6 — 11-13 são do Manager. Nenhuma edição em `orq/` antes disso.
