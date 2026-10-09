# Continuidade orientada por evidências

Esta política governa correção/revisão e diagnóstico de estagnação. Não é
autorização de chamadas, alteração de escopo ou entrega Git.

## Rodadas e progresso

Não há teto global de duas rodadas. A terceira ou posterior pode ser necessária.
`review_rounds` é o total persistente; os recibos e o consumo nunca são zerados
para esconder custo. `stalled_rounds` mede apenas a sequência sem progresso.
Um teto explícito concedido pelo dono para um card ou envio continua valendo:
quando consumido, prepare o gate adicional e avance em outras ações locais elegíveis.
Sem limite externo e saldo comprovados, nenhuma chamada adicional está coberta.
A antiga regra operacional de duas rodadas não era autorização humana para duas
chamadas nem para uma terceira. Preserve a cobertura realmente aprovada, inclusive
gates antigos; não converta a retirada do teto global em renovação ou saldo implícito.

Duas rodadas consecutivas sem progresso verificável exigem diagnóstico e uma
abordagem diferente, não encerramento automático da meta ou da fila. Exemplos:
reproduzir a causa, tornar o teste discriminante, auditar o oráculo, aplicar
mutação ou decompor o bloqueador. Editar arquivo, mudar digest, repetir um parecer
ou zerar um contador não prova progresso. RED/GREEN, mutação detectada e
bloqueador auditado encerrado têm recibos próprios; o Manager os verifica.
Depois de executar uma estratégia diferente, registre o resultado. Só o Manager,
após auditar um recibo novo de progresso real, pode registrar `stalled_rounds=0`;
sem progresso confirmado a sequência continua. Isso não reinicia `review_rounds`
nem o saldo de chamadas externas. Nenhuma resposta JEV ou presença autodeclarada
de hashes altera o contador; o helper recebe o estado já auditado e não o grava.
Diagnóstico por estagnação exige pendência local real e autoridade local. Testes
verdes e review aprovado do snapshot atual seguem para validação do dono, mesmo
se o contador antigo ainda for 2; testes verdes sem review seguem para seu gate,
não para um diagnóstico local sem autorização.

Um parecer atual `blocked` com zero bloqueadores confirmados ainda exige
auditoria local dos achados (`audit_review_findings`), não nova chamada nem
aprovação tácita; zero pode significar achados ainda não auditados ou rejeitados
pelo Manager. Sem autoridade local, prepare esse gate. Parecer `unavailable`
do snapshot atual exige gate humano próprio de nova tentativa, mesmo com saldo
genérico em outro gate. O helper sugere `prepare_review_gate`; não faz retry,
não reclassifica a falha como review ausente e não renova o saldo. Review antigo
não é aprovação do snapshot novo; cobertura externa deve ser auditada para os
bytes/modelo/destino reais antes de qualquer despacho.

Sem ação útil dentro da autoridade existente, estacione somente a dependência
com a pergunta concreta; continue as demais frentes aprovadas. Respeite parada
humana, orçamento de tempo/custo, proteção de dados e limites reais do host.

## Apoio local e JEV

O helper offline `ORQ_PACKAGE_ROOT/scripts/work_evidence.py` recebe metadata
tipada, verificada pelo Manager; não interpreta código nem certifica recibos.
O Manager pode usá-lo para organizar a próxima ação de um card:

```bash
python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/work_evidence.py" recommend <evidencia.json>
python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/work_evidence.py" prepare-jev <evidencia.json>
python3 "<ORQ_PACKAGE_ROOT-resolvido>/scripts/work_evidence.py" interpret-jev <evidencia.json> <recibo.json>
```

Substitua `<ORQ_PACKAGE_ROOT-resolvido>` pelo caminho absoluto, existente e
comprovado do pacote carregado; é marcador explicativo, não variável exportada
nem comando literal executável. Resolva também os caminhos dos dois JSONs.

O schema está no validador do helper e em `test_work_evidence.py`. O arquivo de
entrada limita-se a risco, classe do defeito, lacuna, contadores, estado de
testes/review, digest do snapshot e referências hash de progresso auditado.
Não coloque briefing, código, caminhos privados, PII, credenciais ou logs.

`prepare-jev` só produz pacote tipado e digest: **não envia**, não lê chave,
não acessa rede e não autoriza consulta. O envio real depende de gate humano
próprio, pacote/destino/modelo/tetos registrados e capacidade de transporte
comprovada. Não instalar SDK ou outra skill por conta desse preparo.
O digest cobre exatamente `request_body_utf8` codificado em UTF-8 e o
tamanho está em `request_bytes`; o envelope local inteiro não é o corpo
HTTP. Transporte futuro deve usar esses bytes sem reserializar, incluir
LF ou reformar o JSON; conferir digest imediatamente antes do envio.
`interpret-jev` exige recibo vinculado ao pacote e modelo fixado
`jev-1.13.0`; mudança de snapshot invalida a sugestão antiga. O limiar local
de confiança 0,75 é uma política candidata, não calibração demonstrada.

JEV sugere prioridade entre opções admissíveis: causa raiz, novo teste
discriminante ou próxima revisão que já cabe no gate declarado. Não concede
permissões, rebaixa risco, dispensa testes/review, aprova release ou fecha card.
Mesmo uma resposta aceita continua consultiva e exige auditoria do Manager.
Resposta inválida, ausência, abstenção ou baixa confiança conserva as regras locais,
sem retry. O recibo distingue `abstained` (escolha explícita do modelo) de
`low_confidence` (escolha válida abaixo de 0,75), sem atribuir baixa confiança a
uma abstenção que não aconteceu.
Na CLI, recibo ilegível, inválido ou acima do limite preserva o baseline da
evidência válida com `advice_status: rejected` e exit 0; não ecoa conteúdo nem
repete a consulta. Evidência de entrada inválida ou argumento de recibo ausente
é erro de uso/estado (exit 2, `INVALID_INPUT`), sem recomendação inventada.

## Aceite e entrega

Correção local autorizada continua durante falha da via externa. Revisão
independente ausente/reprovada ou de snapshot antigo não equivale a aceite.
Sem ela, prepare pacote/gate; não mova o card para VALIDATE como aprovado.
Mesmo review e testes verdes não são DONE: o dono valida o produto.
Esta política não cancela exigências de bump, commit, publicação, instalação
ou teste comportamental; cada uma mantém sua autoridade própria.

O formato acima é um contrato local candidato, com fixtures sintéticas; os testes
não comprovam aceitação pelo serviço nem benefício comparativo. A
[referência pública Typesafe](https://docs.typesafe.ai/introduction/quickstart)
é somente um ponteiro para conferência futura: este snapshot não homologa a
origem do URL, o contrato remoto, a capacidade ou o modelo do serviço. Essa
conferência e qualquer ativação real exigem seus gates próprios.
