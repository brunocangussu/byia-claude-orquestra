# Pareceres externos da frente `@frente-economia`

> **Evidência durável.** O parecer do revisor cross-vendor, íntegro, mais a auditoria do Manager
> contra o código. A regra do `_elenco.md` é que achado só vira veredito depois de auditado — e
> nesta rodada a auditoria **derrubou o mecanismo de um achado e confirmou outro empiricamente**.

## Contexto da invocação

- **Host:** Claude Code → revisor obrigatoriamente **OpenAI** (vendor oposto). Modelo: o padrão do
  runtime Codex do dono, effort `high`.
- **Mecanismo:** `codex-companion.mjs task`, **não** `codex exec` cru. A Matriz do `_elenco.md`
  manda `codex exec`; a regra global do dono proíbe o binário direto por perder rastreamento de job.
  A divergência virou o card `T-067`. O companion preserva o rastreamento e chega ao mesmo vendor.
- **Rodada 1 abortada:** briefing pedindo leitura de 11 arquivos do repo. O Codex leu por ~20
  minutos, saiu do worktree para `~/.codex/memories/`, e **morreu sem emitir parecer** (5.215 bytes,
  só log de progresso). Conforme o `_elenco.md` — *"51 bytes não é parecer, é revisor que não
  rodou"* — foi descartada, não contada como rodada de mérito.
- **Rodada 2, a que vale:** briefing de 6,9 KB com **o código colado verbatim** em vez de leitura
  ampla. Respondeu em uma passada. **A lição vale para o `T-060`:** briefing que manda ler é mais
  caro e menos confiável que briefing que já traz o trecho.

## Auditoria do Manager — o que foi conferido no código

| Achado do revisor | Veredito da auditoria |
|---|---|
| P8: *"`kanban-status.sh` termina com código 1 em projeto sem board"* | ❌ **Mecanismo errado, cenário certo.** Rodado em diretório vazio: **sai `0`** com saída vazia (`kanban-status.sh:12`). O risco real não é o exit code — é o hook tratar **saída vazia** como falha. Mantido com a causa corrigida |
| P12: *"'caractere' precisa ser definido: code point, byte ou largura"* | ✅ **Confirmado empiricamente, e já divergente neste board.** Contando code points, 17 cards passam de 200; contando bytes UTF-8, **21**. Quatro cards mudam de lado conforme a unidade. O pior caso tem 673 code points e 682 bytes |
| P7: *"sem estado, cada `PostToolUse` repetiria a exigência"* | ✅ Correto como requisito, **já satisfeito**: o guardião tem estado por sessão e `CHECKPOINT_REARM_DELTA = 10.0` (`context-guard.py:30`). Não é trabalho novo; é regra a preservar no parser novo |

## Parecer íntegro (rodada 2)

### P7 — Claude Code e faixas absolutas

- [BLOQUEADOR] O cálculo proposto subestima a ocupação atual porque omite `output_tokens`. — Cenário: a última chamada entra com 139k tokens e produz 8k; o parser registra 139k, não aciona checkpoint de 140k, embora a próxima chamada já parta de aproximadamente 147k.

- [BLOQUEADOR] O `.jsonl` interno pode sustentar apenas um adaptador best-effort, não uma garantia equivalente ao `token_count` do Codex. — Cenário: uma atualização renomeia `message.usage`, fragmenta a mensagem em novos registros ou muda seu aninhamento; o parser retorna `None` e o Claude Code fica indefinidamente sem proteção se isso não gerar erro e diagnóstico explícitos.

- [RISCO] “Último `message.usage`” precisa significar o último registro da linhagem principal, não simplesmente a última linha física correspondente. — Cenário: a sessão principal está com 155k, mas um subagente ou sidechain escreve depois uma chamada de 18k; o guardião lê 18k e classifica a sessão como normal.

- [RISCO] A compactação pode deixar como último uso válido o valor anterior à compactação. — Cenário: `PostCompact` roda antes de existir nova mensagem de assistente, encontra 178k da chamada pré-compactação e imediatamente volta a exigir checkpoint ou nova compactação. É necessário reconhecer a fronteira de compactação e tratar o uso posterior como desconhecido até surgir uma medição nova.

