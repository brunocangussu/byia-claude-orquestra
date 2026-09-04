"""Testes do `kanban-status.sh` — o parser do board.

Por que estes testes existem: o `kanban-status.sh` é o contrato do board e, até
2026-09-02, **nenhum teste o cobria**. Ele já falhou em silêncio antes (`T-015`:
contagem errada sem nenhum `⚠`), e a statusline é o único lugar onde a falha
apareceria — de relance, para quem não está procurando.

O caso que mais importa aqui é o do teto em **bytes**: com locale UTF-8, um awk
que use `length()` conta caracteres, e a mesma linha cabe numa máquina e estoura
noutra. O teste roda com um locale explícito para provar que a régua não depende
do ambiente.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "kanban-status.sh"
TETO = 240


def rodar(board_texto: str | None, *, locale: str | None = None) -> subprocess.CompletedProcess:
    """Monta um projeto temporário com esse board e devolve a saída do script."""
    tmp = tempfile.mkdtemp()
    if board_texto is not None:
        wiki = Path(tmp) / "memory" / "wiki"
        wiki.mkdir(parents=True)
        (wiki / "KANBAN.md").write_text(board_texto, encoding="utf-8")
    env = dict(os.environ)
    if locale is not None:
        env["LC_ALL"] = locale
        env["LANG"] = locale
    return subprocess.run(
        ["sh", str(SCRIPT), tmp],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def card(marcador: str, cid: str, titulo: str, nota: str = "n") -> str:
    return f"- [{marcador}] `{cid}` {titulo} — {nota}"


class KanbanStatusContagemTest(unittest.TestCase):
    def test_board_ausente_sai_vazio_e_zero(self):
        """Projeto sem board não é erro — é projeto sem board.

        O guardião pós-compactação vai depender disto: precisa distinguir
        "sem board" de "falhou ao ler o board".
        """
        r = rodar(None)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_conta_cards_e_progresso(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "a"),
                card("x", "T-002", "b"),
                card("?", "T-003", "c"),
                card("~", "T-004", "d"),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(1/4)", saida)
        self.assertIn("⏳1", saida)
        self.assertIn("25%", saida)

    def test_linha_fora_do_contrato_vira_alerta(self):
        board = "\n".join(["# board", card(" ", "T-001", "a"), "**- [ ]** `T-002` negrito no marcador"])
        saida = rodar(board).stdout
        self.assertIn("⚠1", saida)

    def test_secao_arquivada_encerra_a_contagem(self):
        board = "\n".join(
            ["# board", card(" ", "T-001", "a"), "## Arquivado", card("x", "T-900", "velho")]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/1)", saida)


class KanbanStatusTetoTest(unittest.TestCase):
    """O teto da linha do card — `_schema.md`, seção "O teto da linha"."""

    def test_card_dentro_do_teto_nao_acende_sinal(self):
        board = "\n".join(["# board", card(" ", "T-001", "curto")])
        self.assertNotIn("📏", rodar(board).stdout)

    def test_card_acima_do_teto_acende_o_sinal_de_regua(self):
        gordo = card(" ", "T-002", "t", "x" * 400)
        board = "\n".join(["# board", card(" ", "T-001", "curto"), gordo])
        self.assertIn("📏1", rodar(board).stdout)

    def test_sinal_do_teto_e_distinto_do_sinal_de_contrato(self):
        """`⚠` e `📏` são doenças diferentes e não podem se somar.

        `⚠` é contrato quebrado — raro, acionável na hora. `📏` é dívida
        acumulada, acesa durante toda uma migração. Fundir os dois deixaria o
        `⚠` cronicamente aceso, e alarme crônico é alarme ignorado.
        """
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "t", "x" * 400),
                "**- [ ]** `T-002` fora do contrato",
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("⚠1", saida)
        self.assertIn("📏1", saida)

    def test_teto_conta_bytes_e_nao_caracteres(self):
        """A régua é byte UTF-8, e não pode variar com o locale.

        Esta linha tem menos de 240 *caracteres* e mais de 240 *bytes*: cada
        "ç" ocupa dois. Um contador que meça caracteres a considera dentro do
        teto; um que meça bytes a reprova. O teste fixa a resposta esperada
        (reprovar) e roda sob locale UTF-8, que é justamente onde `length()` do
        awk deixaria de contar bytes.
        """
        nota = "ç" * 130  # 130 caracteres, 260 bytes
        linha = card(" ", "T-001", "t", nota)
        self.assertLess(len(linha), TETO, "premissa: cabe contando caracteres")
        self.assertGreater(len(linha.encode("utf-8")), TETO, "premissa: estoura contando bytes")

        board = "\n".join(["# board", linha])
        self.assertIn("📏1", rodar(board, locale="pt_BR.UTF-8").stdout)
        self.assertIn("📏1", rodar(board, locale="C").stdout)

    def test_fronteira_exata_do_teto(self):
        """240 cabe; 241 não. É onde mora o off-by-one.

        Um teto testado só com linha muito curta e linha muito longa passa com
        `>=` no lugar de `>` e ninguém percebe — até alguém escrever um card no
        limite exato e ser reprovado por um byte que a regra dizia caber.
        """
        prefixo = "- [ ] `T-020` t — "
        for n, esperado in ((239, False), (240, False), (241, True)):
            with self.subTest(bytes=n):
                linha = prefixo + "a" * (n - len(prefixo.encode("utf-8")))
                self.assertEqual(len(linha.encode("utf-8")), n, "premissa do teste")
                saida = rodar("# b\n" + linha + "\n").stdout
                self.assertEqual("📏" in saida, esperado)

    def test_board_com_crlf_ainda_e_medido(self):
        """Board salvo no Windows não escapa da régua."""
        gordo = card(" ", "T-030", "t", "x" * 400)
        saida = rodar("# b\r\n" + gordo + "\r\n").stdout
        self.assertIn("📏1", saida)

    def test_crlf_nao_empurra_card_no_limite_para_fora_do_teto(self):
        """O `\\r` é terminador de linha, não conteúdo — e não pode contar.

        Sem descontá-lo, um card de exatamente 240 bytes acende `📏` só porque
        o arquivo veio com CRLF: o mesmo board reprovaria ou passaria conforme
        quem o salvou. O teto mede o card, não o checkout.
        """
        prefixo = "- [ ] `T-040` t — "
        linha = prefixo + "a" * (TETO - len(prefixo.encode("utf-8")))
        self.assertEqual(len(linha.encode("utf-8")), TETO, "premissa do teste")
        self.assertNotIn("📏", rodar("# b\r\n" + linha + "\r\n").stdout)

    def test_linha_indentada_nao_e_card_e_nao_entra_na_regua(self):
        """Sub-item indentado não é card — nem para contar, nem para medir.

        Ele já aparece como `⚠` por parecer card fora do contrato. Contá-lo
        também no `📏` acusaria a mesma linha duas vezes, por dois motivos
        diferentes, e mandaria encurtar algo que nem card é.
        """
        board = "\n".join(["# b", card(" ", "T-001", "ok"), "  " + card(" ", "T-002", "t", "x" * 400)])
        saida = rodar(board).stdout
        self.assertIn("⚠1", saida)
        self.assertNotIn("📏", saida)

    def test_card_arquivado_nao_conta_para_o_teto(self):
        """Arquivado sai da contagem de progresso — e da régua também.

        Senão a dívida de um card encerrado ficaria acesa para sempre, sem
        ninguém poder apagá-la a não ser reescrevendo história.
        """
        board = "\n".join(
            ["# board", card(" ", "T-001", "curto"), "## Arquivado", card("x", "T-900", "t", "x" * 400)]
        )
        self.assertNotIn("📏", rodar(board).stdout)


class KanbanStatusFalhaDaMedicaoTest(unittest.TestCase):
    """"Não consegui medir" ≠ "está tudo dentro do teto".

    Este é o modo de falha que uma statusline não denuncia sozinha: se a
    contagem quebrar e o sinal simplesmente sumir, o board pode ter dezenas de
    cards fora do teto e a barra dizer que está tudo bem. A distinção é `📏?`.
    """

    def _script_com_medicao_quebrada(self, destino: Path) -> Path:
        fonte = SCRIPT.read_text(encoding="utf-8")
        quebrado = fonte.replace("LC_ALL=C awk -v teto", "LC_ALL=C awk-que-nao-existe -v teto")
        self.assertNotEqual(fonte, quebrado, "a substituição precisa casar de fato")
        alvo = destino / "kanban-status-quebrado.sh"
        alvo.write_text(quebrado, encoding="utf-8")
        return alvo

    def test_falha_na_medicao_aparece_como_interrogacao(self):
        tmp = Path(tempfile.mkdtemp())
        wiki = tmp / "memory" / "wiki"
        wiki.mkdir(parents=True)
        (wiki / "KANBAN.md").write_text("# b\n" + card(" ", "T-001", "t") + "\n", encoding="utf-8")

        alvo = self._script_com_medicao_quebrada(tmp)
        r = subprocess.run(["sh", str(alvo), str(tmp)], capture_output=True, text=True, check=False)

        self.assertIn("📏?", r.stdout, "falha silenciosa: o sinal sumiu em vez de virar 📏?")
        self.assertIn("(0/1)", r.stdout, "o resto da statusline tem que continuar funcionando")
        self.assertEqual(r.returncode, 0, "statusline não pode matar o prompt")


if __name__ == "__main__":
    unittest.main()
