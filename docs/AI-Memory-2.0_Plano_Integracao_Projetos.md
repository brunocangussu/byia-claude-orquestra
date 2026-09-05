# AI-Memory 2.0 --- Plano de Avaliação e Integração

**Data:** 04/09/2026\
**Uso:** contexto para Codex, Claude Code, OpenCode e equipe técnica.

## 1. Decisão executiva

O AI-Memory 2.0 merece um **piloto real**. Seu melhor papel inicial não
é substituir Obsidian, Git, AGENTS.md, ClickUp, Supabase ou bancos
operacionais, mas atuar como **memória operacional compartilhada dos
agentes de desenvolvimento**.

A tese é: **LLMs e harnesses são substituíveis; a memória do projeto
deve ser independente deles.**

``` text
Codex ─┐
Claude ├──> AI-Memory ───> memória persistente do projeto
OpenCode ┘
```

## 2. Problema

Hoje, conhecimento adquirido em uma sessão pode ficar preso ao Codex,
Claude Code, Cursor ou outro agente. Isso causa fragmentação, repetição
de investigação, perda após compactações, dependência do fornecedor e
dificuldade para trocar de máquina/agente.

O AI-Memory captura trabalho, consolida conhecimento e o disponibiliza
para sessões futuras.

## 3. Modelo mental

Não tratar como simples vector database.

``` text
sessões → captura → consolidação → wiki Markdown/OKF
                                      ↓
                              full-text + embeddings
                                      ↓
                                   retrieval
                                      ↓
                                novos agentes
```

## 4. OKF v0.2

O 2.0 usa nativamente **Open Knowledge Format v0.2**, especificação
aberta publicada pelo Google Cloud. OKF é essencialmente Markdown + YAML
frontmatter.

Isso permite abrir a memória no Obsidian, versionar no Git, usar
grep/scripts, entregar a outro agente ou migrar para outro consumidor
OKF.

``` yaml
---
type: decision
title: Estratégia de autenticação
tags: [backend, auth]
---
Decisão e contexto...
```

Esse é um dos maiores diferenciais: o conhecimento pode sobreviver ao
próprio AI-Memory.

## 5. Fonte de verdade

A wiki Markdown/OKF é a camada durável; índices e banco podem ser
reconstruídos.

``` text
Markdown/OKF = conhecimento
índices/SQLite = aceleração
```

Isso reduz lock-in.

## 6. Retrieval

O 2.0 combina full-text com embeddings locais. Full-text é excelente
para símbolos, erros, endpoints e arquivos; embeddings ajudam em
perguntas conceituais sem correspondência textual exata.

O modelo local informado é `all-MiniLM-L6-v2`, com download aproximado
de 87 MB, sem API externa ou GPU obrigatória.

## 7. Benchmark e evals

A release 2.0.0 informa LongMemEval-S `hit@5` de **0,617 → 0,823**. Mais
importante que o número: existe um harness reproduzível.

Precisamos criar eval próprio com perguntas reais: - qual foi a causa do
bug X? - qual workaround usamos? - por que abandonamos Y? - o que já
tentamos e falhou? - qual decisão está vigente? - qual era o estado em
determinada data?

Medir Recall@5, precisão, contexto irrelevante, obsolescência,
contradições e impacto na resposta final.

## 8. Captura automática

O valor aumenta porque o sistema tenta evitar a cerimônia "lembre
disso".

``` text
trabalho → captura → memória
```

é melhor que:

``` text
trabalho → lembrar de documentar → talvez memória
```

## 9. Multiagente

O 2.0 foi desenhado para Codex, Claude Code, OpenCode e outros
trabalharem simultaneamente no mesmo projeto. Há isolamento por ator e
serialização de escritas para reduzir corrupção e sobrescrita.

## 10. Handoff

O handoff permite:

``` text
Claude Code → handoff → Codex → continuação
```

com noção de posse/reivindicação. Isso é muito útil numa estratégia em
que modelos diferentes exercem papéis diferentes.

## 11. Multi-modelo e multi-machine

A camada durável passa a ser **repositório + memória**, e não a IDE.

``` text
Codex → implementação
Claude → arquitetura/refactor
OpenCode → alternativa
outro → revisão
```

MacBook, desktop, VM e servidor também podem consumir o mesmo store
central.

