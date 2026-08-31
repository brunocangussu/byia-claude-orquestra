# T-049 — verificador de instalação cross-host

**Estado:** validada e fechada em 2026-08-31 · **frente:** `@frente-auditoria-nativa`.

## Objetivo

Eliminar o falso negativo da verificação pós-instalação sem tornar o contrato permissivo: somente
artefatos comprovadamente gerados pelo host podem ser ignorados; qualquer outro extra, ausência ou
divergência de bytes continua falhando.

## Evidência de origem

- Claude cria `.in_use/` no cache instalado.
- Codex cria `.codex-plugin/migrated-command-skills/` no cache instalado.
- O núcleo da 0.22.5 permaneceu byte-idêntico quando esses dois caminhos foram excluídos da comparação.
- `orq/commands/instalar.md` ainda orienta `diff -rq` bruto e por isso acusa esses caches corretos.

## Restrições

- A allowlist deve depender do host e valer somente no lado do cache instalado.
- `.in_use` ou `.codex-plugin` presentes na fonte continuam sendo divergência.
- Não aceitar outros filhos de `.codex-plugin` nem outros extras por prefixo amplo.
- Nenhuma instalação, cache real, hook, commit, push ou publicação muda durante o planejamento.

## Causa raiz confirmada pelo Planner

`orq/commands/instalar.md` (Codex) e `orq/commands/stack.md` (Claude) usam `diff -rq` bruto, que não
distingue metadado do host de produto divergente. O helper `find_cache_divergences` do lint também
não serve como CLI: compara somente arquivos, tem regras Claude embutidas, ignora nomes em ambos os
lados e está acoplado a verificações sem relação com instalação.

O desenho recomendado cria `orq/scripts/verify_installed_cache.py`: comparador puro tipado + CLI,
usado pelo lint, instalador e diagnóstico. A enumeração inclui diretórios vazios e tipos de entrada,
não segue symlinks e aplica a allowlist somente ao instalado. Plano completo:
`docs/superpowers/plans/2026-08-30-t049-verificador-instalacao.md`.

## Política recomendada pelo Manager

- Claude: permitir `.in_use` no topo (arquivo legado ou diretório/PIDs) e `.orphaned_at` no topo
  como arquivo regular, pois ambos são marcadores nominais da CLI Claude já cobertos pela T-046.
- Codex: permitir somente `.codex-plugin/migrated-command-skills/` e seus descendentes, preservando
  a comparação dos outros filhos de `.codex-plugin`.
- Remover a exceção de `.DS_Store`: ela não é artefato nominal de nenhum host e hoje pode mascarar
  contaminação inclusive na fonte.
- Alvo de release: `0.22.7`, promovido após a colisão da 0.22.6 com a T-050; commit, instalação, push e publicação permanecem gates separados.

## Parecer do Planner

Planner real `gpt-5.6-sol@ultra`, em clone descartável e read-only. Recomendou uma implementação
compartilhada em vez de filtros de shell ou execução integral do lint. Matriz exigida: igualdade,
metadados válidos por host, homônimos na fonte, host trocado, prefixos parecidos, extras, ausências,
byte drift, diretório vazio, mudança de tipo, symlink e metadado válido junto de divergência real.

## Gate do dono

**Aprovado em 2026-08-30:** comparador compartilhado + CLI; `.orphaned_at` somente no cache Claude
instalado com `.DS_Store` estrito; candidata inicial `0.22.6`. Após a colisão com a T-050, o dono
aprovou reconciliação e promoção para `0.22.7`. Implementação inline por TDD. Commit, instalação,
push, publicação e restart continuam gates separados.

## Implementação

- ✅ Task 1: matriz com 9 testes escrita antes do produto; RED confirmou 9 falhas pela API ausente.
- ✅ Comparador mínimo implementado com entradas tipadas, diretórios vazios, bytes, symlinks sem
  follow e allowlist instalada-only por host; GREEN 9/9.
- ✅ `py_compile` e Ruff 3.12.12 passaram nos dois arquivos novos.
- ✅ Task 2: CLI com exits 0/1/2 e saída determinística, coberta por testes RED→GREEN.
- ✅ Task 3: lint, `/orq:instalar`, `/orq:stack` e documentação passaram a consumir o verificador
  compartilhado; `.DS_Store` voltou a ser divergência estrita.
