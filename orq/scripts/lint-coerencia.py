#!/usr/bin/env python3
"""Lint de coerência interna do plugin Orquestra.

Falha quando uma instrução cita algo que não existe: comando, agente, skill ou
arquivo referenciado via ${CLAUDE_PLUGIN_ROOT}. É o defeito que `claude plugin
validate --strict` NÃO pega — ele valida o manifesto, não a coerência entre os
prompts. Foi assim que `/orquestra:*` sobreviveu a três releases depois da
renomeação para `orq`.

Uso:
    python3 orq/scripts/lint-coerencia.py [raiz-do-repo]

Saída: 0 se coerente, 1 se achou referência quebrada.
"""

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

# `memory/` é deliberadamente excluído: o log é append-only e o gotchas.md citam
# nomes de comandos QUE DEIXARAM DE EXISTIR, de propósito, ao descrever bugs
# passados. Varrer memory/ produz falso positivo em todo checkpoint — e lint que
# grita à toa é lint que o dono desliga.
DIRS_IGNORADOS = {"memory", ".git", "node_modules"}

PADROES = [
    # (regex, nome do universo, mensagem)
    # Capturam o identificador INTEIRO (incl. dígitos e _), senão `/orq:revisar2`
    # casaria só "revisar" e passaria como válido — deixando a referência quebrada
    # invisível, que é justamente o que este lint existe para impedir.
    (re.compile(r"/orq:([A-Za-z0-9_-]+)"), "comandos", "comando /orq:{} não existe"),
    # Sem exigir crases: `orq-inexistente` solto no texto também é referência.
    (re.compile(r"\b(orq-[A-Za-z0-9_-]+)"), "agentes", "agente {} não existe"),
    # Crases OBRIGATÓRIAS aqui — ao contrário do padrão de agente acima.
    # Testado: sem elas, "a skill e o comando" / "skill ou agente" viram falso
    # positivo, porque "skill" é palavra comum na prosa em português. O prefixo
    # `orq-` não tem esse problema: não aparece em texto corrido.
    # Assimetria proposital: falso positivo é o que faz um lint ser desligado.
    (re.compile(r"skill `([A-Za-z0-9][A-Za-z0-9_-]*)`"), "skills", "skill `{}` não existe"),
]


def universos(plugin: Path) -> dict:
    return {
        "comandos": {p.stem for p in (plugin / "commands").glob("*.md")},
        "agentes": {p.stem for p in (plugin / "agents").glob("*.md")},
        "skills": {p.parent.name for p in plugin.glob("skills/*/SKILL.md")},
    }


# CommonMark: cerca aceita no máximo 3 espaços de indentação — com 4 a linha
# vira bloco indentado, e as crases são conteúdo, não abertura. Tab conta
# como 4, então também não abre. A versão anterior usava `[ \t]*` (indentação
# ilimitada) e por isso uma linha de crases indentada com 4 espaços mascarava
# texto vivo: um probe escondeu a segunda ocorrência de um heading duplicado e
# o lint ficou verde com a duplicata invisível.
_ABRE_CERCA_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def _mascara_cercas(texto: str) -> str:
    """Devolve `texto` com as linhas dentro de blocos cercados trocadas por
    espaços, preservando o comprimento exato — assim um heading CITADO dentro de
    um exemplo de código não é confundido com um heading de verdade, e os
    índices continuam valendo no texto original.

    Reconhecimento no estilo CommonMark, porque a versão ingênua
    (`linha.lstrip().startswith("```")` alternando um booleano) aceitava dois
    headings falsos, os dois comprovados por probe:
      1. cerca de tis (`~~~markdown`) não era reconhecida — o conteúdo inteiro
         contava como texto vivo;
      2. cerca de 4 crases "fechada" por uma de 3 — o toggle desligava e o que
         vinha depois, ainda dentro do bloco, virava texto vivo.
    Regras aplicadas: abertura com 3+ crases OU 3+ tis; fecha só com o **mesmo
    caractere**, comprimento **>= o da abertura** e **sem info string** (texto
    após a cerca de fechamento a desqualifica, como no CommonMark).
    Cerca não fechada: o resto do texto conta como dentro — lado seguro, deixa
    de achar um heading em vez de achar um heading falso.
    """
    linhas = texto.split("\n")
    char_aberto = ""
    tam_aberto = 0
    for i, linha in enumerate(linhas):
        m = _ABRE_CERCA_RE.match(linha)
        if not char_aberto:
            if m:
                char_aberto = m.group(1)[0]
                tam_aberto = len(m.group(1))
                linhas[i] = " " * len(linha)
            continue
        # dentro de um bloco: só uma cerca compatível fecha
        fecha = (
            m is not None
            and m.group(1)[0] == char_aberto
            and len(m.group(1)) >= tam_aberto
            and m.group(2).strip() == ""
        )
        linhas[i] = " " * len(linha)
        if fecha:
            char_aberto = ""
            tam_aberto = 0
    return "\n".join(linhas)


