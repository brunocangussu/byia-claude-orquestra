---
description: Fecha o bloco de trabalho — atualiza a wiki de memória (log + páginas + thread) para reiniciar ou compactar sem perder a linha de raciocínio
argument-hint: "[rótulo do marco — opcional; se presente, cria snapshot]"
---

Você é um **mantenedor disciplinado de wiki**, não um chatbot. Faça um **CHECKPOINT durável**:
registre o conhecimento FORA da janela, para ela poder ser reiniciada ou compactada sem perder nada.
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
  saída**: é a âncora da seção `📋 Board` do relatório final (passo 6). **Não** a chame de "antes" —
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
  ainda não tem página e é recorrente, **crie**. (Isto não é a "iniciativa própria" que o N1 da
  skill `orq` restringe — o checkpoint só roda quando o dono pede, mesmo em frase natural como
  "terminamos"; a correção de página aqui vale sem pedir ok de novo.)
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

## 5. Verificar ANTES de emitir o handshake do host

A frase final é a promessa deste comando — sustente-a antes de fazê-la e emita **exatamente uma**,
conforme o host real:

- **Claude:** termine com a frase exata **Seguro dar `/clear`.**. O dono executa `/clear`
  manualmente; este fluxo permanece inalterado.
- **Codex:** termine com a frase exata **Checkpoint verificado; compactação liberada.**. O guardião
  grava `checkpoint_verified`, deixa de bloquear trabalho novo e permite a compactação nativa,
  manual ou automática. Depois de `SessionStart(source=compact)`, a sessão relê a memória, o board
  e a thread ativa.

Nunca emita as duas frases na mesma resposta. Se uma verificação falhar, emita somente a frase
negativa do contrato e corrija o sinal quebrado; texto equivalente não destrava o guardião.

**Com board**, rode de novo `sh ${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh .` e confira:

1. saída **vazia havendo cards escritos** no board → nenhum card reconhecido *(board legitimamente
   sem card sai vazio e está correto — não é falha)*;
2. **`⚠N`** no fim → N linhas parecem card e não casam o contrato;
3. **denominador ≠ contagem manual** dos cards acima da seção `## …Arquivad…`.

**Com thread ativa:** ela termina em **⏭️ RETOMAR AQUI**?

**Vai afirmar que dá pra FECHAR a janela?** Então tudo que você põe na seção ⏸️ tem que sobreviver
sem ela — em card **`[!]`** com a pergunta escrita (decisão) ou **`[?]`** com o que testar (validação).
São os dois estados que o `/orq:quadro` mostra como espera dele. Card em `[>]` ou `[~]` cai em
"🟡 Fazendo", que a próxima janela lê como *trabalho em curso*, não como *aguardando o dono* — a
pendência desaparece do lugar onde ele olha. Nesse caso, mova o card ou afirme apenas que é seguro dar
o handshake do host. Fechar a janela é irreversível: o transcript vai embora, e só o disco resta.

**Falhou qualquer um → corrija e verifique de novo; não afirme "seguro" por cima de verificação
falhando.** Falha que não é sua (outra janela)? Reporte-a no lugar da afirmação. O que o projeto não
tem (board, thread) não se verifica — e não bloqueia.

## 6. Confirmar — a audiência é o DONO, não o próximo assistente

A instrução de retomada ("leia `memory/MEMORY.md` → thread X") é para a **próxima janela** — e ela
**nunca lê esta tela**: o que ela lê é o `⏭️ RETOMAR AQUI` e o índice, que você acabou de escrever
e verificar. Na tela, só o que serve ao dono.

**Seções com título, uma por bloco, nesta ordem.** Duas são **sempre presentes** (`✅ Verificação` e
o fecho `💡`); as outras aparecem **só quando têm conteúdo** — e `📋 Board` aparece sempre que o
projeto tiver board, mesmo que a sessão não tenha movido card (o `X%` é a âncora).

