# Thread — desenvolvimento do próprio plugin

**Frente:** o Orquestra desenvolvendo o Orquestra (dogfooding).
**Aberta em** 2026-07-26 · **último checkpoint** 2026-07-28 · **versão** 0.10.0.

## Fases

- ✅ Dogfooding: board e wiki instalados no próprio repo
- ✅ Correção do namespace `/orquestra:*` → `/orq:*` (sobrevivera a 3 releases)
- ✅ Stack complementar auto-detectada, com consentimento e registro de recusa
- ✅ Painel de revisores consertado (2 causas raiz) e ampliado para 3 revisores
- ✅ Lint de coerência interna, testado nos dois sentidos
- ✅ Contrato do board (`_schema.md`) + smoke test de três sinais
- ✅ Protocolo de várias janelas
- ✅ Roteamento automático (cobertura de gatilho 0% → 100%)
- ✅ Problemas conhecidos documentados e diagnosticáveis
- ⬜ Hooks de segurança (`T-001`) — o único enforcement que bloqueia de verdade
- ⬜ Piloto dos loops A e B (`T-012`) — nunca invocados de verdade
- ⬜ **9 cards em VALIDATE** aguardando o dono usar o produto

## Decisões que não devem ser re-litigadas

- **Kimi dentro do Orquestra, não como comandos globais.** Comandos globais criariam um segundo
  sistema de revisão paralelo ao `/orq:revisar`, que já tem reconciliação — mais forte que tabela
  comparativa.
- **Catálogo da stack aponta repositório, não comando.** Comando envelhece; repositório não. E some
  a assimetria de deixar uma ferramenta sem comando por falta de procedência.
- **Sem lock global no protocolo multi-janela.** Mataria o paralelismo que motiva as N janelas. A
  causa da perda é a reescrita do arquivo inteiro, não a concorrência.
- **Crases obrigatórias para skill no lint, opcionais para agente.** Assimetria proposital: "skill" é
  palavra comum em prosa portuguesa; `orq-` não aparece em texto corrido. Um revisor externo sugeriu
  uniformizar e a "correção" gerou 3 falsos positivos na hora.
- **CLI do Codex em vez do plugin.** O plugin não é invocável pelo modelo (`codex:codex-rescue` não
  existe como agent type; `/codex:review` tem `disable-model-invocation`). Contraria a regra global
  do dono, que só é executável quando **ele** digita o comando.

## Padrão de erro que se repetiu — vigiar

**Concluir "não existe" a partir de verificação de fonte única.** Aconteceu duas vezes em dois dias:
`claude plugin --help | head` cortando lista alfabética (levou a escrever instrução falsa no plugin)
e `which kimi` respondendo sobre o PATH da sessão em vez do disco (levou outra sessão a quase
instalar pacote desnecessário). Nos dois casos a conclusão errada ia gerar ação real.

**E o irmão dele:** documentar o contrato sem endurecer o parser. A 0.6.0 escreveu a spec do board e
deixou o consumidor aceitando lixo; o painel reprovou.

## ⏭️ RETOMAR AQUI

O trabalho de **código** está em ponto estável: tudo publicado, plugin global em 0.10.0, as três
verificações passando.

O gargalo agora **não é técnico, é de validação**: 9 cards esperando o dono usar o produto. A pilha
crescer tanto é sinal de que a validação não está acontecendo — e o desenho diz que card fecha quando
ele confirma, não quando o commit passa.

**Próxima ação concreta, em ordem:**
1. Pedir ao dono que valide 1 ou 2 cards de verdade (o `T-015` é o mais rápido: dizer *"parece que
   não conectou"* num projeto e ver se roda o diagnóstico).
2. `T-012` — exercitar `/orq:plan-next` e `/orq:implement-next` numa tarefa real, sem atalho. É o
   último contrato entre partes que ninguém testou.
3. `T-001` — hooks de segurança, o único enforcement que de fato bloqueia.

**Não começar código novo antes do item 1.** Empilhar mais entrega sobre 9 validações pendentes é
exatamente o que o board existe para impedir.
