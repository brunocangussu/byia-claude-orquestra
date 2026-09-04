# Gotchas — armadilhas que já custaram tempo

> Só entra aqui o que **já** causou erro ou desperdício. Não é lista de boas intenções.

---

### `diff -rq` cru acusa artefatos corretos gerados pelo host

Na instalação da 0.22.5, o núcleo dos caches bateu byte a byte com o clone limpo, mas o Claude
criou `.in_use` e o Codex criou `.codex-plugin/migrated-command-skills/`. O comando literal do
`instalar.md` acusou divergência mesmo com o pacote correto. Não ignore extras genericamente: a
correção futura (T-049) deve allowlistar somente esses caminhos de runtime e continuar falhando para
qualquer outro arquivo extra ou byte divergente.

### Revisor externo em foreground morre no teto de 10 min do shell — e parece falha do revisor

Em 2026-08-07 o painel dos três foi disparado assim, e Codex e Kimi voltaram **os dois** com
`Exit code 143 — Command timed out after 10m 0s`:

```bash
codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh -s read-only "<briefing>" < /dev/null
```

O comando estava **correto** — `< /dev/null` presente, flags na ordem certa. O que estourou foi o
teto do **chamador**: a ferramenta Bash do Claude Code tem máximo de 600 000 ms. Relançados com
`run_in_background: true`, os mesmos comandos entregaram 64 KB e 83 KB de parecer.

**Por que engana:** o sintoma ("os externos não voltaram") é idêntico ao de revisor que falhou, e o
`T-024` chegou a registrar "Codex e Kimi estouraram o tempo e voltaram parciais" atribuindo a causa
aos revisores. A causa é o chamador, e revisor com `reasoning_effort=xhigh` sobre diff de ~30 KB
passa de 10 minutos com folga.

→ **Revisor externo roda sempre em background**, com a saída redirecionada para arquivo; confira o
tamanho do arquivo antes de tratá-lo como parecer (51 bytes não é parecer).

---

### Renomear o plugin não renomeia as auto-referências

A v0.2.0 trocou `orquestra` por `orq` no pacote, mas os prompts continuaram mandando rodar
`/orquestra:plan-next` e ler a skill `orquestra`. Sobreviveu a **três releases** porque
`claude plugin validate --strict` valida o *manifesto*, não a coerência entre instruções.
→ Ao renomear qualquer comando, skill ou agente, faça `grep` do nome antigo no `orq/` inteiro.

### `claude plugin validate` não testa comportamento

Ele passa com um plugin cujas instruções se contradizem ou apontam pro nada. Validação verde ≠
plugin correto. O teste real é comportamental: rodar num projeto e ver se o Claude faz o esperado.

### Cron no Claude Code é *session-scoped*

Não existe execução realmente desacompanhada dentro do CLI. O modo noturno depende da sessão
**aberta** e da máquina ligada e sem suspender. Se a máquina dormir, o trabalho pausa.
→ Nunca prometer ao dono que algo "roda sozinho de madrugada".

### O `model:` no arquivo do agente é só padrão de fábrica

Quem manda é `memory/wiki/_elenco.md`. Comando que spawna sem ler o elenco antes ignora
silenciosamente a escalação escolhida pro projeto — e ninguém percebe, porque não dá erro.

### `manager` não é configurável pelo elenco

O Manager é a sessão principal, definida pelo `/model`. Tentar trocá-lo via `/orq:elenco` não faz
sentido e confunde — não é um spawn.

### `which kimi` falhar NÃO significa que o Kimi não está instalado

O instalador põe o binário em `~/.kimi-code/bin/kimi` e adiciona o diretório ao **`.zshrc`** — o que
só alcança shell aberto **depois**. Sessão já em curso não enxerga: `which kimi` falha **enquanto o
binário está lá, funcionando**.

Isso já produziu dois erros em cascata (2026-07-28): o agente global `kimi-revisor` parava dizendo
"não instalado" (comportamento correto, diagnóstico errado), e uma sessão irmã concluiu o mesmo e foi
procurar o pacote **no npm** — onde ele nunca esteve. Os `kimi`, `kimi-cli` e `kimi-code` do npm são
homônimos sem relação; instalar um deles no papel de revisor seria risco de supply chain de verdade.
A distribuição oficial é `code.kimi.com`, binário com checksum.

→ **Detecte com fallback, nunca só pelo PATH:**
`KIMI=$(command -v kimi || echo "$HOME/.kimi-code/bin/kimi")`
→ Nesta máquina há symlink em `~/.local/bin/kimi` (diretório já no PATH), então `kimi` solto resolve.
→ Igual ao Codex, o `< /dev/null` é obrigatório (sem TTY, bloqueia lendo stdin).

### O plugin do Codex não é invocável pelo modelo — só pelo dono

`codex:codex-rescue` **não aparece** como agent type disponível, e `/codex:review` tem
`disable-model-invocation: true`. Ou seja, a regra "use sempre o subagente, nunca o binário" só é
executável quando **o dono digita** o comando; de dentro de um turno do Claude, o único caminho é a
CLI (`codex exec … < /dev/null`). Verificado empiricamente em 2026-07-28.

> ⚠️ **Esta premissa venceu — não a cite como definitiva.** Desde 29/jul/2026 o
> `codex:codex-rescue` **aparece** na lista de agent types das sessões (reconfirmado em 30/jul).
> O que ficou desatualizado é só a *justificativa* do parágrafo acima, não necessariamente a
> escolha: `memory/wiki/_elenco.md` e `orq/commands/revisar.md` continuam instruindo a CLI direta,
> enquanto a regra global do dono (`~/.claude/CLAUDE.md`) manda **nunca** invocar o binário `codex`
> por Bash de dentro do Claude Code, para não perder o rastreamento de job. **Isso é decisão dele,
> não do Manager** — está registrado como card no board (`T-027`). Até ele decidir, o projeto segue
> como está, cientes de que é uma exceção à regra global, não uma impossibilidade técnica.

