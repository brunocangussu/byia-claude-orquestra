"""Apoio consultivo offline: prioriza evidência; nunca despacha nem aprova."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys


MODEL = "jev-1.13.0"
MAX_BYTES = 16 * 1024
STATUSES = {"passed", "failed", "not_run"}
ACTIONS = {
    "diagnose_and_change_strategy": "Diagnosticar causa e escolher uma abordagem diferente.",
    "fix_and_test": "Corrigir bloqueador auditado e provar a correção.",
    "add_regression_case": "Adicionar um caso que discrimine a falha, sem repetir o mesmo teste.",
    "run_targeted_tests": "Executar testes focados pendentes.",
    "run_full_suite": "Executar a suíte completa pendente.",
    "run_mutation_checks": "Verificar se os oráculos detectam a regressão.",
    "audit_review_findings": "Auditar os achados do parecer atual antes de propor outra chamada.",
    "request_independent_review": "Propor revisão independente dentro do gate humano registrado.",
    "prepare_review_gate": "Preparar pacote e pedir gate externo, sem chamada.",
    "prepare_local_gate": "Pedir escopo local necessário, sem ampliar autorização.",
    "await_owner_validation": "Pedir validação do produto pelo dono, sem declarar DONE.",
    "abstain": "Informação insuficiente; conservar regra local.",
}


def _keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("INVALID_FIELDS")


def _count(value):
    if type(value) is not int or not 0 <= value <= 10000:
        raise ValueError("INVALID_COUNT")


def _enum(value, choices):
    if not isinstance(value, str) or value not in choices:
        raise ValueError("INVALID_ENUM")


def _boolean(value):
    if type(value) is not bool:
        raise ValueError("INVALID_BOOLEAN")


def _digest(value):
    if not isinstance(value, str) or re.fullmatch("[0-9a-f]{64}", value) is None:
        raise ValueError("INVALID_DIGEST")


def _unit(value):
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("INVALID_PROBABILITY")


def validate(value):
    """Recibos são referências declaradas: o Manager ainda audita sua autenticidade."""
    _keys(value, {
        "schema", "snapshot_sha256", "risk", "review_rounds", "stalled_rounds",
        "blockers", "snapshot_changed", "defect_class", "evidence_gap", "progress",
        "verification", "review", "authority",
    })
    if type(value["schema"]) is not int or value["schema"] != 1:
        raise ValueError("INVALID_SCHEMA")
    _digest(value["snapshot_sha256"])
    _enum(value["risk"], {"leve", "normal", "pesada"})
    _enum(value["defect_class"], {
        "unknown", "contract", "permissions", "concurrency", "integration", "documentation"})
    _enum(value["evidence_gap"], {"none", "regression", "coverage", "independence", "root_cause"})
    for key in ("review_rounds", "stalled_rounds", "blockers"):
        _count(value[key])
    _boolean(value["snapshot_changed"])
    if not isinstance(value["progress"], list) or len(value["progress"]) > 64:
        raise ValueError("INVALID_PROGRESS")
    for item in value["progress"]:
        _keys(item, {"kind", "receipt_sha256"})
        _enum(item["kind"], {"red_green", "mutation_killed", "blocker_closed"})
        _digest(item["receipt_sha256"])
    _keys(value["verification"], {"targeted", "suite", "mutations"})
    for status in value["verification"].values():
        _enum(status, STATUSES)
    _keys(value["review"], {"state", "snapshot_current"})
    _enum(value["review"]["state"], {"missing", "blocked", "approved", "unavailable"})
    _boolean(value["review"]["snapshot_current"])
    _keys(value["authority"], {"local_work", "external_remaining", "external_covered"})
    _boolean(value["authority"]["local_work"])
    _boolean(value["authority"]["external_covered"])
    _count(value["authority"]["external_remaining"])


def recommend(value):
    """Contadores não encerram o trabalho nem renovam orçamento de inferência."""
    validate(value)
    verification, authority = value["verification"], value["authority"]
    audit_pending = value["review"]["snapshot_current"] and value["review"]["state"] == "blocked"
    local_pending = audit_pending or bool(value["blockers"]) or any(
        status != "passed" for status in verification.values())
    if not authority["local_work"] and local_pending:
        action = "prepare_local_gate"
    elif authority["local_work"] and local_pending and value["stalled_rounds"] >= 2:
        action = "diagnose_and_change_strategy"
    elif value["blockers"] or "failed" in verification.values():
        action = "fix_and_test"
    elif verification["targeted"] != "passed":
        action = "run_targeted_tests"
    elif verification["suite"] != "passed":
        action = "run_full_suite"
    elif verification["mutations"] != "passed":
        action = "run_mutation_checks"
    elif value["review"]["state"] == "approved" and value["review"]["snapshot_current"]:
        action = "await_owner_validation"
    elif audit_pending:
        action = "audit_review_findings"
    elif value["review"]["state"] == "unavailable" and value["review"]["snapshot_current"]:
        # Um saldo genérico não cobre nova tentativa do mesmo snapshot.
        action = "prepare_review_gate"
    elif authority["external_covered"] and authority["external_remaining"] > 0:
        action = "request_independent_review"
    else:
        action = "prepare_review_gate"
    return {
        "schema": 1, "action": action, "reason": ACTIONS[action], "source": "local_rules",
        "advice_status": "not_requested", "network": "disabled",
        "permissions_granted": False, "ready_for_done": False,
        "requires_manager_audit": True,
    }


def _allowed(value, baseline):
    # A escolha apenas muda a prioridade local, nunca elimina o próximo gate.
    actions = {baseline["action"], "abstain"}
    if value["authority"]["local_work"] and value["stalled_rounds"] < 2:
        if baseline["action"] not in {"prepare_local_gate", "await_owner_validation"}:
            actions.update({"diagnose_and_change_strategy", "add_regression_case"})
    return sorted(actions)


def prepare_jev(value):
    """Prepara estado tipado. Sem texto livre, código, caminhos ou leitura de chave."""
    baseline = recommend(value)
    state = {key: value[key] for key in (
        "snapshot_sha256", "risk", "review_rounds", "stalled_rounds", "blockers",
        "snapshot_changed", "defect_class", "evidence_gap", "verification",
    )}
    state["progress_count"] = len(value["progress"])
    state["review_state"] = value["review"]["state"]
    state["baseline_action"] = baseline["action"]
    return {
        "model": MODEL, "state": state,
        "questions": {
            "next_action": {
                "type": "choice",
                "instructions": (
                    "Priorize uma ação que acrescente evidência ao desenvolvimento. "
                    "Não aprove o produto, dispense gates, rebaixe risco ou renove permissões. "
                    "Com pendência local autorizada, duas rodadas estagnadas exigem "
                    "diagnóstico, não repetição. "
                    "Escolha somente uma opção oferecida; abstenha-se se não houver evidência."
                ),
                "criteria": {key: ACTIONS[key] for key in _allowed(value, baseline)},
            },
            "additional_tests": {
                "type": "noul",
                "instructions": "Há lacuna de evidência que justifica um novo teste discriminante?",
            },
            "further_review": {
                "type": "noul",
                "instructions": "O snapshot precisa de revisão independente nova, sem autorizar seu envio?",
            },
        },
    }


def request_digest(request):
    raw = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def freeze_jev(value):
    """Expõe os bytes exatos do corpo futuro; o envelope local não é o corpo HTTP."""
    request = prepare_jev(value)
    body = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "network": "disabled", "permissions_granted": False,
        "request": request, "request_body_utf8": body,
        "request_bytes": len(body.encode("utf-8")),
        "request_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }


def interpret_jev(value, receipt):
    """Resposta ausente/inválida/abstenção preserva o baseline; nenhum retry."""
    baseline = recommend(value)
    request = prepare_jev(value)
    try:
        _keys(receipt, {"schema", "request_sha256", "response"})
        if type(receipt["schema"]) is not int or receipt["schema"] != 1:
            raise ValueError("INVALID_SCHEMA")
        if receipt["request_sha256"] != request_digest(request):
            raise ValueError("REQUEST_MISMATCH")
        response = receipt["response"]
        if not isinstance(response, dict) or response.get("model") != MODEL:
            raise ValueError("MODEL_MISMATCH")
        answers = response.get("answers")
        _keys(answers, {"next_action", "additional_tests", "further_review"})
        answer = answers["next_action"]
        _keys(answer, {"type", "choice", "confidence", "probabilities"})
        if answer["type"] != "choice" or answer["choice"] not in _allowed(value, baseline):
            raise ValueError("INVALID_CHOICE")
        _unit(answer["confidence"])
        probabilities = answer["probabilities"]
        _keys(probabilities, request["questions"]["next_action"]["criteria"])
        for probability in probabilities.values():
            _unit(probability)
        if abs(sum(probabilities.values()) - 1) > 0.02:
            raise ValueError("INVALID_DISTRIBUTION")
        if probabilities[answer["choice"]] < max(probabilities.values()):
            raise ValueError("CHOICE_MISMATCH")
        for key in ("additional_tests", "further_review"):
            _keys(answers[key], {"type", "noul"})
            if answers[key]["type"] != "noul":
                raise ValueError("INVALID_TYPE")
            _unit(answers[key]["noul"])
        if answer["choice"] == "abstain":
            baseline["advice_status"] = "abstained"
            return baseline
        if answer["confidence"] < 0.75:
            baseline["advice_status"] = "low_confidence"
            return baseline
        action = answer["choice"]
        return dict(baseline, action=action, reason=ACTIONS[action], source="jev_advice",
                    advice_status="accepted", confidence=answer["confidence"],
                    additional_tests=answers["additional_tests"]["noul"],
                    further_review=answers["further_review"]["noul"])
    except (ValueError, TypeError, KeyError):
        return dict(baseline, advice_status="rejected")


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_KEY")
        result[key] = value
    return result


def _read(path):
    try:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("INPUT_TOO_LARGE")
        return json.loads(raw, object_pairs_hook=_unique)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError):
        raise ValueError("INPUT_INVALID") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("recommend", "prepare-jev", "interpret-jev"))
    parser.add_argument("evidence")
    parser.add_argument("receipt", nargs="?")
    args = parser.parse_args()
    try:
        value = _read(args.evidence)
        if args.mode == "interpret-jev":
            if args.receipt is None:
                raise ValueError("RECEIPT_REQUIRED")
            baseline = recommend(value)
            try:
                receipt = _read(args.receipt)
            except ValueError:
                result = dict(baseline, advice_status="rejected")
            else:
                result = interpret_jev(value, receipt)
        elif args.receipt is not None:
            raise ValueError("UNEXPECTED_RECEIPT")
        elif args.mode == "prepare-jev":
            result = freeze_jev(value)
        else:
            result = recommend(value)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, TypeError):
        # Não ecoar dado inválido, caminho privado ou conteúdo de exceção.
        print(json.dumps({"error": "INVALID_INPUT"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
