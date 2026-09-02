# Stack deste ambiente

> Levantado em 2026-07-26 a partir da máquina (marketplaces, MCPs e PATH reais — não presumido).
> O catálogo com ganho, custo e **repositório oficial** é `orq/stack.md` — ele não traz comando de
> instalação de propósito.

## Ativas

| Ferramenta | Como está | Para que serve aqui |
|---|---|---|
| `rtk` | `0.42.4` via Homebrew (há `0.44.0` disponível) | proxy CLI, economia nas operações de git/dev |
| `context-mode` | plugin, marketplace `mksglu/context-mode` | mantém saída grande de ferramenta fora da janela |
| `claude-mem` | plugin, marketplace `thedotmack/claude-mem` | captura a sessão e reinjeta na seguinte |
| Serena | MCP stdio via `uvx` (repo `oraios/serena`) | LSP: símbolo exato + edição cirúrgica |
| codebase-memory | binário em `~/.local/bin/` (~255 MB) | grafo de relações: quem chama o quê, impacto |
| `codex` | CLI em `/usr/local/bin/codex` | GPT-5.6 Sol como **o** revisor do host Claude (vendor oposto), `--effort xhigh` |

## Dispensadas (não repropor)

| Ferramenta | Quando | Motivo |
|---|---|---|
| SuperMemory | 2026-08-15 | conexão/autenticação recorrente; retirado por decisão do dono no `T-037`. Não repropor no init nem no stack |
| indexação semântica **deste** repo | 2026-07-26 | 24 arquivos de markdown — `grep` resolve e a indexação não se paga. Vale nos projetos-alvo, não aqui |
| Kimi K3 (revisor) | 2026-09-01 | terceiro host e terceiro revisor **saíram do produto** no `T-051`: a revisão é de um revisor só, do vendor oposto ao host. Fechou o antigo `T-007`. Não repropor |

## Procedência

Todas as fontes oficiais estão confirmadas e registradas em `orq/stack.md`. O `codebase-memory-mcp`,
que na primeira passada não tinha origem rastreável na máquina, é
[`DeusData/codebase-memory-mcp`](https://github.com/DeusData/codebase-memory-mcp) — binário estático
único, o que bate com o Mach-O de ~255 MB em `~/.local/bin/`. **Existem forks populares de nome
parecido** (e o mesmo vale para o `rtk`): conferir o dono do repo antes de instalar em outra máquina.
