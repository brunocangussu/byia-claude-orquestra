# Elenco — qual LLM toca cada papel

> **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
> O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste papel a papel com
> `/orq:elenco <papel> <modelo>`, ou troque o **time inteiro** com `/orq:elenco perfil <nome>` —
> ou fale naturalmente: *"quero o Fable planejando"*, *"tô com pouco crédito"*, *"modo economia"*.

> **Este arquivo vale nos três hosts (Claude, Codex, Kimi) — mas nem toda seção vale igual em
> todos.** A tabela `## Papéis`, a linha `Perfil ativo`, a lista `Valores aceitos` e a seção
> `## Perfis` (perfis de crédito, `padrao`/`economia`), logo abaixo, são o **estado do host
> Claude**. Rodando noutro host, seu time é a tabela do **SEU** host em `## Times por host` —
> **resolvido na leitura, sem ativação** — `## Times por host` não é preset ativável, então nenhum
> comando o reescreve e nenhuma janela troca o time de outra por ali. **O que ainda escreve neste
> arquivo é o `/orq:elenco`, e ele só pode escrever a tabela do host Claude** (`## Papéis`,
> `Perfil ativo`, `## Perfis`). Rodando noutro host, **não use o comando**: mudar o time é edição
> manual desta seção, com o dono — usá-lo ali reescreveria o time do Claude no meio de uma janela
> Claude paralela.

**Perfil ativo:** `padrao` — desde 2026-07-28, sem desvio.
*(Trocar o perfil reescreve a tabela "Papéis" abaixo e vale a partir do **próximo spawn, em todas
as janelas** — crédito é da conta, não da frente. Agente já em execução termina no modelo antigo;
não se refaz nada. Ajuste papel a papel que diverge do preset ativo — inclusive com `padrao`
ativo — vira `padrao · desvio: papel→modelo`; devolvido ao preset, remove-se o desvio. Ver passo 3
de "Com argumento — ajustar" em `/orq:elenco`.)*

## Papéis (tabela ativa — é ESTA que os comandos leem)

| Papel | Modelo | Por quê |
|---|---|---|
| `manager` | *sessão principal* | definido pelo `/model` — **não é spawn, não se configura aqui** |
| `planner` | `fable` | achar causa raiz e desenhar solução é o trabalho mais difícil — **escolha do dono em 2026-07-28** |
| `implementer` | `sonnet` | executar plano já aprovado é trabalho dirigido — **escolha do dono em 2026-07-28** |
| `reviewer` | `opus` | revisão adversarial exige raciocínio forte |
| `docs` | `sonnet` | escrita objetiva sobre código já pronto |
| `scout` | `sonnet` | leitura ampla e barata |

Valores aceitos **na tabela ativa do host Claude**: `opus` · `sonnet` · `haiku` · `fable` ·
`inherit` · ou um id específico (`claude-opus-5`). Modelos de outros vendors (`gpt-5.6-sol`,
`kimi-code/k3`, ...) existem em `## Times por host` e na `## Matriz de invocação` — pô-los num
papel **desta** tabela é o `T-021`, ainda não decidido; até lá, este arquivo não os aceita aqui.

## Revisores externos

Regras, cada uma escrita 1×:

- **Nunca dependa de default de config de terceiro** — declare o modelo aqui, não confie no que o
  binário do vendor assume sozinho. Foi assim que o painel rodou `kimi-code/k3` por acidente em
  2026-08-05: o `default_model` do `~/.kimi-code/config.toml` decidiu por omissão.
- **O vendor do host nunca é externo de si mesmo.** Rodando noutro host, pule a linha do SEU
  vendor — seu painel fresco (mesmo modelo, sessão nova) entra pela `## Matriz de invocação`, não
  por aqui.
- **Toda invocação por CLI exige `< /dev/null`** — sem TTY, os três CLIs (Codex, Kimi e o
  `claude -p` cross-vendor) bloqueiam lendo stdin e travam até o timeout.

| Revisor | Estado | Config |
|---|---|---|
| codex | **ativo** | binário `/usr/local/bin/codex` (`codex` no PATH) · modelo `gpt-5.6-sol` @ `xhigh` · comando completo: ver **Matriz de invocação** |
| kimi | **ativo** | `KIMI=$(command -v kimi \|\| echo "$HOME/.kimi-code/bin/kimi")` · modelo `kimi-code/k3` · v0.29.2, OAuth, symlink em `~/.local/bin/kimi` (2026-07-28) · comando completo: ver **Matriz de invocação** |

