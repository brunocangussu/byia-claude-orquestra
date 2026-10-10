# T-151 — autonomia técnica por meta e paralelismo útil

**Frente dona:** alinhamento · **Host:** Codex · **Trilha/faixa:** sistema/pesada.
**Estado:** plano aprovado para implementação local em 09/10, após a
confirmação humana de que a referência era T-151; não autoriza entrega. Pedido humano na thread T-151;
recibo em `docs/T-151-analise-2026-10-09-recibo.json`.

## Resultado desejado

O dono define o objetivo e as fronteiras. O Manager, usando a capacidade da
própria sessão, decide os detalhes técnicos necessários, organiza subtarefas,
aceita ou devolve planos técnicos e distribui trabalho dentro desse acordo.
Não espera nova confirmação por cada correção, teste, complemento ou agente
já coberto. Um bloqueio em uma dependência não paralisa as demais frentes.

Há dois problemas concretos, sem necessidade de um subsistema novo:

1. O acordo de continuidade existe, mas a coleta de autorização continua
   fragmentada. Um mesmo objetivo passa por perguntas adicionais quando o
   planejamento não explicita sua delegação e cobertura desde o início.
   O Loop A:206 e SKILL.md:343 exigem aprovação, enquanto o Loop B:47 já
   proíbe nova pergunta por subpasso coberto: falta ligar esses critérios
   ao aceite técnico do complemento dentro da meta aprovada.
2. `orq/skills/orq/SKILL.md:154` ainda diz “um sub-agente por card”. O Planner
   já decompõe frentes, mas essa restrição não dá ao Manager uma política
   útil de despacho paralelo para entregas independentes.

O cache Codex 0.32.0 foi conferido contra fonte remota limpa em 09/10. Usar
uma versão antiga não é a causa atual dessas duas lacunas. Não prometer que
a atualização da sessão, sozinha, implementou esta proposta.

## Abordagem recomendada

### Um Manager, não outra LLM aprovadora

A autoridade técnica é delegada pelo humano e exercida pelo Manager. Ele
não precisa abrir uma chamada adicional para aprovar cada etapa. O Planner
ajuda a fechar desenho e dependências; o Reviewer continua independente e
não cria permissões. Uma resposta “aprovado” de agente nunca substitui o
acordo humano de escopo, operação ou orçamento.

O registro inicial da meta reúne finalidade, frente, exclusões, aceite,
delegação técnica e operações locais cobertas. O Manager propõe os limites
e mantém a referência da fonte humana. Subplanos necessários e compatíveis
com essa meta são avaliados tecnicamente por ele, não reenviados ao dono
como pedidos repetidos. Sem meta/acordo verificável, não se inventa um.

Reutilizar o registro da thread, o medidor e o contrato T-143/T-150. Não
criar ledger paralelo, segundo Manager, novo agente obrigatório, serviço
remoto, API aprovadora ou mecanismo global que ligue tudo silenciosamente.

### Decomposição e paralelismo

O Manager avalia utilidade, não número de arquivos. Duas entregas com
interfaces fechadas, sem dependência serial e sem disputa de escrita são
candidatas a paralelismo. Tarefa pequena ou desenho ainda aberto continua
serial quando o custo de delegar superar o ganho esperado.

Começar com poucas frentes úteis; ampliar somente quando houver outra
entrega independente e capacidade. Isso não é teto de revisões nem obrigação
de criar dois agentes para qualquer tarefa. Modelo/effort/via continuam
resolvidos pelo elenco vigente e sua prova contextual; não usar a herança
do Manager como atalho para economizar a conferência.

Cada agente recebe contexto curto e fresco, objetivo, entregável, arquivos
permitidos/exclusivos, interfaces, dependências, proibições, critério de
aceite e handoff. Scout/Planner investigam read-only. Writers ficam em
checkouts próprios e não disputam os mesmos arquivos. Havendo sobreposição
ou dependência, serializar o trecho afetado. Não criar worker por arquivo,
fork do histórico inteiro ou árvore de agentes recursiva por padrão.

O Manager prepara o isolamento local coberto pelo acordo e é o integrador
único. Worker não cria refs/worktrees, assume frente alheia, despacha outro
worker ou faz entrega Git. A conclusão de um agente não certifica a
integração: conferir diff e contratos, executar gates finais e preservar
resultados/handles. Observar o mesmo handle não é repetir a chamada.

### Onde uma decisão humana ainda importa

Uma decisão técnica dentro da meta não precisa de nova autorização. Mudança
material de finalidade, gasto/contratação novo, produção, dado sensível,
exclusão ou ação fora do acordo não vira “complemento técnico”. O Manager
explica a diferença e estaciona somente a ação dependente.

Revisões cross-vendor usam o envelope real já autorizado, saldo cumulativo,
destino/modelo/modo e tetos. Snapshot corrigido coberto não exige nova
pergunta nem renova saldo. Este pedido atual não abriu um orçamento
Anthropic nem recuperou gates consumidos. Se a meta incluir tais revisões,
o acordo inicial deve cobri-las, em vez de apresentar um pedido por rodada.

Entrega allowlistada, bump, commit, push e integração podem constar do mesmo
acordo inicial quando aprovados. Publicação, instalação, restart e produção
continuam distinguíveis. Nem aceitar o plano técnico nem concluir um teste
autoriza uma operação de entrega ausente. Validação prática não é presumida.

