#!/usr/bin/env python3
"""Recibos e cadeia wrapper→CLI falsa: somente fixtures locais, sem rede."""

from __future__ import annotations

import hashlib
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock


RUNNER = Path(__file__).with_name("run-opus-reviewer.py")
RECEIPT_PREFIX = "OPUS_PROCESS_RECEIPT "
SYNTHETIC_SECRET = "sk-ant-TESTE-NAO-REAL"
SYNTHETIC_PII = "paciente-ficticio@example.invalid"
SYNTHETIC_UNICODE_BRIEFING = "briefing-fictício-🧪"


class OpusDiagnosticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-receipt-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cwd = self.root / "cwd-vazio"
        self.cwd.mkdir()
        self.observed = self.root / "observed.jsonl"
        self.wrapper_log = self.root / "wrapper.log"
        self.leaf = self.root / "fake-cli"
        self.leaf.write_text(textwrap.dedent(f"""\
            #!{sys.executable}
            import hashlib,json,os,sys,time
            from pathlib import Path
            raw = sys.stdin.buffer.read()
            observation = {{"args":sys.argv[1:], "stdin_bytes":len(raw),
                "stdin_sha256":hashlib.sha256(raw).hexdigest(),
                "cwd_empty":not any(Path.cwd().iterdir())}}
            with open(os.environ["FAKE_OBSERVED"], "a") as out:
                out.write(json.dumps(observation) + "\\n")
            stdout = bytes.fromhex(os.environ["FAKE_STDOUT_HEX"]) if "FAKE_STDOUT_HEX" in os.environ else os.environ["FAKE_STDOUT"].encode()
            sys.stdout.buffer.write(stdout)
            sys.stdout.buffer.flush()
            sys.stderr.buffer.write(os.environ.get("FAKE_STDERR", "").encode())
            sys.stderr.buffer.flush()
            time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
            raise SystemExit(int(os.environ.get("FAKE_EXIT", "0")))
            """), encoding="utf-8")
        self.leaf.chmod(0o755)
        # Mesmo corpo do wrap-claude.sh da R3. Substituído SOMENTE o alvo exec;
        # a CLI real não pode ser invocada e --safe-mode permanece no wrapper.
        self.wrapper = self.root / "wrap-claude.sh"
        self.wrapper.write_text(
            '#!/bin/sh\n'
            'echo "ARGS: $*" >> "${WRAP_LOG:-/dev/null}"\n'
            f'exec "{self.leaf}" "$@" --safe-mode\n', encoding="utf-8")
        self.wrapper.chmod(0o755)

    def invoke(self, payload: str, *, cli_exit: int = 0, stderr: str = "",
               sleep: str = "0", timeout: str = "2", stdout_hex: str | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(CLAUDE_BIN=str(self.wrapper), FAKE_STDOUT=payload,
                   FAKE_STDERR=stderr, FAKE_EXIT=str(cli_exit), FAKE_SLEEP=sleep,
                   FAKE_OBSERVED=str(self.observed), WRAP_LOG=str(self.wrapper_log),
                   PYTHONDONTWRITEBYTECODE="1")
        if stdout_hex is not None:
            env["FAKE_STDOUT_HEX"] = stdout_hex
        return subprocess.run([sys.executable, str(RUNNER), "--model",
                               "claude-opus-5-5", "--timeout", timeout],
                              input="briefing sintético\r\nlinha 2\n", text=True,
                              capture_output=True, env=env, cwd=self.cwd, timeout=5)

    def receipt(self, result: subprocess.CompletedProcess[str]) -> dict:
        lines = [x[len(RECEIPT_PREFIX):] for x in result.stderr.splitlines()
                 if x.startswith(RECEIPT_PREFIX)]
        self.assertEqual(len(lines), 1, "cada tentativa deve ter um recibo independente")
        return json.loads(lines[0])

    def assert_chain(self) -> None:
        calls = self.observed.read_text().splitlines()
        self.assertEqual(len(calls), 1, "nenhum retry nem segundo processo de CLI")
        observation = json.loads(calls[0])
        self.assertEqual(observation["args"], [
            "-p", "--model", "claude-opus-5-5", "--permission-mode", "plan",
            "--tools", "", "--setting-sources", "", "--disable-slash-commands",
            "--no-session-persistence", "--output-format", "json", "--safe-mode"])
        raw = "briefing sintético\r\nlinha 2\n".encode()
        self.assertEqual(observation["stdin_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(observation["stdin_bytes"], len(raw))
        self.assertIs(observation["cwd_empty"], True)
        self.assertEqual(self.wrapper_log.read_text().count("ARGS:"), 1)
        self.assertNotIn("briefing", self.wrapper_log.read_text())

    def assert_private(self, result: subprocess.CompletedProcess[str]) -> None:
        for forbidden in (SYNTHETIC_SECRET, SYNTHETIC_PII, "briefing sintético"):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def assert_decoded_private(self, receipt: dict) -> None:
        decodificado = json.dumps(receipt, ensure_ascii=False, sort_keys=True)
        for forbidden in (SYNTHETIC_SECRET, SYNTHETIC_PII, SYNTHETIC_UNICODE_BRIEFING):
            self.assertNotIn(forbidden, decodificado,
                             f"marcador livre presente no recibo JSON decodificado: {forbidden!r}")

    def test_nonzero_json_error_is_preserved_as_metadata_not_verdict(self) -> None:
        raw = json.dumps({"is_error":True, "subtype":"error_during_execution",
                          "error":{"type":"authentication_error", "message":SYNTHETIC_SECRET},
                          "result":SYNTHETIC_PII})
        result = self.invoke(raw, cli_exit=1)
        self.assertEqual(result.returncode, 5, result.stderr)
        self.assertEqual(result.stdout, "")
        receipt = self.receipt(result)
        self.assertEqual(receipt["cli_exit"], 1)
        self.assertEqual(receipt["diagnostic"]["error_code"], "authentication_error")
        self.assertEqual(receipt["diagnostic"]["subtype"], "error_during_execution")
        self.assertIs(receipt["diagnostic"]["is_error"], True)
        self.assertEqual(receipt["stdout"]["bytes"], len(raw.encode()))
        self.assertEqual(receipt["stdout"]["sha256"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertIsNone(receipt["observed_model"])
        self.assertIsNone(receipt["cost_usd"])
        self.assert_private(result)
        self.assert_chain()

    def test_nonzero_plain_streams_are_fingerprinted_without_echo(self) -> None:
        raw = SYNTHETIC_SECRET + "\r\n" + SYNTHETIC_PII
        err = SYNTHETIC_PII + "\r\n" + SYNTHETIC_SECRET
        result = self.invoke(raw, cli_exit=1, stderr=err)
        self.assertEqual(result.returncode, 5)
        self.assertEqual(result.stdout, "")
        receipt = self.receipt(result)
        self.assertEqual(receipt["stdout"]["sha256"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(receipt["stderr"]["bytes"], len(err.encode()))
        self.assertEqual(receipt["stderr"]["sha256"], hashlib.sha256(err.encode()).hexdigest())
        self.assertEqual(receipt["diagnostic"]["format"], "invalid_json")
        self.assert_private(result)
        self.assert_chain()

    def test_exit_zero_api_error_never_leaks_result_or_unknown_metadata(self) -> None:
        raw = json.dumps({"is_error":True,"subtype":SYNTHETIC_SECRET,
                          "error":{"type":SYNTHETIC_PII}, "result":SYNTHETIC_SECRET})
        result = self.invoke(raw)
        self.assertEqual(result.returncode, 5)
        self.assertEqual(result.stdout, "")
        receipt = self.receipt(result)
        self.assertIsNone(receipt["diagnostic"]["error_code"])
        self.assertIsNone(receipt["diagnostic"]["subtype"])
        self.assert_private(result)

    def test_unicode_escapado_em_campo_livre_nao_vaza_no_recibo_decodificado(self) -> None:
        raw = json.dumps({
            "is_error": True,
            "subtype": "error_during_execution",
            "error": {"type": "authentication_error"},
            "diagnostic": {"briefing": SYNTHETIC_UNICODE_BRIEFING},
            "result": SYNTHETIC_SECRET,
        }, ensure_ascii=True)
        self.assertIn("\\u", raw)
        result = self.invoke(raw)
        self.assertEqual(result.returncode, 5, result.stderr)
        receipt = self.receipt(result)
        self.assert_decoded_private(receipt)
        self.assert_private(result)
        self.assert_chain()

    def test_empty_failure_streams_stay_unknown_not_zero_cost(self) -> None:
        result = self.invoke("", cli_exit=1)
        self.assertEqual(result.returncode, 5)
        receipt = self.receipt(result)
        self.assertEqual(receipt["stdout"]["bytes"], 0)
        self.assertEqual(receipt["stderr"]["bytes"], 0)
        self.assertIsNone(receipt["observed_model"])
        self.assertIsNone(receipt["cost_usd"])
        self.assertIsNone(receipt["provider_request_sent"])

    def test_structured_error_without_is_error_is_never_a_verdict(self) -> None:
        for marker in ({"subtype":"error_during_execution"},
                       {"error":{"type":"authentication_error"}},
                       {"error_code":"authentication_error"},
                       {"errors":[SYNTHETIC_SECRET]}):
            with self.subTest(marker=next(iter(marker))):
                raw = json.dumps({"is_error":False,"result":SYNTHETIC_SECRET,
                                  "modelUsage":{"claude-opus-5-5":{}}, **marker})
                result = self.invoke(raw)
                self.assertEqual(result.returncode, 5)
                self.assertEqual(result.stdout, "")
                self.assert_private(result)

    def test_outcome_and_process_receipt_share_attempt_identity(self) -> None:
        for cli_exit, raw, expected_exit in (
            (1, "", 5), (0, "[]", 6),
            (0, '{"result":"PARECER_OK","modelUsage":{"claude-opus-5-5":{}}}', 0),
        ):
            with self.subTest(cli_exit=cli_exit, expected=expected_exit):
                result = self.invoke(raw, cli_exit=cli_exit)
                receipt = self.receipt(result)
                outcomes = [json.loads(x[len("OPUS_OUTCOME "):]) for x in result.stderr.splitlines()
                            if x.startswith("OPUS_OUTCOME ")]
                self.assertEqual(len(outcomes), 1)
                self.assertEqual(outcomes[0]["runner_exit"], expected_exit)
                self.assertEqual(outcomes[0].get("attempt_id"), receipt["attempt_id"])
                self.assertIs(outcomes[0]["has_verdict"], expected_exit == 0)

    def test_invalid_json_and_nonobject_json_have_receipts_and_no_traceback(self) -> None:
        for raw in (SYNTHETIC_SECRET, "[]", "null", '"' + SYNTHETIC_PII + '"'):
            with self.subTest(shape=raw[:5]):
                result = self.invoke(raw)
                self.assertEqual(result.returncode, 6, result.stderr)
                self.assertEqual(result.stdout, "")
                self.receipt(result)
                self.assertNotIn("Traceback", result.stderr)
                self.assert_private(result)

    def test_success_has_receipt_before_verdict_and_proves_wrapper_chain(self) -> None:
        raw = json.dumps({"result":"PARECER_OK", "modelUsage":{"claude-opus-5-5":{}}})
        result = self.invoke(raw)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "PARECER_OK")
        receipt = self.receipt(result)
        self.assertEqual(receipt["cli_exit"], 0)
        self.assertEqual(receipt["source_sha256"], hashlib.sha256(RUNNER.read_bytes()).hexdigest())
        self.assertEqual(receipt["execution"]["entry_sha256"], hashlib.sha256(self.wrapper.read_bytes()).hexdigest())
        self.assertIsNone(receipt["execution"]["entry_version_from_path"])
        self.assertIs(receipt["execution"]["cwd_empty"], True)
        self.assertEqual(receipt["execution"]["args"][0], "-p")
        self.assertLess(result.stderr.index(RECEIPT_PREFIX), result.stderr.index("OPUS_MODEL="))
        self.assert_private(result)
        self.assert_chain()

    def test_timeout_captures_partial_streams_without_leaks_or_retry(self) -> None:
        result = self.invoke(SYNTHETIC_SECRET, stderr=SYNTHETIC_PII,
                             sleep="2", timeout="1")
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertEqual(result.stdout, "")
        receipt = self.receipt(result)
        self.assertIs(receipt["timed_out"], True)
        self.assertIsNone(receipt["cli_exit"])
        self.assertEqual(receipt["stdout"]["bytes"], len(SYNTHETIC_SECRET.encode()))
        self.assert_private(result)
        self.assert_chain()

    def test_failure_privacy_is_independent_of_receipt_presence(self) -> None:
        for code, raw, err in (
            (1, SYNTHETIC_PII, SYNTHETIC_SECRET),
            (0, json.dumps({"is_error":True,"result":SYNTHETIC_SECRET}), SYNTHETIC_PII),
            (1, json.dumps({"is_error":False,"result":SYNTHETIC_SECRET,
                             "modelUsage":{"claude-opus-5-5":{}}}), ""),
        ):
            with self.subTest(cli_exit=code):
                result = self.invoke(raw, cli_exit=code, stderr=err)
                self.assertEqual(result.returncode, 5)
                self.assertEqual(result.stdout, "")
                self.assert_private(result)

    def test_start_failure_has_receipt_and_unknown_streams_without_retry(self) -> None:
        self.wrapper.write_text("#!/nao/existe/interprete\n", encoding="utf-8")
        result = self.invoke("{}"); receipt = self.receipt(result)
        self.assertEqual(result.returncode, 3)
        self.assertIsNone(receipt["cli_exit"])
        self.assertIsNone(receipt["stdout"]["bytes"])
        self.assertIs(receipt["timed_out"], False)
        self.assertFalse(self.observed.exists())
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_utf8_stream_keeps_exact_binary_fingerprint(self) -> None:
        raw = b"\xff\x00\r\n"
        result = self.invoke("", stdout_hex=raw.hex())
        self.assertEqual(result.returncode, 6, result.stderr)
        receipt = self.receipt(result)
        self.assertEqual(receipt["stdout"]["bytes"], len(raw))
        self.assertEqual(receipt["stdout"]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.stdout, "")
        self.assertNotIn("Traceback", result.stderr)

    def test_deep_nonobject_json_has_receipt_instead_of_parser_traceback(self) -> None:
        result = self.invoke("[" * 1100 + "]" * 1100)
        self.assertEqual(result.returncode, 6, result.stderr[-200:])
        self.assertIn(self.receipt(result)["diagnostic"]["format"], ("invalid_json", "json_non_object"))
        self.assertNotIn("Traceback", result.stderr)

    def test_parser_recursion_failure_is_quarantined_without_cli(self) -> None:
        namespace = {"__name__":"t131_parser_test", "__file__":str(RUNNER)}
        exec(compile(RUNNER.read_text(), str(RUNNER), "exec"), namespace)
        with mock.patch.object(namespace["json"], "loads", side_effect=RecursionError):
            self.assertEqual(namespace["read_payload"](b"[]"), (None, "invalid_json"))


class OpusDiagnosticMutationTest(unittest.TestCase):
    """Oráculo em memória: subprocesso substituído, nunca Anthropic real."""

    def check_contract(self, source: str) -> None:
        namespace = {"__name__":"t131_receipt_mutation", "__file__":str(RUNNER)}
        exec(compile(source, str(RUNNER), "exec"), namespace)
        namespace["parse_args"] = lambda: argparse.Namespace(
            model="claude-opus-5-5", timeout=600, max_input_bytes=16_384)
        namespace["resolve_claude"] = lambda: "/fixture/claude-inexistente"
        raw_json = json.dumps({"is_error":True,"subtype":"error_during_execution",
                               "error":{"type":"authentication_error"},
                               "result":SYNTHETIC_SECRET}).encode()
        cases = [
            (1, raw_json, SYNTHETIC_PII.encode(), 5),
            (1, json.dumps({"result":SYNTHETIC_SECRET,
                           "modelUsage":{"claude-opus-5-5":{}}}).encode(), b"", 5),
            (1, (SYNTHETIC_SECRET + "\r\n" + SYNTHETIC_PII).encode(), b"", 5),
            (0, json.dumps({"is_error":True,"subtype":SYNTHETIC_SECRET,
                           "error":{"type":SYNTHETIC_PII},"result":SYNTHETIC_SECRET}).encode(), b"", 5),
            (0, json.dumps({"is_error":False,"subtype":"error_during_execution",
                           "modelUsage":{"claude-opus-5-5":{}},"result":SYNTHETIC_SECRET}).encode(), b"", 5),
        ]
        for cli_exit, stdout, stderr, expected_exit in cases:
            processes = []

            class FakeProcess:
                def __init__(self) -> None:
                    self.returncode = cli_exit
                    self.communicate_calls = []

                def communicate(self, *, input=None, timeout=None):
                    self.communicate_calls.append((input, timeout))
                    return stdout, stderr

            def fake_popen(command, **kwargs):
                self.assertEqual(kwargs["stdin"], subprocess.PIPE)
                self.assertEqual(kwargs["stdout"], subprocess.PIPE)
                self.assertEqual(kwargs["stderr"], subprocess.PIPE)
                self.assertEqual(kwargs["start_new_session"], namespace["POSIX"])
                process = FakeProcess()
                processes.append(process)
                return process

            out, err = io.StringIO(), io.StringIO()
            with mock.patch("sys.stdin", io.TextIOWrapper(io.BytesIO(b"briefing\r\n"))), \
                    mock.patch("subprocess.Popen", side_effect=fake_popen) as call, \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                actual_exit = namespace["main"]()
            self.assertEqual(actual_exit, expected_exit)
            self.assertEqual(out.getvalue(), "")
            self.assertEqual(call.call_count, 1)
            self.assertEqual(processes[0].communicate_calls, [(b"briefing\r\n", 600)])
            for secret in (SYNTHETIC_SECRET, SYNTHETIC_PII):
                self.assertNotIn(secret, err.getvalue())
            lines = [x[len(RECEIPT_PREFIX):] for x in err.getvalue().splitlines()
                     if x.startswith(RECEIPT_PREFIX)]
            self.assertEqual(len(lines), 1)
            receipt = json.loads(lines[0])
            outcomes = [json.loads(x[len("OPUS_OUTCOME "):]) for x in err.getvalue().splitlines()
                        if x.startswith("OPUS_OUTCOME ")]
            self.assertEqual(len(outcomes), 1)
            self.assertEqual(outcomes[0].get("attempt_id"), receipt["attempt_id"])
            self.assertEqual(outcomes[0]["runner_exit"], expected_exit)
            self.assertIs(outcomes[0]["has_verdict"], False)
            self.assertEqual(receipt["cli_exit"], cli_exit)
            self.assertIsNone(receipt["cost_usd"])
            self.assertEqual(receipt["stdout"]["bytes"], len(stdout))
            self.assertEqual(receipt["stdout"]["sha256"], hashlib.sha256(stdout).hexdigest())
            if stdout == raw_json:
                self.assertEqual(receipt["diagnostic"]["error_code"], "authentication_error")

    def check_decoded_privacy_contract(self, source: str) -> None:
        namespace = {"__name__": "t131_receipt_unicode_mutation", "__file__": str(RUNNER)}
        exec(compile(source, str(RUNNER), "exec"), namespace)
        namespace["parse_args"] = lambda: argparse.Namespace(
            model="claude-opus-5-5", timeout=600, max_input_bytes=16_384)
        namespace["resolve_claude"] = lambda: "/fixture/claude-inexistente"
        raw = json.dumps({
            "is_error": True,
            "subtype": "error_during_execution",
            "error": {"type": "authentication_error"},
            "diagnostic": {"briefing": SYNTHETIC_UNICODE_BRIEFING},
            "result": SYNTHETIC_SECRET,
        }, ensure_ascii=True).encode()
        processes = []

        class FakeProcess:
            returncode = 0

            def __init__(self) -> None:
                self.communicate_calls = []

            def communicate(self, *, input=None, timeout=None):
                self.communicate_calls.append((input, timeout))
                return raw, b""

        def fake_popen(command, **kwargs):
            self.assertEqual(kwargs["stdin"], subprocess.PIPE)
            self.assertEqual(kwargs["stdout"], subprocess.PIPE)
            self.assertEqual(kwargs["stderr"], subprocess.PIPE)
            self.assertEqual(kwargs["start_new_session"], namespace["POSIX"])
            process = FakeProcess()
            processes.append(process)
            return process

        out, err = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdin", io.TextIOWrapper(io.BytesIO(b"briefing\r\n"))), \
                mock.patch("subprocess.Popen", side_effect=fake_popen) as call, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            actual_exit = namespace["main"]()
        self.assertEqual(actual_exit, 5)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(call.call_count, 1)
        self.assertEqual(processes[0].communicate_calls, [(b"briefing\r\n", 600)])
        lines = [x[len(RECEIPT_PREFIX):] for x in err.getvalue().splitlines()
                 if x.startswith(RECEIPT_PREFIX)]
        self.assertEqual(len(lines), 1)
        receipt = json.loads(lines[0])
        decodificado = json.dumps(receipt, ensure_ascii=False, sort_keys=True)
        self.assertNotIn(SYNTHETIC_UNICODE_BRIEFING, decodificado,
                         "briefing escapado reapareceu no recibo decodificado")

    def test_original_passes_receipt_and_privacy_contract(self) -> None:
        self.check_contract(RUNNER.read_text())
        self.check_decoded_privacy_contract(RUNNER.read_text())

    def test_dez_diagnostic_regressions_are_killed(self) -> None:
        source = RUNNER.read_text()
        for name, old, new in (
            ("recibo descartado", 'print("OPUS_PROCESS_RECEIPT " + json.dumps(receipt, sort_keys=True), file=sys.stderr, flush=True)', 'pass'),
            ("stderr bruto", 'diagnóstico sanitizado no recibo",', 'diagnóstico sanitizado no recibo" + stderr.decode(),'),
            ("stdout tratado como parecer", 'if completed.returncode != 0:', 'if False:'),
            ("JSON do stdout perdido", '"diagnostic": diagnostic_metadata(stdout)', '"diagnostic": diagnostic_metadata(None)'),
            ("custo desconhecido vira zero", '"cost_usd": None', '"cost_usd": 0'),
            ("exit da CLI colapsado", '"cli_exit": cli_exit', '"cli_exit": 0'),
            ("digest normaliza CRLF", 'return value if isinstance(value, bytes) else value.encode("utf-8")', 'return value.replace(b"\\r\\n", b"\\n") if isinstance(value, bytes) else value.encode("utf-8")'),
            ("subtype livre vaza", 'subtype if isinstance(subtype, str) and subtype in RESULT_SUBTYPES else None', 'subtype'),
            ("erro sem is_error vira parecer", 'if payload.get("is_error") or structured_error:', 'if payload.get("is_error"):'),
            ("outcome sem identidade", '"attempt_id": attempt_id,', '"attempt_id": None,'),
        ):
            with self.subTest(mutant=name):
                self.assertEqual(source.count(old), 1, "mutação deve aplicar uma vez")
                with self.assertRaises(AssertionError):
                    self.check_contract(source.replace(old, new, 1))

    def test_mutacao_ensure_ascii_com_briefing_no_diagnostico_e_morta(self) -> None:
        source = RUNNER.read_text()
        antigo = '"diagnostic": diagnostic_metadata(stdout)'
        mutante = '"diagnostic": json.loads(stdout).get("diagnostic")'
        self.assertEqual(source.count(antigo), 1, "mutação deve atingir o recibo real")
        with self.assertRaisesRegex(AssertionError, "briefing escapado"):
            self.check_decoded_privacy_contract(source.replace(antigo, mutante, 1))


if __name__ == "__main__":
    unittest.main()