Escreva **renderizado na tela**, não dentro de cerca de código — o espaçamento é o ponto:

    ### ⏸️ Esperando você                                        [só se houver]

    - <card + a pergunta exata — TUDO que depende dele mora aqui>

    ### 📋 Board · <X% (feitos/total)>                           [sempre que houver board]

    - **<T-NNN>** → <para onde foi>
    - **Nasceram:** <IDs>

    ### 💾 Gravado                                               [só se houver]

    - log · <páginas tocadas> · thread <nome> (⏭️ ok)

    ### ⛔ Não entrou                                            [só se houver]

    - <deixado de fora — e por quê, em meia linha>
    - <tentado e falhou>

    ### ✅ Verificação                                           [SEMPRE]

    - <parser X/Y = contagem manual · sem ⚠ · thread ⏭️>

    **<handshake exato do host: Claude ou Codex>**

    ---

    💡 Ao voltar, nada é seu — a próxima janela lê `memory/MEMORY.md` sozinha.
    Se quiser o board: "onde paramos".

**O que faz este formato funcionar — e o que o quebra:**

- **Espaçamento é a informação.** O título e a linha em branco existem para o olho pular direto ao
  bloco que interessa. Colapsar em prosa corrida devolve o problema que este formato resolveu:
  relatório denso é relatório que o dono não lê. **Nunca junte seções para "economizar linhas".**
- **Bullet de uma linha, não parágrafo.** Não há teto de linhas — há teto de **densidade**. Precisou
  de parágrafo para explicar um item? Ele não pertence ao relatório: vira card, ou já mora na thread.
- **A seção Verificação nunca desaparece, e carrega a evidência — nunca só o ✓.** Sem os números ela é
  indistinguível de um checkpoint que não rodou nada, que é o defeito do passo 5. Ela é também a única
  que autoriza o handshake: suprimi-la deixa o dono sem resposta. **Rodou o `wiki-lint` por iniciativa
  própria (N1) neste checkpoint?** O achado dele entra como bullet **aqui** — é evidência de verificação,
  não seção à parte, mas **não é sinal de verificação falhada**: o N1 só lê e nunca corrige (nem o
  trivial — ver skill `orq`), então o achado nunca troca o título para `⚠️ Verificação falhou` nem
  impede o handshake do host. Projeto sem board nem thread? Ela
  aparece dizendo o que **não** havia a verificar, e autoriza:

      ### ✅ Verificação
      - projeto sem board nem thread — nada a verificar
      **<handshake exato do host: Claude ou Codex>**

- **Falhou um sinal?** Título vira `### ⚠️ Verificação falhou`, diga **qual** sinal e **o que corrigir**,
  e troque a linha em negrito por esta — nunca a omita, senão o dono fica sem saber onde está (o
  achado do `wiki-lint` reportado acima nunca conta como esse sinal):

      ### ⚠️ Verificação falhou
      - <qual sinal> — <o que corrigir>
      **Gravado, mas NÃO afirmo que é seguro limpar.**

- **"Pode fechar a janela" é informação separada, nunca mutação do handshake.** Quando o gate do
  passo 5 permitir (pendência em card `[!]` ou `[?]`), acrescente outra frase ou bullet depois do
  handshake. Nunca altere a frase exata do Claude ou do Codex e nunca escreva a condição na tela.
- **Tudo que espera o dono fica na seção ⏸️** — inclusive card aguardando validação. "Não entrou"
  é só para o que **não** depende dele. Pendência espalhada em duas seções faz ele agir na primeira e
  não ver a segunda.
- **Board é estado, não delta calculado.** O número do passo 2b já inclui o que a sessão moveu antes do
  checkpoint, então "antes → depois" mentiria com os dois lados iguais. O delta verdadeiro é a **lista
  de movimentos**; o total é só a âncora. E a saída do script já começa com `📋` — não duplique.

## Regras
- **NÃO** faça `git commit`/`push` sem o usuário pedir.
- **NÃO** invente: registre só o que aconteceu de fato nesta sessão.
- Sessão trivial (nada relevante)? Diga isso em vez de forçar entrada.
- Densidade > extensão. Página de tópico deve caber numa leitura (~150 linhas).
