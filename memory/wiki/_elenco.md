# Elenco — qual LLM toca cada papel

> **Os comandos leem este arquivo antes de spawnar** e passam o modelo como override.
> O `model:` do arquivo do agente é só o padrão de fábrica. Ajuste com `/orq:elenco <papel> <modelo>`
> — ou fale naturalmente: *"quero o Fable planejando"*, *"tira o GPT da revisão"*.

## Papéis

| Papel | Modelo | Por quê |
|---|---|---|
| `manager` | *sessão principal* | definido pelo `/model` — **não é spawn, não se configura aqui** |
| `planner` | `opus` | achar causa raiz e desenhar solução é o trabalho mais difícil |
| `implementer` | `inherit` | acompanha o modelo da sessão |
| `reviewer` | `opus` | revisão adversarial exige raciocínio forte |
| `docs` | `sonnet` | escrita objetiva sobre código já pronto |
| `scout` | `sonnet` | leitura ampla e barata |

Valores aceitos: `opus` · `sonnet` · `haiku` · `fable` · `inherit` · ou um id específico
(`claude-opus-5`).

## Revisores externos

| Revisor | Estado | Config |
|---|---|---|
| codex | **ativo** | `--model gpt-5.6-sol --effort xhigh` (read-only) · CLI em `/usr/local/bin/codex` |
| kimi-k2 | inativo | sem CLI e sem MCP nesta máquina — ver card `T-007` |

## Por que o painel importa neste projeto

O produto aqui são **instruções**, não código. Onde dois modelos divergem sobre o que uma instrução
significa, **a divergência é o achado** — é sinal de ambiguidade real no texto, que um leitor futuro
também vai encontrar. O Codex tem contexto adicional: foi ele quem auditou a arquitetura original e
produziu o parecer que virou o roadmap.

Em card pequeno e de baixo risco, `--rapido` (só o revisor interno). Painel em mudança trivial é
desperdício.
