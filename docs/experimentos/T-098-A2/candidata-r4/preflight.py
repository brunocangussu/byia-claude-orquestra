"""Preflight local da bancada T-098; não faz rede, inferência ou escrita."""

from collections import Counter, defaultdict
import re

CLASSES = {"alto_risco", "abster", "consulta", "trivial", "pequeno", "normal"}
FIELDS = {"id", "text", "gold", "reason", "family", "split"}
# Manifesto por mecanismo, decidido antes da projeção; não segue o substantivo.
FAMILY_SPLIT = {
    "controle-identidade": "dev", "exposicao-de-registros": "dev",
    "cadeia-de-dependencias": "dev", "reducao-de-medidas": "dev",
    "documentacao-executavel": "dev", "geracao-de-sequencias": "dev",
    "roteamento-de-entrada": "dev", "coordenacao-de-tarefas": "dev",
    "renderizacao-fixa": "dev", "evolucao-de-schema": "reserved",
    "promocao-de-ambiente": "reserved", "retencao-de-historico": "reserved",
    "tratamento-de-arquivos": "reserved", "agrupamento-temporal": "reserved",
    "composicao-de-relatorios": "reserved", "diagnostico-de-processos": "reserved",
    "compatibilidade-de-protocolo": "reserved", "empacotamento-de-recursos": "reserved",
}
# Controles pontuais de cobertura; não são um oráculo semântico para os 48 casos.
CONTROLS = {
    "Y037": ("alto_risco", ("uma linha", "assinatura")),
    "Y012": ("alto_risco", ("só leitura", "identificadores pessoais")),
    "Y048": ("alto_risco", ("urgente", "escape")),
    "Y009": ("normal", ("instrucoes.md", "sequência ainda não existe")),
    "Y027": ("trivial", ("guia.md", "não altere regras")),
    "Y026": ("normal", ("implemente", "simulação")),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_sample(sample):
    """Estrutura/cobertura, não aprovação de gabarito ou independência semântica."""
    require(isinstance(sample, dict) and set(sample) == {"cases"}, "envelope inválido")
    cases = sample["cases"]
    require(isinstance(cases, list) and len(cases) == 48, "exige 48 casos")
    ids, texts, counts, families, by_id = set(), set(), Counter(), defaultdict(list), {}
    for case in cases:
        require(isinstance(case, dict) and set(case) == FIELDS, "campos fora da allowlist")
        require(all(isinstance(value, str) and value.strip() for value in case.values()), "campo vazio ou inválido")
        require(re.fullmatch(r"Y\d{3}", case["id"]) is not None, "ID inválido")
        require(case["id"] not in ids, "ID duplicado")
        ids.add(case["id"])
        require(case["gold"] in CLASSES, "classe inválida")
        require(FAMILY_SPLIT.get(case["family"]) == case["split"], "família desconhecida ou cruzada")
        normalized = " ".join(case["text"].casefold().split())
        require(normalized not in texts, "pedido literal repetido")
        texts.add(normalized)
        counts[(case["split"], case["gold"])] += 1
        families[case["family"]].append(case["gold"])
        by_id[case["id"]] = case
    require(ids == {f"Y{i:03d}" for i in range(1, 49)}, "conjunto de IDs divergente")
    require(counts == Counter({(s, g): 4 for s in ("dev", "reserved") for g in CLASSES}), "classes/partições desequilibradas")
    require(set(families) == set(FAMILY_SPLIT), "família ausente")
    require(all(len(v) in (2, 3) for v in families.values()), "tamanho de família divergente")
    spectra = {s: Counter(tuple(sorted(v)) for f, v in families.items() if FAMILY_SPLIT[f] == s)
               for s in ("dev", "reserved")}
    require(spectra["dev"] != spectra["reserved"], "distribuições de famílias totalmente espelhadas")
    for identifier, (gold, terms) in CONTROLS.items():
        case = by_id[identifier]
        require(case["gold"] == gold and all(t in case["text"].casefold() for t in terms), "controle contrastivo ausente")


def classifier_batches(sample):
    """Dry-run de quatro lotes; só id/text, sem congelamento ou transmissão."""
    validate_sample(sample)
    batches = []
    for split in ("dev", "reserved"):
        cases = sorted((c for c in sample["cases"] if c["split"] == split), key=lambda c: c["id"])
        projected = [{"id": c["id"], "text": c["text"]} for c in cases]
        batches.extend(projected[i:i + 12] for i in range(0, len(projected), 12))
    return batches
