# Paridade operacional do Orquestra no Codex

**Data:** 2026-08-09  
**Card coordenador:** `T-040`  
**Estado:** desenho aprovado pelo dono; aguardando revisão desta especificação antes do plano executável

## Problema

O Codex instala e habilita `orq@orquestra`, mas não expõe `orq/commands/*.md` como comandos `/orq:*`. Esses comandos pertencem à superfície do Claude Code. No Codex, o workflow chega como skill e é ativado por linguagem natural ou por `/skills`.

Essa diferença é tecnicamente válida, porém hoje o produto não a torna inequívoca. O usuário vê o plugin instalado, procura `/orq`, não encontra e interpreta o estado como instalação defeituosa. O mesmo teste em projeto externo revelou outros pontos que precisam virar contrato do plugin, não ajustes locais: elenco incompleto em projeto novo, resolução inconsistente do time por host, diagnóstico impreciso de memória preexistente e expectativa de paridade de statusline que o Codex ainda não oferece.

## Objetivo

Fazer o mesmo Orquestra operar de forma previsível no Claude Code e no Codex, preservando um único núcleo de processo e adaptando apenas as capacidades de cada host.

O resultado deve permitir que uma pessoa instale o plugin, abra um repositório novo ou preexistente e entenda, sem conhecer detalhes internos:

1. como ativar o Orquestra naquele host;
2. se o plugin está apenas instalado ou realmente carregado e funcional;
3. qual modelo executará cada papel;
4. quais degradações existem naquele ambiente;
5. o que será ou não alterado em memória, configuração e statusline.

## Decisões aprovadas

### Interface

- Claude Code: linguagem natural e `/orq:*`.
- Codex: linguagem natural e `/skills`.
- `/prompts:orq` não integra o contrato principal. Pode ser oferecido como compatibilidade opcional, porque custom prompts são locais, exigem reinício e estão depreciados.
- O instalador nunca escreve em `~/.codex/prompts/` silenciosamente.

### Arquitetura

O produto terá um núcleo compartilhado e adaptadores por host.

- O núcleo continua responsável por intenção, board, máquina de estados, gates, memória e handoffs.
- `commands/` continua sendo o mecanismo explícito do Claude e a descrição canônica das operações.
- A skill `orq` continua roteando linguagem natural. Fora do Claude, resolve a operação correspondente e lê o arquivo canônico pela raiz real do pacote.
- Referências específicas de host ficam isoladas em arquivos próprios, evitando espalhar condicionais de Codex e Kimi pela disciplina central.
- Nenhum workflow será duplicado integralmente por host.

## Contrato de ativação por host

### Claude Code

1. Plugin instalado e habilitado.
2. Comandos `/orq:*` disponíveis após update/restart aplicável.
3. Skill reconhece linguagem natural.
4. Smoke usa uma frase natural e um comando explícito.

### Codex

1. `codex plugin list` confirma `installed, enabled` e a versão esperada.
2. `/plugins` mostra o plugin e `/skills` mostra a skill `orq`.
3. Uma conversa nova reconhece uma frase natural como “onde paramos?” ou “quero melhorar X”.
4. A skill abre a operação canônica na raiz do pacote e respeita as capacidades reais do host.
5. A ausência de `/orq:*` é apresentada como diferença de interface, não falha de instalação.

Os estados “instalado”, “habilitado”, “skill carregada” e “smoke comportamental aprovado” são independentes. O diagnóstico deve mostrar os quatro separadamente.

## Elenco padrão do host Codex

| Papel | Configuração desejada | Restrições |
|---|---|---|
| Manager | `gpt-5.6-sol@high` | é a sessão principal; verificar o modelo real, nunca alegar que foi alterado em uma sessão já aberta |
| Planner | `gpt-5.6-sol@ultra` | somente leitura; produz plano e para no gate |
| Implementer | `gpt-5.6-terra@xhigh` | único writer; roda em worktree dedicado com `workspace-write` |
| Reviewer 1 | Opus 5 | somente parecer; sem ferramentas de escrita |
| Reviewer 2 | Kimi K3 (`kimi-code/k3`) | somente parecer; sem `--yolo` e sem `--auto` |

