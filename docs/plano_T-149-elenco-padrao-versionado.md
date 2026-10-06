# T-149 — Elenco padrão da versão, adotado explicitamente por projeto

> Plano aprovado pelo dono em 2026-10-05; implementação local em verificação/revisão.
> Commit/push autorizados após gates. Revisão externa, bump e integração pendentes de cobertura;
> sem publicação, instalação, restart ou adoção automática dos elencos ativos.
> Frente `elenco-padrao`, host Codex. Base: main `fbc9b2f`, Orquestra 0.30.0.

## Resultado esperado

Cada release distribui uma única sugestão de modelos e efforts para os dois
hosts. Depois de atualizar/carregar o plugin, o dono pode dizer:

> Siga o elenco padrão desta versão do Orquestra.

O Manager identifica o host e a versão carregada, mostra a diferença, verifica
a capacidade dos papéis que mudam e adota o padrão no projeto atual. A frase
define o alvo da adoção; não autoriza inferência de prova, transferência de
código, instalação, restart nem mudança de outras contas/projetos.

O padrão é uma recomendação de release, não um seletor automático do modelo
recém-lançado. Atualizar o plugin disponibiliza uma nova proposta; não modifica
silenciosamente um elenco já adotado nem workers em execução.

## Diagnóstico verificado

1. `orq/commands/elenco.md:365` e `:389` ainda sugerem Astra para planners/review
   OpenAI e modelos antigos para docs/scout, embora as três faixas de
   implementação Codex já sejam Luna 6/medium, Sol 6.1/high e Sol 6.1/xhigh.
2. `memory/wiki/_elenco.md:202` mantém na seção Codex planners Astra/max,
   implementers/docs/scout Terra 5.6/xhigh e reviewer no alias `opus`. Na seção
   Claude, planner de sistema/reviewer já usam Sol 6.1, mas seu preset local
   `padrao` ainda restaura Astra. Isso foi preservado deliberadamente no T-148;
   não é evidência de merge perdido ou de migração já autorizada.
3. `orq/commands/elenco.md:304` troca um preset persistido do projeto, não o
   padrão da versão instalada. Fábrica, preset e time ativo são coisas distintas
   sem uma origem versionada que as torne fáceis de comparar.
4. Os frontmatters de `orq/agents/orq-planner.md`, `orq-docs.md`,
   `orq-reviewer.md` e `orq-scout.md` ainda usam aliases; nenhum dos cinco agentes
   declara effort. `run-opus-reviewer.py:166` aceita `--model`, mas não recebe nem
   encaminha `--effort`. Atualizar só as tabelas não resolve a chamada real.
5. `lint-coerencia.py:941` valida cada documento contra seus próprios presets.
   Em `:2511`, a guarda de reviewer ainda congela Astra. Em
   `test_elenco_perfis.py:206`, o snapshot histórico impede promover candidatos
   no projeto, mas não é uma definição de fábrica para releases futuras.
6. A cópia global `~/.agents/skills/orq/SKILL.md` ainda ensina
   painel de revisores e exemplos antigos, divergindo da skill versionada.
   Existe concorrência de instruções; não foi comprovado qual delas prevaleceu
   nos outros chats. Sua substituição/remoção não será feita neste plano local.

Foram consultados os CLIs locais sem inferência: Claude Code 2.1.290 e Codex CLI
0.160.0. Isso não prova acesso à conta, modelo efetivo ou capacidade dos demais
projetos. Este é um plano preparado pelo Manager; não há parecer de planner
externo nem aprovação de revisão independente nesta etapa.

## Elenco recomendado

Faixa continua significando risco/incerteza, não quantidade de arquivos. O
Manager classifica a tarefa, explica a escolha e reavalia a faixa após o plano;
alto risco conserva piso pesada. Não exigir que o dono escolha um modelo por
tarefa.

| Papel | Host Codex | Host Claude |
|---|---|---|
| planner · interface | Opus 5.5 / high | Opus 5.5 / high |
| planner · sistema | Sol 6.1 / xhigh | Sol 6.1 / xhigh |
| implementer · leve | Luna 6 / medium | Sonnet 5.5 / low |
| implementer · normal | Sol 6.1 / high | Sonnet 5.5 / medium |
| implementer · pesada | Sol 6.1 / xhigh | Sonnet 5.5 / high |
| reviewer | Opus 5.5 / high | Sol 6.1 / xhigh |
| docs | Luna 6 / low | Sonnet 5.5 / low |
| scout | Luna 6 / medium | Sonnet 5.5 / low |

IDs candidatos exatos: `gpt-6.1-sol`, `gpt-6-luna`, `claude-opus-5-5` e
`claude-sonnet-5-5`. Astra, Terra, Fable e outros modelos não são apagados de
presets ou overrides; deixam de ser a sugestão de rotina deste novo padrão.
O Manager permanece no modelo/effort da sessão escolhido pelo dono.

