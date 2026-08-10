---
description: Instala o próprio plugin Orquestra nos hosts alternativos do dono — Codex e Kimi — a partir da mesma fonte já registrada no Claude Code; confere Claude sem reinstalar
argument-hint: "[codex | kimi | claude — sem argumento, avalia os três e propõe o que falta]"
---

O `/orq:init` instala o Orquestra **neste projeto** (memória, board, elenco). Este comando é outro:
instala **o plugin em si**, escopo de usuário, nos hosts alternativos que o dono usa como motor
principal — Codex e Kimi. Decisão do dono: o que roda fora do Claude Code é **o mesmo plugin**, não
uma cópia adaptada — por isso não há "instalador" com lógica própria por host, só o mecanismo que
cada CLI já aceita.

⚠️ **Você não instala nada sem o "pode instalar" explícito.** Mostre os comandos exatos e o que cada
um faz; só rode depois da confirmação — mesma regra do `/orq:stack`. Sem argumento, avalie os três
hosts e proponha; com um host nomeado, vá direto nele.

## 0. Descobrir a fonte — nunca hardcode caminho desta máquina

```bash
claude plugin marketplace list
```

Ache a linha do marketplace `orquestra` e leia a `Source`:
- `Directory (<caminho>)` → clone local de desenvolvimento; use esse caminho como `<fonte>` **e**
  como `<fonte-local>` abaixo — já é um diretório real, serve pra tudo.
- referência remota (ex.: `brunocangussu/byia-claude-orquestra`) → use essa referência como
  `<fonte>` só onde for pedida literalmente (`codex plugin marketplace add <fonte>` aceita a
  referência como está). **Não é caminho de filesystem** — os passos que leem arquivo do disco (as
  cópias do Kimi, e a conferência `diff -rq` do Codex) precisam de um diretório real: resolva
  `<fonte-local>` antes de chegar neles, nesta ordem:
  1. O Claude **já baixou** o conteúdo do plugin — `ls ~/.claude/plugins/cache/orquestra/orq/` e
     cruze com `claude plugin list` (mostra a versão **de fato** instalada) antes de escolher a
     pasta: o cache pode ter mais de uma versão coexistindo, algumas órfãs (`.orphaned_at`), e o
     `ls` sozinho não distingue qual está ativa. Esse caminho **já É** a pasta `orq/` (o cache
     guarda só o conteúdo do plugin, sem repositório em volta) — use-o como `<fonte-local>/orq`
     diretamente, **sem** acrescentar outro `/orq`, em todo comando abaixo.
  2. Sem esse cache nesta máquina (nunca foi instalado por aqui): clone a referência para um
     diretório temporário — `git clone https://github.com/<referência> <tmp>` — e use `<tmp>` como
     `<fonte-local>` (aí `<fonte-local>/orq` existe, igual ao caso `Directory`).

A fonte que o Claude já usa é a única verdade disponível sobre onde este plugin vive nesta máquina —
não presuma um caminho.

## Claude — já instalado, só confere

Vale quando você **é** o Claude Code — identifique pelo host, não pelo caminho deste arquivo: com
`commands/` agora copiado para os outros hosts (seções abaixo), este mesmo texto também é lido pelo
Codex e pelo Kimi. Sendo Claude, não reinstale: **não invoque `/orq:stack`** — você não roda
slash command de dentro de outro comando (mesma regra do `/orq:init`, seção "Stack complementar").
Em vez disso, leia `${CLAUDE_PLUGIN_ROOT}/commands/stack.md`, seção "Plugin: versão E conteúdo
(nunca conclua de fonte única)", e aplique o passo a passo de lá — é a checagem que decide se o
cache está em dia, e não deve ser duplicada aqui.

## Codex

```bash
codex plugin marketplace add <fonte>
codex plugin add orq@orquestra
```

Verificação:
```bash
codex plugin list                                                            # orq: installed, enabled
diff -rq ~/.codex/plugins/cache/orquestra/orq/<versão>/ <fonte-local>/orq/    # tem que voltar vazio
```

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

Reversão (mecanismo comprovado limpo — instala, confere e remove sem sobra):
`codex plugin remove orq@orquestra` + `codex plugin marketplace remove orquestra`.

**Não prometa mais do que foi comprovado**: o que o Codex efetivamente *ativa* do plugin instalado
numa sessão viva (skill? gatilho por frase? commands? agents?) só se sabe testando ao vivo — isto
aqui instala e confere que o conteúdo bateu, não substitui abrir uma sessão e conversar. Se `codex`
não responder no PATH, não conclua ausência: instaladores escrevem em `.zshrc`, que só alcança shell
aberto depois de reabrir o terminal — o mesmo cuidado vale para o `kimi` abaixo.

## Kimi

O Kimi **não tem subcomando de instalação de plugin** (o `--help` não lista nada de plugin/install —
só `migrate`/`upgrade` do próprio CLI). Instalar é copiar para os diretórios que ele auto-descobre.

**Copiar só a skill não entrega o framework completo**: a `SKILL.md` roteia intenção para comandos
`/orq:*` que só existem como tal no Claude Code. Por isso o Kimi recebe também os arquivos de
procedimento (comandos, scripts, o catálogo de stack) lado a lado com a skill, no mesmo diretório —
a `SKILL.md` já sabe (seção "Interface NATURAL") ler `commands/<nome>.md` ali dentro quando o
comando não existe como tal:

