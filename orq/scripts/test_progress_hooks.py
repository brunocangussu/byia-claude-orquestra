#!/usr/bin/env python3
"""Testes do adaptador consultivo de hooks do medidor de progresso (`progress-hook.py`).

O adaptador só lembra, nunca decide: `SessionStart` entrega a chave da sessão nativa e `PostToolUse`
conta eventos de uma sessão vinculada que ainda não registrou plano. Os testes provam o contrato
consultivo (sempre exit 0, nunca bloqueio), o isolamento entre sessões e hosts, a deduplicação, a
leitura mínima do payload (sem transcript, sem conteúdo de ferramenta) e a coexistência com o
`context-guard` no `hooks.json`. Tudo roda em diretórios temporários; este módulo é independente de
`test_progress.py` e repete só o necessário do seu andaime.
"""

from __future__ import annotations

import builtins
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
CORE = SCRIPTS / "progress.py"
HOOK = SCRIPTS / "progress-hook.py"
PLUGIN = SCRIPTS.parent
HOOKS_JSON = PLUGIN / "hooks" / "hooks.json"

_spec = importlib.util.spec_from_file_location("orq_progress_for_hooks", CORE)
core = importlib.util.module_from_spec(_spec)
sys.modules["orq_progress_for_hooks"] = core
_spec.loader.exec_module(core)

BOARD_ACTIVE = "- [~] `T-144` Medidor — nota\n"
SOURCES = ("startup", "resume", "clear", "compact", "fork")
HOSTS = ("claude", "codex")
RAW_SESSION = "SESSAO-BRUTA-DO-HOST-7c1e"
SECRET = "SEGREDO-DA-FERRAMENTA-4471"
FORBIDDEN_WORDS = ("block", "deny", "continue", "decision", "stopreason", "suppressoutput")

# Os seis grupos do context-guard como estavam antes do medidor: a coexistência exige igualdade exata.
GUARD_GROUPS = {
    "PostToolUse": {
        "hooks": [
            {
                "type": "command",
                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"',
                "timeout": 5,
                "statusMessage": "Verificando janela de contexto",
                "additionalContextLimit": 300,
            }
        ]
    },
    "Stop": {
        "hooks": [
            {
                "type": "command",
                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"',
                "timeout": 5,
                "statusMessage": "Verificando checkpoint preventivo",
            }
        ]
    },
    "UserPromptSubmit": {
        "hooks": [
            {
                "type": "command",
                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"',
                "timeout": 5,
                "statusMessage": "Protegendo contexto antes do trabalho",
                "additionalContextLimit": 300,
            }
        ]
    },
    "SessionStart": {
        "matcher": "^(clear|compact)$",
        "hooks": [
            {
                "type": "command",
                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"',
                "timeout": 5,
                "statusMessage": "Reidratando memória do Orquestra",
                "additionalContextLimit": 300,
            }
        ],
    },
    "PreCompact": {
        "matcher": "^(manual|auto)$",
        "hooks": [
            {
                "type": "command",
                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"',
                "timeout": 5,
                "statusMessage": "Registrando contingência de compactação",
            }
        ],
    },
    "PostCompact": {
        "matcher": "^(manual|auto)$",
        "hooks": [
            {
                "type": "command",
                "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"',
                "timeout": 5,
                "statusMessage": "Recuperando após compactação",
            }
        ],
    },
}


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


class Scenario:
    """Uma frente com ledger aberto e uma sessão nativa vinculada."""

    def __init__(self, root: Path, ledger: str, owner_key: str, host: str, session_id: str, kind: str) -> None:
        self.root, self.ledger, self.owner_key = root, ledger, owner_key
        self.host, self.session_id, self.kind = host, session_id, kind
        self.key = core.derive_session_key(host, session_id)
        self.binding_path = root / ".orq/progress/v1/sessions" / f"{self.key}.json"

    def binding(self) -> dict:
        return json.loads(self.binding_path.read_text(encoding="utf-8"))


class HookTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-progress-hooks-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(os.path.realpath(self.tmp.name))
        self.home = self.base / "home"
        self.home.mkdir()
        self.systmp = self.base / "systmp"
        self.systmp.mkdir()
        self.counter = 0

    # ── ambiente e execução ────────────────────────────────────────────────

    def env(self, host=None, **extra) -> dict:
        """Ambiente do host, sem herdar o do desenvolvedor: `PLUGIN_ROOT` é do Codex, `CLAUDE_PLUGIN_ROOT` do Claude."""
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in ("PLUGIN_ROOT", "CLAUDE_PLUGIN_ROOT", "PLUGIN_DATA", "CLAUDE_PLUGIN_DATA")
        }
        environment.update({"HOME": str(self.home), "TMPDIR": str(self.systmp), "PYTHONDONTWRITEBYTECODE": "1"})
        if host == "claude":
            environment["CLAUDE_PLUGIN_ROOT"] = str(PLUGIN)
        elif host == "codex":
            environment["PLUGIN_ROOT"] = str(PLUGIN)
        environment.update(extra)
        return environment

    def cli(self, *args: str, env=None, stdin=None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CORE), *args], input=stdin, capture_output=True, text=True, timeout=60,
            env=env or self.env(), cwd=self.base, check=False,
        )

    def ok(self, *args: str, stdin=None) -> dict:
        result = self.cli(*args, stdin=stdin)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def run_hook(self, payload, host="claude", env=None, script: Path = HOOK, timeout: float = 60) -> subprocess.CompletedProcess:
        data = payload if isinstance(payload, (bytes, str)) else json.dumps(payload)
        return subprocess.run(
            [sys.executable, str(script)], input=data if isinstance(data, bytes) else data.encode("utf-8"),
            capture_output=True, timeout=timeout, env=env or self.env(host), cwd=self.base, check=False,
        )

    @staticmethod
    def text(result: subprocess.CompletedProcess) -> str:
        return result.stdout.decode("utf-8")

    # ── cenários ──────────────────────────────────────────────────────────

    def make_front(self, name: str = "frente", board: str = BOARD_ACTIVE, git: bool = False) -> Path:
        root = self.base / name
        (root / "memory" / "wiki").mkdir(parents=True)
        if board is not None:
            (root / "memory" / "wiki" / "KANBAN.md").write_text(board, encoding="utf-8")
        if git:
            self.git(root, "init", "-q")
            self.git(root, "add", "-A")
            self.assertEqual(self.git(root, "commit", "-q", "-m", "board").returncode, 0)
        return root

    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        environment = self.env(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
        for inherited in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            environment.pop(inherited, None)
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=environment, check=False)

    def scenario(self, kind="card", host="claude", session_id=RAW_SESSION, board=BOARD_ACTIVE, git=False, name="frente") -> Scenario:
        root = self.make_front(name, board, git)
        if kind == "card":
            begun = self.ok(
                "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
                "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "frente-mods", "--host", host,
            )
        else:
            begun = self.ok("begin", "--kind", "goal", "--root", str(root), "--host", host)
        sc = Scenario(root, begun["ledger_path"], begun["session_key"], host, session_id, kind)
        self.ok("bind", "--ledger", sc.ledger, "--host", host, "--session-id", session_id)
        return sc

    def scenario_sem_bind(self, kind="goal", host="claude", session_id=RAW_SESSION, board=BOARD_ACTIVE, git=False, name="frente") -> Scenario:
        """A frente depois do `begin`, antes de qualquer `bind`: a sessão que abriu o medidor ainda não foi vinculada."""
        root = self.make_front(name, board, git)
        if kind == "card":
            begun = self.ok(
                "begin", "--kind", "card", "--root", str(root), "--board", str(root / "memory/wiki/KANBAN.md"),
                "--thread-root", str(root / "memory/wiki"), "--card", "T-144", "--front", "frente-mods", "--host", host,
            )
        else:
            begun = self.ok("begin", "--kind", "goal", "--root", str(root), "--host", host)
        return Scenario(root, begun["ledger_path"], begun["session_key"], host, session_id, kind)

    def register_plan(self, sc: Scenario) -> None:
        data = {"tasks": [{"id": "P01", "title": "Passo", "size": "M", "acceptance_ref": "A01"}]}
        if sc.kind == "card":
            data.update(source_ref="docs/plano.md#passos", approval_ref="threads/T-144.md#aprovacao")
        self.ok("plan", "--ledger", sc.ledger, "--session-key", sc.owner_key, "--input", "-", stdin=json.dumps(data))

    # ── payloads ──────────────────────────────────────────────────────────

    def post(self, sc: Scenario, n: int, host=None, **extra) -> dict:
        host = host or sc.host
        event = {
            "session_id": sc.session_id,
            "transcript_path": str(self.base / "transcript-inexistente.jsonl"),
            "cwd": str(sc.root),
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_use_id": f"toolu_{n:03d}" if host == "claude" else f"call_{n:03d}",
            "tool_input": {"command": f"{SECRET}-entrada-{n}"},
            "tool_response": {"stdout": f"{SECRET}-saida-{n}"},
        }
        if host == "codex":
            event["turn_id"] = "turn-001"
        event.update(extra)
        return event

    def session_start(self, sc: Scenario, source: str, host=None, **extra) -> dict:
        event = {
            "session_id": sc.session_id,
            "transcript_path": str(self.base / "transcript-inexistente.jsonl"),
            "cwd": str(sc.root),
            "hook_event_name": "SessionStart",
            "source": source,
        }
        event.update(extra)
        return event

    # ── asserções ─────────────────────────────────────────────────────────

    def assert_consultivo(self, result: subprocess.CompletedProcess) -> dict | None:
        """Exit 0, stderr vazio e, se houver saída, só contexto adicional — nunca bloqueio, negação ou continuação."""
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        out = self.text(result)
        if not out:
            return None
        payload = json.loads(out)
        self.assertEqual(set(payload), {"hookSpecificOutput"})
        self.assertEqual(set(payload["hookSpecificOutput"]), {"hookEventName", "additionalContext"})
        lowered = out.lower()
        for word in FORBIDDEN_WORDS:
            self.assertNotIn(word, lowered)
        self.assertLessEqual(len(payload["hookSpecificOutput"]["additionalContext"].encode("utf-8")), 300)
        return payload["hookSpecificOutput"]

    def silent(self, result: subprocess.CompletedProcess) -> None:
        self.assertIsNone(self.assert_consultivo(result))
        self.assertEqual(result.stdout, b"")

    def feed(self, sc: Scenario, count: int, start: int = 1, host=None, **extra) -> list:
        return [self.run_hook(self.post(sc, n, host, **extra), host or sc.host) for n in range(start, start + count)]

    def hold_binding_lock(self, sc: Scenario, seconds: float) -> subprocess.Popen:
        holder = subprocess.Popen(
            [sys.executable, "-c",
             "import sys,time\nimport importlib.util\n"
             "s=importlib.util.spec_from_file_location('p',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
             "from pathlib import Path\nwith m.ledger_lock(Path(sys.argv[2])):\n print('preso',flush=True)\n time.sleep(float(sys.argv[3]))\n",
             str(CORE), str(sc.binding_path), str(seconds)],
            stdout=subprocess.PIPE, text=True, env=self.env(),
        )
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), "preso")
        return holder


