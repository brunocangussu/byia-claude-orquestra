# T-138 — Agency Agents: especialidades opcionais sob controle da Orquestra

Data: 2026-09-24. Investigação read-only; nenhuma instalação ou execução de script externo.
Revisão pública examinada: `053ddbbf392a1688fc7043d81529f47ef2cf86c8`, obtida por `git ls-remote`.
A API de metadados do GitHub respondeu 403; isso não impediu fixar o SHA e ler arquivos raw nesse SHA.

## Veredito

**Vale testar como fonte de perfis especializados, não adotar como outro orquestrador.**
O ganho possível é melhorar critérios de trabalho e aceite do executor, enquanto JEV ajuda a
classificar o pedido. Nenhum dos dois, isoladamente, prova qual LLM fará a melhor entrega.
As instruções são hipóteses a medir; personalidade e alegações de experiência não conferem
treinamento, ferramentas, memória persistente ou competência comprovada a um modelo.

## O que existe e o que isso significa aqui

O repositório reúne perfis Markdown, exemplos e conversores/instaladores para vários hosts.
A [integração Codex](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/integrations/codex/README.md)
declara TOMLs em `~/.codex/agents/`, com nome, descrição e corpo integral do Markdown em
`developer_instructions`. O instalador também permite selecionar agentes/divisões; não é
necessário importar o catálogo inteiro. Não executei conversor, instalador ou aplicativo.

Esse formato não equivale ao ciclo da Orquestra nem garante o contrato de invocação, versão do
modelo, effort, sandbox ou revisão cross-vendor. Copiar instruções integrais para o host pode
introduzir regras concorrentes com prioridade operacional. A adaptação deve ocorrer **antes**
da instalação, não depender de um aviso genérico “ignore conflitos” em tempo de execução.

| Camada | Responsabilidade proposta | O que não decide |
|---|---|---|
| Orquestra | Autoridade, estado do card, orçamento, capacidade da via, isolamento e revisão | Não trata confiança do classificador como aprovação |
| JEV | Sugere natureza, risco, domínio e necessidade de esclarecer | Não concede permissão, lança agentes ou troca o elenco |
| Perfil especializado | Acrescenta critérios/checklist de uma especialidade | Não escolhe vendor, encerra card ou muda teto de tentativas |
| LLM | Executa o papel e o escopo explicitamente autorizados | Não transforma a persona em capacidade verificada |

**Inferência de arquitetura:** essas camadas são complementares se a saída do JEV for uma
sugestão validada pelo Manager e por política explícita, e se apenas o perfil escolhido for
carregado. Não é funcionalidade existente na Orquestra nem prova de integração com Agency.

## Conflitos concretos encontrados

1. **Segundo Manager e multiplicação de chamadas.** O
   [Agents Orchestrator](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/specialized/agents-orchestrator.md)
   propõe pipeline autônomo, Dev/QA por tarefa e tentativas próprias. Isso pode recriar exatamente
   a proliferação de subagentes que o projeto controla por card. Há ainda tensão interna: exige
   todas as tarefas aprovadas antes de avançar, mas a seção de falhas manda continuar após bloquear
   uma tarefa. **Não importar esse perfil.**
2. **Dados reais e promoção automática.** O
   [Autonomous Optimization Architect](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/engineering/engineering-autonomous-optimization-architect.md)
   sugere testes em dados reais e promoção autônoma de modelos. Traz ideias úteis de limites e
   avaliação prévia, mas essas duas orientações não são autorizadas aqui. Não usar como roteador
   vivo nem como política de fallback: falha de acesso/orçamento não autoriza novo fornecedor.
3. **Revisão com exigência inadequada ao artefato.** O
   [Reality Checker](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/testing/testing-reality-checker.md)
   exige screenshots para certificação e tende a reprovar por padrão. Evidência é útil; exigir
   imagem para um contrato de CLI ou presumir defeito sem cenário concreto aumenta falso positivo
   e retrabalho. Não substitui o reviewer independente da Orquestra.
4. **Expansão não pedida.** O
   [API Tester](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/testing/testing-api-tester.md)
   inclui carga, monitoramento de produção e metas genéricas, como latência e cobertura fixas.
   Nada disso deve virar requisito de um card pequeno por ativar a especialidade. Selecionar só
   os critérios pertinentes e usar os limites aprovados para aquele projeto.
5. **Custo de contexto e sobreposição.** Os perfis examinados têm exemplos, identidade e workflows
   extensos; carregar vários pode custar mais que a decisão do JEV. Já existem skills de frontend,
   testes e segurança neste ambiente. O comparador correto é o fluxo atual **com** esses recursos,
   não um assistente artificialmente privado deles. Medir tokens do perfil e da seleção também.

