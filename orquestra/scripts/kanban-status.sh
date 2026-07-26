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
  # para de contar ao chegar no arquivado
  /^## .*Arquivad/ { archived=1 }
  archived { next }
  # só linhas de tarefa: "- [x] `T-001` Título — nota"
  /^- \[.\]/ {
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
  }
  END {
    if (total == 0) exit 0
    pct = int(done * 100 / total)
    out = sprintf("📋 %d%% (%d/%d)", pct, done, total)
    if (validar > 0) out = out sprintf(" ⏳%d", validar)
    if (doing_title != "") {
      t = doing_title
      if (length(t) > 34) t = substr(t, 1, 33) "…"
      out = out " · " t
    }
    print out
  }
' "$board"
