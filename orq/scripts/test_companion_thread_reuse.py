#!/usr/bin/env python3
"""Guardas do reúso de tasks do Codex Companion por card e papel (T-075)."""

from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent


def read_repo(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


class CompanionThreadReuseTest(unittest.TestCase):
    def test_canonical_skill_defines_durable_same_card_same_role_reuse(self) -> None:
        skill = read_repo("orq/skills/orq/SKILL.md")
        skill_flat = " ".join(skill.split())

        self.assertIn("Mesmo card + mesmo papel", skill)
        self.assertIn("card`, `papel`, `jobId`, `threadId`, `status`", skill)
        self.assertIn("--fresh --json", skill)
        self.assertIn("--resume-thread <threadId> --json", skill)
        self.assertIn("Mudou o card ou o papel", skill)
        self.assertIn("segunda revisão deliberadamente independente", skill_flat)
        self.assertIn("nunca delete", skill)

    def test_planning_and_review_commands_apply_the_protocol(self) -> None:
        planning = read_repo("orq/commands/plan-next.md")
        review = read_repo("orq/commands/revisar.md")

        for document in (planning, review):
            self.assertIn("codex:codex-rescue", document)
            self.assertIn("--fresh --json", document)
            self.assertIn("--resume-thread <threadId> --json", document)
            self.assertIn("rawOutput", document)
            self.assertIn("jobId", document)
            self.assertIn("threadId", document)

    def test_invocation_matrices_route_openai_on_claude_through_companion(self) -> None:
        factory = read_repo("orq/commands/elenco.md")
        live = read_repo("memory/wiki/_elenco.md")

        for document in (factory, live):
            self.assertIn("OpenAI × host Claude", document)
            self.assertIn("codex:codex-rescue", document)
            self.assertIn("codex-companion.mjs task", document)
            self.assertIn("--model <modelo> --effort <effort>", document)


if __name__ == "__main__":
    unittest.main()
