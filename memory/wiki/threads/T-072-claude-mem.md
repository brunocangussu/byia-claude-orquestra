# Frente `@frente-economia` — o claude-mem: papel, fiação e cobertura

**Origem:** análise que o dono fez em outra conversa, sobre o banco `~/.claude-mem/claude-mem.db` e
os transcripts de agosto/2026. Trazida aqui para o ciclo. **Auditada contra o código antes de virar
card** — as três afirmações verificáveis conferem:

| Afirmação da análise | Verificação |
|---|---|
| a `SKILL.md` tirou o claude-mem da lista de ferramentas | ✅ `SKILL.md:364` diz "memória local/confiável realmente disponível no host" — **sem nomear nada** |
| o `stack.md` o marcou como "opcional; não propor no Codex" | ✅ `stack.md:214`, literal |
| o gatilho "lembra quando" não chama busca nenhuma | ✅ `SKILL.md:144` manda consultar "uma busca confiável do host" — sem nomear ferramenta, sem dizer como |

## ⚠️ Correção de uma medição minha, que mudou a decisão

Eu havia dito ao dono que a injeção custava **12,1k tokens por sessão** e recomendado cortar 74%
com base nisso. **Estava errado por 4,4×.** A análise dele, de ~2,3k, é que está certa.

**O erro:** medi os 10 resumos de sessão como se todos fossem injetados por inteiro
(`len(str(dict(row)))`, que ainda inflava com nomes de coluna e escapes do Python). O formato real,
conferido contra o bloco que este projeto recebeu no `SessionStart`, é outro: **os resumos antigos
entram como uma linha cada; só o mais recente traz o corpo.**

| Parte | Real |
|---|---|
| 50 observações (1 linha cada) | 5.234 chars ≈ 1,45k tok |
| 9 resumos (1 linha cada) | 1.618 chars ≈ 0,45k tok |
| 1 resumo completo (o último) | 2.199 chars ≈ 0,61k tok |
| cabeçalho, legenda, stats | ~900 chars |
| **Total** | **≈ 2,8k tokens/sessão** |

**Consequência: o argumento de custo cai por terra.** 2,8k numa sessão de 379k é ruído. Rebaixar a
ferramenta por causa disso não se sustentava — o dono estava certo em desconfiar.

## O problema real é sinal, não custo — e a medição confirma

Distribuição das 1.534 observações deste projeto:

| | Tipo | Qtd |
|---|---|---|
| corta | discovery | 697 |
| corta | change | 527 |
| ✅ | decision | 101 |
| ✅ | bugfix | 99 |
| ✅ | security_alert | 7 |
| ✅ | gotcha · security_note | 1 · 1 |
| corta | os outros 19 tipos | ~100 |

**80% é narração de sessão** ("215 tests green", "final gate status") — exatamente o que o
`_schema.md` deste projeto chama de *derivável* e manda não guardar. Os tipos que interessam somam
**209**, folgado para `CONTEXT_OBSERVATIONS=25`.

## A divisão de papéis (decisão do dono, não re-litigar)

- **wiki + checkpoint** = o porquê e as consequências. **Fonte da verdade.** Não muda.
- **claude-mem** = **rede de segurança** do que não chegou ao checkpoint: gotcha de meio de sessão,
  decisão não registrada, sessão que morreu antes do checkpoint.

Complemento, nunca substituto. É o que precisa estar escrito nos dois lugares que hoje o rebaixam.

## O aporte desta janela: `T-073` e a configuração são um PAR

A análise trata "ligar a fiação" e "filtrar a injeção por tipo" como itens separados. **Não são, e a
ordem importa.**

O filtro por tipo corta **86% do volume** da injeção — e quem classifica o tipo é o **observer
Haiku**, não uma regra determinística. Uma decisão que ele rotule como `change` (há 527 delas) some
da injeção automática. Isso é aceitável **se** a busca sob demanda alcançar o material; hoje ela não
alcança, porque o gatilho não nomeia ferramenta nenhuma — 3 chamadas MCP em 79 sessões, zero
`mem-search`.

👉 **Aplicar o filtro sem o `T-073` deixa o material valioso inalcançável pelos dois caminhos.**
Recomendação: `T-073` primeiro, ou os dois juntos. Nunca o filtro sozinho.

## Restrições

- Nada é bumpado, commitado ou publicado sem o dono.
- A configuração da máquina dele (item 5) **não vira card** — é ambiente, não produto.
- O `T-074` para no gate **antes** de instalar: o gargalo do Codex é número de chamadas, e o
  observer roda por tool use. Medir antes de prometer.

## `T-074` — o plano para o Codex, com o custo medido

**O diagnóstico original:** o `claude-mem` não estava no Codex — por isso o `bruno-brain`, com
11.777 chamadas naquele host, não tinha observação nenhuma. Era ausência de instalação, não defeito.

✅ **Instalado em 02/09** (`13.23.1`), mas leia o incidente abaixo antes de deixar ligado.

### Os 5 hooks e o que custam

| Evento | Timeout |
|---|---|
| SessionStart | 20 s |
| UserPromptSubmit | 20 s |
| PreToolUse | 30 s |
| **PostToolUse** | **120 s** ← é aqui que o observer roda |
| Stop | 60 s |

**Volume estimado, projetado do Claude:** 13.639 chamadas geraram 7.572 observações (taxa 0,56). O
Codex fez 58.363 chamadas no mês → **~32.400 observações/mês, cerca de 4,3× o volume atual**.

### O que decide o gate — e a boa notícia

⚠️ A preocupação natural seria "isso piora o gargalo do Codex". **Não piora.** O observer chama um
**modelo Anthropic barato**, não o GPT: **não consome o limite semanal do Codex**, que é justamente
o gargalo daquele host. O custo real é outro, e são dois:

1. **Conta Anthropic** — 4,3× mais chamadas do observer do que hoje.
2. **Latência** — o `PostToolUse` tem teto de 120 s. Num host cujo problema é *número de chamadas*,
   somar espera a cada uso de ferramenta é o risco concreto a vigiar.

### Procedimento (o mesmo padrão do próprio Orquestra, `instalar.md:92`)

```
codex plugin marketplace add thedotmack/claude-mem
codex plugin marketplace list            # ⚠️ PASSO OBRIGATÓRIO: pegue o nome de REGISTRO
codex plugin add claude-mem@claude-mem-local
codex plugin list
```

⚠️ O nome do marketplace **não é previsível**: o repositório se declara `thedotmack`, e o Codex o
registrou como **`claude-mem-local`**. `@thedotmack` falha. Ver `gotchas.md`.

Depois: **sessão nova** (sessão aberta não recarrega plugin) e conferir o **carimbo do banco** — não
o `plugin list`, que só prova instalação, nunca gravação.

**Recomendação REVISADA depois do incidente de 02/09: não deixar ligado no Codex ainda.** As 24
sessões com `memory_session_id` nulo são todas daquele host; ligar agora tende a reproduzir a falha.
Reavaliar quando o upstream corrigir.

