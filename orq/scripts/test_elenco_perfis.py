#!/usr/bin/env python3
"""Testes da guarda de perfil ativo × preset (T-080).

Nada impedia a tabela viva do Host Claude e o preset que a linha `Perfil
ativo` diz estar em vigor de divergirem em silêncio — foi o que aconteceu por
três dias em setembro de 2026, com os três gates automatizados verdes o tempo
todo. Este módulo cobre a matriz de aceite do plano
(`docs/plano_T-080-guarda-preset.md`).
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")

lint_spec = importlib.util.spec_from_file_location("orq_lint_coerencia_t080", LINT_PATH)
assert lint_spec is not None and lint_spec.loader is not None
lint_module = importlib.util.module_from_spec(lint_spec)
sys.modules[lint_spec.name] = lint_module
lint_spec.loader.exec_module(lint_module)


def run_lint_main(root: Path, home: Path) -> tuple[int, str]:
    """Roda a CÓPIA do lint que mora dentro de `root` (não o módulo importado
    no topo deste arquivo) como **subprocesso** — não in-process.

    `main()` exclui a si mesmo da varredura de vocabulário do host de terceiro
    aposentado na 0.24.0 comparando `Path(__file__).resolve()` com cada
    arquivo varrido (`este_script`, `lint-coerencia.py:1060`). Rodar in-process
    com o módulo carregado da fonte real, mas apontando `raiz` para uma CÓPIA,
    quebra essa exclusão: `__file__` continua sendo o original, o script
    dentro da cópia deixa de bater com ele, e o lint acusa o próprio
    código-fonte da guarda (que legitimamente cita o nome do host aposentado
    na definição do padrão) como se fosse instrução viva. Subprocesso evita o
    problema: `__file__`, ali dentro, é a cópia.

    Isola `HOME` (que é de onde `Path.home()` deriva em POSIX) em vez do cache
    real desta máquina — mesmo precedente de `run_lint_main` em
    `test_context_guard.py:1978`, adaptado para subprocesso: sem cache
    instalado para a versão do manifesto, a guarda de cache stale se cala de
    propósito, e sobra só o que este módulo quer medir.
    """
    script = root / "orq" / "scripts" / "lint-coerencia.py"
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    resultado = subprocess.run(
        [sys.executable, str(script), str(root)],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    return resultado.returncode, resultado.stdout + resultado.stderr


class ElencoPerfisRedIntegrationTest(unittest.TestCase):
    """Prova que a guarda está de fato ligada em `main()` — não só existe como
    função isolada. A fixture é uma cópia completa do repositório real (que é
    coerente hoje, ver `test_real_documents_have_no_t080_diagnostic`), com UMA
    mutação cirúrgica: só o `implementer·pesada` do preset `padrao` do projeto,
    de `sonnet` para `opus` — a tabela ativa e a linha `Perfil ativo` (`sem
    desvio`) ficam intocadas.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-elenco-perfis-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(
            REPO_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git"),
        )
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()

    def mutar_preset_padrao(self, de: str, para: str) -> None:
        elenco = self.root / "memory" / "wiki" / "_elenco.md"
        texto = elenco.read_text(encoding="utf-8")
        alvo = (
            "| implementer·pesada | sonnet | executar plano já aprovado é "
            "trabalho dirigido — reconciliado com a tabela ativa |"
        )
        self.assertIn(alvo, texto, "linha do preset padrao mudou de forma inesperada")
        self.assertEqual(de, "sonnet")
        novo = alvo.replace("sonnet", para, 1)
        elenco.write_text(texto.replace(alvo, novo, 1), encoding="utf-8")

    def test_real_documents_have_no_t080_diagnostic(self) -> None:
        """Controle negativo: a cópia sem mutação tem que passar — se isto
        falhar, o defeito é da cópia/fixture, não da guarda."""
        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 0, output)

    def test_implementer_pesada_alterado_so_no_preset_reprova(self) -> None:
        self.mutar_preset_padrao("sonnet", "opus")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("memory/wiki/_elenco.md", output)
        self.assertIn("Host Claude", output)
        self.assertIn("padrao", output)
        self.assertIn("implementer·pesada", output)
        self.assertIn("ativo=sonnet", output)
        self.assertIn("preset=opus", output)

    # -- revisão adversarial do T-080, rodada 3, achado 6 -------------------
    # `validate_elenco_perfis` protegia a PRIMEIRA leitura de `_elenco.md` e
    # de `elenco.md`, mas `main()` RELÊ os dois em vários outros pontos (o
    # teto do runner Opus, os contratos do Codex, o template do elenco…) sem
    # proteção — um `UnicodeDecodeError` numa dessas releituras matava
    # `main()` inteiro e a saída saía VAZIA, perdendo até o diagnóstico que
    # `validate_elenco_perfis` já tinha acumulado. Estes dois testes rodam o
    # lint de verdade, via subprocesso, contra uma cópia completa do repo —
    # não chamam `validate_elenco_perfis` isoladamente, que já era protegida
    # antes desta rodada.
    def test_encoding_invalido_no_elenco_do_projeto_nao_derruba_main(self) -> None:
        elenco = self.root / "memory" / "wiki" / "_elenco.md"
        elenco.write_bytes(b"## Perfis\n\xff\xfe conteudo fora de utf-8\n")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertNotIn("Traceback", output)
        self.assertIn("memory/wiki/_elenco.md", output)
        self.assertIn("não foi possível ler", output)

    def test_encoding_invalido_no_elenco_do_template_nao_derruba_main(self) -> None:
        elenco_cmd = self.root / "orq" / "commands" / "elenco.md"
        elenco_cmd.write_bytes(b"## Modelo do arquivo\n\xff\xfe conteudo fora de utf-8\n")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertNotIn("Traceback", output)
        self.assertIn("orq/commands/elenco.md", output)
        self.assertIn("não foi possível ler", output)


