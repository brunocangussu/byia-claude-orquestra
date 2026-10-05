# R1 / lote 2 — parecer integral

Recibo: exit 0; uma chamada, sem retry. Payload `lote-02.md` conforme SHA no manifesto.

OPUS_MODEL=claude-opus-5-5 OPUS_SECONDS=76.4 BRIEFING_BYTES=15455 OPUS_MODEL_USAGE=claude-opus-5-5
## BLOQUEADORES

1. **`memory/wiki/_elenco.md:190`**: a linha `manager` do host Codex mudou de "modelo da sessão (`/model`), sempre escolha do dono" para `gpt-6-astra@max`.
   - **Entrada:** o dono abre uma sessão Codex com outro modelo (por exemplo `gpt-5.6-terra`). A linha 190 declara Astra@max, e a linha 154 continua dizendo "sempre escolha do dono, **em qualquer host**".
   - **Erro:** as duas linhas se contradizem. O texto "sem troca silenciosa" também não diz o que fazer na divergência: anunciar, bloquear ou trocar. A mudança não faz parte do objetivo aprovado, que cobre Fable→Opus 5.5, a prova do runner e Sol/Luna como pendência. Ela também não cita card nem data da "decisão declarada".
   - **Correção mínima:** reverter a linha 190 ao texto anterior. Se a decisão existe de fato, citar card e data, dizer o que fazer quando o modelo real diverge, e ajustar a linha 154 no mesmo lote.

## RISCOS

1. **`memory/wiki/_elenco.md:155`** (e também 290 e 310): `planner·interface` passa a `claude-opus-5-5` por spawn nativo com a nota "capacidade confirmada no uso".
   - **Entrada:** o comando lê o elenco e passa `model: claude-opus-5-5` como override no Task.
   - **Erro:**
     - Nenhuma célula registra prova desse ID no spawn nativo. O Fable, que ocupava o papel, tinha prova com data.
     - A frase pode ser lida como "já comprovado", o que contraria "não prometer antes de rodar".
     - Se o override do Task aceitar só aliases, o spawn falha, e a falha não aparece antes do primeiro uso.
   - **Correção mínima:** trocar a nota por "`não testado`; comprovar no primeiro spawn" e acrescentar esse item em `### Pendências comprováveis`.

2. **`memory/wiki/_elenco.md:126` e `:196`**: o reviewer ativo do host Codex passa a `claude-opus-5-5` via runner.
   - **Entrada:** a matriz lista provas com data só para `opus` e `fable`.
   - **Erro:** o ID novo não tem estado registrado (`comprovado` ou `não testado`), e a linha 196 perdeu a data de prova que tinha. O runtime continua fail-closed por causa da regra 3, então não há risco de aceitar parecer de outro modelo. O problema é que o estado anunciado fica incompleto.
   - **Correção mínima:** acrescentar "`claude-opus-5-5`: `não testado`" na célula 126 até a primeira sonda real.

3. **`orq/scripts/run-opus-reviewer.py:160-161`**: a comparação por igualdade estrita pode travar a via.
   - **Entrada:** a CLI reporta em `modelUsage` uma chave com sufixo, por exemplo um sufixo de release ou de variante de contexto. O comentário novo nas linhas 26-29 admite que a CLI usa esses sufixos.
   - **Erro:** a comparação `name == expected_model` reprova com exit 7 em toda chamada, e o reviewer fica ausente de forma permanente. Isso é seguro, mas desliga a via inteira.
   - **Correção mínima:** manter a igualdade, que é o objetivo aprovado, e condicionar a ativação a uma sonda real com `--model claude-opus-5-5` registrando a chave exata observada. Se aparecer sufixo, tratá-lo de forma explícita, sem voltar ao prefixo `claude-opus-5`.

4. **`memory/wiki/_elenco.md:310` (e 260)**: a economia no host Claude trocou `opus`, que estava marcado como "escolha verbatim do dono" e "decisão anterior do dono, preservada aqui", por `claude-opus-5-5`.
   - **Entrada:** o dono aplica o perfil `economia` esperando o comportamento que registrou.
   - **Erro:** um registro de decisão explícita do dono foi reescrito sem citar aprovação. Isso só estaria coberto pelo objetivo se "Opus → Opus 5.5" valer também para este perfil, e o objetivo não diz isso.
   - **Correção mínima:** confirmar com o dono. Se não houver confirmação, manter `opus` com a justificativa original.

Sem achados nas outras mudanças do script: alias desconhecido falha antes de chamar a CLI, `fable` com Opus na resposta reprova, e aliases legados mantêm a prova por prefixo. Também sem achados no bloco Sol 6/Luna 6 (212-218), que fica como pendência sem ativação nem fallback, com Astra e Terra preservados.

Não vejo a definição do argparse (`choices` e texto de ajuda de `--model`) nem a mensagem completa de `MODEL_ALIAS_DESCONHECIDO`. Não atribuo cobertura a essas partes.

## VEREDITO

**REPROVADO**, por causa do bloqueador 1. Revertida a linha 190, ou comprovada a decisão com o ajuste da linha 154, o lote passa a **APROVADO_COM_RESSALVAS** pelos riscos 1 a 4.

Nota: segui a restrição "somente texto, nenhuma ferramenta" do pedido. Por isso não criei arquivo de plano nem chamei ferramentas do modo de planejamento.
