#!/bin/sh
# Lê memory/wiki/KANBAN.md do repo e emite um resumo compacto pra statusline.
# Modos: `<dir>` emite o resumo normal; `--resolver <dir>` emite o contrato
# JSON; `--board-path <absoluto>` é a recursão interna do modo normal.
# Uso: kanban-status.sh <dir>
# Saída: "📋 47% (7/15) · fazendo: Título curto"  (vazio se não houver quadro)

# `--resolver` emite JSON UTF-8 (path absoluto, existência e proveniência) e
# nunca deve ser interpretado linha a linha: caminhos Git podem conter newline.
# O modo normal resolve e faz exec deste próprio arquivo com `--board-path`; assim
# o caminho viaja como argumento de processo, não por substituição de comando.
case "$1" in
  --board-path)
    board="$2"
    case "$board" in
      /*) ;;
      *) exit 2 ;;
    esac
    [ -f "$board" ] || exit 0
    ;;
  *)
    structured=0
    [ "$1" = "--resolver" ] && structured=1 && shift
    dir="$1"
    [ -z "$dir" ] && dir="$PWD"

    if ! command -v python3 >/dev/null 2>&1; then
      if [ "$structured" -eq 1 ]; then
        printf '%s\n' '{"state":"erro","code":"python-indisponivel","board":null,"front_root":null,"thread_root":null,"exists":false,"provenance":null}'
        exit 2
      fi
      printf '%s\n' '⚠ quadro: Python 3 indisponível; não foi possível localizar o checkout principal'
      exit 0
    fi

    exec python3 - "$dir" "$0" "$structured" <<'PY'
import json
import os
import subprocess
import sys


origin, script, structured = sys.argv[1:]
origin = os.path.realpath(os.path.abspath(origin))
GIT_TIMEOUT_SECONDS = 0.75
GIT_TIMEOUT = object()
GIT_OSERROR = object()
GIT_ENV = os.environ.copy()
for inherited in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
    GIT_ENV.pop(inherited, None)


def git(*args):
    try:
        return subprocess.run(
            ["git", "-C", origin, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            env=GIT_ENV,
        )
    except subprocess.TimeoutExpired:
        return GIT_TIMEOUT
    except OSError:
        return GIT_OSERROR


def tem_metadado_git(path):
    """Evita chamar falha de Git de projeto sem Git quando há um `.git` no caminho."""
    current = os.path.abspath(path)
    while True:
        if os.path.lexists(os.path.join(current, ".git")):
            return True
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent


def common_dir(path):
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--git-common-dir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            env=GIT_ENV,
        )
    except subprocess.TimeoutExpired:
        return None
    except OSError:
        return GIT_OSERROR
    if result.returncode or not result.stdout.endswith(b"\n"):
        return None
    # Git termina esta saída com um LF. Remover só esse byte preserva um LF que
    # pertença ao próprio nome de diretório; `rstrip()` corromperia esse caminho.
    value = os.fsdecode(result.stdout[:-1])
    if not os.path.isabs(value):
        value = os.path.join(path, value)
    return os.path.realpath(value)


def caminho_git(path, *args):
    """Lê um caminho newline-terminated do Git sem apagar newline do nome."""
    try:
        result = subprocess.run(
            ["git", "-C", path, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            env=GIT_ENV,
        )
    except subprocess.TimeoutExpired:
        return None
    except OSError:
        return GIT_OSERROR
    if result.returncode or not result.stdout.endswith(b"\n"):
        return None
    value = os.fsdecode(result.stdout[:-1])
    if not os.path.isabs(value):
        value = os.path.join(path, value)
    return os.path.realpath(value)


def erro(code):
    return {
        "state": "erro",
        "code": code,
        "board": None,
        "front_root": None,
        "thread_root": None,
        "exists": False,
        "provenance": None,
    }


def ok(board, provenance, front_root):
    front_root = os.path.realpath(front_root)
    board = os.path.realpath(board)
    thread_root = os.path.realpath(os.path.join(front_root, "memory", "wiki"))
    return {
        "state": "ok",
        "code": None,
        "board": board,
        "front_root": front_root,
        "thread_root": thread_root,
        "exists": os.path.isfile(board),
        "provenance": provenance,
    }


def resolver():
    if not os.path.isdir(origin):
        return erro("origem-inexistente")
    inside = git("rev-parse", "--is-inside-work-tree")
    bare = git("rev-parse", "--is-bare-repository")
    if inside is GIT_OSERROR or bare is GIT_OSERROR:
        return erro("git-indisponivel")
    if inside is GIT_TIMEOUT or bare is GIT_TIMEOUT:
        return erro("git-timeout")
    if inside is None or bare is None:
        # Sem Git só o diretório sem metadado é comprovadamente local. Um `.git`
        # pode apontar a um checkout principal que não podemos confirmar.
        if tem_metadado_git(origin):
            return erro("git-indisponivel")
        board = os.path.join(origin, "memory", "wiki", "KANBAN.md")
        return ok(board, "local", origin)

    if bare.returncode == 0 and bare.stdout.strip() == b"true":
        return erro("checkout-bare")

    if inside.returncode or inside.stdout.strip() != b"true":
        if tem_metadado_git(origin):
            return erro("git-inconsistente")
        board = os.path.join(origin, "memory", "wiki", "KANBAN.md")
        return ok(board, "local", origin)

    front_root = caminho_git(origin, "rev-parse", "--show-toplevel")
    if front_root is GIT_OSERROR:
        return erro("git-indisponivel")
    if front_root is None:
        return erro("front-root-indisponivel")

    source_common = common_dir(origin)
    if source_common is GIT_OSERROR:
        return erro("git-indisponivel")
    if source_common is None:
        return erro("common-dir-indisponivel")

    listing = git("worktree", "list", "--porcelain", "-z")
    if listing is GIT_OSERROR:
        return erro("git-indisponivel")
    if listing is GIT_TIMEOUT:
        return erro("git-timeout")
    if listing is None or listing.returncode:
        return erro("worktree-list-indisponivel")
    if b"\0" not in listing.stdout:
        return erro("worktree-list-sem-nul")

    first = listing.stdout.split(b"\0\0", 1)[0]
    primary = next((field[9:] for field in first.split(b"\0") if field.startswith(b"worktree ")), None)
    if not primary:
        return erro("principal-ausente")
    primary = os.path.realpath(os.fsdecode(primary))
    if primary == source_common:
        # `git init --separate-git-dir` registra o Git dir como primeiro item.
        # A própria origem só pode substituí-lo quando ela aponta diretamente ao
        # common-dir. Em worktree ligada, Git não informa a raiz original: buscar
        # um ponteiro `.git` no disco não prova que ele é único nem atual. Portanto
        # preferimos falhar a aceitar cópia stale.
        source_git = caminho_git(origin, "rev-parse", "--git-dir")
        source_top = front_root
        if source_git is GIT_OSERROR:
            return erro("git-indisponivel")
        if source_git != source_common or source_top is None:
            return erro("principal-separate-git-dir-indisponivel")
        primary = source_top
    if not os.path.isdir(primary):
        return erro("principal-indisponivel")

    primary_common = common_dir(primary)
    if primary_common is GIT_OSERROR:
        return erro("git-indisponivel")
    if primary_common is None or primary_common != source_common:
        return erro("principal-inconsistente")
    try:
        primary_bare = subprocess.run(
            ["git", "-C", primary, "rev-parse", "--is-bare-repository"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            env=GIT_ENV,
        )
    except subprocess.TimeoutExpired:
        return erro("principal-timeout")
    except OSError:
        return erro("git-indisponivel")
    if primary_bare.returncode or primary_bare.stdout.strip() == b"true":
        return erro("principal-bare")

    board = os.path.join(primary, "memory", "wiki", "KANBAN.md")
    return ok(board, "principal" if front_root == primary else "worktree", front_root)


result = resolver()
if structured == "1":
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
    raise SystemExit(2 if result["state"] == "erro" else 0)
if result["state"] == "erro":
    print(f"⚠ quadro: checkout principal indisponível ({result['code']})")
    raise SystemExit(0)
os.execvp("sh", ["sh", script, "--board-path", result["board"]])
PY
    ;;
esac

# A partir daqui, o parser de cards recebe exclusivamente o board já resolvido.

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
