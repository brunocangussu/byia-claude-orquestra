# Frente: paridade operacional no Codex

## Card

`T-040` — transformar os atritos observados num projeto externo em comportamento padrão do plugin para qualquer repositório usado com Claude Code ou Codex.

## Evidência confirmada em 2026-08-09

- A árvore do repositório está limpa e a fonte, marketplace e cache do Codex estão em `0.20.0`.
- `codex plugin list` mostra `orq@orquestra` como `installed, enabled`.
- O Codex carrega a skill `orq`, mas não converte `orq/commands/*.md` em comandos `/orq:*`.
- A interface suportada pelo Codex é linguagem natural ou seleção por `/skills`; custom prompts com slash command são locais e estão depreciados.
- O Codex oferece `/statusline` nativa com itens fechados. A issue `openai/codex#17827` segue aberta para execução de script arbitrário, necessária para renderizar diretamente o board do Orquestra.
- O relato externo também expôs a necessidade de defaults reais por host: Manager Sol/high, Planner Sol/ultra, Implementer Terra/xhigh e painel obrigatório Opus 5 + Kimi K3.

## Escopo relacionado já existente

- `T-026`: instalação e smoke em hosts fora do Claude.
- `T-033`: template do elenco incompleto em projetos novos.
- `T-034`: consumidores não resolvem corretamente o time por host.
- `T-038`: composição não destrutiva da statusline no Claude.
- `T-039`: detecção de memória preexistente em outro formato.

`T-040` coordena a experiência Codex e os critérios de aceitação; não absorve nem reimplementa os cards acima.

## Decisão aprovada em 2026-08-09

- Linguagem natural + `/skills` formam o contrato principal no Codex.
- `/prompts:orq` pode existir somente como compatibilidade opcional, nunca como requisito nem como promessa universal do plugin.
- O desenho deve deixar explícito que `commands/` continua sendo a superfície de slash commands do Claude Code.

## Especificação

- Arquivo: `docs/superpowers/specs/2026-08-09-paridade-operacional-codex-design.md`.
- Desenho aprovado pelo dono em 2026-08-09.
- Autocrítica concluída: nenhum placeholder real, escopo de coordenação explicitado, limitações de statusline e modelos sem entitlement tratadas sem promessa falsa.
- Nenhum arquivo em `orq/` foi alterado nesta fase.

## Planos executáveis

- Core Codex `0.21.0`: `docs/superpowers/plans/2026-08-09-paridade-core-codex.md` — 4 Tasks, 27 Steps no desenho original; execução acrescentou o gate explícito de painel/correção antes do commit.
- Statusline nativa `0.22.0`: `docs/superpowers/plans/2026-08-09-statusline-nativa-codex.md` — 4 Tasks, 18 Steps.
- Autocrítica passou: cobertura de interface, elenco, init, statusline, diagnóstico, privacidade, verificação e release; nenhum placeholder.
- A primeira execução é `T-041`; `T-042` depende dela.
- Publicação, atualização de cache global e push não estão autorizados.

## Implementação T-041

- Worktree: `.worktrees/t041-paridade-core-codex`, branch `feat/t041-paridade-core-codex`.
- Task 1 RED→GREEN: template gera Matriz/Times, init migra aditivamente e lint guarda headings.
- Task 2 RED→GREEN: Planner/Implementer/painel resolvem host→papel→executor; Codex usa Sol/ultra,
  Terra/xhigh, Opus 5 e Kimi K3.
- Task 3 RED→GREEN: interface Codex por linguagem natural + `/skills`, diagnóstico em sete camadas,
  smoke em conversa nova e classificação de memória virgem/legada/parcial/completa.
- O bump `0.21.0` foi antecipado porque o guard de cache torna lint intermediário impossível quando
  `orq/` diverge de uma versão já publicada. Os quatro locais estão sincronizados.
- Manifesto, lint de coerência e probes locais passaram antes do painel.

## RETOMAR AQUI

`T-041` está em VALIDATE. A `0.21.0` passou localmente e em projeto externo; push foi autorizado e
confirmado no GitHub. Próxima ação: o dono abre nova sessão Codex no projeto real que antes falhava,
pede revisão e confirma `OPUS_MODEL=claude-opus-5` + parecer não vazio.

## Reabertura por validação real do Opus 5

