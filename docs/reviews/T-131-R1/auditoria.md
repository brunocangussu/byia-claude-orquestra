# T-131 — auditoria da R1 pelo Manager

Data: 2026-09-23. Snapshot `479dce3e6cd0b370f20f70a232d7ceda29af9547bba39798ec3e9afc4efa7fda`.
Uma rodada, cinco lotes completos, nenhuma repetição. Todos saíram 0 e comprovaram
`OPUS_MODEL=claude-opus-5-5`; tempos 72,0 / 76,4 / 49,5 / 50,7 / 67,1 segundos.
Vereditos crus: lotes 1, 2, 3 e 5 REPROVADO; lote 4 APROVADO_COM_RESSALVAS.
O parecer é sobre texto colado, sem ferramentas; o Manager conferiu a fonte local.

## Veredito auditado: corrigir antes de integrar

Quatro grupos de correção, sem confundir cada menção duplicada com outro defeito:

1. **Gate de capacidade sem caminho de obtenção da prova** — L1/B1 + L3/B1. Confirmado
   em `orq/commands/elenco.md:191` e `:271`, `README.md:229`: exige prova de todos os valores,
   mas não define registro/validade e proíbe nova sonda sem delimitar a fase. Isso transforma
   a proteção dos candidatos novos em obstáculo a ajustes normais. Correção deve permitir
   prova autorizada e referenciada por modelo/mecanismo/conta; **não** aceitar automaticamente
   qualquer valor de preset como prova, como uma sugestão do revisor permitiria.
2. **Inicialização ficou ambígua** — L1/B2, confirmado em `elenco.md:191-196` e `:337-343`.
   O caminho explícito de criação foi removido; a frase “se não existe elenco, pare” admite
   parar mesmo quando há prova. Não afirmar que nenhuma interpretação permitiria criar:
   o defeito é ausência de caminho feliz inequívoco. Restaurar a condição “com prova válida”.
3. **Manager fixado além da escolha verificável** — L2/B1, parcialmente confirmado em
   `memory/wiki/_elenco.md:190`. O dono **pediu Astra**, ao contrário da premissa de ausência
   de decisão do parecer. Entretanto, sua fala não fixa `@max` nem torna esse valor verdade
   permanente sobre todas as sessões. Preservar “modelo da sessão, escolha do dono” ou separar
   preferência datada de identidade observada. Não trocar a sessão nem o elenco vivo nesta revisão.
4. **Teste não protege todos os papéis ativos** — L5/B1, confirmado por reprodução somente
   em memória: substituir apenas o scout do Host Codex por `gpt-6-sol@low` e depois por
   `gpt-6-luna`, interceptando `Path.read_text` do elenco, deixa **60/60 testes do módulo**
   `test_elenco_perfis` verdes nos dois casos. Nenhum arquivo foi alterado. A promessa de
   preservação integral tem cobertura incompleta. Acrescentar verificação por seção/papel,
   vinculada ao snapshot aprovado, sem proibir eternamente uma futura ativação autorizada.

A primeira tentativa desse ensaio falhou antes de executar testes por falta do diretório
`orq/scripts` no `sys.path` do sandbox. Corrigido somente o harness de auditoria; não era falha
do produto. Os dois resultados 60/60 acima são da execução válida posterior.

## Auditoria das ressalvas

