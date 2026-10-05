Revisão independente T-131, R1, somente texto/diff. READ-ONLY; nenhuma ferramenta, arquivo, delegação ou pesquisa. O produto são instruções: procure ambiguidade, contradição e comando inexistente com cenário concreto. Objetivo aprovado: Fable ativo -> Opus5.5; ID explícito claude-opus-5-5 exige igualdade, aliases opus/fable/sonnet/haiku conservam prefixo legado e fable não vira Opus. Catálogo passa a oferecer Sol6/Luna6, mas as sondas desta CLI/conta ChatGPT recusaram ambos: não ativar sem prova modelo+via+conta/host, nem fallback. Elenco do projeto mantém Astra/Terra; catálogo de fábrica não é elenco ativo. Nenhum bump/cache/commit/install/restart nesta fase. Lint cache divergente conhecido é gate de release, não defeito novo. Audite somente mudanças deste lote, não atribua cobertura aos outros. Defeitos antigos fora do diff não bloqueiam esta migração salvo regressão introduzida. Formato obrigatório: ## BLOQUEADORES; ## RISCOS; ## VEREDITO (APROVADO | APROVADO_COM_RESSALVAS | REPROVADO). Cada achado arquivo:linha, entrada -> erro, correção mínima. Se nenhum, diga nenhum. Não invente problema de estilo.

LOTE 5/5. Sem acesso ao repositório; cada hunk tem coordenadas Git. Snapshot local, nenhuma instalação ou integração.

diff --git a/orq/scripts/test_elenco_perfis.py b/orq/scripts/test_elenco_perfis.py
index 8f80121..c12c8f4 100644
--- a/orq/scripts/test_elenco_perfis.py
+++ b/orq/scripts/test_elenco_perfis.py
@@ -186,6 +186,43 @@ class ElencoPerfisRealDocumentsTest(unittest.TestCase):
 
         self.assertEqual(problemas, [])
 
+    def test_modelos_sem_capacidade_preservam_o_elenco_ativo_inteiro(self) -> None:
+        """Sol/Luna são candidatos, nunca substituição parcial sem prova da via.
+
+        A guarda é contratual para perfil, ajuste individual e inicialização:
+        exige prova para modelo+via+conta/host. Recusa ou falta de prova mantém
+        o elenco inteiro; a proposta não cria fallback para Terra.
+        """
+        template = (PLUGIN_ROOT / "commands" / "elenco.md").read_text(encoding="utf-8")
+        projeto = (REPO_ROOT / "memory" / "wiki" / "_elenco.md").read_text(encoding="utf-8")
+        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
+
+        for modelos in (ATIVOS_BASE, PRESET_PADRAO_BASE, PRESET_ECONOMIA_BASE):
+            self.assertNotIn("fable", modelos.values())
+            self.assertEqual(modelos["planner·interface"], "claude-opus-5-5")
+
+        self.assertIn("| planner·interface | `claude-opus-5-5` |", template)
+        self.assertIn("| reviewer | `claude-opus-5-5` (exigir comprovação da identidade exata", template)
+        self.assertIn("### Host Codex\n\n**Proposta de fábrica, não elenco ativo.**", template)
+        self.assertIn("| implementer·pesada | `gpt-6-sol@xhigh` |", template)
+        self.assertIn("| implementer·normal | `gpt-5.6-terra@xhigh` |", template)
+        self.assertIn("| implementer·leve | `gpt-6-luna` (sem effort declarado — ver nota) |", template)
+        self.assertIn("| docs | `gpt-6-sol@low` |", template)
+        self.assertIn("| scout | `gpt-6-sol@low` |", template)
+        self.assertIn("| planner·interface | `claude-opus-5-5` |", projeto)
+        self.assertIn("| reviewer | `claude-opus-5-5` |", projeto)
+        self.assertIn("| planner·interface | `gpt-6-astra@max` |", projeto)
+        self.assertIn("| implementer·pesada | `gpt-5.6-terra@xhigh` |", projeto)
+        self.assertIn("gpt-6-sol", projeto)
+        self.assertIn("gpt-6-luna", projeto)
+        for documento in (template, readme):
+            contrato = re.sub(r"\s+", " ", documento)
+            self.assertIn("prova válida de capacidade para modelo + via + conta/host", contrato)
+            self.assertIn("preserva o elenco ativo inteiro", contrato)
+            self.assertIn("perfil, ajuste papel a papel ou inicialização de elenco novo", contrato)
+            self.assertIn("não grave a tabela nem acione fallback", contrato)
+            self.assertIn("se ele não existe, pare e peça ao dono uma escolha entre opções comprovadas", contrato)
+
 
 # ── Fixtures mínimas para os testes diretos ─────────────────────────────────
 # Uma tabela de 9 papéis (host) ou 8 (preset) por caso da matriz de aceite
