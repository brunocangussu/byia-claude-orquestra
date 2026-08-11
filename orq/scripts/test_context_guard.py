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
import threading
import time
import unittest
from unittest import mock


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

    def test_read_latest_usage_expands_scan_past_one_large_tool_output(self) -> None:
        huge_tool_event = {
            "type": "response_item",
            "payload": {"output": "x" * (5 * 1024 * 1024)},
        }
        write_jsonl(
            self.transcript,
            [token_event(620_000, 1_000_000), huge_tool_event],
        )

        snapshot = guard.read_latest_usage(self.transcript)

        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.percent, 62.0)


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

    def test_default_state_uses_version_two_checkpoint_fields(self) -> None:
        state = guard.default_state()

        self.assertEqual(state["state_version"], 2)
        self.assertFalse(state["checkpoint_verified"])
        self.assertFalse(state["recovery_required"])
        self.assertNotIn("clear_required", state)

    def test_legacy_clear_required_migrates_to_checkpoint_verified(self) -> None:
        path = guard.state_path(self.data_dir, "session-a")
        path.parent.mkdir(parents=True)
        legacy = {
            "phase": "clear_required",
            "pre_alert_sent": True,
            "checkpoint_started": True,
            "clear_required": True,
            "telemetry_warning_sent": False,
            "last_percent": 67.1,
            "updated_at": 1,
        }
        path.write_text(json.dumps(legacy), encoding="utf-8")

        state = guard.load_state(self.data_dir, "session-a")

        self.assertEqual(state["state_version"], 2)
        self.assertEqual(state["phase"], "checkpoint_verified")
        self.assertTrue(state["checkpoint_verified"])
        self.assertFalse(state["checkpoint_started"])
        self.assertNotIn("clear_required", state)

    def test_inconsistent_legacy_clear_phase_is_normalized(self) -> None:
        path = guard.state_path(self.data_dir, "session-a")
        path.parent.mkdir(parents=True)
        legacy = {
            "phase": "clear_required",
            "pre_alert_sent": False,
            "checkpoint_started": False,
            "clear_required": False,
            "telemetry_warning_sent": False,
            "last_percent": 63.0,
            "updated_at": 1,
        }
        path.write_text(json.dumps(legacy), encoding="utf-8")

        state = guard.load_state(self.data_dir, "session-a")

        self.assertEqual(state["phase"], "checkpoint_required")
        self.assertFalse(state["checkpoint_verified"])

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

        self.assertEqual(
            {key: state[key] for key in guard.STATE_KEYS},
            guard.default_state(),
        )
        self.assertIn("corrompido", state["_state_warning"].lower())
        self.assertFalse(path.exists())
        self.assertEqual(len(list(path.parent.glob(path.name + ".corrupt-*"))), 1)

    def test_state_with_invalid_field_types_is_quarantined(self) -> None:
        path = guard.state_path(self.data_dir, "session-a")
        path.parent.mkdir(parents=True)
        invalid = guard.default_state()
        invalid["checkpoint_verified"] = "false"
        invalid["last_percent"] = "63.0"
        path.write_text(json.dumps(invalid), encoding="utf-8")

        state = guard.load_state(self.data_dir, "session-a")

        self.assertEqual(
            {key: state[key] for key in guard.STATE_KEYS},
            guard.default_state(),
        )
        self.assertIn("inválido", state["_state_warning"].lower())
        self.assertFalse(path.exists())
        self.assertEqual(len(list(path.parent.glob(path.name + ".corrupt-*"))), 1)

    def test_session_id_cannot_escape_plugin_data(self) -> None:
        path = guard.state_path(self.data_dir, "../../outside")

        self.assertEqual(path.parent, self.data_dir / "context-guard")
        self.assertNotIn("..", path.name)

    def test_save_state_reports_failure_and_removes_temporary_file(self) -> None:
        with mock.patch.object(guard.os, "replace", side_effect=OSError("disk full")):
            saved = guard.save_state(
                self.data_dir,
                "session-a",
                guard.default_state(),
            )

        self.assertIs(saved, False)
        state_dir = guard.state_path(self.data_dir, "session-a").parent
        self.assertEqual(list(state_dir.glob(".*.json.*")), [])

    def test_process_exit_releases_state_lock_without_stale_reclamation(self) -> None:
        child_code = f"""
import importlib.util, os, pathlib, sys
spec = importlib.util.spec_from_file_location('orq_context_guard_child', {str(GUARD_PATH)!r})
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
lock = module._acquire_state_lock(pathlib.Path({str(self.data_dir)!r}), 'session-a')
print('LOCKED' if lock is not None else 'FAILED', flush=True)
os._exit(0)
"""
        child = subprocess.run(
            [sys.executable, "-c", child_code],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )

        self.assertEqual(child.returncode, 0)
        self.assertEqual(child.stdout.strip(), "LOCKED")
        recovered = guard._acquire_state_lock(self.data_dir, "session-a")
        try:
            self.assertIsNotNone(
                recovered,
                "o SO deve liberar o lock quando o processo morre, sem rmdir TOCTOU",
            )
        finally:
            if recovered is not None:
                guard._release_state_lock(recovered)


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

    def test_claude_only_plugin_environment_is_ignored(self) -> None:
        event = self.event("Stop", 60.0, stop_hook_active=False)
        compat_env = {
            "CLAUDE_PLUGIN_ROOT": self.env["PLUGIN_ROOT"],
            "CLAUDE_PLUGIN_DATA": self.env["PLUGIN_DATA"],
        }

        result = guard.handle_event(event, compat_env)

        self.assertIsNone(result)
        self.assertFalse(any(self.data_dir.rglob("*.json")))

    def test_codex_native_plugin_environment_still_runs(self) -> None:
        event = self.event("Stop", 60.0, stop_hook_active=False)

        result = guard.handle_event(event, self.env)

        self.assertEqual(result["decision"], "block")
        self.assertIn("checkpoint", result["reason"].lower())

    def test_stop_pre_alert_is_emitted_once(self) -> None:
        event = self.event("Stop", 55.0, stop_hook_active=False)

        first = guard.handle_event(event, self.env)
        second = guard.handle_event(event, self.env)

        self.assertIn("55", first["systemMessage"])
        self.assertIsNone(second)

    def test_state_write_failure_is_visible_but_does_not_block(self) -> None:
        event = self.event("Stop", 55.0, stop_hook_active=False)

        with mock.patch.object(guard, "save_state", return_value=False):
            result = guard.handle_event(event, self.env)

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIn("telemetria", result["systemMessage"].lower())

    def test_corrupt_state_is_visible_and_recovered_without_blocking(self) -> None:
        path = guard.state_path(self.data_dir, "session-a")
        path.parent.mkdir(parents=True)
        path.write_text("{", encoding="utf-8")
        event = self.event("Stop", 40.0, stop_hook_active=False)

        result = guard.handle_event(event, self.env)

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIn("corrompido", result["systemMessage"].lower())

    def test_concurrent_hook_preserves_state_written_while_waiting_for_lock(self) -> None:
        held_lock = guard._acquire_state_lock(self.data_dir, "session-a")
        self.assertIsNotNone(held_lock)
        event = self.event("Stop", 60.0, stop_hook_active=False)
        result: list[dict | None] = []

        worker = threading.Thread(
            target=lambda: result.append(guard.handle_event(event, self.env)),
            daemon=True,
        )
        worker.start()
        time.sleep(0.05)

        concurrent_state = guard.default_state()
        concurrent_state["pre_alert_sent"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", concurrent_state))
        guard._release_state_lock(held_lock)
        worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        final_state = guard.load_state(self.data_dir, "session-a")
        self.assertTrue(final_state["pre_alert_sent"])
        self.assertTrue(final_state["checkpoint_started"])
        self.assertEqual(result[0]["decision"], "block")

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

    def test_codex_checkpoint_phrase_marks_checkpoint_verified(self) -> None:
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message=(
                "### ✅ Verificação\n"
                "**Checkpoint verificado; compactação liberada.**"
            ),
        )

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        self.assertTrue(state["checkpoint_verified"])
        self.assertFalse(state["checkpoint_started"])
        self.assertEqual(state["phase"], "checkpoint_verified")
        self.assertIn("compactação", result["systemMessage"].lower())

    def test_verified_checkpoint_allows_next_prompt_in_codex_app(self) -> None:
        guard.handle_event(
            self.event(
                "Stop",
                72.0,
                stop_hook_active=True,
                last_assistant_message=(
                    "Checkpoint verificado; compactação liberada."
                ),
            ),
            self.env,
        )

        result = guard.handle_event(
            self.event("UserPromptSubmit", 72.0, prompt="continue"),
            self.env,
        )

        self.assertIsNone(result)
        state = guard.load_state(self.data_dir, "session-a")
        self.assertTrue(state["checkpoint_verified"])
        self.assertEqual(state["phase"], "checkpoint_verified")

    def test_legacy_safe_clear_phrase_allows_next_prompt(self) -> None:
        guard.handle_event(
            self.event(
                "Stop",
                72.0,
                stop_hook_active=True,
                last_assistant_message="### ✅ Verificação\n**Seguro dar `/clear`.**",
            ),
            self.env,
        )

        result = guard.handle_event(
            self.event("UserPromptSubmit", 72.0, prompt="continue"),
            self.env,
        )

        self.assertIsNone(result)
        self.assertTrue(
            guard.load_state(self.data_dir, "session-a")["checkpoint_verified"]
        )

    def test_instruction_about_safe_phrase_does_not_complete_checkpoint(self) -> None:
        self.assertEqual(
            guard.handle_event(
                self.event("Stop", 63.0, stop_hook_active=False),
                self.env,
            )["decision"],
            "block",
        )
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message="Vou terminar informando se é seguro dar /clear.",
        )

        result = guard.handle_event(event, self.env)

        self.assertFalse(
            guard.load_state(self.data_dir, "session-a")["checkpoint_verified"]
        )
        self.assertIn("frase contratual", result["systemMessage"].lower())

    def test_failed_checkpoint_phrase_does_not_mark_checkpoint_verified(self) -> None:
        started = self.event("Stop", 63.0, stop_hook_active=False)
        self.assertEqual(guard.handle_event(started, self.env)["decision"], "block")
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message="Gravado, mas NÃO afirmo que é seguro limpar.",
        )

        guard.handle_event(event, self.env)

        self.assertFalse(
            guard.load_state(self.data_dir, "session-a")["checkpoint_verified"]
        )

        retry = guard.handle_event(
            self.event("Stop", 63.0, stop_hook_active=False),
            self.env,
        )
        self.assertEqual(
            retry["decision"],
            "block",
            "checkpoint falho precisa permitir uma nova tentativa controlada",
        )

    def test_failed_checkpoint_wins_if_message_also_quotes_success_phrase(self) -> None:
        self.assertEqual(
            guard.handle_event(
                self.event("Stop", 63.0, stop_hook_active=False),
                self.env,
            )["decision"],
            "block",
        )
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message=(
                "O contrato seria:\n**Seguro dar `/clear`.**\n"
                "**Gravado, mas NÃO afirmo que é seguro limpar.**"
            ),
        )

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        self.assertFalse(state["checkpoint_verified"])
        self.assertFalse(state["checkpoint_started"])
        self.assertIn("não foi verificado", result["systemMessage"].lower())

    def test_checkpoint_without_contract_phrase_reopens_retry(self) -> None:
        self.assertEqual(
            guard.handle_event(
                self.event("Stop", 63.0, stop_hook_active=False),
                self.env,
            )["decision"],
            "block",
        )
        result = guard.handle_event(
            self.event(
                "Stop",
                63.0,
                stop_hook_active=True,
                last_assistant_message="Checkpoint salvo. É seguro dar /clear agora.",
            ),
            self.env,
        )

        state = guard.load_state(self.data_dir, "session-a")
        self.assertFalse(state["checkpoint_verified"])
        self.assertFalse(state["checkpoint_started"])
        self.assertIn("frase contratual", result["systemMessage"].lower())
        retry = guard.handle_event(
            self.event("Stop", 63.0, stop_hook_active=False),
            self.env,
        )
        self.assertEqual(retry["decision"], "block")

    def test_post_tool_use_injects_checkpoint_context(self) -> None:
        event = self.event("PostToolUse", 61.0)

        result = guard.handle_event(event, self.env)

        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PostToolUse")
        self.assertIn("checkpoint", output["additionalContext"].lower())

    def test_post_tool_use_is_silent_after_verified_checkpoint(self) -> None:
        state = guard.default_state()
        state["phase"] = "checkpoint_verified"
        state["checkpoint_verified"] = True
        guard.save_state(self.data_dir, "session-a", state)
        event = self.event("PostToolUse", 72.0)

        result = guard.handle_event(event, self.env)

        self.assertIsNone(result)

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
        state = guard.default_state()
        state["checkpoint_started"] = True
        state["checkpoint_verified"] = True
        state["phase"] = "checkpoint_verified"
        guard.save_state(self.data_dir, "session-a", state)
        event = self.event("SessionStart", 10.0, source="clear")

        result = guard.handle_event(event, self.env)

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("memory/MEMORY.md", context)
        self.assertIn("KANBAN", context)
        self.assertEqual(
            guard.load_state(self.data_dir, "session-a"),
            guard.default_state(),
            "o /clear precisa destravar o mesmo session_id, se o host o reutilizar",
        )

    def test_clear_during_lock_contention_resets_before_next_prompt(self) -> None:
        blocked = guard.default_state()
        blocked["phase"] = "checkpoint_verified"
        blocked["checkpoint_verified"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", blocked))
        held_lock = guard._acquire_state_lock(self.data_dir, "session-a")
        self.assertIsNotNone(held_lock)
        try:
            result = guard.handle_event(
                self.event("SessionStart", 10.0, source="clear"),
                self.env,
            )
        finally:
            guard._release_state_lock(held_lock)

        next_prompt = guard.handle_event(
            self.event("UserPromptSubmit", 10.0, prompt="continue"),
            self.env,
        )
        self.assertNotEqual((next_prompt or {}).get("decision"), "block")
        self.assertFalse(
            guard.load_state(self.data_dir, "session-a")["checkpoint_verified"]
        )
        self.assertIn("falhou aberto", result["systemMessage"])

    def test_compact_without_checkpoint_requires_recovery(self) -> None:
        event = self.event("SessionStart", 20.0, source="compact")

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("compactação", context.lower())
        self.assertIn("checkpoint de recuperação", context.lower())
        self.assertEqual(state["phase"], "recovery_required")
        self.assertTrue(state["recovery_required"])

    def test_recovery_required_blocks_new_work_until_checkpoint(self) -> None:
        guard.handle_event(
            self.event("SessionStart", 20.0, source="compact"),
            self.env,
        )

        result = guard.handle_event(
            self.event("UserPromptSubmit", 20.0, prompt="continue o trabalho"),
            self.env,
        )

        self.assertEqual(result["decision"], "block")
        self.assertIn("recuperação", result["reason"].lower())

    def test_compact_after_verified_checkpoint_rehydrates_and_resets(self) -> None:
        state = guard.default_state()
        state["phase"] = "checkpoint_verified"
        state["checkpoint_verified"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", state))

        result = guard.handle_event(
            self.event("SessionStart", 75.0, source="compact"),
            self.env,
        )

        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("memory/MEMORY.md", context)
        self.assertIn("KANBAN", context)
        self.assertNotIn("checkpoint de recuperação", context.lower())
        reset = guard.load_state(self.data_dir, "session-a")
        self.assertEqual(reset["phase"], "normal")
        self.assertFalse(reset["checkpoint_verified"])
        self.assertFalse(reset["recovery_required"])
        self.assertIsInstance(reset["updated_at"], int)

    def test_precompact_auto_never_blocks(self) -> None:
        event = self.event("PreCompact", 91.0, trigger="auto")

        result = guard.handle_event(event, self.env)

        self.assertIsNot((result or {}).get("continue"), False)
        self.assertNotEqual((result or {}).get("decision"), "block")

    def test_postcompact_defers_rehydration_to_sessionstart(self) -> None:
        event = self.event("PostCompact", 91.0, trigger="auto")

        result = guard.handle_event(event, self.env)

        self.assertIsNone(result)

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
        state = json.loads(state_text)

        self.assertNotIn(secret, state_text)
        self.assertNotIn("last_assistant_message", state_text)
        self.assertNotIn("tool_input", state_text)
        self.assertEqual(set(state), set(guard.STATE_KEYS))


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

        board = (repo_root / "memory" / "wiki" / "KANBAN.md").read_text()
        t042_line = next(
            line for line in board.splitlines() if "`T-042` Statusline" in line
        )
        statusline_plan = (
            repo_root
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-08-09-statusline-nativa-codex.md"
        ).read_text()
        self.assertIn("0.23.0", t042_line)
        self.assertIn("Release alvo deste plano: `0.23.0`", statusline_plan)


class ContextGuardDocumentationContractTest(unittest.TestCase):
    def test_guard_contract_is_present_in_live_instructions(self) -> None:
        required = {
            PLUGIN_ROOT / "commands" / "checkpoint.md": [
                "Checkpoint verificado; compactação liberada.",
                "Seguro dar `/clear`.",
                "Claude",
                "Codex",
            ],
            PLUGIN_ROOT / "commands" / "stack.md": [
                "model_auto_compact_token_limit",
                "90%",
                "opt-in",
                "checkpoint_verified",
                "compact",
            ],
            PLUGIN_ROOT / "commands" / "instalar.md": [
                "/hooks",
                "confiança",
                "ambiente somente `CLAUDE_*`",
                "sem efeito",
            ],
            PLUGIN_ROOT / "skills" / "orq" / "SKILL.md": [
                "55%",
                "60%",
                "70%",
                "SessionStart(source=compact)",
                "Claude",
                "/clear",
            ],
        }
        missing: dict[str, list[str]] = {}
        for path, phrases in required.items():
            text = path.read_text(encoding="utf-8")
            absent = [phrase for phrase in phrases if phrase not in text]
            if absent:
                missing[str(path.relative_to(PLUGIN_ROOT))] = absent

        self.assertEqual(missing, {})

        live_text = "\n".join(
            path.read_text(encoding="utf-8") for path in required
        )
        self.assertNotIn("CLEAR_REQUIRED", live_text)
        self.assertNotIn("compactação detectada como contingência", live_text)


if __name__ == "__main__":
    unittest.main()