Planner cruza vendor pelo domínio; reviewer permanece único e do vendor oposto
ao host. Implementer, docs e scout permanecem no vendor do host. Anthropic no
Codex continua somente via Claude CLI; OpenAI no Claude usa a via do Companion
aprovada no projeto, com o contrato de identidade T-089 preservado. Não há API
key manual, proxy de autenticação ou substituição automática de mecanismo.

Os efforts acima são uma recomendação a validar, não prova de qualidade ou
economia. O mesmo nome de effort não garante trabalho/custo igual entre modelos.

## Desenho fechado proposto

### Uma fonte distribuída, uma versão derivada

- Criar `orq/references/elenco-padrao.json`, com schema, host, papel, ID exato,
  effort e política de mecanismo. Não guardar credenciais, conta, recibos locais
  nem um número de versão independente.
- A versão vem exclusivamente de `orq/.claude-plugin/plugin.json`; permanecem
  as quatro âncoras existentes. O novo JSON não é uma quinta âncora.
- Um resolvedor Python de biblioteca padrão carrega e valida o catálogo. Os
  consumidores leem essa fonte; tabelas demonstrativas distribuídas são
  renderizadas dela e conferidas pelo lint, não defaults mantidos à mão.
- Obter o pacote pelo `ORQ_PACKAGE_ROOT` absoluto, existente e verificado da
  sessão. Não usar `latest`, symlink mutável, cache antigo incompleto ou checkout
  de desenvolvimento como padrão de produção. Se a sessão carrega uma versão
  diferente da instalada, informar a diferença antes da adoção.

### Adoção explícita e escopo

- `padrão da versão` / `padrão Orquestra` seleciona o catálogo do pacote
  carregado. `perfil padrao` continua sendo o preset local legado: mostrar sua
  origem e diferença, sem reinterpretar um comando antigo silenciosamente.
- Em projetos novos, propor a fábrica do mesmo catálogo no `init`; materializar
  só depois do gate de capacidade e aprovação do alvo.
- Em projetos existentes, trocar apenas os papéis do host resolvido, com diff
  anunciado. Preservar a seção do outro host, presets personalizados e vias
  habilitadas/desligadas. Não percorrer nem reescrever todos os repositórios.
- Exceções explicitamente registradas permanecem e aparecem no resumo. Para
  removê-las, exigir intenção explícita de substituir também as exceções.
  Valores legados sem origem são exibidos como legados, nunca certificados como
  capacidade nem classificados como override por suposição.
- O perfil adotado registra origem, versão do pacote, digest do catálogo, data
  e exceções. A origem pertence ao perfil adotado, não ao release corrente:
  instalar N+1 não falsifica que o projeto continua em N.
- Reaproveitar apenas recibos reais compatíveis para modelo, effort, mecanismo,
  sandbox e conta/host. A aprovação do padrão não libera novas sondas. Havendo
  lacuna, manter o elenco inteiro inalterado e listar somente as provas faltantes;
  não aplicar metade do perfil, não repetir provas já válidas e não improvisar
  fallback. Outras ações locais elegíveis podem continuar.
- Workers já iniciados concluem com a configuração fixada no despacho. A troca
  vale para despachos futuros; não interrompe nem reinicia chats em curso.

### Effort deve chegar à chamada

- Resolver modelo e effort juntos; não herdar do Manager sem avisar nem usar
  modelo declarado na tabela com outro effort no mecanismo.
- No runner Anthropic, acrescentar argumento explícito de effort validado e
  encaminhá-lo ao Claude CLI. Preservar isolamento, zero-tools, identidade exata,
  recibos, sanitização, limites de bytes e regra sem retry.
- Nos agentes Claude, alinhar frontmatter/fallback e despacho por papel/faixa;
  o implementer compartilhado não pode fixar a mesma faixa para os três casos.
- No Codex/Companion, usar o mecanismo de override realmente suportado pelo
  runtime; não introduzir flag inventada. Não inferir capacidade nativa da prova
  da CLI nem capacidade de escrita de uma prova read-only.
- Recibo distingue effort solicitado, argumento enviado e effort observado.
  Ausência de campo observado não vira comprovação do servidor; se o CLI recusar
  ou limitar o effort, devolver diagnóstico, sem downgrade silencioso.

### Cópias globais e outros projetos

O release deve declarar como localizar versões/skills concorrentes e mostrar um
diagnóstico específico, sem recomendar modelos antigos a partir delas. Este
plano documenta a cópia global encontrada e prepara uma correção distribuída da
prioridade/procedimento. Alterar, instalar ou remover aquela cópia na máquina
exige gate separado, com alvo explícito e recuperação. Não presumir que uma
instrução escrita consegue impedir o carregamento de uma skill pelo harness.

## Implementação em seis passos

Somente após aprovação deste plano, em worktree dedicado `codex/t149-elenco-padrao`
(preferir reutilizar um checkout apropriado). Sem tocar no checkout vivo T-144.

