# Plano — T-080 (guarda: preset `padrao` × tabela viva)

> Planejado pelo planner·sistema (job Codex `task-mtpuur24-nx0gtw`), auditado pelo Manager.
> ⚠️ **Procedência não comprovada:** o runtime não expôs a variante nem o effort — não há prova
> de que rodou como `gpt-6-astra@max`. Sabe-se apenas que foi Codex/OpenAI, base GPT-6.

## Procedência (diga qual modelo de fato rodou esta análise)

Análise feita por **Codex/OpenAI, baseado em GPT-6**, nesta sessão. A interface não expõe comprovação da variante e do effort executados; a configuração `gpt-6-astra@max` no elenco não serve como prova de execução.

Confirmei `main`, HEAD `7f64adcaa81ab88c4a79145cbde963c668999775`. **Nenhum arquivo foi editado.**

Há uma correção de procedência: a thread T-079 registra a separação deste card, mas o rascunho detalhado de aceite está em [docs/plano_T-079-elenco-astra.md:349](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/docs/plano_T-079-elenco-astra.md:349>).

Executei o lint atual: **exit `1`**, com um único diagnóstico, `bytes:commands/checkpoint.md`, na comparação com o cache `0.27.0`. Essa falha permanece fora do T-080.

## Respostas às cinco perguntas

1. **Qual é a semântica de “Perfil ativo”?**

   A linha declara **qual preset é a base da tabela daquele host e quais substituições estão vigentes sobre essa base**. Não identifica agentes já em execução.

   O formato completo atual está em [orq/commands/elenco.md:314](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/elenco.md:314>):

   ```markdown
   **Perfil ativo:** `padrao` — desde <data de hoje>, sem desvio.
   ```

   A nota seguinte admite `padrao · desvio: papel→modelo`, mas não define separador para múltiplos papéis nem exemplifica data junto dos desvios. Proponho completar o contrato com:

   ```markdown
   **Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: docs→haiku; scout→haiku.
   ```

   O separador será **ponto e vírgula**. A forma abreviada já documentada, `padrao · desvio: papel→modelo`, continuará aceita. A data será metadado; `<data de hoje>` será permitido somente no template. Espaços laterais e formatação Markdown não alterarão a comparação.

   Para os oito papéis, sejam `A` os modelos ativos, `P` os modelos do preset selecionado e `D` os desvios declarados:

   - **Sem desvio:** exigir `A = P`.
   - **Com desvios:** exigir que `D` seja **exatamente** o conjunto `papel→A[papel]` para os papéis em que `A[papel] ≠ P[papel]`.

   Portanto, desvio legítimo passa; diferença não declarada, valor declarado diferente do ativo e desvio que já deixou de existir reprovam. Isso segue o comando, que manda remover o desvio quando o papel volta ao preset.

2. **E quando o perfil ativo é `economia`?**

   Comparar a tabela Claude com **`economia`**, aplicando a mesma regra de desvios. Isso concretiza a instrução existente de comparar com o preset **ativo**, em `elenco.md:190`.

   O `padrao` inativo continua sujeito à validação estrutural: tabela completa, papéis únicos, modelos preenchidos e ausência de `manager`. Seus modelos não serão comparados com a tabela que está em economia.

   Perfil declarado sem preset correspondente será erro explícito, nunca motivo para ignorar a guarda.

3. **E o host Codex sem presets?**

   **Não se aplica a comparação de perfis.** A seção Codex e sua linha explicativa “este host não tem presets” não serão interpretadas como uma declaração de perfil inválida.

   O vínculo entre `## Perfis` e Host Claude será respeitado. A existência dessa seção no mesmo arquivo não atribui presets ao Codex. Um `_elenco.md` somente de Codex, sem perfis, deve ser aceito por esta guarda.

   Diferentemente disso, desaparecer o preset ou a linha ativa de uma configuração Claude sujeita ao contrato deve gerar diagnóstico: ausência não pode desarmar a validação silenciosamente.

4. **Onde a guarda mora?**

   Será uma **nova validação semântica de perfis**, em `lint-coerencia.py`, integrada a `main()` junto das verificações do elenco.

   As estruturas existentes têm outros propósitos:

   | Estrutura real | Responsabilidade atual |
   |---|---|
   | `CONTRATOS_CODEX` — linha 844 | Presença de fragmentos normativos |
   | `VOCABULARIO_EXTINTO` — linha 1102 | Proibição de instruções aposentadas |
   | `REVIEWER_CLAUDE`, `REVIEWER_CODEX`, `REVIEWER_POR_HOST` — linha 931 | Titulares e separação dos reviewers no template |
   | `TABELAS_DE_PAPEL`, `ESPERADO_HOST`, `ESPERADO_PRESET` — linha 986 | Conjunto e multiplicidade dos papéis |

   Nenhuma delas representa igualdade entre mapas condicionada ao perfil ativo. Acrescentar frases a `CONTRATOS_CODEX` não provaria essa propriedade.

   A nova função — **a criar** — seguirá o contrato existente de `validate_hooks` e `validate_codex_consultive_language`: retornar problemas como `(Path, linha, mensagem)`. `main()` acrescentará esses problemas a `problemas`; o encerramento existente já retorna `1` quando há falhas.

