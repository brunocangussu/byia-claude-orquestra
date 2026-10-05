"""Bancada local e determinística da candidata R6 do T-098.

Este módulo não importa cliente de modelo, SDK, HTTP ou rede. Ele protege a
estrutura local e a derivação lexical; não certifica o significado humano dos
golds e não calcula métrica nova da partição ``reserved``.
"""

from __future__ import annotations

from collections import Counter
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
V1_SAMPLE_SHA256 = "db8ff9a874315012a9799c7794a741bc39270e30303df506cc7210c3fdae55ed"
V3_REPLACEMENTS = {
    "Y004": "Quais verificações de expiração e assinatura o fluxo atual aplica antes de aceitar um token de acesso? Explique sem alterar arquivos.",
    "Y007": "Altere o roteamento desta tarefa entre as duas filas. As regras de prioridade estão em conflito e ainda não foi definido qual regra ou autoridade prevalece.",
    "Y016": "Quais opções de largura e formato o renderer atual aceita para produzir o comprovante? Não altere a composição nem gere um novo arquivo.",
    "Y023": "Qual conjunto de entradas e qual fórmula a métrica de tempo médio atual usa para chegar ao valor exibido? Não edite o cálculo.",
    "Y028": "Você pode ajustar o pacote para ficar certo antes da próxima janela? Ainda não foram definidos o artefato, a operação concreta e o destino.",
    "Y031": "Mude a sequência de lembretes. Ainda não foi informado se deve criar, cancelar ou reenviar mensagens, nem qual resultado é esperado.",
    "Y032": "Ajuste a compatibilidade da integração do parceiro. Sei apenas que ela mudou; ainda não há versão, campo afetado ou exemplo de mensagem.",
    "Y042": "Corrija as falhas intermitentes do processo. Ainda não há horário, mensagem de erro, entrada ou etapa identificada.",
    "Y043": "Trate o histórico antigo. O pedido ainda não define se deve consultar, arquivar, excluir ou restaurar, nem o período.",
    "Y044": "Você pode liberar a tarefa bloqueada? Ainda não foi informado quem pode autorizar, qual é o bloqueio e qual efeito deve ocorrer.",
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


def load_inputs(root=ROOT):
    root = Path(root)
    return (
        _read_json(root / SAMPLE_NAME),
        _read_json(root / MANIFEST_NAME),
        _read_json(root / RULE_NAME),
    )


def _case_map(manifest):
    return {case["id"]: case for case in manifest["adjudications"]}


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
        "corpus_lineage", "historical_r6_v1", "historical_r6_v2",
    }
    require(set(manifest) == required, "campos do manifesto divergentes")
    require(manifest["candidate"] == "T-098-A2-R6-v3-local", "candidata inválida")
    require(manifest["version"] == 3 and manifest["state"] == "local_exploratory_not_campaign", "estado do manifesto inválido")
    classes = manifest["classes"]
    require(isinstance(classes, list) and classes == sorted(classes) and len(classes) == 6, "classes inválidas")
    require(all(isinstance(item, str) and item for item in classes), "classe inválida")

    sample = manifest["sample"]
    require(isinstance(sample, dict) and set(sample) == {"path", "sha256", "text_sha256"}, "selo da amostra inválido")
    require(sample["path"] == SAMPLE_NAME and isinstance(sample["sha256"], str), "fonte da amostra inválida")
    require(isinstance(sample["text_sha256"], dict), "selos de texto inválidos")

    rule = manifest["rule"]
    require(isinstance(rule, dict), "política da regra inválida")
    require(rule["path"] == RULE_NAME and rule["algorithm"] == "presence_top5_log_odds_v2", "regra declarada inválida")
    require(rule["trained_split"] == "dev" and rule["used_reserved_for_fit"] is False, "origem de treino inválida")
    require(rule["top_k"] == 5 and rule["smoothing"] == 1 and rule["minimum_token_length"] == 2, "parâmetros lexicais inválidos")
    require(rule["evaluation"] == "nenhuma métrica R6 é calculada nesta candidata", "escopo de avaliação inválido")

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
    require(isinstance(historical, dict) and historical["state"] == "R5_NO_GO_AUDITED", "ligação histórica inválida")
    require(isinstance(historical["files"], dict) and len(historical["files"]) == 14, "selos R5 incompletos")
    lineage = manifest["corpus_lineage"]
    require(isinstance(lineage, dict) and set(lineage) == {"base", "base_sha256", "allowed_text_replacements"}, "linhagem de corpus inválida")
    require(lineage["base"] == "docs/experimentos/T-098-A2/candidata-r6-local/amostra.json", "base textual inválida")
    require(lineage["base_sha256"] == V1_SAMPLE_SHA256, "selo da base textual inválido")
    require(lineage["allowed_text_replacements"] == sorted(V3_REPLACEMENTS), "trocas textuais permitidas divergentes")
    for key, expected_count in (("historical_r6_v1", 9), ("historical_r6_v2", 10)):
        historical_r6 = manifest[key]
        require(isinstance(historical_r6, dict) and set(historical_r6) == {"files"}, f"baseline {key} inválido")
        require(isinstance(historical_r6["files"], dict) and len(historical_r6["files"]) == expected_count, f"selos {key} incompletos")
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