```bash
mkdir -p ~/.agents/skills/orq/commands ~/.agents/skills/orq/scripts ~/.kimi-code/agents
cp -r <fonte-local>/orq/skills/orq/. ~/.agents/skills/orq/
cp -r <fonte-local>/orq/commands/. ~/.agents/skills/orq/commands/
cp -r <fonte-local>/orq/scripts/. ~/.agents/skills/orq/scripts/
cp <fonte-local>/orq/stack.md ~/.agents/skills/orq/stack.md
cp <fonte-local>/orq/agents/*.md ~/.kimi-code/agents/
```

`cp -r <origem>/. <destino>/` (o `/.` no fim copia o **conteúdo**, não a pasta) — reinstalar depois
de um release não aninha (`~/.agents/skills/orq/orq/…`), só atualiza os arquivos no lugar; mas
**não apaga** o que a release nova removeu ou renomeou lá, e a verificação abaixo acusa isso como
`Only in <destino>` — apague esse arquivo (ou rode `rm -rf <destino>` antes de copiar, pra espelho
limpo).

Verificação:
```bash
diff -q  ~/.agents/skills/orq/SKILL.md  <fonte-local>/orq/skills/orq/SKILL.md   # vazio
diff -rq ~/.agents/skills/orq/commands/ <fonte-local>/orq/commands/             # vazio
diff -rq ~/.agents/skills/orq/scripts/  <fonte-local>/orq/scripts/             # vazio
diff -q  ~/.agents/skills/orq/stack.md  <fonte-local>/orq/stack.md             # vazio
for f in <fonte-local>/orq/agents/*.md; do
  diff -q "$f" ~/.kimi-code/agents/"$(basename "$f")"                          # arquivo a arquivo
done
```

`~/.kimi-code/agents/` é **compartilhado** com qualquer outro agente que o dono já tenha aí — por
isso a última verificação compara arquivo a arquivo (`orq-planner.md`, `orq-implementer.md`…),
nunca `diff -rq` do diretório inteiro contra `<fonte-local>/orq/agents/`, que acusaria divergência
falsa no dia em que houver mais alguma coisa ali. O diretório em si é **hipótese, não confirmada**:
o binário cita o equivalente por diretório de projeto por strings, mas o diretório de usuário nunca
foi exercitado vivo. Depois de copiar, rode uma fumaça fora de qualquer projeto, sem `-y`:

```bash
KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")
"$KIMI" -p "onde paramos?" --output-format text < /dev/null
```

A skill `orq` aparece no índice da sessão? Se `~/.kimi-code/agents/` não for descoberto, caia no
fallback: `--agent-file` apontando pro arquivo do papel, ou `.kimi-code/agents/` **dentro do
projeto** em vez do diretório de usuário — registre qual funcionou (seção "Registrar" abaixo).

Reversão: `rm -rf ~/.agents/skills/orq` (pasta dedicada ao Orquestra, segura de apagar inteira); em
`~/.kimi-code/agents/`, remova só os `orq-*.md` que este comando copiou — **não apague o diretório
inteiro**, ele é compartilhado.

⚠️ **Escrita no Kimi como host segue condicionada** a um hook `PreToolUse` testado **vivo** negando
um `git checkout` de verdade — os hooks do Kimi são fail-open, "configurei" não é "funciona". Sem
esse teste passar, o Kimi fica só leitura/planejamento, aqui e como implementer remoto.

## O gotcha que atravessa os três hosts

Cache indexado por versão vale para **Claude e Codex**, comprovado nos dois: editar `orq/` sem
bumpar não muda o que roda, e nenhum `plugin list` acusa. **Release novo → rode `/orq:instalar` de
novo** em todo host onde o Orquestra já estiver instalado. No Kimi a cópia é um snapshot sem
versionamento — sem re-rodar depois de um release, ela fica velha e nada avisa.

⚠️ **Ordem de precedência quando `<fonte-local>` veio do cache do Claude (fonte remota, passo 0):**
se o `diff -rq` do Codex ou do Kimi não bater, confira **primeiro** se esse cache está desatualizado
— rode a seção "Claude" acima de novo antes de suspeitar do host que você acabou de instalar; o
desatualizado costuma ser a referência velha, não o host novo corrompido, e presumir "corrompido"
leva a reinstalar em loop atrás da referência errada.

## Registrar

Terminado (mesmo que parcial), e **se este projeto tiver `memory/`**, registre em
`memory/fixes-history.md` o que foi instalado, em qual host, e o resultado das verificações acima.
Achado novo (ex.: `~/.kimi-code/agents/` não existe e o fallback foi outro) vai em
`memory/gotchas.md` deste mesmo projeto, se existir. Sem `memory/` neste projeto, não invente onde
gravar: relate o resultado ao dono diretamente na resposta.

## Regras

- **Nunca instale sem o "pode instalar" explícito** — mostrar o comando não é o mesmo que ter
  autorização para rodá-lo.
- **Nunca** hardcode caminho desta máquina — a fonte (e a fonte local resolvida) vêm sempre do
  passo 0.
- **Nunca** use `-y`/`--auto`/`--yolo` em comando nenhum do Kimi mostrado aqui.
- Falhou? Mostre o erro real e pare esse host — não invente rota alternativa por conta própria.
