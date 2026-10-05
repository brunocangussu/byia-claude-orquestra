# T-141 — Orquestra portátil no Orca

Data: 2026-09-29. Estado: desenho para revisão, **não implementado**.
Frente: `@frente-orca-portabilidade`, host `@codex`.

## Intenção e limites

O dono quer usar Orca como IDE principal e preservar agentes especializados,
qualidade e economia, sem depender das interfaces desktop Codex/Claude.
Isso não significa eliminar os CLIs/harnesses: eles continuam executando
as tarefas nos terminais do Orca. Não trocar autenticação, providers,
configuração global, memória ou permissões implicitamente.

## Alternativas e escolha proposta

1. **Orca como ambiente; Orquestra como política (recomendada).** Reusar
   Codex CLI e Claude CLI, papéis e skills existentes. Adaptar despacho e
   recibos às capacidades do Orca, preservando revisão e memória.
2. Orquestrador novo em API/SDK: maior controle de ferramentas, mas outra
   autenticação/cobrança e harness; não é requisito desta migração.
3. Substituir o núcleo por Orca/Pi: mistura mudança de harness com mudança
   de política e invalida comparações do T-139. Não recomendado agora.

## Fronteiras de responsabilidade

- **Orca:** IDE, terminais, worktrees e coordenação de execução.
- **Orquestra:** board, ownership, papéis, classificação de risco, gates,
  composição das instruções e critérios de aceite.
- **CLIs:** loop agêntico, ferramentas e sessão de cada vendor. Opus/Sonnet
  permanecem chamados pela Claude CLI, sem credencial manual nem API direta.
- **Roteador opcional:** recomenda faixa/necessidade de etapa; não executa,
  não altera permissões e não move cards.
- **AI-Memory:** captura e consulta compartilhadas, validadas pelo banco e
  por sessão real, não por health/exit code isolados.

Um único Manager conduz cada fluxo e altera o board. Não criar um segundo
orquestrador concorrente porque Orca também oferece coordenação.

## Agentes especializados sob demanda

Preservar os contratos já existentes de Scout, Planner, Implementer,
Reviewer e Docs. Cada despacho fixa responsabilidade, arquivos permitidos,
tools/permissões, skill de domínio pertinente e aceite observável.
Contexto carregado sob demanda; não copiar bibliotecas inteiras de perfis.
Exploração e planejamento dependem da necessidade real do card; não retirar
um gate obrigatório para tornar o desenho mais enxuto.

Implementer é writer único no worktree. Reviewer independente é read-only e
de vendor oposto à implementação/host conforme contrato vigente. Manager
integra somente após review e revalida o estado integrado. Docs registra o
resultado e a prova; commit não encerra o card sem validação do dono.

## Interface portátil de despacho

Contrato lógico, ainda sem código: card/papel, objetivo, snapshot, ownership,
critérios de aceite, modelo/effort solicitados, permissões e teto/tentativas.
O adaptador usa argumentos estruturados e valida o catálogo/capacidade;
texto do roteador não vira argumento livre de shell.

Recibo liga despacho, sessão, snapshot e resultado a artefatos/testes.
Identidade solicitada e identidade observada são campos diferentes; ausência
de prova é `UNKNOWN`, não sucesso presumido. `accepted` não é `turn_started`,
e prompt entregue não comprova carregamento de skill nem modelo efetivo.

O guia local do Orca expõe preferências `--model`/`--effort` em
`orchestration worker-start` para terminais novos de Claude/Codex e pede
comparar `launch.requested`/`launch.effective`. Não reproduzir flags do
Companion nessa via. Reuso de terminal só após settlement; se precisar
trocar modelo/effort, abrir despacho compatível em vez de presumir override.

Reusar os trabalhos T-085/T-087/T-089/T-090; não implementá-los novamente
nem alterar suas frentes. IDs de runtime Orca complementam, não substituem,
ownership e estado canônico da Orquestra.

## JEV e Decisions sem prender o executor a um vendor

No T-098, manter uma interface neutra: entradas mínimas sanitizadas e
saídas de catálogo fechado — faixa sugerida, categoria de tratamento e
abstenção. Motivo/confiança só entram se a superfície fornecer esses campos;
nunca fabricar confiança nem comparar scores não calibrados entre providers.

Regras locais aplicam piso de risco/privacidade/autoridade antes e depois da
recomendação. Timeout, resposta inválida ou abstenção mantêm o caminho seguro
do Manager. O roteador não remove review/gates nem libera execução sozinho.
Um serviço OpenAI pode recomendar Claude CLI, e vice-versa: quem classifica
não precisa executar. Isso é proposta arquitetural, não integração comprovada.

Decisions API foi mencionada pelo dono como anúncio de hoje. A pesquisa
oficial desta sessão não confirmou documentação técnica, preço ou acesso;
não assumir endpoint, compatibilidade ou equivalência com JEV. É candidata
condicionada à verificação desses itens. Não muda pacotes congelados nem
autoriza chamadas. API/classificador é uma superfície diferente das
assinaturas usadas pelos CLIs; verificar seu contrato de acesso/cobrança.

## Provas antes de migrar

1. Contrato local sem inferência: composição exata, modelo/effort, isolamento,
   ownership, argumentos inválidos e recibos correlacionados.
2. Piloto sintético Orca: Manager único, uma implementação em worktree e
   review cruzado; conferir identidade/permissões efetivas e resultado real.
3. Memória: no banco AI-Memory, ligar a sessão a `session-start`, `user-prompt`,
   `pre/post-tool-use` e `stop` nos dois CLIs; só session-start não basta.
4. Continuidade: seguir o fluxo sem as interfaces desktop Codex/Claude como
   dependência; não encerrar sessões reais do dono para realizar essa prova.
5. Comparar a mesma tarefa/modelo/effort nas duas interfaces, com critérios
   independentes, latência, retrabalho, falhas e custo até aceite.

O benchmark do T-098 continua separado: regras locais/Manager versus JEV e,
quando verificável, Decisions. Erro de downgrade de alto risco, abstenção,
tempo e custo até entrega aceita importam mais que preço por classificação.
Não reciclar gabarito aberto como amostra cega nem alegar ganho do T-139
com a troca simultânea de harness/modelo.

O gate preventivo de **zero-tools** do avaliador Codex no T-139 permanece
obrigatório: read-only, flags solicitadas ou ausência de eventos não o
comprovam. Migrar para Orca não libera os pacotes congelados nem autoriza
trocar o avaliador para contornar essa lacuna.

## Evidência e fronteira desta etapa

Orca local 1.4.216: `orca status --json` retornou app em execução,
runtime pronto/alcançável e capacidades de orquestração/preferências de
launch. Isso não prova o fluxo completo. Não iniciamos worker, inferência,
migração, instalação, publicação, commit/push ou restart nesta análise.

Fontes: [Orca oficial](https://github.com/stablyai/orca), guias versionados
locais `orca skills get orca-cli` e `orca skills get orchestration`, incluindo
`references/coordinator-loop.md`; [agentes focados](https://developers.openai.com/api/docs/guides/agents/define-agents).

Próxima etapa: revisar este desenho e preparar o piloto executor-ready,
aproveitando as frentes existentes. Rollback de um piloto futuro encerra
somente seus terminais/fixtures, preservando branch, board, memória e sessões
reais; não toca nos caches/homes globais para contornar incompatibilidade.
