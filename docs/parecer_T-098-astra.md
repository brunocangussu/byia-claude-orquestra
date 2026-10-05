# Parecer T-098 — Astra

Execução real de `gpt-6-astra`, effort `max`, via `codex exec`, sandbox read-only, em clone
isolado de `a82a35f`. Sessão `01a0ca17-fad0-7f11-91e1-b518183c4624`, 22/09/2026, exit 0.
O parecer usa fatos oficiais selecionados pelo Manager; não é um benchmark do JEV. Caminhos no
texto abaixo apontam para o clone utilizado. Conteúdo do parecer preservado sem edição.

1. **Veredito: não implementaria Jev como roteador econômico agora.**

   O benefício ainda é uma hipótese; integração, manutenção e revisão seriam custos certos. A Orquestra já classifica tarefas, distingue cerimônias e resolve modelos por papel. Falta demonstrar que decisões ruins de roteamento consomem uma parcela relevante da cota.

   Jev pode produzir classificações estruturadas baratas. Isso não demonstra que saiba escolher o modelo mais econômico **capaz de entregar aquela tarefa com qualidade**. O experimento sintético de sugestão de skills não estabelece essa competência.

   Primeiro mediria o desperdício evitável com as regras e o Manager existentes. Só consideraria Jev se sobrasse um problema econômico concreto.

2. **O que pode ser economizado — e o que já foi gasto.**

   São potencialmente evitáveis: planejamento completo em tarefas legitimamente pequenas, contexto redundante nas próximas chamadas, delegações desnecessárias, esforço excessivo em trabalhos determinados e repetições além dos limites existentes. A revisão independente continua obrigatória nos casos previstos.

   Há um limite decisivo: **as três faixas usam Terra@xhigh no Codex e Sonnet no Claude**. No Codex, as duas trilhas de planejamento também usam Astra@max. Portanto, trocar apenas a classificação frequentemente não troca modelo nem esforço. O [elenco atual](/private/tmp/orq-astra-t098.Vvdjre/source/memory/wiki/_elenco.md:182) explicita essa situação.

   O processamento já realizado pelo Astra e o histórico já consumido são custos incorridos. Um roteador consultado depois não os recupera. Pode reduzir chamadas futuras, mas preparar seu resumo e interpretar sua resposta também custa. Histórico reenviado nas próximas chamadas continua sendo custo futuro; reduzir isso exige gestão de contexto, não apenas classificação.

3. **Comparação das alternativas.**

   | Alternativa | Vantagem | Limite e avaliação |
   |---|---|---|
   | Regras locais | Previsíveis, auditáveis, sem chamada de inferência adicional | Melhor ponto de partida para pisos de risco, casos determinados e resolução do elenco. |
   | Manager existente | Já possui contexto e interpreta ambiguidades | Pode exagerar a cerimônia; corrigir critérios e exemplos tende a custar menos que outro componente. |
   | Pequeno LLM | Pode interpretar linguagem variada e explicar decisões | Acrescenta chamada, latência e erros. Ser barato não demonstra competência para selecionar outros modelos. |
   | Jev | Saída enumerada e preço de entrada muito baixo | Exige critérios claros; tem limitações em PT-BR, indirection e ambiguidades. Probabilidade concentrada não equivale a acerto calibrado. |

   Minha preferência atual é **regras existentes aplicadas pelo Manager**, com classificação incorporada à etapa que ele já executa. Um classificador externo precisa superar esse baseline, não apenas parecer barato isoladamente.

4. **Desenho mínimo seguro, caso a hipótese sobreviva.**

   A classificação continuaria usando `escala + trilha + faixa`, com o elenco existente como fonte única de resolução. Um eventual adaptador sem estado receberia um resumo curto, sanitizado, com objetivo, critérios de aceite, riscos conhecidos e alternativas permitidas; devolveria uma recomendação enumerada ou abstenção.

   As restrições seriam verificadas localmente: Manager permanece Astra; alto risco mantém piso `pesada`; aprovações e independência da revisão permanecem obrigatórias; papéis respeitam host e mecanismos autorizados. Classificação desconhecida, conflito ou falha retorna à decisão conservadora do Manager. Uma resposta confiante não autoriza rebaixamento.

   O adaptador teria uma chamada limitada, versão fixa e registro curto da decisão. Cálculos de preço e orçamento seriam determinísticos. O classificador não receberia autoridade para editar, executar ferramentas ou alterar políticas.

   Como não treinar com requests não equivale a ZDR, qualquer experimento usaria somente material permitido e sanitizado. Se preparar esse material exigir quase toda a análise do Astra, essa despesa entra integralmente na conta.

