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
  Sem esse arquivo (projeto ainda sem Orquestra), trate como primeira vez — mas **não crie o arquivo
  agora**: ele nasce no passo 5, com o resultado real.
- **Exige chave ou conta paga** → só proponha se houver ganho claro, e diga o custo na mesma linha.

## 3. Propor e ESPERAR

Para cada ferramenta ausente que sobreviveu ao filtro, uma linha honesta:

> **`nome`** — o que resolve, em uma frase · **ganho aqui:** por que *neste* projeto · **custo:** chave,
> serviço externo, disco, ou "nenhum" · link do **repositório oficial**

Ordene por **ganho/custo**, melhor primeiro. Se nada faz sentido, **diga isso** — não invente
recomendação para parecer útil.

**PARE e espere.** Ele escolhe o que quer, e pode escolher nenhuma.

## 4. Instalar só o aprovado

O catálogo **não traz comando de instalação de propósito** — comando envelhece, repositório não.
Para cada ferramenta aprovada:

1. **Abra o repositório oficial** e leia as instruções de instalação **de lá**. São elas que estão
   atualizadas e corretas para esta plataforma.
2. **Confira que é o repo oficial, não um fork.** Vários destes têm forks populares de nome parecido.
3. **Mostre ao dono o que você vai rodar** e de onde tirou. Ele aprovou a ferramenta, não um comando
   que ele não viu.
4. Execute.

**O que o "pode instalar" dele cobre:** a ferramenta que ele nomeou, instalada do jeito que o repo
oficial manda. Mostrar o comando no passo 3 é transparência, não um segundo gate — **você não precisa
esperar ele aprovar o comando de novo**.

**Volte a perguntar** se as instruções do repo exigirem qualquer coisa além de instalar: `sudo`,
alterar PATH ou shell profile, desabilitar verificação de assinatura, instalar dependência de sistema,
abrir porta, ou rodar script baixado por `curl | sh`. Nesses casos, mostre o que ele exige e **pare**.
Aprovar a ferramenta não é aprovar mexer na máquina.

- **Nunca** instale o que exige chave sem que ele forneça a chave. Não invente credencial, não leia
  chave de outro arquivo para reaproveitar.
- Falhou? Mostre o **erro real** e pare essa ferramenta. Não tente rota alternativa por conta própria.
- O repositório sumiu, mudou de dono ou as instruções não batem com a plataforma? **Pare e relate.**
  Não improvise instalação a partir de fonte secundária.
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
