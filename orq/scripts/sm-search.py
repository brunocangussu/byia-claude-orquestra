#!/usr/bin/env python3
"""Busca no Supermemory CONTORNANDO o bug do MCP.

O MCP oficial escopa por header `x-sm-project`, mas o endpoint /v3/search IGNORA
esse header e devolve 0 resultados. A busca só funciona passando `containerTags`
no CORPO. Este script faz isso. (Diagnosticado 25/Jul/2026.)

Uso:
  sm-search.py "termo de busca" [--limit N] [--full] [--project TAG]

Lê o token de ~/.claude.json (mcpServers.api-supermemory-ai). NUNCA imprime o token.
"""
import argparse, json, os, sys, urllib.request, urllib.error

CFG = os.path.expanduser("~/.claude.json")


def load_auth():
    try:
        sm = json.load(open(CFG))["mcpServers"]["api-supermemory-ai"]["headers"]
    except Exception as e:
        sys.exit(f"nao consegui ler a config do supermemory em {CFG}: {e}")
    proj = sm.get("x-sm-project", "")
    tag = proj if proj.startswith("sm_project_") else f"sm_project_{proj}" if proj else None
    return sm["Authorization"], tag


def search(q, limit, tag):
    token, default_tag = load_auth()
    tag = tag or default_tag
    payload = {"q": q, "limit": limit}
    if tag:
        payload["containerTags"] = [tag]
    req = urllib.request.Request(
        "https://api.supermemory.ai/v3/search",
        data=json.dumps(payload).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        sys.exit(f"{type(e).__name__}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--full", action="store_true", help="mostra o chunk inteiro")
    ap.add_argument("--project", default=None, help="containerTag alternativo")
    a = ap.parse_args()
    q = " ".join(a.query)

    res = search(q, a.limit, a.project)
    hits = res.get("results") or []
    print(f'busca: "{q}"  ·  {res.get("total", len(hits))} resultado(s)  ·  {res.get("timing","?")}ms\n')
    if not hits:
        print("(nada encontrado — tente termos mais gerais)")
        return
    for i, h in enumerate(hits, 1):
        when = (h.get("createdAt") or h.get("updatedAt") or "")[:10]
        score = h.get("score")
        head = f"[{i}] {when}"
        if score is not None:
            head += f"  score={score:.3f}" if isinstance(score, float) else f"  score={score}"
        if h.get("documentId") or h.get("id"):
            head += f"  id={h.get('documentId') or h.get('id')}"
        print(head)
        chunks = h.get("chunks") or []
        text = " ".join(c.get("content", "") for c in chunks) or (h.get("summary") or "")
        text = " ".join(text.split())
        print("   " + (text if a.full else text[:600] + ("…" if len(text) > 600 else "")))
        print()


if __name__ == "__main__":
    main()
