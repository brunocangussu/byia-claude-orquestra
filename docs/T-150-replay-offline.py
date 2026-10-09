"""Reproduz o snapshot local e controles sintéticos; não chama modelos."""

import copy
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "orq/scripts"))
import work_evidence as helper  # noqa: E402


def main():
    raw = (ROOT / "docs/T-150-evidencias-replay.json").read_bytes()
    base = json.loads(raw)
    gate_sha = hashlib.sha256(
        (ROOT / "docs/T-150-verificacoes-locais.json").read_bytes()
    ).hexdigest()
    report = []

    def record(name, result, expected, kind):
        assert result["action"] == expected, name
        assert result["permissions_granted"] is False, name
        assert result["ready_for_done"] is False, name
        assert result["network"] == "disabled", name
        report.append({
            "case": name, "kind": kind, "action": result["action"],
            "advice_status": result["advice_status"], "pass": True,
        })

    record("historical_T150_no_external_budget", helper.recommend(base),
           "prepare_review_gate", "historical_control_not_current_state")
    stalled = copy.deepcopy(base)
    stalled.update(review_rounds=3, stalled_rounds=2, blockers=1, progress=[])
    record("two_stalled_rounds", helper.recommend(stalled),
           "diagnose_and_change_strategy", "synthetic_control")
    approved = copy.deepcopy(base)
    approved.update(stalled_rounds=2, blockers=0)
    approved["verification"] = {key: "passed" for key in ("targeted", "suite", "mutations")}
    approved["review"] = {"state": "approved", "snapshot_current": True}
    for local_work in (True, False):
        approved["authority"]["local_work"] = local_work
        record("approved_snapshot_with_old_stagnation_" + str(local_work),
               helper.recommend(approved), "await_owner_validation", "synthetic_control")
    third = copy.deepcopy(base)
    third.update(review_rounds=3, blockers=1, stalled_rounds=0)
    third["progress"] = [{"kind": "mutation_killed", "receipt_sha256": gate_sha}]
    record("third_review_with_progress", helper.recommend(third),
           "fix_and_test", "synthetic_control")

    def mock(choice, confidence=0.9):
        frozen = helper.freeze_jev(base)
        criteria = frozen["request"]["questions"]["next_action"]["criteria"]
        probabilities = {key: 0.0 for key in criteria}
        probabilities[choice if choice in criteria else "prepare_review_gate"] = 1.0
        return {
            "schema": 1, "request_sha256": frozen["request_sha256"],
            "response": {"model": helper.MODEL, "answers": {
                "next_action": {"type": "choice", "choice": choice,
                                "confidence": confidence,
                                "probabilities": probabilities},
                "additional_tests": {"type": "noul", "noul": 0.8},
                "further_review": {"type": "noul", "noul": 0.9},
            }},
        }

    record("mock_JEV_adds_discriminating_test",
           helper.interpret_jev(base, mock("add_regression_case")),
           "add_regression_case", "synthetic_JEV_response")
    record("mock_JEV_unbudgeted_review",
           helper.interpret_jev(base, mock("request_independent_review")),
           "prepare_review_gate", "synthetic_JEV_response")
    low_confidence = helper.interpret_jev(base, mock("add_regression_case", 0.5))
    assert low_confidence["advice_status"] == "low_confidence"
    record("mock_JEV_low_confidence", low_confidence,
           "prepare_review_gate", "synthetic_JEV_response")
    stale = mock("add_regression_case")
    stale["request_sha256"] = "0" * 64
    record("mock_JEV_stale_snapshot", helper.interpret_jev(base, stale),
           "prepare_review_gate", "synthetic_JEV_response")
    wrong = mock("add_regression_case")
    wrong["response"]["model"] = "untrusted-model"
    record("mock_JEV_wrong_model", helper.interpret_jev(base, wrong),
           "prepare_review_gate", "synthetic_JEV_response")
    freeze = helper.freeze_jev(base)
    body = freeze["request_body_utf8"].encode("utf-8")
    assert len(body) == freeze["request_bytes"]
    assert hashlib.sha256(body).hexdigest() == freeze["request_sha256"]
    print(json.dumps({
        "schema": 1, "state": "OFFLINE_REPLAY_VERIFIED", "cases": report,
        "total": len(report), "passed": len(report),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "request_bytes": freeze["request_bytes"],
        "request_sha256": freeze["request_sha256"],
        "external_calls": 0, "actual_JEV_responses": 0,
        "benefit_proved": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
