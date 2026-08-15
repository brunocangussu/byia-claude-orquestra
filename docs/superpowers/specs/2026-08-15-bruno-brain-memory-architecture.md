# Bruno Brain — arquitetura de memória independente de LLM

**Status:** aprovado pelo dono em 2026-08-15
**Escopo desta especificação:** fonte canônica, separação de dados, integração dos clientes e ordem de migração.
**Primeira implementação:** `T-037`, retirada do SuperMemory da Orquestra.

## Objetivo

Manter memória pessoal e conhecimento durável em Markdown pertencente ao dono, acessível de forma
consistente por Obsidian, Codex, Claude, ChatGPT e Hermes, sem transformar um provedor de LLM ou um
serviço externo de memória em fonte de verdade.

## Decisões aprovadas

1. O Obsidian continua como interface humana; ele não é substituído pelo GitHub.
2. O Dropbox continua como mecanismo de sincronização do vault na primeira fase.
3. Git é histórico e rollback. Um remoto privado só receberá a parcela sanitizada do Bruno Brain.
4. Dados clínicos, PHI, PII, credenciais e prontuários ficam fora da memória compartilhável e fora
   do MCP geral por padrão.
5. O SuperMemory deixa de ser dependência, recomendação ou fallback da Orquestra, do Codex e do
   Claude.
6. Cada projeto preserva seu próprio `memory/MEMORY.md` e `memory/wiki/KANBAN.md` como estado
   operacional. O Bruno Brain armazena apenas fatos duráveis e conhecimento transversal.
7. O Memory Gateway começa somente leitura. Escritas entram como candidatas revisáveis, nunca como
   mutação silenciosa da memória canônica.
8. O Hermes pode propor e organizar candidatas, mas não ganha escrita irrestrita no corpus
   canônico na primeira versão.
9. Uma atualização de plugin só passa a valer em uma conversa depois de instalação, validação e
   reinício/reabertura da respectiva thread. O agente deve avisar explicitamente quando isso for
   necessário.

## Fontes de verdade

| Informação | Fonte canônica | Réplica/índice |
|---|---|---|
| trabalho atual de um projeto | `memory/wiki/KANBAN.md` do projeto | nenhuma obrigatória |
| checkpoint e retomada | `memory/MEMORY.md` e snapshots do projeto | índice local opcional |
| preferências e decisões transversais | Markdown sanitizado do Bruno Brain | Git privado + índice MCP |
| conteúdo clínico identificável | área clínica segregada | nenhum MCP geral |
| implementação do processo | repositório da Orquestra | caches instalados por versão |
| estado de conversa | thread do cliente | checkpoint explícito antes de trocar de cliente |

Nenhum cache, embedding, banco vetorial ou histórico de conversa substitui os arquivos canônicos.
Todos os índices devem poder ser reconstruídos a partir do Markdown.

## Componentes

### Vault Obsidian/Dropbox

O vault atual permanece no Dropbox. A reorganização será feita por migração rastreável, com
inventário, classificação, plano de movimentos, dry-run e validação de links antes de qualquer
movimentação.

O vault terá ao menos duas zonas:

- `Bruno Brain/`: conteúdo sanitizado e compartilhável;
- área clínica/privada: conteúdo não exportável e não indexável pelo MCP geral.

O Git local pode coexistir com o Dropbox como histórico, mas não haverá `pull` automático
concorrendo com o sincronizador do Dropbox. O remoto privado será configurado somente depois da
segregação e de uma auditoria de arquivos rastreados e histórico.

### Memory Gateway MCP

O primeiro contrato será somente leitura:

- `memory_search(query, project?, tags?, limit?)`;
- `memory_get(id)`;
- `project_context(project)`;
- `memory_propose_candidate(content, provenance, scope)` grava apenas numa fila de candidatas e
  sempre exige revisão humana antes de promoção.

O gateway deve aplicar allowlist de diretórios, negar caminhos clínicos/privados, registrar
proveniência e nunca devolver segredos. A instância remota recebe somente a réplica sanitizada.

### Orquestra

A Orquestra continua responsável por plano, card, worktree, revisão, checkpoint e gates. Ela não
duplica a memória dos projetos nem faz gravação automática em fornecedor externo.

O adaptador futuro para Bruno Brain deve degradar de forma declarada: se o MCP não estiver
disponível, a Orquestra consulta somente a wiki local e informa essa limitação.

### Clientes

- Codex Desktop, CLI e extensão compartilham a configuração MCP do mesmo host.
- Claude usa instalação/configuração própria e deve receber a mesma versão da Orquestra.
- ChatGPT web não lê a configuração local do Codex; usa plugin/app com MCP remoto.
- Hermes consome o mesmo contrato MCP ou uma réplica local equivalente, com as mesmas políticas.

## Propagação e reabertura de threads

Editar o repositório da Orquestra não atualiza caches instalados. A sequência obrigatória é:

1. implementar e validar na fonte;
2. revisar;
3. aprovar o release;
4. instalar a mesma versão no Codex e no Claude;
5. comparar a fonte empacotada com os caches;
6. executar smoke em sessão nova;
7. avisar o dono: **“reabra esta thread agora”**.

Cada projeto será migrado individualmente. A conversa só deve presumir a versão nova depois que o
checkpoint local registrar a migração e a sessão tiver sido reaberta.

## Fases independentes

1. `T-037`: remover SuperMemory do produto Orquestra e das páginas vivas.
2. Paridade de release: instalar uma única versão no Codex e no Claude e limpar instruções globais
   antigas.
3. Vault: separar a zona compartilhável da zona privada e normalizar metadados/links.
4. Gateway: implementar MCP somente leitura sobre a zona sanitizada.
5. Hermes: conectar leitura e fila de candidatas.
6. Projetos: migrar, um por vez, os repositórios que possuem KANBAN.
7. ChatGPT: publicar/conectar o MCP remoto conforme o plano disponível e validar permissões.

Cada fase produz um resultado testável e pode ser interrompida sem deixar duas fontes canônicas.

## Critérios globais de aceite

- Nenhuma configuração ativa do Codex ou Claude referencia SuperMemory.
- A mesma versão da Orquestra está instalada e validada nos dois clientes.
- Nenhum dado clínico identificável entra no Git remoto ou no MCP geral.
- O Gateway funciona sem depender do Mac ligado.
- Toda memória compartilhada possui proveniência, escopo e data de atualização.
- Toda escrita automática vira candidata revisável.
- Cada projeto consegue retomar apenas com Orquestra + `MEMORY.md` + KANBAN, mesmo sem o Gateway.
