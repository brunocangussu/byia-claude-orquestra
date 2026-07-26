---
description: Busca na memória de longo prazo (Supermemory) — contorna o bug do MCP oficial cuja busca devolve 0 resultados
argument-hint: "<o que você quer lembrar>"
---

Busque na memória de longo prazo do usuário usando o script que contorna o bug do MCP:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sm-search.py" "$ARGUMENTS" --limit 8
```

**Por que não usar a MCP `api-supermemory-ai__search`:** ela escopa por header `x-sm-project`,
mas o endpoint `/v3/search` do Supermemory **ignora esse header** e devolve sempre 0 resultados
(ou "Internal server error" via MCP). A busca só funciona passando `containerTags` no corpo —
é o que o script faz. Diagnosticado em 25/Jul/2026. **Escrever** (`addMemory`) continua OK pela MCP.

Depois de rodar:
1. **Sintetize** os achados em vez de colar a saída crua — o usuário quer a resposta, não o dump.
2. Cite **quando** cada memória foi gravada (a data vem no resultado) — contexto antigo pode estar
   superado por trabalho posterior.
3. Se os resultados forem fracos, **tente outros termos** (mais gerais, ou sinônimos do domínio)
   antes de dizer que não achou.
4. Cruze com a wiki local (`memory/`) quando fizer sentido — ela costuma ter a versão mais atual.

Se o script falhar (token ausente, rede), diga o erro e sugira conferir
`~/.claude.json` -> `mcpServers.api-supermemory-ai`.
