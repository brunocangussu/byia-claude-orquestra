---
description: Mostra e ajusta o elenco — qual LLM toca cada papel (planner, implementer, reviewer, docs, scout) e quais revisores externos estão ativos neste projeto, e perfis nomeados para trocar o time inteiro
argument-hint: "[papel modelo | perfil nome — ex: 'planner fable' | 'codex off' | 'perfil economia']"
---

O **elenco** define qual modelo interpreta cada papel **neste projeto**. Fica em
`memory/wiki/_elenco.md` e vale como override no momento do spawn — o `model:` do arquivo do agente
é só o padrão de fábrica.

## Sem argumento — mostrar

Leia `memory/wiki/_elenco.md` e apresente a escalação atual em tabela (papel · modelo · por quê),
mais os revisores externos ativos. Se o arquivo não existir, mostre os **padrões de fábrica** e
ofereça criá-lo.

Feche sugerindo, em uma linha, o que costuma valer a pena ajustar (ex.: *"plano difícil rende mais
com um modelo mais forte no planner"*).

## Com argumento — ajustar

`$ARGUMENTS` no formato `<papel> <valor>`. Exemplos: `planner fable` · `reviewer opus` ·
`implementer inherit` · `codex off` · `codex xhigh`.

**`$ARGUMENTS` começando com `perfil ` (ex.: `perfil economia`) não é papel** — vá direto para a
seção "Com argumento `perfil <nome>` — trocar o time inteiro" abaixo, em vez desta.

1. Valide o papel: `manager` · `planner` · `implementer` · `reviewer` · `docs` · `scout`, ou um
   revisor externo (`codex`, ou outro registrado).
2. Valide o modelo: `opus` · `sonnet` · `haiku` · `fable` · `inherit`, ou um id específico
   (`claude-opus-5`). Valor desconhecido → **pergunte** em vez de gravar errado.
3. Grave em `memory/wiki/_elenco.md` (crie a partir do modelo abaixo se não existir). **Sem seção
   "Perfis" no arquivo (instância anterior à 0.16.0): semeie a seção ANTES de gravar este ajuste**,
   pela mesma regra do passo 0 de `perfil <nome>` abaixo — avise em uma linha que semeou. **Tabela
   ativa sem o heading `## Papéis` (mesmo arquivo legado): regrave-o também, pela mesma regra do
   passo 2 de `perfil <nome>` abaixo**, antes de gravar o ajuste. Semear
   **depois** do ajuste faria o valor recém-alterado virar baseline permanente do `padrao`, e a
   divergência nunca mais apareceria como desvio. Só então: compare o valor novo ao preset **ativo**
   na seção Perfis — inclusive quando o ativo é `padrao`, que não é estado-zero, é um preset como
   outro qualquer: divergiu → registre o desvio na linha **Perfil ativo**, no formato da linha do
   template; voltou a bater com o preset → **remova** o desvio dessa linha. Desvio vale só para
   papéis da tabela `## Papéis`; estado de revisor externo não é desvio e nenhum perfil o toca (passo
   2 de `perfil <nome>` abaixo).
4. Confirme o que mudou e **a partir de quando vale** (próximo spawn — não afeta agente em execução).

**`manager` é caso especial:** é a sessão principal, definida pelo `/model` do Claude Code — não dá
pra trocar por aqui. Se ele pedir, explique e sugira o `/model`.

## Com argumento `perfil <nome>` — trocar o time inteiro

`$ARGUMENTS` no formato `perfil <nome>`. Exemplos: `perfil economia` · `perfil padrao`.

0. **Seção "Perfis" ausente** (arquivo gerado antes da 0.16.0)? Semeie antes de aplicar, e avise em
   uma linha que semeou: preset `padrao` = a **tabela ativa atual** do arquivo, sem a linha
   `manager` (ela é o titular deste projeto — semear da fábrica devolveria, em silêncio, um time que
   o projeto nunca usou); preset `economia` = o time de fábrica (o projeto nunca teve um). Grave a
   seção **Perfis** com os dois presets antes de seguir para o passo 1. Arquivo sem a linha **Perfil
   ativo**? Grave-a também — `padrao`, com a data de hoje, sem desvio — no formato da linha do
   template.
1. Leia a seção **Perfis** do `_elenco.md`. Perfil inexistente → liste os que existem e
   **pergunte**; não crie perfil novo sem pedido explícito.
2. **Localize a tabela ativa:** é a que está sob o heading `## Papéis`. Arquivo de versão anterior
   sem esse heading → é a **primeira tabela** do arquivo — regrave acrescentando o heading (é a
   mesma tabela, só ainda sem marcação). Reescreva-a a partir do preset (modelos e "Por quê") e
   atualize a linha **Perfil ativo** — nome + data, zerando desvios anteriores, no formato da linha
   do template. **A linha `manager` não faz parte de preset nenhum — preserve-a como está.** Os
   presets têm 5 linhas (sem `manager`); a tabela ativa tem 6. Reescrever "as 5 linhas do preset"
   apagaria o `manager` da tabela, e `perfil padrao` não o devolve — é perda permanente. **O estado
   dos revisores externos (seção "Revisores externos", fora da tabela `## Papéis`) também não é
   preset — não aplique o que o preset declarar; preserve o que está registrado agora**, pela mesma
   razão do `manager`: é o que está de fato instalado e ativo no projeto, não uma escolha do time. A
   linha "Revisores externos" dentro de cada preset é só informativa (estado de fábrica, de leitura).
3. Confirme mostrando o time novo **e o que se perde** — resuma a nota do preset em até 3 linhas.
   Havia desvio registrado na linha Perfil ativo? **Diga em uma linha que ele foi descartado** — sem
   isso, o registro só muda onde a escolha some, não o silêncio. **Anuncie, não pergunte**, e diga
   **na hora como reverter** (ex.: "quando o crédito voltar, é só dizer" ou `/orq:elenco perfil
   padrao`) — não invente nem espere que ele decore uma frase fixa de volta; o pedido de reverter é
   reconhecido como o pedido de mudança que é, na hora em que ele vier.
4. A troca vale a partir do **próximo spawn, em todas as janelas** — crédito é da conta, não da
   frente. Agente já em execução termina no modelo antigo; não refaça nada. Se houver card `[~]`
   no board, diga em uma linha que ele termina com elenco misto, e que isso é esperado.
5. **`manager` não muda por perfil.** Ao ativar um perfil de economia, sugira em uma linha que o
   dono avalie o `/model` da sessão — é onde mora o maior consumo, e só ele troca.

## Modelo do arquivo

```markdown
# Elenco — quem toca cada papel

## Papéis (a tabela ativa — é esta que os comandos leem)

| Papel | Modelo | Por quê |
|---|---|---|
| manager (sessão principal) | opus | coordena, decide, fala com o dono — definido pelo `/model` |
| planner | opus | achar causa raiz e desenhar solução é o trabalho mais difícil |
| implementer | inherit | segue o modelo da sessão |
| reviewer (interno) | opus | revisão adversarial exige raciocínio forte |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

**Perfil ativo:** `padrao` — desde <data de hoje>, sem desvio.
*(É o formato canônico da linha — a única vez que ele é definido. Ajuste papel a papel que diverge
do preset ativo — inclusive com `padrao` ativo — vira `padrao · desvio: papel→modelo`; devolvido ao
preset, remove-se o desvio. Ver passo 3 de "Com argumento — ajustar".)*

## Revisores externos
| Revisor | Estado | Config |
|---|---|---|
| codex | ativo | `--model gpt-5.6-sol --effort xhigh` (read-only) |
| kimi-k2 | inativo | registrar aqui quando houver CLI ou MCP |

## Perfis — times nomeados

Cada preset abaixo é uma tabela **literal e completa** — nunca uma referência a "a tabela acima".
É isso que permite voltar (`perfil padrao`) sem depender de memória: se `padrao` fosse só um ponteiro
para a tabela ativa, ativar `economia` reescreveria a tabela ativa e `padrao` passaria a apontar
para o próprio `economia` — o time titular sumiria do arquivo. `manager` e o estado dos revisores
externos (ativo/inativo) ficam fora dos dois presets: nenhum perfil os toca, e aplicar um preset na
tabela ativa **preserva a linha `manager` e a seção "Revisores externos"** como estão.

### `padrao` — o time titular

| Papel | Modelo | Por quê |
|---|---|---|
| planner | opus | achar causa raiz e desenhar solução é o trabalho mais difícil |
| implementer | inherit | segue o modelo da sessão |
| reviewer | opus | revisão adversarial exige raciocínio forte |
| docs | sonnet | escrita objetiva sobre código já pronto |
| scout | sonnet | leitura ampla e barata |

Revisores externos: `codex` ativo · `kimi-k2` inativo — estado de fábrica, informativo: o perfil não
aplica isto (ver passo 2 de "Com argumento `perfil <nome>`"), vale o que está de fato registrado.
Painel completo em card normal; `--rapido` em card pequeno.

### `economia` — crédito curto

| Papel | Modelo | Por quê |
|---|---|---|
| planner | opus | não rebaixado — um erro de plano custa a implementação inteira |
| implementer | sonnet | rebaixado um degrau — evita herdar Opus da sessão no perfil de economia |
| reviewer | sonnet | rebaixado um degrau — com externo ativo, o desempate desloca pra lá |
| docs | haiku | escrita objetiva; rebaixar aqui custa pouco |
| scout | haiku | leitura ampla e barata |

Revisores externos: `codex` ativo · `kimi-k2` inativo — mesmo estado de fábrica do preset `padrao`,
também informativo, não aplicado pelo perfil (ver passo 2 acima). Quem decide o painel mínimo do
`--rapido` é o `/orq:revisar` — regra lá.

**O que se perde — registre com todas as letras ao criar este perfil neste projeto:** reconciliação
interna mais fraca (quem desempata o painel é o reviewer, agora rebaixado); **com externo ativo**, o
desempate desloca para o painel externo — **sem externo ativo, não há pra onde deslocar**: o reviewer
rebaixado decide sozinho; mais peso em qualquer revisor sem sandbox. Ajuste os modelos e a nota à
realidade do projeto — os valores acima são ponto de partida, não contrato fixo.
```

## Como isso é aplicado

Ao spawnar um papel, os comandos (`plan-next`, `implement-next`, `revisar`, `init`) **leem o elenco**
e passam o modelo como override. Sem elenco, valem os padrões de fábrica dos arquivos em `agents/`.

## Orientação (quando ele pedir recomendação)

- **Planner e Reviewer** são onde modelo forte mais se paga: um erro de plano custa a implementação
  inteira; um review fraco deixa passar o que vai quebrar depois.
- **Docs e Scout** são leitura/escrita objetiva — modelo menor resolve e sai mais barato.
- **Implementer** costuma ir bem com `inherit` (acompanha o que você escolheu pra sessão).
- **Só Claude, sem GPT?** `codex off` e deixe o reviewer interno em `opus`. Você perde a diversidade
  de painel (dois modelos erram diferente), mas ganha simplicidade e um fornecedor só.
- Trocar modelo **não** troca a disciplina: as regras dos agentes valem igual.
- **Fim do ciclo de crédito?** `perfil economia` troca o time inteiro — e o preset diz, com todas as
  letras, o que se perde. `perfil padrao` desfaz.
