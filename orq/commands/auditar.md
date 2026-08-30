---
description: Audita remoção de legado ou prova adoção graph-first com evidência offline e reproduzível
---

Use quando o dono disser “audite a remoção de X”, “prove que X saiu”, “verifique se começamos pelo
grafo” ou fornecer um trace para conferir a ordem de descoberta. Este comando é explícito: não cria
hook, não captura sessão viva e não bloqueia trabalho.

## Pré-condição comum

Resolva `ORQ_PACKAGE_ROOT` conforme a skill `orq` e comprove que estes arquivos existem:

- `ORQ_PACKAGE_ROOT/scripts/audit-removal.py`
- `ORQ_PACKAGE_ROOT/scripts/audit-adoption.py`
- `ORQ_PACKAGE_ROOT/schemas/audit-ledger-v1.json`

Fora do Claude Code, `/orq:auditar` não é slash command: reconheça a intenção em linguagem natural
e siga este mesmo procedimento usando a raiz comprovada do pacote.

## Modo remoção

1. Fixe o alvo literal e a raiz do repositório. Não transforme o alvo em código shell.
2. Faça primeiro a descoberta vigente do projeto com codebase-memory/Serena, quando disponível.
   Registre cada consulta real como `--graph-receipt 'FERRAMENTA=CONSULTA'`; nunca invente recibo.
3. Declare com o dono ou com o plano aprovado:
   - históricos que podem reter a expressão (`--retain CAMINHO`, repetível);
   - arquivos críticos que devem continuar existindo (`--critical CAMINHO`, repetível);
   - validações obrigatórias (`--require NOME`, repetível).
4. Escolha um nome sanitizado para `memory/audits/removal-<slug>.json` e rode, passando argumentos
   como argv, sem `eval` e sem `shell=True`. O ledger deve permanecer dentro da raiz auditada e não
   pode apontar para diretório, FIFO, dispositivo ou symlink:

```text
python3 ORQ_PACKAGE_ROOT/scripts/audit-removal.py scan \
  --root RAIZ --target ALVO --ledger LEDGER \
  --retain HISTORICO --critical ARQUIVO --require TESTE \
  --graph-receipt FERRAMENTA=CONSULTA
```

O exit `1` do scan é o resultado normal quando ainda há evidência a remover ou recibos a comprovar;
não o descreva como crash. Leia o JSON curto da saída e use o ledger como fonte detalhada.

Depois da implementação e das validações reais, verifique:

```text
python3 ORQ_PACKAGE_ROOT/scripts/audit-removal.py verify \
  --ledger LEDGER --root RAIZ --target ALVO \
  --retain HISTORICO --critical ARQUIVO --require TESTE \
  --receipt TESTE=pass
```

Repita no `verify` o mesmo escopo usado no `scan`. O CLI compara raiz, alvo, exclusões, históricos,
âncoras e validações com o ledger antes de escanear; o JSON não é autoridade sobre o próprio escopo.
Só registre `pass` para comando realmente executado. `active`, `ambiguous`, âncora ausente, recibo
ausente ou recibo `fail` mantêm a auditoria vermelha. `retained-historical` não bloqueia.
Cada validação aceita um único recibo por nome; duplicata é entrada inválida, mesmo quando repete o
mesmo resultado.

## Modo adoção

Exija um arquivo JSON explícito com `"schemaVersion": "orq.audit-trace.v1"` e `events[]`; não
misture eventos com `sequence` e sem `sequence`, não reconstrua telemetria de memória nem afirme que
uma sessão foi observada quando o trace não existe.

Cada evento deve fornecer `tool`, `name` e/ou `command` no topo, em `item` ou em `data.item`.
Qualquer outra forma é inválida, em vez de ser ignorada silenciosamente. Preserve o identificador
completo da ferramenta: `codebase-memory-mcp.search_graph`,
`mcp__codebase_memory_mcp__search_graph` e `serena.find_symbol` têm procedência; `search_graph` nu é
`unverified` e não certifica adoção. Comandos shell entram como texto ou argv e são classificados de
forma conservadora; comando ou ferramenta desconhecida também é `unverified`, nunca ignorada. O
auditor nunca executa o conteúdo. `counts` registra categorias observadas, portanto um evento misto
pode contar em mais de uma categoria.

Campos canônicos aceitam string ou lista de strings. Tipo inválido e lista vazia de ferramenta
invalidam o trace; lista vazia de comando e shell não tokenizável são `unverified`, nunca prova de
grafo.

O trace é uma evidência normalizada de fonte confiável. Por isso, o executável nominal explícito
`codebase-memory-mcp` ou `serena` no campo `command` preserva procedência; isso não verifica o
binário do `PATH` e não torna um trace fabricado em prova de execução.

```text
python3 ORQ_PACKAGE_ROOT/scripts/audit-adoption.py TRACE.json
```

Interprete o resultado literalmente:

- `pass` / exit `0`: primeiro acesso relevante foi grafo/índice;
- `fail` / exit `1`: busca, leitura, mutação ou descoberta sem procedência veio antes do grafo;
- `not-observed` / exit `1`: não houve evento de grafo, portanto não há prova;
- `invalid-trace` / exit `2`: JSON ou schema de entrada inválido.

## Limites

- Os auditores não substituem revisão humana, codebase-memory, Serena nem testes do projeto.
- Dependências e artefatos gerados são fora do escopo por padrão; se o runtime carregar código dali,
  remova a exclusão conscientemente no `scan` e repita-a no `verify`.
- Nenhum conteúdo é enviado à rede ou a LLM externa.
- O ledger é o único write permitido e só existe no modo remoção solicitado.
- Nunca integrar este fluxo a `hooks.json` ou `context-guard.py` sem card e gate próprios.
