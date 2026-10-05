# T-098 — JEV na Orquestra: decisão antes de implementação

Data: 2026-09-22. Escopo: estudo, sem integração, chamada à TypeSafe ou alteração do roteamento.
Estado: análise concluída, com parecer real `gpt-6-astra@max` (exit 0), auditado pelo Manager.
Evidência integral: [parecer Astra](parecer_T-098-astra.md). Não equivale a teste de JEV.

**Atualização após o pedido do dono:** a avaliação agora inclui **maior assertividade a custo
aceitável**, não só economia. O piloto sintético foi executado com regras locais, Opus 5.5 e,
em 24/09, Jev 1.13.0 real: 22/24 acertos, 8/8 alto risco preservados, sem integração. Protocolo,
limitações do gabarito, resultados e simulação econômica em
[comparação de custo e assertividade](plano_T-098-benchmark.md). A recomendação abaixo é o parecer
anterior preservado, não uma conclusão de que JEV não possa ser útil.

## Decisão recomendada

**Não implementar o roteador JEV agora.** A ideia é tecnicamente compatível como classificador
auxiliar, mas o primeiro investimento recomendado é concluir a migração Opus 5.5 e medir onde há
desperdício acionável. Se regras locais/Manager resolverem o problema, não acrescentar dependência.

Isso revisa a recomendação inicial de começar diretamente por um POC shadow: o Astra apontou que
até esse POC pode medir apenas rótulos sem consequência econômica. Primeiro precisamos de um
baseline e de alternativas efetivas de execução. Adoção do JEV permanece uma hipótese posterior.

O parecer propôs, como exemplo negociável, piso de 20% de ganho no recurso limitante e preparação
inicial de até um dia. **Não são benchmark, compromisso nem critérios aprovados pelo dono.**

## 1. Pergunta correta

Não basta perguntar se o JEV classifica tarefas. Precisamos provar que uma decisão dele muda uma
ação executável da Orquestra e reduz **custo por tarefa aceita**, preservando qualidade e limites
de risco, melhor que regras locais e que o julgamento que o Manager já faz.

Escolher um modelo mais barato pode reduzir preço por token e ainda aumentar o total de tokens,
chamadas e retrabalho. Esses efeitos não se confundem. Também não há, neste estudo, medida de
quanto da cota atual do dono é consumida por cada papel.

## 2. O que o produto oferece de fato

A documentação da TypeSafe descreve JEV como modelo de decisão estruturada: Choice, Score e Noul.
Não gera código, não conversa e não substitui a LLM de um coding agent. Um programa consumidor
precisa transformar suas respostas em ações. O caso de intent routing se parece com a proposta,
mas não oferece uma tabela comprovada de qual LLM resolve melhor cada card da Orquestra.

O `jev-1.13.0` custa US$ 0,042/MTok de entrada e não cobra saída. **Exemplo hipotético:** mil
decisões com 2.000 tokens de entrada cada custariam US$ 0,084. Isso exclui processamento adicional,
resumos produzidos por outra LLM, operação, avaliações e erros de roteamento.

Há riscos de contexto adversarial, literalidade, números e critérios contraditórios. Inglês é a
língua mais forte declarada; PT-BR precisa de avaliação própria. A confiança da resposta deriva
da concentração das probabilidades, não é, por si, probabilidade calibrada de sucesso da tarefa.
Não treinar com requests/responses não equivale a retenção zero; ZDR é citado para enterprise.

Fontes oficiais:

- https://docs.typesafe.ai/introduction/coding-agents
- https://docs.typesafe.ai/models
- https://docs.typesafe.ai/patterns/intent-routing
- https://docs.typesafe.ai/confidence
- https://docs.typesafe.ai/model-jaggedness/jev-1.13
- https://docs.typesafe.ai/legal

## 3. Onde a economia poderia existir — e onde não existe

O Manager recebe a mensagem no Codex antes de poder chamar ferramentas. Se Astra já processou o
histórico, a chamada ao JEV **não recupera esse custo**. Para economizar a primeira decisão do
Manager seria necessário roteamento anterior ao modelo, controlado pelo host/harness. Não se deve
prometer que uma skill muda automaticamente a LLM da sessão viva.

Depois da primeira decisão ainda é possível reduzir trabalho futuro: dimensionar workers,
escolher effort, limitar contexto enviado, evitar delegação sem valor e reduzir retrabalho. Porém:

- Host Codex: os três implementers são Terra/xhigh; planners de ambas as trilhas são Astra/max.
- Host Claude: os três implementers ativos são Sonnet.
- A escala já permite trivial sem spawn e fluxo reduzido para pequeno; isso não depende de JEV.
- O reviewer independente é política, não opção que o classificador pode retirar.
- Os históricos T-054 e T-094 já distinguem redução de contexto, sondas sintéticas e benefício real.
  Não reiniciar esses experimentos nem chamar uma sonda de modelo de prova de economia.

Assim, classificar como leve/normal/pesada sem mudar um executor elegível ou o trabalho necessário
é **mudar o rótulo**, não a conta. Primeiro é preciso demonstrar quais decisões são realmente
acionáveis e quais modelos/efforts alternativos já têm capacidade comprovada na via utilizada.

