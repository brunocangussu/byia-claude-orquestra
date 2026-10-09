# T-150 — avaliação do lançamento Haiku 5.5

**Consulta:** 2026-10-07, noite de 07→08; identidade confirmada pelo dono em
08/10. **Estado:** pesquisa e proposta;
zero inferências Haiku, nenhuma adoção, nenhuma branch ou frente adicional.

## Resultado

**Vale preparar um piloto seletivo; não vale substituir o Sonnet nas tarefas
moderadas por padrão ainda.** O dono confirmou que o nome falado era
**Claude Haiku 5.5**, em 08/10. A proposta é exclusiva do Host Claude:
implementer/docs/scout no Host Codex continuam OpenAI, sem trigger, troca
de vendor, fallback ou chamada Haiku durante implementação Codex.

O Haiku é apresentado como auxiliar para operações curtas/repetitivas e
subagentes. Na tabela publicada, Terminal-Bench 4.0 tem 39,2% para Haiku e
70,6% para Sonnet; FrontierCode tem 46,4% e 52,1%, respectivamente. São
resultados do fornecedor, não testes nesta Orquestra, nem garantia por tarefa.
[Anúncio Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5).

## Economia: quatro preços diferentes

Valores publicados por milhão de tokens, no modo padrão de API:

| Modelo | Entrada sem cache | Saída | Leitura de cache |
|---|---:|---:|---:|
| Haiku 5.5, prompt até 100 mil tokens | US$ 0,10 | US$ 0,50 | US$ 0,01 |
| Haiku 5.5, prompt acima de 100 mil | US$ 0,50 | US$ 2,50 | US$ 0,05 |
| Sonnet 5.5 | US$ 2,00 | US$ 10,00 | US$ 0,10 |
| Opus 5.5 | US$ 4,00 | US$ 20,00 | US$ 0,20 |

