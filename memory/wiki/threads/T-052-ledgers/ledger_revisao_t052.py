#!/usr/bin/env python3
"""Ledger da revisão externa do T-052 — 3 bloqueadores + 2 riscos.

Mesmo padrão dos outros dois: regra positiva + contraprova negativa executada.
Validação do ledger: tem que reprovar na árvore ANTES da correção.

Uso: python3 ledger_revisao_t052.py <raiz>
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def contraprova(mutar, nome, espera):
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "arv"
        shutil.copytree(RAIZ, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        try:
            mutar(tmp)
        except Exception as exc:
            return False, f"mutação falhou: {exc}"
        r = subprocess.run(
            [sys.executable, "-B", "orq/scripts/lint-coerencia.py", "."],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        saida = r.stdout + r.stderr
        if r.returncode == 0:
            return False, f"lint passou VERDE com a mutação ({nome})"
        if espera not in saida:
            return False, f"lint reprovou por OUTRO motivo (esperava {espera!r})"
        return True, f"reprovou pelo guarda certo: {espera!r}"


def acrescenta(rel, texto):
    def _m(tmp):
        p = tmp / rel
        p.write_text(p.read_text(encoding="utf-8") + texto, encoding="utf-8")

    return _m


# ---------------------------------------------------------------- B1
def b1():
    """README ressuscitou 240s enquanto runner, elenco e wiki fixam 600s."""
    teto = re.search(
        r"^DEFAULT_TIMEOUT_SECONDS\s*=\s*(\d+)",
        ler("orq/scripts/run-opus-reviewer.py"),
        re.M,
    ).group(1)
    superficies = (
        "README.md",
        "orq/commands/revisar.md",
        "orq/commands/elenco.md",
        "memory/wiki/_elenco.md",
        "memory/wiki/arquitetura.md",
    )
    ok = all(f"{teto}s" in ler(s) for s in superficies)
    # nenhuma superfície pode anunciar outro número para o runner
    linha_runner = [
        l
        for s in superficies
        for l in ler(s).splitlines()
        if ("runner-opus" in l or "run-opus-reviewer" in l) and re.search(r"\d{2,4}\s*s\b", l)
    ]
    ok &= all(f"{teto}s" in l for l in linha_runner)
    return ok, f"teto derivado={teto}s presente nas 5 superfícies; {len(linha_runner)} linhas de runner coerentes"


def b1_guarda_valor():
    return contraprova(
        lambda tmp: (tmp / "README.md").write_text(
            (tmp / "README.md").read_text(encoding="utf-8").replace(
                "16 KiB/lote · 600s", "16 KiB/lote · 240s"
            ),
            encoding="utf-8",
        ),
        "README volta a 240s",
        "anuncia 240s para o runner Opus",
    )


def b1_guarda_ausencia():
    return contraprova(
        lambda tmp: (tmp / "memory/wiki/_elenco.md").write_text(
            (tmp / "memory/wiki/_elenco.md").read_text(encoding="utf-8").replace(
                "· timeout 600s ", "· "
            ),
            encoding="utf-8",
        ),
        "wiki apaga o teto",
        "não declara o teto do runner Opus",
    )


def b1_guarda_derivacao():
    """Sobe o teto no runner sem mexer na prosa: se o guarda derivasse, acusa."""
    return contraprova(
        lambda tmp: (tmp / "orq/scripts/run-opus-reviewer.py").write_text(
            (tmp / "orq/scripts/run-opus-reviewer.py").read_text(encoding="utf-8").replace(
                "DEFAULT_TIMEOUT_SECONDS = 600.0", "DEFAULT_TIMEOUT_SECONDS = 900.0"
            ),
            encoding="utf-8",
        ),
        "runner sobe para 900s e a prosa fica em 600s",
        "`DEFAULT_TIMEOUT_SECONDS` é 900",
    )


# ---------------------------------------------------------------- B2
def b2():
    """`PAINEL PARCIAL` sobrevivendo contradiz REVISÃO DEGRADADA."""
    d = ler("memory/wiki/distribuicao.md")
    ok = "precisam resultar em **`REVISÃO DEGRADADA — sem parecer`**" in d
    ok &= "o card não avança sozinho" in d
    ok &= "nunca `PAINEL PARCIAL`" in d  # só como negação explícita
    r = ler("orq/commands/revisar.md")
    ok &= "REVISÃO DEGRADADA — sem parecer" in r and "O card **não** avança sozinho" in r
    return ok, "distribuição alinhada ao contrato do /orq:revisar"


def b2_guarda():
    return contraprova(
        acrescenta(
            "memory/wiki/distribuicao.md",
            "\n\nTimeout do revisor: aplique PAINEL PARCIAL e siga o release.\n",
        ),
        "PAINEL PARCIAL vivo",
        "`PAINEL PARCIAL` em instrução viva",
    )


# ---------------------------------------------------------------- B3
def b3():
    """A distribuição mandava manter a quinta fonte de versão."""
    d = ler("memory/wiki/distribuicao.md")
    ok = "A versão vive em **quatro** lugares" in d
    ok &= "**cinco** lugares" not in d
    ok &= all(
        "deriva" in l for l in d.splitlines() if "ContextGuardReleaseVersionTest" in l
    )
    for arq in ("CLAUDE.md", "AGENTS.md"):
        t = ler(arq)
        ok &= "(são quatro, e" in t
        ok &= all("deriva" in l for l in t.splitlines() if "ContextGuardReleaseVersionTest" in l)
    return ok, "quatro fontes declaradas; o teste é citado sempre como guarda derivada"


def b3_guarda():
    return contraprova(
        acrescenta(
            "memory/wiki/distribuicao.md",
            "\n\nAtualize também a constante de ContextGuardReleaseVersionTest a cada bump.\n",
        ),
        "quinta fonte de versão de volta",
        "sem dizer que ele",
    )


# ---------------------------------------------------------------- R1
def r1():
    """`RETOMAR AQUI` do T-048 apontava para trabalho concluído."""
    t = ler("memory/wiki/threads/T-048-auditores-nativos.md")
    ok = t.count("RETOMAR AQUI") == 1
    bloco = t.split("## ⏭️ RETOMAR AQUI", 1)[1]
    ok &= "Nada pendente nesta thread" in bloco
    ok &= "Não reabra o `T-049`" in bloco
    ok &= "Topologia de hosts vencida" in t
    return ok, f"1 marcador vivo, thread declarada encerrada ({len(bloco.strip())} chars)"


# ---------------------------------------------------------------- R2
def r2():
    """`diff -rq` sobrevivia como prova de cache na mesma página que o proíbe."""
    d = ler("memory/wiki/distribuicao.md")
    ok = "entra na cobertura do\n`verify_installed_cache.py`" in d
    ok &= "precisa entrar no `diff -rq`" not in d
    ok &= len([l for l in d.splitlines() if "diff -rq" in l]) == 1  # só a negação
    return ok, "hooks cobertos pelo verificador compartilhado"


def r2_guarda():
    return contraprova(
        acrescenta(
            "memory/wiki/distribuicao.md",
            "\n\nConfira os hooks com diff -rq contra o cache instalado.\n",
        ),
        "diff -rq de volta como prova",
        "`diff -rq` em instrução viva",
    )


# ------------------------------------------------- páginas vivas realmente varridas
def pagina_viva_varrida():
    """Prova que o lint deixou de pular as duas páginas vivas."""
    a = contraprova(
        acrescenta(
            "memory/wiki/distribuicao.md",
            "\n\nUse o Kimi K3 (Moonshot) para revisar o release.\n",
        ),
        "host aposentado vivo em distribuicao.md",
        "cita o host aposentado",
    )
    b = contraprova(
        acrescenta(
            "memory/wiki/arquitetura.md",
            "\n\nUse o Kimi K3 (Moonshot) como terceiro revisor.\n",
        ),
        "host aposentado vivo em arquitetura.md",
        "cita o host aposentado",
    )
    c = ler("memory/gotchas.md")  # continua fora do guarda, de propósito
    ok = a[0] and b[0] and ("Kimi" in c or "kimi" in c)
    return ok, f"distribuicao: {a[1]} | arquitetura: {b[1]} | log/gotchas segue fora do guarda"


PROBES = [
    ("B1", "README ressuscitou o teto de 240s", b1),
    ("B1-g1", "guarda: valor divergente na prosa", b1_guarda_valor),
    ("B1-g2", "guarda: teto apagado da superfície", b1_guarda_ausencia),
    ("B1-g3", "guarda: DERIVA do runner (não é número fixo no lint)", b1_guarda_derivacao),
    ("B2", "PAINEL PARCIAL contra REVISÃO DEGRADADA", b2),
    ("B2-g", "guarda: PAINEL PARCIAL em instrução viva", b2_guarda),
    ("B3", "quinta fonte de versão na distribuição", b3),
    ("B3-g", "guarda: teste citado sem derivação", b3_guarda),
    ("R1", "RETOMAR AQUI do T-048 apontava para concluído", r1),
    ("R2", "diff -rq como prova de cache", r2),
    ("R2-g", "guarda: diff -rq em instrução viva", r2_guarda),
    ("PV", "páginas vivas de memory/ realmente varridas", pagina_viva_varrida),
]


def main():
    print(f"# Ledger da revisão T-052 · árvore: {RAIZ}\n")
    passou, falhos = 0, []
    for pid, titulo, fn in PROBES:
        try:
            ok, det = fn()
        except Exception as exc:
            ok, det = False, f"ERRO no probe: {type(exc).__name__}: {exc}"
        print(f"[{'PASS' if ok else 'FAIL'}] {pid} — {titulo}\n        {det}")
        passou += ok
        if not ok:
            falhos.append(pid)
    print(f"\n=== {passou}/{len(PROBES)} ===")
    if falhos:
        print("FALHARAM:", ", ".join(falhos))
    return 0 if passou == len(PROBES) else 1


if __name__ == "__main__":
    sys.exit(main())
