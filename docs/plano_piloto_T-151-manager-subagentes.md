# T-151 — plano do piloto de subagentes proativos

**Estado:** proposta de avaliação, não executada. Pedido humano de 09/10/2026.
Não altera a candidata congelada da R1, o elenco nem o roteamento.

> Para os agentes da avaliação: executar somente após aprovação deste plano.
> A preparação e a execução seguem Orquestra, com isolamento, ownership e
> provas reais de modelo/effort/via; não criar uma árvore recursiva de agentes.

**Objetivo:** comprovar se o Manager decompõe trabalho e usa subagentes
proativamente quando isso é útil, supervisionando falhas e integrando resultados
sem perguntas humanas repetidas dentro do acordo da meta.

**Arquitetura:** comparação pareada A/B de instruções, em sandboxes descartáveis,
com um único Manager por execução, modelos fixados e critérios objetivos. Sem
JEV, roteador novo, agente aprovador ou alteração de configuração dos hosts.

**Tecnologia:** Python/unittest para a fixture e o oráculo local; harness
comprovado do host para os agentes; recibos JSON com IDs, digests e consumo.

**Especificação:** `docs/plano_T-151-autonomia-por-meta.md` e o pedido humano
atual. Este documento complementa a validação; não reabre a implementação.

## O que reaproveitar e o que falta

| Dimensão | Evidência existente | Lacuna real |
|---|---|---|
| Decomposição | Contratos e guardas da candidata; Planner/Scout reais na análise | O Manager escolher entregas/interfaces e delegar sem um prompt mandando paralelizar |
| Paralelismo útil | Ownership disjunto usado na implementação; guardas e sonda C02 | Duas entregas reais avançarem simultaneamente, sem disputa e com benefício líquido mensurável |
| Supervisão de falhas | Testes contratuais e mutações da política | Observar uma falha controlada, continuar a entrega independente e recuperar só a dependência afetada |
| Integração | Manager integrou o consumidor disjunto e conferiu gates | Comparar a integração de dois resultados, inclusive um handoff bloqueado, com oráculo funcional oculto |

Reaproveitar os recibos de análise/implementação, os 936 testes registrados e
as 41 mutações. Não rodar novamente a suíte só para obter outro número igual.
As sondas de consumo já deram **8/8 em ambos os lados**; a final recebeu duas
fontes adicionais e teve uma citação imprecisa. Não demonstram ganho causal,
economia ou coordenação real. Não repeti-las como se fossem o novo piloto.

## Desenho pequeno e comparável

Quatro execuções novas: **dois cenários × dois braços**. Ordem congelada:
cenário S1 em A→B; cenário S2 em B→A. Não rodar os quatro ao mesmo tempo:
concorrência entre braços tornaria a medição de tempo menos comparável.

- **A:** fontes da base `6c8482a`, Orquestra 0.32.0.
- **B:** snapshot T-151 atual, ou seu sucessor auditado se a R1 exigir correção.
  Congelar os digests antes de executar; nunca avaliar bytes diferentes dos
  registrados. Mudança material no desenho volta ao gate do piloto.
- Mesmo conjunto de superfícies em ambos: AGENTS, CLAUDE, skill, plan-next,
  implement-next, planner, implementer e referências inalteradas necessárias.
  Nada de adicionar só ao braço B o plano explicativo ou o oráculo.
- Mesmo briefing de meta, fixture, ambiente, elenco, modelos, efforts,
  permissões e critérios de aceite. Sessões frescas; sem histórico ou respostas
  de outro braço. Registrar bytes por fonte e a diferença própria do tratamento.
- O briefing descreve objetivo e autorização técnica, mas **não** pede
  “crie dois agentes”, não oferece a decomposição e não manda paralelizar.
  A oportunidade e a decisão precisam surgir do Manager.
- Avaliar a aplicação das fontes fornecidas no sandbox, não fingir que a
  candidata já está instalada/carregada nos projetos.

### Fixture e interfaces fechadas

Uma ferramenta sintética, sem rede ou dados reais, resume filas de tarefas:

- `fila/entrada.py`: `parse_tasks(text: str) -> list[dict]`. Entrada JSON;
  valida `id` único não vazio, `status` em `pending|done` e `duration` inteiro
  não negativo, recusando booleanos, duplicatas e formatos inválidos.
- `fila/relatorio.py`: `summarize(tasks: list[dict]) -> dict` e
  `render(summary: dict) -> str`. Calcula total, pendentes, concluídas e soma
  das durações; renderização determinística, inclusive coleção vazia.
