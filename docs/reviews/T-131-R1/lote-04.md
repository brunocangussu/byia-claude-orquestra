Revisão independente T-131, R1, somente texto/diff. READ-ONLY; nenhuma ferramenta, arquivo, delegação ou pesquisa. O produto são instruções: procure ambiguidade, contradição e comando inexistente com cenário concreto. Objetivo aprovado: Fable ativo -> Opus5.5; ID explícito claude-opus-5-5 exige igualdade, aliases opus/fable/sonnet/haiku conservam prefixo legado e fable não vira Opus. Catálogo passa a oferecer Sol6/Luna6, mas as sondas desta CLI/conta ChatGPT recusaram ambos: não ativar sem prova modelo+via+conta/host, nem fallback. Elenco do projeto mantém Astra/Terra; catálogo de fábrica não é elenco ativo. Nenhum bump/cache/commit/install/restart nesta fase. Lint cache divergente conhecido é gate de release, não defeito novo. Audite somente mudanças deste lote, não atribua cobertura aos outros. Defeitos antigos fora do diff não bloqueiam esta migração salvo regressão introduzida. Formato obrigatório: ## BLOQUEADORES; ## RISCOS; ## VEREDITO (APROVADO | APROVADO_COM_RESSALVAS | REPROVADO). Cada achado arquivo:linha, entrada -> erro, correção mínima. Se nenhum, diga nenhum. Não invente problema de estilo.

LOTE 4/5. Sem acesso ao repositório; cada hunk tem coordenadas Git. Snapshot local, nenhuma instalação ou integração.

diff --git a/orq/scripts/test_run_opus_reviewer.py b/orq/scripts/test_run_opus_reviewer.py
index 0bf9a99..0a88042 100644
--- a/orq/scripts/test_run_opus_reviewer.py
+++ b/orq/scripts/test_run_opus_reviewer.py
@@ -44,7 +44,7 @@ class OpusReviewerRunnerTest(unittest.TestCase):
                     subprocess.Popen([sys.executable, "-c", child_code])
                     time.sleep(2)
                 time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
-                expect_model = os.environ.get("FAKE_EXPECT_MODEL", "opus")
+                expect_model = os.environ.get("FAKE_EXPECT_MODEL", "claude-opus-5-5")
                 expected = [
                     "-p", "--model", expect_model, "--permission-mode", "plan", "--tools", "",
                     "--setting-sources", "", "--disable-slash-commands",
@@ -67,7 +67,7 @@ class OpusReviewerRunnerTest(unittest.TestCase):
                 if raw_stdout is not None:
                     print(raw_stdout)
                     raise SystemExit(0)
-                model = os.environ.get("FAKE_MODEL", "claude-opus-5")
+                model = os.environ.get("FAKE_MODEL", "claude-opus-5-5")
                 result = os.environ.get("FAKE_RESULT", "PARECER_OK")
                 payload = {{"result": result, "modelUsage": {{model: {{}}}}}}
                 extra_model = os.environ.get("FAKE_EXTRA_MODEL")
@@ -102,12 +102,12 @@ class OpusReviewerRunnerTest(unittest.TestCase):
             timeout=5,
         )
 
-    def test_returns_parecer_only_after_proving_opus_5(self) -> None:
+    def test_returns_parecer_only_after_proving_explicit_opus_5_5(self) -> None:
         result = self.run_runner()
         self.assertEqual(result.returncode, 0, result.stderr)
         self.assertEqual(result.stdout.strip(), "PARECER_OK")
         self.assertIn("OPUS_STARTED", result.stderr)
-        self.assertIn("OPUS_MODEL=claude-opus-5", result.stderr)
+        self.assertIn("OPUS_MODEL=claude-opus-5-5", result.stderr)
 
     def test_default_timeout_accommodates_real_opus_review_latency(self) -> None:
         result = self.run_runner()
@@ -136,6 +136,70 @@ class OpusReviewerRunnerTest(unittest.TestCase):
         self.assertIn("MODEL_ALIAS=fable", result.stderr)
         self.assertIn("OPUS_MODEL=claude-fable-5-1", result.stderr)
 
