# T-150 — auditoria e correções locais da R1, 2026-10-07

Parecer real Opus 5.5/high: **REPROVADO**, uma chamada, sem retry.
Pacote preservado: `T-150-R1-v2-pacote-local.md`, 49.256 bytes,
SHA-256 `a5e9713443cba3df866f52eb472d6c977b605cea23f2e6b6878ca81cfbd7705b`.
O reviewer só leu o diff colado; não executou testes. A auditoria abaixo não
substitui revisão independente do snapshot corrigido. R2 não autorizada.

## Achados auditados

| Achado | Resultado da auditoria | Correção local |
|---|---|---|
| B1, saldo externo implícito | Cenário não se confirma no contrato completo: `revisar.md`, §1c, e skill, contrato de continuidade, já exigem fonte humana, teto/saldo, snapshot/envelope e proíbem derivar autorização da regra operacional. O diff não incluía todo esse contexto. A referência nova admite esclarecimento | Referência explicita que, sem teto/saldo comprovados, nenhuma chamada adicional está coberta; a regra histórica não concedia duas chamadas nem uma terceira. Nenhum saldo foi criado |
| B2 A/B, estagnação prevalece sobre review aprovado e autoridade | **Confirmado por execução**: ambos retornaram `diagnose_and_change_strategy` com tudo verde, review atual aprovado e contador 2; inclusive `local_work=false` | Diagnóstico exige pendência local real e autoridade. Contador consecutivo só pode ser zerado pelo Manager com recibo novo auditado; total e orçamento nunca zeram |
| B3, fila vazia não encerra noturno | **Confirmado como contradição da instrução**: §2 manda não inventar trabalho, mas §4 dizia que só orçamento/parada encerravam | Ausência de card elegível encerra com relatório; não reabre estacionados. Guarda de texto não é prova comportamental de uma LLM |
| R1, JSON profundo | **Confirmado na CLI nativa Python 3.9.6**: teste real de 2.401 bytes saiu 1, traceback em evidência e recibo. A bancada context-mode usa outro Python e não reproduziu o mesmo erro; não generalizar entre ambientes | Parser normaliza `RecursionError` para `INVALID_INPUT`, exit 2, sem traceback/caminho/payload |
| R2, Matriz histórica | Ambiguidade textual real, não mudança funcional comprovada | `manda` mantém vigente a Matriz; somente o teto antigo continua histórico |
| R3, baixa confiança confundida com abstenção | **Confirmado**: escolha válida com confiança 0,5 era `abstained` | Status distintos `low_confidence`/`abstained`; ambos mantêm regra local, sem retry |
| R4, formato remoto dado como conferido | Afirmação excedia o gate: fixtures locais não comprovam aceitação remota | Documentação explicita contrato local candidato e conferência futura sob gate próprio |

## RED observado antes das correções

Comando real na worktree: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_work_evidence.py'`.
Python nativo 3.9.6: 34 testes, exit 1, nove falhas de assertions/subtests,
nenhum erro de infraestrutura. Capturaram: estagnação em estado aprovado/sem
pendência, status de baixa confiança, JSON profundo em ambos os argumentos e
contradição de término do noturno. Guardas documentais são estáticas.

## Contabilidade preservada

Sete sondas sintéticas e uma R1 foram iniciadas, todas sem retry. Os oito recibos
individuais sobreviveram a uma sobrescrita de estado no harness documental:
o término da R1 salvou uma leitura do gate anterior às seis sondas Codex.
Registro recomposto pelos IDs únicos dos recibos, sem chamada nova e sem renovar
orçamento. A R1 continua consumida 1/1 e não aprovada; provas de capacidade não
são aprovação técnica nem prova de qualidade/economia.

## GREEN e gates frescos concluídos

Após as correções: 34 testes focados passaram; suíte descoberta completa
910/910, exit 0, 253,262 s, handle 90265 terminal; manifesto estrito,
coerência interna, Ruff e diff-check exit 0. Dois ResourceWarnings já
existentes no baseline, sem falhas. Todas as 22 mutações foram detectadas,
sem erro de infraestrutura; dez controles/replay offline passaram, sem JEV real.
Recibo: `docs/T-150-verificacoes-pos-R1.json`.

O snapshot local corrigido continua sem aprovação independente. R2 preparada,
não enviada, 78.999 bytes, teto proposto 96 KiB; inventário em
`docs/reviews/T-150-R2-inventario-local.json`. A auditoria colada naquele pacote
é o registro anterior a esta conclusão dos gates; seu digest não foi alterado.
Nada foi bumpado, staged, commitado, integrado, publicado, instalado ou reiniciado.
