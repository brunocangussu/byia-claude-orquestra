#!/usr/bin/env python3
"""Ledger das guardas que vieram do ramo REMOTO (0.22.4–0.22.7).

Espelha o ledger do T-051: cada guarda tem contraprova negativa executada.
Validação do próprio ledger: TEM que dar 4/4 contra `6fde3e3` e reprovar em
`dcc350b` (o golden não conhece nenhuma delas).

Uso: python3 ledger_remoto.py <raiz-da-arvore>
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()


def roda_lint(raiz):
    r = subprocess.run(
        [sys.executable, "-B", "orq/scripts/lint-coerencia.py", "."],
        cwd=raiz,
        capture_output=True,
        text=True,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def contraprova(mutar, nome, espera):
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "arv"
        shutil.copytree(RAIZ, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        try:
            mutar(tmp)
        except Exception as exc:
            return False, f"mutação falhou: {exc}"
        rc, saida = roda_lint(tmp)
        if rc == 0:
            return False, f"lint passou VERDE com a mutação ({nome})"
        if espera not in saida:
            return False, f"lint reprovou por OUTRO motivo (esperava {espera!r})"
        return True, f"lint reprovou pelo guarda certo: {espera!r}"


def rem_1():
    """`validate_codex_consultive_language`: instrução viva não pode voltar a bloquear."""
    def mutar(tmp):
        p = tmp / "orq/commands/checkpoint.md"
        p.write_text(
            p.read_text(encoding="utf-8")
            + "\n\nNo Codex, o trabalho fica bloqueado até o checkpoint ser concluído.\n",
            encoding="utf-8",
        )

    return contraprova(
        mutar, "guardião voltando a bloquear", "contrato Codex inválido"
    )


def rem_2():
    """Comparação de cache host-aware: allowlist só do lado instalado, extra reprova."""
    sys.path.insert(0, str(RAIZ / "orq" / "scripts"))
    try:
        from verify_installed_cache import find_installation_divergences
    except ImportError as exc:
        return False, f"verify_installed_cache indisponível: {exc}"
    finally:
        sys.path.pop(0)

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src, inst = base / "src", base / "inst"
        for d in (src, inst):
            d.mkdir()
            (d / "a.md").write_text("igual\n")
        limpo = find_installation_divergences(source=src, installed=inst, host="claude")
        (inst / ".in_use").mkdir()
        (inst / ".in_use" / "123").write_text("")
        (inst / ".orphaned_at").write_text("x")
        normalizado = find_installation_divergences(source=src, installed=inst, host="claude")
        (inst / "intruso.md").write_text("extra\n")
        com_extra = find_installation_divergences(source=src, installed=inst, host="claude")
        (inst / "intruso.md").unlink()
        (src / ".in_use").mkdir()  # homônimo NA FONTE não é metadado: é produto
        fonte_suja = find_installation_divergences(source=src, installed=inst, host="claude")

    ok = limpo == [] and normalizado == [] and len(com_extra) == 1 and fonte_suja != []
    return ok, (
        f"limpo={len(limpo)} · metadados do host normalizados={len(normalizado)} · "
        f"extra instalado={len(com_extra)} · homônimo na fonte={len(fonte_suja)}"
    )


def rem_3():
    """Teto de 600s do runner Opus é exigido pelo lint nas duas superfícies."""
    def mutar_doc(tmp):
        p = tmp / "orq/commands/revisar.md"
        p.write_text(
            p.read_text(encoding="utf-8").replace("timeout de 600s", "timeout de 240s"),
            encoding="utf-8",
        )

    def mutar_codigo(tmp):
        p = tmp / "orq/scripts/run-opus-reviewer.py"
        p.write_text(
            p.read_text(encoding="utf-8").replace(
                "DEFAULT_TIMEOUT_SECONDS = 600.0", "DEFAULT_TIMEOUT_SECONDS = 240.0"
            ),
            encoding="utf-8",
        )

    a = contraprova(mutar_doc, "revisar.md volta a 240s", "timeout de 600s")
    b = contraprova(mutar_codigo, "runner volta a 240s", "DEFAULT_TIMEOUT_SECONDS = 600.0")
    return a[0] and b[0], f"doc: {a[1]} | código: {b[1]}"


def rem_4():
    """Import seguro do comparador + bytecode desligado, nos dois modos de execução."""
    fonte = (RAIZ / "orq/scripts/lint-coerencia.py").read_text(encoding="utf-8")
    ok = "sys.dont_write_bytecode = True" in fonte
    ok &= "except ModuleNotFoundError:" in fonte
    ok &= "from verify_installed_cache import find_installation_divergences" in fonte
    ok &= "problemas.extend(validate_codex_consultive_language(raiz, plugin))" in fonte
    # execução direta a partir do diretório de scripts (o modo do cache instalado)
    r = subprocess.run(
        [sys.executable, str(RAIZ / "orq/scripts/lint-coerencia.py"), str(RAIZ)],
        capture_output=True,
        text=True,
    )
    ok &= r.returncode == 0
    lixo = list((RAIZ / "orq" / "scripts").glob("__pycache__"))
    ok &= not lixo
    return ok, f"execução direta exit={r.returncode}, __pycache__ criado: {bool(lixo)}"


PROBES = [
    ("REM-1", "linguagem consultiva do guardião Codex", rem_1),
    ("REM-2", "comparação de cache host-aware (allowlist só no instalado)", rem_2),
    ("REM-3", "teto de 600s do runner Opus, doc e código", rem_3),
    ("REM-4", "import seguro do comparador + bytecode desligado", rem_4),
]


def main():
    print(f"# Ledger remoto — 4 guardas · árvore: {RAIZ}\n")
    passou, falhos = 0, []
    for pid, titulo, fn in PROBES:
        try:
            ok, detalhe = fn()
        except Exception as exc:
            ok, detalhe = False, f"ERRO no probe: {type(exc).__name__}: {exc}"
        print(f"[{'PASS' if ok else 'FAIL'}] {pid} — {titulo}\n        {detalhe}")
        passou += ok
        if not ok:
            falhos.append(pid)
    print(f"\n=== {passou}/{len(PROBES)} ===")
    if falhos:
        print("FALHARAM:", ", ".join(falhos))
    return 0 if passou == len(PROBES) else 1


if __name__ == "__main__":
    sys.exit(main())
