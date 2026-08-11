# Distribuição — empacotar, validar e publicar o plugin

> Como a coisa é hoje. O que muda aqui é raro, mas é exatamente o que se esquece entre sessões.

## Estrutura

```
.claude-plugin/marketplace.json   catálogo (aponta pro dir "orq")
orq/
├── .claude-plugin/plugin.json    manifesto (nome, versão, autor)
├── commands/                     os /orq:* — um arquivo por passo do fluxo
├── agents/                       o time — frontmatter define tools e o model padrão
├── skills/orq/SKILL.md           a disciplina: gatilhos naturais + regras invioláveis
└── scripts/                      kanban-status.sh · lint-coerencia.py · sm-search.py
```

**Onde mexer em quê:** comportamento geral e gatilhos → a **skill**. Um passo do fluxo → o **command**.
Um papel → o **agent**.

## Ciclo de edição

```bash
claude plugin validate ./orq --strict          # manifesto
python3 orq/scripts/lint-coerencia.py .        # coerência
claude plugin marketplace update orquestra     # relê o marketplace local
claude plugin update orq@orquestra             # copia para o cache — teste válido só após restart
claude plugin list                             # confirma versão e escopo
V=$(python3 -c "import json;print(json.load(open('orq/.claude-plugin/plugin.json'))['version'])")
diff -rq ~/.claude/plugins/cache/orquestra/orq/$V/ ./orq/   # TEM que voltar vazio
```

