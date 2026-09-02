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
└── scripts/                      kanban-status.sh · lint-coerencia.py · guardiões e runners testados
```

**Onde mexer em quê:** comportamento geral e gatilhos → a **skill**. Um passo do fluxo → o **command**.
Um papel → o **agent**.

## Ciclo de edição

⚠️ **Mexeu em `orq/`? O primeiro passo é o bump — antes dos gates, no mesmo commit.** Os quatro
lugares andam juntos: `orq/.claude-plugin/plugin.json` · `.claude-plugin/marketplace.json` · a seção
**Status** do `README.md` · `memory/MEMORY.md`. Nenhum gate pega a omissão: o teste de coordenação
só compara os quatro **entre si**, e sem bump eles continuam iguais; o bloco de cache do lint só roda
quando aquela versão **já existe** no disco, então em máquina limpa ou no CI ele nem é exercitado.
Sem bump, o release reaproveita a chave e o cache conserva os bytes antigos — o `T-017`.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'   # suíte — 201 testes
claude plugin validate ./orq --strict          # manifesto
python3 orq/scripts/lint-coerencia.py .        # coerência
claude plugin marketplace update orquestra     # relê o marketplace local
claude plugin update orq@orquestra             # copia para o cache — teste válido só após restart
claude plugin list                             # confirma versão e escopo
ORQ_CLEAN_SOURCE="<clean-source>"
test -z "$(git -C "$ORQ_CLEAN_SOURCE" status --porcelain)"
V=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' \
  "$ORQ_CLEAN_SOURCE/orq/.claude-plugin/plugin.json")
python3 "$ORQ_CLEAN_SOURCE/orq/scripts/verify_installed_cache.py" \
  --host claude --source "$ORQ_CLEAN_SOURCE/orq" \
  --installed ~/.claude/plugins/cache/orquestra/orq/$V/     # exit 0
```

`<clean-source>` é checkout detached do SHA remoto aprovado, com `git status --porcelain` vazio;
cache de host, working tree com artefatos e cópia derivada de cache não são fonte. O verificador
compara entrada, tipo e bytes. No lado instalado, Claude permite
somente `.in_use` (arquivo legado ou diretório no topo) e `.orphaned_at` (arquivo no topo); Codex
permite somente `.codex-plugin/migrated-command-skills/`. A fonte não recebe exceção, `.DS_Store`
falha e qualquer outro extra, ausência, mudança de tipo ou byte drift sai `1`; leia `tipo:caminho`
e corrija a fonte/cache sem bump automático. Erro operacional sai `2`. São os dois únicos hosts
com cache de bundle — e, desde a `0.24.0`, os dois únicos hosts do produto.

Esse fecho pós-release só vale quando o marketplace/update resolve o **mesmo SHA** de
`ORQ_CLEAN_SOURCE`. Marketplace `Directory` é iteração local, não prova publicação nem pode ser
misturado com clone remoto para declarar o cache validado.

Evidência operacional de 2026-08-30: a fonte remota final `41ed5da` foi clonada em detached e limpa;
os caches 0.22.7 de Claude e Codex passaram com `rc=0`. A mesma ferramenta rejeitou com `rc=1` um
`unexpected-extra.txt` inserido somente em cópias descartáveis. Se os caches reais já estiverem
instalados, habilitados e coerentes, não repita o instalador apenas para produzir movimento.

Validação natural de 2026-08-31: uma task Codex nova carregou a skill 0.22.7 pela frase *"onde
paramos?"* e retomou `memory/MEMORY.md` antes do board e da thread ativa. Isso fecha o smoke Codex
da T-049. O smoke Claude permanece separado e exige restart explicitamente autorizado; nunca use o
fechamento do Codex como autorização implícita para reiniciar outro host.