| ID | Porte | Arquivos/responsabilidade | Critério de conclusão local |
|---|---|---|---|
| P1 | M | `orq/references/elenco-padrao.json`, `orq/scripts/elenco_padrao.py`, `test_elenco_padrao.py` | RED/GREEN de schema, papéis, IDs/efforts, versão derivada e digest; consulta pura, sem rede nem escrita de elenco |
| P2 | M | `orq/commands/elenco.md`, `init.md`, `orq/skills/orq/SKILL.md` | Fábrica/adoção distinguem versão, preset e override; diff por host, legado explícito e rollback preservado |
| P3 | M | `plan-next.md`, `implement-next.md`, `revisar.md`, `orq/agents/orq-*.md` | Todos resolvem a mesma fonte; faixas, vendor, via, isolamento e effort ficam coerentes; sem bypass do gate de capacidade |
| P4 | M | `run-opus-reviewer.py` e seus testes existentes | CLI falsa comprova `--model`/effort corretos, recusa inválido, não altera zero-tools/identidade nem introduz retry |
| P5 | M | `lint-coerencia.py`, `test_elenco_perfis.py`, novos testes descobertos | Guarda estrutural vem do catálogo; fixtures históricas continuam testando preservação sem congelar a fábrica ou o projeto para sempre |
| P6 | S | `arquitetura.md`, `distribuicao.md`, índice/thread e instruções de atualização | A frase natural, proveniência, escopo, exceções e limites de instalação estão descritos; gates locais e diff allowlistado registrados |

O `_elenco.md` ativo deste repositório não é ativado durante P1–P6. A migração
prática ocorre depois da entrega/carregamento autorizados e da comprovação dos
papéis novos. A fixture legada é separada do arquivo vivo para não forçar
reintrodução de Terra/Fable a cada mudança futura aprovada.

## Testes de aceite e mutation checks

- Dois hosts completos; Manager não é spawn nem modelo trocado pelo perfil.
- Mudar uma célula do catálogo atualiza todos os consumidores; deixar uma tabela
  ou fallback desatualizado reprova o lint/teste correspondente.
- Release N+1 aparece como proposta; projeto adotado em N não muda sozinho.
- Adoção no Codex não modifica Host Claude; preset local e override explícito
  sobrevivem; vias desligadas não são reativadas pela adoção.
- Uma prova ausente impede qualquer escrita do perfil; receipt válido é
  reaproveitado; catálogo/alias sem prova não libera execução.
- CLI falsa recebe o ID completo e effort por papel/faixa; retirar o argumento,
  trocar modelo ou aceitar effort inválido faz o teste falhar.
- Alterar o modelo do revisor para o vendor do host, quebrar igualdade do
  `threadId`, enviar `--wait` ao `task` ou enfraquecer zero-tools reprova guardas
  existentes, sem novas chamadas a provedores.
- Frase natural inequívoca adota o padrão versionado; troca genérica de perfil
  conserva a semântica local e informa a origem. Não prometer propagação para
  todos os chats de uma edição de arquivo.

Gates locais obrigatórios de produto, sem bytecode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'
claude plugin validate ./orq --strict
PYTHONDONTWRITEBYTECODE=1 python3 orq/scripts/lint-coerencia.py .
```

Depois: revisão independente do vendor oposto com pacote sanitizado, somente
com autorização de egress e teto explícitos; não simular parecer nem trocar o
revisor por dificuldade de acesso. Publicação/instalação e teste comportamental
nos hosts não são substituídos pelos gates locais.

## Alternativas e rollback

Recomendado: padrão versionado com adoção explícita. Herança dinâmica mudaria
projetos silenciosamente e prejudicaria reprodução de tarefas em execução.
Reescrever todos os elencos agora exigiria escopo/autoridade desconhecidos e
continuaria sem resolver a divergência do próximo release.

Manter o perfil anterior e sua proveniência durante a adoção para reversão
cirúrgica na seção do host. Reverter um perfil também precisa de capacidade
compatível; não restaurar vias/modelos antigos como fallback automático. Se a
instalação tiver instruções concorrentes, diagnosticar antes de declarar adoção.

## Uma decisão agora

**Aprova o elenco proposto e a implementação local do T-149 com adoção explícita
por versão?** Esta aprovação não inclui bump, commit, push, publicação,
instalação, restart, migração em massa ou chamadas externas. A próxima versão
livre e a entrega serão tratadas no gate correspondente; nenhuma foi reservada.

## Fontes públicas consultadas

- [GPT-6.1 Sol — modelos e efforts](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
  e [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).
- [Claude Code — configuração de modelos, versão mínima e precedência de effort](https://code.claude.com/docs/en/model-config)
  e [subagentes e effort explícito](https://code.claude.com/docs/en/sub-agents).
- [Anthropic — significado dos níveis de effort](https://platform.claude.com/docs/en/build-with-claude/effort).

Documentação e catálogo sustentam a proposta de compatibilidade, não prova de
modelo efetivo, acesso da conta, economia ou disponibilidade em todos os hosts.
