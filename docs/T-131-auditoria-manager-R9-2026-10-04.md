# T-131 — auditoria da rechecagem R9

## Resultado e escopo

Opus 5.5/Claude CLI oficial, uma chamada de 152.325 bytes, sem retry:
exit 0 em 95,203 s, formato válido, **GO**. B1 da R8 classificado CORRIGIDO.
Parecer/recibo/log imutáveis em
`docs/reviews/T-131-R9-rechecagem-correcoes-2026-10-04/`.
O GO fecha a rechecagem de B1 e regressões do ajuste; não certifica host
instalado, migração do elenco, execução dos testes pelo reviewer ou entrega Git.

## B1 — conferência do Manager

Os consumidores corrigidos exigem combinação autorizada no projeto, recibo
real consultável, verificação de origem/compatibilidade e ausência de isenção
de prova. Default/alias/cache não certificam e recibo compatível dispensa nova
sonda por uso. Os oito arquivos corrigidos, os hunks e a classe R8 constam do
pacote. Runner preservado, SHA
`625d9d2998696e67ccfe11b0bf731920be03617d31ee0762ff891b3d552af2ce`.
Nenhum novo bloqueador operativo foi apontado no escopo pelo titular.

## Ressalvas auditadas, sem novo ajuste após o GO

- **Fixture de data/modelo observado — confirmado, restrito a teste.**
  `test_elenco_perfis.py`, classe `T131PosR8LegadoComprovadoTest`:
  `CONTEXTO` inclui ambos e `decidir_despacho_legado` compara todos os
  campos. A própria docstring limita a projeção à fixture; não é executor
  usado pelo Manager/produto. Um recibo de outra data seria recusado nessa
  projeção, enquanto a instrução permite reuso compatível. Risco de
  manutenção/teste, não regressão operacional demonstrada. Não modificar
  essa fonte no snapshot aprovado nem fingir que a ressalva foi corrigida.
- **Marcos textuais fracos — parcial/confirmado como limite da prova.**
  `MARCOS_COMUNS` não exige a frase de ausência de sonda; campos do recibo
  são procurados no texto inteiro. A bancada não prova comportamento do
  LLM. Isso já delimita os testes e não constitui novo caso de ação errada
  demonstrado no contrato B1 fornecido.
- **Recibo nativo/modelo observado — não verificável nesta rechecagem.**
  Nenhuma sonda nova foi autorizada. Preservar fail-closed e a necessidade
  de capacidade comprovada por via; GO não autoriza declarar nativo apto.
- **Persistência de recibo Anthropic — lacuna documental reconhecida.**
  Runner emite o recibo no stderr; `revisar.md` não prescreve de forma
  explícita sua persistência como faz para os IDs Companion. Nesta frente
  os recibos estão gravados. O risco indicado é ausência de prova em uso
  futuro e consequente bloqueio, não bypass demonstrado. Não ocultar.
- **Runtime novo — comportamento deliberado do gate.**
  O gate inclui versão do executável/runtime na compatibilidade; não
  revalidá-la por conta própria nem interpretar atualização como recibo.
- **Thread de init — ambiguidade residual reconhecida.**
  `init.md:290–291` distingue destino durável do card atual da operação
  legada comprovada. A definição genérica de thread não nomeia a de origem.
  Não autoriza criar thread de outra frente; a interpretação coerente
  conserva o recibo de origem. Ressalva não bloqueante do titular.
- **Lista de riscos herdados da R8:** não foi transformada em sete bugs
  novos. Identidade/provider, aliases, subtype, sinais e relógio mantêm
  suas delimitações históricas. O pacote desta rechecagem não é prova
  comportamental de todos esses pontos.

## Correção de uma afirmação factual do parecer

O reviewer leu a falha inicial do implementer e diz que não registra suíte
verde; o isolamento sozinho de fato não apaga a falha. Porém também houve
**suíte completa fresca do Manager**, registrada antes do envio em
`docs/T-131-gates-manager-pos-R8-lote-545205-2026-10-04.json`:
525 testes, exit 0, junto de manifesto/lint/diff-check exit 0. Conferidos
os quatro registros nesta auditoria. A falha inicial continua preservada
e sua causa não comprovada. O reviewer não recebeu esse recibo completo,
portanto não há certificação remota do gate — mas o gate local passou.

## Decisão do Manager

**GO com ressalvas não bloqueantes registrado, sem repetir a revisão.**
Não usar o GO como autorização para bump/commit/push/integração/instalação.
Elenco ativo, T-089, fonte e pacote continuam preservados. Próxima fase é
conciliação/entrega com gate próprio, e depois prova comportamental de host.
