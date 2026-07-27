#!/bin/sh
# Lê memory/wiki/KANBAN.md do repo e emite um resumo compacto pra statusline.
# Uso: kanban-status.sh <dir>
# Saída: "📋 47% (7/15) · fazendo: Título curto"  (vazio se não houver quadro)

dir="$1"
[ -z "$dir" ] && dir="$PWD"

# acha a raiz do repo (ou usa o dir)
root=$(cd "$dir" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null) || root="$dir"
board="$root/memory/wiki/KANBAN.md"
[ -f "$board" ] || exit 0

awk '
  # para de contar ao chegar no arquivado — casa Arquivado/Arquivadas/Arquivo/arquiv…
  /^##+ .*[Aa]rquiv/ { archived=1 }
  archived { next }

  # CARD VÁLIDO, estrito: "- [m] `T-001` Título — nota"
  # marcador tem que ser um dos 6; o ID tem que vir entre crases logo depois.
  # Estrito de propósito: um item de checklist solto ("- [x] revisor aprovou")
  # NÃO é card e não pode entrar na contagem.
  /^- \[[ >!~?x]\] `[^`]+`/ {
    st = substr($0, 4, 1)
    total++
    if (st == "x") done++
    else if (st == "~") {
      doing++
      # extrai o título entre o ` do ID e o travessão
      line = $0
      sub(/^- \[.\] *`[^`]*` */, "", line)
      sub(/ *—.*$/, "", line)
      if (doing_title == "") doing_title = line
    }
    else if (st == "?") validar++
    next
  }

  # PARECE card mas não casa o contrato (marcador inválido, ID sem crases,
  # indentado, negrito em volta do marcador...). Conta como suspeita para a
  # falha aparecer em vez de sumir em silêncio.
  /^[[:space:]]*[-*] *\[/ { suspeitas++ }

  END {
    if (total == 0 && suspeitas == 0) exit 0
    if (total == 0) { printf "⚠ %d linha(s) parecem card fora do formato\n", suspeitas; exit 0 }
    pct = int(done * 100 / total)
    out = sprintf("📋 %d%% (%d/%d)", pct, done, total)
    if (validar > 0) out = out sprintf(" ⏳%d", validar)
    if (doing_title != "") {
      t = doing_title
      if (length(t) > 34) t = substr(t, 1, 33) "…"
      out = out " · " t
    }
    if (suspeitas > 0) out = out sprintf(" ⚠%d", suspeitas)
    print out
  }
' "$board"