## O incidente de 02/09 — o claude-mem parou 22h em silêncio

**Diagnóstico fechado, e é bug do plugin, não de configuração.** A sessão foi marcada
`status='completed'` enquanto a conversa continuava; ao gravar o resumo de uma sessão já dada como
encerrada, o `memory_session_id` vem nulo e o `NOT NULL` de `session_summaries` recusa. 42 falhas
consecutivas. **126 das 481 sessões** receberam observação depois de marcadas como completas — o
padrão é geral, esta sessão só foi a que travou.

Enquanto isso: `{"status":"ok"}` na porta, worker vivo, sessões registrando — e zero observações
gravadas, de **nenhum** projeto (a sessão 483, de outro projeto, também ficou em zero).

**Hipótese errada que testei antes:** mensagem envenenada em `pending_messages`. Limpei a fila com
backup e o erro continuou subindo durante a investigação. Fila vazia + nada gravado provou que o
problema era antes. Registrado em `gotchas.md` porque o erro de método importa mais que o acerto.

**Feito:** backup do banco em `~/.claude-mem/claude-mem.db.bak-2026-09-02` (226 MB) e as 3 mensagens
removidas preservadas íntegras em `~/.claude-mem/removidas-2026-09-02.json`.

**Contorno:** sessão nova nasce sem o conflito. Não conserta o bug.

⚠️ **Consequência para o `T-074`:** as **24 sessões com `memory_session_id` nulo são todas do
Codex** — nenhuma das 285 do Claude. O claude-mem já rodou naquele host em maio e produziu
exatamente este defeito. O plugin **foi instalado** no Codex nesta janela
(`codex plugin add claude-mem@claude-mem-local`, note o nome de **registro** do marketplace, não
`@thedotmack`), mas **a recomendação virou: não deixar ligado até o upstream corrigir.**

## Checkpoint anterior — instalação e incidente de 02/09

**`T-072` e `T-073` publicados na `0.26.0` e em VALIDATE.** O `T-074` também: o claude-mem **foi
instalado no Codex** (`codex plugin add claude-mem@claude-mem-local` — atenção ao nome de
**registro** do marketplace, não `@thedotmack`).

**A decisão que resta é sua:** deixar ligado no Codex ou não. O dado contra é que as **24 sessões
com `memory_session_id` nulo são todas daquele host**, nenhuma das 285 do Claude — o mesmo defeito
que travou o observer por 22 h em 02/09.

**Antes de confiar de novo:** o teste não é `plugin list` nem o health da porta 37701, que respondeu
`ok` durante as 22 h paradas. É o **carimbo do banco**:

    python3 -c "import sqlite3,os,datetime;c=sqlite3.connect(os.path.expanduser('~/.claude-mem/claude-mem.db'));print(datetime.datetime.fromtimestamp(c.execute('select max(created_at_epoch) from observations').fetchone()[0]/1000))"

Se a data não avançar depois de trabalho real, continua quebrado — e a investigação recomeça pelo
`observer-health.json`, não pela fila.

**A config de filtro por tipo** (`OBSERVATION_TYPES`, `OBSERVATIONS=25`, `SESSION_COUNT=5`) ficou
segura de aplicar **depois** do `T-073`: agora que a busca é nomeada e chamada, o que o filtro
esconder da injeção continua alcançável sob demanda.

## ⏭️ RETOMAR AQUI

**Checkpoint de recuperação verificado em 2026-09-05.** O pedido atual do dono continua sendo
corrigir e provar o `claude-mem` no Claude Code e no Codex antes da comparação com o AI-Memory. O
`T-075` está em PLANNING, `trilha: sistema · faixa: pesada`; plano completo em
`../../../docs/superpowers/plans/2026-09-05-t075-claude-mem-paridade.md`.

**Causa raiz nova e literal:** o Codex anuncia `claude-mem` `13.24.0`, mas o bundle instalado é
`13.23.1`. O log mostra mismatch → `SIGKILL` → respawn do mesmo bundle. O upstream `13.24.1`
recompilou os bundles para corrigir exatamente o empacotamento quebrado de `13.24.0`. O cache do
Claude já tem `13.24.1`; o cache do Codex ainda está em `13.24.0`.

**Estado dos hosts:** depois que o worker `13.24.1` do Claude assumiu, não houve novo mismatch nem
`SIGKILL` literal e as observações voltaram a avançar. Ainda assim, Claude e Codex têm sessões
marcadas `completed` antes de prompts/observações posteriores; há respostas não XML descartadas e
fila acumulada. Portanto o Claude captura, mas também está degradado. No Codex, Orquestra e
`bruno-brain` são intermitentes; New ByIA está atrasado; MVP e Bruno Vascular tiveram sessão com
prompt e zero observações. Não foi lido conteúdo clínico.

**Limite LGPD:** o observer usa Claude/Anthropic. A proposta fail-closed é excluir
`*Bruno Vascular*` e validar esse projeto apenas como `EXCLUÍDO`, com prompt sintético e sem abrir
arquivos. Os demais projetos Codex salvos recebem canário de duas interações e prova metadata-only
no banco.

**Execução depois do gate:** backup da configuração do `claude-mem` em
`~/.claude-mem/settings.json.bak-antes-t075-2026-09-05-1630`; exclusão
`*Bruno Vascular*` aplicada e provada com ferramenta sintética — zero sessão e zero prompt no banco.
O Codex foi atualizado para `13.24.1`; manifesto, marketplace e bundle têm a mesma versão e o SHA do
bundle coincide com o cache Claude. O comando oficial de upgrade do marketplace terminou duas vezes
sem mover o snapshot; o checkout limpo foi avançado por fast-forward de `be44b6c8` para `b6e05382`.

**Canários anteriores ao fallback:** quatro projetos não clínicos executaram dois turnos na mesma
sessão. Todos reprovaram após o SLO: nenhum gravou `user_prompts`; dois ficaram sem
`memory_session_id`; houve resumo sem prompt/observação e 11 falhas estruturadas de autenticação do
SDK entre 16:35:13 e 16:36:06, afetando sessões novas e antigas.
O Claude, em diretório temporário vazio, gravou três prompts na mesma sessão, mas ainda estava
`ATRASADO`, sem `memory_session_id` ou observação, na última leitura. Não houve novo mismatch de
versão nem loop de `SIGKILL` nesta janela.

**Primeiro estágio ausente fechado:** o `UserPromptSubmit` manual do `claude-mem` gravou uma linha
imediatamente, enquanto oito prompts automáticos do Codex gravaram zero. O handler funciona; o host
não está disparando esse evento do manifesto do plugin. Foi adicionado somente o fallback
`UserPromptSubmit` ao `~/.codex/config.toml`, sem duplicar `PostToolUse` ou `Stop`, após backup em
`~/.codex/config.toml.bak-antes-claude-mem-t075-2026-09-05-1650`. TOML válido; nenhum
`trusted_hash` escrito manualmente.

