#!/usr/bin/env python3
"""Testes do auditor offline de adoção graph-first."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("audit-adoption.py")
GRAPH_TOOL = "mcp__codebase_memory_mcp__search_graph"
SERENA_GRAPH_TOOL = "mcp__serena__find_symbol"


class AuditAdoptionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-audit-adoption-")
        self.addCleanup(self.tmp.cleanup)

    def run_trace(self, payload: object | str) -> subprocess.CompletedProcess[str]:
        trace = Path(self.tmp.name) / "trace.json"
        if isinstance(payload, str):
            trace.write_text(payload, encoding="utf-8")
        else:
            if isinstance(payload, dict) and "events" in payload and "schemaVersion" not in payload:
                payload = {"schemaVersion": "orq.audit-trace.v1", **payload}
            trace.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(trace)],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_graph_first_passes(self) -> None:
        result = self.run_trace(
            {
                "schemaVersion": "orq.audit-trace.v1",
                "events": [
                    {"sequence": 1, "tool": "codebase-memory-mcp.search_graph"},
                    {"sequence": 2, "command": "rg -n legacy src"},
                    {"sequence": 3, "tool": "Read", "path": "src/index.ts"},
                ],
            }
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["firstRelevant"]["category"], "graph")

    def test_direct_read_or_text_search_before_graph_fails(self) -> None:
        for first in (
            {"sequence": 1, "tool": "Read", "path": "src/index.ts"},
            {"sequence": 1, "command": "grep -R legacy src"},
        ):
            with self.subTest(first=first):
                result = self.run_trace(
                    {"events": [first, {"sequence": 2, "tool": SERENA_GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_no_graph_is_not_observed_not_success(self) -> None:
        result = self.run_trace({"events": [{"tool": "Read", "path": "src/index.ts"}]})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "not-observed")

    def test_irrelevant_events_do_not_precede_graph(self) -> None:
        result = self.run_trace(
            {
                "events": [
                    {"tool": "update_plan"},
                    {"data": {"item": {"command": "codebase-memory-mcp index_repository ."}}},
                    {"command": "sed -n '1,20p' src/index.ts"},
                ]
            }
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_graph_terms_in_paths_or_destructive_commands_do_not_fake_graph(self) -> None:
        for first in (
            {"tool": "Read", "path": "docs/query_graph-design.md"},
            {"command": "rm -rf codebase-memory"},
        ):
            with self.subTest(first=first):
                result = self.run_trace({"events": [first, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_native_search_and_write_tools_before_graph_fail(self) -> None:
        for tool in ("Glob", "Search", "Write", "Edit", "MultiEdit"):
            with self.subTest(tool=tool):
                result = self.run_trace({"events": [{"tool": tool}, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_numeric_sequence_controls_order_when_events_arrive_unsorted(self) -> None:
        result = self.run_trace(
            {
                "events": [
                    {"sequence": 20, "tool": "Read", "path": "src/index.ts"},
                    {"sequence": 10, "tool": GRAPH_TOOL},
                ]
            }
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_graph_augmented_search_code_counts_as_graph(self) -> None:
        result = self.run_trace({"events": [{"tool": "mcp__codebase_memory_mcp__search_code"}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_chained_text_search_before_graph_fails(self) -> None:
        result = self.run_trace(
            {"events": [{"command": "pwd; rg legacy src; codebase-memory-mcp search_graph legacy"}]}
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_namespaced_non_graph_tools_before_graph_fail(self) -> None:
        tools = (
            "mcp__filesystem__read_file",
            "mcp__serena__read_file",
            "mcp__github__get_file_contents",
            "mcp__serena__search_for_pattern",
            "ReadFile",
            "WriteFile",
        )
        for tool in tools:
            with self.subTest(tool=tool):
                result = self.run_trace({"events": [{"tool": tool}, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_command_argv_array_is_classified(self) -> None:
        result = self.run_trace(
            {"events": [{"command": ["rg", "-n", "legacy", "src"]}, {"tool": GRAPH_TOOL}]}
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_mixed_or_invalid_sequences_are_invalid_trace(self) -> None:
        cases = (
            {"events": [{"sequence": 100, "tool": "Read"}, {"tool": GRAPH_TOOL}]},
            {"events": [{"sequence": 1.5, "tool": "Read"}]},
            {"events": [{"sequence": -1, "tool": "Read"}]},
            {"events": [{"sequence": 1, "tool": "Read"}, {"sequence": 1, "tool": GRAPH_TOOL}]},
        )
        for payload in cases:
            with self.subTest(payload=payload):
                result = self.run_trace(payload)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "invalid-trace")

    def test_remote_search_code_is_text_search_not_graph(self) -> None:
        result = self.run_trace(
            {"events": [{"tool": "mcp__github__search_code"}, {"tool": GRAPH_TOOL}]}
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_nested_hook_name_cannot_contaminate_bash_command(self) -> None:
        result = self.run_trace(
            {
                "events": [
                    {"tool": "Bash", "command": "rg -n legacy src", "hook": {"name": "search_code"}},
                    {"tool": GRAPH_TOOL},
                ]
            }
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertGreaterEqual(payload["counts"]["graph"], 1)

    def test_wrong_schema_or_nan_is_invalid_trace(self) -> None:
        wrong_schema = self.run_trace({"schemaVersion": "orq.audit-trace.v2", "events": []})
        self.assertEqual(wrong_schema.returncode, 2)
        self.assertEqual(json.loads(wrong_schema.stdout)["status"], "invalid-trace")

        nan_trace = self.run_trace('{"schemaVersion":"orq.audit-trace.v1","events":[{"sequence":NaN,"tool":"Read"}]}')
        self.assertEqual(nan_trace.returncode, 2)
        self.assertEqual(json.loads(nan_trace.stdout)["status"], "invalid-trace")

    def test_wrapped_text_search_before_graph_fails(self) -> None:
        for command in ("FOO=bar rg legacy src", "sudo grep legacy src", "bash -c 'rg legacy src'"):
            with self.subTest(command=command):
                result = self.run_trace({"events": [{"command": command}, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["status"], "fail")

    def test_multiline_shell_command_cannot_hide_direct_read(self) -> None:
        result = self.run_trace(
            {"events": [{"command": "echo começo\ncat src/index.ts"}, {"tool": GRAPH_TOOL}]}
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertGreaterEqual(payload["counts"]["direct-read"], 1)

    def test_output_redirection_and_tee_are_mutations(self) -> None:
        for command in (
            "echo x > out.py",
            "cat template.py > out.py",
            "printf x >> out.py",
            "printf x | tee out.py",
        ):
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"]["mutation"], 1)

    def test_unparseable_shell_cannot_launder_redirection_into_graph(self) -> None:
        for command in (
            "codebase_memory query_graph >dump.json --note 'unclosed",
            "codebase_memory query_graph >>dump.json 'x",
            "serena find_symbol <in.txt 'x",
        ):
            with self.subTest(command=command):
                result = self.run_trace({"events": [{"command": command}]})
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "not-observed")
                self.assertGreaterEqual(payload["counts"]["unverified"], 1)

    def test_nested_shell_wrappers_cannot_hide_text_search(self) -> None:
        for command in (
            "bash -lc 'rg legacy src'",
            "sh -euc 'rg legacy src'",
            "sudo bash -c 'rg legacy src'",
            "env -i bash -c 'rg legacy src'",
            "timeout 5 bash -c 'rg legacy src'",
        ):
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"]["text-search"], 1)

    def test_bare_graph_action_is_unverified_without_provider(self) -> None:
        for tool in ("search_code", "search_graph", "query_graph", "find_symbol"):
            with self.subTest(tool=tool):
                result = self.run_trace(
                    {"events": [{"tool": tool}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertEqual(payload["firstRelevant"]["category"], "unverified")

    def test_noncanonical_event_shape_is_invalid_trace(self) -> None:
        result = self.run_trace(
            {"events": [{"data": {"tool": "Read"}}, {"tool": GRAPH_TOOL}]}
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid-trace")

    def test_malformed_canonical_field_cannot_disappear_beside_graph(self) -> None:
        events = (
            {"tool": GRAPH_TOOL, "command": 123},
            {"tool": GRAPH_TOOL, "command": ["cat", 123]},
            {"tool": [GRAPH_TOOL, 123]},
            {"tool": [], "name": GRAPH_TOOL},
        )
        for event in events:
            with self.subTest(event=event):
                result = self.run_trace({"events": [event]})
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "invalid-trace")

    def test_mixed_event_is_conservative_independent_of_key_order(self) -> None:
        events = (
            {"tool": GRAPH_TOOL, "command": "rg legacy src"},
            {"command": "rg legacy src", "tool": GRAPH_TOOL},
        )
        for event in events:
            with self.subTest(event=event):
                result = self.run_trace({"events": [event]})
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertEqual(payload["firstRelevant"]["category"], "text-search")

    def test_notebook_edit_and_git_c_are_mutations_or_reads(self) -> None:
        cases = (
            ({"tool": "NotebookEdit"}, "mutation"),
            ({"command": "git -C repo show HEAD:src/index.ts"}, "direct-read"),
        )
        for event, category in cases:
            with self.subTest(event=event):
                result = self.run_trace({"events": [event, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"][category], 1)

    def test_find_delete_or_exec_mutation_is_not_plain_search(self) -> None:
        commands: tuple[str | list[str], ...] = (
            "find src -name '*.tmp' -delete",
            "find src -exec rm {} ;",
            ["find", "src", "-exec", "rm", "{}", ";"],
        )
        for command in commands:
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"]["mutation"], 1)

    def test_invalid_trace_error_does_not_leak_absolute_path(self) -> None:
        trace = Path(self.tmp.name) / "segredo-paciente.json"
        trace.write_bytes(b"\xff\xfe\x00")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(trace)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid-trace")
        self.assertNotIn(str(trace), result.stdout)

        missing = Path(self.tmp.name) / "nao-existe-segredo.json"
        missing_result = subprocess.run(
            [sys.executable, str(SCRIPT), str(missing)],
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(missing_result.returncode, 2)
        self.assertEqual(json.loads(missing_result.stdout)["status"], "invalid-trace")
        self.assertNotIn(str(missing), missing_result.stdout)

    def test_invalid_json_or_events_schema_exits_two(self) -> None:
        invalid_json = self.run_trace("{")
        self.assertEqual(invalid_json.returncode, 2)
        self.assertEqual(json.loads(invalid_json.stdout)["status"], "invalid-trace")

        invalid_events = self.run_trace({"events": "not-a-list"})
        self.assertEqual(invalid_events.returncode, 2)
        self.assertEqual(json.loads(invalid_events.stdout)["status"], "invalid-trace")

    def test_shell_tool_with_noncanonical_command_is_unverified(self) -> None:
        result = self.run_trace(
            {
                "events": [
                    {"tool": "Bash", "input": {"command": "cat src/segredo.py"}},
                    {"tool": GRAPH_TOOL},
                ]
            }
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["firstRelevant"]["category"], "unverified")

    def test_wrapper_options_cannot_hide_relevant_commands(self) -> None:
        cases = (
            ("bash --norc -c 'cat src/index.ts'", "direct-read"),
            ("sudo -u root bash -c 'rg legacy src'", "text-search"),
            ("timeout -s KILL 5 cat src/index.ts", "direct-read"),
            ("uv run --with requests python script.py", "direct-read"),
        )
        for command, category in cases:
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"][category], 1)

    def test_shell_substitution_or_grouping_is_unverified_not_ignored(self) -> None:
        for command in (
            "echo $(rm -rf build)",
            "echo `cat src/index.ts`",
            "(cat src/index.ts)",
            "{ cat src/index.ts; }",
            "echo x >| out.py",
        ):
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"]["unverified"], 1)

    def test_duplicate_json_keys_are_invalid_trace(self) -> None:
        result = self.run_trace(
            '{"schemaVersion":"orq.audit-trace.v1","events":'
            '[{"tool":"grep","tool":"mcp__codebase_memory_mcp__search_graph"}]}'
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid-trace")

    def test_fifo_is_rejected_without_blocking(self) -> None:
        fifo = Path(self.tmp.name) / "trace.fifo"
        os.mkfifo(fifo)
        process = subprocess.Popen(
            [sys.executable, str(SCRIPT), str(fifo)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, _ = process.communicate(timeout=0.5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            self.fail("o auditor bloqueou ao tentar ler FIFO")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(stdout)["status"], "invalid-trace")

    def test_git_diff_is_direct_read_before_graph(self) -> None:
        result = self.run_trace(
            {"events": [{"command": "git diff -- src/index.ts"}, {"tool": GRAPH_TOOL}]}
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertGreaterEqual(payload["counts"]["direct-read"], 1)

    def test_unknown_command_or_tool_is_unverified_not_ignored(self) -> None:
        events = (
            {"command": "chmod 755 gen.py"},
            {"command": "./inspecionar-repo.sh"},
            {"tool": "OpenRepositoryFile"},
        )
        for event in events:
            with self.subTest(event=event):
                result = self.run_trace({"events": [event, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertEqual(payload["firstRelevant"]["category"], "unverified")

    def test_graph_command_with_stderr_to_dev_null_remains_graph(self) -> None:
        result = self.run_trace(
            {"events": [{"command": "codebase-memory-mcp query_graph Foo 2>/dev/null"}]}
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["counts"]["mutation"], 0)

    def test_bash_combined_output_redirection_is_mutation(self) -> None:
        for command in ("echo x &> out.log", "echo x &>> out.log"):
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"]["mutation"], 1)

    def test_nested_shell_preserves_every_observed_category(self) -> None:
        result = self.run_trace(
            {
                "events": [
                    {"command": "bash -c 'codebase-memory-mcp query_graph Foo; cat src/index.ts'"},
                    {"tool": GRAPH_TOOL},
                ]
            }
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertGreaterEqual(payload["counts"]["graph"], 1)
        self.assertGreaterEqual(payload["counts"]["direct-read"], 1)

    def test_input_then_output_redirection_keeps_mutation_category(self) -> None:
        result = self.run_trace(
            {"events": [{"command": "cat < in.txt > out.txt"}, {"tool": GRAPH_TOOL}]}
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertGreaterEqual(payload["counts"]["mutation"], 1)

    def test_ambiguous_argv_wrapper_and_namespace_fail_closed(self) -> None:
        invalid_argv = self.run_trace(
            {"events": [{"command": ["head", "-n", 20, "src/index.ts"]}]}
        )
        self.assertEqual(invalid_argv.returncode, 2)
        self.assertEqual(json.loads(invalid_argv.stdout)["status"], "invalid-trace")

        for event in (
            {"command": "env -S 'cat src/index.ts'"},
            {"tool": "mcp__qualquer__query_graph"},
        ):
            with self.subTest(event=event):
                result = self.run_trace({"events": [event, {"tool": GRAPH_TOOL}]})
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["firstRelevant"]["category"], "unverified")

    def test_unknown_tilde_user_is_invalid_json_error_not_traceback(self) -> None:
        missing = "~orq-user-definitely-missing-9f8d7c/trace.json"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), missing],
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "invalid-trace")
        self.assertNotIn(missing, result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_empty_shell_command_is_unverified_not_other(self) -> None:
        for command in ("", "   \n ", [], ";;", "&&", "bash -c ''"):
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"tool": "Bash", "command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertEqual(payload["firstRelevant"]["category"], "unverified")

    def test_nested_shell_keeps_outer_redirection(self) -> None:
        for command in (
            "bash -c '' > out.txt",
            "bash -c 'cat src/index.ts' > out.txt",
        ):
            with self.subTest(command=command):
                result = self.run_trace(
                    {"events": [{"tool": "Bash", "command": command}, {"tool": GRAPH_TOOL}]}
                )
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "fail")
                self.assertGreaterEqual(payload["counts"]["mutation"], 1)


if __name__ == "__main__":
    unittest.main()