5. **Avaliação empírica em PT-BR.**

   O baseline principal deve ser a Orquestra **após a troca aprovada para Opus5.5**, mantendo constantes políticas, modelos e critérios. Compararia regras locais, julgamento normal do Manager, pequeno LLM e Jev sobre os mesmos dados disponíveis no momento da decisão.

   Separaria desenvolvimento e holdout **por card**, mantendo também revisões e cards quase duplicados na mesma partição. Usar o histórico completo de um card para prever sua dificuldade inicial vazaria a solução. A amostra incluiria tarefas típicas, casos ambíguos e erros caros: segurança descrita como “ajuste simples”, dependências escondidas, negações, números, contexto irrelevante e instruções adversariais.

   Avaliaria PT-BR original. Traduzir para inglês seria outra variante, com custo e falhas próprios. Concordância com o Manager mede reprodução da classificação, não qualidade objetiva nem optimalidade econômica.

   **Classificação em sombra não prova qualidade da execução.** Ela permite medir estabilidade, divergências, abstenções e violações de política. Para medir economia real, seria necessário executar alternativas numa amostra isolada, com condições comparáveis, e avaliar entregas sem revelar qual roteador as escolheu.

   Mediria: aceite, testes pertinentes, defeitos posteriores, retrabalho, escaladas, rodadas de revisão, tokens/cota por vendor, tempo humano e latência até entrega aceita. Neste repositório, incluiria ambiguidades, contradições e referências inexistentes: testes automatizados não cobrem toda a qualidade das instruções.

   Subestimar alto risco teria peso muito maior que exagerar cerimônia. Reportaria incerteza e distribuição dos resultados; zero erros críticos numa amostra pequena não demonstra segurança geral. Também contabilizaria o custo de produzir os resumos e da própria avaliação.

6. **Critérios de abandonar ou adotar; próximos passos delimitados.**

   Abandonaria a integração se as decisões não alterarem chamadas reais, se regras simples obtiverem resultado equivalente, se a vantagem desaparecer após contabilizar retrabalho ou se a segurança depender de reler tudo com Astra. Violação de piso de risco ou aprovação bloquearia adoção.

   Adotaria somente diante de ganho líquido repetido em holdout, qualidade preservada e retorno compatível com o volume real de cards. **Como critério proposto, não benchmark**, poderia exigir redução de pelo menos 20% no consumo do recurso limitante por entrega aceita, com limite prévio para piora de latência e retrabalho.

   A sequência seria: concluir a migração já escolhida; inventariar consumo por papel e repetição; identificar decisões realmente econômicas; testar primeiro regras e Manager. Só depois caberia um experimento Jev delimitado.

   Proponho limitar a preparação inicial a um dia de trabalho. Evidência insuficiente produziria “inconclusivo”, sem justificar automaticamente uma integração ou meses de aperfeiçoamento.

7. **Economia de API e economia de assinatura são contas diferentes.**

   Na API, calcula-se gasto efetivo com entrada, saída, cache, tentativas e chamadas auxiliares. **Exemplo hipotético:** 10 mil requests Jev com 3 mil tokens de entrada cada custariam US$1,26, usando o preço informado no briefing. Isso mostra que sua inferência é barata; não paga automaticamente engenharia e manutenção.

   Nas assinaturas, menos tokens não implica redução proporcional da mensalidade. O benefício pode ser mais cards concluídos antes do limite, menos interrupções ou evitar gastos adicionais. É preciso observar o consumo e os limites efetivos, separadamente em Claude e Codex.

   A métrica econômica principal deve refletir o gargalo do dono: **entregas aceitas por cota disponível, com tempo humano e retrabalho contabilizados**.

8. **A troca Fable → Opus5.5 reduz o espaço econômico disponível ao Jev.**

   Pelos preços fornecidos, Opus5.5 custa **60% menos na entrada e na saída**, para volumes iguais, antes de outras diferenças de faturamento. É uma economia potencial de API nos papéis afetados, não de toda a operação nem necessariamente da assinatura.

   Se Opus5.5 atender à maioria dessas tarefas, uma escolha estática já captura parte importante da vantagem antes atribuída ao roteador. Jev precisaria demonstrar economia adicional sobre esse novo baseline, preservando os casos que exigem raciocínio superior.

   No Codex atual, Fable nem aparece nos papéis ativos descritos: predominam Astra, Terra e Opus. Portanto, o impacto direto depende do host e do papel realmente usado. **A prioridade de investimento é medir e simplificar o fluxo existente após a migração; Jev permanece uma hipótese posterior, com ônus de demonstrar retorno.**