## Candidatos limitados — não ativos

| Candidato | Material útil para um perfil enxuto | Restrição |
|---|---|---|
| API Tester | Contratos, compatibilidade, erros e casos de fronteira | Começar com respostas fictícias locais; sem carga, rede ou produção |
| Accessibility Auditor | Teclado, foco, semântica e evidência por barreira | Apenas tarefas de UI; não aplicar ao repositório CLI por padrão |
| Application Security Engineer | Fronteiras de confiança, fluxo de dados e testes de regressão | Mantém piso de alto risco, escopo autorizado e reviewer independente |

Fontes dos dois últimos:
[Accessibility Auditor](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/testing/testing-accessibility-auditor.md) e
[Application Security Engineer](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/security/security-appsec-engineer.md).
Também foram inspecionados Frontend Developer e Test Automation Engineer; não os incluir no
primeiro lote evita duplicar especialidades já disponíveis sem benefício adicional medido.

Um perfil candidato precisa ser um suplemento de escopo fechado, não agente com lifecycle próprio:
identificador, SHA de origem, critérios selecionados, exclusões e teto de contexto. Um perfil por
execução; nenhum subagente adicional apenas para interpretar a persona. Na proposta inicial,
limite de 600 tokens adicionais medidos pelo tokenizer da via; não é limite implementado hoje.

A [licença da revisão examinada](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/LICENSE)
é MIT e exige preservar o aviso de copyright/licença em cópias ou porções substanciais.
Nenhum perfil foi copiado para o produto. Uma adoção futura deve fixar SHA, conservar atribuição
e revisar atualizações; sem auto-update global de instruções.

## Como medir sem atribuir o ganho à peça errada

Primeiro resolver a rubrica do T-098, antes de selecionar executor. Depois, um ensaio 2×2:

| Grupo | Seleção do executor | Instruções de trabalho |
|---|---|---|
| A | Regra explícita congelada | Orquestra e recursos atuais |
| B | Sugestão JEV validada pelas mesmas regras de autoridade | Idênticas a A |
| C | Mesma seleção de A | A + um perfil especializado enxuto |
| D | Mesma seleção de B | B + o mesmo perfil de C |

- A/B isolam a seleção; A/C isolam o perfil. Só comparar A/D confundiria os dois efeitos.
- Usar o mesmo catálogo de modelos/vias elegíveis, prompts de tarefa, base e aceite. Selecionar
  uma vez por tarefa e manter o mesmo executor nos pares A/C e B/D; não rerotear após ver resultados.
- Orquestra e modelo permanecem separados: o teste não muda o elenco vivo. Se todas as rotas
  escolherem o mesmo executor, declarar ausência de efeito de seleção, não simular economia.
- Começar, se aprovado, com **quatro tarefas fictícias de contratos/erros × quatro grupos = 16
  execuções**, um perfil API Tester adaptado. É estudo de viabilidade, não prova estatística.
- Fixar testes ocultos e critérios antes; avaliador sem rótulo do grupo/modelo. Mostrar artefatos,
  não as narrativas persuasivas dos agentes. Não esconder failures ou excluir tentativas ruins.
- Medir aceite na primeira tentativa, regressões, violações de escopo, custo até aceite, tokens
  de entrada/saída/cache/raciocínio, latência e retrabalho. Preço equivalente não é fatura nem
  percentual de assinatura. Sem teto numérico e capacidade de escrita comprovada, não despachar.
- Uma fuga de dados/permissão impede adoção. Um resultado inválido não aciona fallback externo
  ou retry invisível. Um perfil que melhora qualidade com custo maior pode ser útil por opt-in;
  não precisa necessariamente economizar para ter valor.

## Decisão antes de implementar

Recomendo **piloto seletivo, sem instalação global**. Não instalar o pacote completo, não
introduzir segundo Manager e não substituir revisão cross-vendor por persona. A alternativa de
menor complexidade é usar apenas critérios já presentes nas nossas skills; ela precisa estar no
controle. Nos arquivos avaliados não encontrei comparação controlada contra nossa configuração;
as alegações promocionais do README não substituem o experimento.

**Atualização após aprovação:** o “prossiga” autorizou a preparação seletiva. O
[perfil local API Tester v1](experimentos/T-138/api-tester-enxuto.md) e os
[quatro contratos candidatos B2](experimentos/T-138/tarefas-b2.md) estão preparados, não executados.
Capacidade da via, tokenização, orçamento e revisão continuam precedendo as 16 execuções;
nenhum perfil instalado, elenco alterado ou novo modelo chamado nesta etapa.