**Detector entregue no working tree:** `orq/scripts/claude_mem_status.py` abre o SQLite em
`mode=ro`, nunca seleciona conteúdo e distingue `CAPTURANDO`, `ATRASADO`, `PARADO`, `OCIOSO`,
`INDETERMINADO` e `EXCLUÍDO`. Há 12 testes novos; suíte completa 232/232, manifesto estrito e lint
verdes. Sem bump, commit, release, instalação do Orquestra ou push — continuam gates separados.

**Leitura correta do log:** depois do baseline houve zero mismatch, zero `SIGKILL` e zero erro
`NOT NULL` estruturados. As 11 ocorrências de `NOT NULL` numa busca bruta vinham do próprio texto
diagnóstico capturado em metadados do log; filtrar por nível/categoria eliminou esse falso positivo.
As 11 falhas de autenticação são erros estruturados reais.

**Próxima ação do dono:** criar pela interface um chat novo em qualquer projeto não clínico e
aprovar o hook **“Recording prompt in claude-mem”**. Tarefas criadas em background não mostraram o
gate; o estado `config.toml:user_prompt_submit:1:0` continua sem confiança. Depois o Manager repete o
canário de dois turnos em cada projeto permitido e só move o card se prompts, observações e resumos
avançarem. Patch/fork do upstream continua fora da autorização.

**Checkpoint de recuperação — limpeza dos canários (2026-09-05):** os seis chats auxiliares
criados para isolar a captura por projeto e validar o fallback foram concluídos e arquivados a
pedido do dono. O arquivamento é reversível e não apagou o histórico. A tarefa principal permanece
aberta exatamente no gate acima: criar um chat novo pela interface e aprovar
**“Recording prompt in claude-mem”**; nenhum novo canário deve ser criado antes dessa aprovação.

**Checkpoint de recuperação — canário visual e saturação (2026-09-05):** o dono criou pela
interface a sessão Codex `01a07345-457f-7c62-8437-ef4ab7a86bb1` e executou dois turnos com `pwd`.
O banco registrou `session_db_id=548` e exatamente dois prompts. O log provou a cadeia automática:
dois `PostToolUse` e dois `Stop/summarize` foram enfileirados; portanto, o host chama os hooks e o
fallback de `UserPromptSubmit` funciona. Após 15 minutos, porém, o detector marcou `PARADO`, com
zero observações, zero resumos e `memory_session_id` ausente.

A causa operacional observada é saturação do pool global: `CLAUDE_MEM_MAX_CONCURRENT_AGENTS=2`,
com dois subprocessos SDK legítimos ocupando os slots e várias sessões esperando. O código mantém
os eventos pendentes somente em RAM; reiniciar o worker agora poderia perdê-los e foi recusado.
A documentação `docs/production-guide.md` do próprio `claude-mem` recomenda valor `3` para melhor
vazão sem sobrecarga. Esse ajuste não foi aplicado: aguarda decisão explícita do dono por alterar o
paralelismo do provedor. O chat-canário deve permanecer sem arquivamento até a validação final.

**Decisão e aplicação:** o dono aprovou o ajuste. Backup criado em
`~/.claude-mem/settings.json.bak-antes-concorrencia-t075-2026-09-05-175953`; somente
`CLAUDE_MEM_MAX_CONCURRENT_AGENTS` mudou de `2` para `3`. JSON válido e worker preservado no mesmo
PID `8366`, sem restart. O canário `session_db_id=548` continuou `PARADO` após mais de 30 minutos
porque sua espera foi criada com o limite antigo. Próximo gate: um único chat novo, com um turno e
`pwd`, para nascer sob o limite `3`; comprovar no banco prompt + observação + resumo e arquivar os
dois chats de teste. Nenhum outro canário deve ser criado.

**Checkpoint de recuperação e validação final — 2026-09-05:** após compactação sem checkpoint, o
pedido corrente foi preservado e o estado durável foi relido. O dono criou pela interface a sessão
Codex `01a07432-4407-7290-9662-72c743836117`, que nasceu como `session_db_id=571`, `status=active`
e gravou o prompt do canário. O primeiro lote, contendo apenas `pwd`, foi processado e gerou resumo,
mas deliberadamente `obsCount=0`: não havia aprendizado relevante para observar.

Sem criar outro chat, a mesma sessão recebeu uma leitura somente leitura do card `T-075`. O envio
programático não incrementou `user_prompts`, portanto não foi usado como prova desse hook; porém os
hooks `PostToolUse` e `Stop` enfileiraram observação e resumo. O banco persistiu a observação
`32999` e os resumos `5103` e `5106`. A execução fresca do detector terminou com exit `0` e estado
`CAPTURANDO`: 1 prompt, 1 observação, 2 resumos e `memory_session_id` real, todos atribuídos à
sessão 571. O fallback global do Codex e a concorrência `3` ficam comprovados em projeto não
clínico; `*Bruno Vascular*` permanece excluído por LGPD. `T-075` vai para `VALIDATE`, nunca `DONE`,
até o dono confirmar o uso prático.

**Correção do gate após checagem cruzada do Claude:** o detector atual da última sessão Claude no
Orquestra (`session_db_id=518`) retornou `PARADO/event_after_session_completion`. Há captura real —
11 prompts, 50 observações e 8 resumos — mas a sessão foi marcada `completed` antes de eventos
posteriores, a anomalia upstream já documentada. Um canário sintético novo pelo CLI local não
chegou à API: `claude -p` respondeu `Not logged in`, com zero tokens e custo zero; portanto não
produziu evidência e não autoriza declarar os dois hosts limpos. O chat-canário Codex foi arquivado
depois da prova. `T-075` retorna a `AWAITING_OWNER`; gate restante: um chat novo na interface já
autenticada do Claude, em projeto não clínico, com uma leitura relevante, seguido do mesmo detector
metadata-only. A conclusão anterior de ir a `VALIDATE` fica explicitamente superada por esta nota.

**Canário Claude pela interface — 2026-09-06:** a sessão nova
`ff967ab8-12ca-49bd-91ca-3a39f9e9e426` nasceu às 09:25:55 no projeto `IVA - App System` como
`session_db_id=574`, `status=active`, com 1 prompt e `memory_session_id` real. O `rg T-075` não
encontrou o card porque esse checkout tem outro quadro. O observer recebeu o evento, mas respondeu
literalmente `No observation recorded` por não ter resultado útil do comando; o resumo foi
persistido como `summaryId=5111`. Portanto os hooks e o gerador funcionaram, mas o critério forte
continua parcial: falta uma observação. Próximo gate, sem criar outro chat: no mesmo Claude, ler
`README.md` e explicar em uma frase o problema principal do projeto; depois repetir o detector.

**Fechamento do segundo turno Claude — reprovado em 2026-09-06:** o dono executou a leitura no
mesmo chat. `README.md` não existia, mas o Claude encontrou e leu `CLAUDE.md`, produzindo uma
conclusão concreta e sem editar arquivos. O banco gravou o segundo prompt às 09:29:23. O defeito de
ciclo reapareceu antes: a sessão 574 fora finalizada às 09:29:14. Os hooks ainda enfileiraram a
observação `messageId=17` às 09:29:29 e o resumo `messageId=18` às 09:29:37, ambos apenas em RAM.

