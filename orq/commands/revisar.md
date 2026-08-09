---
description: Painel de revisores independentes (Claude + Codex + Kimi, e outros configurados) sobre a mudança atual, com os achados reconciliados num parecer só
argument-hint: "[T-NNN | caminho | 'o que revisar'] [--rapido para painel mínimo — normalmente só o revisor interno]"
---

Rode uma **revisão por painel**: revisores independentes olham a mesma mudança **em paralelo**, e
você reconcilia os achados num parecer único.

Por que painel: revisores diferentes erram de formas diferentes. Um acha o bug de lógica, outro acha
o vazamento de escopo. O valor está na **interseção** (alta confiança) e na **divergência** (onde
vale investigar).

## 1. Definir o alvo
- `$ARGUMENTS` com `T-NNN` → o diff/escopo daquele card.
- Caminho ou descrição → aquilo.
- Vazio → as mudanças não commitadas (`git status` + `git diff`), ou o último commit se estiver limpo.

Monte o **briefing** uma vez (será o mesmo pra todos): o que mudou, por quê, o critério de aceite,
o que está **fora** de escopo, e as convenções do projeto. Sem briefing igual, os pareceres não são
comparáveis.

**Exija o MESMO formato de saída de todos** — sem isso a reconciliação vira leitura de prosa solta:

```
## BLOQUEADORES
- [arquivo:linha] problema — por que quebra — correção mínima   (ou "nenhum")
## RISCOS
- [arquivo:linha] risco — em que cenário aparece                 (ou "nenhum")
## VEREDITO
APROVADO | APROVADO_COM_RESSALVAS | REPROVADO
```

## 1b. ⛔ Antes de mandar QUALQUER coisa para fora

Revisor externo é **transferência de dados para terceiro** (OpenAI, Moonshot). Antes de montar o
briefing, **inspecione o que vai nele**:

**Nunca envie:** dado de paciente ou pessoal (PII), prontuário, credencial, token, chave, `.env`,
dump de banco com linhas reais.
**Pode enviar:** código, schema, arquitetura, infra, mensagem de erro sem payload.

Achou dado sensível no diff? **PARE e avise o dono** — não tente higienizar sozinho e seguir. O
revisor interno (`orq-reviewer`) roda no mesmo ambiente e **não** tem essa restrição: em mudança que
toca dado sensível, use `--rapido` e diga por quê.

## 2. Disparar os revisores EM PARALELO

**Leia `memory/wiki/_elenco.md` primeiro** — ele define o modelo do reviewer interno e **quais
revisores externos estão ativos**. **Sem elenco, valem os padrões de fábrica: reviewer `opus`,
Codex ativo e Kimi K3 ativo**; ausência de qualquer capacidade vira `PAINEL PARCIAL`, não exclusão
silenciosa do revisor.

Primeiro **identifique o host** e resolva o papel em `## Times por host`; depois use a célula da
`## Matriz de invocação`. O Manager que reconcilia não conta como parecer independente.

**Host Claude — Claude interno:** subagente `orq-reviewer` (read-only, adversarial), com o modelo do
papel `reviewer` do elenco.

> Isto só existe no host Claude (é spawn nativo). **No Host Kimi**, o membro Moonshot do próprio
> host entra pela célula-diagonal da `## Matriz de invocação`, em sessão nova. **Host Codex é exceção:**
> seu painel é exatamente Opus 5 + Kimi K3; o Manager OpenAI só reconcilia e não há
> terceiro parecer OpenAI pela diagonal.

> ⚠️ **Spawne o `orq-reviewer` SEM `name`.** Com `name` ele vira teammate endereçável e fica vivo em
> loop de *idle* em vez de devolver o parecer — o painel morre esperando. Sem nome, ele retorna o
> resultado normalmente. (Quebrou assim em 2026-07-26; ver `memory/gotchas.md`.)

**Host Codex — painel obrigatório Opus 5 + Kimi K3:** dispare em paralelo dois pareceres
independentes, ambos sobre o mesmo briefing sanitizado:

O briefing do Opus tem orçamento de **16 KiB = 16.384 bytes UTF-8 por lote, medidos depois da
sanitização**. Até esse limite, envie o pacote inteiro. Acima dele, divida por arquivo/hunk em lotes
independentes, repetindo em cada lote o objetivo, os critérios e o fora de escopo; cubra todos os
hunks e registre a cobertura. **Nunca corte bytes nem resuma em silêncio** para caber. Um lote
omitido ou que falhar torna a cobertura do Opus parcial.

```bash
# ORQ_PACKAGE_ROOT já foi resolvido pela skill para um caminho absoluto.
OPUS_RUNNER="<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py"
OPUS_OUT=$(printf '%s' "$OPUS_BRIEFING_SANITIZADO" | python3 "$OPUS_RUNNER")
OPUS_EXIT=$?
if [ "$OPUS_EXIT" -ne 0 ] || [ -z "$OPUS_OUT" ]; then
  echo "PAINEL PARCIAL: Opus ausente; preserve o diagnóstico do stderr"
fi

KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")
"$KIMI" -m kimi-code/k3 --output-format text -p "<briefing>" < /dev/null
```

O runner anuncia `OPUS_STARTED` imediatamente **no stderr** e aplica timeout de 240s. A validação
de tamanho ocorre antes do anúncio: `BRIEFING_TOO_LARGE` significa que nenhuma chamada começou;
redivida o lote e execute, sem contar isso como retry. O runner exige
`claude-opus-5` no `modelUsage` JSON e não imprime parecer em modelo errado, timeout, erro ou saída
vazia (`OPUS_EMPTY_RESULT`). `OPUS_EXIT != 0`, `OPUS_OUT` vazio ou qualquer lote incompleto →
**PAINEL PARCIAL** com o diagnóstico do stderr;
não faça retry automático após chamada iniciada, para não duplicar custo.

O Manager Codex reconcilia Opus 5 e `kimi-code/k3`; ele próprio não vira um terceiro parecer. Se um
não rodar, escreva **PAINEL PARCIAL**, nomeie o revisor ausente e a causa real: PATH, autenticação,
timeout, modelo indisponível ou saída vazia. Nunca anuncie painel completo com um único parecer.
Todo host que usar o alias `opus` como Opus 5 usa o mesmo runner e precisa verificar essa resolução
antes do parecer. Se ela não puder ser comprovada, trate Opus 5 como ausente e marque **PAINEL
PARCIAL**, sem trocar de modelo. A regra vale também no Host Kimi.

**Se o Codex estiver ATIVO no elenco e o host não for Codex** e a CLI existir (`codex` no PATH):
rode direto, read-only:

```bash
codex exec -m <modelo do elenco> -c model_reasoning_effort=<effort> -s read-only "<briefing>" < /dev/null
```

> ⚠️ **`< /dev/null` não é opcional.** Sem ele o `codex exec` fica bloqueado lendo stdin (não há TTY
> aqui), trava até o timeout e não produz nada — mesmo com o prompt passado como argumento. Com o
> stdin fechado responde em segundos.

Prompt **READ-ONLY explícito** ("não implemente nada, não edite arquivos"). Peça CONFIRMA/REFUTA por
afirmação + achados priorizados com `arquivo:linha` + cenário de falha concreto.

**Se o Kimi estiver ATIVO no elenco e o host não for Kimi:** rode a CLI direto, resolvendo o
binário com fallback e passando o modelo do elenco:

```bash
KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")
"$KIMI" -m <modelo do elenco> --output-format text -p "<briefing>" < /dev/null
```

> ⚠️ **Ordem das flags importa: `-m` antes, `-p` por último.** O `-p` aceita valor, então com o `-m`
> vindo depois dele o Kimi consome o nome do modelo como se fosse o próprio briefing — não roda e
> devolve saída vazia em silêncio (pago em 2026-08-05; ver `gotchas.md`). Confira o tamanho da saída
> antes de tratá-la como parecer.
>
> ⚠️ **O instalador do Kimi põe o binário em `~/.kimi-code/bin/` e adiciona ao `.zshrc`** — o que só
> vale em shell aberto **depois** da instalação. Uma sessão já em curso não enxerga, `which kimi`
> falha, e o painel vira silenciosamente um revisor a menos **enquanto o binário está lá, funcionando**.
> Por isso o fallback acima. (Uma sessão irmã concluiu "Kimi não instalado" exatamente assim, e ainda
> foi procurar no npm — onde ele nunca esteve: a distribuição é por `code.kimi.com`, não por pacote.)
>
> ⚠️ **Ele não tem flag de sandbox** como o `-s read-only` do Codex. **Não** passe `-y`/`--yolo` nem
> `--auto`: sem elas, em modo `-p`, ele não aplica mudança. Reforce no prompt: *"não edite arquivo
> nenhum, apenas relate"*. Se precisar de garantia dura, rode-o num worktree descartável.

