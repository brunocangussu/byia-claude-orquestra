import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import claude_mem_status


NOW = 2_000_000
MINUTE = 60_000


class ClaudeMemStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.db_path = self.root / "claude-mem.db"
        self.settings_path = self.root / "settings.json"
        self.settings_path.write_text(
            json.dumps({"CLAUDE_MEM_EXCLUDED_PROJECTS": ""}),
            encoding="utf-8",
        )
        self.connection = sqlite3.connect(self.db_path)
        self.connection.executescript(
            """
            CREATE TABLE sdk_sessions (
                id INTEGER PRIMARY KEY,
                content_session_id TEXT,
                memory_session_id TEXT,
                project TEXT,
                platform_source TEXT,
                started_at_epoch INTEGER,
                completed_at_epoch INTEGER,
                status TEXT
            );
            CREATE TABLE user_prompts (
                id INTEGER PRIMARY KEY,
                session_db_id INTEGER,
                content_session_id TEXT,
                prompt_number INTEGER,
                prompt_text TEXT,
                created_at_epoch INTEGER
            );
            CREATE TABLE observations (
                id INTEGER PRIMARY KEY,
                memory_session_id TEXT,
                prompt_number INTEGER,
                created_at_epoch INTEGER
            );
            CREATE TABLE session_summaries (
                id INTEGER PRIMARY KEY,
                memory_session_id TEXT,
                prompt_number INTEGER,
                created_at_epoch INTEGER
            );
            """
        )
        self.connection.commit()

    def tearDown(self) -> None:
        self.connection.close()
        self.temporary.cleanup()

    def evaluate(self, **overrides):
        arguments = {
            "db_path": self.db_path,
            "settings_path": self.settings_path,
            "platform": "codex",
            "project": "safe-project",
            "content_session_id": "content-1",
            "since_epoch_ms": NOW - MINUTE,
            "stale_after_minutes": 15,
            "expect_summary": True,
            "now_epoch_ms": NOW,
            "extra_excluded_patterns": (),
        }
        arguments.update(overrides)
        return claude_mem_status.evaluate_status(**arguments)

    def insert_session(
        self,
        *,
        session_id=1,
        content_session_id="content-1",
        memory_session_id="memory-1",
        project="safe-project",
        platform="codex",
        started=NOW - 10 * MINUTE,
        completed=None,
        status="active",
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO sdk_sessions
                (id, content_session_id, memory_session_id, project, platform_source,
                 started_at_epoch, completed_at_epoch, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                content_session_id,
                memory_session_id,
                project,
                platform,
                started,
                completed,
                status,
            ),
        )
        self.connection.commit()

    def insert_prompt(self, *, session_id=1, content_session_id="content-1", at=NOW - MINUTE):
        self.connection.execute(
            """
            INSERT INTO user_prompts
                (session_db_id, content_session_id, prompt_number, prompt_text, created_at_epoch)
            VALUES (?, ?, 1, 'SENTINEL_CONTENT_MUST_NOT_BE_READ', ?)
            """,
            (session_id, content_session_id, at),
        )
        self.connection.commit()

    def insert_observation(self, *, memory_session_id="memory-1", at=NOW - 30_000):
        self.connection.execute(
            """
            INSERT INTO observations (memory_session_id, prompt_number, created_at_epoch)
            VALUES (?, 1, ?)
            """,
            (memory_session_id, at),
        )
        self.connection.commit()

    def insert_summary(self, *, memory_session_id="memory-1", at=NOW - 10_000):
        self.connection.execute(
            """
            INSERT INTO session_summaries (memory_session_id, prompt_number, created_at_epoch)
            VALUES (?, 1, ?)
            """,
            (memory_session_id, at),
        )
        self.connection.commit()

    def test_excluded_project_does_not_require_database(self):
        self.settings_path.write_text(
            json.dumps({"CLAUDE_MEM_EXCLUDED_PROJECTS": "*Bruno Vascular*"}),
            encoding="utf-8",
        )
        result = self.evaluate(
            db_path=self.root / "missing.db",
            project="Bruno Vascular - Gestão Dados Marketing",
        )
        self.assertEqual("EXCLUÍDO", result["state"])
        self.assertEqual("project_matches_exclusion", result["reason"])

    def test_no_session_is_delayed_inside_slo(self):
        result = self.evaluate(since_epoch_ms=NOW - MINUTE)
        self.assertEqual("ATRASADO", result["state"])
        self.assertEqual("session_not_created_yet", result["reason"])

    def test_no_session_is_stopped_after_slo(self):
        result = self.evaluate(since_epoch_ms=NOW - 16 * MINUTE)
        self.assertEqual("PARADO", result["state"])
        self.assertEqual("session_not_created", result["reason"])

    def test_no_session_without_watermark_is_idle(self):
        result = self.evaluate(since_epoch_ms=None)
        self.assertEqual("OCIOSO", result["state"])

    def test_complete_metadata_path_is_capturing(self):
        self.insert_session()
        self.insert_prompt()
        self.insert_observation()
        self.insert_summary()
        result = self.evaluate()
        self.assertEqual("CAPTURANDO", result["state"])
        self.assertEqual(1, result["metrics"]["prompts"])
        self.assertEqual(1, result["metrics"]["observations"])
        self.assertEqual(1, result["metrics"]["summaries"])
        self.assertNotIn("SENTINEL_CONTENT_MUST_NOT_BE_READ", json.dumps(result))

    def test_prompt_without_observation_is_delayed_inside_slo(self):
        self.insert_session(started=NOW - MINUTE)
        self.insert_prompt(at=NOW - 30_000)
        result = self.evaluate(since_epoch_ms=NOW - MINUTE)
        self.assertEqual("ATRASADO", result["state"])
        self.assertEqual("observation_not_committed_yet", result["reason"])

    def test_prompt_without_observation_is_stopped_after_slo(self):
        self.insert_session(started=NOW - 20 * MINUTE)
        self.insert_prompt(at=NOW - 16 * MINUTE)
        result = self.evaluate(since_epoch_ms=NOW - 20 * MINUTE)
        self.assertEqual("PARADO", result["state"])
        self.assertEqual("observation_not_committed", result["reason"])

    def test_null_memory_session_is_stopped_after_slo(self):
        self.insert_session(memory_session_id=None, started=NOW - 20 * MINUTE)
        result = self.evaluate(since_epoch_ms=NOW - 20 * MINUTE)
        self.assertEqual("PARADO", result["state"])
        self.assertEqual("memory_session_id_missing", result["reason"])

    def test_event_after_completion_is_stopped(self):
        self.insert_session(completed=NOW - 5 * MINUTE, status="completed")
        self.insert_prompt(at=NOW - 4 * MINUTE)
        self.insert_observation(at=NOW - 3 * MINUTE)
        self.insert_summary(at=NOW - 2 * MINUTE)
        result = self.evaluate()
        self.assertEqual("PARADO", result["state"])
        self.assertEqual("event_after_session_completion", result["reason"])

    def test_missing_summary_is_delayed_when_required(self):
        self.insert_session(started=NOW - MINUTE)
        self.insert_prompt(at=NOW - 50_000)
        self.insert_observation(at=NOW - 40_000)
        result = self.evaluate(since_epoch_ms=NOW - MINUTE)
        self.assertEqual("ATRASADO", result["state"])
        self.assertEqual("summary_not_committed_yet", result["reason"])

    def test_missing_database_is_indeterminate(self):
        result = self.evaluate(
            db_path=self.root / "missing.db",
            project="safe-project",
        )
        self.assertEqual("INDETERMINADO", result["state"])
        self.assertEqual("database_unavailable", result["reason"])

    def test_project_scope_does_not_accept_another_project(self):
        self.insert_session(project="another-project")
        self.insert_prompt()
        self.insert_observation()
        self.insert_summary()
        result = self.evaluate(since_epoch_ms=NOW - 16 * MINUTE)
        self.assertEqual("PARADO", result["state"])
        self.assertEqual("session_not_created", result["reason"])


if __name__ == "__main__":
    unittest.main()
