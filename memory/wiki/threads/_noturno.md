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

## ⏭️ RETOMAR AQUI

Modo noturno em andamento. Ao acordar, o dono lê o **relatório final** no fim deste arquivo (ainda
não escrito) ou pede o `/orq:acordar`. Nada foi implementado; nenhum commit tocou `orq/`.
