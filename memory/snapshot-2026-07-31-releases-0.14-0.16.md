# Snapshot — 2026-07-31 · 0.14.0, 0.15.0 e 0.16.0 entregues

Estado exato para retomar. Complementa o índice (`memory/MEMORY.md`) e a thread
`wiki/threads/desenvolvimento-do-plugin.md`; não substitui nenhum dos dois.

## Onde o produto está

**0.16.0** publicada, commitada (`e15101d`) e com push. Plugin em escopo `user`, cache idêntico ao
repo (`diff -rq` vazio). Board: **17% (5/28)**, **12 em VALIDATE**, nada em curso, nada esperando
decisão.

## O que entrou nestas três versões

| Versão | Entrega | O que o review pegou |
|---|---|---|
| 0.14.0 | `reload` × `restart` deixa de ser regra binária e vira **tabela de evidência por componente** | a correção **criou** contradição entre `orq/stack.md` e `orq/commands/stack.md`, e citou procedência errada num card cuja causa raiz é "afirmação sem procedência" |
| 0.15.0 | `/orq:ajuda` (cardápio por situação) · gatilhos medidos · **iniciativa em três níveis** | a SKILL afirmava que o `wiki-lint` "já proíbe corrigir" quando ele autorizava; o teto desligava a salvaguarda de contexto; "bloco de trabalho" não estava definido; dois gatilhos inventados |
| 0.16.0 | **perfis de elenco** (`padrao` · `economia`) trocados por frase | o template definia `padrao` como ponteiro para si mesmo (voltar virava no-op); a correção disso plantou o único caminho relativo do plugin |

## As três lições que valem mais que o código

1. **Corrigir é uma mudança como outra** — precisa da mesma revisão que o original. Nos três
   releases, o review achou defeito **criado pela correção anterior**.
2. **Não adivinhe a fala do dono.** Terceira reincidência do `T-014`: gatilho inventado em vez de
   medido, com o plano sabendo e a marca não chegando ao produto. A saída boa está na 0.16.0 —
   descrever a **intenção** como categoria e **ensinar** a frase no anúncio, no instante em que ele
   precisa dela.
3. **Gate verde não é prova.** Nenhum dos ~12 achados desta sequência foi pego por `validate` ou
   pelo lint. O caso extremo virou o card `T-029`: caminho relativo resolve **por acidente** dentro
   deste repo, porque o repo *é* o plugin — verde aqui, quebrado em qualquer outro projeto.

## Para retomar

Leia `memory/MEMORY.md` → `wiki/threads/desenvolvimento-do-plugin.md` (⏭️ RETOMAR AQUI). A fila
aprovada acabou; o próximo passo é o dono **validar** os 12 cards, e depois `T-029` → `T-028` →
`T-019` → `T-001`.
