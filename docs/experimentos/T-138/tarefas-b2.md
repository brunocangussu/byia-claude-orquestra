# T-138 — contratos candidatos do ensaio de entrega B2

Preparação local, **não execução autorizada por este arquivo**. Quatro tarefas totalmente fictícias;
nenhum servidor, banco, credencial, dependência ou recurso de projeto real. Antes do despacho,
materializar os artefatos em diretórios isolados, fixar testes visíveis/ocultos e seus hashes,
comprovar a via de escrita e aprovar teto de chamadas/cota. Não usar worktrees em desenvolvimento.

## Casos e oráculos de aceite

| ID | Pedido do executor | Contrato a preservar/implementar | Oráculos mínimos preparados antes do despacho |
|---|---|---|---|
| B01 | Corrigir `DEFAULT_LIMIT=10` para 20 em um módulo local; a documentação e contrato existentes já dizem 20 | Uma constante, nenhuma outra regra alterada | Ausência de argumento → 20; argumento 3 continua 3; diff não altera validação nem testes |
| B02 | Acrescentar paginação por deslocamento a uma função pura que recebe lista, offset e limit | Inteiros não booleanos; offset ≥ 0; limit 1..50; retornar itens e próximo offset ou `null`; não mutar a lista | Lista vazia, fronteiras 1/50/51, offset além do fim, bool recusado, última página exata, ordem e entrada intactas |
| B03 | Corrigir tradutor de erros de um cliente fictício conforme tabela já existente, num arquivo | 404 → `not_found`, 429 → `retry_later`, 500..599 → `upstream`; demais status de erro → `unknown`; nunca realizar retry | 403/404/429/499/500/599/600; tabela exata, zero chamadas de rede, corpo não exposto na mensagem |
| B04 | Implementar suporte local a ETag na resposta GET de um recurso fictício | ETag exata e sensível a maiúsculas; se `If-None-Match` corresponder, 304 sem body; senão 200 com body e ETag; não alterar outros headers | Header ausente, valor diferente, match exato, diferença de caixa no valor, GET idempotente, input não mutado |

B02/B04 têm comportamento novo; B01/B03 têm resultado fechado segundo contrato existente.
Essas expectativas são notas de planejamento, não rótulos a enviar ao roteador. As quatro tarefas
não demonstram cobertura de produção/segurança; a seleção real pode coincidir entre regras/JEV.
O teste de header B04 precisa explicitar no fixture se nomes de headers já chegam normalizados;
não cobrar essa decisão oculta de um executor com contrato ambíguo.

## Comparação pareada

Cada tarefa terá A/B/C/D conforme [análise](../../analise_T-138-agency-agents.md). Uma seleção por
regra e uma por JEV são congeladas antes; A/C usam o mesmo modelo/effort, assim como B/D.
A/B recebem baseline canônico idêntico. C/D recebem esse baseline mais somente o bloco delimitado
do [perfil v1](api-tester-enxuto.md). Não remover TDD, gates ou skills pertinentes do controle para
fabricar vantagem do suplemento. Inventariar baseline realmente carregado e tokens de cada braço.

Não adotar o suplemento pela beleza do relatório: pontuar artefato e testes executados. Testes
ocultos ficam fora do diretório legível pelo executor; evaluator separado e limitado a fixtures
locais. Revisão recebe artefatos sem modelo/grupo, e seu custo entra na conta. Uma modificação fora
do escopo ou alteração dos testes de aceite invalida a entrega, mesmo se a suíte do executor passar.

Permanecem pendentes: baseline literal, catálogo experimental, mapeamento de classes para modelos,
tokenização do perfil, harness, capacidade de escrita, orçamento de 16 execuções e revisão.
Nada neste protocolo modifica o elenco vivo ou concede automaticamente uma faixa barata.
