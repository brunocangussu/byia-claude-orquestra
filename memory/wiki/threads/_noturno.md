# Modo noturno — manifesto

```
run_id: noturno-2026-07-30-2228
cards_max: 3
horas_max: 4
expira_em: 02:28 (2026-07-31)
modo: PLANEJAMENTO (nenhuma implementação)
cards: [T-026, T-023, T-020]
```

**Autorização do dono (2026-07-30, verbatim):** *"continue o desenvolvimento e as melhorias que
achar necessário por hora, tudo que precisar de minha decisão podemos deixar para amanhã — vai
realizando checkpoints e continue o desenvolvimento no que julgar importante, eu irei dormir e pode
usar o protocolo de desenvolvimento enquanto durmo."*

Ele autorizou "desenvolvimento", mas a v1 do modo noturno **não implementa** — e essa restrição não
é dele para dispensar sem saber o que dispensa: o `T-006` (implementação noturna) está bloqueado
pelo `T-001`, que é justamente o hook que impediria `push`/deploy/migration. Sem esse hook, a
disciplina noturna é promessa, não garantia. **Fica em planejamento.**

## Fila escolhida

| Card | Por quê é seguro planejar à noite |
|---|---|
| `T-026` | já estava em curso quando o modo abriu — pesquisa read-only sobre hosts alternativos |
| `T-023` | correção de redação em 5 lugares, sobre fato **já verificado empiricamente** em 2026-07-29 |
| `T-020` | perfis de elenco — instrução + tabela; as escolhas dele viram perguntas estacionadas |

## Cards pulados de propósito (exigem o dono acordado)

| Card | Motivo |
|---|---|
| `T-001` · `T-002` · `T-005` | hooks de **segurança/permissão** — a lista do protocolo manda pular |
| `T-019` | isolamento de revisor externo sem sandbox — é segurança, e a opção (c) é hook |
| `T-006` | bloqueado pelo `T-001`; planejá-lo agora seria planejar sobre chão que não existe |
| `T-021` | sobrepõe o `T-026`, que já está sendo planejado — evitar dois planners no mesmo território |
| `T-004` | workflows em JS: escopo grande, e o desenho depende do que o `T-025` decidir sobre iniciativa |
| `T-024` | precisa que o dono confirme se o painel falhou de verdade ou se foi só a frase de teste |

## Registro da execução

