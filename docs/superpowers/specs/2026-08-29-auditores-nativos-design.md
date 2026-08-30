# Auditores nativos de remoção e adoção — desenho

**Card:** T-048
**Estado:** aprovado pelo dono em 2026-08-29
**Escopo:** fase 1 offline, explícita e comum a Claude Code e Codex

## Objetivo

Portar para o Orquestra as duas ideias úteis observadas no piloto Cartographer sem incorporar o
Cartographer: um ledger verificável de remoção e uma prova determinística de que a descoberta de
código começou pelo grafo. Os auditores complementam revisão humana e codebase-memory/Serena; não
substituem nenhum deles.

## Contratos

### Auditor de remoção

`audit-removal.py scan` recebe raiz, alvo, ledger, âncoras críticas, históricos retidos, exclusões e
validações obrigatórias. A busca é Python puro, sem shell e sem rede. O alvo é expandido para formas
literal, kebab, snake, upper snake, camel e Pascal. Evidências são classificadas como `active`,
`retained-historical`, `removed` ou `ambiguous`.

`audit-removal.py verify` relê o ledger, exige que o operador repita raiz, alvo e listas de escopo,
compara esses valores com o scan, reescaneia a árvore e recebe recibos explícitos no formato
`NOME=pass|fail`. Assim o JSON não redefine silenciosamente o próprio escopo. Ele atualiza o bloco
de verificação do ledger. O resultado só é `pass` quando não
há evidência ativa ou ambígua, todas as âncoras críticas existem e todos os recibos exigidos passam.
Histórico declarado não bloqueia. O ledger, `.git`, dependências, ambientes virtuais e artefatos
gerados são excluídos por padrão para impedir autocontaminação.

O ledger deve ser um arquivo regular dentro da raiz auditada. FIFO, dispositivo, symlink ou arquivo
ilegível nunca são abertos como arquivo comum: entram como evidência `ambiguous`. A busca binária
inclui UTF-16/UTF-32 com ou sem BOM e arquivos grandes por streaming. Recibo repetido é entrada
inválida, e evidências `removed` permanecem no ledger nas verificações seguintes.

Exit codes: `0` conforme; `1` remoção incompleta; `2` argumento, ledger ou schema inválido.

### Auditor de adoção

`audit-adoption.py TRACE.json` exige `schemaVersion: orq.audit-trace.v1` e consome uma lista
normalizada de eventos. Os campos `tool`, `name` e/ou `command` são aceitos somente no topo do
evento, em `item` ou em `data.item`; evento sem campo canônico é `invalid-trace`. Identificador de
grafo precisa preservar a procedência `codebase-memory-mcp` ou `serena`: ação nua como
`search_graph` ou `find_symbol` é `unverified`, nunca prova graph-first.

Valor canônico deve ser string ou lista não vazia de strings; tipo inválido e lista vazia de
ferramenta são `invalid-trace`. Lista vazia de comando representa comando vazio e é `unverified`.
Shell que não pode ser tokenizado também é `unverified`, sem fallback aproximado.

No campo `command`, os executáveis nominais `codebase-memory-mcp` e `serena` contam como procedência
porque o input já é um trace normalizado e confiável, não uma prova criptográfica do binário no
`PATH`. Essa confiança é assimétrica de propósito: `tool: search_graph` perdeu o provider;
`command: codebase-memory-mcp search_graph ...` o preservou. Trace não confiável ou fabricado não é
atestado de execução e fica fora do contrato.

O classificador reconhece grafo/índice, busca textual, leitura direta, mutação, descoberta sem
procedência e evento irrelevante. Comandos shell são apenas analisados, nunca executados; linhas,
pipelines, redirecionamentos e wrappers encadeados são decompostos conservadoramente. Se um único
evento contiver grafo e operação não-grafo, a operação de maior risco prevalece independentemente
da ordem das chaves; comandos aninhados preservam todas as categorias observadas e têm profundidade
máxima defensiva. Comando ou ferramenta fora do léxico vira `unverified`, não `other`; somente
ações de controle explicitamente permitidas, como `update_plan`, são irrelevantes. `counts` mede
categorias observadas e não é partição: um evento misto pode contar em mais de uma categoria. Não há
captura ao vivo na fase 1.

O resultado é `pass` quando o primeiro acesso de descoberta é grafo/índice e nenhuma busca textual
ou leitura direta o antecede; `fail` quando a ordem é violada; `not-observed` quando não existe
evento de grafo; `invalid-trace` para entrada inválida. Exit codes: `0`, `1`, `1`, `2`,
respectivamente.

## Integração multi-host

- Claude Code recebe `/orq:auditar` em `commands/auditar.md`.
- Codex e Kimi reconhecem a intenção pela skill `orq` e executam os mesmos scripts do pacote.
- Nenhum host ganha hook, bloqueio, captura automática ou dependência externa.
- Ledgers só são escritos quando o usuário pede a auditoria de remoção.

## Segurança e compatibilidade

- Nenhum comando vindo do alvo ou do trace é executado.
- Caminhos com espaço e Unicode são tratados pela API de arquivos do Python.
- Arquivos binários, especiais, ilegíveis ou grandes que não possam ser inspecionados com segurança
  são `ambiguous`, nunca verdes.
- O schema JSON é versionado e o formato permanece legível por ferramentas externas.
- O trace precisa ser arquivo regular de até 2 MiB; FIFO/dispositivo e chave JSON duplicada são
  entrada inválida.
- `orq/hooks/hooks.json` e `orq/scripts/context-guard.py` devem permanecer byte-idênticos à base.
- Nenhum dado, código ou trace é enviado a rede ou a outro modelo.

## Critérios de aceite

1. Fixture autoral com treze âncoras: 13/13 detectadas, histórico retido e ledger sem se detectar.
2. Remoção incompleta falha; remoção completa com âncoras e recibos válidos passa.
3. Graph-first com procedência passa; direct-first, ação nua e evento misto falham; sem grafo é
   `not-observed`; JSON ou evento fora da forma canônica sai com código 2.
4. Testes cobrem caminhos com espaço/Unicode e alvo com metacaracteres de shell.
5. Suíte completa, lint de coerência e validação de manifesto passam.
6. Nenhuma instalação, publicação, commit ou push faz parte deste gate.