+    def test_legacy_opus_alias_remains_supported(self) -> None:
+        """Mudar o default não redireciona nem remove o alias legado `opus`."""
+        result = self.run_runner(
+            "revise", "--model", "opus",
+            FAKE_EXPECT_MODEL="opus", FAKE_MODEL="claude-opus-5",
+        )
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertIn("MODEL_ALIAS=opus", result.stderr)
+        self.assertIn("OPUS_MODEL=claude-opus-5", result.stderr)
+
+    def test_legacy_opus_alias_keeps_its_prefix_proof(self) -> None:
+        """O alias legado aceita a versão que o CLI atual anuncia no modelUsage."""
+        result = self.run_runner(
+            "revise", "--model", "opus",
+            FAKE_EXPECT_MODEL="opus", FAKE_MODEL="claude-opus-5-5",
+        )
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertIn("OPUS_MODEL=claude-opus-5-5", result.stderr)
+
+    def test_legacy_haiku_alias_keeps_its_prefix_proof(self) -> None:
+        """Sufixo de release do Haiku não invalida o alias legado."""
+        result = self.run_runner(
+            "revise", "--model", "haiku",
+            FAKE_EXPECT_MODEL="haiku", FAKE_MODEL="claude-haiku-4-5-20251001",
+        )
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertIn("OPUS_MODEL=claude-haiku-4-5-20251001", result.stderr)
+
+    def test_runs_explicit_opus_5_5_and_proves_its_exact_identity(self) -> None:
+        """A opção explícita chega intacta à CLI e só aceita o ID oficial."""
+        result = self.run_runner(
+            "revise", "--model", "claude-opus-5-5",
+            FAKE_EXPECT_MODEL="claude-opus-5-5",
+            FAKE_MODEL="claude-opus-5-5",
+        )
+        self.assertEqual(result.returncode, 0, result.stderr)
+        self.assertEqual(result.stdout.strip(), "PARECER_OK")
+        self.assertIn("MODEL_ALIAS=claude-opus-5-5", result.stderr)
+        self.assertIn("OPUS_MODEL=claude-opus-5-5", result.stderr)
+
+    def test_rejects_old_opus_5_when_explicit_opus_5_5_was_requested(self) -> None:
+        """O modelo anterior não prova a identidade explícita 5.5."""
+        result = self.run_runner(
+            "revise", "--model", "claude-opus-5-5",
+            FAKE_EXPECT_MODEL="claude-opus-5-5",
+            FAKE_MODEL="claude-opus-5",
+        )
+        self.assertEqual(result.returncode, 7)
+        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)
+        self.assertIn("esperado claude-opus-5-5", result.stderr)
+        self.assertEqual(result.stdout, "")
+
+    def test_rejects_opus_5_5_lookalike_when_explicit_identity_was_requested(self) -> None:
+        """Prefixo não basta: `claude-opus-5-50` não é `claude-opus-5-5`."""
+        result = self.run_runner(
+            "revise", "--model", "claude-opus-5-5",
+            FAKE_EXPECT_MODEL="claude-opus-5-5",
+            FAKE_MODEL="claude-opus-5-50",
+        )
+        self.assertEqual(result.returncode, 7)
+        self.assertIn("OPUS_MODEL_MISMATCH", result.stderr)
+        self.assertIn("esperado claude-opus-5-5", result.stderr)
+        self.assertEqual(result.stdout, "")
+
     def test_rejects_fable_5_0_when_fable_5_1_is_required(self) -> None:
         """Pedir Fable e receber 5.0 é reprovado — o prefixo exige exatamente 5.1.
 
@@ -181,11 +245,14 @@ class OpusReviewerRunnerTest(unittest.TestCase):
         self.assertIn("MODEL_ALIAS_DESCONHECIDO", result.stderr)
         self.assertFalse(marker.exists(), "o CLI não pode ser chamado com alias inválido")
 
-    def test_default_model_is_still_opus(self) -> None:
-        """Sem `--model`, nada muda — o host Codex tem chamadas gravadas sem a flag."""
-        result = self.run_runner()
+    def test_default_model_is_explicit_opus_5_5(self) -> None:
+        """Sem `--model`, o revisor padrão pede a identidade explícita 5.5."""
+        result = self.run_runner(
+            FAKE_EXPECT_MODEL="claude-opus-5-5",
+            FAKE_MODEL="claude-opus-5-5",
+        )
         self.assertEqual(result.returncode, 0, result.stderr)
-        self.assertIn("MODEL_ALIAS=opus", result.stderr)
+        self.assertIn("MODEL_ALIAS=claude-opus-5-5", result.stderr)
 
     def test_rejects_oversized_briefing_before_calling_claude(self) -> None:
         marker = Path(self.tmp.name) / "called"
@@ -268,7 +335,7 @@ class OpusReviewerRunnerTest(unittest.TestCase):
     def test_success_logs_every_model_used_for_audit(self) -> None:
         result = self.run_runner(FAKE_EXTRA_MODEL="claude-haiku-4-5")
         self.assertEqual(result.returncode, 0, result.stderr)
-        self.assertIn("OPUS_MODEL_USAGE=claude-haiku-4-5,claude-opus-5", result.stderr)
+        self.assertIn("OPUS_MODEL_USAGE=claude-haiku-4-5,claude-opus-5-5", result.stderr)
 
     def test_api_error_message_is_bounded(self) -> None:
         result = self.run_runner(FAKE_IS_ERROR="1", FAKE_RESULT="E" * 10_000)

diff --git a/orq/skills/orq/SKILL.md b/orq/skills/orq/SKILL.md
index 8479017..07efddd 100644
--- a/orq/skills/orq/SKILL.md
+++ b/orq/skills/orq/SKILL.md
@@ -161,7 +161,7 @@ silêncio.
 | "anota isso" · "cria uma tarefa" · "isso vira card" · "não esquece disso" | **Cria o card** no BACKLOG com ID e contexto suficiente pra retomar |
 | "revisa isso" · "manda revisar" · "valida isso" · "o que você acha desse código?" | **Revisão independente** (`/orq:revisar`) — **um** revisor, sempre de um modelo do **vendor oposto ao host** (resolvido no `_elenco.md`; outro modelo do mesmo vendor do host **não** serve), com os achados auditados por você contra o código antes de virarem veredito |
 | "audite a remoção de X" · "prove que X saiu" · "verifique se começamos pelo grafo" | **Auditoria explícita e offline** (`/orq:auditar`) — ledger de remoção ou análise de trace graph-first; sem hook, captura viva ou bloqueio |
-| "quem tá revisando?" · "troca o modelo do planner" · "quero o Fable planejando" (Fable 5.1) · "tira o GPT" · "tô com pouco crédito" · "acabando os créditos" · "final do ciclo semanal" · "modo economia" · e qualquer pedido de sair do perfil ou voltar ao time normal | **Elenco** (`/orq:elenco`) — mostra ou ajusta qual LLM toca cada papel; frase de contexto de crédito troca o **time inteiro** pelo perfil nomeado (`perfil economia` / `perfil padrao`), anunciando o que muda, **o que se perde** e **como reverter** — sem depender de uma frase fixa de volta, que ele pede naturalmente quando o crédito voltar |
+| "quem tá revisando?" · "troca o modelo do planner" · "quero o Fable planejando" (override legado; o padrão é `claude-opus-5-5`) · "tira o GPT" · "tô com pouco crédito" · "acabando os créditos" · "final do ciclo semanal" · "modo economia" · e qualquer pedido de sair do perfil ou voltar ao time normal | **Elenco** (`/orq:elenco`) — mostra ou ajusta qual LLM toca cada papel; frase de contexto de crédito troca o **time inteiro** pelo perfil nomeado (`perfil economia` / `perfil padrao`), anunciando o que muda, **o que se perde** e **como reverter** — sem depender de uma frase fixa de volta, que ele pede naturalmente quando o crédito voltar |
 | "lembra quando a gente…?" · "o que a gente decidiu sobre…?" | **Busca a memória em DUAS etapas, nesta ordem.** (1) **Wiki do projeto** — `memory/MEMORY.md` e a página ou thread do assunto. É a fonte da verdade: se ela responde, acabou. (2) **Não achou, ou achou incompleto → busque a memória de sessão, chamando a ferramenta pelo nome.** Com `claude-mem` instalado, ele expõe `mem-search` (e `search`/`smart_search` no MCP) para procurar, e `get_observations([IDs])` para abrir o que interessar. **Nomeie e chame** — "consultar alguma busca do host" não é instrução, é o motivo de isto nunca ter disparado. Só pule a etapa 2 se não houver busca instalada **ou** se ela estiver como **Dispensada** em `memory/wiki/_stack.md`; provider dispensado nunca vira fallback só por estar conectado. Sem busca elegível, **declare** que a cobertura ficou limitada à wiki — não finja que procurou |
 | "tá lento" · "o que falta instalar?" · "dá pra melhorar a performance?" · "que ferramenta ajudaria?" | **Stack** (`/orq:stack`) — detecta o que falta, mostra ganho e custo, instala **só o que ele aprovar** |
 | "o revisor sumiu" · "a statusline está muda" · "não conecta com X" · "parece que o plugin não pegou" — queixa sobre o **ferramental** (plugin, revisor, statusline, MCP, PATH), nunca sobre o que o produto faz | **Diagnóstico** (`/orq:stack --verificar`) — checa plugin desatualizado (versão **e** conteúdo), escopo errado, binário fora do PATH, board ilegível. **Antes de dizer que algo falta, cheque o caminho de instalação** — `which` só enxerga o PATH daquela sessão |

diff --git a/orq/commands/revisar.md b/orq/commands/revisar.md
index 8b95ee0..5434919 100644
--- a/orq/commands/revisar.md
+++ b/orq/commands/revisar.md
@@ -89,7 +89,7 @@ Prompt **READ-ONLY explícito** ("não implemente nada, não edite arquivos"). P
 afirmação + achados priorizados com `arquivo:linha` + cenário de falha concreto.
 
 **Host Codex — titular Anthropic pelo runner.** No host Codex, o titular é o modelo Anthropic
-resolvido da linha `reviewer` do elenco (hoje `fable`, Fable 5.1), executado pelo runner; o Manager
+resolvido da linha `reviewer` do elenco (hoje `claude-opus-5-5`), executado pelo runner; o Manager
 OpenAI só audita: ele não vira parecer.
 
 O briefing tem orçamento de **16 KiB = 16.384 bytes UTF-8 por lote, medidos depois da
@@ -98,7 +98,7 @@ independentes, repetindo em cada lote o objetivo, os critérios e o fora de esco
 hunks e registre a cobertura. **Nunca corte bytes nem resuma em silêncio** para caber. Um lote
 omitido ou que falhar torna a cobertura do parecer parcial — e isso se declara.
 
-**Nunca chamar o runner sem `--model`:** sem a flag ele cai no default `opus`, e repetiria a
+**Nunca chamar o runner sem `--model`:** sem a flag ele cai no default `claude-opus-5-5`, e repetiria a
 contradição que motivou este card — elenco declarando um modelo, execução rodando outro.
 
 ```bash
@@ -119,14 +119,15 @@ O runner anuncia `OPUS_STARTED` imediatamente **no stderr** e aplica timeout de
 acomoda a latência real observada de 267,1s em revisão arquitetural, sem remover a proteção contra
 processo órfão. A validação
 de tamanho ocorre antes do anúncio: `BRIEFING_TOO_LARGE` significa que nenhuma chamada começou;
-redivida o lote e execute, sem contar isso como retry. O runner exige o prefixo do alias pedido no
-`modelUsage` JSON (hoje, `fable` exige `claude-fable-5-1`) e não imprime parecer em modelo errado,
+redivida o lote e execute, sem contar isso como retry. O runner exige igualdade para a opção
+explícita `claude-opus-5-5` e preserva a prova por prefixo dos aliases legados no `modelUsage` JSON;
+não imprime parecer em modelo errado,
 timeout, erro ou saída vazia (`OPUS_EMPTY_RESULT`). `OPUS_EXIT != 0`, `OPUS_OUT` vazio ou qualquer
 lote incompleto → **REVISÃO DEGRADADA** com o diagnóstico do stderr;
 não faça retry automático após chamada iniciada, para não duplicar custo.
-Todo host que invocar o runner com um alias precisa verificar que o `modelUsage` comprova o prefixo
-daquele alias antes do parecer. Se a resolução não puder ser comprovada, trate o modelo como ausente
-e marque **REVISÃO DEGRADADA**, sem trocar de modelo nem alargar o prefixo aceito.
+Todo host que invocar o runner com uma opção precisa verificar igualdade para o ID explícito ou o
+prefixo esperado para alias legado antes do parecer. Se a resolução não puder ser comprovada, trate
+o modelo como ausente e marque **REVISÃO DEGRADADA**, sem trocar de modelo nem alargar a prova aceita.
 
 ### Titular indisponível → REVISÃO DEGRADADA, e o card não avança sozinho
 

