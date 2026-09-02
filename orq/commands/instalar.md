---
description: Instala o próprio plugin Orquestra no host alternativo do dono — Codex — a partir da mesma fonte já registrada no Claude Code; confere Claude sem reinstalar
argument-hint: "[codex | claude — sem argumento, avalia os dois e propõe o que falta]"
---

O `/orq:init` instala o Orquestra **neste projeto** (memória, board, elenco). Este comando é outro:
instala **o plugin em si**, escopo de usuário, no host alternativo que o dono usa como motor
principal — o Codex. Decisão do dono: o que roda fora do Claude Code é **o mesmo plugin**, não
uma cópia adaptada — por isso não há "instalador" com lógica própria por host, só o mecanismo que
cada CLI já aceita.

⚠️ **Você não instala nada sem o "pode instalar" explícito.** Mostre os comandos exatos e o que cada
um faz; só rode depois da confirmação — mesma regra do `/orq:stack`. Sem argumento, avalie os dois
hosts e proponha; com um host nomeado, vá direto nele.

## 0. Descobrir a fonte — nunca hardcode caminho desta máquina

```bash
claude plugin marketplace list
```

Ache a linha do marketplace `orquestra` e leia a `Source`. `Directory` serve somente para iteração
local explicitamente não publicável: **`Directory` é proibida como fonte de release**. Ela pode
conter working tree sujo, outra branch ou uma candidata sem gate, e um `diff` contra a mesma pasta
errada produziria um falso verde.

Em release, `<fonte>` tem que ser a referência GitHub aprovada e o commit remoto precisa ser o mesmo
commit local já revisado. Antes de remover ou registrar marketplace, prove o `HEAD` publicado com
`git ls-remote`:

```bash
ORQ_RELEASE_REPO="<diretório-do-repo-orquestra-revisado>"
ORQ_RELEASE_SHA="$(git -C "$ORQ_RELEASE_REPO" rev-parse HEAD)"
ORQ_REMOTE_SHA="$(git ls-remote https://github.com/<referência-remota>.git refs/heads/main | awk '{print $1}')"
test -z "$(git -C "$ORQ_RELEASE_REPO" status --porcelain)"
test "$ORQ_RELEASE_SHA" = "$ORQ_REMOTE_SHA"
```

Qualquer falha para aqui: não instale de `Directory`, não use cache antigo como substituto e não
compare duas cópias da mesma fonte não comprovada. `ORQ_RELEASE_REPO` é nominal e obrigatório: não
rode `git rev-parse` ou `git status` no diretório corrente de um projeto consumidor. Depois da igualdade, registre
`<referência-remota>` como `<fonte>`. Para os passos de filesystem, **`<fonte-local>` vem de clone limpo no mesmo SHA**:
clone a referência remota em diretório temporário, faça checkout detached de
`ORQ_RELEASE_SHA`, confirme `git status --porcelain` vazio e use a raiz desse clone. Cache de host
nunca substitui esse clone: contém metadados runtime e não prova o commit remoto. Sem clone limpo,
a instalação para como **fonte não validada**.

## Claude — já instalado, só confere

Vale quando você **é** o Claude Code — identifique pelo host, não pelo caminho deste arquivo: com
`commands/` agora copiado para o outro host (seção abaixo), este mesmo texto também é lido pelo
Codex. Sendo Claude, não reinstale — mas **conferir aqui é obrigatório**, e você já tem com o que: o passo
0 resolveu `<fonte-local>` como clone detached e limpo do SHA aprovado. Use-o direto:

```bash
python3 <fonte-local>/orq/scripts/verify_installed_cache.py \
  --host claude \
  --source <fonte-local>/orq \
  --installed ~/.claude/plugins/cache/orquestra/orq/<versão>/                 # exit 0
```

⛔ **Não caia no ramo "Source remota" do diagnóstico genérico.** Ele encerra em *"conteúdo não
verificável daqui — indeterminado"* porque assume que **não existe** fonte local; aqui existe, e
concluir "indeterminado" com o clone limpo na mão é desistir de uma prova disponível. Exit `1` → leia
`tipo:caminho` e reconcilie contra o clone; exit `2` → **instalação não validada**.

**Não invoque `/orq:stack`** — você não roda slash command de dentro de outro comando (mesma regra do
`/orq:init`, seção "Stack complementar"). O que o `${CLAUDE_PLUGIN_ROOT}/commands/stack.md` acrescenta
e não se duplica aqui é o resto do diagnóstico: escopo, PATH, skill carregada, board legível.

## Codex

Antes de `add`/`update`, preserve os caches que tasks existentes ainda podem carregar pelo caminho
absoluto. Este preflight é obrigatório em upgrade — uma versão antiga referenciada não é lixo:

```bash
ORQ_CACHE_ROOT="$HOME/.codex/plugins/cache/orquestra/orq"
ORQ_CACHE_BACKUP="$(mktemp -d "${TMPDIR:-/tmp}/codex-plugin-cache.XXXXXX")"
ORQ_REFERENCED="$ORQ_CACHE_BACKUP/referenced-caches.txt"
rg -o --no-filename "$ORQ_CACHE_ROOT/[0-9]+\.[0-9]+\.[0-9]+" \
  "$HOME/.codex/sessions" "$HOME/.codex/archived_sessions" 2>/dev/null \
  | sort -u > "$ORQ_REFERENCED" || true
test ! -d "$ORQ_CACHE_ROOT" || cp -a "$ORQ_CACHE_ROOT/." "$ORQ_CACHE_BACKUP/"
```

