---
description: Mostra e ajusta o elenco — qual LLM toca cada papel (planner por trilha, implementer por faixa, reviewer, docs, scout) no host em que você está, quais vias cross-vendor estão habilitadas, e perfis nomeados para trocar o time inteiro
argument-hint: "[papel modelo | perfil nome — ex: 'planner interface <modelo>' | 'implementer leve <modelo>' | 'codex off' | 'perfil economia']"
---

O **elenco** define qual modelo interpreta cada papel **neste projeto**. Fica em
`memory/wiki/_elenco.md` e vale como override no momento do spawn. O `model: inherit` dos agentes
é neutro: nunca autoriza executar no modelo ou effort do Manager por ausência de override.

**A regra que organiza tudo:** *domínio decide quem pensa; host decide quem escreve.* Dois eixos
independentes, definidos canonicamente aqui e apenas referenciados nos outros comandos.

## ⚠️ Onde o modelo é resolvido — a única frase normativa

**Identifique o host, leia a tabela DELE em `## Times por host`, e aplique a célula da
`## Matriz de invocação`. Não existe outra tabela ativa.**

Tabela marcada como **proposta, não adotada** não é ativa. Arquivo sem marca de origem é legado:
verifique a escolha e os recibos existentes, sem inventar adoção da fábrica ou bloquear capacidade
legada já comprovada. O gate confere os parâmetros efetivamente declarados na linha, não os
parâmetros sugeridos pela fábrica: **legado sem effort** mantém override só do modelo e registra
effort **não solicitado** (observado: não verificado). Não invente `@effort` nem exija nova sonda
quando a prova existente da combinação legada continua válida no contexto real.

Isto vale para ler e para escrever: `/orq:elenco` (ajuste papel a papel e `perfil <nome>`) grava na
tabela do **host resolvido**, nunca numa tabela compartilhada. É o que impede uma janela Codex de
trocar, em silêncio, o time de uma janela Claude aberta no mesmo repositório — cada host mexe só na
sua seção.

> **Arquivo com um heading `## Papéis`** (formato anterior à 0.24.0) — aquela tabela era, na
> prática, o time do host Claude, mas nada dizia isso, e consumidor nenhum a lê mais. Trate-a como
> **legada: não leia, não grave**. Proponha a migração (regra em "Migração de arquivo legado"), com
> gate. Enquanto a migração não acontecer, o time vem de `## Times por host`.

## Padrão da versão — proposta e adoção explícita

“Siga o elenco padrão desta versão”, “padrão da versão” e “padrão Orquestra” consultam a fábrica
do **pacote carregado**, não um preset local. Depois de comprovar `ORQ_PACKAGE_ROOT` absoluto,
existente e com `scripts/kanban-status.sh`, consulte:

```bash
python3 "${ORQ_PACKAGE_ROOT}/scripts/elenco_padrao.py" --package-root "${ORQ_PACKAGE_ROOT}" --host <host-resolvido>
```

O único dado de fábrica é `references/elenco-padrao.json`. O resolvedor retorna **modelo e effort**
juntos, as vias candidatas, a versão derivada do manifesto e o digest do catálogo. Não há quinta
âncora de versão. Tabelas deste comando são demonstrações derivadas e conferidas pelo lint, nunca
outra fonte. **Consulta é pura:** não escreve elenco, autentica, faz probe, chama modelo ou adota.
Se instalada e carregada diferirem, diga as duas; não procure `latest`, não troque a raiz em silêncio.

Para adotar em projeto existente:

1. Identifique o host e mostre a proposta/diff só da seção dele. Preserve o outro host, o Manager,
   os presets locais, overrides explícitos e todas as vias desligadas. Escolha sem origem registrada
   é **legada**, não prova nem override inventado: mostre a diferença antes de migrar.
   A proposta pura cobre somente os oito papéis de fábrica: normalize essa projeção antes de
   chamar o helper, mantenha Manager/papéis adicionais e seus overrides fora dela e aplique
   só as linhas dos oito papéis. Nunca substitua a seção inteira pela proposta JSON; papéis
   locais, presets e dados fora da projeção ficam byte a byte preservados no diff auditado.
2. Para cada par/via/sandbox/contexto **novo ou alterado**, aplique o gate de capacidade abaixo.
   Reuse recibo real ainda compatível (conta, versão do cliente, mecanismo e sandbox); não repita
   prova válida. Catalogado não é disponível, e texto autodeclarado não é recibo auditado.
3. Faltou comprovação? Liste só os papéis pendentes e **não grave nenhuma parte** da adoção.
   Não faça probe, retry, fallback, reativação de via nem rebaixamento de effort automaticamente.
   O restante do desenvolvimento local já aprovado segue seu contrato de continuidade.
4. A intenção explícita de adotar autoriza o ajuste local delimitado; chamadas externas e provas
   não são implícitas. Depois dos gates, grave todas as mudanças do host juntas, preservando um
   snapshot anterior para rollback. Registre origem `orquestra-version`, versão, `catalog_sha256`,
   data e overrides preservados. `preview_adoption()` apenas monta essa proposta em memória: não
   certifica recibos, concede autoridade ou escreve Markdown. O Manager audita e aplica o diff.
5. Não reescreva presets para fazê-los coincidir. Se o preset ativo divergir, registre os desvios
   dos papéis alterados no formato de `Perfil ativo`; mantenha também a proveniência da adoção.
   Atualizar/instalar N+1 **não migra** a adoção de N. Workers vivos terminam no perfil original;
   a adoção vale para os próximos despachos. Rollback também exige intenção e prova compatível.

`perfil padrao` e `perfil economia` continuam **snapshots locais congelados**, não aliases da fábrica
mais recente. Ao recomendar um deles, mostre origem e diferenças; economia é opcional, não outro
elenco de fábrica mantido à mão. Não crie esse preset nem descarte desvios sem pedido correspondente.

### Modelo, effort e via no despacho

Resolva host → papel/faixa → **perfil ativo** → via habilitada/comprovada. Numa linha `modelo@effort`,
passe modelo e effort explicitamente juntos; registre solicitado, enviado e observado como
campos distintos. Effort ausente na resposta não comprova o effort efetivo no servidor.
Recusa de effort declarado é recusa, sem downgrade nem omissão da flag.

