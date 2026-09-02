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

# O lint importa o comparador antes de comparar fonte e cache. Sem esta guarda,
# Python pode criar scripts/__pycache__ no próprio lado comparado e produzir um
# falso vermelho autoinfligido em runtimes cujo pycache_prefix é local.
sys.dont_write_bytecode = True

try:
    from orq.scripts.verify_installed_cache import find_installation_divergences
except ModuleNotFoundError:  # execução direta a partir do cache instalado
    from verify_installed_cache import find_installation_divergences

# `memory/` é deliberadamente excluído: o log é append-only e o gotchas.md citam
# nomes de comandos QUE DEIXARAM DE EXISTIR, de propósito, ao descrever bugs
# passados. Varrer memory/ produz falso positivo em todo checkpoint — e lint que
# grita à toa é lint que o dono desliga.
DIRS_IGNORADOS = {"memory", ".git", "node_modules"}

# `memory/` é pulado inteiro por um motivo bom (log append-only e threads citam
# nomes extintos ao descrever o passado) — mas DUAS páginas ali não são registro
# histórico: são instrução viva, dizem como o sistema funciona e como publicar
# HOJE. Foi exatamente aí que a reconciliação da 0.25.0 deixou três contradições
# que passaram nos dois gates: `PAINEL PARCIAL` sobrevivendo ao revisor único,
# `diff -rq` sobrevivendo ao verificador, e a quinta fonte de versão que o T-052
# aboliu. Nominal de propósito: nada de varrer `memory/` por padrão, nada de
# afrouxar o guarda para caber — se uma página nova virar instrução viva, ela
# entra aqui com revisão.
PAGINAS_VIVAS_FORA_DO_PLUGIN = (
    "memory/wiki/distribuicao.md",
    "memory/wiki/arquitetura.md",
)

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


