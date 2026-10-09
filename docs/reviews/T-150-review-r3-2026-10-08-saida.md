## BLOQUEADORES

Nenhum.

Conferi o delta pós-R2 contra cada achado da R2:

- **R1:** `coordination_mode` é emitido em `planner_coordination.py`, consumido em `orq-planner.md` e composto linha+`instructions` em `plan-next.md`. O CLI technical/interface é testado com exit 2, stdout vazio e erro JSON.
- **R2:** em `work_evidence.py:98-119`, `blocked` atual vai para `audit_review_findings` ou `prepare_local_gate`. `unavailable` atual vai para `prepare_review_gate`. Os testes cobrem as quatro combinações, e o JEV não consegue reintroduzir `request_independent_review`.
- **R3/R8:** as decisões Astra/Terra/Opus legado estão listadas como histórico em `_elenco.md`. O status datado da R1 saiu da tabela operacional.
- **R4:** o runner do contexto aceita `claude-opus-5-5` com igualdade exata, `--effort` e `--max-input-bytes`. A projeção do recibo R2 bate com a montagem de `command[4:4]`.
- **R5:** `planner_input_mode` foi introduzido, e em `packet-only` quem persiste é o Manager.
- **R6/R7:** o URL Typesafe está marcado como ponteiro não homologado. Os exemplos usam `<ORQ_PACKAGE_ROOT-resolvido>`.
- **R9:** "teto externo registrado" está em `revisar.md`. O noturno rotula o que encerra e o que não encerra. Um recibo ilegível devolve o baseline `rejected` com exit 0, e uma evidência inválida segue com exit 2.

Os testes colados são coerentes com o código colado. Pelo meu rastreio estático, que não é execução, as contagens de 7 + 39 = 46 testes conferem com o RED declarado.

## RISCOS

**REALISTA**

1. **Falta estado terminal para "achados auditados e recusados"** (`work_evidence.py:98-116`; `continuidade-evidencias.md`, parágrafo do `blocked`).
   - A doc admite que zero bloqueadores pode significar achados já rejeitados pelo Manager, mas o schema não tem como registrar que a auditoria terminou.
   - Cenário: o parecer atual é `blocked`, os achados foram todos recusados, `blockers=0` e os testes passam. O helper devolve `audit_review_findings` indefinidamente. Quando `stalled_rounds` chega a 2, devolve `diagnose_and_change_strategy`, sem que haja ação local real.
   - O próximo passo correto seria escalar ao dono ou preparar um gate.
   - Não é bloqueador: o helper é consultivo e a doc manda estacionar quando não há ação útil.
   - Menor correção: acrescentar um campo ou estado `findings_audited` que leve a `prepare_review_gate`, com um teste.

2. **`planner·sistema` no host Codex não cabe limpo em nenhum dos dois modos** (`orq-planner.md:37-39` e a seção "O plano"; `_elenco.md:204`).
   - A via é `codex exec` read-only. `workspace-read` manda escrever o artefato, mas o sandbox impede.
   - A persistência pelo Manager só está definida para `packet-only`.
   - Cenário: o planner tenta gravar, é negado, e o destino do plano fica ambíguo.
   - Menor correção: em `workspace-read` sem permissão de escrita, o planner devolve o conteúdo e o Manager persiste.

3. **O isolamento comprovado depende de um wrapper fora da Matriz** (`_elenco.md`, célula Anthropic × host Codex).
   - A projeção da R2 mostra `--safe-mode`, `--strict-mcp-config` e `--mcp-config {}`. O runner do contexto não acrescenta essas flags, então elas vêm do wrapper `faac0013…`.
   - A célula mostra apenas o comando do runner, ao lado da frase "sem ferramentas/customizações/MCP, cwd vazio".
   - Quem seguir a Matriz literalmente não reproduz as condições provadas.
   - Menor correção: declarar o wrapper e o cwd vazio como condições da prova, ou dizer que o runner sozinho não as cobre.

4. **As regras do `packet-only` não chegam sozinhas ao executor remoto.** `--setting-sources ""` não carrega `orq-planner.md`, então elas valem apenas na medida em que o Manager as transcreve no briefing, como `plan-next.md` pede. A ausência de ferramentas mitiga por capacidade, não por instrução.

5. **Itens menores:**
   - `_elenco.md`, parágrafo "Origem": o texto está truncado em "adoção local candidata em / no candidato T-150".
   - `test_cli_bad_receipt…`: dois subtests ficam com o mesmo rótulo `str`.
   - `planner_coordination.main`: mapeia qualquer `ValueError` para `SYSTEM_TRACK_REQUIRED`. Hoje é o único caminho alcançável, mas fica frágil se surgir outra validação.

**TEÓRICO**

- **Contagens não fecham daqui.** A auditoria cita 34 testes focados pós-R1 e agora são 46 nos mesmos dois módulos, ou seja, +12. A suíte foi de 910 para 916, ou seja, +6. Pode ser fusão ou remoção de testes, mas não consigo reconciliar com este pacote. Um recibo por módulo resolveria.
- **`_allowed` deixa o JEV trocar a ordem.** Ele pode pôr `add_regression_case` antes de `audit_review_findings`. É aceitável, porque o conselho é consultivo e passa por auditoria do Manager.

**Não verificável daqui**

- Digests de produto, elenco e runner.
- Execução real das suítes, das 28 mutações e dos 6 casos do parser Markdown. O script de mutação e o harness não foram incluídos.
- O conteúdo do wrapper.
- A escrita sintética e as provas Codex citadas no elenco.
- A existência do gate humano da R3 e o tamanho deste pacote frente ao teto.
- Conduta real de LLM e comportamento pós-release.
- Qualquer benefício do JEV.

## VEREDITO

APROVADO_COM_RESSALVAS
