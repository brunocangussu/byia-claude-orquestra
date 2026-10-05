"""Bancada local e determinística da candidata R6 do T-098.

Este módulo não importa cliente de modelo, SDK, HTTP ou rede. Ele protege a
estrutura local e a derivação lexical; não certifica o significado humano dos
golds e não calcula métrica nova da partição ``reserved``.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parent
SAMPLE_NAME = "amostra.json"
MANIFEST_NAME = "manifesto.json"
RULE_NAME = "regra-lexical-dev.json"
CASE_FIELDS = {"id", "text"}
ADJUDICATION_FIELDS = {"id", "split", "gold", "family", "policy_code", "facts", "rationale"}
SPLITS = ("dev", "reserved")
CLASSES = ("abster", "alto_risco", "consulta", "normal", "pequeno", "trivial")
V5_ALLOWLIST = ("Y004", "Y007", "Y016", "Y023", "Y028", "Y031", "Y032", "Y042", "Y043", "Y044", "Y045")
V5_REPLACEMENTS = {
    "Y007": "Altere o roteamento desta tarefa entre as duas filas. As regras de prioridade estão em conflito e ainda não foi definido qual regra ou autoridade prevalece.",
    "Y031": "Mude a sequência de lembretes. Ainda não foi informado se deve criar, cancelar ou reenviar mensagens, nem qual resultado é esperado.",
    "Y042": "Corrija as falhas intermitentes do processo. Ainda não há horário, mensagem de erro, entrada ou etapa identificada.",
    "Y045": "Resolva o acesso aos registros do parceiro. Ainda não foi definido se isso significa consultar, mudar permissões ou exportar, nem quais dados seriam envolvidos.",
}
PROTECTED_FIXTURES = {
    "Y009": "Crie, na interface fictícia de revisão, uma etapa de prévia que liste as alterações, permita navegar entre elas e apresente um resumo antes do botão de confirmação.",
    "Y011": "Edite `assets/roteador-legenda.svg`, a fonte usada para gerar `assets/roteador-legenda.png`, retirando o ponto final das três etiquetas marcadas. Não toque no código do roteador.",
    "Y041": "Acrescente regressões para a média existente: `[2,4]` deve resultar em `3` e `[]` deve resultar em `null`. Corrija apenas o denominador se a implementação contrariar essas saídas.",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path):
    return _sha256_bytes(path.read_bytes())


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _project_root(root):
    return root.resolve().parents[3]


def _project_file(root, relative_path, message):
    """Resolve um arquivo histórico somente dentro da raiz conhecida do projeto."""
    require(isinstance(relative_path, str) and relative_path, message)
    relative = Path(relative_path)
    require(not relative.is_absolute() and ".." not in relative.parts, message)
    project_root = _project_root(Path(root)).resolve()
    path = project_root / relative
    require(path.is_file() and not path.is_symlink(), message)
    try:
        path.resolve().relative_to(project_root)
    except ValueError:
        require(False, message)
    return path


def load_inputs(root=ROOT):
    root = Path(root)
    return (
        _read_json(root / SAMPLE_NAME),
        _read_json(root / MANIFEST_NAME),
        _read_json(root / RULE_NAME),
    )


def _case_map(manifest):
    return {case["id"]: case for case in manifest["adjudications"]}


def _is_sha256(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_adjudications(manifest):
    """Aplica a política declarada; não substitui revisão semântica humana."""
    policy_codes = manifest["policy_codes"]
    for case in manifest["adjudications"]:
        code = case["policy_code"]
        require(code in policy_codes, f"policy code desconhecido: {case['id']}")
        policy = policy_codes[code]
        require(case["gold"] == policy["gold"], f"adjudicação {case['id']} diverge da política")
        require(set(policy["required_facts"]).issubset(set(case["facts"])), f"fatos da adjudicação insuficientes: {case['id']}")
        if case["gold"] == "abster":
            require("question_required" in case["facts"], f"abstenção sem pergunta: {case['id']}")
            require("missing_decisive_scope" in case["facts"], f"abstenção sem lacuna decisiva: {case['id']}")


def validate_manifest(manifest):
    require(isinstance(manifest, dict), "manifesto não é objeto")
    required = {
        "candidate", "version", "state", "scope", "classes", "sample", "rule", "batches",
        "policy_codes", "taxonomy", "adjudications", "historical_r5",
        "corpus_lineage", "historical_r6_v1", "historical_r6_v2", "historical_r6_v3", "historical_r6_v4",
    }
    require(set(manifest) == required, "campos do manifesto divergentes")
    require(manifest["candidate"] == "T-098-A2-R7-v5-local", "candidata inválida")
    require(manifest["version"] == 5 and manifest["state"] == "local_exploratory_not_campaign", "estado do manifesto inválido")
    classes = manifest["classes"]
    require(isinstance(classes, list) and classes == list(CLASSES), "classes literais inválidas")

    sample = manifest["sample"]
    require(isinstance(sample, dict) and set(sample) == {"path", "sha256", "text_sha256"}, "selo da amostra inválido")
    require(sample["path"] == SAMPLE_NAME and _is_sha256(sample["sha256"]), "fonte da amostra inválida")
    require(isinstance(sample["text_sha256"], dict) and len(sample["text_sha256"]) == 48, "selos de texto inválidos")
    require(all(isinstance(identifier, str) and _is_sha256(digest) for identifier, digest in sample["text_sha256"].items()), "digest de texto inválido")

    rule = manifest["rule"]
    expected_rule_fields = {"path", "sha256", "algorithm", "trained_split", "used_reserved_for_fit", "top_k", "smoothing", "minimum_token_length", "tie_break", "evaluation", "weight_serialization"}
    require(isinstance(rule, dict) and set(rule) == expected_rule_fields, "schema da política da regra inválido")
    require(rule["path"] == RULE_NAME and _is_sha256(rule["sha256"]), "selo da regra inválido")
    require(rule["algorithm"] == "presence_top5_log_odds_v3_exact_ratio", "algoritmo da regra inválido")
    require(rule["trained_split"] == "dev" and rule["used_reserved_for_fit"] is False, "origem de treino inválida")
    require(rule["top_k"] == 5 and rule["smoothing"] == 1 and rule["minimum_token_length"] == 2, "parâmetros lexicais inválidos")
    require(rule["tie_break"] == "razão exata descendente, token ASCII ascendente; classe ASCII ascendente para predição", "desempate declarado inválido")
    require(rule["weight_serialization"] == "ln(numerador/denominador) com razão reduzida em weight_ratio", "serialização de peso inválida")
    require(rule["evaluation"] == "nenhuma métrica R7 é calculada nesta candidata", "escopo de avaliação inválido")

    records = manifest["adjudications"]
    require(isinstance(records, list) and len(records) == 48, "adjudicações devem ter 48 casos")
    identifiers = set()
    counts = Counter()
    for case in records:
        require(isinstance(case, dict) and set(case) == ADJUDICATION_FIELDS, "adjudicação inválida")
        require(isinstance(case["id"], str) and re.fullmatch(r"Y\d{3}", case["id"]) is not None, "id de adjudicação inválido")
        require(case["id"] not in identifiers, "id de adjudicação duplicado")
        identifiers.add(case["id"])
        require(case["split"] in SPLITS and case["gold"] in classes, "split ou gold inválido")
        require(isinstance(case["family"], str) and case["family"], "família inválida")
        require(isinstance(case["policy_code"], str) and case["policy_code"], "policy code inválido")
        require(isinstance(case["facts"], list) and case["facts"] and all(isinstance(fact, str) and fact for fact in case["facts"]), "fatos inválidos")
        require(isinstance(case["rationale"], str) and case["rationale"].strip(), "rationale inválida")
        counts[(case["split"], case["gold"])] += 1
    require(counts == Counter({(split, gold): 4 for split in SPLITS for gold in classes}), "classes e splits desequilibrados")

    policies = manifest["policy_codes"]
    require(isinstance(policies, dict) and policies, "políticas ausentes")
    for name, policy in policies.items():
        require(isinstance(name, str) and isinstance(policy, dict) and set(policy) == {"gold", "required_facts"}, "política inválida")
        require(policy["gold"] in classes, "gold de política inválido")
        require(isinstance(policy["required_facts"], list) and policy["required_facts"], "fatos requeridos inválidos")
    validate_adjudications(manifest)

    taxonomy = manifest["taxonomy"]
    require(isinstance(taxonomy, dict) and taxonomy, "taxonomia ausente")
    taxonomic_ids = []
    for family, ids in taxonomy.items():
        require(isinstance(family, str) and family and isinstance(ids, list) and ids, "família taxonômica inválida")
        require(all(isinstance(identifier, str) for identifier in ids), "id taxonômico inválido")
        taxonomic_ids.extend(ids)
    require(len(taxonomic_ids) == len(set(taxonomic_ids)) and set(taxonomic_ids) == identifiers, "taxonomia não cobre os IDs")
    for case in records:
        require(case["family"] in taxonomy, f"família não reconhecida: {case['id']}")
        require(case["id"] in taxonomy[case["family"]], f"família divergente: {case['id']}")

    batches = manifest["batches"]
    require(isinstance(batches, dict) and set(batches) == set(SPLITS), "lotes inválidos")
    batch_ids = []
    by_id = _case_map(manifest)
    for split in SPLITS:
        split_batches = batches[split]
        require(isinstance(split_batches, list) and len(split_batches) == 2, "split deve ter dois lotes")
        for batch in split_batches:
            require(isinstance(batch, list) and len(batch) == 12 and all(isinstance(identifier, str) for identifier in batch), "lote inválido")
            for identifier in batch:
                require(identifier in by_id and by_id[identifier]["split"] == split, f"split incompatível com lote: {identifier}")
            batch_ids.extend(batch)
    require(len(batch_ids) == len(set(batch_ids)) and set(batch_ids) == identifiers, "identidade dos lotes divergente")

    historical = manifest["historical_r5"]
    require(isinstance(historical, dict) and set(historical) == {"state", "inventory", "inventory_sha256", "files"}, "schema histórico R5 inválido")
    require(historical["state"] == "R5_NO_GO_AUDITED", "estado histórico R5 inválido")
    require(historical["inventory"] == "docs/reviews/T-098-r5-gold-preparacao-local/inventario.json" and _is_sha256(historical["inventory_sha256"]), "inventário R5 inválido")
    require(isinstance(historical["files"], dict) and len(historical["files"]) == 14, "selos R5 incompletos")
    require(all(isinstance(path, str) and _is_sha256(digest) for path, digest in historical["files"].items()), "selos R5 inválidos")
    lineage = manifest["corpus_lineage"]
    require(isinstance(lineage, dict) and set(lineage) == {"base", "base_sha256", "allowlist_ids", "changed_text_ids"}, "linhagem de corpus inválida")
    require(lineage["base"] == "docs/experimentos/T-098-A2/candidata-r6-v4-local/amostra.json" and _is_sha256(lineage["base_sha256"]), "base textual inválida")
    require(lineage["allowlist_ids"] == list(V5_ALLOWLIST), "allowlist textual divergente")
    require(lineage["changed_text_ids"] == sorted(V5_REPLACEMENTS), "trocas textuais efetivas divergentes")
    for key, expected_count in (("historical_r6_v1", 9), ("historical_r6_v2", 10), ("historical_r6_v3", 10), ("historical_r6_v4", 10)):
        historical_r6 = manifest[key]
        require(isinstance(historical_r6, dict) and set(historical_r6) == {"files"}, f"baseline {key} inválido")
        require(isinstance(historical_r6["files"], dict) and len(historical_r6["files"]) == expected_count, f"selos {key} incompletos")
        require(all(isinstance(path, str) and _is_sha256(digest) for path, digest in historical_r6["files"].items()), f"selos {key} inválidos")
    return by_id


def validate_sample(sample, manifest):
    by_id = validate_manifest(manifest)
    require(isinstance(sample, dict) and set(sample) == {"cases"}, "amostra inválida")
    cases = sample["cases"]
    require(isinstance(cases, list) and len(cases) == 48, "amostra deve ter 48 casos")
    source = {}
    for case in cases:
        require(isinstance(case, dict) and set(case) == CASE_FIELDS, "campos da amostra inválidos")
        require(isinstance(case["id"], str) and case["id"] in by_id, "id da amostra inválido")
        require(case["id"] not in source, "id da amostra duplicado")
        require(isinstance(case["text"], str) and case["text"].strip(), "texto da amostra inválido")
        source[case["id"]] = case
    require(set(source) == set(by_id), "IDs da amostra divergentes")
    text_hashes = manifest["sample"]["text_sha256"]
    require(set(text_hashes) == set(source), "selos por texto divergentes")
    for identifier, case in source.items():
        require(_sha256_bytes(case["text"].encode("utf-8")) == text_hashes[identifier], f"texto da amostra diverge do manifesto: {identifier}")
    return source


def classifier_batches(sample, manifest):
    source = validate_sample(sample, manifest)
    return [
        [{"id": identifier, "text": source[identifier]["text"]} for identifier in batch]
        for split in SPLITS
        for batch in manifest["batches"][split]
    ]


def validate_projection(batches, sample, manifest):
    """Exige identidade, ordem, split e bytes exatos antes de qualquer uso."""
    source = validate_sample(sample, manifest)
    require(isinstance(batches, list) and len(batches) == 4, "projeção exige quatro lotes")
    expected_groups = [batch for split in SPLITS for batch in manifest["batches"][split]]
    projected_ids = []
    for batch, expected_ids in zip(batches, expected_groups):
        require(isinstance(batch, list) and len(batch) == 12, "lote de projeção inválido")
        batch_ids = []
        for case in batch:
            require(isinstance(case, dict), "item de projeção não é objeto")
            require(set(case) == CASE_FIELDS, "campos da projeção inválidos")
            require(isinstance(case["id"], str), "id da projeção inválido")
            require(isinstance(case["text"], str) and case["text"].strip(), "texto da projeção inválido")
            require(case["id"] in source, "id fora da projeção")
            require(case["text"].encode("utf-8") == source[case["id"]]["text"].encode("utf-8"), f"projeção texto divergente: {case['id']}")
            batch_ids.append(case["id"])
            projected_ids.append(case["id"])
        require(batch_ids == expected_ids, "ordem ou identidade da projeção divergente")
    require(len(projected_ids) == len(set(projected_ids)) and set(projected_ids) == set(source), "cobertura da projeção divergente")


def _tokens(text, minimum_length=2):
    normalized = unicodedata.normalize("NFKD", text).casefold()
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return set(re.findall(rf"[a-z0-9]{{{minimum_length},}}", ascii_text))


def training_projection(sample, manifest):
    source = validate_sample(sample, manifest)
    by_id = _case_map(manifest)
    return [
        {"id": identifier, "text": source[identifier]["text"], "gold": by_id[identifier]["gold"]}
        for identifier in sorted(source)
        if by_id[identifier]["split"] == "dev"
    ]


def _reduced_weight_ratio(positive, negative, positive_total, negative_total, smoothing):
    """Representa log-odds como razão exata antes de qualquer ordenação."""
    numerator = (positive + smoothing) * (negative_total + 2 * smoothing)
    denominator = (negative + smoothing) * (positive_total + 2 * smoothing)
    divisor = math.gcd(numerator, denominator)
    return {"numerator": numerator // divisor, "denominator": denominator // divisor}


def _serialized_weight(ratio):
    return f"ln({ratio['numerator']}/{ratio['denominator']})"


def _feature_sort_key(feature):
    ratio = feature["weight_ratio"]
    return (-Fraction(ratio["numerator"], ratio["denominator"]), feature["word"])


def fit_rule_from_rows(rows, classes, top_k=5, smoothing=1, minimum_token_length=2):
    """Deriva pesos só das linhas fornecidas, com razão exata e desempate ASCII."""
    require(isinstance(rows, list) and rows, "linhas de treino inválidas")
    require(isinstance(classes, list) and classes == sorted(classes), "classes de treino inválidas")
    require(isinstance(top_k, int) and top_k > 0 and isinstance(smoothing, int) and smoothing > 0, "parâmetros de treino inválidos")
    require(isinstance(minimum_token_length, int) and minimum_token_length >= 2, "tamanho mínimo inválido")
    expected_fields = {"id", "text", "gold"}
    for row in rows:
        require(isinstance(row, dict) and set(row) == expected_fields, "linha de treino inválida")
        require(isinstance(row["id"], str) and isinstance(row["text"], str) and row["text"].strip(), "valor de treino inválido")
        require(row["gold"] in classes, "gold de treino inválido")
    total = len(rows)
    all_words = sorted({word for row in rows for word in _tokens(row["text"], minimum_token_length)})
    features_by_class = []
    for gold in classes:
        positive_rows = [row for row in rows if row["gold"] == gold]
        positive_total = len(positive_rows)
        negative_total = total - positive_total
        features = []
        for word in all_words:
            positive = sum(word in _tokens(row["text"], minimum_token_length) for row in positive_rows)
            negative = sum(word in _tokens(row["text"], minimum_token_length) for row in rows if row["gold"] != gold)
            ratio = _reduced_weight_ratio(positive, negative, positive_total, negative_total, smoothing)
            features.append({
                "word": word,
                "positive": positive,
                "negative": negative,
                "weight_ratio": ratio,
                "weight": _serialized_weight(ratio),
            })
        features_by_class.append({"class": gold, "features": sorted(features, key=_feature_sort_key)[:top_k]})
    return {
        "algorithm": "presence_top5_log_odds_v3_exact_ratio",
        "trained_split": "dev",
        "trained_cases": total,
        "used_reserved_for_fit": False,
        "classes": classes,
        "parameters": {"top_k": top_k, "smoothing": smoothing, "minimum_token_length": minimum_token_length},
        "rules": features_by_class,
    }


def fit_rule(sample, manifest):
    validate_manifest(manifest)
    policy = manifest["rule"]
    return fit_rule_from_rows(
        training_projection(sample, manifest),
        manifest["classes"],
        top_k=policy["top_k"],
        smoothing=policy["smoothing"],
        minimum_token_length=policy["minimum_token_length"],
    )


def validate_rule_schema(rule, manifest):
    require(isinstance(rule, dict), "regra não é objeto")
    expected_fields = {"algorithm", "trained_split", "trained_cases", "used_reserved_for_fit", "classes", "parameters", "rules"}
    require(set(rule) == expected_fields, "schema da regra divergente")
    policy = manifest["rule"]
    require(rule["algorithm"] == policy["algorithm"] and rule["trained_split"] == "dev", "origem declarada da regra inválida")
    require(rule["trained_cases"] == 24 and rule["used_reserved_for_fit"] is False, "contagem declarada da regra inválida")
    require(rule["classes"] == manifest["classes"], "classes da regra divergentes")
    require(rule["parameters"] == {"top_k": 5, "smoothing": 1, "minimum_token_length": 2}, "parâmetros da regra divergentes")
    rules = rule["rules"]
    require(isinstance(rules, list) and len(rules) == len(manifest["classes"]), "regras por classe inválidas")
    require([entry["class"] if isinstance(entry, dict) and "class" in entry else None for entry in rules] == manifest["classes"], "ordem das regras inválida")
    for entry in rules:
        require(isinstance(entry, dict) and set(entry) == {"class", "features"}, "entrada de regra inválida")
        features = entry["features"]
        require(isinstance(features, list) and len(features) == 5, "top cinco inválido")
        previous = None
        words = set()
        for feature in features:
            require(isinstance(feature, dict) and set(feature) == {"word", "positive", "negative", "weight_ratio", "weight"}, "feature inválida")
            require(isinstance(feature["word"], str) and re.fullmatch(r"[a-z0-9]{2,}", feature["word"]) is not None, "token inválido")
            require(feature["word"] not in words, "token duplicado")
            words.add(feature["word"])
            require(all(isinstance(feature[key], int) and not isinstance(feature[key], bool) for key in ("positive", "negative")), "contagem não inteira")
            require(0 <= feature["positive"] <= 4 and 0 <= feature["negative"] <= 20, "contagem fora do intervalo")
            ratio = feature["weight_ratio"]
            require(isinstance(ratio, dict) and set(ratio) == {"numerator", "denominator"}, "razão do peso inválida")
            require(all(isinstance(ratio[key], int) and not isinstance(ratio[key], bool) and ratio[key] > 0 for key in ratio), "razão do peso inválida")
            require(math.gcd(ratio["numerator"], ratio["denominator"]) == 1, "razão do peso não reduzida")
            require(isinstance(feature["weight"], str) and feature["weight"] == _serialized_weight(ratio), "peso serializado inválido")
            key = _feature_sort_key(feature)
            require(previous is None or previous <= key, "ordem de desempate inválida")
            previous = key


def validate_rule(rule, sample, manifest):
    validate_rule_schema(rule, manifest)
    expected = fit_rule(sample, manifest)
    require(_canonical_json_bytes(rule) == _canonical_json_bytes(expected), "derivação da regra divergente")


def _raw_text_map(sample, source_name):
    require(isinstance(sample, dict) and set(sample) == {"cases"}, f"{source_name} inválida")
    cases = sample["cases"]
    require(isinstance(cases, list) and len(cases) == 48, f"{source_name} deve ter 48 casos")
    mapped = {}
    for case in cases:
        require(isinstance(case, dict), f"caso de {source_name} não é objeto")
        require(set(case) == CASE_FIELDS, f"campos de {source_name} divergentes")
        require(isinstance(case["id"], str) and isinstance(case["text"], str), f"tipos de {source_name} inválidos")
        require(case["id"] not in mapped and case["text"].strip(), f"caso de {source_name} inválido")
        mapped[case["id"]] = case["text"]
    require(set(mapped) == {f"Y{index:03d}" for index in range(1, 49)}, f"IDs de {source_name} divergentes")
    return mapped


def validate_corpus_lineage(root, sample, manifest):
    """Compara a v5 à v4 e protege os 37 textos que precisam igualar a v1."""
    root = Path(root)
    lineage = manifest["corpus_lineage"]
    base_path = _project_file(root, lineage["base"], "base textual ausente")
    require(_sha256_file(base_path) == lineage["base_sha256"], "base textual histórica divergente")
    base = _raw_text_map(_read_json(base_path), "base textual")
    candidate = _raw_text_map(sample, "corpus v5")
    require(lineage["allowlist_ids"] == list(V5_ALLOWLIST), "allowlist textual divergente")
    require(lineage["changed_text_ids"] == sorted(V5_REPLACEMENTS), "lista de trocas da linhagem divergente")
    for identifier, base_text in base.items():
        expected = V5_REPLACEMENTS.get(identifier, base_text)
        require(candidate[identifier] == expected, f"texto do corpus divergente: {identifier}")

    v1_files = manifest["historical_r6_v1"]["files"]
    v1_paths = [path for path in v1_files if path.endswith("/amostra.json")]
    require(len(v1_paths) == 1, "amostra v1 histórica ambígua")
    v1_path = _project_file(root, v1_paths[0], "amostra v1 histórica ausente")
    require(_sha256_file(v1_path) == v1_files[v1_paths[0]], "amostra v1 histórica divergente")
    v1 = _raw_text_map(_read_json(v1_path), "corpus v1")
    for identifier, original_text in v1.items():
        if identifier not in V5_ALLOWLIST:
            require(candidate[identifier] == original_text, f"texto v1 protegido divergente: {identifier}")
    return candidate


def validate_adjudication_baseline(root, manifest):
    """Exige gold, split e família idênticos à fonte R6 v1 já selada."""
    root = Path(root)
    v1_files = manifest["historical_r6_v1"]["files"]
    v1_paths = [path for path in v1_files if path.endswith("/manifesto.json")]
    require(len(v1_paths) == 1, "manifesto v1 histórico ambíguo")
    v1_path = _project_file(root, v1_paths[0], "manifesto v1 histórico ausente")
    require(_sha256_file(v1_path) == v1_files[v1_paths[0]], "manifesto v1 histórico divergente")
    baseline = _read_json(v1_path)
    records = baseline.get("adjudications") if isinstance(baseline, dict) else None
    require(isinstance(records, list) and len(records) == 48, "adjudicações v1 inválidas")
    expected = {}
    for case in records:
        require(isinstance(case, dict), "adjudicação v1 inválida")
        identifier = case.get("id")
        require(isinstance(identifier, str) and identifier not in expected, "adjudicação v1 inválida")
        values = (case.get("gold"), case.get("split"), case.get("family"))
        require(all(isinstance(value, str) and value for value in values), "adjudicação v1 inválida")
        expected[identifier] = values
    current = {
        case["id"]: (case["gold"], case["split"], case["family"])
        for case in manifest["adjudications"]
    }
    require(set(current) == set(expected), "IDs de adjudicação v1 divergentes")
    for identifier in sorted(expected):
        require(current[identifier] == expected[identifier], f"metadados v1 divergentes: {identifier}")
    return current


def format_profile(cases, manifest):
    labels = _case_map(manifest)
    require(isinstance(cases, list), "casos de formato inválidos")
    totals, questions = Counter(), Counter()
    for case in cases:
        require(isinstance(case, dict), "caso de formato não é objeto")
        require(set(case) == CASE_FIELDS, "campos de formato divergentes")
        identifier, text = case["id"], case["text"]
        require(isinstance(identifier, str) and isinstance(text, str), "tipos de formato inválidos")
        require(identifier in labels, "ID de formato ausente")
        gold = labels[identifier]["gold"]
        totals[gold] += 1
        questions[gold] += int("?" in text)
    return dict(totals), dict(questions)


def validate_format_diversity(cases, manifest):
    """Diagnóstico do corpus; não classifica nem altera gold por pontuação."""
    totals, questions = format_profile(cases, manifest)
    require(totals.get("abster") == 8, "contagem de abster divergente")
    require(questions.get("abster", 0) < totals["abster"], "formato exclusivo de abster")
    require(sum(count for gold, count in questions.items() if gold != "abster") > 0, "formato exclusivo de abster")
    return totals, questions


def lexical_shortcut_profile(cases, manifest):
    """Mede o atalho confirmado sem usá-lo como regra de classificação."""
    labels = _case_map(manifest)
    phrase = Counter()
    token_totals = Counter()
    token_by_class = Counter()
    for case in cases:
        identifier, text = case["id"], case["text"]
        gold = labels[identifier]["gold"]
        phrase[gold] += int("ainda não" in text.casefold())
        for token in set(_tokens(text, 2)):
            token_totals[token] += 1
            if gold == "abster":
                token_by_class[token] += 1
    phrase_abster = phrase["abster"]
    phrase_other = sum(value for gold, value in phrase.items() if gold != "abster")
    require(not (phrase_abster == 8 and phrase_other <= 1), "atalho lexical de frase exclusivo de abster")
    exclusive_tokens = sorted(
        token for token, abster_count in token_by_class.items()
        if abster_count == 8 and token_totals[token] - abster_count <= 1
    )
    require(not exclusive_tokens, f"token exclusivo de abster: {', '.join(exclusive_tokens)}")
    return {
        "phrase_ainda_nao": {"abster": phrase_abster, "other": phrase_other},
        "exclusive_tokens": exclusive_tokens,
    }


def validate_consulta_abster_boundary(manifest):
    """Valida fatos e comportamento de saída, sem usar a gramática do prompt."""
    for case in manifest["adjudications"]:
        facts = set(case["facts"])
        if case["gold"] == "consulta":
            require(case["policy_code"] == "consulta_delimitada", f"consulta com política divergente: {case['id']}")
            require({"information_only", "specified_scope"}.issubset(facts), f"consulta sem escopo delimitado: {case['id']}")
            require("missing_decisive_scope" not in facts, f"consulta marcada com escopo ausente: {case['id']}")
        if case["gold"] == "abster":
            require(case["policy_code"] == "esclarecimento_obrigatorio", f"abstenção com política divergente: {case['id']}")
            require({"question_required", "missing_decisive_scope"}.issubset(facts), f"abstenção sem comportamento de esclarecimento: {case['id']}")


def validate_fixture_scenarios(sample, manifest):
    texts = _raw_text_map(sample, "cenários protegidos")
    by_id = _case_map(manifest)
    required_facts = {
        "Y009": {"new_local_behavior", "specified_scope"},
        "Y011": {"presentation_only", "editable_raster_source"},
        "Y041": {"existing_behavior", "bounded_change", "complete_fixture"},
    }
    for identifier, expected_text in PROTECTED_FIXTURES.items():
        require(texts[identifier] == expected_text, f"cenário protegido divergente: {identifier}")
        require(required_facts[identifier].issubset(set(by_id[identifier]["facts"])), f"fatos do cenário divergentes: {identifier}")


def verify_frozen_snapshot(root, sample, manifest, rule):
    root = Path(root)
    require(_sha256_file(root / SAMPLE_NAME) == manifest["sample"]["sha256"], "snapshot da amostra divergente")
    require(_sha256_file(root / RULE_NAME) == manifest["rule"]["sha256"], "snapshot da regra divergente")
    require(_canonical_json_bytes(_read_json(root / SAMPLE_NAME)) == _canonical_json_bytes(sample), "amostra carregada divergente")
    require(_canonical_json_bytes(_read_json(root / RULE_NAME)) == _canonical_json_bytes(rule), "regra carregada divergente")


def verify_historical_r5(root=ROOT):
    root = Path(root)
    manifest = _read_json(root / MANIFEST_NAME)
    validate_manifest(manifest)
    historical_r5 = manifest["historical_r5"]
    inventory_path = _project_file(root, historical_r5["inventory"], "inventário R5 inválido")
    require(_sha256_file(inventory_path) == historical_r5["inventory_sha256"], "selo do inventário R5 divergente")
    inventory = _read_json(inventory_path)
    require(isinstance(inventory, dict) and inventory.get("card") == "T-098" and inventory.get("round") == "R5", "inventário R5 inválido")
    entries = inventory.get("files")
    require(isinstance(entries, list) and len(entries) == 14, "inventário R5 inválido")
    inventory_files = {}
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == {"path", "sha256", "bytes"}, "inventário R5 inválido")
        require(isinstance(entry["path"], str) and _is_sha256(entry["sha256"]), "inventário R5 inválido")
        require(isinstance(entry["bytes"], int) and not isinstance(entry["bytes"], bool) and entry["bytes"] >= 0, "inventário R5 inválido")
        require(entry["path"] not in inventory_files, "inventário R5 inválido")
        inventory_files[entry["path"]] = entry["sha256"]
    historical = historical_r5["files"]
    require(inventory_files == historical, "inventário R5 divergente")
    for relative_path, digest in historical.items():
        path = _project_file(root, relative_path, f"fonte histórica ausente: {relative_path}")
        require(_sha256_file(path) == digest, f"fonte histórica divergente: {relative_path}")
    return dict(historical)


def verify_historical_baseline(root, manifest, key, expected_count):
    root = Path(root)
    files = manifest[key]["files"]
    require(len(files) == expected_count, f"quantidade de fontes {key} divergente")
    for relative_path, digest in files.items():
        path = _project_file(root, relative_path, f"baseline ausente: {relative_path}")
        require(_sha256_file(path) == digest, f"baseline divergente: {relative_path}")
    return dict(files)


def run_local_preflight(root=ROOT):
    """Verifica somente artefatos locais R7; não produz score."""
    sample, manifest, rule = load_inputs(root)
    validate_manifest(manifest)
    validate_corpus_lineage(root, sample, manifest)
    adjudications_v1 = validate_adjudication_baseline(root, manifest)
    validate_sample(sample, manifest)
    validate_fixture_scenarios(sample, manifest)
    validate_consulta_abster_boundary(manifest)
    totals, questions = validate_format_diversity(sample["cases"], manifest)
    lexical_profile = lexical_shortcut_profile(sample["cases"], manifest)
    batches = classifier_batches(sample, manifest)
    validate_projection(batches, sample, manifest)
    validate_rule(rule, sample, manifest)
    verify_frozen_snapshot(root, sample, manifest, rule)
    historical = verify_historical_r5(root)
    historical_v1 = verify_historical_baseline(root, manifest, "historical_r6_v1", 9)
    historical_v2 = verify_historical_baseline(root, manifest, "historical_r6_v2", 10)
    historical_v3 = verify_historical_baseline(root, manifest, "historical_r6_v3", 10)
    historical_v4 = verify_historical_baseline(root, manifest, "historical_r6_v4", 10)
    return {
        "candidate": manifest["candidate"],
        "batches": batches,
        "historical_r5": historical,
        "historical_r6_v1": historical_v1,
        "historical_r6_v2": historical_v2,
        "historical_r6_v3": historical_v3,
        "historical_r6_v4": historical_v4,
        "adjudications_v1": adjudications_v1,
        "lexical_profile": lexical_profile,
        "questions": questions,
        "totals": totals,
        "rule_sha256": manifest["rule"]["sha256"],
        "scores": "not_evaluated",
    }


if __name__ == "__main__":
    result = run_local_preflight(ROOT)
    summary = {
        "candidate": result["candidate"],
        "historical_counts": {
            "r5": len(result["historical_r5"]),
            "r6_v1": len(result["historical_r6_v1"]),
            "r6_v2": len(result["historical_r6_v2"]),
            "r6_v3": len(result["historical_r6_v3"]),
            "r6_v4": len(result["historical_r6_v4"]),
        },
        "lexical_profile": result["lexical_profile"],
        "scores": result["scores"],
        "totals": result["totals"],
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