**Legado sem effort:** linha ativa só com modelo, autorizada e já comprovada no contexto real,
continua com override só do modelo. Não envie `--effort ""` nem acrescente um effort de fábrica:
omita a flag e registre **não solicitado** / observado **não verificado**. Isso não transforma
o default do cliente em effort adotado. O critério de legado é a **combinação autorizada e
comprovada do papel/contexto**, não a data de escrita da linha. Voltar a um preset local já
autorizado pode reutilizar seu recibo compatível sem nova chamada; existir no preset, sozinho,
não comprova uso. Combinação nova/candidata só com modelo não ganha essa exceção: **não grave
nem despache**, apresente um `@effort` explícito pela via candidata e peça a decisão/gate do
dono antes de qualquer prova nova. Não invente effort de fábrica nem transfira prova de
outro papel/conta/cliente/sandbox; as demais ações locais autorizadas continuam elegíveis.

O **Manager** confere capacidade antes do despacho. Native spawn exige override efetivo dos
parâmetros declarados: ambos numa linha `@effort`, só modelo no legado sem effort comprovado.
Frontmatter neutro e catálogo não comprovam capacidade. Sem esse override, não herde o modelo
da sessão: use apenas via alternativa já autorizada/comprovada, ou preserve o perfil anterior
e estacione a dependência. O subagente recebe o perfil/recibo já conferidos; não precisa provar
o próprio spawn nem criar um gate de capacidade com base em parâmetros que não foram pedidos.

Na proposta pura, `runner-opus` desligado no host Codex significa `claude-cli` desligado;
`codex` desligado no host Claude significa `codex-companion` desligado. Esses nomes não
desligam o vendor nativo do outro host. O snapshot preserva a lista original de vias; a
normalização é host-aware. Adote somente o mecanismo do recibo validado, nunca a lista
de candidatos do catálogo. Proveniência registra essa via e os campos mínimos da prova,
que são revalidados no contexto exato antes de reutilização, sem nova chamada automática.
Essa conferência vale ao adotar/reusar o recibo para um despacho, não para cada ação local.
Auto-update que altera a versão do cliente invalida o recibo daquela via: preserve a
combinação registrada e estacione só os despachos dependentes, sem interromper workers
já vivos ou tarefas locais elegíveis. Não presuma compatibilidade entre versões.

Instrução global antiga não redefine a fábrica deste pacote. Havendo skills `orq` concorrentes,
registre caminhos/versões e use este contrato versionado para o Orquestra, respeitando as regras
do dono/projeto. Não edite ou apague skills/configs globais por conta própria, nem afirme que todos
os chats carregaram o pacote. Configuração de fábrica não é prova de ativação em outro harness.

## As duas réguas (definição canônica — os outros comandos apontam para cá)

### Trilha (`interface` | `sistema`) — escolhe o **vendor de quem pensa**

Aplicável por um modelo lendo o card, sem o dono no meio:

| Trilha | Critério | Vendor do `planner` |
|---|---|---|
| `interface` | o critério de aceite é **perceptual**: o dono valida olhando/usando — aparência, texto voltado a humano, fluxo de interação, experiência, marca | **Anthropic** |
| `sistema` | o critério de aceite é **comportamental**: valida-se verificando — lógica, dados, contrato, infra, CLI, build, desempenho | **OpenAI** |

**Desempate:** card misto ou ambíguo → `sistema`. `interface` exige critério de aceite perceptual
explícito. Não é frontend/backend: um CLI é `sistema`, um brand book é `interface`, uma migração de
banco é `sistema`. Projeto sem UI simplesmente não usa a linha de interface.

### Faixa (`pesada` | `normal` | `leve`) — escolhe o **degrau de quem escreve**

**Pré-condição, antes da pergunta 1:** o card é **Trivial** na escala de roteamento da skill `orq`
(typo, renomear variável local, ajuste de texto sem efeito)? → **não há faixa.** Em Trivial não há
implementer spawnado — o Manager escreve na sessão —, e faixa é o degrau de **quem foi spawnado**.
Encerre a classificação aqui e não anuncie faixa nenhuma. A faixa só existe de **Pequeno** para
cima.

Havendo implementer, três perguntas, nesta ordem:

1. O card é **Alto risco** na escala de roteamento, **ou** resta decisão de desenho por tomar (mais
   de uma solução defensável)? → `pesada`
2. Senão: o resultado está **completamente determinado** e a verificação é mecânica (rename
   mecânico, aplicar diff já aprovado, doc sobre código pronto, ajuste de texto **já classificado
   Pequeno** — 1 arquivo, sem decisão de desenho)? → `leve`
3. Senão → `normal`

Na dúvida, sobe uma faixa (mesma regra da escala).

**Reavaliação no gate do Loop A — com piso.** A faixa é default inicial, não veredito, e muda nos
dois sentidos quando o plano é aprovado:

- ⛔ **Piso: card Alto risco continua `pesada`, sempre.** Schema, segurança, dependência nova,
  dado de terceiro, irreversível: **plano fechado não rebaixa.** O que torna esse card caro é a
  **consequência do erro**, e o plano muda a incerteza, não a consequência. Rebaixar aqui mandaria
  a mudança mais perigosa do board para o modelo mais fraco.
- **Rebaixa** só quando a `pesada` veio **exclusivamente** da segunda metade da pergunta 1
  (desenho aberto) e o plano aprovado fechou esse desenho.
- **Sobe** quando o desenho continua aberto depois do plano.

### Registro no card

O Manager grava `trilha: … · faixa: …` na nota do card, na criação e revalidado no gate. **Card sem
registro → `sistema · normal`** — o default seguro. Card Trivial: `trilha: … · faixa: —`.

## Quem pode vir de outro vendor

**Só dois papéis cruzam vendor, e cada um por uma razão própria** — não é "read-only pode":

- **`planner`** cruza pelo **domínio**: a trilha do card escolhe quem pensa melhor naquele tipo de
  problema. Aceita modelo de qualquer vendor com célula na `## Matriz de invocação`, **desde que o
  mecanismo daquela célula execute aquele modelo** (a célula Anthropic×Codex é o runner Anthropic
  parametrizado por `--model <alias-ou-id>`: só entra valor presente no mapa de prova do runner, e a
  saída só vale com identidade exata para `claude-opus-5-5` ou prefixo legado no `modelUsage`).
