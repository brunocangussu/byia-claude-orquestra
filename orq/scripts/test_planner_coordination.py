"""Modo de coordenação é opt-in no mesmo Planner, não outro Manager."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import planner_coordination as coordination


class CoordinationBriefTest(unittest.TestCase):
    def test_default_is_off_not_inherited_from_other_card(self):
        value = coordination.compose()
        self.assertEqual(value.get("coordination_mode"), "off")
        self.assertEqual(value["instructions"], "")
        self.assertEqual(value["extra_calls"], 0)

    def test_technical_mode_reuses_system_planner_with_one_authority(self):
        value = coordination.compose("technical", "sistema")
        self.assertEqual(value.get("coordination_mode"), "technical")
        self.assertEqual(value["role"], "planner·sistema")
        self.assertEqual(value["authority"], "Manager")
        self.assertEqual(value["extra_calls"], 0)
        for term in ("dependências", "dono", "contratos", "integração", "testes",
                     "Não despache", "Não aprove", "não altera o board"):
            self.assertIn(term, value["instructions"])
        self.assertNotIn("gpt-", value["instructions"])

    def test_interface_does_not_silently_use_system_profile(self):
        with self.assertRaises(ValueError):
            coordination.compose("technical", "interface")

    def test_unknown_mode_does_not_create_new_agent_or_permission(self):
        for mode in ("auto", True, "reviewer", "orchestrator"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    coordination.compose(mode, "sistema")

    def test_real_cli_is_opt_in_and_does_not_follow_environment(self):
        script = Path(__file__).with_name("planner_coordination.py")
        result = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True,
            env={"COORDINATION_MODE": "technical", "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout).get("coordination_mode"), "off")

    def test_cli_technical_is_explicit(self):
        script = Path(__file__).with_name("planner_coordination.py")
        result = subprocess.run(
            [sys.executable, str(script), "--mode", "technical", "--track", "sistema"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["role"], "planner·sistema")
        self.assertEqual(json.loads(result.stdout).get("coordination_mode"), "technical")

    def test_cli_rejects_technical_interface_without_partial_contract(self):
        script = Path(__file__).with_name("planner_coordination.py")
        result = subprocess.run(
            [sys.executable, str(script), "--mode", "technical", "--track", "interface"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr), {"error": "SYSTEM_TRACK_REQUIRED"})


if __name__ == "__main__":
    unittest.main()