### Achado de revisor externo não se aplica cru — reconcilie

O Kimi apontou (corretamente) que o lint exigia crases para skill e não para agente. Apliquei a
"correção" tornando as crases opcionais → **três falsos positivos na hora**, porque "skill" é palavra
comum em prosa portuguesa ("a skill **e** o comando", "skill **ou** agente"). O prefixo `orq-` não
tem esse problema: não aparece em texto corrido.
→ A assimetria era **proposital** e o revisor não tinha como saber. Diagnóstico certo, correção
errada. Sempre teste a correção antes de aceitar — e falso positivo é o que faz lint ser desligado.

### Marketplace local ≠ plugin atualizado — editar o repo NÃO basta

O marketplace `orquestra` aponta para o **diretório** deste repo, o que dá a impressão de que editar
um arquivo já vale na hora. **Não vale.** O plugin instalado é uma **cópia em cache**
(`~/.claude/plugins/cache/orquestra/orq/<versão>/`), e ela só muda com:

```bash
claude plugin marketplace update orquestra
claude plugin update orq@orquestra          # copia para o cache — teste válido só após restart
claude plugin list                          # confirma versão e escopo
```

Foi assim que a máquina do dono ficou usando a **0.4.0 em todos os outros projetos** enquanto o repo
já estava na 0.7.0 — sete releases de diferença, sem nenhum sinal. Testar comportamento sem atualizar
testa a versão errada.

### `claude plugin` TEM install/update/marketplace — não conclua por `--help | head`

Em 2026-07-27 eu rodei `claude plugin --help | head -20`, vi a lista alfabética parar em `help` e
concluí que a CLI **não tinha** `install` nem `marketplace add`. Escrevi isso como fato no
`/orq:stack` e no `init`, mandando "entregar o comando pro dono colar". **Era falso** — a lista
continuava em `install`, `list`, `marketplace`, `prune`, `tag`, `uninstall`, `update`, `validate`.
→ Nunca conclua ausência a partir de saída truncada. `head` corta; a ausência precisa ser verificada
no comando específico (`claude plugin update --help`).

### Board fora do formato = statusline muda, sem erro nenhum

`kanban-status.sh` casa `/^- \[.\]/` e lê o título **por posição** (entre a crase do ID e o travessão).
Um card escrito como `` - `[!]` **T-001 · Título** `` não casa — e o script **sai em silêncio**, sem
mensagem, sem código de erro. O board parece perfeito e o progresso simplesmente nunca aparece.

Aconteceu na primeira instalação em projeto de terceiro (2026-07-27): a LLM escreveu o board com o
marcador dentro de crases e só descobriu porque testou por conta própria — o `/orq:init` não mandava
testar. A causa é estrutural: **produtor e consumidor não compartilhavam especificação.**
→ O contrato agora vive em `memory/wiki/_schema.md`, o `init` cria esse arquivo e a FASE 5 exige
smoke test com saída não-vazia.

### Nome de agente do projeto nunca deve colidir com o do plugin

Os cinco `orq-*` vêm do plugin. Criar `.claude/agents/orq-planner.md` no projeto tem resolução
**indefinida** — pode sobrescrever, pode duplicar na lista, pode variar. Papel adicional usa nome
próprio (`dados`, `infra`, `frontend`).

### `codex exec` trava esperando stdin — sempre feche com `< /dev/null`

**Causa raiz (diagnosticada em 2026-07-26, card `T-010`).** Sem TTY — que é o caso dentro do Bash tool
do Claude Code — o `codex exec` imprime `Reading additional input from stdin...` e **bloqueia até o
timeout**, mesmo com o prompt passado como argumento. Não é lentidão, não é o modelo, não é o tamanho
do briefing: é o stdin que nunca fecha.

```bash
codex exec -s read-only "..." < /dev/null      # responde em segundos
codex exec -s read-only "..."                  # trava até o timeout
```

Custou duas tentativas de 10 e 3 minutos, e a hipótese errada de "poluição de contexto do ambiente do
Codex" — o que se via era só a sessão pendurada.

### Subagente spawnado COM `name` não devolve resultado

Com `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` no ambiente, passar `name` no spawn transforma o agente
em **teammate endereçável**: ele fica vivo emitindo `idle_notification` e **nunca retorna o parecer**.
Sem `name`, o mesmo agente com o mesmo prompt entregou em 231 s.
→ Revisor, planner, implementer e docs: **spawnar sem `name`**. Nome só para agente com quem você
realmente vai conversar em várias rodadas.

### Painel parcial nunca vira "consenso"

Se um revisor do painel não entregar, **diga ao dono que o painel foi parcial**. Nunca apresente
parecer de um revisor como se fosse a interseção de dois — o valor do painel está justamente em
confirmado-por-dois vs. achado-por-um.

### Lint de coerência não pode varrer `memory/`

O log é append-only e o `gotchas.md` citam nomes de comandos **que deixaram de existir**, de propósito,
ao descrever bugs passados. Um lint ingênuo acusa isso como referência quebrada em todo checkpoint —
e lint que dá falso positivo é lint que o dono desliga.

### Agent teams são experimentais

Mais caros e **não** isolam arquivos automaticamente. Dois agentes escrevendo no mesmo checkout dá
conflito. Tarefa que escreve → worktree próprio.

## Revisor externo sem sandbox escreve no repo vivo — e a instrução não segura

**Custou:** o working tree inteiro da 0.11.0, em 2026-07-28. Recuperado, mas com perda.

O Kimi foi spawnado como revisor **read-only**, com "não edite arquivo nenhum, apenas relate" no
prompt. No meio da revisão ele rodou `git checkout -- .` e descartou 16 arquivos de mudança não
commitada. Restaurou sozinho e avisou — mas o replay perdeu os marcadores de estado dos cards,
porque edições feitas por script não ficam no transcript de onde ele reconstruiu.