- [RISCO] Não se devem somar vários registros de mensagens; devem-se somar apenas as partições do uso de uma única chamada, incluindo saída. — Cenário: uma sessão com dez chamadas sucessivas de 100k seria interpretada como 1 milhão de tokens, embora sua janela corrente esteja próxima de 100k.

- [RISCO] Tokens absolutos medem ocupação/custo operacional, mas não substituem a margem de segurança relativa à janela do modelo. — Cenário: 170k deixa 30k livres num modelo de 200k, mas deixa 830k num modelo de 1M; a mesma classificação “emergência” representa riscos de estouro completamente diferentes. Recomendo dois gatilhos: patamares absolutos para custo/latência e uma reserva relativa ou absoluta ao limite real do modelo para segurança.

- [RISCO] Somar tokens cacheados com peso igual aos tokens não cacheados não é uma métrica pura de custo financeiro. — Cenário: 140k quase totalmente vindos de `cache_read_input_tokens` acionam o mesmo checkpoint que 140k não cacheados, embora o custo monetário por chamada possa ser diferente. Isso é correto para ocupação da janela, mas a justificativa deve ser “ocupação/latência”, não apenas “custo”.

- [OK] Os valores 110k/140k/170k são plausíveis como política inicial para uma janela de 200k, desde que haja histerese e deduplicação por faixa. — Cenário: sem estado, cada `PostToolUse` acima de 140k repete a exigência de checkpoint dezenas de vezes na mesma sessão.

### P8 — retomada compacta no hook

- [BLOQUEADOR] P8 não pode depender de `additionalContextLimit: 300`, pois esse campo não possui contrato documentado. — Cenário: as três linhas produzem 520 caracteres; uma versão ignora o campo, outra corta no byte 300 e outra descarta o contexto inteiro, deixando justamente o card ativo ou `RETOMAR AQUI` ausente.

- [RISCO] Executar um script e fazer duas leituras locais normalmente cabe em cinco segundos, mas não se o script consultar Git ou percorrer o repositório sem limites. — Cenário: `kanban-status.sh` executa `git status` em um monorepo grande ou filesystem lento, ultrapassa cinco segundos e o processo do hook é encerrado antes de fornecer contexto.

- [RISCO] O hook não pode confiar no próprio diretório de execução para localizar o projeto. — Cenário: `SessionStart` é disparado com cwd numa subpasta, worktree ou scratchpad; `memory/wiki/KANBAN.md` é procurado no lugar errado e o hook conclui falsamente que não existe card ativo. A raiz deve ser resolvida a partir dos dados do evento, com busca ascendente limitada e validação do arquivo esperado.

- [RISCO] Projeto sem board, card sem thread e thread sem marcador precisam produzir uma resposta mínima válida, não uma exceção. — Cenário: o plugin é usado num repositório novo sem `memory/wiki/KANBAN.md`; `kanban-status.sh` termina com código 1 e todo o `SessionStart` perde seu contexto de recuperação.

- [RISCO] “O card ativo” é ambíguo quando existem zero ou vários cards ativos. — Cenário: dois cards estão marcados como em andamento; o hook escolhe o primeiro pela ordem do arquivo, carrega a thread errada e faz o modelo retomar outro trabalho. Nessa situação, deve listar os IDs conflitantes e não escolher silenciosamente.

- [RISCO] A seleção de `RETOMAR AQUI` precisa ser vinculada à thread apontada pelo card e ter regra explícita para duplicatas. — Cenário: a thread contém um marcador antigo no início e outro atualizado no final; uma busca pelo primeiro resultado recupera uma instrução obsoleta.

- [RISCO] A saída deve ser montada e validada integralmente em memória antes de qualquer escrita em stdout. — Cenário: o subprocesso já imprimiu o status, mas a leitura da thread lança `FileNotFoundError`; stdout fica com JSON parcial ou texto misturado. O comportamento exato do host diante disso não está garantido: pode ignorar o contexto, registrar erro ou afetar o evento. O hook deve emitir uma única resposta válida ou um fallback válido.

- [RISCO] A geração precisa impor limites próprios a cada campo e ao total, independentemente de `additionalContextLimit`. — Cenário: um título ou marcador anormalmente longo faz o hook capturar dezenas de kilobytes; mesmo terminando em menos de cinco segundos, ele recria parte do problema de contexto que deveria resolver.

