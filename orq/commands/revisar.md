---
description: Parecer independente sobre a mudança atual — todo revisor é de um modelo do vendor OPOSTO ao do host (o titular e qualquer segundo parecer pedido pelo dono), com os achados auditados pelo Manager antes de virarem veredito
argument-hint: "[T-NNN | caminho | 'o que revisar'] [--rapido para briefing enxuto ao mesmo revisor titular]"
---

Rode uma **revisão independente**: um revisor lê a mudança sem ter escrito nada dela, devolve o
parecer, e você **audita cada achado contra o código** antes de repassar.

O revisor é **um só, e sempre do vendor oposto ao host** — host Claude é revisado por OpenAI, host
Codex é revisado por Anthropic. A razão de existir do revisor é ser independente de quem escreveu;
um revisor do mesmo vendor do host não entrega isso, por mais forte que seja o modelo.

## 1. Definir o alvo
- `$ARGUMENTS` com `T-NNN` → o diff/escopo daquele card.
- Caminho ou descrição → aquilo.
- Vazio → as mudanças não commitadas (`git status` + `git diff`), ou o último commit se estiver limpo.

Monte o **briefing**: o que mudou, por quê, o critério de aceite, o que está **fora** de escopo, e
as convenções do projeto. A disciplina do papel está em `agents/orq-reviewer.md` — ela é o conteúdo
do briefing, não um segundo parecer a spawnar.

**Exija este formato de saída** — sem ele a auditoria vira leitura de prosa solta:

```
## BLOQUEADORES
- [arquivo:linha] problema — por que quebra — correção mínima   (ou "nenhum")
## RISCOS
- [arquivo:linha] risco — em que cenário aparece                 (ou "nenhum")
## VEREDITO
APROVADO | APROVADO_COM_RESSALVAS | REPROVADO
```

## 1b. ⛔ Antes de mandar QUALQUER coisa para fora

O revisor titular é, por definição, **transferência de dados para terceiro** — do ponto de vista de
cada host, o vendor oposto é terceiro. Antes de montar o briefing, **inspecione o que vai nele**:

**Nunca envie:** dado de paciente ou pessoal (PII), prontuário, credencial, token, chave, `.env`,
dump de banco com linhas reais.
**Pode enviar:** código, schema, arquitetura, infra, mensagem de erro sem payload.

**Achou dado sensível no diff? PARE e avise o dono — e saiba o que isso significa: não haverá
revisor nenhum.** A regra LGPD impede o titular, e **não existe substituto**: spawnar um revisor do
mesmo vendor do host para "ter algum parecer" é proibido, porque devolveria a aparência de revisão
sem a independência que a justifica. O que resta é o **Manager auditando o diff ele mesmo** — o que
ele já faz no passo 3 — e **declarando** "sem revisão independente por restrição de dados". Isso não
é revisão degradada por falha: é ausência de revisor, nomeada, e o dono decide se segue assim.

Não tente higienizar sozinho e seguir.

## 2. Disparar o revisor titular

**O passo 1b vence tudo e já rodou:** dado sensível no diff encerra o assunto — não há revisor, e
nada deste passo se aplica. Só siga aqui com o briefing já inspecionado.

**Leia `memory/wiki/_elenco.md` primeiro.** **Sem elenco, vale o padrão de fábrica: reviewer único
do vendor oposto ao host** — as vias registradas em "Revisores externos" são capacidade, não
composição de painel. `ativo` ali é **política habilitada, não capacidade comprovada**, e as duas
se checam antes de disparar:

1. **Coluna `Estado` da via** — `inativo` significa que o dono **desligou** aquela transferência
   cross-vendor. Não dispare, nem "só desta vez": escreva **REVISÃO DEGRADADA — via desligada pelo
   dono** e siga a regra de titular indisponível abaixo. Não é falha, é política.
2. **Capacidade** — binário, autenticação, modelo e saída não vazia no momento do parecer.

Os dois diagnósticos são diferentes e o dono precisa saber qual dos dois aconteceu: "você desligou"
e "o binário não respondeu" pedem ações opostas.

