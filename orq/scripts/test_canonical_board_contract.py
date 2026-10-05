"""Guarda do contrato T-076 para o único board operacional.

Instrução sem enforcement vira lembrança frágil: um comando novo pode voltar a
ler `memory/wiki/KANBAN.md` do worktree e bifurcar o controle do Manager. Esta
guarda exige a âncora explícita em cada consumidor e prova que o lint recebe a
raiz da fixture, nunca a árvore de onde o teste foi iniciado.
"""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent
LINT_PATH = Path(__file__).with_name("lint-coerencia.py")


def _fixture_root(directory: str, name: str = "fixture") -> Path:
    return Path(directory).resolve(strict=True) / name
INVOCACAO_RESOLVER_ORQ = 'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" --resolver .'
POLITICA_FALHA_RESOLVER = (
    "Se a chamada tiver `exit != 0`, stdout vazio, JSON inválido, `state` diferente de `ok`, "
    "`exists` não booleano, ou `board`/`thread_root` ausentes ou não absolutos, trate como "
    "`state: erro`, declare indisponível e não use cópia local. Sem JSON, informe `exit` e "
    "`stderr`; com JSON de erro, informe `code`."
)
CONTRATO_THREAD_ROOT = (
    "THREAD_ROOT é o `thread_root` absoluto devolvido pelo resolver: `memory/wiki` da raiz do "
    "projeto/worktree que iniciou a operação, nunca do `BOARD_CANONICO`. O ponteiro `threads/...` "
    "do card só identifica a thread: leia/escreva exclusivamente `THREAD_ROOT/threads/...`. Somente "
    "a frente dona pode criar a thread: ela criou o card agora, ou, para card legado do BACKLOG sem "
    "ponteiro/thread, o reivindica e marca com `@frente-<slug>`. Card já marcado para "
    "outra frente, ou card existente com ponteiro cuja thread falta em `THREAD_ROOT`, deve parar: "
    "não crie, duplique, troque de frente nem use fallback."
)
PROVA_ORQ_PACKAGE_ROOT = (
    "Antes de qualquer uso, comprove `ORQ_PACKAGE_ROOT` absoluto, existente e com "
    "`scripts/kanban-status.sh` disponível."
)
CONSUMIDORES_ESPERADOS = frozenset(
    {
        Path("orq/commands/quadro.md"),
        Path("orq/commands/plan-next.md"),
        Path("orq/commands/implement-next.md"),
        Path("orq/commands/checkpoint.md"),
        Path("orq/commands/stack.md"),
        Path("orq/commands/init.md"),
        Path("orq/scripts/context-guard.py"),
        Path("orq/skills/orq/SKILL.md"),
        Path("memory/wiki/_schema.md"),
    }
)

lint_spec = importlib.util.spec_from_file_location("orq_lint_coerencia_t076", LINT_PATH)
assert lint_spec is not None and lint_spec.loader is not None
lint = importlib.util.module_from_spec(lint_spec)
lint_spec.loader.exec_module(lint)


