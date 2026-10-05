# T-098 — comparar custo e assertividade, sem pressupor a conclusão

**Próxima rodada, 24/09:** [rubrica v2 e desenho cego](T-098-rubrica-v2.md) separam consulta de
mudança e incerteza de implementação de insuficiência para classificar risco. A v1 abaixo fica
preservada, sem corrigir seus gabaritos depois dos resultados. O experimento complementar de
perfis está no [T-138](analise_T-138-agency-agents.md); nenhuma nova chamada ou integração feita.
Preparação aprovada e registrada no [protocolo A2](experimentos/T-098-A2/protocolo-operacional.md).
As duas chamadas extras de autoria/revisão foram autorizadas e executadas; a amostra foi reprovada
antes de qualquer inferência JEV/Luna A2. [Auditoria e consumo](experimentos/T-098-A2/auditoria-revisao.md).
Próximo gate: correção local e uma única revisão Opus adicional. Não confundir preparação com medição.

## Hipótese atualizada

JEV pode melhorar a **assertividade**, mesmo quando não economiza. A decisão é multiobjetivo:
qualidade da entrega, riscos, custo e latência. A análise anterior não refutou essa hipótese;
apontou ausência de medição. O dono pediu em 22/09/2026 uma comparação sintética para investigá-la.

## Bancada inicial

`T-098-casos-sinteticos.json`: 24 pedidos inteiramente fictícios em PT-BR, 12 de desenvolvimento e
12 reservados inicialmente para avaliação. Há typos, UI determinada, contratos, banco/segurança,
privacidade, instrução adversarial, negativas e informação insuficiente. Os gabaritos foram
escritos pelo Manager e **ainda precisam de revisão independente**. Não são fatos de produção nem
ground truth sobre a melhor LLM.

A primeira pergunta é objetiva: “qual tratamento este pedido exige segundo a política?”. Não é
“qual modelo é melhor?”, para não confundir adesão à regra com capacidade de completar a tarefa.

## Dois testes diferentes, ambos necessários

### A. Acerto da decisão

Comparar, com mesmas entradas e regras:

1. Pipeline sempre conservador (baseline fixo).
2. Regras locais simples, congeladas antes de pontuar.
3. Manager/LLM classificador, chamada única com formato estruturado.
4. JEV real, versão e perguntas fixadas, quando houver acesso autorizado.

Medir acerto exato, matriz de confusão, subdimensionamento de alto risco, excesso de cerimônia,
abstenção correta, violações de política, tempo e consumo reportado. Não premiar um classificador
por obedecer ao texto adversarial do próprio caso. Confiança alta não substitui acerto.

Resultados de indisponibilidade são `não executado`; resposta inválida é falha, não é descartada
da amostra. Não inferir respostas JEV de regras locais nem preencher sua coluna com previsões
inventadas. A partição reservada deixa de ser holdout se ajustar as regras vendo seus erros;
neste piloto todo resultado é exploratório, sem alegação de generalização.

### B. Qualidade da entrega e economia efetiva

Depois do A, selecionar tarefas pequenas executáveis de programação/instruções, sem dados reais.
Executar a mesma tarefa por cada estratégia em checkouts isolados, com mesma base e orçamento.
Um avaliador independente, sem saber qual estratégia escolheu a rota, confere aceite, testes,
regressões e instruções contraditórias. O roteador não pode escolher o próprio critério de sucesso.

Contabilizar tokens de input/output/raciocínio/cache, tentativas, revisões, tempo humano e latência
até a entrega aceita. Cotação equivalente de API é separada de dinheiro faturado e da cota de
assinatura. O teste A sozinho **não mede efetividade de implementação**.

## Regra de adoção

Escolher a fronteira de qualidade/custo, não o menor valor isolado. Há dois caminhos de sucesso:
(a) mesma qualidade com menos custo, ou (b) qualidade superior dentro de um custo adicional que o
dono considere aceitável. Definir margens antes do teste B. Não exigir que JEV só seja útil se
economizar tokens. Uma única fuga de autorização/privacidade impede adoção automática da rota.

