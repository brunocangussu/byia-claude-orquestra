Revisei apenas o texto do pacote: não usei ferramentas, não abri arquivos e não executei nada. Os números de linha são aproximados (`~`) ou repetem os números declarados no handoff. O modo de planejamento estava ativo, mas a regra do briefing proíbe ferramentas, então não criei arquivo de plano.

## RECHECAGEM

**B1 — inspeção do briefing completo do Planner antes do envio para o outro vendor: CORRIGIDO**
- **Onde:** `orq/commands/plan-next.md:~41-47`, dentro do §3. O handoff declara a linha 43.
- **Por quê:**
  - O parágrafo manda inspecionar "o briefing completo do Planner conforme o §1b de `/orq:revisar`". A lista cobre card, título, notas, plano, páginas de wiki e leituras que entrarão no envio.
  - Proíbe PII, prontuário, credencial, token, chave, `.env` e dump real.
  - Com achado sensível, manda parar e avisar o dono, sem higienizar por conta própria.
  - Diz que a inspeção "antecede o gate de saldo e envelope e não autoriza transferência alguma". Não há autorização implícita de egress.
  - A ordem no texto é: inspeção, depois o gate externo, depois o Companion e a célula da Matriz.
- **Cenário da R6 (prontuário na nota ou na wiki):** agora é barrado antes do gate, igual ao que o §1b faz na revisão. O texto antigo só falava de leitura adicional; essa frase continua no bullet seguinte e agora é redundante, não contraditória.
- **Teste:** a asserção de ordem (inspeção antes do despacho) e as duas mutações discriminam o defeito original:
  - remover a inspeção;
  - reduzi-la a "leituras adicionais".
- **Qualificação do Manager:** procede. A correção aplica a política do §1b, não afrouxa o gate de saldo e não cria capacidade nova.

**B3 anterior — schema e recuperação: CORRIGIDO**
- **Onde:** `memory/wiki/_schema.md` em três pontos. O handoff declara as linhas 208 e 245.
  - Regra 3: os exemplos agora usam `@frente-auth`/`@frente-billing`.
  - Regra 4 (~208): quem retoma "durante a recuperação reafirma somente a marca de host". A marca de host "não transfere a propriedade da frente". A transferência "exige instrução humana específica e é ação separada da recuperação". E a regra fecha com "Durante a recuperação, não crie, duplique, troque de frente nem use fallback".
  - Pendência (~245): o "Qualquer janela" virou "Qualquer janela da frente dona… somente com a raiz e a thread existentes em seu `THREAD_ROOT`". Outra frente, ou raiz/thread ausente, faz parar e registrar, sem copiar nem fabricar.
- **Coerência:** o texto agora bate com `SKILL.md:~395-399`. O "reafirmar ou transferir" e a retomada universal sumiram.
- **Qualificação do Manager:** procede, e a aceito. O bloco do resolver no topo do `_schema.md` e na `SKILL.md` ficou intacto: "não crie, duplique, troque de frente nem use fallback". O ramo de falha continua fechado (fail-closed), sem a exceção "salvo transferência" que eu tinha sugerido na R6. Retirar essa sugestão é o certo, porque a transferência humana não deve virar exceção dentro da recuperação.
- **Teste:** as duas mutações (transferência durante a recuperação e retomada universal) discriminam o defeito.

## BLOQUEADORES

Nenhum.

## RISCOS

- **Frase ambígua em `plan-next.md:~46`:** "não higienize por conta própria e envie" pode ser lida, por um modelo hostil, como "não higienize; e envie". O "pare e avise o dono" logo antes desfaz a leitura, e o §1b tem a mesma construção, já aceita. Uma redação sem ambiguidade seria "não higienize nem envie por conta própria".
- **Guardas R6 só verificam presença de frases, nunca ausência.** Se alguém reintroduzir "reafirmar ou transferir a posse" ou um "Qualquer janela" universal ao lado do texto novo, os testes não pegam. Nenhuma asserção protege o ramo de erro do resolver contra a reentrada de "salvo transferência".
- **A ordem verificada é inspeção antes do despacho, não antes do gate.** A precedência sobre o gate está garantida pela prosa, não pelo teste.
- **Reenvio ao Planner no §4 ("devolva ao Planner com o apontamento").** O "qualquer briefing" do §3 cobre esse reenvio, mas o §4 não remete de volta à inspeção nem ao gate. Um modelo pode pular os dois na rodada seguinte. É um ponto anterior à R7, não regressão.
- **A transferência de frente é, na prática, inoperável.** Isso vale especialmente entre worktrees, porque a thread fica no `THREAD_ROOT` do dono original e o resolver para. É fechado e coerente com a decisão de não criar protocolo de transferência; só deve ser comunicado ao dono.
- **A frente continua sendo autodeclarada dentro do mesmo checkout.** Duas janelas com o mesmo `THREAD_ROOT` ainda podem colidir. Fica com o T-092, fora do escopo.
- **Ressalvas da R6 que seguem abertas e não são bloqueadores:**
  - `dormir.md` sem as marcas de frente e host ao entrar em `[>]`;
  - timeout de shell abaixo dos 600 s do runner;
  - "limiar do controlador de metas" sem definição;
  - prova da raiz do pacote duplicada;
  - guarda autorreferente do `test_r4`;
  - nenhuma prova comportamental de LLM, zero-tools ou host.

## COBERTURA

- **Examinado:**
  - o parecer R6 e as duas auditorias do Manager;
  - o handoff em MD e JSON e o recibo de gates;
  - `SKILL.md`, `implement-next.md`, `revisar.md`, `plan-next.md`, `checkpoint.md`, `_schema.md` e `test_continuidade_aprovada.py`, todos completos.
- **Não reexaminado:** `dormir.md` e `arquitetura.md`. Pela declaração do pacote, os hashes são os mesmos da R6; não conferi os hashes e não alego nova revisão integral desses dois.
- **Não disponível:** `elenco.md`, `_elenco.md`, `orq-reviewer.md`, o runner e o código do resolver.
- **Não executado nem verificado por mim:**
  - o RED;
  - o GREEN focado (18 testes, quatro mutações);
  - a suíte de 465 testes;
  - manifesto, lint, diff-check e hashes.

  Tudo isso é evidência declarada. As mutações são estruturais e não provam conduta de LLM nem capacidade runtime.
- **Conectores:** Era Context, Gmail, Google Calendar e Zapier precisam ser autorizados nas configurações de conectores do claude.ai e ficam indisponíveis até isso ser feito. Nenhum era necessário para esta revisão.
- **Limite do GO:** ele fecha apenas esta rechecagem. Não autoriza entrega, Git, release nem instalação.

## VEREDITO

GO
