#!/usr/bin/env python3
"""Contrato executável para instruções futuras de escrita do checkpoint."""

from __future__ import annotations

import errno
import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SOURCE_ROOT = Path(__file__).resolve().parents[2]
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")
DOCUMENTOS_DE_INSTRUCAO = (
    Path("memory/wiki/_schema.md"),
    Path("orq/commands/checkpoint.md"),
    Path("orq/commands/init.md"),
    Path("orq/skills/orq/SKILL.md"),
)
TABELA_SCHEMA_ANTIGA = "| `fixes-history.md` | todas | append **no fim**, relendo antes; entrada carimbada com a frente |"
TABELA_SCHEMA_NOVA = "| `fixes-history.md` | todas | append **no TOPO**, relendo antes; autoria obrigatória |"
CONTRATO_SCHEMA = """### Contrato de escrita do checkpoint

Para cada nova entrada em `fixes-history.md`, releia o arquivo e insira a nova entrada no topo,
preservando as anteriores. Toda entrada tem autoria explícita: use `@frente-<slug>` quando houver
frente dona; sem frente ativa, use `@codex` ou `@claude` e declare `sem frente ativa`.
"""
LOG_CHECKPOINT_ANTIGO = """- **LOG** (`fixes-history.md`): append no TOPO, formato greppável
  `## [AAAA-MM-DD] <tipo> | <título>` (tipos: `feat` `fix` `plan` `investig` `decisão` `incidente` `processo`).
  Havendo mais de uma frente ativa, **carimbe a frente** no título: `| @auth · rotação de token`."""
LOG_CHECKPOINT_NOVO = """- **LOG** (`fixes-history.md`): formato greppável
  `## [AAAA-MM-DD] <tipo> | <título>` (tipos: `feat` `fix` `plan` `investig` `decisão` `incidente` `processo`).
  Toda entrada nova fica no topo e tem autoria obrigatória: `@frente-<slug>`; sem frente ativa,
  `@codex` ou `@claude` e a declaração `sem frente ativa`. Veja `memory/wiki/_schema.md`,
  seção `Contrato de escrita do checkpoint`."""
REFERENCIA_CONTRATO = "Consulte o `Contrato de escrita do checkpoint` em `memory/wiki/_schema.md`."