- ✅ Task 4: candidata 0.22.7 aplicada nos cinco anchors ativos; suíte pré-rebase com 200 testes,
  Ruff, `claude plugin validate --strict`, lint de coerência, identidade AGENTS/CLAUDE e
  `git diff --check` verdes.
- ✅ Checkpoint de recuperação após compactação: memória, board, thread, branch e worktree
  reconciliados em 2026-08-30; nenhum gate externo foi cruzado.
- ✅ Opus 5 real confirmado pelo runner (`OPUS_MODEL=claude-opus-5`) deu GO final em produção,
  comparador, CLI/import, integração, comandos e contrato/versionamento. Os NO-GO intermediários
  geraram contraprovas e correções RED→GREEN antes dos pareceres finais.
- ⏸️ Kimi K3 foi invocado inicialmente em clone descartável, mas a API terminou com `403 weekly
  usage limit` antes de emitir `VERDICT`. Após autorização explícita do dono, uma nova chamada foi
  executada uma única vez em outro clone descartável e falhou com o mesmo `403`, stdout vazio e sem
  veredito. Nenhuma das tentativas conta como parecer e não haverá novo retry automático.
- ✅ Em 2026-08-30, o dono autorizou seguir sem o Kimi especificamente na T-049. A exceção fecha o
  gate de revisão desta task com o GO real do Opus 5, mas não transforma ausência de parecer em GO
  do Kimi nem muda automaticamente a política padrão de outras tasks.
- ✅ Gates frescos após todas as correções: 200 testes, `claude plugin validate --strict`, Ruff,
  lint de coerência, AGENTS/CLAUDE idênticos, cinco anchors e `git diff --check` verdes.
- ⚠️ No check pós-commit surgiram caches `0.22.6` em Claude e Codex com timestamps de 17:09. Os dois
  têm o mesmo `commands/instalar.md` antigo (`sha256 51300f…`), divergem em sete arquivos e não
  contêm `scripts/verify_installed_cache.py` nem seu teste. A fonte commitada tem hash `929a11…`
  nesse arquivo. Esta task não executou instalação e não sobrescreveu os caches externos.
- ⚠️ `origin/main` avançou em paralelo com `fbaff1c` (T-050, timeout do Opus) e `bc060b3` (registro
  da instalação), também usando a versão 0.22.6. A branch T-049 está 1 commit à frente e 2 atrás do
  merge-base `986a45d`, com nove arquivos sobrepostos. Instalar antes de reconciliar misturaria
  fonte local e release remoto e violaria o contrato novo.
- ✅ Reconciliação autorizada e concluída: rebase sobre `origin/main`, T-050 preservada, cinco
  anchors promovidos para 0.22.7 e nenhuma marca de conflito restante. A suíte combinada passou em
  201 testes, seguida de validate, Ruff, lint, identidade AGENTS/CLAUDE e `git diff --check` verdes.
- ✅ Push fast-forward autorizado e verificado: `deabd4d` chegou a `origin/main` sem force. Nenhum
  cache, marketplace local, Kimi ou sessão foi alterado durante o push.

## ✅ Validação final

Gate autorizado e verificação concluída em 2026-08-30. O SHA remoto final `41ed5da` foi clonado em
detached com `git status --porcelain` vazio e versão 0.22.7. Claude e Codex já apareciam instalados e
habilitados em 0.22.7 antes da mutação; seus caches reais passaram no verificador da fonte limpa com
`rc=0`. Em cópias descartáveis, `unexpected-extra.txt` produziu `extra` e `rc=1` nos dois hosts.
Não houve reinstalação redundante, alteração do Kimi nem restart.

Em 2026-08-31, o dono abriu a task Codex de validação com a frase natural *"onde paramos?"*. A
skill carregada veio do cache 0.22.7, e o Manager releu sequencialmente `memory/MEMORY.md`,
`memory/wiki/KANBAN.md` e esta thread antes de fechar o card. Na mesma task, os verificadores dos
caches reais Codex e Claude foram repetidos contra o pacote `orq/` sem diff no SHA `41ed5da`; ambos
retornaram `ok`/`rc=0`, e os dois hosts reportaram 0.22.7 habilitada.

O dono delegou explicitamente a conclusão da T-049 e manteve commit, push e restart fora do escopo.
Nenhum deles foi executado. O smoke Claude não é pendência deste card: continua condicionado a um
restart futuro em gate próprio. Não há `RETOMAR AQUI` ativo para a T-049.