Primeiro **identifique o host** e resolva a linha `reviewer` em `## Times por host`; depois use a
célula da `## Matriz de invocação`. O Manager que audita não conta como parecer independente.

**Host Claude — titular OpenAI pela CLI `codex`**, read-only:

```bash
codex exec -m <modelo do elenco> -c model_reasoning_effort=<effort> -s read-only "<briefing>" < /dev/null
```

> ⚠️ **`< /dev/null` não é opcional.** Sem ele o `codex exec` fica bloqueado lendo stdin (não há TTY
> aqui), trava até o timeout e não produz nada — mesmo com o prompt passado como argumento. Com o
> stdin fechado responde em segundos.

Prompt **READ-ONLY explícito** ("não implemente nada, não edite arquivos"). Peça CONFIRMA/REFUTA por
afirmação + achados priorizados com `arquivo:linha` + cenário de falha concreto.

**Host Codex — titular Anthropic pelo runner.** No host Codex, o titular é o Opus 5 pelo runner, e
o Manager OpenAI só audita: ele não vira parecer.

O briefing do Opus tem orçamento de **16 KiB = 16.384 bytes UTF-8 por lote, medidos depois da
sanitização**. Até esse limite, envie o pacote inteiro. Acima dele, divida por arquivo/hunk em lotes
independentes, repetindo em cada lote o objetivo, os critérios e o fora de escopo; cubra todos os
hunks e registre a cobertura. **Nunca corte bytes nem resuma em silêncio** para caber. Um lote
omitido ou que falhar torna a cobertura do parecer parcial — e isso se declara.

```bash
# ORQ_PACKAGE_ROOT já foi resolvido pela skill para um caminho absoluto.
OPUS_RUNNER="<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py"
OPUS_OUT=$(printf '%s' "$OPUS_BRIEFING_SANITIZADO" | python3 "$OPUS_RUNNER")
OPUS_EXIT=$?
if [ "$OPUS_EXIT" -ne 0 ] || [ -z "$OPUS_OUT" ]; then
  echo "REVISÃO DEGRADADA: titular ausente; preserve o diagnóstico do stderr"
fi
```

O runner anuncia `OPUS_STARTED` imediatamente **no stderr** e aplica timeout de 240s. A validação
de tamanho ocorre antes do anúncio: `BRIEFING_TOO_LARGE` significa que nenhuma chamada começou;
redivida o lote e execute, sem contar isso como retry. O runner exige
`claude-opus-5` no `modelUsage` JSON e não imprime parecer em modelo errado, timeout, erro ou saída
vazia (`OPUS_EMPTY_RESULT`). `OPUS_EXIT != 0`, `OPUS_OUT` vazio ou qualquer lote incompleto →
**REVISÃO DEGRADADA** com o diagnóstico do stderr;
não faça retry automático após chamada iniciada, para não duplicar custo.
Todo host que usar o alias `opus` como Opus 5 usa o mesmo runner e precisa verificar essa resolução
antes do parecer. Se ela não puder ser comprovada, trate Opus 5 como ausente e marque **REVISÃO
DEGRADADA**, sem trocar de modelo.

### Titular indisponível → REVISÃO DEGRADADA, e o card não avança sozinho

Binário fora do PATH, autenticação vencida, timeout, modelo indisponível, saída vazia: escreva
**REVISÃO DEGRADADA — sem parecer**, nomeie a causa real, e **pare**. O card **não** avança sozinho:
seguir sem revisão é decisão do dono, pedida na hora.

**Nunca substitua o titular por um revisor do mesmo vendor do host** — nem "só pra ter algo", nem
como contingência. Não existe cair num revisor interno: ou o parecer vem do vendor oposto, ou não
há parecer, e a ausência se declara. Um parecer do próprio vendor do host devolveria a *aparência*
de revisão independente sem a independência.