5. **Vale para o projeto e para o template?**

   **Sim, separadamente dentro de cada documento.**

   Confirmei oito papéis comparáveis e nenhuma divergência atual nos dois pares:

   | Documento | Implementers ativos e no próprio `padrao` |
   |---|---|
   | Projeto, `_elenco.md` | `sonnet / sonnet / sonnet` |
   | Template de fábrica | `opus / sonnet / haiku` |

   Essa diferença entre projeto e fábrica é válida. A guarda não deve uniformizar as escolhas.

   O template será validado dentro do bloco Markdown de `## Modelo do arquivo`. O projeto será lido nominalmente por essa validação, sem acrescentar todo `_elenco.md` à varredura de vocabulário nem ampliar a varredura de `memory/`.

## Plano (passos numerados, arquivo e linha onde souber)

1. **Preparar a implementação isolada após o gate.** Partir de `7f64adc` em worktree próprio. Registrar o diagnóstico atual do T-075 e preservar as alterações da outra frente, incluindo `checkpoint.md` e `stack.md`. Não copiar o checkout compartilhado inteiro como se fosse uma candidata limpa.

2. **Escrever primeiro a regressão observável.** Criar o módulo proposto `orq/scripts/test_elenco_perfis.py`. Seguir os padrões reais de [test_context_guard.py:56](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/test_context_guard.py:56>): importação via `importlib.util`, `unittest`, fixtures temporárias e captura do resultado de `main()`.

   A primeira prova será uma fixture completa e coerente que altera **somente** `implementer·pesada` no preset do projeto, de `sonnet` para `opus`. Exigir exit `1` e diagnóstico específico. Antes da guarda, a fixture deve retornar `0`, fazendo a asserção falhar. Não aceitar como RED um erro de importação, ausência da função nova ou falha de cache.

   Usar isolamento de `Path.home()` **somente no teste**, conforme o precedente de `run_lint_main` em `test_context_guard.py:1978`, para não depender do cache real.

3. **Fechar a gramática documental.** Em `orq/commands/elenco.md:314`, documentar as duas formas completas, múltiplos desvios separados por `;`, significado do valor após `→` e remoção de desvios resolvidos. Em [_elenco.md:157](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/_elenco.md:157>), manter a referência ao contrato canônico, sem criar uma segunda especificação. Preservar os modelos atuais.

4. **Implementar extração estrutural e comparação.** Usar como base os auxiliares reais de [lint-coerencia.py:87](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/lint-coerencia.py:87>): `_mascara_cercas`, `secoes_de`, `secao_unica` e `_linha_unica`.

   O extrator novo deve:
   
   - Resolver `### Host Claude` dentro de `## Times por host`, e os presets dentro de `## Perfis` daquele host.
   - Reconhecer os nomes `padrao` e `economia` independentemente dos subtítulos descritivos, que diferem entre projeto e fábrica.
   - Exigir unicidade de seções, linha ativa, tabelas e papéis; não escolher silenciosamente a primeira ocorrência.
   - Extrair as duas primeiras células, preservando linha de origem. `papeis_da_tabela` hoje extrai apenas a primeira célula; sozinho não resolve a comparação.
   - Normalizar apenas apresentação. Alias e `@effort` continuam significativos; a terceira coluna não participa.
   - Excluir `manager` da comparação e rejeitá-lo nos presets e nos desvios.

   Mascarar exemplos cercados antes de ler linhas e tabelas. No template, remover primeiro a cerca externa canônica: mascará-la antes disso esconderia todo o documento a validar.

5. **Integrar os dois alvos em `main()`.** Acrescentar a chamada perto das guardas de papéis, após [lint-coerencia.py:988](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/lint-coerencia.py:988>), reutilizando `ESPERADO_PRESET`.

   Aproveitar `template_elenco`, cuja extração começa na linha 807, tornando explícitas a seleção única do bloco canônico e sua posição no arquivo para os diagnósticos. Ler nominalmente `memory/wiki/_elenco.md` quando existir. Erros de estrutura ou leitura devem retornar problemas, sem traceback.

   Exemplo de diagnóstico esperado:

   ```text
   memory/wiki/_elenco.md:267 Host Claude, perfil padrao: implementer·pesada — ativo=sonnet; preset=opus; diferença sem desvio declarado
   ```