**Efeito colateral que quase virou conclusão errada:** o revisor interno, rodando em paralelo,
relatou "o working tree mudou três vezes" e "metade das correções não está em disco". Parecia
alucinação — era descrição fiel do repo sendo destruído e remontado. O Manager atribuiu a worktree
e errou. **Relato estranho de um revisor pode ser sintoma, não defeito do revisor.**

**O que dói:** `_elenco.md` e `revisar.md` **já avisavam** — "o Kimi não tem flag de sandbox como o
`-s read-only` do Codex; garantia dura só em worktree descartável". A instrução estava escrita,
estava correta, e não impediu nada. Só o Codex tem sandbox de verdade (`-s read-only`).

**Regra:** revisor externo sem flag de sandbox **não olha o repo vivo**. Worktree descartável ou
clone. Prompt não é permissão negada — é pedido educado.

## `git diff` esconde arquivo NOVO — e o painel de revisão revisa o vazio

**Pago em 2026-08-04, na 0.18.0.** O painel roda sobre um patch (`git diff > x.patch` + `git apply`
num worktree descartável). Arquivo novo é **untracked**, e `git diff` **não inclui untracked** — o
worktree do revisor externo nasceu sem `orq/commands/instalar.md`, que era **a peça central da
release**. O revisor reprovou com um bloqueador correto para o que via, e a premissa é que estava
furada.

**Sempre `git add -N .` antes de gerar o patch do painel.** Vale para toda release que cria arquivo
— e um comando novo é exatamente isso.

**Como apareceu:** o revisor foi **conferir se o arquivo existia** (`ls`, `git status -uall`) em vez
de assumir. Nenhum gate pegaria: `validate` e `lint` rodam no repo real, onde o arquivo está.

## Guarda mecânico prova ausência de STRING, não ausência de REGRA

**Pago em 2026-08-04, na 0.17.0.** O critério de aceite do A1 era `grep "Teto:" orq/` retornar 1
ocorrência — e retornou. A regra **sobreviveu mesmo assim**, em `SKILL.md:207`, escrita como
*"propõe **1×** o resto"*. O `grep` procurava uma redação; o defeito estava em outra.

Foram **cinco reincidências** do mesmo defeito, cada uma com redação diferente
(`"proponha 1× por bloco"` · `"propõe 1× o resto"` · `"(a unidade do teto do N2)"` ·
`"até o fim do bloco"` · `"insistir sem a condição ter piorado"`).

**Critério de aceite baseado em `grep` precisa vir acompanhado de leitura humana ou de revisor.**
A quinta só apareceu na releitura manual do Manager, depois de dois gates verdes e do `grep` limpo.

## Ao acrescentar cláusula a uma regra, a frase que a RESUME é sempre suspeita