**Reload vs restart, por componente (medido em 2026-07-29):** `/reload-plugins` na sessão viva
**aplica** o update para **skill** (a 0.11.0 foi servida sem restart). Comando, agente, hook e MCP:
**não testados** — presuma restart. Novo dado atualiza uma célula da tabela do README ("Problemas
conhecidos"), nunca vira regra binária de novo.

⚠️ **Um marketplace local pode apontar para o diretório deste repo, mas isso NÃO significa que editar já vale.**
O plugin em uso é uma **cópia em cache** (`~/.claude/plugins/cache/orquestra/orq/<versão>/`). Sem os
dois comandos de update, a máquina continua rodando a versão antiga — foi assim que ficou presa na
0.4.0 por sete releases, sem nenhum sinal.

**Versão igual não prova conteúdo igual.** O cache é indexado por versão: editar sem bump não muda
o que roda e o `list` segue dizendo que está tudo certo (aconteceu no `5b75296`). O verificador é o
fecho do ciclo: exit `1` exige reconciliar `tipo:caminho`; não autoriza bump automático.

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
timeout, modelo errado ou saída vazia precisam resultar em **`REVISÃO DEGRADADA — sem parecer`**,
com a causa real nomeada — nunca silêncio e **nunca `PAINEL PARCIAL`**, que é vocabulário da época do
painel. Nessa situação **o card não avança sozinho**: seguir sem revisão independente é decisão do
dono, pedida na hora. O contrato completo é o do `/orq:revisar`; esta página não o reescreve.

## As três verificações

**1. A suíte** — o único gate que executa código de verdade:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'
```

São 201 testes cobrindo `verify_installed_cache`, `context-guard`, `run-opus-reviewer` e os dois
auditores. **Rode-a antes de publicar**: os outros dois gates leem texto e manifesto, então uma
regressão no verificador, no runner ou no guardião passa por eles **inteira**. A lista de módulos é
**descoberta**, não enumerada — enumerar já custou caro: a instrução citava três dos cinco, e quem a
seguia rodava 119 dos 201 achando que rodara tudo.

**2. `validate --strict`** checa o **manifesto** e nada mais: passa com instruções que mandam rodar
comando inexistente — foi assim que o namespace `/orquestra:*` sobreviveu a três releases.

**3. O lint de coerência:**

```bash
python3 orq/scripts/lint-coerencia.py .
```

Confere que todo `/orq:x`, `` `orq-agente` ``, `` skill `nome` `` e `${CLAUDE_PLUGIN_ROOT}/arquivo`
citado **existe de fato**. Sai com código 1 e lista `arquivo:linha` quando não.

**A fronteira do `memory/`, exata.** O lint pula `memory/` por padrão — o log é append-only e o
`gotchas.md` citam nomes de comandos extintos ao descrever bugs passados; sem essa exclusão ele
acusaria falso positivo em todo checkpoint, e lint que grita à toa é lint desligado. **Duas páginas
são exceção nominal e SÃO varridas**, porque não são registro histórico e sim instrução viva sobre
como o sistema funciona hoje: `memory/wiki/distribuicao.md` (esta) e `memory/wiki/arquitetura.md`.
Nelas valem os guardas de host aposentado, vocabulário extinto e fonte de versão. **Continuam fora:**
`fixes-history.md`, `gotchas.md` e tudo em `memory/wiki/threads/`. Falha nessas duas páginas **não é
falso positivo** — é regra viva contradita. A lista está em `PAGINAS_VIVAS_FORA_DO_PLUGIN`, no lint.

**O que nenhum dos três cobre:** contradição semântica entre arquivos (uma regra que nega outra em
linguagem natural). Isso é trabalho do revisor independente do vendor oposto — e é onde ele se paga.

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

**Instalar no outro host é o mesmo release, por outro mecanismo** (`/orq:instalar`): Codex por
`codex plugin add orq@orquestra` — cache indexado por versão, mesmo gotcha do Claude, e por isso a
mesma prova pelo `verify_installed_cache.py`, nunca por comparação bruta de diretórios.
**Estado da release combinada T-037 + T-043:** a `0.22.3` foi publicada em `origin/main` no commit
`3bb1a24e9c06e483cc987b2b34bff9a2fac6858c`, instalada no Codex e no Claude a partir do marketplace
GitHub nominal — e, na época, espelhada também no terceiro host que desde a `0.24.0` saiu do
produto. Os caches novos bateram com a fonte remota limpa;
os antigos ainda referenciados por tasks abertas foram preservados. A candidata T-044/`0.22.2`
ficou fora. Esta task provou um detalhe operacional adicional: enquanto uma sessão viva ainda cita
um cache antigo, esse diretório precisa continuar existente e marcado com `.in_use`; a restauração
do `0.22.2` resolveu o hook sem modificar a `0.22.3`.

⚠️ **Gotcha do Codex, pago em 2026-08-08:** marketplace apontando para pasta local copia inclusive
trabalho não commitado e não revisado. Foi assim que o Codex rodou uma "0.20.0" tirada do meio de uma
sessão. Registre o marketplace no GitHub depois do push e sempre use versão nova. Não apague caches
antigos: antes do upgrade, inventarie os caminhos ainda citados em `~/.codex/sessions/` e
`~/.codex/archived_sessions/`, faça backup e restaure qualquer diretório referenciado que o
instalador remova. Compare com a fonte somente o cache da versão recém-instalada.

**Convenção de commit** (do `git log`): `feat(0.X.0): descrição em minúscula, sem acento no assunto`,
travessão para o subtítulo. A versão vive em **quatro** lugares — e só quatro — e os quatro andam
juntos no mesmo commit: `orq/.claude-plugin/plugin.json` · a seção **Status** do `README.md` ·
`memory/MEMORY.md` · `.claude-plugin/marketplace.json`. **Esta página já disse "dois" e isso custou
caro:** o `marketplace.json` ficou declarando `0.4.0` por **sete releases** sem ninguém notar — é a
origem do card `T-017`. O lint (`orq/scripts/lint-coerencia.py`) confere os quatro, e o
`ContextGuardReleaseVersionTest` **deriva** a versão do manifesto para conferir os outros três contra
ela. ⚠️ **Não literalize a versão dentro do teste**: uma constante `expected` fixa seria uma **quinta
fonte de verdade** e um quinto ponto de esquecimento a cada bump — foi assim que ela nasceu, e o
`T-052` a desfez.

**Nunca commitar nem publicar sem o ok do dono.**

## Hooks do guardião de contexto

Desde `0.22.0`, `hooks/hooks.json` faz parte do cache e por isso entra na cobertura do
`verify_installed_cache.py` como qualquer outro arquivo do pacote — **não** o compare com `diff -rq`:
a comparação bruta reprova cache válido por artefato instalado-only legítimo (`.in_use`,
`.orphaned_at`, `migrated-command-skills/`), que é exatamente o falso positivo do `T-049`. Na
`0.22.1`,
o smoke exige `checkpoint_verified`, compactação não bloqueada e reidratação em
`SessionStart(source=compact)`. Instalação no
Codex só está validada quando `/hooks` mostra o bundle com confiança aprovada e uma sessão nova roda
`SessionStart` sem erro. `plugin list` e presença no disco não provam hook ativo.

O backstop de 90% usa `model_auto_compact_token_limit` absoluto e `scope = "total"`; ele não é
gravado pelo pacote. Diagnóstico calcula o valor da janela efetiva, mostra backup/operação e aguarda
aprovação nominal antes de alterar `~/.codex/config.toml`.
