"""Bancada local determinística da candidata R5, sem transporte nem inferência."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parent
R4_ROOT = ROOT.parent / "candidata-r4"
FIELDS = frozenset({"id", "text", "gold", "family", "split", "reason"})
EXPECTED_IDS = frozenset(f"Y{number:03d}" for number in range(1, 49))
FROZEN_HASHES = {
    "amostra.json": "fba8c8a5f07375540369cb471c6cd8a21959564259edc7a823f2d897096ca4fb",
    "regra-lexical-congelada.json": "1099ea053837a70a5e1c7a9da7b4c9d7c6f19a0b6663103fb9f74521eee9a751",
    "resultado-diagnostico-local.json": "1bbc316515b66fa2ee0c3dc575c4aee7006b94e5d6f9567503f8ad4a2ab29b49",
}
TRAINING_SHA256 = "0ca1a92733cdf4d6c8f419dc8e022fdaaa4887d1d1f7dc0924a376f1380a8875"
EXPECTED_SCORE = {"dev": (24, 23), "reserved": (24, 16)}

# São âncoras contratuais textuais, não aprovação de gold ou independência semântica.
CONTROL_PHRASES = {
    "Y006": (
        "inicio=2",
        "passo=2",
        "quantidade=3",
        "[2,4,6]",
        "[2,2,2]",
        "não crie opção ou algoritmo novo",
    ),
    "Y038": (
        "remover espaços externos",
        "rejeições previstas no contrato",
        "categoria desconhecida ou vazia",
    ),
    "Y047": (
        "prosa estática fora dos exemplos gerados",
        "não é lida por agentes, parser ou gerador",
    ),
    "Y026": (
        "calendário de simulação",
        "feriado fictício",
        "não crie compromissos reais, envios ou dependências novas",
    ),
    "Y009": (
        "preview não concede permissão",
        "não executa a confirmação",
        "não muda autorização ou produção",
    ),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _sha256_bytes(value):
    return sha256(value).hexdigest()


def _sha256_text(value):
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_file(path):
    return _sha256_bytes(path.read_bytes())


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _reference_metadata():
    reference = _read_json(R4_ROOT / "amostra.json")
    require(isinstance(reference, dict) and isinstance(reference.get("cases"), list), "referência R4 inválida")
    metadata, family_split = {}, {}
    for case in reference["cases"]:
        require(isinstance(case, dict) and set(case) == FIELDS, "campos inválidos na referência R4")
        identifier = case["id"]
        require(identifier not in metadata, "ID duplicado na referência R4")
        metadata[identifier] = (case["gold"], case["family"], case["split"])
        previous = family_split.setdefault(case["family"], case["split"])
        require(previous == case["split"], "família cruzada na referência R4")
    require(set(metadata) == EXPECTED_IDS, "IDs divergentes na referência R4")
    require(len(family_split) == 18, "a referência R4 deve ter 18 mecanismos")
    return metadata, family_split


REFERENCE_METADATA, FAMILY_SPLIT = _reference_metadata()
CLASSES = tuple(sorted({gold for gold, _, _ in REFERENCE_METADATA.values()}))


def _canonical_text_digests():
    source = ROOT / "amostra.json"
    require(_sha256_file(source) == FROZEN_HASHES[source.name], "amostra congelada divergente")
    sample = _read_json(source)
    return {case["id"]: _sha256_text(case["text"]) for case in sample["cases"]}


CANONICAL_TEXT_DIGESTS = _canonical_text_digests()


def artifact_hashes(root=ROOT):
    """Retorna os selos dos três artefatos congelados, sem os alterar."""
    root = Path(root)
    return {name: _sha256_file(root / name) for name in FROZEN_HASHES}


def verify_frozen_inputs(root=ROOT):
    """Falha antes de pontuar quando amostra, regra ou resultado foram alterados."""
    root = Path(root)
    hashes = artifact_hashes(root)
    for name, expected in FROZEN_HASHES.items():
        require(hashes[name] == expected, f"selo divergente: {name}")
    sample = _read_json(root / "amostra.json")
    rule = _read_json(root / "regra-lexical-congelada.json")
    result = _read_json(root / "resultado-diagnostico-local.json")
    validate_rule(rule)
    require(result.get("rule_sha256") == FROZEN_HASHES["regra-lexical-congelada.json"], "resultado referencia regra errada")
    require(result.get("scored_after_freeze_receipt") is True, "resultado sem selo prévio")
    return sample, rule, result


def validate_sample(sample):
    """Valida estrutura e congelamento; não aprova significado semântico do gold."""
    require(isinstance(sample, dict) and set(sample) == {"cases"}, "envelope inválido")
    cases = sample["cases"]
    require(isinstance(cases, list) and len(cases) == 48, "exige 48 casos")
    ids, texts, counts, families, by_id = set(), set(), Counter(), Counter(), {}
    for case in cases:
        require(isinstance(case, dict) and set(case) == FIELDS, "campos fora da allowlist")
        require(all(isinstance(value, str) and value.strip() for value in case.values()), "campo vazio ou inválido")
        identifier = case["id"]
        require(re.fullmatch(r"Y\d{3}", identifier) is not None, "ID inválido")
        require(identifier not in ids, "ID duplicado")
        ids.add(identifier)
        require(identifier in REFERENCE_METADATA, "ID fora da referência R4")
        require(
            (case["gold"], case["family"], case["split"]) == REFERENCE_METADATA[identifier],
            "metadados id/gold/family/split divergentes da referência R4",
        )
        text = case["text"]
        lowered = text.casefold()
        for phrase in CONTROL_PHRASES.get(identifier, ()):
            require(phrase in lowered, f"controle textual ausente: {identifier}")
        require(_sha256_text(text) == CANONICAL_TEXT_DIGESTS[identifier], "texto congelado divergente")
        normalized = " ".join(lowered.split())
        require(normalized not in texts, "pedido literal repetido")
        texts.add(normalized)
        counts[(case["split"], case["gold"])] += 1
        families[case["family"]] += 1
        by_id[identifier] = case
    require(ids == EXPECTED_IDS, "conjunto de IDs divergente")
    require(
        counts == Counter({(split, gold): 4 for split in ("dev", "reserved") for gold in CLASSES}),
        "classes/partições desequilibradas",
    )
    require(set(families) == set(FAMILY_SPLIT), "manifesto de famílias divergente")
    require(all(size in (2, 3) for size in families.values()), "tamanho de família divergente")
    return by_id


def classifier_batches(sample):
    """Cria quatro lotes locais de doze, com transporte restrito a id/text."""
    validate_sample(sample)
    batches = []
    for split in ("dev", "reserved"):
        cases = sorted((case for case in sample["cases"] if case["split"] == split), key=lambda case: case["id"])
        projected = [{"id": case["id"], "text": case["text"]} for case in cases]
        batches.extend(projected[index:index + 12] for index in range(0, len(projected), 12))
    validate_projection(batches, sample)
    return batches


def validate_projection(batches, sample):
    """Garante que nenhuma razão ou gold cruza a fronteira de classificação."""
    validate_sample(sample)
    require(isinstance(batches, list) and len(batches) == 4, "projeção exige quatro lotes")
    expected_groups = []
    for split in ("dev", "reserved"):
        identifiers = sorted(case["id"] for case in sample["cases"] if case["split"] == split)
        expected_groups.extend(identifiers[index:index + 12] for index in range(0, len(identifiers), 12))
    projected_ids = []
    for batch, expected_ids in zip(batches, expected_groups):
        require(isinstance(batch, list) and len(batch) == 12, "lote deve conter doze casos")
        require([case.get("id") for case in batch] == expected_ids, "lote mistura ou reordena partições")
        for case in batch:
            require(isinstance(case, dict) and set(case) == {"id", "text"}, "projeção contaminada")
            require(all(isinstance(value, str) and value.strip() for value in case.values()), "projeção inválida")
            projected_ids.append(case["id"])
    require(set(projected_ids) == EXPECTED_IDS and len(projected_ids) == 48, "IDs divergentes na projeção")


def training_projection(sample):
    """Projeção compacta e auditável usada somente para o treino dev congelado."""
    validate_sample(sample)
    return [
        {"id": case["id"], "text": case["text"], "gold": case["gold"]}
        for case in sorted(sample["cases"], key=lambda case: case["id"])
        if case["split"] == "dev"
    ]


def training_projection_sha256(sample):
    projection = training_projection(sample)
    compact = json.dumps(projection, ensure_ascii=False, separators=(",", ":"))
    return _sha256_text(compact)


def _tokens(text):
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(character for character in normalized if not unicodedata.combining(character))
    return set(re.findall(r"[a-z0-9]+", without_accents.casefold()))


def validate_rule(rule):
    require(isinstance(rule, dict), "regra inválida")
    require(rule.get("state") == "frozen_local_diagnostic_not_campaign", "estado da regra inválido")
    require(rule.get("trained_partition") == "dev" and rule.get("trained_cases") == 24, "treino da regra inválido")
    require(rule.get("used_reserved_for_fitting") is False, "reserved usado no fit")
    require(rule.get("algorithm") == "presence_top5_log_odds_v1", "algoritmo da regra inválido")
    require(rule.get("training_sha256") == TRAINING_SHA256, "projeção de treino divergente")
    require(rule.get("classes") == list(CLASSES), "classes da regra divergentes")
    rules = rule.get("rules")
    require(isinstance(rules, list) and len(rules) == len(CLASSES), "regras por classe divergentes")
    require([entry.get("class") for entry in rules] == list(CLASSES), "ordem das regras divergente")
    for entry in rules:
        features = entry.get("features")
        require(isinstance(features, list) and len(features) == 5, "regra deve ter top5 por classe")
        for feature in features:
            require(set(feature) == {"word", "positive", "negative", "weight"}, "feature inválida")
            require(isinstance(feature["word"], str) and re.fullmatch(r"[a-z0-9]+", feature["word"]) is not None, "palavra inválida")
            require(all(isinstance(feature[key], (int, float)) and not isinstance(feature[key], bool) for key in ("positive", "negative", "weight")), "peso inválido")


def predict(text, rule):
    """Aplica a regra já congelada; não reestima pesos nem consulta serviço externo."""
    validate_rule(rule)
    present = _tokens(text)
    scores = {}
    for entry in rule["rules"]:
        scores[entry["class"]] = sum(feature["weight"] for feature in entry["features"] if feature["word"] in present)
    return min(CLASSES, key=lambda label: (-scores[label], label))


def lexical_scores(sample, rule):
    """Pontua a regra fixa para auditoria local, sem alegar validação cega."""
    validate_sample(sample)
    validate_rule(rule)
    scores = {}
    predictions = []
    for split in ("dev", "reserved"):
        cases = sorted((case for case in sample["cases"] if case["split"] == split), key=lambda case: case["id"])
        predicted = [(case, predict(case["text"], rule)) for case in cases]
        scores[split] = (len(cases), sum(case["gold"] == label for case, label in predicted))
        predictions.extend({"id": case["id"], "split": split, "gold": case["gold"], "prediction": label} for case, label in predicted)
    return scores, predictions


def run_local_bench(root=ROOT):
    """Executa somente verificações determinísticas da bancada local T-098."""
    sample, rule, result = verify_frozen_inputs(root)
    validate_sample(sample)
    require(training_projection_sha256(sample) == TRAINING_SHA256, "hash da projeção de treino divergente")
    batches = classifier_batches(sample)
    scores, predictions = lexical_scores(sample, rule)
    require(scores == EXPECTED_SCORE, "pontuação lexical congelada divergente")
    recorded = {row["split"]: (row["n"], row["correct"]) for row in result.get("scores", [])}
    require(recorded == EXPECTED_SCORE, "resultado registrado divergente")
    recorded_predictions = {row["id"]: row["prediction"] for row in result.get("predictions", [])}
    require(
        recorded_predictions == {row["id"]: row["prediction"] for row in predictions},
        "predições registradas divergentes",
    )
    return {"hashes": artifact_hashes(root), "scores": scores, "batches": batches}
