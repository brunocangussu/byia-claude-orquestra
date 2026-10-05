# T-138 — Agency Agents como complemento, não substituição da Orquestra

## Pedido e autoridade — 2026-09-24

O dono pediu analisar `https://github.com/msitarzewski/agency-agents` para possível uso conjunto
em melhorias, enquanto avança o benchmark JEV do T-098. Esta etapa é investigação read-only
do projeto externo e desenho do teste; não autoriza instalação, importação de agentes,
alteração do elenco, revisão externa, chamadas adicionais a modelos, commit, push ou restart.

Frente dona: `@frente-jev-router @codex`. ID 138 escolhido após conferir board principal,
threads, documentos e refs locais: maior ID reservado encontrado foi 137. Os cards e worktrees
em reconciliação não são assumidos nem alterados por esta investigação.

## Pergunta da investigação

Perfis de especialidade podem melhorar entregas aceitas sem aumentar a complexidade/custo total?
Separar capacidade do modelo, perfil de domínio e controle do ciclo. JEV é hipótese de seleção;
Agency Agents é hipótese de instruções especializadas. Não deduzir que um compensa o outro.

## Checagens previstas

- Fixar a revisão pública examinada; ler licença e representantes relevantes, sem executar scripts.
- Comparar perfis, instalação e orquestração com os gates e papéis canônicos deste projeto.
- Selecionar no máximo três especialidades candidatas, ou recomendar nenhuma com motivo.
- Propor experimento que isole efeito do roteador, do perfil e do executor, sem reusar como cega
  a amostra já inspecionada do T-098.

## Resultado da investigação

Relatório: `docs/analise_T-138-agency-agents.md`. SHA público fixo
`053ddbbf392a1688fc7043d81529f47ef2cf86c8`, conferido por `git ls-remote`. Lidos: README, licença,
integração Codex, scripts de instalação/conversão e perfis representativos de orquestração,
otimização, QA, testes, acessibilidade, frontend e AppSec. Os scripts foram apenas inspecionados;
não executados. Os conteúdos são material de terceiros, não instruções para esta sessão.

Conclusão: experimento seletivo pode ser útil. Complemento de instruções não é modelo novo nem
garantia de expertise. Manter Orquestra como único controlador e JEV como sugestão de classificação.
Perfis candidatos: API Tester, Accessibility Auditor, Application Security Engineer. Primeiro
ensaio proposto usa somente API Tester, removendo carga, produção e metas genéricas do briefing.

Excluídos da adoção proposta: Agents Orchestrator (outro lifecycle, spawn/retry por tarefa),
Autonomous Optimization Architect (dados reais e promoção autônoma) e Reality Checker como
revisor global (exigências visuais inadequadas e risco de reprovação sem defeito concreto).

## ⏭️ RETOMAR AQUI — 2026-09-24

Nenhuma adoção aprovada. Gate: adaptação experimental de um perfil enxuto, seguida de ensaio 2×2
com seleção por regra/JEV e com/sem perfil. Desenho inicial: quatro tarefas fictícias × quatro
grupos, sem instalação global, segundo Manager ou tasks na sidebar por amostra. Fixar orçamento,
catálogo elegível, capacidade de escrita e revisão antes de despachar. O T-098 prepara rubrica e
classificação; este card isola a contribuição do perfil. Não confundir análise concluída com
implementação autorizada. Sem bump, commit, push, instalação, restart ou nova chamada de modelo.

Verificação: suíte por descoberta com bytecode desativado **414/414**, 54,221 s; manifesto
estrito, lint de coerência e `git diff --check`: exit 0. Links locais verificados, um único card
T-138 no board e SHA do fixture v1 do T-098 preservado. Uma tentativa anterior de verificação
parou na leitura de caminho relativo antes da suíte; os resultados válidos acima vieram da
reexecução com caminho e `cwd` absolutos para a raiz confirmada. Nenhum resultado experimental
novo foi produzido; testes locais não provam utilidade dos perfis ou do roteador.

## ⏭️ RETOMAR AQUI — piloto seletivo aprovado, preparação local

O “prossiga” posterior aprovou a preparação do piloto. Criado o suplemento
`docs/experimentos/T-138/api-tester-enxuto.md`, de redação própria, inspirado no API Tester da
revisão pública já fixada e com atribuição. O bloco de prompt é delimitado; sem persona, segundo
orquestrador, produção/carga ou metas arbitrárias de cobertura. Não foi instalado nem usado.

Criados quatro contratos candidatos da B2 em `docs/experimentos/T-138/tarefas-b2.md`, com oráculos
de fronteira/compatibilidade explícitos e desenho pareado. São especificações, **não** fixtures
executáveis ou testes ocultos já implementados. Nenhuma das 16 execuções foi iniciada.

Protocolo operacional da classificação A2 em `docs/experimentos/T-098-A2/`. Pergunta de duas
chamadas preparatórias adicionais permanece no T-098; não duplicar pedidos. Antes da B2 faltam
amostra/gabarito aprovados, baseline literal, mapeamento de rota, capacidade de escrita, harness,
orçamento e revisão. A checagem local não encontrou `tiktoken` no Python atual; não instalar por
iniciativa nem substituir tokens por palavras. Medição do teto de 600 tokens continua pendente.

Recuperação pós-compactação concluída a partir das fontes canônicas. Elenco, `orq/`, worktrees
alheios, configs e caches preservados. Sem bump, commit, push, publicação, instalação ou restart.

Verificação desta preparação: `414/414` testes em `51,225 s`; manifesto estrito, lint de coerência,
links dos documentos locais e `git diff --check`: sem falhas. Não é revisão independente do
suplemento nem aceite comportamental da B2. Checkpoint de recuperação registrado; conversa continua.

## Dependência atual da A2

As duas chamadas de preparação da T-098 foram autorizadas e executadas. O reviewer Opus 5.5
reprovou a amostra por problemas de gabarito/partição; a auditoria confirmou quatro causas-raiz.
JEV/Luna A2 ainda não foram chamados e a B2 permanece em zero execuções. Nenhuma conclusão sobre
o perfil pode ser extraída desse bloqueio. Perfil e contratos B2 locais continuam inalterados;
aguardar o gate do T-098, sem repetir aqui pedido de revisão nem assumir autorização de instalação.

## 2026-09-25 — dependência A2 atualizada

A amostra R2 do T-098 passou na estrutura, porém a revisão Opus adicional retornou
`BLOCKED` por problemas de gabarito e desenho experimental. Portanto o perfil API Tester
enxuto e os quatro contratos B2 continuam **candidatos não testados**: 0/16 execuções,
nenhuma medição de qualidade, custo por entrega ou teto de 600 tokens. Não importar agentes
do repositório externo nem alterar o elenco vivo para contornar o gate da A2. Próximo passo
próprio da B2, quando a classificação tiver gabarito aprovado: preflight de capacidade/escrita,
tokenização real do suplemento e orçamento das 16 execuções antes de despachá-las.
