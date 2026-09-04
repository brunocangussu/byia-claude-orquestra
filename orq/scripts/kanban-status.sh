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

# Cards acima do teto de 240 BYTES (_schema.md, "O teto da linha").
#
# Passo separado, com LC_ALL=C, de propósito: `length()` no awk conta caracteres
# ou bytes conforme o locale, então a mesma linha "cabe" numa máquina e "estoura"
# noutra — o defeito que este teto existe para não ter. LC_ALL=C fixa bytes.
#
# E é passo SEPARADO em vez de LC_ALL=C no awk principal porque lá embaixo
# `length(t)` trunca o título em 34 para a statusline: sob LC_ALL=C isso cortaria
# emoji e acento no meio do caractere. Uma régua por finalidade.
#
# Duas consequências de ser passo separado, ambas deliberadas:
#
#  1. A regra de "arquivado" fica DUPLICADA entre os dois awk. É duas fontes de
#     verdade, e seria bug esperando acontecer — se não estivesse coberta:
#     `test_card_arquivado_nao_conta_para_o_teto` quebra assim que os dois
#     passos discordarem. Mexeu num, rode a suíte.
#  2. Se este awk falhar, a statusline sai sem quebrar — mas NÃO em silêncio:
#     falha vira `📏?`, não ausência de sinal. "Não consegui medir" e "está
#     tudo dentro do teto" são estados diferentes, e a statusline é o único
#     lugar onde o usuário veria a diferença. Renderizar os dois igual é o
#     modo de falha que uma statusline não denuncia sozinha.
#
# O `sub(/\r$/, "")` tira o terminador de linha do Windows ANTES de medir: `\r`
# é byte e contaria, então um card de exatamente 240 bytes acenderia `📏` só
# porque o arquivo veio com CRLF. O teto mede conteúdo, não como o arquivo foi
# salvo.
gordos=$(LC_ALL=C awk -v teto=240 '
  { sub(/\r$/, "") }
  /^##+ .*[Aa]rquiv/ { archived=1 }
  archived { next }
  /^- \[[ >!~?x]\] `[^`]+`/ { if (length($0) > teto) n++ }
  END { print n+0 }
' "$board" 2>/dev/null) || gordos="?"
[ -n "$gordos" ] || gordos="?"

awk -v gordos="$gordos" '
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
  # indentado, negrito/itálico/crase envolvendo o traço ou o marcador...).
  # Conta como suspeita para a falha aparecer em vez de sumir em silêncio.
  # [*_`]* opcional nos dois pontos: pega "**- [ ]", "- **[ ]" e "`- [ ]`" —
  # os casos reais que produziam contagem errada SEM nenhum ⚠ (T-015).
  # [-*+] cobre os três bullets do CommonMark: "+ [ ] `T-001`" sumia inteiro.
  # O ESPAÇO OBRIGATÓRIO depois do bullet é o que separa card de prosa: sem
  # ele, "**[Contrato](x)** — leia antes" vira suspeita e o board conforme
  # acende ⚠ para sempre. Alarme crônico é alarme ignorado — a doença que
  # este contador existe para curar.
  # ~ no grupo: "~~- [ ]~~ `T-300`" (tachado GFM) sumia da contagem sem ⚠ —
  # é como se cancela um card em vez de arquivá-lo.
  /^[[:space:]]*[*_`~]*[-*+][[:space:]]+[*_`~]*\[/ { suspeitas++ }

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
    # Sinal PRÓPRIO, nunca o ⚠: são doenças diferentes. ⚠ é "linha parece card e
    # quebra o contrato" — raro e acionável na hora. 📏 é "card acima do teto" —
    # dívida acumulada, que fica acesa durante toda a migração. Somar as duas no
    # mesmo símbolo deixaria o ⚠ cronicamente aceso, e alarme crônico é alarme
    # ignorado: exatamente o que este contador existe para curar.
    if (gordos == "?") out = out " 📏?"
    else if (gordos + 0 > 0) out = out sprintf(" 📏%d", gordos + 0)
    print out
  }
' "$board"
