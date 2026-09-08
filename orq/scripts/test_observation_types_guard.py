#!/usr/bin/env python3
"""Guarda T-081 para a chave morta de filtro por tipo do claude-mem.

`CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES` é aceita pelo endpoint de settings,
mas não é consumida pelo gerador de contexto. A guarda descobre as superfícies
textuais vivas do repositório, ignora registros históricos/testes e só reprova
prescrição funcional — não diagnóstico negativo ou histórico.
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHAVE_MORTA = "CLAUDE_MEM_CONTEXT_OBSERVATION_TYPES"
ARQUIVOS_DE_FIXTURE = (
    "docs/brief-economia-tokens-2026-09-02.md",
    "memory/wiki/threads/T-054-economia-tokens.md",
)
EXTENSOES_TEXTO = {".json", ".md", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
DIRETORIOS_RUNTIME = {".git", ".worktrees", ".venv", "node_modules"}
PREFIXOS_HISTORICOS = (
    "docs/arquivo-worktrees-",
    "docs/superpowers/plans/",
    "memory/snapshot-",
    "memory/wiki/threads/T-052-ledgers/",
    "memory/wiki/threads/_concluidas/",
)
ARQUIVOS_HISTORICOS = {
    "memory/fixes-history.md",
    "memory/gotchas.md",
    "memory/wiki/threads/_notas-de-cards.md",
}
NOME_CHAVE_DE_TIPO = rf"(?:{re.escape(CHAVE_MORTA)}|\bOBSERVATION_TYPES\b)"
CHAVE_DE_TIPO = re.compile(NOME_CHAVE_DE_TIPO)
ATRIBUICAO_DE_TIPO = re.compile(
    rf"[\"']?{NOME_CHAVE_DE_TIPO}[\"']?\s*(?::|=(?!=))"
)
NEGACAO_OU_HISTORICO = re.compile(
    r"\b(?:diagn[óo]stic\w*|hist[óo]ric\w*|inerte|superad\w*|fals[ao]|mandava)\b"
    r"|\bhip[óo]tese\s+foi\s+descartad\w*\b"
    r"|\b(?:n[aã]o|nunca|sem)\s+(?:configur\w*|aplic\w*|usar\w*|"
    r"(?:[ée]\s+)?lid\w*)|\blid\w*\s+por\s+ningu[ée]m\b",
    re.IGNORECASE,
)
LINGUAGEM_PRESCRITIVA = re.compile(
    r"\b(?:configura(?:ç[aã]o|r)|aplic\w*|alvo|recomend\w*|segur[ao]|"
    r"efetiv[ao]|deve|export\w*|defin\w*|set\w*|lig\w*|ativ\w*|habilit\w*|"
    r"us(?:ar|e|ando|ad[oa]s?))\b",
    re.IGNORECASE,
)


def eh_registro_historico_ou_teste(relativo: str) -> bool:
    """Exclui somente logs/artefatos de histórico e código de teste."""
    return (
        relativo in ARQUIVOS_HISTORICOS
        or relativo.startswith(PREFIXOS_HISTORICOS)
        or relativo.startswith("orq/scripts/test_")
    )


def descobrir_superficies_textuais(raiz: Path) -> list[str]:
    """Descobre instruções, scripts e templates sem uma allowlist fechada."""
    superficies = []
    for diretorio, subdiretorios, arquivos in os.walk(raiz):
        subdiretorios[:] = [nome for nome in subdiretorios if nome not in DIRETORIOS_RUNTIME]
        for arquivo in arquivos:
            caminho = Path(diretorio) / arquivo
            relativo = caminho.relative_to(raiz).as_posix()
            if caminho.suffix in EXTENSOES_TEXTO and not eh_registro_historico_ou_teste(relativo):
                superficies.append(relativo)
    return sorted(superficies)


def linha_prescreve_chave_morta(linhas: list[str], indice: int) -> bool:
    """Distingue instrução funcional de uma negação ou registro diagnóstico."""
    linha = linhas[indice]
    if ATRIBUICAO_DE_TIPO.search(linha):
        return True

    contexto = " ".join(linhas[max(0, indice - 1) : indice + 3])
    if NEGACAO_OU_HISTORICO.search(linha):
        return False
    return bool(CHAVE_DE_TIPO.search(linha) and LINGUAGEM_PRESCRITIVA.search(contexto))


def achar_prescricoes_mortas(raiz: Path) -> list[str]:
    """Retorna toda superfície viva que prescreve a chave sem consumidor."""
    encontradas = []
    for relativo in descobrir_superficies_textuais(raiz):
        linhas = (raiz / relativo).read_text(encoding="utf-8", errors="replace").splitlines()
        if any(linha_prescreve_chave_morta(linhas, indice) for indice in range(len(linhas))):
            encontradas.append(relativo)
    return encontradas


class ObservationTypesGuardTest(unittest.TestCase):
    def criar_superficies_atuais(self, raiz: Path) -> None:
        for relativo in ARQUIVOS_DE_FIXTURE:
            caminho = raiz / relativo
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text("configuração sem chave morta", encoding="utf-8")

    def test_superficies_prescritivas_nao_prescrevem_chave_morta(self) -> None:
        """A regressão é prescrição funcional, não a menção histórica da chave."""
        self.assertEqual(achar_prescricoes_mortas(REPO_ROOT), [])

    def test_guarda_detecta_regressao_em_superficie_prescritiva(self) -> None:
        """Uma atribuição reintroduzida precisa falhar sem varrer o histórico."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)

            alvo = raiz / ARQUIVOS_DE_FIXTURE[0]
            alvo.write_text(f"{CHAVE_MORTA}=decision", encoding="utf-8")

            self.assertEqual(achar_prescricoes_mortas(raiz), [ARQUIVOS_DE_FIXTURE[0]])

    def test_mencao_negativa_explicita_nao_e_prescricao(self) -> None:
        """Negação legítima cita a chave, sem atribuir valor a ela."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                f"{CHAVE_MORTA} não é lida; não configurar filtro por tipo.",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [])

    def test_negacao_em_linha_anterior_nao_inocenta_atribuicao(self) -> None:
        """Uma negação de outro filtro não muda a prescrição seguinte."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                f"Não configurar outro filtro.\n{CHAVE_MORTA}=decision",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [ARQUIVOS_DE_FIXTURE[0]])

    def test_atribuicao_na_linha_diagnostica_e_bloqueada(self) -> None:
        """Rótulo diagnóstico não inocenta uma atribuição funcional."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                f"Diagnóstico: {CHAVE_MORTA}=decision",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [ARQUIVOS_DE_FIXTURE[0]])

    def test_historico_em_linha_anterior_nao_inocenta_atribuicao(self) -> None:
        """Um marcador histórico anterior não reclassifica a prescrição seguinte."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                f"Histórico antigo encerrado.\nConfiguração alvo: {CHAVE_MORTA}=decision",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [ARQUIVOS_DE_FIXTURE[0]])

    def test_forma_abreviada_em_instrucao_nova_e_detectada(self) -> None:
        """A abreviação funcional fora da antiga allowlist precisa ser bloqueada."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            relativo = "orq/templates/claude-mem.md"
            caminho = raiz / relativo
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(
                "**Configuração alvo:** `OBSERVATION_TYPES`, `OBSERVATIONS=25` — agora é seguro.",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [relativo])

    def test_historico_em_linha_anterior_nao_inocenta_mencao_prescritiva(self) -> None:
        """A classificação negativa de menção sem valor pertence à própria linha."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                f"Superado pelo diagnóstico.\nConfiguração alvo: {CHAVE_MORTA}",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [ARQUIVOS_DE_FIXTURE[0]])

    def test_verbos_prescritivos_detectam_mencao_sem_atribuicao(self) -> None:
        """Instruções usuais de configuração não podem abrir nova porta verde."""
        verbos = ("exportar", "definir", "setar", "ligar", "ativar", "habilitar", "use", "usando")
        for verbo in verbos:
            with self.subTest(verbo=verbo), tempfile.TemporaryDirectory() as tmp:
                raiz = Path(tmp)
                self.criar_superficies_atuais(raiz)
                (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                    f"{verbo.capitalize()} {CHAVE_MORTA}",
                    encoding="utf-8",
                )

                self.assertEqual(achar_prescricoes_mortas(raiz), [ARQUIVOS_DE_FIXTURE[0]])

    def test_atribuicao_json_com_chave_entre_aspas_e_bloqueada(self) -> None:
        """JSON com separador de dois-pontos também é configuração funcional."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            relativo = "configs/claude-mem.json"
            caminho = raiz / relativo
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(f'{{"{CHAVE_MORTA}": "decision"}}', encoding="utf-8")

            self.assertEqual(achar_prescricoes_mortas(raiz), [relativo])

    def test_comparacao_nao_e_atribuicao(self) -> None:
        """A primeira metade de `==` não pode ser tratada como configuração."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            (raiz / ARQUIVOS_DE_FIXTURE[0]).write_text(
                f"{CHAVE_MORTA} == decision",
                encoding="utf-8",
            )

            self.assertEqual(achar_prescricoes_mortas(raiz), [])

    def test_texto_invalido_usa_substituicao_sem_perder_atribuicao(self) -> None:
        """Arquivo textual inválido não interrompe a varredura da superfície viva."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            relativo = "docs/configuracao.md"
            caminho = raiz / relativo
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_bytes(b"texto invalido \xff\n" + f"{CHAVE_MORTA}=decision".encode("utf-8"))

            self.assertEqual(achar_prescricoes_mortas(raiz), [relativo])

    def test_diretorio_de_runtime_nao_e_superficie_viva(self) -> None:
        """Checkout aninhado não pode alimentar a guarda do repositório atual."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            caminho = raiz / ".worktrees/x/docs/configuracao.md"
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(f"{CHAVE_MORTA}=decision", encoding="utf-8")

            self.assertEqual(achar_prescricoes_mortas(raiz), [])

    def test_registro_append_only_nao_e_superficie_prescritiva(self) -> None:
        """O diagnóstico em gotchas continua fora da descoberta automática."""
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_superficies_atuais(raiz)
            caminho = raiz / "memory/gotchas.md"
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.write_text(f"{CHAVE_MORTA}=decision", encoding="utf-8")

            self.assertEqual(achar_prescricoes_mortas(raiz), [])


if __name__ == "__main__":
    unittest.main()