def secoes_de(texto: str, heading: str):
    """Todas as seções abertas por `heading`, cada uma do fim do heading até o
    próximo heading de nível igual ou superior (ou o fim do texto).

    O casamento é de **linha inteira** (`^### Host Codex$`, com o texto
    escapado), não substring: a versão anterior usava `heading in texto` +
    `split`, e por isso um arquivo que só tivesse `### Host Codex antigo`
    satisfazia o guarda inteiro — bastava renomear a heading obrigatória para o
    lint ficar verde com a tabela do host inválida.

    Devolve lista: vazia = heading ausente; mais de um item = heading
    duplicado, que é ambiguidade e o chamador precisa reprovar em vez de
    escolher a primeira em silêncio.
    (Sem anotação de retorno: `list[str] | None` etc. elevaria o piso de
    Python; o resto do arquivo se mantém em 3.9.)
    """
    nivel = len(heading) - len(heading.lstrip("#"))
    mascarado = _mascara_cercas(texto)
    inicio = re.compile(r"^" + re.escape(heading) + r"[ \t]*$", re.MULTILINE)
    proximo = re.compile(r"^#{1," + str(nivel) + r"}[ \t]", re.MULTILINE)
    achadas = []
    for m in inicio.finditer(mascarado):
        fim = len(texto)
        seguinte = proximo.search(mascarado, m.end())
        if seguinte is not None:
            fim = seguinte.start()
        achadas.append(texto[m.end():fim])
    return achadas


def secao_unica(texto: str, heading: str):
    """`(secao, estado)` para o heading que só pode existir uma vez.

    `estado` é `"ok"`, `"ausente"` ou `"duplicado:<n>"`. Existe porque todo
    chamador de `secoes_de` quer exatamente uma seção, e o jeito "óbvio" de
    consumir a lista esconde a duplicata: `secoes[0]` valida em silêncio só a
    primeira, e `"\n".join(secoes)` valida o conjunto — os dois deixam passar
    um segundo bloco divergente. Foi assim que dois `## Status`, um em 0.23.0 e
    outro em 0.24.0, mantiveram o lint verde enquanto o bloco que se lê primeiro
    anunciava a versão velha.
    """
    achadas = secoes_de(texto, heading)
    if not achadas:
        return None, "ausente"
    if len(achadas) > 1:
        return None, f"duplicado:{len(achadas)}"
    return achadas[0], "ok"


def _linha_unica(texto: str, prefixo: str):
    """Mesma semântica de `secao_unica`, para âncora que é uma linha só."""
    achadas = [l for l in texto.splitlines() if l.startswith(prefixo)]
    if not achadas:
        return None, "ausente"
    if len(achadas) > 1:
        return None, f"duplicado:{len(achadas)}"
    return achadas[0], "ok"


def papeis_da_tabela(secao: str):
    """Primeira célula de cada linha de dados de uma tabela markdown.

    Existe porque procurar o nome do papel na SEÇÃO (`papel in secao`) prova que
    o texto aparece em algum lugar — numa nota de rodapé, por exemplo — e não que
    ele é uma linha da tabela. Um probe do revisor trocou `implementer·leve` por
    `auditor` na tabela, manteve a contagem e citou o papel numa nota fora dela:
    o lint ficou verde com o template gerando elenco inválido.

    Descarta o cabeçalho (primeira célula `Papel`) e o separador (`---`), e
    normaliza crases/negrito para comparar por valor.
    """
    papeis = []
    for linha in secao.splitlines():
        if not linha.startswith("|"):
            continue
        celulas = linha.split("|")
        if len(celulas) < 3:
            continue
        bruta = celulas[1].strip()
        if set(bruta) <= {"-", ":"} and bruta:
            continue
        nome = bruta.strip("`* ").strip()
        if nome.lower() == "papel":
            continue
        papeis.append(nome)
    return papeis


def arquivos_a_varrer(raiz: Path, plugin: Path):
    for p in plugin.rglob("*.md"):
        yield p
    for nome in ("README.md", "CLAUDE.md", "AGENTS.md"):
        alvo = raiz / nome
        if alvo.exists():
            yield alvo