**Segundo parecer só sob demanda do dono — e sob a MESMA regra de vendor.** Se ele pedir ("quero
uma segunda opinião"), o parecer extra também é do **vendor oposto ao host**: pode ser outro
modelo, outro effort ou outro briefing, nunca o outro lado da regra. **Um parecer do vendor do
host não vale como segundo parecer** — chamá-lo de "avulso" não o torna independente, e é por
essa porta que o revisor interno voltaria. Não havendo outro modelo do vendor oposto disponível,
**não há segundo parecer**: diga isso ao dono, em vez de improvisar um nativo. Parecer extra não
ressuscita painel nem vira padrão.

### `--rapido` — briefing enxuto, mesmo titular

`--rapido` **não troca de revisor** (um revisor já é o padrão) e **não dispensa a revisão**. Ele
encolhe o briefing: só o diff, o critério de aceite e o fora de escopo, sem a contextualização
longa. Use em card pequeno e de baixo risco. Quem decide o que entra no briefing enxuto é sempre
este comando — os demais consumidores (`/orq:implement-next`, o README do repositório do plugin,
preset `economia`) não re-enunciam a regra, só apontam para cá.

## 3. Auditar o parecer (o passo que dá o valor)

Nunca repasse parecer cru. **Qual dos dois ramos vale depende de quantos pareceres chegaram** — e
são só dois, porque o segundo parecer só existe quando o dono pede.

### Ramo padrão — um parecer (N=1)

**Todo achado é solitário por construção** e não há com o que cruzar:

- **Verifique cada achado no código, você mesmo**, antes de aceitar. Revisor sozinho erra, e neste
  ramo não existe outro parecer para contrapor; achado não verificado vira ruído e queima a
  confiança da revisão.
- **Descarte achado sem cenário de falha concreto** (entrada → resultado errado) — ou marque
  explicitamente como "opinião de estilo".
- **Discordou do parecer?** Você desempata olhando o código e **explica por quê**. Não deixe a
  contradição pro dono resolver.

Aqui a auditoria é a **única** defesa contra o erro do revisor único. Não é opcional nem se delega.

### Ramo excepcional — dois pareceres (o dono pediu segunda opinião)

Só entra aqui quando o passo 2 produziu um segundo parecer **do mesmo vendor oposto**. Neste ramo
existe cruzamento, e ignorá-lo desperdiçaria o que o dono pagou:

- **Os dois apontaram o mesmo defeito** → confiança alta, vai no topo — mas **ainda assim confirme
  no código**: dois modelos do mesmo vendor erram de forma correlacionada, então acordo entre eles
  é indício, não prova.
- **Achado de um só** → trate pelo ramo padrão: você verifica antes de aceitar.
- **Divergem** (um diz que quebra, outro diz que está certo) → **você desempata olhando o código** e
  explica qual está certo e por quê. Concordância entre pareceres nunca substitui essa verificação:
  **a verificação direta do Manager é o desempate final**, nos dois ramos.
- Na entrega, diga **quantos pareceres houve** e o que cada um sustentou. Sem isso o dono não sabe
  se está lendo um cruzamento ou um parecer só.

### Vale nos dois ramos

**Trilha cruzada:** quando o plano veio do mesmo vendor do revisor (host Claude + card `sistema`, ou
o simétrico), o parecer é independente **do writer**, não do planner. Audite os achados também
contra o plano, e diga isso na entrega.

## 4. Entregar

- **Veredito:** aprovar · aprovar com correções · refazer.
- **Achados** ordenados por severidade: `arquivo:linha` · o defeito em uma frase · como falha na
  prática · **verificado por você no código** (ou descartado, com o motivo).
- **Roteiro de teste manual** — passos de usar o produto (vira o guia de validação do dono).
- **Onde você discordou do revisor** e sua decisão.
- Revisão degradada ou ausência de revisor por dado sensível → diga **na primeira linha**, não no
  rodapé.

Se nada relevante apareceu, diga em uma linha. **Não invente achado pra parecer útil.**

## Regras
- Revisor **não corrige** — quem implementou aplica. Você (Manager) roteia as correções.
- Máximo **2 rodadas** de correção+revisão; persistindo, escale pro dono.
- Nunca mande segredo/credencial no briefing do revisor.