class ElencoPerfisRealDocumentsTest(unittest.TestCase):
    """Complemento rápido, sem cópia, de
    `ElencoPerfisRedIntegrationTest.test_real_documents_have_no_t080_diagnostic`
    — chama a validação diretamente sobre os DOIS documentos reais (projeto e
    template de fábrica), sem passar por `main()` nem por subprocesso."""

    def test_projeto_e_template_reais_sem_diagnostico(self) -> None:
        problemas = lint_module.validate_elenco_perfis(REPO_ROOT, PLUGIN_ROOT)

        self.assertEqual(problemas, [])


# ── Fixtures mínimas para os testes diretos ─────────────────────────────────
# Uma tabela de 9 papéis (host) ou 8 (preset) por caso da matriz de aceite
# seria ilegível repetida 15×; os mapas e o montador abaixo isolam só o que
# cada caso muda.

PAPEIS_HOST_ORDEM = [
    "manager",
    "planner·interface",
    "planner·sistema",
    "implementer·pesada",
    "implementer·normal",
    "implementer·leve",
    "reviewer",
    "docs",
    "scout",
]
PAPEIS_PRESET_ORDEM = PAPEIS_HOST_ORDEM[1:]

ATIVOS_BASE = {
    "manager": "modelo da sessão",
    "planner·interface": "fable",
    "planner·sistema": "gpt-6-astra@max",
    "implementer·pesada": "sonnet",
    "implementer·normal": "sonnet",
    "implementer·leve": "sonnet",
    "reviewer": "gpt-6-astra@max",
    "docs": "sonnet",
    "scout": "sonnet",
}
PRESET_PADRAO_BASE = {p: v for p, v in ATIVOS_BASE.items() if p != "manager"}
PRESET_ECONOMIA_BASE = {
    "planner·interface": "opus",
    "planner·sistema": "gpt-6-astra@high",
    "implementer·pesada": "sonnet",
    "implementer·normal": "sonnet",
    "implementer·leve": "haiku",
    "reviewer": "gpt-6-astra@high",
    "docs": "haiku",
    "scout": "haiku",
}


def _tabela_md(mapa: dict, ordem: list, motivos: dict | None = None) -> str:
    motivos = motivos or {}
    linhas = ["| Papel | Modelo | Por quê |", "|---|---|---|"]
    for papel in ordem:
        if papel in mapa:
            linhas.append(f"| {papel} | {mapa[papel]} | {motivos.get(papel, 'motivo')} |")
    return "\n".join(linhas)


def build_elenco(
    *,
    ativos: dict | None = None,
    ativos_remover: tuple = (),
    padrao: dict | None = None,
    padrao_remover: tuple = (),
    economia: dict | None = None,
    perfil_ativo_linha: str | None = (
        "**Perfil ativo:** `padrao` — desde 2026-09-01, sem desvio."
    ),
    incluir_perfis: bool = True,
    incluir_host_claude: bool = True,
    incluir_padrao: bool = True,
    incluir_economia: bool = True,
    tabela_ativos_bruta: str | None = None,
    tabela_padrao_bruta: str | None = None,
    motivos_ativos: dict | None = None,
    motivos_padrao: dict | None = None,
) -> str:
    """Monta um `_elenco.md` mínimo, mas estruturalmente completo (`##  Times
    por host` com `### Host Claude`/`### Host Codex`, `## Perfis` com
    `padrao`/`economia`) — o bastante para `validate_elenco_perfis` andar até
    o fim sem tropeçar em seção ausente por acidente. Cada parâmetro cobre
    exatamente uma variação da matriz de aceite do plano.
    """
    mapa_ativos = dict(ATIVOS_BASE)
    if ativos:
        mapa_ativos.update(ativos)
    for papel in ativos_remover:
        mapa_ativos.pop(papel, None)

    mapa_padrao = dict(PRESET_PADRAO_BASE)
    if padrao:
        mapa_padrao.update(padrao)
    for papel in padrao_remover:
        mapa_padrao.pop(papel, None)

    mapa_economia = dict(PRESET_ECONOMIA_BASE)
    if economia:
        mapa_economia.update(economia)

    partes = ["# Elenco de teste\n", "## Times por host\n"]
    if incluir_host_claude:
        partes.append("### Host Claude\n")
        tabela_ativos = (
            tabela_ativos_bruta
            if tabela_ativos_bruta is not None
            else _tabela_md(mapa_ativos, PAPEIS_HOST_ORDEM, motivos_ativos)
        )
        partes.append(tabela_ativos + "\n")
        if perfil_ativo_linha is not None:
            partes.append(perfil_ativo_linha + "\n")
    partes.append("### Host Codex\n")
    partes.append("Este host não tem presets.\n")
    if incluir_perfis:
        partes.append("## Perfis — nomeados por teste\n")
        if incluir_padrao:
            partes.append("### `padrao` — time de teste\n")
            tabela_padrao = (
                tabela_padrao_bruta
                if tabela_padrao_bruta is not None
                else _tabela_md(mapa_padrao, PAPEIS_PRESET_ORDEM, motivos_padrao)
            )
            partes.append(tabela_padrao + "\n")
        if incluir_economia:
            partes.append("### `economia` — time de teste\n")
            partes.append(_tabela_md(mapa_economia, PAPEIS_PRESET_ORDEM) + "\n")
    return "\n".join(partes)


