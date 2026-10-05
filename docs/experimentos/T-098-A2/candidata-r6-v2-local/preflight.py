"""Preflight local determinístico da candidata R6 v2; não chama rede."""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

SAMPLE_NAME = "amostra.json"
MANIFEST_NAME = "manifesto.json"
RULE_NAME = "regra-lexical-dev.json"
CASE_FIELDS = {"id", "text"}
ADJUDICATION_FIELDS = {"id", "gold", "split", "family", "policy", "response_behavior", "facts"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _tokens(text):
    require(isinstance(text, str), "texto não é string")
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    return sorted(set(re.findall(r"[a-z0-9]{2,}", folded)))


def validate_sample(sample):
    require(isinstance(sample, dict) and set(sample) == {"cases"}, "schema da amostra divergente")
    cases = sample["cases"]
    require(isinstance(cases, list) and len(cases) == 48, "amostra deve ter 48 casos")
    ids = []
    for case in cases:
        require(isinstance(case, dict), "caso da amostra não é objeto")
        require(set(case) == CASE_FIELDS, "schema do caso divergente")
        require(all(isinstance(case[field], str) and case[field].strip() for field in CASE_FIELDS), "caso da amostra inválido")
        ids.append(case["id"])
    require(ids == [f"Y{index:03d}" for index in range(1, 49)], "ordem ou IDs da amostra divergentes")


def validate_adjudications(manifest):
    require(isinstance(manifest, dict), "manifesto não é objeto")
    classes = manifest.get("classes")
    entries = manifest.get("adjudications")
    require(isinstance(classes, list) and classes == ["trivial", "pequeno", "normal", "consulta", "alto_risco", "abster"], "classes do manifesto divergentes")
    require(isinstance(entries, list) and len(entries) == 48, "adjudicações inválidas")
    ids, per_class, per_split = [], Counter(), Counter()
    for entry in entries:
        require(isinstance(entry, dict), "adjudicação não é objeto")
        require(set(entry) == ADJUDICATION_FIELDS, "schema da adjudicação divergente")
        require(isinstance(entry["id"], str) and re.fullmatch(r"Y[0-9]{3}", entry["id"]) is not None, "ID da adjudicação inválido")
        require(entry["gold"] in classes, "gold da adjudicação inválido")
        require(entry["split"] in {"dev", "reserved"}, "split da adjudicação inválido")
        require(isinstance(entry["family"], str) and entry["family"].strip(), "família da adjudicação inválida")
        require(isinstance(entry["policy"], str) and entry["policy"].strip(), "política da adjudicação inválida")
        require(isinstance(entry["response_behavior"], str) and entry["response_behavior"].strip(), "comportamento de saída inválido")
        require(isinstance(entry["facts"], list) and entry["facts"] and all(isinstance(fact, str) and fact for fact in entry["facts"]), "fatos da adjudicação inválidos")
        ids.append(entry["id"])
        per_class[entry["gold"]] += 1
        per_split[entry["split"]] += 1
    require(ids == [f"Y{index:03d}" for index in range(1, 49)], "ordem ou IDs das adjudicações divergentes")
    require(all(per_class[name] == 8 for name in classes), "classes devem ter oito casos")
    require(per_split == {"dev": 24, "reserved": 24}, "splits devem ter 24 casos")


def validate_taxonomy(manifest):
    taxonomy = manifest.get("taxonomy")
    entries = manifest["adjudications"]
    require(isinstance(taxonomy, dict) and taxonomy, "taxonomia inválida")
    by_id = {entry["id"]: entry for entry in entries}
    assigned = []
    for family, identifiers in taxonomy.items():
        require(isinstance(family, str) and family.strip(), "nome de família inválido")
        require(isinstance(identifiers, list) and identifiers, "família sem casos")
        for identifier in identifiers:
            require(isinstance(identifier, str), "ID de taxonomia inválido")
            require(identifier in by_id, "ID ausente da taxonomia")
            require(by_id[identifier]["family"] == family, "família da adjudicação divergente")
            assigned.append(identifier)
    require(sorted(assigned) == [f"Y{index:03d}" for index in range(1, 49)], "taxonomia não cobre os casos uma vez")


def validate_batches(manifest):
    batches = manifest.get("batches")
    entries = manifest["adjudications"]
    require(isinstance(batches, list) and len(batches) == 4, "manifesto exige quatro lotes")
    expected = []
    for split in ("dev", "reserved"):
        identifiers = sorted(entry["id"] for entry in entries if entry["split"] == split)
        expected.extend(identifiers[index:index + 12] for index in range(0, len(identifiers), 12))
    for batch in batches:
        require(isinstance(batch, list) and len(batch) == 12 and all(isinstance(identifier, str) for identifier in batch), "lote do manifesto inválido")
    require(batches == expected, "ordem dos quatro lotes divergente")


def validate_policy_boundary(manifest):
    policies = manifest.get("policies")
    require(isinstance(policies, dict) and set(policies) == set(manifest["classes"]), "políticas do manifesto divergentes")
    for gold, policy in policies.items():
        require(isinstance(policy, dict), "política não é objeto")
        require(isinstance(policy.get("name"), str) and policy["name"], "nome de política inválido")
        require(isinstance(policy.get("response_behavior"), str) and policy["response_behavior"], "comportamento de política inválido")
        facts = policy.get("required_facts")
        require(isinstance(facts, list) and facts and all(isinstance(fact, str) and fact for fact in facts), "fatos de política inválidos")
    for entry in manifest["adjudications"]:
        policy = policies[entry["gold"]]
        require(entry["policy"] == policy["name"], "política da adjudicação não corresponde ao gold")
        require(entry["response_behavior"] == policy["response_behavior"], "comportamento da adjudicação não corresponde à política")
        require(set(policy["required_facts"]).issubset(set(entry["facts"])), "fatos obrigatórios ausentes")
        if entry["gold"] == "consulta":
            require("missing_decisive_scope" not in entry["facts"], "consulta delimitada marcada como sem escopo")
        if entry["gold"] == "abster":
            require(entry["response_behavior"] == "ask_clarifying_question", "abster sem pergunta de esclarecimento")
            require("missing_decisive_scope" in entry["facts"], "abster sem escopo decisivo ausente")


def validate_fixtures(manifest):
    fixtures = manifest.get("fixtures")
    require(isinstance(fixtures, dict) and set(fixtures) == {"Y009", "Y011", "Y041"}, "fixtures obrigatórias divergentes")
    by_id = {entry["id"]: entry for entry in manifest["adjudications"]}
    for identifier, fixture in fixtures.items():
        require(isinstance(fixture, dict), "fixture não é objeto")
        require(by_id[identifier]["gold"] == fixture.get("expected_gold"), "gold da fixture divergente")
        expected_facts = fixture.get("expected_facts")
        require(isinstance(expected_facts, list), "fatos da fixture inválidos")
        require(set(expected_facts).issubset(set(by_id[identifier]["facts"])), "fatos da fixture divergentes")
    require(fixtures["Y041"].get("empty_result") is None, "Y041 exige vazio igual a null")


def gold_by_id(manifest):
    return {entry["id"]: entry["gold"] for entry in manifest["adjudications"]}


def format_profile(cases, labels):
    require(isinstance(cases, list), "casos de formato inválidos")
    require(isinstance(labels, dict), "rótulos de formato inválidos")
    totals, questions = Counter(), Counter()
    for case in cases:
        require(isinstance(case, dict), "caso de formato não é objeto")
        require(set(case) == CASE_FIELDS, "schema de formato divergente")
        identifier = case["id"]
        text = case["text"]
        require(isinstance(identifier, str) and isinstance(text, str), "tipo de formato inválido")
        require(identifier in labels and isinstance(labels[identifier], str), "rótulo de formato ausente")
        totals[labels[identifier]] += 1
        questions[labels[identifier]] += int("?" in text)
    return dict(totals), dict(questions)


def validate_format_diversity(cases, labels):
    totals, questions = format_profile(cases, labels)
    require(totals.get("abster") == 8, "contagem de abster divergente")
    require(questions.get("abster", 0) < totals["abster"], "formato exclusivo de abster")
    require(sum(count for gold, count in questions.items() if gold != "abster") > 0, "formato exclusivo de abster")
    require(questions.get("consulta", 0) > 0, "consulta delimitada sem pergunta na amostra")
    return totals, questions


def classifier_batches(sample, manifest):
    validate_sample(sample)
    validate_adjudications(manifest)
    by_id = {case["id"]: case["text"] for case in sample["cases"]}
    return [[{"id": identifier, "text": by_id[identifier]} for identifier in batch] for batch in manifest["batches"]]


def validate_projection(batches, sample, manifest):
    validate_sample(sample)
    validate_adjudications(manifest)
    validate_batches(manifest)
    require(isinstance(batches, list) and len(batches) == 4, "projeção exige quatro lotes")
    source = {case["id"]: case["text"] for case in sample["cases"]}
    projected_ids = []
    for batch, expected_ids in zip(batches, manifest["batches"]):
        require(isinstance(batch, list) and len(batch) == 12, "lote deve conter doze casos")
        identifiers = []
        for case in batch:
            require(isinstance(case, dict), "item de projeção não é objeto")
            require(set(case) == CASE_FIELDS, "projeção contaminada")
            require(isinstance(case["id"], str) and isinstance(case["text"], str) and case["text"].strip(), "projeção inválida")
            require(case["id"] in source, "ID divergente na projeção")
            require(case["text"] == source[case["id"]], "projeção texto divergente")
            identifiers.append(case["id"])
            projected_ids.append(case["id"])
        require(identifiers == expected_ids, "lote mistura ou reordena partições")
    require(projected_ids == [identifier for batch in manifest["batches"] for identifier in batch], "IDs divergentes na projeção")


def derive_rule_rows(cases, labels, classes, parameters):
    require(isinstance(cases, list) and cases, "casos para fit inválidos")
    require(isinstance(labels, dict) and labels, "rótulos para fit inválidos")
    require(isinstance(classes, list) and classes, "classes para fit inválidas")
    require(isinstance(parameters, dict), "parâmetros para fit inválidos")
    top_k = parameters.get("top_k")
    smoothing = parameters.get("smoothing")
    require(isinstance(top_k, int) and top_k > 0, "top_k para fit inválido")
    require(isinstance(smoothing, int) and smoothing > 0, "smoothing para fit inválido")
    rows = []
    for gold in classes:
        positive = [set(_tokens(case["text"])) for case in cases if labels.get(case["id"]) == gold]
        negative = [set(_tokens(case["text"])) for case in cases if labels.get(case["id"]) != gold]
        require(positive, "classe sem caso de treino")
        candidates = sorted(set().union(*positive, *negative))
        scored = []
        for word in candidates:
            positive_count = sum(word in words for words in positive)
            negative_count = sum(word in words for words in negative)
            weight = round(math.log((positive_count + smoothing) / (negative_count + smoothing)), 6)
            scored.append({"word": word, "positive": positive_count, "negative": negative_count, "weight": weight})
        scored.sort(key=lambda feature: (-feature["weight"], feature["word"]))
        require(len(scored) >= top_k, "tokens insuficientes para fit")
        rows.append({"class": gold, "features": scored[:top_k]})
    return rows


def fit_rule(sample, manifest):
    validate_sample(sample)
    validate_adjudications(manifest)
    labels = gold_by_id(manifest)
    split_by_id = {entry["id"]: entry["split"] for entry in manifest["adjudications"]}
    dev_cases = [case for case in sample["cases"] if split_by_id[case["id"]] == "dev"]
    require(len(dev_cases) == 24, "dev para fit divergente")
    parameters = manifest["rule"]["parameters"]
    return {
        "algorithm": manifest["rule"]["algorithm"],
        "trained_split": "dev",
        "trained_cases": 24,
        "used_reserved_for_fit": False,
        "classes": manifest["classes"],
        "parameters": parameters,
        "rules": derive_rule_rows(dev_cases, labels, manifest["classes"], parameters)
    }


def validate_rule_schema(rule, manifest):
    require(isinstance(rule, dict), "regra não é objeto")
    expected_fields = {"algorithm", "trained_split", "trained_cases", "used_reserved_for_fit", "classes", "parameters", "rules"}
    require(set(rule) == expected_fields, "schema da regra divergente")
    require(rule["algorithm"] == manifest["rule"]["algorithm"] and rule["trained_split"] == "dev", "origem declarada da regra inválida")
    require(rule["trained_cases"] == 24 and rule["used_reserved_for_fit"] is False, "contagem declarada da regra inválida")
    require(rule["classes"] == manifest["classes"], "classes da regra divergentes")
    require(rule["parameters"] == manifest["rule"]["parameters"], "parâmetros da regra divergentes")
    rules = rule["rules"]
    require(isinstance(rules, list) and len(rules) == len(manifest["classes"]), "regras por classe inválidas")
    previous_classes = []
    for entry in rules:
        require(isinstance(entry, dict), "entrada de regra não é objeto")
        require(set(entry) == {"class", "features"}, "entrada de regra inválida")
        previous_classes.append(entry["class"])
        features = entry["features"]
        require(isinstance(features, list) and len(features) == 5, "top cinco inválido")
        previous = None
        words = set()
        for feature in features:
            require(isinstance(feature, dict), "feature não é objeto")
            require(set(feature) == {"word", "positive", "negative", "weight"}, "feature inválida")
            require(isinstance(feature["word"], str) and re.fullmatch(r"[a-z0-9]{2,}", feature["word"]) is not None, "token inválido")
            require(feature["word"] not in words, "token duplicado")
            words.add(feature["word"])
            require(all(isinstance(feature[key], int) and not isinstance(feature[key], bool) for key in ("positive", "negative")), "contagem não inteira")
            require(0 <= feature["positive"] <= 4 and 0 <= feature["negative"] <= 20, "contagem fora do intervalo")
            require(isinstance(feature["weight"], (int, float)) and not isinstance(feature["weight"], bool) and math.isfinite(feature["weight"]), "peso não finito")
            key = (-feature["weight"], feature["word"])
            require(previous is None or previous <= key, "ordem de desempate inválida")
            previous = key
    require(previous_classes == manifest["classes"], "ordem das regras inválida")


def validate_rule(rule, sample, manifest):
    validate_rule_schema(rule, manifest)
    require(rule == fit_rule(sample, manifest), "derivação da regra divergente")


def verify_frozen_snapshot(root, sample, manifest, rule):
    root = Path(root)
    require(_sha256_file(root / SAMPLE_NAME) == manifest["sample"]["sha256"], "snapshot da amostra divergente")
    require(_sha256_file(root / RULE_NAME) == manifest["rule"]["sha256"], "snapshot da regra divergente")
    require(_read_json(root / SAMPLE_NAME) == sample, "amostra carregada divergente")
    require(_read_json(root / RULE_NAME) == rule, "regra carregada divergente")


def verify_historical_snapshots(root, manifest):
    a2_root = Path(root).resolve().parent
    for section in ("historical_r5", "historical_r6_v1"):
        snapshots = manifest.get(section)
        require(isinstance(snapshots, dict) and snapshots, f"histórico {section} inválido")
        for relative, expected in snapshots.items():
            require(isinstance(relative, str) and isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected) is not None, "hash histórico inválido")
            require(_sha256_file(a2_root / relative) == expected, f"histórico alterado: {relative}")


def run_local_preflight(root):
    root = Path(root)
    sample = _read_json(root / SAMPLE_NAME)
    manifest = _read_json(root / MANIFEST_NAME)
    rule = _read_json(root / RULE_NAME)
    validate_sample(sample)
    validate_adjudications(manifest)
    validate_taxonomy(manifest)
    validate_batches(manifest)
    validate_policy_boundary(manifest)
    validate_fixtures(manifest)
    totals, questions = validate_format_diversity(sample["cases"], gold_by_id(manifest))
    validate_rule(rule, sample, manifest)
    verify_frozen_snapshot(root, sample, manifest, rule)
    verify_historical_snapshots(root, manifest)
    batches = classifier_batches(sample, manifest)
    validate_projection(batches, sample, manifest)
    return {"cases": len(sample["cases"]), "questions": questions, "totals": totals}


if __name__ == "__main__":
    print(json.dumps(run_local_preflight(Path(__file__).resolve().parent), ensure_ascii=False, sort_keys=True))
