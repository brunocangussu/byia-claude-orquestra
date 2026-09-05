# Plano aprovado — T-079 (GPT-6 Astra no elenco e Fable 5.1 nomeado)

> Planejado pelo planner·sistema (job Codex `task-mtoliuvx-w9pjqp`, sessão `01a07245`), auditado
> pelo Manager e **aprovado pelo dono em 2026-09-05**. Texto do planner, íntegro, a partir daqui.

## Procedência

Esta tarefa foi processada pelo **Codex, da família GPT-5 (OpenAI)**. O ambiente não expõe o identificador mais específico da variante desta sessão.

A chamada ao Fable descrita abaixo foi um subprocesso real, usado como sonda; não foi o modelo que elaborou este plano.

Nenhum arquivo foi editado.

## ⛔ ERRATA — ler antes de executar (Manager, 2026-09-05)

O plano abaixo afirma, no Passo 0/Riscos, que **"Astra não aceita `@ultra`"**. **Isso é falso.** O
planner generalizou a partir da mensagem de erro de um teste com `none`, que devolveu lista parcial.

O estado do Codex do dono (`~/.codex/.codex-global-state.json`) declara, por modelo:

```
gpt-6-astra   -> low, medium, high, xhigh, max, ultra
gpt-5.6-sol   -> low, medium, high, xhigh, max, ultra
gpt-5.6-terra -> low, medium, high, xhigh, max, ultra
gpt-5.6-luna  -> low, medium, high, xhigh, max          (sem ultra)
```

Consequências obrigatórias para quem implementa:

1. **O valor `gpt-6-astra@max` continua valendo** — decisão do dono em 2026-09-05, tomada **com o
   `ultra` disponível na frente dele**. Não é limitação técnica.
2. **Nunca escrever, em nenhum arquivo, que o Astra não aceita `ultra`**, nem que presets antigos
   "precisam usar no máximo `@max`". Se precisar justificar o `@max`, escreva: *escolha do dono em
   2026-09-05; `ultra` está disponível e não foi adotado*.
3. **O preset `padrao` com `gpt-5.6-sol@ultra` NÃO era inexecutável.** O plano supõe isso ao
   corrigi-lo; a correção continua (o modelo muda para Astra), mas **sem** essa justificativa.

---

## Passo 0 — prova real do alias fable

Este gate foi executado agora, antes de qualquer alteração no prefixo:

```bash
printf '%s' \
  'Não leia arquivos nem use ferramentas. Responda somente FABLE_REAL_OK.' |
python3 orq/scripts/run-opus-reviewer.py \
  --model fable \
  --timeout 600
```

Resultado observado:

```text
exit: 0
stdout: FABLE_REAL_OK
OPUS_MODEL=claude-fable-5-1
OPUS_MODEL_USAGE=claude-fable-5-1,claude-haiku-4-5-20251001
```

Aprovação do gate exige simultaneamente:

- exit `0`;
- stdout não vazio;
- `MODEL_ALIAS=fable` no início da execução;
- `OPUS_MODEL` iniciado por `claude-fable-5-1`;
- `OPUS_MODEL_USAGE` contendo pelo menos um modelo iniciado por `claude-fable-5-1`.

A presença adicional de `claude-haiku-4-5-20251001` no `modelUsage` não invalida a prova: o modelo atribuído pelo runner foi literalmente `OPUS_MODEL=claude-fable-5-1`, e o contrato atual aceita usos auxiliares desde que o prefixo solicitado esteja comprovado.

Ramo obrigatório de falha:

- Se o alias resolver para `claude-fable-5`, `claude-fable-5-0` ou qualquer valor que não comece por `claude-fable-5-1`, parar o T-079 antes de editar `MODEL_ALIASES`.
- Não alargar o prefixo para fazer a sonda passar e não documentar Fable 5.1 como executável.
- Registrar o `modelUsage` literal na thread e devolver o card ao dono para escolher entre atualizar a CLI/cache Anthropic, usar um identificador explícito comprovado ou manter temporariamente o contrato anterior.
- Se ocorrer autenticação vencida, timeout, erro de processo ou saída vazia, não fazer retry automático após a chamada iniciada. Registrar a capacidade como não comprovada e parar.

