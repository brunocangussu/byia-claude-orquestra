# T-045 — piloto do Cartographer

**Estado:** concluído e validado pelo dono · **frente:** `@frente-cartographer` · **host:** Codex.

## Por que existe

O Cartographer v2 oferece quatro capacidades potencialmente úteis ao Orquestra: briefs delimitados,
verificação de frescor, auditoria de remoção e medição de adoção graph-first. O grafo em si se
sobrepõe a codebase-memory e Serena; o piloto precisa provar valor incremental, não apenas que a CLI
funciona.

O Planner externo não foi executado porque esta sessão não dispõe de delegação autorizada. O Manager
produziu este plano diretamente, preservando o gate do dono.

## Abordagens consideradas

1. **Copiar apenas as ideias:** menor risco e nenhuma dependência, mas não mede a qualidade real dos
   algoritmos. É o fallback se o piloto não demonstrar ganho.
2. **CLI v2 isolada e fixada por SHA — recomendação:** roda apenas no clone temporário, escreve em
   diretório descartável e é comparada com o stack atual. Não instala plugin, MCP ou comando global.
3. **Instalar Cartographer como MCP/plugin:** integração rápida, porém cria duas fontes de grafo,
   aumenta o runtime obrigatório e mistura o fluxo legado Claude com o multi-host. Rejeitada nesta
   fase.

## Pergunta do spike

Em pelo menos duas das três capacidades únicas — `brief`, `audit removal` e `adoption` — o
Cartographer entrega evidência útil que o stack Serena + codebase-memory não entrega com custo igual
ou menor?

## Restrições invioláveis

- Fixar o upstream no SHA `a62d16981b6aa1f5f6ef56701c49b81a16a8e30a`.
- Sem instalação global, MCP, alteração de hooks, cache do Orquestra, commit, push ou publicação.
- Sem `annotate`, OpenRouter ou qualquer chamada que envie código a terceiro.
- Rodar somente em clones/cópias descartáveis; nenhum projeto de produção recebe `.cartographer/`.
- Excluir credenciais, dumps, PII, dados clínicos e qualquer artefato gerado por usuário.
- A wiki/board do Orquestra continua sendo a única memória canônica.
- A ambiguidade MIT × Apache-2.0 bloqueia incorporação ou redistribuição de código, mas não a
  avaliação local read-only.

## Plano reduzido aprovado

Depois da pesquisa pública, o piloto foi reduzido: não há comparativo independente direto entre
Cartographer, codebase-memory e Serena; os três publicam avaliações próprias contra built-ins ou
fixtures. Como codebase-memory e Serena já cobrem grafo, navegação e refatoração, testar essas áreas
novamente não pagaria o custo.

### A/B 1 — auditoria de remoção

Criar fora do produto uma fixture pequena e determinística com TypeScript, Python, Shell, SQL,
GitHub Actions, variável de ambiente e uma feature removível. Registrar antes o gabarito: entry
points, dependências, testes afetados e todas as referências que a remoção precisa encontrar.

Comparar Cartographer, codebase-memory e Serena pelo mesmo gabarito. Serena só recebe tarefas dentro
do seu escopo semântico; referências textuais/configuração que ela não pretende cobrir são
registradas como “fora de escopo”, não como falha.

### A/B 2 — brief e adoção

Dar a mesma tarefa de investigação ao Cartographer e ao codebase-memory; usar Serena para o recorte
por símbolo. Medir cobertura do gabarito, tamanho do retorno, chamadas e tempo. Exercitar `adoption`
com dois traces sintéticos — graph-first e leitura-direta-primeiro — e avaliar se essa prova tem
valor que o Orquestra ainda não possui.

### Gate de decisão

Não haverá fase em projeto real nesta autorização. Ao final, o Manager recomenda adotar
opcionalmente, portar somente a ideia útil ou descartar. Qualquer teste posterior em repo real volta
ao gate do dono.

## Métricas registradas

| Métrica | Critério mínimo |
|---|---|
| precisão contra gabarito | 100% das âncoras críticas; zero falso negativo na remoção sintética |
| brief delimitado | até 4.000 tokens e todos os arquivos obrigatórios presentes |
| indexação | inicial até 2 min; incremental até 15 s no alvo médio |
| frescor | toda mutação controlada torna `verify --fresh` não-verde |
| isolamento | zero arquivo fora do diretório temporário |
| privacidade | zero rede e zero segredo/PII nos artefatos |
| valor incremental | ganho exclusivo claro em `audit removal` ou `adoption`; o grafo sozinho não conta |

Tempos absolutos são guardrails locais, não benchmark universal. Também registrar CPU, tamanho do
SQLite, tokens do pacote retornado e falsos positivos.

## Decisão ao final

