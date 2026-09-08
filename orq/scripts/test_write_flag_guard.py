#!/usr/bin/env python3
"""Testes da guarda que proíbe `--write` fora da frase-âncora nos convites ao
Codex Companion (T-019).

Em 2026-07-28 um revisor rodou `git checkout -- .` num working tree que a
instrução dizia ser "read-only": `codex-companion.mjs` resolve
`sandbox: request.write ? "workspace-write" : "read-only"`, e nada no produto
proibia a flag `--write` — só não a listava, e "não listar" não é
enforcement. Este módulo prova que a proibição (T-019) tem enforcement real
no `lint-coerencia.py`, não só prosa: remover a frase-âncora ou injetar
`--write` numa linha de invocação real tem que reprovar o lint, nomeando o
arquivo — mesmo que a frase-âncora continue presente em outro parágrafo.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")

lint_spec = importlib.util.spec_from_file_location("orq_lint_coerencia_t019", LINT_PATH)
assert lint_spec is not None and lint_spec.loader is not None
lint_module = importlib.util.module_from_spec(lint_spec)
sys.modules[lint_spec.name] = lint_module
lint_spec.loader.exec_module(lint_module)

# Byte-idêntica à constante `ANCORA_PROIBICAO_WRITE` de `lint-coerencia.py` e
# à linha que o T-019 gravou nos três arquivos. Duplicada aqui de propósito
# (como o restante da suíte faz com fragmentos do lint): o teste tem que
# continuar válido mesmo se alguém reformular a constante do lint sem tocar
# nos documentos — nesse caso ele é quem denuncia a divergência.
ANCORA = (
    "⚠️ **Nunca acrescente `--write`.** O read-only desta chamada vem da "
    "ausência dessa flag: com ela, o sandbox do Companion vira "
    "`workspace-write` e o papel deixa de ser read-only."
)

# A revisão independente de 2026-09-07 mostrou que os três comandos não eram
# todos os produtores de argumento: a SKILL.md especifica a chamada e é produto
# distribuído, e a matriz viva do projeto é a configuração que os próprios
# comandos mandam consultar. Injetar a flag em qualquer uma das duas passava
# com `main()` retornando 0.
ARQUIVOS_RELATIVOS = (
    "orq/commands/revisar.md",
    "orq/commands/plan-next.md",
    "orq/commands/elenco.md",
    "orq/skills/orq/SKILL.md",
    "memory/wiki/_elenco.md",
)

# Uma linha de invocação real por arquivo, única no documento, usada para
# simular alguém acrescentando `--write` a uma chamada de verdade (não à
# frase-âncora). O par (alvo, substituto) preserva tudo ao redor — só a flag
# nova muda.
INJECOES_WRITE = {
    "orq/commands/revisar.md": (
        "primeira chamada do Reviewer na rodada: `--wait --fresh --json --model "
        "<modelo> --effort <effort> <briefing read-only>`",
        "primeira chamada do Reviewer na rodada: `--wait --fresh --write --json --model "
        "<modelo> --effort <effort> <briefing read-only>`",
    ),
    "orq/commands/plan-next.md": (
        "primeira chamada do Planner naquele card: `--wait --fresh --json --model "
        "<modelo> --effort <effort> <briefing read-only>`",
        "primeira chamada do Planner naquele card: `--wait --fresh --write --json --model "
        "<modelo> --effort <effort> <briefing read-only>`",
    ),
    "orq/commands/elenco.md": (
        "`codex-companion.mjs task --model <modelo> --effort <effort>`; primeira "
        "chamada por `card+papel` usa `--fresh --json`",
        "`codex-companion.mjs task --model <modelo> --effort <effort> --write`; "
        "primeira chamada por `card+papel` usa `--fresh --json`",
    ),
    "orq/skills/orq/SKILL.md": (
        "`--fresh --json`; a continuação leva `--resume-thread <threadId> --json`.",
        "`--fresh --json --write`; a continuação leva `--resume-thread <threadId> --json`.",
    ),
    "memory/wiki/_elenco.md": (
        "primeira chamada por `card+papel` usa `--fresh --json`, continuação usa "
        "`--resume-thread <threadId> --json`",
        "primeira chamada por `card+papel` usa `--fresh --json --write`, continuação usa "
        "`--resume-thread <threadId> --json`",
    ),
}

# A grafia de hífen único resolve para a MESMA chave booleana no parser do
# Companion (`lib/args.mjs` faz `token.slice(1)` no ramo de um hífen), então
# procurar só por `--write` deixava esta porta aberta. Achado bloqueador da
# revisão de 2026-09-07.
INJECAO_HIFEN_UNICO = (
    "orq/commands/revisar.md",
    "primeira chamada do Reviewer na rodada: `--wait --fresh --json --model "
    "<modelo> --effort <effort> <briefing read-only>`",
    "primeira chamada do Reviewer na rodada: `--wait --fresh -write --json --model "
    "<modelo> --effort <effort> <briefing read-only>`",
)


# Isola a cópia efêmera do board da guarda de posse do T-086: o board vivo muda
# a cada card assumido, e um card em `[>]`/`[~]` sem marcador reprovaria aqui
# por um motivo alheio ao que este módulo mede. Este módulo testa T-019 (proibição de `--write`), não T-086: sem isto, todo
# controle negativo que copia o repositório real reprovaria por um motivo
# alheio ao que está sendo medido aqui. Marca só a CÓPIA efêmera, nunca o
# arquivo rastreado pelo git — duplicada com o mesmo nome em
# `test_elenco_perfis.py` de propósito, mesma disciplina de duplicação que o
# resto da suíte já aplica a fragmentos do lint.
def neutralizar_marcador_host_kanban(root: Path) -> None:
    board = root / "memory" / "wiki" / "KANBAN.md"
    if not board.is_file():
        return
    texto = board.read_text(encoding="utf-8")

    def marca(m: "re.Match[str]") -> str:
        linha = m.group(0)
        return linha if ("@claude" in linha or "@codex" in linha) else linha + " @claude"

    marcado = re.sub(r"(?m)^- \[[>~]\] `[^`]+`.*$", marca, texto)
    board.write_text(marcado, encoding="utf-8")


def run_lint_main(root: Path, home: Path) -> tuple[int, str]:
    """Roda a CÓPIA do lint que mora dentro de `root` (não o módulo importado
    no topo deste arquivo) como **subprocesso** — mesmo motivo documentado em
    `test_elenco_perfis.py::run_lint_main`: `main()` exclui a si mesmo da
    varredura de vocabulário do host aposentado comparando `Path(__file__)`
    com cada arquivo varrido, e essa exclusão só bate certo quando
    `__file__`, ali dentro, É a cópia — o que só acontece rodando a cópia
    como processo próprio.

    `HOME` isolado no diretório do teste (não o cache real desta máquina):
    sem isso, a guarda "Cache stale por edição sem bump" (T-017) acusaria a
    cópia mutada contra `~/.claude/plugins/cache/...` desta máquina — ruído
    que este módulo não quer medir.
    """
    script = root / "orq" / "scripts" / "lint-coerencia.py"
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    resultado = subprocess.run(
        [sys.executable, str(script), str(root)],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    return resultado.returncode, resultado.stdout + resultado.stderr


class WriteFlagGuardTest(unittest.TestCase):
    """Fixture: cópia completa do repositório real. `setUp` roda antes de
    CADA método de teste — cada um começa de uma árvore limpa, sem mutação
    de um teste vazando para o próximo.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-write-flag-guard-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(REPO_ROOT, self.root, ignore=shutil.ignore_patterns(".git"))
        neutralizar_marcador_host_kanban(self.root)
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()

    def test_documentos_reais_sem_mutacao_passam(self) -> None:
        """Controle negativo: os três documentos reais, do jeito que o T-019
        os deixou, não acionam a guarda nova (nem nenhuma outra). Se isto
        falhar, o defeito é da guarda (falso positivo), não de quem edita os
        arquivos."""
        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 0, output)

    def test_remover_frase_ancora_reprova_nomeando_arquivo(self) -> None:
        """Vermelho 1: sem a frase-âncora, o contrato obrigatório (passo 2a)
        falta e o lint reprova citando o arquivo."""
        for relativo in ARQUIVOS_RELATIVOS:
            with self.subTest(arquivo=relativo):
                arq = self.root / relativo
                original = arq.read_text(encoding="utf-8")
                self.assertIn(ANCORA, original, f"{relativo} não tem a frase-âncora esperada")
                arq.write_text(original.replace(ANCORA, "", 1), encoding="utf-8")

                result, output = run_lint_main(self.root, self.home)

                self.assertEqual(result, 1, output)
                self.assertIn(relativo, output)

                arq.write_text(original, encoding="utf-8")

    def test_write_fora_da_ancora_reprova_mesmo_com_frase_presente(self) -> None:
        """Vermelho 2: a frase-âncora continua no arquivo, mas `--write`
        vazou para uma linha de invocação de verdade — a guarda de contagem
        (passo 2b) tem que reprovar mesmo assim, porque uma checagem que só
        procurasse a presença da frase não pegaria este caso."""
        for relativo, (alvo, substituto) in INJECOES_WRITE.items():
            with self.subTest(arquivo=relativo):
                arq = self.root / relativo
                original = arq.read_text(encoding="utf-8")
                self.assertEqual(
                    original.count(alvo), 1, f"{relativo}: linha de invocação mudou de forma inesperada"
                )
                self.assertIn(ANCORA, original, f"{relativo} não tem a frase-âncora esperada")
                mutado = original.replace(alvo, substituto, 1)
                self.assertIn(ANCORA, mutado, "a mutação também apagou a frase-âncora — teste inválido")
                arq.write_text(mutado, encoding="utf-8")

                result, output = run_lint_main(self.root, self.home)

                self.assertEqual(result, 1, output)
                self.assertIn(relativo, output)
                self.assertIn("--write", output)

                arq.write_text(original, encoding="utf-8")


    def test_grafia_de_hifen_unico_tambem_reprova(self) -> None:
        """A revisão de 2026-09-07 derrubou a versão anterior desta guarda por
        aqui: `-write`, com um hífen só, resolve para a mesma chave booleana no
        parser do Companion e abre `workspace-write` igual. Uma busca pelo
        literal `--write` não via essa ocorrência."""
        relativo, alvo, substituto = INJECAO_HIFEN_UNICO
        arq = self.root / relativo
        original = arq.read_text(encoding="utf-8")
        self.assertEqual(original.count(alvo), 1, f"{relativo}: linha de invocação mudou")
        mutado = original.replace(alvo, substituto, 1)
        self.assertIn(ANCORA, mutado, "a mutação apagou a frase-âncora — teste inválido")
        arq.write_text(mutado, encoding="utf-8")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn(relativo, output)
        self.assertIn("-write", output)

    def test_workspace_write_fora_da_ancora_nao_e_falso_positivo(self) -> None:
        """Controle do lado oposto: `workspace-write` contém a sequência
        `-write` colada a uma letra e aparece nos documentos FORA da âncora
        (descrevendo o sandbox do implementer). A fronteira da regex existe
        para isso — se ela for afrouxada, este teste cai antes de a guarda
        virar ruído em produção."""
        alheio = (self.root / "orq" / "commands" / "elenco.md").read_text(encoding="utf-8")
        sem_ancora = alheio.replace(ANCORA, "")
        self.assertIn(
            "workspace-write",
            sem_ancora,
            "o documento parou de citar workspace-write fora da âncora — o controle perdeu o objeto",
        )

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()
