# R1 / lote 4 — parecer integral

Recibo: exit 0; uma chamada, sem retry. Payload `lote-04.md` conforme SHA no manifesto.

OPUS_MODEL=claude-opus-5-5 OPUS_SECONDS=50.7 BRIEFING_BYTES=15483 OPUS_MODEL_USAGE=claude-opus-5-5
*(Revisão feita só sobre o texto do diff. Não criei arquivo de plano nem chamei ferramentas, conforme a restrição READ-ONLY do pedido.)*

## BLOQUEADORES

Nenhum.

## RISCOS

1. **`orq/commands/revisar.md:123-130`: a instrução de prova perdeu o mapeamento concreto de prefixo por alias.**
   - **Entrada:** host Codex com elenco em override `fable` chama `--model fable`. O stderr traz `OPUS_MODEL=claude-fable-5`, por exemplo vindo de um runner divergente ou de uma leitura manual do JSON.
   - **Erro:** o texto antigo dizia "`fable` exige `claude-fable-5-1`". O novo diz só "prefixo esperado para alias legado", sem dizer qual. O Manager que audita não tem como saber que `claude-fable-5` não serve. Pode aceitar a versão 5.0, que `test_rejects_fable_5_0_when_fable_5_1_is_required` proíbe. Isso contradiz o próprio "sem alargar a prova aceita" da linha 131. O runner ainda barra com exit 7, então é perda de defesa em profundidade, não furo direto.
   - **Correção mínima:** reintroduzir a lista após a linha 124, por exemplo: "`claude-opus-5-5` → igualdade; `fable` → prefixo `claude-fable-5-1`; `opus` → `claude-opus-5`; `haiku` → `claude-haiku-4-5`; `sonnet` → prefixo definido no runner".

2. **`orq/skills/orq/SKILL.md:164`: "(override legado; o padrão é `claude-opus-5-5`)" é ambíguo e pode redirecionar Fable para Opus.**
   - **Entrada:** o usuário diz "quero o Fable planejando".
   - **Erro:** "legado" junto de "o padrão é `claude-opus-5-5`" permite ler que Fable foi substituído. O agente pode então gravar `claude-opus-5-5` no planner, violando "fable não vira Opus". Além disso, "padrão" não diz de qual papel, e o parêntese removeu a informação "Fable 5.1", que ancora a versão exigida.
   - **Correção mínima:** "(alias `fable` = Fable 5.1, override aceito e aplicado como pedido; o padrão do elenco é `claude-opus-5-5`)".

3. **`orq/scripts/test_run_opus_reviewer.py:139-201`: a cobertura dos aliases legados neste lote é parcial.**
   - **Entrada:** uma regressão no runner que reescreva `sonnet` para o ID explícito, ou que aceite `claude-opus-5-5` quando o pedido foi `fable`.
   - **Erro:** o lote testa `opus` e `haiku`, mas nenhum teste deste lote cobre:
     - `--model sonnet`, que o objetivo lista;
     - `--model fable` com `FAKE_MODEL=claude-opus-5-5` → exit 7.
     
     O teste em torno da linha 136 só cobre o caminho feliz de `fable`. Pela instrução de não atribuir cobertura a outros lotes, esses dois requisitos do objetivo ficam sem prova aqui.
   - **Correção mínima:** acrescentar dois testes no padrão dos existentes:
     - `run_runner("revise","--model","sonnet", FAKE_EXPECT_MODEL="sonnet", FAKE_MODEL=<ID sonnet atual>)` → rc 0;
     - `run_runner("revise","--model","fable", FAKE_EXPECT_MODEL="fable", FAKE_MODEL="claude-opus-5-5")` → rc 7 com `OPUS_MODEL_MISMATCH`.

4. **`orq/scripts/test_run_opus_reviewer.py:338`: a semântica de igualdade com múltiplas chaves em `modelUsage` está implícita, não documentada.**
   - **Entrada:** `modelUsage` contém `{claude-haiku-4-5, claude-opus-5-5}` no default explícito.
   - **Erro:** o teste passa só se a igualdade for "alguma chave == ID". `revisar.md:123` diz "exige igualdade" sem qualificar. Um host que audite exigindo que todas as chaves sejam iguais marcaria **REVISÃO DEGRADADA** falsa sempre que a CLI usar um subagente Haiku.
   - **Correção mínima:** em `revisar.md:123-124`, escrever "exige que uma chave do `modelUsage` seja exatamente `claude-opus-5-5` (outras chaves são só auditoria)".

Ficou fora do diff e não foi auditado: o bloco `bash` de `revisar.md` (~104-117), que pode ainda citar `fable` como exemplo.

## VEREDITO

APROVADO_COM_RESSALVAS
