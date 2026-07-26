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
└── scripts/                      kanban-status.sh · sm-search.py
```

**Onde mexer em quê:** comportamento geral e gatilhos → a **skill**. Um passo do fluxo → o **command**.
Um papel → o **agent**.

## Ciclo de edição

```bash
claude plugin validate ./orq --strict     # tem que passar
/plugin marketplace update orquestra
/reload-plugins                            # ou: claude plugin update orq@orquestra
```

O marketplace do dono aponta pro **caminho local deste repo**, então uma edição vale na hora — mas a
sessão em curso pode ter os prompts em cache até o `/reload-plugins`.

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
travessão para o subtítulo. A versão vive em `orq/.claude-plugin/plugin.json` e é repetida na seção
**Status** do README — os dois têm que andar juntos.

**Nunca commitar nem publicar sem o ok do dono.**
