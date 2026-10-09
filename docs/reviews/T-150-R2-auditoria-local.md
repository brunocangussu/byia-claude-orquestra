# T-150 — auditoria local da R2

## Recibo e interpretação

R2 única consumida: pacote de 78.999 bytes, SHA-256
`ad766afa58baa44cc8ff15b3497e542bc0113a20527133a4199b4c0273f6d6e3`,
teto 98.304 bytes. Início `2026-10-08T01:35:34.702Z`, fim
`2026-10-08T01:41:31.772Z`, 357,07 s. Runner exit 0, identidade observada
`claude-opus-5-5`; effort `high` enviado, não observado no servidor.
Cwd vazio antes e depois. Nenhuma repetição, nova autenticação ou fallback.

Parecer original preservado em
`docs/reviews/T-150-review-r2-2026-10-07-saida.md`: 7.952 bytes, SHA-256
`92bacb5be7e609743cf41a9c9dbe803070d16a5e3f2db9847c8e4fc34be17643`.
As três seções canônicas estão presentes. O literal sob `## VEREDITO` é
**REPROVADO**. O harness marcou `format_valid=false` porque procurava
`VEREDITO:` com dois-pontos, não o cabeçalho Markdown contratado. É um falso
negativo do parser local, não falha de autenticação, transporte ou ausência
de parecer. O recibo original não foi reescrito. Esta auditoria separada não
transforma o parecer em aprovação.

## Auditoria dos achados

- **B1 — parcialmente confirmado, documental.** GREEN existia antes do envio:
  `docs/T-150-verificacoes-pos-R1.json`, verificado em `2026-10-07T20:21:20Z`,
  snapshot `bba7959ad9326ac9ca94ee2848679eeb8916ef8fad65d9cef54c2084d5b3f44e`.
  Python nativo 3.9.6: 34 testes focados exit 0; suíte descoberta 910 testes
  exit 0 (253,262 s); 22/22 mutações detectadas, zero erro de infraestrutura;
  manifesto/lint/Ruff/diff-check exit 0. O pacote R2 havia sido congelado
  antes do apêndice GREEN, mas enviado depois dos gates. Não procede dizer
  que o envio antecedeu os testes; procede que o pacote não trouxe a prova.
  O próximo pacote deve incluir o recibo vigente e seu snapshot, sem alterar
  retrospectivamente o R2 congelado.
- **R1 — confirmado.** Helper emite `mode`, consumidor exige
  `coordination_mode`. Corrigir chave e montagem do briefing; testar saída
  real da CLI, sem afirmar que a guarda estática prova comportamento da LLM.
- **R2 — confirmado.** `blocked`/`unavailable` atuais, com testes verdes,
  podem recomendar outra chamada no mesmo snapshot. Manter auditoria do
  parecer e gate de nova tentativa explícitos; saldo genérico não é retry.
- **R3 — confirmado, documental.** Há decisões antigas do dono na tabela
  substituída. Registrar a substituição candidata e sua autoridade, mantendo
  a integração na main pendente de validação/gate; não afirmar que não havia
  decisões humanas. Manager, Host Claude e presets não são substituídos.
- **R4 — não confirmado como capacidade ausente; lacuna de pacote confirmada.**
  O runner vigente já aceita ID completo Opus 5.5, effort e teto por bytes,
  e os recibos R1/R2 são invocações reais por ele. Incluir o código inalterado
  e o recibo sanitizado como contexto na próxima revisão, sem nova sonda.
- **R5 — confirmado.** Explicitar modo de entrada autocontido sem ferramentas
  nas instruções do Planner: memória/âncoras inline, lacunas declaradas;
  persistência do plano pelo Manager. A via nativa continua distinta.
- **R6 — lacuna de verificação remota no pacote.** Ponteiro público não prova
  compatibilidade do contrato JEV. Identificar essa condição no documento;
  nenhuma API, chave ou ativação JEV será usada nesta correção.
- **R7 — confirmado para os novos exemplos.** Caminho comprovado não garante
  variável exportada. Usar caminho absoluto resolvido explícito nos exemplos
  novos; não mudar silenciosamente toda a convenção legada.
- **R8 — confirmado, documental.** Remover estado datado de review da tabela
  operacional e apontar provas/rollback por caminhos duráveis do projeto.
- **R9 — confirmado em partes.** Nomear teto externo registrado; distinguir
  condições de término/estacionamento do noturno; definir fallback local de
  recibo ilegível e testar a rejeição real de coordenação technical/interface.

## Próxima ação autorizada

Aplicar correções locais confirmadas com RED/GREEN, mutações e os três gates
obrigatórios. Sem bump, stage, commit, push, integração, publicação, instalação,
restart ou inferência nova. R3, se preparada, exige gate humano próprio.
O snapshot e o pacote da R2 permanecem históricos e imutáveis.

## Correções e gates GREEN — 08/10, 02:15 UTC

R1: `coordination_mode` é o campo emitido e consumido; a CLI foi testada
em off/technical e recusou technical/interface com exit 2 sem contrato parcial.
R2: revisão bloqueada atual segue para auditoria local, nunca nova chamada
por saldo genérico. Zero bloqueador confirmado não é estado inválido por si
só: pode significar achados ainda não auditados ou recusados pelo Manager.
Por isso foi escolhida ação consultiva explícita em vez de rejeitar o schema.
Review indisponível atual propõe gate próprio de nova tentativa, sem retry.

R3/R8: decisões anteriores e substituição candidata explícitas; estado de R1
retirado da linha operacional, provas/rollback apontados por caminhos do projeto.
Host Claude, Manager, presets e main preservados. R4: runner vigente não foi
alterado; contexto inalterado + projeção sanitizada do recibo comporão o próximo
pacote. R5: `planner_input_mode` distingue pacote sem ferramentas de leitura
nativa delimitada; Manager persiste o plano quando packet-only. R6/R7: ponteiro
remoto não homologa contrato JEV; exemplos novos usam caminho absoluto resolvido.
R9: teto externo específico, noturno com condições rotuladas, baseline local
preservado em recibo ilegível e teste real da CLI de coordenação inválida.

RED: 46 testes nativos, 15 falhas esperadas incluindo subtests, zero erro de
infraestrutura. GREEN focado: 64/64 em Python 3.9.6 e 3.14.7. Primeira suíte
completa 916/916 executada, exit 1 por uma guarda textual antiga; corrigida,
nova suíte descoberta **916/916**, exit 0, 259,863 s, handle 98537 terminal.
Manifesto estrito, lint de coerência, Ruff e diff-check exit 0. **28/28 mutações**
detectadas, zero erro de infraestrutura; dez controles offline e seis casos
de parser local válidos. Dois ResourceWarnings já existiam no baseline.

Snapshot corrigido:
`721d4e833a9ab7b83513810c18f6c632587d594f8b3aa78029245b98768fa0e6`.
Recibo: `docs/T-150-verificacoes-pos-R2.json`. Produto e elenco são identificados
separadamente no recibo; wrappers/contadores privados não entram no produto.
Não foi feita revisão independente R3, sonda nova ou inferência JEV/Haiku.
Guardas textuais não provam conduta de LLM; testes locais não são aceite do dono.