def validate_hooks(raiz: Path, plugin: Path) -> list[tuple[Path, int, str]]:
    hooks_path = plugin / "hooks" / "hooks.json"
    if not hooks_path.exists():
        return []
    rel = hooks_path.relative_to(raiz)
    try:
        config = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [(rel, 0, f"hooks/hooks.json inválido: {exc}")]
    hooks = config.get("hooks") if isinstance(config, dict) else None
    if not isinstance(hooks, dict):
        return [(rel, 0, "hooks/hooks.json precisa conter objeto `hooks`")]

    problemas: list[tuple[Path, int, str]] = []
    raiz_plugin = plugin.resolve()
    root_ref = re.compile(r"\$\{(?:CLAUDE_)?PLUGIN_ROOT\}/([\w./-]+)")
    for evento, grupos in hooks.items():
        if not isinstance(grupos, list):
            problemas.append((rel, 0, f"hook {evento} precisa ser uma lista"))
            continue
        for grupo in grupos:
            handlers = grupo.get("hooks") if isinstance(grupo, dict) else None
            if not isinstance(handlers, list):
                problemas.append((rel, 0, f"hook {evento} não contém lista de handlers"))
                continue
            for handler in handlers:
                if not isinstance(handler, dict) or handler.get("type") != "command":
                    problemas.append((rel, 0, f"hook {evento} tem handler não-command"))
                    continue
                command = handler.get("command")
                if not isinstance(command, str):
                    problemas.append((rel, 0, f"hook {evento} não tem command string"))
                    continue
                for match in root_ref.finditer(command):
                    ref = match.group(1).rstrip(".")
                    alvo = (plugin / ref).resolve()
                    dentro = os.path.commonpath([str(alvo), str(raiz_plugin)]) == str(raiz_plugin)
                    if not dentro or not alvo.is_file():
                        motivo = "escapa do plugin" if not dentro else "não existe"
                        problemas.append((rel, 0, f"{ref} {motivo}"))
    return problemas


