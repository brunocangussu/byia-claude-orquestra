# Elenco — qual LLM toca cada papel

> **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
> O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste papel a papel com
> `/orq:elenco <papel> <modelo>`, ou troque o **time inteiro** com `/orq:elenco perfil <nome>` —
> ou fale naturalmente: *"quero o Fable planejando"*, *"tô com pouco crédito"*, *"modo economia"*.

**Perfil ativo:** `padrao` — desde 2026-07-28, sem desvio.
*(Trocar o perfil reescreve a tabela "Papéis" abaixo e vale a partir do **próximo spawn, em todas
as janelas** — crédito é da conta, não da frente. Agente já em execução termina no modelo antigo;
não se refaz nada. Ajuste papel a papel depois da troca é permitido: registre nesta linha como
desvio — ex.: `economia · desvio: planner→fable`.)*

## Papéis (tabela ativa — é ESTA que os comandos leem)

| Papel | Modelo | Por quê |
|---|---|---|
| `manager` | *sessão principal* | definido pelo `/model` — **não é spawn, não se configura aqui** |
| `planner` | `fable` | achar causa raiz e desenhar solução é o trabalho mais difícil — **escolha do dono em 2026-07-28** |
| `implementer` | `sonnet` | executar plano já aprovado é trabalho dirigido — **escolha do dono em 2026-07-28** |
| `reviewer` | `opus` | revisão adversarial exige raciocínio forte |
| `docs` | `sonnet` | escrita objetiva sobre código já pronto |
| `scout` | `sonnet` | leitura ampla e barata |

Valores aceitos: `opus` · `sonnet` · `haiku` · `fable` · `inherit` · ou um id específico
(`claude-opus-5`).

## Revisores externos

| Revisor | Estado | Config |
|---|---|---|
| codex | **ativo** | `codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh -s read-only "<briefing>" < /dev/null` · CLI em `/usr/local/bin/codex` |
| kimi | **ativo** | `KIMI=$(command -v kimi \|\| echo "$HOME/.kimi-code/bin/kimi")` então `"$KIMI" -p "<briefing>" --output-format text < /dev/null` · v0.29.2, OAuth · symlink em `~/.local/bin/kimi` criado em 2026-07-28 |

**Os dois exigem `< /dev/null`** — sem TTY eles bloqueiam lendo stdin e travam até o timeout.
**Nenhum dos dois recebe dado sensível** (ver a regra em `/orq:revisar`, passo 1b).

O Kimi **não tem flag de sandbox**. Não passar `-y`/`--yolo` nem `--auto`; reforçar "não edite
arquivo" no prompt. Garantia dura só em worktree descartável.

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

Revisores externos: codex **ativo** · kimi **ativo**. Painel completo em card normal; `--rapido`
em card pequeno.

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

Revisores externos: codex **ativo** · kimi **ativo** — e `--rapido` (só o interno) **deixa de ser
recomendado**: o interno é justamente o revisor rebaixado; em card pequeno, some pelo menos um
externo.

**O que se perde neste perfil — dito com todas as letras:**
- plano mais raso: card de **alto risco não se planeja em economia** — ou espera o crédito voltar,
  ou o dono aceita o risco por escrito no card;
- reconciliação mais fraca: quem desempata o painel é o reviewer interno, agora menor;
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
desperdício. **Exceção: no perfil `economia`, ver a nota do preset.**