- `fila/app.py`: integração dos contratos. O Manager é o único integrador;
  workers não disputam esse arquivo.
- `tests/test_entrada.py` e `tests/test_relatorio.py`: testes dos entregáveis,
  com ownership correspondente. `tests/test_aceite.py` fica fora do contexto
  dos agentes e só é aplicado pelo controlador ao artefato integrado.

O controlador prepara arquivos e testes de aceite por `apply_patch` depois do
gate. Ambos os braços recebem cópias byte a byte da mesma fixture. O oráculo
confere os resultados esperados, não o texto elogioso de um handoff.

### S1 — trabalho maior com entregas independentes

Entregar a ferramenta funcional, com parser, relatório, testes e integração.
As duas interfaces estão fechadas; há oportunidade legítima de dois writers
disjuntos. Observar se o Manager reconhece isso e delega com contexto curto,
arquivos exclusivos, aceite e handoff. A quantidade de agentes, sozinha,
não conta como sucesso.

### S2 — mesma oportunidade com falha controlada

Mesma fixture, acrescida de uma sonda local declarada `probe_fail_once.py`.
Ao início da primeira entrega, ela retorna **exit 42** uma vez e o worker
devolve handoff bloqueado com esse recibo, sem “corrigir” a sonda. A injeção
é determinística e idêntica nos braços; não altera credenciais, API, limites
do provedor, trabalho de outro projeto ou processos fora do sandbox.

O acordo autoriza ao Manager recuperar essa falha técnica local e concluir
o escopo dentro do orçamento. Não lhe diz como distribuir as entregas.
Observar se a entrega independente avança enquanto a dependência está
bloqueada, se o Manager preserva os resultados/handles e se corrige somente
o necessário. Não fingir que isto comprova recuperação de falhas da API ou
autenticação: é prova de supervisão de **falha local simulada**.

Não reenviar chamadas externas como retry. O Manager pode concluir localmente
o entregável bloqueado; um novo despacho só cabe no saldo explícito da
execução, nunca é saldo renovado por erro. Registrar tentativas, inclusive
as incompletas; não repetir um braço ruim nem selecionar somente sucessos.

## Elenco, limites e intervenção humana

Preservar os perfis vigentes, sem editar `_elenco.md` ou o catálogo padrão:
Manager com o mesmo modelo/effort da sessão de referência, verificado e fixado
nos quatro runs; implementer normal Sol 6.1/high; Scout Luna 6/medium,
read-only, somente se útil. Planner·sistema Sol 6.1/xhigh apenas se necessário
e dentro do mesmo teto de auxiliares. Sem fallback silencioso.

Proposta de orçamento finito para este piloto, **não teto do produto**:

- Quatro Managers frescos; até três despachos auxiliares por run, no máximo
  dois writers simultâneos e um auxiliar read-only. Total máximo de **16
  chamadas OpenAI**, contando Managers e auxiliares; não incluir Anthropic/JEV.
- 15 minutos por run, 60 minutos de execução total. Registrar o tempo de
  preparação separadamente; não esconder setup, supervisão ou integração.
- No máximo 300.000 tokens de entrada e 12.000 de saída **por run somado**,
  Managers+auxiliares. Entrada cached continua no total, mas aparece separada.
  Teto do piloto: 1.200.000 de entrada e 48.000 de saída; não é previsão
  de gasto. Os bundles de instruções são extensos, portanto um teto inferior
  poderia medir apenas interrupção por falta de contexto, não coordenação.
  Limite de raciocínio faz parte da saída quando o provedor assim o contabiliza;
  não somar duas vezes. Sem custo monetário fabricado a partir de tokens.
- Se a via não comprovar contadores completos, o teto de tokens não é
  estritamente enforceable: verificar antes de despachar, contar incrementalmente
  e registrar qualquer ultrapassagem. Timeout e teto de chamadas continuam
  obrigatórios; não iniciar quando nenhuma proteção útil estiver disponível.
- Sem novas sondas pagas se houver prova contextual compatível. Se faltar
  capacidade na via, registrar a lacuna e não trocar o elenco para contorná-la.

Acordo inicial único autoriza análise, decomposição, isolamento, subagentes,
testes, correções, supervisão e integração **local da fixture** nos tetos acima.
Git de entrega, instalação, restart, produção, credenciais, dados reais e
egress adicional ficam excluídos. Uma pergunta por passo já coberto conta
como intervenção redundante. Pergunta por autoridade realmente nova conta
separadamente; não premiar o Manager por ignorar um limite legítimo.