Como o valor real observado foi `claude-fable-5-1`, o ramo aprovado deste plano pode endurecer o verificador.

## Plano

1. Endurecer a prova do Fable com TDD.

   Arquivos:

   - [test_run_opus_reviewer.py](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/test_run_opus_reviewer.py:123>)
   - [run-opus-reviewer.py](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/run-opus-reviewer.py:29>)

   Alterações:

   - Adicionar `test_rejects_fable_5_0_when_fable_5_1_is_required`, invocando `--model fable` com:
   
   ```python
   FAKE_EXPECT_MODEL="fable"
   FAKE_MODEL="claude-fable-5-0"
   ```

   - Antes da implementação, esse teste deve falhar porque o prefixo atual `claude-fable-5` aceita 5.0.
   - O resultado final deve exigir exit `7`, `OPUS_MODEL_MISMATCH`, mensagem `esperado claude-fable-5-1` e stdout vazio.
   - Apertar a asserção de `test_proof_is_per_alias_not_hardcoded_to_opus`: verificar o prefixo completo `claude-fable-5-1`, não apenas o substring largo `claude-fable-5`.
   - Preservar o teste positivo existente com `FAKE_MODEL=claude-fable-5-1`.
   - Alterar `MODEL_ALIASES["fable"]` para:

   ```python
   "fable": "claude-fable-5-1",
   ```

   - Atualizar a descrição do `argparse` na linha 58 para “parecer comprovado do modelo Anthropic”.
   - Preservar `run-opus-reviewer.py`, `DEFAULT_MODEL_ALIAS="opus"` e os códigos/prefixos `OPUS_*`, que são compatibilidade deliberada.

2. Atualizar o elenco ativo do projeto.

   Arquivo: [_elenco.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/_elenco.md:38>).

   Alterações:

   - Nas linhas 38–45, retirar “runner de Opus fixo”. A regra passa a aceitar somente aliases presentes no mapa de prova, sempre executados com `--model <alias>` e validados pelo prefixo correspondente.
   - Em `## Revisores externos`, linhas 63–66:
     - via `codex`: manter `planner·sistema` e `reviewer` do host Claude e registrar `gpt-6-astra@max`;
     - via `runner-opus`: retirar `planner·interface` de `Consumida por` e manter apenas `host Codex: reviewer`;
     - registrar a sonda real de `--model fable` e a prova `claude-fable-5-1`.
   - Na Matriz, linhas 117–120:
     - Anthropic×Codex continua usando o runner com `--model <alias>` e prova específica;
     - OpenAI×Claude passa a citar `gpt-6-astra@max`;
     - registrar o smoke já realizado do Astra com `low|medium|high|xhigh|max` e a rejeição de `none`.
   - Na tabela Host Claude:
     - `planner·interface`: manter `fable`, identificado como Claude Fable 5.1;
     - `planner·sistema`: `gpt-6-astra@max`;
     - `reviewer`: `gpt-6-astra@max`;
     - manter implementers, docs e scout.
   - Na tabela Host Codex:
     - `planner·interface`: `gpt-6-astra@max`;
     - `planner·sistema`: `gpt-6-astra@max`;
     - `reviewer`: manter `fable`, identificado como Fable 5.1 e invocado com `--model fable`;
     - manter implementers, docs e scout.
   - Declarar que, no host Codex, as duas trilhas passam a usar Astra: a trilha continua governando classificação e cerimônia, mas deixa de escolher vendor ou executor diferente.
   - Atualizar `### Pendências comprováveis`: Astra e os efforts estão comprovados; o comportamento em um Loop A completo ainda depende do primeiro uso real.
   - Corrigir o preset `padrao` para espelhar a tabela ativa Claude:
     - Fable 5.1 em `planner·interface`;
     - Astra `@max` em `planner·sistema` e `reviewer`;
     - três implementers em `sonnet`;
     - docs e scout em `sonnet`.
   - Em `economia`, substituir os dois `gpt-5.6-sol@high` por `gpt-6-astra@high`, preservando os demais valores.
   - Essa correção dos valores do preset permanece no T-079. O que fica fora é somente a criação de uma nova guarda automatizada de igualdade.

