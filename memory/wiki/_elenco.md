# Elenco — qual LLM toca cada papel

> **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
> O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste com `/orq:elenco <papel> <modelo>`
> — ou fale naturalmente: *"quero o Fable planejando"*, *"tira o GPT da revisão"*.

## Papéis

| Papel | Modelo | Por quê |
|---|---|---|
| `manager` | *sessão principal* | definido pelo `/model` — **não é spawn, não se configura aqui** |
| `planner` | `fable` | achar causa raiz e desenhar solução é o trabalho mais difícil — **escolha do dono em 2026-07-28** |
| `implementer` | `sonnet` | executar plano já aprovado é trabalho dirigido — **escolha do dono em 2026-07-28** |
| `reviewer` | `opus` | revisão adversarial exige raciocínio forte |
| `docs` | `sonnet` | escrita objetiva sobre código já pronto |
| `scout` | `sonnet` | leitura ampla e barata |

Valores aceitos: `opus` · `sonnet` · `haiku` · `fable` · `inherit` · ou um id específico
(`claude-opus-5`).

## Revisores externos

| Revisor | Estado | Config |
|---|---|---|
| codex | **ativo** | `codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh -s read-only "<briefing>" < /dev/null` · CLI em `/usr/local/bin/codex` |
| kimi | **ativo** | `KIMI=$(command -v kimi \|\| echo "$HOME/.kimi-code/bin/kimi")` então `"$KIMI" -p "<briefing>" --output-format text < /dev/null` · v0.29.2, OAuth · symlink em `~/.local/bin/kimi` criado em 2026-07-28 |

**Os dois exigem `< /dev/null`** — sem TTY eles bloqueiam lendo stdin e travam até o timeout.
**Nenhum dos dois recebe dado sensível** (ver a regra em `/orq:revisar`, passo 1b).

O Kimi **não tem flag de sandbox**. Não passar `-y`/`--yolo` nem `--auto`; reforçar "não edite
arquivo" no prompt. Garantia dura só em worktree descartável.

## Por que o painel importa neste projeto

O produto aqui são **instruções**, não código. Onde dois modelos divergem sobre o que uma instrução
significa, **a divergência é o achado** — é sinal de ambiguidade real no texto, que um leitor futuro
também vai encontrar. O Codex tem contexto adicional: foi ele quem auditou a arquitetura original e
produziu o parecer que virou o roadmap.

Com **três** revisores (Claude · Codex · Kimi) a reconciliação fica mais forte: "confirmado por 2+"
deixa de ser unanimidade e vira **maioria**, o que separa melhor o achado sólido do palpite de um
modelo só. Três fornecedores distintos (Anthropic · OpenAI · Moonshot) erram de formas menos
correlacionadas que duas instâncias do mesmo.

Em card pequeno e de baixo risco, `--rapido` (só o revisor interno). Painel em mudança trivial é
desperdício.