Às 09:44:35, passado o SLO de 15 minutos, o banco permanecia com 2 prompts, 0 observações e somente
o resumo 5111 do primeiro turno. O detector seguia `PARADO/event_after_session_completion`. O
worker estava vivo, mas havia quatro subprocessos Claude descendentes enquanto a configuração era
3; nenhuma consulta SDK da sessão 574 chegou a iniciar. Não houve restart, pois os eventos pendentes
vivem em RAM. Conclusão literal para o comparativo: a fiação global do Codex está `CAPTURANDO`; no
Claude, a fiação dispara, mas o claude-mem continua operacionalmente degradado por finalização
prematura e saturação. Próximo gate é decisão do dono: autorizar plano de patch local/fork do
upstream ou aceitar esta reprovação como resultado do comparativo.

**Checkpoint de recuperação — 2026-09-06:** após nova compactação sem checkpoint, foram relidos
`memory/MEMORY.md`, o board e esta thread. O pedido corrente foi preservado: o dono autorizou
**planejar** um patch local/fork controlado do claude-mem; implementação, restart, instalação,
commit, push e comunicação externa continuam fora deste gate. `T-075` permanece em `PLANNING`.
Checkpoint verificado; conversa continua.

**Checkpoint de recuperação — 2026-09-06, pós-compactação:** `memory/MEMORY.md`, o board e esta
thread foram relidos novamente. O pedido atual continua limitado a concluir e registrar o plano do
patch local/fork do `claude-mem`; não há autorização para implementar, instalar, reiniciar, commitar,
publicar ou contatar o upstream. O próximo gate continua sendo a aprovação explícita do plano.

**Plano do patch concluído — 2026-09-06:** a comparação do checkout instalado `13.24.1`
(`b6e05382`) com o `main` oficial inspecionado (`3939fbb2`) mostrou os seis arquivos de lifecycle
selecionados byte a byte iguais; não existe correção pronta no upstream para apenas transplantar.
O plano local combina três garantias: (1) reativar no SQLite uma sessão completada quando um evento
válido posterior é admitido; (2) correlacionar respostas do SDK a IDs individuais por FIFO, sem
confirmar todo o lote prefetched; e (3) terminar o subprocesso somente depois do resultado do resumo,
liberando o slot e preservando/reiniciando a `ActiveSession` se houver turno novo ou buffer restante.

Plano executável em
`../../../docs/superpowers/plans/2026-09-06-t075-claude-mem-lifecycle-patch.md`. Ele inclui TDD,
suíte completa, typecheck, lints, build, gate anterior ao restart, canários Claude/Codex, teste de
quatro sessões com pool 3, exclusão LGPD e rollback. Nada foi implementado, instalado ou reiniciado;
`T-075` passa a `AWAITING_OWNER` e aguarda aprovação literal do dono.

**Gate de implementação aprovado — 2026-09-06:** o dono respondeu literalmente
`pode implementar o plano T-075`. O card passa a `READY/DEV_REVIEW`. A autorização cobre código e
testes no checkout isolado; o gate separado do plano continua valendo antes de instalar o build ou
reiniciar o worker com mensagens potencialmente residentes apenas em RAM.

**Implementação isolada pronta; revisão bloqueada — 2026-09-06:** no worktree
`/private/tmp/claude-mem-t075-lifecycle`, branch `codex/t075-claude-mem-lifecycle`, o implementer
concluiu as tarefas 2–8 em TDD. A matriz específica passou 42/42; no tree pós-build, a suíte literal
passou 2.991 testes, com 27 skips e zero falhas; typecheck, `lint:hook-io`, `lint:spawn-env` e build
também passaram. Um teste temporal de `SIGTERM`, sem diff, oscilou uma vez e passou isolado 6/6 e na
repetição integral. Nenhum cache, configuração, banco ou worker foi alterado; não houve commit/push.

O preflight do diff encontrou zero e-mail, bearer, atribuição de segredo, chave privada, caminho de
usuário ou termo clínico. A revisão independente seria feita pelo titular do host Codex,
Anthropic Fable 5.1, em cinco lotes de no máximo 16 KiB contendo somente hunks de código/testes; os
quatro bundles gerados (6,6 MB) ficam fora do envio e são validados mecanicamente. A execução foi
bloqueada antes do egress porque falta autorização explícita para enviar esse código privado ao
fornecedor Anthropic. Nenhum lote saiu da máquina. `T-075` volta a `AWAITING_OWNER` com a pergunta:
autoriza esse envio delimitado para a revisão independente?

**Checkpoint de recuperação — 2026-09-06, revisão corretiva:** após compactação, foram relidos
`memory/MEMORY.md`, o board e esta thread. O dono já autorizou o envio sanitizado, e os cinco lotes
foram revisados pelo Anthropic Fable 5.1. O parecer encontrou três cenários concretos que precisam
de correção antes do gate: múltiplos frames `assistant` para a mesma resposta podem deslocar o FIFO
cedo demais; um evento pode chegar durante `finalizeSession` e ser removido ao final; e o limite de
turno usa o número do prompt capturado no começo do gerador, não o resumo que de fato concluiu.
Também será impedido que `turn-complete` sobrescreva erro de quota/autenticação/resultado. O pedido
corrente continua sendo implementar e revisar o plano T-075 no worktree isolado. Instalação,
restart, commit, push e publicação permanecem fora deste gate. Checkpoint verificado.

**Checkpoint de recuperação — 2026-09-06, validação final:** após nova compactação,
`memory/MEMORY.md`, o board e esta thread foram relidos integralmente. O pedido corrente continua
sendo concluir a implementação e a validação local do patch T-075 no worktree isolado. As correções
pós-review já estão no tree e a matriz dirigida passou; falta repetir a suíte completa e os gates
no estado final. A autorização anterior não inclui instalar o build, reiniciar o worker, alterar
cache/configuração/banco, commitar, publicar ou enviar novos lotes externos. Checkpoint verificado.

**Implementação e gates locais concluídos — 2026-09-06:** o patch permanece isolado em
`/private/tmp/claude-mem-t075-lifecycle`, branch `codex/t075-claude-mem-lifecycle`. A versão final
correlaciona dispatches por UUID e resultado do SDK, agrega frames `assistant`, usa o texto canônico
do `result`, confirma somente IDs cobertos e devolve mensagens à fila em erro ou correlação
inválida. A reativação ocorre apenas após enqueue inédito; a finalização lida com trabalho que chega
durante a corrida de idle/finalize e não sobrescreve erros de quota, autenticação, overflow ou
resultado.

