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
