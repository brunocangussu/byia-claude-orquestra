#!/usr/bin/env python3
"""Testes do guardião preventivo de contexto do Codex."""

from __future__ import annotations

import errno
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


def legacy_reset_marker(data_dir: Path, session_id: str) -> Path:
    """Deriva o caminho legado pelo contrato público, sem chamar a produção."""

    digest = hashlib.sha256(session_id.encode("utf-8", errors="replace")).hexdigest()
    return data_dir / "context-guard" / f"{digest}.reset"


def pending_reset_markers(data_dir: Path, session_id: str) -> list[Path]:
    """Enumera marcadores observáveis sem reutilizar a lógica de produção."""

    legacy_marker = legacy_reset_marker(data_dir, session_id)
    if not legacy_marker.parent.exists():
        return []
    generation_prefix = f"{legacy_marker.name}."
    return sorted(
        path
        for path in legacy_marker.parent.iterdir()
        if path.name == legacy_marker.name or path.name.startswith(generation_prefix)
    )


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
        path.parent.mkdir(parents=True, exist_ok=True)
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
        path.parent.mkdir(parents=True, exist_ok=True)
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
        path.parent.mkdir(parents=True, exist_ok=True)
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
        path.parent.mkdir(parents=True, exist_ok=True)
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

    def test_reset_created_during_apply_survives_for_next_transaction(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        first_generation = pending_reset_markers(self.data_dir, "session-a")
        self.assertEqual(len(first_generation), 1)

        state_file = guard.state_path(self.data_dir, "session-a")
        original_unlink = Path.unlink
        second_generation_created = False

        def create_second_generation_during_state_removal(
            path: Path,
            *args: object,
            **kwargs: object,
        ) -> None:
            nonlocal second_generation_created
            if path == state_file and not second_generation_created:
                second_generation_created = True
                self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
            return original_unlink(path, *args, **kwargs)

        with mock.patch.object(
            Path,
            "unlink",
            new=create_second_generation_during_state_removal,
        ):
            first_snapshot = guard._prepare_pending_reset(self.data_dir, "session-a")

        self.assertEqual(first_snapshot, first_generation)
        self.assertTrue(guard._finish_pending_reset(first_snapshot))
        pending_after_first_apply = pending_reset_markers(self.data_dir, "session-a")
        self.assertTrue(second_generation_created)
        self.assertFalse(state_file.exists())
        self.assertEqual(len(pending_after_first_apply), 1)
        self.assertNotEqual(pending_after_first_apply, first_generation)
        second_snapshot = guard._prepare_pending_reset(self.data_dir, "session-a")
        self.assertEqual(second_snapshot, pending_after_first_apply)
        self.assertTrue(guard._finish_pending_reset(second_snapshot))
        self.assertEqual(pending_reset_markers(self.data_dir, "session-a"), [])

    def test_legacy_fixed_reset_marker_is_consumed(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        legacy_marker = legacy_reset_marker(self.data_dir, "session-a")
        legacy_marker.touch()

        pending_snapshot = guard._prepare_pending_reset(self.data_dir, "session-a")
        self.assertIsNotNone(pending_snapshot)
        assert pending_snapshot is not None
        self.assertEqual(len(pending_snapshot), 1)
        self.assertNotEqual(pending_snapshot[0], legacy_marker)
        self.assertTrue(pending_snapshot[0].name.startswith(f"{legacy_marker.name}."))
        self.assertFalse(legacy_marker.exists())
        self.assertTrue(guard._finish_pending_reset(pending_snapshot))

        self.assertEqual(
            guard.load_state(self.data_dir, "session-a"),
            guard.default_state(),
        )
        self.assertFalse(legacy_marker.exists())

    def test_legacy_reset_created_after_snapshot_survives_for_next_transaction(
        self,
    ) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        legacy_marker = legacy_reset_marker(self.data_dir, "session-a")
        legacy_marker.touch()

        first_snapshot = guard._prepare_pending_reset(self.data_dir, "session-a")
        self.assertIsNotNone(first_snapshot)
        assert first_snapshot is not None
        self.assertEqual(len(first_snapshot), 1)

        legacy_marker.touch()
        self.assertTrue(guard._finish_pending_reset(first_snapshot))

        self.assertTrue(
            legacy_marker.exists(),
            "o clear legado posterior à fotografia não pode ser consumido pela transação anterior",
        )
        second_snapshot = guard._prepare_pending_reset(self.data_dir, "session-a")
        assert second_snapshot is not None
        self.assertEqual(len(second_snapshot), 1)
        self.assertNotEqual(second_snapshot[0], legacy_marker)
        self.assertTrue(second_snapshot[0].name.startswith(f"{legacy_marker.name}."))
        self.assertTrue(guard._finish_pending_reset(second_snapshot))
        self.assertFalse(legacy_marker.exists())

    def test_msvcrt_backend_locks_and_unlocks_same_byte(self) -> None:
        class FakeMsvcrt:
            LK_NBLCK = 23
            LK_UNLCK = 42

            def __init__(self) -> None:
                self.calls: list[tuple[int, int, int]] = []

            def locking(self, file_descriptor: int, mode: int, count: int) -> None:
                self.calls.append(
                    (mode, count, os.lseek(file_descriptor, 0, os.SEEK_CUR))
                )

        fake_msvcrt = FakeMsvcrt()
        with (
            mock.patch.object(guard, "fcntl", None),
            mock.patch.object(guard, "msvcrt", fake_msvcrt, create=True),
        ):
            lock = guard._acquire_state_lock(self.data_dir, "session-a")
            self.assertIsNotNone(lock)
            assert lock is not None
            try:
                self.assertEqual(
                    fake_msvcrt.calls,
                    [(fake_msvcrt.LK_NBLCK, 1, 0)],
                )
                self.assertIsNotNone(lock.handle)
                handle = lock.handle
                assert handle is not None
                handle.seek(5)
            finally:
                guard._release_state_lock(lock)

        self.assertEqual(
            fake_msvcrt.calls,
            [
                (fake_msvcrt.LK_NBLCK, 1, 0),
                (fake_msvcrt.LK_UNLCK, 1, 0),
            ],
        )
        self.assertTrue(handle.closed)

    def test_msvcrt_permanent_error_fails_open_without_retry(self) -> None:
        class FailingMsvcrt:
            LK_NBLCK = 23
            LK_UNLCK = 42

            def __init__(self) -> None:
                self.calls = 0

            def locking(self, file_descriptor: int, mode: int, count: int) -> None:
                self.calls += 1
                raise OSError(errno.EINVAL, "backend indisponível")

        fake_msvcrt = FailingMsvcrt()
        with (
            mock.patch.object(guard, "fcntl", None),
            mock.patch.object(guard, "msvcrt", fake_msvcrt, create=True),
            mock.patch.object(guard, "STATE_LOCK_WAIT_SECONDS", 0.01),
            mock.patch.object(guard.time, "sleep") as sleep,
        ):
            lock = guard._acquire_state_lock(self.data_dir, "session-a")

        self.assertIsNone(lock)
        self.assertEqual(fake_msvcrt.calls, 1)
        sleep.assert_not_called()

    def test_msvcrt_transient_contention_retries_then_acquires(self) -> None:
        class ContendedMsvcrt:
            LK_NBLCK = 23
            LK_UNLCK = 42

            def __init__(self) -> None:
                self.acquire_calls = 0

            def locking(self, file_descriptor: int, mode: int, count: int) -> None:
                if mode == self.LK_NBLCK:
                    self.acquire_calls += 1
                    if self.acquire_calls == 1:
                        raise OSError(errno.EACCES, "lock ocupado")

        fake_msvcrt = ContendedMsvcrt()
        with (
            mock.patch.object(guard, "fcntl", None),
            mock.patch.object(guard, "msvcrt", fake_msvcrt, create=True),
            mock.patch.object(guard.time, "sleep") as sleep,
        ):
            lock = guard._acquire_state_lock(self.data_dir, "session-a")
            self.assertIsNotNone(lock)
            assert lock is not None
            try:
                self.assertEqual(fake_msvcrt.acquire_calls, 2)
                sleep.assert_called_once_with(0.01)
            finally:
                guard._release_state_lock(lock)

    def test_missing_kernel_lock_backend_fails_open_without_lockdir(self) -> None:
        with (
            mock.patch.object(guard, "fcntl", None),
            mock.patch.object(guard, "msvcrt", None, create=True),
        ):
            lock = guard._acquire_state_lock(self.data_dir, "session-a")
            try:
                self.assertIsNone(lock)
            finally:
                if lock is not None:
                    guard._release_state_lock(lock)

        self.assertFalse(
            guard._state_lock_path(self.data_dir, "session-a")
            .with_suffix(".lockdir")
            .exists()
        )


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

        self.assertIsNotNone(result)
        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIn("checkpoint", result["systemMessage"].lower())

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

    def test_persist_response_strips_every_blocking_field_and_legacy_reason(self) -> None:
        result = guard._persist_response(
            self.data_dir,
            "session-a",
            guard.default_state(),
            {
                "decision": "block",
                "reason": "Pare e execute /clear.",
                "continue": False,
                "stopReason": "checkpoint obrigatório",
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "Atenda o pedido atual.",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "bloqueado",
                },
            },
        )

        self.assertEqual(set(result or {}), {"hookSpecificOutput"})
        hook_output = result["hookSpecificOutput"]
        self.assertEqual(
            set(hook_output),
            {"hookEventName", "additionalContext"},
        )
        self.assertNotIn("/clear", json.dumps(result).lower())

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
        self.assertNotEqual((result[0] or {}).get("decision"), "block")

    def test_stop_at_sixty_continues_once_with_checkpoint_instruction(self) -> None:
        event = self.event("Stop", 60.0, stop_hook_active=False)

        first = guard.handle_event(event, self.env)
        second = guard.handle_event(event, self.env)

        self.assertIsNotNone(first)
        self.assertNotEqual((first or {}).get("decision"), "block")
        self.assertIn("checkpoint", first["systemMessage"].lower())
        self.assertIn("mesma conversa pode continuar", first["systemMessage"].lower())
        self.assertNotEqual((second or {}).get("decision"), "block")
        self.assertIsNone(second)

    def test_stop_hook_active_does_not_loop(self) -> None:
        guard.handle_event(
            self.event("Stop", 65.0, stop_hook_active=False),
            self.env,
        )
        event = self.event("Stop", 65.0, stop_hook_active=True)

        result = guard.handle_event(event, self.env)

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIsNone(result)

    def test_jump_to_emergency_requests_checkpoint(self) -> None:
        event = self.event("Stop", 72.0, stop_hook_active=False)

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIn("checkpoint", result["systemMessage"].lower())
        self.assertEqual(state["phase"], "emergency")

    def test_codex_checkpoint_phrase_marks_checkpoint_verified(self) -> None:
        event = self.event(
            "Stop",
            63.0,
            stop_hook_active=True,
            last_assistant_message=(
                "### ✅ Verificação\n"
                "**Checkpoint verificado; conversa continua.**"
            ),
        )

        result = guard.handle_event(event, self.env)
        state = guard.load_state(self.data_dir, "session-a")

        self.assertTrue(state["checkpoint_verified"])
        self.assertFalse(state["checkpoint_started"])
        self.assertEqual(state["phase"], "checkpoint_verified")
        self.assertEqual(result["systemMessage"], "Checkpoint verificado; conversa continua.")

    def test_codex_checkpoint_phrase_accepts_period_outside_bold(self) -> None:
        result = guard.handle_event(
            self.event(
                "Stop",
                63.0,
                stop_hook_active=True,
                last_assistant_message=(
                    "### ✅ Verificação\n"
                    "**Checkpoint verificado; conversa continua**."
                ),
            ),
            self.env,
        )

        self.assertTrue(
            guard.load_state(self.data_dir, "session-a")["checkpoint_verified"]
        )
        self.assertEqual(result["systemMessage"], "Checkpoint verificado; conversa continua.")

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

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIsNone(result)
        state = guard.load_state(self.data_dir, "session-a")
        self.assertTrue(state["checkpoint_verified"])
        self.assertEqual(state["phase"], "checkpoint_verified")

    def test_verified_checkpoint_rearms_consultively_after_ten_more_percent(self) -> None:
        guard.handle_event(
            self.event("Stop", 60.0, stop_hook_active=False),
            self.env,
        )
        guard.handle_event(
            self.event(
                "Stop",
                60.0,
                stop_hook_active=True,
                last_assistant_message="Checkpoint verificado; conversa continua.",
            ),
            self.env,
        )

        before_delta = guard.handle_event(
            self.event("UserPromptSubmit", 69.9, prompt="continue"),
            self.env,
        )
        after_delta = guard.handle_event(
            self.event("UserPromptSubmit", 70.0, prompt="continue"),
            self.env,
        )
        state = guard.load_state(self.data_dir, "session-a")

        self.assertIsNone(before_delta)
        self.assertIsNotNone(after_delta)
        self.assertNotEqual((after_delta or {}).get("decision"), "block")
        self.assertIn(
            "checkpoint",
            after_delta["hookSpecificOutput"]["additionalContext"].lower(),
        )
        self.assertFalse(state["checkpoint_verified"])
        self.assertTrue(state["checkpoint_started"])

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

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIsNone(result)
        self.assertTrue(
            guard.load_state(self.data_dir, "session-a")["checkpoint_verified"]
        )

    def test_instruction_about_safe_phrase_does_not_complete_checkpoint(self) -> None:
        started = guard.handle_event(
            self.event("Stop", 63.0, stop_hook_active=False),
            self.env,
        )
        self.assertNotEqual((started or {}).get("decision"), "block")
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
        self.assertNotEqual(
            (guard.handle_event(started, self.env) or {}).get("decision"),
            "block",
        )
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
        self.assertNotEqual(
            (retry or {}).get("decision"),
            "block",
            "checkpoint falho precisa permitir uma nova tentativa consultiva",
        )

    def test_failed_checkpoint_wins_if_message_also_quotes_success_phrase(self) -> None:
        started = guard.handle_event(
            self.event("Stop", 63.0, stop_hook_active=False),
            self.env,
        )
        self.assertNotEqual((started or {}).get("decision"), "block")
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
        started = guard.handle_event(
            self.event("Stop", 63.0, stop_hook_active=False),
            self.env,
        )
        self.assertNotEqual((started or {}).get("decision"), "block")
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
        self.assertNotEqual((retry or {}).get("decision"), "block")

    def test_post_tool_use_injects_checkpoint_context(self) -> None:
        event = self.event("PostToolUse", 61.0)

        result = guard.handle_event(event, self.env)
        repeated = guard.handle_event(event, self.env)

        self.assertIsNotNone(result)
        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PostToolUse")
        self.assertIn("checkpoint", output["additionalContext"].lower())
        self.assertIn("próximo ponto seguro", output["additionalContext"].lower())
        self.assertNotIn("pare", output["additionalContext"].lower())
        self.assertIsNone(repeated)

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
        self.assertIsNotNone(result)
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("atenda o pedido atual", context.lower())
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
        self.assertIn("BOARD_CANONICO", context)
        self.assertIn("Comprove `ORQ_PACKAGE_ROOT`", context)
        self.assertIn("thread_root", context)
        self.assertIn("`state: ok` com `exists: false`", context)
        self.assertIn("`/orq:init`", context)
        self.assertIn("não leia o `board` e encaminhe para `/orq:init`", context)
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
        self.assertIn("mantenha o pedido atual", context.lower())
        self.assertNotIn("antes de iniciar trabalho novo", context.lower())
        self.assertNotIn("pare", context.lower())
        self.assertEqual(state["phase"], "recovery_required")
        self.assertTrue(state["recovery_required"])

    def test_recovery_required_advises_current_work_until_checkpoint(self) -> None:
        guard.handle_event(
            self.event("SessionStart", 20.0, source="compact"),
            self.env,
        )

        result = guard.handle_event(
            self.event("UserPromptSubmit", 20.0, prompt="continue o trabalho"),
            self.env,
        )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIsNotNone(result)
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("atenda o pedido atual", context.lower())
        self.assertIn("recuperação", context.lower())

    def test_recovery_required_advises_without_token_telemetry(self) -> None:
        missing_transcript = self.root / "rollout-without-token-count.jsonl"
        base_event = {
            "session_id": "session-a",
            "transcript_path": str(missing_transcript),
            "cwd": str(self.root),
        }
        guard.handle_event(
            {**base_event, "hook_event_name": "SessionStart", "source": "compact"},
            self.env,
        )

        result = guard.handle_event(
            {
                **base_event,
                "hook_event_name": "UserPromptSubmit",
                "prompt": "continue o trabalho",
            },
            self.env,
        )

        self.assertIsNotNone(result)
        self.assertNotEqual((result or {}).get("decision"), "block")
        context = result["hookSpecificOutput"]["additionalContext"].lower()
        self.assertIn("atenda o pedido atual", context)
        self.assertIn("recuperação", context)

    def test_recovery_checkpoint_prompt_executes_now(self) -> None:
        guard.handle_event(
            self.event("SessionStart", 20.0, source="compact"),
            self.env,
        )

        result = guard.handle_event(
            self.event(
                "UserPromptSubmit",
                20.0,
                prompt="Faça o checkpoint de recuperação agora.",
            ),
            self.env,
        )

        self.assertIsNotNone(result)
        self.assertNotEqual((result or {}).get("decision"), "block")
        context = result["hookSpecificOutput"]["additionalContext"].lower()
        self.assertIn("checkpoint", context)
        self.assertIn("agora", context)
        self.assertNotIn("concluir a unidade atual", context)
        self.assertTrue(
            guard.load_state(self.data_dir, "session-a")["checkpoint_started"]
        )

    def test_recovery_post_tool_use_advises_once_at_next_safe_point(self) -> None:
        guard.handle_event(
            self.event("SessionStart", 20.0, source="compact"),
            self.env,
        )
        event = self.event("PostToolUse", 20.0)

        result = guard.handle_event(event, self.env)
        repeated = guard.handle_event(event, self.env)

        self.assertIsNotNone(result)
        context = result["hookSpecificOutput"]["additionalContext"].lower()
        self.assertIn("checkpoint", context)
        self.assertIn("próximo ponto seguro", context)
        self.assertNotIn("pare", context)
        self.assertIsNone(repeated)

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
        self.assertIn("BOARD_CANONICO", context)
        self.assertIn("Comprove `ORQ_PACKAGE_ROOT`", context)
        self.assertIn("thread_root", context)
        self.assertIn("`state: ok` com `exists: false`", context)
        self.assertIn("`/orq:init`", context)
        self.assertIn("não leia o `board` e encaminhe para `/orq:init`", context)
        self.assertNotIn("checkpoint de recuperação", context.lower())
        reset = guard.load_state(self.data_dir, "session-a")
        self.assertEqual(reset["phase"], "normal")
        self.assertFalse(reset["checkpoint_verified"])
        self.assertIsNone(reset["checkpoint_percent"])
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

    def test_legacy_clear_required_continues_current_request_above_ninety(self) -> None:
        path = guard.state_path(self.data_dir, "session-a")
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "phase": "clear_required",
                    "pre_alert_sent": True,
                    "checkpoint_started": True,
                    "clear_required": True,
                    "telemetry_warning_sent": False,
                    "last_percent": 90.2,
                    "updated_at": 1,
                }
            ),
            encoding="utf-8",
        )

        result = guard.handle_event(
            self.event(
                "UserPromptSubmit",
                90.2,
                prompt="Continue o pedido atual no modo Goal.",
            ),
            self.env,
        )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIsNone(result)
        state = guard.load_state(self.data_dir, "session-a")
        persisted = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(state["checkpoint_verified"])
        self.assertEqual(state["phase"], "checkpoint_verified")
        self.assertNotIn("clear_required", persisted)
        self.assertNotEqual(persisted["phase"], "clear_required")

    def test_codex_stop_and_prompt_never_block_at_consultive_bands(self) -> None:
        cases = [
            ("Stop", 55.0, {"stop_hook_active": False}),
            ("Stop", 60.0, {"stop_hook_active": False}),
            ("Stop", 70.0, {"stop_hook_active": False}),
            ("Stop", 90.2, {"stop_hook_active": False}),
            (
                "UserPromptSubmit",
                60.0,
                {"prompt": "Continue a tarefa atual."},
            ),
            (
                "UserPromptSubmit",
                70.0,
                {"prompt": "Continue a tarefa atual."},
            ),
            (
                "UserPromptSubmit",
                90.2,
                {"prompt": "Continue o objetivo atual no modo Goal."},
            ),
        ]

        for index, (event_name, percent, extra) in enumerate(cases):
            with self.subTest(event_name=event_name, percent=percent):
                event = self.event(event_name, percent, **extra)
                event["session_id"] = f"consultive-{index}"
                result = guard.handle_event(event, self.env)

                self.assertNotEqual((result or {}).get("decision"), "block")
                self.assertNotIn("reason", result or {})
                if event_name == "Stop":
                    self.assertIsNotNone(result)
                    self.assertIn("checkpoint", result["systemMessage"].lower())
                else:
                    self.assertIsNotNone(result)
                    context = result["hookSpecificOutput"]["additionalContext"]
                    self.assertIn("atenda o pedido atual", context.lower())
                    self.assertNotIn("/clear", context.lower())

    def test_clear_marker_creation_failure_resets_state_without_persistence(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        state_file = guard.state_path(self.data_dir, "session-a")
        self.assertEqual(pending_reset_markers(self.data_dir, "session-a"), [])
        original_named_temporary_file = guard.tempfile.NamedTemporaryFile

        def fail_only_reset_marker_creation(*args: object, **kwargs: object) -> object:
            if str(kwargs.get("prefix", "")).endswith(".reset."):
                raise OSError("sem espaço para o marcador")
            return original_named_temporary_file(*args, **kwargs)

        with mock.patch.object(
            guard.tempfile,
            "NamedTemporaryFile",
            side_effect=fail_only_reset_marker_creation,
        ):
            result = guard.handle_event(
                self.event("SessionStart", 10.0, source="clear"),
                self.env,
            )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertFalse(state_file.exists())
        self.assertEqual(pending_reset_markers(self.data_dir, "session-a"), [])
        self.assertIn("falhou aberto", result["systemMessage"].lower())
        self.assertIn("reset", result["systemMessage"].lower())
        self.assertIn("estado anterior foi removido", result["systemMessage"].lower())
        self.assertNotIn("não foi aplicado", result["systemMessage"].lower())

    def test_clear_marker_creation_failure_warns_when_fallback_cannot_remove_state(
        self,
    ) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        state_file = guard.state_path(self.data_dir, "session-a")
        state_before = state_file.read_text(encoding="utf-8")
        original_named_temporary_file = guard.tempfile.NamedTemporaryFile
        original_unlink = Path.unlink
        unlink_attempts: list[Path] = []

        def fail_only_reset_marker_creation(*args: object, **kwargs: object) -> object:
            if str(kwargs.get("prefix", "")).endswith(".reset."):
                raise OSError("sem espaço para o marcador")
            return original_named_temporary_file(*args, **kwargs)

        def reject_state_removal(
            path: Path,
            *args: object,
            **kwargs: object,
        ) -> None:
            if path == state_file:
                unlink_attempts.append(path)
                raise OSError("estado não removível")
            return original_unlink(path, *args, **kwargs)

        with (
            mock.patch.object(
                guard.tempfile,
                "NamedTemporaryFile",
                side_effect=fail_only_reset_marker_creation,
            ),
            mock.patch.object(Path, "unlink", new=reject_state_removal),
        ):
            result = guard.handle_event(
                self.event("SessionStart", 10.0, source="clear"),
                self.env,
            )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertEqual(unlink_attempts, [state_file])
        self.assertEqual(state_file.read_text(encoding="utf-8"), state_before)
        self.assertEqual(pending_reset_markers(self.data_dir, "session-a"), [])
        message = result["systemMessage"].lower()
        self.assertIn("reset do estado de contexto não foi aplicado por completo", message)
        self.assertIn("falhou aberto", message)
        self.assertNotIn("o estado anterior foi removido", message)

    def test_reset_marker_scan_failure_is_visible_without_new_persistence(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        state_file = guard.state_path(self.data_dir, "session-a")
        state_before = state_file.read_text(encoding="utf-8")
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        pending_marker = pending_reset_markers(self.data_dir, "session-a")[0]
        reset_dir = pending_marker.parent
        original_iterdir = Path.iterdir

        def reject_only_reset_marker_scan(path: Path) -> object:
            if path == reset_dir:
                raise OSError("diretório indisponível")
            return original_iterdir(path)

        with mock.patch.object(Path, "iterdir", new=reject_only_reset_marker_scan):
            result = guard.handle_event(
                self.event("UserPromptSubmit", 10.0, prompt="continue"),
                self.env,
            )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertTrue(pending_marker.exists())
        self.assertEqual(state_file.read_text(encoding="utf-8"), state_before)
        self.assertIn("falhou aberto", result["systemMessage"].lower())
        self.assertIn("reset", result["systemMessage"].lower())

    def test_generated_reset_marker_is_found_without_entry_stat(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        legacy_marker = guard._state_reset_path(self.data_dir, "session-a")
        pending_marker = pending_reset_markers(self.data_dir, "session-a")[0]
        self.assertNotEqual(pending_marker.name, legacy_marker.name)

        with mock.patch.object(
            Path,
            "is_file",
            side_effect=AssertionError("a enumeração não deve consultar stat da entrada"),
        ):
            result = guard.handle_event(
                self.event("UserPromptSubmit", 10.0, prompt="continue"),
                self.env,
            )

        self.assertIsNone(result)
        self.assertFalse(pending_marker.exists())
        reset_state = guard.load_state(self.data_dir, "session-a")
        self.assertFalse(reset_state["recovery_required"])
        self.assertFalse(reset_state["checkpoint_started"])

    def test_reset_marker_removal_failure_keeps_marker_for_retry(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        pending_marker = pending_reset_markers(self.data_dir, "session-a")[0]
        original_unlink = Path.unlink

        def reject_pending_marker_removal(
            path: Path,
            *args: object,
            **kwargs: object,
        ) -> None:
            if path == pending_marker:
                raise OSError("marcador não removível")
            return original_unlink(path, *args, **kwargs)

        with mock.patch.object(
            Path,
            "unlink",
            new=reject_pending_marker_removal,
        ):
            result = guard.handle_event(
                self.event("UserPromptSubmit", 10.0, prompt="continue"),
                self.env,
            )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertTrue(pending_marker.exists())
        persisted_state = guard.load_state(self.data_dir, "session-a")
        self.assertEqual(persisted_state["phase"], "normal")
        self.assertFalse(persisted_state["recovery_required"])
        self.assertIn("falhou aberto", result["systemMessage"].lower())
        self.assertIn("reset", result["systemMessage"].lower())

        retry = guard.handle_event(
            self.event("UserPromptSubmit", 10.0, prompt="continue"),
            self.env,
        )
        self.assertIsNone(retry)
        self.assertFalse(pending_marker.exists())

    def test_failed_persist_keeps_observed_reset_pending(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        pending_marker = pending_reset_markers(self.data_dir, "session-a")[0]

        with mock.patch.object(guard, "save_state", return_value=False):
            result = guard.handle_event(
                self.event("UserPromptSubmit", 10.0, prompt="continue"),
                self.env,
            )

        self.assertNotEqual((result or {}).get("decision"), "block")
        self.assertIn("reset", result["systemMessage"].lower())
        self.assertIn("falhou aberto", result["systemMessage"].lower())
        self.assertTrue(
            pending_marker.exists(),
            "falha ao persistir não pode consumir o reset fotografado",
        )

        next_result = guard.handle_event(
            self.event("UserPromptSubmit", 10.0, prompt="continue"),
            self.env,
        )
        self.assertIsNone(next_result)
        self.assertFalse(pending_marker.exists())
        reset_state = guard.load_state(self.data_dir, "session-a")
        self.assertEqual(reset_state["phase"], "normal")
        self.assertFalse(reset_state["recovery_required"])

    def test_failed_persist_preserves_context_calculated_after_reset(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))

        with mock.patch.object(guard, "save_state", return_value=False):
            result = guard.handle_event(
                self.event(
                    "UserPromptSubmit",
                    61.0,
                    prompt="implemente a próxima tela",
                ),
                self.env,
            )

        self.assertIsNotNone(result)
        assert result is not None
        context = result["hookSpecificOutput"]["additionalContext"].lower()
        self.assertIn("atenda o pedido atual", context)
        self.assertIn("checkpoint", context)
        self.assertIn("não foi aplicado por completo", result["systemMessage"].lower())

    def test_reset_without_persistence_keeps_observed_reset_pending(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        pending_marker = pending_reset_markers(self.data_dir, "session-a")[0]
        event_without_persistence = {
            "hook_event_name": "EventoDesconhecido",
            "session_id": "session-a",
        }

        result = guard.handle_event(event_without_persistence, self.env)

        self.assertTrue(
            pending_marker.exists(),
            "um reset fotografado exige ao menos uma persistência comprovada antes do consumo",
        )
        self.assertIn("reset", result["systemMessage"].lower())
        self.assertIn("falhou aberto", result["systemMessage"].lower())

    def test_reset_marker_already_removed_is_treated_as_consumed(self) -> None:
        old_state = guard.default_state()
        old_state["phase"] = "recovery_required"
        old_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", old_state))
        self.assertTrue(guard._mark_state_reset(self.data_dir, "session-a"))
        pending_marker = pending_reset_markers(self.data_dir, "session-a")[0]
        original_pending_paths = guard._pending_state_reset_paths

        def enumerate_then_remove(data_dir: Path, session_id: str) -> list[Path] | None:
            paths = original_pending_paths(data_dir, session_id)
            pending_marker.unlink()
            return paths

        with mock.patch.object(
            guard,
            "_pending_state_reset_paths",
            side_effect=enumerate_then_remove,
        ):
            result = guard.handle_event(
                self.event("UserPromptSubmit", 10.0, prompt="continue"),
                self.env,
            )

        self.assertIsNone(result)
        reset_state = guard.load_state(self.data_dir, "session-a")
        self.assertEqual(reset_state["phase"], "normal")
        self.assertFalse(reset_state["recovery_required"])

    def test_prior_transaction_cannot_consume_newer_clear_reset(self) -> None:
        stale_state = guard.default_state()
        stale_state["phase"] = "recovery_required"
        stale_state["recovery_required"] = True
        self.assertTrue(guard.save_state(self.data_dir, "session-a", stale_state))
        held_lock = guard._acquire_state_lock(self.data_dir, "session-a")
        self.assertIsNotNone(held_lock)
        reset_created = threading.Event()
        clear_response: list[dict | None] = []
        original_mark_reset = guard._mark_state_reset

        def mark_reset_and_signal(data_dir: Path, session_id: str) -> bool:
            marked = original_mark_reset(data_dir, session_id)
            reset_created.set()
            return marked

        try:
            with (
                mock.patch.object(
                    guard,
                    "_mark_state_reset",
                    side_effect=mark_reset_and_signal,
                ),
                mock.patch.object(guard, "STATE_LOCK_WAIT_SECONDS", 0.05),
            ):
                clear_worker = threading.Thread(
                    target=lambda: clear_response.append(
                        guard.handle_event(
                            self.event("SessionStart", 10.0, source="clear"),
                            self.env,
                        )
                    ),
                    daemon=True,
                )
                clear_worker.start()
                self.assertTrue(reset_created.wait(timeout=1))
                guard._persist_response(
                    self.data_dir,
                    "session-a",
                    stale_state,
                    None,
                )
                self.assertTrue(
                    pending_reset_markers(self.data_dir, "session-a"),
                    "a persistência antiga não pode consumir a geração criada depois",
                )
                clear_worker.join(timeout=1)
        finally:
            guard._release_state_lock(held_lock)

        self.assertFalse(clear_worker.is_alive())
        self.assertIn("falhou aberto", clear_response[0]["systemMessage"])
        next_prompt = guard.handle_event(
            self.event("UserPromptSubmit", 10.0, prompt="continue"),
            self.env,
        )

        self.assertIsNone(next_prompt)
        reset_state = guard.load_state(self.data_dir, "session-a")
        self.assertEqual(reset_state["phase"], "normal")
        self.assertFalse(reset_state["checkpoint_started"])
        self.assertFalse(reset_state["checkpoint_verified"])
        self.assertFalse(reset_state["recovery_required"])


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
        self.assertNotEqual(output.get("decision"), "block")
        self.assertIn("checkpoint", output["systemMessage"].lower())


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


class ContextGuardConsultiveLanguageLintTest(unittest.TestCase):
    """Impede que a prosa distribuída volte a contradizer os hooks consultivos."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-consultive-lint-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plugin = self.root / "orq"
        (self.plugin / "commands").mkdir(parents=True)

    def test_reports_blocking_codex_checkpoint_language(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        stack.write_text(
            "No Codex, o checkpoint é obrigatório aos 60%. "
            "Até concluir o checkpoint, o trabalho novo fica bloqueado.\n",
            encoding="utf-8",
        )

        problems = lint_module.validate_codex_consultive_language(
            self.root,
            self.plugin,
        )

        messages = [item[2] for item in problems]
        self.assertTrue(any("checkpoint obrigatório" in item for item in messages))
        self.assertTrue(any("trabalho bloqueado" in item for item in messages))

    def test_reports_paraphrase_in_any_live_command(self) -> None:
        command = self.plugin / "commands" / "implement-next.md"
        command.write_text(
            "No Codex, é obrigatório fazer checkpoint; "
            "pare o trabalho até concluir o checkpoint.\n",
            encoding="utf-8",
        )

        problems = lint_module.validate_codex_consultive_language(
            self.root,
            self.plugin,
        )

        self.assertTrue(
            any(item[0] == Path("orq/commands/implement-next.md") for item in problems)
        )
        messages = [item[2] for item in problems]
        self.assertTrue(any("checkpoint obrigatório" in item for item in messages))
        self.assertTrue(any("trabalho interrompido" in item for item in messages))

    def test_accepts_consultive_codex_checkpoint_language(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, 60% recomenda checkpoint; o pedido atual continua e nada é bloqueado.\n",
            encoding="utf-8",
        )

        self.assertEqual(
            lint_module.validate_codex_consultive_language(self.root, self.plugin),
            [],
        )

    def test_accepts_explicit_negative_blocking_phrases(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, não é obrigatório fazer checkpoint; não interrompa o trabalho.\n",
            "No Codex, nunca é obrigatório fazer checkpoint; jamais interrompa o trabalho.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_negative_clause_does_not_mask_later_blocking_clause(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        probes = (
            (
                "No Codex, checkpoint não é obrigatório em teste. "
                "Em produção, checkpoint é obrigatório.\n",
                "checkpoint obrigatório",
            ),
            (
                "No Codex, o trabalho não é bloqueado em teste. "
                "Em produção, o trabalho fica bloqueado até checkpoint.\n",
                "trabalho bloqueado",
            ),
        )
        for phrase, expected in probes:
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(any(expected in item for item in messages))

    def test_contrast_and_host_switch_do_not_mask_codex_blocking_clause(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        probes = (
            "No Codex, checkpoint não é obrigatório em teste, "
            "mas em produção checkpoint é obrigatório.\n",
            "Claude: checkpoint não é obrigatório — "
            "Codex: checkpoint é obrigatório.\n",
        )
        for phrase in probes:
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_claude_blocking_contract_does_not_contaminate_codex(self) -> None:
        (self.plugin / "commands" / "checkpoint.md").write_text(
            "Claude: checkpoint é obrigatório antes do clear — "
            "Codex: checkpoint não é obrigatório.\n",
            encoding="utf-8",
        )

        self.assertEqual(
            lint_module.validate_codex_consultive_language(self.root, self.plugin),
            [],
        )

    def test_shared_host_clause_is_codex_contract_in_any_order(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for hosts in ("Codex e Claude", "Claude e Codex"):
            with self.subTest(hosts=hosts):
                stack.write_text(
                    f"{hosts}: checkpoint é obrigatório antes do clear.\n",
                    encoding="utf-8",
                )
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_labeled_host_rules_split_on_conjunction(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for connector in ("e", "enquanto"):
            with self.subTest(connector=connector, direction="codex_positive"):
                stack.write_text(
                    "Claude: checkpoint não é obrigatório "
                    f"{connector} Codex: checkpoint é obrigatório.\n",
                    encoding="utf-8",
                )
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )
            with self.subTest(connector=connector, direction="claude_positive"):
                stack.write_text(
                    "Claude: checkpoint é obrigatório "
                    f"{connector} Codex: checkpoint é apenas recomendado.\n",
                    encoding="utf-8",
                )
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_unpunctuated_host_switch_does_not_mask_codex_rule(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Claude checkpoint não é obrigatório e "
            "no Codex checkpoint é obrigatório.\n",
            encoding="utf-8",
        )

        messages = [
            item[2]
            for item in lint_module.validate_codex_consultive_language(
                self.root,
                self.plugin,
            )
        ]
        self.assertTrue(any("checkpoint obrigatório" in item for item in messages))

    def test_reports_checkpoint_as_precondition_to_continue(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        probes = (
            "No Codex, deve-se fazer checkpoint antes de continuar o trabalho.\n",
            "No Codex, só continue o trabalho depois do checkpoint.\n",
            "No Codex, checkpoint é requisito para prosseguir o pedido.\n",
        )
        for phrase in probes:
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("continuidade condicionada" in item for item in messages)
                )

    def test_comma_does_not_detach_checkpoint_subject(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, checkpoint não é opcional, "
            "é obrigatório antes de continuar o trabalho.\n",
            encoding="utf-8",
        )

        messages = [
            item[2]
            for item in lint_module.validate_codex_consultive_language(
                self.root,
                self.plugin,
            )
        ]
        self.assertTrue(any("checkpoint obrigatório" in item for item in messages))

    def test_reports_passive_checkpoint_precondition(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, só é permitido continuar o trabalho depois do checkpoint.\n",
            encoding="utf-8",
        )

        messages = [
            item[2]
            for item in lint_module.validate_codex_consultive_language(
                self.root,
                self.plugin,
            )
        ]
        self.assertTrue(any("continuidade condicionada" in item for item in messages))

    def test_incidental_codex_mention_keeps_claude_scope(self) -> None:
        (self.plugin / "commands" / "checkpoint.md").write_text(
            "Claude: checkpoint é obrigatório porque o Codex não oferece /clear.\n",
            encoding="utf-8",
        )

        self.assertEqual(
            lint_module.validate_codex_consultive_language(self.root, self.plugin),
            [],
        )

    def test_accepts_negation_with_auxiliary_before_mandatory(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, checkpoint não deve ser obrigatório.\n",
            "No Codex, checkpoint jamais será obrigatório.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_same_host_conjunction_does_not_mask_later_positive(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for connector in ("e", "enquanto"):
            with self.subTest(connector=connector):
                stack.write_text(
                    "No Codex, checkpoint não é obrigatório em teste "
                    f"{connector} em produção checkpoint é obrigatório.\n",
                    encoding="utf-8",
                )
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_shared_host_subject_with_prepositions_is_codex_contract(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "Para o Claude e o Codex, checkpoint é obrigatório.\n",
            "No Codex e no Claude, checkpoint é obrigatório.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_compound_predicate_keeps_checkpoint_subject(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, checkpoint é requisito de segurança "
            "e condição para continuar o trabalho.\n",
            encoding="utf-8",
        )

        messages = [
            item[2]
            for item in lint_module.validate_codex_consultive_language(
                self.root,
                self.plugin,
            )
        ]
        self.assertTrue(any("continuidade condicionada" in item for item in messages))

    def test_implicit_checkpoint_subject_does_not_mask_later_positive(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for connector in ("e", "enquanto"):
            with self.subTest(connector=connector):
                stack.write_text(
                    "No Codex, checkpoint não é obrigatório em teste "
                    f"{connector} é obrigatório em produção.\n",
                    encoding="utf-8",
                )
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_shared_host_subject_with_or_is_codex_contract(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for hosts in ("Claude ou Codex", "Codex ou Claude"):
            with self.subTest(hosts=hosts):
                stack.write_text(
                    f"{hosts}: checkpoint é obrigatório.\n",
                    encoding="utf-8",
                )
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_unrelated_explicit_subject_is_not_checkpoint_obligation(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, checkpoint é recomendado e o backup é obrigatório.\n",
            "No Codex, checkpoint não é obrigatório e o backup é obrigatório.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_shared_host_subject_with_literal_and_or_is_codex_contract(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for hosts in ("Claude e/ou Codex", "Codex e/ou Claude"):
            with self.subTest(hosts=hosts):
                stack.write_text(
                    f"{hosts}: checkpoint é obrigatório.\n",
                    encoding="utf-8",
                )
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(
                    any("checkpoint obrigatório" in item for item in messages)
                )

    def test_owner_gate_is_not_checkpoint_blocking(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, checkpoint é recomendado; "
            "o pedido fica bloqueado até aprovação do dono.\n",
            "No Codex, checkpoint é recomendado; "
            "pare o trabalho apenas se o dono negar aprovação.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_unrelated_subject_without_article_is_not_checkpoint_obligation(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, checkpoint é recomendado e backup é obrigatório.\n",
            "No Codex, checkpoint é recomendado e `git status` é obrigatório.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_owner_gate_in_same_clause_is_not_checkpoint_blocking(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, checkpoint é recomendado e "
            "o pedido fica bloqueado até aprovação do dono.\n",
            encoding="utf-8",
        )

        self.assertEqual(
            lint_module.validate_codex_consultive_language(self.root, self.plugin),
            [],
        )

    def test_adverbial_does_not_hide_unrelated_subject(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, checkpoint é recomendado e "
            "em produção o backup é obrigatório.\n",
            encoding="utf-8",
        )

        self.assertEqual(
            lint_module.validate_codex_consultive_language(self.root, self.plugin),
            [],
        )

    def test_demonstrative_resumes_checkpoint_subject(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, checkpoint deve ser feito e isso é obrigatório.\n",
            encoding="utf-8",
        )

        messages = [
            item[2]
            for item in lint_module.validate_codex_consultive_language(
                self.root,
                self.plugin,
            )
        ]
        self.assertTrue(any("checkpoint obrigatório" in item for item in messages))

    def test_checkpoint_clitic_keeps_causal_blocking_link(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        probes = (
            (
                "No Codex, checkpoint é recomendado; "
                "até concluí-lo, o trabalho fica bloqueado.\n",
                "trabalho bloqueado",
            ),
            (
                "No Codex, checkpoint é recomendado; "
                "pare o trabalho até concluí-lo.\n",
                "trabalho interrompido",
            ),
        )
        for phrase, expected in probes:
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(any(expected in item for item in messages))

    def test_checkpoint_elliptical_reference_keeps_causal_blocking_link(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        probes = (
            (
                "No Codex, checkpoint é recomendado; "
                "até concluir, o trabalho fica bloqueado.\n",
                "trabalho bloqueado",
            ),
            (
                "No Codex, checkpoint é recomendado; "
                "pare o trabalho até fazê-lo.\n",
                "trabalho interrompido",
            ),
        )
        for phrase, expected in probes:
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(any(expected in item for item in messages))

    def test_checkpoint_ellipsis_does_not_resume_unrelated_subject(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, checkpoint é recomendado; até concluir a revisão, "
            "o trabalho fica bloqueado pela CI.\n",
            "No Codex, checkpoint é recomendado; o backup é exigido; "
            "pare o trabalho até fazê-lo.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_checkpoint_ellipsis_survives_incidental_clause(self) -> None:
        (self.plugin / "commands" / "stack.md").write_text(
            "No Codex, checkpoint é recomendado; avise o dono; "
            "até concluí-lo, o trabalho fica bloqueado.\n",
            encoding="utf-8",
        )

        messages = [
            item[2]
            for item in lint_module.validate_codex_consultive_language(
                self.root,
                self.plugin,
            )
        ]
        self.assertTrue(any("trabalho bloqueado" in item for item in messages))

    def test_closest_explicit_subject_replaces_checkpoint_antecedent(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, checkpoint é recomendado e o backup é exigido; "
            "pare o trabalho até fazê-lo.\n",
            "No Codex, checkpoint é recomendado; faça o backup; "
            "pare o trabalho até fazê-lo.\n",
            "No Codex, checkpoint é recomendado; inicie a revisão; "
            "até concluir, o trabalho fica bloqueado pela CI.\n",
            "No Codex, checkpoint é recomendado; faça o backup antes do checkpoint; "
            "pare o trabalho até fazê-lo.\n",
            "No Codex, checkpoint é recomendado; o backup do checkpoint é exigido; "
            "pare o trabalho até fazê-lo.\n",
            "No Codex, checkpoint é recomendado; faça o checkpoint e envie o backup; "
            "pare o trabalho até fazê-lo.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )

    def test_owner_attribution_does_not_hide_explicit_checkpoint_condition(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, até concluir o checkpoint, "
            "o trabalho fica bloqueado pelo dono.\n",
            "No Codex, explique por que o trabalho fica bloqueado pelo dono "
            "até concluir o checkpoint.\n",
            "No Codex, explique por que, até concluir o checkpoint, "
            "o trabalho fica bloqueado pelo dono.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                messages = [
                    item[2]
                    for item in lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    )
                ]
                self.assertTrue(any("trabalho bloqueado" in item for item in messages))

    def test_narrative_owner_block_is_not_checkpoint_policy(self) -> None:
        stack = self.plugin / "commands" / "stack.md"
        for phrase in (
            "No Codex, antes do checkpoint, explique por que "
            "o pedido foi bloqueado pelo dono.\n",
            "No Codex, antes do checkpoint, explique por que "
            "o pedido está bloqueado pelo dono.\n",
            "No Codex, explique por que o pedido está bloqueado pelo dono "
            "e, depois do checkpoint, informe a decisão.\n",
            "No Codex, explique por que o pedido está bloqueado pelo dono "
            "e, depois do checkpoint, apresente a decisão.\n",
            "No Codex, explique por que o pedido está bloqueado pelo dono e, "
            "depois do checkpoint, então informe a decisão.\n",
        ):
            with self.subTest(phrase=phrase):
                stack.write_text(phrase, encoding="utf-8")
                self.assertEqual(
                    lint_module.validate_codex_consultive_language(
                        self.root,
                        self.plugin,
                    ),
                    [],
                )


class ContextGuardReleaseVersionTest(unittest.TestCase):
    def test_release_version_is_coordinated(self) -> None:
        repo_root = PLUGIN_ROOT.parent
        manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text()
        )
        # A versão vive em QUATRO lugares e o manifesto é a fonte. Fixar um
        # quinto valor aqui criaria uma quinta fonte de verdade — e um bump
        # legítimo passaria a "quebrar" o teste. Derivar do manifesto mantém a
        # prova de coordenação sem inventar mais um lugar para esquecer.
        expected = manifest["version"]
        marketplace = json.loads(
            (repo_root / ".claude-plugin" / "marketplace.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "orq")
        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        memory = (repo_root / "memory" / "MEMORY.md").read_text(encoding="utf-8")

        self.assertRegex(expected, r"^\d+\.\d+\.\d+$")
        self.assertEqual(entry["version"], expected)
        self.assertIn(f"## Status\n\n`{expected}`", readme)
        self.assertIn(f"**Versão:** {expected} ", memory)

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
    def test_reset_concurrency_contract_is_unambiguous(self) -> None:
        architecture = (
            PLUGIN_ROOT.parent / "memory" / "wiki" / "arquitetura.md"
        ).read_text(encoding="utf-8")
        distribution = (
            PLUGIN_ROOT.parent / "memory" / "wiki" / "distribuicao.md"
        ).read_text(encoding="utf-8")
        architecture_contract = " ".join(architecture.split())
        distribution_contract = " ".join(distribution.split())

        for phrase in (
            "marcador legado é reivindicado por renomeação atômica",
            "a ação do host continua sem tocar no estado",
            "a garantia de exclusão mútua fica indisponível",
        ):
            self.assertIn(phrase, architecture_contract)
        for phrase in (
            "o suporte a Windows só está validado",
            "não bloqueia a publicação para plataformas já validadas",
            "não permite declarar Windows validado",
        ):
            self.assertIn(phrase, distribution_contract)

    def test_guard_contract_is_present_in_live_instructions(self) -> None:
        required = {
            PLUGIN_ROOT / "commands" / "checkpoint.md": [
                "Checkpoint verificado; conversa continua.",
                "Seguro dar `/clear`.",
                "Claude",
                "Codex",
                "mesma conversa",
                "consultivo",
                "compactação é sempre livre",
                "texto equivalente não registra `checkpoint_verified`",
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
                "`Directory` é proibida como fonte de release",
                "`git ls-remote`",
                "`HEAD` publicado",
                "`<fonte-local>` vem de clone limpo no mesmo SHA",
            ],
            PLUGIN_ROOT / "skills" / "orq" / "SKILL.md": [
                "55%",
                "60%",
                "70%",
                "SessionStart(source=compact)",
                "Claude",
                "/clear",
                "consultivo",
                "nunca bloqueia",
                "modo Goal",
                "additionalContext",
                "compactação é sempre livre",
            ],
            PLUGIN_ROOT.parent / "memory" / "wiki" / "arquitetura.md": [
                "consultivo",
                "nunca bloqueia",
                "modo Goal",
                "SessionStart(source=compact)",
                "aviso consultivo",
                "clear_required",
                "falha de persistência",
                "additionalContext",
            ],
            PLUGIN_ROOT.parent / "README.md": [
                "Claude Code e Codex",
                "compactação é sempre livre",
                "additionalContext",
                "clear_required",
            ],
        }
        missing: dict[str, list[str]] = {}
        for path, phrases in required.items():
            text = path.read_text(encoding="utf-8")
            absent = [phrase for phrase in phrases if phrase not in text]
            if absent:
                missing[str(path.relative_to(PLUGIN_ROOT.parent))] = absent

        self.assertEqual(missing, {})

        live_text = "\n".join(
            path.read_text(encoding="utf-8") for path in required
        )
        self.assertNotIn("CLEAR_REQUIRED", live_text)
        self.assertNotIn("compactação detectada como contingência", live_text)
        self.assertNotIn("trabalho novo é bloqueado", live_text)
        self.assertNotIn("compactação liberada", live_text)
        self.assertNotIn("não destrava", live_text)


class ContextGuardCacheComparisonTest(unittest.TestCase):
    """Metadados do runtime não podem mascarar divergência real do plugin."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-cache-lint-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def make_pair(self, name: str) -> tuple[Path, Path]:
        case = self.root / name
        cache = case / "cache"
        plugin = case / "plugin"
        cache.mkdir(parents=True)
        plugin.mkdir(parents=True)
        for base in (cache, plugin):
            (base / "same.txt").write_text("same\n", encoding="utf-8")
        return cache, plugin

    def make_installed_cache(self, name: str) -> tuple[Path, Path]:
        manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text()
        )
        home = self.root / name / "home"
        cache = (
            home
            / ".claude"
            / "plugins"
            / "cache"
            / "orquestra"
            / "orq"
            / manifest["version"]
        )
        shutil.copytree(PLUGIN_ROOT, cache)
        return home, cache

    def run_lint_main(self, home: Path) -> tuple[int, str]:
        # `raiz` aqui é o repositório REAL (`PLUGIN_ROOT.parent`), não uma
        # cópia — esta classe mede comparação de cache, não o board. A guarda
        # de posse do T-086 é neutralizada porque o board vivo muda a cada card
        # assumido: um card em `[>]`/`[~]` sem marcador reprovaria o controle
        # negativo daqui por um motivo alheio ao que esta classe testa.
        output = io.StringIO()
        argv = [str(LINT_PATH), str(PLUGIN_ROOT.parent)]
        with (
            mock.patch.object(Path, "home", return_value=home),
            mock.patch.object(sys, "argv", argv),
            mock.patch("sys.stdout", output),
            mock.patch.object(lint_module, "validate_marcador_host_kanban", return_value=[]),
        ):
            result = lint_module.main()
        return result, output.getvalue()

    def test_main_ignores_in_use_in_installed_cache(self) -> None:
        home, cache = self.make_installed_cache("main-in-use")
        marker = cache / ".in_use" / "4242"
        marker.parent.mkdir()
        marker.write_text("", encoding="utf-8")

        result, output = self.run_lint_main(home)

        self.assertEqual(result, 0)
        self.assertIn("coerência interna ok", output)

    def test_main_ignores_top_level_orphaned_at_in_installed_cache(self) -> None:
        home, cache = self.make_installed_cache("main-orphaned")
        (cache / ".orphaned_at").write_text("2026-08-30\n", encoding="utf-8")

        result, output = self.run_lint_main(home)

        self.assertEqual(result, 0)
        self.assertIn("coerência interna ok", output)

    def test_main_reports_ds_store_as_real_extra(self) -> None:
        home, cache = self.make_installed_cache("main-ds-store")
        (cache / ".DS_Store").write_text("finder\n", encoding="utf-8")

        result, output = self.run_lint_main(home)

        self.assertEqual(result, 1)
        self.assertIn("extra:.DS_Store", output)
        self.assertIn("corrija a árvore instalada ou a fonte", output)
        self.assertNotIn("bumpe a versão", output)

    def test_main_reports_real_extra_alongside_in_use(self) -> None:
        home, cache = self.make_installed_cache("main-combined")
        marker = cache / ".in_use" / "4242"
        marker.parent.mkdir()
        marker.write_text("", encoding="utf-8")
        (cache / "real-extra.txt").write_text("extra\n", encoding="utf-8")

        result, output = self.run_lint_main(home)

        self.assertEqual(result, 1)
        self.assertIn("real-extra.txt", output)
        self.assertNotIn(".in_use/4242", output)


if __name__ == "__main__":
    unittest.main()
