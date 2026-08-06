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
revisores externos estão ativos**. Sem elenco, valem os padrões (reviewer `opus`; Codex ativo se o
plugin existir).

**Sempre — Claude interno:** subagente `orq-reviewer` (read-only, adversarial), com o modelo do papel
`reviewer` do elenco.

> Isto só existe no host Claude (é spawn nativo). **Em host que não é Claude, o membro do vendor do
> host entra pela célula-diagonal da `## Matriz de invocação`** (`_elenco.md`), em sessão nova — sem
> esse passo, o painel fecha só dois vendors e ninguém avisa.

> ⚠️ **Spawne o `orq-reviewer` SEM `name`.** Com `name` ele vira teammate endereçável e fica vivo em
> loop de *idle* em vez de devolver o parecer — o painel morre esperando. Sem nome, ele retorna o
> resultado normalmente. (Quebrou assim em 2026-07-26; ver `memory/gotchas.md`.)

**Se o Codex estiver ATIVO no elenco** e a CLI existir (`codex` no PATH): rode direto, read-only:

```bash
codex exec -m <modelo do elenco> -c model_reasoning_effort=<effort> -s read-only "<briefing>" < /dev/null
```

> ⚠️ **`< /dev/null` não é opcional.** Sem ele o `codex exec` fica bloqueado lendo stdin (não há TTY
> aqui), trava até o timeout e não produz nada — mesmo com o prompt passado como argumento. Com o
> stdin fechado responde em segundos.

Prompt **READ-ONLY explícito** ("não implemente nada, não edite arquivos"). Peça CONFIRMA/REFUTA por
afirmação + achados priorizados com `arquivo:linha` + cenário de falha concreto.

**Se o Kimi estiver ATIVO no elenco:** rode a CLI direto, resolvendo o binário com fallback e
passando o modelo do elenco:

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

**Outros revisores** marcados como **ativo** na seção "Revisores externos" do `_elenco.md`: dispare
do jeito registrado ali.

**Revisor ativo no elenco que falhar** (binário ausente, timeout, saída vazia) → **diga ao dono que
o painel foi parcial**, nomeando quem faltou. Nunca apresente parecer de um revisor como se fosse a
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
