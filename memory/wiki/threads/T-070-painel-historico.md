# T-070 — afirmação vencida sobre o painel de três revisores

## Fato e decisão proposta

O `wiki-lint` N1 registrou a contradição em `T-054-economia-tokens.md:433-437`.
No snapshot `5032bf7`, `memory/MEMORY.md` diz que o painel Claude · Codex ·
Kimi **“funciona”**. O bullet está sob “Onde paramos”, foi introduzido no
checkpoint `5b75296` de 2026-07-28 e relata três ocasiões; não deve ser
atribuído a um ensaio de 2026-08-05. O presente gramatical compete com a
regra atual: **revisor único, vendor oposto ao host; painel encerrado e Kimi
aposentado**. A `main` paralela ainda contém a frase vencida, agora por volta
da linha 349; não há correção posterior a preservar ali.

Proposta mínima, **ainda não aprovada nem aplicada**: substituir só as três
linhas do bullet histórico por:

> O antigo **painel de três revisores** (Claude · Codex · Kimi) funcionou e se
> pagou três vezes: achou a brecha de instalação por slash command, o parser
> permissivo do board, e — na mesma rodada — Codex e Kimi acharam bugs
> **diferentes** no mesmo arquivo. **Esse painel foi aposentado pelo T-051;
> o contrato atual é revisor único, de vendor oposto ao host.**

Os demais bullets de “Onde paramos” são registro histórico, não alvo deste card.
Não criar regra geral de substituir todo “painel” — o lint apontou apenas
esta afirmação como vencida, e menções históricas continuam legítimas.

## Verificação planejada após aprovação

1. Rebase/integração cuidadosa da **linha específica** da `main`, que tem
   `MEMORY.md` modificado pelo Claude; não sobrescrever o arquivo inteiro.
2. `rg -n 'painel de três revisores|Revisor único|Kimi aposentado' memory/MEMORY.md`
   deve mostrar o episódio com verbo passado e a regra atual coerente.
3. Conferir manualmente o bullet anterior e o seguinte, as três ocasiões e a
   autoria distinta de Codex/Kimi para não mudar o contexto histórico;
   `git diff --check`. Executar
   `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'`,
   `claude plugin validate ./orq --strict` e
   `python3 orq/scripts/lint-coerencia.py .`. Registrar falhas preexistentes
   separadamente, sem declarar sucesso global se algum gate continuar vermelho.
4. Review documental do diff restrito ao bullet; só depois propor fechamento
   ao dono. Por ser alteração apenas em memória, não há bump de `orq/`.

## Histórico — checkpoint de recuperação

Worktree `codex/t070-memory-truth`, criado de `5032bf7`, somente plano/board/
índice. O Manager releu o índice, board e checkpoint T-062 pós-compactação;
T-062 segue sem autorização para R8 e T-076/T-071 aguardam decisão própria.
Baseline isolado: 332 testes, as mesmas quatro falhas preexistentes em
`test_elenco_perfis`, `test_observation_types_guard` e `test_write_flag_guard`.
O card está `[!] @codex`. Retomar pela proposta acima; **não** corrigir a
frase, revisar externamente, commitar, dar push ou integrar sem autorização.

Revisão interna do planner, 2026-09-14: a primeira proposta recebeu NO-GO por
cronologia falsa. A redação acima foi corrigida para preservar as três ocasiões
e os achados distintos; a rechecagem interna deu GO para levar ao gate. O gate
continua sendo sua aprovação explícita desta redação. A `main` e o bullet
publicado não foram alterados.

Revalidação noturna, 2026-09-15: o alvo ainda existe sem alteração em
`memory/MEMORY.md` da `main` (linhas 349–351), enquanto a regra atual de revisor
único e Kimi aposentado permanece registrada acima dele. O plano continua
necessário e restrito a esse único bullet. Como a `main` está modificada pela
janela Claude, a implementação deve esperar aprovação e então aplicar somente o
hunk dessa linha sobre o conteúdo relido, sem copiar o arquivo deste worktree.

Decisão do dono, 2026-09-15: plano aprovado e autorizada a correção documental
cirúrgica somente neste worktree, seguida de revisão. Permanecem vedados commit,
push e integração na `main`; nenhum outro bullet histórico entra no escopo.

## Revisão Fable 5.1 — 2026-09-15

O diff sanitizado e restrito a `memory/MEMORY.md` foi revisado pelo modelo
`claude-fable-5-1` com `exit 0` e veredito **APROVADO**, sem bloqueadores. A
revisão confirmou passado, três ocasiões distintas, achados diferentes de
Codex/Kimi, aposentadoria pelo T-051 e contrato atual de revisor único de vendor
oposto. O risco aceito é transitório: o parágrafo de índice que descreve o
worktree ficará falso depois da integração, portanto deve ser removido ou
reescrito no mesmo commit. A thread apontada existe neste worktree.

Verificação fresca pós-review: `git diff --check` e manifesto estrito verdes;
suíte descoberta com 332 testes e somente as quatro falhas basais já
registradas (T-081, chave morta e write-flag); lint com apenas o marcador basal
do T-081. Nenhuma dessas falhas foi causada pelo hunk documental do T-070.

## Decisão do dono e fechamento — 2026-09-15

O dono autorizou commit, push e integração allowlistados do T-070 em commit
separado. O parágrafo transitório do índice foi reescrito como registro durável,
e o card foi fechado porque a correção é exclusivamente documental, já passou
pela revisão Fable 5.1 e não depende de teste comportamental pós-release.

## ⏭️ RETOMAR AQUI — T-070 fechado

Não há ação pendente neste card. O arquivo `_noturno.md`, modificado no mesmo
worktree por outra frente, não pertence ao T-070 e permanece fora do commit.
