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
    manifesto = plugin / ".claude-plugin" / "plugin.json"
    versao = json.loads(manifesto.read_text(encoding="utf-8")).get("version")
    for arq, rotulo in ((raiz / "README.md", "README"), (raiz / "memory" / "MEMORY.md", "MEMORY.md")):
        if not arq.exists():
            continue
        txt = arq.read_text(encoding="utf-8")
        if re.search(r"\b\d+\.\d+\.\d+\b", txt) and versao not in txt:
            achadas = sorted(set(re.findall(r"\b\d+\.\d+\.\d+\b", txt)))[:3]
            problemas.append(
                (arq.relative_to(raiz), 0, f"{rotulo} não cita a versão atual {versao} (achei {achadas})")
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
        if exigida and heading not in template_elenco:
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
            "Host Codex é exceção",
            "exatamente Opus 5 + Kimi K3",
            "política habilitada, não capacidade comprovada",
            "não acrescente a diagonal OpenAI",
            "PAINEL PARCIAL",
            "Sem elenco, valem os padrões de fábrica: reviewer `opus`,",
            "Codex ativo e Kimi K3 ativo",
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
            "| reviewer 1 | `opus` (exigir comprovação de que o alias resolve para Opus 5)",
            "| reviewer 2 | `kimi-code/k3` |",
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

    # A comprovação do alias Opus 5 é obrigatória tanto no Host Codex quanto
    # no Host Kimi; uma única ocorrência deixaria a outra tabela degradar com
    # lint verde.
    reviewer_opus = "| reviewer 1 | `opus` (exigir comprovação de que o alias resolve para Opus 5)"
    if template_elenco.count(reviewer_opus) != 2:
        problemas.append(
            (
                elenco_cmd.relative_to(raiz),
                0,
                "template precisa comprovar alias Opus 5 nos hosts Codex e Kimi",
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
    print(f"✓ coerência interna ok — {total} nomes conferidos, memory/ ignorado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