3. Corrigir a regra canônica e o template de fábrica.

   Arquivo: [elenco.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/elenco.md:78>).

   Alterações:

   - Linhas 82–85: substituir “runner de Opus fixo” pelo contrato real pós-T-077.
   - Linhas 111–115: retirar “no Codex a trilha interface só aceita opus” e atualizar o exemplo OpenAI para `gpt-6-astra@max`.
   - Linhas 166–178: reescrever “Vendor certo não basta” para preservar a proteção correta:
     - o runner precisa conhecer o alias;
     - o consumidor precisa passar `--model <alias>`;
     - o JSON precisa comprovar o prefixo daquele alias;
     - pedir Fable e receber Opus ou Fable 5.0 reprova;
     - alias desconhecido continua recusado antes da chamada.
   - No template Host Claude, usar Fable 5.1 em interface e Astra `@max` em planner·sistema/reviewer.
   - No template Host Codex, usar Astra `@max` nas duas trilhas e Fable 5.1 no reviewer.
   - Manter os demais papéis do template sem alteração.
   - No template de `Revisores externos`, retirar `planner·interface` dos consumidores de `runner-opus` e registrar a prova por alias.
   - Na Matriz do template, acrescentar `--model <alias>` à chamada Anthropic×Codex.
   - Atualizar os presets de fábrica:
     - `padrao`: Astra `@max`;
     - `economia`: Astra `@high`;
     - Fable sempre identificado como 5.1.

4. Fazer o reviewer executar o modelo declarado no elenco.

   Arquivo: [revisar.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/commands/revisar.md:69>).

   Alterações:

   - Nas linhas 85–115, substituir “titular é o Opus 5” pelo modelo Anthropic resolvido da linha `reviewer`; no elenco atual, Fable 5.1.
   - Extrair o alias do valor do papel e passá-lo explicitamente:

   ```bash
   REVIEWER_MODEL_ALIAS="<alias resolvido da linha reviewer>"
   OPUS_RUNNER="<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py"
   OPUS_OUT=$(
     printf '%s' "$OPUS_BRIEFING_SANITIZADO" |
       python3 "$OPUS_RUNNER" --model "$REVIEWER_MODEL_ALIAS"
   )
   OPUS_EXIT=$?
   ```

   - Nunca chamar o runner sem `--model`: isso cairia no default Opus e repetiria a contradição atual.
   - Tornar a prova dependente do alias; para `fable`, exigir `claude-fable-5-1`.
   - Preservar limite de 16 KiB, timeout de 600s, stderr, ausência de retry automático e política `REVISÃO DEGRADADA`.

5. Reconciliar a skill e a documentação viva.

   Arquivos:

   - [SKILL.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/skills/orq/SKILL.md:96>)
   - [README.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/README.md:167>)
   - [arquitetura.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/wiki/arquitetura.md:118>)
   - [orq/stack.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/stack.md:201>)
   - [memory/MEMORY.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/MEMORY.md:64>)

   Alterações:

   - Na skill, substituir “comando do Opus” por “comando do modelo Anthropic”, exigindo o alias vindo da Matriz; nomear Fable 5.1 no exemplo do elenco.
   - No README:
     - retirar a alegação de que interface Codex só aceita Opus;
     - atualizar tabela Claude, exemplos, vias e resumo do host Codex;
     - documentar Astra nas duas trilhas Codex e Fable 5.1 no reviewer;
     - substituir “o Opus roda pelo runner” por modelo Anthropic escolhido por `--model`;
     - corrigir o resumo da linha 431.
   - Em `arquitetura.md`, descrever o runner como via Anthropic parametrizada e registrar que o reviewer Codex atual é Fable 5.1.
   - Em `orq/stack.md`, trocar a comprovação fixa de `claude-opus-5` por comprovação do prefixo do modelo selecionado; para o elenco atual, `claude-fable-5-1`.
   - Em `memory/MEMORY.md`, atualizar o estado corrente e registrar as provas reais de Astra e Fable. Registros históricos permanecem intactos.

