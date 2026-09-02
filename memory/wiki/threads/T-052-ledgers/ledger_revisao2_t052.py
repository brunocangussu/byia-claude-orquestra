#!/usr/bin/env python3
"""Ledger da 2ª rodada de revisão do T-052 — 3 bloqueadores + 2 riscos.

Mesmo padrão: regra positiva + contraprova negativa executada. Onde dá, o probe
DERIVA a expectativa da fonte (lint, `_elenco.md`, suíte real) em vez de fixar
literal — assim doc e código não podem divergir sem o probe acusar.

Uso: python3 ledger_revisao2_t052.py <raiz>
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
SUITE = "python3 -m unittest discover -s orq/scripts -p 'test_*.py'"
INSTRUCOES_DE_RELEASE = ("CLAUDE.md", "AGENTS.md", "README.md", "memory/wiki/distribuicao.md")


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
            cwd=tmp, capture_output=True, text=True,
        )
        saida = r.stdout + r.stderr
        if r.returncode == 0:
            return False, f"lint passou VERDE com a mutação ({nome})"
        if espera not in saida:
            return False, f"lint reprovou por OUTRO motivo (esperava {espera!r})"
        return True, f"reprovou pelo guarda certo: {espera!r}"


# ------------------------------------------------------------------ B1
def b1():
    """Guia de release mandava publicar sem rodar a suíte."""
    gates = (SUITE, "claude plugin validate ./orq --strict", "python3 orq/scripts/lint-coerencia.py .")
    faltas, enumera = [], []
    for rel in INSTRUCOES_DE_RELEASE:
        txt = ler(rel)
        faltas += [f"{rel}:{g[:28]}" for g in gates if g not in txt]
        if re.search(r"python3 -m unittest\s+orq\.scripts\.", txt):
            enumera.append(rel)
    ok = not faltas and not enumera
    ok &= ler("CLAUDE.md") == ler("AGENTS.md")
    return ok, f"4 superfícies × 3 gates; faltas={faltas or 'nenhuma'}; enumeração={enumera or 'nenhuma'}"


def b1_executa():
    """A suíte descoberta roda MESMO os 5 módulos — não 3 de 5."""
    r = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "orq/scripts", "-p", "test_*.py", "-v"],
        cwd=RAIZ, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    saida = r.stderr
    modulos = {m for m in re.findall(r"\(test_(\w+?)\.", saida)}
    total = re.search(r"Ran (\d+) tests", saida)
    no_disco = {p.stem[len("test_"):] for p in (RAIZ / "orq/scripts").glob("test_*.py")}
    ok = r.returncode == 0 and modulos == no_disco and total is not None
    return ok, f"{total.group(1) if total else '?'} testes, {len(modulos)}/{len(no_disco)} módulos do disco executados"


def b1_guarda_ausencia():
    def mutar(tmp):
        p = tmp / "memory/wiki/distribuicao.md"
        p.write_text(p.read_text(encoding="utf-8").replace(SUITE, "echo pulei a suite"), encoding="utf-8")
    return contraprova(mutar, "distribuição sem a suíte", "não cita a suíte")


def b1_guarda_enumeracao():
    def mutar(tmp):
        for nome in ("CLAUDE.md", "AGENTS.md"):
            p = tmp / nome
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    SUITE,
                    "python3 -m unittest orq.scripts.test_context_guard orq.scripts.test_run_opus_reviewer",
                ),
                encoding="utf-8",
            )
    return contraprova(mutar, "volta a enumerar módulos", "enumera módulos de teste")


# ------------------------------------------------------------------ B2
def b2():
    """A stack não sabia provisionar o revisor do host Codex."""
    s = ler("orq/stack.md")
    ok = "Esta camada é host-aware: resolva o host ANTES de propor." in s
    ok &= "### `claude` + `run-opus-reviewer.py` — o revisor do host Codex" in s
    ok &= "anthropics/claude-code" in s                      # origem oficial
    ok &= 'CLAUDE=$(command -v claude || echo "$(npm prefix -g 2>/dev/null)/bin/claude")' in s  # detecção
    ok &= "| **Claude Code** | a CLI `codex` (OpenAI) | é o revisor |" in s
    ok &= "vendor oposto ao host**: `codex` se o host é o Claude Code" in s  # perfil host-aware
    ok &= "| **Trabalho crítico** (dinheiro, dados de terceiros, segurança) | `codex` como revisor |" not in s
    return ok, "camada 4 com as duas rotas, detecção, origem oficial e perfil host-aware"


# ------------------------------------------------------------------ B3
def b3():
    """O ramo Claude abandonava a fonte limpa já resolvida no passo 0."""
    i = ler("orq/commands/instalar.md")
    ramo = i.split("## Claude — já instalado, só confere", 1)[1].split("## Codex", 1)[0]
    ok = "verify_installed_cache.py" in ramo and "--host claude" in ramo
    ok &= "<fonte-local>/orq" in ramo
    ok &= "Não caia no ramo \"Source remota\" do diagnóstico genérico." in ramo
    ok &= "aplique o passo a passo de lá" not in ramo   # não delega mais a checagem
    ok &= "**Não invoque `/orq:stack`**" in ramo        # a regra que continua válida
    s = ler("orq/commands/stack.md")
    ok &= "**e sem fonte limpa à mão**" in s            # o indeterminado ganhou condição
    ok &= "Prova disponível não vira\n     indeterminação." in s
    return ok, "ramo Claude fecha a igualdade com o clone do passo 0"


# ------------------------------------------------------------------ R1
def r1():
    """A doc negava a cobertura nominal que o lint passou a ter — agora DERIVA do lint."""
    fonte = ler("orq/scripts/lint-coerencia.py")
    bloco = fonte.split("PAGINAS_VIVAS_FORA_DO_PLUGIN = (", 1)[1].split(")", 1)[0]
    nominais = set(re.findall(r'"([^"]+)"', bloco))
    ok = bool(nominais)
    for rel in ("memory/wiki/distribuicao.md", "CLAUDE.md"):
        txt = ler(rel)
        ok &= all(n in txt for n in nominais)          # a doc lista exatamente o que o lint varre
        ok &= "fixes-history.md" in txt and "gotchas.md" in txt and "threads/" in txt
        ok &= "ignora `memory/` de propósito** — o log" not in txt   # a frase absoluta saiu
    ok &= ler("CLAUDE.md") == ler("AGENTS.md")
    return ok, f"fronteira documentada e derivada do lint: {sorted(nominais)}"


# ------------------------------------------------------------------ R2
def r2():
    """A arquitetura descrevia papéis singulares; o elenco tem dois eixos."""
    elenco = ler("memory/wiki/_elenco.md")
    tabela = elenco.split("### Host Codex", 1)[1].split("###", 1)[0]
    celulas = {}
    for linha in tabela.splitlines():
        m = re.match(r"\|\s*([a-z]+(?:·[a-z]+)?)\s*\|\s*`([^`]+)`", linha)
        if m:
            celulas[m.group(1)] = m.group(2)
    arq = ler("memory/wiki/arquitetura.md")
    faltando = []
    for papel, modelo in celulas.items():
        if papel == "manager":
            continue
        # o papel tem que aparecer com o MESMO modelo que o `_elenco.md` registra
        if not re.search(rf"`{re.escape(papel)}`[^\n]{{0,40}}`{re.escape(modelo)}`", arq):
            faltando.append(f"{papel}={modelo}")
    ok = not faltando and len(celulas) >= 8
    ok &= "**Esta página não é a fonte\ndos modelos concretos**" in arq
    ok &= "seção `## Times por host`, que é de onde os comandos leem" in arq
    ok &= "o titular é Manager `gpt-5.6-sol@high`, Planner `gpt-5.6-sol@ultra` e Implementer" not in arq
    return ok, f"{len(celulas)} células do `_elenco.md` conferidas; divergentes={faltando or 'nenhuma'}"


PROBES = [
    ("B1", "release sem a suíte nos três gates", b1),
    ("B1-x", "a suíte descoberta executa os 5 módulos", b1_executa),
    ("B1-g1", "guarda: superfície de release sem a suíte", b1_guarda_ausencia),
    ("B1-g2", "guarda: volta a enumerar módulos", b1_guarda_enumeracao),
    ("B2", "camada 4 host-aware, com rota Anthropic", b2),
    ("B3", "ramo Claude usa a fonte limpa do passo 0", b3),
    ("R1", "fronteira do memory/ documentada e derivada", r1),
    ("R2", "arquitetura em dois eixos, batendo com o elenco", r2),
]


def main():
    print(f"# Ledger da revisão T-052 · rodada 2 · árvore: {RAIZ}\n")
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
