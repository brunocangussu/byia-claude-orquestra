#!/usr/bin/env python3
"""Testes da guarda de marcador de host no board (T-086).

Duas janelas (Claude e Codex) no mesmo checkout já colidiram em silêncio: um
commit levou junto o trabalho não commitado da outra janela porque nada no
card dizia qual janela estava com ele (`docs/plano_coexistencia_hosts.md`,
seção "Evidência decisiva para o T-086"). A guarda em `lint-coerencia.py`
(`validate_marcador_host_kanban`) exige `@claude` ou `@codex` em todo card
`[>]`/`[~]`, proíbe os dois marcadores juntos e proíbe marcador sobrando fora
dos dois estados em curso.

⚠️ **Este módulo não usa o `memory/wiki/KANBAN.md` real, de propósito.** O
card aprovado proíbe marcar os cards existentes do board vivo — essa migração
é do Manager, no merge — e manda usar "um card fictício em teste" quando um
exemplo for necessário. Por isso o "board real" do controle negativo abaixo é
um board **sintético, mas fiel ao contrato** (`_schema.md`): representativo
do formato de verdade, sem tocar no arquivo rastreado pelo git. O board sintético isola os
casos do movimento diário do board vivo; ele não substitui a conferência do
board real, que o próprio `lint-coerencia.py` faz a cada execução.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent

# Board sintético que satisfaz o contrato inteiro (`_schema.md`): um card por
# estado, cobrindo os dois "em curso" (marcados, um marcador cada), os três
# que proíbem marcador (sem nenhum) e o `[!]` fora do escopo desta guarda
# (também sem marcador — a guarda não exige nem proíbe ali). A seção
# `## Arquivado` encerra a contagem, como em `kanban-status.sh`.
BOARD_BASE = """# Board de teste (fixture do T-086, não é o board real)

## Em curso
- [~] `T-900` Card fictício em implementação — nota @claude
- [>] `T-901` Card fictício em planejamento — nota @codex

## Fila
- [ ] `T-902` Card fictício no backlog — nota

## Aguardando o dono
- [!] `T-903` Card fictício aguardando decisão — nota

## Encerrados
- [?] `T-904` Card fictício em validação — nota
- [x] `T-905` Card fictício concluído — nota

## Arquivado
- [x] `T-800` Card fictício antigo, sem marcador — nota
"""


def run_lint_main(root: Path, home: Path) -> tuple[int, str]:
    """Mesma estratégia de `test_write_flag_guard.py::run_lint_main`: roda a
    CÓPIA do lint dentro de `root` como subprocesso (a exclusão de
    autovarredura de `main()` compara `Path(__file__)` com cada arquivo
    varrido, e só bate certo rodando a cópia como processo próprio), com
    `HOME` isolado para a guarda de cache do T-017 não acusar ruído desta
    máquina.
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