6. Atualizar o custo e o significado do perfil `economia`.

   Arquivos: `_elenco.md`, `orq/commands/elenco.md` e README.

   Registrar somente fatos comprovados:

   - Astra: US$ 10/MTok de entrada e US$ 50/MTok de saída.
   - Fable 5.1: aproximadamente 25% abaixo do Fable 5; não derivar preço absoluto sem fonte verificada.
   - `economia` é perfil de crédito e esforço, não garantia de menor custo total:
     - Astra cai de `@max` para `@high`;
     - implementer leve, docs e scout usam degraus menores;
     - planner·interface continua mudando de Fable 5.1 para Opus por decisão anterior do dono.

7. Atualizar apenas as guardas de lint pertencentes ao T-079.

   Arquivo: [lint-coerencia.py](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/scripts/lint-coerencia.py:844>).

   Alterações:

   - Atualizar os fragmentos obrigatórios para:
     - reviewer Claude `gpt-6-astra@max`;
     - reviewer Codex `fable`/Fable 5.1;
     - `revisar.md` contendo `--model` na chamada do runner;
     - runner contendo `claude-fable-5-1`.
   - Atualizar `REVIEWER_CLAUDE` e `REVIEWER_CODEX`, preservando a checagem host-ancorada que impede autorrevisão de vendor.
   - Acrescentar proibição das instruções falsas “runner de Opus fixo” e “no Codex só aceita opus” nas superfícies vivas.
   - Preservar o nome `run-opus-reviewer.py`, o default Opus e os códigos `OPUS_*`.
   - **Não** adicionar neste card guarda que compare a tabela Host Claude com o preset `padrao`.
   - **Não** transformar a divergência antiga dos implementers em requisito automatizado do T-079.

8. Fazer o bump atômico para `0.27.0`.

   Os quatro pontos, e somente eles:

   - [orq/.claude-plugin/plugin.json](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/orq/.claude-plugin/plugin.json:5>)
   - [README.md — Status](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/README.md:410>)
   - [memory/MEMORY.md](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/memory/MEMORY.md:7>)
   - [.claude-plugin/marketplace.json](</Users/brunocangucu/Projetos DEV - Cursor/byia-claude-orquestra/.claude-plugin/marketplace.json:12>)

   Os quatro entram no mesmo commit das alterações em `orq/`.

   Commit sugerido:

   ```text
   feat(0.27.0): atualiza elenco para astra e fable 5.1
   ```

   Não publicar, instalar, fazer push ou afirmar “publicada” sem a autorização e as evidências posteriores.

## Critérios de aceite

- A prova real do Passo 0 está registrada com:

```text
exit 0
OPUS_MODEL=claude-fable-5-1
OPUS_MODEL_USAGE contendo claude-fable-5-1
```

- Teste focado:

```bash
PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest discover -s orq/scripts -p 'test_run_opus_reviewer.py'
```

Deve provar:

- Fable 5.1 aceito;
- Fable 5.0 recusado com exit `7`;
- Fable solicitado e Opus recebido recusado;
- alias desconhecido recusado antes de chamar a CLI;
- default Opus e contratos `OPUS_*` preservados.

- Estado documental final:

  - Host Claude: interface Fable 5.1; sistema e reviewer Astra `@max`.
  - Host Codex: interface e sistema Astra `@max`; reviewer Fable 5.1.
  - Reviewer continua sempre do vendor oposto.
  - `runner-opus` é consumido somente pelo reviewer Codex.
  - Via `codex` continua consumida por planner·sistema e reviewer Claude.
  - Toda chamada do runner originada por `revisar.md` contém `--model`.
  - O preset `padrao` está materialmente reconciliado com a tabela Claude.
  - Nenhuma guarda nova de igualdade tabela↔preset foi adicionada ao lint.
  - Implementer, docs e scout permanecem nos modelos aprovados para cada host.