**Corolário do anterior.** Toda regra tem uma frase de fecho que a resume ("o que o teto proíbe
é…"). Ao acrescentar uma cláusula nova, **essa frase foi escrita para a versão anterior** e passa a
contradizer a cláusula que você acabou de adicionar. Foi exatamente a quinta reincidência.

## `claude -p` como revisor externo NÃO lê arquivos — o briefing tem que carregar o conteúdo

**Pago em 2026-08-05, no primeiro painel cross-vendor com o Codex como host.** O Codex precisava do
Opus 5 revisando e montou a invocação sozinho (sem ter a linha na tabela — iniciativa correta dele).
Três atritos, nesta ordem:

1. **`--tools 'Read,Grep,Glob'` engole o prompt.** A flag é variádica, então o argumento seguinte
   virou item da lista de ferramentas: *"Input must be provided either through stdin or as a prompt
   argument"*. Ponha o prompt **antes** das flags, ou passe por stdin.
2. **Com ferramentas habilitadas, `claude -p` pendura.** Mais de 2 min sem um byte de saída, duas
   vezes. Autenticação válida (`Max`), modelo válido — não era login.
3. **Sem ferramentas, o Opus se recusa a revisar — e está CERTO.** Ele respondeu que não tinha
   `Read`/`Grep`/`Glob` e que **não inventaria `arquivo:linha`**. Recusa é o comportamento correto de
   um revisor sem evidência.

**A assimetria que isso revela, e ela importa para o `T-026`:** `codex exec -s read-only` e
`kimi -p` **leem o repositório sozinhos**. O `claude -p` invocado de dentro de outro agente, **não**.

**Forma que funcionou:**
```bash
claude -p '<briefing COM o conteúdo verbatim, numerado por linha>' \
  --model opus --permission-mode plan --tools '' \
  --setting-sources '' --disable-slash-commands --no-session-persistence < /dev/null
```

⚠️ **E um cuidado de método:** quando o revisor demora, a tentação é mandar *"não verifique mais
nada, emita o parecer agora"*. Foi o que destravou — mas **o veredito que sai daí vale menos**: é
parecer sobre o texto colado, não sobre o estado do repositório. Quem reconcilia tem que dizer isso
com todas as letras, senão um APROVADO forçado entra no board com peso que não tem.

## Ordem das flags derruba o revisor em silêncio — no Claude e no Kimi, por causas diferentes

**Pago duas vezes no mesmo dia, 2026-08-05, com CLIs diferentes.** (O Codex apareceu como chamador
no incidente 1, mas nunca falhou por ordem de flag — não é o terceiro caso, é o mesmo `claude -p`.)

1. **Codex chamando o Claude:** `claude -p '<prompt>' --tools 'Read,Grep,Glob'` → a flag `--tools`
   é **variádica** e engoliu o que vinha depois; erro real: *"Input must be provided either through
   stdin or as a prompt argument"*.
2. **Manager chamando o Kimi:** `kimi -p -m kimi-code/k3 '<prompt>'` → o `-p` **aceita valor**,
   então consumiu o `-m`, e o nome do modelo virou comando posicional; erro real:
   *"unknown command 'kimi-code/k3'"*.

**Forma segura, por CLI — não generalizável (a causa é oposta em cada um):**
- `claude`: prompt **antes** das flags — `claude -p '<prompt>' --tools '...'` (nunca o inverso).
- `kimi`: configuração primeiro, `-p` por último —
  `kimi -m <modelo> --output-format text -p '<prompt>' < /dev/null`.

⚠️ **O que torna isto perigoso não é o erro — é o silêncio depois dele.** Um revisor que não roda
devolve arquivo vazio, e quem reconcilia pode reportar "não achou nada" em vez de "não rodou". São
coisas opostas. **Depois de invocar revisor externo, confira o tamanho e o conteúdo da saída antes
de tratá-la como parecer** — `wc -c` e um `grep` pelo formato exigido bastam.

## Correção que ACRESCENTA em vez de SUBSTITUIR mantém a afirmação falsa viva

**Sétima ocorrência da família em duas semanas, pega em 2026-08-05 na releitura manual do Manager —
depois de gates verdes e de um painel de três aprovar a rodada.**

O review apontou que a garantia *"uma janela Codex nunca muda o que uma janela Claude lê"* era falsa,
porque o `/orq:elenco` grava no arquivo. A correção **acrescentou** a regra certa (*"o `/orq:elenco`
só escreve a tabela do host Claude"*) **no mesmo parágrafo, sem remover a promessa absoluta**.

Resultado: duas frases vizinhas se contradizendo — *"nenhum comando reescreve nada aqui"* seguido de
*"o `/orq:elenco` escreve…"*.

**A regra que sai daqui:** ao corrigir uma afirmação falsa, **localize e reescreva a afirmação**, não
escreva a verdade ao lado dela. Frase acrescentada não revoga frase anterior — para um leitor, as
duas valem, e ele escolhe a que vier primeiro.

**Sintoma para procurar em review:** um parágrafo onde uma frase promete um absoluto ("nunca",
"nenhum") e outra, perto, descreve a exceção. Se a exceção é verdadeira, o absoluto está errado.

### Em configuração com precedência, ADICIONAR é sobrescrever

`.claude/settings.json` do projeto **vence** `~/.claude/settings.json`. Gravar uma chave nova no
projeto **desliga** o comportamento global sem tocar em arquivo nenhum do usuário — o diff é
`+N -0`, aditivo, e nenhuma verificação do tipo "sobrescrevi algum arquivo?" acusa. Foi assim que o
`/orq:init` anulou a statusline do dono em dois projetos (2026-08-08, `T-036`).
→ Ao instruir gravação em settings: **diga em qual escopo checar**, e trate "existe no global" como
"já existe". Precedência: Local > Projeto > Usuário.

### Varredura rasa devolve falso negativo com cara de conclusão

Procurando projetos afetados, uma varredura de **1 nível** (`~/Projetos DEV - Cursor/*/`) devolveu
"só um projeto". O dono falou em "projetos", no plural, e insistiu; a varredura de **6 níveis** achou
o segundo — com a chave já **commitada**. (2026-08-08)
→ Ao afirmar "só X está afetado", diga **qual foi o alcance da busca**. Sem isso, "não achei" vira
"não existe".

### `[ -x ]` é guarda falso para script invocado via `sh`

`sh script.sh` **não exige** o bit de execução. Um guarda `[ -x "$script" ]` antes de `sh "$script"`
reprova arquivo perfeitamente utilizável — e o modo 644, que qualquer Write de LLM produz, passa a
zerar a saída. No `T-036` isso deixava a barra **completamente vazia** quando faltava `jq`.
→ Use `[ -r ]` para o que vai ser lido por um interpretador; `[ -x ]` só para o que é executado
diretamente. **E não documente o sintoma como se fosse lei da natureza** — foi o que o texto fez,
criando um item de smoke para um defeito de uma linha.

### `jq '…' arquivo > arquivo` trunca o arquivo para zero byte

O shell abre o redirecionamento **antes** de o `jq` ler. É a forma que qualquer executor escreve
primeiro, e destrói exatamente o que uma instrução de "mescle, não sobrescreva" existe para
proteger.
→ Instrução que manda mesclar JSON **tem que dar o comando seguro**: `> tmp && mv tmp arquivo`.
E preservar o modo do arquivo original — o `mv` do temporário traz a permissão do umask, o que pode
**abrir** um settings que estava restrito.

### Interpolar dado dentro do programa do `awk` é execução arbitrária

`awk "BEGIN { printf \"%.2f\", $var }"` põe `$var` no **código**, não nos dados. Com um valor
malicioso vindo do stdin, o `awk` executa. Provado com PoC no `T-036` (2026-08-08).
→ `awk -v c="$var" 'BEGIN { printf "%.2f", c+0 }'`. Vale para qualquer interpolação em `awk`, `sed`
ou `eval`.

### `jq '…' arquivo > arquivo` trunca o arquivo para 0 byte — e settings vazio faz o merge falhar calado

Duas faces do mesmo buraco, as duas provadas por revisor executando (2026-08-09, `T-036`):
- o shell abre o redirecionamento **antes** de o `jq` ler → o arquivo vira 0 byte. É a forma que
  qualquer executor escreve primeiro. Use `> tmp && mv tmp arquivo`, **preservando o modo**;
- `jq` **sem entrada** devolve **0 bytes com exit 0**; validar o temporário com `jq .` também sai 0;
  o `mv` conclui; e a chave **nunca é gravada**. Instalação relatada como sucesso, efeito zero.
→ Antes de mesclar JSON: exigir arquivo **não vazio** (`test -s`) **e raiz objeto**
(`jq -e 'type == "object"'`). Vazio, `null`, lista ou malformado → **abortar e relatar**.

### Guarda que reprova o caminho feliz vira alarme ignorado — e isso reincidiu 3× no mesmo card

Padrão observado no `T-036`: a verificação existe, funciona, e acusa falha numa situação **correta**
— recusa legítima do dono, folha que por desenho não escreve, `jq` ausente num ramo criado para
máquinas sem `jq`. O executor aprende a ignorar o item inteiro, e quando a falha for real ela some
no ruído. É a mesma doença que o comentário do `kanban-status.sh` já documentava.
→ Toda asserção nova precisa da pergunta: **em que caminho correto isto fica vermelho?** Se houver
um, ele vira exceção nomeada — não observação em prosa.

### `grep` vazio não prova ausência quando o arquivo está staged no índice do git

Ao remover `orq/compor-statusline.md`, o `grep -rn` no diretório voltou vazio e eu reportei "resíduo
limpo". O arquivo continuava **no índice**, como blob vazio (`e69de29`) — teria entrado no commit,
e nem o lint nem o `validate` olham para o índice. (2026-08-09)
→ Antes de fechar release que **removeu** arquivo: `git ls-files --stage | grep <nome>` tem que
voltar vazio. `git rm --cached` resolve.

### Marketplace local do Codex copia o DISCO, não o commit

`~/.codex/plugins/cache/orquestra/` vem do marketplace `orquestra`, que aponta para **a pasta do
projeto**. Um `codex plugin add` copia o working tree **como estiver** — inclusive trabalho não
commitado e não revisado. Em 2026-08-08 o Codex ficou com uma "0.20.0" tirada do meio de uma sessão,
que tinha reprovado em três rodadas de painel. E como o cache é indexado **por versão**, atualizar
depois **não troca nada**: mesmo rótulo, conteúdo velho.
→ Para consertar: apagar `~/.codex/plugins/cache/orquestra/orq/<versão>/` e reinstalar. Para
prevenir: só instalar noutro host **depois** do commit.

### Migração de memória com PII não pode passar por Codex nem Kimi

Projeto com dado de paciente (`Bruno Vascular`): ler e reescrever os arquivos de memória **é** enviar
o conteúdo ao modelo. Codex (OpenAI) e Kimi (Moonshot) são transferência internacional — a regra do
dono proíbe. (2026-08-09)
→ Host padrão pode ser o Codex para o **produto** (código e instruções). Projeto com PII fica em
host Anthropic, e isso vale como regra permanente daquele projeto, não exceção pontual.

### Guarda que prova a string, não a regra — a família mais recorrente do lint

Apareceu **quatro vezes** no `T-051` (2026-09-01), sempre com o mesmo formato: a checagem confirma que
um texto existe **em algum lugar** quando a regra exige que ele exista **num lugar específico**.
Casos reais, todos com probe que passava verde: `heading not in texto` aceitando `### Host Codex
antigo` como se fosse `### Host Codex` · papel obrigatório sobrevivendo nos presets depois de sumir da
tabela do host · papel trocado por intruso com a contagem mantida e o nome citado numa **nota fora da
tabela** · versão nova aparecendo só numa linha de changelog enquanto o bloco `## Status` anunciava a
anterior — justamente o defeito que aquele guarda existe para pegar.
→ Guarda de posição extrai **a célula/linha exata** e compara conjunto **e multiplicidade**; nunca
`x in texto`. E heading duplicado tem que **reprovar por ambiguidade**, não ser concatenado nem
resolvido pelo primeiro. Ao consertar um caso, **varra a família inteira** — foi assim que dois
guardas extras apareceram.

### A frase-resumo continua contando a versão anterior da regra

Mudar uma regra em `orq/` conserta o normativo e deixa vivo o **resumo** dela em 4-6 outras
superfícies: `README.md`, `memory/wiki/_elenco.md`, `init.md`, `ajuda.md`, `stack.md`, e a própria
thread do plano. No `T-051`, **22 dos 25 bloqueadores** foram disto. Casos: a wiki dizendo *"plano
fechado rebaixa a faixa"* depois do piso de Alto risco existir; o `init` com regra própria de
migração recriando as duas fontes que o card acabara de eliminar; o README exibindo `codex xhigh`
num exemplo, violando o contrato escrito no comando ao lado.
→ Ao mudar uma regra, **caçar onde ela está resumida** antes de devolver. E: o **plano** também
envelhece — no `T-051` o bloqueador do `scout` nasceu de contradição dentro da própria thread
aprovada, que dizia as duas coisas em seções diferentes.

### Identificador de job fantasma — subagente que diz ter despachado e não despachou

2026-09-01: o subagente de revisão devolveu `task-mtivartx-7nfsa3` como se tivesse enfileirado o
trabalho. `codex-companion.mjs status --all` respondia **"No jobs recorded yet"** — a revisão nunca
existiu. Aceitar o identificador como prova teria reportado ao dono uma revisão que não aconteceu.
→ Identificador não é resultado. Conferir no runtime (`status`/`result`) antes de contar como feito;
sem job registrado, é **revisão degradada declarada**, nunca silêncio. O `adversarial-review` do
companion, com saída redirecionada para arquivo, é a via confiável — a saída em background chega
**truncada** e perde o começo do parecer.

### Probe do Manager que falha por erro do Manager

2026-09-01: rodei o probe do papel intruso trocando `` | `implementer·leve` `` — mas a tabela escreve
sem crases, então o `sed` não casou e o lint passou verde. Quase reportei que o guarda estava furado;
teria mandado "consertar" um guarda que funcionava, e a correção provavelmente quebraria algo.
→ Verificar que a **injeção do probe aconteceu** (`MUDOU? True`) antes de interpretar o resultado.
Probe que não altera o arquivo prova exatamente nada.

### Modelo novo no menu não significa modelo disponível — confira o cache, não a documentação

2026-09-01: o menu do Claude Code passou a listar **Fable 5.1**, e eu concluí, a partir do texto do
`claude --help` (*"an alias for the latest model"*), que o alias `fable` já o estaria usando. **Errado.**
O `~/.claude.json` → `additionalModelOptionsCache` mostrava a verdade: `{"value":
"cc-update-required-1", "label": "Fable 5.1 (disabled)", "description": "Update to 2.1.255+ to use
Fable 5.1", "disabled": true}` — o item aparece no menu, o `value` é um **sentinela de update**, e o
CLI local era 2.1.246. O alias resolvia para `claude-fable-5[1m]`, o Fable 5.
**Desfecho (mesmo dia, após `claude update`):** com o CLI em **2.1.258**, o cache passou a ter uma
entrada só — `{"value": "claude-fable-5-1[1m]", "label": "Fable"}` — e o alias `fable` passou a
resolver o 5.1 **sozinho**, sem tocar no produto. A regra do alias estava certa; errada estava a
afirmação sobre aquela máquina naquele momento.
→ A regra "alias = mais recente" só vale entre os modelos que **aquela instalação alcança**. Antes de
afirmar qual modelo está em uso, ler `additionalModelOptionsCache` — o `--help` descreve a intenção,
o cache descreve o estado. Gotcha irmão do que já vale para o plugin: **documentação não é evidência
de comportamento**.

### Grep que "confirma" o que você acabou de escrever

No mesmo episódio: `grep -rl 'Fable 5.1' ~/.claude/` retornou vários arquivos e por um instante
pareceu confirmação. Eram os **transcripts desta própria conversa** (o `.jsonl` da sessão, os
`events.md` do context-mode, backups tocados no mesmo minuto) — texto que eu tinha escrito minutos
antes.
→ Ao buscar evidência no disco, verificar **a origem do match** antes de contá-lo como prova.
Transcript de sessão, log de memória e cache de conversa refletem o que foi dito, não o que é.

### `.DS_Store` na pasta de trabalho reprova o verificador de cache

2026-09-02: o lint reprovou com `versão 0.25.0 diverge do cache instalado (missing:.DS_Store)` logo
depois de um release verificado com sucesso. Causa: o Finder criou `orq/.DS_Store` (0 bytes) na
pasta local. Ele está no `.gitignore` e **nunca foi commitado**, mas o verificador compara a **pasta
de trabalho** com o cache — e `missing` significa *existe na fonte, falta no instalado*. O cache
estava correto; a fonte é que tinha lixo. Por isso a verificação contra **clone limpo** passava e a
mesma verificação contra o working tree falhava.
→ `rm -f orq/.DS_Store` resolve. E é a razão de o `T-049` ter deixado `.DS_Store` **estrito**, fora
da allowlist instalada-only: permitir mascararia divergência real. Prova de release usa **fonte
limpa** (clone detached do SHA publicado), nunca o working tree — o lint local usa a pasta e por isso
acusa lixo que o clone não tem.

### `find` (e outros comandos) podem voltar filtrados — confirme com `ls` antes de concluir

No mesmo episódio: `find orq/ -name ".DS_Store"` respondeu como se não houvesse nada, e eu quase
concluí que o arquivo estava do outro lado. `ls -la orq/.DS_Store` mostrou o arquivo na hora.
→ Quando um comando de busca "não acha" algo que o erro afirma existir, **confirme por outro
caminho** antes de inverter a hipótese. Vale a mesma regra do probe que não injetou: resultado de
ferramenta não é evidência até você saber que a ferramenta olhou onde você acha que olhou.

### Reescrever página viva pode apagar contrato que um TESTE exige

2026-09-02: a reescrita do `arquitetura.md` (229 → 388 linhas, para virar página de consulta) removeu
três termos da seção do guardião — `clear_required`, `falha de persistência` e `additionalContext`.
Eles não são prosa: `test_context_guard.py::test_guard_contract_is_present_in_live_instructions`
**exige** cada um, nesta página e no `README.md`. A suíte reprovou; os outros dois gates passaram
verdes, porque `validate` lê manifesto e o lint confere referências, não contrato semântico.
→ Antes de reescrever página viva, **rode a suíte depois** — não só o lint. E o diagnóstico do
subagente atribuiu a falha a um `.DS_Store` no ambiente; era outra coisa. **Ler o traceback antes de
aceitar a causa relatada**: teste isolado passando e suíte falhando quase nunca é ambiente.

## Encolher o card do board pode quebrar um consumidor automático — 2026-09-02

**O que aconteceu.** A migração do `T-056` moveu a nota longa de 31 cards para as threads. A nota do
`T-042` citava a release alvo `0.23.0`; foi junto. A suíte caiu no mesmo instante:
`ContextGuardReleaseVersionTest.test_release_version_is_coordinated` lê a **linha do card** e exige
que `0.23.0` esteja lá, para provar que card e plano estão coordenados.

**A lição.** O board não é lido só por gente. `trilha:`/`faixa:` são lidos por três comandos; a
release alvo, por um teste; `@frente`, pelo protocolo de várias janelas. **Antes de mover a nota de
um card, pergunte quem mais lê aquela linha.** A tabela do que nunca migra está em
`wiki/_schema.md`, seção "O que NUNCA migra para a thread".

**Por que valeu a pena mesmo assim.** O gate pegou na hora, e o custo foi repor 25 bytes na linha.
Sem a suíte, teria virado um teste-fantasma passando por ausência de dado.

## `awk length()` conta bytes ou caracteres conforme o locale — 2026-09-02

**Onde queima.** Qualquer teto medido em `awk`. Com `LANG` vazio ou `C`, `length()` conta bytes; com
locale UTF-8, conta caracteres. Board em português tem acento em quase toda linha: medindo este
board, **17 cards passavam de 200 contando code points e 21 contando bytes** — quatro cards ficavam
de lados opostos da mesma régua, e o mesmo arquivo passaria numa máquina e falharia noutra.

**O que fazer.** Fixe a unidade e force o locale onde ela é medida. No `kanban-status.sh` a
contagem do teto roda num passo separado com `LC_ALL=C`, **de propósito não no awk principal**: lá
`length(t)` trunca o título da statusline em 34, e sob `LC_ALL=C` isso cortaria emoji no meio.
Uma régua por finalidade, cada uma com o locale que ela precisa.

## Validação depois de efeito colateral não é validação — 2026-09-02

**O que aconteceu.** O script que migrava a nota do card escrevia na thread e **só depois** conferia
se a linha nova cabia no teto. O `T-036` estourou: a thread já tinha recebido a nota, o board não
tinha sido tocado, e o texto ficou duplicado. Nada se perdeu, mas o estado ficou inconsistente sem
ninguém avisar.

**A regra.** Valide tudo o que dá para validar **antes** da primeira escrita, e ordene os efeitos do
mais recuperável para o menos. Aqui: valida o teto → escreve na thread → só então reescreve o board.
Se a escrita da thread falhar, o board continua íntegro e a operação inteira pode ser repetida — e o
migrador ficou idempotente para que repetir não duplique.

## Verificador que reprova TUDO está quebrado, não o código — 2026-09-02

**O que aconteceu.** Escrevi um reconciliador para provar que as 48 notas migradas do board estavam
íntegras nas threads. Ele acusou **48 de 48 falhando**. O defeito era dele: o regex
`/^## Marca\n([\s\S]*?)(?=\n## |$)/gm` — com a flag `m`, o `$` do lookahead casa fim de **linha**,
não fim de string, então o não-guloso encerrava a seção na primeira quebra de linha. Conferido um
caso à mão, a nota batia 5027 de 5027 caracteres.

**A regra.** Reprovação universal é sinal de verificador quebrado, não de código quebrado —
especialmente quando outra checagem já passou. **Confira um caso à mão antes de agir sobre o próprio
alarme.** Custa um minuto e evita "consertar" o que estava certo. Corrigido, o resultado real foi
48/48 íntegras, na seção do próprio ID, sem duplicata nem órfã.

## Statusline que some com o sinal esconde a falha que devia mostrar — 2026-09-02

**O que aconteceu.** O contador de cards fora do teto (`📏`) roda num awk separado. Se esse awk
falhar, a variável fica vazia e o sinal simplesmente não aparece. Eu documentei isso como
*"fail-open de propósito"* — e a revisão externa mostrou o buraco: um board com dezenas de cards
fora do teto renderiza **exatamente igual** a um board limpo.

**A regra.** *"Não consegui medir"* e *"está tudo certo"* são estados diferentes e não podem
renderizar igual. Fail-open protege o prompt de quebrar; não autoriza mentir sobre o que foi
medido. Falha agora vira `📏?`, com teste que injeta a falha e exige o `?`.

## `\r` do CRLF conta como byte em qualquer teto medido por linha — 2026-09-02

**Onde queima.** Teto de tamanho por linha, medido em bytes. O `\r` do CRLF é byte e entra na conta:
um card de exatamente 240 bytes de conteúdo acende o alarme só porque o arquivo veio com CRLF. O
mesmo board reprova ou passa conforme quem o salvou — que é o oposto de ter uma régua.

**O que fazer.** `sub(/\r$/, "")` antes de medir. O teto mede o conteúdo, não como o arquivo foi
gravado. E o teste tem que ser de **fronteira exata com CRLF**, não só "linha gorda com CRLF": a
linha gorda acusa dos dois jeitos e não prova nada.

## Citar skill de OUTRO plugin com o padrão `` skill `nome` `` derruba o lint — 2026-09-02

**O que aconteceu.** Escrevi na `SKILL.md` que o gatilho de memória deve chamar *"a skill
`mem-search`"*. O lint reprovou: `` skill `mem-search` não existe ``. E **dois testes caíram junto** —
`test_main_ignores_in_use_in_installed_cache` e `test_main_ignores_top_level_orphaned_at_in_installed_cache`
rodam o lint inteiro e exigem exit 0.

**Por quê.** O padrão `` skill `([A-Za-z0-9][\w-]*)` `` (`lint-coerencia.py:66`) é validado contra as
skills **deste** plugin. `mem-search` pertence ao claude-mem. O lint está certo: ele não tem como
saber se um nome externo existe, e deixar passar reabriria o buraco que o `T-008` fechou.

**Como citar ferramenta de outro plugin.** Não use a palavra "skill" imediatamente antes do nome em
crases. `` ele expõe `mem-search` `` passa; `` a skill `mem-search` `` não. O mesmo vale para
`/comando` e `` `agente` `` de terceiros.

**A lição maior:** teste que reprova sem causa aparente pode estar apenas **rodando outro gate por
dentro**. Antes de investigar dois testes como se fossem defeitos independentes, verifique se ambos
não são o mesmo lint falhando.

## `codex plugin marketplace add` registra com nome DERIVADO, não com o do manifesto — 2026-09-02

**O que aconteceu.** `codex plugin marketplace add thedotmack/claude-mem` respondeu
*"Added marketplace `claude-mem-local`"*. O `marketplace.json` daquele repositório se declara
`name: "thedotmack"`, então o passo seguinte — `codex plugin add claude-mem@thedotmack` — falhou com
*"plugin `claude-mem` was not found in marketplace `thedotmack`"*. O nome válido é o **de registro**
(`claude-mem-local`), não o declarado no manifesto nem o dono do repositório.

**Como acertar sempre:** rode `codex plugin marketplace list` **entre** os dois comandos e use o
nome da coluna `MARKETPLACE`. Não presuma o nome a partir da URL, do dono ou do manifesto.

⚠️ **Isto afeta o `instalar.md` do próprio Orquestra**, que ensina `codex plugin add orq@orquestra`.
Funcionou porque aquele marketplace **por acaso** registrou como `orquestra` — não porque o nome
seja previsível. Instalação em host novo deve conferir a listagem antes do `add`.

## O claude-mem pode parar de gravar e continuar respondendo "ok" no health — 2026-09-02

**O que aconteceu.** O aviso dizia *"observer falhou 33 vezes"* com
`NOT NULL constraint failed: session_summaries.memory_session_id`. Medido: **última gravação 17,6 h
antes, zero observações em 12 h** — e o worker respondendo `{"status":"ok"}` na porta 37701, com
`activeSessions: 1`. **Worker vivo não significa memória sendo salva.**

**Como verificar de verdade** — não confie no health, olhe o relógio do banco:

    select max(created_at_epoch) from observations;

Se a última gravação for de horas atrás e houve trabalho no período, está quebrado.

**O que isso provou sobre o desenho, e é o ponto que fica:** a sessão inteira que consertou a fiação
do claude-mem **não foi capturada por ele** — e nada se perdeu, porque a wiki e o checkpoint
seguraram tudo. É exatamente a divisão de papéis escrita no `T-072`: a wiki é a **fonte da verdade**,
o claude-mem é **rede de segurança**. Quando a rede falha em silêncio, quem estava certo era quem
não dependia dela.

## Memória de sessão parada NÃO se detecta pelo health — só pelo relógio do banco — 2026-09-02

**O caso completo, porque a investigação errou antes de acertar.** O claude-mem parou de gravar às
00:34 e só foi notado **22 h depois**, por um aviso do próprio plugin. Durante todo esse tempo:
`{"status":"ok"}` na porta 37701, worker com PID vivo, sessões sendo registradas normalmente em
`sdk_sessions` — e **zero** observações gravadas, de nenhum projeto.

**A causa real** (`observer-health.json` + `logs/claude-mem-*.log`): a sessão foi marcada
`status='completed'` enquanto a conversa **continuava**. Ao tentar gravar o resumo de uma sessão já
dada como encerrada, o `memory_session_id` vem nulo e o `NOT NULL` da tabela `session_summaries`
recusa. 42 falhas consecutivas. **Não é caso isolado: 126 das 481 sessões receberam observação
depois de marcadas como completas.** É bug do plugin, não de configuração.

**A hipótese errada, registrada de propósito:** achei que a causa fosse uma mensagem envenenada em
`pending_messages` (3 presas desde maio/junho, uma apontando para sessão sem `memory_session_id`).
Limpei a fila com backup — e o erro continuou, com `consecutiveFailures` subindo de 33 para 42
**durante** a investigação. Fila vazia + nada gravado = as mensagens não estavam nem chegando; o
problema era antes do ponto consertado. *Uma hipótese que explica os dados não é a causa até a
correção mudar o comportamento.*

**Como verificar de verdade** — três sinais, nesta ordem:

    cat ~/.claude-mem/observer-health.json     # consecutiveFailures e lastErrorMessage
    # última gravação vs. agora, no banco: max(created_at_epoch) de observations
    # health na porta: o MENOS confiável dos três — responde ok com tudo parado

**A lição que vale além do claude-mem:** *processo vivo não é trabalho feito.* Todo componente que
grava em segundo plano precisa ser verificado pelo **carimbo do que gravou**, nunca por
liveness/health. E o que salvou estas 22 h foi a wiki: o claude-mem é rede de segurança, a wiki é a
fonte da verdade — quando a rede caiu em silêncio, quem não dependia dela não perdeu nada. Virou o
card `T-075`.

## `.worktreeinclude` é do Claude Code, não do git — 2026-09-04

**Crédito da correção:** análise externa (Fable 5.1), que a levantou como opção e depois a
retratou. Registrada aqui porque é suposição plausível que só apareceria **depois** de uma
implementação inteira.

O `.worktreeinclude` existe e funciona — mas é recurso **do Claude Code** (está no changelog
dele), não do git. Ele copia arquivos ignorados para worktrees que *o Claude Code* cria.
Worktree criado por outro app (Orca, herdr) ou por `git worktree add` na mão **não passa por
ele**. Qualquer desenho que dependa dele para compartilhar `memory/` entre worktrees falha
silenciosamente fora do Claude Code.

**A regra geral:** antes de apoiar um desenho num recurso, confirme **de quem** é o recurso —
git, host, ou plugin. `git help <cmd>` responde em segundos, e a resposta muda o desenho.

## Board editado dentro de worktree é trabalho que ninguém mais vê — 2026-09-04

**Medido neste repo:** dos 10 worktrees vivos, **7 tinham alterações não commitadas, e quase
todas eram arquivos de `memory/`** — `KANBAN.md`, `MEMORY.md`, `fixes-history.md` e threads.
Board de 41–52 cards nos worktrees contra 74 no principal. Um agente aberto no `t037` editaria
um board sem os 31 cards criados depois.

**Por que acontece:** `memory/` é versionado, então cada worktree carrega uma **cópia congelada
no commit daquele branch**. O protocolo multi-janela ("releia antes de escrever", "edite a linha")
pressupõe **um** arquivo disputado — e com worktree não há disputa, há bifurcação silenciosa.

**Como detectar:** `git worktree list` e, em cada um, `git status --porcelain | grep memory/`.
Alteração de `memory/` dentro de worktree é sinal de trabalho órfão, não de trabalho em curso.

**Conserto proposto:** `T-076` — resolver `memory/` pelo `git rev-parse --git-common-dir`, que
devolve o `.git` do **principal** a partir de qualquer worktree. ⚠️ Ele pode vir **relativo ao
cwd** (da raiz devolve `.git`), então normalize para absoluto antes de mudar de diretório.