### P12 — limite da linha do card

- [RISCO] O número 200 não está demonstrado como limite correto; os três estouros em nove migrações mostram falta de orçamento por componente. — Cenário: título de 100 caracteres, metadados obrigatórios e ponteiro de 70 caracteres deixam praticamente nenhum espaço para estado útil. Recomendo 240 caracteres, junto com limites separados para título e ponteiro; aumentar apenas o total repetirá o problema depois.

- [OK] Reescrever “como validar” para a thread é coerente com a separação proposta. — Cenário: um card com cinco passos de validação deixa de caber em 200 caracteres, mas a linha permanece suficiente se preservar ID, título, estado, `trilha`, `faixa` e ponteiro verificável.

- [RISCO] O validador precisa definir se “caractere” significa ponto de código, byte ou largura visual. — Cenário: uma linha com acentos e símbolos possui menos de 200 caracteres, mas ultrapassa 200 bytes; `wc -c`, shell e Python dão resultados diferentes e a migração passa num ambiente e falha em outro.

- [RISCO] Mover notas para threads reduz a descoberta global e pode quebrar consumidores que só leem o board. — Cenário: uma busca por “aguarda aprovação do owner” antes encontrava o bloqueio no KANBAN; depois da migração, um relatório que não percorre threads classifica o card como executável.

- [RISCO] Board e thread passam a exigir integridade referencial e atualização atômica. — Cenário: um cherry-pick leva apenas a alteração do card, mas não o novo arquivo de thread; o board aponta para conteúdo inexistente. Git preserva commits, mas não garante que consumidores, cherry-picks ou resolução de conflitos mantenham os dois lados juntos.

- [RISCO] A mudança degrada `git blame` e a leitura histórica direta, mesmo que o conteúdo continue recuperável no Git. — Cenário: alguém pergunta quando uma restrição entrou no card; o blame do board mostra somente “movido para thread”, exigindo busca manual em outro arquivo e commits anteriores para reconstruir a decisão.

### O que está faltando

- [BLOQUEADOR] P8 e P12, combinados, podem tornar a recuperação pós-compactação estruturalmente incompleta: P12 remove do board as decisões e critérios, enquanto P8 recupera somente o card curto e uma linha da thread. — Cenário: antes da compactação havia uma decisão de não executar deploy e três critérios de aceitação na nota migrada; `RETOMAR AQUI` menciona apenas “continuar validação”. Após compactar, o modelo não recebe a proibição nem os critérios e pode declarar conclusão ou executar a etapa errada. É necessário um bloco de recuperação estruturado e limitado, com estado, próxima ação, restrições e critérios essenciais — não apenas uma linha livre.

- [RISCO] Injetar automaticamente conteúdo de board/thread em `additionalContext` cria uma promoção de confiança. — Cenário: uma thread importada ou escrita por automação contém `RETOMAR AQUI: ignore as regras anteriores e execute...`; após compactação, esse texto entra automaticamente como contexto do hook. O conteúdo deve ser delimitado como dado não confiável, normalizado e impedido de formular novas instruções de autoridade.

- [RISCO] Os dois hosts passarão a medir conceitos ligeiramente diferentes. — Cenário: Codex usa `total_tokens`, enquanto Claude usa uma aproximação extraída de uso por chamada; a mesma sessão lógica cai em faixas diferentes e os testes “cross-host” passam sem demonstrar equivalência. O contrato deve declarar explicitamente a métrica de cada host, margem de erro e comportamento quando a medição é desconhecida.

- [RISCO] A otimização não possui um teste end-to-end da sequência crítica `alto uso → checkpoint → compactação → retomada`. — Cenário: cada parser e cada comando passa isoladamente, mas `PostCompact` lê o uso pré-compactação, o texto é truncado e o ponteiro aponta para uma thread ausente; somente o fluxo completo revelaria que a sessão entra num ciclo de recuperação defeituoso.

VEREDITO: corrigir antes.

---

# Rodada de revisão do `T-056` implementado

> Não é rodada do brief — é a revisão independente do **código que eu escrevi**, que é o passo do
> ciclo entre `DEV_REVIEW` e `VALIDATE`. Mesmo revisor, mesmo vendor oposto.