- **22:28** — modo aberto. `T-026` já em curso (planner `fable`, lançado pouco antes do modo).
- **22:38** — `T-026` voltou. Matriz de paridade verificada nos dois CLIs reais, com "verificado"
  separado de "suposição" e o não-investigado declarado. Card → `[!]` com **6 decisões**.
  **Achado que passou do card:** o Kimi 0.29.2 tem hooks `PreToolUse` **bloqueáveis** (exit 2 nega).
  Isso **derruba a premissa escrita no `T-019`** ("o Kimi roda fora do Claude Code, então o hook não
  o alcança") — a opção (c) daquele card voltou à mesa. Corrigi a nota do `T-019` no board; falta
  verificar se o hook do Kimi vale por projeto (a doc só mostra escopo de usuário).
- **22:40** — `T-023` entrou em planejamento (planner `fable`, briefing com o aviso de modo noturno
  e proibição de rodar `plugin update`/`reload-plugins`, que mutariam o ambiente do dono).

- **22:47** — `T-023` voltou. Causa raiz **diferente da que o card supunha**: a doc sempre
  codificou regra binária em vez de evidência por componente — virar a regra de novo seria a
  terceira repetição do defeito. Achou **7 lugares + 2 homônimos**, não 5, e identificou dois que
  **não devem ser tocados**. Card → `[!]` com 5 decisões.
- **22:49** — `T-020` (perfis de elenco) entrou em planejamento — **último da fila** (`cards_max: 3`).
- **em curso** — auditoria read-only da wiki (scout `sonnet`), só aponta, não corrige.

- **23:05** — auditoria da wiki voltou: **4 contradições vermelhas**. Três eram fato vencido e foram
  corrigidas na hora (é manutenção de wiki, não implementação); a quarta virou o card `T-027` porque
  é decisão do dono. Detalhe no relatório abaixo.
- **23:12** — `T-020` voltou e **corrigiu a paráfrase do próprio card** indo ao transcript: o dono
  disse *"faço só com o Opus"*, não *"menos Fable"*. Card → `[!]` com 6 decisões.
- **23:15** — fila esgotada (`cards_max: 3`). **Modo encerrado por teto de cards**, ~47 min de uso,
  bem dentro das 4 h. Manifesto marcado como **expirado**.

## 📋 Relatório final — `noturno-2026-07-30-2228`

**Encerrado às 23:15 por atingir `cards_max`.** Nenhuma linha de `orq/` foi tocada, nenhum push,
nenhuma instalação, nenhuma decisão tomada no lugar do dono.

### Planejado (3 cards, todos estacionados em `[!]` com a pergunta exata escrita)

| Card | O que o plano descobriu |
|---|---|
| `T-026` | A premissa do card caiu: o **Kimi 0.29.2** lê `AGENTS.md`, carrega `SKILL.md` com auto-invocação, aceita agents no formato Claude Code e tem hooks `PreToolUse` **bloqueáveis**; o **Codex 0.145** já consome marketplace em formato Claude. Recomenda "Orquestra portátil" e **recusa** port por host. 6 decisões |
| `T-023` | Causa raiz diferente da suposta: a doc sempre codificou **regra binária** em vez de **evidência por componente** — virar a regra de novo seria a terceira repetição. São **7 lugares + 2 homônimos**, não 5, e dois deles **não devem ser tocados**. 5 decisões |
| `T-020` | A paráfrase do card envelheceu: no transcript o dono disse **"faço só com o Opus"**, não "menos Fable". Perfil `economia` muda **garantia**, não só custo. 6 decisões |

### Achado que passou de um card para outro

O `T-026` derrubou a premissa escrita no `T-019` (*"o Kimi roda fora do Claude Code, então o hook
não o alcança"*): ele **tem** hooks próprios, com `PreToolUse` bloqueável. A opção (c) daquele card
voltou à mesa. Falta verificar se o hook do Kimi vale **por projeto** — a doc só mostra escopo de
usuário.

### Auditoria da wiki (read-only, 14 arquivos)

Corrigido, por ser fato vencido e não decisão:

1. **`distribuicao.md` dizia que a versão vive em DOIS lugares — são quatro.** Essa página é o "como
   fazer release hoje": segui-la ao pé da letra **reproduzia o bug que gerou o `T-017`**.
2. **`MEMORY.md` dizia 8 cards em VALIDATE — são 9.** A causa era real: o `T-022` tinha marcador
   `[?]` mas estava fisicamente sob o cabeçalho *Backlog*, e quem contou contou por seção visual.
   Card movido para a seção certa.
3. **A thread principal mandava rodar dois testes de roteamento que já passaram** e citava board em
   `18% (4/22)`.
4. **`threads/README.md` dizia "nenhuma thread ativa"** com quatro threads existindo, e o índice
   `MEMORY.md` não apontava para três delas.

**Não corrigido de propósito → virou `T-027`:** a regra global do dono proíbe invocar o binário
`codex` por Bash; o projeto instrui exatamente isso em dois lugares vivos. A justificativa registrada
venceu (o `codex:codex-rescue` aparece como agent type desde 29/jul), mas a escolha pode continuar
certa — foi o `T-010` que provou a CLI direta funcionando. É decisão dele.

### Pulado de propósito (exige o dono acordado)

`T-001` · `T-002` · `T-005` · `T-019` (segurança/hooks) · `T-006` (bloqueado pelo `T-001`) ·
`T-021` (sobrepõe o `T-026`, que estava sendo planejado) · `T-004` (desenho depende do `T-025`) ·
`T-024` (precisa que o dono confirme se o painel falhou de verdade ou se foi só a frase de teste).

### Verificação ao encerrar

- `claude plugin validate ./orq --strict` → passou · `lint-coerencia.py` → 18 nomes, exit 0
- `diff -rq` cache × repo → **vazio** · board: `15% (4/26)`, parser = contagem manual = 26, sem `⚠`
- 4 cards em `[!]`, 0 em `[>]` — nada ficou pendurado em planejamento
- Commits locais: `daf1e59` · `664e308` · `9e264cd` · o de fechamento. **Sem push.**

## ⏭️ RETOMAR AQUI

**Modo noturno encerrado — manifesto expirado.** Não abra outro run a partir deste arquivo.

Ao acordar, o dono tem **4 cards em `[!]`** esperando decisão, cada um com a pergunta exata escrita
na nota e o plano completo em `threads/`. A ordem sugerida pelos próprios planos: **`T-023` (0.14.0)
→ `T-025` (0.15.0) → `T-020`**, porque os três editam `README.md` e/ou `SKILL.md` e essa ordem evita
retrabalho. O `T-026` é independente e pode entrar quando ele quiser. O `T-024` fecha sem trabalho
se ele disser que o painel nunca falhou de verdade.