def wrap_template(texto_interno: str) -> str:
    """Envolve um `_elenco.md` de teste no bloco canônico que
    `_bloco_canonico_elenco` procura dentro de `## Modelo do arquivo`."""
    return "## Modelo do arquivo\n\n```markdown\n" + texto_interno + "\n```\n"


class ElencoPerfisDiretoTest(unittest.TestCase):
    """Testes diretos de `validate_elenco_perfis`, um por linha da matriz de
    aceite do plano — fixtures minúsculas, sem cópia de repositório."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-elenco-perfis-direto-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plugin = self.root / "orq"
        (self.root / "memory" / "wiki").mkdir(parents=True)

    def escrever_projeto(self, texto: str) -> None:
        (self.root / "memory" / "wiki" / "_elenco.md").write_text(texto, encoding="utf-8")

    def escrever_template(self, texto_interno: str) -> None:
        (self.plugin / "commands").mkdir(parents=True, exist_ok=True)
        (self.plugin / "commands" / "elenco.md").write_text(
            wrap_template(texto_interno), encoding="utf-8"
        )

    def validar(self) -> list:
        return lint_module.validate_elenco_perfis(self.root, self.plugin)

    # -- linha 1 da matriz (coerência básica) ---------------------------
    def test_fixture_padrao_coerente_sem_diagnostico(self) -> None:
        self.escrever_projeto(build_elenco())

        self.assertEqual(self.validar(), [])

    # -- linha 3: só a tabela ativa muda, "sem desvio" ------------------
    def test_alteracao_so_na_tabela_ativa_sem_desvio_reprova(self) -> None:
        self.escrever_projeto(build_elenco(ativos={"docs": "haiku"}))

        problemas = self.validar()

        self.assertTrue(problemas)
        mensagens = [p[2] for p in problemas]
        self.assertTrue(any("docs" in m and "ativo=haiku" in m and "preset=sonnet" in m for m in mensagens))

    # -- linha 4: um desvio legítimo, e vários -------------------------
    def test_desvio_legitimo_unico_passa(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: docs→haiku."
                ),
            )
        )

        self.assertEqual(self.validar(), [])

    def test_desvios_legitimos_multiplos_passa(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku", "scout": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: "
                    "docs→haiku; scout→haiku."
                ),
            )
        )

        self.assertEqual(self.validar(), [])

    # -- linha 5: desvio legítimo + diferença não declarada -------------
    def test_desvio_legitimo_mais_diferenca_nao_declarada_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku", "scout": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: docs→haiku."
                ),
            )
        )

        problemas = self.validar()

        mensagens = [p[2] for p in problemas]
        self.assertTrue(any("scout" in m and "diferença sem desvio declarado" in m for m in mensagens))
        self.assertFalse(any("docs" in m and "diferença sem desvio declarado" in m for m in mensagens))

    # -- linha 6: valor errado, papel desconhecido, repetido, obsoleto --
    def test_desvio_com_valor_errado_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: docs→opus."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(any("não bate com o modelo ativo" in p[2] for p in problemas))

    def test_desvio_com_papel_desconhecido_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: auditor→opus."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(
            any("auditor" in p[2] and "não é um dos oito papéis" in p[2] for p in problemas)
        )

    def test_desvio_com_papel_repetido_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: "
                    "docs→haiku; docs→sonnet."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(any("ilegível" in p[2] and "repetido" in p[2] for p in problemas))

    def test_desvio_ja_igual_ao_preset_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: docs→sonnet."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(any("já é igual ao preset" in p[2] for p in problemas))

    # -- linha 7: "sem desvio" junto de uma lista de desvios ------------
    def test_sem_desvio_com_lista_de_desvios_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-01, sem desvio · "
                    "desvio: docs→haiku."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(any("ilegível" in p[2] and "ao mesmo tempo" in p[2] for p in problemas))

    # -- linha 8: `economia` ativo não compara com `padrao` -------------
    def test_perfil_economia_ativo_nao_compara_com_padrao(self) -> None:
        ativos_economia = dict(PRESET_ECONOMIA_BASE)
        self.escrever_projeto(
            build_elenco(
                ativos=ativos_economia,
                perfil_ativo_linha=(
                    "**Perfil ativo:** `economia` — desde 2026-09-01, sem desvio."
                ),
            )
        )

        self.assertEqual(self.validar(), [])

    # -- linha 9: perfil ativo inexistente / linha ativa ausente --------
    def test_perfil_ativo_com_nome_inexistente_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                perfil_ativo_linha=(
                    "**Perfil ativo:** `turbo` — desde 2026-09-01, sem desvio."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(any("turbo" in p[2] and "não existe em" in p[2] for p in problemas))

    def test_linha_perfil_ativo_ausente_reprova(self) -> None:
        self.escrever_projeto(build_elenco(perfil_ativo_linha=None))

        problemas = self.validar()

        self.assertTrue(any("ausente" in p[2] for p in problemas))

    # -- linha 10: papel ausente, duplicado, intruso; modelo vazio ------
    def test_papel_ausente_no_preset_reprova(self) -> None:
        self.escrever_projeto(build_elenco(padrao_remover=("docs",)))

        problemas = self.validar()

        self.assertTrue(any("docs" in p[2] and "ausente" in p[2] for p in problemas))

    def test_papel_duplicado_no_preset_reprova(self) -> None:
        tabela = _tabela_md(PRESET_PADRAO_BASE, PAPEIS_PRESET_ORDEM)
        linha_duplicada = "| implementer·pesada | sonnet | duplicata de teste |"
        self.escrever_projeto(
            build_elenco(tabela_padrao_bruta=tabela + "\n" + linha_duplicada)
        )

        problemas = self.validar()

        self.assertTrue(
            any("implementer·pesada" in p[2] and "aparece 2×" in p[2] for p in problemas)
        )

    def test_papel_intruso_no_preset_reprova(self) -> None:
        tabela = _tabela_md(PRESET_PADRAO_BASE, PAPEIS_PRESET_ORDEM)
        linha_intrusa = "| auditor | sonnet | não é papel de eixo nem fixo |"
        self.escrever_projeto(
            build_elenco(tabela_padrao_bruta=tabela + "\n" + linha_intrusa)
        )

        problemas = self.validar()

        self.assertTrue(
            any("auditor" in p[2] and "não pertence a esta tabela" in p[2] for p in problemas)
        )

    def test_modelo_vazio_reprova(self) -> None:
        self.escrever_projeto(build_elenco(ativos={"docs": ""}))

        problemas = self.validar()

        self.assertTrue(any("docs" in p[2] and "modelo vazio" in p[2] for p in problemas))

    # -- linha 11 e 12: `manager` --------------------------------------
    def test_manager_alterado_na_tabela_ativa_nao_afeta_igualdade(self) -> None:
        self.escrever_projeto(build_elenco(ativos={"manager": "qualquer-outro-modelo"}))

        self.assertEqual(self.validar(), [])

    def test_manager_inserido_no_preset_reprova(self) -> None:
        tabela = _tabela_md(PRESET_PADRAO_BASE, PAPEIS_PRESET_ORDEM)
        linha_manager = "| manager | opus | não é papel de preset |"
        self.escrever_projeto(
            build_elenco(tabela_padrao_bruta=tabela + "\n" + linha_manager)
        )

        problemas = self.validar()

        self.assertTrue(
            any("manager" in p[2] and "não pertence a esta tabela" in p[2] for p in problemas)
        )

    def test_manager_em_desvio_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · desvio: manager→opus."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(
            any("manager" in p[2] and "não é papel de preset nem de desvio" in p[2] for p in problemas)
        )

    # -- linha 13: só justificativa/espaçamento/crase não diverge ------
    def test_mudanca_so_em_justificativa_nao_diverge(self) -> None:
        self.escrever_projeto(
            build_elenco(
                motivos_ativos={"docs": "motivo A, bem diferente"},
                motivos_padrao={"docs": "motivo B, completamente outro"},
            )
        )

        self.assertEqual(self.validar(), [])

    def test_espacamento_e_crases_nao_criam_divergencia(self) -> None:
        self.escrever_projeto(build_elenco(ativos={"docs": "`sonnet`  "}))

        self.assertEqual(self.validar(), [])

    # -- linha 14: host Codex sem presets --------------------------------
    # Revisão adversarial do T-080 (achado 1): a dispensa de `## Perfis`
    # ausente só é legítima quando o documento NÃO tem `### Host Claude` — é
    # o caso do `_elenco.md` só-Codex. Um documento COM Host Claude e sem
    # `## Perfis` reconhecível é diagnóstico, não silêncio: era exatamente
    # esse buraco que deixava a guarda inteira se desarmar bastando remover
    # ou renomear `## Perfis`, com PoC reproduzido nas duas superfícies.
    def test_perfis_ausente_com_host_claude_reprova(self) -> None:
        self.escrever_projeto(build_elenco(incluir_perfis=False))

        problemas = self.validar()

        self.assertTrue(problemas)
        mensagens = [p[2] for p in problemas]
        self.assertTrue(
            any("## Perfis" in m and "Host Claude" in m for m in mensagens)
        )

    def test_perfis_ausente_sem_host_claude_nao_reprova(self) -> None:
        self.escrever_projeto(
            build_elenco(incluir_host_claude=False, incluir_perfis=False)
        )

        self.assertEqual(self.validar(), [])

    # -- revisão adversarial do T-080, rodada 3, achado 1 ------------------
    # A dispensa dependia de RECONHECER o heading `### Host Claude` por nome
    # exato. Deformar esse heading E `## Perfis` ao mesmo tempo — mantendo a
    # tabela viva e a linha `**Perfil ativo:**` intocadas, com uma divergência
    # real por baixo (`docs` ativo diverge do preset, "sem desvio") — fazia a
    # guarda concluir "documento sem Host Claude" e devolver `[]` em silêncio.
    # Três formas de deformação, três reproduções da mesma classe: renomear o
    # heading, fechá-lo no estilo ATX (`### Host Claude ###`, sintaxe
    # CommonMark válida que o reconhecedor de heading não cobria) e cercar só
    # a LINHA do heading como se fosse exemplo, deixando tabela e `Perfil
    # ativo` vivos por fora da cerca.
    def _elenco_divergente_com_host_claude_deformado(self, heading_deformado: str) -> str:
        texto = build_elenco(ativos={"docs": "haiku"})
        texto = texto.replace("### Host Claude\n", heading_deformado, 1)
        self.assertIn(heading_deformado, texto, "substituição do heading não aplicou")
        return texto.replace(
            "## Perfis — nomeados por teste\n", "## PerfisDeTeste\n", 1
        )

    def test_heading_renomeado_com_divergencia_real_reprova(self) -> None:
        self.escrever_projeto(
            self._elenco_divergente_com_host_claude_deformado(
                "### Host Claude antigo\n"
            )
        )

        self.assertTrue(self.validar())

    def test_heading_com_fechamento_atx_com_divergencia_real_reprova(self) -> None:
        self.escrever_projeto(
            self._elenco_divergente_com_host_claude_deformado("### Host Claude ###\n")
        )

        self.assertTrue(self.validar())

    def test_heading_cercado_como_exemplo_com_divergencia_real_reprova(self) -> None:
        self.escrever_projeto(
            self._elenco_divergente_com_host_claude_deformado(
                "```\n### Host Claude\n```\n"
            )
        )

        self.assertTrue(self.validar())

    # -- linha 15: heading/tabela/linha ativa falsos dentro de exemplo --
    def test_host_claude_falso_dentro_de_exemplo_nao_satisfaz(self) -> None:
        tabela_fake = _tabela_md(ATIVOS_BASE, PAPEIS_HOST_ORDEM)
        tabela_padrao = _tabela_md(PRESET_PADRAO_BASE, PAPEIS_PRESET_ORDEM)
        texto = (
            "## Times por host\n\n"
            "### Host Codex\n\nEste host não tem presets.\n\n"
            "## Perfis — nomeados por teste\n\n"
            "Exemplo de como ficaria a seção do Host Claude:\n\n"
            "```markdown\n"
            "### Host Claude\n\n"
            f"{tabela_fake}\n\n"
            "**Perfil ativo:** `padrao` — desde 2026-09-01, sem desvio.\n"
            "```\n\n"
            "### `padrao` — time de teste\n\n"
            f"{tabela_padrao}\n"
        )
        self.escrever_projeto(texto)

        problemas = self.validar()

        self.assertTrue(
            any("Host Claude" in p[2] and "ausente" in p[2] for p in problemas)
        )

    # -- linha 16: projeto e template são superfícies independentes -----
    def test_mutacao_no_template_nao_aparece_como_diagnostico_do_projeto(self) -> None:
        self.escrever_projeto(build_elenco())
        self.escrever_template(build_elenco(padrao={"docs": "haiku"}))

        problemas = self.validar()

        self.assertTrue(problemas)
        self.assertTrue(all(p[0] == Path("orq/commands/elenco.md") for p in problemas))

    def test_mutacao_no_projeto_nao_aparece_como_diagnostico_do_template(self) -> None:
        self.escrever_projeto(build_elenco(padrao={"docs": "haiku"}))
        self.escrever_template(build_elenco())

        problemas = self.validar()

        self.assertTrue(problemas)
        self.assertTrue(all(p[0] == Path("memory/wiki/_elenco.md") for p in problemas))

    # -- revisão adversarial do T-080, achado 3 --------------------------
    # `## PerfisDeTeste`, sem fronteira depois do prefixo `## Perfis`, virava
    # uma segunda ocorrência do MESMO heading e reprovava com
    # "`## Perfis` duplicado:2" — falso positivo que bloqueava documentação
    # legítima só por citar uma palavra que começa com "Perfis".
    def test_heading_com_continuacao_do_nome_nao_causa_falso_duplicado(self) -> None:
        texto = build_elenco() + (
            "\n## PerfisDeTeste\n\nSeção sem relação, só para testar a fronteira.\n"
        )
        self.escrever_projeto(texto)

        self.assertEqual(self.validar(), [])

    # -- revisão adversarial do T-080, achado 4 --------------------------
    # As tabelas removem crases/negrito do valor (`_papel_modelo_com_offset`);
    # os desvios da linha `Perfil ativo` não removiam. Um desvio correto,
    # citado com crases, era acusado de divergir do próprio valor que
    # declara.
    def test_desvio_com_crases_normaliza_igual_a_tabela(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · "
                    "desvio: docs→`haiku`."
                ),
            )
        )

        self.assertEqual(self.validar(), [])

    # -- revisão adversarial do T-080, rodada 3, achado 3 -------------------
    # A correção do achado 4 (rodada 2, acima) normalizava com
    # `.strip("`* ")`, que descasca crase/asterisco/espaço das pontas
    # INDEPENDENTEMENTE, sem checar se formam um par — apagando conteúdo
    # LITERAL. `` `modelo-teste*` `` é um code span cujo CONTEÚDO termina em
    # asterisco literal; `` `modelo-teste` `` não tem asterisco nenhum. As
    # duas viravam a MESMA string e um valor divergente passava como igual.
    def test_asterisco_literal_dentro_de_code_span_nao_e_apagado_e_diverge(self) -> None:
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "`modelo-teste*`"},
                padrao={"docs": "`modelo-teste`"},
            )
        )

        problemas = self.validar()

        mensagens = [p[2] for p in problemas]
        self.assertTrue(
            any(
                "docs" in m
                and "ativo=modelo-teste*" in m
                and "preset=modelo-teste" in m
                for m in mensagens
            )
        )

    def test_desvio_com_asterisco_literal_nao_bate_com_ativo_sem_asterisco(self) -> None:
        # `docs→`haiku*`` (desvio) normalizava para "haiku" com o `strip`
        # antigo — igual ao ativo "haiku" sem asterisco nenhum — e o desvio
        # era aceito quando na verdade declara um valor DIFERENTE.
        self.escrever_projeto(
            build_elenco(
                ativos={"docs": "haiku"},
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · "
                    "desvio: docs→`haiku*`."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(any("não bate com o modelo ativo" in p[2] for p in problemas))

    # -- revisão adversarial do T-080, achado 6 --------------------------
    # Separar desvios com vírgula em vez de `;` produzia "desvio malformado,
    # esperado papel→modelo" — sem ensinar qual é o separador certo, num
    # produto cujo entregável é instrução.
    def test_desvio_com_virgula_ensina_separador_correto(self) -> None:
        self.escrever_projeto(
            build_elenco(
                perfil_ativo_linha=(
                    "**Perfil ativo:** `padrao` — desde 2026-09-06 · "
                    "desvio: docs→haiku, scout→haiku."
                ),
            )
        )

        problemas = self.validar()

        self.assertTrue(problemas)
        mensagens = [p[2] for p in problemas]
        self.assertTrue(any("`;`" in m for m in mensagens))

    # -- revisão adversarial do T-080, achado 5 --------------------------
    # `_elenco.md` com encoding incompatível levantava `UnicodeDecodeError`
    # sem tratamento e matava `main()` inteiro, engolindo junto qualquer
    # problema já acumulado por outras guardas. O contrato é devolver
    # `(Path, linha, mensagem)`, não propagar a exceção.
    def test_arquivo_com_encoding_invalido_produz_diagnostico_em_vez_de_estourar(
        self,
    ) -> None:
        caminho = self.root / "memory" / "wiki" / "_elenco.md"
        caminho.write_bytes(b"## Perfis\n\xff\xfe conteudo fora de utf-8\n")

        problemas = lint_module.validate_elenco_perfis(self.root, self.plugin)

        self.assertTrue(problemas)
        self.assertTrue(
            any(p[0] == Path("memory/wiki/_elenco.md") for p in problemas)
        )


class DesembrulhaMarcacaoPareadaTest(unittest.TestCase):
    """Revisão adversarial do T-080, rodada 3, achado 3: `_desembrulha_marcacao_pareada`
    substitui `.strip("`* ")`, que descascava crase/asterisco/espaço das
    pontas INDEPENDENTEMENTE, sem checar se formavam um par — apagando
    conteúdo literal. Testes diretos da primitiva."""

    def test_code_span_com_asterisco_literal_preserva_o_asterisco(self) -> None:
        self.assertEqual(
            lint_module._desembrulha_marcacao_pareada("`modelo-teste*`"),
            "modelo-teste*",
        )

    def test_code_span_sem_asterisco_normaliza_sem_ganhar_um(self) -> None:
        self.assertEqual(
            lint_module._desembrulha_marcacao_pareada("`modelo-teste`"),
            "modelo-teste",
        )

    def test_as_duas_formas_normalizam_para_valores_diferentes(self) -> None:
        com_asterisco = lint_module._desembrulha_marcacao_pareada("`modelo-teste*`")
        sem_asterisco = lint_module._desembrulha_marcacao_pareada("`modelo-teste`")

        self.assertNotEqual(com_asterisco, sem_asterisco)

    def test_asterisco_solto_nao_tem_par_e_nao_vira_string_vazia(self) -> None:
        self.assertEqual(lint_module._desembrulha_marcacao_pareada("*"), "*")

    def test_papel_com_ponto_medio_sobrevive_intocado(self) -> None:
        # `implementer·pesada` já sobrevivia ao `.strip("`* ")` antigo (não
        # tem crase/asterisco nenhum) — teste de não-regressão anti-falso-
        # positivo: continua sobrevivendo com a normalização pareada.
        self.assertEqual(
            lint_module._desembrulha_marcacao_pareada("implementer·pesada"),
            "implementer·pesada",
        )

    def test_negrito_pareado_e_removido(self) -> None:
        self.assertEqual(
            lint_module._desembrulha_marcacao_pareada("**sonnet**"), "sonnet"
        )


class SecaoUnicaOffsetFronteiraTest(unittest.TestCase):
    """Revisão adversarial do T-080, achado 3: `_secao_unica_offset` com
    `exato=False` casava o heading por PREFIXO sem exigir fronteira depois
    dele — `## PerfisDeTeste` contava como uma segunda ocorrência de
    `## Perfis`. Testes diretos da primitiva, com a calibração comprovada
    pelo revisor."""

    def test_subtitulo_decorativo_legitimo_casa(self) -> None:
        texto = "## Perfis — nomeados por teste\n\nconteúdo\n"

        _secao, _offset, estado = lint_module._secao_unica_offset(
            texto, "## Perfis", exato=False
        )

        self.assertEqual(estado, "ok")

    def test_continuacao_do_nome_sem_fronteira_nao_casa(self) -> None:
        texto = "## PerfisDeTeste\n\nconteúdo\n"

        _secao, _offset, estado = lint_module._secao_unica_offset(
            texto, "## Perfis", exato=False
        )

        self.assertEqual(estado, "ausente")

    def test_calibracao_variantes_sem_prefixo_exato_nao_casam(self) -> None:
        # As duas correm risco oposto (nenhuma fronteira em jogo: o prefixo
        # `` ### `padrao` `` — com crases — simplesmente não é um prefixo
        # literal de nenhuma das duas linhas) — confirmadas pelo revisor
        # como corretamente sem match, para calibrar o alvo do achado.
        for linha in ("### padrao-antigo", "### `padrao-antigo`"):
            with self.subTest(linha=linha):
                texto = linha + "\n\nconteúdo\n"

                _secao, _offset, estado = lint_module._secao_unica_offset(
                    texto, "### `padrao`", exato=False
                )

                self.assertEqual(estado, "ausente")

    def test_calibracao_hifen_colado_apos_fronteira_nao_casa(self) -> None:
        # Hífen colado bem depois do fecho de crase NÃO é fronteira válida —
        # é parte do nome, não separador. Comprovado pelo revisor como um
        # falso positivo que a correção precisa fechar.
        texto = "### `padrao`-antigo\n\nconteúdo\n"

        _secao, _offset, estado = lint_module._secao_unica_offset(
            texto, "### `padrao`", exato=False
        )

        self.assertEqual(estado, "ausente")

    # -- revisão adversarial do T-080, rodada 3, achado 4 -------------------
    # A fronteira virou uma ALLOWLIST de pontuação aceita (espaço, vírgula,
    # ponto, parênteses de FECHAMENTO…) e toda allowlist esquece algo: um
    # parêntese de ABERTURA colado sem espaço, e um espaço não separável
    # (U+00A0) antes do travessão decorativo, reprovavam documentação
    # legítima com "preset ausente" — falso positivo. A correção inverteu
    # para denylist (só letra/dígito/hífen são continuação do nome).
    def test_parentese_de_abertura_colado_sem_espaco_e_decoracao_valida(self) -> None:
        texto = "### `padrao`(time titular)\n\nconteúdo\n"

        _secao, _offset, estado = lint_module._secao_unica_offset(
            texto, "### `padrao`", exato=False
        )

        self.assertEqual(estado, "ok")

    def test_espaco_nao_separavel_antes_do_travessao_e_decoracao_valida(self) -> None:
        # `\xa0` (U+00A0, espaço não separável) antes do travessão — não
        # um espaço comum; a allowlist antiga só conhecia espaço/tab.
        texto = "### `padrao` — time titular\n\nconteúdo\n"

        _secao, _offset, estado = lint_module._secao_unica_offset(
            texto, "### `padrao`", exato=False
        )

        self.assertEqual(estado, "ok")


class BlocoCanonicoElencoTest(unittest.TestCase):
    """Revisão adversarial do T-080, achado 2: `_bloco_canonico_elenco`
    escolhia a PRIMEIRA ocorrência textual de `## Modelo do arquivo` e do
    `` ```markdown `` seguinte, sem checar unicidade nem respeitar cercas
    externas — os dois cenários reproduzidos pelo revisor.

    Os fixtures abaixo levam `## Times por host` dentro do conteúdo do bloco
    — desde o achado 5, só bloco que PARECE elenco compete a candidato
    (`_PARECE_TEMPLATE_ELENCO_RE`); um placeholder sem essa marca não seria
    mais contado, e os testes de ambiguidade genuína ficariam sem candidato
    nenhum."""

    def test_dois_blocos_markdown_sob_o_mesmo_heading_e_ambiguo(self) -> None:
        # (a) dois blocos candidatos sob o MESMO heading: o primeiro
        # coerente, o segundo divergente. Escolher o primeiro em silêncio
        # deixaria o divergente (o que de fato vale) escapar da guarda.
        txt = (
            "## Modelo do arquivo\n\n"
            "```markdown\nprimeiro bloco (coerente)\n\n## Times por host\n```\n\n"
            "```markdown\nsegundo bloco (divergente)\n\n## Times por host\n```\n\n"
            "## Outra seção\n"
        )

        bloco, _offset, erro = lint_module._bloco_canonico_elenco(txt)

        self.assertEqual(bloco, "")
        self.assertIsNotNone(erro)
        self.assertIn("ambíguo", erro)

    def test_exemplo_historico_cercado_por_4_crases_nao_mascara_o_real(self) -> None:
        # (b) um exemplo histórico, cercado por 4 crases e ANTES do template
        # real, cita o marcador `## Modelo do arquivo` e uma cópia coerente
        # dentro dele. A busca ingênua (primeira ocorrência textual) achava
        # o marcador FALSO (dentro da cerca externa) e devolvia a cópia
        # coerente — a declaração real, mais adiante e divergente, escapava
        # inteira da guarda.
        txt = (
            "Exemplo histórico (não usar mais):\n\n"
            "````\n"
            "## Modelo do arquivo\n\n"
            "```markdown\nCOPIA_ANTIGA_COERENTE\n\n## Times por host\n```\n"
            "````\n\n"
            "## Modelo do arquivo\n\n"
            "```markdown\nDECLARACAO_REAL_DIVERGENTE\n\n## Times por host\n```\n"
        )

        bloco, _offset, erro = lint_module._bloco_canonico_elenco(txt)

        self.assertIsNone(erro)
        self.assertIn("DECLARACAO_REAL_DIVERGENTE", bloco)
        self.assertNotIn("COPIA_ANTIGA_COERENTE", bloco)

    def test_heading_duplicado_e_ambiguo(self) -> None:
        txt = (
            "## Modelo do arquivo\n\n```markdown\nprimeiro\n```\n\n"
            "## Modelo do arquivo\n\n```markdown\nsegundo\n```\n"
        )

        bloco, _offset, erro = lint_module._bloco_canonico_elenco(txt)

        self.assertEqual(bloco, "")
        self.assertIsNotNone(erro)
        self.assertIn("ambíguo", erro)

    # -- revisão adversarial do T-080, rodada 3, achado 2 (2ª reprodução) --
    # `_blocos_markdown_de_topo` só registrava um candidato quando achava o
    # FECHAMENTO da cerca — uma cerca aberta e nunca fechada simplesmente
    # sumia da lista, e com ela sumia a ambiguidade real (o segundo bloco,
    # divergente, escapava por baixo). Cerca sem fechamento é anomalia
    # estrutural: tem que virar diagnóstico, nunca "só achei um".
    def test_segunda_cerca_sem_fechamento_e_diagnostico_nao_ambiguidade_silenciosa(
        self,
    ) -> None:
        txt = (
            "## Modelo do arquivo\n\n"
            "```markdown\nprimeiro bloco (coerente)\n\n## Times por host\n```\n\n"
            "```markdown\nsegundo bloco (divergente)\n\n## Times por host\n"
            # sem fechamento do segundo bloco — cerca aberta até o fim do texto.
        )

        bloco, _offset, erro = lint_module._bloco_canonico_elenco(txt)

        self.assertEqual(bloco, "")
        self.assertIsNotNone(erro)
        self.assertIn("aberta", erro)

    def test_segundo_bloco_em_lista_com_cerca_indentada_produz_diagnostico(
        self,
    ) -> None:
        # `` - ```markdown `` dentro de um item de lista não é reconhecida
        # como ABERTURA pelo reconhecedor de cerca (que exige 0-3 espaços
        # seguidos direto da crase — "- " na frente não casa); a cerca de
        # fechamento indentada (2 espaços + crases) que viria depois é então
        # lida como uma ABERTURA NOVA, que nunca fecha — mesma anomalia
        # estrutural da reprodução anterior, por um caminho diferente.
        txt = (
            "## Modelo do arquivo\n\n"
            "```markdown\nprimeiro bloco (coerente)\n\n## Times por host\n```\n\n"
            "- ```markdown\n"
            "  segundo bloco (divergente)\n"
            "  ```\n"
        )

        bloco, _offset, erro = lint_module._bloco_canonico_elenco(txt)

        self.assertEqual(bloco, "")
        self.assertIsNotNone(erro)
        self.assertIn("aberta", erro)

    # -- revisão adversarial do T-080, rodada 3, achado 5 -------------------
    # Contar QUALQUER cerca ```markdown``` como candidato, sem olhar o
    # conteúdo, fazia um bloco auxiliar (uma nota solta, sem nenhuma marca de
    # elenco) virar "segundo candidato" e reprovar a seção inteira com
    # ambiguidade que não existe de verdade.
    def test_bloco_auxiliar_sem_marca_de_elenco_nao_conta_como_candidato(self) -> None:
        txt = (
            "## Modelo do arquivo\n\n"
            "```markdown\nmodelo real\n\n## Times por host\n```\n\n"
            "### Exemplo de anotação\n\n"
            "```markdown\n# Nota\nRevisão concluída.\n```\n"
        )

        bloco, _offset, erro = lint_module._bloco_canonico_elenco(txt)

        self.assertIsNone(erro)
        self.assertIn("modelo real", bloco)


if __name__ == "__main__":
    unittest.main()
