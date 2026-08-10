#!/usr/bin/env python3
"""Testes do guardião preventivo de contexto do Codex."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


GUARD_PATH = Path(__file__).with_name("context-guard.py")


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


class ContextGuardPresenceTest(unittest.TestCase):
    def test_guard_script_exists(self) -> None:
        self.assertTrue(GUARD_PATH.is_file(), f"guardião ausente: {GUARD_PATH}")


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


if __name__ == "__main__":
    unittest.main()
