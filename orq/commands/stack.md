---
description: Verifica quais ferramentas de contexto e memória estão faltando nesta máquina, explica o ganho de cada uma e instala as que você aprovar
argument-hint: "[--verificar para só diagnosticar, sem propor instalação]"
---

Você vai avaliar a **stack complementar** deste ambiente. Leia
`${CLAUDE_PLUGIN_ROOT}/stack.md` — é o catálogo canônico, com o que cada ferramenta resolve, como
detectá-la e como instalá-la.

> **Nada disso é dependência do Orquestra.** Ele funciona sozinho. Estas ferramentas atacam um
> problema vizinho — o contexto acaba — e por isso se somam bem. Não venda como obrigatório.

## 1. Detectar (sem perguntar nada ainda)

Rode as verificações da coluna **Detectar** do catálogo. Verifique **de verdade**, não presuma:
comando no PATH, marketplace registrado, MCP configurado e **respondendo**.

Registre três grupos: **presente** · **ausente** · **presente mas quebrado** (instalado e não
responde — isso é pior que ausente, porque o dono acha que tem).

Se `$ARGUMENTS` tiver `--verificar`, mostre o diagnóstico e **pare aqui**.

## 2. Filtrar pelo que faz sentido AQUI

Não proponha a lista inteira. Corte pelo projeto:

- **Menos de ~50 arquivos** → camada 3 (Serena / codebase-memory) não se paga. Não proponha.
- **Sem repositório grande nem histórico longo** → Supermemory é prematuro.
- **Já recusado antes** → leia `memory/wiki/_stack.md` e **não reproponha** o que ele já dispensou.
- **Exige chave ou conta paga** → só proponha se houver ganho claro, e diga o custo na mesma linha.

## 3. Propor e ESPERAR

Para cada ferramenta ausente que sobreviveu ao filtro, uma linha honesta:

> **`nome`** — o que resolve, em uma frase · **ganho aqui:** por que *neste* projeto · **custo:** chave,
> serviço externo, disco, ou "nenhum" · `comando exato de instalação`

Ordene por **ganho/custo**, melhor primeiro. Se nada faz sentido, **diga isso** — não invente
recomendação para parecer útil.

**PARE e espere.** Ele escolhe o que quer, e pode escolher nenhuma.

## 4. Instalar só o aprovado

- Rode **o comando exato** que você mostrou. Nada além dele.
- **Nunca** instale o que exige chave sem que ele forneça a chave. Não invente credencial, não leia
  chave de outro arquivo para reaproveitar.
- Falhou? Mostre o **erro real** e pare essa ferramenta. Não tente rota alternativa por conta própria.
- Ao terminar: `/reload-plugins` e **confirme que a ferramenta responde** antes de dizer que está
  pronta. Instalado ≠ funcionando.

## 5. Registrar

Escreva `memory/wiki/_stack.md` com três seções — **é isso que impede a conversa de se repetir toda
sessão**:

```markdown
# Stack deste ambiente

## Ativas
| Ferramenta | Desde | Para que serve aqui |

## Dispensadas (não repropor)
| Ferramenta | Quando | Motivo do dono |

## Bloqueadas
| Ferramenta | O que falta |
```

Registre também no `memory/fixes-history.md` o que foi instalado, e acrescente a `memory/gotchas.md`
qualquer armadilha que a instalação revelou.

## Regras

- **Nunca instale nada sem "pode instalar" explícito.** Nem "só essa que é rapidinho".
- **Nunca** rode instalação com `sudo`, nem altere PATH ou shell profile do dono.
- Não desinstale nem atualize o que já está lá — se algo está velho, **relate** e deixe ele decidir.
- "Dispensada" é decisão permanente até ele reabrir. Respeite silenciosamente.
