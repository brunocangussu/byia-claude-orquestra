# T-150 — auditoria local da R3

**Data:** 08/10/2026, Bahia. **Veredito externo literal:**
APROVADO_COM_RESSALVAS. Nenhum bloqueador apontado. O Manager leu o
parecer inteiro e auditou os riscos abaixo; não houve retry ou R4.

## Vínculo ao snapshot

- Pacote: 131.019 bytes; teto 131.072; SHA-256
  `1d4cd33b76faeaf9eaacb8ec22bd37e7671e307483e353218f165b23ba73a343`.
- Produto, 12 arquivos: SHA-256
  `721d4e833a9ab7b83513810c18f6c632587d594f8b3aa78029245b98768fa0e6`.
- Elenco candidato: SHA-256
  `676dc191665c758d079d2cc0b42b75110ccdf01c6de6422e78d39772a5c6373a`.
- Consumo: 1/1; exit 0, formato válido, 160,335 segundos. Modelo observado
  `claude-opus-5-5`; effort enviado `high`, efetivo não exposto.
- Isolamento desta chamada: wrapper conferido, safe-mode, configuração MCP
  estrita/vazia, ferramentas desativadas, cwd vazio, zero bytes adicionais.
  O runner sozinho não comprova todas essas condições.
- Parecer e recibo originais permanecem locais em `docs/reviews/`; o recibo
  bruto contém dados de conta e não entra automaticamente na entrega pública.

As correções R2 foram aceitas pelo reviewer. A aprovação pertence a estes
bytes, não a outra versão, ao futuro catálogo Haiku ou a mudanças novas.

## Auditoria das ressalvas

1. **Estado de achados recusados: confirmado, não bloqueante.**
   `orq/scripts/work_evidence.py:98-116` não representa auditoria encerrada
   quando o parecer continua `blocked`, embora os bloqueadores confirmados
   sejam zero. Reprodução offline com a fixture válida: recomenda
   `audit_review_findings`; com duas estagnações, recomenda diagnóstico.
   É conselho, não execução, mudança de card ou encerramento da meta.
   Aceitar essa limitação exige registrar a auditoria e decidir o próximo
   gate fora do helper; nunca falsificar `approved` para escapar dela.
   Um campo de auditoria concluída será uma mudança funcional futura,
   com testes próprios, não algo inserido depois desta aprovação.

2. **Persistência do planner read-only: confirmado, não bloqueante.**
   `orq/agents/orq-planner.md:37-39,73-75` só explicita persistência pelo
   Manager em packet-only. O planner·sistema Codex usa sandbox read-only,
   portanto não pode receber permissão de escrita pelo nome workspace-read.
   No uso atual, o Manager deve persistir o conteúdo devolvido e declarar
   essa divisão no briefing; não pedir ao planner para elevar permissões.
   A ausência do fallback textual na instrução permanece registrada como
   ressalva. Não declarar que um Loop A real foi validado por uma sonda.

3. **Wrapper fora da Matriz: confirmado, não bloqueante.**
   `memory/wiki/_elenco.md:125` mostra o runner; as condições comprovadas
   vieram também do wrapper local. `run-opus-reviewer.py` não acrescenta
   safe-mode/configuração MCP estrita por conta própria. Futura adoção
   precisa preservar wrapper e cwd vazio ou provar a alternativa. Não
   repetir uma chamada literal da Matriz alegando isolamento equivalente.
   O wrapper privado não deve ser publicado sem saneamento.

4. **Contrato do planner inline: condição conhecida e verificável.**
   `orq/commands/plan-next.md:19-26,149-160` manda compor o pacote e o
   contrato. A via sem customizações não carrega o agente do repo: é o
   Manager que deve incluir as instruções no briefing. Sem ferramentas é
   uma capacidade preventiva, não prova de obediência ou plano correto.

5. **Texto de origem, rótulos de subtests e ValueError genérico:**
   confirmados como manutenção não bloqueante. A linha de origem candidata
   tem redação duplicada; dois recibos str compartilham o rótulo; o único
   ValueError atual da coordenação é o contrato sistema/interface.
   Nenhum permite egress, escrita, review extra ou autorização automática.
   Produto/elenco permanecem iguais aos bytes revisados nesta auditoria.

6. **Contagens e ordenação consultiva: ressalvas teóricas preservadas.**
   Descoberta atual reconferida: 916 testes; módulos foco com 18 de
   continuidade, 7 de coordenação e 39 do helper, total 64. Os dois novos
   módulos somam 46, como o RED relatado. Não inventar um detalhamento
   retroativo do delta 910→916 a partir de totais de rodadas diferentes.
   A ordem sugerida pelo JEV continua sujeita à auditoria do Manager;
   nenhuma chamada JEV ocorreu nesta etapa.

## O que está e não está concluído

- Revisão independente do snapshot: aprovada com as limitações acima.
- Gates locais do snapshot: recibo pós-R2 preservado, 916 testes e 28
  mutações; a descoberta atual confirma a composição, não reexecuta a suíte.
- Prontidão para pedir entrega Git: sim, sem alegar adoção geral ou DONE.
- Entrega Git, bump, push, integração, publicação, instalação e restart:
  não autorizados neste gate e não executados.
- Haiku: identidade confirmada apenas para planejamento do Host Claude.
  Não foi testado nem incorporado ao produto revisto.
- T-144: auditoria de branch é separada e não transfere a frente mods.

As ressalvas não serão escondidas nem transformadas em novas chamadas por
omissão. Se uma correção funcional alterar o snapshot, a aprovação atual
não é reciclada para afirmar que os bytes novos foram revisados.