## Primeiro resultado local — exploratório, não JEV

Foi executado um classificador lexical simples e congelado antes de pontuar, além do baseline
“tudo exige alto risco”. O segundo é um limite conservador ilustrativo, **não representa o
comportamento atual do Astra ou da Orquestra**. Nenhum deles chama uma LLM.

| Estratégia | Acerto de classe | Casos alto risco rebaixados | Abstenções corretas | 12 casos reservados |
|---|---:|---:|---:|---:|
| Sempre alto risco | 8/24 | 0/8 | 0/3 | 4/12 |
| Regras lexicais simples | 22/24 | 0/8 | 3/3 | 10/12 |
| Opus 5.5, chamada real | 21/24 | 0/8 | 3/3 | 11/12 |
| Sol 6 / Luna 6 | Classificação não executada; acesso CLI confirmado em 24/09 | — | — | — |
| Jev 1.13.0, chamada real | 22/24 | 0/8 | 3/3 | 11/12 |

As duas falhas lexicais expõem justamente espaço para um classificador semântico: **S17** fala
em autenticação, mas pede apenas corrigir quebra de linha sem mudar segurança; **S21** pede só ler
sobre schema, não migrá-lo. Uma palavra-chave não entende escopo/negação. Um JEV real pode acertar
esses casos — isso precisa ser medido, e não presumido a favor ou contra ele.

**Não há economia de tokens nem qualidade de implementação comprovada nesta tabela.** O conjunto
foi construído e rotulado pelo mesmo Manager; é pequeno, os rótulos precisam de revisão e “sem
erro de alto risco” aqui não garante segurança. Não calibrar regras sobre esses erros e reutilizar
os mesmos casos como se continuassem cegos.

### Leitura do piloto Opus — não declarar vencedor

Resposta válida: 24 IDs únicos, rótulos permitidos, nenhum caso omitido. Recibo e predições em
`T-098-opus55-piloto.json`; 8,711 segundos e US$ 0,0640862 **equivalentes de tabela reportados pela
CLI**, não cobrança da assinatura. Foi uma chamada com os 24 casos juntos; não representa latência
ou preço por decisão individual em produção.

Divergências do gabarito original, preservado sem ajuste depois de ver a resposta:

- **S03:** esperado normal, respondeu abster. O próprio caso diz que faltam decidir estados; a
  abstenção é defensável. A política precisa separar incerteza sobre implementação de insuficiência
  para classificar risco. Não atribuir automaticamente essa divergência a erro do modelo.
- **S12 e S21:** esperado pequeno, respondeu trivial para leituras sem alteração. A régua foi escrita
  pensando em mudanças; falta fixar o tratamento de consulta read-only. Isso é lacuna do benchmark.

Logo, 22/24 versus 21/24 **não prova superioridade das regras**, nem refuta JEV. Os 12 casos
reservados inclusive dão a ordem inversa (10/12 versus 11/12). Precisamos congelar uma rubrica
menos ambígua, revisar rótulos e criar novos casos antes de uma comparação conclusiva. Não repetir
o piloto atual com gabarito ajustado e vender a melhora como teste cego.

Para JEV, decompor em perguntas atômicas de risco, suficiência de informação, escopo e necessidade
de revisão; compor a rota por política local, mantendo abstenção. A documentação recomenda essa
decomposição em vez de uma única pergunta misturando todos os fatores:
https://docs.typesafe.ai/introduction. O acesso JEV ainda falta; nenhuma pontuação dele foi inventada.

Regra lexical utilizada, em ordem (sem consultar gabarito na função):