**Outros revisores** marcados como **ativo** na seção "Revisores externos" do `_elenco.md`: `ativo`
é política habilitada, não capacidade comprovada; verifique CLI, autenticação, modelo e saída no
momento do parecer. No Host Codex, a composição obrigatória permanece exatamente Opus 5 + Kimi K3;
não acrescente a diagonal OpenAI. No Host Kimi, pule o externo Moonshot duplicado porque o parecer
fresco desse vendor já entrou pela diagonal da Matriz. Em outros hosts, siga a composição registrada.

**Revisor ativo no elenco que falhar** (binário ausente, timeout, saída vazia) → **diga ao dono que
o painel parcial perdeu aquele revisor**, nomeando quem faltou. Nunca apresente parecer de um revisor como se fosse a
interseção de vários: o valor do painel está em distinguir confirmado-por-dois de achado-por-um.

**Dado sensível no diff → a regra LGPD do passo 1b deste arquivo vence tudo, antes de qualquer outra
coisa**: rode só o revisor interno, mesmo rebaixado, dizendo por quê. Sem esta precedência na frente,
a saída "rebaixado + externo ativo" abaixo correria primeiro e mandaria dado sensível para fora.

Sem dado sensível, com `--rapido`: rode só o revisor interno **salvo se ele estiver rebaixado** —
modelo mais fraco que o do preset `padrao` do mesmo `_elenco.md` (ordem `haiku < sonnet < opus`;
`fable` sem ordem definida → trate como **não rebaixado**; `inherit` → compare com o modelo real da
sessão, não com o rótulo — é o caso em que o rótulo esconde o modelo, e é justamente o que esta regra
existe para pegar; arquivo sem seção Perfis → trate como **não rebaixado**, na dúvida). Rebaixado,
duas saídas, sem beco:

1. **há externo ativo** → o `--rapido` inclui **um** externo, mesmo assim mais barato que o painel
   completo;
2. **nenhum externo ativo** (projeto solo-Claude) → roda só o interno e **anuncia em uma linha que o
   painel está no mínimo** — não trave, não exija um revisor que não existe.

Quem decide o painel mínimo é sempre este comando — os demais consumidores do `--rapido` (
`/orq:implement-next`, o README do repositório do plugin, preset `economia`) não re-enunciam a
condição, só apontam para cá.

## 3. Reconciliar (o passo que dá o valor)

**Não despeje os pareceres um embaixo do outro.** Consolide:

- **Confirmado por 2+** → alta confiança, vai no topo.
- **Achado por só um** → mantenha, mas **verifique você mesmo no código** antes de repassar.
  Revisor sozinho erra; achado não verificado vira ruído e queima a confiança do painel.
- **Divergência** (um diz que quebra, outro diz que está certo) → **você desempata olhando o
  código** e explica qual está certo e por quê. Não deixe a contradição pro dono resolver.
- **Duplicata** → funda num item só, citando quem achou.

Descarte achado sem **cenário de falha concreto** (entrada → resultado errado) — ou marque
explicitamente como "opinião de estilo".

## 4. Entregar

- **Veredito:** aprovar · aprovar com correções · refazer.
- **Achados** ordenados por severidade: `arquivo:linha` · o defeito em uma frase · como falha na
  prática · quem apontou (Claude / Codex / …).
- **Roteiro de teste manual** — passos de usar o produto (vira o guia de validação do dono).
- **O que os revisores discordaram** e sua decisão.

Se nada relevante apareceu, diga em uma linha. **Não invente achado pra parecer útil.**

## Regras
- Revisor **não corrige** — quem implementou aplica. Você (Manager) roteia as correções.
- Máximo **2 rodadas** de correção+revisão; persistindo, escale pro dono.
- Nunca mande segredo/credencial no briefing de um revisor externo.