- **ADOTAR OPCIONAL:** wrapper CLI opt-in, fixado por SHA, apenas para briefs/audits/adoption.
- **PORTAR IDEIAS:** implementar no Orquestra os gates úteis sem depender do Cartographer.
- **DESCARTAR:** nenhum ganho material sobre Serena + codebase-memory.

Mesmo em “adotar”, o Cartographer não vira dependência para o Orquestra funcionar e não substitui
wiki, board, Serena ou codebase-memory.

## Riscos e critérios de parada

- Parar se houver rede inesperada, escrita fora do sandbox, artefato com segredo ou necessidade de
  ativar OpenRouter.
- Parar a incorporação enquanto README/package continuarem divergindo sobre licença.
- Parar se a cobertura de Markdown/Shell tornar o Gate 2 pior que o stack atual.
- Não ajustar o gabarito depois de ver a saída; isso invalidaria a comparação.

## Checkpoint de recuperação — 2026-08-29

- A compactação ocorreu depois da autorização do dono e antes da criação da fixture.
- Memória, board e esta thread foram relidos; o escopo aprovado permanece inalterado.
- O diretório temporário reservado é `/tmp/orq-t045-cartographer.T3q3l8`.
- Próxima ação concreta: criar o gabarito imutável e a fixture sintética, então executar A/B 1 e A/B 2.
- Este checkpoint é somente documental: não exige `/clear`, não bloqueia a task e não autoriza integração.

## Resultado medido — 2026-08-29

Fixture congelada antes das ferramentas: 16 arquivos no commit temporário
`1d50179cd702d565a9221abe5499f05e11584377`; gabarito SHA-256
`b16889b31406f8463c7092bc9cb6740e016521622f65b6db01c0ba38edcb27ca`. O alvo tinha 13
âncoras críticas e uma nota histórica que deveria permanecer.

| Caminho | Cobertura crítica | Histórico marcado como ativo | Custo observado |
|---|---:|---:|---|
| Cartographer `audit removal` + brief por ledger | 11/13 | sim | index 0,11 s; audit 0,03 s; brief 0,04 s |
| codebase-memory, busca literal + símbolo + callers/export | 12/13 | sim | index 0,17 s; pacote canônico de 5 chamadas ~0,59 s |
| stack atual completo, incluindo fallback `rg` para config/literais | 13/13 | sim | 1 chamada; 0,007 s |
| Serena | não pontuada | não pontuada | host preso ao projeto da sessão e sem ativação da fixture exposta |

O Cartographer perdeu `src/checkout.ts` e `src/index.ts`, que dependiam do símbolo sem repetir o
literal. O codebase-memory encontrou ambos pelo grafo, mas não retornou `package.json`; o fallback
textual previsto no stack atual fechou a lacuna. O Cartographer também classificou
`docs/history.md` como documentação ativa e ingeriu o próprio `GROUND_TRUTH.json` como hit
desconhecido. Logo, o gate de 100% e zero falso negativo não passou.

O brief ancorado no ledger ficou dentro do limite (2.664 tokens estimados, 15.440 bytes), porém
repetiu 11/13, incluiu o histórico e sugeriu somente `bun run test`, omitindo as validações de
ambiente, CI, banco e deploy declaradas no gabarito. O ledger formal é útil como recibo estruturado,
mas sua classificação não superou o fluxo atual nesta fixture.

O teste `adoption --require-graph-first` passou para o trace que executou preflight antes da leitura
e falhou com exit 1 para o trace que leu fonte primeiro. Essa é a única capacidade incremental
confirmada: prova mecânica da ordem de adoção, não melhor descoberta de código.

Isolamento preservado: `.cartographer/` ficou somente em `/tmp`, com 292 KiB e SQLite de 253.952
bytes; API keys foram removidas do ambiente dos comandos e nenhum recurso de rede/LLM foi invocado.
O clone upstream não recebeu mudança rastreada e `orq/` teve diff vazio. O único untracked do clone,
`graphify-out/`, é anterior ao piloto (timestamps de 17:58–18:04; execução começou às 21:50) e foi
preservado.

## Parecer

**PORTAR IDEIAS.** Não instalar Cartographer nem adicioná-lo como dependência. Se o dono quiser
continuar, abrir um card separado e pequeno para estudar dois conceitos sem copiar código:

1. ledger de remoção com gabarito explícito e classes verificáveis;
2. verificador de disciplina graph-first baseado nos eventos que o Orquestra já registra.

A ambiguidade de licença e a cobertura inferior bloqueiam incorporação. Um teste em repositório real
continua fora desta autorização.

## ⏭️ RETOMAR AQUI

Concluído: o dono respondeu “prossiga”, validando **PORTAR IDEIAS**. O follow-up é T-048; nenhuma
instalação ou integração do Cartographer foi autorizada.
