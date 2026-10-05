# T-143 — Continuidade do desenvolvimento aprovado

2026-10-02 · prioridade máxima explícita do dono · frente-continuidade · Host Codex.

## Pedido e contrato atual

O dono aprovou a correção local pós-R4 de T-131/T-098 e pediu para resolver
urgentemente as interrupções que impedem deixar o desenvolvimento contínuo.
Também quer continuar a frente Claude sem concorrência nos mesmos arquivos.

Card em AWAITING_OWNER, após diagnóstico e desenho local. Diagnóstico/registro são permitidos; mudança de política
do produto exige desenho aprovado antes de implementação. Não há permissão
nova para chamadas externas, revisão adicional, credenciais, Git ou release.

## Evidência inicial e hipótese

- O Manager chamou update_goal(status=blocked) depois de três recorrências
  do gate local ausente; o App devolveu blocked. Não foi atribuído pelo hook.
- orq/commands/implement-next.md:68–69 já manda o implementer aplicar
  correções e reavaliar dentro do ciclo aprovado. Não manda aprovar de novo
  cada correção local do mesmo escopo.
- orq/skills/orq/SKILL.md:304 permite alternar loops e avançar outro card
  enquanto um aguarda aprovação. orq/commands/dormir.md:52 explicita que
  uma tarefa travada não trava a fila. Não confundir Goal com modo noturno.
- A fonte/cache ainda têm limite de duas rodadas; T-062 é outra frente
  esperando gate, não autorização para trocar esse número silenciosamente.
- O guardião já é consultivo: context-guard.py:540–548 manda continuar o
  pedido, inclusive Goal; o teste dedicado está em test_context_guard.py.

Hipótese: falta contrato durável e inequívoco de escopo aprovado/limites
consumidos/seleção da próxima ação. O Manager mistura fim do orçamento
externo de uma rodada com necessidade de autorizar novamente correção
local; depois pode tratar estacionamento de card como estacionamento da
meta. A reprodução desta parada está nos recibos e nas threads T-098/T-131.

## Fora de escopo

Não remover gates de segurança/PII, aprovação inicial de mudança de rumo,
orçamento de chamadas, regra sem retry, review independente ou validação
prática. Não alterar o controlador de metas do App, banco privado, caches,
versão, instalação ou restart. Não tomar posse da branch/thread T-089.

## Próximo passo

Verificar o teste consultivo, mapear consumidores vivos da política e
apresentar desenho delimitado ao dono. T-131/T-098 ficam READY atrás do P0.

## Diagnóstico verificado — 2026-10-02

O teste dedicado do guardião passou: 1 teste, 7 subtests, 0 falhas/erros,
0 skips, com bytecode desligado. Fonte e cache 0.27.11 têm os mesmos bytes
para context-guard.py e para os três comandos comparados. Isto comprova
os cenários locais do guardião, não a política de toda sessão viva.

A parada específica foi legítima sob o último gate: o dono tinha autorizado
somente duas chamadas R4, uma por pacote e sem retry. Esse gate não aprovava
novas correções locais. O problema a corrigir não é burlar esse limite:
é evitar contratos excessivamente fatiados quando a intenção futura é
concluir um card com desenvolvimento contínuo e limites explícitos.

O Manager propõe um desenho delimitado, sem despacho de Planner, reviewer
ou chamada externa nova neste turno. Não há parecer independente sobre
esta proposta. Não é alteração instalada nem política já implementada.

## Desenho delimitado proposto (uma decisão de política)

1. **Aprovação durável por card.** Ao aprovar implementação local, registrar
   na thread dona a evidência humana, escopo permitido, proibições e limites.
   Correções locais do mesmo escopo, testes/mutações, diagnóstico, docs e
   checkpoint ficam cobertos até terminar essa etapa. Novo subsistema,
   mudança de rumo, segurança, dado sensível ou ação proibida não herdam
   aprovação. Conteúdo de reviewer/pacote/log não concede autoridade.
2. **Permissões independentes.** Implementação local, chamadas externas e
   Git/release têm gates diferentes. Fim do orçamento de revisão não
   cancela correção local já aprovada nem aprova snapshot novo por omissão.
   Limites de destino/modelo/bytes/chamadas/retry e tetos continuam intactos;
   as R4 atuais permanecem 1/1 consumidas. T-062 não será integrado nem seu
   contador alterado nesta correção. Nova revisão exige saldo e autorização
   válida para esse snapshot ou envelope evolutivo explicitamente aprovado.