class CanonicalBoardContractTest(unittest.TestCase):
    def _texto_consumidor(self, relative: Path) -> str:
        caminho = PLUGIN_ROOT.joinpath(*relative.parts[1:]) if relative.parts[0] == "orq" else REPO_ROOT / relative
        return caminho.read_text(encoding="utf-8")

    def _fixture_com_ancoras(self, root: Path) -> None:
        for relative in CONSUMIDORES_ESPERADOS:
            arquivo = root / relative
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            texto = (
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
            )
            if relative == Path("orq/commands/init.md"):
                texto += (
                    "Em `state: erro`, pare: `exists: false` não prova ausência e nunca autoriza criar um board.\n"
                    "Somente em `state: ok` com `exists: false`, crie o board no caminho `board` devolvido.\n"
                )
            arquivo.write_text(
                texto,
                encoding="utf-8",
            )

    def test_conjunto_de_consumidores_e_contratos_de_board_e_thread_sao_explicitos(self):
        """O teste não deriva quem vigia da mesma lista que precisa auditar."""
        self.assertEqual(frozenset(lint.CONSUMIDORES_BOARD_CANONICO), CONSUMIDORES_ESPERADOS)
        self.assertEqual(lint.INVOCACAO_RESOLVER_QUALIFICADA, INVOCACAO_RESOLVER_ORQ)
        self.assertEqual(lint.CONTRATO_THREAD_ROOT, CONTRATO_THREAD_ROOT)
        for relative in CONSUMIDORES_ESPERADOS:
            with self.subTest(consumidor=relative):
                texto = self._texto_consumidor(relative)
                self.assertIn(INVOCACAO_RESOLVER_ORQ, texto)
                self.assertIn(POLITICA_FALHA_RESOLVER, texto)
                self.assertIn(CONTRATO_THREAD_ROOT, texto)

        guard = self._texto_consumidor(Path("orq/scripts/context-guard.py"))
        self.assertIn("Comprove `ORQ_PACKAGE_ROOT`", guard)
        self.assertIn("Leia o `board` devolvido e a thread ativa antes de continuar.", guard)

        plan_next = self._texto_consumidor(Path("orq/commands/plan-next.md"))
        self.assertIn("`state: ok` com `exists: false`", plan_next)
        self.assertIn("encaminhe para `/orq:init`", plan_next)
        self.assertIn("`@frente-<slug>`", plan_next)

    def test_init_cita_fontes_e_placeholders_operacionais_com_aspas(self):
        init = self._texto_consumidor(Path("orq/commands/init.md"))
        self.assertIn('"${ORQ_PACKAGE_ROOT}/scripts/statusline.sh"', init)
        self.assertIn('"${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh"', init)
        self.assertIn('sh "<cópia-nova>/statusline.sh"', init)
        self.assertIn('diff <(sed \'2d\' "<cópia>") "${ORQ_PACKAGE_ROOT}/scripts/<nome>.sh"', init)
        self.assertIn('diff "<cópia>" "${ORQ_PACKAGE_ROOT}/scripts/<nome>.sh"', init)

    def test_init_instala_o_trio_indivisivel_da_statusline_com_backup_e_rollback_do_conjunto(self):
        """A statusline é o trio statusline.sh + kanban-status.sh + progress.py; o hook vem do bundle, não da cópia."""
        init = " ".join(self._texto_consumidor(Path("orq/commands/init.md")).split())  # as quebras de linha da prosa não contam
        self.assertIn('"${ORQ_PACKAGE_ROOT}/scripts/progress.py"', init)
        self.assertIn("o trio `statusline.sh` + `kanban-status.sh` + `progress.py` em `~/.claude/orq/`", init)
        self.assertIn("Instale **sempre o trio completo**", init)
        self.assertIn("nunca um sem os outros", init)
        self.assertIn("`.claude/progress.py`", init)  # a guarda de destino ocupado cobre o terceiro arquivo
        self.assertIn("Conjunto indivisível, backup e rollback", init)
        self.assertIn("rollback do conjunto anterior exato", init)
        self.assertIn("`progress-hook.py` **NÃO é copiado**", init)
        # o rollback não destrói alteração concorrente: confere cada arquivo contra uma referência registrada ANTES
        sem_negrito = init.replace("**", "")  # a frase conta, não o realce
        for frase in (
            # instalação indivisível; rollback arquivo a arquivo, por exceção explícita (uma só leitura possível)
            "O conjunto é indivisível na INSTALAÇÃO",
            "No ROLLBACK cada arquivo é decidido sozinho, um a um",
            "por exceção explícita, o arquivo com alteração concorrente detectada é preservado",
            "os demais são restaurados ou removidos conforme a referência",
            "o conjunto pode ficar misto",
            "Não há tentativa automática de completar o trio",
            # a referência do arquivo instalado é colhida ANTES do mv, sobre os bytes que a operação gerou
            "registre o hash esperado do conteúdo novo ANTES do `mv`",
            "Confira que o `arquivo.orq_new` no disco tem esse hash",
            "nunca use o conteúdo encontrado depois do `mv` como prova de autoria",
            "não promova, deixe o `arquivo.orq_new` onde está (não o apague: pode não ser nosso)",
            "hash esperado registrado ANTES do `mv`",
            # o backup segue a mesma lógica: referência do original antes do cp, conferida antes de restaurar
            "registre o hash do original ANTES do `cp -p`",
            "confira que o backup recém-criado tem o mesmo hash",
            "conferindo antes que o backup ainda tem o hash de referência do passo 1",
            # a conferência e o que fazer quando diverge
            "confira que o arquivo no destino ainda é exatamente o que esta operação instalou",
            "arquivo regular (não link simbólico)",
            "preserve-o: não o remova nem o restaure",
            "relate ao dono qual arquivo divergiu",
            "Ausente conta como divergente",
            "Sem o registro dos hashes, não faça rollback automático",
        ):
            self.assertIn(frase, sem_negrito)
        # as leituras antigas e ambíguas não sobrevivem
        for velha in (
            "nunca instale, atualize nem restaure um sozinho",  # contradizia a decisão arquivo a arquivo do rollback
            "Logo depois de cada `mv`, registre o hash",  # a referência colhida depois do mv aceita arquivo trocado por terceiro
            "registre o hash do arquivo que esta operação instalou",
            "cujo hash agora é igual ao registrado no passo 2",
        ):
            self.assertNotIn(velha, sem_negrito)
        self.assertIn("Conjunto incompleto", init)  # o re-sync acusa o trio que ficou sem o progress.py
        self.assertNotIn("sempre o par completo", init)

    def test_handoff_das_raizes_e_posse_da_frente_sao_explicitos(self):
        implement = self._texto_consumidor(Path("orq/commands/implement-next.md"))
        self.assertIn(
            "Passe `BOARD_CANONICO=<board>` e `THREAD_ROOT=<thread_root>` como caminhos absolutos",
            implement,
        )
        self.assertIn("papéis despachados não re-resolvem nem mudam a raiz de memória", implement)

        init = self._texto_consumidor(Path("orq/commands/init.md"))
        self.assertIn("`board` = `BOARD_CANONICO`", init)
        self.assertIn("campo JSON absoluto entregue pelo resolver", init)
        self.assertIn("igual a `<front_root>/memory/wiki`", init)
        self.assertIn("nunca é `front_root`, caminho relativo nem a raiz da frente", init)
        self.assertIn("`threads/...` relativo sob `THREAD_ROOT`", init)
        self.assertIn("`THREAD_ROOT/threads/T-NNN.md`", init)
        self.assertIn("A frente vive somente em `@frente-<slug>`", init)

        plan_next = self._texto_consumidor(Path("orq/commands/plan-next.md"))
        self.assertIn("`@frente-<slug>`", plan_next)
        self.assertIn("Não derive o slug do basename", plan_next)
        self.assertIn("Card novo é somente o criado nesta invocação", plan_next)
        self.assertIn("Card legado do BACKLOG", plan_next)
        self.assertIn("independentemente de a thread existir", plan_next)
        self.assertIn("card existente com ponteiro cuja thread falta em `THREAD_ROOT`", plan_next)

    def test_checkpoint_nao_confirma_handshake_quando_o_resolver_falha(self):
        checkpoint = self._texto_consumidor(Path("orq/commands/checkpoint.md"))
        guard = self._texto_consumidor(Path("orq/scripts/context-guard.py"))
        inexistente = "Com `state: ok` com `exists: false`, não leia o `board` e encaminhe para `/orq:init`."
        sem_handshake = "Em `state: erro`, não emita handshake positivo de checkpoint."

        self.assertIn(inexistente, checkpoint)
        self.assertIn(sem_handshake, checkpoint)
        self.assertIn(inexistente, guard)
        self.assertIn(sem_handshake, guard)

    def test_checkpoint_nao_confirma_handshake_quando_thread_obrigatoria_esta_ausente(self):
        checkpoint = self._texto_consumidor(Path("orq/commands/checkpoint.md"))
        guard = self._texto_consumidor(Path("orq/scripts/context-guard.py"))
        politica = (
            "Com card ativo desta frente cuja thread obrigatória falta em `THREAD_ROOT`, o sinal falha "
            "e não autoriza handshake; somente projeto sem card ativo desta frente pode registrar que "
            "não havia thread a verificar."
        )

        self.assertIn(politica, checkpoint)
        self.assertIn(politica, guard)

    def test_checkpoint_nao_reabre_handshake_generico_para_thread_ausente(self):
        checkpoint = self._texto_consumidor(Path("orq/commands/checkpoint.md"))
        checkpoint_sem_quebras = " ".join(checkpoint.split())

        self.assertNotIn("Thread inexistente não se verifica", checkpoint)
        self.assertNotIn("thread ausente — nada a verificar nela", checkpoint)
        self.assertIn(
            "Thread ausente só não se verifica quando não há card ativo desta frente",
            checkpoint_sem_quebras,
        )
        self.assertIn(
            "sem card ativo desta frente — nenhuma thread obrigatória a verificar",
            checkpoint_sem_quebras,
        )

    def test_skill_nomeia_thread_pelo_card_e_frente_pelo_marcador(self):
        skill = self._texto_consumidor(Path("orq/skills/orq/SKILL.md"))

        self.assertNotIn("`THREAD_ROOT/threads/<frente>.md`", skill)
        self.assertIn("`THREAD_ROOT/threads/T-NNN.md`", skill)
        self.assertIn("A frente é identificada por `@frente-<slug>`", skill)

    def test_medicoes_usam_caminho_absoluto_do_board_canonico(self):
        stack = self._texto_consumidor(Path("orq/commands/stack.md"))
        self.assertIn("`state: erro` → pare e reporte", stack)
        self.assertIn("`state: ok` com `exists: false` → o board está ausente", stack)
        self.assertIn("encaminhe para `/orq:init`, sem medição", stack)

        medida_canonica = (
            'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" --board-path "$BOARD_CANONICO"'
        )
        invocacao_diretorio_local = 'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" .'
        invocacao_posicional = 'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" "$BOARD_CANONICO"'

        for relativo in (
            Path("orq/commands/stack.md"),
            Path("orq/commands/checkpoint.md"),
            Path("orq/commands/init.md"),
        ):
            with self.subTest(consumidor=relativo):
                texto = self._texto_consumidor(relativo)
                self.assertIn(medida_canonica, texto)
                self.assertNotIn(invocacao_diretorio_local, texto)
                self.assertNotIn(invocacao_posicional, texto)

    def test_consumidores_comprovam_orq_package_root_antes_do_resolver(self):
        for relative in CONSUMIDORES_ESPERADOS:
            with self.subTest(consumidor=relative):
                self.assertIn(PROVA_ORQ_PACKAGE_ROOT, self._texto_consumidor(relative))

        skill = self._texto_consumidor(Path("orq/skills/orq/SKILL.md"))
        prova_codex = "No Codex, suba a partir desta\nskill"
        self.assertLess(skill.index(prova_codex), skill.index(INVOCACAO_RESOLVER_ORQ))

    def test_consumidores_reais_declaram_o_board_canonico(self):
        self.assertTrue(hasattr(lint, "validate_board_canonico"))
        self.assertTrue(hasattr(lint, "validate_thread_root"))
        problemas = lint.validate_board_canonico(REPO_ROOT, PLUGIN_ROOT)

        self.assertEqual(problemas, [])
        self.assertEqual(lint.validate_thread_root(REPO_ROOT, PLUGIN_ROOT), [])

    def test_contrato_simbolico_e_rejeitado_pelos_dois_validadores(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            schema = Path("memory/wiki/_schema.md")
            caminho = root / schema
            externo = root / "schema-externo.md"
            externo.write_text(caminho.read_text(encoding="utf-8"), encoding="utf-8")
            caminho.unlink()
            caminho.symlink_to(externo)

            problemas_board = lint.validate_board_canonico(root, root / "orq")
            problemas_thread = lint.validate_thread_root(root, root / "orq")

        for problemas in (problemas_board, problemas_thread):
            self.assertTrue(
                any(str(path) == str(schema) and "simbólico" in mensagem for path, _, mensagem in problemas),
                problemas,
            )

    def test_reprova_thread_derivada_do_board_em_vez_da_frente_inicial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            mutado = root / "orq" / "commands" / "quadro.md"
            mutado.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                "A thread do card é relativa ao diretório do board canônico.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_thread_root(root, root / "orq")

            self.assertEqual(len(problemas), 1)
            self.assertEqual(problemas[0][0], Path("orq/commands/quadro.md"))
            self.assertIn("THREAD_ROOT", problemas[0][2])

    def test_reprova_busca_de_thread_em_outra_frente_mesmo_com_contrato_presente(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Se ela faltar, procure a thread no checkout principal.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_thread_root(root, root / "orq")

            self.assertEqual(len(problemas), 1)
            self.assertEqual(problemas[0][0], Path("orq/commands/quadro.md"))
            self.assertIn("fallback", problemas[0][2])

    def test_raiz_explicita_com_espacos_nao_consulta_o_repositorio_principal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, "fixture com espacos")
            plugin = root / "orq"
            script = plugin / "scripts" / "kanban-status.sh"
            script.parent.mkdir(parents=True)
            script.write_text("#!/bin/sh\nprintf 'resolver seguro\\n'\n", encoding="utf-8")

            resultado = subprocess.run(
                ["/bin/sh", "-c", lint.INVOCACAO_RESOLVER_QUALIFICADA],
                capture_output=True,
                env={"ORQ_PACKAGE_ROOT": str(plugin)},
                text=True,
                check=False,
            )

            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual(resultado.stdout, "resolver seguro\n")
            self._fixture_com_ancoras(root)

            self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

            mutado = root / "orq" / "commands" / "quadro.md"
            mutado.write_text("board local relativo\n", encoding="utf-8")
            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertEqual(len(problemas), 1)
            self.assertEqual(problemas[0][0], Path("orq/commands/quadro.md"))
            self.assertIn("BOARD_CANONICO", problemas[0][2])

    def test_reprova_resolver_nu_ou_desprotegido_mesmo_com_invocacao_qualificada(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)

            mutado = root / "orq" / "commands" / "quadro.md"
            for invocacao, motivo in (
                ("kanban-status.sh --resolver .", "invocação nua"),
                (
                    "sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh --resolver .",
                    "invocação desprotegida",
                ),
            ):
                with self.subTest(invocacao=invocacao):
                    mutado.write_text(
                        f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}; "
                        f"depois execute {invocacao}.\n"
                        f"{POLITICA_FALHA_RESOLVER}\n",
                        encoding="utf-8",
                    )
                    problemas = lint.validate_board_canonico(root, root / "orq")

                    self.assertEqual(len(problemas), 1)
                    self.assertEqual(problemas[0][0], Path("orq/commands/quadro.md"))
                    self.assertIn(motivo, problemas[0][2])

    def test_reprova_resolver_nu_entre_aspas_sem_confundir_instrucao_negada(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            mutado = root / "orq" / "commands" / "quadro.md"

            mutado.write_text(
                f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                'Depois execute `sh "kanban-status.sh" --resolver .`.\n',
                encoding="utf-8",
            )
            problemas = lint.validate_board_canonico(root, root / "orq")
            self.assertEqual(len(problemas), 1)
            self.assertIn("invocação nua", problemas[0][2])

            for negada in (
                'Não execute `sh "kanban-status.sh" --resolver .`.\n',
                "Nunca execute `sh 'kanban-status.sh' --resolver .`.\n",
            ):
                with self.subTest(negada=negada):
                    mutado.write_text(
                        f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                        f"{POLITICA_FALHA_RESOLVER}\n"
                        + negada,
                        encoding="utf-8",
                    )
                    self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

    def test_reprova_medicao_nao_canonica_do_kanban_status(self):
        """A medição preserva o caminho absoluto devolvido pelo resolvedor."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp, "fixture com espacos")
            self._fixture_com_ancoras(root)
            mutado = root / "orq" / "commands" / "checkpoint.md"

            mutado.write_text(
                f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                "Depois rode `sh ${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh .`.\n",
                encoding="utf-8",
            )
            problemas = lint.validate_board_canonico(root, root / "orq")
            self.assertEqual(len(problemas), 1)
            self.assertEqual(problemas[0][0], Path("orq/commands/checkpoint.md"))
            self.assertIn("invocação desprotegida", problemas[0][2])

            for invocacao in (
                'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh"',
                'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" .',
                "sh '${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh' .",
                'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" "$BOARD_CANONICO"',
                'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" --board-path "$BOARD_CANONICO" .',
                "sh '${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh' --board-path \"$BOARD_CANONICO\"",
            ):
                with self.subTest(invocacao=invocacao):
                    mutado.write_text(
                        f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                        f"{POLITICA_FALHA_RESOLVER}\n"
                        f"Depois rode `{invocacao}`.\n",
                        encoding="utf-8",
                    )
                    problemas = lint.validate_board_canonico(root, root / "orq")
                    self.assertEqual(len(problemas), 1)
                    self.assertEqual(problemas[0][0], Path("orq/commands/checkpoint.md"))
                    self.assertIn("medição do board", problemas[0][2])

            mutado.write_text(
                f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                'Depois rode `sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" '
                '--board-path "$BOARD_CANONICO".\n',
                encoding="utf-8",
            )
            self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

            mutado.write_text(
                f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                'sh "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh" '
                '--board-path "$BOARD_CANONICO"\n'
                'Depois confira os três sinais.\n',
                encoding="utf-8",
            )
            self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

    def test_reprova_consumidor_que_nao_classifica_falhas_de_resolver_como_erro(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            mutado = root / "orq" / "commands" / "quadro.md"
            mutado.write_text(
                f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                "Use apenas o caminho `board` devolvido.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertEqual(len(problemas), 1)
            self.assertIn("falha de resolver", problemas[0][2])

    def test_reprova_leitura_edicao_ou_movimento_prescritivo_do_board_relativo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            mutado = root / "orq" / "commands" / "quadro.md"

            for instrucao in (
                "Leia `memory/wiki/KANBAN.md` antes de continuar.\n",
                "Edite `memory/wiki/KANBAN.md` para registrar o card.\n",
                "Mova o card em `memory/wiki/KANBAN.md`.\n",
            ):
                with self.subTest(instrucao=instrucao):
                    mutado.write_text(
                        f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                        f"{POLITICA_FALHA_RESOLVER}\n"
                        + instrucao,
                        encoding="utf-8",
                    )
                    problemas = lint.validate_board_canonico(root, root / "orq")
                    self.assertEqual(len(problemas), 1)
                    self.assertIn("instrução prescritiva local", problemas[0][2])

            mutado.write_text(
                f"BOARD_CANONICO: execute {INVOCACAO_RESOLVER_ORQ}.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                "Não leia `memory/wiki/KANBAN.md` local.\n",
                encoding="utf-8",
            )
            self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

    def test_reprova_instrucao_local_no_corpo_do_init_com_ancora_intacta(self):
        """Uma regra no topo não pode ser anulada por uma FASE posterior."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)

            init = root / "orq" / "commands" / "init.md"
            init.write_text(
                (PLUGIN_ROOT / "commands" / "init.md").read_text(encoding="utf-8")
                + "\nA FASE 4 cria `memory/wiki/KANBAN.md` quando não houver board.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertEqual(len(problemas), 1)
            self.assertEqual(problemas[0][0], Path("orq/commands/init.md"))
            self.assertIn("instrução prescritiva local", problemas[0][2])

    def test_init_separa_inexistencia_verdadeira_de_erro_de_resolucao(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

            init = root / "orq" / "commands" / "init.md"
            init.write_text(
                f"BOARD_CANONICO: use {lint.INVOCACAO_RESOLVER_QUALIFICADA} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                "Em `state: erro`, use `exists: false` como ausência e crie um board.\n"
                "Somente em `state: ok` com `exists: false`, crie o board no caminho `board` devolvido.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertEqual(len(problemas), 1)
            self.assertEqual(problemas[0][0], Path("orq/commands/init.md"))
            self.assertIn("erro de resolução", problemas[0][2])

    def test_lint_percorre_violacao_posterior_a_negacao_e_cobre_ferramenta_real(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Nunca rode `kanban-status.sh --resolver` sem a raiz qualificada.\n"
                "Use Edit em `memory/wiki/KANBAN.md` para mover o card.\n"
                "Depois rode `kanban-status.sh --resolver .`.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            mensagens = [problema[2] for problema in problemas if problema[0] == Path("orq/commands/quadro.md")]
            self.assertTrue(any("invocação nua" in mensagem for mensagem in mensagens), mensagens)
            self.assertTrue(any("instrução prescritiva" in mensagem for mensagem in mensagens), mensagens)

    def test_lint_nao_confunde_negacao_isolada_com_instrucao_prescritiva(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Nunca use Edit em `memory/wiki/KANBAN.md`.\n"
                "Nunca rode `kanban-status.sh --resolver` sem a raiz qualificada.\n",
                encoding="utf-8",
            )

            self.assertEqual(lint.validate_board_canonico(root, root / "orq"), [])

    def test_lint_reprova_verbo_de_mutacao_para_kanban_relativo_sem_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            checkpoint = root / "orq" / "commands" / "checkpoint.md"
            checkpoint.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Atualize `KANBAN.md` movendo o card concluído.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertTrue(
                any(
                    problema[0] == Path("orq/commands/checkpoint.md")
                    and "instrução prescritiva" in problema[2]
                    for problema in problemas
                ),
                problemas,
            )

    def test_lint_nao_deixa_negacao_adversativa_ocultar_verbo_posterior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Nunca use Edit em `memory/wiki/KANBAN.md` mas use Edit em `memory/wiki/KANBAN.md` depois.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertTrue(
                any("instrução prescritiva" in problema[2] for problema in problemas),
                problemas,
            )

    def test_lint_nao_deixa_negacao_adversativa_consumir_edicao_posterior_do_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Não leia o board relativo, mas edite memory/wiki/KANBAN.md.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            self.assertTrue(
                any("instrução prescritiva" in problema[2] for problema in problemas),
                problemas,
            )

    def test_lint_nao_deixa_negacao_adversativa_consumir_fallback_de_thread_posterior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "Não use fallback, mas procure a thread na worktree principal.\n",
                encoding="utf-8",
            )

            problemas = lint.validate_thread_root(root, root / "orq")

            self.assertTrue(
                any("fallback" in problema[2] for problema in problemas),
                problemas,
            )

    def test_lint_reprova_invocacao_sem_aspas_por_bash_ou_direta(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _fixture_root(tmp)
            self._fixture_com_ancoras(root)
            quadro = root / "orq" / "commands" / "quadro.md"
            quadro.write_text(
                f"BOARD_CANONICO: use {INVOCACAO_RESOLVER_ORQ} antes de ler ou escrever.\n"
                f"{POLITICA_FALHA_RESOLVER}\n"
                f"{CONTRATO_THREAD_ROOT}\n"
                "bash ${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh --resolver .\n"
                "${ORQ_PACKAGE_ROOT}/scripts/kanban-status.sh --resolver .\n",
                encoding="utf-8",
            )

            problemas = lint.validate_board_canonico(root, root / "orq")

            mensagens = [problema[2] for problema in problemas]
            self.assertGreaterEqual(sum("desprotegida" in mensagem for mensagem in mensagens), 2, problemas)


if __name__ == "__main__":
    unittest.main()