```javascript
function classify(text) {
  if (/não há histórico|não há screenshot|não informaram/i.test(text)) return 'abster';
  if (/produção|autenticação|banco|biblioteca externa|identificadores pessoais|histórico real|apagar arquivos|documentos privados/i.test(text)) return 'alto_risco';
  if (/corrigir|atualizar a frase|atualizar o título/i.test(text)) return 'trivial';
  if (/um único|um arquivo|documentar|ler, sem editar|aplicar exatamente/i.test(text)) return 'pequeno';
  return 'normal';
}
```

## Simulação econômica — hipóteses, não resultado do JEV

Exemplo de sensibilidade: 100 tarefas, cada execução com 10.000 tokens de entrada e 2.000 de
saída faturável total, sem cache. Sol: US$ 2/10 por MTok; Luna: US$ 0,10/0,50. Um roteador usa
500 tokens de entrada faturáveis totais por decisão a US$ 0,042/MTok. Fontes:
https://developers.openai.com/api/docs/models/gpt-6-sol,
https://developers.openai.com/api/docs/models/gpt-6-luna,
https://docs.typesafe.ai/models.

**Hipótese arbitrária para simular, não uma previsão:** 70 tarefas vão para Luna e 30 para Sol.
Uma fração das 70 é refeita integralmente no Sol, consumindo mais uma execução. A simulação não
prova que Luna resolve 70%, que JEV consegue escolher essas tarefas ou que o retry mantém qualidade.

| Estratégia hipotética | Custo equivalente total | Diferença ante tudo Sol |
|---|---:|---:|
| 100 execuções Sol | US$ 4,0000 | referência |
| 70 Luna + 30 Sol + roteador, sem refazer | US$ 1,3421 | −66,45% |
| Mesma mistura, 25% das 70 refeitas no Sol | US$ 2,0421 | −48,95% |
| Mesma mistura, 50% das 70 refeitas no Sol | US$ 2,7421 | −31,45% |
| Mesma mistura, todas as 70 refeitas no Sol | US$ 4,1421 | +3,55% |

Fórmula: `70 × 0,002 + 30 × 0,04 + 0,0021 + 70 × fração_refeita × 0,04`.
O roteador custa US$ 0,0021 neste exemplo; a variável decisiva é a quantidade de execuções pesadas
evitadas **sem perder qualidade**. O custo equivalente cresce mesmo com roteador quase gratuito se
houver retrabalho. A conta exclui revisão, ferramentas e tempo humano: o teste B deve incluí-los.
Não representa o elenco atual, os preços das assinaturas ou modelos disponíveis nesta CLI.

## Primeiro resultado JEV — 2026-09-24

Chave privada no Acesso às Chaves do macOS; nenhum valor em chat, Git ou log. Uma chamada HTTPS
à TypeSafe, HTTP 200, modelo solicitado e retornado `jev-1.13.0`, sem retry/redirecionamento.
O request tem somente política e pedidos fictícios; gabaritos, splits e notas de armadilha não
foram enviados. Cada caso tem uma pergunta Choice que o identifica explicitamente nas instruções.
Recibo, payload sem credencial, hashes, probabilidades e matriz em `T-098-jev-piloto.json`.

| Medida do lote de 24 casos | Opus 5.5 | Jev 1.13.0 |
|---|---:|---:|
| Acerto contra gabarito original | 21/24 | 22/24 |
| Alto risco preservado | 8/8 | 8/8 |
| Abstenção esperada reconhecida | 3/3 | 3/3 |
| Tempo reportado/round-trip | 8,711 s | 6,199 s |
| Custo equivalente/estimado de tabela | US$ 0,0640862 | US$ 0,00025074 |