Não apague nem sobrescreva em massa `ORQ_CACHE_ROOT`. Depois da instalação, restaure do backup
somente qualquer diretório listado em `ORQ_REFERENCED` que tenha desaparecido e confirme, em cada
um, que `scripts/context-guard.py` continua presente e executável. Esses diretórios antigos são
compatibilidade para tasks já abertas; não devem ser comparados com a versão nova.

```bash
codex plugin marketplace add <fonte>
codex plugin add orq@orquestra
```

Verificação:
```bash
codex plugin list                                                            # orq: installed, enabled
python3 <fonte-local>/orq/scripts/verify_installed_cache.py \
  --host codex \
  --source <fonte-local>/orq \
  --installed ~/.codex/plugins/cache/orquestra/orq/<versão>/                  # exit 0
```

O verificador deve vir da **fonte limpa**, nunca do cache que está sendo verificado. Ele normaliza
somente `.codex-plugin/migrated-command-skills/` no lado instalado e falha para qualquer outro
extra, ausência, mudança de tipo ou byte drift. Use-o **somente** para `<versão>` recém-instalada.
Exit `1` exige ler `tipo:caminho`: corrija a árvore instalada ou a fonte e reinstale a candidata;
não faça bump automático. Exit `2` é erro de host, raiz ou leitura e deixa a instalação não
validada.
Se o instalador removeu um cache
referenciado, recupere o diretório homônimo de `ORQ_CACHE_BACKUP` sem substituir a versão nova;
falha nessa restauração deixa o host **instalado, não validado**.

O diagnóstico do Codex tem **nove camadas independentes** — não pule da primeira para a última:

1. marketplace/fonte encontrada;
2. plugin instalado;
3. plugin **instalado e habilitado**;
4. versão e conteúdo do cache coerentes;
5. **skill carregada** e visível em `/skills`;
6. estrutura do projeto e elenco resolvidos;
7. hooks do plugin visíveis em `/hooks` e com a **confiança** aprovada;
8. guardião de contexto carregado, `PLUGIN_DATA` gravável e telemetria disponível;
9. **smoke comportamental** aprovado em conversa nova.

No Codex, use linguagem natural ou `/skills`; `/orq:*` pertence ao Claude Code. Depois das quatro
primeiras camadas, abra uma conversa Codex nova: confirme `/plugins` e `/skills`, diga “onde
paramos?” e verifique leitura de `memory/MEMORY.md` antes do board. Em fixture sem dado real, diga
“quero melhorar X”: o Orquestra deve criar/planejar o card e parar no gate. Sem esse smoke, reporte
**“instalado, não validado”** — nunca “pronto”.

O bundle `hooks/hooks.json` é parte do pacote e pode pedir revisão de confiança na primeira carga ou
quando mudar. Confirme em `/hooks`; não trate hook apenas presente no disco como ativo. A instalação
não edita `~/.codex/config.toml`: o backstop de 90% é opt-in e entra por proposta nominal separada.

No smoke do guardião, use uma conversa nova e confirme a sequência inteira: checkpoint completo →
estado `checkpoint_verified` → prompt seguinte permitido → `PreCompact`/`PostCompact` sem bloqueio →
`SessionStart(source=compact)` reidratando memória, board e thread. Rode também a prova negativa do
outro host: com ambiente somente `CLAUDE_*`, `context-guard.py` deve sair `0`, sem stdout, sem estado
e portanto **sem efeito**. Uma release exclusiva do Codex não atualiza nem reempacota o cache do
Claude.

Reversão (mecanismo comprovado limpo — instala, confere e remove sem sobra):
`codex plugin remove orq@orquestra` + `codex plugin marketplace remove orquestra`.

**Não prometa mais do que foi comprovado**: o que o Codex efetivamente *ativa* do plugin instalado
numa sessão viva (skill? gatilho por frase? commands? agents?) só se sabe testando ao vivo — isto
aqui instala e confere que o conteúdo bateu, não substitui abrir uma sessão e conversar. Se `codex`
não responder no PATH, não conclua ausência: instaladores escrevem em `.zshrc`, que só alcança shell
aberto depois de reabrir o terminal.

## O gotcha que atravessa os dois hosts

Cache indexado por versão vale para **Claude e Codex**, comprovado nos dois: editar `orq/` sem
bumpar não muda o que roda, e nenhum `plugin list` acusa. **Release novo → rode `/orq:instalar` de
novo** em todo host onde o Orquestra já estiver instalado.

⚠️ **Ordem de precedência:** `<fonte-local>` é sempre o clone detached e limpo do SHA remoto
aprovado no passo 0. Se o verificador do Codex não bater, leia o `tipo:caminho` e reconcilie contra
esse clone; nunca troque a referência por cache Claude, nunca presuma corrupção do host e nunca faça
bump apenas porque o exit foi `1`.

## Registrar

Terminado (mesmo que parcial), e **se este projeto tiver `memory/`**, registre em
`memory/fixes-history.md` o que foi instalado, em qual host, e o resultado das verificações acima.
Achado novo (ex.: o diretório que o host auto-descobre não existe e o fallback foi outro) vai em
`memory/gotchas.md` deste mesmo projeto, se existir. Sem `memory/` neste projeto, não invente onde
gravar: relate o resultado ao dono diretamente na resposta.

## Regras

- **Nunca instale sem o "pode instalar" explícito** — mostrar o comando não é o mesmo que ter
  autorização para rodá-lo.
- **Nunca** hardcode caminho desta máquina — a fonte (e a fonte local resolvida) vêm sempre do
  passo 0.
- **Nunca** use `-y`/`--auto`/`--yolo` em comando nenhum mostrado aqui.
- Falhou? Mostre o erro real e pare esse host — não invente rota alternativa por conta própria.