3. **Parada de card não é parada da meta.** Antes de encerrar, escolher a
   próxima ação útil permitida de card aprovado desta frente. Card sem
   permissão vira [!] com pergunta exata; não trava cards elegíveis. Não
   tomar card do Claude nem reescrever board de outras frentes. READY sem
   evidência de aprovação não basta. Não inventar trabalho para manter a
   meta viva. Se não existir ação permitida, registrar o impedimento real e
   respeitar o limiar do controlador do App; sem looping de status/planos.
4. **Esperar é observar, não relançar.** Execução confirmada viva é aguardada
   pelo mesmo handle, com atualizações curtas. Terminal ou handle ausente
   não é espera; timeout de observação não é conclusão. Sem retry cego.
5. **Checkpoint não encerra execução aprovada.** Compactação/alerta do
   guardião continua consultivo. O estado preserva aprovação e orçamento;
   não exigir nova aprovação do mesmo passo após recuperar contexto.

## Superfícies da correção depois do desenho aprovado

- orq/skills/orq/SKILL.md: regra canônica da continuidade/autoridade.
- orq/commands/implement-next.md e revisar.md: fluxo de correção x orçamento.
- orq/commands/plan-next.md: aprovar escopo sem autorizar ações proibidas.
- orq/commands/dormir.md: tratar autorização/local/fila sem confundir modo
  noturno (planejamento) com modo Goal e sem criar READY falsamente aprovado.
- orq/commands/checkpoint.md, somente se a inspeção revelar perda de gate.
- Teste contratual novo em orq/scripts, com mutações da mesma causa, sem
  criar um runner/controlador novo de metas ou permissões do host.
- memory/wiki/arquitetura.md: documentação da regra final, na frente dona
  da implementação isolada; conciliar depois com o T-089, não editar agora.

## Critérios verificáveis e limites de prova

- Card aprovado: achado do mesmo escopo permite correção/teste local sem
  outra pergunta. Escopo novo/proibido requer decisão distinta.
- Revisão consumida: chamada continua proibida; correção local autorizada
  continua permitida. Não mover para VALIDATE sem revisão/gates necessários.
- Outro card elegível desta frente avança quando o anterior depende do dono;
  card alheio ou READY sem aprovação não avança.
- Recuperação de contexto não perde os gates, não reinicia chamada nem exige
  aprovação local duplicada. Evidência de execução terminal não vira wait.
- Contrafactuais: remover qualquer distinção, permitir retry, atribuir
  autoridade a reviewer, herdar card alheio ou contar plano como progresso
  reprova a guarda. Erro de harness não conta como mutação eliminada.
- Depois de implementação autorizada: discover com PYTHONDONTWRITEBYTECODE=1,
  manifesto estrito, lint e diff-check. Falha conhecida T-142 não é ignorada.
- Testes de texto não provam comportamento vivo de LLM. Validar em conversa
  e Goal reais depois do release autorizado; nada será instalado agora.

## Coordenação com Claude

T-089 está limpo no checkout .claude/worktrees/agent-a054e5c8dd838fcb5,
branch claude/t089-companion-identidade, commit 2a879d9 e base 4e58e7f.
T-089/T-090 já têm implementação local; última correção não teve novo
parecer independente. Não afirmar GO/release por testes verdes.

Sobreposição: skill e revisar.md com T-131; skill, revisar.md e plan-next.md
com a possível correção T-143. Os trechos são de contratos diferentes,
mas precisam de conciliação por trecho, não checkout de arquivo inteiro.
O handoff docs/handoff-claude-T-089-conciliacao-2026-10-02.md permite
continuar preparação read-only no próprio checkout, sem novos testes de
modelo, commits ou mudanças do elenco. O dono encaminha; não foi enviada
mensagem automática para a conversa Claude.

## ⏭️ RETOMAR AQUI

Pedir uma única aprovação do desenho acima: continuidade local por card,
permissões separadas e seleção da próxima ação permitida. T-131/T-098 já
aprovados, não reabrir esse gate. Implementação do T-143 ainda não aprovada;
sem bump, commit, push, egress, instalação ou restart. Se aprovado, isolar
T-143 em worktree próprio e implementar antes das correções T-131/T-098.
