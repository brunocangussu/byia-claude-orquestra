# T-098 A2 — auditoria do gabarito, primeira revisão

## Resultado

**Amostra reprovada antes da classificação.** Uma autoria Terra e uma revisão Opus foram
executadas; zero chamadas JEV e zero Luna. Não há nova taxa de acerto ou economia A2.
O problema observado está no desenho/conteúdo da amostra, **não** em autenticação do Claude,
indisponibilidade do JEV ou qualidade já medida dos classificadores.

Autoria: `gpt-5.6-terra@xhigh` solicitado via Codex CLI 0.156.1; exit0, 124,206 s, nenhuma
ferramenta nos eventos. O recibo não expõe identidade resolvida independente do modelo solicitado.
Revisão: `claude-opus-5-5` comprovado em `modelUsage`, via runner canônico/Claude CLI 2.1.280;
exit0, 45,499 s, uma chamada CLI, 48 itens declarados revisados, oito achados.

## Evidência preservada

- [Recibo original do autor](autor-recibo.json), sem correção retroativa.
- [Amostra proposta](amostra-proposta.json), com gabaritos e partições originais intactos.
- [Validação estrutural](validacao-autoria.json): 48 itens; 8/classe; 4/classe/partição;
  12 famílias de 4, sem atravessar split por **nome**; tamanhos e scanner preventivo válidos.
- [Pacote efetivamente enviado](revisao-pacote.txt): 9.723 bytes UTF-8 incluindo newline final.
  Hash efetivo no [recibo da revisão](revisao-recibo.json); o cálculo anterior de 9.722 bytes
  era antes do newline acrescentado ao salvar. Nenhum item foi cortado, alterado ou relotado.
- [Parecer para auditoria](parecer-para-auditoria.json): removida somente a cerca Markdown para
  leitura local. O original contrariou o contrato de JSON puro; isso permanece falha de formato,
  não aprovação inferida. O conteúdo interno também é `BLOCKED`, não resultado ambíguo.
- [Resultado operacional](resultado-preparacao.json) distingue contagem de chamadas, uso,
  limitações e falhas. [Payloads planejados](payloads-planejados.json) **não foram enviados**.

## Achados auditados pelo Manager

| Achado Opus | Auditoria contra a amostra e a rubrica | Decisão |
|---|---|---|
| X015: rótulo `pequeno` ao trocar texto de botão | Pedido fixa apenas “Ver rotina”, sem efeito funcional; regra 4 precede regra 5. O rótulo original é incompatível com a rubrica | Bloqueador confirmado |
| X027/X008: produção nas duas partições | Ambos ativam/publicam um produto em produção; muda painel/boletim e a redação, mantendo a decisão operacional. Separar famílias por nome do produto não separou o cenário | Bloqueador de partição confirmado |
| X045/X004: novo serviço nas duas partições | Ambos conectam o produto a um novo serviço externo. X004 acrescenta tentativa de rebaixar risco; não justifica, sozinho, reutilizar o mesmo núcleo entre splits | Mesmo grupo de bloqueio de partição; contraste adversarial deve ficar na mesma família |
| X019/X034: “confidenciais dos personagens” | X019 expõe notas, X034 retém documentos: ações e fluxos diferentes. Vocabulário comum de risco não prova, sozinho, paráfrase | Não confirmado como bloqueador independente; observar repetição lexical |
| X031/X024: consulta a permissões de edição | Perguntar quem edita e explicar como uma restrição funciona não são necessariamente a mesma pergunta. Não há detalhe de implementação para provar vazamento operacional | Não confirmado como bloqueador independente |
| X005 e outros triviais: molde repetido | Há cinco correções ortográficas muito parecidas, mas também pontuação/espaços. A acusação de que **todos** são a mesma tarefa é excessiva | Homogeneidade confirmada como limitação; refutada a generalização para os oito |
| X003 e demais `normal`: sufixo exclusivo | Checagem local confirma `; escolha/decida/defina` em **8/8 normal**, e **0** nos demais. O formato vira atalho perfeito para esse rótulo | Bloqueador metodológico confirmado |
| X006/X009/X036: resultado não fechado | Largura, espaçamento e margem não têm valor-alvo; não se comprova um arquivo. Ampliando a mesma checagem, os oito `pequeno` omitem prova de um arquivo; X047 nem fixa qual ícone | Bloqueador de sustentação do gabarito confirmado; não inventar escopo para classificá-los |

