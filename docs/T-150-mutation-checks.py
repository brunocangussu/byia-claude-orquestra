"""Mutações locais em memória; nunca altera produto, Git ou chama um modelo."""
import importlib
import io
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "orq/scripts"))


CASES = [
    ("round_ceiling", "work_evidence", "test_work_evidence",
     '    verification, authority = value["verification"], value["authority"]',
     '    verification, authority = value["verification"], value["authority"]\n'
     '    if value["review_rounds"] > 2:\n'
     '        return {"action": "prepare_review_gate"}',
     "ContinuityTest.test_third_or_later_round_does_not_stop_authorized_local_work"),
    ("stagnation_threshold", "work_evidence", "test_work_evidence",
     'and value["stalled_rounds"] >= 2:', 'and value["stalled_rounds"] >= 3:',
     "ContinuityTest.test_two_stalled_rounds_change_strategy_not_global_shutdown"),
    ("local_authority", "work_evidence", "test_work_evidence",
     'if not authority["local_work"] and local_pending:', 'if False:',
     "ContinuityTest.test_no_local_authorization_yields_gate_not_permission"),
    ("external_budget", "work_evidence", "test_work_evidence",
     'elif authority["external_covered"] and authority["external_remaining"] > 0:',
     'elif True:',
     "ContinuityTest.test_external_review_needs_covered_budget_not_round_count"),
    ("stale_review", "work_evidence", "test_work_evidence",
     'elif value["review"]["state"] == "approved" and value["review"]["snapshot_current"]:',
     'elif value["review"]["state"] == "approved":',
     "ContinuityTest.test_old_review_is_not_approval_of_new_snapshot"),
    ("request_binding", "work_evidence", "test_work_evidence",
     'if receipt["request_sha256"] != request_digest(request):', 'if False:',
     "JevAdviceTest.test_pinned_model_and_request_hash_are_required"),
    ("model_identity", "work_evidence", "test_work_evidence",
     'response.get("model") != MODEL', 'False',
     "JevAdviceTest.test_pinned_model_and_request_hash_are_required"),
    ("low_confidence", "work_evidence", "test_work_evidence",
     'answer["confidence"] < 0.75', 'False',
     "JevAdviceTest.test_low_confidence_and_abstention_preserve_baseline"),
    ("permission_grant", "work_evidence", "test_work_evidence",
     '"permissions_granted": False, "ready_for_done": False,',
     '"permissions_granted": True, "ready_for_done": True,',
     "ContinuityTest.test_review_and_tests_never_close_card_without_owner"),
    ("bool_count", "work_evidence", "test_work_evidence",
     'type(value) is not int or not 0 <= value <= 10000',
     'not isinstance(value, int) or not 0 <= value <= 10000',
     "ContinuityTest.test_invalid_metadata_is_rejected_without_echoing_it"),
    ("edit_is_progress", "work_evidence", "test_work_evidence",
     '{"red_green", "mutation_killed", "blocker_closed"}',
     '{"red_green", "mutation_killed", "blocker_closed", "edited_file"}',
     "ContinuityTest.test_progress_requires_receipt_and_closed_kind"),
    ("implicit_coordination", "planner_coordination", "test_planner_coordination",
     'def compose(mode="off", track="sistema"):', 'def compose(mode="technical", track="sistema"):',
     "CoordinationBriefTest.test_default_is_off_not_inherited_from_other_card"),
    ("second_manager", "planner_coordination", "test_planner_coordination",
     '"authority": "Manager"', '"authority": "Coordinator"',
     "CoordinationBriefTest.test_technical_mode_reuses_system_planner_with_one_authority"),
    ("extra_call", "planner_coordination", "test_planner_coordination",
     '"extra_calls": 0', '"extra_calls": 1',
     "CoordinationBriefTest.test_technical_mode_reuses_system_planner_with_one_authority"),
    ("silent_track_change", "planner_coordination", "test_planner_coordination",
     'if mode == "technical" and track != "sistema":', 'if False:',
     "CoordinationBriefTest.test_interface_does_not_silently_use_system_profile"),
    ("duplicate_json_keys", "work_evidence", "test_work_evidence",
     'if key in result:', 'if False:',
     "ContinuityTest.test_duplicate_keys_are_rejected_even_in_otherwise_valid_evidence"),
    ("unbudgeted_jev_review", "work_evidence", "test_work_evidence",
     'actions = {baseline["action"], "abstain"}',
     'actions = {baseline["action"], "abstain", "request_independent_review"}',
     "JevAdviceTest.test_jev_cannot_skip_failed_tests_or_request_unbudgeted_review"),
    ("wire_byte_count", "work_evidence", "test_work_evidence",
     '"request_bytes": len(body.encode("utf-8"))',
     '"request_bytes": len(body)',
     "JevAdviceTest.test_frozen_request_digest_covers_exact_utf8_body_not_envelope"),
    ("stale_stagnation_overrides_approval", "work_evidence", "test_work_evidence",
     'elif authority["local_work"] and local_pending and value["stalled_rounds"] >= 2:',
     'elif value["stalled_rounds"] >= 2:',
     "ContinuityTest.test_old_stagnation_does_not_hide_current_approved_snapshot"),
    ("stagnation_hides_external_gate", "work_evidence", "test_work_evidence",
     'elif authority["local_work"] and local_pending and value["stalled_rounds"] >= 2:',
     'elif authority["local_work"] and value["stalled_rounds"] >= 2:',
     "ContinuityTest.test_stagnation_without_local_pending_work_preserves_external_gate"),
    ("low_confidence_is_false_abstention", "work_evidence", "test_work_evidence",
     'baseline["advice_status"] = "low_confidence"',
     'baseline["advice_status"] = "abstained"',
     "JevAdviceTest.test_low_confidence_and_abstention_preserve_baseline"),
    ("coordination_field_mismatch", "planner_coordination", "test_planner_coordination",
     '"coordination_mode": mode', '"mode": mode',
     "CoordinationBriefTest.test_technical_mode_reuses_system_planner_with_one_authority"),
    ("current_review_audit_omitted", "work_evidence", "test_work_evidence",
     'elif audit_pending:', 'elif False:',
     "ContinuityTest.test_current_failed_review_does_not_spend_generic_external_balance"),
    ("current_review_not_local_pending", "work_evidence", "test_work_evidence",
     'local_pending = audit_pending or bool(value["blockers"])',
     'local_pending = bool(value["blockers"])',
     "ContinuityTest.test_repeated_current_review_audit_changes_strategy_not_external_retry"),
    ("transport_failure_auto_retry", "work_evidence", "test_work_evidence",
     'elif value["review"]["state"] == "unavailable" and value["review"]["snapshot_current"]:',
     'elif False:',
     "ContinuityTest.test_current_failed_review_does_not_spend_generic_external_balance"),
    ("confidence_boundary_rejected", "work_evidence", "test_work_evidence",
     'answer["confidence"] < 0.75', 'answer["confidence"] <= 0.75',
     "JevAdviceTest.test_confidence_boundary_accepts_only_at_or_above_threshold"),
]


