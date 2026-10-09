# T-150 — alinhamento operacional da Orquestra

**Data:** 2026-10-06 · **Trilha:** sistema · **Faixa:** pesada.
**Estado atual, 08/10:** R3 consumida 1/1: APROVADO_COM_RESSALVAS, sem bloqueadores, auditoria encerrada. Entrega Git allowlistada e limpeza local T-144 autorizadas pelo dono; candidata 0.32.0 nos quatro anchors. Produto/elenco iguais ao snapshot revisto (916 testes/28 mutações pós-R2); gates frescos antes da entrega. Sem publicação, instalação, restart ou revisão adicional.
**Frente:** `@frente-alinhamento`, host Codex. Base inspecionada: main `4cdbcbc`, fonte 0.31.0.

## Pedido e interpretação

O dono quer adotar o elenco padrão neste repositório, conferir a coordenação
dentro dos agentes, evitar que duas rodadas encerrem um trabalho não resolvido
e esclarecer o resultado do JEV. “Java” foi interpretado como JEV/Typesafe;
se o dono se referia à linguagem Java, este último diagnóstico não responde a ela.

A frase sobre duas rodadas admite duas leituras. A proposta é: **não parar
automaticamente na segunda rodada; usar estagnação para mudar de abordagem**,
não para repetir indefinidamente a mesma chamada. A aprovação deste desenho
confirma essa interpretação. Nenhum gate antigo de chamada única é renovado.

Este card coordena o alinhamento, sem duplicar nem mudar silenciosamente a
posse de T-062 (revisões), T-139 (especialização) e T-098 (JEV). A retomada das
respectivas implementações exige reafirmação explícita da frente dona.

## O que a inspeção inicial demonstrou — histórico de 06/10

| Item | Estado constatado | Consequência |
|---|---|---|
| Fábrica T-149 | Catálogo único 0.31.0 entregue em `orq/references/elenco-padrao.json` | O padrão existe, mas não migrou o elenco ativo deste projeto |
| Host Codex ativo | Planners Astra `max`, implementers/docs/scout Terra 5.6 `xhigh`; reviewer `opus` legado | A divergência é real; não é preciso recriar a fábrica |
| Revisão | `orq/commands/revisar.md:317` impõe máximo de duas rodadas | Contrato vivo ainda precisa de mudança |
| Noturno | `orq/commands/dormir.md:65` encerra após duas rodadas sem progresso | Planejamento noturno não equivale a desenvolvimento autônomo ilimitado |
| Agentes | Cinco agentes: Planner, Implementer, Reviewer, Docs e Scout | Manager ainda concentra a orquestração; não existe coordenador técnico separado |
| Especialização | T-139 tem compositor/perfis em piloto; sem adoção | Não anunciar os perfis experimentais como comportamento de produção |
| JEV | Um lote exploratório real; bancada v6 integrada pela 0.30.0 | Ainda não classifica nem escolhe modelos no fluxo diário |

## 1. Adotar a fábrica no Host Codex deste projeto

Preservar a sessão do Manager, o Host Claude, presets, vias desativadas,
papéis adicionais e overrides explícitos. Não apagar decisões históricas.

| Papel | Modelo e esforço pretendidos |
|---|---|
| planner·interface | `claude-opus-5-5@high` |
| planner·sistema | `gpt-6.1-sol@xhigh` |
| implementer·leve | `gpt-6-luna@medium` |
| implementer·normal | `gpt-6.1-sol@high` |
| implementer·pesada | `gpt-6.1-sol@xhigh` |
| reviewer | `claude-opus-5-5@high` |
| docs | `gpt-6-luna@low` |
| scout | `gpt-6-luna@medium` |

Usar `elenco_padrao.preview_adoption`, existente, para projetar os oito papéis.
Ele não escreve o Markdown nem autentica recibos. Auditar modelo, esforço,
via, versão do cliente, contexto de conta e capacidade exigida pelo papel.
Reutilizar somente provas compatíveis; leitura sintética não prova escrita.
Se faltar prova, registrar a pendência e não ativar uma configuração pela metade.
Essa pendência não deve impedir a correção local independente da regra de revisões.

Aplicar somente os trechos próprios de `### Host Codex` e suas referências
operacionais em `memory/wiki/_elenco.md`, depois dos gates de adoção/prova.
Catálogo disponível e skill carregada não comprovam todos os chats ativos.
Autenticação, sondas e chamadas pagas, quando necessárias, terão gate delimitado;
não estão incluídas na preparação deste plano.

## 2. Revisões orientadas à resolução, não a um número fixo

Reconciliar na frente T-062, preservando contadores, pareceres e tentativas gastas.
Não restaurar uma worktree histórica nem portar sua política automaticamente.

Contrato proposto:

- Retirar o teto global obrigatório de duas rodadas de correção/revisão.
- Continuar correções aprovadas enquanto houver uma ação local útil e verificável.
- Após duas reavaliações sem avanço, exigir diagnóstico e mudança de estratégia:
  causa-raiz, teste reproduzível, RED/GREEN, contrato contraditório ou decomposição.
  Não chamar novamente o mesmo revisor com o mesmo snapshot para simular avanço.
- Progresso significa teste antes vermelho agora verde, mutação detectada,
  bloqueador confirmado encerrado ou contrato verificável esclarecido.
  Alterar um hash, esperar ou escrever mais texto não basta.
- Revisão nova de snapshot corrigido usa o orçamento autorizado do card;
  não renova chamadas únicas, não autoriza retry e não ignora custo/tempo/egress.
- Oferecer um envelope de revisões por card com orçamento definido pelo dono,
  para não pedir permissão a cada correção já coberta. Preparar o envelope não o aprova.
- Se a revisão externa ficar indisponível, continuar trabalho local autorizado
  e outros itens elegíveis; não declarar aprovação, VALIDATE ou DONE por omissão.
- Se não existir ação autorizada útil, informar o impedimento concreto. Não
  criar um loop ocioso, trabalho fora do escopo ou chamadas sem autorização.

Reconciliar as instruções vivas em `orq/commands/revisar.md`,
`orq/commands/dormir.md`, `orq/skills/orq/SKILL.md` e consumidores atingidos.
Preservar logs, planos antigos identificados como históricos e pacotes congelados.
Manter limites de segurança, plataforma, orçamento e a separação entre noturno
de planejamento e implementação pré-aprovada. Este plano não entrega o T-006.

## 3. Coordenação técnica dentro dos agentes

**Desenho inicial aprovado:** um coordenador técnico opcional,
subordinado ao Manager, acionado apenas quando dependências entre módulos ou
contratos justificarem sua presença. Manager permanece dono da autorização,
do board, do despacho efetivo e do aceite/integração.

O coordenador devolve decomposição, dependências, responsabilidades por arquivo,
contratos entre entregas, sequência de integração e testes. Ele não escreve
código, cria agentes recursivamente, move cards, concede permissões, aprova
seu próprio plano/review ou faz Git/release. O Reviewer continua independente.

Para não cobrar uma camada extra em toda tarefa, o planejamento sistêmico
pode usar esse contrato de coordenação na mesma chamada. Um agente separado
é opt-in e exige justificativa de benefício/custo. O modelo e esforço vêm de
`planner·sistema` resolvido para o host, não de `inherit` silencioso nem de
uma escolha própria do coordenador. A fábrica continua com seus oito papéis.

Na frente T-139, comparar o contrato atual com essa coordenação limitada.
Não importar integralmente o Agents Orchestrator do Agency Agents: sua
autonomia/retries não podem conceder uma segunda autoridade neste produto.
Não confundir persona/skill com treinamento de uma LLM.

Arquivos candidatos, depois da aprovação: instrução de agente de coordenação,
`orq/agents/orq-planner.md`, skill central, comandos de planejamento/despacho
afetados e `memory/wiki/arquitetura.md`. Confirmar o mecanismo de resolução
antes de criar um sexto agente; um modo explícito do Planner pode bastar.

**Resultado atual:** implementado como modo `technical` explícito do mesmo
Planner, sem sexto agente, segundo Manager ou chamada extra. O contrato
composto vai inline na mesma chamada; as provas estão no snapshot R3.
Isso não promove o piloto T-139 nem comprova ganho de qualidade/economia.

## 4. JEV: separar entrega, experiência e benefício

O recibo `docs/T-098-jev-piloto.json` registra uma chamada real, sem retry:
22/24 classificações corretas contra o gabarito original, 8/8 casos de alto
risco corretos e custo estimado US$ 0,00025074, **não uma fatura**.
O próprio recibo alerta para gabarito original ambíguo, amostra exploratória,
ausência de prova da implementação e latência não representativa de produção.

A bancada v6 tem 48 casos, 31 testes e preflight reconferidos na entrega
T-148. A campanha atual A2/B2 segue sem execução e os scores sem avaliação.
Isso não apaga o piloto anterior, nem comprova economia/qualidade comparativa.

Retomar T-098 pelo snapshot selado e medir regras atuais versus JEV nos mesmos
casos: erro por risco, abstenção, custo total até aceite, latência e retrabalho.
Comparação de perfis é fator separado da comparação de roteadores.
Primeiro rodar em observação: JEV recomenda; não executa código, concede
permissões, reduz proteção de alto risco nem remove revisão independente.
A campanha paga e a adoção diária continuam gates próprios. Nenhuma chave
foi consultada, copiada ou alterada nesta inspeção.

