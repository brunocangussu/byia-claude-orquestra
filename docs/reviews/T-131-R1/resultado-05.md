# R1 / lote 5 — parecer integral

Recibo: exit 0; uma chamada, sem retry. Payload `lote-05.md` conforme SHA no manifesto.

OPUS_MODEL=claude-opus-5-5 OPUS_SECONDS=67.1 BRIEFING_BYTES=9156 OPUS_MODEL_USAGE=claude-opus-5-5
## BLOQUEADORES

1. **`orq/scripts/test_elenco_perfis.py:212-217`**: o teste não protege o elenco do projeto contra ativação de Sol ou Luna.
   - **Entrada:** alguém troca em `memory/wiki/_elenco.md` a linha `| scout | ... |` (ou `docs`, ou `implementer·leve`) para `` `gpt-6-sol@low` `` ou `` `gpt-6-luna` ``.
   - **Erro:** o teste continua verde. Ele só ancora duas linhas Astra/Terra (`planner·interface` com Astra e `implementer·pesada` com Terra). As linhas 216-217 exigem a presença de `gpt-6-sol` e `gpt-6-luna` no documento, e uma linha de tabela ativa satisfaz essa exigência. O docstring promete "preservam o elenco ativo inteiro", mas nenhuma asserção cobre isso. Como a restrição aprovada é justamente "não ativar sem prova", a guarda deste lote dá cobertura falsa.
   - **Correção mínima:** acrescentar uma asserção negativa sobre as linhas de tabela do projeto, por exemplo `self.assertIsNone(re.search(r"^\|[^|\n]+\|\s*`gpt-6-(sol|luna)", projeto, re.M))`. Se o objetivo é mesmo o elenco inteiro, a alternativa é ancorar todas as linhas esperadas da seção ativa.

## RISCOS

1. **`orq/scripts/test_elenco_perfis.py:200-202`**: a asserção é tautológica.
   - **Entrada:** `ATIVOS_BASE` e os presets de fixture, que o próprio diff define nas linhas 247 e 258.
   - **Erro:** o teste checa constantes locais, não documentos reais, mas está numa classe `...RealDocumentsTest`. Não prova nada sobre o template ou o elenco.
   - **Correção mínima:** remover essas três linhas, ou movê-las para uma classe de fixtures sem atribuir a elas cobertura documental.

2. **`orq/scripts/test_elenco_perfis.py:258`**: o preset de economia sai do escopo aprovado.
   - **Entrada:** o preset de economia passa de `opus` (alias) para `claude-opus-5-5` (ID explícito).
   - **Erro:** o objetivo aprovado é trocar o Fable ativo por Opus 5.5, e economia não era Fable. A troca muda a semântica de prefixo legado para igualdade exata. Também pode apagar a cobertura de algum caso da matriz que exercitava o alias `opus`, o que não dá para verificar só pelo diff.
   - **Correção mínima:** manter `"opus"` no preset de economia, salvo se a mudança do preset real estiver explicitamente aprovada em outro lote.

3. **`orq/scripts/lint-coerencia.py:2109`**: o lint perdeu a âncora do prefixo legado de `opus`.
   - **Entrada:** o runner muda o mapeamento do alias `opus` (por exemplo, para um prefixo errado).
   - **Erro:** a âncora antiga `"claude-opus-5"` foi substituída pela literal do ID explícito, e nada mais ancora o prefixo do alias `opus`. `fable` continua ancorado na linha seguinte, mas `opus` não. Isso contraria "aliases conservam prefixo legado". Há ainda um segundo problema: a literal `"claude-opus-5-5": "claude-opus-5-5"` tem a forma de uma entrada numa tabela de prefixos. Se o runner fizer `startswith`, um ID como `claude-opus-5-50` passaria, e a âncora não prova igualdade.
   - **Correção mínima:** acrescentar uma âncora para o alias `opus` (ex.: `'"opus": "claude-opus-5"'`, no formato real do runner) e uma âncora para o ramo de igualdade exata usado para IDs explícitos.

4. **`orq/scripts/test_elenco_perfis.py:213-214`**: as asserções do projeto não são ancoradas por seção.
   - **Entrada:** `| reviewer | `claude-opus-5-5` |` aparece na seção Host Claude do `_elenco.md`.
   - **Erro:** isso seria um revisor do mesmo vendor do host, e o teste passa, porque `assertIn` roda sobre o arquivo inteiro. O lint (linhas 2224-2228) só ancora por seção o template, não o projeto.
   - **Correção mínima:** recortar a seção com `secao_unica` antes de fazer as asserções do projeto.

5. **`orq/scripts/test_elenco_perfis.py:219`**: o novo teste usa `re.sub`.
   - **Entrada:** o módulo não importa `re`, o que não é visível no diff.
   - **Erro:** o teste quebraria com `NameError`.
   - **Correção mínima:** confirmar que `import re` existe no cabeçalho do arquivo.

6. **`orq/scripts/test_elenco_perfis.py:206`**: a âncora contém `\n\n` literal.
   - **Entrada:** o template é salvo com CRLF, ou com espaço sobrando depois do heading.
   - **Erro:** falso vermelho no teste.
   - **Correção mínima:** normalizar o documento (`re.sub(r"\s+", " ", ...)`) antes dessa asserção, como já é feito nas linhas 218-219.

**`orq/stack.md:166,223-225`**: nenhum problema. O texto é coerente com o objetivo: igualdade para o ID explícito e prefixo para aliases legados.

## VEREDITO

**REPROVADO.** O bloqueador 1 deixa sem guarda efetiva, neste lote, a restrição central de não ativar Sol ou Luna no elenco do projeto. A correção é pontual: uma asserção negativa. Os riscos 1 a 4 são recomendados, mas não bloqueiam.