def carregar_lint() -> object:
    spec = importlib.util.spec_from_file_location("lint_coerencia_t130", LINT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckpointWriteContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        # Em macOS, tempfile pode usar o alias /var. A fixture precisa de um
        # caminho físico para que a recusa no-follow teste links da entrada,
        # não um alias do próprio sistema.
        self.fixture_dir = Path(self.tempdir.name).resolve(strict=True)
        self.root = self.fixture_dir / "candidate"
        for relativo in DOCUMENTOS_DE_INSTRUCAO:
            destino = self.root / relativo
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_ROOT / relativo, destino)
        self.module = carregar_lint()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def caminho(self, relativo: Path) -> Path:
        return self.root / relativo

    def texto(self, relativo: Path) -> str:
        return self.caminho(relativo).read_text(encoding="utf-8")

    def escrever(self, relativo: Path, texto: str) -> None:
        self.caminho(relativo).write_text(texto, encoding="utf-8")

    def substituir_uma_vez(self, relativo: Path, antigo: str, novo: str) -> None:
        texto = self.texto(relativo)
        self.assertIn(antigo, texto)
        self.escrever(relativo, texto.replace(antigo, novo, 1))

    def preparar_documentos_canonicos(self) -> None:
        schema = Path("memory/wiki/_schema.md")
        texto_schema = self.texto(schema)
        if TABELA_SCHEMA_ANTIGA in texto_schema:
            self.escrever(schema, texto_schema.replace(TABELA_SCHEMA_ANTIGA, TABELA_SCHEMA_NOVA, 1))
        else:
            self.assertIn(TABELA_SCHEMA_NOVA, texto_schema)
        if CONTRATO_SCHEMA not in self.texto(schema):
            self.escrever(schema, self.texto(schema).rstrip() + "\n\n" + CONTRATO_SCHEMA)

        checkpoint = Path("orq/commands/checkpoint.md")
        texto_checkpoint = self.texto(checkpoint)
        if LOG_CHECKPOINT_ANTIGO in texto_checkpoint:
            self.escrever(checkpoint, texto_checkpoint.replace(LOG_CHECKPOINT_ANTIGO, LOG_CHECKPOINT_NOVO, 1))
        else:
            self.assertIn(LOG_CHECKPOINT_NOVO, texto_checkpoint)

        for relativo in (Path("orq/commands/init.md"), Path("orq/skills/orq/SKILL.md")):
            if REFERENCIA_CONTRATO not in self.texto(relativo):
                self.escrever(relativo, self.texto(relativo).rstrip() + "\n\n" + REFERENCIA_CONTRATO + "\n")

    def validar(self) -> list[tuple[Path, int, str]]:
        validador = getattr(self.module, "validate_checkpoint_write_contract", None)
        self.assertTrue(callable(validador), "o linter deve expor o validador do contrato de checkpoint")
        return validador(self.root, self.root / "orq")

    def test_documentos_canonicos_passam_no_validador(self) -> None:
        self.preparar_documentos_canonicos()
        self.assertEqual([], self.validar())

    def test_documentos_atuais_passam_no_validador(self) -> None:
        self.assertEqual([], self.validar())

    def test_instrucao_de_append_no_fim_e_rejeitada(self) -> None:
        self.preparar_documentos_canonicos()
        self.substituir_uma_vez(
            Path("memory/wiki/_schema.md"),
            "append **no TOPO**",
            "append **no fim**",
        )
        problemas = self.validar()
        self.assertTrue(any(str(caminho) == "memory/wiki/_schema.md" for caminho, _, _ in problemas))

    def test_instrucao_equivalente_de_adicionar_no_final_e_rejeitada(self) -> None:
        self.preparar_documentos_canonicos()
        schema = Path("memory/wiki/_schema.md")
        self.escrever(
            schema,
            self.texto(schema).rstrip() + "\n\nEm casos especiais, adicione a entrada no final.\n",
        )
        problemas = self.validar()
        self.assertTrue(
            any("fim" in mensagem and str(caminho) == "memory/wiki/_schema.md" for caminho, _, mensagem in problemas)
        )

    def test_autoria_condicional_e_rejeitada(self) -> None:
        self.preparar_documentos_canonicos()
        self.substituir_uma_vez(
            Path("orq/commands/checkpoint.md"),
            "Toda entrada nova fica no topo e tem autoria obrigatória",
            "Havendo mais de uma frente ativa, carimbe a frente",
        )
        problemas = self.validar()
        self.assertTrue(any(str(caminho) == "orq/commands/checkpoint.md" for caminho, _, _ in problemas))

    def test_instrucao_de_autoria_opcional_e_rejeitada(self) -> None:
        self.preparar_documentos_canonicos()
        checkpoint = Path("orq/commands/checkpoint.md")
        self.escrever(
            checkpoint,
            self.texto(checkpoint).rstrip() + "\n\nA autoria pode ser opcional em checkpoints pequenos.\n",
        )
        problemas = self.validar()
        self.assertTrue(
            any("autoria" in mensagem and str(caminho) == "orq/commands/checkpoint.md" for caminho, _, mensagem in problemas)
        )

    def test_historico_legado_sem_autoria_nao_e_inspecionado(self) -> None:
        self.preparar_documentos_canonicos()
        historico = self.root / "memory/fixes-history.md"
        historico.write_text("## [2000-01-01] fix | sem autor\n", encoding="utf-8")
        self.assertEqual([], self.validar())

    def test_documento_de_contrato_simbolico_e_rejeitado(self) -> None:
        self.preparar_documentos_canonicos()
        schema = Path("memory/wiki/_schema.md")
        caminho = self.caminho(schema)
        externo = self.root / "schema-externo.md"
        externo.write_text(self.texto(schema), encoding="utf-8")
        caminho.unlink()
        caminho.symlink_to(externo)

        problemas = self.validar()

        self.assertTrue(
            any(
                str(path) == str(schema) and "simbólico" in mensagem
                for path, _, mensagem in problemas
            ),
            problemas,
        )

    def test_diretorio_pai_simbolico_e_rejeitado(self) -> None:
        self.preparar_documentos_canonicos()
        schema = Path("memory/wiki/_schema.md")
        parent = self.caminho(schema).parent
        externo = self.root / "wiki-externa"
        shutil.move(parent, externo)
        parent.symlink_to(externo, target_is_directory=True)

        problemas = self.validar()

        self.assertTrue(
            any(
                str(path) == str(schema) and "não foi possível ler" in mensagem
                for path, _, mensagem in problemas
            ),
            problemas,
        )

    def test_raiz_simbolica_e_rejeitada(self) -> None:
        self.preparar_documentos_canonicos()
        raiz_simbolica = Path(self.tempdir.name) / "candidate-link"
        raiz_simbolica.symlink_to(self.root, target_is_directory=True)
        validador = self.module.validate_checkpoint_write_contract

        problemas = validador(raiz_simbolica, raiz_simbolica / "orq")

        self.assertTrue(
            any(
                str(path) == "memory/wiki/_schema.md" and "raiz" in mensagem
                for path, _, mensagem in problemas
            ),
            problemas,
        )

    def test_ancestral_simbolico_da_raiz_e_rejeitado(self) -> None:
        self.preparar_documentos_canonicos()
        diretorio_real = self.fixture_dir / "diretorio-real"
        raiz_real = diretorio_real / "candidate"
        shutil.copytree(self.root, raiz_real)
        ancestral_simbolico = self.fixture_dir / "ancestral-link"
        ancestral_simbolico.symlink_to(diretorio_real, target_is_directory=True)
        raiz_por_ancestral_simbolico = ancestral_simbolico / "candidate"

        problemas = self.module.validate_checkpoint_write_contract(
            raiz_por_ancestral_simbolico,
            raiz_por_ancestral_simbolico / "orq",
        )

        self.assertTrue(
            any(
                str(path) == "memory/wiki/_schema.md" and "não foi possível ler" in mensagem
                for path, _, mensagem in problemas
            ),
            problemas,
        )

    def test_falha_fechado_sem_o_nofollow(self) -> None:
        with mock.patch.object(self.module.os, "O_NOFOLLOW", new=None):
            problemas = self.validar()

        self.assertTrue(
            any(str(path) == "memory/wiki/_schema.md" for path, _, _ in problemas),
            problemas,
        )

    def test_arquivo_final_e_aberto_sem_bloquear_fifo(self) -> None:
        self.preparar_documentos_canonicos()
        original_open = self.module.os.open
        nonblock = self.module.os.O_NONBLOCK

        def conferir_flags(caminho, flags, *args, **kwargs):
            if caminho == "_schema.md":
                self.assertTrue(flags & nonblock, "arquivo final deve usar O_NONBLOCK")
            return original_open(caminho, flags, *args, **kwargs)

        with mock.patch.object(self.module.os, "open", side_effect=conferir_flags) as patched_open:
            supported = set(self.module.os.supports_dir_fd) | {patched_open}
            with mock.patch.object(self.module.os, "supports_dir_fd", supported):
                self.module._read_utf8_regular_file(self.root, Path("memory/wiki/_schema.md"))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO indisponível")
    def test_fifo_no_lugar_de_contrato_falha_sem_travar(self) -> None:
        self.preparar_documentos_canonicos()
        schema = Path("memory/wiki/_schema.md")
        caminho = self.caminho(schema)
        caminho.unlink()
        self.module.os.mkfifo(caminho)

        problemas = self.validar()

        self.assertTrue(
            any(str(path) == str(schema) and "arquivo regular" in mensagem for path, _, mensagem in problemas),
            problemas,
        )

    def test_troca_do_arquivo_apos_abertura_e_rejeitada(self) -> None:
        self.preparar_documentos_canonicos()
        schema = Path("memory/wiki/_schema.md")
        caminho = self.caminho(schema)
        original_fdopen = self.module.os.fdopen
        substituido = False

        def trocar_apos_abertura(descriptor: int, *args: object, **kwargs: object) -> object:
            nonlocal substituido
            leitor = original_fdopen(descriptor, *args, **kwargs)
            if not substituido:
                substituto = caminho.with_name("schema-substituto.md")
                substituto.write_text("# externo\n", encoding="utf-8")
                substituto.replace(caminho)
                substituido = True
            return leitor

        with mock.patch.object(self.module.os, "fdopen", side_effect=trocar_apos_abertura):
            problemas = self.validar()

        self.assertTrue(
            any(
                str(path) == str(schema) and "substituído" in mensagem
                for path, _, mensagem in problemas
            ),
            problemas,
        )

    def test_segunda_fotografia_fecha_descritor_no_sucesso(self) -> None:
        relativo = Path("memory/wiki/_schema.md")
        descritores_do_arquivo: list[int] = []
        abrir_original = self.module.os.open

        def registrar_abertura(caminho: object, *args: object, **kwargs: object) -> int:
            descritor = abrir_original(caminho, *args, **kwargs)
            if caminho == relativo.name and kwargs.get("dir_fd") is not None:
                descritores_do_arquivo.append(descritor)
            return descritor

        try:
            with mock.patch.object(self.module.os, "open", side_effect=registrar_abertura) as abrir_simulado:
                with mock.patch.object(
                    self.module.os,
                    "supports_dir_fd",
                    new=set(self.module.os.supports_dir_fd) | {abrir_simulado},
                ):
                    texto = self.module._read_utf8_regular_file(self.root, relativo)

            self.assertEqual(self.texto(relativo), texto)
            self.assertEqual(2, len(descritores_do_arquivo))
            with self.assertRaises(OSError) as contexto:
                self.module.os.fstat(descritores_do_arquivo[-1])
            self.assertEqual(errno.EBADF, contexto.exception.errno)
        finally:
            if descritores_do_arquivo:
                try:
                    self.module.os.close(descritores_do_arquivo[-1])
                except OSError:
                    pass

    def test_segunda_fotografia_fecha_descritor_ao_rejeitar_identidade(self) -> None:
        relativo = Path("memory/wiki/_schema.md")
        caminho = self.caminho(relativo)
        descritores_do_arquivo: list[int] = []
        abrir_original = self.module.os.open
        fdopen_original = self.module.os.fdopen
        substituido = False

        def registrar_abertura(caminho_aberto: object, *args: object, **kwargs: object) -> int:
            descritor = abrir_original(caminho_aberto, *args, **kwargs)
            if caminho_aberto == relativo.name and kwargs.get("dir_fd") is not None:
                descritores_do_arquivo.append(descritor)
            return descritor

        def trocar_apos_abertura(descritor: int, *args: object, **kwargs: object) -> object:
            nonlocal substituido
            leitor = fdopen_original(descritor, *args, **kwargs)
            if not substituido:
                substituto = caminho.with_name("schema-substituto.md")
                substituto.write_text("# externo\n", encoding="utf-8")
                substituto.replace(caminho)
                substituido = True
            return leitor

        try:
            with mock.patch.object(self.module.os, "open", side_effect=registrar_abertura) as abrir_simulado:
                with mock.patch.object(
                    self.module.os,
                    "supports_dir_fd",
                    new=set(self.module.os.supports_dir_fd) | {abrir_simulado},
                ):
                    with mock.patch.object(self.module.os, "fdopen", side_effect=trocar_apos_abertura):
                        with self.assertRaisesRegex(OSError, "substituído durante a leitura"):
                            self.module._read_utf8_regular_file(self.root, relativo)

            self.assertEqual(2, len(descritores_do_arquivo))
            with self.assertRaises(OSError) as contexto:
                self.module.os.fstat(descritores_do_arquivo[-1])
            self.assertEqual(errno.EBADF, contexto.exception.errno)
        finally:
            if descritores_do_arquivo:
                try:
                    self.module.os.close(descritores_do_arquivo[-1])
                except OSError:
                    pass


if __name__ == "__main__":
    unittest.main()
