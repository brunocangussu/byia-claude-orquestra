# `T-078` — Avaliar o AI-Memory 2.0

**Origem:** o dono trouxe `docs/AI-Memory-2.0_Plano_Integracao_Projetos.md` (análise externa, outro chat)
sobre `akitaonrails/ai-memory`, e pediu explicitamente para rodar pelo ciclo do Orquestra: planner →
revisor → decisão dele. **Nada foi implementado — nenhuma instalação, nenhum arquivo do produto
tocado.** Este é o registro do planejamento, não da execução.

## O que a pesquisa confirmou sobre a ferramenta (antes do planner)

Real e ativo: MIT, Rust, 5,7k stars, 1.609 commits, `v2.0.0` lançada há 2 dias (migração maior de
formato). Um binário roda servidor MCP/HTTP standalone (systemd ou Docker), dono de um data-dir
(`wiki/` markdown git-versionado, `db/` SQLite FTS5+embeddings). Suporte de primeira classe a Claude
Code e Codex (MCP + hooks, "kept honest by CI"). **Zero chamadas de LLM por padrão** — embeddings
locais em Rust, sem API key; LLM é opcional e só melhora resumo/busca semântica. Roteamento por
projeto/worktree via `.ai-memory.toml`. Nada instalado nesta máquina; porta padrão livre.

## O parecer do planner (GPT-5.6-sol via `codex exec`, read-only)

**Recomendação:** piloto reversível, claude-mem continua ativo. **"Hoje não há causa raiz
demonstrada que justifique substituir a wiki curada do Orquestra."** Trata como duas decisões
distintas — usar a ferramenta neste repositório não é o mesmo que incorporá-la ao framework
distribuído.

Desenhou 8 passos (linha de base → escolha de repo → verificação de custo zero em dois perfis →
medição de custo completo → verificação de gravação independente do health check → coleta paralela
de 10 dias/24 sessões/200 eventos → avaliação com 40 perguntas em 4 condições → reversibilidade +
dois pareceres), com critérios de aceite numéricos separados para "adoção pessoal" e "adoção no
Orquestra", e 7 decisões que ficam com o dono.

Achado de mérito, que sobrevive à revisão: **captura automática tende a acumular o que é derivável**
— o próprio `_schema.md` deste projeto já diz para não guardar isso, e foi exatamente o problema
medido no claude-mem (80% das observações eram narração de sessão). Esse argumento não depende de
nenhum dos números questionados abaixo.

## A revisão adversarial (mesmo vendor, contexto fresco — 8 bloqueadores)