- **`reviewer`** cruza pela **independência**, e é obrigado a cruzar: sempre o vendor **oposto** ao
  do host, com a mesma checagem de mecanismo.
- **`implementer`, `docs` e `scout` ficam no vendor do host.** Nos dois primeiros porque **escrevem**
  — escrita cross-vendor está fora do desenho. No `scout` porque **domínio não se paga em leitura
  ampla e barata**: ele varre território e relata, não decide nem julga. Cruzar vendor ali compra
  zero aptidão e cobra caro — transferência de dados para terceiro, uma via a mais para verificar
  antes de cada spawn, e um papel que some da coluna `Consumida por` das vias, ficando fora do
  cálculo de impacto quando o dono desliga uma via. `scout` cross-vendor é **recusa com motivo**.
- **No `reviewer`, a independência ganha do domínio, sempre.** Ele é **um só e sempre do vendor
  oposto ao host**, inclusive em card de `interface` no host Claude. A razão de existir do revisor é
  ser independente de quem escreveu, não ser apto no domínio; a trilha modula o *planner* (e, quando
  útil, a ênfase do briefing), **nunca o vendor do revisor**. Regra completa em `/orq:revisar`.

## Sem argumento — mostrar

Identifique o host, leia `memory/wiki/_elenco.md` e apresente **a tabela daquele host** (papel ·
modelo · por quê), mais as vias cross-vendor habilitadas e o `Perfil ativo` daquela seção. Diga qual
host você resolveu — sem isso o dono não sabe qual das tabelas está vendo. Se o arquivo não existir,
mostre os **padrões de fábrica** e ofereça criá-lo.

