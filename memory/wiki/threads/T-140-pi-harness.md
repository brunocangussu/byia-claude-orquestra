# T-140 — Pi como executor opcional da Orquestra

**Origem:** estudo pela frente `@frente-jev-router` no host Codex · **estado:** `[ ]` backlog de piloto opcional. Nenhuma decisão é exigida agora.

## Pedido e limite

O dono perguntou se [Pi](https://pi.dev/) pode orientar melhor os agentes no terminal. O objetivo assumido para a avaliação é melhorar a qualidade de resolução com papéis e skills específicos, sem perder os gates da Orquestra nem aumentar custo até aceite. Corrigir esta hipótese se a intenção for outra. Este card não autoriza instalar Pi, trocar o elenco, enviar código a outro provedor ou alterar o T-139.

## Evidência atual — 2026-09-26

- Pi é um *harness* mínimo para agentes, não um LLM separado. Suporta modelos/provedores, skills sob demanda, extensões TypeScript e modos interativo, print/JSON, RPC e SDK. Não traz subagentes nem modo de planejamento nativos como contrato padrão. [Visão oficial](https://pi.dev/), [SDK](https://pi.dev/docs/latest/sdk), [RPC](https://pi.dev/docs/latest/rpc).
- Skills seguem o padrão Agent Skills; Pi descobre `.agents/skills/`, mas o carregamento relevante pelo modelo não é prova automática de que a skill foi seguida. Isso favorece portabilidade, não substitui os recibos/digests do compositor T-139. [Skills](https://pi.dev/docs/latest/skills).
- Extensões podem controlar ferramentas, eventos, contexto e estado, mas rodam com as permissões do processo e podem ver prompts, arquivos, credenciais e histórico. Código de terceiros exigiria revisão de segurança e isolamento próprios. [Extensões](https://pi.dev/docs/latest/extensions).
- `pi` não está no PATH desta sessão. Não houve instalação, autenticação ou chamada de modelo.
- A parada recente da meta veio do estado `blocked` do próprio Codex, aplicado após o gate de egress B do T-139; não foi causada pelo guardião do Orquestra. Pi não altera esse estado nem concede autorização de envio.

## Hipótese nova de observabilidade — 2026-09-26

Os dez JSONL A/B do T-139 via `codex exec --ephemeral` não contêm campo
estrutural de modelo ou effort; os recibos registram corretamente
`effective_model=null`. Em contraste, o contrato documentado do Pi expõe
no `AssistantMessage` os campos `provider`, `model`, `responseModel?` e
`usage` com custo calculado, inclusive em eventos JSONL de `message_end`.
O RPC também oferece `get_state` com objeto de modelo selecionado. Ver
[Message Types](https://pi.dev/docs/latest/message-types),
[JSON Event Stream](https://pi.dev/docs/latest/json) e
[RPC Commands](https://pi.dev/docs/latest/rpc-commands).

Isso torna Pi uma hipótese concreta para **recibos mais auditáveis** em um
piloto futuro, não uma prova de modelo efetivo ou faturamento: `model` pode
refletir a solicitação/configuração; `responseModel` é opcional; `usage.cost`
depende do preço configurado. Primeiro seria necessário inspecionar uma
resposta real, origem desses campos, sandbox e isolamento. Uma execução Pi
não pode substituir um dos braços Codex já congelados do T-139, pois mudaria
o harness junto da skill. Permanece sem instalação, autenticação ou egress.

## Opções

1. **Aproveitar padrões sem acoplar Pi agora (recomendado).** Manter Manager único e T-139 no Codex/Claude; comparar as ideias de skills/RPC/recibos com o compositor existente. Menor custo operacional e nenhuma variável nova no experimento em curso.
2. **Piloto posterior como terceiro host opcional.** Adaptador isolado CLI/RPC, versão fixa, sem extensões de terceiros, mesmo modelo/effort/fixtures e orçamento que o host de referência. Pode oferecer observabilidade e portabilidade, mas adiciona autenticação, manutenção e superfície de segurança.
3. **Substituir o núcleo do Orquestra por Pi.** Não recomendado: duplicaria planejamento, gates e ownership já existentes sem evidência de melhora. A troca confunde efeito do harness com efeito da skill ou do modelo.

## Prova mínima para a opção 2

Depois de fechar o par T-139 sem contaminar seus snapshots, definir tarefas sintéticas independentes com controles limpos e defeitos semeados. Primeiro, contrato local sem modelo: captura byte a byte do briefing, skill realmente carregada, ferramentas/sandbox, modelo solicitado, sessão e recibo; falhar fechado se a via não comprovar capacidade. Só então pedir autorização separada para instalar e para chamadas externas. Comparar Pi e host atual com modelo, effort, tarefa e limites equivalentes; medir solução aceita por testes, falsos bloqueadores, violações de escopo, tentativas, latência, tokens e custo até aceite. Se a identidade do modelo ou a equivalência da via não puderem ser provadas, classificar o resultado como exploratório. Nenhuma adoção por prompt menor ou resposta mais fluente isoladamente.

## Próxima etapa opcional

Adotar a opção 1 por enquanto. Só retomar o piloto da opção 2 se o T-139 mostrar uma lacuna que Pi possa resolver e o dono quiser avaliá-la; isso exigirá plano e gates próprios. Nada aqui implica instalação, integração, mudança de elenco, API key ou egress.

⏭️ RETOMAR AQUI: preservar T-139 como experimento principal. Se este card for retomado depois, reivindicar a frente, escrever desenho do adaptador e gates separados antes de implementação; não usar Pi para contornar a autorização B ou o estado da meta do Codex.