- Codex e Claude instalados: `orq 0.20.0`; GitHub `main`: commit `164387c`, também `0.20.0`.
- No `0.20.0`, `revisar.md` não contém painel Opus no Host Codex; portanto o silêncio observado em
  outro projeto é reproduzível por contrato: o Opus nem é invocado.
- Sonda direta do CLI em repo e diretório externo: exit 0 em 4–6s, resultado `OPUS_REVIEWER_OK` e
  `modelUsage` contendo `claude-opus-5`. CLI/auth/modelo estão saudáveis.
- Na candidata `0.21.0`, prompt completo de 31–40 KB excedeu 180–300s; trechos focados responderam.
  A instrução crua não tem limite de entrada, timeout estruturado nem validação do modelo/saída.
- Hipótese confirmada: versão antiga explica a ausência total; briefings sem orçamento explicam o
  risco residual de silêncio mesmo depois da atualização. A correção deve atacar as duas camadas.

## Runner Opus 5 — implementação e revisão

- Runner lê briefing só por stdin; a sonda real do CLI confirmou esse modo em 5,7s.
- `OPUS_STARTED` sai imediatamente no stderr; prazo padrão 240s; cada lote tem no máximo 16.384
  bytes UTF-8 depois da sanitização; excesso falha antes de chamar o provedor.
- Saída só é liberada com `modelUsage` contendo `claude-opus-5` e resultado não vazio. O diagnóstico
  registra todos os modelos auxiliares observados para auditoria.
- Testes stdlib: 14 casos verdes, incluindo argv, timeout, alias errado, JSON inválido, API error,
  saída vazia, input grande, override inválido e auditoria de modelos.
- Opus revisou código e integração em dois lotes reais; um lote anterior expirou e foi contado como
  parcial, não como parecer. Kimi revisou o mesmo runner.
- Achados de "flags inexistentes" foram refutados por `claude --help` e chamadas reais. A tese de
  descendente sobrevivente foi refutada por teste com marcador repetido 5×. Foram aceitos os
  achados confirmados: stdin em vez de argv, anúncio imediato, erro limitado, lint fail-closed e
  cobertura explícita de saída vazia/modelos usados.

## Smoke externo instalado — PASS

- Projeto descartável: `/private/tmp/orq-opus-smoke-20260809-01`, nova sessão Codex.
- Plugin carregado do cache `~/.codex/plugins/cache/orquestra/orq/0.21.0`.
- Gate LGPD: clear; alvo artificial sem PII/credencial/dado clínico.
- Opus: exit 0, `OPUS_STARTED`, `OPUS_MODEL=claude-opus-5`, 956 bytes de briefing, parecer real com
  contradição `contrato.md:3↔4` e veredito reprovado.
- Kimi K3: exit 0, 2.167 bytes, confirmou a mesma contradição.
- Painel: completo; os quatro arquivos do escopo permaneceram idênticos. O hook de sessão criou
  `.serena/` como untracked fora do escopo; o projeto temporário inteiro foi descartado depois.
- GitHub verificado depois do smoke: `origin/main=164387c`, versão `0.20.0`, zero referência ao
  runner e zero bloco do painel Opus no Host Codex. A distribuição pública ainda não está corrigida.

## Painel e reconciliação de T-041

- Rodada 1: Opus 5 e Kimi K3 reprovaram a contradição da diagonal no Host Codex. O Opus também
  confirmou override nativo não comprovado, raiz host-específica e lint permissivo.
- Correções: painel Codex fixado em exatamente Opus 5 + Kimi K3; `codex exec` virou padrão; a skill
  resolve `ORQ_PACKAGE_ROOT`; o lint passou a exigir contratos no arquivo normativo.
- Rodada 2: os dois revisores deram `APROVADO_COM_RESSALVAS` e confirmaram os quatro bloqueadores
  fechados. O Manager verificou e corrigiu as ressalvas presentes: defaults sem elenco agora incluem
  Kimi, degradação/diagonal entram no lint, alias Opus é verificado em todo host e raiz Kimi valida o
  layout antes de usar.
- Tentativas que expiraram não foram contadas como parecer. Os dois pareceres válidos da rodada 2
  retornaram exit 0 sobre trechos verbatim numerados e foram reconciliados antes dos gates finais.