**Reload vs restart, por componente (medido em 2026-07-29):** `/reload-plugins` na sessão viva
**aplica** o update para **skill** (a 0.11.0 foi servida sem restart). Comando, agente, hook e MCP:
**não testados** — presuma restart. Novo dado atualiza uma célula da tabela do README ("Problemas
conhecidos"), nunca vira regra binária de novo.

⚠️ **O marketplace aponta pro diretório deste repo, mas isso NÃO significa que editar já vale.**
O plugin em uso é uma **cópia em cache** (`~/.claude/plugins/cache/orquestra/orq/<versão>/`). Sem os
dois comandos de update, a máquina continua rodando a versão antiga — foi assim que ficou presa na
0.4.0 por sete releases, sem nenhum sinal.

**Versão igual não prova conteúdo igual.** O cache é indexado por versão: editar sem bump não muda
o que roda e o `list` segue dizendo que está tudo certo (aconteceu no `5b75296`). O `diff` é o fecho
do ciclo — não-vazio depois do update = o release não aconteceu; bumpa e repete.

**Consequência prática:** o teste comportamental que **fecha card** só é válido depois do update **e
do restart** — reload basta para experimentar skill, não para validar.

A CLI `claude plugin` tem `install`, `update`, `marketplace`, `list`, `uninstall`, `validate` e
`tag` — dá para operar tudo sem os slash commands do cliente.

### Codex: instalação não é smoke

No Codex, reporte separadamente: fonte encontrada · plugin instalado · plugin habilitado · cache
coerente · skill visível em `/skills` · projeto/elenco resolvidos · smoke comportamental aprovado.
`codex plugin list` prova só parte dessa cadeia.

O smoke exige conversa nova: `/plugins` e `/skills` encontram o Orquestra; “onde paramos?” lê
`memory/MEMORY.md` antes do board; “quero melhorar X” cria/planeja card e para no gate. Até esse
teste passar, o estado correto é **“instalado, não validado”**. `/orq:*` permanece exclusivo do
Claude Code; no Codex a interface oficial é linguagem natural ou `/skills`.

Para validar o reviewer externo de verdade, use um projeto de teste sem instruções locais e peça
revisão em linguagem natural. A evidência mínima do Opus é: runner exit 0, stderr com
`OPUS_MODEL=claude-opus-5` e parecer não vazio. Testar só `claude --version` ou o alias no help não
prova modelo nem integração do plugin. Briefing acima de 16 KiB deve aparecer como lotes completos;
timeout/modelo errado/saída vazia precisam resultar em `PAINEL PARCIAL`, nunca silêncio.

## As duas verificações

`validate --strict` checa o **manifesto** e nada mais: passa com instruções que mandam rodar comando
inexistente — foi assim que o namespace `/orquestra:*` sobreviveu a três releases.

Por isso existe a segunda:

```bash
python3 orq/scripts/lint-coerencia.py .
```

Confere que todo `/orq:x`, `` `orq-agente` ``, `` skill `nome` `` e `${CLAUDE_PLUGIN_ROOT}/arquivo`
citado **existe de fato**. Sai com código 1 e lista `arquivo:linha` quando não.

**Ele ignora `memory/` de propósito** — o log é append-only e o `gotchas.md` citam nomes de comandos
extintos ao descrever bugs passados. Sem essa exclusão o lint acusaria falso positivo em todo
checkpoint, e lint que grita à toa é lint desligado.

**O que nenhuma das duas cobre:** contradição semântica entre arquivos (uma regra que nega outra em
linguagem natural). Isso é trabalho do painel de revisores — e é onde ele se paga.

O teste que importa é **comportamental**: instalar, conversar com o Claude em português natural e ver
se ele reconhece a intenção sem que ninguém digite comando.

## Formato do board (contrato com a statusline)

`scripts/kanban-status.sh` lê `memory/wiki/KANBAN.md` por regex. As linhas de card **precisam** ser:

```
- [x] `T-001` Título curto — nota livre depois do travessão
```

O marcador é o 4º caractere; o título é lido entre a crase do ID e o travessão. Uma seção cujo
título casa com `## .*Arquivad` **encerra a contagem** — tudo abaixo dela é ignorado no progresso.

## Publicar

```bash
git push origin main      # remote já configurado
```

Instalação a partir do GitHub: `/plugin marketplace add brunocangussu/byia-claude-orquestra`.

**O repositório é público, então o que está no `main` é o que terceiros instalam.** Enquanto um
release fica commitado sem push, quem instalar recebe a versão **anterior** e nada acusa — foi o
estado entre 05 e 07/ago, com a 0.19.0 parada localmente e o mundo recebendo a 0.18.0. Publicar é,
portanto, parte do release, não um passo opcional depois dele.

**Instalar nos outros dois hosts é o mesmo release, por outro mecanismo** (`/orq:instalar`):
Codex por `codex plugin add orq@orquestra` (cache indexado por versão, mesmo gotcha do Claude);
Kimi por **cópia** para `~/.agents/skills/orq/` + `~/.kimi-code/agents/` — snapshot **sem
versionamento**, que envelhece em silêncio se `/orq:instalar` não for re-rodado a cada release.
**Estado da frente T-043:** Claude permanece na `0.21.0`; a candidata corretiva `0.22.1` é exclusiva
do Codex e só pode atualizar o cache Codex depois dos gates e do painel Opus 5 + Kimi K3. GitHub e
publicação não fazem parte desta implementação local. O Kimi participa apenas como revisor em clone
descartável; sua instalação como host não é atualizada.

⚠️ **Gotcha do Codex, pago em 2026-08-08:** o marketplace `orquestra` dele aponta para **a pasta do projeto**, não para o GitHub. Então `codex plugin add` copia **o que estiver no disco naquele instante — inclusive trabalho não commitado e não revisado**. Foi assim que o Codex ficou rodando uma "0.20.0" tirada do meio de uma sessão, reprovada em três rodadas de painel. E como o cache é indexado **por versão**, atualizar depois **não troca nada**: mesmo rótulo, conteúdo velho. A saída é apagar `~/.codex/plugins/cache/orquestra/orq/<versão>/` e reinstalar.

**Convenção de commit** (do `git log`): `feat(0.X.0): descrição em minúscula, sem acento no assunto`,
travessão para o subtítulo. A versão vive em **quatro** lugares e os quatro andam juntos no mesmo
commit: `orq/.claude-plugin/plugin.json` · a seção **Status** do `README.md` · `memory/MEMORY.md` ·
`.claude-plugin/marketplace.json`. **Esta página já disse "dois" e isso custou caro:** o
`marketplace.json` ficou declarando `0.4.0` por **sete releases** sem ninguém notar — é a origem do
card `T-017`. O lint (`orq/scripts/lint-coerencia.py`) hoje confere os quatro.

**Nunca commitar nem publicar sem o ok do dono.**

## Hooks do guardião de contexto

Desde `0.22.0`, `hooks/hooks.json` faz parte do cache e precisa entrar no `diff -rq`. Na `0.22.1`,
o smoke exige `checkpoint_verified`, compactação não bloqueada e reidratação em
`SessionStart(source=compact)`. Instalação no
Codex só está validada quando `/hooks` mostra o bundle com confiança aprovada e uma sessão nova roda
`SessionStart` sem erro. `plugin list` e presença no disco não provam hook ativo.

O backstop de 90% usa `model_auto_compact_token_limit` absoluto e `scope = "total"`; ele não é
gravado pelo pacote. Diagnóstico calcula o valor da janela efetiva, mostra backup/operação e aguarda
aprovação nominal antes de alterar `~/.codex/config.toml`.
