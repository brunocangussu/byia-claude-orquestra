## BLOQUEADORES

**1. `orq/commands/revisar.md:187` contradiz `:195-196` e `:202`, e a leitura por prefixo aceita o modelo errado.**
- **O conflito:** a linha 187 diz que o runner aceita "o prefixo do alias legado pedido". As linhas 195-196 dizem outra coisa: só valem a identidade base ou um "sufixo numérico permitido". Pela linha 187, `claude-opus-5-5` e `claude-opus-5-50` começam com `claude-opus-5` e passam. Pela linha 202, o `-5` final também conta como "sufixo numérico de release".
- **Cenário concreto:** o host Codex tem `reviewer = opus` no elenco, ou omite `--model` e cai no default `opus` (linha 197). O `modelUsage` volta com `claude-opus-5-5`. Um host que confere pela linha 194 e pela linha 187 aceita o parecer como sendo do Opus 5. O mesmo acontece com `sonnet`, que aceitaria `claude-sonnet-5-5`. Isso amplia a identidade aceita, o que a linha 199 proíbe. A linha 203 só cobre o ID explícito e o caso Fable → Opus 5.5. O par alias legado → modelo 5.5 fica sem regra.
- **Correção mínima (texto):**
  - Na linha 187, trocar "o prefixo do alias legado pedido" por "a identidade base do alias legado pedido ou um sufixo de release permitido".
  - Na linha 195 ou 202, definir "sufixo de release" com formato fechado, por exemplo `-AAAAMMDD` com 8 dígitos. Esse formato não colide com `-5` nem com `-50`.
  - Na linha 203, acrescentar: "pedir `opus`/`sonnet` e receber `claude-opus-5-5`/`claude-sonnet-5-5` reprova".

## RISCOS

1. **`revisar.md:181` vs `:183-184`:** a linha 181 diz que `OPUS_STARTED` é anunciado "imediatamente", mas a validação de tamanho vem antes do anúncio. Um leitor hostil pode emitir o anúncio antes de validar e então tratar `BRIEFING_TOO_LARGE` como chamada iniciada. Correção: trocar "imediatamente" por "logo após a validação de tamanho".
2. **`revisar.md:184-186` vs `:190-191`:** é provável que `BRIEFING_TOO_LARGE` saia com código diferente de 0. A regra das linhas 190-191 ("`OPUS_EXIT != 0` → REVISÃO DEGRADADA") então colide com "redivida". Falta dizer qual regra vence. Correção: "`BRIEFING_TOO_LARGE` sem `OPUS_STARTED` não é degradação. Só degrada se não houver autorização para os novos digests."
3. **`revisar.md:193`:** "o runner não lê esse arquivo" aponta para um arquivo (o elenco) que não é nomeado nos trechos recebidos. Se a linha anterior, fora do escopo, não o nomear, a referência fica sem dono. Correção: nomear o arquivo explicitamente.
4. **`arquitetura.md:141-142` vs `revisar.md:197`:** o texto diz "sem hardcode de modelo", mas o default sem argumento é `opus`. Hoje a contradição é só redacional, porque a linha 198 manda sempre passar a flag. Correção: acrescentar ", salvo o default legado `opus`".
5. **`arquitetura.md:125-134`:** o trecho diz que a ausência de `--write` não prova nada, mas não diz que `--write` continua proibido. O aceite exige essa proibição. Se ela não estiver em outro ponto do arquivo, uma leitura hostil pode concluir que `--write` é opcional. Correção: uma frase "`--write` permanece proibido para papéis read-only".
6. **`arquitetura.md:130-134` está coerente com o aceite.** Exige threadId igual ao solicitado, status 0, jobId e threadId completos. Divergência preserva o vínculo anterior, sem retry, sem fallback, sem task nova e sem pegar a "última" task. O `--wait` fica só no envelope. Não há ressalva aqui.

Fora de escopo e não revisados: o medidor sem Git e sem passar card a VALIDATE, o worker sem `session_key`, a pausa para validar e o código do runner. Esses itens não aparecem nos trechos e não declaro que foram revisados.

## VEREDITO

**REPROVADO.** Só o bloqueador 1 impede a aprovação, e a correção é apenas de texto, em três linhas. Com essa correção e sem outras mudanças, o parecer passa a **APROVADO_COM_RESSALVAS**, com os riscos 1 a 5 como ressalvas.

*Nota operacional:* respeitei a proibição de usar ferramentas, então não gravei arquivo de plano nem chamei ExitPlanMode, embora o modo de planejamento estivesse ativo. Os conectores Era Context, Gmail, Google Calendar e Zapier pedem autorização nas configurações de conectores do claude.ai, mas não eram necessários aqui.