A revisão externa delimitada consumiu as duas rodadas previstas com Anthropic Fable 5.1. Os achados
reproduzíveis das rodadas foram corrigidos. A árvore final não recebeu uma terceira revisão externa;
foi auditada e validada localmente pelo Manager. No estado pós-build, a matriz dirigida passou
`67/67` com 262 asserts; a suíte completa passou `3010`, pulou 27 integrações opcionais e teve zero
falhas, com 8690 asserts em 276 arquivos. Typecheck, `lint:hook-io`, `lint:spawn-env`, build e
`git diff --check` saíram 0. O diff final contém 20 arquivos: 13 fontes/bundles e 7 arquivos de
teste, com 1982 inserções e 365 remoções.

Nenhum cache instalado, configuração, banco ou worker foi alterado; não houve restart, commit,
push, publicação nem novo envio externo. `T-075` retorna a `AWAITING_OWNER`. Próximo gate literal:
autorizar a instalação controlada do mesmo build nos caches Claude e Codex e um único restart,
somente depois de provar por metadados que a fila residente em RAM drenou. Depois disso ainda faltam
os canários funcionais Claude/Codex, o teste de quatro sessões com pool 3, a prova de exclusão LGPD
e a validação prática do dono; gates verdes locais, sozinhos, não provam funcionamento em runtime.

**Gate documental do Orquestra:** o card T-075 mede 215 bytes, a suíte obrigatória do Orquestra
saiu 0, o manifesto estrito passou e `git diff --check` saiu 0. O lint de coerência não ficou verde:
ele detectou que `orq/commands/checkpoint.md` diverge do cache instalado na mesma versão 0.27.0.
Esse arquivo já estava modificado por outra frente antes desta retomada e não foi alterado pelo
T-075; por isso a divergência foi preservada e registrada, sem correção lateral nem falsa alegação
de gate integralmente verde para o repositório Orquestra.

**Instalação autorizada e caches preparados — 2026-09-06:** o dono autorizou literalmente o gate
operacional. A fila RAM do worker antigo chegou a zero após 155 segundos, com o mesmo PID `59682`;
só então foram criados backups em
`~/.claude-mem/t075-backups/20260906-185848/`. Os dois caches, `settings.json`, registros de plugin
Claude, `config.toml` do Codex e o metadado local do marketplace Codex foram copiados. `diff -qr` e
`cmp` provaram que os backups correspondem byte a byte aos alvos.

Hashes antigos, iguais nos dois hosts: `worker-service.cjs`
`f301b7bdb6f9ff6f3571ad21a303625000fdd592ad29c863fc5e93d4cc588118`;
`transcript-watcher.cjs` `b99c292940b9a0a452692d5927c0a7906e6fe3e94a52305c948123b20892c57e`;
`SessionStore.js` `f6eabc9eb8f288ef5dae5ed7ed9799aa6ac4ac715b6ea416e75537f29ab81ad0`;
`viewer-bundle.js` `5114a4394e046082905303770bcd96762798aa7dd91bebca6ee2d86922691000`.

O diff completo foi aplicado, sem commit, aos marketplaces locais Claude e Codex. No Claude, o
updater oficial recusou recópia por manter a mesma versão `13.24.1`; o plugin foi então removido com
`--keep-data` e reinstalado pelo próprio marketplace. No Codex, `codex plugin add
claude-mem@claude-mem-local` reinstalou o cache. Os quatro artefatos críticos ficaram byte a byte
iguais entre worktree, cache Claude e cache Codex. Hashes novos: `worker-service.cjs`
`4ccfc8061e013fc177069285a0662e61c1d8686706126f0ccc6f274d6aee83ae`;
`transcript-watcher.cjs` `6476018a5de9d27993ce20737688bcd926c7ba56b78dfc1cd75dd044c798ea65`;
`SessionStore.js` `2b59c47d4605a153a2407ff445de2ccc12ca5396e9425c0c00c1540957869ec3`;
`viewer-bundle.js` `e3fa117c63c6bc6056d50e6bd6f04cc300c4f0084de7a2d9e4458d94112d28e2`.

**Restart bloqueado sem perda:** depois da instalação, os próprios hooks e outras tarefas voltaram
a alimentar o worker antigo. A fila passou de 2 para 18, depois de 69 para 94 e finalmente de 125
para 162; sessões ativas chegaram a 9. O processo `59682` mostrou quatro subprocessos Claude apesar
do limite configurado em 3, reproduzindo a saturação que o patch corrige. Todas as tentativas
controladas encerraram sem chamar o endpoint quando a fila não zerou. Um monitor único em
`/private/tmp/t075-drain-restart.mjs` permanece aguardando duas leituras zero consecutivas e uma
confirmação final; só então chamará uma vez `POST /api/admin/restart` e exigirá PID sucessor mais
readiness. Não houve restart, perda aceita, alteração de banco, commit, push ou publicação. Para
liberar o gate, todas as outras tarefas Claude, Codex e companions precisam parar de produzir
eventos por tempo suficiente para a fila antiga drenar.

**Checkpoint de recuperação — 2026-09-06, restart ainda bloqueado:** após compactação sem
checkpoint, `memory/MEMORY.md`, o board e esta thread foram relidos. O monitor fail-closed de 30
minutos terminou com `queueDepth=217`, `activeSessions=9` e PID antigo `59682`, sem chamar o endpoint
de restart. Numa segunda janela, a fila havia caído a 43, mas voltou de 45 para 51 enquanto as
sessões ativas subiram de 8 para 9; o monitor foi interrompido antes de qualquer leitura zero. O
worker não reiniciou, e nenhuma perda foi aceita. `settings.json` e `~/.codex/config.toml` continuam
byte a byte iguais aos backups de `~/.claude-mem/t075-backups/20260906-185848/`; os caches patchados
permanecem instalados, aguardando somente o restart seguro. Próxima ação: o dono pausa as demais
tarefas Claude, Codex e companions e avisa `PRONTO`; então o mesmo monitor aguarda a drenagem,
reinicia uma única vez e prova PID sucessor mais readiness antes dos canários. Checkpoint
verificado; conversa continua.

**Restart forçado autorizado e concluído — 2026-09-06:** o dono aceitou literalmente a perda da
fila pendente do claude-mem. Antes da ação, foi criado um backup consistente do SQLite em
`~/.claude-mem/t075-backups/20260906-force-restart-nBqAqm/` (249.974.784 bytes). O snapshot do gate
registrou `queueDepth=43`, `activeSessions=5` e PID `59682`; `POST /api/admin/restart` respondeu 200.
O sucessor subiu no PID `72744`, versão `13.24.1`, com readiness 200, fila 0 e zero sessões ativas.
A perda aceita se limita aos 43 itens residentes na fila no instante do restart; o AI-Memory não
foi reiniciado nem alterado.

**Checkpoint de recuperação — 2026-09-06, pós-restart:** após compactação sem checkpoint,
`memory/MEMORY.md`, o board e esta thread foram relidos, preservando o pedido atual. O card volta a
`IMPLEMENTING`: faltam os canários funcionais metadata-only e a melhoria aprovada para reutilizar a
task exata do Codex Companion por card e papel, em vez de criar uma task nova a cada continuação.
O trabalho do Companion está isolado em `/private/tmp/openai-codex-t075-companion-reuse`, branch
`codex/t075-companion-thread-reuse`; a base limpa passou 91/91 testes. Não há commit, push,
publicação ou bump autorizados. Checkpoint verificado; implementação continua.

