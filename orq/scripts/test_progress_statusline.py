#!/usr/bin/env python3
"""Testes do segmento do medidor de progresso na statusline do Claude (`progress.py statusline` + `statusline.sh`).

O segmento é uma vista: lê o binding da sessão nativa, carrega o ledger ligado a ele e imprime a MESMA
linha do `show --format segment`. Nunca escolhe "o ledger mais recente", nunca escreve nada e nunca derruba
a barra: sem binding some, com binding ou ledger ruins mostra uma indisponibilidade curta, e sem `jq`,
sem `python3` ou sem o `progress.py` ao lado a barra fica idêntica à anterior ao medidor. Tudo roda em
diretórios temporários; o módulo é independente de `test_progress.py`.
"""

from __future__ import annotations

import builtins
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
CORE = SCRIPTS / "progress.py"
STATUSLINE = SCRIPTS / "statusline.sh"
KANBAN = SCRIPTS / "kanban-status.sh"

RAW_SESSION = "SESSAO-DA-STATUSLINE-3b9d"
BOARD_ACTIVE = "- [~] `T-144` Medidor — nota\n"
HAS_JQ = shutil.which("jq") is not None

_spec = importlib.util.spec_from_file_location("orq_progress_for_statusline", CORE)
core = importlib.util.module_from_spec(_spec)
sys.modules["orq_progress_for_statusline"] = core
_spec.loader.exec_module(core)


def snapshot(root: Path) -> dict:
    """Nome, tamanho, mtime e hash de tudo sob a raiz, diretórios incluídos."""
    result = {}
    for current, directories, files in os.walk(root):
        for name in directories + files:
            path = Path(current) / name
            info = path.lstat()
            digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            result[str(path.relative_to(root))] = (info.st_size, info.st_mtime_ns, digest)
    return result


class StatuslineTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-progress-statusline-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(os.path.realpath(self.tmp.name))
        self.home = self.base / "home"
        self.home.mkdir()

    # ── execução ──────────────────────────────────────────────────────────

    def env(self, **extra) -> dict:
        environment = dict(os.environ)
        environment.update({"HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"})
        environment.update(extra)
        return environment

    def cli(self, *args: str, stdin=None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CORE), *args], input=stdin, capture_output=True, text=True, timeout=60,
            env=self.env(), cwd=self.base, check=False,
        )

    def ok(self, *args: str, stdin=None) -> dict:
        result = self.cli(*args, stdin=stdin)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def install(self, name: str = "instalada", stamped: bool = False, with_core: bool = True) -> Path:
        """Cópia dos scripts fora do plugin, como o `/orq:init` instala; `stamped` repete o carimbo da linha 2."""
        destino = self.base / name
        destino.mkdir()
        for origem in (STATUSLINE, KANBAN) + ((CORE,) if with_core else ()):
            texto = origem.read_text(encoding="utf-8").splitlines(keepends=True)
            if stamped:
                texto.insert(1, f"# orq v0.0.0 — instalado por /orq:init em 2026-10-04; fonte: orq/scripts/{origem.name}. Não editar à mão; re-sync: /orq:init --reinstalar\n")
            (destino / origem.name).write_text("".join(texto), encoding="utf-8")
        return destino

    def bar(self, payload: dict, install: Path, env=None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["sh", str(install / "statusline.sh")], input=json.dumps(payload), capture_output=True, text=True,
            timeout=60, env=env or self.env(), cwd=self.base, check=False,
        )

    # ── cenários ──────────────────────────────────────────────────────────

    def make_front(self, name: str = "frente", board: str = BOARD_ACTIVE) -> Path:
        root = self.base / name
        (root / "memory" / "wiki").mkdir(parents=True)
        (root / "memory" / "wiki" / "KANBAN.md").write_text(board, encoding="utf-8")
        return root

    def card(self, name: str = "frente", board: str = BOARD_ACTIVE, bind: bool = True, session_id: str = RAW_SESSION, plan: bool = True) -> dict:
        root = self.make_front(name, board)
        begun = self.ok(
            "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
            "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "frente-mods", "--host", "claude",
        )
        sc = {"root": root, "ledger": begun["ledger_path"], "owner": begun["session_key"], "session_id": session_id}
        if plan:
            tasks = [{"id": "P01", "title": "Núcleo", "size": "L", "acceptance_ref": "A01"}, {"id": "P02", "title": "Docs", "size": "S", "acceptance_ref": "A02"}]
            data = {"source_ref": "docs/plano.md#passos", "approval_ref": "threads/T-144.md#aprovacao", "tasks": tasks}
            self.ok("plan", "--ledger", sc["ledger"], "--session-key", sc["owner"], "--input", "-", stdin=json.dumps(data))
            self.ok("start", "--ledger", sc["ledger"], "--session-key", sc["owner"], "--task", "P01", "--executor-host", "claude", "--executor-role", "implementer", "--executor-label", "normal")
        if bind:
            sc["binding"] = self.ok("bind", "--ledger", sc["ledger"], "--host", "claude", "--session-id", session_id)["binding_path"]
        return sc

    def payload(self, sc: dict, **extra) -> dict:
        root = str(sc["root"])
        payload = {
            "session_id": sc["session_id"], "transcript_path": str(self.base / "t.jsonl"), "cwd": root,
            "model": {"display_name": "Modelo Teste"}, "workspace": {"current_dir": root, "project_dir": root},
        }
        payload.update(extra)
        return payload

    def segment_of(self, sc: dict) -> str:
        return self.cli("show", "--ledger", sc["ledger"], "--format", "segment").stdout.strip()

    def statusline(self, payload, raw: bool = False, timeout: float = 60) -> subprocess.CompletedProcess:
        """`progress.py statusline`; `raw` manda os bytes como estão (a entrada não precisa ser JSON nem UTF-8)."""
        data = payload if raw else json.dumps(payload).encode("utf-8")
        result = subprocess.run(
            [sys.executable, str(CORE), "statusline", "--host", "claude", "--input", "-"], input=data,
            capture_output=True, timeout=timeout, env=self.env(), cwd=self.base, check=False,
        )
        return subprocess.CompletedProcess(
            result.args, result.returncode, result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
        )


