#!/usr/bin/env python3
"""Testes do guardião preventivo de contexto do Codex."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


GUARD_PATH = Path(__file__).with_name("context-guard.py")
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOKS_PATH = PLUGIN_ROOT / "hooks" / "hooks.json"
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")


def token_event(used_tokens: int, context_window: int) -> dict:
    return {
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "last_token_usage": {"total_tokens": used_tokens},
                "model_context_window": context_window,
            },
        },
    }


def write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )


if GUARD_PATH.exists():
    spec = importlib.util.spec_from_file_location("orq_context_guard", GUARD_PATH)
    assert spec is not None and spec.loader is not None
    guard = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = guard
    spec.loader.exec_module(guard)
else:
    guard = None

lint_spec = importlib.util.spec_from_file_location("orq_lint_coerencia", LINT_PATH)
assert lint_spec is not None and lint_spec.loader is not None
lint_module = importlib.util.module_from_spec(lint_spec)
sys.modules[lint_spec.name] = lint_module
lint_spec.loader.exec_module(lint_module)


class ContextGuardPresenceTest(unittest.TestCase):
    def test_guard_script_exists(self) -> None:
        self.assertTrue(GUARD_PATH.is_file(), f"guardião ausente: {GUARD_PATH}")

    def test_hooks_bundle_exists(self) -> None:
        self.assertTrue(HOOKS_PATH.is_file(), f"bundle de hooks ausente: {HOOKS_PATH}")


@unittest.skipIf(guard is None, "guardião ainda não implementado")
class ContextGuardUsageParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-context-guard-test-")
        self.addCleanup(self.tmp.cleanup)
        self.transcript = Path(self.tmp.name) / "rollout.jsonl"

    def test_read_latest_usage_uses_last_complete_token_count(self) -> None:
        write_jsonl(
            self.transcript,
            [
                token_event(540_000, 1_000_000),
                {"type": "event_msg", "payload": {"type": "other"}},
                token_event(610_000, 1_000_000),
            ],
        )

        snapshot = guard.read_latest_usage(self.transcript)

        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.used_tokens, 610_000)
        self.assertEqual(snapshot.context_window, 1_000_000)
        self.assertEqual(snapshot.percent, 61.0)

    def test_read_latest_usage_ignores_partial_trailing_json(self) -> None:
        self.transcript.write_text(
            json.dumps(token_event(600_000, 1_000_000)) + "\n{",
            encoding="utf-8",
        )

        snapshot = guard.read_latest_usage(self.transcript)

        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.percent, 60.0)

    def test_read_latest_usage_rejects_invalid_numbers(self) -> None:
        write_jsonl(
            self.transcript,
            [
                token_event(600_000, 0),
                token_event(-1, 1_000_000),
            ],
        )

        self.assertIsNone(guard.read_latest_usage(self.transcript))

    def test_read_latest_usage_returns_none_for_missing_transcript(self) -> None:
        self.assertIsNone(guard.read_latest_usage(self.transcript))


STATE_API = ("band_for", "state_path", "default_state", "load_state", "save_state")


class ContextGuardStateInterfaceTest(unittest.TestCase):
    def test_state_api_exists(self) -> None:
        missing = [name for name in STATE_API if guard is None or not hasattr(guard, name)]
        self.assertEqual(missing, [], f"interfaces de estado ausentes: {missing}")


@unittest.skipUnless(
    guard is not None and all(hasattr(guard, name) for name in STATE_API),
    "interfaces de estado ainda não implementadas",
)
class ContextGuardStateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-context-state-test-")
        self.addCleanup(self.tmp.cleanup)
        self.data_dir = Path(self.tmp.name)

    def test_band_boundaries(self) -> None:
        cases = [
            (54.9, "normal"),
            (55.0, "pre_alert"),
            (59.9, "pre_alert"),
            (60.0, "checkpoint_required"),
            (69.9, "checkpoint_required"),
            (70.0, "emergency"),
            (90.0, "emergency"),
        ]
        for percent, expected in cases:
            with self.subTest(percent=percent):
                self.assertEqual(guard.band_for(percent), expected)

    def test_state_round_trip_is_isolated_by_session(self) -> None:
        state_a = guard.load_state(self.data_dir, "session-a")
        state_a["checkpoint_started"] = True
        guard.save_state(self.data_dir, "session-a", state_a)

        self.assertTrue(
            guard.load_state(self.data_dir, "session-a")["checkpoint_started"]
        )
        self.assertFalse(
            guard.load_state(self.data_dir, "session-b")["checkpoint_started"]
        )

    def test_corrupt_state_is_quarantined_and_recreated(self) -> None:
        path = guard.state_path(self.data_dir, "session-a")
        path.parent.mkdir(parents=True)
        path.write_text("{", encoding="utf-8")

        state = guard.load_state(self.data_dir, "session-a")

        self.assertEqual(state, guard.default_state())
        self.assertFalse(path.exists())
        self.assertEqual(len(list(path.parent.glob(path.name + ".corrupt-*"))), 1)

    def test_session_id_cannot_escape_plugin_data(self) -> None:
        path = guard.state_path(self.data_dir, "../../outside")

        self.assertEqual(path.parent, self.data_dir / "context-guard")
        self.assertNotIn("..", path.name)


class ContextGuardHookInterfaceTest(unittest.TestCase):
    def test_hook_api_exists(self) -> None:
        missing = [
            name for name in ("handle_event", "main") if not hasattr(guard, name)
        ]
        self.assertEqual(missing, [], f"interfaces de hook ausentes: {missing}")


@unittest.skipUnless(
    guard is not None and hasattr(guard, "handle_event"),
    "decisões dos hooks ainda não implementadas",
)
class ContextGuardHookDecisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-context-hook-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.transcript = self.root / "rollout.jsonl"
        self.data_dir = self.root / "plugin-data"
        self.env = {
            "PLUGIN_ROOT": str(self.root / "plugin"),
            "PLUGIN_DATA": str(self.data_dir),
        }

    def event(self, event_name: str, percent: float, **extra: object) -> dict:
        write_jsonl(
            self.transcript,
            [token_event(round(percent * 10_000), 1_000_000)],
        )
        return {
            "session_id": "session-a",
            "transcript_path": str(self.transcript),
            "cwd": str(self.root),
            "hook_event_name": event_name,
            **extra,
        }

    def test_non_codex_host_fails_open(self) -> None:
        event = self.event("Stop", 65.0, stop_hook_active=False)

        self.assertIsNone(guard.handle_event(event, {}))

    def test_stop_pre_alert_is_emitted_once(self) -> None:
        event = self.event("Stop", 55.0, stop_hook_active=False)

        first = guard.handle_event(event, self.env)
        second = guard.handle_event(event, self.env)

        self.assertIn("55", first["systemMessage"])
        self.assertIsNone(second)

    def test_stop_at_sixty_continues_once_with_checkpoint_instruction(self) -> None:
        event = self.event("Stop", 60.0, stop_hook_active=False)

        first = guard.handle_event(event, self.env)
        second = guard.handle_event(event, self.env)

        self.assertEqual(first["decision"], "block")
        self.assertIn("checkpoint", first["reason"].lower())
        self.assertNotEqual((second or {}).get("decision"), "block")

    def test_stop_hook_active_does_not_loop(self) -> None:
        event = self.event("Stop", 65.0, stop_hook_active=True)

        result = guard.handle_event(event, self.env)

        self.assertNotEqual((result or {}).get("decision"), "block")

    def test_jump_to_emergency_requests_checkpoint(self) -> None:
        event = self.event("Stop", 72.0, stop_hook_active=False)

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        self.assertEqual(result["decision"], "block")
        self.assertEqual(state["phase"], "emergency")

    def test_safe_checkpoint_phrase_marks_clear_required(self) -> None:
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message="### ✅ Verificação\n**Seguro dar `/clear`.**",
        )

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        self.assertTrue(state["clear_required"])
        self.assertIn("/clear", result["systemMessage"])

    def test_failed_checkpoint_phrase_does_not_mark_clear_required(self) -> None:
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message="Gravado, mas NÃO afirmo que é seguro limpar.",
        )

        guard.handle_event(event, self.env)

        self.assertFalse(
            guard.load_state(self.data_dir, "session-a")["clear_required"]
        )

    def test_post_tool_use_injects_checkpoint_context(self) -> None:
        event = self.event("PostToolUse", 61.0)

        result = guard.handle_event(event, self.env)

        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PostToolUse")
        self.assertIn("checkpoint", output["additionalContext"].lower())

    def test_user_prompt_is_blocked_after_safe_checkpoint(self) -> None:
        state = guard.default_state()
        state["clear_required"] = True
        guard.save_state(self.data_dir, "session-a", state)
        event = self.event("UserPromptSubmit", 63.0, prompt="continue implementando")

        result = guard.handle_event(event, self.env)

        self.assertEqual(result["decision"], "block")
        self.assertIn("/clear", result["reason"])

    def test_checkpoint_prompt_is_allowed_during_emergency(self) -> None:
        event = self.event("UserPromptSubmit", 72.0, prompt="faça o checkpoint agora")

        result = guard.handle_event(event, self.env)

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIn(
            "checkpoint",
            result["hookSpecificOutput"]["additionalContext"].lower(),
        )

    def test_ordinary_prompt_at_sixty_injects_checkpoint_before_work(self) -> None:
        event = self.event("UserPromptSubmit", 61.0, prompt="implemente a próxima tela")

        result = guard.handle_event(event, self.env)

        self.assertNotEqual((result or {}).get("decision"), "block")
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("antes", context.lower())
        self.assertIn("checkpoint", context.lower())

    def test_session_start_clear_injects_memory_rehydration(self) -> None:
        event = self.event("SessionStart", 10.0, source="clear")

        result = guard.handle_event(event, self.env)

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("memory/MEMORY.md", context)
        self.assertIn("KANBAN", context)

    def test_session_start_compact_marks_recovery_mode(self) -> None:
        event = self.event("SessionStart", 20.0, source="compact")

        result = guard.handle_event(event, self.env)

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("compactação", context.lower())
        self.assertIn("checkpoint", context.lower())

    def test_precompact_never_returns_continue_false(self) -> None:
        event = self.event("PreCompact", 91.0, trigger="auto")

        result = guard.handle_event(event, self.env)

        self.assertIsNot((result or {}).get("continue"), False)

    def test_state_never_persists_conversation_content(self) -> None:
        secret = "PACIENTE-NAO-PERSISTIR"
        event = self.event(
            "Stop",
            60.0,
            stop_hook_active=False,
            last_assistant_message=secret,
            prompt=secret,
            tool_input={"message": secret},
        )

        guard.handle_event(event, self.env)
        state_text = guard.state_path(self.data_dir, "session-a").read_text()

        self.assertNotIn(secret, state_text)
        self.assertNotIn("last_assistant_message", state_text)
        self.assertNotIn("tool_input", state_text)


@unittest.skipUnless(
    guard is not None and hasattr(guard, "main"),
    "entrada CLI ainda não implementada",
)
class ContextGuardCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-context-cli-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.transcript = self.root / "rollout.jsonl"
        self.data_dir = self.root / "plugin-data"
        self.env = os.environ.copy()
        self.env.update(
            {
                "PLUGIN_ROOT": str(self.root / "plugin"),
                "PLUGIN_DATA": str(self.data_dir),
            }
        )

    def run_guard(self, raw_stdin: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input=raw_stdin,
            text=True,
            capture_output=True,
            env=self.env,
            timeout=5,
            check=False,
        )

    def test_invalid_stdin_fails_open_without_output(self) -> None:
        result = self.run_guard("{")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_valid_event_emits_one_json_object(self) -> None:
        write_jsonl(self.transcript, [token_event(600_000, 1_000_000)])
        event = {
            "session_id": "session-cli",
            "transcript_path": str(self.transcript),
            "cwd": str(self.root),
            "hook_event_name": "Stop",
            "stop_hook_active": False,
            "last_assistant_message": "trabalho concluído",
        }

        result = self.run_guard(json.dumps(event))

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["decision"], "block")
        self.assertIn("checkpoint", output["reason"].lower())


@unittest.skipUnless(HOOKS_PATH.is_file(), "bundle de hooks ainda não implementado")
class ContextGuardHooksBundleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(HOOKS_PATH.read_text(encoding="utf-8"))

    def test_bundle_registers_exact_codex_events(self) -> None:
        expected = {
            "PostToolUse",
            "Stop",
            "UserPromptSubmit",
            "SessionStart",
            "PreCompact",
            "PostCompact",
        }

        self.assertEqual(set(self.config["hooks"]), expected)

    def test_handlers_are_bounded_commands_to_guard(self) -> None:
        context_events = {"PostToolUse", "UserPromptSubmit", "SessionStart"}
        for event_name, groups in self.config["hooks"].items():
            with self.subTest(event=event_name):
                self.assertEqual(len(groups), 1)
                handlers = groups[0]["hooks"]
                self.assertEqual(len(handlers), 1)
                handler = handlers[0]
                self.assertEqual(handler["type"], "command")
                self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py", handler["command"])
                self.assertLessEqual(handler["timeout"], 5)
                if event_name in context_events:
                    self.assertGreater(handler["additionalContextLimit"], 0)
                    self.assertLessEqual(handler["additionalContextLimit"], 300)
                else:
                    self.assertNotIn("additionalContextLimit", handler)


class ContextGuardLintInterfaceTest(unittest.TestCase):
    def test_hook_lint_api_exists(self) -> None:
        self.assertTrue(
            hasattr(lint_module, "validate_hooks"),
            "validate_hooks ausente no lint-coerencia",
        )


@unittest.skipUnless(
    hasattr(lint_module, "validate_hooks"),
    "validação de hooks ainda não implementada no lint",
)
class ContextGuardHookLintTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-hooks-lint-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plugin = self.root / "orq"
        (self.plugin / "hooks").mkdir(parents=True)

    def write_hooks(self, command: str) -> None:
        config = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": command,
                                "timeout": 5,
                            }
                        ]
                    }
                ]
            }
        }
        (self.plugin / "hooks" / "hooks.json").write_text(
            json.dumps(config),
            encoding="utf-8",
        )

    def test_missing_hook_script_is_reported(self) -> None:
        self.write_hooks(
            'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inexistente.py"'
        )

        problems = lint_module.validate_hooks(self.root, self.plugin)

        self.assertTrue(any("scripts/inexistente.py não existe" in item[2] for item in problems))

    def test_valid_hook_script_has_no_problem(self) -> None:
        (self.plugin / "scripts").mkdir()
        (self.plugin / "scripts" / "context-guard.py").write_text("# ok\n")
        self.write_hooks(
            'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/context-guard.py"'
        )

        self.assertEqual(lint_module.validate_hooks(self.root, self.plugin), [])


class ContextGuardReleaseVersionTest(unittest.TestCase):
    def test_release_version_is_coordinated(self) -> None:
        repo_root = PLUGIN_ROOT.parent
        expected = "0.22.0"
        manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text()
        )
        marketplace = json.loads(
            (repo_root / ".claude-plugin" / "marketplace.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "orq")
        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        memory = (repo_root / "memory" / "MEMORY.md").read_text(encoding="utf-8")

        self.assertEqual(manifest["version"], expected)
        self.assertEqual(entry["version"], expected)
        self.assertIn(f"## Status\n\n`{expected}`", readme)
        self.assertIn(f"**Versão:** {expected} ·", memory)


if __name__ == "__main__":
    unittest.main()