6. **Completar a matriz de testes e registrar a evidência RED→GREEN.** Cobrir os casos abaixo no novo módulo. Usar testes diretos da nova validação para combinações pequenas e testes de `main()` para comprovar que a guarda foi efetivamente conectada ao comando.

7. **Coordenar versão e executar os gates.** Propor `0.27.1`, condicionado à autorização e à versão disponível quando a frente integrar. Atualizar atomicamente os quatro anchors: manifesto, [README.md:413](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/README.md:413>), `memory/MEMORY.md:7` e `.claude-plugin/marketplace.json:12`.

   Durante o desenvolvimento, o módulo novo pode rodar isoladamente por descoberta. Na candidata integrada, são obrigatórios:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'
   claude plugin validate ./orq --strict
   python3 orq/scripts/lint-coerencia.py .
   ```

   Rodar os três também sobre a fonte limpa da candidata, conforme [CLAUDE.md:47](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/CLAUDE.md:47>). Não remover a guarda de cache nem transformar o vermelho do checkout compartilhado em aprovação global.

8. **Revisar e validar o comportamento distribuído.** O review deve procurar ambiguidades de parsing e contradições entre documentação e guarda. Após release autorizado, cumprir verificação dos caches a partir da fonte limpa e teste comportamental com `economia → padrao`. Registrar restauração dos oito papéis, preservação de `manager` e limpeza dos desvios; o fechamento depende da validação do dono.

## Critérios de aceite

| Caso | Resultado exigido |
|---|---|
| Projeto e fábrica atuais, cada qual coerente | Nenhum diagnóstico T-080 |
| Um único implementer alterado somente no preset | Exit `1`; arquivo, linha, host, perfil, papel, ativo e preset identificados |
| Alteração somente na tabela viva, ainda “sem desvio” | Reprova |
| Um desvio legítimo ou vários desvios legítimos | Passa |
| Um desvio legítimo acompanhado de outra diferença não declarada | Reprova |
| Desvio com valor errado, papel desconhecido, repetido ou já igual ao preset | Reprova |
| `sem desvio` junto de declaração de desvios | Reprova |
| `economia` ativo e tabela correspondente | Passa na nova guarda; não compara valores contra `padrao` |
| Perfil ativo inexistente; linha ativa ausente ou ilegível onde exigida | Diagnóstico explícito |
| Papel ausente, duplicado ou intruso; modelo vazio | Reprova |
| `manager` alterado na tabela ativa | Não afeta igualdade dos oito papéis |
| `manager` inserido em preset ou desvio | Reprova |
| Mudança somente em justificativa, espaçamento ou crases | Não cria divergência de modelo |
| Host Codex sem presets | Sem falso positivo e sem exceção |
| Heading, tabela ou linha ativa falsos dentro de exemplo | Não satisfazem a guarda |
| Mutação no template ou no projeto | Cada superfície é detectada independentemente |
| Candidata final | Suíte completa, validate e lint com exit `0` |

**Melhorias sobre o rascunho:** comparar com o perfil ativo evita falso positivo em economia; validar exatamente os desvios impede que uma exceção esconda diferenças adicionais; exigir estrutura válida impede que apagar ou deformar a declaração desligue a guarda; testar as duas superfícies impede regressão na fábrica; comprovar RED com diagnóstico específico evita confundir o T-075 com evidência do T-080.

## Riscos e ambiguidades

- **Múltiplos desvios e data estavam subespecificados.** O plano resolve isso com gramática e exemplos canônicos, sem delegar uma decisão técnica ao dono.
- **As guardas `REVIEWER_*` fixam os titulares do template.** Os testes completos de ativação de economia devem alterar o elenco do projeto, preservando a fábrica em `padrao`. A nova comparação pode ser exercitada isoladamente com economia nas duas superfícies, sem relaxar a guarda independente dos reviewers.
- **Coerência não comprova autorização histórica.** Alterar tabela e preset juntos pode produzir um estado coerente, porém contrário à escolha do dono. Também não há referência suficiente para reconhecer modelos antigos num `padrao` alterado enquanto está inativo. Esse limite precisa ficar declarado: o T-080 verifica consistência declarada, não substitui aprovação de mudanças.
- **O lint não executa a troca de perfil.** A preservação efetiva do manager e a restauração pelo comando continuam exigindo teste comportamental após o release.
- **A frente T-075 continua concorrente.** Testes isolados provam o T-080; não autorizam declarar o checkout compartilhado inteiro verde.

## Decisões que faltam ao dono

**Nenhuma decisão de produto ou negócio permanece aberta.** O plano resolve parsing, economia, Codex, integração e cobertura das duas superfícies.

Implementação, bump e publicação continuam sujeitos aos gates do projeto. Nesta análise houve somente leitura e execução do lint existente.