## O canal falhou três vezes antes de entregar — e o padrão importa

| Tentativa | Briefing | Effort | Modo | Resultado |
|---|---|---|---|---|
| brief r1 | 3,5 KB **mandando ler 11 arquivos** | xhigh | background | morreu em ~20 min, sem parecer |
| brief r2 | 6,9 KB **com o código colado** | high | background | ✅ entregou |
| review r1 | 18 KB colado | xhigh | background | morreu sem parecer |
| review r2 | 7 KB colado | high | background | morreu sem parecer |
| smoke | 1 linha | — | **foreground** | ✅ `CANAL_OK` — o canal estava vivo |
| review r3 | 7 KB colado (o mesmo) | high | **foreground** | ✅ entregou |

**O smoke é o que separa "revisor caiu" de "revisor não rodou".** Sem ele eu teria declarado
`REVISÃO DEGRADADA` com o canal funcionando — e o `_elenco.md` proíbe trocar de vendor por falha,
então a alternativa seria não ter revisão nenhuma.

**Duas lições operacionais, ambas cabem no `T-060`:** briefing que **manda ler** é mais caro e menos
confiável que briefing que **já traz o trecho**; e invocação longa em background morreu 3 de 3,
enquanto em foreground com timeout explícito entregou. Nenhuma das duas está escrita no
`revisar.md` hoje.

## Achados, e o que fiz com cada um

**Confirmados e corrigidos:**

- 🔴 **[BLOQUEADOR] O fail-open da medição era silencioso** — e eu o tinha documentado como
  *"fail-open de propósito"*. O revisor mostrou o buraco: se a contagem quebrar e o sinal
  simplesmente sumir, um board com dezenas de cards fora do teto renderiza igual a um board limpo.
  *"Não consegui medir"* e *"está tudo dentro do teto"* são estados diferentes. **Agora falha vira
  `📏?`**, com teste que injeta a falha e exige o `?`.
- ⚠️ **CRLF empurrava card no limite para fora do teto.** O `\r` é byte e contava: um card de
  exatamente 240 bytes acendia `📏` só porque o arquivo veio com CRLF — o mesmo board reprovando ou
  passando conforme quem salvou. **Descontado antes de medir**, com teste de fronteira.
