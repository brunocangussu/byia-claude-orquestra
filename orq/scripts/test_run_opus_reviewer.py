#!/usr/bin/env python3
"""Testes stdlib do runner determinístico do reviewer Opus."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest


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
                time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
                expected = [
                    "-p", "--model", "opus", "--permission-mode", "plan", "--tools", "",
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
        **env_overrides: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CLAUDE_BIN"] = str(self.fake)
        env.update(env_overrides)
        return subprocess.run(
            [sys.executable, str(RUNNER), *args],
            input=briefing,
            text=True,
            capture_output=True,
            env=env,
            timeout=5,
        )

    def test_returns_parecer_only_after_proving_opus_5(self) -> None:
        result = self.run_runner()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PARECER_OK")
        self.assertIn("OPUS_STARTED", result.stderr)
        self.assertIn("OPUS_MODEL=claude-opus-5", result.stderr)

    def test_rejects_alias_resolving_to_a_different_model(self) -> None:
        result = self.run_runner(FAKE_MODEL="claude-opus-4-1")
        self.assertEqual(result.returncode, 7)
        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)
        self.assertEqual(result.stdout, "")

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

    def test_timeout_kills_process_group_without_waiting_for_pipe_holder(self) -> None:
        child_marker = Path(self.tmp.name) / "child-survived"
        started = time.monotonic()
        result = self.run_runner(
            "briefing",
            "--timeout",
            "0.05",
            FAKE_SPAWN_HOLDER="1",
            FAKE_CHILD_MARKER=str(child_marker),
        )
        elapsed = time.monotonic() - started
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertLess(elapsed, 1.0, f"timeout levou {elapsed:.2f}s; descendente manteve pipe aberto")
        time.sleep(0.7)
        self.assertFalse(child_marker.exists(), "descendente do Claude sobreviveu ao timeout")

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

    def test_rejects_missing_model_usage(self) -> None:
        result = self.run_runner(FAKE_NO_MODEL="1")
        self.assertEqual(result.returncode, 7)
        self.assertIn("observado <ausente>", result.stderr)

    def test_success_logs_every_model_used_for_audit(self) -> None:
        result = self.run_runner(FAKE_EXTRA_MODEL="claude-haiku-4-5")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OPUS_MODEL_USAGE=claude-haiku-4-5,claude-opus-5", result.stderr)

    def test_api_error_message_is_bounded(self) -> None:
        result = self.run_runner(FAKE_IS_ERROR="1", FAKE_RESULT="E" * 10_000)
        self.assertEqual(result.returncode, 5)
        self.assertIn("OPUS_API_ERROR", result.stderr)
        self.assertLess(len(result.stderr), 2_500)


if __name__ == "__main__":
    unittest.main()
