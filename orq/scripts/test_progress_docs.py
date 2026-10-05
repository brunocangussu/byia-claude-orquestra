#!/usr/bin/env python3
"""Contrato dos procedimentos do medidor de progresso (instruções, não código).

O produto aqui são instruções: o que o Manager lê em `references/progress.md`, em `implement-next.md` e em
`hosts/codex.md` precisa concordar com o CLI real e entre si. Estes testes ancoram as regras que não podem
se perder numa reescrita — as duas chaves, o `get_goal` do Codex, o plano nativo que não é espelhado, a
statusline e o anúncio da primeira execução — e conferem que as flags documentadas existem de verdade.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
CORE = SCRIPTS / "progress.py"
PROGRESS_MD = PLUGIN / "skills/orq/references/progress.md"
CODEX_MD = PLUGIN / "skills/orq/references/hosts/codex.md"
IMPLEMENT_NEXT = PLUGIN / "commands/implement-next.md"


def text(path: Path) -> str:
    """Prosa com as quebras de linha da formatação colapsadas: o teste confere a frase, não o enquadramento."""
    return " ".join(path.read_text(encoding="utf-8").split())


class ProgressProcedureTest(unittest.TestCase):
    def test_get_goal_no_codex_e_consulta_opcional_e_nunca_fecha_nada(self):
        progress = text(PROGRESS_MD)
        self.assertIn("No Codex, com a ferramenta `get_goal` disponível", progress)
        self.assertIn("o Manager PODE consultá-la", progress)
        self.assertIn("é só leitura", progress)
        self.assertIn("Sem a ferramenta, vale o início explícito", progress)
        self.assertIn("`goal: null` não é perda de ledger", progress)
        self.assertIn("Nunca feche um card nem um Goal porque o ledger chegou a 100%", progress)
        self.assertIn("o ledger só se encerra com `close`, pelo Manager", progress)
        self.assertNotIn("docs/parecer", progress)  # o plugin não cita arquivo de docs que ele não distribui

    def test_as_duas_chaves_tem_flags_diferentes_e_o_bind_so_aceita_a_nativa(self):
        progress = text(PROGRESS_MD)
        self.assertIn("## Duas chaves — não as confunda", progress)
        self.assertIn("`--native-key` (só no `bind`)", progress)
        self.assertIn("`--session-key` (begin e mutações)", progress)
        self.assertIn("`--session-key` é sempre a de **dono** e o `bind` a recusa (exit 2)", progress)
        for linha in PROGRESS_MD.read_text(encoding="utf-8").splitlines():
            if re.search(r"\bORQ bind\b", linha):
                self.assertNotIn("--session-key", linha, f"o bind não tem --session-key: {linha}")

    def test_o_manager_vincula_a_sessao_depois_do_begin_e_le_o_view_nos_marcos(self):
        progress = text(PROGRESS_MD)
        self.assertIn(
            "Depois do `begin` — antes ou depois do `plan`, tanto faz; o Loop B faz depois de gravar a chave de dono na thread —, "
            "com a chave da sessão nativa que o hook entregou no contexto",
            progress,
        )
        self.assertNotIn("Logo depois do `begin`", progress)
        self.assertIn("leia o `view` dele em vez de rodar um `show` extra", progress)
        self.assertIn("Nos marcos, leia o `view` do recibo da marcação em vez de rodar um `show` extra", progress)

    def test_o_anuncio_da_primeira_execucao_e_a_statusline_estao_descritos(self):
        progress = text(PROGRESS_MD)
        self.assertIn("**Primeira execução de uma frente.**", progress)
        self.assertIn("o **primeiro `PostToolUse`** da sessão principal", progress)
        self.assertIn("`sessions/.anunciada-<chave>.json`", progress)
        self.assertIn("## Statusline do Claude", progress)
        self.assertIn("Nunca escolhe \"o ledger mais recente\"", progress)
        self.assertIn("`◎ medidor indisponível (<código>)`", progress)
        self.assertIn("o trio `statusline.sh` + `kanban-status.sh` + `progress.py`", progress)

    def test_a_exclusao_por_planejamento_e_gate_vem_do_board_dos_cards_e_goal_conta_em_planning(self):
        progress = text(PROGRESS_MD)
        self.assertIn("**Card:** conta só com o board em `[~]`", progress)
        self.assertIn("vem do **board**, nunca da `activity` declarada no ledger", progress)
        self.assertIn("**Goal ativo** conta em **qualquer** `activity`, inclusive `planning`", progress)
        self.assertIn("o `begin` o deixa nela", progress)
        self.assertIn("Pausa e execução encerrada nunca contam, em card ou goal", progress)
        self.assertNotIn("Planejamento, gate, validação, pausa e execução encerrada nunca contam", progress)
        for outro in (PLUGIN / "skills/orq/SKILL.md", IMPLEMENT_NEXT, CODEX_MD):  # nenhum outro texto promete o contrário
            self.assertNotIn("nunca contam", text(outro))
            self.assertNotRegex(text(outro), r"(?i)planejamento[^.]*não conta")

    def test_chave_nativa_nova_cria_outro_binding_e_a_idempotencia_e_so_da_mesma_chave(self):
        progress = text(PROGRESS_MD)
        self.assertIn("o `bind` com a chave nova cria **outro** binding, com os contadores **zerados**", progress)
        self.assertIn("o da chave anterior fica parado, sem uso", progress)
        self.assertIn("A idempotência (`changed: false`, contadores preservados) vale só para a **mesma** chave nativa e o mesmo ledger", progress)
        self.assertNotIn("refaça o `bind` (idempotente: não zera os contadores do mesmo ledger)", progress)

    def test_implement_next_aponta_para_os_passos_sem_duplicar_a_regra(self):
        implement = text(IMPLEMENT_NEXT)
        self.assertIn("Vincule a sessão ao ledger com `bind`", implement)
        self.assertIn("**chave da sessão nativa** que o hook entregou", implement)
        self.assertIn("leia o `view` do recibo da marcação em vez de rodar `show`", implement)
        self.assertIn("ORQ_PACKAGE_ROOT/skills/orq/references/progress.md", implement)
        self.assertIn('("Vínculo de sessão" e "Recibo")', implement)
        # a regra (flags, garantias, exclusões) mora num lugar só
        for duplicado in ("--native-key", "--session-id", "sessions/", "recent_event_ids", "sha256"):
            self.assertNotIn(duplicado, implement)

    def test_codex_registra_que_o_plano_nativo_nao_e_espelhado_e_preserva_o_contrato_restritivo(self):
        codex = text(CODEX_MD)
        self.assertIn("## Medidor de progresso", codex)
        self.assertIn("(`update_plan`, que alimenta o item `task-progress`) **não é espelhado**", codex)
        self.assertIn("A decisão de um espelho opt-in", codex)
        self.assertIn("é do dono e fica para a fase 3 do medidor, no card T-147", codex)
        self.assertIn("não grava `tui.status_line`", codex)
        # o contrato restritivo que já existia segue de pé
        for ancora in (
            "TUI do Codex CLI", "Codex Desktop", "[tui].status_line", "não é o board do Orquestra",
            "não exibe nem persiste valores", "ID presumido", "nova TUI",
            "Este contrato não fornece escritor de TOML, backup, merge, rollback nem automação de configuração",
        ):
            self.assertIn(ancora, codex)

    def test_as_flags_documentadas_existem_no_cli_real(self):
        ajuda = {
            comando: subprocess.run([sys.executable, str(CORE), comando, "--help"], capture_output=True, text=True, timeout=60).stdout
            for comando in ("bind", "statusline")
        }
        for flag in ("--native-key", "--session-id", "--host", "--ledger", "--root", "--card", "--run"):
            self.assertIn(flag, ajuda["bind"])
        self.assertIsNone(re.search(r"(?m)^\s{1,4}--session-key\b", ajuda["bind"]))  # a ajuda só cita a flag de dono, não a define
        self.assertNotIn("--session-key SESSION_KEY", ajuda["bind"])
        for flag in ("--host", "--input"):
            self.assertIn(flag, ajuda["statusline"])
        progress = PROGRESS_MD.read_text(encoding="utf-8")
        self.assertIn("progress.py statusline --host claude --input -", progress.replace("\n", " "))

    def test_o_que_o_procedimento_cita_existe(self):
        for caminho in (
            PLUGIN / "scripts/progress.py", PLUGIN / "scripts/progress-hook.py", PLUGIN / "scripts/statusline.sh",
            PLUGIN / "scripts/kanban-status.sh", PLUGIN / "commands/init.md", PLUGIN / "commands/checkpoint.md",
            PLUGIN / "schemas/progress-binding-v1.json", PLUGIN / "schemas/progress-ledger-v1.json",
        ):
            self.assertTrue(caminho.is_file(), caminho)
        self.assertIn("hosts/codex.md", text(PROGRESS_MD))


if __name__ == "__main__":
    unittest.main()