class HostMarkerGuardTest(unittest.TestCase):
    """Fixture: cópia completa do repositório real, com o `KANBAN.md`
    rastreado substituído pelo board sintético `BOARD_BASE`. `setUp` roda
    antes de CADA método — cada um começa de uma árvore limpa.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-host-marker-guard-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        shutil.copytree(REPO_ROOT, self.root, ignore=shutil.ignore_patterns(".git"))
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()
        self.board = self.root / "memory" / "wiki" / "KANBAN.md"
        self.board.write_text(BOARD_BASE, encoding="utf-8")

    def test_board_sintetico_sem_mutacao_passa(self) -> None:
        """Controle negativo: um board bem-formado, com marcador nos dois
        estados em curso e sem marcador nos demais, não aciona a guarda nova
        (nem nenhuma outra). Se isto falhar, o defeito é da guarda (falso
        positivo), não do board de exemplo."""
        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 0, output)

    def test_card_em_curso_sem_marcador_reprova(self) -> None:
        """Vermelho 1: card em `[~]` sem `@claude` nem `@codex`."""
        mutado = BOARD_BASE.replace(
            "- [~] `T-900` Card fictício em implementação — nota @claude",
            "- [~] `T-900` Card fictício em implementação — nota",
            1,
        )
        self.assertNotEqual(mutado, BOARD_BASE, "a substituição precisa casar de fato")
        self.board.write_text(mutado, encoding="utf-8")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("KANBAN.md", output)
        self.assertIn("T-900", output)
        self.assertIn("sem marcador de host", output)

    def test_card_com_dois_marcadores_de_host_reprova(self) -> None:
        """Vermelho 2: `@claude` e `@codex` juntos na mesma linha — posse
        ambígua é o mesmo defeito que posse ausente."""
        mutado = BOARD_BASE.replace(
            "- [>] `T-901` Card fictício em planejamento — nota @codex",
            "- [>] `T-901` Card fictício em planejamento — nota @codex @claude",
            1,
        )
        self.assertNotEqual(mutado, BOARD_BASE, "a substituição precisa casar de fato")
        self.board.write_text(mutado, encoding="utf-8")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("T-901", output)
        self.assertIn("@claude", output)
        self.assertIn("@codex", output)

    def test_card_fora_do_estado_em_curso_com_marcador_sobrando_reprova(self) -> None:
        """Vermelho 3: card em `[ ]`, `[?]` ou `[x]` com marcador de host —
        ele mentiria sobre quem ainda está com o card fora dos dois estados
        em que a posse é declarada."""
        mutado = BOARD_BASE.replace(
            "- [ ] `T-902` Card fictício no backlog — nota",
            "- [ ] `T-902` Card fictício no backlog — nota @claude",
            1,
        )
        self.assertNotEqual(mutado, BOARD_BASE, "a substituição precisa casar de fato")
        self.board.write_text(mutado, encoding="utf-8")

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("T-902", output)
        self.assertIn("marcador de host", output)


    # ── Falsos verdes reproduzidos na revisão de 2026-09-08 ────────────────
    # Cada um destes passava ANTES do endurecimento: a guarda dizia "ok" para
    # um card sem responsável declarado, que é pior que acusar falta, porque
    # parece conferido.

    def test_marcador_dentro_de_palavra_maior_nao_declara_posse(self) -> None:
        """`@claude-legado` não é o host `@claude`. A versão anterior usava
        `\b`, e entre `e` e `-` existe fronteira de palavra — o token casava
        e o card passava sem dono."""
        self.board.write_text(
            BOARD_BASE.replace("nota @claude", "nota sobre @claude-legado", 1),
            encoding="utf-8",
        )

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("T-900", output)

    def test_marcador_em_trecho_citado_nao_declara_posse(self) -> None:
        """Marcador dentro de crase ou de comentário HTML é conteúdo — um card
        que documente o token não está reivindicando posse."""
        for citado in ("`@claude`", "<!-- @claude -->"):
            with self.subTest(citado=citado):
                self.board.write_text(
                    BOARD_BASE.replace("nota @claude", f"nota {citado}", 1),
                    encoding="utf-8",
                )

                result, output = run_lint_main(self.root, self.home)

                self.assertEqual(result, 1, output)
                self.assertIn("T-900", output)

    def test_linha_que_parece_card_mas_foge_do_contrato_e_denunciada(self) -> None:
        """Card indentado, com ID sem crase ou espaço a mais escapava inteiro
        do regex estrito e o lint terminava verde."""
        for fora_do_contrato in (
            "  - [~] `T-906` Indentado, sem host",
            "- [~] T-907 Sem crase no ID, sem host",
            "* [~] `T-908` Bullet diferente, sem host",
        ):
            with self.subTest(linha=fora_do_contrato):
                self.board.write_text(
                    BOARD_BASE.replace("## Fila", f"## Fila\n{fora_do_contrato}", 1),
                    encoding="utf-8",
                )

                result, output = run_lint_main(self.root, self.home)

                self.assertEqual(result, 1, output)
                self.assertIn("parece card", output)

    def test_titulo_parecido_com_arquivado_nao_desliga_a_guarda(self) -> None:
        """`[Aa]rquiv` casava em "Arquivos compartilhados", e um título assim
        apagava a verificação até o fim do arquivo."""
        self.board.write_text(
            BOARD_BASE.replace(
                "## Fila",
                "## Arquivos compartilhados\n\n- [~] `T-909` Depois do titulo, sem host\n\n## Fila",
                1,
            ),
            encoding="utf-8",
        )

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("T-909", output)

    def test_arquivado_dentro_de_bloco_de_codigo_nao_desliga_a_guarda(self) -> None:
        """Um exemplo cercado por crases não é a seção de arquivados."""
        self.board.write_text(
            BOARD_BASE.replace(
                "## Fila",
                "```\n## Arquivado\n```\n\n- [~] `T-910` Fora do bloco, sem host\n\n## Fila",
                1,
            ),
            encoding="utf-8",
        )

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("T-910", output)

    def test_cabecalhos_adversariais_nao_desligam_posse(self) -> None:
        titulos = (
            "## Como arquivar",
            "## Não arquivados",
            "## Arquivos",
            "## Arquivados pendentes",
            "# Arquivado",
            "### Arquivado",
            "#### Arquivado",
            "##Arquivado",
            "## Arquivado ##",
            " ## Arquivado",
            "## ARQUİVADOS",
            "##\u00a0Arquivado",
            "##\u2003Arquivado",
            "##\u200bArquivado",
            "## arquıvados",
            "## arquivadoſ",
            "## Аrquivado",
            "## Arquivadо",
            "## Ａrquivado",
            "## Arquivado\u00a0",
            "## Arquivado 📦",
            "## 📦",
            "## 📦📦 Arquivado",
            "## 📦️ Arquivado",
        )
        for titulo in titulos:
            with self.subTest(titulo=titulo):
                self.board.write_text(
                    BOARD_BASE.replace(
                        "## Fila",
                        f"{titulo}\n- [~] `T-911` Sem host — nota\n\n## Fila",
                        1,
                    ),
                    encoding="utf-8",
                )
                result, output = run_lint_main(self.root, self.home)
                self.assertEqual(result, 1, output)
                self.assertIn("T-911", output)

    def test_separadores_que_nao_sao_lf_nao_viram_quebra_de_linha(self) -> None:
        separadores = (
            "\rtexto",
            "\x0b",
            "\x0c",
            "\x1c",
            "\x1d",
            "\x1e",
            "\x85",
            "\u2028",
            "\u2029",
        )
        for separador in separadores:
            with self.subTest(separador=repr(separador)):
                self.board.write_text(
                    BOARD_BASE.replace(
                        "## Arquivado",
                        f"## Arquivado{separador}\n- [~] `T-917` Vivo sem host — nota",
                        1,
                    ),
                    encoding="utf-8",
                )
                result, output = run_lint_main(self.root, self.home)
                self.assertEqual(result, 1, output)
                self.assertIn("T-917", output)

    def test_titulo_parecido_na_posicao_historica_nao_desliga_posse(self) -> None:
        self.board.write_text(
            BOARD_BASE.replace(
                "## Arquivado",
                "## Arquivados pendentes\n- [~] `T-918` Vivo sem host — nota",
                1,
            ),
            encoding="utf-8",
        )
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 1, output)
        self.assertIn("T-918", output)

    def test_cabecalhos_exatos_desligam_posse_historica(self) -> None:
        titulos = (
            "## Arquivo",
            "## Arquivado",
            "## Arquivada",
            "## ARQUIVADOS",
            "## ArQuIvAdAs",
            "## 📦Arquivado",
            "##\t📦\tArquivadas",
        )
        for titulo in titulos:
            with self.subTest(titulo=titulo):
                self.board.write_text(
                    BOARD_BASE.replace(
                        "## Arquivado",
                        f"{titulo}\n- [~] `T-911` Histórico sem host — nota",
                        1,
                    ),
                    encoding="utf-8",
                )
                result, output = run_lint_main(self.root, self.home)
                self.assertEqual(result, 0, output)
                self.assertNotIn("T-911", output)

    def test_cabecalho_exato_com_crlf_desliga_posse_historica(self) -> None:
        mutado = BOARD_BASE.replace(
            "## Arquivado",
            "##\t📦\tARQUIVADOS\n- [~] `T-916` Histórico sem host — nota",
            1,
        )
        self.board.write_bytes(mutado.replace("\n", "\r\n").encode("utf-8"))
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 0, output)
        self.assertNotIn("T-916", output)

    def test_cabecalho_arquivado_em_cercas_validas_nao_desliga_posse(self) -> None:
        cercas = {
            "fechamento_curto": ("````", "```", "## Arquivados", "````"),
            "marcador_trocado": ("```", "~~~", "## Arquivados", "```"),
            "fechamento_com_texto": ("```", "``` texto", "## Arquivados", "```"),
            "indentacao_tres": ("   ```", "## Arquivados", "   ```"),
            "til_com_info": ("~~~ info ` permitida", "## Arquivados", "~~~"),
            "fechamento_maior": ("```", "## Arquivados", "````"),
            "fechamento_com_espacos": ("```", "## Arquivados", "``` \t"),
            "fechamento_indentado": ("```", "## Arquivados", "   ```"),
        }
        for nome, trecho in cercas.items():
            with self.subTest(caso=nome):
                bloco = "\n".join((*trecho, "- [~] `T-912` Fora da cerca, sem host — nota"))
                self.board.write_text(
                    BOARD_BASE.replace("## Fila", f"{bloco}\n\n## Fila", 1),
                    encoding="utf-8",
                )
                result, output = run_lint_main(self.root, self.home)
                self.assertEqual(result, 1, output)
                self.assertIn("T-912", output)

    def test_cerca_com_crlf_fecha_e_reativa_guarda(self) -> None:
        bloco = "\n".join(
            ("```", "## Arquivados", "```` \t", "- [~] `T-919` Fora da cerca, sem host — nota")
        )
        mutado = BOARD_BASE.replace("## Fila", f"{bloco}\n\n## Fila", 1)
        self.board.write_bytes(mutado.replace("\n", "\r\n").encode("utf-8"))
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 1, output)
        self.assertIn("T-919", output)

    def test_titulo_real_depois_da_cerca_desliga_posse(self) -> None:
        bloco = "\n".join(
            (
                "```",
                "## Arquivados",
                "```",
                "## 📦 Arquivo",
                "- [~] `T-920` Histórico sem host — nota",
            )
        )
        self.board.write_text(
            BOARD_BASE.replace("## Arquivado", bloco, 1), encoding="utf-8"
        )
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 0, output)
        self.assertNotIn("T-920", output)

    def test_fechamento_com_quatro_espacos_nao_reativa_guarda(self) -> None:
        bloco = "\n".join(
            ("```", "    ```", "- [~] `T-921` Exemplo sem host — nota")
        )
        self.board.write_text(
            BOARD_BASE.replace("## Fila", f"{bloco}\n\n## Fila", 1), encoding="utf-8"
        )
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 0, output)
        self.assertNotIn("T-921", output)

    def test_quatro_espacos_nao_abrem_cerca_para_a_guarda(self) -> None:
        bloco = "\n".join(
            (
                "    ```",
                "## Arquivados",
                "```",
                "- [~] `T-913` Histórico sem host — nota",
            )
        )
        self.board.write_text(
            BOARD_BASE.replace("## Fila", f"{bloco}\n\n## Fila", 1),
            encoding="utf-8",
        )
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 0, output)
        self.assertNotIn("T-913", output)

    def test_abertura_invalida_por_crase_no_info_nao_esconde_titulo(self) -> None:
        bloco = "\n".join(
            (
                "```info`invalida",
                "## Arquivados",
                "```",
                "- [~] `T-914` Histórico sem host — nota",
            )
        )
        self.board.write_text(
            BOARD_BASE.replace("## Fila", f"{bloco}\n\n## Fila", 1),
            encoding="utf-8",
        )
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 0, output)
        self.assertNotIn("T-914", output)

    def test_cerca_sem_fechamento_ignora_exemplo_historico(self) -> None:
        bloco = "\n".join(
            (
                "```",
                "- [~] `T-915` Exemplo sem host — nota",
            )
        )
        self.board.write_text(
            BOARD_BASE.replace("## Fila", f"{bloco}\n\n## Fila", 1),
            encoding="utf-8",
        )
        result, output = run_lint_main(self.root, self.home)
        self.assertEqual(result, 0, output)
        self.assertNotIn("T-915", output)

    def test_marca_sobrando_reprova_em_cada_estado_proibido(self) -> None:
        """A mutação da revisão mostrou o buraco: tirar `[?]` e `[x]` da
        proibição deixava todos os testes verdes. Cada estado é exercitado
        separadamente para que a regressão em qualquer um deles caia aqui."""
        casos = {
            " ": ("`T-902` Card fictício no backlog — nota", "[ ]"),
            "?": ("`T-904` Card fictício em validação — nota", "[?]"),
            "x": ("`T-905` Card fictício concluído — nota", "[x]"),
        }
        for estado, (trecho, rotulo) in casos.items():
            with self.subTest(estado=rotulo):
                self.board.write_text(
                    BOARD_BASE.replace(trecho, trecho + " @claude", 1), encoding="utf-8"
                )

                result, output = run_lint_main(self.root, self.home)

                self.assertEqual(result, 1, output)
                self.assertIn("ainda tem marcador de host", output)

    def test_aguardando_o_dono_recusa_posse_ambigua(self) -> None:
        """`[!]` preserva a posse de quem estacionou — mas dois hosts ali é o
        mesmo defeito que posse ausente."""
        self.board.write_text(
            BOARD_BASE.replace(
                "`T-903` Card fictício aguardando decisão — nota",
                "`T-903` Card fictício aguardando decisão — nota @claude @codex",
                1,
            ),
            encoding="utf-8",
        )

        result, output = run_lint_main(self.root, self.home)

        self.assertEqual(result, 1, output)
        self.assertIn("T-903", output)


if __name__ == "__main__":
    unittest.main()
