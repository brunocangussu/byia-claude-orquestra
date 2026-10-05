# T-098 R4 — auditoria read-only do Manager

2026-10-02. **NO-GO: três bloqueadores confirmados, gabarito não aprovado.**
Parecer: `parecer.json`; execução/identidade: `resultado.json`.
Uma chamada autorizada/consumida; CLI/runner exit 0, modelo observado
`claude-opus-5-5`. Cobertura declarada válida: sete arquivos, 48 casos,
18 famílias, dev/reserved. Não é comprovação de leitura interna do modelo.

## Bloqueadores

1. **CONFIRMADO E REPRODUZIDO — atalhos lexicais.** A cascata descrita no
   parecer foi calculada localmente sobre os textos congelados:
   marcadores de falta de informação → abster; explique/entender/diga apenas/
   mostre a conta → consulta; apóstrofos ou pontos finais → trivial;
   extensão .py/.json → pequeno; implemente/construa/acrescente/instrucoes.md
   → normal; restante → alto_risco. Resultado: **48/48**, sem raciocínio
   sobre risco/escopo. `candidata-r4/amostra.json:3`–`:50`;
   rubrica `docs/T-098-rubrica-v2.md:89` exige ganho sobre regras.
   Diagnóstico pós-hoc com gabarito conhecido; NÃO benchmark cego nem prova
   de que uma regra foi derivada/congelada apenas no dev antes de abrir reservado.

2. **CONFIRMADO, com escopo delimitado — mecanismos repetidos entre partições.**
   `Y044` (`amostra.json:22`, dev) e `Y042` (`:46`, reserved) pedem
   resolver tarefa sem alvo/estado/comportamento esperado. `Y002` (`:9`,
   dev) e `Y040` (`:31`, reserved) repetem grafia em comentário de artefato
   executável com a execução preservada. A troca de substantivo não comprova
   independência de mecanismo. Rubrica `:58`–`:59` proíbe repartir quase
   paráfrases. Não se conclui que toda similaridade entre classes seja vazamento:
   a exigência relevante é retirar/repartir esses esqueletos recorrentes,
   não proibir qualquer exemplo de uma mesma classe nos dois conjuntos.
   `Y007`, `Y027` e `Y014` do parecer reforçam a proximidade, sem prova
   adicional independente de que todos devam ser substituídos.

3. **CONFIRMADO — Y006 contradiz a precedência.** `amostra.json:17` garante
   mesmas saídas/algoritmo e ausência de leitura entre atribuições idênticas.
   A regra 4 da rubrica (`:29`) classifica edição local sem efeito funcional
   como trivial antes da regra 5. Gold pequeno penaliza quem segue a rubrica.
   Corrigir o caso ou o contrato e preservar o balanceamento requer nova
   candidata; não editamos o conjunto congelado.

As linhas acima foram resolvidas pelos IDs no JSON atual; o parecer cita
algumas linhas aproximadas. Nenhum ID, exemplo ou gold foi alterado.

## Auditoria dos onze riscos do parecer

| ID | Classificação e evidência |
|---|---|
| R1 | **CONFIRMADO como limitação conhecida.** Y046/Y034 são off-by-one nas duas partições; `resultado-local.md:48` já registra a proximidade residual. Não chamar Jaccard baixo de independência semântica. |
| R2 | **DESCARTADO como quebra de protocolo comprovada.** Y013 (`amostra.json:47`) explicita contrato vigente que exige total e ramo defeituoso Total. Reparar aderência ao contrato fechado não introduz automaticamente compatibilidade nova. O cenário de consumidores dependendo do bug não está no caso. |
| R3 | **CONFIRMADO como ambiguidade textual.** Y038 (`amostra.json:20`) pede strip ausente conforme contrato, mas “rejeições atuais” pode incluir justamente rejeições erradas que o reparo muda. Deve dizer rejeições previstas no contrato; não transforma por si só o reparo em alto risco. |
| R4 | **PARCIAL.** Y047 (`amostra.json:42`) preserva nomes/números/formato consumido e o motivo diz prosa humana. O pedido não explicita onde a prosa vive; estreitar isso ajuda, mas não foi demonstrado efeito executável. |
| R5 | **DESCARTADO como alto risco demonstrado.** Y009 (`amostra.json:13`) trata exportação fictícia, exclui mudança de permissões/produção e pede sequência não sensível. Confirmação de interface não equivale automaticamente a controle de segurança/consentimento legal. |
| R6 | **CONFIRMADO como viés de calibração.** Y012/Y027/Y037 se parecem com exemplos da rubrica `:42`–`:46`. Dev pode ser usado para calibrar, mas seu acerto não deve ser vendido como generalização cega. Já é estudo exploratório; não desclassifica sozinho todo o reservado. |
| R7 | **CONFIRMADO como limite estrutural.** `preflight.py:62` compara espectros globais; não barra todo par de famílias espelhadas nem prova independência semântica. Não usar essa guarda como oráculo de conteúdo. |
| R8 | **CONFIRMADO — documentação incompleta.** `preflight.py:27` contém Y026 em CONTROLS; `resultado-local.md:22`–`:25` lista os outros cinco. Contagens/amostra não dependem de retirar esse controle. |
| R9 | **LIMITE FUTURO, não envio prematuro atual.** `preflight.py:68` é explicitamente dry-run, sem congelamento/transmissão; `resultado-local.md:58`–`:61` declara lotes não congelados/autorizados. O transportador futuro deve exigir selos e ordem; essa função não fez envio nem concede autoridade. |
| R10 | **PENDÊNCIA DE FASE, não hash corrompido.** Rubrica `:62` exige selos separados para pedidos/gold antes de medir. Candidata ainda sem aprovação, explicitamente não congelada (`resultado-local.md:61`, `:88`). Não declarar esse requisito cumprido nem despachar classificação antes dele. |
| R11 | **FRAGILIDADE CONFIRMADA, não regressão atual.** `test_mutations.py:15`–`:40` usa alvos literais e 13 testes focais fixos. Refatoração exige atualizar bancada; erro de aplicação é separado de mutante morto em `:32` e `:41`. Não contamos erro de harness como defeito detectado. |

## Limites e próximo gate

As seis limitações “não verificável” foram preservadas. Esta auditoria não
comparou v1/R3 nem demonstrou anterioridade do manifesto. Os hashes atuais
e IDs/linhas foram reconferidos; nenhum benchmark, JEV/Luna, chaveiro ou
serviço de produção foi acessado. A2 segue JEV 0/4 e Luna 0/4; B2 0/16.

Recomendação: preparar nova candidata com variedade lexical, independência
semântica real e Y006 coerente; resolver ambiguidades/documentação confirmadas
sem trocar as contagens/famílias silenciosamente. Executar gates locais antes
de pedir uma revisão nova. Correção e R5 externa exigem escopo próprio; não
reutilizar o gate consumido desta R4 nem chamar o gabarito de aprovado.
Sem bump, commit, push, integração, publicação, instalação ou restart.