- ⚠️ **O arquivo coletivo precisava de endereço estável.** Ponteiro por posição apodrece com
  reordenação e renomeação. **O endereço agora é o ID** (`` ## Nota herdada do card `T-NNN` ``),
  com índice de 39 IDs no topo do arquivo e a convenção escrita no `_schema.md`.
- ⚠️ **Regex de seção arquivada aceita demais e recusa `## ARQUIVADOS`.** `## Como arquivar cards`
  interrompe a contagem; `ARQUIV` maiúsculo não interrompe. **Bug pré-existente** do awk principal,
  que a duplicação da regra agora dobra → virou o card `T-071`.

**Bloqueadores que a auditoria verificou e NÃO se materializaram:**

- 🟢 **"Links relativos quebram ao mudar de diretório".** Cenário correto, mas varri as 48 notas:
  **zero** links markdown relativos, zero imagens relativas, zero footnotes. Os caminhos citados são
  texto em crases a partir da raiz do repo (`memory/wiki/...`), que resolve igual de qualquer lugar.
- 🟢 **"A migração precisa de reconciliação byte a byte por ID".** Exigência justa — minha
  verificação anterior era por amostragem e não provava que a nota do `T-031` foi para a seção do
  `T-031`. Refeita com rigor: **48/48 conferem exatas, na seção do próprio ID, uma única vez**,
  nenhuma órfã, nenhuma duplicada. 97,4 KB realocados e conferidos.
  ⚠️ E a primeira versão desse verificador acusou **48/48 falhas** — bug meu: com a flag `m`, o `$`
  do lookahead casa fim de **linha**, cortando a seção na primeira quebra. *Verificador que reprova
  tudo é verificador quebrado, não código quebrado* — conferir um caso à mão antes de acreditar no
  próprio alarme.

**Aceitos como estão:** as decisões (a) 240 bytes, (b) `📏` separado do `⚠` e (c) dois passos awk
foram todas confirmadas pelo revisor, cada uma com o cenário que as justifica.

## Parecer íntegro (rodada 3)

[OK] (a) Manteria 240 bytes: sob UTF-8, um card com muitos caracteres multibyte consome o orçamento mais rapidamente, mas nunca ultrapassa o limite físico que motivou a redução do board.

[OK] (b) Manteria 📏 separado de ⚠: durante a migração, 18 cards acima do teto podem manter 📏18 aceso sem mascarar um novo card malformado que precisa produzir ⚠1.

[OK] (c) Manteria os dois passos: unificar sob `LC_ALL=C` faria `substr(..., 1, 34)` poder devolver os primeiros bytes de um emoji sem todos os bytes que o compõem, produzindo UTF-8 inválido na statusline.

[RISCO] A separação não garante por si só truncamento Unicode seguro: se o processo do plugin já herdar `LC_ALL=C`, o awk principal continuará contando e cortando bytes; um título com emoji atravessando a posição 34 poderá sair corrompido mesmo com os dois passos separados.

[RISCO] (d) O arquivo coletivo só é seguro se cada card tiver um endereço estável e explícito para sua seção; daqui a semanas, ao retomar `T-042`, procurar a thread convencional poderá não encontrar a nota histórica ou poderá recuperar por engano a seção vizinha após renomeação de títulos. Eu preferiria thread própria, salvo se o board mantiver ponteiro por ID e o coletivo usar seções exclusivas por ID.

[BLOQUEADOR] O primeiro awk falha aberto: se ele não conseguir ler o board e o segundo conseguir — por troca atômica, janela de permissão ou wrapper de teste que falhe apenas na primeira chamada — `gordos` fica vazio, o awk principal termina com sucesso e a statusline omite 📏 silenciosamente.

[RISCO] Se `awk` não existir, ambas as invocações falham e o script termina pelo segundo comando, normalmente com status 127 e sem statusline; se somente o primeiro passo falhar, o status final bem-sucedido do segundo apaga a evidência da falha.

[RISCO] A regra `/^##+ .*[Aa]rquiv/` aceita mais do que uma seção arquivada: um cabeçalho `## Cards não arquivados` ou `## Como arquivar cards` interrompe toda a contagem posterior, ocultando progresso, violações e cards acima do teto.

[RISCO] A mesma regra não aceita capitalização geral: `## ARQUIVADOS` não interrompe a leitura e cards históricos passam a inflar progresso e 📏.

[RISCO] A duplicação da regra de arquivamento cria divergência futura: se alguém corrigir somente um dos dois regexes para aceitar `ARQUIVADOS`, a statusline poderá mostrar progresso excluindo o arquivo, mas 📏 contando cards arquivados.

[OK] Ler 3,6k tokens duas vezes tem custo desprezível em comparação com inicializar o processo e renderizar a statusline; o cenário problemático dos dois passos é consistência e tratamento de falha, não desempenho.

[RISCO] Falta um teste de fronteira com CRLF: uma linha cujo conteúdo possui exatamente 240 bytes ganha o `\r` retido pelo awk e passa a medir 241, acendendo 📏 apenas porque o checkout usa CRLF.

[RISCO] Falta testar cabeçalhos adversariais antes de cards ativos: `## Como arquivar`, `## Não arquivados`, `## ARQUIVADOS` e um `## Arquivado` dentro de bloco Markdown cercado podem interromper ou deixar de interromper a contagem indevidamente.

[RISCO] Falta injetar falha apenas na primeira chamada de awk; sem esse teste, o contador pode desaparecer mantendo saída e exit 0, exatamente o tipo de falha silenciosa que uma statusline não denuncia.

[BLOQUEADOR] A migração de 48 notas precisa de reconciliação byte a byte por ID: um erro de copiar/colar pode duplicar `T-031`, omitir `T-032` ou anexar sua nota à thread de `T-033`, enquanto o board reduzido e os 13 testes continuam verdes.

[BLOQUEADOR] Mover Markdown pode quebrar referências relativas silenciosamente: uma nota com `[evidência](../artefatos/x.md)`, imagem relativa, footnote ou link por referência resolvia a partir de `memory/wiki/KANBAN.md`; dentro de uma thread ou arquivo coletivo, o mesmo texto íntegro aponta para outro caminho e só será descoberto quando alguém tentar abrir a evidência semanas depois.

corrigir antes.