@@ -207,7 +244,7 @@ PAPEIS_PRESET_ORDEM = PAPEIS_HOST_ORDEM[1:]
 
 ATIVOS_BASE = {
     "manager": "modelo da sessão",
-    "planner·interface": "fable",
+    "planner·interface": "claude-opus-5-5",
     "planner·sistema": "gpt-6-astra@xhigh",
     "implementer·pesada": "sonnet",
     "implementer·normal": "sonnet",
@@ -218,7 +255,7 @@ ATIVOS_BASE = {
 }
 PRESET_PADRAO_BASE = {p: v for p, v in ATIVOS_BASE.items() if p != "manager"}
 PRESET_ECONOMIA_BASE = {
-    "planner·interface": "opus",
+    "planner·interface": "claude-opus-5-5",
     "planner·sistema": "gpt-6-astra@high",
     "implementer·pesada": "sonnet",
     "implementer·normal": "sonnet",

diff --git a/orq/scripts/lint-coerencia.py b/orq/scripts/lint-coerencia.py
index 3490c91..b09bfcb 100755
--- a/orq/scripts/lint-coerencia.py
+++ b/orq/scripts/lint-coerencia.py
@@ -2096,7 +2096,7 @@ def main() -> int:
             "Host Codex: `codex exec` é obrigatório",
             "política habilitada, não capacidade comprovada",
             "a independência ganha do domínio, sempre",
-            "| reviewer | `fable` (exigir comprovação de que o alias resolve para `claude-fable-5-1`)",
+            "| reviewer | `claude-opus-5-5` (exigir comprovação da identidade exata `claude-opus-5-5`)",
             "| reviewer | `gpt-6-astra@xhigh` |",
             "run-opus-reviewer.py",
             ANCORA_PROIBICAO_WRITE,
@@ -2106,7 +2106,7 @@ def main() -> int:
             "OPUS_TIMEOUT",
             "OPUS_MODEL_MISMATCH",
             "OPUS_STARTED",
-            "claude-opus-5",
+            '"claude-opus-5-5": "claude-opus-5-5"',
             "claude-fable-5-1",
             "OPUS_MODEL_USAGE",
             "DEFAULT_TIMEOUT_SECONDS = 600.0",
@@ -2219,13 +2219,13 @@ def main() -> int:
     # independência que a regra do dono existe para impedir, com lint verde.
     # Por isso o guarda ancora na seção: recorta a tabela daquele host e exige
     # (a) a linha do vendor oposto presente 1× e (b) a linha do OUTRO host
-    # ausente. A linha do host Codex carrega junto a comprovação do alias
-    # correspondente (hoje `fable` → `claude-fable-5-1`), que continua obrigatória.
+    # ausente. A linha do host Codex carrega junto a comprovação da identidade
+    # explícita (`claude-opus-5-5`), que continua obrigatória.
     REVIEWER_CLAUDE = "| reviewer | `gpt-6-astra@xhigh` |"
-    REVIEWER_CODEX = "| reviewer | `fable` (exigir comprovação de que o alias resolve para `claude-fable-5-1`)"
+    REVIEWER_CODEX = "| reviewer | `claude-opus-5-5` (exigir comprovação da identidade exata `claude-opus-5-5`)"
     REVIEWER_POR_HOST = {
         "### Host Claude": (REVIEWER_CLAUDE, REVIEWER_CODEX, "titular OpenAI"),
-        "### Host Codex": (REVIEWER_CODEX, REVIEWER_CLAUDE, "titular Anthropic, alias comprovado"),
+        "### Host Codex": (REVIEWER_CODEX, REVIEWER_CLAUDE, "titular Anthropic, identidade comprovada"),
     }
     for heading, (esperada, proibida, papel) in REVIEWER_POR_HOST.items():
         secao, estado = secao_unica(template_elenco, heading)

diff --git a/orq/stack.md b/orq/stack.md
index d4c7701..80c88ff 100644
--- a/orq/stack.md
+++ b/orq/stack.md
@@ -163,7 +163,7 @@ mais o tempo de indexação. Existem **forks populares** — confira que é o re
 Modelos diferentes erram diferente — e **fornecedores** diferentes erram de forma menos
 correlacionada que duas instâncias do mesmo modelo. Por isso o revisor do Orquestra é **um só, e
 sempre do vendor oposto ao host**: no host Claude, quem revisa é o GPT; no host Codex, o modelo
-Anthropic do elenco (hoje `fable`, Fable 5.1). Sem a via para o outro vendor, **não há revisão
+Anthropic do elenco (hoje `claude-opus-5-5`). Sem a via para o outro vendor, **não há revisão
 independente nenhuma** — não existe cair num revisor do mesmo vendor do host.
 
 ⚠️ **Esta camada é host-aware: resolva o host ANTES de propor.** A ferramenta a instalar é a do
@@ -221,8 +221,8 @@ abre no host Claude, na direção oposta.
 `.zshrc`, que não alcança sessão já aberta.
 
 ⚠️ **CLI respondendo não é revisor funcionando.** O runner só imprime parecer quando o JSON comprova
-o prefixo do modelo selecionado — para o elenco atual, `claude-fable-5-1`; conta sem acesso a esse
-modelo devolve **revisão degradada**, não um parecer mais fraco. A sonda viva é o próprio runner
+igualdade para o ID explícito selecionado — para o elenco atual, `claude-opus-5-5` — ou o prefixo do
+alias legado. Conta sem acesso ao modelo devolve **revisão degradada**, não um parecer mais fraco. A sonda viva é o próprio runner
 (16 KiB por lote, timeout 600s) e é **chamada paga** — use-a só quando o sintoma for revisor mudo,
 sempre com `< /dev/null`.
 