def validate_codex_consultive_language(
    raiz: Path,
    plugin: Path,
) -> list[tuple[Path, int, str]]:
    """Rejeita instruções vivas que transformem o guardião Codex em bloqueio."""

    def atualiza_referente_checkpoint(clausula: str, anterior: bool) -> bool:
        """Mantém elipse incidental, mas deixa o sujeito explícito mais recente vencer."""

        def nucleo_e_checkpoint(sintagma: str) -> bool:
            sem_adjunto = re.split(
                r"\b(?:do|da|dos|das|de|no|na|nos|nas|em|com|sem|para)\b",
                sintagma,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0]
            return bool(re.search(r"\bcheckpoint\b", sem_adjunto, re.IGNORECASE))

        sem_host = re.sub(
            r"^\s*(?:(?:no|para\s+o)\s+)?(?:Codex|Claude)\s*[:,]?\s*",
            "",
            clausula,
            flags=re.IGNORECASE,
        )
        candidatos: list[tuple[int, bool]] = []
        sujeitos = list(
            re.finditer(
                r"(?:^|\b(?:e|mas|porém|contudo|entretanto|enquanto)\b)\s*"
                r"(?P<sujeito>(?:(?:o|a|os|as)\s+)?"
                r"(?:`[^`]+`|[\wÀ-ÿ-]+(?:\s+[\wÀ-ÿ-]+){0,3}))\s+"
                r"(?:é|são|foi|está|fica|permanece|será|deve|precisa)\b",
                sem_host,
                re.IGNORECASE,
            )
        )
        candidatos.extend(
            (
                sujeito.start("sujeito"),
                nucleo_e_checkpoint(sujeito.group("sujeito")),
            )
            for sujeito in sujeitos
        )
        for acao in re.finditer(
            r"\b(?:faça|execute|inicie|realize|rode|crie|gere|conclua|revise|"
            r"valide|atualize|salve|envie)\s+"
            r"(?P<objeto>(?:(?:o|a|os|as|um|uma)\s+)?"
            r"(?:`[^`]+`|[\wÀ-ÿ-]+(?:\s+"
            r"(?!(?:e|ou|antes|depois|após|sem|com|para|do|da|de|no|na|em)\b)"
            r"[\wÀ-ÿ-]+){0,2}))",
            sem_host,
            re.IGNORECASE,
        ):
            candidatos.append(
                (
                    acao.start("objeto"),
                    nucleo_e_checkpoint(acao.group("objeto")),
                )
            )
        if candidatos:
            return max(candidatos, key=lambda item: item[0])[1]
        if "checkpoint" in sem_host.casefold():
            return True
        return anterior

    padroes = (
        (
            re.compile(
                r"(?:"
                r"(?:até|sem|antes|depois|após).{0,45}"
                r"(?:checkpoint|concluir\s+o\s+checkpoint).{0,90}"
                r"(?:trabalho|pedido|sessão).{0,30}"
                r"(?:fica|está|permanece|será)\s+"
                r"(?:bloquead|impedid|interrompid|recusad)\w*|"
                r"(?:trabalho|pedido|sessão).{0,30}"
                r"(?:fica|está|permanece|será)\s+"
                r"(?:bloquead|impedid|interrompid|recusad)\w*.{0,60}"
                r"(?:até|sem|antes|depois|após).{0,45}"
                r"(?:checkpoint|concluir\s+o\s+checkpoint)"
                r")",
                re.IGNORECASE | re.DOTALL,
            ),
            "contrato Codex inválido: trabalho bloqueado",
            re.compile(
                r"\b(?:não|nada|nenhum(?:a)?|sem)\b.{0,40}"
                r"\b(?:bloquead|impedid|interrompid|recusad)",
                re.IGNORECASE | re.DOTALL,
            ),
        ),
        (
            re.compile(
                r"(?:"
                r"\b(?:pare|interrompa|suspenda)\s+(?:o\s+)?"
                r"(?:trabalho|pedido|sessão).{0,80}"
                r"(?:checkpoint|concluir\s+o\s+checkpoint)|"
                r"(?:checkpoint|concluir\s+o\s+checkpoint).{0,80}"
                r"\b(?:pare|interrompa|suspenda)\s+(?:o\s+)?"
                r"(?:trabalho|pedido|sessão)|"
                r"\bnão\s+(?:continue|prossiga|trabalhe)\b.{0,80}"
                r"(?:checkpoint|concluir\s+o\s+checkpoint)"
                r")",
                re.IGNORECASE | re.DOTALL,
            ),
            "contrato Codex inválido: trabalho interrompido",
            re.compile(
                r"\b(?:não|nunca|jamais)\s+(?:pare|interrompa|suspenda)\b",
                re.IGNORECASE,
            ),
        ),
        (
            re.compile(
                r"(?:"
                r"(?:deve(?:-se)?|precisa(?:-se)?|necessár\w*|exigid\w*|"
                r"requisit\w*|condiç\w*).{0,90}checkpoint.{0,90}"
                r"(?:continu\w*|pross\w*|trabalh\w*|pedido)|"
                r"checkpoint.{0,90}(?:deve(?:-se)?|precisa(?:-se)?|necessár\w*|"
                r"exigid\w*|requisit\w*|condiç\w*).{0,90}"
                r"(?:continu\w*|pross\w*|trabalh\w*|pedido)|"
                r"\bsó\s+(?:continue|prossiga|trabalhe).{0,90}checkpoint|"
                r"\b(?:só|somente)\s+(?:é\s+)?permitid\w*.{0,90}"
                r"(?:continu\w*|pross\w*|trabalh\w*).{0,90}checkpoint|"
                r"checkpoint.{0,90}(?:antes\s+de|pré-condiç\w*).{0,90}"
                r"(?:continu\w*|pross\w*|trabalh\w*|pedido)"
                r")",
                re.IGNORECASE | re.DOTALL,
            ),
            "contrato Codex inválido: continuidade condicionada ao checkpoint",
            re.compile(
                r"\b(?:não|nunca|jamais)\b.{0,45}"
                r"(?:deve|precisa|necessár|exigid|requisit|condiç|só)",
                re.IGNORECASE | re.DOTALL,
            ),
        ),
    )

    problemas: list[tuple[Path, int, str]] = []
    for arq in arquivos_a_varrer(raiz, plugin):
        if not arq.is_file():
            continue
        texto = arq.read_text(encoding="utf-8")
        headings: list[tuple[int, str]] = []
        heading_matches = list(re.finditer(r"(?m)^(#{1,6})\s+(.+)$", texto))
        for bloco_match in re.finditer(
            r"(?s)(?:\A|\n[ \t]*\n)(.*?)(?=\n[ \t]*\n|\Z)",
            texto,
        ):
            bloco = bloco_match.group(1)
            inicio = bloco_match.start(1)
            headings.clear()
            for heading in heading_matches:
                if heading.start() >= inicio:
                    break
                nivel = len(heading.group(1))
                headings[:] = [item for item in headings if item[0] < nivel]
                headings.append((nivel, heading.group(2)))
            contexto_codex = "codex" in bloco.casefold() or any(
                "codex" in titulo.casefold() for _, titulo in headings
            )
            if not contexto_codex or "checkpoint" not in bloco.casefold():
                continue
            host_atual = (
                "codex"
                if any("codex" in titulo.casefold() for _, titulo in headings)
                else None
            )
            separadores = re.compile(
                r"[.!?;\n—]+|\b(?:mas|porém|contudo|entretanto)\b",
                re.IGNORECASE,
            )
            marcadores = list(separadores.finditer(bloco))
            for conector in re.finditer(
                r",|\b(?:e|enquanto)\b",
                bloco,
                re.IGNORECASE,
            ):
                esquerda = bloco[max(0, conector.start() - 240) : conector.start()]
                direita = bloco[conector.end() :]
                regra_rotulada_antes = re.search(
                    r"(?:\b(?:Codex|Claude)\s*:|"
                    r"\b(?:no|para\s+o)\s+(?:Codex|Claude)\b)[^.!?;—\n]*$",
                    esquerda,
                    re.IGNORECASE,
                )
                regra_rotulada_depois = re.match(
                    r"\s*(?:(?:Codex|Claude)\s*:|"
                    r"(?:no|para\s+o)\s+(?:Codex|Claude)\b)",
                    direita,
                    re.IGNORECASE,
                )
                sujeito_compartilhado = re.search(
                    r"\b(?:Codex|Claude)\s*$",
                    esquerda,
                    re.IGNORECASE,
                ) and re.match(
                    r"\s*(?:(?:no|o|para\s+o)\s+)?(?:Codex|Claude)\b\s*[:,]",
                    direita,
                    re.IGNORECASE,
                )
                if conector.group(0) == ",":
                    if regra_rotulada_antes and regra_rotulada_depois:
                        marcadores.append(conector)
                elif not sujeito_compartilhado and (
                    (regra_rotulada_antes and regra_rotulada_depois)
                    or (
                        "checkpoint" in esquerda.casefold()
                        and "checkpoint" in direita[:240].casefold()
                    )
                ):
                    marcadores.append(conector)
            marcadores.sort(key=lambda item: item.start())
            cursor = 0
            intervalos: list[tuple[int, int]] = []
            for separador in marcadores:
                intervalos.append((cursor, separador.start()))
                cursor = separador.end()
            intervalos.append((cursor, len(bloco)))
            referente_checkpoint = False
            for inicio_clausula, fim_clausula in intervalos:
                clausula = bloco[inicio_clausula:fim_clausula]
                compartilhado = re.match(
                    r"\s*(?:(?:no|para\s+o)\s+)?(Codex|Claude)\s+"
                    r"(?:e/ou|e|ou)\s+"
                    r"(?:(?:no|o|para\s+o)\s+)?(Codex|Claude)\b",
                    clausula,
                    re.IGNORECASE,
                )
                rotulado = re.match(
                    r"\s*(?:(?:no|para\s+o)\s+)?(Codex|Claude)\b",
                    clausula,
                    re.IGNORECASE,
                )
                if compartilhado:
                    citados = {
                        compartilhado.group(1).casefold(),
                        compartilhado.group(2).casefold(),
                    }
                    host_atual = "codex" if "codex" in citados else "claude"
                elif rotulado:
                    host_atual = rotulado.group(1).casefold()
                retoma_checkpoint = referente_checkpoint
                referente_checkpoint = atualiza_referente_checkpoint(
                    clausula,
                    referente_checkpoint,
                )
                if host_atual != "codex":
                    continue
                clausula_padroes = clausula
                if retoma_checkpoint:
                    clausula_padroes = re.sub(
                        r"\b(?:concluí-lo|fazê-lo)\b|"
                        r"\bconcluir\b(?=\s*[,.;:!?]|\s*$)",
                        "checkpoint",
                        clausula_padroes,
                        flags=re.IGNORECASE,
                    )
                if "checkpoint" in clausula.casefold():
                    for obrigatorio in re.finditer(
                        r"\bobrigat\w*\b",
                        clausula,
                        re.IGNORECASE,
                    ):
                        prefixo_completo = clausula[: obrigatorio.start()]
                        conectores_anteriores = list(
                            re.finditer(
                                r"\b(?:e|enquanto|mas|porém|contudo|entretanto)\b",
                                prefixo_completo,
                                re.IGNORECASE,
                            )
                        )
                        inicio_escopo = (
                            conectores_anteriores[-1].end()
                            if conectores_anteriores
                            else 0
                        )
                        escopo_sujeito = prefixo_completo[inicio_escopo:]
                        candidato_sujeito = re.search(
                            r"(?P<sujeito>.+?)\s+(?:é|são|será|deve|precisa)\s*$",
                            escopo_sujeito,
                            re.IGNORECASE,
                        )
                        sujeito_explicito_alheio = False
                        if (
                            "checkpoint" not in escopo_sujeito.casefold()
                            and candidato_sujeito
                        ):
                            sujeito = candidato_sujeito.group("sujeito").strip(" `*_\t")
                            sujeito = re.sub(
                                r"^(?:(?:no|para\s+o)\s+)?(?:Codex|Claude)\s*[:,]?\s*",
                                "",
                                sujeito,
                                flags=re.IGNORECASE,
                            )
                            sujeito = re.sub(
                                r"^(?:(?:em|no|na|nos|nas)\s+[\wÀ-ÿ-]+\s+)+",
                                "",
                                sujeito,
                                flags=re.IGNORECASE,
                            )
                            retomadas = {"isso", "isto", "essa regra", "esta regra"}
                            sujeito_explicito_alheio = bool(sujeito) and (
                                sujeito.casefold() not in retomadas
                            )
                        if sujeito_explicito_alheio:
                            continue
                        prefixo_obrigatorio = clausula[
                            max(0, obrigatorio.start() - 70) : obrigatorio.start()
                        ]
                        negado = re.search(
                            r"\b(?:não|nunca|jamais)\s+"
                            r"(?:(?:deve|deveria|deverá|ser|será|é|foi|pode)\s+){0,3}$",
                            prefixo_obrigatorio,
                            re.IGNORECASE,
                        )
                        if negado:
                            continue
                        posicao = inicio + inicio_clausula + obrigatorio.start()
                        linha = texto.count("\n", 0, posicao) + 1
                        problemas.append(
                            (
                                arq.relative_to(raiz),
                                linha,
                                "contrato Codex inválido: checkpoint obrigatório",
                            )
                        )
                for regex, mensagem, negacao in padroes:
                    if mensagem in {
                        "contrato Codex inválido: trabalho bloqueado",
                        "contrato Codex inválido: trabalho interrompido",
                    } and not re.search(
                        r"checkpoint|concluir\s+o\s+checkpoint",
                        clausula_padroes,
                        re.IGNORECASE,
                    ):
                        continue
                    for match in regex.finditer(clausula_padroes):
                        janela = clausula_padroes[
                            max(0, match.start() - 80) : min(len(clausula_padroes), match.end() + 50)
                        ]
                        if mensagem == "contrato Codex inválido: trabalho bloqueado":
                            narrativa_dono = re.search(
                                r"\b(?:explique|descreva|registre|documente|informe)\b.{0,80}"
                                r"\bpor\s+que\b.{0,80}"
                                r"(?P<bloqueio>(?:bloquead|impedid|interrompid|recusad)\w*)\s+"
                                r"(?:pelo|pela|por)\s+(?:(?:o|a)\s+)?dono\b",
                                janela,
                                re.IGNORECASE | re.DOTALL,
                            )
                            if narrativa_dono:
                                depois_explicador = janela[narrativa_dono.start() :]
                                relacoes_temporais = list(re.finditer(
                                    r"(?:até|sem|antes|depois|após).{0,45}"
                                    r"(?:checkpoint|concluir\s+o\s+checkpoint)",
                                    depois_explicador,
                                    re.IGNORECASE | re.DOTALL,
                                ))
                                bloqueio_relativo = (
                                    narrativa_dono.start("bloqueio")
                                    - narrativa_dono.start()
                                )
                                causa_checkpoint_depois = any(
                                    relacao.start() < bloqueio_relativo
                                    or not re.search(
                                        r"[\wÀ-ÿ]",
                                        depois_explicador[relacao.end() :],
                                        re.IGNORECASE,
                                    )
                                    for relacao in relacoes_temporais
                                )
                                if not causa_checkpoint_depois:
                                    continue
                        if negacao is not None and negacao.search(janela):
                            continue
                        prefixo = clausula_padroes[max(0, match.start() - 20) : match.start()]
                        if re.search(
                            r"\b(?:não|nunca|jamais)\s*$",
                            prefixo,
                            re.IGNORECASE,
                        ):
                            continue
                        posicao = inicio + inicio_clausula + match.start()
                        linha = texto.count("\n", 0, posicao) + 1
                        problemas.append((arq.relative_to(raiz), linha, mensagem))
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
    problemas.extend(validate_codex_consultive_language(raiz, plugin))

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
            "timeout de 600s",
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
            "DEFAULT_TIMEOUT_SECONDS = 600.0",
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
    alvos += [raiz / rel for rel in PAGINAS_VIVAS_FORA_DO_PLUGIN]
    for arq in alvos:
        if not arq.is_file() or arq.resolve() == este_script:
            continue
        rel = arq.relative_to(raiz)
        # As páginas vivas nominais entram apesar de morarem sob `memory/`.
        if (
            DIRS_IGNORADOS & set(rel.parts)
            and rel.as_posix() not in PAGINAS_VIVAS_FORA_DO_PLUGIN
        ):
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

    # ── Vocabulário extinto em instrução viva (T-052) ──────────────────────
    # Termo que descreve um mecanismo aposentado não é erro de estilo: ele
    # ENSINA o mecanismo aposentado. `PAINEL PARCIAL` manda "seguir com painel
    # incompleto" onde o contrato é parar; `diff -rq` reprova cache válido por
    # artefato instalado-only. Os dois sobreviveram à reconciliação em
    # `distribuicao.md`, contradizendo `revisar.md` e a própria página.
    #
    # A allowlist é estrutural, como a do host aposentado: a linha que NEGA o
    # termo é permitida no texto exato; qualquer linha nova reprova.
    VOCABULARIO_EXTINTO = (
        (
            "PAINEL PARCIAL",
            "vocabulário do painel — o contrato hoje é `REVISÃO DEGRADADA — sem "
            "parecer`, e o card não avança sozinho (ver `/orq:revisar`)",
        ),
        (
            "diff -rq",
            "comparação bruta reprova cache válido por artefato instalado-only "
            "(T-049) — a prova de instalação é `verify_installed_cache.py`",
        ),
    )
    NEGACOES_PERMITIDAS = frozenset({
        "com a causa real nomeada — nunca silêncio e **nunca `PAINEL PARCIAL`**, que é vocabulário da época do",
        "`verify_installed_cache.py` como qualquer outro arquivo do pacote — **não** o compare com `diff -rq`:",
    })
    superficies_vivas = [a for a in plugin.rglob("*.md") if a.is_file()]
    superficies_vivas += [raiz / nome for nome in ("README.md", "CLAUDE.md", "AGENTS.md")]
    superficies_vivas += [raiz / rel for rel in PAGINAS_VIVAS_FORA_DO_PLUGIN]
    for arq in superficies_vivas:
        if not arq.is_file():
            continue
        try:
            conteudo = arq.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for num, linha in enumerate(conteudo.splitlines(), 1):
            if linha.strip() in NEGACOES_PERMITIDAS:
                continue
            for termo, porque in VOCABULARIO_EXTINTO:
                if termo in linha:
                    problemas.append(
                        (arq.relative_to(raiz), num, f"`{termo}` em instrução viva: {porque}")
                    )
        # A versão tem QUATRO fontes. O teste de coordenação é guarda derivada,
        # não a quinta fonte: citá-lo sem dizer que ele deriva reabre o ponto de
        # esquecimento que o T-052 fechou.
        for num, linha in enumerate(conteudo.splitlines(), 1):
            if "ContextGuardReleaseVersionTest" in linha and "deriva" not in linha:
                problemas.append(
                    (
                        arq.relative_to(raiz),
                        num,
                        "cita `ContextGuardReleaseVersionTest` sem dizer que ele "
                        "**deriva** a versão do manifesto — a versão vive em quatro "
                        "lugares, e uma constante fixa seria a quinta",
                    )
                )

    # ── Os TRÊS gates em toda instrução viva de release (T-052, rodada 2) ──
    # A suíte veio do ramo remoto; a documentação de release veio do ramo local,
    # que só conhecia dois gates. Ninguém errou — o texto simplesmente não sabia
    # do outro, e o resultado era um guia que manda publicar sem rodar os 201
    # testes. Regressão no verificador, no runner ou no guardião passa inteira
    # por `validate` e pelo lint: os dois leem texto e manifesto, não executam
    # nada.
    #
    # A lista de módulos NÃO entra aqui nem na doc: a instrução já enumerou três
    # dos cinco, e quem a seguia rodava 119 dos 201 achando que rodara tudo. Por
    # isso o guarda exige `discover` e PROÍBE enumeração no comando obrigatório.
    GATES_OBRIGATORIOS = (
        ("python3 -m unittest discover -s orq/scripts -p 'test_*.py'", "a suíte"),
        ("claude plugin validate ./orq --strict", "o manifesto"),
        ("python3 orq/scripts/lint-coerencia.py .", "o lint de coerência"),
    )
    INSTRUCOES_DE_RELEASE = (
        "CLAUDE.md",
        "AGENTS.md",
        "README.md",
        "memory/wiki/distribuicao.md",
    )
    ENUMERACAO_RE = re.compile(r"python3 -m unittest\s+orq\.scripts\.")
    for rel in INSTRUCOES_DE_RELEASE:
        arq = raiz / rel
        if not arq.is_file():
            continue
        conteudo = arq.read_text(encoding="utf-8")
        for gate, papel in GATES_OBRIGATORIOS:
            if gate not in conteudo:
                problemas.append(
                    (
                        Path(rel),
                        0,
                        f"instrução viva de release não cita {papel} — os gates "
                        "automatizados são TRÊS e todos obrigatórios; faltando um, "
                        "o texto autoriza publicar sem ele",
                    )
                )
        for num, linha in enumerate(conteudo.splitlines(), 1):
            if ENUMERACAO_RE.search(linha):
                problemas.append(
                    (
                        Path(rel),
                        num,
                        "enumera módulos de teste no comando obrigatório — use "
                        "`discover`: lista enumerada envelhece calada (já rodou 3 "
                        "de 5 módulos, 119 de 201 testes, sem ninguém notar)",
                    )
                )

    # ── O bump é PASSO do fluxo, não advertência avulsa (T-052, rodada 3) ──
    # O README descrevia o desenvolvimento como editar → gates → update, sem o
    # bump coordenado. Numa máquina ou CI SEM o cache daquela versão, seguir a
    # lista publica com a chave antiga e o cache conserva os bytes velhos: o
    # teste de coordenação passa (os quatro seguem iguais ENTRE SI) e o lint não
    # confere cache inexistente. É o T-017 ressuscitado por omissão.
    #
    # Duas decisões de desenho, e as duas importam:
    #
    # 1. ANCORA NA SEÇÃO. Procurar os quatro lugares "no arquivo" passaria verde
    #    com o fluxo quebrado, porque o alerta lá adiante ("quem edita sem
    #    bumpar…") e a tabela de memória satisfazem a busca. Presença em
    #    qualquer lugar ≠ presença onde a instrução é executada.
    # 2. MASCARA AS CERCAS. Dentro desta seção existe o diagrama de estrutura,
    #    que LISTA `plugin.json` e `marketplace.json` como arquivos. Sem
    #    mascarar, um diagrama satisfaria a obrigação de um procedimento.
    OBRIGACAO_DO_BUMP = (
        ("O primeiro passo é o bump", "a obrigação explícita do bump"),
        ("orq/.claude-plugin/plugin.json", "o manifesto"),
        (".claude-plugin/marketplace.json", "o catálogo"),
        ("memory/MEMORY.md", "o índice da wiki"),
        ("Status", "a seção Status do README"),
    )
    # Os DOIS procedimentos ordenados do projeto. Cobrir só um deixaria o outro
    # ensinando a publicar sem bump — foi o que a varredura encontrou depois de
    # corrigir o README: o `## Ciclo de edição` tinha exatamente o mesmo buraco.
    PROCEDIMENTOS_ORDENADOS = (
        ("README.md", "## Desenvolver o plugin"),
        ("memory/wiki/distribuicao.md", "## Ciclo de edição"),
    )
    for rel, heading in PROCEDIMENTOS_ORDENADOS:
        arq = raiz / rel
        if not arq.is_file():
            continue
        secao, estado = secao_unica(arq.read_text(encoding="utf-8"), heading)
        if estado != "ok":
            problemas.append(
                (
                    Path(rel),
                    0,
                    f"`{heading}` {estado} — é onde o procedimento de release é "
                    "executado; sem essa seção não há onde exigir o bump",
                )
            )
            continue
        prosa = _mascara_cercas(secao)
        for trecho, papel in OBRIGACAO_DO_BUMP:
            if trecho not in prosa:
                problemas.append(
                    (
                        Path(rel),
                        0,
                        f"`{heading}` não manda bumpar {papel} — o bump dos quatro "
                        "lugares é PASSO do procedimento, não advertência em outra "
                        "seção: quem segue a lista ordenada não lê o alerta, e "
                        "release sem bump deixa o cache stale sem nenhum gate acusar",
                    )
                )

    # ── Teto do runner Opus: uma fonte, várias superfícies (T-052) ─────────
    # O valor real mora em `scripts/run-opus-reviewer.py`; a prosa o repete em
    # cinco lugares. A reconciliação da 0.25.0 corrigiu dois e esqueceu o
    # README, que ficou anunciando o teto antigo — nenhum gate reclamou. No host
    # Codex o `runner-opus` é o ÚNICO revisor cross-vendor: um modelo seguindo o
    # número errado declara REVISÃO DEGRADADA e descarta um parecer válido que
    # chegou dentro do contrato real.
    #
    # O guarda DERIVA o número do runner — nunca o fixa aqui — e exige que toda
    # menção a segundos, em linha que fale do runner/teto/limite, bata com ele.
    # Allowlist estrutural para os relógios que não são este.
    runner_py = plugin / "scripts" / "run-opus-reviewer.py"
    teto_m = (
        re.search(
            r"^DEFAULT_TIMEOUT_SECONDS\s*=\s*(\d+)(?:\.\d+)?\s*$",
            runner_py.read_text(encoding="utf-8"),
            re.M,
        )
        if runner_py.is_file()
        else None
    )
    if teto_m is None:
        problemas.append(
            (
                Path("orq/scripts/run-opus-reviewer.py"),
                0,
                "não achei `DEFAULT_TIMEOUT_SECONDS` — é a fonte única do teto "
                "documentado; sem ela este guarda fica cego",
            )
        )
    else:
        teto = teto_m.group(1)
        TETO_GATILHO = re.compile(r"run-opus-reviewer|runner-opus|timeout|teto|limite", re.I)
        TETO_NUM = re.compile(r"(?<![\d,.])(\d{2,4})\s*s\b")
        OUTROS_RELOGIOS = frozenset({
            # sonda viva da CLI do revisor: mede disponibilidade, não parecer
            "`< /dev/null`, timeout de ~60s) é **chamada paga a serviço de terceiro**: rode-a apenas quando o",
            # menção histórica ao teto que matava parecer válido (T-050)
            "resposta válida levar 267,1s e ser morta pelo limite anterior de 240s. Diff maior é dividido por arquivo/hunk, cobrindo",
        })
        TETO_SUPERFICIES = (
            raiz / "README.md",
            plugin / "commands" / "revisar.md",
            plugin / "commands" / "elenco.md",
            plugin / "commands" / "stack.md",
            plugin / "stack.md",
            raiz / "memory" / "wiki" / "_elenco.md",
            raiz / "memory" / "wiki" / "arquitetura.md",
        )
        # Onde o valor TEM que aparecer: apagar o número em silêncio também é
        # perda de contrato, e só o check negativo não pegaria.
        TETO_DECLARAM = {
            raiz / "README.md",
            plugin / "commands" / "revisar.md",
            plugin / "commands" / "elenco.md",
            raiz / "memory" / "wiki" / "_elenco.md",
            raiz / "memory" / "wiki" / "arquitetura.md",
        }
        for arq in TETO_SUPERFICIES:
            if not arq.is_file():
                continue
            conteudo = arq.read_text(encoding="utf-8")
            if arq in TETO_DECLARAM and f"{teto}s" not in conteudo:
                problemas.append(
                    (
                        arq.relative_to(raiz),
                        0,
                        f"não declara o teto do runner Opus ({teto}s) — o valor vem "
                        "de `DEFAULT_TIMEOUT_SECONDS`, e superfície muda deixa o "
                        "leitor sem o contrato",
                    )
                )
            for num, linha in enumerate(conteudo.splitlines(), 1):
                if not TETO_GATILHO.search(linha) or linha.strip() in OUTROS_RELOGIOS:
                    continue
                for achado in TETO_NUM.finditer(linha):
                    if achado.group(1) != teto:
                        problemas.append(
                            (
                                arq.relative_to(raiz),
                                num,
                                f"anuncia {achado.group(1)}s para o runner Opus, mas "
                                f"`DEFAULT_TIMEOUT_SECONDS` é {teto} — outro relógio? "
                                "entre na allowlist do lint, com revisão",
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
        # .orphaned_at é escrito pela CLI quando uma versão deixa de ser a
        # instalada. .in_use e seus PIDs protegem caches de sessões Claude
        # vivas. O helper ignora esses metadados somente no lado do cache; um
        # caminho homônimo no fonte continua sendo divergência de produto.
        try:
            divergentes = find_installation_divergences(
                source=plugin,
                installed=cache,
                host="claude",
            )
        except OSError as exc:
            problemas.append(
                (Path("orq"), 0, f"não foi possível comparar o cache instalado: {exc}")
            )
            divergentes = []
        if divergentes:
            primeira = divergentes[0]
            problemas.append(
                (
                    Path("orq"),
                    0,
                    f"versão {versao} diverge do cache instalado "
                    f"({primeira.kind}:{primeira.path}) — corrija a árvore "
                    "instalada ou a fonte; depois reinstale a candidata e repita "
                    "o verificador",
                )
            )

    if problemas:
        print(f"✗ {len(problemas)} referência(s) quebrada(s):\n")
        for rel, num, msg in problemas:
            print(f"  {rel}:{num}  {msg}")
        print("\nRenomeou algo? Faça grep do nome antigo no orq/ inteiro.")
        return 1

    total = sum(len(v) for v in conhecidos.values())
    print(
        f"✓ coerência interna ok — {total} nomes conferidos, memory/ ignorado "
        f"(exceto {len(PAGINAS_VIVAS_FORA_DO_PLUGIN)} páginas vivas nominais)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
