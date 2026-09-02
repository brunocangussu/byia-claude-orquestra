#!/usr/bin/env python3
"""Ledger da 3ª rodada de revisão do T-052 — 1 bloqueador.

O bump coordenado tem de ser PASSO da seção `Desenvolver o plugin` do README,
não advertência avulsa em outra seção. Os probes provam as duas propriedades que
tornam o guarda não-decorativo: ele **ancora na seção** e **mascara as cercas**.

Uso: python3 ledger_revisao3_t052.py <raiz>
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
OBRIGACAO = "⚠️ **Mexeu em `orq/`? O primeiro passo é o bump"
MSG = "não manda bumpar"
# Os dois procedimentos ordenados. O segundo saiu da varredura pós-correção: o
# `## Ciclo de edição` tinha o mesmo buraco do README, e cobrir só um deixaria
# a página mais usada em release ensinando a publicar sem bump.
PROCEDIMENTOS = (
    ("README.md", "## Desenvolver o plugin", "Ao editar, **os três gates"),
    ("memory/wiki/distribuicao.md", "## Ciclo de edição", "```bash"),
)
HEADING = PROCEDIMENTOS[0][1]


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def lint(raiz):
    r = subprocess.run(
        [sys.executable, "-B", "orq/scripts/lint-coerencia.py", "."],
        cwd=raiz, capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr


def _lint_modulo():
    import importlib.util
    scripts = RAIZ / "orq" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location("lint_r3", scripts / "lint-coerencia.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def com_mutacao(mutar):
    td = tempfile.mkdtemp()
    tmp = Path(td) / "arv"
    shutil.copytree(RAIZ, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    mutar(tmp)
    return td, tmp


def _tira_da_secao(rel, fim_marcador):
    """Remove a obrigação SÓ da seção do fluxo; o alerta do resto do arquivo fica."""

    def _m(tmp):
        p = tmp / rel
        t = p.read_text(encoding="utf-8")
        i = t.index(OBRIGACAO)
        j = t.index(fim_marcador, i)
        p.write_text(t[:i] + t[j:], encoding="utf-8")

    return _m


# ------------------------------------------------------------------ probes
def b1():
    """A obrigação existe nos DOIS procedimentos, como prosa e antes dos gates."""
    mod = _lint_modulo()
    exigidos = [
        "O primeiro passo é o bump",
        "orq/.claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
        "memory/MEMORY.md",
        "Status",
    ]
    detalhes, ok = [], True
    for rel, heading, _ in PROCEDIMENTOS:
        secao, estado = mod.secao_unica(ler(rel), heading)
        if estado != "ok":
            ok = False
            detalhes.append(f"{rel}: seção {estado}")
            continue
        prosa = mod._mascara_cercas(secao)
        faltando = [e for e in exigidos if e not in prosa]
        # a obrigação abre a seção — vem antes de qualquer comando
        primeiro = prosa.strip().startswith("⚠️") or prosa.index("O primeiro passo é o bump") < 200
        ok &= not faltando and primeiro
        detalhes.append(f"{rel}: 4 lugares ok={not faltando}, abre a seção={primeiro}")
    return ok, " | ".join(detalhes)


def b1_g1_ancora():
    """Contraprova exigida: apagar SÓ da seção, mantendo o alerta, tem de reprovar."""
    td, tmp = com_mutacao(_tira_da_secao("README.md", "Ao editar, **os três gates"))
    try:
        alerta_intacto = "quem edita sem bumpar deixa o cache stale" in (tmp / "README.md").read_text(encoding="utf-8")
        rc, saida = lint(tmp)
        ok = alerta_intacto and rc != 0 and MSG in saida
        quantos = saida.count(MSG)
        return ok, f"alerta posterior intacto={alerta_intacto}; lint exit={rc}; {quantos} achados `{MSG}`"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def b1_g2_ancora_importa():
    """O guarda ANCORADO acha o que um guarda de arquivo inteiro não acharia.

    Escrito do jeito preguiçoso — procurar os nomes soltos no README todo — o
    guarda ficaria verde com o fluxo quebrado, porque o alerta e as tabelas de
    outras seções satisfazem a busca.
    """
    td, tmp = com_mutacao(_tira_da_secao("README.md", "Ao editar, **os três gates"))
    try:
        texto = (tmp / "README.md").read_text(encoding="utf-8")
        ingenuo = {a: (a in texto) for a in ("plugin.json", "marketplace.json", "MEMORY.md", "Status")}
        rc, saida = lint(tmp)
        ok = all(ingenuo.values()) and rc != 0 and MSG in saida
        return ok, (
            f"guarda ingênuo (arquivo inteiro, nomes soltos) = {'VERDE' if all(ingenuo.values()) else 'vermelho'}"
            f" · guarda ancorado = {'vermelho' if rc != 0 else 'VERDE'} — é a diferença que o torna útil"
        )
    finally:
        shutil.rmtree(td, ignore_errors=True)


def b1_g3_cerca():
    """Obrigação dentro de cerca é listagem, não procedimento: tem de reprovar."""
    def mutar(tmp):
        p = tmp / "README.md"
        t = p.read_text(encoding="utf-8")
        i = t.index(OBRIGACAO)
        j = t.index("Ao editar, **os três gates", i)
        bloco = t[i:j]
        p.write_text(t[:i] + "```text\n" + bloco.rstrip() + "\n```\n\n" + t[j:], encoding="utf-8")

    td, tmp = com_mutacao(mutar)
    try:
        rc, saida = lint(tmp)
        ok = rc != 0 and MSG in saida
        return ok, f"cercada → lint exit={rc}, {saida.count(MSG)} achados `{MSG}`"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def b1_g4_secao_sumida():
    """Renomear/duplicar a seção não pode virar rota de fuga."""
    def renomeia(tmp):
        p = tmp / "README.md"
        p.write_text(p.read_text(encoding="utf-8").replace(HEADING, HEADING + " (antigo)", 1), encoding="utf-8")

    def duplica(tmp):
        p = tmp / "README.md"
        t = p.read_text(encoding="utf-8")
        p.write_text(t + f"\n\n{HEADING}\n\nnada aqui.\n", encoding="utf-8")

    saidas = []
    for nome, mut, esperado in (("renomeada", renomeia, "ausente"), ("duplicada", duplica, "duplicado")):
        td, tmp = com_mutacao(mut)
        try:
            rc, saida = lint(tmp)
            saidas.append((nome, rc != 0 and esperado in saida))
        finally:
            shutil.rmtree(td, ignore_errors=True)
    ok = all(v for _, v in saidas)
    return ok, "; ".join(f"{n}: {'reprovou' if v else 'PASSOU VERDE'}" for n, v in saidas)


def b1_g5_irmao():
    """Cobrir só o README deixaria `## Ciclo de edição` ensinando a publicar sem bump."""
    td, tmp = com_mutacao(_tira_da_secao("memory/wiki/distribuicao.md", "```bash"))
    try:
        rc, saida = lint(tmp)
        ok = rc != 0 and "## Ciclo de edição" in saida and MSG in saida
        return ok, f"distribuicao sem a obrigação → lint exit={rc}, cita a seção certa={'## Ciclo de edição' in saida}"
    finally:
        shutil.rmtree(td, ignore_errors=True)


PROBES = [
    ("B1", "bump é passo dos dois procedimentos ordenados", b1),
    ("B1-g1", "contraprova: apagar só da seção (alerta intacto)", b1_g1_ancora),
    ("B1-g2", "o ancoramento é o que faz o guarda valer", b1_g2_ancora_importa),
    ("B1-g3", "obrigação dentro de cerca não conta", b1_g3_cerca),
    ("B1-g4", "seção renomeada ou duplicada não é rota de fuga", b1_g4_secao_sumida),
    ("B1-g5", "o procedimento irmão (`## Ciclo de edição`) também é coberto", b1_g5_irmao),
]


def main():
    print(f"# Ledger da revisão T-052 · rodada 3 · árvore: {RAIZ}\n")
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
