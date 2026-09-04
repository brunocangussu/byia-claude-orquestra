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

## ⏭️ RETOMAR AQUI

**Estado:** `T-072` e `T-073` implementados e em VALIDATE. `T-074` medido, instalado no Codex, mas
**com recomendação de não ligar ainda**. `T-075` criado no backlog. Gates verdes: 215 testes ·
`validate` ✔ · lint ✓. **Versão 0.26.0 bumpada, NADA commitado nem publicado.**

### A primeira coisa a fazer na sessão nova (30 segundos)

O claude-mem estava travado há 22 h. A sessão nova deve nascer sem o conflito — **confirme**:

```
python3 -c "import sqlite3,os,datetime;c=sqlite3.connect(os.path.expanduser('~/.claude-mem/claude-mem.db'));r=c.execute('select max(created_at_epoch) from observations').fetchone()[0];print(datetime.datetime.fromtimestamp(r/1000))"
```

Se a data for **de agora**, destravou. Se ainda for `02/09 00:34`, o contorno não funcionou e o bug
é mais fundo que "sessão marcada como completa" — reabrir a investigação pelo `observer-health.json`.

### O que espera o dono

| Card | O que falta |
|---|---|
| `T-072` `T-073` | **teste conversacional:** dizer *"lembra quando a gente…"* sobre algo que não está na wiki e ver se a busca do claude-mem é de fato consultada **depois** dela |
| `T-064` `T-056` | validação em uso |
| `T-074` | decidir se remove o claude-mem do Codex por ora (`codex plugin remove claude-mem@claude-mem-local`) |
| `T-065` | aplicar a config da máquina — **agora é seguro**, o `T-073` ligou a busca |
| `T-075` | **próximo a planejar** — é o pedido explícito do dono nesta janela |
| — | `AGENTS.md`/`CLAUDE.md`: pendente, o dono não decidiu. **Nada será cortado sem ele ver linha a linha** |

### O que NÃO re-litigar

- Autocompactação: **recusada com motivo** (`_stack.md`). Checkpoint + `/clear` já resolve melhor.
- `codebase-memory` + `serena`: **ficam os dois** (~570 tok/sessão juntos).
- Caveman: **nunca esteve instalado**.
- claude-mem: **fica, com papel de rede de segurança**. Custo real 2,8k/sessão, não 12,1k.
- Teto de card: **240 bytes**, decidido com o dono. Não voltar a 200.

### O contexto do `T-075`, para planejar sem reler tudo

O dono pediu, com estas palavras: *"instalar alguma coisa no orquestra que ajude a detectar esse
tipo de erro, para não ficar eternamente travado"*. O caso concreto está na seção "O incidente de
02/09" acima. O desenho tem que respeitar três coisas aprendidas:

1. **Health/liveness não serve** — o worker respondeu `ok` durante as 22 h paradas. O sinal correto
   é o **carimbo do que foi gravado** (`max(created_at_epoch)`), comparado com "houve trabalho no
   período".
2. **Onde encaixa:** `/orq:stack --verificar` já é o diagnóstico de ferramental ("o revisor sumiu",
   "a statusline está muda") — é o lar natural. O `/orq:checkpoint` é o segundo candidato, por ser
   onde o bloco fecha.
3. **Genérico, não específico do claude-mem** — o plugin é provider-neutral. A checagem deve ser
   "a memória de sessão declarada como Ativa no `_stack.md` gravou algo desde que começamos?", não
   "o claude-mem está ok?".

⚠️ **O dono levantou trocar por memória externa (SuperMemory ou outra).** Contraponto registrado:
o SuperMemory saiu no `T-037` por **falha de conexão recorrente** — mesma classe de problema, e
externo ainda adiciona rede como ponto de falha. E o que segurou estas 22 h foi a **wiki**: nada se
perdeu. O problema não é onde a memória mora; é a falha ser **silenciosa**. Se ele insistir, é
decisão dele — mas leve o dado antes.
