#!/bin/sh
input=$(cat)

# Sem jq: a barra encolhe para o board — nunca quebra por falta da dependência.
# O init instala o par completo sempre (Decisão 12 do T-036; o ramo "só kanban
# sem jq" foi eliminado — virava beco sem saída no --reinstalar). Este script
# é quem degrada sozinho quando falta jq, e se completa sozinho, sem re-run,
# quando jq aparecer depois. Extrai project_dir do stdin sem jq (grep/sed
# simples, em vez de $PWD — cwd do processo da statusline não é confiável);
# guarda a existência da irmã antes de invocar. Sem jq e sem a irmã ao lado:
# degradação best-effort, barra sai vazia (exit 0) — nunca "No such file or
# directory".
if ! command -v jq >/dev/null 2>&1; then
  project_dir=$(printf '%s' "$input" | grep -o '"project_dir"[[:space:]]*:[[:space:]]*"[^"]*"' | head -n 1 | sed -E 's/.*:[[:space:]]*"([^"]*)".*/\1/')
  [ -z "$project_dir" ] && project_dir="$PWD"
  kanban_script="$(dirname "$0")/kanban-status.sh"
  # -r, não -x: a irmã é sempre invocada via `sh`, o bit de execução é
  # irrelevante (T-036, achado 1 do painel). Exigir -x deixava a barra vazia
  # sempre que a cópia perdia o +x (ex.: `cp` sem preservar modo).
  [ -r "$kanban_script" ] && exec sh "$kanban_script" "$project_dir"
  exit 0
fi

model=$(echo "$input" | jq -r '.model.display_name // "Unknown Model"')
effort=$(echo "$input" | jq -r '.effort.level // empty')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
worktree=$(echo "$input" | jq -r '.workspace.git_worktree // .worktree.name // empty')
total_cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
current_dir=$(echo "$input" | jq -r '.workspace.project_dir // .workspace.current_dir // empty')
[ -z "$current_dir" ] && current_dir="$PWD"
rl_5h_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty' | awk '{printf "%.0f", $1}')
rl_5h_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')

if [ -n "$used" ]; then
  used_display=$(printf "%.0f" "$used")
  usage_str="${used_display}%"
else
  usage_str="0%"
fi

if [ -n "$worktree" ]; then
  worktree_str="${worktree}"
else
  worktree_str="no worktree"
fi

GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

git_str=""
# -C "$current_dir": o cwd do processo da statusline nem sempre é o projeto
# (ex.: project_dir vindo do stdin, cwd real em outro lugar) — sem -C, branch
# sai de um repo diferente do nome/board mostrados ao lado.
if git -C "$current_dir" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$current_dir" branch --show-current 2>/dev/null)
  [ -z "$branch" ] && branch=$(git -C "$current_dir" rev-parse --abbrev-ref HEAD 2>/dev/null)
  staged=$(git -C "$current_dir" diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
  modified=$(git -C "$current_dir" diff --numstat 2>/dev/null | wc -l | tr -d ' ')

  git_str="$branch"
  [ "$staged" -gt 0 ] && git_str="${git_str} $(printf "${GREEN}+${staged}${RESET}")"
  [ "$modified" -gt 0 ] && git_str="${git_str} $(printf "${YELLOW}~${modified}${RESET}")"
else
  git_str="no branch"
fi


if [ -n "$total_cost" ]; then
  # -v em vez de interpolar no CÓDIGO do awk (T-036, achado 8 do painel): a
  # forma antiga executava o que viesse em total_cost_usd a cada render.
  cost_display=$(awk -v c="$total_cost" 'BEGIN { printf "%.2f", c+0 }')
  block_str="\$${cost_display}"
else
  block_str="\$0.00"
fi

make_bar() {
  pct="$1"
  width=10
  filled=$(( pct * width / 100 ))
  empty=$(( width - filled ))
  bar=""
  i=0
  while [ $i -lt $filled ]; do bar="${bar}█"; i=$(( i + 1 )); done
  while [ $i -lt $width ];  do bar="${bar}░"; i=$(( i + 1 )); done
  printf "%s" "$bar"
}

format_rl() {
  pct="$1"
  reset_ts="$2"
  label="$3"
  [ -z "$pct" ] && return
  if [ "$pct" -ge 90 ]; then color="$RED"
  elif [ "$pct" -ge 70 ]; then color="$YELLOW"
  else color="$GREEN"
  fi
  # Assume epoch (segundos) em resets_at, BSD (date -r) ou GNU (date -d) — se
  # a doc mudar para ISO-8601 os dois falham e reset_time sai vazio. Herdado
  # da barra original; risco registrado, não corrigido aqui (N4 do T-036).
  reset_time=$(date -r "$reset_ts" "+%-I:%M%p" 2>/dev/null || date -d "@$reset_ts" "+%-I:%M%p" 2>/dev/null)
  bar=$(make_bar "$pct")
  printf "${color}${label} ${bar} ${pct}%% resets ${reset_time}${RESET}"
}

rate_limit_str=""
rate_limit_str="${rate_limit_str}$(format_rl "$rl_5h_pct" "$rl_5h_reset" "5h")"

repo_root=$(cd "$current_dir" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null || echo "$current_dir")
dir_display=$(basename "$repo_root")

# Kanban do projeto (memory/wiki/KANBAN.md) — vazio se o projeto não tiver quadro.
# Achado por vizinhança, não por caminho fixo: a irmã mora ao lado deste
# script, onde quer que o par tenha sido copiado (.claude/ do projeto ou
# ~/.claude/orq/) — é o que satisfaz R3 sem hardcode.
kanban_str=""
# -r, não -x: mesma razão do ramo sem jq acima (invocação é sempre via `sh`).
if [ -r "$(dirname "$0")/kanban-status.sh" ]; then
  kanban_str=$(sh "$(dirname "$0")/kanban-status.sh" "$current_dir" 2>/dev/null)
fi
[ -n "$kanban_str" ] && kanban_str=" | ${kanban_str}"

# Sem bloco de rate-limit no stdin, rate_limit_str fica vazio: omite o
# segmento inteiro (rótulo + separador) em vez de deixar "⏱️ " pendurado.
rl_segment=""
[ -n "$rate_limit_str" ] && rl_segment=" | ⏱️ ${rate_limit_str}"

if [ -n "$effort" ]; then
  printf "🤖 %s | 💪 %s | 🧠 %s | 💰 %s%s\n📁 %s | 🌳 %s | 🌿 %s%s" "$model" "$effort" "$usage_str" "$block_str" "$rl_segment" "$dir_display" "$worktree_str" "$git_str" "$kanban_str"
else
  printf "🤖 %s | 🧠 %s | 💰 %s%s\n📁 %s | 🌳 %s | 🌿 %s%s" "$model" "$usage_str" "$block_str" "$rl_segment" "$dir_display" "$worktree_str" "$git_str" "$kanban_str"
fi
