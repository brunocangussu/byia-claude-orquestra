---
description: Fecha o bloco de trabalho — atualiza a wiki de memória (log + páginas + thread) pra você poder /clear sem perder a linha de raciocínio
argument-hint: "[rótulo do marco — opcional; se presente, cria snapshot]"
---

Você é um **mantenedor disciplinado de wiki**, não um chatbot. Faça um **CHECKPOINT durável**:
registre o conhecimento FORA da janela, pra ela poder ser reiniciada sem perder nada.
Contexto = RAM (descartável); memória em disco = HD (durável).

## 1. Descobrir a estrutura
Procure nesta ordem: `memory/wiki/_schema.md` (regras da wiki e **formato do board** — **se existir**;
instalações anteriores à 0.6.0 não têm, e a ausência dele não é erro) · `memory/MEMORY.md` (índice) ·
`memory/fixes-history.md` (log) · `memory/wiki/threads/` (trabalho em curso) · `docs/plano_*.md`.

**Vai mexer no board?** Siga o formato do `_schema.md`. Sem ele, o contrato é este — o parser lê por
posição: o ID **vem entre crases**, e negrito ou crase **envolvendo** o marcador ou o ID tira a
linha da contagem (ela reaparece como `⚠N`, mas o denominador encolhe sem alarde):

    - [ ] `T-001` Título curto — nota livre depois do travessão

**Se o projeto NÃO tem wiki**, crie o mínimo: `memory/MEMORY.md` (índice) + `memory/fixes-history.md`
(log) e siga — não precisa da estrutura completa num projeto pequeno.

## 2. Resumir ESTA sessão
O que foi decidido/implementado/corrigido/testado e qual o **PRÓXIMO passo**. Condensado, "o quê +
por quê" não-derivável. **Não** cole diffs nem listas de arquivos (o git já tem).

## 2b. RELEIA antes de escrever (outras janelas podem ter mexido)

O dono trabalha com **várias janelas abertas no mesmo projeto**, cada uma numa frente. O arquivo em
disco pode ter mudado desde que você o leu.

- **Releia `KANBAN.md`, o log e as páginas que você vai tocar — agora**, mesmo que já estejam no seu
  contexto. A cópia que você tem pode estar velha.
- **Ao reler o board, rode** `sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh .` **e guarde a
  saída**: é a âncora da linha de board do relatório final (passo 6). **Não** a chame de "antes" —
  ela já contém o que esta sessão moveu antes do checkpoint.
- **Altere apenas as linhas que são suas.** Nunca reescreva o `KANBAN.md` inteiro a partir da versão
  que você leu no começo da sessão: é isso que apaga o trabalho das outras janelas.
- **Mudou algo que você não fez?** Outra janela trabalhou. **Não sobrescreva** — incorpore e siga.
  Se não der para conciliar, registre no card e leve ao dono.

O protocolo completo está em `memory/wiki/_schema.md`, seção "Trabalho em VÁRIAS JANELAS".

## 3. Ingerir na wiki (a parte que importa — não pule)
- **LOG** (`fixes-history.md`): append no TOPO, formato greppável
  `## [AAAA-MM-DD] <tipo> | <título>` (tipos: `feat` `fix` `plan` `investig` `decisão` `incidente` `processo`).
  Havendo mais de uma frente ativa, **carimbe a frente** no título: `| @auth · rotação de token`.
- **PÁGINAS DE TÓPICO** (`memory/wiki/*.md`): **atualize as afetadas** — reescreva pra refletir o
  estado ATUAL; se o trabalho contradiz o que a página afirmava, **corrija a página**. Se o assunto
  ainda não tem página e é recorrente, **crie**.
- **THREAD ativa** (`memory/wiki/threads/*.md`): status das fases (✅/🔄/⬜), decisões novas (com o
  porquê, pra não re-litigar), perguntas abertas e — obrigatório — **⏭️ RETOMAR AQUI** com a próxima
  ação concreta. Thread concluída → sintetize nas páginas de tópico e mova pra `threads/_concluidas/`.
- **BOARD** (`wiki/KANBAN.md`): mova o que ESTA sessão moveu de fato e registre card que nasceu —
  formato do passo 1, regras de janelas do 2b. Guarde a lista de movimentos pro relatório.
- **GOTCHA** novo → `gotchas.md`.
- **ÍNDICE** (`MEMORY.md`): registre página/thread nova; atualize a linha de resumo do que mudou.
- **SNAPSHOT**: se `$ARGUMENTS` estiver presente (marco), crie
  `memory/snapshot-<AAAA-MM-DD>-<rótulo>.md` com o estado exato pra retomar.

