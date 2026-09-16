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

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "kanban-status.sh"
STATUSLINE = Path(__file__).resolve().parent / "statusline.sh"
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


def locales_de_teste() -> tuple[str, str]:
    """Garante que o segundo passe roda de fato sob um locale UTF-8."""
    disponiveis = subprocess.run(
        ["locale", "-a"], capture_output=True, text=True, check=True
    ).stdout.splitlines()
    preferido = next((item for item in disponiveis if item.lower() == "pt_br.utf-8"), None)
    if preferido is None:
        preferido = next(
            (
                item
                for item in disponiveis
                if "utf" in item.lower() and item.lower() not in {"c.utf-8", "c.utf8"}
            ),
            None,
        )
    if preferido is None:
        raise AssertionError("nenhum locale UTF-8 não-C disponível para o teste")
    return "C", preferido


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

    def test_titulos_parecidos_nao_cortam_contagem_nem_regua(self):
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
        for locale in locales_de_teste():
            for titulo in titulos:
                with self.subTest(locale=locale, titulo=titulo):
                    board = "\n".join(
                        [
                            "# board",
                            card(" ", "T-001", "ativo"),
                            titulo,
                            card(" ", "T-002", "longo", "x" * 400),
                        ]
                    )
                    saida = rodar(board, locale=locale).stdout
                    self.assertIn("(0/2)", saida)
                    self.assertIn("📏1", saida)

    def test_titulos_exatos_cortam_contagem_e_regua(self):
        titulos = (
            "## Arquivo",
            "## Arquivado",
            "## Arquivada",
            "## ARQUIVADOS",
            "## ArQuIvAdAs",
            "##  Arquivado",
            "## Arquivado   ",
            "##\tArquivado\t",
            "## 📦Arquivado",
            "##\t📦\tArquivadas",
        )
        for locale in locales_de_teste():
            for titulo in titulos:
                with self.subTest(locale=locale, titulo=titulo):
                    board = "\r\n".join(
                        [
                            "# board",
                            card(" ", "T-001", "ativo"),
                            titulo,
                            card(" ", "T-900", "histórico", "x" * 400),
                        ]
                    )
                    saida = rodar(board, locale=locale).stdout
                    self.assertIn("(0/1)", saida)
                    self.assertNotIn("📏", saida)

    def test_titulo_arquivado_dentro_de_cerca_nao_corta(self):
        cercas = {
            "fechamento_curto": ("````", "```", "## Arquivados", "````"),
            "marcador_trocado": ("```", "~~~", "## Arquivados", "```"),
            "fechamento_com_texto": ("```", "``` texto", "## Arquivados", "```"),
            "indentacao_tres": ("   ```", "## Arquivados", "   ```"),
            "fechamento_maior": ("```", "## Arquivados", "````"),
            "fechamento_com_espacos": ("```", "## Arquivados", "``` \t"),
            "fechamento_indentado": ("```", "## Arquivados", "   ```"),
            "til_com_info": ("~~~ info ` permitida", "## Arquivados", "~~~"),
        }
        for nome, trecho in cercas.items():
            with self.subTest(caso=nome):
                board = "\n".join(
                    [
                        "# board",
                        card(" ", "T-001", "ativo"),
                        *trecho,
                        card(" ", "T-002", "longo", "x" * 400),
                    ]
                )
                saida = rodar(board).stdout
                self.assertIn("(0/2)", saida)
                self.assertIn("📏1", saida)

    def test_cerca_com_crlf_fecha_e_preserva_card_ativo(self):
        board = "\r\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "```",
                "## Arquivados",
                "```` \t",
                card(" ", "T-002", "longo", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/2)", saida)
        self.assertIn("📏1", saida)

    def test_fechamento_com_quatro_espacos_nao_fecha_cerca(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "```",
                "    ```",
                card(" ", "T-002", "exemplo", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/1)", saida)
        self.assertNotIn("📏", saida)

    def test_setext_nao_corta_contagem_nem_regua(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "Arquivado",
                "----------",
                card(" ", "T-002", "longo", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/2)", saida)
        self.assertIn("📏1", saida)

    def test_quatro_espacos_nao_abrem_cerca(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "    ```",
                "## Arquivados",
                card(" ", "T-900", "histórico", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/1)", saida)
        self.assertNotIn("📏", saida)

    def test_crase_na_info_impede_abertura_da_cerca(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "```info`invalida",
                "## Arquivados",
                "```",
                card(" ", "T-900", "histórico", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/1)", saida)
        self.assertNotIn("📏", saida)

    def test_cerca_sem_fechamento_ignora_o_restante(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "```",
                "## Arquivados",
                card(" ", "T-002", "exemplo", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/1)", saida)
        self.assertNotIn("📏", saida)

    def test_titulo_arquivado_real_depois_da_cerca_corta(self):
        board = "\n".join(
            [
                "# board",
                card(" ", "T-001", "ativo"),
                "```",
                "## Arquivados",
                "```",
                "## 📦 Arquivo",
                card("x", "T-900", "histórico", "x" * 400),
            ]
        )
        saida = rodar(board).stdout
        self.assertIn("(0/1)", saida)
        self.assertNotIn("📏", saida)


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


class KanbanStatusCheckoutPrincipalTest(unittest.TestCase):
    def test_worktree_antigo_le_o_board_do_checkout_principal(self):
        """O board operacional não pode bifurcar entre worktrees Git."""
        with tempfile.TemporaryDirectory() as tmp:
            principal = Path(tmp) / "principal"
            principal.mkdir()
            subprocess.run(["git", "init", str(principal)], check=True, capture_output=True, text=True)
            subprocess.run(["git", "-C", str(principal), "config", "user.email", "teste@example.com"], check=True)
            subprocess.run(["git", "-C", str(principal), "config", "user.name", "Teste"], check=True)

            board = principal / "memory" / "wiki" / "KANBAN.md"
            board.parent.mkdir(parents=True)
            board.write_text("# board\n" + card(" ", "T-001", "primeiro") + "\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(principal), "add", "memory/wiki/KANBAN.md"], check=True)
            subprocess.run(["git", "-C", str(principal), "commit", "-m", "board inicial"], check=True, capture_output=True, text=True)

            board.write_text(
                "# board\n" + card(" ", "T-001", "primeiro") + "\n" + card(" ", "T-002", "segundo") + "\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(principal), "add", "memory/wiki/KANBAN.md"], check=True)
            subprocess.run(["git", "-C", str(principal), "commit", "-m", "board atual"], check=True, capture_output=True, text=True)

            worktree = Path(tmp) / "frente-antiga"
            subprocess.run(
                ["git", "-C", str(principal), "worktree", "add", "--detach", str(worktree), "HEAD~1"],
                check=True,
                capture_output=True,
                text=True,
            )

            resultado = subprocess.run(
                ["sh", str(SCRIPT), str(worktree)], capture_output=True, text=True, check=False
            )

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertIn("(0/2)", resultado.stdout)


class KanbanStatusResolverTest(unittest.TestCase):
    def _git(self, directory: Path, *args: str, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(directory), *args], check=True, capture_output=True, text=True, **kwargs)

    def _iniciar_repo(self, principal: Path, board_texto: str | None) -> None:
        principal.mkdir()
        subprocess.run(["git", "init", str(principal)], check=True, capture_output=True, text=True)
        self._git(principal, "config", "user.email", "teste@example.com")
        self._git(principal, "config", "user.name", "Teste")
        if board_texto is not None:
            board = principal / "memory" / "wiki" / "KANBAN.md"
            board.parent.mkdir(parents=True)
            board.write_text(board_texto, encoding="utf-8")
            self._git(principal, "add", "memory/wiki/KANBAN.md")
            self._git(principal, "commit", "-m", "board inicial")

    def _resolver(self, directory: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["sh", str(SCRIPT), "--resolver", str(directory)], capture_output=True, text=True, env=env, check=False
        )

    def _fake_git(self, directory: Path, body: str) -> dict[str, str]:
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        fake = directory / "bin"
        fake.mkdir(exist_ok=True)
        (fake / "git").write_text("#!/bin/sh\n" + body, encoding="utf-8")
        (fake / "git").chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = f"{fake}{os.pathsep}{env.get('PATH', '')}"
        env["REAL_GIT"] = str(real_git)
        return env

    def test_raiz_subpasta_e_detached_usam_o_mesmo_board_principal_com_caminho_complexo(self):
        with tempfile.TemporaryDirectory() as tmp:
            principal = Path(tmp) / "principal espaço ü\nquebra"
            self._iniciar_repo(principal, "# board\n" + card(" ", "T-001", "primeiro") + "\n")
            board = principal / "memory" / "wiki" / "KANBAN.md"
            board.write_text(
                "# board\n" + card(" ", "T-001", "primeiro") + "\n" + card(" ", "T-002", "segundo") + "\n",
                encoding="utf-8",
            )
            self._git(principal, "add", "memory/wiki/KANBAN.md")
            self._git(principal, "commit", "-m", "board atual")

            worktree = Path(tmp) / "frente espaço ü\nquebra"
            self._git(principal, "worktree", "add", "--detach", str(worktree), "HEAD~1")
            subpasta = worktree / "sub espaço ü\nquebra"
            subpasta.mkdir()

            esperado = os.path.realpath(principal / "memory" / "wiki" / "KANBAN.md")
            for origem in (worktree, subpasta):
                structured = self._resolver(origem)
                self.assertEqual(structured.returncode, 0, structured.stderr)
                info = json.loads(structured.stdout)
                self.assertEqual(
                    info,
                    {
                        "state": "ok",
                        "code": None,
                        "board": esperado,
                        "front_root": os.path.realpath(worktree),
                        "thread_root": os.path.realpath(worktree / "memory" / "wiki"),
                        "exists": True,
                        "provenance": "worktree",
                    },
                )
                normal = subprocess.run(["sh", str(SCRIPT), str(origem)], capture_output=True, text=True, check=False)
                self.assertEqual(normal.returncode, 0, normal.stderr)
                self.assertIn("(0/2)", normal.stdout)

    def test_sem_git_mantem_board_local_e_principal_sem_board_nao_usa_copia_antiga(self):
        with tempfile.TemporaryDirectory() as tmp:
            sem_git = Path(tmp) / "sem-git"
            sem_git.mkdir()
            local = self._resolver(sem_git)
            self.assertEqual(local.returncode, 0, local.stderr)
            self.assertEqual(
                json.loads(local.stdout),
                {
                    "state": "ok",
                    "code": None,
                    "board": os.path.realpath(sem_git / "memory" / "wiki" / "KANBAN.md"),
                    "front_root": os.path.realpath(sem_git),
                    "thread_root": os.path.realpath(sem_git / "memory" / "wiki"),
                    "exists": False,
                    "provenance": "local",
                },
            )

            principal = Path(tmp) / "principal"
            self._iniciar_repo(principal, "# board\n" + card(" ", "T-001", "antigo") + "\n")
            self._git(principal, "rm", "memory/wiki/KANBAN.md")
            self._git(principal, "commit", "-m", "remove board")
            worktree = Path(tmp) / "frente-antiga"
            self._git(principal, "worktree", "add", "--detach", str(worktree), "HEAD~1")

            structured = self._resolver(worktree)
            self.assertEqual(structured.returncode, 0, structured.stderr or structured.stdout)
            info = json.loads(structured.stdout)
            self.assertFalse(info["exists"])
            self.assertEqual(info["provenance"], "worktree")
            normal = subprocess.run(["sh", str(SCRIPT), str(worktree)], capture_output=True, text=True, check=False)
            self.assertEqual(normal.stdout, "")

    def test_git_ausente_com_metadado_nao_aceita_board_local_stale(self):
        """Sem binário Git, `.git` ainda impede provar que o board local vale."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            principal = raiz / "principal"
            self._iniciar_repo(principal, "# board\n" + card(" ", "T-001", "stale") + "\n")

            ferramentas = raiz / "sem-git"
            ferramentas.mkdir()
            python = sys.executable
            shell = shutil.which("sh")
            self.assertIsNotNone(python)
            self.assertIsNotNone(shell)
            (ferramentas / "python3").symlink_to(python)
            (ferramentas / "sh").symlink_to(shell)
            env = dict(os.environ)
            env["PATH"] = str(ferramentas)

            structured = self._resolver(principal, env=env)
            self.assertEqual(structured.returncode, 2)
            self.assertEqual(json.loads(structured.stdout)["code"], "git-indisponivel")
            normal = subprocess.run(
                ["/bin/sh", str(SCRIPT), str(principal)], capture_output=True, text=True, env=env, check=False
            )
            self.assertIn("⚠ quadro: checkout principal indisponível", normal.stdout)
            self.assertNotIn("(0/1)", normal.stdout)

    def test_git_ausente_com_link_git_quebrado_nao_aceita_board_local_stale(self):
        """`lexists` preserva o sinal de um `.git` cujo destino já desapareceu."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            local = raiz / "local"
            board = local / "memory" / "wiki" / "KANBAN.md"
            board.parent.mkdir(parents=True)
            board.write_text("# board\n" + card(" ", "T-001", "stale") + "\n", encoding="utf-8")
            (local / ".git").symlink_to(raiz / "metadados-ausentes")

            ferramentas = raiz / "sem-git"
            ferramentas.mkdir()
            python = sys.executable
            shell = shutil.which("sh")
            self.assertIsNotNone(shell)
            (ferramentas / "python3").symlink_to(python)
            (ferramentas / "sh").symlink_to(shell)
            env = dict(os.environ)
            env["PATH"] = str(ferramentas)

            structured = self._resolver(local, env=env)
            self.assertEqual(structured.returncode, 2)
            self.assertEqual(json.loads(structured.stdout)["code"], "git-indisponivel")

            normal = subprocess.run(
                ["/bin/sh", str(SCRIPT), str(local)], capture_output=True, text=True, env=env, check=False
            )
            self.assertIn("⚠ quadro: checkout principal indisponível", normal.stdout)
            self.assertNotIn("(0/1)", normal.stdout)

    def test_resolver_devolve_erro_estruturado_se_git_some_antes_da_lista_worktree(self):
        """O sentinel de OSError da listagem não pode vazar AttributeError."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            principal = raiz / "principal"
            self._iniciar_repo(principal, "# board\n")
            contador = raiz / "chamadas-git"
            env = self._fake_git(
                raiz,
                """contador=0
if [ -r \"$GIT_CALL_COUNT_FILE\" ]; then
  IFS= read -r contador < \"$GIT_CALL_COUNT_FILE\"
fi
contador=$((contador + 1))
printf '%s\\n' \"$contador\" > \"$GIT_CALL_COUNT_FILE\"
if [ \"$contador\" -eq 4 ]; then
  /bin/rm \"$0\"
fi
exec \"$REAL_GIT\" \"$@\"
""",
            )
            ferramentas = raiz / "bin"
            (ferramentas / "python3").symlink_to(sys.executable)
            shell = shutil.which("sh")
            self.assertIsNotNone(shell)
            (ferramentas / "sh").symlink_to(shell)
            env["PATH"] = str(ferramentas)
            env["GIT_CALL_COUNT_FILE"] = str(contador)

            structured = self._resolver(principal, env=env)

            self.assertEqual(structured.returncode, 2, structured.stderr)
            self.assertEqual(
                json.loads(structured.stdout),
                {
                    "state": "erro",
                    "code": "git-indisponivel",
                    "board": None,
                    "front_root": None,
                    "thread_root": None,
                    "exists": False,
                    "provenance": None,
                },
            )

    def test_separate_git_dir_e_copia_isolada_do_par_conservam_o_resolver(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            principal = raiz / "principal"
            metadados = raiz / "metadados-git"
            subprocess.run(
                ["git", "init", "--separate-git-dir", str(metadados), str(principal)],
                check=True,
                capture_output=True,
                text=True,
            )
            board = principal / "memory" / "wiki" / "KANBAN.md"
            board.parent.mkdir(parents=True)
            board.write_text("# board\n" + card(" ", "T-001", "único") + "\n", encoding="utf-8")
            structured = self._resolver(principal)
            self.assertEqual(structured.returncode, 0, structured.stderr)
            info = json.loads(structured.stdout)
            self.assertEqual(info["provenance"], "principal")
            self.assertEqual(info["board"], os.path.realpath(board))
            self.assertTrue(info["exists"])

            subprocess.run(
                ["git", "-C", str(principal), "config", "user.email", "teste@example.com"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(principal), "config", "user.name", "Teste"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(principal), "add", "memory/wiki/KANBAN.md"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(principal), "commit", "-m", "board inicial"],
                check=True,
                capture_output=True,
                text=True,
            )
            linked = raiz / "linked"
            subprocess.run(
                ["git", "-C", str(principal), "worktree", "add", "--detach", str(linked)],
                check=True,
                capture_output=True,
                text=True,
            )
            linked_structured = self._resolver(linked)
            self.assertEqual(linked_structured.returncode, 2)
            self.assertEqual(
                json.loads(linked_structured.stdout)["code"], "principal-separate-git-dir-indisponivel"
            )

            copia = raiz / "cópia isolada"
            copia.mkdir()
            shutil.copy2(SCRIPT, copia / "kanban-status.sh")
            shutil.copy2(STATUSLINE, copia / "statusline.sh")
            saida = subprocess.run(
                ["sh", str(copia / "kanban-status.sh"), str(principal)], capture_output=True, text=True, check=False
            )
            self.assertEqual(saida.returncode, 0, saida.stderr)
            self.assertIn("(0/1)", saida.stdout)

    def test_git_sem_saida_nul_e_checkout_principal_indisponivel_falham_sem_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            principal = raiz / "principal"
            self._iniciar_repo(principal, "# board\n" + card(" ", "T-001", "local") + "\n")

            sem_nul = self._fake_git(
                raiz,
                'if [ "$3" = "worktree" ] && [ "$6" = "-z" ]; then exec "$REAL_GIT" -C "$2" worktree list --porcelain; fi\nexec "$REAL_GIT" "$@"\n',
            )
            resultado = self._resolver(principal, env=sem_nul)
            self.assertEqual(resultado.returncode, 2)
            self.assertEqual(json.loads(resultado.stdout)["code"], "worktree-list-sem-nul")
            normal = subprocess.run(["sh", str(SCRIPT), str(principal)], capture_output=True, text=True, env=sem_nul, check=False)
            self.assertIn("⚠ quadro: checkout principal indisponível", normal.stdout)
            self.assertNotIn("(0/1)", normal.stdout)

            ausente = raiz / "principal-ausente"
            sem_principal = self._fake_git(
                raiz,
                'if [ "$3" = "worktree" ] && [ "$6" = "-z" ]; then printf "worktree %s\\0HEAD 0000000000000000000000000000000000000000\\0\\0" "$PRINCIPAL_AUSENTE"; exit 0; fi\nexec "$REAL_GIT" "$@"\n',
            )
            sem_principal["PRINCIPAL_AUSENTE"] = str(ausente)
            resultado = self._resolver(principal, env=sem_principal)
            self.assertEqual(resultado.returncode, 2)
            self.assertEqual(json.loads(resultado.stdout)["code"], "principal-indisponivel")

    def test_git_lento_degrada_sem_travar_a_statusline(self):
        """Uma statusline não pode esperar um Git travado para cada render."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            principal = raiz / "principal"
            self._iniciar_repo(principal, "# board\n" + card(" ", "T-001", "stale") + "\n")
            lento = self._fake_git(raiz, 'sleep 2\nexec "$REAL_GIT" "$@"\n')

            inicio = time.monotonic()
            structured = self._resolver(principal, env=lento)
            duracao = time.monotonic() - inicio
            self.assertEqual(structured.returncode, 2)
            self.assertEqual(json.loads(structured.stdout)["code"], "git-timeout")
            # `resolver()` faz duas sondas independentes antes de degradar. O
            # teto composto continua bem abaixo dos 4 s sem timeout (2 × 2 s).
            self.assertLess(duracao, 3.0)

            normal = subprocess.run(
                ["sh", str(SCRIPT), str(principal)], capture_output=True, text=True, env=lento, check=False
            )
            self.assertIn("⚠ quadro: checkout principal indisponível", normal.stdout)
            self.assertNotIn("(0/1)", normal.stdout)

            toleravel = self._fake_git(raiz, 'sleep 0.4\nexec "$REAL_GIT" "$@"\n')
            structured = self._resolver(principal, env=toleravel)
            self.assertEqual(structured.returncode, 0, structured.stderr)
            self.assertEqual(json.loads(structured.stdout)["provenance"], "principal")

    def test_timeout_da_listagem_de_worktrees_degrada_sem_traceback(self):
        """O sentinela interno de timeout nunca pode vazar para o consumidor."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            principal = raiz / "principal"
            self._iniciar_repo(principal, "# board\n" + card(" ", "T-001", "stale") + "\n")
            lento = self._fake_git(
                raiz,
                'if [ "$3" = "worktree" ] && [ "$4" = "list" ]; then sleep 2; fi\nexec "$REAL_GIT" "$@"\n',
            )

            structured = self._resolver(principal, env=lento)

            self.assertEqual(structured.returncode, 2)
            self.assertEqual(
                json.loads(structured.stdout),
                {
                    "state": "erro",
                    "code": "git-timeout",
                    "board": None,
                    "front_root": None,
                    "thread_root": None,
                    "exists": False,
                    "provenance": None,
                },
            )
            self.assertNotIn("Traceback", structured.stderr)

            normal = subprocess.run(
                ["sh", str(SCRIPT), str(principal)], capture_output=True, text=True, env=lento, check=False
            )
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertIn("⚠ quadro: checkout principal indisponível (git-timeout)", normal.stdout)
            self.assertNotIn("Traceback", normal.stderr)

    def test_checkout_bare_e_python_ausente_sao_erros_visiveis(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            bare = raiz / "bare.git"
            subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True, text=True)
            structured = self._resolver(bare)
            self.assertEqual(structured.returncode, 2)
            self.assertEqual(json.loads(structured.stdout)["code"], "checkout-bare")
            normal = subprocess.run(["sh", str(SCRIPT), str(bare)], capture_output=True, text=True, check=False)
            self.assertIn("⚠ quadro: checkout principal indisponível", normal.stdout)

            ferramentas = raiz / "sem-python"
            ferramentas.mkdir()
            for comando in ("sh", "cat", "grep", "head", "sed", "dirname"):
                origem = shutil.which(comando)
                self.assertIsNotNone(origem)
                (ferramentas / comando).symlink_to(origem)
            env = dict(os.environ)
            env["PATH"] = str(ferramentas)
            copia = raiz / "copia"
            copia.mkdir()
            shutil.copy2(SCRIPT, copia / "kanban-status.sh")
            shutil.copy2(STATUSLINE, copia / "statusline.sh")
            structured = subprocess.run(
                [str(ferramentas / "sh"), str(copia / "kanban-status.sh"), "--resolver", str(raiz)],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(structured.returncode, 2)
            self.assertEqual(
                json.loads(structured.stdout),
                {
                    "state": "erro",
                    "code": "python-indisponivel",
                    "board": None,
                    "front_root": None,
                    "thread_root": None,
                    "exists": False,
                    "provenance": None,
                },
            )
            self.assertEqual(structured.stderr, "")
            sem_python = subprocess.run(
                [str(ferramentas / "sh"), str(copia / "statusline.sh")],
                input=json.dumps({"workspace": {"project_dir": str(raiz)}}),
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(sem_python.returncode, 0, sem_python.stderr)
            self.assertIn("⚠ quadro: Python 3 indisponível", sem_python.stdout)


    def test_resolver_estrutura_raizes_da_frente_para_subpasta_e_erro(self):
        with tempfile.TemporaryDirectory() as tmp:
            principal = Path(tmp) / "principal"
            self._iniciar_repo(principal, "# board\n")
            frente = Path(tmp) / "frente"
            self._git(principal, "worktree", "add", str(frente))
            subpasta = frente / "pacotes" / "filha"
            subpasta.mkdir(parents=True)

            structured = self._resolver(subpasta)

            self.assertEqual(structured.returncode, 0, structured.stderr)
            info = json.loads(structured.stdout)
            self.assertEqual(info["state"], "ok")
            self.assertEqual(info["board"], os.path.realpath(principal / "memory" / "wiki" / "KANBAN.md"))
            self.assertEqual(info["front_root"], os.path.realpath(frente))
            self.assertEqual(info["thread_root"], os.path.realpath(frente / "memory" / "wiki"))
            self.assertTrue(info["exists"])
            self.assertTrue(os.path.isabs(info["board"]))
            self.assertTrue(os.path.isabs(info["thread_root"]))

            shell = shutil.which("sh")
            self.assertIsNotNone(shell)
            sem_python = subprocess.run(
                [shell, str(SCRIPT), "--resolver", str(frente)],
                capture_output=True,
                text=True,
                env={**os.environ, "PATH": ""},
                check=False,
            )
            self.assertEqual(sem_python.returncode, 2)
            self.assertEqual(
                json.loads(sem_python.stdout),
                {
                    "state": "erro",
                    "code": "python-indisponivel",
                    "board": None,
                    "front_root": None,
                    "thread_root": None,
                    "exists": False,
                    "provenance": None,
                },
            )

    def test_resolver_rejeita_origem_inexistente_e_nao_diretorio_com_json_completo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            arquivo = raiz / "arquivo"
            arquivo.write_text("não sou diretório", encoding="utf-8")
            for origem in (raiz / "inexistente", arquivo):
                with self.subTest(origem=origem):
                    structured = self._resolver(origem)
                    self.assertEqual(structured.returncode, 2)
                    self.assertEqual(
                        json.loads(structured.stdout),
                        {
                            "state": "erro",
                            "code": "origem-inexistente",
                            "board": None,
                            "front_root": None,
                            "thread_root": None,
                            "exists": False,
                            "provenance": None,
                        },
                    )

    def test_resolver_ignora_redirecionadores_git_herdados_e_distingue_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            principal = Path(tmp) / "principal"
            self._iniciar_repo(principal, "# board\n")
            frente = Path(tmp) / "frente"
            self._git(principal, "worktree", "add", str(frente))
            ambiente = {
                **os.environ,
                "GIT_DIR": str(Path(tmp) / "git-falso"),
                "GIT_WORK_TREE": str(Path(tmp) / "worktree-falsa"),
                "GIT_COMMON_DIR": str(Path(tmp) / "common-falso"),
                "GIT_INDEX_FILE": str(Path(tmp) / "index-falso"),
            }

            structured = self._resolver(frente, env=ambiente)

            self.assertEqual(structured.returncode, 0, structured.stderr)
            info = json.loads(structured.stdout)
            self.assertEqual(info["state"], "ok")
            self.assertEqual(info["code"], None)
            self.assertEqual(info["provenance"], "worktree")
            self.assertEqual(info["front_root"], os.path.realpath(frente))

    def test_board_path_recusa_caminho_relativo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            board = raiz / "KANBAN.md"
            board.write_text("# Quadro\n", encoding="utf-8")

            resultado = subprocess.run(
                ["sh", str(SCRIPT), "--board-path", "KANBAN.md"],
                cwd=raiz,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(resultado.returncode, 2)
            self.assertEqual(resultado.stdout, "")


if __name__ == "__main__":
    unittest.main()
