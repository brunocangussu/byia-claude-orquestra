# T-151 — fonte 0.33.0 entregue, piloto ainda proposto

## O que está entregue

Commit `0b998e44c7eae72d13fe4f93841a5be2dc43c841`, na main/local e em
`origin/main`, push exit 0 e SHA exato confirmado por leitura remota.
Manager portou o snapshot funcional revisado do worktree à main e bumpou
os quatro anchors no mesmo commit. **Não foi um merge da branch candidata**:
o worktree e o pacote congelado continuam preservados para rastreabilidade.
Os rascunhos e trechos compartilhados T-150/T-152 não entraram no commit.

- Acordo inicial verificável por meta; complementos técnicos cobertos seguem
  pelo aceite do Manager, sem nova pergunta por etapa.
- Manager único decide a decomposição por entregas independentes; workers
  recebem ownership disjunto, testes e contrato de handoff.
- Manager supervisiona falhas, aceita os resultados e integra localmente.
- Sem agente aprovador, novo roteador ou alteração de elenco/modelos/efforts.
  Uma LLM não concede autoridade humana nova nem renova saldo externo.

## Evidências e limites

R1 Opus 5.5/high, uma chamada de 187.361 bytes sanitizados via Claude CLI,
sem retry: **GO**, dez ressalvas auditadas, zero bloqueadores. Modelo
`claude-opus-5-5` comprovado; sem ferramentas/customizações/MCP. Nenhuma
mudança funcional após a revisão. Parecer bruto e auditoria preservados
em `docs/reviews/`; recibo terminal `docs/T-151-R1-envio-2026-10-10.json`.

Descoberta completa fresca na árvore de entrega: **936 testes, 266,475 s,
OK**, com bytecode desativado. Manifesto estrito, coerência, Ruff e diff-check
saíram 0. O exit final do processo da descoberta não ficou retido após
compactação; o log terminal OK foi preservado e vinculado por digest.
Recibo: `docs/T-151-verificacoes-entrega.json`.

As sondas anteriores deram 8/8 em ambos os lados e não são comparáveis
causalmente. **Não há prova de economia, velocidade ou benefício geral de
subagentes.** O plano do piloto aborda exatamente essas lacunas.

Fonte entregue não é pacote instalado/carregado: esta sessão continua na
0.32.0. Não houve publicação, instalação ou restart. Não há prova de
atualização de todos os chats, nem adoção comportamental Claude/Orca.
T-151 permanece em VALIDATE, não DONE; T-098/T-150 não foram encerrados.

## Próximo passo solicitado pelo dono

Apresentar `docs/plano_piloto_T-151-manager-subagentes.md` **antes de executar**:
dois cenários sintéticos × dois braços, mesmo briefing e elenco, ordem
balanceada, ownership disjunto e falha local controlada. Medir tempo total,
tokens de todos os agentes, retrabalho e intervenções humanas reais.

Teto proposto: quatro runs, até 16 chamadas OpenAI, 60 min de execução,
1,2 milhão de tokens de entrada e 48 mil de saída. A observabilidade dos
limites é um preflight; consumo divulgado só no fim não é hard cap.
Sem Anthropic/JEV adicional; Claude/Orca ficam para smokes separados,
sem transferir o elenco Codex. **Piloto não executado e ainda não aprovado.**

Ao retomar, comprovar o pacote absoluto e resolver o board/thread_root.
Ler índice, card e `threads/T-151-autonomia-por-meta.md`. Continuar o run
`05118f07-4c9e-4e92-8c2a-eda7ea7b478f`, sem reset e sem repetir a R1.
Os marcos finais do medidor e da entrega documental ficam na thread.