### Aplicação real do elenco

- O arquivo `_elenco.md` gerado pelo `init` deve conter `Matriz de invocação` e `Times por host`; não pode apontar para seções ausentes.
- Todo consumidor de papel resolve primeiro o host atual, depois o papel e só então o mecanismo de invocação.
- Se a primitiva nativa aceitar modelo e effort, ela é preferida.
- Se a primitiva não aceitar override, usa-se o subprocesso rastreável documentado para o mesmo vendor, com modelo, effort e sandbox explícitos.
- Se modelo, assinatura ou CLI não estiver disponível, o papel não é falsificado. O Manager informa a degradação e mantém o card no estado seguro correspondente.
- Modelos privados ou não liberados para outro usuário não são substituídos silenciosamente. O template registra o padrão desejado e o diagnóstico exige uma escolha explícita de fallback.

## Inicialização e migração

O `init` distingue quatro estados:

1. projeto virgem, sem memória;
2. memória preexistente em formato legado;
3. Orquestra parcialmente inicializado;
4. Orquestra completo.

Regras:

- criação e migração são aditivas e idempotentes;
- arquivos preexistentes nunca são sobrescritos;
- memória legada permanece onde está e recebe um ponteiro em `memory/MEMORY.md` quando necessário;
- `AGENTS.md` e `CLAUDE.md` preservam conteúdo existente e recebem somente o bloco delimitado do Orquestra;
- `_elenco.md` existente recebe apenas seções obrigatórias ausentes, preservando escolhas do projeto;
- qualquer conflito sem merge determinístico interrompe a operação antes da escrita e apresenta o alvo exato.

## Statusline

### Claude Code

Mantém a integração existente com `kanban-status.sh` e a composição não destrutiva já tratada por `T-036`/`T-038`.

### Codex

O Codex oferece uma statusline nativa com lista fechada de campos. O perfil recomendado do Orquestra pode incluir:

- `model-with-reasoning`;
- `run-state` ou o identificador equivalente aceito pela versão instalada;
- `task-progress`;
- `context-used`;
- `five-hour-limit` e `weekly-limit`;
- `current-dir` e `git-branch`;
- `permissions` e `approval-mode`;
- `fast-mode` quando disponível.

O procedimento deve consultar os identificadores aceitos pela versão instalada antes de gravar. A configuração é opt-in, preserva a ordem e os campos já escolhidos pelo usuário e cria backup antes de qualquer alteração.

O plugin não promete renderizar o `KANBAN.md` na statusline do Codex. Isso exige execução de script arbitrário, capacidade ainda não exposta pelo TUI. `task-progress` representa o plano da sessão Codex, não o board do Orquestra, e a documentação deve dizer isso explicitamente.

## Diagnóstico e mensagens de erro

O diagnóstico reporta camadas independentes:

1. marketplace/fonte encontrada;
2. plugin instalado e habilitado;
3. versão e conteúdo do cache coerentes;
4. skill visível no host;
5. estrutura Orquestra do projeto válida;
6. elenco resolvido e executores disponíveis;
7. smoke comportamental aprovado.

Mensagens obrigatórias:

- “Plugin instalado, mas skill ainda não carregada nesta sessão” quando aplicável.
- “No Codex, use linguagem natural ou `/skills`; `/orq:*` pertence ao Claude Code.”
- “Painel parcial” com o revisor ausente e o motivo real.
- “Modelo configurado” e “modelo rodando agora” em blocos separados.
- “Memória preexistente detectada em outro formato” em vez de “projeto sem memória”.

Falhas de autenticação, PATH, modelo indisponível, timeout e saída vazia têm causas distintas e não podem ser condensadas em “não instalado”.

## Privacidade e segurança

- Dados de paciente, PII, prontuários, credenciais e dumps de produção nunca são enviados ao Codex, Kimi ou outro modelo externo.
- Reviewers recebem somente código, schema, arquitetura e evidências sanitizadas.
- Reviewer é read-only e não aplica correções.
- Implementer é o único writer e trabalha em worktree dedicado.
- Nenhum fluxo usa bypass de permissões.
- Configurações globais de usuário só mudam com autorização explícita e backup verificável.