class ProgressHookLembreteTest(HookTestCase):
    def test_quarto_evento_elegivel_emite_um_lembrete_e_o_quinto_nao_repete(self):
        for host in HOSTS:
            for kind in ("card", "goal"):
                with self.subTest(host=host, kind=kind):
                    sc = self.scenario(kind, host, name=f"frente-{host}-{kind}")
                    results = self.feed(sc, 6)
                    for index, result in enumerate(results, 1):
                        output = self.assert_consultivo(result)
                        if index == 4:
                            self.assertEqual(output["hookEventName"], "PostToolUse")
                            self.assertIn("`plan`", output["additionalContext"])
                            self.assertIn("consultivo", output["additionalContext"])
                        else:
                            self.assertIsNone(output, f"evento {index} não deveria emitir")
                    binding = sc.binding()
                    self.assertEqual((binding["calls_without_plan"], binding["nudged"]), (4, True))

    def test_registrar_o_plano_interrompe_o_lembrete(self):
        for kind in ("card", "goal"):
            with self.subTest(kind=kind):
                sc = self.scenario(kind, name=f"frente-{kind}")
                for result in self.feed(sc, 3):
                    self.silent(result)
                self.register_plan(sc)
                for result in self.feed(sc, 4, start=4):
                    self.silent(result)
                binding = sc.binding()
                self.assertEqual((binding["calls_without_plan"], binding["nudged"]), (3, False))

    def test_planning_gate_pausa_encerramento_e_board_ilegivel_nunca_cobram(self):
        board_file = lambda sc: sc.root / "memory/wiki/KANBAN.md"  # noqa: E731
        casos = {
            "planning [>]": "- [>] `T-144` Medidor — n\n",
            "gate [!]": "- [!] `T-144` Medidor — n\n",
            "validate [?]": "- [?] `T-144` Medidor — n\n",
            "done [x]": "- [x] `T-144` Medidor — n\n",
            "backlog [ ]": "- [ ] `T-144` Medidor — n\n",
            "card ausente": "- [~] `T-999` Outro — n\n",
        }
        for nome, board in casos.items():
            with self.subTest(nome):
                sc = self.scenario(name=f"frente-{abs(hash(nome))}")
                board_file(sc).write_text(board, encoding="utf-8")
                for result in self.feed(sc, 6):
                    self.silent(result)
                self.assertEqual(sc.binding()["calls_without_plan"], 0)
        with self.subTest("board sumiu"):
            sc = self.scenario(name="frente-sem-board")
            board_file(sc).unlink()
            for result in self.feed(sc, 5):
                self.silent(result)
            self.assertEqual(sc.binding()["calls_without_plan"], 0)
        with self.subTest("pausado e retomado"):
            sc = self.scenario(name="frente-pausa")
            self.ok("pause", "--ledger", sc.ledger, "--session-key", sc.owner_key)
            for result in self.feed(sc, 5):
                self.silent(result)
            self.assertEqual(sc.binding()["calls_without_plan"], 0)
            self.ok("resume", "--ledger", sc.ledger, "--session-key", sc.owner_key)  # a prova de que a configuração conta
            outputs = [self.assert_consultivo(result) for result in self.feed(sc, 4, start=10)]
            self.assertEqual([item is not None for item in outputs], [False, False, False, True])
        with self.subTest("encerrado"):
            sc = self.scenario(name="frente-encerrada")
            self.ok("close", "--ledger", sc.ledger, "--session-key", sc.owner_key, "--outcome", "cancelled", "--evidence-ref", "t#c")
            for result in self.feed(sc, 5):
                self.silent(result)
            self.assertEqual(sc.binding()["calls_without_plan"], 0)

    def test_sessao_sem_binding_e_frente_sem_medidor_nao_cobram(self):
        sc = self.scenario()
        antes_binding = sc.binding_path.read_bytes()
        outra = Scenario(sc.root, sc.ledger, sc.owner_key, "claude", "OUTRA-SESSAO", "card")  # só para derivar a chave
        resultados = self.feed(outra, 6)
        self.assertEqual(sum(1 for r in resultados if r.stdout), 1)  # só o anúncio da chave (C2), uma vez; nunca o lembrete de plano
        for result in resultados:
            self.assertNotIn(b"`plan`", result.stdout)
        self.assertEqual(sc.binding_path.read_bytes(), antes_binding)  # o binding de outra sessão não é tocado
        self.assertFalse((sc.root / ".orq/progress/v1/sessions" / f"{outra.key}.json").exists())  # e nada vira binding sozinho
        sem_medidor = self.make_front("sem-medidor")
        isolada = Scenario(sem_medidor, sc.ledger, sc.owner_key, "claude", RAW_SESSION, "card")
        for result in self.feed(isolada, 6):
            self.silent(result)
        self.assertEqual(sorted(p.name for p in sem_medidor.iterdir()), ["memory"])  # nem .orq
        outro_host = self.feed(sc, 6, host="codex")  # o mesmo ID bruto em outro host é outra chave: sem binding
        self.assertEqual(sum(1 for r in outro_host if r.stdout), 1)
        for result in outro_host:
            self.assertNotIn(b"`plan`", result.stdout)
        self.assertEqual(sc.binding()["calls_without_plan"], 0)

    def test_sobe_de_subdiretorios_ate_a_frente_do_binding(self):
        sc = self.scenario()
        sub = sc.root / "pacote" / "fundo"
        sub.mkdir(parents=True)
        outputs = [self.assert_consultivo(result) for result in self.feed(sc, 4, cwd=str(sub))]
        self.assertEqual([o is not None for o in outputs], [False, False, False, True])
        self.assertEqual(sc.binding()["calls_without_plan"], 4)

    def test_eventos_de_duas_sessoes_e_dois_hosts_nao_se_contaminam(self):
        one = self.scenario("goal", "claude", "SESSAO-A", name="frente-a")
        two = self.scenario("goal", "codex", "SESSAO-B", name="frente-b")
        self.feed(one, 2)
        self.feed(two, 3)
        self.assertEqual((one.binding()["calls_without_plan"], two.binding()["calls_without_plan"]), (2, 3))
        self.assertFalse(one.binding()["nudged"] or two.binding()["nudged"])

    def test_subagente_e_ignorado(self):
        for host in HOSTS:
            with self.subTest(host=host):
                sc = self.scenario("goal", host, name=f"frente-{host}")
                for result in self.feed(sc, 6, agent_id="agent-sub-01", agent_type="Explore"):
                    self.silent(result)
                self.assertEqual(sc.binding()["calls_without_plan"], 0)
                self.silent(self.run_hook(self.post(sc, 90, agent_id=""), host))  # agent_id vazio não é subagente: conta
                self.assertEqual(sc.binding()["calls_without_plan"], 1)

    def test_concorrencia_conta_exatamente_quatro_e_emite_um_unico_lembrete(self):
        sc = self.scenario("goal")
        procs = [
            subprocess.Popen(
                [sys.executable, str(HOOK)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=self.env("claude"), cwd=self.base,
            )
            for _ in range(8)
        ]
        for n, proc in enumerate(procs, 1):  # todos recebem o payload antes de qualquer um terminar
            proc.stdin.write(json.dumps(self.post(sc, n)).encode("utf-8"))
            proc.stdin.close()
        outs = []
        for proc in procs:
            out, err = proc.stdout.read(), proc.stderr.read()
            self.assertEqual((proc.wait(timeout=60), err), (0, b""))
            proc.stdout.close()
            proc.stderr.close()
            outs.append(out)
        binding = sc.binding()
        self.assertEqual(sum(1 for out in outs if out), 1)
        self.assertEqual((binding["nudged"], binding["calls_without_plan"]), (True, 4))
        self.assertEqual(sorted(p.name for p in sc.binding_path.parent.iterdir()), [sc.binding_path.name])  # nenhum temporário


class ProgressHookDeduplicacaoTest(HookTestCase):
    def test_entrega_duplicada_simultanea_conta_uma_vez(self):
        for host in HOSTS:
            with self.subTest(host=host):
                sc = self.scenario("goal", host, name=f"frente-{host}")
                payload = json.dumps(self.post(sc, 1)).encode("utf-8")
                procs = [
                    subprocess.Popen(
                        [sys.executable, str(HOOK)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=self.env(host), cwd=self.base,
                    )
                    for _ in range(6)
                ]
                for proc in procs:
                    proc.stdin.write(payload)
                    proc.stdin.close()
                for proc in procs:
                    out, err = proc.stdout.read(), proc.stderr.read()
                    self.assertEqual((proc.wait(timeout=60), out, err), (0, b"", b""))
                    proc.stdout.close()
                    proc.stderr.close()
                self.assertEqual(sc.binding()["calls_without_plan"], 1)

    def test_claude_deduplica_por_sessao_ferramenta_e_evento(self):
        sc = self.scenario("goal", "claude")
        payload = self.post(sc, 1)
        for _ in range(3):
            self.silent(self.run_hook(payload))
        self.assertEqual(sc.binding()["calls_without_plan"], 1)
        self.silent(self.run_hook(self.post(sc, 2)))  # outra ferramenta conta
        self.assertEqual(sc.binding()["calls_without_plan"], 2)
        self.silent(self.run_hook(self.post(sc, 2, turn_id="turn-xyz")))  # turn_id não faz parte da chave do Claude
        self.assertEqual(sc.binding()["calls_without_plan"], 2)

    def test_codex_deduplica_por_sessao_turno_ferramenta_e_evento(self):
        sc = self.scenario("goal", "codex")
        payload = self.post(sc, 1)
        for _ in range(3):
            self.silent(self.run_hook(payload, "codex"))
        self.assertEqual(sc.binding()["calls_without_plan"], 1)
        self.silent(self.run_hook(self.post(sc, 1, turn_id="turn-002"), "codex"))  # mesmo tool_use_id em outro turno conta
        self.assertEqual(sc.binding()["calls_without_plan"], 2)

    def test_so_o_hash_vai_para_o_binding_e_nunca_o_id_bruto(self):
        for host in HOSTS:
            with self.subTest(host=host):
                sc = self.scenario("goal", host, name=f"frente-{host}")
                self.silent(self.run_hook(self.post(sc, 7), host))
                texto = sc.binding_path.read_text(encoding="utf-8")
                ids = sc.binding()["recent_event_ids"]
                self.assertEqual(len(ids), 1)
                self.assertRegex(ids[0], r"^[0-9a-f]{64}$")
                for bruto in (RAW_SESSION, "toolu_007", "call_007", "turn-001", SECRET):
                    self.assertNotIn(bruto, texto)
                for current, directories, files in os.walk(sc.root):  # nem em outro arquivo qualquer
                    for name in files:
                        self.assertNotIn(RAW_SESSION.encode(), (Path(current) / name).read_bytes(), name)
                        self.assertNotIn(RAW_SESSION, name)

    def test_sem_identificador_a_contagem_e_por_entrega(self):
        for host in HOSTS:
            with self.subTest(host=host):
                sc = self.scenario("goal", host, name=f"frente-{host}")
                for _ in range(3):
                    event = self.post(sc, 1)
                    del event["tool_use_id"]
                    self.silent(self.run_hook(event, host))
                binding = sc.binding()
                self.assertEqual((binding["calls_without_plan"], binding["recent_event_ids"]), (3, []))

    def test_codex_sem_turn_id_tambem_conta_por_entrega(self):
        sc = self.scenario("goal", "codex")
        event = self.post(sc, 1)
        del event["turn_id"]
        for _ in range(2):
            self.silent(self.run_hook(event, "codex"))
        self.assertEqual(sc.binding()["calls_without_plan"], 2)

    def test_a_janela_de_ids_recentes_tem_teto_de_128_e_descarta_os_mais_antigos(self):
        sc = self.scenario("goal")
        document = sc.binding()
        document["recent_event_ids"] = [f"{i:064x}" for i in range(core.MAX_RECENT_EVENTS)]
        sc.binding_path.write_text(json.dumps(document), encoding="utf-8")
        self.silent(self.run_hook(self.post(sc, 1)))
        ids = sc.binding()["recent_event_ids"]
        self.assertEqual(len(ids), core.MAX_RECENT_EVENTS)
        self.assertEqual(ids[0], f"{1:064x}")  # o mais antigo saiu
        self.assertEqual(sc.binding()["calls_without_plan"], 1)


class ProgressHookAnuncioTest(HookTestCase):
    """A sessão que roda o `begin` já passou do SessionStart: o primeiro PostToolUse anuncia a chave nativa, uma vez."""

    def marcador(self, sc: Scenario) -> Path:
        return sc.root / ".orq/progress/v1/sessions" / f".anunciada-{sc.key}.json"

    def test_a_primeira_sessao_recebe_a_chave_no_primeiro_posttooluse_depois_do_begin_e_nao_repete(self):
        for host in HOSTS:
            for kind in ("card", "goal"):
                with self.subTest(host=host, kind=kind):
                    sc = self.scenario_sem_bind(kind, host, name=f"frente-{host}-{kind}")
                    self.assertFalse(self.marcador(sc).exists())
                    primeiro = self.run_hook(self.post(sc, 1), host)
                    output = self.assert_consultivo(primeiro)
                    self.assertEqual(output["hookEventName"], "PostToolUse")
                    contexto = output["additionalContext"]
                    self.assertIn(sc.key, contexto)
                    self.assertIn(f"bind --host {host} --native-key", contexto)
                    self.assertIn("chave de dono", contexto)
                    self.assertNotIn(RAW_SESSION, self.text(primeiro))
                    self.assertTrue(self.marcador(sc).is_file())
                    for result in self.feed(sc, 5, start=2):  # nunca repete, nem no 2º evento nem depois
                        self.silent(result)
                    self.assertFalse(sc.binding_path.exists())  # anunciar não vincula

    def test_o_texto_do_anuncio_e_o_do_session_start(self):
        sc = self.scenario_sem_bind()
        anuncio = self.assert_consultivo(self.run_hook(self.post(sc, 1)))["additionalContext"]
        inicio = self.assert_consultivo(self.run_hook(self.session_start(sc, "startup")))["additionalContext"]
        self.assertEqual(anuncio, inicio)

    def test_com_binding_nao_anuncia_e_nao_cria_marcador(self):
        for host in HOSTS:
            with self.subTest(host=host):
                sc = self.scenario("goal", host, name=f"frente-{host}")
                for result in self.feed(sc, 3):
                    self.silent(result)
                self.assertFalse(self.marcador(sc).exists())

    def test_subagente_nao_anuncia_e_a_sessao_principal_ainda_anuncia_depois(self):
        sc = self.scenario_sem_bind()
        for result in self.feed(sc, 3, agent_id="agent-sub-01"):
            self.silent(result)
        self.assertFalse(self.marcador(sc).exists())
        self.assertIsNotNone(self.assert_consultivo(self.run_hook(self.post(sc, 9))))

    def test_sem_medidor_nada_e_anunciado_nem_criado(self):
        raiz = self.make_front("sem-medidor")
        sc = Scenario(raiz, "/x", "a" * 64, "claude", RAW_SESSION, "goal")
        for result in self.feed(sc, 3):
            self.silent(result)
        self.assertEqual(sorted(p.name for p in raiz.iterdir()), ["memory"])

    def test_cada_sessao_tem_o_seu_anuncio_e_o_marcador_nao_guarda_id_bruto(self):
        um = self.scenario_sem_bind(session_id="SESSAO-UM")
        dois = Scenario(um.root, um.ledger, um.owner_key, "claude", "SESSAO-DOIS", "goal")
        for sc in (um, dois):
            self.assertIn(sc.key, self.assert_consultivo(self.run_hook(self.post(sc, 1)))["additionalContext"])
            self.silent(self.run_hook(self.post(sc, 2)))
        for sc, bruto in ((um, "SESSAO-UM"), (dois, "SESSAO-DOIS")):
            self.assertTrue(self.marcador(sc).is_file())
            for current, directories, files in os.walk(sc.root):
                for name in files:
                    self.assertNotIn(bruto.encode(), (Path(current) / name).read_bytes(), name)
                    self.assertNotIn(bruto, name)
        for current, directories, files in os.walk(sc.root):  # nem conteúdo de ferramenta
            for name in files:
                self.assertNotIn(SECRET.encode(), (Path(current) / name).read_bytes(), name)

    def test_depois_do_bind_a_contagem_do_lembrete_segue_normal(self):
        sc = self.scenario_sem_bind()
        self.assert_consultivo(self.run_hook(self.post(sc, 1)))  # anúncio
        self.ok("bind", "--ledger", sc.ledger, "--host", "claude", "--native-key", sc.key)
        saidas = [self.assert_consultivo(r) for r in self.feed(sc, 5, start=2)]
        self.assertEqual([o is not None for o in saidas], [False, False, False, True, False])

    def test_binding_corrompido_nao_e_anunciado_nem_sobrescrito(self):
        sc = self.scenario("goal")
        sc.binding_path.write_text("{ quebrado", encoding="utf-8")
        for result in self.feed(sc, 3):
            self.silent(result)
        self.assertFalse(self.marcador(sc).exists())
        self.assertEqual(sc.binding_path.read_text(encoding="utf-8"), "{ quebrado")

    def test_concorrencia_anuncia_uma_unica_vez(self):
        sc = self.scenario_sem_bind()
        procs = [
            subprocess.Popen(
                [sys.executable, str(HOOK)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=self.env("claude"), cwd=self.base,
            )
            for _ in range(6)
        ]
        for n, proc in enumerate(procs, 1):
            proc.stdin.write(json.dumps(self.post(sc, n)).encode("utf-8"))
            proc.stdin.close()
        outs = []
        for proc in procs:
            out, err = proc.stdout.read(), proc.stderr.read()
            self.assertEqual((proc.wait(timeout=60), err), (0, b""))
            proc.stdout.close()
            proc.stderr.close()
            outs.append(out)
        self.assertEqual(sum(1 for out in outs if out), 1)
        self.assertTrue(self.marcador(sc).is_file())

    def test_se_a_gravacao_do_marcador_falha_fica_em_silencio_e_tenta_de_novo_depois(self):
        sc = self.scenario_sem_bind(git=True)
        ignore = sc.root / ".orq/progress/.gitignore"
        with self.subTest("o Git deixou de ignorar sessions"):
            ignore.write_text("*\n!v1/\n!v1/sessions/\n!v1/sessions/*.json\n", encoding="utf-8")
            self.silent(self.run_hook(self.post(sc, 1)))
            self.assertFalse(self.marcador(sc).exists())
        with self.subTest("Git sumiu do PATH"):
            ignore.write_text("*\n", encoding="utf-8")
            vazio = self.base / "path-vazio"
            vazio.mkdir()
            self.silent(self.run_hook(self.post(sc, 2), env=self.env("claude", PATH=str(vazio))))
            self.assertFalse(self.marcador(sc).exists())
        with self.subTest("lock ocupado"):
            holder = subprocess.Popen(
                [sys.executable, "-c",
                 "import sys,time\nimport importlib.util\n"
                 "s=importlib.util.spec_from_file_location('p',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
                 "from pathlib import Path\nwith m.ledger_lock(Path(sys.argv[2])):\n print('preso',flush=True)\n time.sleep(float(sys.argv[3]))\n",
                 str(CORE), str(self.marcador(sc)), "4.0"],
                stdout=subprocess.PIPE, text=True, env=self.env(),
            )
            self.addCleanup(holder.kill)
            self.assertEqual(holder.stdout.readline().strip(), "preso")
            self.silent(self.run_hook(self.post(sc, 3)))
            self.assertFalse(self.marcador(sc).exists())
            holder.kill()
            holder.wait(timeout=10)
        with self.subTest("tudo certo: anuncia, e o Git do consumidor segue limpo"):
            self.assertIsNotNone(self.assert_consultivo(self.run_hook(self.post(sc, 4))))
            self.assertTrue(self.marcador(sc).is_file())
            self.assertEqual(self.git(sc.root, "status", "--porcelain", "--untracked-files=all").stdout, "")

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignora permissões de diretório")
    def test_sem_permissao_de_escrita_fica_em_silencio_e_nao_deixa_temporario(self):
        sc = self.scenario_sem_bind()
        sessions = sc.root / ".orq/progress/v1/sessions"
        os.chmod(sessions, 0o500)
        self.addCleanup(os.chmod, sessions, 0o700)
        self.silent(self.run_hook(self.post(sc, 1)))
        self.assertEqual(list(sessions.iterdir()), [])

    def test_sessions_symlink_para_fora_nao_grava_marcador_fora(self):
        sc = self.scenario_sem_bind()
        fora = self.base / "fora"
        fora.mkdir()
        sessions = sc.root / ".orq/progress/v1/sessions"
        sessions.rmdir()
        os.symlink(fora, sessions)
        self.silent(self.run_hook(self.post(sc, 1)))
        self.assertEqual(list(fora.iterdir()), [])

    def test_o_marcador_fica_na_frente_mais_proxima_e_sobe_de_subdiretorios(self):
        sc = self.scenario_sem_bind()
        sub = sc.root / "pacote" / "fundo"
        sub.mkdir(parents=True)
        self.assertIsNotNone(self.assert_consultivo(self.run_hook(self.post(sc, 1, cwd=str(sub)))))
        self.assertTrue(self.marcador(sc).is_file())
        self.silent(self.run_hook(self.post(sc, 2, cwd=str(sub))))


class ProgressHookContencaoDoLedgerTest(HookTestCase):
    """O `ledger_path` do binding só vale se, resolvido, ainda cai no layout da frente onde o binding foi achado."""

    ENV = {"CLAUDE_PLUGIN_ROOT": str(PLUGIN)}

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

    def fora(self, nome="fora") -> dict:
        """Alvos fora da frente: um FIFO (abrir trava para sempre), um ledger válido de outra frente e um arquivo comum."""
        if getattr(self, "_alvos_de_fora", None):
            return self._alvos_de_fora
        pasta = self.base / nome
        pasta.mkdir(exist_ok=True)
        fifo = pasta / "ledger.fifo"
        os.mkfifo(fifo)
        outra = self.scenario("goal", name=f"{nome}-outra-frente", session_id="OUTRA")
        comum = pasta / "comum.json"
        comum.write_text("NAO-ABRIR", encoding="utf-8")
        self._alvos_de_fora = {"fifo": fifo, "outra frente": Path(outra.ledger), "arquivo comum": comum}
        return self._alvos_de_fora

    def troca_binding(self, sc: Scenario, caminho) -> None:
        document = sc.binding()
        document["ledger_path"] = str(caminho)
        sc.binding_path.write_text(json.dumps(document), encoding="utf-8")

    def troca_ledger_por_symlink(self, sc: Scenario, alvo) -> None:
        Path(sc.ledger).unlink()
        os.symlink(alvo, sc.ledger)

    def casos(self, sc: Scenario) -> dict:
        """Cada caso é (aplica, quais alvos de fora não podem ser abertos)."""
        alvos = self.fora()
        kanban = sc.root / "memory/wiki/KANBAN.md"
        casos = {}
        for nome, alvo in alvos.items():
            casos[f"binding aponta para {nome}"] = (lambda alvo=alvo: self.troca_binding(sc, alvo), alvo)
            casos[f"ledger trocado por symlink para {nome}"] = (lambda alvo=alvo: self.troca_ledger_por_symlink(sc, alvo), alvo)
        casos["binding aponta para arquivo da frente fora do layout"] = (lambda: self.troca_binding(sc, kanban), kanban)
        casos["ledger trocado por symlink para arquivo da frente fora do layout"] = (lambda: self.troca_ledger_por_symlink(sc, kanban), kanban)
        return casos

    def test_o_hook_nao_abre_ledger_fora_do_layout_nem_fora_da_frente(self):
        for nome in ("binding aponta para fifo", "ledger trocado por symlink para fifo"):
            with self.subTest(nome):  # o FIFO trava a leitura: o timeout derruba o teste se o hook o abrir
                sc = self.scenario("goal", name=f"frente-{abs(hash(nome))}")
                aplica, alvo = self.casos(sc)[nome]
                aplica()
                antes = sc.binding_path.read_bytes()
                self.silent(self.run_hook(self.post(sc, 1), timeout=20))
                self.assertEqual(sc.binding_path.read_bytes(), antes)
        sc = self.scenario("goal", name="frente-espiada")
        for nome, (aplica, alvo) in self.casos(sc).items():
            if "fifo" in nome:
                continue  # em processo um FIFO travaria o próprio teste: ele já foi coberto acima, com timeout
            with self.subTest(nome):
                original_ledger = Path(sc.ledger).read_bytes()
                original_binding = sc.binding_path.read_bytes()
                aplica()
                resultado, abertos = self.abertos_por(lambda: core.handle_hook(self.post(sc, 7), self.ENV))
                self.assertIsNone(resultado)
                self.assertNotIn(os.path.realpath(alvo), [os.path.realpath(a) for a in abertos if a], "o hook abriu o arquivo de fora")
                self.assertEqual(sc.binding()["calls_without_plan"], 0)
                if Path(sc.ledger).is_symlink():
                    Path(sc.ledger).unlink()
                Path(sc.ledger).write_bytes(original_ledger)
                sc.binding_path.write_bytes(original_binding)
        self.assertEqual(sc.binding()["calls_without_plan"], 0)

    def test_diretorio_de_ledgers_trocado_por_symlink_para_fora_nao_e_aberto(self):
        sc = self.scenario("goal")
        fora = self.base / "goals-fora"
        goals = Path(sc.ledger).parent
        goals.rename(fora)
        os.symlink(fora, goals)
        resultado, abertos = self.abertos_por(lambda: core.handle_hook(self.post(sc, 1), self.ENV))
        self.assertIsNone(resultado)
        self.assertNotIn(os.path.realpath(fora / Path(sc.ledger).name), [os.path.realpath(a) for a in abertos if a])
        self.assertEqual(sc.binding()["calls_without_plan"], 0)

    def test_ledger_legitimo_dentro_do_layout_continua_sendo_lido(self):
        sc = self.scenario("goal")
        resultado, abertos = self.abertos_por(lambda: core.handle_hook(self.post(sc, 1), self.ENV))
        self.assertIsNone(resultado)
        self.assertIn(os.path.realpath(sc.ledger), [os.path.realpath(a) for a in abertos if a])
        self.assertEqual(sc.binding()["calls_without_plan"], 1)

    def test_marcador_que_e_symlink_para_fora_nunca_e_seguido_nem_aberto(self):
        sc = self.scenario_sem_bind()
        marcador = sc.root / ".orq/progress/v1/sessions" / f".anunciada-{sc.key}.json"
        fifo = self.base / "marcador.fifo"
        os.mkfifo(fifo)
        comum = self.base / "marcador-fora.json"
        comum.write_text("INTOCADO", encoding="utf-8")
        for nome, alvo in {"fifo": fifo, "arquivo comum": comum, "ledger da frente": Path(sc.ledger)}.items():
            with self.subTest(nome):
                os.symlink(alvo, marcador)
                antes = alvo.read_bytes() if alvo.is_file() else None
                self.silent(self.run_hook(self.post(sc, 1), timeout=20))
                self.assertTrue(marcador.is_symlink())  # nada o substituiu
                if antes is not None:
                    self.assertEqual(alvo.read_bytes(), antes)
                marcador.unlink()

    def scenario_sem_bind(self, **kwargs):  # noqa: D102 - atalho, o andaime vive na classe base
        return HookTestCase.scenario_sem_bind(self, **kwargs)


class ProgressHookElegibilidadeNaSecaoCriticaTest(HookTestCase):
    """A elegibilidade é conferida de novo DENTRO da seção crítica do binding: o estado muda entre a consulta e a contagem."""

    ENV = {"CLAUDE_PLUGIN_ROOT": str(PLUGIN)}

    def prepara(self, kind="card", name="frente") -> Scenario:
        sc = self.scenario(kind, name=name)
        document = sc.binding()
        document["calls_without_plan"] = 3  # o próximo evento elegível seria o 4º, o do lembrete
        sc.binding_path.write_text(json.dumps(document), encoding="utf-8")
        return sc

    def injeta_depois_da_consulta(self, sc: Scenario, muda) -> tuple:
        """Roda o hook e executa `muda()` depois da primeira consulta e antes do lock do binding."""
        real = core.ensure_destinations_ignored

        def injeta(*args, **kwargs):
            muda()
            return real(*args, **kwargs)

        with mock.patch.object(core, "ensure_destinations_ignored", side_effect=injeta):
            return core.handle_hook(self.post(sc, 1), self.ENV)

    def test_o_plano_registrado_entre_a_consulta_e_a_contagem_impede_o_lembrete(self):
        for kind in ("card", "goal"):
            with self.subTest(kind=kind):
                sc = self.prepara(kind, name=f"frente-{kind}")
                saida = self.injeta_depois_da_consulta(sc, lambda: self.register_plan(sc))
                self.assertIsNone(saida)
                binding = sc.binding()
                self.assertEqual((binding["calls_without_plan"], binding["nudged"], binding["recent_event_ids"]), (3, False, []))

    def test_pausa_encerramento_e_mudanca_de_board_na_janela_tambem_impedem(self):
        casos = {
            "pausa": lambda sc: self.ok("pause", "--ledger", sc.ledger, "--session-key", sc.owner_key),
            "encerramento": lambda sc: self.ok("close", "--ledger", sc.ledger, "--session-key", sc.owner_key, "--outcome", "cancelled", "--evidence-ref", "t#c"),
            "board em gate": lambda sc: (sc.root / "memory/wiki/KANBAN.md").write_text("- [!] `T-144` Medidor — n\n", encoding="utf-8"),
            "board em planning": lambda sc: (sc.root / "memory/wiki/KANBAN.md").write_text("- [>] `T-144` Medidor — n\n", encoding="utf-8"),
        }
        for nome, muda in casos.items():
            with self.subTest(nome):
                sc = self.prepara(name=f"frente-{abs(hash(nome))}")
                saida = self.injeta_depois_da_consulta(sc, lambda: muda(sc))
                self.assertIsNone(saida)
                binding = sc.binding()
                self.assertEqual((binding["calls_without_plan"], binding["nudged"]), (3, False))

    def test_sem_mudanca_na_janela_o_quarto_evento_emite_o_lembrete(self):
        for kind in ("card", "goal"):
            with self.subTest(kind=kind):
                sc = self.prepara(kind, name=f"controle-{kind}")
                saida = self.injeta_depois_da_consulta(sc, lambda: None)
                self.assertIsNotNone(saida)
                self.assertEqual(sc.binding()["calls_without_plan"], 4)
                self.assertTrue(sc.binding()["nudged"])

    def test_goal_conta_em_qualquer_activity_e_card_so_pelo_board(self):
        sc = self.scenario("goal", name="goal-activities")
        for activity in ("planning", "execution", "verification"):  # o begin deixa o goal em planning: precisa contar
            self.ok("phase", "--ledger", sc.ledger, "--session-key", sc.owner_key, "--value", activity)
            antes = sc.binding()["calls_without_plan"]
            self.silent(self.run_hook(self.post(sc, 100 + len(activity))))
            self.assertEqual(sc.binding()["calls_without_plan"], antes + 1, activity)
        card = self.scenario("card", name="card-activities")
        for activity in ("planning", "gate", "ready"):  # com o board em [~] a atividade declarada não exclui
            self.ok("phase", "--ledger", card.ledger, "--session-key", card.owner_key, "--value", activity)
            antes = card.binding()["calls_without_plan"]
            self.silent(self.run_hook(self.post(card, 200 + len(activity))))
            self.assertEqual(card.binding()["calls_without_plan"], antes + 1, activity)


class ProgressHookCustoTest(HookTestCase):
    """Sem medidor, o hook sai antes de importar o núcleo: o custo cai em toda chamada de ferramenta de todo projeto."""

    SENTINELA = (
        "import os\n"
        "open(os.environ['ORQ_SENTINELA'], 'a').write('importado\\n')\n"
        "def handle_hook(event, env):\n"
        "    return None\n"
    )

    def hook_com_nucleo_espiao(self, payload, host="claude") -> tuple:
        """Copia só o adaptador para uma pasta própria, com um `progress.py` de mentira que avisa quando é importado."""
        pasta = self.base / "adaptador-isolado"
        pasta.mkdir(exist_ok=True)
        (pasta / "progress-hook.py").write_bytes(HOOK.read_bytes())
        (pasta / "progress.py").write_text(self.SENTINELA, encoding="utf-8")
        marca = self.base / "sentinela.txt"
        marca.unlink(missing_ok=True)
        result = self.run_hook(payload, env=self.env(host, ORQ_SENTINELA=str(marca)), script=pasta / "progress-hook.py")
        return result, marca.exists()

    def test_sem_medidor_o_nucleo_nao_e_importado(self):
        sem_medidor = self.make_front("sem-medidor")
        com_orq_sem_sessions = self.make_front("com-orq")
        (com_orq_sem_sessions / ".orq/progress/v1/cards").mkdir(parents=True)  # o medidor só existe com sessions/
        sc = self.scenario(name="com-medidor")
        for nome, cwd in {"projeto sem .orq": sem_medidor, ".orq sem sessions": com_orq_sem_sessions, "cwd inexistente": self.base / "nao-existe"}.items():
            for evento in ("PostToolUse", "SessionStart"):
                with self.subTest(nome, evento=evento):
                    payload = self.post(sc, 1, cwd=str(cwd)) if evento == "PostToolUse" else self.session_start(sc, "startup", cwd=str(cwd))
                    result, importou = self.hook_com_nucleo_espiao(payload)
                    self.silent(result)
                    self.assertFalse(importou, "o núcleo foi importado sem medidor")
        with self.subTest("host desconhecido, mesmo com medidor"):
            result, importou = self.hook_com_nucleo_espiao(self.post(sc, 1), host=None)
            self.silent(result)
            self.assertFalse(importou)
        with self.subTest("evento que o medidor não trata"):
            result, importou = self.hook_com_nucleo_espiao(self.post(sc, 1, hook_event_name="Stop"))
            self.silent(result)
            self.assertFalse(importou)

    def test_com_medidor_o_nucleo_e_importado(self):
        sc = self.scenario(name="com-medidor")
        for evento, payload in (("PostToolUse", self.post(sc, 1)), ("SessionStart", self.session_start(sc, "startup"))):
            with self.subTest(evento):
                result, importou = self.hook_com_nucleo_espiao(payload)
                self.assertEqual(result.returncode, 0)
                self.assertTrue(importou)

    def test_a_saida_rapida_nao_muda_o_comportamento_com_o_nucleo_real(self):
        sem_medidor = self.make_front("sem-medidor")
        sc = self.scenario(name="com-medidor")
        silencio = self.run_hook(self.post(sc, 1, cwd=str(sem_medidor)))
        self.silent(silencio)
        self.assertEqual(sorted(p.name for p in sem_medidor.iterdir()), ["memory"])


class ProgressHookFalhasTest(HookTestCase):
    """Toda falha sai 0, sem bloquear: no máximo uma saída vazia."""

    def test_payload_invalido_nao_faz_nada_e_sai_zero(self):
        sc = self.scenario("goal")
        antes = snapshot(sc.root)
        casos = {
            "stdin vazio": b"",
            "json quebrado": b"{",
            "lista": b"[]",
            "texto": b'"x"',
            "null": b"null",
            "numero": b"42",
            "utf8 invalido": b"\xff\xfe\x00{",
            "enorme": b'{"cwd": "' + b"x" * (5 * 1024 * 1024) + b'"}',
        }
        for nome, bruto in casos.items():
            with self.subTest(nome):
                self.silent(self.run_hook(bruto))
        base = self.post(sc, 1)
        mutacoes = {
            "sem session_id": {"session_id": None},
            "session_id numerico": {"session_id": 12345},
            "session_id vazio": {"session_id": ""},
            "session_id com controle": {"session_id": "a\x1b[2Jb"},
            "cwd relativo": {"cwd": "relativo/frente"},
            "cwd inexistente": {"cwd": str(self.base / "nao-existe")},
            "cwd numerico": {"cwd": 7},
            "sem evento": {"hook_event_name": None},
            "evento desconhecido": {"hook_event_name": "Stop"},
            "pre-tool": {"hook_event_name": "PreToolUse"},
            "prompt": {"hook_event_name": "UserPromptSubmit"},
            "agent_id lista": {"agent_id": ["x"]},
        }
        for nome, mudanca in mutacoes.items():
            with self.subTest(nome):
                self.silent(self.run_hook({**base, **mudanca}))
        self.assertEqual(snapshot(sc.root), antes)

    def test_host_desconhecido_nao_faz_nada(self):
        sc = self.scenario("goal")
        antes = snapshot(sc.root)
        for nome, ambiente in {
            "sem variavel de plugin": self.env(None),
            "variaveis vazias": self.env(None, PLUGIN_ROOT="", CLAUDE_PLUGIN_ROOT=""),
        }.items():
            with self.subTest(nome):
                for payload in (self.post(sc, 1), self.session_start(sc, "startup")):
                    self.silent(self.run_hook(payload, env=ambiente))
        self.assertEqual(snapshot(sc.root), antes)

    def test_host_e_decidido_pelo_ambiente_nativo_e_plugin_root_vence(self):
        self.assertEqual(core.hook_host({"PLUGIN_ROOT": "/x"}), "codex")
        self.assertEqual(core.hook_host({"CLAUDE_PLUGIN_ROOT": "/x"}), "claude")
        self.assertEqual(core.hook_host({"PLUGIN_ROOT": "/x", "CLAUDE_PLUGIN_ROOT": "/y"}), "codex")
        for ambiente in ({}, {"PLUGIN_ROOT": ""}, {"CLAUDE_PLUGIN_ROOT": ""}, {"OUTRA": "x"}):
            self.assertIsNone(core.hook_host(ambiente))
        sc = self.scenario("goal", "codex")
        ambos = self.env("codex", CLAUDE_PLUGIN_ROOT=str(PLUGIN))  # Codex que também exporta o nome do Claude
        self.silent(self.run_hook(self.post(sc, 1), env=ambos))
        self.assertEqual(sc.binding()["calls_without_plan"], 1)

    def test_binding_ledger_ou_lock_com_problema_nao_bloqueiam(self):
        sc = self.scenario("goal")
        binding_bytes = sc.binding_path.read_bytes()
        ledger = Path(sc.ledger)
        ledger_bytes = ledger.read_bytes()
        with self.subTest("binding corrompido"):
            sc.binding_path.write_text("{ quebrado", encoding="utf-8")
            self.silent(self.run_hook(self.post(sc, 1)))
            self.assertEqual(sc.binding_path.read_text(encoding="utf-8"), "{ quebrado")
        with self.subTest("binding de versão futura"):
            sc.binding_path.write_text(json.dumps({"schema_version": 9}), encoding="utf-8")
            self.silent(self.run_hook(self.post(sc, 2)))
        sc.binding_path.write_bytes(binding_bytes)
        with self.subTest("ledger corrompido"):
            ledger.write_text("{ quebrado", encoding="utf-8")
            self.silent(self.run_hook(self.post(sc, 3)))
            self.assertEqual(sc.binding_path.read_bytes(), binding_bytes)
        with self.subTest("ledger ausente"):
            ledger.unlink()
            self.silent(self.run_hook(self.post(sc, 4)))
            self.assertEqual(sc.binding_path.read_bytes(), binding_bytes)
        ledger.write_bytes(ledger_bytes)
        with self.subTest("ledger de outra execução (binding obsoleto)"):
            document = sc.binding()
            document["run_id"] = "00000000-0000-4000-8000-000000000000"
            sc.binding_path.write_text(json.dumps(document), encoding="utf-8")
            outdated = sc.binding_path.read_bytes()
            self.silent(self.run_hook(self.post(sc, 5)))
            self.assertEqual(sc.binding_path.read_bytes(), outdated)
        sc.binding_path.write_bytes(binding_bytes)
        with self.subTest("de volta ao normal conta"):
            self.silent(self.run_hook(self.post(sc, 6)))
            self.assertEqual(sc.binding()["calls_without_plan"], 1)

    def test_lock_ocupado_nao_bloqueia_o_host_e_nao_grava(self):
        sc = self.scenario("goal")
        antes = sc.binding_path.read_bytes()
        holder = self.hold_binding_lock(sc, 4.0)
        started = time.monotonic()
        result = self.run_hook(self.post(sc, 1))
        self.assertLess(time.monotonic() - started, 4.0)  # esperou pouco e desistiu antes de o lock soltar
        self.silent(result)
        self.assertEqual(sc.binding_path.read_bytes(), antes)
        holder.kill()
        holder.wait(timeout=10)
        self.silent(self.run_hook(self.post(sc, 2)))
        self.assertEqual(sc.binding()["calls_without_plan"], 1)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignora permissões de diretório")
    def test_falta_de_permissao_de_escrita_sai_zero_sem_saida(self):
        sc = self.scenario("goal")
        antes = sc.binding_path.read_bytes()
        sessions = sc.binding_path.parent
        os.chmod(sessions, 0o500)
        self.addCleanup(os.chmod, sessions, 0o700)
        self.silent(self.run_hook(self.post(sc, 1)))
        self.assertEqual(sc.binding_path.read_bytes(), antes)
        self.assertEqual(sorted(p.name for p in sessions.iterdir()), [sc.binding_path.name])  # nenhum temporário

    def test_git_indisponivel_ou_destino_nao_ignorado_nao_grava_e_nao_bloqueia(self):
        sc = self.scenario("goal", git=True)
        antes = sc.binding_path.read_bytes()
        vazio = self.base / "path-vazio"
        vazio.mkdir()
        with self.subTest("git sumiu do PATH"):
            self.silent(self.run_hook(self.post(sc, 1), env=self.env("claude", PATH=str(vazio))))
            self.assertEqual(sc.binding_path.read_bytes(), antes)
        with self.subTest("o .gitignore deixou de cobrir sessions"):
            (sc.root / ".orq/progress/.gitignore").write_text("*\n!v1/\n!v1/sessions/\n!v1/sessions/*.json\n", encoding="utf-8")
            self.silent(self.run_hook(self.post(sc, 2)))
            self.assertEqual(sc.binding_path.read_bytes(), antes)
        (sc.root / ".orq/progress/.gitignore").write_text("*\n", encoding="utf-8")
        with self.subTest("coberto: grava e o Git do consumidor segue limpo"):
            self.silent(self.run_hook(self.post(sc, 3)))
            self.assertEqual(sc.binding()["calls_without_plan"], 1)
            self.assertEqual(self.git(sc.root, "status", "--porcelain", "--untracked-files=all").stdout, "")

    def test_sessions_symlink_para_fora_nao_e_seguido(self):
        sc = self.scenario("goal")
        fora = self.base / "fora"
        fora.mkdir()
        (fora / sc.binding_path.name).write_bytes(sc.binding_path.read_bytes())
        sessions = sc.binding_path.parent
        sessions.rename(self.base / "sessions-original")
        os.symlink(fora, sessions)
        antes = snapshot(fora)
        self.silent(self.run_hook(self.post(sc, 1)))
        self.assertEqual(snapshot(fora), antes)

    def test_sem_o_nucleo_ao_lado_o_hook_sai_zero_sem_saida(self):
        isolado = self.base / "isolado"
        isolado.mkdir()
        copia = isolado / "progress-hook.py"
        copia.write_bytes(HOOK.read_bytes())
        sc = self.scenario("goal")
        self.silent(self.run_hook(self.post(sc, 1), script=copia))
        self.assertEqual(sc.binding()["calls_without_plan"], 0)


class ProgressHookLeituraMinimaTest(HookTestCase):
    """O hook não abre o transcript e não inspeciona nem grava conteúdo de ferramenta ou de prompt."""

    def test_transcript_que_travaria_a_leitura_nao_e_aberto(self):
        sc = self.scenario("goal")
        fifo = self.base / "transcript.fifo"
        os.mkfifo(fifo)  # abrir um FIFO sem escritor trava para sempre: o timeout derruba o teste se o hook o abrir
        for event in (self.post(sc, 1, transcript_path=str(fifo)), self.session_start(sc, "startup", transcript_path=str(fifo))):
            self.assert_consultivo(self.run_hook(event, timeout=20))
        self.assertEqual(sc.binding()["calls_without_plan"], 1)

    def test_em_processo_so_os_campos_do_contrato_sao_acessados_e_o_transcript_nao_e_aberto(self):
        sc = self.scenario("goal")
        proibidos = ("tool_input", "tool_response", "transcript_path", "prompt", "user_prompt", "last_assistant_message")

        class Guarded(dict):
            def _barra(self, key):
                if key in proibidos:
                    raise AssertionError(f"o hook leu o campo proibido {key!r}")

            def __getitem__(self, key):
                self._barra(key)
                return super().__getitem__(key)

            def get(self, key, default=None):
                self._barra(key)
                return super().get(key, default)

            def __contains__(self, key):
                self._barra(key)
                return super().__contains__(key)

            def __iter__(self):
                raise AssertionError("o hook percorreu o payload inteiro")

            items = keys = values = __iter__

        abertos = []
        real_open, real_os_open = builtins.open, os.open

        def espia_open(file, *args, **kwargs):
            abertos.append(str(file))
            return real_open(file, *args, **kwargs)

        def espia_os_open(path, *args, **kwargs):
            abertos.append(str(path))
            return real_os_open(path, *args, **kwargs)

        transcript = str(self.base / "transcript-que-nao-pode-ser-aberto.jsonl")
        Path(transcript).write_text("NAO-LER", encoding="utf-8")
        ambiente = {"CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
        for factory in (self.post, self.session_start):
            event = factory(sc, 1 if factory == self.post else "startup", transcript_path=transcript)
            with mock.patch.object(builtins, "open", espia_open), mock.patch.object(os, "open", espia_os_open):
                core.handle_hook(Guarded(event), ambiente)
        self.assertNotIn(transcript, abertos)
        self.assertTrue(abertos, "o espião deveria ter visto ao menos a leitura do binding")

    def test_conteudo_de_ferramenta_nao_vai_para_o_disco_nem_para_a_saida(self):
        for host in HOSTS:
            with self.subTest(host=host):
                sc = self.scenario("goal", host, name=f"frente-{host}")
                resultados = self.feed(sc, 5)
                self.assertTrue(any(r.stdout for r in resultados))
                for result in resultados:
                    self.assertNotIn(SECRET.encode(), result.stdout)
                for current, directories, files in os.walk(self.base):
                    for name in files:
                        self.assertNotIn(SECRET.encode(), (Path(current) / name).read_bytes(), name)


class ProgressHookSessionStartTest(HookTestCase):
    def test_entrega_a_chave_nativa_nas_cinco_fontes_e_nunca_o_id_bruto(self):
        for host in HOSTS:
            sc = self.scenario("card", host, name=f"frente-{host}")
            antes = snapshot(sc.root)
            for source in SOURCES:
                with self.subTest(host=host, source=source):
                    result = self.run_hook(self.session_start(sc, source), host)
                    output = self.assert_consultivo(result)
                    context = output["additionalContext"]
                    self.assertEqual(output["hookEventName"], "SessionStart")
                    self.assertIn(core.derive_session_key(host, RAW_SESSION), context)
                    self.assertNotIn(RAW_SESSION, self.text(result))
                    self.assertIn(f"bind --host {host} --native-key", context)
                    self.assertIn("chave de dono", context)
                    self.assertIn("medidor ativo", context)
            self.assertEqual(snapshot(sc.root), antes)  # só informa: não cria, não vincula, não toca

    def test_fonte_ausente_ou_desconhecida_e_frente_sem_medidor_nao_emitem(self):
        sc = self.scenario("goal")
        for source in ("manual", "", None, 7):
            with self.subTest(source=source):
                self.silent(self.run_hook(self.session_start(sc, source)))
        sem_source = self.session_start(sc, "startup")
        del sem_source["source"]
        self.silent(self.run_hook(sem_source))
        sem_medidor = self.make_front("sem-medidor")
        self.silent(self.run_hook(self.session_start(sc, "startup", cwd=str(sem_medidor))))
        self.assertEqual(sorted(p.name for p in sem_medidor.iterdir()), ["memory"])

    def test_session_start_nao_zera_contadores_de_binding_existente(self):
        sc = self.scenario("goal")
        for result in self.feed(sc, 2):
            self.silent(result)
        antes = sc.binding_path.read_bytes()
        self.assert_consultivo(self.run_hook(self.session_start(sc, "resume")))
        self.assertEqual(sc.binding_path.read_bytes(), antes)
        self.assertEqual(sc.binding()["calls_without_plan"], 2)

    def test_session_start_nao_cria_goal_nem_interpreta_prompt(self):
        sc = self.scenario("goal")
        antes = snapshot(sc.root)
        event = self.session_start(sc, "startup", prompt="quero um goal novo: refatorar tudo")
        self.assert_consultivo(self.run_hook(event))
        self.assertEqual(snapshot(sc.root), antes)
        self.assertEqual(len(list((sc.root / ".orq/progress/v1/goals").glob("*.json"))), 1)

    def test_fluxo_ponta_a_ponta_da_chave_do_hook_ate_o_lembrete(self):
        for host in HOSTS:
            with self.subTest(host=host):
                root = self.make_front(f"frente-{host}")
                begun = self.ok("begin", "--kind", "goal", "--root", str(root), "--host", host)
                owner = begun["session_key"]
                event = {
                    "session_id": RAW_SESSION, "transcript_path": str(self.base / "t.jsonl"), "cwd": str(root),
                    "hook_event_name": "SessionStart", "source": "clear",
                }
                context = self.assert_consultivo(self.run_hook(event, host))["additionalContext"]
                native = re.search(r"[0-9a-f]{64}", context).group(0)
                self.assertNotEqual(native, owner)  # são duas chaves, e o hook entrega a nativa
                bound = self.ok("bind", "--ledger", begun["ledger_path"], "--host", host, "--native-key", native)
                self.assertEqual(bound["session_key"], native)
                sc = Scenario(root, begun["ledger_path"], owner, host, RAW_SESSION, "goal")
                outputs = [self.assert_consultivo(r) for r in self.feed(sc, 5)]
                self.assertEqual([o is not None for o in outputs], [False, False, False, True, False])
                # as mutações seguem com a chave de DONO; a chave nativa não autoriza escrita
                self.ok("plan", "--ledger", begun["ledger_path"], "--session-key", owner, "--input", "-", stdin=json.dumps({"tasks": [{"id": "P01", "title": "t", "size": "S"}]}))
                recibo = self.cli("pause", "--ledger", begun["ledger_path"], "--session-key", native)
                self.assertEqual(recibo.returncode, 3)


class ProgressHookBundleTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))["hooks"]

    def progress_groups(self, event: str) -> list:
        return [g for g in self.config.get(event, []) if any("progress-hook.py" in h.get("command", "") for h in g["hooks"])]

    def guard_groups(self, event: str) -> list:
        return [g for g in self.config.get(event, []) if any("context-guard.py" in h.get("command", "") for h in g["hooks"])]

    def test_as_seis_entradas_do_context_guard_seguem_intactas(self):
        self.assertEqual(set(GUARD_GROUPS), {"PostToolUse", "Stop", "UserPromptSubmit", "SessionStart", "PreCompact", "PostCompact"})
        for event, group in GUARD_GROUPS.items():
            with self.subTest(event=event):
                self.assertEqual(self.guard_groups(event), [group])  # igualdade exata: matcher, timeout, mensagem, limite
                self.assertEqual(self.config[event][0], group)  # e a posição original

    def test_o_medidor_so_acrescenta_posttooluse_e_sessionstart(self):
        com_medidor = {event for event in self.config if self.progress_groups(event)}
        self.assertEqual(com_medidor, {"PostToolUse", "SessionStart"})
        self.assertEqual(set(self.config), set(GUARD_GROUPS))  # nenhum evento novo no bundle
        for event in ("Stop", "UserPromptSubmit", "PreCompact", "PostCompact"):
            self.assertEqual(self.progress_groups(event), [])

    def test_entradas_do_medidor_sao_proprias_curtas_e_em_portugues(self):
        for event in ("PostToolUse", "SessionStart"):
            with self.subTest(event=event):
                grupos = self.progress_groups(event)
                self.assertEqual(len(grupos), 1)
                self.assertEqual(len(grupos[0]["hooks"]), 1)  # nenhum handler do medidor dentro de grupo do guardião
                handler = grupos[0]["hooks"][0]
                self.assertEqual(handler["type"], "command")
                self.assertEqual(handler["command"], 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/progress-hook.py"')
                self.assertLessEqual(handler["timeout"], 5)
                self.assertTrue(handler["statusMessage"].strip())
                self.assertNotIn("additionalContextLimit", handler)  # campo sem contrato documentado: o limite é do próprio hook
                self.assertEqual(self.guard_groups(event) + grupos, self.config[event])  # o do medidor vem depois
        self.assertTrue(HOOK.is_file())

    def test_matchers_cobrem_as_cinco_fontes_do_session_start_e_o_posttooluse_vale_para_toda_ferramenta(self):
        grupo = self.progress_groups("SessionStart")[0]
        for source in SOURCES:
            self.assertRegex(source, grupo["matcher"])
            self.assertTrue(re.fullmatch(grupo["matcher"], source))
        for outra in ("", "other", "manual", "startup2", "pre-startup"):
            self.assertIsNone(re.fullmatch(grupo["matcher"], outra))
        self.assertNotIn("matcher", self.progress_groups("PostToolUse")[0])


class ProgressHookCoexistenciaTest(HookTestCase):
    def test_guardiao_e_medidor_rodam_no_mesmo_evento_sem_se_tocar(self):
        guard = SCRIPTS / "context-guard.py"
        sc = self.scenario("goal", "codex")
        data = self.base / "plugin-data"
        data.mkdir()
        ambiente = self.env("codex", PLUGIN_DATA=str(data))
        event = self.session_start(sc, "clear")
        medidor = self.run_hook(event, env=ambiente)
        guardiao = self.run_hook(event, env=ambiente, script=guard)
        self.assertEqual(guardiao.returncode, 0)
        self.assertEqual(guardiao.stderr, b"")
        for result in (medidor, guardiao):
            if result.stdout:
                json.loads(result.stdout)  # cada um responde um objeto JSON próprio
        contexto = self.assert_consultivo(medidor)["additionalContext"]
        self.assertIn(core.derive_session_key("codex", RAW_SESSION), contexto)
        self.assertFalse(any((self.base / "plugin-data").rglob("*progress*")))  # o medidor não escreve no estado do guardião
        self.assertNotIn(b"progress", guardiao.stdout.lower())  # e o guardião não fala do medidor

    def test_guardiao_segue_inerte_no_claude_e_o_medidor_age(self):
        guard = SCRIPTS / "context-guard.py"
        sc = self.scenario("goal", "claude")
        event = self.post(sc, 1)
        self.assertEqual(self.run_hook(event, env=self.env("claude"), script=guard).stdout, b"")
        self.silent(self.run_hook(event, env=self.env("claude")))
        self.assertEqual(sc.binding()["calls_without_plan"], 1)


if __name__ == "__main__":
    unittest.main()