def main():
    rows = []
    for name, module, test_module, old, new, test in CASES:
        source = (ROOT / "orq/scripts" / (module + ".py")).read_text(encoding="utf-8")
        if source.count(old) != 1:
            raise RuntimeError("MUTATION_TARGET_NOT_UNIQUE:" + name)
        mutant = types.ModuleType(module + "_mutant")
        exec(compile(source.replace(old, new, 1), module + "_mutant", "exec"), mutant.__dict__)
        tests = importlib.import_module(test_module)
        variable = "support" if module == "work_evidence" else "coordination"
        previous = getattr(tests, variable)
        try:
            setattr(tests, variable, mutant)
            suite = unittest.defaultTestLoader.loadTestsFromName(test, tests)
            result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        finally:
            setattr(tests, variable, previous)
        # Erro de infraestrutura não vale como mutação detectada.
        killed = bool(result.failures) and not result.errors
        rows.append({"mutation": name, "killed": killed, "errors": len(result.errors)})
    # A regressão do parser depende da CLI real, não do módulo mutante em memória.
    # Copie somente script/teste para diretório descartável; nunca edite produto.
    import tempfile
    test_module = importlib.import_module("test_work_evidence")
    source = (ROOT / "orq/scripts/work_evidence.py").read_text(encoding="utf-8")
    old = 'except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):'
    new = 'except (OSError, UnicodeError, json.JSONDecodeError):'
    if source.count(old) != 1:
        raise RuntimeError("MUTATION_TARGET_NOT_UNIQUE:deep_json_traceback")
    with tempfile.TemporaryDirectory(prefix="t150-parser-mutant-") as directory:
        path = Path(directory) / "work_evidence.py"
        path.write_text(source.replace(old, new, 1), encoding="utf-8")
        previous = test_module.OfflineCliTest.script
        try:
            test_module.OfflineCliTest.script = path
            suite = unittest.defaultTestLoader.loadTestsFromName(
                "OfflineCliTest.test_cli_normalizes_deep_json_in_evidence_and_receipt_without_traceback",
                test_module)
            result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        finally:
            test_module.OfflineCliTest.script = previous
    rows.append({"mutation": "deep_json_traceback",
                 "killed": bool(result.failures) and not result.errors,
                 "errors": len(result.errors)})
    # Recibo ilegível não elimina a recomendação local de evidência válida.
    old = '            except ValueError:\n                result = dict(baseline, advice_status="rejected")'
    new = '            except ValueError:\n                raise ValueError("RECEIPT_INVALID") from None'
    if source.count(old) != 1:
        raise RuntimeError("MUTATION_TARGET_NOT_UNIQUE:receipt_local_fallback")
    with tempfile.TemporaryDirectory(prefix="t150-receipt-mutant-") as directory:
        path = Path(directory) / "work_evidence.py"
        path.write_text(source.replace(old, new, 1), encoding="utf-8")
        previous = test_module.OfflineCliTest.script
        try:
            test_module.OfflineCliTest.script = path
            suite = unittest.defaultTestLoader.loadTestsFromName(
                "OfflineCliTest.test_cli_bad_receipt_keeps_local_rules_without_echo_or_retry",
                test_module)
            result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        finally:
            test_module.OfflineCliTest.script = previous
    rows.append({"mutation": "receipt_local_fallback",
                 "killed": bool(result.failures) and not result.errors,
                 "errors": len(result.errors)})
    print(json.dumps({"network_calls": 0, "product_writes": 0, "mutations": rows}, indent=2))
    return 0 if all(row["killed"] for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
