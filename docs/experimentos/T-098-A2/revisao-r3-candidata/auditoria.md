# T-098 A2 — auditoria da revisão R3

## Decisão do Manager

**NO-GO para congelar os payloads de classificação ou executar a campanha.**
A única chamada autorizada terminou; não foi repetida. O acesso à Claude CLI
foi recuperado pela autenticação única confirmada no navegador. A causa da
indisponibilidade anterior continua não comprovada.

O recibo registra uma chamada concluída, CLI/runner exit 0, um turno e
`modelUsage` exatamente `claude-opus-5-5`. A resposta do modelo cercou o JSON
com Markdown: **formato inválido**, embora o corpo extraído para diagnóstico
declare `BLOCKED`, 48 casos avaliados e oito problemas. Essa extração não
converte a resposta em aprovação nem autoriza retry. `recibo.json` conserva a
saída original; `resposta.txt` remove apenas o marcador conhecido do envelope
local, não as cercas produzidas pelo modelo.

O custo de tabela informado pela CLI foi **US$ 0,2091782**. Não é prova de
cobrança efetiva ou consumo percentual da assinatura. O contrato da invocação
e seus limites estão em `contrato-invocacao.md`. Zero retries do orquestrador
não comprova zero retries de transporte internos à CLI/SDK.

## Integridade e autoridade

- Pacote enviado: 16.115 bytes; SHA-256
  `a1500809c056cebdbee2953b38211fe20d33f81c0331155fdf9d287fdb1fdcf6`.
- Amostra preservada: SHA-256
  `8cc2e3b5225cb59fa869de66b466912fb607781d6ba587761e874492f7f987e1`.
- 48 casos fictícios, seis classes, 12 famílias. O autor conhece ambas as
  partições: o estudo não é cego.
- JEV/Luna A2 permanecem **0/4 cada**; B2 permanece **0/16**. Não houve nova
  classificação, congelamento final, adoção de roteador ou mudança de elenco.
- Rubrica normativa: `docs/T-098-rubrica-v2.md`, especialmente o congelamento
  3 (famílias inteiras e ausência de quase paráfrases entre partições) e o 5
  (payload sem gabarito, partição ou pistas administrativas).

## Auditoria dos oito problemas

| Referência do parecer | Classificação do Manager | Evidência e consequência |
|---|---|---|
| X017 / X021 | CONFIRMADO | Reservado/desenvolvimento repetem promoção a produção, destruição do estado anterior e ausência de rollback. A partição mede reconhecimento do mesmo molde. |
| X001 / X029 | CONFIRMADO | Repete-se o envio de material confidencial com identificadores a serviço externo, trocando registros por eventos. |
| X035 / X046 | CONFIRMADO | Ambos alteram coluna de schema e migram dados dependentes; separação por domínio não cria independência. |
| X011 / X010 | CONFIRMADO | Ambos retiram verificação de acesso para permitir qualquer chamada/usuário. Gabaritos individuais adequados não consertam a partição. |
| X043 / X042 / X041 | CONFIRMADO | Pedidos vagos de retorno ao estado anterior repetem o mesmo gatilho lexical nas duas partições. |
| X033 e demais pequenos | CONFIRMADO COMO FRAQUEZA METODOLÓGICA | Os oito pequenos usam alteração determinada de valor em configuração única; trivial/consulta também têm moldes muito regulares. Faltam controles mínimos de risco com vocabulário semelhante. Não foi medido um erro de classificador nesta etapa. |
| X039 e famílias espelhadas | PARCIAL | As 12 famílias têm quatro classes distintas; famílias reservadas repetem o multiconjunto das correspondentes de desenvolvimento. A artificialidade é real. **Vazamento direto ao classificador não foi observado:** o protocolo proíbe enviar família, gold, reason e split, usando somente `id`/`text`. |
| X031 | CONFIRMADO COMO AMBIGUIDADE | “Desenhe ... uma simulação” permite projeto/esboço ou implementação de cálculo e estados. Tornar a ação inequívoca; não declarar o rótulo isolado errado sem essa decisão. |

Também se confirmam lacunas de cobertura: leitura que expõe dados protegidos,
patch mínimo de alto risco, alto risco sob urgência e edição de Markdown que
altera política/comando. “Poucas linhas” e “só leitura” não podem ser atalhos
para baixo risco. Nenhum dado real ou protegido foi incluído no envio.

O parecer não identificou outros conflitos individuais de rótulo. Isso não
supera a falta de independência da amostra nem comprova assertividade,
segurança estatística ou economia.

## Próximo passo proposto — somente local

1. Preparar uma **nova candidata**, preservando amostra, pacote e recibo R3.
2. Separar famílias por mecanismo de tarefa, não apenas por substantivo/domínio;
   eliminar quase paráfrases cruzadas e os multiconjuntos espelhados.
3. Acrescentar controles contrastivos de risco, variar o vocabulário dentro das
   classes e remover a ambiguidade de X031, mantendo gabaritos justificáveis.
4. Conferir cobertura, recomposição e allowlist do futuro payload; não chamar
   a amostra de cega nem abrir classificação enquanto a revisão estiver bloqueada.

**Nenhuma dessas correções foi implementada neste checkpoint.** Novo envio
externo exige autorização do novo pacote, bytes, destino, teto e contador;
não é retry automático desta R3. Sem commit, push, integração, publicação,
instalação ou restart.
