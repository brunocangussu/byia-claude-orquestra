"""Compõe um modo opcional do Planner; não cria agentes nem escolhe modelos."""
import argparse
import json
import sys


CONTRACT = """Coordenação técnica limitada, no mesmo planejamento.
Decomponha as frentes e suas dependências; designe um dono de escrita por
arquivo, explicite contratos de interface e proponha ordem de integração
e testes que discriminem os riscos. Marque a investigação ainda pendente.
Uma decomposição não autoriza paralelismo: o Manager decide o despacho.
Não despache workers, crie threads ou execute código. Não aprove planos,
review ou release, não altera o board, elenco, ledger ou permissões.
Não faça Git, instalação, restart, retry ou chamada adicional de modelo.
Entregue proposta e handoff ao Manager único, que audita escopo e evidências.
"""


def compose(mode="off", track="sistema"):
    if mode not in {"off", "technical"} or track not in {"sistema", "interface"}:
        raise ValueError("INVALID_COORDINATION_MODE")
    if mode == "technical" and track != "sistema":
        raise ValueError("SYSTEM_TRACK_REQUIRED")
    return {
        "schema": 1,
        "coordination_mode": mode,
        "role": "planner·sistema" if mode == "technical" else None,
        "authority": "Manager",
        "extra_calls": 0,
        "instructions": CONTRACT if mode == "technical" else "",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("off", "technical"), default="off")
    parser.add_argument("--track", choices=("sistema", "interface"), default="sistema")
    args = parser.parse_args()
    try:
        print(json.dumps(compose(args.mode, args.track), ensure_ascii=False))
        return 0
    except ValueError:
        print('{"error":"SYSTEM_TRACK_REQUIRED"}', file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
