#!/usr/bin/env python3
"""Guardas do reúso de tasks do Codex Companion por card e papel (T-075)."""

from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parent


def read_repo(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def flat(text: str) -> str:
    return " ".join(text.split())


def section(relative: str, start: str, end: str) -> str:
    """Recorta o trecho relevante do documento: as cláusulas do T-089 são
    conferidas onde vivem, não em qualquer ponto do arquivo."""
    text = read_repo(relative)
    assert start in text, f"{relative}: marcador inicial ausente: {start!r}"
    tail = text.split(start, 1)[1]
    assert end in tail, f"{relative}: marcador final ausente: {end!r}"
    return flat(start + tail.split(end, 1)[0])


def contract_sections() -> dict[str, str]:
    return {
        "orq/skills/orq/SKILL.md": section(
            "orq/skills/orq/SKILL.md",
            "### Reúso durável do Codex Companion",
            "## Máquina de estados",
        ),
        "orq/commands/plan-next.md": section(
            "orq/commands/plan-next.md",
            "**OpenAI × host Claude — Codex Companion.**",
            "Modelo, CLI ou override indisponível",
        ),
        "orq/commands/revisar.md": section(
            "orq/commands/revisar.md",
            "**OpenAI × host Claude — titular pelo Codex Companion**",
            "Prompt **READ-ONLY explícito**",
        ),
    }


def matriz_sections() -> dict[str, str]:
    """Do início da linha OpenAI da Matriz até o próximo `## ` — inclui a
    âncora de `--write` e o parágrafo que a segue."""
    return {
        "orq/commands/elenco.md (Matriz)": section(
            "orq/commands/elenco.md", "| OpenAI | **OpenAI × host Claude:**", "\n## Perfis"
        ),
        "memory/wiki/_elenco.md (Matriz)": section(
            "memory/wiki/_elenco.md", "| **OpenAI** | **OpenAI × host Claude:**", "\n## Times por host"
        ),
    }


def consumers(sections: dict[str, str]) -> dict[str, str]:
    """Os quatro consumidores da regra curta: os dois comandos e a Matriz dos
    dois elencos — tudo, menos a skill que define o contrato."""
    out = {k: v for k, v in sections.items() if k != "orq/skills/orq/SKILL.md"}
    out.update(matriz_sections())
    return out


def elenco_openai_cells() -> dict[str, str]:
    """Promessa e Matriz que descrevem a chamada `task` sem o envelope."""
    factory = read_repo("orq/commands/elenco.md")
    live = read_repo("memory/wiki/_elenco.md")
    return {
        "orq/commands/elenco.md (promessa)": section(
            "orq/commands/elenco.md",
            "- **OpenAI × host Claude** — a célula usa",
            "- **OpenAI × host Codex**",
        ),
        "orq/commands/elenco.md (Matriz)": flat(
            next(l for l in factory.splitlines() if l.startswith("| OpenAI |"))
        ),
        "memory/wiki/_elenco.md (via)": flat(
            next(l for l in live.splitlines() if l.startswith("| codex |"))
        ),
        "memory/wiki/_elenco.md (Matriz)": flat(
            next(l for l in live.splitlines() if l.startswith("| **OpenAI** |"))
        ),
    }


class CompanionThreadReuseTest(unittest.TestCase):
    def test_canonical_skill_defines_durable_same_card_same_role_reuse(self) -> None:
        skill = read_repo("orq/skills/orq/SKILL.md")
        skill_flat = " ".join(skill.split())

        self.assertIn("Mesmo card + mesmo papel", skill)
        self.assertIn("card`, `papel`, `jobId`, `threadId`, `status`", skill)
        self.assertIn("--fresh --json", skill)
        self.assertIn("--resume-thread <threadId> --json", skill)
        self.assertIn("Mudou o card ou o papel", skill)
        self.assertIn("segunda revisão deliberadamente independente", skill_flat)
        self.assertIn("nunca delete", skill)

    def test_planning_and_review_commands_apply_the_protocol(self) -> None:
        planning = read_repo("orq/commands/plan-next.md")
        review = read_repo("orq/commands/revisar.md")

        for document in (planning, review):
            self.assertIn("codex:codex-rescue", document)
            self.assertIn("--fresh --json", document)
            self.assertIn("--resume-thread <threadId> --json", document)
            self.assertIn("rawOutput", document)
            self.assertIn("jobId", document)
            self.assertIn("threadId", document)

    def test_invocation_matrices_route_openai_on_claude_through_companion(self) -> None:
        factory = read_repo("orq/commands/elenco.md")
        live = read_repo("memory/wiki/_elenco.md")

        for document in (factory, live):
            self.assertIn("OpenAI × host Claude", document)
            self.assertIn("codex:codex-rescue", document)
            self.assertIn("codex-companion.mjs task", document)
            self.assertIn("--model <modelo> --effort <effort>", document)

    def test_continuacao_exige_identidade_do_thread_id(self) -> None:
        sections = contract_sections()
        self.assertIn(
            "o `threadId` devolvido for exatamente igual ao solicitado",
            sections["orq/skills/orq/SKILL.md"],
        )
        for name, text in consumers(sections).items():
            self.assertIn(
                "Continuação exige sucesso e `threadId` devolvido igual ao solicitado", text, name
            )
            self.assertIn('Aplicar o contrato "Reúso durável do Codex Companion"', text, name)

    def test_tabela_de_vias_condiciona_o_reuso_a_identidade(self) -> None:
        for relative, prefixo in (
            ("orq/commands/elenco.md", "| codex | OpenAI |"),
            ("memory/wiki/_elenco.md", "| codex | OpenAI |"),
        ):
            linha = next(l for l in read_repo(relative).splitlines() if l.startswith(prefixo))
            self.assertIn("aceito só com `threadId` devolvido igual ao solicitado", flat(linha), relative)

    def test_recibo_exige_sucesso_e_ids_presentes(self) -> None:
        skill = contract_sections()["orq/skills/orq/SKILL.md"]
        for clause in (
            "terminar com sucesso",
            "devolver JSON válido com `status: 0`",
            "`jobId` e `threadId` não vazios",
            "IDs ausentes, falha ou divergência invalidam a continuação",
        ):
            self.assertIn(clause, skill)

    def test_divergencia_preserva_vinculo_e_proibe_retry(self) -> None:
        sections = contract_sections()
        skill = sections["orq/skills/orq/SKILL.md"]
        for clause in (
            "preservar o vínculo anterior",
            "registrar IDs solicitado e devolvido, caminho/versão do runtime e motivo da degradação",
            "Não aceitar o `rawOutput` como continuação",
            "não repetir a chamada, iniciar outra fresca ou recorrer à última thread automaticamente",
            "Não apagar a task criada por engano",
        ):
            self.assertIn(clause, skill)
        self.assertNotIn("prova que o runtime não reconheceu", skill)
        for name, text in consumers(sections).items():
            self.assertIn("registrar degradação, preservar o vínculo anterior", text, name)
            self.assertIn("não repetir nem substituir a thread automaticamente", text, name)

    def test_wait_e_controle_do_envelope_nao_do_task(self) -> None:
        sections = contract_sections()
        for name in ("orq/commands/plan-next.md", "orq/commands/revisar.md"):
            text = sections[name]
            for clause in (
                "`--wait` pertence exclusivamente ao envelope enviado ao `codex:codex-rescue`",
                "O intermediário deve removê-lo antes de invocar `task`",
                "ele não integra os argumentos do runtime nem o briefing",
                "`task` executa em foreground quando não recebe `--background`",
            ):
                self.assertIn(clause, text, name)
        # Exemplos finais de `task` (o que o runtime recebe) nunca levam `--wait`.
        self.assertNotIn("--wait", sections["orq/skills/orq/SKILL.md"])
        for name, text in elenco_openai_cells().items():
            self.assertNotIn("--wait", text, name)
        # Toda citação do runtime `task`, em qualquer dos cinco arquivos, fica
        # sem `--wait`; as linhas de ENVELOPE (`--wait --fresh --json ...`) não
        # citam o runtime e seguem permitidas.
        runtime = "codex-companion.mjs task"
        for relative in (
            "orq/skills/orq/SKILL.md",
            "orq/commands/plan-next.md",
            "orq/commands/revisar.md",
            "orq/commands/elenco.md",
            "memory/wiki/_elenco.md",
        ):
            text = read_repo(relative)
            for line in text.splitlines():
                if runtime in line:
                    self.assertNotIn("--wait", line, f"{relative}: {line[:80]}")
            texto = flat(text)
            for trecho in texto.split(runtime)[1:]:
                self.assertNotIn("--wait", trecho[:60], relative)

    def test_via_codex_delega_modelo_ao_time_do_host(self) -> None:
        cells = elenco_openai_cells()
        via = cells["memory/wiki/_elenco.md (via)"]
        self.assertIn("conforme `## Times por host`", via)
        # A decisão do host Claude avançou para Sol 6.1 na raiz; não restaurar
        # o snapshot Astra da branch histórica para satisfazer esta guarda.
        self.assertIn("`gpt-6.1-sol` @ `xhigh`", via)
        for name, text in cells.items():
            self.assertNotRegex(text, r"@\s*`?max`?", name)


if __name__ == "__main__":
    unittest.main()
