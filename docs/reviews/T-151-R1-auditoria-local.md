# T-151 — auditoria local da R1

**Parecer original:** GO, sem bloqueadores demonstrados, dez ressalvas.
Opus 5.5/high via Claude CLI 2.1.290, uma chamada sem retry; exit 0 em
332,369 s. Identidade exata `claude-opus-5-5` validada pelo runner;
effort enviado high, não observado no servidor. Original preservado em
`T-151-R1-opus-verbatim.md`, SHA-256
`af4dea374a1d7e1d3cfb21100101dbd45a4f6efd9a00953c44d66ffc73b343ab`.

Pacote autorizado: 187.361 bytes, SHA-256
`5d8d15f974f53826966f01db1c7aef65ea19183c929f62cdf3678eed42a0c70a`.
Os dez arquivos funcionais continuaram com os digests revisados após a
resposta. Nenhuma ressalva foi transformada em correção não revisada.

## Achados auditados pelo Manager

| Item do parecer | Conferência local | Destino |
|---|---|---|
| R1 — transporte entre checkouts sem Git de entrega | `SKILL.md:579-587` e `implement-next.md:159-170` autorizam integração de artefatos localmente, não stage/commit. O Manager pode conferir o diff read-only e aplicar patch pelo editor, preservando ownership; nenhuma operação Git de entrega é necessária. A falta de uma receita explícita continua ressalva de portabilidade | Não bloqueia; o piloto precisa registrar como os handoffs entram na árvore integrada. Não prometer capacidade não comprovada do host |
| R2 — lista abreviada no registro READY | `plan-next.md:41-50` exige os campos centrais no plano; `:250-263` grava o caminho desse plano e a fonte verificável. `SKILL.md:518-543` exige também a consolidação e a delegação. A lista do command não dispensa os campos centrais; a leitura abreviada pode gerar pergunta conservadora repetida | Ressalva real de atrito, sem ampliação de autoridade. Medir no piloto a referência efetiva ao acordo, não só uma palavra de aprovação |
| R3 — teto dos agentes locais | `SKILL.md:525-527`, `:600-601` e `:637-652` mantêm operações, proibições, limites e consumo por gate. A condição de orçamento local não imposto é explícita e não cria autorização externa. Nenhuma expansão ganha saldo por aceite técnico | Não instalar teto global rígido nem autoridade implícita. O piloto propõe orçamento específico; consumo da implementação permanece registrado, inclusive cached |
| R4 — duas análises versus um reviewer | `SKILL.md:182`, `:563-564` e `implement-next.md:180` determinam um único reviewer de vendor oposto. A tabela de leituras não derroga essa regra específica. Planner workspace-read só escreve artefato autorizado (`orq-planner.md:42-44`) e o briefing discrimina arquivos exclusivos (`SKILL.md:573-575`) | Não autoriza dois revisores simultâneos nem plano compartilhado por dois writers. Sem bloqueador demonstrado |
| R5 — Companion serializado e Scout | O vínculo card+papel é preservado em `SKILL.md:294-307` e `:576-578`; serialização não comprova independência. A alegação de Scout ausente é incorreta: `_elenco.md:45-47`, `:165` e `:210` contêm o papel `scout` nos dois hosts | Preservar o contrato, não criar outro vínculo. Não contabilizar continuação no mesmo contexto como análise independente; portabilidade futura precisa declarar isso |
| R6 — continuação do worker no Claude | `implement-next.md:161-163` condiciona a continuação à cobertura; `SKILL.md:126-131` manda degradar quando a primitiva falta, sem fingir capacidade | Limitação de harness, não permissão para spawn com name/idle. Não comprovada pelo piloto Codex |
| R7 — writer versus Manager/Docs | A regra de ownership em `SKILL.md:386-387` convive com o caminho trivial e com o integrador único em `:585-587`. `orq-docs.md` documenta somente o produto final, não muda código e não commita; `implement-next.md:198` exige contexto/autoridade próprios | Ressalva de aplicação no harness. Nenhum worker deve escrever no checkout do Manager; Docs recebe o artefato final, sem presumir commit-base de isolamento |
| R8 — terminal/timeout versus correção | `SKILL.md:588-592` nega autoridade derivada do resultado; `implement-next.md:162-163` aceita continuação já coberta e `:191-192` preserva revisão dentro da autoridade | Não bloqueia correção coberta nem renova chamada externa. R1 consumida 1/1, sem repetição |
| R9 — enumeração curta do implementer | `orq-implementer.md:43-48` reserva entrega Git ao Manager e proíbe refs/worktrees/delegação; contrato central mantém os gates completos, incluindo publicação/produção | Enumeração não cria autorização de tag/merge/publicação; sem bloqueador concreto |
| R10 — caminhos e substring nos testes | Os testes usam a árvore fonte deste repositório; o procedimento obrigatório roda discover em fonte, não no cache instalado. Guardas textuais/mutações não são prova comportamental e essa limitação está registrada | Não fazer suite no cache nem declarar comportamento real pelas substrings; piloto cobre a lacuna de coordenação |

As linhas acima referem-se aos arquivos da candidata congelada. A avaliação
não é uma segunda revisão independente e não altera o GO recebido.

## Lacunas de evidência do parecer

- **Medidor:** `progress.py:762-772` muda somente a tarefa indicada, não impõe
  executor ativo único. Diagnóstico novo em memória iniciou P01/P02 com
  executores distintos e confirmou ambas active, sem escrever no ledger
  canônico. Isso cobre a dúvida contratual, não corrida de processos vivos.
- **Consumidores fora do pacote:** `revisar.md` já lido, reviewer read-only
  conferido, Docs e elenco conferidos localmente. Reviewer é único/oposto;
  Scout consta do elenco. Manifesto/lint da implementação tiveram exit 0.
- **936 testes / mutações:** log original de discover termina em 936/OK,
  272,039 s; log do worker confirma 31 mutações. Recibo separado do Manager
  conserva dez mutações adicionais, total 41. O reviewer não tinha esses
  originais privados; não tratá-los como certificados por ele.
- **Bases criadas pelo host:** não verificadas em Claude/Orca. Não inferir
  commit-base, escrita, egress ou isolamento pelo nome de uma flag.

## Decisão local e entrega

**GO preservado, zero bloqueadores confirmados.** As ressalvas permanecem
visíveis; transportar resultados, orçamento, perguntas repetidas e limites
de harness serão observados na avaliação proposta, não declarados resolvidos.

O gate humano permite bump/commit/push e integração allowlistados após essa
aprovação. Bump afeta somente as quatro âncoras; conteúdo funcional revisado
permanece congelado. Antes de commitar: descoberta completa fresca na árvore
de entrega, manifesto estrito, coerência, Ruff e diff-check. Não enviar nova
revisão, não publicar, instalar ou reiniciar. Não mover o card para DONE:
validação prática e piloto proposto continuam pendentes.
