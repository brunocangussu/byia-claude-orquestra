# Rascunho do `T-038` (movido de `orq/compor-statusline.md` em 2026-08-09)

> **Isto NÃO é instrução ativa do plugin — é rascunho.** O `T-036` foi partido (3 rodadas de painel,
> 8 pareceres, 8 reprovações); a folha F4 (compor o board dentro de uma statusline alheia) e este
> procedimento saíram do `T-036` e viraram o `T-038`. Mora aqui, fora de `orq/`, de propósito: dentro
> do plugin um modelo poderia lê-lo e segui-lo como se fosse produto distribuído, mesmo sem citação.
> **Carrega achados abertos da rodada 3 do painel, não corrigidos** — a lista completa ("Os 8
> achados do painel — onde cada um entra") está na seção `# PLANO v3` de
> `memory/wiki/threads/T-036-statusline.md`. Destaque, porque é de segurança: a guarda de
> metacaracteres do T2 abaixo (o comando inteiro não pode conter `|`, `&&`, `||`, `;`, `` ` `` ou
> `$(`) **não cobre `>`, `<` nem `&`**, e o `eval echo "$script"` que expande `~`/`$HOME` no mesmo T2
> **permite que conteúdo vindo de settings dispare execução de processo**. Nenhum dos dois foi
> corrigido aqui — só registrado. Ver o card `T-038` em `memory/wiki/KANBAN.md`.

---

# Compor o board dentro de uma statusline alheia (folha F4 do `/orq:init`)

> **Procedimento canônico (T-036, plano v3).** O `/orq:init` chega aqui só na folha **F4** da árvore
> da FASE 4: existe uma statusline efetiva, de terceiros, que não mostra o board. Este arquivo é a
> **regra operacional inteira** — o `init.md` só resume a árvore e delega para cá, para não duplicar
> a mesma instrução em dois lugares (T-015 já cobrou o preço de duas cópias divergirem).

## A tese, para quem for executar isto

**Trocar juízo por propriedade verificável.** Este procedimento não pede para "entender a
arquitetura" do script alheio lendo-o — ele encolhe o que precisa entender até caber em **checagens
binárias** (T1-T6 abaixo) e prova o resto por **experimento**: rodar o script original e o composto
com a mesma entrada e exigir que a saída antiga seja **prefixo byte-a-byte** da nova.

Se você se pegar pensando *"acho que entendi como esse script funciona, vou inserir aqui"* sem que
uma das checagens abaixo tenha validado isso — **pare**. Não existe "o modelo lê e se vira" neste
procedimento: ou o estado passa nas seis checagens e no experimento, ou você **nomeia o motivo** e
cai no fallback (mostrar o bloco, não escrever nada). Um "não sei" nomeado é sucesso deste
procedimento; uma escrita não verificada é o defeito que reprovou cinco vezes no painel.

## Quando cada parte roda

- **P0-P2 são read-only** — rodam ainda na FASE 1 do `/orq:init` (investigação), para que a
  pergunta 4 da FASE 3 já mostre ao dono o bloco exato e os arquivos nomeados, antes de pedir
  aprovação.
- **P3-P7 só rodam na FASE 4**, depois de o dono ter aprovado nominalmente — nunca antes.
- Qualquer T de P0 que falhar, em qualquer momento, interrompe o procedimento ali: nada abaixo dele
  roda, e o resultado é o fallback (seção "Fallback — contrato único").

## P0 — Resolver e qualificar o alvo (read-only; T1-T6)

O "alvo" é o **arquivo real** de script que a chave `statusLine` efetiva invoca — nunca o comando em
si. Resolva symlink com `realpath`/`readlink -f` antes de qualquer checagem: é **esse** arquivo real
que a aprovação nominal (FASE 3) nomeia, e é nele que P3-P7 escrevem.

- **T1 — o tipo é `command`.** Leia o campo `type` da chave `statusLine` efetiva. Qualquer valor
  diferente de `"command"` → fallback (motivo: "tipo de statusline não suportado — só sei compor
  comando de shell").

- **T2 — isolar um único arquivo de script no `command`.** Critério, em ordem:
  1. descarte prefixos `NOME=valor` no início do comando (zero ou mais);
  2. o próximo token tem que ser um interpretador shell — `sh`, `bash` ou `zsh`, com ou sem caminho
     (`/bin/sh`, `env bash`, etc.);
  3. o token seguinte é o candidato a script — expanda `~` e `$HOME` e resolva para caminho
     absoluto;
  4. o comando **inteiro** não pode conter `|`, `&&`, `||`, `;`, `` ` `` ou `$(` fora do próprio
     caminho entre aspas — qualquer um desses no nível de cima significa que não há **um** arquivo
     isolável.

  Ilustração (equivalente vale, desde que produza o mesmo resultado nas fixtures do passo 9 da
  thread):
  ```sh
  c="$statusline_command"
  case "$c" in *"|"*|*"&&"*|*"||"*|*";"*|*'`'*|*'$('*) fallback_motivo="comando tem pipe/subshell/&&/; — não isolo um único arquivo" ;; esac
  c=$(printf '%s\n' "$c" | sed -E 's/^([A-Za-z_][A-Za-z0-9_]*=[^ ]* )*//')
  interp=$(printf '%s\n' "$c" | awk '{print $1}')
  case "$(basename "$interp")" in sh|bash|zsh) ;; *) fallback_motivo="comando não começa por sh/bash/zsh" ;; esac
  resto=$(printf '%s\n' "$c" | sed -E 's/^[^ ]+ //')
  case "$resto" in
    \"*\") script=$(printf '%s\n' "$resto" | sed -E 's/^"([^"]*)".*/\1/') ;;
    *)     script=$(printf '%s\n' "$resto" | awk '{print $1}') ;;
  esac
  script_exp=$(eval echo "$script")  # expande ~ e $HOME
  ```
  Zero candidato (comando inline sem arquivo — ex.: `sh -c 'printf ...'`), mais de um candidato, ou
  qualquer sinal do passo 4 acima → fallback (motivo: "não consigo isolar um único arquivo de
  script").

- **T3 — o alvo é shell.** Shebang `#!` com `sh`, `bash` ou `zsh` (direto ou via `env`); ou, sem
  shebang, o interpretador já reconhecido no T2. Byte `NUL` no arquivo — checagem portátil:
  `od -An -c "$alvo" | tr -s ' ' '\n' | grep -qx '\\0'`. Use `-c`, não `-tx1`: um dump em
  hexadecimal concatenado sem separador dá **falso positivo** sempre que o fim de um byte e o início
  do próximo formam "00" por coincidência (provado em mesa em 2026-08-08 — um script comum de 3
  linhas já bastou); `-c` marca o byte nulo como o token isolado `\0`, sem essa ambiguidade. Byte
  `NUL` achado, ou shebang de outra linguagem (`python`, `node`, `ruby`, …) → fallback (motivo: "só
  sei compor shell; para `<linguagem>`, o trecho a
  adaptar é este:" + o bloco P3).

- **T4 — o alvo é gravável.** `[ -w "$alvo" ]`. Não → fallback (motivo: "sem permissão de escrita em
  `<alvo>`").

- **T5 — escolher o ponto de inserção.** Ache a última linha não-vazia e que não seja comentário
  (`^[[:space:]]*#`); chame o número dela de **`L`**. Se o texto dessa linha é `exit` ou
  `exit <código>` (`<código>` numérico) começando na coluna 0 → o ponto é **antes dela** (linha
  `L`). Senão → o ponto é **EOF**.
  *De propósito*, T5 não tenta provar que o fluxo do script realmente chega até esse ponto (um
  `exec` no meio, um `exit` escondido dentro de um `if` mais acima) — isso é o papel do experimento
  em P5. Análise estática de fluxo em shell alheio é exatamente o juízo que este procedimento existe
  para não fazer.

- **T6 — determinismo, e captura do "antes".** Monte os dois mocks fixos (ver abaixo) e rode o
  script **original** (antes de qualquer edição) **duas vezes por mock**, mesmo `cwd` (a raiz deste
  projeto):
  ```sh
  MOCK_RICO='{"model":{"display_name":"Sonnet"},"workspace":{"project_dir":"<abs-do-projeto>"},"context_window":{"used_percentage":10},"cost":{"total_cost_usd":1.23}}'
  MOCK_VAZIO='{}'

  out1=$(printf '%s' "$MOCK_RICO"  | sh "$alvo" 2>&1); rc1=$?
  out2=$(printf '%s' "$MOCK_RICO"  | sh "$alvo" 2>&1); rc2=$?
  [ "$out1" = "$out2" ] && [ "$rc1" -eq "$rc2" ] || fallback_motivo="sua barra não é reprodutível com o mock rico; não consigo validar uma edição sem risco"
  antes_rico="$out1"

  out1=$(printf '%s' "$MOCK_VAZIO" | sh "$alvo" 2>&1); rc1=$?
  out2=$(printf '%s' "$MOCK_VAZIO" | sh "$alvo" 2>&1); rc2=$?
  [ "$out1" = "$out2" ] && [ "$rc1" -eq "$rc2" ] || fallback_motivo="sua barra não é reprodutível com o mock vazio; não consigo validar uma edição sem risco"
  antes_vazio="$out1"
  ```
  Use o interpretador do shebang identificado no T3 em vez de `sh` fixo, se o shebang for
  `bash`/`zsh`. `antes_rico`/`antes_vazio` são o "antes" que P5 vai comparar — **este é o registro
  que substitui o "antes" impossível da v2** (lá, a FASE 5 tentava capturar um "antes" depois de a
  FASE 4 já ter escrito).

- **Colisão de nome (guarda fechado).** `grep -c 'orq_kanban' "$alvo"` maior que 0 → fallback
  (motivo: "já existe algo chamado `orq_kanban` neste script — não arrisco colidir nome de
  variável"). Na prática não deve ocorrer; é barato o suficiente para não pular.

Qualquer T (ou o guarda de colisão) que falhar interrompe aqui — vá direto para "Fallback — contrato
único", nomeando o motivo exato. Nenhum P1 em diante roda sem T1-T6 verdes.

## P1 — Variável de diretório (nunca causa fallback)

Procure no alvo **exatamente uma** linha que case, aproximadamente:
```sh
candidatos=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*=\$\(.*(jq|grep|sed).*(project_dir|current_dir|cwd).*\)' "$alvo")
```
- Exatamente 1 linha → `VAR` é o nome antes do `=`; o bloco P3 usa `"$VAR"`.
- 0 ou mais de 1 → `VAR` fica vazio; o bloco P3 usa `"$PWD"`.

Os dois caminhos degradam com segurança: pior caso é board vazio ou do diretório errado — visível e
reversível, nunca barra quebrada. (`$PWD` como `cwd` do processo de render é comportamento empírico,
não documentado — ver autocrítica na thread.)

## P2 — Cópia do `kanban-status.sh`

A fonte no plugin (`${CLAUDE_PLUGIN_ROOT}/scripts/kanban-status.sh`) **nunca** é o que a chave/bloco
aponta (R3) — o caminho muda a cada update. Copie para um destino estável:

- Alvo dentro deste projeto → `.claude/kanban-status.sh`.
- Alvo fora deste projeto (ex.: `~/.claude/statusline.sh`) → `~/.claude/orq/kanban-status.sh` (R4/D10).

**Guarda do achado 7 — Caso C é ausência da CHAVE, não dos ARQUIVOS, e o mesmo vale aqui:**
- Destino já existe **sem** o stamp deste plugin na linha 2 → **parar e relatar** (é arquivo de
  alguém; não sobrescreva). Cai no fallback total.
- Destino já existe **com** o stamp → recopiar é re-sync legítimo (mesmo mecanismo do
  `--reinstalar`).
- Destino está sob controle de versão do projeto (`git -C <dir-do-destino> ls-files --error-unmatch
  <destino>` sem erro) → diga isso explicitamente na proposta (FASE 3): um arquivo rastreado será
  alterado.

Copie, `chmod 755`, e insira como linha 2 (após o shebang) o mesmo stamp da Decisão 2:
```
# orq v<versão> — instalado por /orq:init em <AAAA-MM-DD>; fonte: orq/scripts/kanban-status.sh. Não editar à mão; re-sync: /orq:init --reinstalar
```

## P3 — O bloco (exato, com sentinelas)

```sh
# >>> orq: kanban no fim da barra (v<versão>, /orq:init <AAAA-MM-DD>) — para desfazer, apague daqui até '<<< orq'
orq_kanban=$(sh "<caminho-absoluto-da-cópia>/kanban-status.sh" "<"$VAR" de P1, senão "$PWD">" 2>/dev/null) || orq_kanban=""
[ -z "$orq_kanban" ] || printf " | %s" "$orq_kanban"
# <<< orq
```

Os dois pontos variáveis, preenchidos na hora de gravar: `<caminho-absoluto-da-cópia>` é o destino
resolvido em P2; o segundo argumento é `"$VAR"` (o nome real da variável achada em P1, ex.:
`"$current_dir"`) ou `"$PWD"` se P1 não achou nenhuma. `<versão>`/`<AAAA-MM-DD>` seguem o mesmo
formato do stamp da Decisão 2.

Três propriedades, **verificadas em mesa em 2026-08-08** (fixtures no scratchpad, reproduzidas no
passo 9 desta implementação):
1. sob `set -e`, com a cópia ausente ou ilegível, a barra sai **intacta** e `exit 0` — o
   `|| orq_kanban=""` protege a atribuição, e `[ -z "$orq_kanban" ] || printf …` retorna `0` nos
   dois ramos (a forma inversa, `[ -n "$orq_kanban" ] && printf …`, retornaria `1` quando o board
   está vazio e derrubaria um script com `set -e` — é por isso que a forma é `[ -z ] ||`, não
   `[ -n ] &&`);
2. com a cópia presente e o board com conteúdo, ele concatena na mesma linha, com o separador
   `" | "`;
3. `sh -n`/`bash -n`/`zsh -n` aceitam o bloco.

Sem `[ -x ]`/`[ -r ]` no bloco: cópia ausente ou ilegível já degrada a vazio pelo `2>/dev/null` +
`||` — testar o bit de permissão aqui seria redundante (e seria o mesmo erro do achado 1).

## P4 — Escrita (travas 1 e 3)

**Trava 1, sempre primeiro:** backup no mesmo diretório do alvo, preservando modo/dono:
```sh
backup="$alvo.orq_bak.$(date +%Y%m%d-%H%M%S)"
cp -p "$alvo" "$backup"
```
Este backup **nunca é apagado por nós** — nem em sucesso, nem em fallback.

**Ponto = EOF** (T5 não achou `exit` final): append em **uma única chamada**, para preservar
inode/modo/dono do arquivo original:
```sh
printf '%s\n' "$BLOCO" >> "$alvo"
```

**Ponto = antes do `exit` final na linha `L`** (T5 achou): monta o conteúdo novo num arquivo
temporário **no mesmo diretório** (mesmo filesystem — `mv` é rename atômico só se for), com o modo
espelhado do original, e substitui por `mv` — o host pode invocar a statusline no meio da escrita, e
o arquivo nunca pode ficar meio-escrito:
```sh
tmp="$(dirname "$alvo")/.orq_tmp.$$"
{ head -n "$((L - 1))" "$alvo"; printf '%s\n' "$BLOCO"; tail -n "+$L" "$alvo"; } > "$tmp"
modo=$(stat -f%Lp "$alvo" 2>/dev/null || stat -c%a "$alvo")   # BSD ou GNU — mesmo padrão do date -r/-d já usado no statusline.sh
chmod "$modo" "$tmp"
mv "$tmp" "$alvo"
```

## P5 — Validação (trava 4)

1. **Sintaxe**, com o interpretador do shebang identificado no T3: `sh -n "$alvo"` (ou
   `bash -n`/`zsh -n`). Falhou → P6.
2. **Experimento**, com os mesmos dois mocks de T6, mesmo `cwd`:
   ```sh
   depois_rico=$(printf '%s' "$MOCK_RICO" | sh "$alvo" 2>&1); rc=$?
   case "$depois_rico" in "$antes_rico"*) ;; *) motivo="prefixo não bateu no mock rico"; falhou=1 ;; esac
   [ "$rc" -eq 0 ] || { motivo="exit != 0 no mock rico"; falhou=1; }
   sufixo="${depois_rico#"$antes_rico"}"
   case "$sufixo" in *📋*|*⚠*) ;; *) motivo="sufixo sem sinal de board no mock rico"; falhou=1 ;; esac

   depois_vazio=$(printf '%s' "$MOCK_VAZIO" | sh "$alvo" 2>&1); rc=$?
   case "$depois_vazio" in "$antes_vazio"*) ;; *) motivo="prefixo não bateu no mock vazio"; falhou=1 ;; esac
   [ "$rc" -eq 0 ] || { motivo="exit != 0 no mock vazio"; falhou=1; }
   ```
   No mock vazio (`{}`), exige-se **só** prefixo + `exit 0` — o board pode não imprimir nada se o
   `project_dir` resolvido não apontar para este projeto (comportamento correto, não falha). No mock
   rico, o sufixo **tem** que conter `📋` ou `⚠`, porque a FASE 4 já criou/confirmou o board deste
   projeto antes de chegar aqui — se o sufixo não aparece, alguma premissa (ponto de inserção, fluxo
   do script) estava errada, mesmo que T1-T6 tenham passado.
3. Qualquer falha (sintaxe ou experimento) → P6, levando `motivo`.

## P6 — Reversão (trava 5)

```sh
cp -p "$backup" "$alvo"
cmp -s "$backup" "$alvo" || { echo "RESTAURAÇÃO FALHOU — pare tudo. Backup em: $backup. Restaure com: cp -p \"$backup\" \"$alvo\""; exit 1; }
```
- Restauração confirmada por `cmp` (prova byte-idêntica) → relate o **motivo exato** da falha (de
  P0 ou P5) e caia no fallback total (mostrar o bloco).
- Se a **própria restauração falhar** (disco cheio, permissão mudou no meio) → **pare tudo**, informe
  o caminho do backup e o comando de restauração manual. Nunca tente de novo por conta própria.

## P7 — Relato (só no caminho de sucesso)

Diga, sempre:
- qual arquivo foi editado (o alvo real, symlink resolvido);
- o caminho do backup criado;
- como desfazer à mão (apagar tudo entre `# >>> orq:` e `# <<< orq`, e restaurar o backup se
  preferir);
- **se o alvo fica fora deste projeto**: aviso explícito — "isto muda a barra de **todos** os
  projetos desta máquina; em projeto sem board o bloco não imprime nada".

## Fallback — contrato único

Qualquer T de P0 falhar, **ou** P5 reprovar (e P6 confirmar a reversão) → o resultado é sempre o
mesmo formato, nunca um estado indefinido:

1. **Nada foi escrito** (ou foi escrito e revertido, com `cmp` provando restauração).
2. Diga o **motivo exato**, nomeado (nunca "não consegui" genérico).
3. Mostre o **bloco P3** preenchido com os valores já resolvidos (caminho da cópia, variável de
   diretório) para o dono colar à mão, se quiser.
4. Cite em uma linha que a barra completa do Orquestra existe como alternativa — nunca proponha
   substituir a statusline dele.

## Mapa travas → passos

| Trava | Onde |
|---|---|
| 1 — backup antes de escrever | P4 |
| 2 — idempotência (não duplicar em re-run) | folha F3 do `init.md` + as sentinelas: um script já composto contém `kanban-status`, cai em F3 no próximo `/orq:init` |
| 3 — nunca editar linha existente | T5 (escolha do ponto) + P3/P4 (bloco-sufixo, nunca reescreve o `printf` alheio — Decisão 11) |
| 4 — validar antes de aceitar | P5 |
| 5 — reversão automática em qualquer falha | P6 |