## 4. Alternativas e ordem de comparação

| Alternativa | Custo incremental | Vantagem | Limite |
|---|---|---|---|
| Regras locais + catálogo aprovado | Sem chamada de modelo | Auditável; risco/autoridade fora da IA | Casos semânticos ambíguos exigem Manager |
| Manager atual escolhe o papel/effort | Já processa o pedido; decisão pode acrescentar saída/raciocínio | Conhece contexto e restrições | Não reduz tokens já gastos pelo próprio Manager |
| Classificador LLM menor separado | Nova chamada e novo contexto | Flexibilidade, ecossistema conhecido | Pode custar mais que regras e errar em risco |
| JEV auxiliar | Inferência muito barata; nova API/retenção/operação | Julgamentos estruturados e frequentes | Precisa de calibração, catálogo e prova de ganho incremental |

Não começar pelo quarto sem medir os dois primeiros. Um desenho fixo de planner forte + executor
forte + revisor forte também não é obrigatório para todo pedido: a disciplina existente já separa
casos triviais. A hipótese interessante é **adaptar capacidade dentro da política**, não removê-la.

## 5. Impacto de migrar Fable para Opus 5.5

A tabela oficial apresenta Fable 5.1 a US$ 10/50 por MTok entrada/saída e Opus 5.5 a US$ 4/20.
Para volumes iguais, o novo preço é 40% do anterior: redução de 60%. Não implica 60% menos tokens,
nem 60% menos mensalidade. A Anthropic recomenda Opus 5.5 para a maioria dos workloads e reserva
Fable para raciocínio exigente/long-horizon quando as avaliações com Opus não bastarem.

A migração é uma otimização independente do JEV. Depois de realizada, a avaliação do roteador tem
que comparar contra o **baseline já com Opus 5.5**, não contra o Fable antigo: caso contrário,
atribuiríamos ao roteador a economia produzida pela troca de modelo.

Fonte: https://platform.claude.com/docs/en/models/overview

## 6. Experimento mínimo proposto, ainda não autorizado

1. Selecionar amostra curta de cards concluídos, sanitizados e estratificados por risco/tipo.
   Usar apenas informação disponível **antes** da execução; não vazar solução ou veredito final
   para a entrada do roteador. Calibração e avaliação separadas por card/família, não por trecho.
2. Medir o baseline atual e uma política local simples com catálogo fechado. Registrar qual ação
   mudaria; separar casos em que todos os rótulos levariam ao mesmo executor.
3. Só se houver oportunidade residual, testar JEV offline/shadow com autorização de egress e
   limite de gasto/chamadas. Descrições mínimas; nenhum código, credencial, PII ou dado de paciente.
4. Medir concordância e erros de subdimensionamento, latência, abstenção e decisões acionáveis.
   **Shadow não prova qualidade do trabalho nem economia realizada**, apenas recomendações.
5. Para provar ganho, executar amostra pareada em checkouts isolados, avaliando resultados contra
   critérios de aceite e testes independentes. Medir input/cache/output/raciocínio conforme o
   runtime disponibilizar, repetição de trabalho, revisões, tempo e intervenção humana.
6. Comparar custo por tarefa **aceita**, não por chamada ou por classificação correta. Fixar
   perguntas, modelo e thresholds antes do conjunto reservado; relatar incerteza, não apenas média.

Nenhum alvo numérico de precisão/economia foi aprovado ou medido. Uma amostra sem erro crítico
não prova segurança universal. O dono define tolerância e piso de ganho antes de abrir o holdout.

## 7. Contenção mínima caso a hipótese sobreviva

Um adaptador opcional, desligado por padrão, não um serviço novo obrigatório. Regras locais
aplicam risco/privacidade/autoridade; JEV sugere uma categoria de um catálogo fechado; código valida
a resposta e o Manager resolve a execução pela Matriz. Saída não é comando de shell nem permissão.
Falha, dúvida ou baixa confiança preserva o caminho seguro vigente, sem downgrade e sem trocar de
vendor. Modelo indisponível também não autoriza fallback silencioso.

Não adicionar nesta hipótese: daemon, banco de memória, hook global, autoatualização de modelo,
reinício de sessão ou eliminação de aprovação/review. Não enviar histórico integral para decidir
que um card simples é simples.

## 8. Regra de decisão econômica

Economia líquida = custo evitado nas execuções futuras − classificação − contexto adicional −
retrabalho adicional − custo de manter/validar a integração.

Em assinatura fixa, o ganho primário é capacidade/tempo antes do limite, não queda automática da
fatura. Cotas de vendors distintos não devem ser somadas como se fossem equivalentes. Melhor uso
da assinatura Claude não compensa necessariamente esgotamento do Codex, e vice-versa.

Abandonar JEV se regras/Manager obtiverem resultado equivalente, se quase nenhuma classificação
mudar uma ação, se o ganho desaparecer após contabilizar retrabalho ou se exigir infraestrutura
desproporcional. Considerar adoção apenas se superar o baseline simples em benefício mensurável,
qualidade preservada, privacidade aceitável e custo operacional limitado.
