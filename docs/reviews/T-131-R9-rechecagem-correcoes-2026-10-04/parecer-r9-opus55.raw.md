## RECHECAGEM

Não usei nenhuma ferramenta. O pacote pede isso de forma expressa e isso prevalece sobre o fluxo de plano do ambiente; por isso também não criei arquivo de plano. Contei as linhas a partir dos cabeçalhos dos hunks do diff. Fiz essa contagem para README, `elenco.md`, `plan-next.md`, `implement-next.md`, `init.md`, `revisar.md` e `SKILL.md`.

**B1 (R8) — CORRIGIDO.**

O que mudou na definição:
- **Antes:** a exceção "padrão legado comprovado" não tinha definição.
- **Agora:** ela tem uma definição verificável, repetida com o mesmo texto em todos os consumidores:
  - README.md:249–254
  - orq/commands/elenco.md:132–137
  - orq/commands/init.md:291–298
  - orq/commands/plan-next.md:41–46
  - orq/commands/implement-next.md:26–30
  - orq/commands/revisar.md:58–65
  - orq/skills/orq/SKILL.md:233–240
- **A definição exige quatro coisas:**
  - uma combinação já usada e autorizada neste projeto;
  - um recibo real consultável na thread;
  - que o Manager verifique a origem e a compatibilidade antes do despacho;
  - "nunca isenção de prova".
- **Campos de compatibilidade:** são os do gate canônico (elenco.md:116–124, README:242–247). Mudança de modelo, effort, mecanismo, sandbox, versão ou conta exige revalidação.

Os dois cenários da R8:
- **Cenário A (contorno), fechado.** "Default, alias ou cache não certificam", e sem recibo a regra é "não despache". Um Manager que declare `fable`, `opus` ou o default do runner como "legado" sem recibo na thread viola agora o texto literal de todos os consumidores, e não apenas uma leitura possível dele.
- **Cenário B (travamento):** a correção não pede sonda por uso. Diz que "Quando o recibo válido ainda é compatível, o reuso não exige nova sonda" e que "papéis preservados não exigem prova nova" (init.md:287). Quanto a um projeto novo pagar provas na inicialização, aceito a delimitação do Manager: é decisão de gate do dono para uma operação própria, e não reabro esse ponto.

A afirmação do Manager confere com o diff:
- os sete consumidores têm o mesmo parágrafo;
- a exceção do `off` está restrita ao desligamento (elenco.md, ramo "É via");
- o runner não mudou.

O que não aceito por autodeclaração:
- **Suíte:** a descoberta completa terminou com `exit=1`. O isolamento posterior de `test_kanban_status` não apaga essa falha. Esse arquivo está fora dos oito, então não a atribuo a este escopo, mas também não registro "suíte verde".
- **Fixture e âncora de lint:** as conclusões sobre `ATIVOS_BASE` (:765+) e sobre a âncora do lint (`lint-coerencia.py:2323–2396`) dependem de trechos que não recebi. Ficam como afirmação do Manager, sem verificação.

## BLOQUEADORES

Nenhum.

## RISCOS

1. **A fixture contradiz o contrato no campo `data`.** Em `test_elenco_perfis.py`, `T131PosR8LegadoComprovadoTest.CONTEXTO` inclui `"data"` e `"modelo_observado"`. Além disso, `decidir_despacho_legado` exige igualdade campo a campo entre o recibo e a operação.
   - **Efeito:** um recibo de 2026-10-01 reutilizado em 2026-10-04 seria bloqueado. Isso inverte a regra "o reuso não exige nova sonda" e trata como critério de compatibilidade um modelo observado que, antes do despacho, ainda não existe.
   - **Por que o teste passa:** as duas fixtures têm a mesma data.
   - **Alcance:** não afeta o consumidor LLM. Mas a docstring chama isso de "projeção executável do contrato", o que pode orientar mal uma manutenção futura.
   - **Correção mínima:** tirar `data` e `modelo_observado` da comparação de compatibilidade e acrescentar um caso com data diferente que deve passar.
2. **O teste é textual e fraco em alguns pontos.**
   - `decidir_despacho_legado` é Python escrito à mão. A ligação com o texto vem só de `comprovar_contrato`, que procura marcos.
   - Os casos `default`/`alias`/`cache` são apenas `recibo=None`, o que é tautológico.
   - A cláusula "o reuso não exige nova sonda a cada uso" não está em `MARCOS_COMUNS`. Além disso, o README usa outra redação ("dispensa sonda repetida em usos sucessivos").
   - Os campos `via`, `data` e `runtime` em `CAMPOS_CANONICOS` aparecem em vários outros lugares do texto, então a mutação deles não acusa nada.
3. **O recibo de via nativa pode não ter "modelo observado".** Um spawn nativo no host Claude talvez não exponha a identidade observada. O pacote não mostra como um legado nativo, como `fable` no `planner·interface`, obtém um recibo completo. O efeito é fail-closed (não despacha), sem contorno. Precisa de evidência viva.
4. **O recibo do runner não persiste sozinho.** `OPUS_PROCESS_RECEIPT` vai para o stderr, e o trecho enviado de `revisar.md` não manda gravá-lo na thread. Sem essa gravação, o uso normal não acumula o "recibo consultável" que a exceção exige. O impacto é restrito a projetos sem elenco.
5. **Atualizar a CLI anula o legado.** "Versão do executável/runtime" faz parte da compatibilidade. Num projeto sem elenco, uma autoatualização do `claude` bloqueia o despacho até o dono decidir. É fail-closed e coerente com o gate, mas tem custo operacional.
6. **A "thread" de `init.md:291–293` é ambígua.** O texto diz que "a falta desse destino não bloqueia operação legada já comprovada", enquanto a definição exige um recibo "na thread" sem dizer qual. A leitura coerente é: o recibo legado fica na thread do card de origem, e o destino novo é a thread do card atual. Explicitar isso tiraria a ambiguidade.
7. **Riscos da R8 ainda abertos, sem mudança por este escopo:**
   - identidade única em `modelUsage` (há um recibo real desta R8, mas ele não garante as próximas chamadas);
   - alias `opus` aceitando o sufixo `-5`;
   - subtype fechado;
   - TERM seguido imediatamente de KILL;
   - hash do executável a cada chamada;
   - testes que dependem do relógio;
   - indentação alternando 3 e 4 espaços em elenco.md, no ramo "É via".

## COBERTURA

Examinei:
- o parecer da R8, a auditoria do Manager e o handoff pós-R8;
- o diff integral dos oito arquivos contra HEAD;
- `run-opus-reviewer.py` completo;
- os trechos selecionados de `test_elenco_perfis.py` (linhas 1–110 e 1633–1812) e de `elenco.md` (linhas 87–212).

Não examinei:
- o restante de `test_elenco_perfis.py`, incluindo `ATIVOS_BASE` completo e `PRESET_ECONOMIA_BASE`;
- `lint-coerencia.py`, `stack.md` e `test_kanban_status`;
- as threads e os recibos reais;
- o JSON do handoff.

Não executei testes, lint nem CLI. Os resultados de gate citados são declarações do Manager. Testes estruturais não provam o comportamento do host. Este GO fecha a revisão do escopo B1 corrigido; não é prova de produto instalado nem autorização de entrega.

## VEREDITO
GO
