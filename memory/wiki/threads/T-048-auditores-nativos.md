# T-048 — auditores nativos de remoção e adoção

**Estado:** implementação aprovada · **frente:** `@frente-auditoria-nativa` · **host:** comum.

## Origem

O T-045 provou duas coisas diferentes: o Cartographer não melhora a cobertura de descoberta frente
ao stack atual, mas os conceitos de ledger de remoção e prova da ordem graph-first são úteis. O
dono validou o parecer **PORTAR IDEIAS**; este card desenha a versão nativa sem copiar código nem
adicionar a dependência.

## Abordagens consideradas

1. **Instalar ou envolver Cartographer:** rejeitada pela cobertura 11/13, histórico falso-ativo,
   ambiguidade de licença e sobreposição com codebase-memory/Serena.
2. **Dois auditores explícitos e offline — recomendada:** scripts puros, um comando natural comum e
   recibos JSON; nenhuma integração com hooks na fase 1.
3. **Observador automático em PostToolUse:** poderia medir sessões ao vivo, mas amplia a superfície
   do guardião de contexto e arrisca regressão/bloqueio. Diferido para outro card, se ainda fizer
   sentido depois do uso offline.

## Desenho recomendado

Uma entrada natural `/orq:auditar` oferece dois modos independentes. No Codex, a skill reconhece a
mesma intenção e chama o script; no Claude, o slash command é apenas a interface. O núcleo e o schema
são os mesmos nos dois hosts.

### `auditar remocao <alvo>`

- Descobre candidatos por variantes literal, kebab-case, snake_case, UPPER_SNAKE, imports e símbolos.
- O Manager adiciona ao ledger os recibos de codebase-memory/Serena; o script não tenta chamar MCP.
- Cada evidência fica em `active`, `retained-historical`, `removed` ou `ambiguous`, com caminho,
  linha, classe, consulta e timestamp.
- O ledger registra root, commit, dirty state, alvo, exclusões, comandos de validação e resultado.
- O próprio ledger, `.git`, dependências e artefatos gerados são excluídos por padrão.
- A verificação falha se houver `active`/`ambiguous`, se faltar âncora crítica declarada ou se um
  comando obrigatório não tiver recibo; histórico retido não bloqueia.

### `auditar adocao <trace.json>`

- Consome eventos normalizados fornecidos explicitamente; não captura a sessão na fase 1.
- Classifica ferramentas de grafo, busca textual, leitura direta de fonte e mutação.
- Passa quando o primeiro acesso relevante é grafo/índice e nenhuma leitura direta o antecede.
- Saída distingue `not-observed`, `pass`, `fail` e `invalid-trace`; nunca transforma ausência de
  telemetria em sucesso.
- Exit codes: `0` conforme, `1` política não cumprida, `2` entrada/schema inválido.

## Artefatos propostos

- `orq/scripts/audit-removal.py` e testes com a fixture autoral do T-045.
- `orq/scripts/audit-adoption.py` e traces graph-first/direct-first/sem-grafo/inválido.
- `orq/commands/auditar.md` como interface Claude; roteamento equivalente na skill para Codex.
- Schema versionado `orq/schemas/audit-ledger-v1.json`.
- Ledgers gerados somente quando solicitado, em `memory/audits/`; a thread guarda o resumo e link.

## Regras que evitam regressão entre hosts

- Nenhuma alteração em `context-guard.py` ou `hooks.json` na fase 1.
- Nenhum `decision: block`; auditores são comandos explícitos e read-only, salvo o ledger pedido.
- Claude e Codex usam o mesmo core; adapters de captura ao vivo, se existirem, serão módulos separados.
- Zero rede, zero LLM externo, zero PII/credencial e nenhuma dependência Python adicional.
- Falha de ferramenta gera recibo incompleto e exit não-verde; nunca falso “auditoria passou”.

## Critérios de aceitação

1. Fixture do T-045: 13/13 âncoras, histórico em `retained`, zero autocontaminação do ledger.
2. Mutação controlada: remoção incompleta falha; remoção completa com recibos passa.
3. Traces: graph-first passa; direct-first falha; sem grafo retorna `not-observed`; JSON inválido sai 2.
4. Testes Linux/macOS e paths com espaço/Unicode; nenhum shell injection pelo alvo.
5. Diff de `hooks.json` e `context-guard.py` obrigatoriamente vazio.
6. Documentação deixa explícito que o audit não substitui review humano nem o stack de descoberta.

## Fora da fase 1

- Captura automática de eventos em sessões vivas.
- Bloqueio por hook, enforcement durante prompts ou alteração do guardião de contexto.
- Instalação/integração do Cartographer e teste em repositório de produção.

## ⏭️ RETOMAR AQUI

Desenho aprovado pelo dono em 2026-08-29. Implementar os dois auditores offline com TDD no worktree
isolado baseado em `origin/main`; preservar diff vazio em `hooks.json` e `context-guard.py`. Não
instalar, publicar, commitar ou enviar ao GitHub sem novo gate explícito.
