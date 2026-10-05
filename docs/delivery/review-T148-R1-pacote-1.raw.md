## BLOQUEADORES

Nenhum. Comparei os trechos numerados com cada item do aceite e não encontrei um cenário concreto que viole um deles de forma inequívoca. Pontos que a ferramenta exibe sem prova direta estão nos riscos.

## RISCOS

1. **`orq/commands/implement-next.md:77` × `:115` e `:121`: a `session_key` pode chegar ao worker por outro caminho.**
   - O passo 3 manda gravar a `session_key` "na thread do card".
   - O briefing entrega `THREAD_ROOT` absoluto ao worker.
   - A linha 121 cumpre a letra do aceite: o briefing não traz a chave. Mas um worker que lê o handoff da thread, o que é comportamento normal, obtém a chave de dono do medidor.
   - Correção mínima: guardar a `session_key` fora de `THREAD_ROOT`, em local só do Manager. Ou acrescentar em `:121`: "nem a lê ou usa se a encontrar na thread".

2. **`orq/commands/implement-next.md:165-166`: "entrega e validação correspondentes estiverem autorizadas" tem duas leituras.**
   - Uma leitura hostil permite mover o card a `[x]` quando a validação foi apenas *autorizada*, sem ter sido *aprovada* pelo dono.
   - A linha 167 resolve isso para `[?]`, mas não para DONE.
   - Correção mínima: "move a `[?]` só com entrega e passagem autorizadas; a `[x]` só após aprovação do dono".

3. **`orq/commands/implement-next.md:157-170`: falta o estado do medidor para "entrega pendente de autorização Git".**
   - Sem autorização, o trabalho local termina com 100% dos passos.
   - O texto proíbe `phase validate` e `pause`, mas não define o que a vista mostra nesse caso.
   - Há risco de 100% ser lido como pronto.
   - Correção mínima: registrar a pendência de entrega no medidor (marco ou nota) e não fazer `pause`.

4. **`orq/commands/plan-next.md:124-125` × `orq/commands/implement-next.md:112`, `:118` e `:162`: criar o worktree é uma operação Git.**
   - `git worktree add`, ainda mais com `-b`, cria refs.
   - A linha 125 chama isso de "etapa local", e a lista da linha 162 não o inclui. Mas a linha 118 diz genericamente "Git não está autorizado neste gate".
   - Não está dito quem cria o worktree nem se essa criação dispensa autorização. Duas saídas possíveis:
     - impasse: a linha 112 exige worktree e o Manager se recusa a criá-lo;
     - ou criação de branch sem autorização humana.
   - Correção mínima: declarar que só o Manager cria e remove o worktree declarado no plano aprovado, e que essa é a única operação Git local permitida sem autorização de entrega.

5. **`orq/commands/implement-next.md:74-76` × `orq/commands/plan-next.md:147-148`: plano sem tabela.**
   - O `plan-next` devolve ao Planner.
   - O `implement-next` permite que o Manager atribua IDs a um "plano antigo".
   - "Antigo" não está definido. Um plano novo sem tabela, aprovado pelo dono, pode ser numerado pelo Manager em vez de voltar ao Planner.
   - Correção mínima: definir "antigo" como aprovado antes da 0.30.0.

6. **`orq/commands/plan-next.md:131`: "no Loop B" aponta para um nome que não aparece nos trechos.**
   - O destino visível é `implement-next` §0b.
   - Correção mínima: trocar por "`/orq:implement-next` §0b", ou confirmar que "Loop B" está definido em outra parte.

7. **`orq/skills/orq/SKILL.md:267` × `:277`: `status` é usado com dois sentidos.**
   - A linha 267 trata `status` como estado ("não terminal").
   - A linha 277 trata como código (`status: 0`).
   - A linha 277 vale só para continuação. Para a chamada `--fresh`, sobra só o critério da 267. Um `status` terminal de falha com IDs presentes poderia criar um vínculo a partir de um job que falhou.
   - Correção mínima: aplicar à primeira chamada o mesmo recibo da 277: `status: 0`, JSON válido, `jobId` e `threadId` não vazios.

8. **Campos do handoff divergem entre `orq/skills/orq/SKILL.md:266` e `orq/commands/elenco.md:450`.**
   - A skill persiste `card`, `papel`, `jobId`, `threadId` e `status`.
   - O elenco persiste `rawOutput`, `jobId`, `threadId` e `status`, sem `card` e `papel`, que são justamente a chave do vínculo.
   - A degradação em `SKILL.md:280-281` exige ainda IDs solicitado e devolvido e o caminho/versão do runtime.
   - A linha 456 do elenco remete à skill, então a união dos dois cobre o caso. Mas quem ler só a matriz perde a chave.
   - Correção mínima: listar no elenco o mesmo conjunto de campos da skill.

9. **Itens do aceite que não aparecem nos trechos.**
   - `--wait` só como envelope: o título do recorte `SKILL.md:255` cita `--wait`, mas as linhas 255-284 e o elenco não o mencionam.
   - Autorização dos novos digests ao dividir o briefing: o elenco (`:423` e `:449`) fixa 16 KiB por lote sem citar essa exigência.
   - Não os declaro ausentes, porque podem estar no código omitido já revisado. Também não os declaro revisados aqui.
   - Correção mínima: o Manager confirma onde esses dois contratos estão, ou acrescenta uma remissão em `SKILL.md` e em `elenco.md:449`.

10. **`orq/skills/orq/SKILL.md:265`: a nota ⚠️ está no meio da lista.**
    - Ela divide a lista de bullets em duas e solta o primeiro item visualmente das regras de vínculo.
    - É cosmético. Correção: mover a nota para antes ou depois da lista.

## VEREDITO

**APROVADO_COM_RESSALVAS**

---
*Nota: não usei ferramentas, conforme a instrução, e não gravei nenhum arquivo de plano. À parte da revisão: os conectores claude.ai Era Context, Gmail, Google Calendar e Zapier precisam de autorização nas configurações de conectores do claude.ai para funcionar.*