**Nenhum dos dois recebe dado sensível** (ver a regra em `/orq:revisar`, passo 1b).

O Kimi **não tem flag de sandbox**. Não passar `-y`/`--yolo` nem `--auto`; reforçar "não edite
arquivo" no prompt. Garantia dura só em worktree descartável.

**Não há linha `claude` nesta tabela — de propósito:** o catch-all do `revisar.md` dispara tudo que
estiver "ativo" aqui, e uma linha `claude` faria o host Claude spawnar um segundo revisor Anthropic
via `claude -p` — que não lê arquivos sozinho. O caminho do `opus` de fora, em host que não é
Claude, é outro: time do host (`## Times por host`) → papel `reviewer` = `opus` → célula
Anthropic×host da `## Matriz de invocação`.

**Honestidade sobre o interno, dita com todas as letras (decisão do dono, 2026-08-05):** o papel
`reviewer` (`opus`, nativo no host Claude) **fica** como reconciliador do painel, mas **não conta
como "outra LLM"** para a diversidade que os dois revisores acima entregam — ele roda no mesmo
vendor do host. A diversidade real, no host Claude, vem só desta tabela (codex + kimi).

## Matriz de invocação

**Origem:** a regra que gera esta tabela mora na skill `orq` (`SKILL.md`, parágrafo "Onde houver
equivalente…"), instalada nos três hosts pela 0.18.0. **Aqui moram só os templates** — esta seção
não reescreve a regra, materializa-a.

**Ordem das flags — regra por CLI, não generalizável** (a mesma família de erro derrubou o painel
duas vezes em 2026-08-05, por causas opostas — ver `gotchas.md`):
- **`claude`:** prompt **antes** das flags — a `--tools` é variádica e engole o que vem depois dela.
- **`kimi`:** configuração primeiro, `-p` **por último** — o `-p` aceita valor, e com o `-m` vindo
  depois dele o Kimi consome o nome do modelo como se fosse o próprio briefing: não roda e devolve
  saída vazia em silêncio.
- **`codex`:** prompt posicional no fim (`codex exec ... "<briefing>"`) — ordem já em uso no painel.

**`< /dev/null` em TODA invocação por CLI** — sem TTY, os três bloqueiam lendo stdin e travam até
o timeout.

**Briefing:** `codex exec` e `kimi` **leem o repositório sozinhos** → isolamento em worktree/clone
descartável (nunca diretório vazio — repo ausente faz o briefing explodir; nunca o repo vivo —
dano sem contenção) + briefing curto + `git add -N .` antes de gerar o patch, para arquivo novo
não sumir do diff. `claude -p` invocado de dentro de outro agente **não lê arquivos** → o briefing
carrega o conteúdo **verbatim, numerado por linha**; o parecer é sobre o texto colado, e quem
reconcilia declara essa natureza.

**Saída conferida antes de virar parecer** (tamanho + formato) — 51 bytes não é parecer, é revisor
que não rodou.

**Procedência por célula:** `comprovado` (testado de ponta a ponta) · `observado 1×` (funcionou
uma vez, não repetido) · `não testado`.

| Vendor do modelo | host Claude | host Codex | host Kimi |
|---|---|---|---|
| **Anthropic** | spawn nativo (Task + `model:`) — comprovado | `claude -p '<briefing COM conteúdo verbatim numerado>' --model opus --permission-mode plan --tools '' --setting-sources '' --disable-slash-commands --no-session-persistence < /dev/null` — flags byte-idênticas ao `gotchas.md`; observado 1×; **não lê arquivos**; escrita: **não testado — e fora do desenho (regra do dono)** | idem coluna Codex — não testado |
| **OpenAI** | `codex exec -m gpt-5.6-sol -c model_reasoning_effort=<e> -s read-only "<briefing>" < /dev/null` — comprovado no painel; escrita cross-vendor: fora do desenho (regra do dono) | nativo: `spawn_agent` com modelo+effort por filho — observado 1×; `-m gpt-5.6-terra` aceito — **comprovado por chamada real 2026-08-05** | como coluna Claude — não testado |
| **Moonshot** | `"$KIMI" -m kimi-code/k3 --output-format text -p "<briefing>" < /dev/null` — **forma segura do `gotchas.md`: `-m` antes, `-p` por último**; comprovado no painel (a ordem inversa, `-m` depois do `-p`, NÃO roda) | idem — observado 1× | nativo: sub-agent, ou CLI para contexto limpo — roteamento comprovado vivo |

## Times por host

**Os times abaixo não são perfis.** Nenhum comando os ativa — `/orq:elenco perfil <nome>` só lê a
seção `## Perfis`, mais abaixo, e o nome de um time de host ali cai sozinho em "perfil
inexistente" (`elenco.md:59-60`). Cada host resolve o próprio time **na leitura** desta seção, sem
escrever nada e sem tocar no `## Papéis`/`Perfil ativo` de ninguém — é assim que uma janela Codex e
uma janela Claude convivem no mesmo repositório sem uma pisar no time da outra.

**Princípios, escritos 1× — valem para os dois times abaixo:**

1. **Regra do dono:** manager, planner e implementer sempre no modelo principal do host; só o
   revisor vem de fora.
2. **Revisor de fora é `opus`** quando o host não é Claude (decisão 10) — via a forma-que-funcionou:
   parecer sobre conteúdo verbatim, e o reconciliador declara essa natureza (`gotchas.md`,
   2026-08-05).
3. **O painel fecha os três vendors** — o do host por mecanismo nativo fresco (diagonal da
   Matriz), os outros dois por CLI.
4. **Docs e scout seguem o vendor do host** — derivado da regra 1 (papel de leitura autônoma fica
   na assinatura principal); composição confirmada pelo dono junto com os times.

### Host Codex

Motor: a sessão Codex (prosa — não é linha da tabela, para não sobrescrever o `manager`, como já
é hoje no host Claude).

| Papel | Modelo | Por quê |
|---|---|---|
| planner | `gpt-5.6-sol@xhigh` | verbatim do dono (2026-08-05) |
| implementer | `gpt-5.6-terra` | verbatim do dono (2026-08-05); existência confirmada por chamada real hoje; effort: da doc, no smoke |
| reviewer | `opus` | decisão 10; template na célula Anthropic×Codex da Matriz |
| docs | `gpt-5.6-sol@low` | princípio 4 — escrita objetiva, effort mínimo |
| scout | `gpt-5.6-sol@low` | verbatim do dono |

Painel: derivação do princípio 3 — sem modelos re-declarados aqui; modelos na Config dos
Revisores externos, templates na Matriz.

### Host Kimi

Motor: `kimi-code/k3` (hoje é acidente do `default_model` de config de terceiro; o arquivo o
registra aqui como **escolha**; editar `~/.kimi-code/config.toml` só com o dono, no smoke).

| Papel | Modelo | Por quê |
|---|---|---|
| planner | `kimi-code/k3` | topo de raciocínio do vendor; princípio 1 |
| implementer | `kimi-code/kimi-for-coding` | coding-tuned; **condicionado**: hook `PreToolUse` testado vivo (decisão 4) + worktree (decisão 8). **Sem fallback cross-vendor** — a regra do dono o proíbe: hook reprovado → o host Kimi **não implementa**, o card de escrita fica com outro host |
| reviewer | `opus` | decisão 10 |
| docs | `kimi-code/kimi-for-coding-highspeed` | princípio 4 (custo relativo não medido — smoke valida) |
| scout | `kimi-code/kimi-for-coding-highspeed` | idem |

`kimi-code/k3-256k` documentado como saída para briefing/patch que estoure contexto (briefing
maior em revisor isolado força mais tamanho).

## Custo

Cada papel cobra a conta do vendor do SEU modelo. Pela regra do dono, isso significa: tudo cobra a
conta do host — motor, trio, docs, scout e o painel fresco — exceto o revisor `opus` (gasto
deliberado, decisão 10) e os dois revisores de fora do painel. Trocar de host move o bloco inteiro
para a outra assinatura; o evento é a troca de assinatura (ciclo de mercado).

O preset `economia`, na seção `## Perfis` abaixo, é a variante de crédito curto **do host Claude**
(pressupõe host Claude — a anotação no preset aponta para cá). Equivalente noutro host nasce sob
demanda, quando o dono pedir.

## Perfis — times nomeados por contexto de crédito

Perfil é um preset do time inteiro. Ativar = reescrever a tabela "Papéis" a partir do preset e
atualizar a linha "Perfil ativo". Os consumidores (`plan-next`, `implement-next`, `revisar`,
`stack`) não mudam: continuam lendo a tabela ativa.

**Frases de gatilho — atestadas vs. paráfrase** (medido no transcript de 2026-07-29, não
imaginado): *"final do ciclo semanal"*, *"pouco crédito"* e *"acabando os créditos"* são falas
verbatim do dono. *"Modo economia"* é **paráfrase** — nasceu do card, não da fala dele — mas vira o
nome de apelo do perfil porque ele reconhece e usa a frase depois de lida. Não existe frase
atestada para "voltar": a reversão não é um gatilho fixo à espera de adivinhação — o Manager diz,
no próprio anúncio da troca, como reverter (ex.: "quando o crédito voltar, é só pedir"), e o pedido
de volta é reconhecido como o pedido de mudança que é, na hora em que ele vier.

**O `manager` não entra em perfil nenhum** — é a sessão principal, definida pelo `/model` do dono.
Ao ativar `economia`, sugerir em uma linha que ele avalie trocar o `/model` também: é onde mora o
maior consumo, e só ele troca.

### `padrao` — o time titular (vale por default — pedido do dono em 2026-07-29)

| Papel | Modelo | Por quê |
|---|---|---|
| planner | fable | achar causa raiz e desenhar solução é o trabalho mais difícil |
| implementer | sonnet | executar plano já aprovado é trabalho dirigido |
| reviewer | opus | revisão adversarial exige raciocínio forte |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

Revisores externos: codex **ativo** · kimi **ativo** — estado informativo, o perfil não aplica isto
(ver passo 2 de "Com argumento `perfil <nome>`" em `/orq:elenco`); vale o que está de fato
registrado acima. Painel completo em card normal; `--rapido` em card pequeno.

### `economia` — fim do ciclo semanal, crédito Claude curto

Composição na palavra do dono (2026-07-29): *"diminuo o planejamento com o Fable e faço só com o
Opus; uso mais as outras, o Codex e o Kimi"*.

| Papel | Modelo | Por quê |
|---|---|---|
| planner | opus | escolha verbatim do dono para este contexto |
| implementer | sonnet | já era o econômico |
| reviewer | sonnet | o peso da revisão desloca para o painel externo, que não gasta crédito Claude |
| docs | haiku | escrita objetiva; rebaixar aqui custa pouco |
| scout | haiku | leitura ampla e barata |

Revisores externos: codex **ativo** · kimi **ativo** — mesmo estado informativo do preset `padrao`,
não aplicado pelo perfil (ver passo 2 de "Com argumento `perfil <nome>`" em `/orq:elenco`). Quem
decide o painel mínimo do `--rapido` é o `/orq:revisar` — regra lá.

**O que se perde neste perfil — dito com todas as letras:**
- reconciliação interna mais fraca: quem desempata o painel é o reviewer, agora rebaixado — **com
  externo ativo**, o desempate desloca para o painel externo (Codex/Kimi) — **sem externo ativo, não
  há pra onde deslocar**: o reviewer rebaixado decide sozinho;
- mais peso no Kimi = mais exposição — ele não tem sandbox (`T-019`); worktree descartável vira
  **mais** obrigatório, não menos;
- Codex e Kimi são read-only: implementação continua queimando crédito Claude — o perfil **reduz,
  não zera**;
- o Manager não muda: o maior consumo é a sessão principal, e só o `/model` do dono a troca.

Quando o `T-021` (motor alternativo) fechar, este preset é o lugar de registrar o que mais o Codex
e o Kimi passam a carregar (ex.: pré-parecer read-only no planejamento). Até lá, não prometer.

## Por que o painel importa neste projeto

O produto aqui são **instruções**, não código. Onde dois modelos divergem sobre o que uma instrução
significa, **a divergência é o achado** — é sinal de ambiguidade real no texto, que um leitor futuro
também vai encontrar. O Codex tem contexto adicional: foi ele quem auditou a arquitetura original e
produziu o parecer que virou o roadmap.

Com **três** revisores (Claude · Codex · Kimi) a reconciliação fica mais forte: "confirmado por 2+"
deixa de ser unanimidade e vira **maioria**, o que separa melhor o achado sólido do palpite de um
modelo só. Três fornecedores distintos (Anthropic · OpenAI · Moonshot) erram de formas menos
correlacionadas que duas instâncias do mesmo.

Em card pequeno e de baixo risco, `--rapido` (só o revisor interno). Painel em mudança trivial é
desperdício. Quem decide o painel mínimo (inclusive no perfil `economia`) é o `/orq:revisar` — regra
lá.
