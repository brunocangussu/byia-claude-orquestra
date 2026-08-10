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
            "timeout de 240s",
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