Quatro causas-raiz suficientes: precedência do rótulo textual; insuficiência de fatos para
`pequeno`; famílias definidas por nome em vez de mecanismo; pista sintática exclusiva de classe.
A falha de formato do parecer é adicional. Não transformar os oito apontamentos em oito
defeitos confirmados nem declarar todos os 48 itens semanticamente validados.

## Consumo real das duas chamadas

| Via | Entrada e cache reportados | Saída reportada | Tempo |
|---|---|---|---|
| Terra | input 19.647; cached input 6.912 (parte do input) | 6.539, incluindo 4.301 de raciocínio | 124,206 s |
| Opus 5.5 | input 2; cache creation 7.731; cache read 531 | 4.825, incluindo 3.421 de thinking | 45,499 s |

Tokenizers e contabilidade diferem: não somar campos de cache/raciocínio de novo nem anunciar
economia agregada. O Opus retornou US$ 0,1584622 **equivalentes à tabela**, `costBasis: list` em
`modelUsage`; isso não é fatura da assinatura. O Codex não retornou custo em dólares. Não houve
custo novo de API JEV nesta etapa e a chave não foi lida. Essas despesas de preparação devem
entrar no custo do experimento, não ser escondidas no custo unitário do classificador.

Houve uma invocação por papel, sem retry do Manager. Retries internos de transporte das CLIs
não foram instrumentados; não declarar “zero tentativas HTTP internas” sem essa prova.
Dois erros locais de análise (`TextEncoder` indisponível e tentativa de persistir `undefined`
quando o parecer veio cercado por Markdown) foram corrigidos sem reinvocar nenhum modelo.

## Próximo passo recomendado, sem executar nova chamada

Corrigir a amostra **localmente**, mantendo o original e congelando rubrica/prompts/regras já
definidos. Trocar o gabarito textual incorreto; explicitar arquivo/resultado/ambiente nos casos
pequenos; diversificar texto e tipos de tarefa; reagrupar cenários por mecanismo antes de
reparticionar. Não basta renomear famílias ou embaralhar IDs. Manter 48 itens/24 reservados se a
nova distribuição realmente satisfizer o contrato; se não satisfizer, reportar o limite.

Depois, pedir **uma única revisão Opus adicional**, sem retry, do novo snapshot sanitizado.
Essa chamada não está autorizada pela R1 já consumida. Somente com novo gate aprovado executar
as quatro JEV + quatro Luna anteriormente previstas, dentro do teto JEV de US$ 0,02.

O Manager abriu itens reservados apenas para auditar bloqueios, não resultados dos classificadores.
Não chamar a proposta atual de “teste cego validado”. Uma revisão local do conjunto precisa
registrar autoria mista e reserva contra ajuste dos classificadores, sem fingir novo autor fresco.
Não houve alteração de produto, elenco, cache, config, instalação, commit, push ou restart.

## Verificação local após as chamadas

Suíte por descoberta com bytecode desativado: **414/414**, 51,008 s; manifesto estrito, lint de
coerência e `git diff --check`: exit0. Conferidos: hashes congelados, equivalência entre resposta
original e amostra persistida, bytes/hash do pacote revisado, hashes dos payloads não enviados,
ausência de gold nos casos preparados para classificação, JSONs válidos e links locais.
Fixture v1 inalterado. Esses checks validam os artefatos; não revertem a reprovação semântica.
Teto aplicado à autoria: 300 s; à revisão canônica: 240 s. Ambas concluíram dentro do limite.