| Origem | Decisão e evidência |
|---|---|
| L1/R1 + L2/R1 | Confirmada a ambiguidade de “capacidade confirmada no uso” no spawn nativo Claude. CLI 5.5 comprovada não prova override do spawn nativo; explicitar pendência por mecanismo. |
| L1/R2 | Confirmada a referência “sem effort declarado — ver nota” sem nota específica sobre effort no novo template. Corrigir junto da documentação. |
| L1/R3 | Terminologia “alias” conflita com a opção ID explícito na mesma seção, mas a linha seguinte cita a exceção por igualdade. Clareza, não recusa inevitável. |
| L1/R4 + L4/R1 | Prefixos concretos sumiram da documentação, mas permanecem em `MODEL_ALIASES` e o runner barra identidade errada. Defesa documental enfraquecida, não bypass atual. |
| L1/R5 | Não é defeito ativar somente depois da prova: a tabela é declaradamente candidata. A recusa anterior era da CLI 0.153.4, não do App nem da conta inteira. Diagnóstico novo separado. |
| L1/R6 + L3/R3 | Duplicação de `opus` e rótulo “legado” fora da célula do runner confirmados; clareza a corrigir. |
| L2/R2 | Falta distinguir recibo CLI explícito, runner candidato e spawn nativo. Já há sonda CLI 5.5 registrada; a R1 usa runner instalado com alias `opus`, não valida instalação do runner candidato. |
| L2/R3 | Igualdade para o ID explícito é requisito deliberado; a sonda anterior já observou `claude-opus-5-5` exato. Não alargar prova por hipótese de sufixo futuro. |
| L2/R4 + L5/R2 | Confirmada a troca adicional do preset `economia` de alias `opus` para ID explícito, fora da substituição estrita de usos Fable. Separar essa decisão ou preservar alias; não presumir autorização ampla. |
| L3/R1 + R2 + R6 | Confirmada mistura de elenco deste projeto com fábrica, e perda do qualificador “host Codex” para Terra no README. Corrigir escopo/sujeito, sem redistribuir os papéis. |
| L3/R4 | Lista de IDs do host Claude ficou ambígua; exemplo explícito não deve virar allowlist universal acidental. |
| L3/R5 | “Via” deve incluir mecanismo nativo quando aplicável; não é impedimento técnico novo. |
| L3/R7 | Descartado: passo 3 real, `elenco.md:272-280`, preserva explicitamente estado das vias. Referência correta ao ler o arquivo completo. |
| L4/R2 | A nota sobre override Fable deve manter identidade e pedido do dono explícitos. Runner não redireciona; risco instrucional, não bug comprovado de execução. |
| L4/R3 | Falta cenário específico Sonnet na suíte; Fable→Opus já é testado com `claude-opus-5`, não exatamente 5.5. O mapa e a comparação atual também rejeitam 5.5. Cobertura a reforçar, sem alegar bypass existente. |
| L4/R4 | Código aceita alguma chave exata em `modelUsage`; teste de múltiplas chaves confirma. Documentar sem alegar que isso prova sozinho a autoria exclusiva da resposta final. |
| L5/R1 | As três primeiras asserções leem fixtures locais, não documentos. Confirmado; não atribuir-lhes cobertura dos arquivos reais. |
| L5/R3 | Lint deixou de ancorar o prefixo de `opus`; comportamento atual continua correto e tem teste. Igualdade/lookalike também têm testes. Lacuna de defesa em profundidade, não bug atual do runner. |
| L5/R4 | `assertIn` sobre documento inteiro não ancora seção; confirmado por leitura. Deve ser resolvido junto do grupo 4. |
| L5/R5 | Descartado: `import re` existe no cabeçalho e o módulo executou 60 testes. |
| L5/R6 | CRLF não é falso vermelho nesse caso: `Path.read_text` usa tradução universal. Espaço depois do heading é sensibilidade textual real, mas o contrato usa heading exato; não normalizar toda a estrutura com `\s+` indiscriminadamente. |

## Limites e próxima ação

Nenhuma correção aplicada ao produto, nenhuma R2 iniciada. Não bumpado, commitado, integrado,
publicado ou instalado. Antes de novas edições, conciliar a renomeação externa do worktree T-131
para T-137; preservar todo trabalho paralelo. Fechar autorização do ajuste do preset `economia`
e do próximo snapshot/review antes de novo envio. Os 421 testes locais anteriores não anulam
os achados documentais nem a lacuna demonstrada pelos mutantes.