## 12. Times

O servidor pode ser compartilhado por equipe, com atribuição e
auditoria.

``` text
             AI-Memory
        ┌──────┼──────┐
      Bruno   Dev A   Dev B
```

Não presumir ACL sofisticada por página. Informação sensível continua
exigindo governança própria.

## 13. Temporalidade

O histórico permite consultar não apenas o conhecimento atual. O 2.0
adiciona `as_of`, permitindo perguntas como:

> O que sabíamos sobre autenticação em 15 de agosto?

Útil para regressões, auditoria e evolução arquitetural.

## 14. Relações tipadas

Suporta relações `causes`, `fixes` e `contradicts`.

``` text
BUG-42 → caused_by → DECISION-17 → fixed_by → PATCH-51
```

É um knowledge graph leve sobre Markdown. Contradições declaradas podem
ser detectadas sem LLM.

## 15. Experience pass

Há uma etapa opcional que revisa várias sessões para encontrar padrões
que não aparecem claramente numa sessão isolada. É uma forma de
transformar trajetórias repetidas em aprendizado operacional.

## 16. O que NÃO substituir

**Obsidian:** conhecimento humano/second brain.\
**Git:** código e configuração.\
**AGENTS.md/CLAUDE.md:** regras estáveis do projeto.\
**Supabase/Postgres/CRM/ClickUp/n8n:** estado operacional e
transacional.

Regra útil:

``` text
AGENTS.md = constituição
AI-Memory = memória institucional dos agentes
Git = realidade executável
```

## 17. Obsidian

Arquitetura recomendada:

``` text
Knowledge Layer
├── Obsidian: human-curated
└── AI-Memory: agent-generated
```

Como ambos trabalham bem com Markdown, existe potencial futuro de
integração. **Não iniciar com sincronização bidirecional irrestrita.**

## 18. Aplicação aos projetos

### Prioridade 1 --- desenvolvimento

Maior ROI provável. Escolher um repositório ativo e testar Codex +
Claude Code + AI-Memory.

### Prioridade 2 --- Hermes/agente pessoal

Explorar depois, separando rigorosamente project memory, personal
knowledge, tarefas, secrets e dados sensíveis.

### Prioridade 3 --- BYIA

Usar inicialmente como **BYIA engineering memory**, não como memória de
pacientes/clientes em produção.

## 19. Arquitetura-alvo inicial

``` text
                         AI-Memory
                            │
            ┌───────────────┼───────────────┐
          Codex         Claude Code       OpenCode
            └───────────────┼───────────────┘
                            │
                       Repositório Git
                    ┌───────┼────────┐
                  código  AGENTS.md  docs

Obsidian = conhecimento humano
ClickUp/Supabase/n8n = sistemas operacionais
```

## 20. Segurança

Antes de centralizar projetos: 1. autenticação; 2. HTTPS para acesso em
rede; 3. backup e restore testado; 4. segregação por projeto; 5.
proibição de secrets; 6. evitar dados clínicos/pacientes; 7. controle de
usuários; 8. auditoria; 9. política de retenção; 10. atualização
coordenada.

A migração 2.0 é condicionada a backup verificado, mas isso não
substitui nossa política de backup.

## 21. Estratégia de implantação

### Fase 0 --- baseline

Mapear agentes, arquivos de instrução, memória atual e selecionar um
projeto. Criar 20--50 perguntas de eval antes da instalação.

### Fase 1 --- piloto local

``` text
1 projeto + 1 máquina + Codex + Claude + AI-Memory
```

Testar captura, retrieval, handoff, restart e troca de agente.

### Fase 2 --- concorrência

Adicionar OpenCode e tarefas paralelas. Testar conflitos, escrita
simultânea e atualização de conhecimento.

### Fase 3 --- servidor central

Somente após sucesso local: container/servidor, HTTPS, autenticação,
backups e múltiplas máquinas.

### Fase 4 --- time

Adicionar usuários e medir se conhecimento produzido por uma pessoa
realmente ajuda agentes de outra.

### Fase 5 --- Obsidian

Só depois definir integração seletiva e unidirecional quando possível.

## 22. Critérios de sucesso

