# R1 / lote 3 — parecer integral

Recibo: exit 0; uma chamada, sem retry. Payload `lote-03.md` conforme SHA no manifesto.

OPUS_MODEL=claude-opus-5-5 OPUS_SECONDS=49.5 BRIEFING_BYTES=14264 OPUS_MODEL_USAGE=claude-opus-5-5
## BLOQUEADORES

1. **`README.md:229-235` — o gate de capacidade exige prova, mas proíbe obtê-la.**
   - **Cenário:** o dono roda `/orq:elenco perfil economia` ou `/orq:elenco implementer leve haiku`. Esses exemplos estão no próprio README, em `README.md:176,181`. Para `haiku`/`economia` nesta conta, a única prova registrada é a de Opus/Astra/Terra. O gate manda "exija prova válida […] modelo + via + conta/host" antes de mudar. A mesma regra termina com "nem dispare nova sonda". Sem sonda, a prova nunca surge. O resultado é elenco preservado e troca recusada.
   - **Erro:** toda troca para um modelo ainda não sondado fica bloqueada para sempre, inclusive trocas legítimas fora de Sol/Luna. Os exemplos de uso do README viram comandos que sempre recusam.
   - **Correção mínima:** restringir a proibição ao escopo aprovado. Por exemplo: "nesta fase, não dispare nova sonda para `gpt-6-sol`/`gpt-6-luna`". Ou dizer explicitamente de onde vem a prova válida, como a chamada real registrada na Matriz ou a sonda autorizada pelo dono.

## RISCOS

1. **`README.md:221` — Terra perdeu o escopo de host.**
   - **Cenário:** o trecho removido dizia "no Codex, os modelos OpenAI com effort". O novo texto diz "**neste projeto**, `gpt-5.6-terra@xhigh` é o degrau ativo", logo após a lista do host Claude. Um leitor no host Claude pode entender Terra como valor ativo para `implementer`/`docs`/`scout` no Claude. Também não fica claro de qual dos três papéis Terra é o degrau.
   - **Correção mínima:** "no Codex, modelos OpenAI com effort; neste projeto, o `implementer` do host Codex usa `gpt-5.6-terra@xhigh`".

2. **`README.md:222-223` — o sujeito da frase está trocado.**
   - **Cenário:** "`gpt-6-sol` e `gpt-6-luna` […] não tornam Terra o default universal". Sol e Luna não teriam como tornar Terra default, então a ressalva fica sem sentido. O leitor pode concluir que Sol/Luna substituem Terra no fábrica.
   - **Correção mínima:** "Terra ser o degrau deste projeto não o torna default universal; Sol/Luna seguem só como candidatos de fábrica, pendentes de capacidade."

3. **`README.md:219-221` — `opus` aparece duas vezes e é chamado de "alias legado" no host Claude.**
   - **Cenário:** a tabela ativa (`README.md:202`) e o preset `padrao` usam `opus` como valor corrente de `implementer·pesada`. O rótulo "legado" sugere descontinuação para esse papel, o que contradiz a tabela.
   - **Correção mínima:** remover "o alias legado `opus`" dessa lista do host Claude. O termo "legado" deve ficar só na célula Anthropic×Codex (`README.md:225-227`).

4. **`README.md:220-221` — a lista pode ter deixado de aceitar IDs arbitrários.**
   - **Cenário:** antes a lista dizia "ou um id (`claude-opus-5`)", e agora diz só "o id explícito `claude-opus-5-5`". No host Claude, `/orq:elenco implementer pesada claude-sonnet-5` passa a ser ambíguo: não fica claro se o valor é aceito ou recusado. Se a intenção era restringir, isso é mudança de regra não declarada no objetivo.
   - **Correção mínima:** manter "ou um ID explícito (hoje `claude-opus-5-5`)", ou declarar a restrição.

5. **`README.md:229-230` — "via" não se define para papéis nativos.**
   - **Cenário:** o gate cobre `implementer`/`docs`/`scout`, que no host Claude são spawn nativo. A tabela de vias diz que o vendor nativo "não é via". Fica indefinido o que conta como prova de "modelo + via" para esses papéis.
   - **Correção mínima:** "via (ou spawn nativo, para papéis do vendor do host)".

6. **`README.md:446-448` — elenco do projeto misturado com template do `init`.**
   - **Cenário:** o parágrafo descreve o que o template do `init` gera. A inserção "**no elenco deste projeto** Implementer Terra/xhigh" deixa ambíguo se um projeto novo recebe Terra do template. Isso toca a regra aprovada de que catálogo de fábrica não é elenco ativo.
   - **Correção mínima:** separar em duas frases: o que o template gera e o que o elenco deste projeto usa.

7. **`orq/commands/elenco.md:428,444` — a referência "passo 3" não é verificável neste lote.**
   - **Cenário:** a renumeração de passo 2 para passo 3 depende da inserção de +14 linhas no hunk anterior, que está fora deste lote. Se o passo 3 real não for o que diz que o perfil não aplica revisores externos, a referência cruzada fica errada.
   - **Correção mínima:** confirmar no lote que contém "Com argumento `perfil <nome>`". Este lote não dá cobertura a isso.

## VEREDITO

**REPROVADO.** O bloqueador 1 é uma contradição normativa introduzida por este lote. A correção é uma frase, restringindo "nem dispare nova sonda" a Sol/Luna nesta fase ou definindo a fonte da prova. Com ela aplicada e os riscos 1–2 esclarecidos, o lote fica apto a APROVADO_COM_RESSALVAS.