**Auditados por mim contra o texto do plano antes de aceitar como veredito** — os dois exemplos
quantificáveis conferem: o plano de fato não define teto de duração ("o prazo só encerra a coleta se
houver material suficiente") e o critério de 34/40 é calculado sobre as 40 perguntas, não só as 8
reservadas — então usar as outras 32 para "ajustar filtros" contamina o próprio limiar de aprovação.

**Os 4 bloqueadores que mais importam:**

1. **Critérios gameáveis.** "Quatro perguntas a mais" não faz sentido se a referência já estiver
   perto do teto; falta regra de ganho líquido e de regressão tolerada.
2. **A coleta com as duas ferramentas ativas ao mesmo tempo contamina o A/B.** Se uma injeta memória
   que influencia o trabalho, ela pode mudar o que a outra depois captura. Não isola causa.
3. **Esforço sem teto.** ~160 respostas avaliadas, 100 registros classificados, auditoria de rede,
   reversão, possível segunda rodada — "para uma decisão pessoal reversível, isso é desproporcional
   como primeira etapa."
4. **"Aprovar o mecanismo de isolamento" pede aprovação de algo que o plano nem desenhou** — a
   viabilidade de isolar e auditar rede por processo no macOS, sem VM/container, não está demonstrada.

**A crítica estrutural, que é o achado mais importante da rodada inteira:**

> *"O plano perdeu a principal economia de esforço: avançar por evidência decisiva. Primeiro,
> demonstrar viabilidade técnica e reversão com orçamento limitado. Depois, procurar ganho concreto
> sobre o claude-mem corrigido em retomadas reais [...]. Não é necessário executar toda a matriz
> para descobrir que a ferramenta apenas duplica o histórico ou exige manutenção excessiva."*

**Veredito do revisor:** precisa ser simplificado e corrigido antes de ir ao dono decidir.

## Síntese do Manager — plano corrigido em estágios, com gate a cada um

Em vez de comprometer 10 dias e uma bateria completa de antemão, três estágios, cada um só abre o
próximo se o anterior passar. **Todos ficam parados no gate até o dono decidir avançar.**

### Estágio 0 — viabilidade técnica e reversão (barato, curto)

Instalar em projeto pessoal de baixo risco (nunca este repo, nunca dado sensível). Verificar, sem
aparato de auditoria pesado: (a) instala e roda; (b) captura grava de fato — mesmo teste que já
sabemos fazer no claude-mem, carimbo do banco antes/depois de uma sessão real, não `status`/health;
(c) sinal leve de rede — `lsof -i` / `nettop` durante uma sessão com LLM desligado, o suficiente para
detectar chamada óbvia, sem prometer auditoria forense que o macOS nativo não sustenta; (d)
`ai-memory uninstall --apply` remove de fato, tudo confirmado por diff de antes/depois nos hooks do
Claude Code. **Orçamento: dias, não semanas. Critério de parar: qualquer um dos quatro falha.**

### Estágio 1 — ganho real contra o claude-mem já corrigido (só se o 0 passar)

Não 40 perguntas sintéticas — um punhado de retomadas **reais** de trabalho, no mesmo projeto
pessoal, comparando o que cada ferramenta de fato devolveu quando precisou. Pergunta única: *o
AI-Memory achou algo relevante que o claude-mem (já sem o bug de 22h) não achou?* Se a resposta for
não depois de tentativas honestas, encerra aqui — sem rodar a matriz inteira só para confirmar que
duplicar histórico não ajuda.

### Estágio 2 — decisão de adoção pessoal e, separadamente, se cabe no Orquestra (só se o 1 mostrar ganho plausível)

Aqui sim cabe algo como a comparação mais formal do plano original — mas dimensionada ao ganho já
observado no Estágio 1, não no tamanho máximo antes de saber se há qualquer ganho. Para o Orquestra
especificamente, a barra do planner continua valendo tal como escrita: casos reais de ganho sobre o
checkpoint, integração opcional (ausência do daemon nunca impede board/checkpoint), e a wiki mantém
precedência sempre — hipótese capturada automaticamente nunca vira autorização.

## Achado paralelo, registrado à parte

O `_elenco.md` promete `@max` para `planner·sistema` e `reviewer` no host Claude; o wrapper
(`codex-companion.mjs`) só aceita até `xhigh` — `max`/`ultra` não existem nessa interface, mesmo
estando na lista de efforts do `codex` binário. Usei `xhigh` nas duas chamadas desta rodada e
declarei a degradação. Vira gotcha; não bloqueia esta análise.

## O Codex não captura — root cause achado em 2026-09-05

**Sintoma:** o Claude captura normalmente (8 sessões, centenas de observações), o Codex capturou
**3 eventos às 09:19 e nunca mais nada**.

**Root cause: dois programas disputam o mesmo arquivo, e o Terminals ganha.**
O `~/.codex/hooks.json` é **gerenciado pelo app Terminals** — era o que o campo
`_managedBy: "terminals.app"` declarava. Ele reescreve o arquivo com a versão dele e apaga o que
outro programa tiver escrito. A linha do tempo prova: sessão do Codex capturou às **09:19:38**;
arquivo reescrito às **09:24:26** sem os hooks do ai-memory. Funcionou uma vez e morreu.

**Diagnóstico que separou as hipóteses:** invocar o comando do hook do Codex **na mão** funcionou
(sessões `codex` foram de 1 para 2). Logo, o comando estava certo, o daemon aceitava, e o problema
era o Codex **não chamar** o hook — não o hook falhar. Sem esse teste eu teria ficado culpando o
ai-memory.

**Achado colateral, anterior a esse:** o mesmo `hooks.json` tinha o campo `_managedBy` no topo, que
o `codex-cli 0.153.2` **não aceita** — `failed to parse hooks config: unknown field _managedBy`. O
arquivo **inteiro** era descartado, derrubando junto os hooks do próprio Terminals. Isso é bug
pré-existente do par Terminals×Codex, **não** causado pela instalação do ai-memory (comprovado pelo
backup automático, que já trazia o campo antes de eu tocar em nada). Removi o campo; o parse voltou
e o aviso "Hooks need review" finalmente apareceu — o dono aprovou os 10 hooks.

**Correção aplicada:** os 6 hooks do ai-memory foram movidos do `hooks.json` para o
**`~/.codex/config.toml`**, que o Terminals não gerencia. O Codex lê hooks dos dois arquivos (é o
aviso *"loading hooks from both … prefer a single representation"*). TOML validado; backup em
`config.toml.bak-antes-hooks-toml-2026-09-05`.

**Estado ao fechar:** nenhuma sessão real do Codex capturada ainda. As duas linhas `codex` no banco
são: a de 09:19 (antes do arquivo ser varrido) e a de 11:29 (**meu teste manual** — tem só um
`session-start`, assinatura de invocação sintética). O dono reiniciou o app, mas relatou que o
Codex só pergunta sobre confiança **ao iniciar um chat novo**, não ao reabrir o app.

**Aprendizado de método, que vale além deste card:** *"funcionou" precisa ser reconferido depois de
um tempo, não só na hora.* Se o dono não tivesse voltado a perguntar, eu teria registrado que o
Codex estava capturando — e estaria errado cinco minutos depois. É a mesma família da falha
silenciosa do claude-mem, por causa completamente diferente.

## ⏭️ RETOMAR AQUI

**Checkpoint de 2026-09-05.** Tudo commitado e publicado. Nada pendente no disco.

**Estado em uma frase:** o AI-Memory está instalado global e persistente; **o Claude captura, o
Codex não**, e o conserto do Codex está aplicado mas **não validado**.

### A única pendência técnica

Validar a captura no Codex, **de dentro do próprio Codex** — daqui não dá, porque não enxergo a
sessão dele. O dono levou uma mensagem de handoff para lá. O que precisa acontecer:

1. Iniciar um **chat novo** no Codex (o gate de confiança só aparece em chat novo, não ao reabrir
   o app) e aprovar os hooks.
2. Conferir pelo **carimbo do banco**, nunca por exit code ou health:
   `select agent_kind, count(*) from sessions group by agent_kind` — e olhar as observações da
   sessão mais recente. Sessão real tem `session-start` + `user-prompt` + `pre/post-tool-use` +
   `stop`. **Só `session-start` é assinatura de invocação sintética, não vale como prova.**
3. Se ainda não capturar: rodar o comando do hook na mão. Já testado, funciona (exit 0, banco
   mexe) — então hook manual OK + automático falhando significa que **o host não está chamando**.

### O que fica esperando decisão do dono (não avança sozinho)

- **`T-074`** — deixar o claude-mem ligado no Codex, agora que há duas camadas de captura em
  paralelo. A pergunta ganhou peso: rodar as duas ao mesmo tempo era o desenho do piloto, mas o
  revisor apontou que isso **contamina a comparação** (uma injeta memória que muda o que a outra
  captura).
- **Estágio 1** (ganho real contra o claude-mem) e **Estágio 2** (adoção pessoal / entrar no
  Orquestra) continuam válidos e **não iniciados**. O dono pulou a validação em estágios ao mandar
  instalar global; o critério de "vale a pena" segue sem resposta.
- **Excluir projeto sensível da captura** (o `Bruno Vascular` é o candidato): já está sendo
  capturado, por decisão informada do dono. O mecanismo de marcador por projeto existe e é rápido —
  não implementado porque não foi pedido.

### Reavaliação combinada

O dono pediu para "usar e reavaliar aqui um tempo". Sugestão: em 1–2 semanas, comparar `ai-memory
status` (contagem, disco) e o que cada camada achou em retomadas reais. É o Estágio 1 acontecendo
organicamente, sem ter que escolher um projeto de antemão.