## Alterações candidatas e ownership

Manter uma única fonte de política, com remissões dos consumidores. Após
auditoria do Planner e Scout, estes são os alvos mínimos candidatos:

- `orq/skills/orq/SKILL.md`: autoridade delegada por meta e troca da regra
  absoluta de agente por card por despacho útil controlado pelo Manager.
- `orq/commands/plan-next.md`: contrato inicial consolidado, auditoria de
  subplano coberto e tabela de ownership/dependências.
- `orq/commands/implement-next.md`: fan-out com writers disjuntos, handles,
  coleta e integração pelo Manager; sem conceder entrega Git.
- `orq/agents/orq-planner.md`: complementar o handoff com vínculo ao aceite
  original e separar dúvida técnica de decisão humana nova.
- `AGENTS.md` e `CLAUDE.md` deste repositório: remissão curta ao contrato,
  sem substituir a aprovação inicial ou editar instruções globais.
- `orq/references/continuidade-evidencias.md`: conciliação com os contratos
  existentes, somente se necessária para evitar duas políticas concorrentes.
- Testes contratuais atuais de continuidade/coordenação: reaproveitar e
  acrescentar cenários específicos, sem refatoração de runner/host.

Não alterar elenco, modelos/efforts, presets, cache instalado, Companion,
AI-Memory, T-139/JEV ou cards de outra frente. Comandos de revisão/noturno
só recebem remissão se o diff real demonstrar necessidade.

## Passos e critérios verificáveis

| ID | Entrega verificável | Tamanho | Critério de aceite |
|---|---|---|---|
| P01 | Conciliar contrato delegado com T-143/T-150 e auditar fonte humana | S | A01: aprovação técnica e nova autoridade têm fronteiras explícitas, sem ledger novo |
| P02 | Corrigir instruções centrais e remissões necessárias | M | A02: subtarefa coberta segue sem pergunta repetida; meta ausente e fora de escopo não herdam aprovação |
| P03 | Definir despacho paralelo e integração com ownership | M | A03: arquivos disjuntos podem avançar; sobreposição/dependência serializam só o trecho afetado |
| P04 | RED/GREEN e mutações das guardas positivas/negativas | M | A04: cada invariante rompe com sua mutação; casos legítimos não geram bloqueio global |
| P05 | Gates locais, documentação e review no envelope efetivo | M | A05: discover/manifesto/coerência/diff-check verdes; review externo só se coberto, sem afirmar aceite antecipado |

O Manager registra a tabela no medidor somente quando começar o Loop B
sob o acordo efetivo. Os agentes desta análise não escrevem o ledger.

### Cenários mínimos de regressão

1. Meta e delegação verificáveis: complemento técnico necessário segue com
   referência ao mesmo acordo, sem aprovação humana repetida.
2. Plano/meta inicial ausentes, finalidade nova, frente/card alheios ou
   operação proibida: não criar cobertura fictícia.
3. Envelope de revisão válido: digest novo coberto conserva saldo; saldo
   gasto, tentativa incerta ou retry não coberto não recebem nova chamada.
4. Duas análises independentes; dois writers com ownership disjunto; disputa
   de arquivo; dependência A→B; falha de A enquanto B útil continua.
5. Worker sugere algo fora do escopo ou tenta delegar/Git: devolve ao Manager
   sem transformar sua resposta em permissão.
6. Recuperação de contexto preserva acordo, posse, consumo e handle; não
   repete chamada, muda modelo em silêncio ou lê outra thread como fallback.
7. Duas rodadas sem progresso exigem diagnóstico/estratégia, não encerram a
   meta, zeram orçamento ou contornam bloqueador comprovado.
8. Integração quebra contrato: gates detectam antes de declarar pronto.

## Evidência desta análise

As duas chamadas solicitadas pelo dono usaram CLI 0.160.1, perfis do elenco,
sandbox read-only e clone detached limpo de 6c8482a. Scout Luna 6/medium e
Planner Sol 6.1/xhigh terminaram com exit 0, sem retry; o clone permaneceu
limpo. Modelos/efforts/sandbox observados no cliente, não modelo interno do
servidor. Não são duas revisões independentes, campanha de desempenho nem
prova de economia. Saídas originais preservadas localmente; hashes/identidades
e uso reportado constam no recibo público. O uso acumulado inclui cache e
não equivale a custo financeiro; não foi medido ganho comparativo.

Auditoria do Manager: adotar vínculo concreto do complemento com o aceite,
recuperação do plano/fonte humana e fonte de política única. Não adotar a
sugestão de abrir três writers agora: contrato, fluxos e guardas têm
dependências. As regras de fan-out devem permitir trabalho realmente
independente, sem um teto por card e sem multiplicar agentes por arquivo.
O Planner não tinha as threads privadas como leitura autorizada; sua lacuna
de meta original é correta e não comprova falta de autoridade na conversa.
O Manager conserva a transcrição humana na thread, sem inventar orçamento
externo ou aprovação do desenho que ainda será apresentado ao dono.

Não houve alteração funcional do produto, bump, commit, push, publicação,
instalação ou restart nesta análise. A execução local do contrato e qualquer
entrega devem usar sua cobertura efetiva, sem renovar gates antigos.