class ProgressStatuslineSubcomandoTest(StatuslineTestCase):
    def test_imprime_so_o_segmento_da_mesma_projecao_do_show(self):
        sc = self.card()
        result = self.statusline(self.payload(sc))
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertEqual(result.stdout, "◎ T-144 · implementação · 0/2 · 0%\n")
        self.assertEqual(result.stdout.strip(), self.segment_of(sc))
        self.ok("done", "--ledger", sc["ledger"], "--session-key", sc["owner"], "--task", "P01", "--evidence-ref", "suite-ok")
        self.assertEqual(self.statusline(self.payload(sc)).stdout.strip(), "◎ T-144 · implementação · 1/2 · 75%")
        self.ok("pause", "--ledger", sc["ledger"], "--session-key", sc["owner"])
        self.assertEqual(self.statusline(self.payload(sc)).stdout.strip(), "◎ T-144 · implementação · 1/2 · 75% · pausado")

    def test_goal_usa_o_nome_do_goal(self):
        root = self.make_front("frente-goal")
        begun = self.ok("begin", "--kind", "goal", "--root", str(root), "--host", "claude")
        self.ok("bind", "--ledger", begun["ledger_path"], "--host", "claude", "--session-id", RAW_SESSION)
        result = self.statusline({"session_id": RAW_SESSION, "cwd": str(root)})
        self.assertEqual(result.stdout.strip(), f"◎ goal {begun['run_id'][:8]} · planejamento · sem plano registrado")

    def test_sem_binding_ou_sem_sessao_ou_sem_medidor_nao_imprime_nada(self):
        sc = self.card()
        outra = self.card("outra-frente", bind=False)
        sem_medidor = self.make_front("sem-medidor")
        casos = {
            "outra sessao": self.payload(sc, session_id="OUTRA-SESSAO"),
            "frente com ledger e sem binding": self.payload(outra),
            "sem session_id": {k: v for k, v in self.payload(sc).items() if k != "session_id"},
            "session_id vazio": self.payload(sc, session_id=""),
            "session_id numerico": self.payload(sc, session_id=42),
            "projeto sem medidor": self.payload({"root": sem_medidor, "session_id": RAW_SESSION}),
            "sem diretorio algum": {"session_id": RAW_SESSION},
        }
        for nome, payload in casos.items():
            with self.subTest(nome):
                result = self.statusline(payload)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_nunca_escolhe_o_ledger_mais_recente_nem_adivinha(self):
        sc = self.card("frente-a", session_id="SESSAO-A")
        recente = self.card("frente-b", bind=False)  # ledger mais novo na mesma máquina, sem ligação com a sessão A
        mesmo_diretorio = self.card("frente-c", bind=False)
        for outro in (recente, mesmo_diretorio):
            self.assertEqual(self.statusline(self.payload(outro, session_id="SESSAO-A")).stdout, "")  # a sessão A não está ligada aqui
        self.assertEqual(self.statusline(self.payload(sc)).stdout.strip(), "◎ T-144 · implementação · 0/2 · 0%")

    def test_o_mesmo_medidor_visto_de_um_subdiretorio_e_pelos_tres_campos_de_diretorio(self):
        sc = self.card()
        sub = sc["root"] / "pacote" / "fundo"
        sub.mkdir(parents=True)
        esperado = "◎ T-144 · implementação · 0/2 · 0%"
        for nome, payload in {
            "cwd no subdiretorio": {"session_id": RAW_SESSION, "cwd": str(sub)},
            "current_dir no subdiretorio": {"session_id": RAW_SESSION, "workspace": {"current_dir": str(sub)}},
            "project_dir da frente": {"session_id": RAW_SESSION, "workspace": {"project_dir": str(sc["root"])}},
            "cwd fora, project_dir dentro": {"session_id": RAW_SESSION, "cwd": str(self.base), "workspace": {"project_dir": str(sc["root"])}},
        }.items():
            with self.subTest(nome):
                self.assertEqual(self.statusline(payload).stdout.strip(), esperado)

    def test_vinculo_ou_ledger_ruins_mostram_indisponibilidade_curta(self):
        sc = self.card()
        binding = Path(sc["binding"])
        ledger = Path(sc["ledger"])
        original_binding, original_ledger = binding.read_bytes(), ledger.read_bytes()
        casos = (
            ("binding corrompido", lambda: binding.write_text("{ quebrado", encoding="utf-8"), "binding-invalido"),
            ("binding de versão desconhecida", lambda: binding.write_text(json.dumps({"schema_version": 9}), encoding="utf-8"), "versao-desconhecida"),
            ("ledger ausente", lambda: ledger.unlink(), "ledger-ausente"),
            ("ledger corrompido", lambda: ledger.write_text("{ quebrado", encoding="utf-8"), "ledger-invalido"),
            ("ledger de outra execução", lambda: binding.write_text(json.dumps({**json.loads(original_binding), "run_id": "00000000-0000-4000-8000-000000000000"}), encoding="utf-8"), "vinculo-obsoleto"),
        )
        for nome, estraga, codigo in casos:
            with self.subTest(nome):
                binding.write_bytes(original_binding)
                ledger.write_bytes(original_ledger)
                estraga()
                result = self.statusline(self.payload(sc))
                self.assertEqual((result.returncode, result.stderr), (0, ""))
                self.assertEqual(result.stdout.strip(), f"◎ medidor indisponível ({codigo})")
                self.assertNotIn("%", result.stdout)  # nunca um percentual inventado
        binding.write_bytes(original_binding)
        ledger.write_bytes(original_ledger)
        self.assertEqual(self.statusline(self.payload(sc)).stdout.strip(), "◎ T-144 · implementação · 0/2 · 0%")

    def test_board_ilegivel_mantem_o_percentual_com_fase_indisponivel(self):
        sc = self.card()
        (sc["root"] / "memory/wiki/KANBAN.md").unlink()
        self.assertEqual(self.statusline(self.payload(sc)).stdout.strip(), "◎ T-144 · fase indisponível · 0/2 · 0%")

    def test_sempre_sai_zero_com_qualquer_entrada(self):
        sc = self.card()
        for nome, bruto in {
            "vazio": b"", "json quebrado": b"{", "lista": b"[]", "texto": b'"x"', "null": b"null", "numero": b"7",
            "utf8 invalido": b"\xff\xfe{", "enorme": b'{"session_id": "' + b"x" * (2 * 1024 * 1024) + b'"}',
            "campos de tipo errado": json.dumps({"session_id": RAW_SESSION, "cwd": 5, "workspace": "x"}).encode(),
            "workspace lista": json.dumps({"session_id": RAW_SESSION, "workspace": []}).encode(),
            "cwd relativo": json.dumps({"session_id": RAW_SESSION, "cwd": "relativo"}).encode(),
        }.items():
            with self.subTest(nome):
                result = self.statusline(bruto, raw=True)
                self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertEqual(self.statusline(self.payload(sc)).returncode, 0)

    def abertos_por(self, funcao):
        """Roda `funcao()` espionando `open` e `os.open`; devolve (resultado, caminhos abertos)."""
        abertos = []
        real_open, real_os_open = builtins.open, os.open

        def espia_open(file, *args, **kwargs):
            abertos.append(str(file))
            return real_open(file, *args, **kwargs)

        def espia_os_open(path, *args, **kwargs):
            abertos.append(str(path))
            return real_os_open(path, *args, **kwargs)

        with mock.patch.object(builtins, "open", espia_open), mock.patch.object(os, "open", espia_os_open):
            resultado = funcao()
        return resultado, abertos

    def alvos_de_fora(self) -> dict:
        pasta = self.base / "fora"
        pasta.mkdir(exist_ok=True)
        fifo = pasta / "ledger.fifo"
        if not fifo.exists():
            os.mkfifo(fifo)
        comum = pasta / "comum.json"
        comum.write_text("NAO-ABRIR", encoding="utf-8")
        outra = self.card("frente-de-fora", bind=False)
        return {"fifo": fifo, "arquivo comum": comum, "ledger de outra frente": Path(outra["ledger"])}

    def test_ledger_do_binding_fora_do_layout_ou_da_frente_nunca_e_aberto(self):
        sc = self.card()
        binding, ledger = Path(sc["binding"]), Path(sc["ledger"])
        original_binding, original_ledger = binding.read_bytes(), ledger.read_bytes()
        kanban = sc["root"] / "memory/wiki/KANBAN.md"
        alvos = self.alvos_de_fora()

        def aponta_binding(alvo):
            binding.write_text(json.dumps({**json.loads(original_binding), "ledger_path": str(alvo)}), encoding="utf-8")

        def troca_ledger(alvo):
            ledger.unlink()
            os.symlink(alvo, ledger)

        casos = []  # (nome, aplica, alvo, código esperado)
        for nome, alvo in alvos.items():
            codigo = "destino-fora-do-root"
            casos.append((f"binding aponta para {nome}", lambda alvo=alvo: aponta_binding(alvo), alvo, codigo))
            casos.append((f"ledger trocado por symlink para {nome}", lambda alvo=alvo: troca_ledger(alvo), alvo, codigo))
        casos.append(("binding aponta para arquivo da frente fora do layout", lambda: aponta_binding(kanban), kanban, "destino-fora-do-layout"))
        casos.append(("ledger trocado por symlink para arquivo da frente fora do layout", lambda: troca_ledger(kanban), kanban, "destino-fora-do-layout"))
        for nome, aplica, alvo, codigo in casos:
            with self.subTest(nome):
                if ledger.is_symlink():
                    ledger.unlink()
                ledger.write_bytes(original_ledger)
                binding.write_bytes(original_binding)
                aplica()
                esperado = f"◎ medidor indisponível ({codigo})"
                if alvo.is_fifo():
                    result = self.statusline(self.payload(sc), timeout=20)  # abrir o FIFO travaria: o timeout derruba o teste
                    self.assertEqual((result.returncode, result.stdout.strip()), (0, esperado))
                    continue
                resultado, abertos = self.abertos_por(lambda: core.statusline_segment(self.payload(sc)))
                self.assertEqual(resultado, esperado)
                self.assertNotIn(os.path.realpath(alvo), [os.path.realpath(a) for a in abertos if a], "a barra abriu o arquivo de fora")
        if ledger.is_symlink():
            ledger.unlink()
        ledger.write_bytes(original_ledger)
        binding.write_bytes(original_binding)
        self.assertEqual(self.statusline(self.payload(sc)).stdout.strip(), "◎ T-144 · implementação · 0/2 · 0%")  # o legítimo segue

    def test_diretorio_de_ledgers_trocado_por_symlink_para_fora_nao_e_aberto(self):
        sc = self.card()
        fora = self.base / "cards-fora"
        cards = Path(sc["ledger"]).parent
        cards.rename(fora)
        os.symlink(fora, cards)
        resultado, abertos = self.abertos_por(lambda: core.statusline_segment(self.payload(sc)))
        self.assertEqual(resultado, "◎ medidor indisponível (destino-fora-do-root)")
        self.assertNotIn(os.path.realpath(fora / Path(sc["ledger"]).name), [os.path.realpath(a) for a in abertos if a])

    def test_falha_inesperada_no_calculo_vira_indisponibilidade_e_nunca_derruba_a_barra(self):
        sc = self.card()
        payload = self.payload(sc)
        with mock.patch.object(core, "build_view", side_effect=RuntimeError("quebrou")):
            self.assertEqual(core.statusline_segment(payload), "◎ medidor indisponível (erro)")
        with mock.patch.object(core, "ledger_board_state", side_effect=core.UnavailableError("sem board", code="board-timeout")):
            self.assertEqual(core.statusline_segment(payload), "◎ medidor indisponível (board-timeout)")
        # e o subcomando, mesmo com a leitura do stdin ou a projeção quebrando, sai 0 e deixa o stdout limpo
        for alvo in ("statusline_segment", "parse_json"):
            with self.subTest(alvo):
                saida, erro = io.StringIO(), io.StringIO()
                with mock.patch.object(core, alvo, side_effect=RuntimeError("quebrou")), contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
                    with mock.patch.object(sys, "stdin", mock.Mock(buffer=io.BytesIO(json.dumps(payload).encode()))):
                        codigo = core.main(["statusline", "--host", "claude", "--input", "-"])
                self.assertEqual((codigo, saida.getvalue(), erro.getvalue()), (0, "", ""))
        self.assertEqual(core.GIT_TIMEOUT_SECONDS, 5.0)  # o ajuste de timeout da barra não vaza para o resto do processo

    def test_so_aceita_o_host_claude_e_entrada_padrao(self):
        self.assertEqual(self.cli("statusline", "--host", "codex", "--input", "-", stdin="{}").returncode, 2)
        self.assertEqual(self.cli("statusline", "--host", "claude", "--input", "arquivo.json", stdin="{}").returncode, 0)  # só '-' é lido; nada a mostrar
        self.assertEqual(self.cli("statusline", "--input", "-", stdin="{}").returncode, 2)

    def test_nao_escreve_nada_nem_cria_diretorio_ou_lock(self):
        sc = self.card()
        antes = snapshot(self.base)
        for payload in (self.payload(sc), self.payload(sc, session_id="outra"), {}):
            self.statusline(payload)
        self.assertEqual(snapshot(self.base), antes)
        sem_medidor = self.make_front("sem-medidor")
        antes = snapshot(sem_medidor)
        self.statusline({"session_id": RAW_SESSION, "cwd": str(sem_medidor)})
        self.assertEqual(snapshot(sem_medidor), antes)
        self.assertFalse((sem_medidor / ".orq").exists())


