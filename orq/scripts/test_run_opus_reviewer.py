#!/usr/bin/env python3
"""Testes stdlib do runner determinístico do reviewer Opus."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock


RUNNER = Path(__file__).with_name("run-opus-reviewer.py")


class OpusReviewerRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-opus-runner-test-")
        self.addCleanup(self.tmp.cleanup)
        self.fake = Path(self.tmp.name) / "claude"
        self.fake.write_text(
            textwrap.dedent(
                f"""\
                #!{sys.executable}
                import json
                import os
                from pathlib import Path
                import subprocess
                import sys
                import time

                marker = os.environ.get("FAKE_MARKER")
                if marker:
                    Path(marker).write_text("called", encoding="utf-8")
                if os.environ.get("FAKE_SPAWN_HOLDER") == "1":
                    child_marker = os.environ["FAKE_CHILD_MARKER"]
                    child_code = (
                        "import pathlib,time; time.sleep(0.5); "
                        f"pathlib.Path({{child_marker!r}}).write_text('survived')"
                    )
                    subprocess.Popen([sys.executable, "-c", child_code])
                    time.sleep(2)
                if os.environ.get("FAKE_TIMEOUT_CHILD") == "1":
                    ready = os.environ["FAKE_CHILD_READY"]
                    late = os.environ["FAKE_CHILD_LATE"]
                    stop = os.environ["FAKE_CHILD_STOP"]
                    done = os.environ["FAKE_CHILD_DONE"]
                    group = os.environ.get("FAKE_CHILD_GROUP")
                    child_code = (
                        "import os\\n"
                        "from pathlib import Path\\n"
                        "import signal\\n"
                        "import time\\n"
                        "if os.environ.get('FAKE_CHILD_ESCAPE') == '1':\\n    os.setsid()\\n"
                        "if os.environ.get('FAKE_CHILD_IGNORE_TERM') == '1':\\n    signal.signal(signal.SIGTERM, signal.SIG_IGN)\\n"
                        f"ready = Path({{ready!r}})\\n"
                        f"late = Path({{late!r}})\\n"
                        f"stop = Path({{stop!r}})\\n"
                        f"done = Path({{done!r}})\\n"
                        f"group = Path({{group!r}}) if {{group!r}} else None\\n"
                        "if group is not None:\\n    group.write_text(str(os.getpgrp()), encoding='utf-8')\\n"
                        "if os.environ.get('FAKE_CHILD_SKIP_READY') != '1':\\n"
                        "    ready.write_text('ready', encoding='utf-8')\\n"
                        "deadline = time.monotonic() + 2.0\\n"
                        "while time.monotonic() < deadline and not stop.exists():\\n"
                        "    time.sleep(0.02)\\n"
                        "if stop.exists():\\n"
                        "    done.write_text('done', encoding='utf-8')\\n"
                        "else:\\n"
                        "    late.write_text('late', encoding='utf-8')\\n"
                    )
                    child_kwargs = {{}}
                    if os.environ.get("FAKE_CHILD_DEVNULL") == "1":
                        child_kwargs = {{"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}}
                    subprocess.Popen([sys.executable, "-c", child_code], **child_kwargs)
                    time.sleep(float(os.environ.get("FAKE_CHILD_PARENT_SLEEP", "4")))
                time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
                expect_model = os.environ.get("FAKE_EXPECT_MODEL", "opus")
                expected = [
                    "-p", "--model", expect_model, "--permission-mode", "plan", "--tools", "",
                    "--setting-sources", "", "--disable-slash-commands",
                    "--no-session-persistence", "--output-format", "json",
                ]
                if sys.argv[1:] != expected:
                    print("unexpected argv: " + repr(sys.argv[1:]), file=sys.stderr)
                    raise SystemExit(19)
                stdin_content = sys.stdin.read()
                expected_stdin = os.environ.get("FAKE_EXPECT_STDIN")
                if expected_stdin is not None:
                    if expected_stdin != stdin_content or expected_stdin in sys.argv:
                        print("briefing was not delivered only by stdin", file=sys.stderr)
                        raise SystemExit(21)
                code = int(os.environ.get("FAKE_EXIT", "0"))
                if code:
                    print("fake claude failed", file=sys.stderr)
                    raise SystemExit(code)
                raw_stdout = os.environ.get("FAKE_RAW_STDOUT")
                if raw_stdout is not None:
                    print(raw_stdout)
                    raise SystemExit(0)
                model = os.environ.get("FAKE_MODEL", "claude-opus-5")
                result = os.environ.get("FAKE_RESULT", "PARECER_OK")
                payload = {{"result": result, "modelUsage": {{model: {{}}}}}}
                extra_model = os.environ.get("FAKE_EXTRA_MODEL")
                if extra_model:
                    payload["modelUsage"][extra_model] = {{}}
                if os.environ.get("FAKE_NO_MODEL") == "1":
                    payload["modelUsage"] = {{}}
                if os.environ.get("FAKE_IS_ERROR") == "1":
                    payload["is_error"] = True
                print(json.dumps(payload))
                """
            ),
            encoding="utf-8",
        )
        self.fake.chmod(0o755)

    def run_runner(
        self,
        briefing: str = "revise este diff",
        *args: str,
        runner_path: Path | None = None,
        outer_timeout: float = 5,
        **env_overrides: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CLAUDE_BIN"] = str(self.fake)
        env.update(env_overrides)
        return subprocess.run(
            [sys.executable, str(runner_path or RUNNER), *args],
            input=briefing,
            text=True,
            capture_output=True,
            env=env,
            timeout=outer_timeout,
        )

    def wait_for_marker(self, marker: Path, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if marker.exists():
                return True
            time.sleep(0.02)
        return marker.exists()

    def timeout_child_paths(self) -> dict[str, Path]:
        root = Path(self.tmp.name)
        return {
            "ready": root / "timeout-child-ready",
            "late": root / "timeout-child-late",
            "stop": root / "timeout-child-stop",
            "done": root / "timeout-child-done",
            "group": root / "timeout-child-group",
        }

    def write_mutated_runner(self, before: str, after: str, *, count: int = 1) -> Path:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertEqual(source.count(before), count, "mutação deixou de ser aplicável")
        mutated = Path(self.tmp.name) / "run-opus-reviewer-mutated.py"
        mutated.write_text(source.replace(before, after, count), encoding="utf-8")
        return mutated

    def cleanup_fixture_group(self, group_marker: Path) -> bool:
        if not group_marker.exists():
            return True
        try:
            group_id = int(group_marker.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        try:
            os.killpg(group_id, signal.SIGKILL)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            try:
                os.killpg(group_id, 0)
            except ProcessLookupError:
                return True
            except PermissionError:
                return False
            time.sleep(0.02)
        return False

    def assert_timeout_cancels_started_child(
        self,
        *,
        runner_path: Path | None = None,
        escape_session: bool = False,
        skip_ready: bool = False,
    ) -> None:
        paths = self.timeout_child_paths()
        started = time.monotonic()
        try:
            result = self.run_runner(
                "briefing",
                "--timeout",
                "1",
                runner_path=runner_path,
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
                FAKE_CHILD_ESCAPE="1" if escape_session else "0",
                FAKE_CHILD_SKIP_READY="1" if skip_ready else "0",
            )
            elapsed = time.monotonic() - started
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("OPUS_STARTED", result.stderr)
            self.assertIn("OPUS_TIMEOUT", result.stderr)
            self.assertLess(elapsed, 1.8, f"timeout levou {elapsed:.2f}s")
            self.assertTrue(
                self.wait_for_marker(paths["ready"], 0.7),
                "filho do fixture nao iniciou; a guarda de sobrevivencia seria vacua",
            )
            self.assertFalse(paths["late"].exists(), "filho iniciado concluiu cedo demais")
            self.assertTrue(paths["ready"].exists(), "prova de inicio sumiu antes da assercao negativa")
            self.assertFalse(
                self.wait_for_marker(paths["late"], 2.3),
                "filho iniciado sobreviveu ao timeout do runner",
            )
        finally:
            paths["stop"].write_text("stop", encoding="utf-8")
            self.wait_for_marker(paths["done"], 1.0)

    def assert_timeout_kills_term_ignoring_same_group_child(
        self, *, runner_path: Path | None = None,
    ) -> None:
        paths = self.timeout_child_paths()
        verified = False
        try:
            started = time.monotonic()
            result = self.run_runner(
                "briefing",
                "--timeout",
                "1",
                runner_path=runner_path,
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_PARENT_SLEEP="5",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
                FAKE_CHILD_GROUP=str(paths["group"]),
                FAKE_CHILD_IGNORE_TERM="1",
                FAKE_CHILD_DEVNULL="1",
            )
            elapsed = time.monotonic() - started
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("OPUS_STARTED", result.stderr)
            self.assertIn("OPUS_TIMEOUT", result.stderr)
            self.assertLess(elapsed, 1.8, f"timeout levou {elapsed:.2f}s")
            self.assertTrue(
                self.wait_for_marker(paths["ready"], 0.7),
                "filho que ignora TERM nao iniciou; a guarda seria vacua",
            )
            self.assertFalse(paths["late"].exists(), "filho ignorante concluiu cedo demais")
            self.assertTrue(paths["ready"].exists(), "prova de inicio sumiu antes da assercao negativa")
            self.assertFalse(
                self.wait_for_marker(paths["late"], 2.3),
                "filho no grupo proprio ignorou TERM e sobreviveu ao timeout",
            )
            verified = True
        finally:
            cleaned = self.cleanup_fixture_group(paths["group"])
            if verified:
                self.assertTrue(cleaned, "cleanup do grupo exclusivo do fixture nao terminou")

    def assert_timeout_kills_same_group_child_after_parent_exits(
        self, *, runner_path: Path | None = None,
    ) -> None:
        paths = self.timeout_child_paths()
        verified = False
        try:
            started = time.monotonic()
            result = self.run_runner(
                "briefing",
                "--timeout",
                "1",
                runner_path=runner_path,
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_PARENT_SLEEP="0",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
                FAKE_CHILD_GROUP=str(paths["group"]),
            )
            elapsed = time.monotonic() - started
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("OPUS_STARTED", result.stderr)
            self.assertIn("OPUS_TIMEOUT", result.stderr)
            self.assertLess(elapsed, 1.8, f"timeout levou {elapsed:.2f}s")
            self.assertTrue(
                self.wait_for_marker(paths["ready"], 0.7),
                "filho que reteve pipe nao iniciou; a guarda seria vacua",
            )
            self.assertFalse(paths["late"].exists(), "filho com pipe concluiu cedo demais")
            self.assertTrue(paths["ready"].exists(), "prova de inicio sumiu antes da assercao negativa")
            self.assertFalse(
                self.wait_for_marker(paths["late"], 2.3),
                "filho no grupo proprio sobreviveu depois da saida do lider",
            )
            verified = True
        finally:
            cleaned = self.cleanup_fixture_group(paths["group"])
            if verified:
                self.assertTrue(cleaned, "cleanup do grupo exclusivo do fixture nao terminou")

    def assert_timeout_returns_with_escaped_pipe_holder(self, *, runner_path: Path | None = None) -> None:
        paths = self.timeout_child_paths()
        completed = False
        try:
            started = time.monotonic()
            result = self.run_runner(
                "briefing",
                "--timeout",
                "1",
                runner_path=runner_path,
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
                FAKE_CHILD_ESCAPE="1",
            )
            elapsed = time.monotonic() - started
            self.assertEqual(result.returncode, 4, result.stderr)
            self.assertIn("OPUS_STARTED", result.stderr)
            self.assertIn("OPUS_TIMEOUT", result.stderr)
            self.assertLess(elapsed, 1.8, f"timeout aguardou pipe herdado por {elapsed:.2f}s")
            self.assertTrue(
                self.wait_for_marker(paths["ready"], 0.7),
                "filho que reteve pipe nao iniciou; a guarda seria vacua",
            )
            self.assertFalse(paths["late"].exists(), "runner esperou o filho escapar ate concluir")
            completed = True
        finally:
            paths["stop"].write_text("stop", encoding="utf-8")
            cleaned = self.wait_for_marker(paths["done"], 1.0)
            if completed:
                self.assertTrue(cleaned, "cleanup cooperativo do fixture nao confirmou o fim do filho")

    def test_returns_parecer_only_after_proving_opus_55(self) -> None:
        result = self.run_runner("revise", "--model", "claude-opus-5-5",
                                 FAKE_EXPECT_MODEL="claude-opus-5-5", FAKE_MODEL="claude-opus-5-5")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PARECER_OK")
        self.assertIn("OPUS_STARTED", result.stderr)
        self.assertIn("OPUS_MODEL=claude-opus-5-5 ", result.stderr)

    def test_default_timeout_accommodates_real_opus_review_latency(self) -> None:
        result = self.run_runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("TIMEOUT=600s", result.stderr)

    def test_rejects_alias_resolving_to_a_different_model(self) -> None:
        result = self.run_runner(FAKE_MODEL="claude-opus-4-1")
        self.assertEqual(result.returncode, 7)
        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_runs_the_requested_anthropic_model_and_proves_it(self) -> None:
        """`--model fable` roda Fable — o runner deixou de ser exclusivo do Opus.

        Antes desta capacidade, a trilha `interface` e o `reviewer` no host Codex
        ficavam presos ao Opus: o elenco podia pedir Fable, mas a execução não
        honrava. Elenco que a execução não honra é pior que elenco ausente.
        """
        result = self.run_runner(
            "revise", "--model", "fable",
            FAKE_EXPECT_MODEL="fable", FAKE_MODEL="claude-fable-5-1",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PARECER_OK")
        self.assertIn("MODEL_ALIAS=fable", result.stderr)
        self.assertIn("OPUS_MODEL=claude-fable-5-1", result.stderr)

    def test_rejects_fable_5_0_when_fable_5_1_is_required(self) -> None:
        """Pedir Fable e receber 5.0 é reprovado — o prefixo exige exatamente 5.1.

        `claude-fable-5` como prefixo casaria com `claude-fable-5-0` e daria a
        prova por comprovada mesmo quando o CLI voltou a versão anterior. O
        elenco declara Fable 5.1; o verificador precisa exigir esse degrau.
        """
        result = self.run_runner(
            "revise", "--model", "fable",
            FAKE_EXPECT_MODEL="fable", FAKE_MODEL="claude-fable-5-0",
        )
        self.assertEqual(result.returncode, 7)
        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)
        self.assertIn("esperado claude-fable-5-1", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_proof_is_per_alias_not_hardcoded_to_opus(self) -> None:
        """Pedir Fable e receber Opus é reprovado — a prova acompanha o alias.

        É a propriedade que dá valor ao runner. Generalizar o modelo sem
        generalizar a prova transformaria o verificador em decoração: ele
        aprovaria qualquer modelo desde que fosse Opus.
        """
        result = self.run_runner(
            "revise", "--model", "fable",
            FAKE_EXPECT_MODEL="fable", FAKE_MODEL="claude-opus-5",
        )
        self.assertEqual(result.returncode, 7)
        self.assertIn("claude-fable-5-1", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_unknown_alias_fails_closed_without_calling_claude(self) -> None:
        """Alias fora do mapa não roda: sem prefixo conhecido não há como provar.

        Aceitar um alias desconhecido devolveria saída que o runner não pode
        atribuir a modelo nenhum — exatamente o que ele existe para impedir.
        """
        marker = Path(self.tmp.name) / "nunca-chamado"
        result = self.run_runner(
            "revise", "--model", "gpt-5.6-sol", FAKE_MARKER=str(marker),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("MODEL_ALIAS_DESCONHECIDO", result.stderr)
        self.assertFalse(marker.exists(), "o CLI não pode ser chamado com alias inválido")

    def test_default_model_preserva_alias_legado_opus(self) -> None:
        """Sem argumento, compatibilidade legada; fábrica 5.5 exige --model."""
        result = self.run_runner(FAKE_EXPECT_MODEL="opus", FAKE_MODEL="claude-opus-5")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL_ALIAS=opus ", result.stderr)

    def test_explicit_opus_55_accepts_only_exact_identity(self) -> None:
        for observed in ("claude-opus-5-5", "claude-opus-5", "claude-opus-5-6", "claude-opus-5-50",
                         "claude-opus-5-5-20260929", "claude-fable-5-1", "claude-sonnet-5"):
            with self.subTest(observed=observed):
                result = self.run_runner("revise", "--model", "claude-opus-5-5",
                                         FAKE_EXPECT_MODEL="claude-opus-5-5", FAKE_MODEL=observed)
                self.assertEqual(result.returncode, 0 if observed == "claude-opus-5-5" else 7,
                                 result.stderr)
                self.assertEqual(result.stdout.strip(), "PARECER_OK" if observed == "claude-opus-5-5" else "")

    def test_fable_requested_opus_55_observed_is_rejected(self) -> None:
        result = self.run_runner("revise", "--model", "fable",
                                 FAKE_EXPECT_MODEL="fable", FAKE_MODEL="claude-opus-5-5")
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_legacy_aliases_keep_their_release_prefixes(self) -> None:
        for alias, prefix in (("opus", "claude-opus-5"), ("fable", "claude-fable-5-1"),
                              ("sonnet", "claude-sonnet-5"), ("haiku", "claude-haiku-4-5")):
            with self.subTest(alias=alias):
                result = self.run_runner("revise", "--model", alias,
                                         FAKE_EXPECT_MODEL=alias, FAKE_MODEL=prefix + "-20260929")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "PARECER_OK")
                self.assertIn("OPUS_MODEL=" + prefix + "-20260929 ", result.stderr)

    def test_alias_com_versao_numerica_registra_identidade_reconhecida(self) -> None:
        result = self.run_runner(FAKE_MODEL="claude-opus-5-6")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OPUS_MODEL=claude-opus-5-6 ", result.stderr)
        self.assertNotIn("OPUS_MODEL=<nao-reconhecido>", result.stderr)

    def test_rejects_oversized_briefing_before_calling_claude(self) -> None:
        marker = Path(self.tmp.name) / "called"
        result = self.run_runner(
            "123456",
            "--max-input-bytes",
            "5",
            FAKE_MARKER=str(marker),
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("BRIEFING_TOO_LARGE", result.stderr)
        self.assertFalse(marker.exists(), "Claude não pode ser invocado antes do limite de entrada")

    def test_reports_timeout_instead_of_hanging(self) -> None:
        result = self.run_runner("briefing", "--timeout", "0.05", FAKE_SLEEP="0.5")
        self.assertEqual(result.returncode, 4)
        self.assertIn("OPUS_STARTED", result.stderr)
        self.assertIn("OPUS_TIMEOUT", result.stderr)

    def test_sends_briefing_only_over_stdin(self) -> None:
        briefing = "diff privado que não pode aparecer no argv"
        result = self.run_runner(briefing, FAKE_EXPECT_STDIN=briefing)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_timeout_terminates_started_child_before_late_marker(self) -> None:
        self.assert_timeout_cancels_started_child()

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_timeout_kills_same_group_child_that_ignores_term_without_pipes(self) -> None:
        self.assert_timeout_kills_term_ignoring_same_group_child()

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_timeout_kills_same_group_child_after_parent_exits_with_pipe(self) -> None:
        self.assert_timeout_kills_same_group_child_after_parent_exits()

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_parent_exit_pipe_fixture_positive_control_reaches_late_marker(self) -> None:
        paths = self.timeout_child_paths()
        try:
            result = self.run_runner(
                "briefing",
                "--timeout",
                "5",
                outer_timeout=6,
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_PARENT_SLEEP="0",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
                FAKE_CHILD_GROUP=str(paths["group"]),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(self.wait_for_marker(paths["ready"], 0.7))
            self.assertTrue(self.wait_for_marker(paths["late"], 0.7))
        finally:
            self.cleanup_fixture_group(paths["group"])

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_term_ignoring_same_group_fixture_positive_control_reaches_late_marker(self) -> None:
        paths = self.timeout_child_paths()
        try:
            result = self.run_runner(
                "briefing",
                "--timeout",
                "7",
                outer_timeout=8,
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_PARENT_SLEEP="5",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
                FAKE_CHILD_GROUP=str(paths["group"]),
                FAKE_CHILD_IGNORE_TERM="1",
                FAKE_CHILD_DEVNULL="1",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(self.wait_for_marker(paths["ready"], 0.7))
            self.assertTrue(self.wait_for_marker(paths["late"], 0.7))
        finally:
            self.cleanup_fixture_group(paths["group"])

    def test_timeout_does_not_wait_for_child_that_escapes_and_holds_pipe(self) -> None:
        self.assert_timeout_returns_with_escaped_pipe_holder()

    def test_mutacao_sem_nova_sessao_deixa_filho_vivo(self) -> None:
        mutated = self.write_mutated_runner(
            "start_new_session=POSIX,\n        )",
            "start_new_session=False,\n        )",
        )
        with self.assertRaisesRegex(AssertionError, "filho iniciado sobreviveu"):
            self.assert_timeout_cancels_started_child(runner_path=mutated)

    def test_mutacao_sinaliza_so_pai_e_deixa_filho_vivo(self) -> None:
        mutated = self.write_mutated_runner("os.killpg(group_id, sig)", "process.send_signal(sig)")
        with self.assertRaisesRegex(AssertionError, "filho iniciado sobreviveu"):
            self.assert_timeout_cancels_started_child(runner_path=mutated)

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_mutacao_consulta_lider_apos_saida_deixa_filho_vivo(self) -> None:
        mutated = self.write_mutated_runner(
            "return process.pid",
            "try:\n        return os.getpgid(process.pid)\n    except ProcessLookupError:\n        return None",
        )
        with self.assertRaisesRegex(AssertionError, "filho no grupo proprio sobreviveu"):
            self.assert_timeout_kills_same_group_child_after_parent_exits(runner_path=mutated)

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_mutacao_sinaliza_so_lider_apos_saida_deixa_filho_vivo(self) -> None:
        mutated = self.write_mutated_runner("os.killpg(group_id, sig)", "process.send_signal(sig)")
        with self.assertRaisesRegex(AssertionError, "filho no grupo proprio sobreviveu"):
            self.assert_timeout_kills_same_group_child_after_parent_exits(runner_path=mutated)

    @unittest.skipUnless(os.name == "posix", "grupo de processo exclusivo requer POSIX")
    def test_mutacao_retorno_apos_term_eof_deixa_filho_ignora_term_vivo(self) -> None:
        mutated = self.write_mutated_runner(
            "signal_owned_process_group(process, group_id, signal.SIGKILL)",
            "return process.communicate(timeout=TERMINATION_GRACE_SECONDS)",
        )
        with self.assertRaisesRegex(AssertionError, "filho no grupo proprio ignorou TERM"):
            self.assert_timeout_kills_term_ignoring_same_group_child(runner_path=mutated)

    def test_mutacao_sem_handshake_reprova_oraculo(self) -> None:
        with self.assertRaisesRegex(AssertionError, "guarda de sobrevivencia seria vacua"):
            self.assert_timeout_cancels_started_child(skip_ready=True)

    def test_mutacao_espera_pipe_escapado_reprova_limite(self) -> None:
        mutated = self.write_mutated_runner(
            "process.communicate(timeout=TERMINATION_GRACE_SECONDS)",
            "process.communicate()",
        )
        with self.assertRaisesRegex(AssertionError, "timeout aguardou pipe herdado"):
            self.assert_timeout_returns_with_escaped_pipe_holder(runner_path=mutated)

    def test_timeout_child_fixture_positive_control_reaches_late_marker(self) -> None:
        paths = self.timeout_child_paths()
        try:
            result = self.run_runner(
                "briefing",
                "--timeout",
                "5",
                FAKE_TIMEOUT_CHILD="1",
                FAKE_CHILD_PARENT_SLEEP="2.4",
                FAKE_CHILD_READY=str(paths["ready"]),
                FAKE_CHILD_LATE=str(paths["late"]),
                FAKE_CHILD_STOP=str(paths["stop"]),
                FAKE_CHILD_DONE=str(paths["done"]),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(self.wait_for_marker(paths["ready"], 0.7))
            self.assertTrue(self.wait_for_marker(paths["late"], 0.7))
        finally:
            paths["stop"].write_text("stop", encoding="utf-8")
            self.wait_for_marker(paths["done"], 1.0)

    def test_invalid_claude_bin_override_is_named_explicitly(self) -> None:
        env = os.environ.copy()
        env["CLAUDE_BIN"] = str(Path(self.tmp.name) / "missing-claude")
        result = subprocess.run(
            [sys.executable, str(RUNNER)],
            input="briefing",
            text=True,
            capture_output=True,
            env=env,
            timeout=5,
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("CLAUDE_BIN_INVALID", result.stderr)

    def test_rejects_empty_briefing(self) -> None:
        result = self.run_runner("")
        self.assertEqual(result.returncode, 2)
        self.assertIn("BRIEFING_EMPTY", result.stderr)

    def test_rejects_invalid_json(self) -> None:
        result = self.run_runner(FAKE_RAW_STDOUT="not-json")
        self.assertEqual(result.returncode, 6)
        self.assertIn("OPUS_INVALID_JSON", result.stderr)

    def test_rejects_empty_result(self) -> None:
        result = self.run_runner(FAKE_RESULT="")
        self.assertEqual(result.returncode, 8)
        self.assertIn("OPUS_EMPTY_RESULT", result.stderr)

    def test_rejects_api_error_even_with_exit_zero(self) -> None:
        result = self.run_runner(FAKE_IS_ERROR="1")
        self.assertEqual(result.returncode, 5)
        self.assertIn("OPUS_API_ERROR", result.stderr)

    def test_subtype_presente_desconhecido_ou_invalido_falha_sem_expor_valor(self) -> None:
        base = {"result": "PARECER_OK", "modelUsage": {"claude-opus-5": {}}}
        for nome, marcador, esperado in (
            ("ausente legado", {}, 0),
            ("success", {"subtype": "success"}, 0),
            ("futuro", {"subtype": "future_result"}, 5),
            ("tipo inválido", {"subtype": 55}, 5),
            ("null presente", {"subtype": None}, 5),
        ):
            with self.subTest(subtype=nome):
                raw = json.dumps({**base, **marcador})
                result = self.run_runner(FAKE_RAW_STDOUT=raw)
                self.assertEqual(result.returncode, esperado, result.stderr)
                self.assertEqual(result.stdout.strip(), "PARECER_OK" if esperado == 0 else "")
                if esperado:
                    self.assertIn("OPUS_INVALID_SUBTYPE", result.stderr)
                    self.assertNotIn("future_result", result.stderr)

    def test_rejects_missing_model_usage(self) -> None:
        result = self.run_runner(FAKE_NO_MODEL="1")
        self.assertEqual(result.returncode, 7)
        self.assertIn("observado <ausente>", result.stderr)

    def test_rejects_multiple_incompatible_model_usage_keys(self) -> None:
        result = self.run_runner(FAKE_EXTRA_MODEL="claude-haiku-4-5")
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)

    def test_rejects_uso_ambiguo_da_mesma_familia(self) -> None:
        result = self.run_runner(
            FAKE_MODEL="claude-opus-5-6",
            FAKE_EXTRA_MODEL="claude-opus-5",
        )
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_unknown_model_usage_key_fails_without_vazar_a_chave(self) -> None:
        chave_sensivel = "SYNTHETIC_PII_modelUsage_chave_desconhecida"
        result = self.run_runner(FAKE_EXTRA_MODEL=chave_sensivel)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)
        self.assertNotIn(chave_sensivel, result.stderr)

    def test_api_error_message_is_bounded(self) -> None:
        result = self.run_runner(FAKE_IS_ERROR="1", FAKE_RESULT="E" * 10_000)
        self.assertEqual(result.returncode, 5)
        self.assertIn("OPUS_API_ERROR", result.stderr)
        self.assertLess(len(result.stderr), 2_500)


class OpusReviewerMutationTest(unittest.TestCase):
    """Mutações em memória; o produto e o CLI real nunca são escritos/invocados."""

    def conferir_contrato(self, fonte: str) -> None:
        ns = {"__name__": "runner_t131_mutation"}
        exec(compile(fonte, str(RUNNER), "exec"), ns)
        with mock.patch("sys.argv", ["runner"]):
            self.assertEqual(ns["parse_args"]().model, "opus")
        for solicitado, observados, subtype, esperado in (
            ("claude-opus-5-5", ("claude-opus-5-50",), None, 7),
            ("claude-opus-5-5", ("claude-opus-5-5-20260929",), None, 7),
            ("claude-opus-5-5", ("claude-opus-5-5",), "success", 0),
            ("fable", ("claude-opus-5-5",), None, 7),
            ("opus", ("claude-opus-5-20260929",), "future_result", 5),
            ("opus", ("claude-opus-5-20260929",), None, 0),
            ("opus", ("claude-opus-5-6",), None, 0),
            ("opus", ("claude-opus-5", "claude-haiku-4-5"), None, 7),
            ("opus", ("claude-opus-5", "claude-opus-5-6"), None, 7),
            ("opus", ("claude-opus-5", "SYNTHETIC_PII_modelUsage"), None, 7),
        ):
            ns["parse_args"] = lambda: argparse.Namespace(
                model=solicitado, timeout=600, max_input_bytes=16384)
            ns["resolve_claude"] = lambda: "/fake/claude"

            def cli_popen(command, **kwargs):
                self.assertEqual(command[command.index("--model") + 1], solicitado)
                self.assertEqual(kwargs["stdin"], subprocess.PIPE)
                self.assertEqual(kwargs["stdout"], subprocess.PIPE)
                self.assertEqual(kwargs["stderr"], subprocess.PIPE)
                payload = {"result": "PARECER_OK", "modelUsage": {observado: {} for observado in observados}}
                if subtype is not None:
                    payload["subtype"] = subtype
                case = self

                class FakeProcess:
                    pid = None
                    returncode = 0

                    def communicate(self, *, input=None, timeout=None):
                        case.assertEqual(input, "briefing sintético".encode())
                        case.assertEqual(timeout, 600)
                        return json.dumps(payload).encode(), b""

                return FakeProcess()

            out, err = io.StringIO(), io.StringIO()
            with mock.patch("sys.stdin", io.TextIOWrapper(io.BytesIO("briefing sintético".encode()))), \
                    mock.patch("subprocess.Popen", side_effect=cli_popen), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                codigo = ns["main"]()
            self.assertEqual(codigo, esperado, err.getvalue())
            self.assertEqual(out.getvalue().strip(), "PARECER_OK" if esperado == 0 else "")
            if esperado == 0:
                self.assertNotIn("OPUS_MODEL=<nao-reconhecido>", err.getvalue())
            self.assertNotIn("SYNTHETIC_PII_modelUsage", err.getvalue())

    def test_controle_original_passando(self) -> None:
        self.conferir_contrato(RUNNER.read_text())

    def test_seis_regressoes_do_runner_sao_mortas(self) -> None:
        fonte = RUNNER.read_text()
        for nome, de, para in (
            ("default legado trocado", 'DEFAULT_MODEL_ALIAS = "opus"', 'DEFAULT_MODEL_ALIAS = "claude-opus-5-5"'),
            ("Fable redirecionado", '"fable": "claude-fable-5-1"', '"fable": "claude-opus-5-5"'),
            ("alias opus alterado", '"opus": "claude-opus-5"', '"opus": "claude-opus-5-5"'),
            ("subtipo futuro aceito",
             "if \"subtype\" in payload and (not isinstance(subtype, str) or subtype not in RESULT_SUBTYPES):",
             "if False:"),
            ("identidade explicita aceita sufixo", "exact=exact_identity", "exact=False"),
            ("uso multiplo aceito", "if len(model_names) != 1 or len(matching_models) != 1:",
             "if len(matching_models) != 1:"),
        ):
            with self.subTest(mutante=nome):
                self.assertEqual(fonte.count(de), 1, "mutação deixou de ser aplicável")
                mutante = fonte.replace(de, para, 1)
                with self.assertRaises(AssertionError):
                    self.conferir_contrato(mutante)


if __name__ == "__main__":
    unittest.main()
