# Discussão para o Manager — o board vs. worktree por frente (app hospedeiro)

**Origem:** análise externa em 2026-09-03 sobre unificar Claude Code + Codex num app só.
**Status:** pedido de análise. **Nada deve ser editado antes da minha aprovação.**
**Trilha sugerida:** `sistema` · **Faixa sugerida:** ver opções (a) = nenhuma; (b) = `pesada`.

---

## O que eu quero decidir

Estou avaliando trocar os dois apps (app do Claude + app do Codex) por **um app hospedeiro** que
roda os dois CLIs na mesma janela. Os candidatos que fazem isso rodando o binário oficial em PTY —
portanto sem risco de política de assinatura — são **Warp** (abas, sem worktree automático),
**herdr** (multiplexador, sessões sobrevivem a fechar a janela, sem worktree automático) e
**Orca** (worktree-nativo).

O Orca é o mais completo (medidor das janelas de uso das **duas** assinaturas na mesma barra, troca
de conta a quente, ciclo de worktree do início ao fim), mas a documentação dele é explícita:

> "Instead of branching and stashing on one checkout, every task gets its own on-disk copy of the
> repo via `git worktree`."

**A pergunta:** o Orquestra sobrevive a um app em que **cada frente é um worktree**? E, se sim, ao
custo de quê?

---

## O problema, como eu o entendo

`memory/` é versionado (39 arquivos no git). O protocolo de várias janelas da `SKILL.md` diz
"releia antes de escrever" e "edite a linha, nunca o arquivo" — e isso pressupõe **um**
`KANBAN.md` no disco, disputado por N janelas.

Com uma frente por worktree, cada frente passa a ter o **seu próprio** `memory/wiki/KANBAN.md`, num
branch diferente. As janelas deixam de disputar o mesmo arquivo — passam a ter cópias divergentes
que só se encontram no merge. O modo de falha muda de "concorrência gerenciável" para
"bifurcação silenciosa", que é exatamente o que o protocolo existe para impedir. As threads
(`threads/<frente>.md`, arquivo de dono único) sofrem menos, mas o board sofre.

Some-se a isso que hoje o `implement-next` **já** roda o writer em worktree dedicado. Ou seja: o
worktree já existe no desenho, no lugar certo (o implementer). O que o app propõe é subir esse
isolamento um nível — para a frente inteira, incluindo o Manager.

---

## As três saídas que enxergo (quero seu parecer, não concordância)

### (a) Frente no checkout principal; worktree só para o implementer — *status quo*
O app abre o agente no diretório principal e o Orquestra continua criando o worktree no spawn do
implementer, como hoje. Custo zero no plugin.
**Risco:** depende de o app permitir. No Warp e no herdr, permite naturalmente. **No Orca, a doc não
descreve como rodar um agente fora de um worktree** — existe uma linha de workspace do "branch
padrão", mas sem opção documentada de desligar o isolamento. Preciso testar.

### (b) `memory/` fora do branch
O `init` passa a criar `memory/` como link para um diretório único e não versionado
(ex.: `~/.orq/<projeto>/memory` ou `<repo>/.orq-memory/` no `.gitignore`), e todo worktree enxerga
o **mesmo** board e a mesma wiki. Versionar a memória vira um commit deliberado a partir do
principal, não um efeito colateral do branch.
**Toca:** `init`, `checkpoint`, `verify_installed_cache.py`, `_schema.md` e a doc do protocolo
multi-janela. **Faixa:** `pesada`.
**Perguntas abertas que eu quero que você responda:** o board deixa de ser versionado — perdemos
histórico do board no git? Isso quebra o `wiki-lint` ou o verificador? Um symlink dentro de
worktree se comporta bem em macOS e no `git status`? Existe alternativa melhor que symlink
(ex.: `.worktreeinclude`, que Claude e Codex já honram)?

### (c) Board por frente, reconciliado no checkpoint
Cada worktree tem seu board e o `checkpoint` reconcilia.
**Minha posição:** contra. O `T-052` mostrou o custo de reconciliação, e aqui ela seria recorrente,
não pontual. Registro para você derrubar ou defender com argumento, não para adotar.

---

## O que eu quero de você

1. **Um parecer sobre (a) vs (b)**, com o custo honesto de cada um — inclusive o que se perde em
   (b) ao tirar o board do git.
2. **A lista dos pontos do produto que assumem "um `memory/` por checkout"** — quero saber o
   tamanho real da mudança antes de decidir, não depois.
3. **Um critério de teste** para o piloto: como eu comprovo, em duas frentes simultâneas, que nada
   sumiu do board? (O `T-013` já tem um critério; serve como está ou precisa de ajuste para o caso
   worktree?)
4. Se for o caso, **um card no board** com trilha e faixa — mas **não implemente nada** antes do
   meu "pode implementar".

---

## Contexto que muda a urgência

- Meu ritmo hoje é **uma ou duas frentes por vez**, em série: abro um chat por problema, resolvo,
  checkpoint, `/clear`, renomeio. Não opero cinco frentes paralelas. Então o ganho do worktree por
  frente é **potencial**, não uma dor atual.
- Por isso o plano provisório é: **Warp agora** (aba por frente, sem worktree, board intacto), Orca
  depois — e só se (a) ou (b) estiver resolvido.
- Eu **não domino** gerência de worktree. Qualquer solução que me obrigue a fazer `git worktree` na
  mão é pior do que parece no papel. Prefiro que o produto ou o app cuidem disso e me devolvam só
  o branch pronto.

---

## Fora do escopo desta discussão (não misturar)

- Qual app adotar — decido depois do seu parecer.
- `codex-plugin-cc` na Matriz de invocação, host sugerido pela trilha no `/orq:quadro`, faixas
  absolutas no guardião do Codex: são cards vizinhos, de outra frente.
