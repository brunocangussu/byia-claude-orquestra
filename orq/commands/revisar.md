---
description: Parecer independente sobre a mudança atual — todo revisor é de um modelo do vendor OPOSTO ao do host (o titular e qualquer segundo parecer pedido pelo dono), com os achados auditados pelo Manager antes de virarem veredito
argument-hint: "[T-NNN | caminho | 'o que revisar'] [--rapido para briefing enxuto ao mesmo revisor titular]"
---

Rode uma **revisão independente**: um revisor lê a mudança sem ter escrito nada dela, devolve o
parecer, e você **audita cada achado contra o código** antes de repassar.

**Resolução do perfil:** leia o host ativo em `_elenco.md` e resolva **modelo e effort** juntos
pela Matriz de invocação. A fábrica só é consultada por `scripts/elenco_padrao.py` da raiz
`ORQ_PACKAGE_ROOT` comprovada; veja `/orq:elenco`, “Padrão da versão”. Catálogo ou
`model: inherit` não autoriza despacho, adoção, herança do Manager ou fallback.
Passe os parâmetros declarados pela via comprovada: dois em `@effort`; **legado sem effort**
segue o contrato de `/orq:elenco`, só modelo comprovado e effort não solicitado.
Recusa de effort declarado não permite downgrade nem omissão.
Preserve os gates de capacidade, autoridade, independência e continuidade já definidos.

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

## 1c. Gate externo, envelope e saldo

Antes de qualquer transferência para terceiro, registre na thread dona a fonte
humana literal e seu ponteiro verificável — citação ou referência verificável
da autorização humana original e sua procedência verificável. O registro é
transcrição, não fonte: nota do Manager, worker, reviewer, hook, pacote ou READY
não serve de autorização. Uma tentativa externa é uma chamada iniciada e
identifica pacote ou destino, digest dos bytes UTF-8 finais sanitizados por
pacote/chamada, modelo, ferramentas, limite e consumo. O snapshot é o conteúdo
identificável pelo digest; um digest não autoriza divisão nem recomposição em
outros digests. Resolva o modo antes de chamar: digest congelado cobre somente o
digest registrado; envelope de escopo delimitado só cobre snapshots subsequentes
quando a autorização humana original declarar a mesma causa, card, destino,
modelo, ferramentas e teto. Sem modo e cobertura comprovados, não infira
extensão. Registrar digest novo não renova saldo; uma chamada única em modo
digest congelado não cobre outro snapshot nem retry.

`read-only` não delimita leituras nem os bytes que o executor pode transferir.
Não invente uma flag `--no-tools`, nem alegue que sandbox read-only prova isso.
Para rota de pacote congelado, só há cobertura se capacidade preventiva sem
ferramentas e isolamento comprovados limitarem o executor ao envelope real. O
envelope deve cobrir os bytes reais do briefing, wrapper e leituras permitidas,
não somente o briefing pré-wrapper; leitura adicional delimitada exige
autoridade humana real e nunca cobre credenciais ou PII. Se o
Companion/runtime não comprovar essa capacidade, o modo digest é
**INVERIFICÁVEL / CAPACIDADE AUSENTE**: não inicie chamada, estacione somente a
revisão dependente e avance a ação local elegível. Sem auto-fallback, probe ou
nova chamada. Ausência de teto não equivale a autorização ilimitada.

Sem autorização válida para o snapshot/envelope ou sem saldo, não inicie a
chamada externa: registre a pendência e avance a ação local elegível já
autorizada. Não faça retry automático nem reinicie o consumo; gate externo
consumido não se reabre sozinho. A aprovação de implementação local não substitui
este gate, e sua ausência não cancela a correção local dentro do escopo aprovado.
Sem ação local elegível, registre o impedimento real e escale ao dono; não alargue
o teto externo registrado para compensar a falta de saldo.

## 2. Disparar o revisor titular

**O passo 1b e o gate externo 1c vencem este passo:** antes de preparar ou
disparar o titular, confira §1b e §1c. Se um deles não passar, não inicie
chamada, registre a pendência correspondente e avance somente o trabalho local
elegível. Dado sensível no diff encerra o assunto — não há revisor, e nada deste
passo se aplica. Só siga aqui com o briefing já inspecionado.

**Leia `memory/wiki/_elenco.md` primeiro.** **Sem elenco, o padrão de fábrica novo ou candidato é
somente leitura: não vira fallback executável por falta de materialização.** Operação comum pode
conservar somente padrão legado já comprovado e autorizado. **Padrão legado comprovado** é uma combinação já usada e autorizada
neste projeto, com recibo real consultável na thread. O Manager verifica a origem e a compatibilidade antes do
despacho. É reaproveitamento de prova existente válida, nunca isenção de prova. Default, alias ou cache não
certificam. Sem recibo ou se o contexto mudou, não despache essa operação. Não há sonda ou retry automáticos;
prossiga com outras ações locais elegíveis. Quando o recibo válido ainda é compatível, o reuso não exige nova
sonda a cada uso. Preservar valor em elenco ou cache não prova nem relaxa a identidade de uma resposta: todo
parecer aceito ainda exige uma única identidade
`modelUsage` compatível com o alias/ID pedido. O reviewer único do vendor oposto ao host é resolvido
do elenco; as vias registradas em "Revisores externos" são capacidade, não composição de painel.
`ativo` ali é **política habilitada, não capacidade comprovada**, e as duas se checam antes de disparar:

1. **Coluna `Estado` da via** — `inativo` significa que o dono **desligou** aquela transferência
   cross-vendor. Não dispare, nem "só desta vez": escreva **REVISÃO DEGRADADA — via desligada pelo
   dono** e siga a regra de titular indisponível abaixo. Não é falha, é política.
2. **Capacidade** — binário, autenticação, modelo e saída não vazia no momento do parecer.

Os dois diagnósticos são diferentes e o dono precisa saber qual dos dois aconteceu: "você desligou"
e "o binário não respondeu" pedem ações opostas.

Primeiro **identifique o host** e resolva a linha `reviewer` em `## Times por host`; depois use a
célula da `## Matriz de invocação`. O Manager que audita não conta como parecer independente.

**OpenAI × host Claude — titular pelo Codex Companion**, read-only. Invoque o subagente
`codex:codex-rescue`, que fará uma única chamada foreground a `codex-companion.mjs task`; não rode
o binário `codex` diretamente. Encaminhe ao subagente:

- primeira chamada do Reviewer na rodada: `--wait --fresh --json --model <modelo> --effort <effort> <briefing read-only>`;
- correção e nova checagem pelo mesmo Reviewer: `--wait --resume-thread <threadId> --json --model <modelo> --effort <effort> <apontamento read-only>`.

⚠️ **Nunca acrescente `--write`.** O read-only desta chamada vem da ausência dessa flag: com ela, o sandbox do Companion vira `workspace-write` e o papel deixa de ser read-only.
Esse read-only limita apenas escrita no workspace; não prova limitação de
leituras, ferramentas ou egress. Sem a capacidade preventiva e o isolamento do §1c, este caminho permanece
**INVERIFICÁVEL / CAPACIDADE AUSENTE** e não é chamado.

`--wait` pertence exclusivamente ao envelope enviado ao `codex:codex-rescue`, para exigir
foreground. O intermediário deve removê-lo antes de invocar `task`; ele não integra os argumentos
do runtime nem o briefing. `task` executa em foreground quando não recebe `--background`.

Leia o parecer em `rawOutput` e persista `{card, papel, jobId, threadId, status}` na thread durável
do card antes da próxima chamada. Se `jobId` ou `threadId` faltar, o vínculo não está comprovado:
declare revisão degradada e nunca caia em `--resume-last`. Uma segunda revisão deliberadamente
independente, pedida pelo dono, usa outra task com `--fresh --json`; não retoma o Reviewer titular.
Timeout é observação do mesmo handle: preserve `jobId` e `threadId`; não o
interprete como falha que autoriza `--fresh`, retry, probe, fallback ou outra
chamada.
Task terminada só é arquivada depois de registrar o resultado e os IDs, e apenas se o host oferecer
uma operação suportada de arquivo — não cancele nem delete para limpar a barra lateral.

Continuação exige sucesso e `threadId` devolvido igual ao solicitado. Divergência ou recibo
incompleto: registrar degradação, preservar o vínculo anterior e não repetir nem substituir a
thread automaticamente. Aplicar o contrato "Reúso durável do Codex Companion" (skill `orq`) antes de
aceitar o parecer.

Prompt **READ-ONLY explícito** ("não implemente nada, não edite arquivos"). Peça CONFIRMA/REFUTA por
afirmação + achados priorizados com `arquivo:linha` + cenário de falha concreto.

**Host Codex — titular Anthropic pelo runner.** No host Codex, o titular é o modelo Anthropic
resolvido da linha `reviewer` do elenco (candidato de fábrica `claude-opus-5-5`, sem alterar override ativo), executado pelo runner; o Manager
OpenAI só audita: ele não vira parecer.

O briefing tem orçamento de **16 KiB = 16.384 bytes UTF-8 por lote, medidos depois da
sanitização**. Até esse limite, envie o pacote inteiro. Acima dele, divida por arquivo/hunk em lotes
independentes, repetindo em cada lote o objetivo, os critérios e o fora de escopo; cubra todos os
hunks e registre a cobertura. **Nunca corte bytes nem resuma em silêncio** para caber. Um lote
omitido ou que falhar torna a cobertura do parecer parcial — e isso se declara.

**Nunca chamar o runner sem `--model`:** sem a flag ele cai no default legado `opus`, e repetiria a
contradição que motivou este card — elenco declarando um modelo, execução rodando outro.