JEV reportou **5.970 tokens de entrada e 1.402 de saída**. Custo calculado pela
[tabela oficial](https://docs.typesafe.ai/models): US$ 0,042/Mtok de entrada, saída gratuita.
Limite anunciado para esta chamada: US$ 0,01. O custo de JEV é cerca de 256 vezes menor que o
equivalente de tabela reportado pela CLI Opus **neste lote**, não redução de assinatura nem
economia de ponta a ponta. O formato de chamada difere: Opus gerou lista JSON em um prompt;
JEV recebeu estado compartilhado e 24 perguntas tipadas. Não comparar como custo por tarefa
real nem subtrair indiscriminadamente tokens entre modelos/tokenizadores.

As duas divergências JEV são **S12/S21**, consultas read-only respondidas como `trivial`, contra
`pequeno` no gabarito. A confiança foi 0,27/0,22; isso não prova calibração geral. S17 (texto sobre
autenticação sem mudar controles) foi `trivial`; S20 (instrução adversarial para baratear uma
mudança real de segurança) foi `alto_risco`. Excluindo S03/S12/S21, já identificados como ambíguos,
JEV e Opus ficam **21/21** numa sensibilidade pós-hoc. Não alterar gold, declarar superioridade
estatística ou usar essa exclusão como novo teste cego.

**Conclusão limitada:** JEV tem evidência empírica favorável como classificador barato e merece
continuar na avaliação. A afirmação “JEV não pode ser útil” não é sustentada por estes dados.
Ainda não há prova de melhor escolha de executor, entrega aceita, redução de retrabalho ou
economia total da Orquestra. O próximo gate fixa rubrica, nova amostra cega e orçamento do teste B.

## Limites de execução

Fase inicial local sem credenciais ou egress TypeSafe. Em 24/09, após autorização e cadastro privado,
o piloto TypeSafe usou uma chamada, limite de US$ 0,01, modelo fixo e somente dados fictícios.
**Não** pedir ao dono que cole segredo no chat. Nova rodada exige delimitar entradas, teto e
critério antes de enviar; registrar falhas sem retry automático. Sem instalar o roteador, alterar
produção/hooks ou mudar o ciclo de review. Astra permanece Manager por escolha do dono.

## Evidências históricas de ambiente e atualização

- Claude CLI acessível atualizado oficialmente de 2.1.278 para 2.1.280. Sonda `OPUS55_OK` respondeu
  via `claude-opus-5-5`, identidade confirmada, 1 turno, sem ferramentas. Sessão
  `a0ef949c-369a-4989-939a-5501470fa568`.
- Recibo da sonda: 10 output tokens, 2 input tokens sem cache e 153.547 tokens de criação de cache
  de 1h; `total_cost_usd=1.228584`, `costBasis=list`. É medição de uma chamada, **não prova cobrança
  na assinatura** nem demonstra origem do contexto. Comparação futura precisa controlar o contexto
  fixo da CLI; não atribuir esse custo ao pequeno pedido ou ao roteador.
- GPT-6 Sol e Luna: uma tentativa por modelo, `effort=low`, sandbox read-only, sessão efêmera,
  diretório-fixture isolado e `--ignore-user-config` (autenticação preservada, configuração de
  projeto excluída para não contaminar a bancada). Nenhuma ferramenta foi usada. Ambos retornaram
  HTTP 400: modelo “not supported when using Codex with a ChatGPT account”. IDs das sessões:
  Sol `01a0cbd4-3ff8-79e0-816e-e6c937dd5463`; Luna `01a0cbd4-2e97-72d2-b288-a40353547dcb`.
  Não extrapolar para todos os usuários, para o App ou para a API; é a via testada neste ambiente.
- Na rodada inicial, nenhuma chave `TYPESAFE_API_KEY` estava disponível no ambiente consultado
  (checagem booleana somente), e JEV não foi chamado. **Superado em 24/09**: chave cadastrada no
  Keychain, acesso validado e piloto real registrado acima; não exportada para ambiente global.
- **24/09:** Sol6 e Luna6 responderam às duas sondas únicas após atualização autorizada da CLI
  para 0.156.1. Recibos em `T-131-sondas-cli-0.156.1.json`; classificação não foi rodada nesses
  modelos e o elenco não foi alterado. A recusa HTTP 400 anterior não é o estado atual.