## 4. Supermemory
Se a MCP `api-supermemory-ai` existir, `addMemory` com o resumo (tema + feito + próximo passo +
gotchas). Se falhar ou não existir, siga sem erro e avise que pulou.

## 5. Verificar ANTES de afirmar "seguro limpar"

"Seguro dar `/clear`" é a promessa deste comando — sustente-a antes de fazê-la.

**Com board**, rode de novo `sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh .` e confira:

1. saída **vazia havendo cards escritos** no board → nenhum card reconhecido *(board legitimamente
   sem card sai vazio e está correto — não é falha)*;
2. **`⚠N`** no fim → N linhas parecem card e não casam o contrato;
3. **denominador ≠ contagem manual** dos cards acima da seção `## …Arquivad…`.

**Com thread ativa:** ela termina em **⏭️ RETOMAR AQUI**?

**Vai afirmar que dá pra FECHAR a janela?** Então tudo que você põe na linha ⏸️ tem que sobreviver
sem ela — em card **`[!]`** com a pergunta escrita (decisão) ou **`[?]`** com o que testar (validação).
São os dois estados que o `/orq:quadro` mostra como espera dele. Card em `[>]` ou `[~]` cai em
"🟡 Fazendo", que a próxima janela lê como *trabalho em curso*, não como *aguardando o dono* — a
pendência desaparece do lugar onde ele olha. Nesse caso, mova o card ou afirme apenas que é seguro dar
`/clear`. Fechar a janela é irreversível: o transcript vai embora, e só o disco resta.

**Falhou qualquer um → corrija e verifique de novo; não afirme "seguro" por cima de verificação
falhando.** Falha que não é sua (outra janela)? Reporte-a no lugar da afirmação. O que o projeto não
tem (board, thread) não se verifica — e não bloqueia.

## 6. Confirmar (3–6 linhas — a audiência é o DONO, não o próximo assistente)

A instrução de retomada ("leia `memory/MEMORY.md` → thread X") é para a **próxima janela** — e ela
**nunca lê esta tela**: o que ela lê é o `⏭️ RETOMAR AQUI` e o índice, que você acabou de escrever
e verificar. Na tela, só o que serve ao dono.

Três regras fazem caber: **um bloco = no máximo 1 linha** (agregue dentro dela) · **linha até ~120
caracteres** (6 linhas de 300 chars não é relatório curto, é parágrafo com quebras) · **bloco marcado
`[cond]` não aparece quando não tem conteúdo**. Não couber? Vira card, não vira texto.

    ⏸️ Sua decisão: <card + pergunta exata; TUDO que espera você mora aqui>   [cond]
    Board: <estado agora> · <o que esta sessão moveu> · nasceram <IDs>        [cond: só com board]
    Gravado: log + <páginas tocadas> + thread <nome> (⏭️ ✓)                   [cond: só com thread]
    Não entrou: <deixado de fora · tentado-e-falhou>                          [cond]
    Verificação <✓ | ⚠>: <parser X/Y = contagem manual · sem ⚠ · thread ⏭️> — <o que é seguro>
    Ao voltar: nada é seu — a próxima janela lê memory/MEMORY.md sozinha; na dúvida, "onde paramos".

**A linha de verificação carrega a evidência, nunca só o ✓** — sem os números ela é indistinguível de
um checkpoint que não rodou nada, que é o defeito que este passo existe para matar. Duas formas:

- passou → `Verificação ✓: parser 4/22 = contagem manual · sem ⚠ · thread ⏭️ — seguro dar /clear`
  (e `+ fechar a janela` **só** se a pendência estiver em card `[!]`, conforme o passo 5);
- falhou → `Verificação ⚠: <qual sinal> — gravado, mas NÃO afirmo seguro; <o que corrigir>`.

**Estado do board, não delta calculado.** O número do passo 2b já inclui o que a sessão moveu antes do
checkpoint, então "antes → depois" mentiria com os dois lados iguais. O delta verdadeiro é a **lista de
movimentos** — ela é a informação; o total é só a âncora. Cuidado: a saída do script já começa com
`📋`, não duplique.

**Tudo que espera o dono vai na linha ⏸️** — inclusive card aguardando validação. A linha "Não entrou"
é só para o que **não** depende dele: deixado de fora, tentado-e-falhou. Espalhar pendência em duas
linhas faz ele agir na primeira e não ver a segunda.

## Regras
- **NÃO** faça `git commit`/`push` sem o usuário pedir.
- **NÃO** invente: registre só o que aconteceu de fato nesta sessão.
- Sessão trivial (nada relevante)? Diga isso em vez de forçar entrada.
- Densidade > extensão. Página de tópico deve caber numa leitura (~150 linhas).