@unittest.skipUnless(HAS_JQ, "a barra completa precisa de jq")
class ProgressStatuslineBarraTest(StatuslineTestCase):
    def test_a_barra_ganha_o_segmento_no_fim_da_segunda_linha(self):
        sc = self.card()
        barra = self.bar(self.payload(sc), self.install())
        self.assertEqual((barra.returncode, barra.stderr), (0, ""))
        segunda = barra.stdout.split("\n")[1]
        self.assertTrue(segunda.endswith(" | ◎ T-144 · implementação · 0/2 · 0%"), segunda)
        self.assertIn("📋", barra.stdout)  # o board segue aparecendo, antes do segmento
        self.assertIn("Modelo Teste", barra.stdout)

    def test_sem_binding_a_barra_e_identica_a_de_uma_instalacao_sem_o_progress_py(self):
        sc = self.card(bind=False)
        com = self.bar(self.payload(sc), self.install("com-core"))
        sem = self.bar(self.payload(sc), self.install("sem-core", with_core=False))
        self.assertEqual((com.returncode, com.stdout), (0, sem.stdout))
        self.assertNotIn("◎", com.stdout)

    def test_sem_o_script_vizinho_ou_sem_python3_a_barra_fica_identica_a_de_hoje(self):
        sc = self.card()
        referencia = self.bar(self.payload(sc), self.install("sem-core", with_core=False))  # barra anterior ao medidor
        self.assertEqual(referencia.returncode, 0)
        self.assertNotIn("◎", referencia.stdout)
        com_core = self.install("com-core")
        # sem python3 no PATH: o segmento some, e o resto da barra continua o mesmo que a referência faria nas mesmas condições
        ferramentas = self.base / "sem-python"
        ferramentas.mkdir()
        for comando in ("sh", "cat", "jq", "git", "awk", "date", "basename", "dirname", "grep", "head", "sed", "wc", "tr", "printf", "env", "stat", "sort", "uniq", "cut", "xargs", "find", "readlink", "pwd"):
            origem = shutil.which(comando)
            if origem:
                (ferramentas / comando).symlink_to(origem)
        env = self.env(PATH=str(ferramentas))
        sem_python = self.bar(self.payload(sc), com_core, env=env)
        referencia_sem_python = self.bar(self.payload(sc), self.install("ref-sem-python", with_core=False), env=env)
        self.assertEqual(sem_python.returncode, 0, sem_python.stderr)
        self.assertEqual(sem_python.stdout, referencia_sem_python.stdout)
        self.assertNotIn("◎", sem_python.stdout)

    def test_sem_jq_a_degradacao_para_o_board_continua_a_mesma_com_ou_sem_o_script(self):
        sc = self.card()
        ferramentas = self.base / "sem-jq"
        ferramentas.mkdir()
        for comando in ("sh", "cat", "grep", "head", "sed", "dirname"):  # as mesmas ferramentas do teste existente do ramo sem jq
            origem = shutil.which(comando)
            self.assertIsNotNone(origem, comando)
            (ferramentas / comando).symlink_to(origem)
        env = self.env(PATH=str(ferramentas))
        com = self.bar(self.payload(sc), self.install("com-core"), env=env)
        sem = self.bar(self.payload(sc), self.install("sem-core", with_core=False), env=env)
        self.assertEqual(com.returncode, 0, com.stderr)
        self.assertEqual(com.stdout, sem.stdout)
        self.assertNotIn("◎", com.stdout)  # a degradação é só o board, como antes

    def test_copia_instalada_fora_do_cache_com_carimbo_mostra_o_segmento(self):
        sc = self.card()
        instalada = self.install("instalada-com-carimbo", stamped=True)
        self.assertTrue((instalada / "progress.py").read_text(encoding="utf-8").splitlines()[1].startswith("# orq v"))
        barra = self.bar(self.payload(sc), instalada)
        self.assertEqual(barra.returncode, 0, barra.stderr)
        self.assertTrue(barra.stdout.split("\n")[1].endswith(" | ◎ T-144 · implementação · 0/2 · 0%"))  # a fase vem do board: o kanban-status.sh vizinho foi achado
        self.assertNotIn(str(SCRIPTS), self.bar(self.payload(sc), instalada).stdout)  # e nada aponta para dentro do plugin

    def test_payload_sem_session_id_e_outra_sessao_nao_mostram_segmento_na_barra(self):
        sc = self.card()
        instalada = self.install()
        for payload in (
            {k: v for k, v in self.payload(sc).items() if k != "session_id"},
            self.payload(sc, session_id="OUTRA-SESSAO"),
        ):
            barra = self.bar(payload, instalada)
            self.assertEqual(barra.returncode, 0)
            self.assertNotIn("◎", barra.stdout)

    def test_o_mesmo_medidor_visto_de_um_subdiretorio_na_barra(self):
        sc = self.card()
        sub = sc["root"] / "pacote" / "fundo"
        sub.mkdir(parents=True)
        payload = self.payload(sc, cwd=str(sub), workspace={"current_dir": str(sub), "project_dir": str(sub)})
        barra = self.bar(payload, self.install())
        self.assertIn("◎ T-144 · implementação · 0/2 · 0%", barra.stdout)

    def test_diretorio_do_payload_que_e_alias_de_um_subdiretorio_da_frente_acha_o_medidor(self):
        sc = self.card()
        sub = sc["root"] / "pacote" / "fundo"
        sub.mkdir(parents=True)
        alias = self.base / "atalho"
        os.symlink(sub, alias)  # o pai lexical do alias (`self.base`) não tem .orq; o físico (a frente) tem
        instalada = self.install()
        for nome, payload in {
            "cwd": self.payload(sc, cwd=str(alias), workspace={}),
            "current_dir": self.payload(sc, cwd=None, workspace={"current_dir": str(alias)}),
            "project_dir": self.payload(sc, cwd=None, workspace={"project_dir": str(alias)}),
            "os três": self.payload(sc, cwd=str(alias), workspace={"current_dir": str(alias), "project_dir": str(alias)}),
        }.items():
            with self.subTest(nome):
                self.assertEqual(self.statusline(payload).stdout.strip(), "◎ T-144 · implementação · 0/2 · 0%")  # o CLI já achava
                barra = self.bar(payload, instalada)
                self.assertEqual(barra.returncode, 0, barra.stderr)
                self.assertIn("◎ T-144 · implementação · 0/2 · 0%", barra.stdout)  # e a barra tem de concordar com o CLI

    def test_alias_para_diretorio_sem_medidor_nao_chama_o_python_nem_quebra(self):
        sem_medidor = self.make_front("sem-medidor")
        alias = self.base / "atalho-sem-medidor"
        os.symlink(sem_medidor, alias)
        pendurado = self.base / "atalho-pendurado"
        os.symlink(self.base / "nao-existe", pendurado)
        instalada = self.install()
        (instalada / "progress.py").write_text("import os\nopen(os.environ['ORQ_SENTINELA'], 'a').write('chamado')\n", encoding="utf-8")
        marca = self.base / "sentinela.txt"
        for diretorio in (alias, pendurado):
            barra = self.bar({"session_id": RAW_SESSION, "cwd": str(diretorio)}, instalada, env=self.env(ORQ_SENTINELA=str(marca)))
            self.assertEqual(barra.returncode, 0, barra.stderr)
        self.assertFalse(marca.exists())

    def test_vinculo_ruim_aparece_na_barra_como_indisponibilidade_sem_derrubar_o_resto(self):
        sc = self.card()
        Path(sc["binding"]).write_text("{ quebrado", encoding="utf-8")
        barra = self.bar(self.payload(sc), self.install())
        self.assertEqual(barra.returncode, 0)
        self.assertIn("◎ medidor indisponível (binding-invalido)", barra.stdout)
        self.assertIn("Modelo Teste", barra.stdout)

    def test_a_barra_nao_escreve_nada(self):
        sc = self.card()
        instalada = self.install()
        antes = snapshot(self.base)
        self.bar(self.payload(sc), instalada)
        self.bar(self.payload(sc, session_id="outra"), instalada)
        self.assertEqual(snapshot(self.base), antes)

    def test_projeto_sem_medidor_nao_paga_a_chamada_do_python(self):
        """O sh só chama o python quando há `.orq/progress/v1/sessions/` no cwd ou acima."""
        sem_medidor = self.make_front("sem-medidor")
        instalada = self.install()
        (instalada / "progress.py").write_text("import os\nopen(os.environ['ORQ_SENTINELA'], 'a').write('chamado')\n", encoding="utf-8")
        marca = self.base / "sentinela.txt"
        self.bar({"session_id": RAW_SESSION, "cwd": str(sem_medidor), "workspace": {"project_dir": str(sem_medidor)}}, instalada, env=self.env(ORQ_SENTINELA=str(marca)))
        self.assertFalse(marca.exists(), "o progress.py foi chamado num projeto sem medidor")
        com_medidor = self.card()
        (instalada / "progress.py").write_text("import os\nopen(os.environ['ORQ_SENTINELA'], 'a').write('chamado')\n", encoding="utf-8")
        self.bar(self.payload(com_medidor), instalada, env=self.env(ORQ_SENTINELA=str(marca)))
        self.assertTrue(marca.exists())


if __name__ == "__main__":
    unittest.main()