Feche sugerindo, em uma linha, o que costuma valer a pena ajustar (ex.: *"plano difícil rende mais
com um modelo mais forte no planner da trilha que você mais usa"*).

## Gate de capacidade — ajuste, perfil e inicialização

Este gate é global: vale também para `init`, para a oferta sem argumento de criar
um elenco ausente e para migração, ajuste de papel ou perfil. Consultá-lo não
autoriza chamadas de prova; mostrar o template é leitura, não ativação.

Antes de gravar, valide **somente os papéis que a operação altera**; não exija provas novas dos
papéis preservados. A prova se vincula a **modelo + via + conta/host**: registre modelo solicitado e observado,
effort quando aplicável, mecanismo (CLI, Companion ou spawn nativo), sandbox, versão do executável/runtime,
contexto de conta não sensível (rótulo local, sem login/token), data e recibo da execução real.
Referencie o recibo e esses pressupostos na thread do card; no elenco, `## Revisores externos`
referencia a thread para vias externas, e a justificativa do papel referencia a thread para via nativa.
**Catálogo não é prova**; prova CLI não comprova spawn nativo, nem read-only comprova escrita.
Mudança em modelo, effort, mecanismo, sandbox, versão ou contexto de conta exige revalidação.
Não há validade global: prova de outra célula ou outra conta não libera esta operação.

Se faltar prova, preserve o elenco inteiro (tabelas, presets e vias), não acione fallback e informe
a limitação. Permita uma **aquisição delimitada de prova autorizada** pelo dono, com modelo/effort,
mecanismo, sandbox, orçamento e número de chamadas definidos; sem sondas ou retry silenciosos.
Recusa de acesso encerra a aquisição; não escale modelo/effort automaticamente. Se não houver
opção comprovada, pare e peça a escolha do dono; não grave uma escolha fictícia.

Operação comum com padrão legado já comprovado conserva a capacidade e a política autorizadas; não exige nova
sonda a cada uso. **Padrão legado comprovado** é uma combinação já usada e autorizada neste projeto, com recibo real consultável na
thread. O Manager verifica a origem e a compatibilidade antes do despacho. É reaproveitamento de prova existente
válida, nunca isenção de prova. Default, alias ou cache não certificam. Sem recibo ou se o contexto mudou, não
despache essa operação. Não há sonda ou retry automáticos; prossiga com outras ações locais elegíveis. Quando o
recibo válido ainda é compatível, o reuso não exige nova sonda a cada uso.

Fábrica nova e candidato não comprovado não viram fallback executável só porque a tabela não
foi materializada. Adotar, gravar, promover, reativar ou executar candidato novo exige o gate específico e
evidência contextual de executor, modelo, workspace e effort.
Desligar exclusivamente uma via autorizada reduz exposição e é exceção expressa à nova sonda: anuncie o impacto
e não escolha fallback. Reativar ou trocar via continua exigindo prova contextual e o gate específico. Remover
override não recebe isenção genérica: pode promover fallback novo.

**Com prova válida e aprovação do alvo**, crie o elenco novo pelo template, registrando os recibos;
em arquivo existente, grave apenas a alteração aprovada na seção do host. Na inicialização,
valide todos os papéis que seriam criados (Manager é apenas registro da sessão, não spawn).
**sem prova, não crie nem reescreva** o arquivo, nem substitua linhas por candidatos.
Mostrar padrões de fábrica não os ativa. O Manager permanece o modelo da sessão escolhido pelo dono;
nenhum ajuste ou perfil troca a sessão viva. Este gate precede qualquer escrita do elenco,
inclusive semeadura de presets/headings; ele não autoriza aquisição de prova sem o dono.

## Com argumento — ajustar

`$ARGUMENTS` no formato `<papel> <valor>`. Exemplos (**do host Claude** — no Codex os modelos são
outros): `planner interface fable` ·
`implementer leve haiku` · `implementer normal gpt-5.6-terra@xhigh` · `codex off` ·
`runner-opus on`. O effort **não** se ajusta por aqui: ele mora no modelo do papel
(`reviewer gpt-6-astra@xhigh`), não na via.

**`$ARGUMENTS` começando com `perfil ` (ex.: `perfil economia`) não é papel** — vá direto para a
seção "Com argumento `perfil <nome>` — trocar o time inteiro" abaixo, em vez desta.

0. **Resolva o host primeiro.** Todo o resto deste passo a passo depende dele: quais modelos são
   aceitos, quais vias existem e **em qual tabela você vai gravar**. Host não identificado → pare e
   diga; não escolha uma tabela por presunção.
1. **É via ou é papel?** Compare o primeiro token com a coluna **Via** da seção
   `## Revisores externos` **deste** `_elenco.md` (de fábrica: `codex` e `runner-opus`), lida na
   hora, nunca uma lista decorada.

    **É via → este é o ramo, e ele termina aqui; não caia na validação de modelo do passo 2.**
    - O único valor aceito é `on` ou `off`. Qualquer outro (um effort, um modelo) → **recuse
      dizendo o que a via aceita**, e diga onde se muda o que ele provavelmente queria: o modelo e o
      effort ficam na linha do **papel**, na tabela do host.
    - `off` é desligamento autorizado que reduz exposição: não exige sonda nova, anuncia impacto e não
      escolhe fallback. `on`, troca de via/modelo ou remoção de override não usam essa exceção; todos
      exigem gate e prova contextual.
    - Grave o valor na coluna **Estado** daquela linha (`ativo` / `inativo`) — é a coluna que
     existe para isso; sem essa escrita, o "desliguei" seria só uma frase.
   - **Antes de gravar, leia a coluna `Consumida por` daquela via e derive o efeito real dali** —
     não presuma que a via mexida é a do seu host. Confirme **o efeito, não o ato**, nomeando
     **quais hosts e quais papéis** mudam:
     - **A via é cross-vendor para o SEU host** (ela aparece com o seu host em `Consumida por`) →
       desligar deixa este projeto **sem revisor independente neste host**: toda revisão passa a ser
       degradada e o Manager audita o diff ele mesmo. Se ela também alimenta um `planner`, diga que
       aquela trilha perde o planner do outro vendor.
     - **A via é do vendor do SEU host, ou só serve a outro host** → diga isso **explicitamente**:
       *"isto não muda nada nesta sessão; afeta o host X, nos papéis Y"*. Continue aceitando o
       comando — o dono pode estar numa janela e querer desligar a via da outra —, mas **nunca
       anuncie uma consequência que não vai acontecer aqui**. Foi esse o defeito: `codex off` rodado
       no host Codex anunciava "ficamos sem revisor", enquanto o revisor daquele host é o
       `runner-opus`, intacto.
   - Via desligada **não** muda a tabela do host: a linha do `reviewer` continua registrada. O que
     muda é que ela não pode ser executada — quem resolve isso é o consumidor, na hora do spawn.

   **É papel** → siga para o passo 2. Válidos: `manager` · `planner` · `implementer` · `reviewer` ·
   `docs` · `scout`. **Papéis com sufixo** aceitam as duas grafias, ponto-médio ou espaço:
   `planner·interface` = `planner interface`; `implementer·leve` = `implementer leve`.
   - **`planner` sem sufixo** → aplique **às duas trilhas** e **avise em uma linha** que o fez
     (colapsar as trilhas apaga o eixo de domínio; ele precisa saber que foi isso que pediu).
   - **`implementer` sem sufixo** → ajuste **só a faixa `normal`** e **avise em uma linha** que
     `pesada` e `leve` ficaram como estavam.
2. Valide o modelo **contra o vendor do host resolvido no passo 0** — não contra uma lista fixa:
   - **`implementer`, `docs` e `scout`: só modelos do vendor do host.** No host Claude, `opus` ·
     `sonnet` · `haiku` · `fable` · `inherit` ou um ID Anthropic suportado pelo spawn nativo,
     com prova delimitada pelo gate acima. O mapa do runner não limita a via nativa.
     No host Codex, um modelo
     OpenAI com effort quando aplicável (`gpt-6.1-sol@high`, `gpt-6-luna@medium`). Modelo de outro vendor
     aqui é **recusa com motivo**, não pergunta: nos dois primeiros porque escrita cross-vendor está
     fora do desenho; no `scout` porque leitura ampla e barata não se paga em domínio — diga isso ao
     recusar, e ofereça o modelo barato do host no lugar.
   - **`planner`**: qualquer vendor **com célula na `## Matriz de invocação`** para este host.
   - **`reviewer`**: idem, com o vendor obrigatoriamente **oposto ao do host** — pedido de revisor do
     vendor do host é recusa com motivo (a independência é a única coisa que ele entrega).
   - ⛔ **Vendor certo não basta: o MECANISMO daquela célula tem que conseguir executar o modelo.**
     Leia a célula antes de aceitar, e recuse o que ela não roda:
     - **Anthropic × host Codex** — a célula é o `run-opus-reviewer.py --model <alias-ou-id>`. O runner só
       aceita `claude-opus-5-5` e os aliases legados (`opus` · `fable` · `sonnet` · `haiku`) e só
       imprime parecer se o `modelUsage` comprovar identidade exata para o ID ou prefixo legado — pedir `fable` e
       receber Opus, ou receber `claude-fable-5-0` quando o elenco exige 5.1, reprova com
       `OPUS_MODEL_MISMATCH`, e alias fora do mapa é recusado **antes** de chamar o CLI. Registrar
       aqui um alias ou ID que o runner não conhece → **recuse citando o mapa**: *"o runner não tem esse
       valor no mapa de prova; registrar aqui gravaria um elenco que a execução não honra"*.
       Ensinar o runner um alias ou ID novo é **card novo**, não improviso deste comando.
       Passe sempre o valor resolvido do elenco em `--model`: o runner não lê `_elenco.md`.
       Seu default sem argumento continua `opus`, só por compatibilidade legada; a fábrica
       `claude-opus-5-5` exige `--model claude-opus-5-5`, nunca omissão da flag.
     - **OpenAI × host Claude** — a célula usa `codex:codex-rescue` e
       `codex-companion.mjs task --model <modelo> --effort <effort>`; o Companion aceita o modelo
       do catálogo e devolve `jobId` + `threadId`; o reúso por `card+papel` só vale quando o `threadId`
       devolvido é igual ao solicitado (contrato "Reúso durável do Codex Companion" da skill `orq`).
       Runtime que não retoma a thread pedida degrada a continuação — não é promessa de capacidade.
     - **OpenAI × host Codex** — a célula usa `codex exec -m <modelo>`; qualquer modelo OpenAI do
       catálogo é candidato, com effort quando aplicável e prova da célula antes de gravar.
     **Por que isto é regra e não zelo:** sem ela o arquivo registra Fable e a execução entrega
     Opus, calada, ou registra Fable 5.1 e a execução entrega 5.0 sem ninguém notar. Elenco que
     mente sobre quem trabalhou é pior que elenco ausente — some a procedência, que é justamente o
     que este arquivo existe para guardar.
   - Valor que não se encaixa em nenhuma dessas → **pergunte** em vez de gravar errado.
3. Grave **na tabela do host resolvido**, dentro de `## Times por host` (crie o arquivo a partir do
   modelo abaixo se não existir). **Host sem seção `## Perfis` própria** (é o caso de fábrica fora do
   host Claude): grave o ajuste e diga em uma linha que este host não tem presets — não invente um.
   **Host com presets e sem a linha `Perfil ativo`**: grave-a antes do ajuste — `padrao`, data de
   hoje, sem desvio, no formato da linha do template. Semear **depois** do ajuste faria o valor
   recém-alterado virar baseline permanente do `padrao`, e a divergência nunca mais apareceria como
   desvio. Só então: compare o valor novo ao preset **ativo** — inclusive quando o ativo é `padrao`,
   que não é estado-zero, é um preset como outro qualquer: divergiu → registre o desvio na linha
   **Perfil ativo** daquele host; voltou a bater com o preset → **remova** o desvio. Desvio vale só
   para papéis da tabela do host; estado de via cross-vendor não é desvio e nenhum perfil o toca.
4. Confirme o que mudou, **em qual host**, e **a partir de quando vale** (próximo spawn — não afeta
   agente em execução).

**Migração aditiva obrigatória:** antes de qualquer ajuste, leia o `_elenco.md` inteiro. Preserve
modelos, perfis e vias escolhidos pelo projeto; acrescente somente headings obrigatórias ausentes.
Se `## Matriz de invocação` ou `## Times por host` existir mas estiver incompleta, mostre o diff
proposto e pare no gate — não substitua uma linha já escolhida sem aprovação explícita.

**Migração de arquivo legado (anterior à 0.24.0)** — proposta com gate, nunca reescrita silenciosa.
Arquivo sem migração continua funcionando: o time vem de `## Times por host`, e onde essa seção não
existir valem os padrões de fábrica deste template.

⚠️ **Migre por SEÇÃO, não só a tabela ativa.** Um arquivo legado tem tabelas de papel em mais de um
lugar: a tabela ativa **e cada preset** de `## Perfis`. Converter só a ativa deixa presets de 5
linhas no arquivo; no primeiro `perfil economia`, a tabela do host é reescrita a partir de um preset
com **papéis faltando e eixos colapsados** — o defeito só aparece muito depois da migração, quando
ninguém mais liga uma coisa à outra. **Aplique as conversões de papel abaixo em todas as tabelas**, e
valide a aritmética antes de propor: preset legado de 5 linhas (`planner`, `implementer`, `reviewer`,
`docs`, `scout`) vira **exatamente 8** (planner +1, implementer +2); tabela de host vira **9** (as 8
mais `manager`). Contagem diferente disso = migração incompleta, não proponha.

**Conversões de papel — valem para a tabela ativa e para cada preset:**

- linha `planner` única → as **duas trilhas** naquele mesmo modelo, e diga que o eixo de domínio
  ficou desligado até ele escolher o par;
- linha `implementer` única → as **três faixas** naquele mesmo modelo;
- linha `reviewer (interno)` → o **reviewer único do vendor oposto ao host**, com a perda nomeada:
  o revisor do mesmo vendor do host saiu do fluxo padrão. **Num preset**, é a linha que mais engana:
  o modelo legado ali é do vendor do host, e mantê-lo devolveria o revisor interno pela porta do
  perfil.

**Conversões de estrutura:**

- **`## Papéis` presente** → era o time do host Claude sem dizê-lo. Proponha copiá-la para
  `### Host Claude` (preservando os modelos escolhidos) e **remover** o heading `## Papéis`, para não
  restar duas fontes. Enquanto o dono não aprovar, ela fica lá, **legada e não lida**.
  **`### Host Claude` já existe?** Então há duas versões do mesmo time e **não existe regra implícita
  de sobrescrita** — nem "o mais novo vence", nem "o `## Papéis` vence por ser o que era lido".
  Monte a **reconciliação linha a linha** (papel · valor em `## Papéis` · valor em `### Host Claude` ·
  o que você propõe · por quê), mostre no gate e espere a escolha dele. Divergência é informação:
  costuma ser um ajuste feito numa das duas e perdido na outra.
- **`## Perfis` presente** → declare de qual host aquele preset é (nos arquivos legados, sempre o
  Claude): o heading passa a nomear o host, como no template (`## Perfis — times nomeados do host
  Claude`). A seção continua no topo do arquivo, **não** vai para dentro de `### Host Claude` —
  aninhar preset dentro da tabela que ele reescreve confunde fonte com cópia.
- **linha de revisor externo de um vendor que este elenco não suporta mais** (host aposentado numa
  release anterior) → proponha a **remoção**, mostrando o diff, e espere o "pode" — apagar em
  silêncio some com o registro de por que ele existia. Vale também dentro dos presets, onde essa
  linha costuma sobreviver esquecida.

**`manager` é caso especial:** é a sessão principal, definida pelo `/model` do host — não dá pra
trocar por aqui. Se ele pedir, explique e sugira o `/model`.

## Com argumento `perfil <nome>` — trocar o time inteiro

`$ARGUMENTS` no formato `perfil <nome>`. Exemplos: `perfil economia` · `perfil padrao`.

0. **Resolva o host primeiro** (mesma razão do passo 0 acima) e vá à seção `## Perfis` **daquele
   host**. Host sem presets → diga isso e ofereça o ajuste papel a papel; **não** aplique preset de
   outro host, que traria modelos do vendor errado para os papéis de escrita.
   **Seção "Perfis" ausente num host que a tinha** (arquivo pré-0.16.0)? Semeie antes de aplicar, e
   avise em uma linha: preset `padrao` = a **tabela atual daquele host**, sem a linha `manager`
   (ela é o titular deste projeto — semear da fábrica devolveria, em silêncio, um time que o projeto
   nunca usou); preset `economia` = o time de fábrica. Arquivo sem a linha **Perfil ativo**?
   Grave-a também — `padrao`, com a data de hoje, sem desvio.
1. Leia a seção **Perfis** daquele host. Perfil inexistente → liste os que existem e **pergunte**;
   não crie perfil novo sem pedido explícito.
2. **Reescreva a tabela do host resolvido** dentro de `## Times por host`, a partir do preset
   (modelos e "Por quê"), e atualize a linha **Perfil ativo** daquela seção — nome + data, zerando
   desvios anteriores. **A linha `manager` não faz parte de preset nenhum — preserve-a como está.**
   Os presets têm 8 linhas (sem `manager`); a tabela do host tem 9. Reescrever "as 8 linhas do
   preset" apagaria o `manager`, e `perfil padrao` não o devolve — é perda permanente. **O estado
   das vias cross-vendor (seção "Revisores externos") também não é preset — não aplique o que o
   preset declarar; preserve o que está registrado agora**, pela mesma razão do `manager`: é o que
   está de fato instalado e ativo no projeto, não uma escolha do time. A linha "Revisores externos"
   dentro de cada preset é só informativa (estado de fábrica, de leitura).
3. Confirme mostrando o time novo, **em qual host**, **e o que se perde** — resuma a nota do preset
   em até 3 linhas. Havia desvio registrado na linha Perfil ativo? **Diga em uma linha que ele foi
   descartado** — sem isso, o registro só muda onde a escolha some, não o silêncio. **Anuncie, não
   pergunte**, e diga **na hora como reverter** (ex.: "quando o crédito voltar, é só dizer" ou
   `/orq:elenco perfil padrao`) — não invente nem espere que ele decore uma frase fixa de volta; o
   pedido de reverter é reconhecido como o pedido de mudança que é, na hora em que ele vier.
4. A troca vale a partir do **próximo spawn, nas janelas daquele host** — crédito é da conta, não da
   frente. Agente já em execução termina no modelo antigo; não refaça nada. Se houver card `[~]`
   no board, diga em uma linha que ele termina com elenco misto, e que isso é esperado.
5. **`manager` não muda por perfil.** Ao ativar um perfil de economia, sugira em uma linha que o
   dono avalie o `/model` da sessão — é onde mora o maior consumo, e só ele troca.
6. **Perfil nunca troca o vendor do `reviewer`.** Ele rebaixa degrau/effort **dentro do mesmo
   vendor**: rebaixar o revisor para o vendor do host acabaria com a independência, que é a única
   coisa que ele entrega.

## Modelo do arquivo

<!-- orq:elenco-padrao:start -->
### Fábrica — Host Codex

| Papel | LLM · effort |
|---|---|
| planner·interface | `claude-opus-5-5@high` |
| planner·sistema | `gpt-6.1-sol@xhigh` |
| implementer·leve | `gpt-6-luna@medium` |
| implementer·normal | `gpt-6.1-sol@high` |
| implementer·pesada | `gpt-6.1-sol@xhigh` |
| reviewer | `claude-opus-5-5@high` |
| docs | `gpt-6-luna@low` |
| scout | `gpt-6-luna@medium` |

### Fábrica — Host Claude

| Papel | LLM · effort |
|---|---|
| planner·interface | `claude-opus-5-5@high` |
| planner·sistema | `gpt-6.1-sol@xhigh` |
| implementer·leve | `claude-sonnet-5-5@low` |
| implementer·normal | `claude-sonnet-5-5@medium` |
| implementer·pesada | `claude-sonnet-5-5@high` |
| reviewer | `gpt-6.1-sol@xhigh` |
| docs | `claude-sonnet-5-5@low` |
| scout | `claude-sonnet-5-5@low` |

<!-- orq:elenco-padrao:end -->

Todos os valores de fábrica são candidatos à inicialização; somente o gate de capacidade acima
autoriza gravá-los. O template não declara que já foram exercitados na conta deste projeto.

```markdown
# Elenco — quem toca cada papel

**Onde o modelo é resolvido:** identifique o host, leia a tabela dele em `## Times por host`, e
aplique a célula da `## Matriz de invocação`. **Não existe outra tabela ativa** — nem para ler, nem
para gravar.

## Times por host

Cada host resolve o próprio time **na leitura** desta seção. `/orq:elenco` grava aqui, sempre na
seção do host onde está rodando — uma janela nunca reescreve o time da outra. “Configurado” não
significa “rodando agora”: o Manager verifica a sessão/CLI real antes de anunciar o papel.

### Host Claude

**Origem:** proposta do catálogo — não adotada. O init só substitui esta linha por
origem, versão, digest e data de adoção no host aprovado e comprovado.

| Papel | Modelo | Sandbox / mecanismo |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal |
| planner·interface | `claude-opus-5-5@high` | spawn nativo read-only; confira sessão, modelo e mecanismo antes do uso |
| planner·sistema | `gpt-6.1-sol@xhigh` | Codex Companion read-only; task fresca por card+papel e retomada pelo `threadId` exato |
| implementer·pesada | `claude-sonnet-5-5@high` | worktree dedicado, writer único |
| implementer·normal | `claude-sonnet-5-5@medium` | worktree dedicado, writer único |
| implementer·leve | `claude-sonnet-5-5@low` | worktree se houver trabalho paralelo |
| reviewer | `gpt-6.1-sol@xhigh` | Codex Companion read-only; vendor oposto ao host, retomada pelo `threadId` exato |
| docs | `claude-sonnet-5-5@low` | arquivos de documentação autorizados |
| scout | `claude-sonnet-5-5@low` | read-only |

**Perfil ativo:** `padrao` — desde <data de hoje>, sem desvio.
*(É o formato canônico da linha — a única vez que ele é definido, e vale por host. Duas formas
completas: sem desvio, `` `<preset>` — desde <data>, sem desvio.``; com um ou mais desvios,
`` `<preset>` — desde <data> · desvio: papel→modelo[; papel→modelo ...]`` — `;` separa múltiplos
desvios, e o valor depois de `→` é o modelo que está de fato na tabela hoje (o ativo), não o do
preset. A forma abreviada sem data, `padrao · desvio: papel→modelo`, continua aceita. Ajuste papel a
papel que diverge do preset ativo — inclusive com `padrao` ativo — grava o desvio; devolvido ao
preset, **remove-se** o desvio daquele papel — um desvio que já voltou a bater com o preset não pode
continuar na lista. Ver passo 3 de "Com argumento — ajustar".)*

### Host Codex

**Origem:** proposta do catálogo — não adotada. O outro host continua proposta até sua própria adoção.

| Papel | Modelo | Sandbox / mecanismo |
|---|---|---|
| manager | modelo da sessão (`/model`) | sessão principal; verificar, não trocar silenciosamente |
| planner·interface | `claude-opus-5-5@high` | runner Anthropic read-only, sem ferramentas; modelo e effort explícitos, identidade exata |
| planner·sistema | `gpt-6.1-sol@xhigh` | `read-only` |
| implementer·pesada | `gpt-6.1-sol@xhigh` | `workspace-write`, em worktree dedicado |
| implementer·normal | `gpt-6.1-sol@high` | `workspace-write`, em worktree dedicado |
| implementer·leve | `gpt-6-luna@medium` | `workspace-write`, em worktree dedicado |
| reviewer | `claude-opus-5-5@high` | runner Anthropic read-only, sem ferramentas; modelo e effort explícitos, identidade exata |
| docs | `gpt-6-luna@low` | arquivos de documentação autorizados |
| scout | `gpt-6-luna@medium` | read-only |

**Effort é parâmetro solicitado, não identidade observada nem garantia de qualidade.** Leve usa
`medium`, normal `high`, pesada `xhigh`; a prova deve exercitar cada par no mecanismo e sandbox
pretendidos. Uma sonda em `low`, sem escrita, não comprova estes pares em `workspace-write`.
Faixa mede risco e incerteza, não quantidade de linhas. O Manager justifica a escolha e conserva
o piso de Alto risco; falha não autoriza promoção silenciosa nem fallback para Terra.

**Aliases legados do runner:** `opus` → prefixo `claude-opus-5`; `fable` → `claude-fable-5-1`;
`sonnet` → `claude-sonnet-5`; `haiku` → `claude-haiku-4-5`. Sufixos de release continuam aceitos
para esses aliases; `claude-opus-5-5` exige igualdade, rejeitando `claude-opus-5-50` e Opus 5.
O alias `fable` não muda de destino. O prefixo de log `OPUS_` e o nome `run-opus-reviewer.py`
são contratos legados de fio, não afirmação de que todo modelo invocado é Opus.

**Perfil ativo:** — este host não tem presets de fábrica; ajuste papel a papel. Criar um `## Perfis`
para ele é pedido do dono, não iniciativa.

## Revisores externos

Esta seção **não é composição de painel** — o revisor é **um só**, resolvido pela tabela do host.
Aqui mora o **registro de capacidade das vias cross-vendor**: por onde um papel read-only alcança o
vendor oposto, com o que já foi comprovado e quando. O nome na coluna **Via** é o que se digita em
`/orq:elenco <via> on|off`.

| Via | Vendor | Consumida por | Estado | Registro |
|---|---|---|---|---|
| codex | OpenAI | **host Claude**: `planner·sistema` e `reviewer`. No host Codex **não é via** — é o vendor nativo | ativo | subagente `codex:codex-rescue` → `codex-companion.mjs task`; modelo e effort vêm da tabela, e `jobId` + `threadId` sustentam o reúso exato, aceito só com `threadId` devolvido igual ao solicitado |
| runner-opus | Anthropic | **host Codex**: `planner·interface` e `reviewer`. No host Claude **não é via** — é o vendor nativo | ativo | runner Anthropic `scripts/run-opus-reviewer.py --model <alias-ou-id> --effort <effort-resolvido>` · identidade exata para ID, prefixo para alias legado · 16 KiB por lote · timeout 600s |

A coluna **Consumida por** é o que torna o efeito de ligar/desligar anunciável sem chute: uma via só
afeta os papéis listados, nos hosts listados. Via cujo vendor é o do próprio host não é via nenhuma
ali — é o mecanismo nativo, e desligá-la não muda nada naquele host.

Aqui, **ativo significa política habilitada, não capacidade comprovada** — são duas checagens
distintas e **as duas são obrigatórias antes de usar a via**:

1. **Política** — a coluna `Estado` diz `ativo`? `inativo` é decisão do dono: **não use a via**, nem
   "só desta vez". Consumidor que ignora o `Estado` faz a transferência cross-vendor que o dono
   desligou.
2. **Capacidade** — binário, autenticação, modelo e saída não vazia, verificados no momento do uso.

Falhar em qualquer uma **não autoriza trocar de vendor**: no reviewer, as duas produzem
`REVISÃO DEGRADADA`, com a causa nomeada (política desligada **ou** capacidade ausente — são
diagnósticos diferentes e o dono precisa saber qual dos dois foi).

## Matriz de invocação

Resolva sempre **host → papel → vendor → mecanismo**. CLI chamada diretamente recebe
`< /dev/null`; sem TTY ela pode bloquear lendo stdin. O briefing para terceiro é sanitizado e
nunca leva dado de paciente, PII, prontuário ou credencial.

| Vendor do modelo | Host Claude | Host Codex |
|---|---|---|
| Anthropic | spawn nativo com overrides de modelo e effort comprovados nessa célula | `printf '%s' "$BRIEFING_SANITIZADO" \| python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/run-opus-reviewer.py" --model <alias-ou-id> --effort <effort-resolvido>` — limite 16 KiB/lote, timeout e identidade exata para `claude-opus-5-5` ou prefixo legado no `modelUsage`; valor fora do mapa de prova (`claude-opus-5-5`·`opus`·`fable`·`sonnet`·`haiku`) é recusado antes da chamada |
| OpenAI | **OpenAI × host Claude:** subagente `codex:codex-rescue` → `codex-companion.mjs task --model <modelo> --effort <effort>`; primeira chamada por `card+papel` usa `--fresh --json`, continuação usa `--resume-thread <threadId> --json`; briefing declara read-only, e o handoff persiste `rawOutput`, `jobId`, `threadId` e `status`; continuação só é aceita com `threadId` devolvido igual ao solicitado | **Host Codex: `codex exec` é obrigatório**; primitiva nativa só quando `_elenco.md` registrar override comprovado por chamada real |

⚠️ **Nunca acrescente `--write`.** O read-only desta chamada vem da ausência dessa flag: com ela, o sandbox do Companion vira `workspace-write` e o papel deixa de ser read-only.

Continuação exige sucesso e `threadId` devolvido igual ao solicitado. Divergência ou recibo
incompleto: registrar degradação, preservar o vínculo anterior e não repetir nem substituir a
thread automaticamente. Aplicar o contrato "Reúso durável do Codex Companion" (skill `orq`).

## Perfis — times nomeados do host Claude

Presets são **por host**: os dois abaixo valem para `### Host Claude` e são aplicados por
`/orq:elenco perfil <nome>` **rodando naquele host**. Cada preset é uma tabela **literal e
completa** — nunca uma referência a "a tabela acima". É isso que permite voltar (`perfil padrao`)
sem depender de memória: se `padrao` fosse só um ponteiro para a tabela do host, ativar `economia`
reescreveria a tabela e `padrao` passaria a apontar para o próprio `economia` — o time titular
sumiria do arquivo. `manager` e o estado das vias cross-vendor ficam fora dos dois presets: nenhum
perfil os toca, e aplicar um preset **preserva a linha `manager` e a seção "Revisores externos"**.

### `padrao` — o time titular

| Papel | Modelo | Por quê |
|---|---|---|
| planner·interface | claude-opus-5-5@high | trilha perceptual por spawn nativo read-only |
| planner·sistema | gpt-6.1-sol@xhigh | trilha comportamental pensa com OpenAI |
| implementer·pesada | claude-sonnet-5-5@high | alto risco ou decisão de desenho ainda aberta |
| implementer·normal | claude-sonnet-5-5@medium | plano fechado, execução dirigida |
| implementer·leve | claude-sonnet-5-5@low | resultado determinado, verificação mecânica |
| reviewer | gpt-6.1-sol@xhigh | vendor oposto ao host — a independência não se rebaixa |
| docs | claude-sonnet-5-5@low | escrita objetiva sobre código já pronto |
| scout | claude-sonnet-5-5@low | leitura ampla e barata |

Revisores externos: via `codex` ativa · via `runner-opus` ativa — estado de fábrica, informativo: o
perfil não aplica isto (ver passo 2 de "Com argumento `perfil <nome>`"), vale o que está registrado.

### `economia` — crédito curto

Exemplo legado opcional, não fábrica da versão. O init omite este preset se não houver pedido.

| Papel | Modelo | Por quê |
|---|---|---|
| planner·interface | opus | um planner só de Anthropic, sem o degrau extra de raciocínio |
| planner·sistema | gpt-6-astra@high | effort rebaixado dentro do mesmo vendor |
| implementer·pesada | sonnet | rebaixado um degrau — evita herdar o modelo caro da sessão |
| implementer·normal | sonnet | já era o degrau econômico |
| implementer·leve | haiku | já era o mais barato |
| reviewer | gpt-6-astra@high | effort rebaixado; **vendor não muda** — sem ele, não há revisão independente |
| docs | haiku | escrita objetiva; rebaixar aqui custa pouco |
| scout | haiku | leitura ampla e barata |

Revisores externos: via `codex` ativa · via `runner-opus` ativa — mesmo estado de fábrica do preset
`padrao`, também informativo, não aplicado pelo perfil (ver passo 2 acima). Quem decide o briefing
enxuto do `--rapido` é o `/orq:revisar` — regra lá.

**O que se perde — registre com todas as letras ao criar este perfil neste projeto:** o parecer
único fica com menos effort, e como ele é o **único** parecer independente, não há segundo revisor
para compensar — a auditoria do Manager contra o código passa a carregar mais peso; a escrita
rebaixada erra mais em card `pesada`, que é justamente onde ou o desenho ainda está aberto ou a
consequência do erro é a maior do board.
Ajuste os modelos e a nota à realidade do projeto somente se esse preset for pedido.
Não semeie esse exemplo legado em projeto novo; um preset econômico aprovado deriva da fábrica
carregada e da decisão do dono, sem transformar estes aliases históricos em recomendação de rotina.
```

**Proposta de fábrica (fora do bloco copiável).** Os valores do template são candidatos e só podem
ser gravados depois do gate de capacidade pela célula real; a aprovação do alvo não substitui essa
prova. Não redistribua docs, scout ou planners para acompanhar o implementer. Manager continua
escolha do dono na sessão.

## Como isso é aplicado

Ao spawnar um papel, os comandos (`plan-next`, `implement-next`, `revisar`, `init`) **leem o elenco**
pela frase normativa do topo: host → tabela do host → Matriz. Sem elenco, consulte `elenco_padrao.py`:
os padrões do catálogo carregado são candidatos, sujeitos ao gate antes de inicializar ou executar;
o `model:` dos arquivos em `agents/` não contorna esse gate nem autoriza fallback.

## Orientação (quando ele pedir recomendação)

- **Planner e Reviewer** são onde modelo forte mais se paga: um erro de plano custa a implementação
  inteira; um review fraco deixa passar o que vai quebrar depois.
- **Docs e Scout** são leitura/escrita objetiva — modelo menor resolve e sai mais barato.
- **Implementer** se dimensiona pela faixa, não pelo gosto: `pesada` só quando resta desenho por
  decidir; `leve` só quando a verificação é mecânica.
- **Só Claude, sem GPT?** `codex off` desliga a via externa — e, com ela, **o único revisor
  independente que existe** naquele host. Toda revisão passa a ser **degradada**: o Manager audita o
  diff ele mesmo e declara a ausência. Diga isso com todas as letras antes de desligar; não existe
  cair num revisor do mesmo vendor do host para tapar o buraco.
- Trocar modelo **não** troca a disciplina: as regras dos agentes valem igual.
- **Fim do ciclo de crédito?** `perfil economia` troca o time inteiro do host Claude — e o preset
  existente diz o que se perde. É opcional: sem ele, ofereça um diff específico; não o crie
  automaticamente. `perfil padrao` restaura o snapshot local, não a fábrica mais recente.
