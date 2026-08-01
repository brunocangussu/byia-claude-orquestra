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

**Convenção de commit** (do `git log`): `feat(0.X.0): descrição em minúscula, sem acento no assunto`,
travessão para o subtítulo. A versão vive em **quatro** lugares e os quatro andam juntos no mesmo
commit: `orq/.claude-plugin/plugin.json` · a seção **Status** do `README.md` · `memory/MEMORY.md` ·
`.claude-plugin/marketplace.json`. **Esta página já disse "dois" e isso custou caro:** o
`marketplace.json` ficou declarando `0.4.0` por **sete releases** sem ninguém notar — é a origem do
card `T-017`. O lint (`orq/scripts/lint-coerencia.py`) hoje confere os quatro.

**Nunca commitar nem publicar sem o ok do dono.**