def main() -> int:
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    plugin = raiz / "orq"
    if not (plugin / ".claude-plugin" / "plugin.json").exists():
        print(f"✗ não achei o plugin em {plugin}", file=sys.stderr)
        return 2

    conhecidos = universos(plugin)
    problemas = []
    problemas.extend(validate_hooks(raiz, plugin))

    for arq in arquivos_a_varrer(raiz, plugin):
        if DIRS_IGNORADOS & set(arq.relative_to(raiz).parts):
            continue
        rel = arq.relative_to(raiz)
        for num, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
            for regex, universo, msg in PADROES:
                for m in regex.finditer(linha):
                    if m.group(1) not in conhecidos[universo]:
                        problemas.append((rel, num, msg.format(m.group(1))))
            for m in re.finditer(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", linha):
                # rstrip('.'): a referência costuma terminar frase ("…/stack.md.")
                # e o ponto final não faz parte do caminho.
                ref = m.group(1).rstrip(".")
                alvo = (plugin / ref).resolve()
                # is_file(): diretório não conta como arquivo referenciado.
                # commonpath: `../` não pode validar arquivo fora do plugin.
                # (commonpath em vez de is_relative_to — este exige Python ≥ 3.9.)
                raiz_plugin = plugin.resolve()
                dentro = (
                    os.path.commonpath([str(alvo), str(raiz_plugin)]) == str(raiz_plugin)
                )
                if not dentro or not alvo.is_file():
                    motivo = "escapa do plugin" if not dentro else "não existe"
                    problemas.append(
                        (rel, num, f"${{CLAUDE_PLUGIN_ROOT}}/{ref} {motivo}")
                    )

    # A versão vive em 3 lugares e eles divergem calados: o manifesto é a fonte,
    # o README anuncia e o MEMORY.md orienta quem retoma. Já desatualizou duas
    # vezes — quem lê o índice primeiro parte de premissa velha.
    #
    # A checagem é ANCORADA no lugar que anuncia, não no arquivo inteiro (mesma
    # família de defeito do guarda de eixo): um README que cite a versão nova só
    # numa linha de changelog, com o bloco `## Status` ainda na anterior, passava
    # por `versao not in txt` — e o `## Status` é justamente o que se lê para
    # saber o que o produto é hoje. Onde a âncora não existir, cai para o arquivo
    # inteiro com a mensagem antiga, para não travar projeto de layout diferente.
    manifesto = plugin / ".claude-plugin" / "plugin.json"
    versao = json.loads(manifesto.read_text(encoding="utf-8")).get("version")
    ANCORAS_VERSAO = {
        "README": ("## Status", lambda txt: secao_unica(txt, "## Status")),
        "MEMORY.md": (
            "linha `**Versão:**`",
            lambda txt: _linha_unica(txt, "**Versão:**"),
        ),
    }
    for arq, rotulo in ((raiz / "README.md", "README"), (raiz / "memory" / "MEMORY.md", "MEMORY.md")):
        if not arq.exists():
            continue
        txt = arq.read_text(encoding="utf-8")
        if not re.search(r"\b\d+\.\d+\.\d+\b", txt):
            continue
        nome_ancora, extrair = ANCORAS_VERSAO[rotulo]
        trecho, estado = extrair(txt)
        if estado.startswith("duplicado"):
            # Duas âncoras = duas verdades. Validar qualquer uma delas (ou as
            # duas juntas) deixa passar a que o leitor vê primeiro estando velha.
            problemas.append(
                (
                    arq.relative_to(raiz),
                    0,
                    f"{rotulo} tem {estado.split(':')[1]}× {nome_ancora} — qual anuncia "
                    "a versão fica ambíguo; deixe só uma",
                )
            )
            continue
        # Sem âncora, cai para o arquivo inteiro: projeto de layout diferente não
        # trava, e a mensagem diz onde procurou.
        alvo, onde = (trecho, nome_ancora) if estado == "ok" else (txt, "arquivo")
        if versao not in alvo:
            achadas = sorted(set(re.findall(r"\b\d+\.\d+\.\d+\b", alvo)))[:3]
            problemas.append(
                (
                    arq.relative_to(raiz),
                    0,
                    f"{rotulo} não cita a versão atual {versao} em {onde} (achei {achadas})",
                )
            )

    # O marketplace.json declara a versão do plugin no catálogo e ficou em
    # 0.4.0 por sete releases sem ninguém notar — é o quarto lugar onde a
    # versão vive, e o único que o lint não olhava.
    mkt = raiz / ".claude-plugin" / "marketplace.json"
    if mkt.exists():
        for entrada in json.loads(mkt.read_text(encoding="utf-8")).get("plugins", []):
            if entrada.get("name") == "orq" and entrada.get("version") != versao:
                problemas.append(
                    (
                        mkt.relative_to(raiz),
                        0,
                        f"marketplace.json declara {entrada.get('version')}, "
                        f"manifesto diz {versao}",
                    )
                )

    # ── AGENTS.md e CLAUDE.md têm que ser byte-idênticos ────────────────────
    # Decisão do dono (T-026, 2026-08-04): não existe mais "portátil" nem
    # "ponteiro" — o que se instala noutro host é o mesmo conteúdo, e
    # identidade vira gate mecânico em vez de "dever de sincronizar" (o
    # defeito que já custou cinco rodadas de painel nesta semana).
    claude_md = raiz / "CLAUDE.md"
    agents_md = raiz / "AGENTS.md"
    claude_existe, agents_existe = claude_md.exists(), agents_md.exists()
    if claude_existe and agents_existe:
        if claude_md.read_bytes() != agents_md.read_bytes():
            problemas.append(
                (
                    Path("AGENTS.md"),
                    0,
                    "diverge de CLAUDE.md — os dois têm que ser byte-idênticos "
                    "(`diff CLAUDE.md AGENTS.md` tem que voltar vazio)",
                )
            )
    elif claude_existe != agents_existe:
        # Um dos dois sumiu (ex.: apagado à mão) e o outro ficou — isso não é
        # "não diverge", é o mesmo silêncio que o guarda acima existe pra
        # eliminar: trocou "divergiu" por "sumiu" sem avisar ninguém.
        faltante, existente = (
            ("AGENTS.md", "CLAUDE.md") if claude_existe else ("CLAUDE.md", "AGENTS.md")
        )
        problemas.append(
            (
                Path(faltante),
                0,
                f"não existe, mas {existente} existe — os dois têm que existir e ser "
                "byte-idênticos (`diff CLAUDE.md AGENTS.md` tem que voltar vazio)",
            )
        )

    # ── Template do elenco host-aware (T-041) ──────────────────────────────
    # Os consumidores leem estas headings literalmente. Se um consumidor
    # exige a seção, o template usado pelo init tem que gerá-la; do contrário
    # projeto novo nasce apontando para o vazio e improvisa o executor.
    elenco_cmd = plugin / "commands" / "elenco.md"
    consumidores_elenco = [
        plugin / "skills" / "orq" / "SKILL.md",
        plugin / "commands" / "plan-next.md",
        plugin / "commands" / "implement-next.md",
        plugin / "commands" / "revisar.md",
    ]
    txt_elenco = elenco_cmd.read_text(encoding="utf-8")
    try:
        template_elenco = txt_elenco.split("## Modelo do arquivo", 1)[1]
        template_elenco = template_elenco.split("```markdown", 1)[1].split("```", 1)[0]
    except IndexError:
        template_elenco = ""
        problemas.append(
            (
                elenco_cmd.relative_to(raiz),
                0,
                "não contém bloco ```markdown canônico em ## Modelo do arquivo",
            )
        )
    for heading in ("## Matriz de invocação", "## Times por host"):
        exigida = any(
            heading in arq.read_text(encoding="utf-8") for arq in consumidores_elenco
        )
        if exigida and secao_unica(template_elenco, heading)[1] != "ok":
            problemas.append(
                (
                    elenco_cmd.relative_to(raiz),
                    0,
                    f"template não gera {heading}, exigida pelos consumidores",
                )
            )

    # ── Interface do Codex (T-041) ─────────────────────────────────────────
    # O guarda antigo procurava apenas "Codex" e "/skills" em qualquer lugar
    # do arquivo. Uma nota histórica solta satisfazia a condição mesmo se o
    # contrato operacional tivesse sido apagado. Estes fragmentos são o
    # contrato mínimo, no arquivo que realmente governa cada comportamento.
    opus_runner = plugin / "scripts" / "run-opus-reviewer.py"
    opus_runner_test = plugin / "scripts" / "test_run_opus_reviewer.py"
    for arq in (opus_runner, opus_runner_test):
        if not arq.is_file():
            problemas.append((arq.relative_to(raiz), 0, "runner/teste obrigatório do Opus não existe"))

    CONTRATOS_CODEX = {
        plugin / "skills" / "orq" / "SKILL.md": (
            "No Codex, a interface oficial é linguagem natural ou `/skills`",
            "`ORQ_PACKAGE_ROOT`",
            ".claude-plugin/plugin.json",
            "ORQ_PACKAGE_ROOT/commands/elenco.md",
        ),
        plugin / "commands" / "instalar.md": ("`/plugins`", "`/skills`"),
        raiz / "README.md": (
            "**Codex:** linguagem natural ou `/skills`",
            "não cria `/orq:*`",
        ),
        plugin / "commands" / "plan-next.md": (
            "`ORQ_PACKAGE_ROOT/commands/elenco.md`",
            "`codex exec` é o caminho padrão",
        ),
        plugin / "commands" / "implement-next.md": (
            "`ORQ_PACKAGE_ROOT/commands/elenco.md`",
            "`codex exec` é o caminho padrão",
        ),
        plugin / "commands" / "revisar.md": (
            "O revisor é **um só, e sempre do vendor oposto ao host**",
            "No host Codex, o titular é o Opus 5 pelo runner",
            "política habilitada, não capacidade comprovada",
            "Nunca substitua o titular por um revisor do mesmo vendor do host",
            "sem revisão independente por restrição de dados",
            "REVISÃO DEGRADADA",
            "Sem elenco, vale o padrão de fábrica: reviewer único",
            "`--rapido` **não troca de revisor**",
            "run-opus-reviewer.py",
            "16 KiB",
            "Nunca corte bytes nem",
            "OPUS_EXIT",
            "OPUS_STARTED",
            "timeout de 240s",
            "BRIEFING_TOO_LARGE",
            "OPUS_EMPTY_RESULT",
            "**no stderr**",
        ),
        elenco_cmd: (
            "Host Codex: `codex exec` é obrigatório",
            "política habilitada, não capacidade comprovada",
            "a independência ganha do domínio, sempre",
            "| reviewer | `opus` (exigir comprovação de que o alias resolve para Opus 5)",
            "| reviewer | `gpt-5.6-sol@xhigh` |",
            "run-opus-reviewer.py",
        ),
        opus_runner: (
            "BRIEFING_TOO_LARGE",
            "OPUS_TIMEOUT",
            "OPUS_MODEL_MISMATCH",
            "OPUS_STARTED",
            "claude-opus-5",
            "OPUS_MODEL_USAGE",
            "DEFAULT_TIMEOUT_SECONDS = 240.0",
            "input=briefing",
            "OPUS_EMPTY_RESULT",
            "file=sys.stderr",
            '"--output-format"',
            '"json"',
        ),
    }
    for arq, fragmentos in CONTRATOS_CODEX.items():
        if not arq.is_file():
            continue
        txt = arq.read_text(encoding="utf-8")
        for fragmento in fragmentos:
            if fragmento not in txt:
                problemas.append(
                    (
                        arq.relative_to(raiz),
                        0,
                        f"contrato Codex ausente: {fragmento}",
                    )
                )

    # O reviewer é ÚNICO e sempre do vendor OPOSTO ao host (T-051). Contar a
    # linha no template inteiro NÃO prova a regra: trocar as duas linhas de
    # lugar entre `### Host Claude` e `### Host Codex` mantém a contagem 1/1 e
    # deixa cada host revisado pelo PRÓPRIO vendor — exatamente a perda de
    # independência que a regra do dono existe para impedir, com lint verde.
    # Por isso o guarda ancora na seção: recorta a tabela daquele host e exige
    # (a) a linha do vendor oposto presente 1× e (b) a linha do OUTRO host
    # ausente. A linha do host Codex carrega junto a comprovação do alias
    # Opus 5, que continua obrigatória.
    REVIEWER_CLAUDE = "| reviewer | `gpt-5.6-sol@xhigh` |"
    REVIEWER_CODEX = "| reviewer | `opus` (exigir comprovação de que o alias resolve para Opus 5)"
    REVIEWER_POR_HOST = {
        "### Host Claude": (REVIEWER_CLAUDE, REVIEWER_CODEX, "titular OpenAI"),
        "### Host Codex": (REVIEWER_CODEX, REVIEWER_CLAUDE, "titular Anthropic, alias comprovado"),
    }
    for heading, (esperada, proibida, papel) in REVIEWER_POR_HOST.items():
        secao, estado = secao_unica(template_elenco, heading)
        if estado != "ok":
            problemas.append(
                (
                    elenco_cmd.relative_to(raiz),
                    0,
                    f"template não gera exatamente 1 tabela `{heading}` ({estado}) — "
                    "heading tem que ser linha inteira, exata e única",
                )
            )
            continue
        for secao in (secao,):
            if secao.count(esperada) != 1:
                problemas.append(
                    (
                        elenco_cmd.relative_to(raiz),
                        0,
                        f"`{heading}` precisa da linha do reviewer oposto ({papel}) 1×",
                    )
                )
            if proibida in secao:
                problemas.append(
                    (
                        elenco_cmd.relative_to(raiz),
                        0,
                        f"`{heading}` traz o reviewer do outro host — vendor do host "
                        "revisando a si mesmo",
                    )
                )

    # Os dois eixos do elenco (T-051) têm que existir em CADA tabela: a trilha
    # (interface/sistema) escolhe o vendor de quem PENSA, a faixa
    # (pesada/normal/leve) escolhe o degrau de quem ESCREVE.
    #
    # A comparação é por CONJUNTO E MULTIPLICIDADE das primeiras células, não
    # por "o nome aparece na seção". É a terceira encarnação do mesmo defeito
    # (heading por substring; papel sobrevivendo nos presets; papel citado numa
    # nota fora da tabela): guarda que confirma que um texto existe em algum
    # lugar quando a regra exige que ele exista NUM lugar. Aqui: papel obrigatório
    # exatamente 1×, nenhum papel intruso, `manager` só na tabela de host.
    PAPEIS_EIXO = (
        "planner·interface",
        "planner·sistema",
        "implementer·pesada",
        "implementer·normal",
        "implementer·leve",
    )
    PAPEIS_FIXOS = ("reviewer", "docs", "scout")
    ESPERADO_HOST = ("manager",) + PAPEIS_EIXO + PAPEIS_FIXOS
    ESPERADO_PRESET = PAPEIS_EIXO + PAPEIS_FIXOS
    TABELAS_DE_PAPEL = {
        "### Host Claude": ("tabela de host", ESPERADO_HOST),
        "### Host Codex": ("tabela de host", ESPERADO_HOST),
        "### `padrao` — o time titular": ("preset", ESPERADO_PRESET),
        "### `economia` — crédito curto": ("preset", ESPERADO_PRESET),
    }
    for heading, (especie, esperado) in TABELAS_DE_PAPEL.items():
        secao, estado = secao_unica(template_elenco, heading)
        if estado != "ok":
            problemas.append(
                (
                    elenco_cmd.relative_to(raiz),
                    0,
                    f"template não gera exatamente 1 {especie} `{heading}` ({estado})",
                )
            )
            continue
        achados = papeis_da_tabela(secao)
        contagem = Counter(achados)
        for papel in esperado:
            n = contagem.get(papel, 0)
            if n != 1:
                falta = "não é linha da tabela" if n == 0 else f"aparece {n}× na tabela"
                problemas.append(
                    (
                        elenco_cmd.relative_to(raiz),
                        0,
                        f"`{heading}`: papel `{papel}` {falta} — a {especie} tem que "
                        f"declarar cada papel exatamente 1×",
                    )
                )
        for intruso in sorted(set(achados) - set(esperado)):
            problemas.append(
                (
                    elenco_cmd.relative_to(raiz),
                    0,
                    f"`{heading}`: papel `{intruso}` não pertence a esta {especie} "
                    f"(esperados: {', '.join(esperado)})",
                )
            )

    # ── Host aposentado (T-051) ────────────────────────────────────────────
    # O suporte ao terceiro host saiu do produto na 0.24.0. O modo de falha nº
    # 1 aqui é textual: sobrar instrução VIVA mandando invocar um host que não
    # existe mais — foi assim que `/orquestra:*` sobreviveu a três releases.
    #
    # Varre `orq/` INTEIRO (proibição total) e mais os três arquivos da raiz que
    # governam modelos: README.md, CLAUDE.md e AGENTS.md. Excluir esses três era
    # buraco real — CLAUDE.md/AGENTS.md são instrução viva lida por todo modelo
    # que abre o repo, e reintroduzir ali "use <host aposentado> como revisor"
    # passava batido pelo guarda de identidade (que só compara um com o outro) e
    # por este.
    #
    # Nos três da raiz a proibição não pode ser total: eles contam a história
    # das releases, e o próprio README precisa poder dizer que o host FOI
    # REMOVIDO. Daí a allowlist estrutural: a linha histórica que existe hoje é
    # permitida no texto exato; qualquer linha nova é reprovada. É deliberado
    # que reflow de parágrafo derrube o lint — a falha é barulhenta e a correção
    # é reconferir a linha, o oposto do silêncio que o guarda existe para matar.
    HOST_APOSENTADO_RE = re.compile(r"kimi|moonshot", re.IGNORECASE)
    HISTORICO_PERMITIDO = {
        "README.md": frozenset({
            "ao antigo terceiro host (Moonshot) **foi removido**, com guarda de regressão no lint.",
        }),
        "CLAUDE.md": frozenset({
            "Este erro já aconteceu aqui: a feature do Kimi (0.8.0) foi implementada direto, sem plano e sem",
        }),
    }
    # AGENTS.md é byte-idêntico ao CLAUDE.md por gate mecânico: mesma allowlist,
    # escrita uma vez só — duas listas divergiriam no primeiro descuido.
    HISTORICO_PERMITIDO["AGENTS.md"] = HISTORICO_PERMITIDO["CLAUDE.md"]

    este_script = Path(__file__).resolve()
    alvos = [a for a in plugin.rglob("*") if a.is_file()]
    alvos += [raiz / nome for nome in ("README.md", "CLAUDE.md", "AGENTS.md")]
    for arq in alvos:
        if not arq.is_file() or arq.resolve() == este_script:
            continue
        if DIRS_IGNORADOS & set(arq.relative_to(raiz).parts):
            continue
        try:
            conteudo = arq.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        permitidas = HISTORICO_PERMITIDO.get(arq.name, frozenset())
        for num, linha in enumerate(conteudo.splitlines(), 1):
            if not HOST_APOSENTADO_RE.search(linha):
                continue
            if linha.strip() in permitidas:
                continue
            problemas.append(
                (
                    arq.relative_to(raiz),
                    num,
                    "cita o host aposentado na 0.24.0 — o suporte saiu do produto "
                    "(linha histórica nova? entre na allowlist do lint, com revisão)",
                )
            )

    # Consumers não repetem modelos nem dependem da variável exclusiva do
    # Claude: ambos causam drift quando o elenco ou o host muda.
    for arq in (plugin / "commands" / "plan-next.md", plugin / "commands" / "implement-next.md"):
        txt = arq.read_text(encoding="utf-8")
        for proibido in (
            "${CLAUDE_PLUGIN_ROOT}/commands/elenco.md",
            "gpt-5.6-sol@ultra",
            "gpt-5.6-terra@xhigh",
        ):
            if proibido in txt:
                problemas.append(
                    (
                        arq.relative_to(raiz),
                        0,
                        f"redeclara contrato do elenco/host: {proibido}",
                    )
                )

    # ── Statusline: tripwire dos três escopos (T-036) ───────────────────────
    # A causa raiz do T-036 foi o `init.md` gravar `statusLine` checando só o
    # escopo do projeto — settings de projeto vencem o global por
    # precedência, então a omissão vira sobrescrita silenciosa mesmo com diff
    # aditivo. O gate é textual: todo arquivo de orq/ que se propõe a
    # ESCREVER a chave (identificado pela forma JSON `"statusLine":`, que só
    # aparece em template de settings a gravar — não em prosa citando o
    # identificador) precisa nomear os três escopos onde ela pode morar,
    # senão a omissão do bug original volta a ser possível sem o lint notar.
    # Mira só quem grava, de propósito: um arquivo que cita `statusLine` sem
    # gravar nada (ex.: a skill listando primitivas por comando) não decide
    # onde a chave mora, e exigir os três escopos ali seria falso positivo.
    #
    # Gatilho: forma JSON de escrita ('"statusLine":') OU forma de atribuição
    # jq ('.statusLine = ...'/'.statusLine |= ...', usadas em filtros tipo
    # `jq '.statusLine = {...}'`) OU forma de merge por adição de objeto
    # ('{statusLine: ...}', usada em `jq '. + {statusLine: {...}}'`) — as
    # versões anteriores só cobriam a primeira forma (depois, `=`/`|=`); o
    # achado 6 do painel (T-036, rodada 2) provou que `jq '. + {statusLine:
    # …}'`, a segunda forma canônica de merge seguro em jq, escapava do lint
    # gravando a chave de verdade.
    # Probes (documentação viva do que o guarda cobre — teste ao mexer aqui):
    #   dispara     — '"statusLine": {...}' · jq '.statusLine = {"type":...}'
    #                 · jq '.statusLine |= {...}' · jq '. + {statusLine: {...}}'
    #   não dispara — '.statusLine // empty'  · "a chave `statusLine`" em prosa
    # Limitação conhecida: o gatilho é textual/sintático, não um parser de
    # comando de verdade. Reescrever o passo em prosa livre, sem nenhuma das
    # formas acima, desarma o guarda — não há como cobrir toda paráfrase
    # possível sem executar o comando descrito.
    GRAVA_STATUSLINE_RE = re.compile(r'"statusLine"\s*:|\.statusLine\s*(\|=|=)(?!=)|\{\s*statusLine\s*:')
    # Escopo do projeto (".claude/settings.json") é SUBSTRING do escopo do
    # usuário ("~/.claude/settings.json") — um `in txt` ingênuo dava falso
    # negativo: um arquivo que cite só o escopo usuário passava a checagem do
    # escopo projeto de graça (o "~/.claude/settings.json" citado já contém a
    # substring). Casa por regex com fronteira, negando os dois prefixos que
    # denotam o HOME (o achado 6 também provou que "$HOME/.claude/settings.json"
    # — forma equivalente a "~/…" — colava como escopo de projeto com um único
    # lookbehind negativo): `~/` e `$HOME/`. Os outros dois escopos não são
    # substring um do outro e seguem checados por substring simples.
    ESCOPO_PROJETO_RE = re.compile(r"(?<!~/)(?<!\$HOME/)\.claude/settings\.json")
    ESCOPOS_STATUSLINE = ("settings.local.json", ".claude/settings.json", "~/.claude/settings.json")
    for arq in plugin.rglob("*.md"):
        if DIRS_IGNORADOS & set(arq.relative_to(raiz).parts):
            continue
        txt = arq.read_text(encoding="utf-8")
        if GRAVA_STATUSLINE_RE.search(txt):
            faltando = [
                e
                for e in ESCOPOS_STATUSLINE
                if not (ESCOPO_PROJETO_RE.search(txt) if e == ".claude/settings.json" else e in txt)
            ]
            if faltando:
                problemas.append(
                    (
                        arq.relative_to(raiz),
                        0,
                        f"grava statusLine mas não menciona o(s) escopo(s) {faltando} — "
                        "reabre o risco do T-036 (settings de projeto vencem o global)",
                    )
                )

    # ── Cache stale por edição sem bump ─────────────────────────────────────
    # O cache do plugin é indexado por versão (~/.claude/plugins/cache/
    # orquestra/orq/<versão>/): editar orq/ sem bumpar NÃO muda o que roda e
    # nenhum comando acusa — `claude plugin list` segue dizendo que está tudo
    # certo (aconteceu no 5b75296). Se a versão do manifesto JÁ existe no
    # cache desta máquina com conteúdo diferente do repo, o dono está editando
    # uma versão já publicada: o release seguinte não acontece sem bump.
    # Onde o cache não existe (CI, máquina de terceiro), silencia de propósito.
    # Comparação por BYTES: a cópia do cache tem mtime diferente e um
    # filecmp raso acusaria divergência falsa em release limpo.
    cache = Path.home() / ".claude" / "plugins" / "cache" / "orquestra" / "orq" / versao
    if cache.is_dir():
        # .orphaned_at é escrito pela CLI no cache quando uma versão deixa de
        # ser a instalada — existe em 8 diretórios de cache do orq nesta
        # máquina. Sem ignorá-lo, fazer checkout de uma tag antiga para
        # investigar um bug acusa "edição sem bump" que nunca houve.
        IGNORAR = {".DS_Store", ".orphaned_at"}

        def _arquivos(base: Path):
            return {
                p.relative_to(base)
                for p in base.rglob("*")
                if p.is_file() and p.name not in IGNORAR
            }

        no_cache, no_repo = _arquivos(cache), _arquivos(plugin)
        divergentes = sorted(str(p) for p in no_cache ^ no_repo) or sorted(
            str(p)
            for p in no_cache & no_repo
            if (cache / p).read_bytes() != (plugin / p).read_bytes()
        )
        if divergentes:
            problemas.append(
                (
                    Path("orq"),
                    0,
                    f"versão {versao} já existe no cache com conteúdo diferente "
                    f"(ex.: {divergentes[0]}) — o que roda não é o que você "
                    f"editou. Antes do release: bumpe a versão; se já bumpou e "
                    f"instalou para testar, repita o `plugin update`",
                )
            )

    if problemas:
        print(f"✗ {len(problemas)} referência(s) quebrada(s):\n")
        for rel, num, msg in problemas:
            print(f"  {rel}:{num}  {msg}")
        print("\nRenomeou algo? Faça grep do nome antigo no orq/ inteiro.")
        return 1

    total = sum(len(v) for v in conhecidos.values())
    print(f"✓ coerência interna ok — {total} nomes conferidos, memory/ ignorado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
