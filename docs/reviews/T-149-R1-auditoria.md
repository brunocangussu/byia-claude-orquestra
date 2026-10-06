# T-149 — auditoria da R1 e correções locais

Data: 2026-10-06. Parecer independente: `T-149-R1-opus55.md`.
R1 única consumida: CLI exit 0, formato válido, `REPROVADO`. Identidade em
`OPUS_MODEL_USAGE`: `claude-opus-5-5`; effort high enviado, observado no
servidor não disponível. Não foi falha de autenticação. Sem retry ou R2.

## Achados confirmados e corrigidos localmente

1. **Bloqueador — legado sem effort.** O snippet antigo mandava `--effort ""`:
   argparse exit 2, sem `OPUS_STARTED`. O teste executa o Bash documentado e o
   runner real contra CLI falsa sem rede. RED no legado; GREEN no legado,
   `opus@high` e recusa de `opus@` (sem contornar effort declarado inválido).
   Elenco, consumidores e agentes agora distinguem parâmetros declarados;
   a capacidade é conferida pelo Manager antes do despacho, não pelo worker.
2. **Risco confirmado — vias desligadas.** `runner-opus` off no Codex e `codex`
   off no Claude eram ignorados por diferença de vocabulário. RED mostrou
   `ready` indevido; GREEN bloqueia só os papéis/host pertinentes, preservando
   a lista original. Não reativa via nem desliga o vendor nativo do outro host.
3. **Risco confirmado — mecanismo candidato virava ativo.** Mesmo com
   `codex-native` desligado e só `codex-cli` comprovado, a proposta gravava
   ambos. RED mostrou a lista indevida; GREEN grava somente a via validada,
   inclusive na proveniência. Provas mínimas são conservadas e revalidadas
   por conta/cliente/sandbox/modelo/effort; alteração contextual invalida o
   reuso sem criar chamada automática. A lista de candidatos não dispensa prova.
4. **Lacuna documental do planner.** O runner não contém persona de reviewer;
   o papel/formato vem do briefing. `plan-next` agora delimita a investigação
   do Manager, pacote sanitizado, formato de plano, limites e quem grava o
   documento. A via read-only continua sem ferramentas/escrita no subprocesso.
5. **Bootstrap do scout.** `init` explica a investigação local pelo Manager
   sem elenco; spawn só com perfil/prova/autoridade prévios. Não se exige do
   agente que descubra/prove o próprio mecanismo depois de nascer.
6. **Raiz do template.** `init` usa `ORQ_PACKAGE_ROOT` também no template,
   impedindo misturar raiz de template com catálogo/manifesto de outra raiz.
7. **Prosa temporal.** Os rascunhos de arquitetura/distribuição ficaram
   atemporais; o estado de implementação/revisão está nesta thread/recibos,
   não na instrução viva. Não declara entrega ou ativação antecipada.

## Riscos delimitados, não convertidos em falso bloqueador

- Capacidade nativa Claude de ID+effort: não comprovada por catálogo, fixture
  ou esta R1. Adoção permanece condicionada a prova contextual; nenhum elenco
  ativo mudou. Não ampliar mecanismo/usar alias ou fallback sem gate.
- Posição real de `--effort high`: a própria R1 concluiu na CLI 2.1.290 com
  esse argumento e `--setting-sources ""`. Isso comprova aceitação dessa via
  nesta chamada, não effort observado no servidor nem outras contas/modelos.
- Desligar runner-opus afeta planner/reviewer no Codex: efeito intencional,
  anunciado na Matriz e no consumidor, sem seleção silenciosa de alternativa.
- Formatação compacta de recibo: consumo é por JSON. Nenhum consumidor por
  regex incompatível foi identificado no escopo; não alterar contrato legado.
- Digest com `--host`: é digest do catálogo completo; a seleção do host só
  recorta a apresentação, não cria uma segunda fonte/digest.
- Marcador de perfil no template e nomes históricos dos testes: demonstração
  proposta não é seção adotada. Fixtures preservam instruções históricas;
  não afirmam medir uso real do catálogo em todos os hosts/projetos.

## Provas locais

- RED/GREEN: adoção (5 falhas reais), invalidação contextual (3 subcasos) e
  snippet executável (legado e effort declarado vazio).
- Mutation checks: 6 mutações válidas, todas rejeitadas por falhas esperadas
  (sem erro de execução): aliases de via, mecanismo não selecionado, contexto
  ignorado, prova não persistida, effort vazio incondicional e omissão indevida
  de effort declarado vazio.
- Focados: 29 testes verdes. A suíte descoberta completa, manifesto e lint
  pós-correção serão registrados em `T-149-gates-pos-R1.json`.

As correções locais não equivalem a revisão independente aprovada. O novo
snapshot exige autorização própria para uma R2; a R1 permanece REPROVADA e
consumida. Sem bump, stage, commit, push, integração, instalação ou restart.
