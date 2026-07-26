---
description: Painel de revisores independentes (Claude + Codex, e outros que estiverem configurados) sobre a mudança atual, com os achados reconciliados num parecer só
argument-hint: "[T-NNN | caminho | 'o que revisar'] [--rapido para só um revisor]"
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

## 2. Disparar os revisores EM PARALELO

**Sempre — Claude interno:** subagente `orq-reviewer` (read-only, adversarial).

**Se o plugin Codex estiver disponível** (`codex:codex-rescue`): dispare com
`--fresh --model gpt-5.6-sol --effort xhigh --background` e prompt **READ-ONLY explícito**
("não implemente nada, não edite arquivos"). Peça CONFIRMA/REFUTA por afirmação + achados
priorizados com `arquivo:linha` + cenário de falha concreto.
> O forwarder devolve um bash-id, **não** o `task-mxxx`. Pegue o id real com
> `node <companion> status | grep "| running | rescue"` e faça poll até concluir.

**Revisores extras configurados** (ver `memory/wiki/_revisores.md`, se existir): dispare também.
Slot previsto p/ **Kimi K2** — hoje não instalado; quando houver CLI ou MCP, basta registrar lá.

Com `--rapido`: só o revisor interno.

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