**Codex Companion com retomada determinística — 2026-09-06:** a melhoria aprovada foi implementada
em TDD no worktree `/private/tmp/openai-codex-t075-companion-reuse`. O runtime agora aceita
`task --resume-thread <thread-id>` e retoma a thread pedida, mesmo quando existe outra mais nova;
rejeita combinações ambíguas com `--resume-last`, `--resume` ou `--fresh`; preserva o ID também no
worker background; e `task --json` devolve juntos `jobId` e `threadId` para o handoff durável.
Instruções do comando, subagente, skill interna e README foram alinhadas.

Os testes provaram RED antes da implementação e GREEN depois. A suíte final passou `95/95`; sintaxe,
`npm run check-version`, build TypeScript e `git diff --check` saíram 0. O patch local foi instalado
no marketplace e nos caches Claude/Codex `openai-codex/codex/1.0.6`; o runtime tem SHA-256
`8d0256f4016267c8c64bb9b1acd4089563aaf9ce2c2e027b9365c54172908054` nos quatro locais. Backup
integral e byte-idêntico do estado anterior:
`~/.claude/plugins/t075-companion-backup-20260906-EQEVDE/`. Não houve commit, push, publicação,
restart das tasks ou bump de versão.

**Prova metadata-only pós-restart do claude-mem:** no worker PID `72744`, observações posteriores ao
restart foram persistidas tanto para Codex (`session_db_id=511`, projeto `byia-claude-orquestra`,
16 observações) quanto para Claude (`session_db_id=518`, mesmo projeto, 2 observações e 1 resumo),
sem ler conteúdo. Outros projetos não clínicos também avançaram. O health retornou `status=ok` e o
worker seguia processando (`queueDepth=29`, 3 sessões ativas). Não nasceu sessão nova depois do
restart; portanto essa evidência prova consumo real nos dois hosts, mas não substitui o canário
forte de uma sessão nova. Nenhum chat adicional foi criado para evitar repetir a poluição da barra
lateral que motivou a melhoria.

**Checkpoint de recuperação — 2026-09-06, protocolo Companion:** após nova compactação sem
checkpoint, foram relidos `memory/MEMORY.md`, o board e esta thread. O pedido atual permanece:
concluir a melhoria aprovada da T-075 para reutilizar a task exata do Codex Companion por
`card+papel`, sem criar chats sintéticos adicionais. O restart forçado já foi concluído com perda
explicitamente aceita de 43 itens da fila; o worker sucessor PID `72744` persiste eventos reais dos
dois hosts. A implementação do protocolo Orquestra segue isolada em
`/private/tmp/orq-t075-companion-reuse`; o teste contratual novo está vermelho por três lacunas
documentais ainda não implementadas. Não há autorização para commit, push, publicação ou bump de
versão. Checkpoint verificado; implementação continua.

**Melhoria T-075 pronta nos worktrees; gate de promoção — 2026-09-06:** o refinamento final do
Codex Companion ficou em `/private/tmp/openai-codex-t075-companion-reuse`: retomada exata por
`--resume-thread`, JSON com `rawOutput`/`jobId`/`threadId`, conflitos de roteamento recusados e
efforts `max|ultra`. A suíte final passou `96/96`; sintaxe, `check-version`, build TypeScript e
`git diff --check` saíram 0. O runtime candidato tem SHA-256
`a810d521826b18c3dcde281533d318d83d6a1a29dc2a6501819dc55e47c3bebb`; marketplace e caches ativos
continuam na revisão anterior, hash
`8d0256f4016267c8c64bb9b1acd4089563aaf9ce2c2e027b9365c54172908054`, porque o gate de instalação
bloqueou a sobrescrita antes de qualquer escrita.

O protocolo Orquestra ficou pronto em `/private/tmp/orq-t075-companion-reuse`, com isolamento por
`card+papel`, primeira chamada fresca, continuação pelo `threadId` exato, handoff durável e arquivo
somente depois do estado terminal. Planejamento, revisão, elenco, arquitetura e a skill canônica
foram alinhados; o teste novo provou RED (3 falhas) e depois GREEN (3/3). A suíte completa passou
`294/294` no Python 3.12, o manifesto estrito passou, o lint de coerência passou e
`git diff --check` saiu 0. O `python3` inicial do shell resolveu para o Python 3.9 do macOS e não
conseguiu importar uma anotação `str | None` preexistente; a repetição no Python 3.12 instalado foi
integralmente verde.

Nada foi commitado, publicado, instalado do worktree Orquestra nem bumpeado. `T-075` vai para
`AWAITING_OWNER`. Próximo gate literal: autorizar (1) sincronizar o Companion final no marketplace
e nos caches Claude/Codex; e (2) bumpar o Orquestra de `0.27.0` para `0.27.1`, promover o patch ao
checkout principal e instalar os caches locais, sem commit, push ou publicação. O canário forte
será feito na próxima sessão real nova, sem criar chat sintético adicional.

**Leitura final metadata-only do runtime — 2026-09-06:** o PID sucessor `72744` continuava ouvindo
apenas em `127.0.0.1:37701`; `/api/health` respondeu 200, `status=ok`, `initialized=true` e
`mcpReady=true`. Desde o restart, a sessão Codex `511` chegou a 62 observações e a sessão Claude
`518` a 3 observações + 2 resumos, com atividade respectivamente até 23:10:28 e 22:34:50 locais.
Nenhuma sessão nasceu depois do restart, confirmado por contagem zero em `sdk_sessions`; por isso o
canário forte continua pendente e será reaproveitado na próxima sessão real, sem poluir a barra
lateral com teste sintético.

**Reconciliação com o T-080 paralelo — 2026-09-06:** o dono avisou que o Claude concluiu outra
tarefa e que o `main` avançara dois commits. A leitura mostrou `main`, `origin/main` e a base do
worktree T-075 no mesmo SHA `af3201c`; os commits `d85856a` e `af3201c` já estavam incorporados à
base, portanto não há rebase nem conflito a resolver. O Orquestra já está em `0.27.1` publicado e
ainda não instalado; a próxima candidata da T-075 é `0.27.2`, não `0.27.1`. O gate recusou tratar
"pode continuar" como autorização específica de bump e bloqueou antes da primeira escrita. Nenhum
arquivo de release foi alterado, nada foi instalado ou staged, e `git add .` não será usado.
Próximo gate literal: autorizar o bump local para `0.27.2` e a instalação local do Companion final
e do Orquestra nos dois hosts, sem commit, push ou publicação.