## Execução após aprovação

| ID | Entrega verificável | Tamanho | Critério |
|---|---|---|---|
| P1 | Diff de adoção Codex e auditoria dos recibos | M | Oito papéis da fábrica; outras escolhas preservadas; pendências não mascaradas |
| P2 | Reconciliação da política T-062 na frente dona | M | Nenhum veto apenas por terceira rodada; estagnação exige ação diferente; orçamentos intactos |
| P3 | Contrato local de coordenador, na frente T-139 | M | Uma autoridade; coordenação limitada e opcional; sem nova chamada por padrão |
| P4 | JEV consultivo para testes e revisões, com preparo local | M | Recomendações limitadas por evidência; sem rede, permissões ou aceite delegados |
| P5 | Testes contratuais e gates locais | M | RED/GREEN e mutações dos contratos alterados; descoberta completa, manifesto estrito e lint |
| P6 | Pacote e gate de revisão independente | M | Diff sanitizado e hash; autorização de chamadas separada, sem envio automático |

P2 pode avançar sem esperar uma sonda de P1 ou a campanha de P4.
Não iniciar desenvolvimento adicional de JEV para explicar seu estado.
Execução isolada usará worktree própria, depois da aprovação. Preservar o
checkout/processos de `claude/t144-medidor-progresso` e suas escolhas vivas.

Testes existentes a revalidar: `test_elenco_padrao.py`,
`test_elenco_perfis.py`, `test_elenco_consumidores.py`,
`test_continuidade_aprovada.py` e testes de progresso afetados.
Acrescentar testes contratuais específicos para orçamento/revisão e
coordenação: terceira rodada permitida sob autorização, contadores
preservados, duas rodadas estagnadas mudam o diagnóstico, negação real de
egress respeitada e coordenador incapaz de tomar posse/autorizar execução.
CLIs falsas servem aos testes locais, não à prova de capacidade do host.

Gates do produto, quando houver implementação:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
```

Não usar testes seletivos para anunciar a suíte completa. Validação
comportamental dos hosts e instalação são etapas posteriores autorizadas.

## Gate e reversibilidade

**Execução local aprovada e verificada:** P1–P6 concluídos localmente;
oito papéis comprovados, adoção candidata só nesta worktree. R1/R2 corrigidas
e preservadas; R3 aprovada com ressalvas e auditada, uma chamada sem retry.
T-062/T-139/T-098 conservam posse. Entrega Git por allowlist autorizada pelo
dono, versão livre 0.32.0/quatro anchors, sem confundir com ativação ou DONE.
Nova chamada Haiku/JEV ou alteração funcional do snapshot não está coberta.

Bump, commit, push e integração T-150 foram autorizados no gate humano
registrado na thread dona, incluindo as quatro âncoras no mesmo commit.
Publicação, instalação e restart continuam expressamente proibidos.
Rollback preserva o elenco anterior e os recibos; remove somente a adoção
ou contrato próprio por patch revisado, nunca restaurando arquivos do Claude
ou evidências congeladas a partir do HEAD.

## Resultado local inicial — histórico de 2026-10-06

Worktree `codex/t150-alinhamento-operacional`: 904 testes descobertos OK,
18 mutações detectadas, manifesto estrito e coerência interna exit 0.
Recibo e handoff nessa raiz: `docs/T-150-verificacoes-locais.json` e
`docs/handoff-T150-local-2026-10-06.md`. R1 v2 preparada, 49.256 bytes,
não enviada; sem adoção do elenco, bump, entrega Git ou ativação de host.
Cinco de seis passos locais concluídos; P1 pendente não encerra as demais
frentes autorizadas nem permite fabricar recibos de capacidade.

## Resultado atual — 2026-10-08

Recibos: `docs/T-150-verificacoes-pos-R2.json`,
`docs/T-150-R3-recibo-publico.json` e auditoria R3 em `docs/reviews/`.
Produto e elenco iguais aos digests revisados; R3 consumida 1/1, sem retry.
Main/remoto 0.31.0 sincronizados, gates frescos 870/manifesto/lint verdes.
T-144 não tem commits exclusivos: fonte integrada, limpeza local proposta
antes de remover. Validação prática das fases 1/2 e T-147 permanecem separadas.

Haiku 5.5 confirmado pelo dono somente para planejamento/piloto do Host
Claude. Codex conserva OpenAI em implementer/docs/scout, sem trigger Haiku.
Guarda do runner testada offline, sem processo/modelo/rede; catálogo e
alias atual não homologam 5.5. Pesquisa não é adoção nem mudança de produto.
Fonte/cache Codex 0.31.0 verificados a partir de checkout limpo; cache
Claude encontrado apenas 0.27.10. Nenhuma instalação ou restart executados.