- Três gates obrigatórios:

```bash
PYTHONDONTWRITEBYTECODE=1 \
python3 -m unittest discover -s orq/scripts -p 'test_*.py'

claude plugin validate ./orq --strict

python3 orq/scripts/lint-coerencia.py .
```

Todos devem sair com exit `0`.

- Verificações auxiliares:

```bash
git diff --check
```

Além disso, o diff deve ser auditado para confirmar que registros históricos não foram reescritos e que os quatro anchors de versão estão em `0.27.0`.

- Depois de release autorizado:

  - verificar os caches Claude e Codex contra fonte detached limpa;
  - abrir sessão nova ou reiniciar cada host;
  - comprovar por linguagem natural a resolução dos planners/reviewers;
  - no host Codex, confirmar novamente que o reviewer usa `--model fable` e produz `OPUS_MODEL=claude-fable-5-1`;
  - aguardar validação explícita do dono antes de DONE.

## Riscos e ambiguidades

- O `modelUsage` real trouxe também `claude-haiku-4-5-20251001`. A prova do Fable permanece válida porque o runner atribuiu `OPUS_MODEL=claude-fable-5-1`; a documentação não deve alegar que o Fable foi o único modelo presente no payload.
- O arquivo e os códigos ainda se chamam `opus`. Renomeá-los quebraria um contrato deliberadamente preservado e está fora do T-079.
- O catálogo local pode não mostrar Astra embora `codex exec -m gpt-6-astra` funcione. O card não deve editar caches globais nem prometer presença no seletor visual.
- Astra não aceita `@ultra`; qualquer preset antigo copiado mecanicamente precisa usar no máximo `@max`.
- Alterar o mapa sem corrigir `revisar.md` deixaria o problema central intacto: o consumidor continuaria chamando o default Opus.
- O checkout está em `main` e contém alterações concorrentes em arquivos de memória. A implementação precisa usar isolamento e reconciliar alterações recentes, sem sobrescrever arquivos inteiros.
- “Três células” no pedido original enumera quatro combinações papel×host. A matriz explícita da thread governa: são quatro células Astra.

## Card novo a abrir

**Título sugerido:** `Perfil padrao pode divergir da tabela ativa sem o lint detectar`.

Defeito: a alteração de 2026-09-03 unificou os três implementers Claude em `sonnet` na tabela ativa, mas o preset `padrao` permaneceu `opus|sonnet|haiku`, enquanto a linha declarava `padrao — sem desvio`. O T-079 corrige os valores atuais, mas não elimina a causa sistêmica que permitiu a divergência.

Por que importa: uma futura ativação de `perfil padrao` pode reintroduzir modelos antigos silenciosamente, e a declaração “sem desvio” pode mentir mesmo com suíte, validate e lint verdes.

Critério de aceite do novo card:

- o lint compara as oito linhas papel→modelo do preset `padrao` com a tabela Host Claude, excluindo `manager`;
- a comparação é aplicada quando o perfil ativo declara `padrao — sem desvio`;
- uma fixture que altere somente um implementer no preset deve fazer o lint sair diferente de zero com diagnóstico que nomeie papel, valor ativo e valor do preset;
- desvio explicitamente registrado não deve ser confundido com inconsistência;
- o repositório reconciliado deve continuar passando os três gates.

Esse card recebe a guarda automatizada. O T-079 recebe somente a reconciliação dos valores necessária para o elenco aprovado.

## Decisões que faltam ao dono

Nenhuma decisão bloqueante para executar o T-079 após a aprovação deste plano.

O Manager precisa apenas criar e priorizar separadamente o card da guarda tabela↔preset. Uma eventual reformulação da composição do perfil `economia` para garantir menor custo monetário também seria outro pedido de produto, não parte deste card.