O anúncio de 07/10 reduziu a leitura de cache do Sonnet de US$ 0,20 para
US$ 0,10; portanto, a comparação não usa o preço anterior do lançamento.
Fontes: [Haiku/preços atualizados](https://www.anthropic.com/claude-haiku-5-5),
[Opus](https://www.anthropic.com/claude/opus) e
[catálogo oficial](https://platform.claude.com/docs/en/about-claude/models/overview).

Inferência própria: para entrada/saída sem cache até o limiar, o preço unitário
Haiku é 20 vezes menor que o Sonnet; acima do limiar, quatro vezes menor.
Isso não significa gastar 20 vezes menos na assinatura Max. Os preços acima
são de API; consumo da assinatura, eventual cobrança extra e crédito de API
são coisas distintas. Não consultamos faturamento nem inferimos um multiplicador
da quota da conta. O uso de subagentes também consome recursos.
[Custos no Claude Code](https://code.claude.com/docs/en/costs).

Também não significa usar menos tokens: um modelo barato pode consumir mais
passos ou demandar retrabalho. A comparação correta é o custo de todas as
tentativas, revisão, correção e eventual escalada **até o aceite**, não apenas
o preço da primeira resposta. Tempo de conclusão e regressões são métricas
separadas. Contexto herdado desnecessário pode atravessar o limiar de preço;
briefing curto e delimitado continua importante mesmo com janela grande.

### Conta offline até o aceite — não é teste do modelo

Tarifas reconferidas na [tabela atual de preços](https://platform.claude.com/docs/en/about-claude/pricing).
Aritmética determinística registrada em `docs/T-150-haiku55-auditoria-local.json`;
nenhuma inferência, faturamento, chave ou conta foi consultado.

| Exemplo sintético | Tokens de entrada sem cache / cache / saída | Haiku por chamada | Sonnet por chamada |
|---|---|---:|---:|
| Prompt de 10 mil | 5.000 / 5.000 / 1.000 | US$ 0,00105 | US$ 0,02050 |
| Prompt de 120 mil | 20.000 / 100.000 / 3.000 | US$ 0,02250 | US$ 0,08000 |

Fórmula: `(entrada_sem_cache × tarifa_entrada + cache_lido × tarifa_cache +
saída × tarifa_saída) / 1.000.000`. O segundo exemplo usa o degrau acima
de 100 mil tokens do Haiku. São tokenizações arbitrárias iguais entre modelos,
não uma previsão de quantos tokens os dois gastariam em um trabalho real.
Não inclui escrita de cache, ferramentas, batch, modo rápido ou retrabalho.

Se o custo da mesma revisão independente cross-vendor for `R`, uma tentativa
Sonnet custa `CS + R`; duas tentativas Haiku que precisem de duas revisões
custam `2×CH + 2×R`. A segunda opção passa a custar mais quando
`R > CS − 2×CH`: **US$ 0,01840** no exemplo curto e **US$ 0,03500** no longo.
Não cotamos o reviewer nem trocamos o vendor de revisão do Host Claude.
Se as correções locais não exigirem nova revisão, o resultado é diferente.
Isso é análise de sensibilidade, não frequência observada de falhas.

A consequência prática é testar primeiro tarefas determinadas e pacotes
pequenos. A economia de uma chamada não basta para promover o Haiku nas
moderadas, nem pode ser convertida em economia da assinatura Max.

## Sugestão por papel no Host Claude — candidata, não ativa

| Papel | Sugestão para o piloto |
|---|---|
| Manager | Modelo da sessão escolhido pelo dono; não trocar |
| planner·interface | Preservar a direção da fábrica: Opus 5.5/high |
| planner·sistema | Preservar Sol 6.1/xhigh pela via comprovada |
| implementer·leve | Haiku 5.5/medium candidato, somente desenho fechado e baixo risco |
| implementer·normal | Manter Sonnet 5.5/medium |
| implementer·pesada | Manter Sonnet 5.5/high; qualquer outra promoção exige escolha/prova |
| reviewer | Preservar Sol 6.1/xhigh, vendor oposto ao host |
| docs | Haiku 5.5/low candidato para atualização determinada por fatos conferidos |
| scout | Haiku 5.5/medium candidato para investigação read-only delimitada |

Esta tabela é recomendação do Manager, não adoção. Faixa mede risco e desenho
aberto, não quantidade de linhas. Haiku não recebe autenticação, permissões,
schema/migração, entrega Git ou decisões de segurança porque o diff é pequeno.
Nas moderadas, podemos comparar Haiku/medium com Sonnet/medium em casos fechados;
não promover o Haiku por benchmark do fornecedor ou por um smoke que apenas passa.

A documentação atual anuncia effort ajustável no Haiku e `medium` como
padrão. Os valores propostos acima ainda precisam de prova na via realmente
usada pelo papel; catálogo, help e disponibilidade anunciada não são recibo.
[Modelo/effort no Claude Code](https://code.claude.com/docs/en/model-config).

## O que falta tecnicamente

1. Identidade confirmada pelo dono: Haiku 5.5. Isso não comprova modelo
   efetivo, effort, escrita ou qualidade; falta o piloto delimitado.
2. A fábrica 0.31.0 ainda sugere Sonnet 5.5 para as três faixas, docs e scout
   Claude. O elenco vivo deste repo é legado e preservado: `sonnet` e planner
   de interface `fable`. Sugestão versionada não atualiza sessões abertas.
3. O runner parametrizado aceita `claude-opus-5-5` explicitamente; seu alias
   `haiku` ainda espera `claude-haiku-4-5` em `modelUsage`
   (`orq/scripts/run-opus-reviewer.py:35`). Não anunciar suporte exato 5.5 por
   esse runner, mudar prefixos silenciosamente ou relaxar a guarda de identidade.
   O piloto de writer no Host Claude deve usar sua via nativa, não transformar
   este runner read-only em implementer.
4. Compor catálogo e testes somente para o Host Claude, sem alterar os
   implementers/docs/scout OpenAI do Host Codex. Mudança no pacote,
   adoção por projeto e ativação prática são gates distintos. A seção ativa
   do Host Claude e sua worktree continuam intactas nesta avaliação.

**Inspeção local adicional, somente leitura:** Claude CLI 2.1.290; `--version`
e `--help` saíram 0 e anunciam `--model`/`--effort`. Não houve chamada ao
modelo, e help não comprova identidade efetiva, effort ou qualidade.
O mapa do runner da fonte mantém Haiku 4.5; `claude-haiku-5-5` não está nele.
Sua guarda de alias desconhecido recusa antes de ler o briefing ou lançar
processo (`run-opus-reviewer.py:283`). Não foi feito um probe para reproduzir
essa recusa. Manter a guarda é o comportamento correto; uma mudança de suporte
precisa de plano/testes próprios, não de um fallback silencioso para 4.5.

**Ensaio offline posterior, 08/10:** o `main()` do runner foi invocado com
argumentos controlados e stdin/resolução de CLI/launchers mockados. O ID
`claude-haiku-5-5` retornou exit 2 antes de leitura ou criação de processo;
os quatro contadores ficaram em zero. A função de identidade também recusou
5.5 para o alias legado e preservou 4.5 datado. Recibo:
`docs/T-150-haiku55-compatibilidade-offline.json`. São testes da guarda,
não chamada ao modelo, disponibilidade, escrita ou qualidade do Haiku.
O piloto no Host Claude continua usando sua via nativa; não transferir essa
limitação do runner read-only para o writer ou para os modelos do Codex.

## Comparação proposta, ainda não executada

Usar três grupos: mudança mecânica com testes claros; bug moderado com caso
vermelho e critérios fechados; busca/documentação com resposta verificável.
Adicionar controles de alto risco que devem ser recusados/escalados, não
implementados pelo modelo leve. Oráculos ficam fora dos briefings.

Cada modelo recebe o mesmo contexto e critérios, em checkouts descartáveis;
ordem alternada e mais de uma réplica. Medir: testes/oráculo, escopo respeitado,
erros de segurança, chamadas, tokens, latência, correções e custo até aceite.
Revisão cega independente, sem expor o modelo na nota. Distinguir preço API
estimado de débito observado na assinatura; sem dado observado, não alegar
economia de quota. Falha de capacidade encerra somente a operação dependente,
sem retry ou fallback silencioso.

A futura autorização deve nomear os modelos/efforts, pacotes sanitizados,
quantidade por braço, teto agregado, destino e ferramentas permitidas. A R2
e a R3 do T-150 **não** autorizam estas chamadas. Nada foi enviado ao Haiku
ou ao JEV. A confirmação do nome não é autorização de inferência ou adoção.

**Recomendação final:** introduzir Haiku primeiro como auxiliar e implementer
leve opt-in; manter Sonnet nas moderadas até evidência comparativa. Preservar
o reviewer independente e o Manager único. Esta pesquisa não altera o snapshot
revisto pela R3. A R3 é terminal e recebeu APROVADO_COM_RESSALVAS sobre
esse snapshot; não avaliou o Haiku. Esta pesquisa não consome nem cria
autorização para outra revisão ou para o piloto Haiku.