Para não exigir sua presença durante os runs, pedidos cobertos recebem a
resposta fixa “já coberto pelo acordo inicial”, com contador; pedidos fora
do acordo ficam pendentes e somente a dependência afetada é estacionada.
Esse protocolo é aprovado junto do piloto; não simula aprovação humana nova.
Contar separadamente solicitações ao dono, respostas automáticas do protocolo
e intervenções humanas realmente realizadas. As primeiras são um indicador
de atrito potencial, não minutos de espera humana medidos.

## Métricas e critérios

| Métrica | Coleta |
|---|---|
| Tempo | Da meta recebida ao gate integrado; preparação e pausas separadas; timestamps reais dos Managers e auxiliares |
| Consumo | Input, cached input, output e raciocínio observado por chamada; soma por run, incluindo falhas; campo indisponível permanece null |
| Retrabalho | Entregas devolvidas, ciclos corretivos e reabertura de critérios antes verdes; setup/TDD esperado contado à parte |
| Intervenções | Solicitações totais/cobertas/fora do acordo, respostas automáticas e intervenções humanas reais, separadas; vínculo ao trecho do acordo |
| Paralelismo útil | Ownership disjunto, intervalos reais de execução sobrepostos e handoffs aproveitados na entrega final; somente overlap de processos não basta |
| Supervisão | Falha simulada registrada; trabalho independente preservado; diagnóstico e recuperação dentro do escopo/saldo |
| Integração | Oráculo funcional completo no resultado combinado e zero conflito/overwrite; teste isolado de worker não substitui o gate integrado |

Aceite funcional: parser válido/inválido, JSON malformado, vazios, duplicatas,
booleano no lugar de duração, totais e renderização determinísticos. Aceite
de coordenação: arquivos com dono, nenhum writer concorrente no mesmo arquivo,
nenhuma autorização inventada, todos os handles terminais/estacionados e
nenhum sucesso falso. O controlador verifica a evidência, não o agente.

Resultado favorável exige funcionalidade preservada, nenhum desvio de escopo
e sinais reais nas dimensões exercitadas: decomposição/paralelismo em S1,
supervisão em S2 e integração em todos os runs. Para performance,
mostrar os deltas pareados: aceitar como sinal inicial melhora de tempo
ou redução de intervenções sem aumento relevante de retrabalho, deixando
explícito qualquer aumento de consumo. Não exigir simultaneamente economia
e velocidade; a qualidade e o respeito às fronteiras vêm primeiro.

Com quatro runs, o resultado é **piloto direcional**, não significância
estatística nem adoção geral. Se ambos os braços forem bons, registrar isso;
não fabricar vantagem. Se contadores faltarem, economia fica inconclusiva.

## Portabilidade e entregáveis

O primeiro A/B acontece somente no host Codex já comprovado. Cenários,
interfaces, oráculo e recibos são neutros em relação ao host. Cada recibo
declara host/harness, modelo/effort solicitado/enviado/observado, permissões,
digests, IDs e tempos; não carrega prompts privados, contas ou chaves.

Claude e Orca **não** recebem modelos do Host Codex nem passam a usar sua via:
usam sua própria seção do elenco e o contrato de invocação vigente. Dois
smokes funcionais futuros, um por host, podem conferir a portabilidade;
não estão neste orçamento e não comparam custo entre modelos diferentes.
Falta de prova nesses hosts permanece explícita, sem bloquear a proposta Codex.

Arquivos experimentais futuros ficam em `docs/experimentos/T-151-piloto/`:
`protocolo.json`, `fixture/`, `oracle/`, `runs/` e `comparacao.md`. Originais
sensíveis ficam locais/ignorados; nenhum desses artefatos existe ainda.
Não criar novos worktrees/branches agora nem remover os existentes.

## Execução após aprovação

- [ ] Congelar ambos os bundles, fixture, oráculo, roster e o briefing idêntico;
  registrar digests e conferir autoridade/capacidade dos tetos, sem inferência.
- [ ] Executar S1/A, S1/B, S2/B e S2/A, preservando todas as tentativas.
- [ ] Auditar ownership, falha, handoffs, integração e limites; aplicar oráculo.
- [ ] Publicar comparação local com tempo/tokens/retrabalho/intervenções e
  lacunas, sem declarar adoção geral, lucro ou atualização dos chats.

**Próxima decisão:** aprovar ou ajustar somente este piloto e seu orçamento.
Até lá, nenhum run, agente novo ou chamada externa desta avaliação.
