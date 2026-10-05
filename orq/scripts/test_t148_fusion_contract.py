#!/usr/bin/env python3
"""Regressões materiais da fusão: identidade, custódia e transições."""

from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[2]
KEY_FILES = (
    "orq/commands/implement-next.md",
    "orq/commands/checkpoint.md",
    "orq/skills/orq/references/progress.md",
)
PUBLIC_HANDOFF = (
    "Na thread pública, registre só caminho, run_id e revisão; "
    "nunca a chave de dono."
)


def normalized(value):
    return " ".join(value.split())


def documents():
    return {
        rel: normalized((ROOT / rel).read_text(encoding="utf-8"))
        for rel in KEY_FILES + (
            "orq/commands/revisar.md",
            "orq/commands/plan-next.md",
            "orq/skills/orq/SKILL.md",
        )
    }


class FusionContractTest(unittest.TestCase):
    def assert_private_handoff(self, docs):
        for rel in KEY_FILES:
            self.assertIn(PUBLIC_HANDOFF, docs[rel], rel)
        self.assertIn(
            "A chave de dono fica somente em `owner.session_key` do ledger local ignorado.",
            docs["orq/skills/orq/references/progress.md"],
        )
        self.assertIn(
            "O worker não lê nem usa a chave de dono, mesmo se encontrar o ledger local.",
            docs["orq/commands/implement-next.md"],
        )

    def assert_identity(self, docs):
        revisar = docs["orq/commands/revisar.md"]
        self.assertNotIn("o prefixo do alias legado pedido", revisar)
        self.assertIn("A comparação legada é completa, nunca por prefixo", revisar)
        self.assertIn("Essa compatibilidade não comprova Opus 5.5", revisar)
        self.assertIn("para exigir 5.5, peça o ID explícito `claude-opus-5-5`", revisar)

    def test_chave_nao_viaja_na_thread_publica_ou_no_briefing(self):
        self.assert_private_handoff(documents())

    def test_alias_legado_tem_gramatica_fechada_sem_promessa_de_55(self):
        self.assert_identity(documents())
        matches = runpy.run_path(str(ROOT / "orq/scripts/run-opus-reviewer.py"))[
            "matches_model_identity"
        ]
        # A compatibilidade existente não é estreitada para datas de oito dígitos.
        for returned in ("claude-opus-5", "claude-opus-5-5", "claude-opus-5-6",
                         "claude-opus-5-20260929"):
            self.assertTrue(matches(returned, "claude-opus-5"))
        for returned in ("claude-opus-5anything", "claude-opus-5--5",
                         "claude-sonnet-5-5"):
            self.assertFalse(matches(returned, "claude-opus-5"))
        self.assertTrue(matches("claude-opus-5-5", "claude-opus-5-5", exact=True))
        for returned in ("claude-opus-5", "claude-opus-5-50",
                         "claude-opus-5-5-20260929"):
            self.assertFalse(matches(returned, "claude-opus-5-5", exact=True))

    def test_done_depende_da_validacao_real_e_git_pendente_nao_para_o_local(self):
        self.assert_transitions(documents())

    def assert_transitions(self, docs):
        implement = docs["orq/commands/implement-next.md"]
        for clause in (
            "`[x]` exige validação positiva do dono, não só autorização para validar",
            "Se a entrega Git ainda estiver pendente, mantenha o medidor aberto em `docs`",
            "não use `validate`, `pause` ou `close` só por chegar a 100%",
        ):
            self.assertIn(clause, implement)

    def test_vinculo_inicial_nao_aceita_recibo_terminal_de_falha(self):
        self.assert_initial_receipt(documents())

    def assert_initial_receipt(self, docs):
        skill = docs["orq/skills/orq/SKILL.md"]
        for clause in (
            "Vínculo inicial comprovado",
            "a chamada fresca exige sucesso, JSON válido, `status: 0`",
            "falha terminal não cria vínculo",
        ):
            self.assertIn(clause, skill)

    def test_worktree_e_plano_antigo_tem_fronteira_operacional(self):
        self.assert_isolation(documents())

    def assert_isolation(self, docs):
        self.assertIn(
            "o Manager prepara o isolamento somente se já previsto no plano aprovado",
            docs["orq/commands/plan-next.md"],
        )
        self.assertIn("o worker não cria nem remove refs ou worktrees",
                      docs["orq/commands/plan-next.md"])
        self.assertIn("Plano antigo é o aprovado antes da adoção do medidor",
                      docs["orq/commands/implement-next.md"])

    def test_mutacoes_rejeitam_chave_publica_prefixo_e_vinculo_falso(self):
        docs = documents()
        self.assert_private_handoff(docs)
        self.assert_identity(docs)
        for rel in KEY_FILES:
            mutated = dict(docs)
            mutated[rel] = mutated[rel].replace(
                PUBLIC_HANDOFF, "Grave também a chave de dono na thread pública.", 1
            )
            with self.subTest(surface=rel), self.assertRaises(AssertionError):
                self.assert_private_handoff(mutated)
        mutated = dict(docs)
        mutated["orq/commands/revisar.md"] = mutated["orq/commands/revisar.md"].replace(
            "A comparação legada é completa, nunca por prefixo",
            "A comparação legada aceita qualquer prefixo", 1
        )
        with self.assertRaises(AssertionError):
            self.assert_identity(mutated)
        for rel, old, new, checker in (
            ("orq/commands/implement-next.md",
             "`[x]` exige validação positiva do dono, não só autorização para validar",
             "`[x]` depende só da autorização para validar", self.assert_transitions),
            ("orq/commands/implement-next.md",
             "não use `validate`, `pause` ou `close` só por chegar a 100%",
             "use `close` automaticamente ao chegar a 100%", self.assert_transitions),
            ("orq/skills/orq/SKILL.md",
             "a chamada fresca exige sucesso, JSON válido, `status: 0`",
             "a chamada fresca aceita qualquer status terminal", self.assert_initial_receipt),
            ("orq/commands/plan-next.md",
             "o worker não cria nem remove refs ou worktrees",
             "o worker pode criar refs e remover worktrees", self.assert_isolation),
            ("orq/commands/implement-next.md",
             "Plano antigo é o aprovado antes da adoção do medidor",
             "Qualquer plano novo sem tabela é antigo", self.assert_isolation),
        ):
            mutated = dict(docs)
            self.assertEqual(mutated[rel].count(old), 1)
            mutated[rel] = mutated[rel].replace(old, new, 1)
            with self.subTest(mutacao=new), self.assertRaises(AssertionError):
                checker(mutated)


if __name__ == "__main__":
    unittest.main()