**Checkpoint de recuperação — 2026-09-07, promoção local autorizada:** após a compactação,
`memory/MEMORY.md`, o board e esta thread foram relidos integralmente. O dono autorizou
literalmente o bump local do Orquestra para `0.27.2` e a instalação local do Companion final e do
Orquestra nos caches Claude/Codex, mantendo fora do escopo commit, push e publicação. O candidato
Orquestra permanece isolado em `/private/tmp/orq-t075-companion-reuse`, agora sobre a base
`3d6131d`, com os quatro anchors em `0.27.2`; o candidato Companion permanece em
`/private/tmp/openai-codex-t075-companion-reuse`, runtime SHA-256
`a810d521826b18c3dcde281533d318d83d6a1a29dc2a6501819dc55e47c3bebb`. O checkout principal tem
mudanças paralelas preexistentes em `_stack.md`, `T-078`, `checkpoint.md` e `stack.md`, que serão
preservadas; nenhuma operação de staging amplo será usada. Próximo passo seguro: criar backups dos
caches atuais, instalar somente os arquivos autorizados e provar identidade byte a byte antes de
promover o patch T-075 ao checkout principal. Checkpoint verificado; execução continua.

**Checkpoint de recuperação — 2026-09-07, após falha do hook legado:** `memory/MEMORY.md`, o board
e esta thread foram relidos integralmente após a compactação. O pedido vigente continua sendo
concluir a promoção local autorizada da T-075: Orquestra `0.27.2` e Companion final nos caches
Claude/Codex, sem commit, push, publicação ou criação de chats. A última ação observada foi o
instalador Codex criar o cache `0.27.2`; em seguida, o hook já carregado por esta tarefa tentou usar
o caminho removido de `0.27.1` e entrou em falha repetitiva. Próximo passo seguro: verificar o
registro e a identidade do `0.27.2`, restaurar o cache legado `0.27.1` somente para compatibilidade
com tarefas antigas e então concluir as provas e a promoção seletiva. Checkpoint verificado;
execução continua.

**Reinstalação final dos caches Orquestra 0.27.2 — 2026-09-07:** a fonte usada foi um worktree
detached limpo no commit remoto aprovado `d7982486498e516649c65aa8ce97d86680e2e670`. Antes da
reinstalação, o verificador encontrou divergência real apenas no cache Claude
(`commands/checkpoint.md` e `commands/stack.md`); o cache Codex já coincidia. Os dois caches foram
sincronizados novamente a partir dessa fonte, preservando `.in_use` no Claude e `.codex-plugin` no
Codex. Backup anterior: `~/Library/Application Support/orquestra-backups/t075-20260907-113424`.

Prova pós-instalação com o verificador vindo da fonte limpa: `host=claude` e `host=codex` saíram
`ok`; os hashes de `scripts/claude_mem_status.py`, `commands/checkpoint.md` e `commands/stack.md`
ficaram idênticos entre fonte e os dois caches. Gates completos com Python 3.12: 294/294 testes,
`claude plugin validate ./orq --strict` verde e `lint-coerencia.py .` verde. O
`~/.codex/config.toml` manteve o mesmo SHA-256
`971c44772912b3c90271beb018b208847b3af64a075b0f1ef4484e7890d2c5c7`: plugin claude-mem no Codex
continua `enabled=false`, fallback direto ativo = 0 e fallback comentado = 1. Nenhum commit, push,
publicação, mudança de card ou chat novo foi feito nesta conclusão.

**Promoção local concluída — 2026-09-07:** o Companion final foi sincronizado no marketplace
local e nos caches Claude/Codex `openai-codex/codex/1.0.6`. O runtime
`scripts/codex-companion.mjs` tem SHA-256
`a810d521826b18c3dcde281533d318d83d6a1a29dc2a6501819dc55e47c3bebb` nos quatro locais; o diff
integral só mostrou os extras esperados de runtime `.generated` e `.in_use`. Backup anterior:
`~/.claude/plugins/t075-companion-final-backup-20260907-QRjPYH/`.

O Orquestra `0.27.2` foi instalado e aparece `installed=true/enabled=true` no Codex e habilitado no
escopo `user` do Claude. Os dois `verify_installed_cache.py` retornaram
`ok: installed cache matches source`; os dois marketplaces locais também batem exatamente com o
candidato `/private/tmp/orq-t075-companion-reuse`. Backup pré-instalação:
`~/.claude/plugins/t075-orquestra-backup-20260907-XK1Dsn/`. O `codex plugin add` concluiu a versão
nova, mas removeu o cache `0.27.1` que esta tarefa antiga ainda usava no hook. Por isso o retorno
entrou num ciclo de `context-guard.py: No such file or directory`. O cache legado foi restaurado
lado a lado a partir do backup e conferido por `diff -qr` e SHA-256, sem alterar o `0.27.2`.

O patch documental T-075 e os quatro anchors de versão foram promovidos seletivamente ao checkout
principal; mudanças paralelas foram preservadas e o índice de staging continuou vazio. No candidato
final, a suíte passou `294/294`, o manifesto estrito passou, o lint de coerência passou e
`git diff --check` saiu 0. Não houve commit, push nem publicação.

**Canários metadata-only pós-instalação — 2026-09-07:** o worker segue no PID `72744`, versão
`13.24.1`, health `status=ok`, `initialized=true` e `mcpReady=true`. Uma sessão Claude nova
(`session_db_id=624`) terminou com 2 prompts, 7 observações e 1 resumo; uma sessão Codex nova
(`session_db_id=616`) terminou com 4 prompts, 13 observações e 3 resumos. O detector classificou as
duas como `CAPTURANDO/metadata_advanced`, sem `event_after_session_completion`. A regra clínica foi
confirmada somente por metadados como `EXCLUÍDO/project_matches_exclusion`, sem abrir arquivo nem
criar linha. O plugin está habilitado globalmente nos dois hosts e o fallback Codex está no
`config.toml` global, sem seção de hooks por projeto; portanto vale para todos os projetos
permitidos, preservando a exclusão deliberada `*Bruno Vascular*`.

O limite de três também está sendo respeitado pelos processos: com quatro sessões lógicas e fila
ativa, havia exatamente 3 subprocessos Claude descendentes do worker. A janela de 29 segundos não
capturou liberação/substituição de PID, então a prova runtime específica de a quarta sessão assumir
o slot dentro do SLO continua pendente; não foi criado chat sintético para forçá-la. `T-075` fica em
`VALIDATE`, aguardando essa observação natural e a validação prática do dono.

**Verificação do checkout principal:** a suíte completa também passou `294/294`, o manifesto
estrito passou e `git diff --check` saiu 0. O lint de coerência do checkout vivo retornou 1 somente
porque `orq/commands/checkpoint.md`, modificado por outra frente antes da promoção, difere do cache
instalado; a T-075 não alterou nem absorveu esse arquivo. O candidato isolado, que é a fonte dos
caches 0.27.2, continua com o mesmo lint em exit 0.

**Correção do registro Codex:** a checagem final encontrou o claude-mem `13.24.1` ainda instalado e
capturando pelo fallback global, porém com `enabled=false` no registro do plugin. O backup
pré-instalação provava que a chave era `true`; a mudança ocorreu durante a sequência local de
instalação. Foi criado
`~/.codex/config.toml.bak-antes-reativar-claude-mem-20260907-110458` e somente essa chave voltou a
`true`. O TOML foi parseado, o diff contra o backup mostrou exatamente duas linhas (`false` →
`true`) e `codex plugin list --json` confirmou `installed=true`, `enabled=true`, versão `13.24.1`.