## Compatibilidade opcional `/prompts:orq`

Quando o usuário pedir explicitamente um slash command no Codex, o Orquestra pode mostrar como criar um custom prompt local que encaminha a solicitação para a skill.

Esse caminho:

- não é instalado automaticamente;
- não é requisito do smoke padrão;
- deve ser rotulado como depreciado;
- exige reiniciar o Codex ou abrir nova conversa;
- não cria uma família paralela `/orq:*`.

## Verificação

### Verificação estática

- `claude plugin validate ./orq --strict`.
- `python3 orq/scripts/lint-coerencia.py .`.
- O lint deve falhar se um consumidor citar `Matriz de invocação` ou `Times por host` sem que o template de `_elenco.md` gere essas seções.
- O lint deve detectar promessas de `/orq:*` como interface do Codex.
- O lint deve conferir os identificadores, caminhos e referências entre skill, comandos e adaptadores.

### Cenários determinísticos

1. projeto vazio;
2. projeto com `MEMORY.md` na raiz e snapshots em `memory/`;
3. projeto com Orquestra parcial;
4. statusline Codex inexistente;
5. statusline Codex já personalizada;
6. Claude CLI ausente;
7. Kimi CLI ausente;
8. modelo/effort sem entitlement;
9. segunda execução do `init` sem mudança adicional.

### Smoke comportamental após release

O smoke só vale depois de bump, validação, atualização do marketplace/cache e nova sessão.

No Codex, deve provar:

1. `/plugins` e `/skills` encontram o Orquestra;
2. “onde paramos?” lê memória e board na ordem correta;
3. “quero melhorar X” cria/planeja card e para no gate;
4. Planner e Implementer usam os modelos/efforts resolvidos ou declaram degradação;
5. “revisa isso” retorna pareceres independentes de Opus 5 e Kimi K3, ou painel parcial nomeado;
6. o repositório não recebe escrita fora do writer autorizado;
7. a ausência de `/orq` não é reportada como falha.

## Decomposição do trabalho

`T-040` coordena o resultado, mas não reimplementa cards existentes.

1. `T-033`: completar o template do elenco e a migração aditiva.
2. `T-034`: fazer Planner, Implementer e painel resolverem o time por host.
3. Frente Codex: corrigir onboarding, descoberta, diagnóstico e compatibilidade opcional.
4. Frente statusline Codex: oferecer perfil nativo opt-in sem prometer board.
5. `T-039`: alinhar a comunicação sobre memória legada.
6. `T-026`: executar o smoke final e fechar a validação cross-host.

O plano executável definirá a ordem dos commits e criará cards adicionais apenas para as duas frentes que ainda não possuem ID próprio.

## Fora de escopo

- alterar o TUI do Codex ou implementar a issue de statusline arbitrária no upstream;
- criar um fork do Orquestra específico para Codex;
- reproduzir todos os comandos `/orq:*` como custom prompts;
- instalar ou autenticar Claude/Kimi sem autorização;
- escolher silenciosamente modelos alternativos;
- publicar ou fazer push sem autorização do dono.

## Critérios de aceite

O trabalho só pode ir para `VALIDATE` quando:

1. projeto novo recebe um elenco completo e host-aware;
2. projeto legado é preservado e reconhecido corretamente;
3. Codex apresenta linguagem natural + `/skills` como interface oficial;
4. o diagnóstico separa instalação, carregamento e smoke;
5. statusline Codex é opcional, não destrutiva e não promete o board;
6. Planner, Implementer, Opus e Kimi são realmente invocados conforme o elenco ou a degradação é explícita;
7. validações estáticas passam;
8. smoke em sessão Codex nova passa;
9. painel final de Opus 5 e Kimi K3 não encontra bloqueador aberto;
10. o dono valida o comportamento no produto.

O número da release não faz parte do contrato funcional. Será o próximo minor livre quando a implementação entrar na fila, sempre com bump sincronizado nos quatro locais exigidos pelo repositório.
