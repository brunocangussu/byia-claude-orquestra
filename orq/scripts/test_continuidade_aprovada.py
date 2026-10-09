#!/usr/bin/env python3
"""Contrato executável da continuidade local já aprovada (T-143)."""

from __future__ import annotations

import shutil
import re
import tempfile
import unittest
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[2]
CONTRATO = Path("orq/skills/orq/SKILL.md")
PLAN_NEXT = Path("orq/commands/plan-next.md")
IMPLEMENT_NEXT = Path("orq/commands/implement-next.md")
REVISAR = Path("orq/commands/revisar.md")
DORMIR = Path("orq/commands/dormir.md")
CHECKPOINT = Path("orq/commands/checkpoint.md")
ARQUITETURA = Path("memory/wiki/arquitetura.md")
SCHEMA_CHECKPOINT = Path("memory/wiki/_schema.md")
CONSUMIDORES_PORTATEIS = (PLAN_NEXT, IMPLEMENT_NEXT, REVISAR, DORMIR, CHECKPOINT)
TITULO_CONTRATO = "## Contrato de continuidade aprovada"
TITULO_REFERENCIA = "## Continuidade de execução aprovada"
CONSUMIDORES = {
    Path("orq/commands/implement-next.md"): "correção local dentro do escopo aprovado",
    Path("orq/commands/revisar.md"): "falha de review não cancela a correção local aprovada",
    Path("orq/commands/plan-next.md"): "planejamento e READY não são aprovação",
    Path("orq/commands/dormir.md"): "modo noturno não transforma plano em aprovação",
    Path("orq/commands/checkpoint.md"): "preserva evidência humana, escopo, proibições e limites consumidos",
    Path("memory/wiki/arquitetura.md"): "permissões local, externa e Git são independentes",
}


def extrair_secao(texto: str, titulo: str) -> str:
    """Extrai uma seção Markdown sem permitir que outra seção satisfaça a guarda."""
    linhas = texto.split("\n")
    titulos = []
    cerca = None
    for indice, linha in enumerate(linhas):
        if cerca is not None:
            caractere, tamanho = cerca
            if re.fullmatch(rf" {{0,3}}{re.escape(caractere)}{{{tamanho},}}[ \t]*", linha):
                cerca = None
            continue
        abertura = re.fullmatch(r" {0,3}(`{3,}|~{3,})(.*)", linha)
        if abertura:
            marcador, info = abertura.groups()
            if marcador[0] != "`" or "`" not in info:
                cerca = (marcador[0], len(marcador))
                continue
        heading = re.match(r"^(#{1,6})[ \t]+", linha)
        if heading:
            titulos.append((indice, len(heading.group(1))))
    try:
        inicio = next(indice for indice, _ in titulos if linhas[indice].rstrip() == titulo)
    except StopIteration as erro:
        raise AssertionError(f"seção ausente: {titulo}") from erro

    nivel = len(titulo) - len(titulo.lstrip("#"))
    fim = len(linhas)
    for indice, nivel_heading in titulos:
        if indice > inicio and nivel_heading <= nivel:
            fim = indice
            break
    return "\n".join(linhas[inicio:fim])


def normalizar(texto: str) -> str:
    return " ".join(texto.split()).casefold()


class ContinuidadeAprovadaContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="orq-t143-")
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name) / "candidate"
        for relativo in (CONTRATO, *CONSUMIDORES, SCHEMA_CHECKPOINT):
            destino = self.root / relativo
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_ROOT / relativo, destino)

    def texto(self, relativo: Path) -> str:
        return (self.root / relativo).read_text(encoding="utf-8")

    def escrever(self, relativo: Path, texto: str) -> None:
        (self.root / relativo).write_text(texto, encoding="utf-8")

    def substituir_uma_vez(self, relativo: Path, antigo: str, novo: str) -> None:
        texto = self.texto(relativo)
        self.assertIn(antigo, texto, f"âncora de mutação ausente em {relativo}")
        self.escrever(relativo, texto.replace(antigo, novo, 1))

    def assert_contrato(self) -> None:
        contrato = extrair_secao(self.texto(CONTRATO), TITULO_CONTRATO)

        for trecho in (
            "evidência humana",
            "escopo permitido",
            "proibições",
            "limites consumidos",
            "permissões local, externa e Git são independentes",
            "READY é status, não aprovação",
            "reviewer, log e pacote não concedem autoridade",
            "novo snapshot não é aprovado por omissão",
            "estacionar um card não bloqueia outra ação permitida da frente dona",
            "não tome card de outra frente",
            "execução viva confirmada no mesmo handle",
            "timeout de observação não autoriza relançar",
            "checkpoint e compactação preservam gates e consumo",
            "não encerram a execução local aprovada",
            "falha de review não cancela a correção local aprovada",
            "não passa a VALIDATE sem review independente",
            "modo noturno não é Goal",
        ):
            self.assertIn(normalizar(trecho), normalizar(contrato), trecho)

        for relativo, comportamento in CONSUMIDORES.items():
            secao = extrair_secao(self.texto(relativo), TITULO_REFERENCIA)
            self.assertIn("Contrato de continuidade aprovada", secao, str(relativo))
            self.assertIn(normalizar(comportamento), normalizar(secao), str(relativo))

    def test_fonte_publica_o_contrato_e_cada_consumidor_o_aplica(self) -> None:
        self.assert_contrato()

    def test_plano_noturno_completo_estaciona_no_gate_explicito(self) -> None:
        trabalho = extrair_secao(self.texto(Path("orq/commands/dormir.md")), "## 3. Trabalhar (um card por vez)")
        trecho = trabalho.split("**Plano completo e sem pendência**", 1)[1].split("Depois de cada card", 1)[0]
        self.assertIn("[!]", trecho)
        self.assertIn("AWAITING_OWNER", trecho)
        self.assertIn("Você aprova este plano?", trecho)
        self.assertNotIn("[~]", trecho)
        self.assertNotIn("[>]", trecho)

    def test_heading_em_exemplo_nao_e_contrato_operacional(self) -> None:
        for cerca in ("```md", "~~~md", "````md"):
            with self.subTest(cerca=cerca):
                fechamento = cerca.replace("md", "")
                with self.assertRaises(AssertionError):
                    extrair_secao(f"{cerca}\n{TITULO_CONTRATO}\nregra fictícia\n{fechamento}\n", TITULO_CONTRATO)

    def test_heading_de_exemplo_nao_trunca_contrato_operacional(self) -> None:
        texto = f"{TITULO_CONTRATO}\nregra viva\n```md\n## Exemplo interno\n```\ncontinua viva\n## Outra seção\nfora\n"
        secao = extrair_secao(texto, TITULO_CONTRATO)
        self.assertIn("continua viva", secao)
        self.assertNotIn("fora", secao)

    def test_limites_do_card_e_limiar_da_meta_nao_sao_resetados(self) -> None:
        contrato = normalizar(extrair_secao(self.texto(CONTRATO), TITULO_CONTRATO))
        self.assertIn("limites consumidos deste card", contrato)
        self.assertIn("limiar do controlador de metas do host", contrato)

    def test_reavaliacao_local_nao_concede_nova_revisao_externa(self) -> None:
        secao = normalizar(extrair_secao(self.texto(Path("orq/commands/revisar.md")), TITULO_REFERENCIA))
        self.assertIn("reavaliar localmente", secao)
        self.assertIn("nova chamada de revisão exige saldo e autorização válida", secao)

    def assert_contrato_r2(self) -> None:
        """Guarda textual; não comprova a conduta de um host ou LLM em execução."""
        contrato = normalizar(extrair_secao(self.texto(CONTRATO), TITULO_CONTRATO))
        for trecho in (
            "citação ou referência verificável da evidência humana",
            "orçamento de chamadas separado por gate",
            "tentativa externa identifica pacote ou destino, digest dos bytes utf-8 finais sanitizados por pacote/chamada, modelo, ferramentas, limite e consumo",
            "saldo é o limite menos as tentativas já iniciadas",
            "o marcador `[!]` do card não é o estado da meta",
            "somente no host que possuir controlador de metas",
        ):
            self.assertIn(normalizar(trecho), contrato, trecho)
        self.assertNotIn("consumidores abaixo", contrato)

        fechar_loop = extrair_secao(self.texto(PLAN_NEXT), "## 6. Fechar o loop")
        for trecho in (
            "antes de marcar `[~]` ready",
            "thread dona",
            "citação ou referência verificável da evidência humana",
            "escopo permitido",
            "proibições",
            "orçamento de chamadas separado por gate",
        ):
            self.assertIn(normalizar(trecho), normalizar(fechar_loop), trecho)

        registro_loop_b = extrair_secao(self.texto(IMPLEMENT_NEXT), "## 0a. Registro durável da aprovação")
        for trecho in (
            "leia o registro da thread dona",
            "verifique que a ação local pretendida cabe no escopo",
            "plano, ready ou commit não são evidência humana",
            "recupere a fonte humana original na conversa ou em documento humano explicitamente endossado",
            "nunca invente a aprovação",
            "peça somente a autoridade realmente ausente",
        ):
            self.assertIn(normalizar(trecho), normalizar(registro_loop_b), trecho)

        gate_externo = extrair_secao(self.texto(REVISAR), "## 1c. Gate externo, envelope e saldo")
        for trecho in (
            "não inicie a chamada externa",
            "registre a pendência",
            "avance a ação local elegível",
            "não faça retry automático nem reinicie o consumo",
            "gate externo consumido não se reabre sozinho",
            "não alargue o teto externo registrado",
        ):
            self.assertIn(normalizar(trecho), normalizar(gate_externo), trecho)
        self.assertNotIn("t-143", normalizar(gate_externo))

        loop_b = self.texto(IMPLEMENT_NEXT)
        self.assertIn(
            normalizar("Antes de disparar a revisão, confira o gate externo específico"),
            normalizar(loop_b),
        )
        self.assertIn(
            normalizar("Antes de cada operação de entrega Git, confira a citação ou referência verificável"),
            normalizar(loop_b),
        )
        self.assertIn("Não há teto global de duas rodadas", self.texto(REVISAR))
        self.assertIn(
            "ORQ_PACKAGE_ROOT/references/continuidade-evidencias.md",
            self.texto(REVISAR),
        )
        self.assertNotIn("Máximo **2 rodadas**", self.texto(REVISAR))
        for relativo in (PLAN_NEXT, IMPLEMENT_NEXT, REVISAR):
            secao = extrair_secao(self.texto(relativo), TITULO_REFERENCIA)
            self.assertIn(
                "ORQ_PACKAGE_ROOT/skills/orq/SKILL.md",
                secao,
                f"raiz portátil ausente em {relativo}",
            )

    def test_r2_exige_registro_duravel_e_gates_especificos_por_acao(self) -> None:
        """Guarda textual; não comprova a conduta de um host ou LLM em execução."""
        self.assert_contrato_r2()

    def test_mutacoes_r2_sao_rejeitadas_no_consumidor_ou_contrato_correto(self) -> None:
        """Cada mutação ocorre somente na cópia descartável do candidato."""
        mutacoes = (
            (
                PLAN_NEXT,
                "citação\n  ou referência verificável da evidência humana",
                "citação\n  dispensável da evidência humana",
            ),
            (
                IMPLEMENT_NEXT,
                "leia o registro da thread dona",
                "ignore o registro da thread dona",
            ),
            (
                REVISAR,
                "não inicie a\nchamada externa",
                "inicie a\nchamada externa",
            ),
            (
                IMPLEMENT_NEXT,
                "Antes de cada operação de entrega Git, confira a citação ou referência\n  verificável da autorização humana original específica que a nomeie.",
                "Antes de cada operação de entrega Git, dispense a citação ou referência\n  verificável da autorização humana original específica que a nomeie.",
            ),
            (
                CONTRATO,
                "Saldo é o limite menos as tentativas já iniciadas.",
                "Saldo recomeça depois de cada tentativa.",
            ),
            (
                PLAN_NEXT,
                "ORQ_PACKAGE_ROOT/skills/orq/SKILL.md",
                "orq/skills/orq/SKILL.md",
            ),
            (
                CONTRATO,
                "O marcador `[!]` do card não é o estado da\n  meta.",
                "O marcador `[!]` do card é o estado da\n  meta.",
            ),
        )
        for relativo, antigo, novo in mutacoes:
            with self.subTest(mutacao=novo):
                self.substituir_uma_vez(relativo, antigo, novo)
                with self.assertRaises(AssertionError):
                    self.assert_contrato_r2()
                self.substituir_uma_vez(relativo, novo, antigo)

    def assert_contrato_r3(self) -> None:
        """Guarda estática R3; não prova execução preventiva em host ou LLM."""
        for relativo in CONSUMIDORES_PORTATEIS:
            secao = extrair_secao(self.texto(relativo), TITULO_REFERENCIA)
            self.assertIn(
                "ORQ_PACKAGE_ROOT/skills/orq/SKILL.md",
                secao,
                f"raiz instalada ausente em {relativo}",
            )

        fechar_plano = normalizar(extrair_secao(self.texto(PLAN_NEXT), "## 6. Fechar o loop"))
        for trecho in (
            "autorização humana original específica de git",
            "padrão é git não autorizado",
            "citação ou referência verificável",
        ):
            self.assertIn(normalizar(trecho), fechar_plano, trecho)

        fechar_impl = normalizar(extrair_secao(self.texto(IMPLEMENT_NEXT), "## 4. Fechar"))
        for trecho in (
            "não faça ações git",
            "mantenha a pendência da entrega",
            "não prometa validate no checkout principal nem done",
            "commit sozinho não prova pronto",
        ):
            self.assertIn(normalizar(trecho), fechar_impl, trecho)

        contrato = normalizar(extrair_secao(self.texto(CONTRATO), TITULO_CONTRATO))
        for trecho in (
            "aprovação local ou de review não concede autorização git",
            "gate externo exige citação ou referência verificável da autorização humana original",
            "nota do manager, reviewer, pacote ou ready não serve de autorização",
            "modo digest congelado cobre somente o digest registrado",
            "envelope de escopo delimitado só cobre snapshots subsequentes",
            "registrar digest novo não renova saldo",
        ):
            self.assertIn(normalizar(trecho), contrato, trecho)

        externo = normalizar(extrair_secao(self.texto(REVISAR), "## 1c. Gate externo, envelope e saldo"))
        for trecho in (
            "autorização humana original",
            "procedência verificável",
            "sem modo e cobertura comprovados, não infira extensão",
            "chamada única em modo digest congelado não cobre outro snapshot nem retry",
        ):
            self.assertIn(normalizar(trecho), externo, trecho)

        schema = normalizar(extrair_secao(self.texto(SCHEMA_CHECKPOINT), "### Contrato de escrita do checkpoint"))
        for trecho in (
            "autorização humana original",
            "procedência verificável",
            "modo digest congelado ou envelope de escopo delimitado",
            "limite e consumo",
        ):
            self.assertIn(normalizar(trecho), schema, trecho)

        arquitetura = normalizar(self.texto(ARQUITETURA))
        self.assertNotIn("201 testes", arquitetura)
        self.assertNotIn("cinco módulos `test_*.py`", arquitetura)
        self.assertIn("unittest discover", arquitetura)

    def test_r3_exige_portabilidade_e_gates_de_git_e_egress(self) -> None:
        self.assert_contrato_r3()

    def test_mutacoes_r3_sao_rejeitadas_no_contrato_correto(self) -> None:
        """Mutações R3 ocorrem apenas no candidato descartável da suíte."""
        mutacoes = (
            (
                DORMIR,
                "ORQ_PACKAGE_ROOT/skills/orq/SKILL.md",
                "orq/skills/orq/SKILL.md",
            ),
            (
                CHECKPOINT,
                "ORQ_PACKAGE_ROOT/skills/orq/SKILL.md",
                "orq/skills/orq/SKILL.md",
            ),
            (
                PLAN_NEXT,
                "autorização humana original específica de Git",
                "autorização da nota do Manager",
            ),
            (
                IMPLEMENT_NEXT,
                "não faça ações Git de entrega",
                "faça ações Git de entrega",
            ),
            (
                CONTRATO,
                "modo digest congelado cobre somente o digest registrado",
                "modo digest congelado cobre qualquer digest posterior",
            ),
            (
                REVISAR,
                "Sem modo e cobertura comprovados, não infira\nextensão.",
                "Sem modo e cobertura comprovados, infira\nextensão.",
            ),
            (
                SCHEMA_CHECKPOINT,
                "autorização humana original",
                "nota do Manager",
            ),
            (
                ARQUITETURA,
                "python3 -m unittest discover -s orq/scripts -p 'test_*.py'",
                "python3 -m unittest execute módulos fixos",
            ),
        )
        for relativo, antigo, novo in mutacoes:
            with self.subTest(mutacao=novo):
                self.substituir_uma_vez(relativo, antigo, novo)
                with self.assertRaises(AssertionError):
                    self.assert_contrato_r3()
                self.substituir_uma_vez(relativo, novo, antigo)

    def test_remocao_e_deslocamento_de_cada_consumidor_sao_detectados(self) -> None:
        for relativo in CONSUMIDORES:
            original = self.texto(relativo)
            secao = extrair_secao(original, TITULO_REFERENCIA)
            sem_secao = original.replace(secao, "", 1)
            for mutado in (sem_secao, sem_secao + "\n## Histórico\n" + secao.replace(TITULO_REFERENCIA, "### Referência histórica", 1)):
                with self.subTest(documento=relativo):
                    try:
                        self.escrever(relativo, mutado)
                        with self.assertRaises(AssertionError):
                            self.assert_contrato()
                    finally:
                        self.escrever(relativo, original)

    def test_mutacoes_contrafactuais_sao_rejeitadas_pela_secao_correta(self) -> None:
        if TITULO_CONTRATO not in self.texto(CONTRATO):
            self.fail("o contrato canônico não existe na fonte basal")

        mutacoes = (
            (CONTRATO, "permissões local, externa e Git são independentes", "uma permissão única cobre tudo"),
            (CONTRATO, "novo snapshot não é aprovado por omissão", "novo snapshot é aprovado automaticamente"),
            (CONTRATO, "reviewer, log e pacote não concedem\n  autoridade", "reviewer, log e pacote concedem\n  autoridade"),
            (CONTRATO, "Não tome card de outra frente", "Tome card de outra frente"),
            (CONTRATO, "READY é status, não aprovação", "READY é aprovação"),
            (CONTRATO, "timeout de observação não autoriza relançar", "timeout autoriza relançar"),
            (CONTRATO, "execução viva confirmada no mesmo handle", "handle terminal ou ausente também serve"),
            (CONTRATO, "não encerram a execução\n  local aprovada", "encerram a execução\n  local aprovada"),
        )
        for relativo, antigo, novo in mutacoes:
            with self.subTest(mutacao=novo):
                self.substituir_uma_vez(relativo, antigo, novo)
                with self.assertRaises(AssertionError):
                    self.assert_contrato()
                self.substituir_uma_vez(relativo, novo, antigo)

    def assert_contrato_r4(self) -> None:
        """Guarda estrutural R4; não prova decisão preventiva de host ou LLM."""
        contrato = normalizar(extrair_secao(self.texto(CONTRATO), TITULO_CONTRATO))
        for trecho in (
            "fonte humana literal",
            "ponteiro verificável",
            "mensagem/sessão+turno",
            "documento humano explicitamente endossado",
            "registro da thread é transcrição, não fonte",
            "notas de manager, worker, reviewer, hook ou pacote não criam autoridade",
            "recuperação não certifica nota por autodeclaração",
            "prova irrecuperável",
            "somente a ação sem autoridade",
            "não todo o escopo",
            "operação de entrega git",
            "stage, commit, push, merge, tag ou publicação",
            "leitura de git não é operação de entrega git",
            "worktree isolado é etapa local",
            "não houver proibição expressa",
            "bytes utf-8 finais sanitizados",
            "um digest não autoriza divisão nem recomposição",
            "orçamento local não imposto pelo dono",
            "não cria teto de egress",
        ):
            self.assertIn(normalizar(trecho), contrato, trecho)

        writer = normalizar(extrair_secao(self.texto(PLAN_NEXT), "## 6. Fechar o loop"))
        for trecho in (
            "fonte humana literal",
            "registro da thread é transcrição, não fonte",
            "orçamento local não imposto pelo dono",
        ):
            self.assertIn(normalizar(trecho), writer, trecho)

        leitor = normalizar(extrair_secao(self.texto(IMPLEMENT_NEXT), "## 0a. Registro durável da aprovação"))
        for trecho in (
            "fonte humana literal",
            "registro da thread é transcrição, não fonte",
            "prova irrecuperável",
            "somente a ação sem autoridade",
            "operação de entrega git",
        ):
            self.assertIn(normalizar(trecho), leitor, trecho)

        fechar = normalizar(extrair_secao(self.texto(IMPLEMENT_NEXT), "## 4. Fechar"))
        self.assertIn(normalizar("operação de entrega Git"), fechar)
        self.assertIn(normalizar("não prometa VALIDATE no checkout principal nem DONE"), fechar)

        externo = normalizar(extrair_secao(self.texto(REVISAR), "## 1c. Gate externo, envelope e saldo"))
        for trecho in (
            "fonte humana literal",
            "bytes utf-8 finais sanitizados",
            "um digest não autoriza divisão nem recomposição",
        ):
            self.assertIn(normalizar(trecho), externo, trecho)

        titular = normalizar(extrair_secao(self.texto(REVISAR), "## 2. Disparar o revisor titular"))
        self.assertIn(normalizar("§1b e §1c"), titular)

        schema = normalizar(extrair_secao(self.texto(SCHEMA_CHECKPOINT), "### Contrato de escrita do checkpoint"))
        for trecho in (
            "fonte humana literal",
            "registro da thread é transcrição, não fonte",
            "recuperação não certifica nota por autodeclaração",
        ):
            self.assertIn(normalizar(trecho), schema, trecho)

        loop_b = normalizar(extrair_secao(self.texto(CONTRATO), "## Os dois loops"))
        self.assertIn(normalizar("loop b não autoriza commit automaticamente"), loop_b)

        transicao = normalizar(extrair_secao(self.texto(CONTRATO), "### Transições — quem pode"))
        for trecho in (
            "alvo de validação e entrega correspondente já autorizados",
            "em `[!]` com a decisão exata",
            "posse preservada",
        ):
            self.assertIn(normalizar(trecho), transicao, trecho)

        posse = normalizar(extrair_secao(self.texto(CONTRATO), "## Várias janelas no mesmo projeto"))
        self.assertIn(normalizar("posse do card não autoriza operações de entrega Git"), posse)

        arquitetura = normalizar(self.texto(ARQUITETURA))
        self.assertIn(
            normalizar("só fica elegível a VALIDATE quando o review estiver fechado e a entrega ao alvo estiver autorizada"),
            arquitetura,
        )

    def test_r4_exige_fonte_humana_git_delimitado_e_transicao_coerente(self) -> None:
        self.assert_contrato_r4()

    def test_r4_mutacoes_sao_rejeitadas_e_contrato_ausente_nao_passa_por_skip(self) -> None:
        """Mutações R4 só tocam a árvore temporária da bancada contratual."""
        mutacoes = (
            (
                CONTRATO,
                "registro da thread é transcrição, não fonte",
                "registro da thread é fonte por autodeclaração",
            ),
            (
                CONTRATO,
                "Leitura de\n  Git não é operação de entrega Git",
                "Leitura de\n  Git é operação de entrega Git",
            ),
            (
                CONTRATO,
                "um digest não autoriza divisão nem recomposição",
                "um digest autoriza divisão e recomposição",
            ),
            (
                CONTRATO,
                "Loop B não autoriza commit\nautomaticamente",
                "Loop B autoriza commit\nautomaticamente",
            ),
            (
                CONTRATO,
                "alvo de validação e entrega\n  correspondente já autorizados",
                "alvo de validação dispensa\n  entrega autorizada",
            ),
            (
                CONTRATO,
                "posse do card não autoriza operações de entrega Git",
                "posse do card autoriza operações de entrega Git",
            ),
            (
                REVISAR,
                "§1b e §1c",
                "§1b apenas",
            ),
            (
                SCHEMA_CHECKPOINT,
                "recuperação não certifica\nnota por autodeclaração",
                "recuperação certifica\nnota por autodeclaração",
            ),
            (
                ARQUITETURA,
                "só fica elegível a VALIDATE quando o review estiver fechado e a entrega ao alvo estiver autorizada",
                "move para VALIDATE automaticamente",
            ),
        )
        for relativo, antigo, novo in mutacoes:
            with self.subTest(mutacao=novo):
                self.substituir_uma_vez(relativo, antigo, novo)
                with self.assertRaises(AssertionError):
                    self.assert_contrato_r4()
                self.substituir_uma_vez(relativo, novo, antigo)

        original = self.texto(CONTRATO)
        try:
            self.escrever(CONTRATO, original.replace(TITULO_CONTRATO, "## Contrato removido", 1))
            with self.assertRaises(AssertionError):
                self.assert_contrato_r4()
        finally:
            self.escrever(CONTRATO, original)

        fonte_teste = Path(__file__).read_text(encoding="utf-8")
        self.assertNotIn("self.skipTest(\"RED: o contrato canônico", fonte_teste)

    def assert_contrato_r5(self) -> None:
        """Contratos R5 executáveis sobre a cópia descartável, não sobre a árvore real."""
        planner = self.texto(PLAN_NEXT)
        gate_planejamento = (
            "Antes de preparar ou despachar planejamento cross-vendor, aplique o gate externo"
        )
        despacho_planejamento = "copie o comando da célula vendor×host da Matriz"
        self.assertIn(gate_planejamento, planner)
        self.assertIn(despacho_planejamento, planner)
        self.assertLess(planner.index(gate_planejamento), planner.index(despacho_planejamento))
        for trecho in (
            "fonte humana literal e seu ponteiro verificável",
            "a aprovação posterior do plano não autoriza esse despacho anterior",
            "ausência de teto não equivale a autorização ilimitada",
            "timeout é observação do mesmo handle",
            "registre o worktree isolado no escopo aprovado",
        ):
            self.assertIn(normalizar(trecho), normalizar(planner), trecho)

        revisor = self.texto(REVISAR)
        for trecho in (
            "não delimita leituras nem os bytes que o executor pode transferir",
            "não invente uma flag `--no-tools`",
            "CAPACIDADE AUSENTE",
            "não inicie chamada, estacione somente a revisão dependente",
            "estacione somente a revisão dependente",
            "sem auto-fallback, probe ou nova chamada",
            "capacidade preventiva sem ferramentas e isolamento comprovados",
            "o envelope deve cobrir os bytes reais do briefing, wrapper e leituras permitidas",
            "nunca cobre credenciais ou PII",
            "timeout é observação do mesmo handle",
        ):
            self.assertIn(normalizar(trecho), normalizar(revisor), trecho)

        implementacao = self.texto(IMPLEMENT_NEXT)
        for trecho in (
            "fonte humana literal e ponteiro verificável",
            "escopo permitido, proibições e limites consumidos por gate",
            "Git não está autorizado neste gate",
            "workers não movem o board",
            "workers não movem o board nem alargam o escopo",
        ):
            self.assertIn(normalizar(trecho), normalizar(implementacao), trecho)

        dormir = self.texto(DORMIR)
        for trecho in (
            "use o mesmo resolver canônico; não reinvente o resolver",
            "a marca de host não transfere a propriedade da frente",
            "thread ausente da frente dona interrompe somente aquela frente",
        ):
            self.assertIn(normalizar(trecho), normalizar(dormir), trecho)

        checkpoint = self.texto(CHECKPOINT)
        self.assertIn("${ORQ_PACKAGE_ROOT}/scripts/claude_mem_status.py", checkpoint)
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}/scripts/claude_mem_status.py", checkpoint)

        gate_externo = normalizar(extrair_secao(self.texto(CONTRATO), TITULO_CONTRATO))
        for trecho in (
            "não delimita leituras nem bytes que o executor pode transferir",
            "não invente `--no-tools`",
            "modo digest é **INVERIFICÁVEL / CAPACIDADE AUSENTE**",
            "sem auto-fallback, probe ou nova chamada",
        ):
            self.assertIn(normalizar(trecho), gate_externo, trecho)

        contrato = normalizar(extrair_secao(self.texto(CONTRATO), "## Várias janelas no mesmo projeto"))
        for trecho in (
            "a marca de host identifica somente o host; não transfere a propriedade da frente",
            "recuperação retoma somente a raiz e a thread existentes da frente dona comprovada",
            "transferência de frente exige instrução humana específica, preserva estado e thread originais",
            "recuperação nunca toma, duplica ou fabrica thread",
        ):
            self.assertIn(normalizar(trecho), contrato, trecho)

        arquitetura = normalizar(self.texto(ARQUITETURA))
        for trecho in (
            "não termina em VALIDATE por si só",
            "review fechado, alvo de validação e entrega correspondente autorizados",
            "VALIDATE não é prometido sem entrega autorizada ao alvo",
            "capacidade preventiva sem ferramentas e isolamento comprovados",
        ):
            self.assertIn(normalizar(trecho), arquitetura, trecho)

    def test_r5_aplica_gates_antes_do_despacho_e_limites_reais(self) -> None:
        self.assert_contrato_r5()

    def test_r5_mutacoes_de_fluxo_sao_rejeitadas_na_bancada_descartavel(self) -> None:
        """Cada mutação altera a decisão documentada na fixture temporária."""
        mutacoes = (
            (
                PLAN_NEXT,
                "Antes de preparar ou despachar planejamento cross-vendor, aplique o gate externo",
                "Depois de despachar planejamento cross-vendor, aplique o gate externo",
            ),
            (
                REVISAR,
                "não inicie chamada, estacione somente a\nrevisão dependente",
                "inicie chamada e avance a\nrevisão dependente",
            ),
            (
                IMPLEMENT_NEXT,
                "workers não movem o board nem alargam o escopo",
                "workers movem o board e alargam o escopo",
            ),
            (
                DORMIR,
                "marca de host não transfere a propriedade da frente",
                "marca de host transfere a propriedade da frente",
            ),
            (
                CHECKPOINT,
                "${ORQ_PACKAGE_ROOT}/scripts/claude_mem_status.py",
                "${CLAUDE_PLUGIN_ROOT}/scripts/claude_mem_status.py",
            ),
            (
                CONTRATO,
                "recuperação nunca toma, duplica ou fabrica\n   thread",
                "recuperação pode fabricar\n   thread",
            ),
            (
                CONTRATO,
                "modo digest é **INVERIFICÁVEL / CAPACIDADE AUSENTE**",
                "modo digest tem capacidade presumida",
            ),
            (
                ARQUITETURA,
                "VALIDATE não é prometido sem entrega\nautorizada ao alvo",
                "VALIDATE é prometido sem entrega\nautorizada ao alvo",
            ),
        )
        for relativo, antigo, novo in mutacoes:
            with self.subTest(mutacao=novo):
                self.substituir_uma_vez(relativo, antigo, novo)
                with self.assertRaises(AssertionError):
                    self.assert_contrato_r5()
                self.substituir_uma_vez(relativo, novo, antigo)

    def assert_contrato_r6(self) -> None:
        """Guarda estrutural R6: não prova conduta de LLM, host ou zero-tools."""
        planner = self.texto(PLAN_NEXT)
        inspecao = "**inspecione o briefing completo do Planner conforme o §1b de `/orq:revisar`**"
        despacho = "copie o comando da célula vendor×host da Matriz"
        self.assertIn(inspecao, planner)
        self.assertIn(despacho, planner)
        self.assertLess(planner.index(inspecao), planner.index(despacho))
        for trecho in (
            "card, título, notas, plano, páginas de wiki e leituras que entrarão no envio",
            "Nunca envie dado de paciente ou pessoal (PII), prontuário, credencial",
            "achou dado sensível, pare e avise o dono",
            "Não higienize por conta própria e envie",
        ):
            self.assertIn(normalizar(trecho), normalizar(planner), trecho)

        schema = self.texto(SCHEMA_CHECKPOINT)
        for trecho in (
            "@frente-auth`, `@frente-billing`",
            "Quem retoma durante a recuperação reafirma somente a marca de host",
            "A marca de host não transfere a propriedade da frente",
            "Transferência de frente exige instrução humana específica e é ação separada da recuperação",
            "Qualquer janela da frente dona, inclusive uma aberta amanhã, retoma somente com a raiz e a thread existentes em seu `THREAD_ROOT`",
            "Durante a recuperação, não crie, duplique, troque de frente nem use fallback",
        ):
            self.assertIn(normalizar(trecho), normalizar(schema), trecho)

    def test_r6_exige_inspecao_completa_e_recuperacao_da_frente_dona(self) -> None:
        self.assert_contrato_r6()

    def test_r6_mutacoes_de_inspecao_e_recuperacao_sao_rejeitadas(self) -> None:
        """Mutações estruturais em fixture temporária; não são prova comportamental de LLM."""
        mutacoes = (
            (
                PLAN_NEXT,
                "**inspecione o briefing completo do Planner conforme o §1b de `/orq:revisar`**",
                "**inspecione apenas leituras adicionais do Planner**",
            ),
            (
                PLAN_NEXT,
                "card, título, notas, plano, páginas de wiki e leituras que entrarão no envio",
                "somente leituras adicionais que entrarão no envio",
            ),
            (
                SCHEMA_CHECKPOINT,
                "**Quem retoma durante a recuperação reafirma\n   somente a marca de host.**",
                "**Quem retoma durante a recuperação transfere\n   a posse.**",
            ),
            (
                SCHEMA_CHECKPOINT,
                "Qualquer janela da frente dona, inclusive uma aberta amanhã, retoma somente com a raiz e a thread\nexistentes em seu `THREAD_ROOT`",
                "Qualquer janela retoma universalmente pelo card e pela\nthread",
            ),
        )
        for relativo, antigo, novo in mutacoes:
            with self.subTest(mutacao=novo):
                self.substituir_uma_vez(relativo, antigo, novo)
                with self.assertRaises(AssertionError):
                    self.assert_contrato_r6()
                self.substituir_uma_vez(relativo, novo, antigo)


if __name__ == "__main__":
    unittest.main()
