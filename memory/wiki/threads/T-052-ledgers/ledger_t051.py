#!/usr/bin/env python3
"""Ledger dos 25 bloqueadores do T-051 — um probe por bloqueador.

Uso: python3 ledger_t051.py <raiz-da-arvore>

Regra de validação do próprio ledger: TEM que dar 25/25 contra `dcc350b`.
Probe que não passa no golden é probe errado, não árvore errada.

Dois tipos de probe:
  · TEXTO   — invariante literal em arquivo de instrução (regra positiva presente,
              regra proibida ausente).
  · GUARDA  — contraprova NEGATIVA: copia a árvore, aplica exatamente a mutação
              que o revisor descreveu, roda o lint e exige exit != 0. Guarda que
              existe mas não é chamado deixa o lint verde e reprova aqui.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def roda_lint(raiz):
    r = subprocess.run(
        [sys.executable, "-B", "orq/scripts/lint-coerencia.py", "."],
        cwd=raiz,
        capture_output=True,
        text=True,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def contraprova(mutar, nome, espera):
    """Aplica `mutar(tmp)` numa cópia e exige que o lint reprove PELO GUARDA CERTO.

    Exigir só `exit != 0` não serve: qualquer erro colateral (divergência de
    cache instalado, por exemplo) satisfaria o probe sem que o guarda existisse.
    Por isso a mensagem específica é parte do critério.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "arv"
        shutil.copytree(RAIZ, tmp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        try:
            mutar(tmp)
        except Exception as exc:  # mutação não aplicável = probe inválido
            return False, f"mutação falhou: {exc}"
        rc, saida = roda_lint(tmp)
        if rc == 0:
            return False, f"lint passou VERDE com a mutação ({nome})"
        if espera not in saida:
            return False, f"lint reprovou por OUTRO motivo (esperava {espera!r}) — {nome}"
        return True, f"lint reprovou pelo guarda certo: {espera!r}"


def _lint_modulo():
    """Importa o lint DA ÁRVORE sob teste, para probar função a função."""
    import importlib.util

    scripts = RAIZ / "orq" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location(
        "lint_sob_teste", scripts / "lint-coerencia.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def troca(p: Path, velho, novo, n=1):
    t = p.read_text(encoding="utf-8")
    if t.count(velho) != n:
        raise AssertionError(f"âncora {velho[:50]!r} ocorre {t.count(velho)}x, esperado {n}")
    p.write_text(t.replace(velho, novo), encoding="utf-8")


# --------------------------------------------------------------------------
# Rodada 1 — 5 bloqueadores
# --------------------------------------------------------------------------
def r1_b1():
    """Painel recriado: 'ao lado do revisor interno' nas instruções-raiz."""
    ok = True
    for arq in ("CLAUDE.md", "AGENTS.md"):
        t = ler(arq)
        ok &= "ao lado do revisor interno" not in t
        ok &= "não há revisor interno ao seu\nlado" in t or "não há revisor interno ao seu lado" in t
        ok &= "Você é o **único** revisor" in t
    ok &= ler("CLAUDE.md") == ler("AGENTS.md")
    return ok, "CLAUDE.md == AGENTS.md, revisor único, sem revisor interno ao lado"


def r1_b2():
    """Bloco Status do README prometia Codex+Kimi e painel de três."""
    m = re.search(r"^## Status$(.*?)^## ", ler("README.md"), re.M | re.S)
    if not m:
        return False, "seção `## Status` não encontrada"
    s = m.group(1)
    ok = "Kimi" not in s and "painel" not in s and "Moonshot" not in s.replace(
        "ao antigo terceiro host (Moonshot) **foi removido**", ""
    )
    return ok, "Status sem Kimi e sem painel"


def r1_b3():
    """Trivial ganhava faixa `leve` contra 'onde não há spawn, não há faixa'."""
    t = ler("orq/skills/orq/SKILL.md")
    linha = next(l for l in t.split("\n") if l.startswith("| **Trivial**"))
    ok = linha.rstrip().endswith("| **—** |")
    ok &= "Onde não há spawn,\nnão há faixa" in t
    ok &= "A faixa só vale de **Pequeno** para cima." in t
    return ok, "Trivial sem faixa + regra explícita"


def r1_b4():
    """Segundo parecer 'avulso' sem restrição de vendor = porta dos fundos."""
    t = ler("orq/commands/revisar.md")
    ok = "**Segundo parecer só sob demanda do dono — e sob a MESMA regra de vendor.**" in t
    ok &= "chamá-lo de \"avulso\" não o torna" in t
    return ok, "segundo parecer preso ao vendor oposto"


def r1_b5():
    """Contar reviewer no template inteiro: trocar as linhas entre hosts ficava 1/1."""
    def mutar(tmp):
        p = tmp / "orq/commands/elenco.md"
        t = p.read_text(encoding="utf-8")
        a = "| reviewer | `gpt-5.6-sol@xhigh` |"
        b = "| reviewer | `opus` (exigir comprovação de que o alias resolve para Opus 5)"
        ia, ib = t.index(a), t.index(b)
        la = t[ia : t.index("\n", ia)]
        lb = t[ib : t.index("\n", ib)]
        t = t[:ia] + lb + t[ia + len(la) :]
        ib = t.index(lb, ia + len(lb))
        t = t[:ib] + la + t[ib + len(lb) :]
        p.write_text(t, encoding="utf-8")

    return contraprova(
        mutar,
        "reviewer trocado entre Host Claude e Host Codex",
        "traz o reviewer do outro host",
    )


# --------------------------------------------------------------------------
# Rodada 2 — 8 bloqueadores
# --------------------------------------------------------------------------
def r2_b1():
    """Duas fontes incompatíveis para o elenco ativo (`## Papéis` vs `## Times por host`)."""
    t = ler("orq/commands/elenco.md")
    ok = "legada: não leia, não grave" in t
    ok &= "## Papéis (a tabela ativa" not in t
    ok &= "leia a tabela DELE em `## Times por host`" in t
    tpl = t.split("## Modelo do arquivo", 1)[1]
    ok &= "\n## Papéis\n" not in tpl  # o template não pode gerar a tabela legada
    return ok, "fonte ativa única e host-aware"


def r2_b2():
    """Régua canônica dava faixa ao Trivial que a skill proíbe."""
    t = ler("orq/commands/elenco.md")
    ok = "**Pré-condição, antes da pergunta 1:**" in t and "Trivial" in t.split(
        "**Pré-condição, antes da pergunta 1:**", 1
    )[1][:400]
    return ok, "Trivial encerra a classificação antes da régua"


def r2_b3():
    """Linha Normal fixava faixa que a régua manda variar."""
    t = ler("orq/skills/orq/SKILL.md")
    ok = "**A coluna é o ponto de partida, não o veredito**" in t
    ok &= "desenho ainda por decidir **sobe** para `pesada`" in t
    ok &= "**Alto risco é a exceção: tem piso `pesada` e\nnão rebaixa nunca**" in t
    return ok, "coluna Faixa declarada como default, com as duas transições"


def r2_b4():
    """`secao_de` aceitava substring: `### Host Codex antigo` passava por `### Host Codex`."""
    mod = _lint_modulo()
    texto = "### Host Codex antigo\n\n| Papel | Modelo |\n|---|---|\n| reviewer | `opus` |\n"
    achadas = mod.secoes_de(texto, "### Host Codex")
    inline = mod.secoes_de("bla ### Host Codex bla\n", "### Host Codex")
    ok = achadas == [] and inline == []
    ok &= len(mod.secoes_de("### Host Codex\ncorpo\n", "### Host Codex")) == 1
    return ok, f"heading prefixado/inline não casa (prefixado={len(achadas)}, inline={len(inline)}), exato casa 1×"


def r2_b5():
    """Guarda do host aposentado ignorava README, CLAUDE.md e AGENTS.md."""
    resultados = []
    for arq in ("README.md", "CLAUDE.md", "AGENTS.md"):
        def mutar(tmp, arq=arq):
            p = tmp / arq
            p.write_text(
                p.read_text(encoding="utf-8")
                + "\n\nUse o Kimi K3 (Moonshot) como revisor deste repositório.\n",
                encoding="utf-8",
            )

        resultados.append(
            contraprova(mutar, f"Kimi vivo em {arq}", "cita o host aposentado")
        )
    ok = all(r[0] for r in resultados)
    return ok, "; ".join(f"{a}: {r[1]}" for a, r in zip(("README", "CLAUDE", "AGENTS"), resultados))


def r2_b6():
    """'outra LLM' enfraquecia 'vendor oposto' no frontmatter e nos consumidores."""
    fm = ler("orq/commands/revisar.md").split("---", 2)[1]
    ok = "vendor OPOSTO ao do host" in fm
    ok &= "todo revisor é de outra LLM" not in ler("orq/commands/revisar.md")
    for arq in ("README.md", "orq/commands/ajuda.md", "orq/skills/orq/SKILL.md"):
        ok &= "outra LLM que a do host" not in ler(arq)
    ok &= "**vendor oposto** ao do host" in ler("orq/commands/ajuda.md")
    return ok, "vendor oposto no frontmatter e nos três consumidores"


def r2_b7():
    """Fluxo permitia segundo parecer e depois dizia que ele não existe."""
    t = ler("orq/commands/revisar.md")
    ok = "### Ramo padrão — um parecer (N=1)" in t
    ok &= "segundo parecer" in t.split("### Ramo padrão — um parecer (N=1)", 1)[1]
    ok &= re.search(r"### Ramo excepcional.*segundo parecer", t, re.I | re.S) is not None
    return ok, "auditoria N=1 separada do ramo com segundo parecer"


def r2_b8():
    """Ajuste do elenco continuava hard-coded para Claude apesar do host Codex."""
    t = ler("orq/commands/elenco.md")
    ok = "**Resolva o host primeiro.**" in t
    ok &= "Valide o modelo **contra o vendor do host resolvido no passo 0**" in t
    ok &= "no host Codex, um modelo\n     OpenAI com effort opcional" in t
    return ok, "host resolvido antes de validar modelo e via"


# --------------------------------------------------------------------------
# Rodada 3 — 4 bloqueadores
# --------------------------------------------------------------------------
def r3_1():
    """`codex off` era reconhecido como via e depois validado como modelo."""
    t = ler("orq/commands/elenco.md")
    ok = "O único valor aceito é `on` ou `off`" in t
    ok &= "Grave o valor na coluna **Estado**" in t
    ok &= "este é o ramo, e ele termina aqui; não caia na validação de modelo do passo 2" in t
    ok &= "codex xhigh" not in t  # exemplo que contradizia o contrato `<via> on|off`
    return ok, "ramo de via com on|off e escrita em Estado"


def r3_2():
    """Transição rebaixava card de Alto risco."""
    t = ler("orq/commands/implement-next.md")
    ok = "inclusive o piso: card Alto risco continua `pesada` mesmo com o plano" in t
    return ok, "piso de Alto risco preservado na transição do Loop B"


def r3_3():
    """Migração não convertia inequivocamente os presets legados."""
    t = ler("orq/commands/elenco.md")
    ok = "⚠️ **Migre por SEÇÃO, não só a tabela ativa.**" in t
    ok &= "a tabela ativa **e cada preset** de `## Perfis`" in t
    ok &= "vira **exatamente 8**" in t and "vira **9**" in t
    ok &= "reconciliação linha a linha" in t
    return ok, "migração por seção, com aritmética 8/9 e reconciliação no gate"


def r3_4():
    """Máscara de cercas só reconhecia crases: heading dentro de `~~~` era contado."""
    mod = _lint_modulo()
    til = "~~~markdown\n### Host Codex\ncorpo\n~~~\n"
    longa = "````markdown\n### Host Codex\ncorpo\n```\nainda dentro\n````\n"
    ok = mod.secoes_de(til, "### Host Codex") == []
    ok &= mod.secoes_de(longa, "### Host Codex") == []
    return ok, "heading dentro de `~~~` e de cerca longa não conta como seção"


# --------------------------------------------------------------------------
# Rodada 4 — 5 bloqueadores
# --------------------------------------------------------------------------
def r4_1():
    """A wiki permitia rebaixar card de Alto risco."""
    t = ler("memory/wiki/_elenco.md")
    ok = "card Alto risco continua `pesada`" in t
    ok &= "Só rebaixa a `pesada` que veio **exclusivamente** de desenho aberto" in t
    return ok, "piso de Alto risco também na síntese da wiki"


def r4_2():
    """Exemplo canônico de roteamento nomeava modelos e quebrava no host Codex."""
    t = ler("orq/skills/orq/SKILL.md")
    ok = "⚠️ **O exemplo nomeia PAPÉIS, não modelos, de propósito**" in t
    bloco = re.search(r"> \*\"Isso é normal.*?\n\n", t, re.S)
    ok &= bloco is not None
    if bloco:
        ex = bloco.group(0)
        ok &= "**planner·sistema**" in ex and "**reviewer**" in ex
        ok &= not any(m in ex for m in ("Sonnet", "GPT", "Opus", "Fable"))
    return ok, "exemplo resolvido por papel, sem modelo fixo"


def r4_3():
    """Ramo de via aceitava via que não é cross-vendor para o host atual."""
    t = ler("orq/commands/elenco.md")
    ok = "leia a coluna `Consumida por` daquela via e derive o efeito real dali" in t
    ok &= "Confirme **o efeito, não o ato**" in t
    ok &= "isto não muda nada nesta sessão; afeta o host X, nos papéis Y" in t
    ok &= "No host Claude, `/orq:elenco codex off`" in ler("README.md")
    return ok, "efeito da via derivado de `Consumida por`, com README qualificado"


def r4_4():
    """`init` ignorava a migração por seção definida pelo elenco."""
    t = ler("orq/commands/init.md")
    ok = "Não improvise migração aqui — siga a canônica.**" in t
    ok &= "(a do host **e cada preset**)" in t
    ok &= "preset 8 linhas, tabela de host 9" in t
    ok &= "remover o `## Papéis` legado depois de copiá-lo" in t
    return ok, "init encaminha para a migração canônica do elenco"


def r4_5():
    """Máscara aceitava indentação que CommonMark não aceita: 4 espaços não abrem cerca."""
    mod = _lint_modulo()
    quatro = "## Times por host\nA\n    ```\n## Times por host\nB\n"
    tres = "## Times por host\nA\n   ```\n## Times por host\nB\n   ```\n"
    tab = "## Times por host\nA\n\t```\n## Times por host\nB\n"
    ok = len(mod.secoes_de(quatro, "## Times por host")) == 2  # duplicata visível
    ok &= len(mod.secoes_de(tab, "## Times por host")) == 2  # tab também não abre
    ok &= len(mod.secoes_de(tres, "## Times por host")) == 1  # 0–3 espaços abrem
    return ok, "4 espaços e tab não abrem cerca (duplicata visível); 3 espaços abrem"


# --------------------------------------------------------------------------
# Rodada 5 — 2 bloqueadores
# --------------------------------------------------------------------------
def r5_1():
    """Guarda aceitava papel ausente quando o nome aparecia na prosa da seção."""
    def mutar(tmp):
        p = tmp / "orq/commands/elenco.md"
        t = p.read_text(encoding="utf-8")
        i = t.index("### Host Claude")
        j = t.index("### Host Codex", i)
        bloco = t[i:j]
        linha = next(l for l in bloco.split("\n") if l.startswith("| implementer·leve |"))
        novo = bloco.replace(linha, linha.replace("| implementer·leve |", "| auditor |", 1))
        novo += "\nNota: o papel implementer·leve continua descrito nesta seção.\n"
        p.write_text(t[:i] + novo + t[j:], encoding="utf-8")

    return contraprova(
        mutar,
        "papel trocado na tabela e citado só na prosa",
        "não é linha da tabela",
    )


def r5_2():
    """Codex podia registrar Fable/Sonnet e o runner executar Opus."""
    t = ler("orq/commands/elenco.md")
    ok = "o MECANISMO daquela célula tem que conseguir executar o modelo" in t
    ok &= "o único modelo Anthropic aceito é **`opus`**" in t
    ok &= "Parametrizar o\n       runner é **card novo**" in t
    return ok, "modelo validado contra o mecanismo da célula, não só contra o vendor"


# --------------------------------------------------------------------------
# Rodada 6 — 1 bloqueador
# --------------------------------------------------------------------------
def r6_1():
    """`scout` recebia políticas incompatíveis de vendor."""
    t = ler("orq/commands/elenco.md")
    ok = "**`implementer`, `docs` e `scout` ficam no vendor do host.**" in t
    ok &= "**`implementer`, `docs` e `scout`: só modelos do vendor do host.**" in t
    # `scout` não pode aparecer em `Consumida por` de nenhuma via
    for arq in ("orq/commands/elenco.md", "memory/wiki/_elenco.md"):
        for linha in ler(arq).split("\n"):
            if linha.startswith("| codex ") or linha.startswith("| runner-opus "):
                ok &= "scout" not in linha
    ok &= "Docs e scout seguem o vendor do host" in ler("memory/wiki/_elenco.md")
    return ok, "scout no vendor do host em todas as superfícies, fora de `Consumida por`"


PROBES = [
    ("R1-B1", "painel recriado em CLAUDE.md/AGENTS.md", r1_b1),
    ("R1-B2", "Status do README prometia Kimi e painel", r1_b2),
    ("R1-B3", "Trivial com faixa contra 'sem spawn, sem faixa'", r1_b3),
    ("R1-B4", "segundo parecer avulso sem restrição de vendor", r1_b4),
    ("R1-B5", "guarda do reviewer não ancorada no host", r1_b5),
    ("R2-B1", "duas fontes para o elenco ativo", r2_b1),
    ("R2-B2", "régua dava faixa ao Trivial", r2_b2),
    ("R2-B3", "linha Normal fixava faixa que a régua varia", r2_b3),
    ("R2-B4", "secao_de aceitava substring de heading", r2_b4),
    ("R2-B5", "guarda do host aposentado ignorava 3 superfícies", r2_b5),
    ("R2-B6", "'outra LLM' enfraquecia 'vendor oposto'", r2_b6),
    ("R2-B7", "segundo parecer permitido e depois negado", r2_b7),
    ("R2-B8", "ajuste do elenco hard-coded para Claude", r2_b8),
    ("R3-1", "via reconhecida mas não aplicável (`codex off`)", r3_1),
    ("R3-2", "transição rebaixava card de Alto risco", r3_2),
    ("R3-3", "migração não convertia presets legados", r3_3),
    ("R3-4", "máscara de cercas ignorava `~~~`", r3_4),
    ("R4-1", "wiki permitia rebaixar Alto risco", r4_1),
    ("R4-2", "exemplo de roteamento quebrava no host Codex", r4_2),
    ("R4-3", "via não cross-vendor aceita para o host atual", r4_3),
    ("R4-4", "init ignorava a migração por seção", r4_4),
    ("R4-5", "cerca indentada com 4 espaços mascarava duplicata", r4_5),
    ("R5-1", "papel ausente aceito por menção na prosa", r5_1),
    ("R5-2", "elenco registrava Fable e o runner executava Opus", r5_2),
    ("R6-1", "scout com políticas de vendor incompatíveis", r6_1),
]


def main():
    print(f"# Ledger T-051 — 25 bloqueadores · árvore: {RAIZ}\n")
    passou = 0
    falhos = []
    for pid, titulo, fn in PROBES:
        try:
            ok, detalhe = fn()
        except Exception as exc:
            ok, detalhe = False, f"ERRO no probe: {type(exc).__name__}: {exc}"
        marca = "PASS" if ok else "FAIL"
        if ok:
            passou += 1
        else:
            falhos.append(pid)
        print(f"[{marca}] {pid} — {titulo}\n        {detalhe}")
    print(f"\n=== {passou}/{len(PROBES)} ===")
    if falhos:
        print("FALHARAM:", ", ".join(falhos))
    return 0 if passou == len(PROBES) else 1


if __name__ == "__main__":
    sys.exit(main())