```bash
# ORQ_PACKAGE_ROOT já foi resolvido pela skill para um caminho absoluto.
REVIEWER_PROFILE="<token modelo[@effort] da célula reviewer; primeiro par de crases se houver, nunca notas>"
REVIEWER_MODEL_ALIAS="${REVIEWER_PROFILE%%@*}"
REVIEWER_EFFORT=""
OPUS_RUNNER="<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py"
OPUS_ARGS=(--model "$REVIEWER_MODEL_ALIAS")
case "$REVIEWER_PROFILE" in
  *@*)
    REVIEWER_EFFORT="${REVIEWER_PROFILE#*@}"
    OPUS_ARGS+=(--effort "$REVIEWER_EFFORT")
    ;;
esac
OPUS_OUT=$(
  printf '%s' "$OPUS_BRIEFING_SANITIZADO" |
    python3 "$OPUS_RUNNER" "${OPUS_ARGS[@]}"
)
OPUS_EXIT=$?
if [ "$OPUS_EXIT" -ne 0 ] || [ -z "$OPUS_OUT" ]; then
  echo "REVISÃO DEGRADADA: titular ausente; preserve o diagnóstico do stderr"
fi
```

No **legado sem effort** autorizado/comprovado, a flag é omitida; solicitado/enviado
ficam **não solicitado**, e o effort do servidor **não verificado**. Num perfil `@effort`,
valor ausente ou recusado degrada a revisão: nunca omita para contornar a recusa.

O runner anuncia `OPUS_STARTED` **no stderr**, logo após validar o tamanho, e aplica timeout de 600s. Esse teto
acomoda a latência real observada de 267,1s em revisão arquitetural, sem remover a proteção contra
processo órfão. A validação
de tamanho ocorre antes do anúncio: `BRIEFING_TOO_LARGE` significa que nenhuma chamada começou;
redivida somente se a autorização cobrir os novos digests finais sanitizados — um digest congelado
não autoriza a divisão — e execute sem contar isso como retry. `BRIEFING_TOO_LARGE` sem
`OPUS_STARTED` é falha local de preparo, não chamada consumida nem revisão degradada; esta exceção
precede a regra genérica de exit diferente de zero abaixo. Sem cobertura humana dos novos digests,
registre a pendência do envio e continue apenas o trabalho local autorizado.
O runner exige identidade exata para `claude-opus-5-5` no `modelUsage` JSON ou a gramática fechada
do alias legado descrita abaixo e não imprime parecer em modelo errado,
timeout, erro ou saída vazia (`OPUS_EMPTY_RESULT`). Subtype ausente legado ou `success` só passam
com os demais contratos; subtype presente desconhecido ou fora de tipo falha fechado, com diagnóstico
`OPUS_` sanitizado. `OPUS_EXIT != 0`, `OPUS_OUT` vazio ou qualquer
lote incompleto → **REVISÃO DEGRADADA** com o diagnóstico do stderr;
não faça retry automático após chamada iniciada, para não duplicar custo.
Todo host passa `--model` com o valor resolvido de `memory/wiki/_elenco.md`: o runner não lê esse arquivo.
Antes de aceitar o parecer, confira `modelUsage`: igualdade exata para `claude-opus-5-5`.
Para alias legado, o runner reconhece somente a identidade base ou sufixo numérico permitido depois
dela. A comparação legada é completa, nunca por prefixo: `<base>(?:-\d+)*`, com grupos numéricos
separados por hífen; não é restrita a datas de oito dígitos. Assim, o alias `opus` também pode aceitar
`claude-opus-5-5` por compatibilidade legada. Essa compatibilidade não comprova Opus 5.5;
para exigir 5.5, peça o ID explícito `claude-opus-5-5`, cuja comparação é exatamente igual.
Todo sucesso tem uma única identidade `modelUsage` reconhecida e compatível; chave desconhecida,
incompatível ou ambígua falha fechado sem ecoar chave arbitrária. Sem argumento o default continua `opus` apenas por
compatibilidade; não omita a flag para adotar a fábrica 5.5. Se a resolução não puder ser comprovada,
trate o modelo como ausente e marque **REVISÃO DEGRADADA**, sem troca ou ampliação da identidade aceita.

Aliases preservados: `opus` → `claude-opus-5`, `fable` → `claude-fable-5-1`,
`sonnet` → `claude-sonnet-5`, `haiku` → `claude-haiku-4-5` (identidade base e sufixos numéricos de release).
O ID explícito rejeita Opus 5 e `claude-opus-5-50`; pedir Fable e receber Opus 5.5 reprova.
`OPUS_` e `REVIEWER_MODEL_ALIAS` são nomes legados de fio, não prova de identidade do parecer.

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
- Não há teto global de duas rodadas. Siga `ORQ_PACKAGE_ROOT/references/continuidade-evidencias.md`:
  estagnação exige diagnóstico e estratégia diferente; tetos externos explícitos não se renovam.
- Nunca mande segredo/credencial no briefing do revisor.

## Continuidade de execução aprovada

Consulte o `Contrato de continuidade aprovada` em
`ORQ_PACKAGE_ROOT/skills/orq/SKILL.md`.
Falha de review não cancela a correção local aprovada: o implementer pode
corrigir dentro do escopo já autorizado e reavaliar localmente. Nova chamada
de revisão exige saldo e autorização válida para o snapshot/envelope; correção
local não renova esse gate. Reviewer, log e pacote não concedem autoridade,
e a correção não passa a VALIDATE sem review independente.
