# T-098 A2 — auditoria da segunda revisão

## Resultado e limite

A correção local produziu [amostra R2](amostra-r2.json), sem sobrescrever a
[proposta R1](amostra-proposta.json). O conjunto manteve 48 IDs, oito por classe,
quatro por classe/partição e 12 famílias sem atravessar partições. Textos e
justificativas respeitaram os limites de bytes; a varredura preventiva do
[pacote enviado](revisao-r2-pacote.txt) não encontrou caminhos pessoais, URLs,
e-mails nem sequências longas de dígitos. O pacote tem 10.046 bytes UTF-8.

Foi feita **uma única chamada** ao runner canônico do Claude CLI, com alias
`opus`, sem ferramentas e sem retry do Manager. Modelo efetivo
`claude-opus-5-5` provado por `modelUsage`; exit 0 em 45,717 s.
O [parecer literal](revisao-r2-parecer.json) veio em JSON cru válido, declarou
48 casos revisados e decidiu `BLOCKED`. [Recibo estruturado](revisao-r2-recibo.json),
[registro de execução](execucao.json) e [resultado R2](resultado-r2.json)
preservam modelo, uso, hash e contadores; o [snapshot R2](snapshot-r2.json)
amarra os três artefatos por SHA-256. O `resultado-preparacao.json`
continua como retrato da R1, não como estado atual.

## Auditoria dos cinco apontamentos

| ID | Juízo do Manager |
|---|---|
| X001 | **Parcial.** O classificador recebe apenas texto e ID, não recebe nome de família nem split; portanto não há vazamento direto desse metadado. Mas cada família da R2 tem uma única classe, e sua redação foi criada por moldes de classe. A correlação textual espúria continua um bloqueio metodológico. |
| X029 | **Confirmado como molde, não como paráfrase semântica.** Corrigir constante e corrigir soma são ações diferentes, mas `pequeno` usa `No arquivo …` em 8/8; `abster` usa dêiticos e `trivial` usa citações. A forma prevê o rótulo sem exigir leitura do efeito. |
| X046 | **Confirmado.** “Chaves” pode ser credencial, logo o pedido de compartilhamento pode cair em `alto_risco` antes de `abster`. Falta uma distinção explícita para sustentar o gabarito. |
| X015 | **Confirmado.** Troca de cor documentada pode ser textual/visual sem efeito funcional. O gabarito `pequeno` não é inequívoco frente a `trivial`. |
| X004 | **Confirmado como cobertura desigual.** Alto risco em dev concentra segurança, enquanto reserved concentra schema/produção/exclusão/dados. O ensaio não permite extrapolar calibração de um subtipo para outro. Não há caso de dependência nova. |

Os três problemas de gabarito/forma (X029, X046, X015) e a cobertura de risco
são suficientes para manter o gate vermelho; o ponto parcialmente refutado
de X001 não altera o veredito. Não apresentar o parecer como prova de
desempenho de JEV, Luna ou do Agency Agents.

## Consumo e próximo limite

O CLI reportou 193.823 tokens de criação de cache, 4.288 de saída
(3.040 de thinking), dois tokens de entrada não-cache e US$ 1,636352 de
**tabela**. Isso é aproximadamente dez vezes o custo de tabela da R1
(US$ 0,1584622), apesar de pacotes comparáveis; o motivo não está provado.
Não equivale a cobrança da assinatura. Investigar essa contabilidade antes de
solicitar outra revisão externa, sem assumir que o texto do pacote causou tudo.

**JEV A2 0/4; Luna A2 0/4; B2 Agency Agents 0/16.** A revisão extra aprovada
foi consumida e não haverá retry. Uma futura candidata precisa variar a
redação dentro das classes, equilibrar subtipos de risco entre partições e
eliminar os dois gabaritos ambíguos. Nova revisão/model call exige gate próprio.
Nenhum produto, elenco, cache, configuração, release ou serviço foi alterado.

## Pré-auditoria local adicional — 2026-09-26, sem chamada externa

Os arquivos de pacote enviados batem com os digests dos recibos: R1 teve
9.723 bytes e R2, 10.046 bytes (+323, ~3,3%). Os recibos indicam **uma**
chamada em cada rodada, mesmo modelo efetivo `claude-opus-5-5` e duração
comparável (~45 s). A criação de cache saltou 7.731 → 193.823 tokens
(25,07×); o custo de **tabela** informado, US$ 0,1584622 → US$ 1,636352
(10,33×). Assim, nem o tamanho do pacote nem retry explicam sozinhos o salto.
O runner usa `--tools ""`, `--setting-sources ""` e
`--no-session-persistence`, mas o recibo não preservou cwd, ambiente
allowlisted nem a lista de mensagens visíveis ao modelo. **Causa raiz
indeterminada:** contexto extra e contabilização do CLI são hipóteses, não
achados confirmados. Antes de outra revisão, registrar essas três superfícies
localmente, sem gravar credenciais/PII; não repetir Opus só para medir custo.

Na R2, cada uma das 12 `family` contém casos de uma única classe `gold`.
Embora o protocolo não envie `family` ao classificador, isso torna o metadado
inadequado para alegar independência semântica por família. Além disso, os
oito casos `pequeno` começam com “No ”, contra três dos outros 40. Nos oito
`alto_risco`, todos os quatro `dev` tratam acesso/credencial; os quatro
`reserved` cobrem schema, produção, destruição ou dados pessoais. A partição
reservada mede subtipos que a calibração não viu. X015 pode ser só visual
(`trivial`); X046 usa “chaves”, que pode significar credenciais e atrair
`alto_risco`. Esses dados sustentam o bloqueio da R2 sem consultar JEV/Luna.

**Proposta para uma R3 candidata, ainda não criada nem aprovada:** preservar
os 48 IDs, oito casos por classe e quatro por classe/split; desenhar famílias
por domínio com várias classes (idealmente quatro), em vez de família→classe;
variar construções
lexicais dentro de cada classe; distribuir acesso, schema, produção/destruição
e dados/credenciais entre os dois splits; reescrever X015 como mudança
funcional de um arquivo ou rotulá-lo trivial com distribuição compensada;
remover de X046 toda leitura plausível de credencial. Congelar texto, razões,
IDs, hashes e regras antes de qualquer revisão nova. Essas verificações são
necessárias, não suficientes: ainda caberá parecer independente com limite
de custo e autorização separados.

### Reprodução exploratória da regra congelada

Reproduzi localmente `regras-locais.json` sobre a R2, com normalização NFD,
remoção de marcas combinantes, minúsculas, espaços reduzidos e primeira
expressão regular correspondente. O resultado foi 13/24 no `dev`, 14/24 no
`reserved` e 27/48 no total. Por classe: `alto_risco` 5/8, `consulta` 7/8,
`normal` 7/8, `trivial` 0/8, `pequeno` 0/8 e `abster` 8/8. Não ajustei a regra
nem a amostra após observar os erros.

Isto **não é placar válido do benchmark**: o `reserved` já foi aberto nesta
auditoria, o gabarito R2 permanece contestado e não houve ensaio de JEV ou
Luna. Serve somente para mostrar a distribuição de falhas da regra local e
evitar a conclusão oposta, igualmente indevida, de que os moldes textuais
implicam acerto automático. A futura amostra precisa ser congelada e
revisada antes de qualquer nova inferência.