def fit_rule_from_rows(rows, classes, top_k=5, smoothing=1, minimum_token_length=2):
    """Deriva pesos só das linhas fornecidas, com presença e desempate ASCII."""
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
    features_by_class = []
    for gold in classes:
        positive_rows = [row for row in rows if row["gold"] == gold]
        positive_total = len(positive_rows)
        negative_total = total - positive_total
        all_words = sorted({word for row in rows for word in _tokens(row["text"], minimum_token_length)})
        features = []
        for word in all_words:
            positive = sum(word in _tokens(row["text"], minimum_token_length) for row in positive_rows)
            negative = sum(word in _tokens(row["text"], minimum_token_length) for row in rows if row["gold"] != gold)
            weight = math.log((positive + smoothing) / (positive_total + 2 * smoothing)) - math.log((negative + smoothing) / (negative_total + 2 * smoothing))
            features.append({"word": word, "positive": positive, "negative": negative, "weight": weight})
        features_by_class.append({"class": gold, "features": sorted(features, key=lambda item: (-item["weight"], item["word"]))[:top_k]})
    return {
        "algorithm": "presence_top5_log_odds_v2",
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
            require(isinstance(feature, dict) and set(feature) == {"word", "positive", "negative", "weight"}, "feature inválida")
            require(isinstance(feature["word"], str) and re.fullmatch(r"[a-z0-9]{2,}", feature["word"]) is not None, "token inválido")
            require(feature["word"] not in words, "token duplicado")
            words.add(feature["word"])
            require(all(isinstance(feature[key], int) and not isinstance(feature[key], bool) for key in ("positive", "negative")), "contagem não inteira")
            require(0 <= feature["positive"] <= 4 and 0 <= feature["negative"] <= 20, "contagem fora do intervalo")
            require(isinstance(feature["weight"], (int, float)) and not isinstance(feature["weight"], bool) and math.isfinite(feature["weight"]), "peso não finito")
            key = (-feature["weight"], feature["word"])
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
    """Compara a v3 com a v1 antes de qualquer selo da própria candidata."""
    root = Path(root)
    lineage = manifest["corpus_lineage"]
    base_path = _project_root(root) / lineage["base"]
    require(base_path.is_file(), "base textual ausente")
    require(_sha256_file(base_path) == V1_SAMPLE_SHA256, "base textual histórica divergente")
    base = _raw_text_map(_read_json(base_path), "base textual")
    candidate = _raw_text_map(sample, "corpus v3")
    require(lineage["allowed_text_replacements"] == sorted(V3_REPLACEMENTS), "lista de trocas da linhagem divergente")
    for identifier, base_text in base.items():
        expected = V3_REPLACEMENTS.get(identifier, base_text)
        require(candidate[identifier] == expected, f"texto do corpus divergente: {identifier}")
    return candidate


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
    totals, questions = format_profile(cases, manifest)
    require(totals.get("abster") == 8, "contagem de abster divergente")
    require(questions.get("abster", 0) < totals["abster"], "formato exclusivo de abster")
    require(sum(count for gold, count in questions.items() if gold != "abster") > 0, "formato exclusivo de abster")
    require(questions.get("consulta", 0) > 0, "consulta delimitada sem pergunta na amostra")
    return totals, questions


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
    historical = manifest["historical_r5"]["files"]
    project_root = _project_root(root)
    for relative_path, digest in historical.items():
        path = project_root / relative_path
        require(path.is_file(), f"fonte histórica ausente: {relative_path}")
        require(_sha256_file(path) == digest, f"fonte histórica divergente: {relative_path}")
    return dict(historical)


def verify_historical_baseline(root, manifest, key, expected_count):
    root = Path(root)
    files = manifest[key]["files"]
    require(len(files) == expected_count, f"quantidade de fontes {key} divergente")
    project_root = _project_root(root)
    for relative_path, digest in files.items():
        path = project_root / relative_path
        require(path.is_file(), f"baseline ausente: {relative_path}")
        require(_sha256_file(path) == digest, f"baseline divergente: {relative_path}")
    return dict(files)


def run_local_preflight(root=ROOT):
    """Verifica somente artefatos locais R6; não produz score."""
    sample, manifest, rule = load_inputs(root)
    validate_manifest(manifest)
    validate_corpus_lineage(root, sample, manifest)
    validate_sample(sample, manifest)
    validate_fixture_scenarios(sample, manifest)
    validate_consulta_abster_boundary(manifest)
    totals, questions = validate_format_diversity(sample["cases"], manifest)
    batches = classifier_batches(sample, manifest)
    validate_projection(batches, sample, manifest)
    validate_rule(rule, sample, manifest)
    verify_frozen_snapshot(root, sample, manifest, rule)
    historical = verify_historical_r5(root)
    historical_v1 = verify_historical_baseline(root, manifest, "historical_r6_v1", 9)
    historical_v2 = verify_historical_baseline(root, manifest, "historical_r6_v2", 10)
    return {
        "candidate": manifest["candidate"],
        "batches": batches,
        "historical_r5": historical,
        "historical_r6_v1": historical_v1,
        "historical_r6_v2": historical_v2,
        "questions": questions,
        "totals": totals,
        "rule_sha256": manifest["rule"]["sha256"],
        "scores": "not_evaluated",
    }