**`T-074` executado e `T-081` nascido — 2026-09-07.** O dono decidiu o `T-074` pela recomendação
registrada no `T-078`: rodar claude-mem e AI-Memory em paralelo no Codex **contamina a comparação**,
porque uma injeta memória que muda o que a outra captura. O claude-mem foi desligado **no Codex
apenas** — o Claude Code segue capturando (`claude-mem@thedotmack: true`).

**O desligamento tinha dois pontos, não um.** Além de `[plugins."claude-mem@claude-mem-local"]`
(`enabled = false`), existe um `[[hooks.UserPromptSubmit]]` **escrito direto no `config.toml`**,
fora do plugin, rotulado *"fallback (plugin hook não disparado pelo host Codex)"*, que chama
`worker-service.cjs hook codex session-init`. **Desabilitar o plugin não desliga esse hook** — quem
parasse no `enabled = false` acharia que desligou e continuaria capturando a cada prompt. O bloco
foi comentado com nota de reversão, não removido. Prova depois da mudança: `claude-mem` com zero
ocorrências nos seis eventos do Codex e `ai-memory` intacto nos seis.

### O achado que virou o `T-081`

A configuração que o `T-065` mandava aplicar (`OBSERVATION_TYPES`, `OBSERVATIONS=25`,
`SESSION_COUNT=5`) **só funciona em dois terços**. As duas contagens são chaves reais e foram
aplicadas. `CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES` **não é lida por ninguém**: aparece na lista de
chaves aceitas pelo endpoint HTTP de settings e **zero vezes** no `context-generator.cjs`. Escrever
ali não faz nada — e, pior, *parece* que fez.

**Onde o filtro mora de verdade:** `getActiveMode().observation_types`, isto é, `modes/code.json`.
O `context-generator` monta o `IN (?,?,…)` da consulta a partir dos tipos do **modo**, não das
settings. Um modo derivado (`code--<nome>.json`) resolveria, e `~/.claude-mem/modes/` é procurado
antes do cache do plugin, portanto sobrevive a update.

**Por que isso não foi feito na hora, e é a parte que importa:** os `observation_types` do modo
também alimentam o `type_guidance` do prompt do observer. Cortar `discovery` e `change` de lá **não
filtra a leitura — muda o vocabulário de classificação do observer**, ou seja, mexe na captura. A
premissa do `T-065` ("filtrar a injeção") não se sustenta nesse caminho: o que o filtro esconder
some do banco, não da tela. Por isso o `T-081` nasceu em vez de a mudança ser aplicada.

**Checkpoint de recuperação — 2026-09-07, correção cross-session:** após compactação,
`memory/MEMORY.md`, o board, esta thread e a thread T-078 foram relidos. O estado canônico vence a
inferência anterior: `claude-mem@claude-mem-local` fica `enabled=false` no Codex e o fallback direto
de `UserPromptSubmit` fica comentado durante a avaliação isolada do AI-Memory; no Claude Code o
claude-mem permanece ligado. `main` e `origin/main` estão no commit limpo `d798248`. O pedido atual
é somente reinstalar os caches Orquestra `0.27.2` a partir dessa fonte commitada e repetir
`verify_installed_cache.py` nos hosts Claude e Codex. Não religar o claude-mem no Codex, não
descomentar o fallback e não criar commit, push, publicação ou chat novo. Checkpoint verificado;
execução continua.

**Fechamento do bloco — 2026-09-07, publicado e com os caches sincronizados.** O dono autorizou o
commit e o push: `d798248` em `origin/main`, 21 arquivos, as duas frentes num commit só porque
tocam os mesmos arquivos. A sessão Codex leu o aviso, desfez a própria reversão do `T-074` e
sincronizou os caches `0.27.2` dos dois hosts com a fonte commitada.

**A conferência independente do lint pagou o custo dela.** A sessão paralela reportou "lint verde";
a repetição aqui mostrou vermelho — divergência **diferente** da anterior. A antiga
(`bytes:commands/checkpoint.md`) estava mesmo resolvida; a nova era `missing:scripts/__pycache__`,
artefato de bytecode da véspera na fonte, ausente (corretamente) nos caches. Virou `T-082`, com a
causa raiz registrada em `_notas-de-cards.md`: a guarda `sys.dont_write_bytecode` do lint impede
**gerar**, não **comparar**, e `verify_installed_cache.py` não filtra bytecode. Paliativo aplicado.

**Estado do claude-mem, canônico e conferido nesta janela:** `enabled = false` no Codex, fallback
`UserPromptSubmit` do `config.toml` comentado, nota inline ao lado da chave para a próxima
auditoria não reverter; ligado no Claude Code. O AI-Memory segue nos seis eventos do Codex, agora
como camada única — que é a condição para o `T-078` medir alguma coisa.

## ⏭️ RETOMAR AQUI

**O `T-075` continua em `[?]`, não fechado.** Falta a prova do pool de três — observar uma quarta
sessão real assumir vaga sem criar chat sintético — e a confirmação do dono usando o produto.

**Espera o dono:** `T-074` (`[?]`) usar o Codex 1–2 semanas com AI-Memory sozinho e dizer se a
captura serve; `T-065` (`[!]`) decidir `AGENTS.md`/`CLAUDE.md`, linha a linha, nada cortado sem ele
ver. **Não religar o claude-mem no Codex** enquanto o `T-078` não tiver resposta.

**Cards prontos para planejar, nenhum começado:** `T-081` (modo derivado para filtrar tipo sem
mexer no vocabulário do observer) e `T-082` (bytecode na allowlist do comparador, não exclusão ad
hoc). Nada pendente de commit nesta frente.

### Checkpoint de recuperação — 2026-09-07, prova natural do pool 3

A pendência técnica final do `T-075` foi encontrada nos logs do próprio restart autorizado, sem
criar chat sintético. Em 2026-09-06 às 22:14:27–22:14:33, as sessões reais `511`, `495` e `519`
ocuparam os três processos SDK. Às 22:14:45, a quarta sessão real (`480`, projeto
`Oss - Agente Pessoal`) entrou em espera com a mensagem literal `Pool limit reached (3/3), waiting
for slot...`. A sessão `519` terminou e liberou a vaga às 22:15:10.894; a query SDK da `480`
começou às 22:15:10.906 — 12 ms depois — e capturou `memory_session_id` às 22:15:11.211.

Isso comprova limite de três, espera da quarta sessão e substituição imediata após liberação. O
`T-075` permanece em `[?]` somente porque commit, testes e telemetria não substituem a validação
prática do dono. `T-074` também permanece `[?]`: sua janela de AI-Memory sozinho começou em
2026-09-07 e precisa de 1–2 semanas reais; não religar o claude-mem no Codex antes da avaliação.