O piloto precisa provar: - agente B continua trabalho do agente A com
pouca reexplicação; - retrieval histórico é correto; - troca Codex ↔
Claude ↔ OpenCode preserva contexto; - captura exige pouco esforço
manual; - origem do conhecimento é auditável; - memória não vira
depósito de lixo; - latência e manutenção são aceitáveis.

## 23. Teste A/B

Comparar:

``` text
A = agente + repositório
B = agente + repositório + AI-Memory
```

Medir acurácia, tempo, arquivos explorados, tokens, perguntas ao humano,
investigações repetidas e erros induzidos por memória antiga.

## 24. Riscos

-   memória errada persistente;
-   knowledge pollution;
-   fatos antigos tratados como atuais;
-   contradições;
-   conteúdo armazenado atuando como prompt/context injection;
-   dependência operacional do servidor;
-   complexidade prematura.

Mitigação: evals, versionamento, fontes canônicas, revisão, escopo
pequeno e observabilidade.

## 25. Promoção de conhecimento

Usar AI-Memory como incubadora:

``` text
sessão → AI-Memory → conhecimento recorrente → ADR/docs/AGENTS.md
```

Quando algo vira regra estável, promover para documentação oficial.

Hierarquia sugerida:

``` text
1. código/testes/schema
2. ADR/docs/AGENTS.md
3. sistemas operacionais oficiais
4. AI-Memory
5. histórico bruto
```

## 26. Tarefa para o agente que receber este documento

Antes de implementar qualquer coisa:

1.  inspecione o repositório atual;
2.  identifique Codex/Claude/OpenCode e hooks já existentes;
3.  localize AGENTS.md, CLAUDE.md e configuração MCP;
4.  verifique conflitos com sistemas de memória já instalados;
5.  proponha arquitetura mínima do piloto;
6.  não altere produção;
7.  não integre dados clínicos ou secrets;
8.  defina rollback;
9.  crie baseline de eval;
10. apresente plano antes de modificar o ambiente.

Depois, implementar em etapas pequenas e testáveis.

## 27. Perguntas que o piloto deve responder

-   AI-Memory reduz reexplicação?
-   Codex consegue continuar uma sessão do Claude?
-   Claude recupera decisões descobertas pelo Codex?
-   A memória permanece útil após dezenas/centenas de sessões?
-   Qual é a taxa de falso retrieval?
-   Como envelhece o conhecimento?
-   Como lidar com decisões revogadas?
-   Quanto cresce o store?
-   Quanto contexto é injetado?
-   Há ganho real comparado a AGENTS.md + Git?
-   O sistema continua simples de operar?

## 28. Recomendação final

**GO para piloto controlado. NÃO GO ainda para adoção universal.**

A combinação de: - formato aberto OKF; - Markdown/Git; - captura
automática; - embeddings locais; - retrieval híbrido; - multi-harness; -
multi-machine; - multiusuário; - handoff; - temporalidade; - evals
reproduzíveis

faz do AI-Memory 2.0 uma das opções mais alinhadas com uma arquitetura
em que **Codex, Claude, OpenCode e futuros agentes são trabalhadores
intercambiáveis sobre uma camada de conhecimento pertencente ao
usuário**.

O teste decisivo não é "o software funciona?". É:

> **Depois de semanas de trabalho real, um agente novo consegue entrar
> no projeto e agir como se tivesse acompanhado a história anterior, sem
> transformar a memória em ruído ou em nova fonte de erro?**

Se a resposta medida for sim, o AI-Memory pode virar uma peça estrutural
da stack.

------------------------------------------------------------------------

## Fontes primárias

-   Fabio Akita --- AI-Memory 2.0:
    https://akitaonrails.com/2026/09/02/ai-memory-2-0-melhor-sistema-memoria-agentes-e-times/
-   Repositório: https://github.com/akitaonrails/ai-memory
-   Release v2.0.0:
    https://github.com/akitaonrails/ai-memory/releases/tag/v2.0.0
-   Migração 2.0:
    https://github.com/akitaonrails/ai-memory/blob/main/docs/MIGRATION-2.0.md
-   Roadmap 2.0:
    https://github.com/akitaonrails/ai-memory/blob/main/docs/ROADMAP-2.0.md
-   OKF v0.2:
    https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
-   Google Cloud --- introdução ao OKF:
    https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/
