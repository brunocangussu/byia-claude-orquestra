#!/usr/bin/env python3
"""Fábrica versionada T-149. Consulta e proposta puras: não adota nem invoca LLM."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

ROLES = ("planner·interface", "planner·sistema", "implementer·leve",
         "implementer·normal", "implementer·pesada", "reviewer", "docs", "scout")
HOSTS = ("codex", "claude")
MODELS = {"gpt-6.1-sol": "openai", "gpt-6-luna": "openai",
          "claude-opus-5-5": "anthropic", "claude-sonnet-5-5": "anthropic"}
EFFORTS = {"openai": {"low", "medium", "high", "xhigh"},
           "anthropic": {"low", "medium", "high"}}
MECHANISMS = {("codex", "openai"): {"codex-native", "codex-cli"},
              ("codex", "anthropic"): {"claude-cli"},
              ("claude", "openai"): {"codex-companion"},
              ("claude", "anthropic"): {"claude-subagent"}}
DISABLED_VIAS = {"codex": {"runner-opus": {"claude-cli"}},
                 "claude": {"codex": {"codex-companion"}}}
PROOF_FIELDS = ("role", "success", "model_id", "effort", "sent_model_id", "sent_effort",
                "observed_model_id", "observed_effort", "mechanism", "evidence_ref",
                "account", "client_version", "sandbox")


def validate_catalog(data: dict) -> None:
    """Schema fechado; erro não vira alias/fallback nem autorização de execução."""
    if not isinstance(data, dict) or set(data) != {"schema", "manager", "hosts"}:
        raise ValueError("ELENCO_SCHEMA: chaves do catálogo inválidas")
    if type(data["schema"]) is not int or data["schema"] != 1:
        raise ValueError("ELENCO_SCHEMA: schema não suportado")
    if data["manager"] != "sessao_do_dono":
        raise ValueError("ELENCO_MANAGER: o Manager permanece na sessão do dono")
    if not isinstance(data["hosts"], dict) or set(data["hosts"]) != set(HOSTS):
        raise ValueError("ELENCO_HOSTS: são necessários os dois hosts")
    for host, profiles in data["hosts"].items():
        if not isinstance(profiles, dict) or set(profiles) != set(ROLES):
            raise ValueError(f"ELENCO_ROLES: papéis incompletos em {host}")
        for role, p in profiles.items():
            if not isinstance(p, dict) or set(p) != {"model_id", "effort", "mechanisms"}:
                raise ValueError(f"ELENCO_PROFILE: {host}/{role}")
            model = p["model_id"]
            if not isinstance(model, str) or model not in MODELS:
                raise ValueError(f"ELENCO_MODEL: ID explícito inválido em {host}/{role}")
            vendor = MODELS[model]
            expected = ("anthropic" if role == "planner·interface" else
                        "openai" if role == "planner·sistema" else
                        ("anthropic" if host == "codex" else "openai") if role == "reviewer" else
                        ("openai" if host == "codex" else "anthropic"))
            if vendor != expected:
                raise ValueError(f"ELENCO_VENDOR: vendor incorreto em {host}/{role}")
            if not isinstance(p["effort"], str) or p["effort"] not in EFFORTS[vendor]:
                raise ValueError(f"ELENCO_EFFORT: esforço inválido em {host}/{role}")
            mechanisms = p["mechanisms"]
            if (not isinstance(mechanisms, list) or not mechanisms or
                    any(not isinstance(m, str) for m in mechanisms) or
                    len(set(mechanisms)) != len(mechanisms) or
                    not set(mechanisms) <= MECHANISMS[(host, vendor)]):
                raise ValueError(f"ELENCO_MECHANISM: via inválida em {host}/{role}")


def catalog_digest(data: dict) -> str:
    validate_catalog(data)
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_catalog(package_root: Path) -> dict:
    """Usa a raiz comprovada do pacote carregado; não procura latest ou caches."""
    root = Path(package_root)
    if not root.is_absolute():
        raise ValueError("ELENCO_ROOT: raiz absoluta do pacote carregado obrigatória")
    try:
        if not (root / "scripts/kanban-status.sh").is_file():
            raise ValueError("ELENCO_ROOT: raiz incompleta")
        manifest = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        data = json.loads((root / "references/elenco-padrao.json").read_text(encoding="utf-8"))
        version = manifest["version"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError("ELENCO_ROOT: manifesto/catálogo ausente ou inválido") from exc
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("ELENCO_VERSION: versão inválida no manifesto")
    validate_catalog(data)
    return {**data, "version": version, "catalog_sha256": catalog_digest(data)}


def render_host_table(catalog: dict, host: str) -> str:
    if host not in HOSTS:
        raise ValueError("ELENCO_HOST: host desconhecido")
    lines = ["| Papel | LLM · effort |", "|---|---|"]
    for role in ROLES:
        p = catalog["hosts"][host][role]
        lines.append(f"| {role} | `{p['model_id']}@{p['effort']}` |")
    return "\n".join(lines)


def factory_block(catalog: dict) -> str:
    """Bloco documental derivado, comparável byte a byte pelo lint."""
    parts = ["<!-- orq:elenco-padrao:start -->"]
    for host in HOSTS:
        parts.extend([f"### Fábrica — Host {host.capitalize()}", "", render_host_table(catalog, host), ""])
    parts.append("<!-- orq:elenco-padrao:end -->")
    return "\n".join(parts)


def classify_intent(text: str) -> str | None:
    normalized = "".join(c for c in unicodedata.normalize("NFD", text.lower())
                         if unicodedata.category(c) != "Mn")
    if re.search(r"\bpadrao\s+(?:d(?:est)?a\s+versao|orquestra)\b", normalized):
        return "versioned-default"
    if re.search(r"\bperfil\s+(?:padrao|economia)\b", normalized):
        return "local-preset"
    return None


def _receipt_matches(receipt: dict, role: str, profile: dict, contexts: dict,
                     disabled: list) -> bool:
    if not isinstance(receipt, dict) or receipt.get("success") is not True:
        return False
    route = receipt.get("mechanism")
    if not isinstance(route, str) or route not in profile["mechanisms"] or route in disabled:
        return False
    role_context = contexts.get(role, {})
    current_context = role_context.get(route) if isinstance(role_context, dict) else None
    if not isinstance(current_context, dict):
        return False
    expected_sandbox = "workspace-write" if role.startswith("implementer") or role == "docs" else "read-only"
    if current_context.get("sandbox") != expected_sandbox:
        return False
    for key in ("account", "client_version", "sandbox"):
        value = current_context.get(key)
        if not isinstance(value, str) or not value.strip() or receipt.get(key) != value:
            return False
    if receipt.get("role") != role or not isinstance(receipt.get("evidence_ref"), str) or not receipt["evidence_ref"].strip():
        return False
    for key, expected in (("model_id", profile["model_id"]), ("effort", profile["effort"]),
                          ("sent_model_id", profile["model_id"]), ("sent_effort", profile["effort"]),
                          ("observed_model_id", profile["model_id"])):
        if receipt.get(key) != expected:
            return False
    # Ausência de effort observado não é prova de effort efetivo no servidor.
    return receipt.get("observed_effort") in (None, profile["effort"])


def preview_adoption(active: dict, catalog: dict, host: str, contexts: dict,
                     receipts: list, *, adopted_at: str) -> dict:
    """Só monta proposta. Recibos devem ser auditados pelo Manager, não autodeclarados.

    Não lê/escreve elenco, chama modelo, aprova egress ou certifica autenticidade
    do recibo. O chamador preserva o snapshot anterior e exige o gate de adoção.
    hosts[host] é a projeção dos oito papéis de fábrica, não a seção Markdown
    completa. Manager/papéis adicionais e overrides locais ficam fora dela;
    o chamador aplica só o diff desses oito papéis, nunca substitui a seção.
    """
    if host not in HOSTS:
        raise ValueError("ELENCO_HOST: host desconhecido")
    if not isinstance(adopted_at, str) or not adopted_at.strip():
        raise ValueError("ELENCO_DATE: data da proposta obrigatória")
    raw_catalog = {k: catalog[k] for k in ("schema", "manager", "hosts")}
    validate_catalog(raw_catalog)
    if (not isinstance(catalog.get("version"), str) or
            not re.fullmatch(r"\d+\.\d+\.\d+", catalog["version"]) or
            catalog.get("catalog_sha256") != catalog_digest(raw_catalog)):
        raise ValueError("ELENCO_PROVENANCE: versão/digest da proposta inválidos")
    if not isinstance(active, dict) or not isinstance(contexts, dict) or not isinstance(receipts, list):
        raise ValueError("ELENCO_SNAPSHOT: entrada inválida")
    if any(not isinstance(active.get(key, {}), dict) for key in ("hosts", "overrides", "provenance")):
        raise ValueError("ELENCO_SNAPSHOT: mapas de estado inválidos")
    previous = active.get("hosts", {}).get(host, {})
    overrides = active.get("overrides", {}).get(host, {})
    disabled_names = active.get("disabled_mechanisms", [])
    if (not isinstance(previous, dict) or not isinstance(overrides, dict) or
            not set(overrides) <= set(ROLES) or not isinstance(disabled_names, list) or
            any(not isinstance(name, str) for name in disabled_names)):
        raise ValueError("ELENCO_SNAPSHOT: host/overrides/vias inválidos")
    disabled = set(disabled_names)
    for name in disabled_names:
        disabled.update(DISABLED_VIAS[host].get(name, set()))
    if any(not isinstance(p, dict) or p != previous.get(role) for role, p in overrides.items()):
        raise ValueError("ELENCO_OVERRIDE: preserve somente o override já ativo")
    target = copy.deepcopy(catalog["hosts"][host])
    # Override é explícito; escolha legada sem marca não é reinterpretada.
    target.update(copy.deepcopy(overrides))
    previous_origin = active.get("provenance", {}).get(host, {})
    retained = previous_origin.get("proofs", {}) if isinstance(previous_origin, dict) else {}
    retained = retained if isinstance(retained, dict) else {}
    selected_proofs = {}
    missing = []
    for role in ROLES:
        if role in overrides:
            continue
        candidates = list(receipts)
        old_profile = previous.get(role, {})
        old_proof = retained.get(role)
        if (isinstance(old_profile, dict) and isinstance(old_proof, dict) and
                old_profile.get("model_id") == target[role]["model_id"] and
                old_profile.get("effort") == target[role]["effort"] and
                old_profile.get("mechanisms") == [old_proof.get("mechanism")]):
            candidates.append(old_proof)
        matched = next((r for r in candidates
                        if _receipt_matches(r, role, target[role], contexts, disabled)), None)
        if matched is None:
            missing.append(role)
            continue
        target[role]["mechanisms"] = [matched["mechanism"]]
        selected_proofs[role] = {key: copy.deepcopy(matched.get(key)) for key in PROOF_FIELDS}
    provenance = active.get("provenance", {}).get(host)
    result = {"state": "needs-proof" if missing else "ready", "host": host,
              "origin": "versioned-default" if provenance else "legacy",
              "missing_roles": missing, "proposal": None,
              "previous_host": copy.deepcopy(previous)}
    if missing:
        return result
    proposal = copy.deepcopy(active)
    proposal.setdefault("hosts", {})[host] = target
    proposal.setdefault("provenance", {})[host] = {
        "origin": "orquestra-version", "version": catalog["version"],
        "catalog_sha256": catalog["catalog_sha256"], "adopted_at": adopted_at,
        "overrides": copy.deepcopy(overrides),
        "mechanisms": {role: p["mechanisms"][0] for role, p in target.items() if role not in overrides},
        "proofs": selected_proofs,
    }
    result["proposal"] = proposal
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta pura do elenco padrão do pacote carregado; não adota.")
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--host", choices=HOSTS)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--installed-version", help="Só diagnóstico; nunca seleciona outra versão")
    args = parser.parse_args()
    try:
        catalog = load_catalog(args.package_root)
        warnings = []
        if args.installed_version and args.installed_version != catalog["version"]:
            warnings.append("Versão instalada difere da carregada; esta proposta usa apenas o pacote carregado.")
        if args.format == "markdown":
            print(render_host_table(catalog, args.host) if args.host else factory_block(catalog))
        else:
            selected = {args.host: catalog["hosts"][args.host]} if args.host else catalog["hosts"]
            print(json.dumps({**catalog, "hosts": selected, "state": "proposal", "warnings": warnings},
                             ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
