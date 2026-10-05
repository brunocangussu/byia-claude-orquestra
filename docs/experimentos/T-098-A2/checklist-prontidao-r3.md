# T-098 — prontidão local para o piloto JEV R3

Data: 2026-09-29. **Preparação, não ativação nem autorização de egress.**
Este complemento não altera casos, rótulos, rubrica, partições ou recibos.

## Estado comprovado

| Item | Evidência atual |
|---|---|
| Candidata R3 | 48 IDs únicos; seis classes com oito casos cada |
| Partições | Quatro casos por classe em cada partição |
| Famílias | 12; quatro classes por família; nenhuma atravessa partições |
| Integridade da candidata | SHA-256 `8cc2e3b5225cb59fa869de66b466912fb607781d6ba587761e874492f7f987e1`, reconferido |
| Acesso histórico | Piloto HTTPS de 24/09 com HTTP 200 e `jev-1.13.0`; não revalidado por nova chamada |
| Classificação A2 | JEV 0/4 e Luna 0/4; não confundir com o piloto histórico |
| Aprovação independente do gabarito R3 | Pendente |
| Executor da revisão R3 | `claude auth status` indisponível nesta sessão Codex, tanto via context-mode quanto execução direta; sem inferência/reautenticação. Ver `preflight-cli-status-local.json` |
| Payloads finais, hashes separados e orçamento R3 | Pendentes após a aprovação do gabarito |

O cabeçalho antigo da thread sobre acesso pendente estava desatualizado:
o próximo obstáculo não é gerar outra chave nem refazer login. É validar a
amostra e delimitar a próxima execução. A disponibilidade atual da credencial
não foi presumida nem testada lendo seu valor.

## Contrato público revalidado

As fontes primárias [API](https://docs.typesafe.ai/api) e
[modelos](https://docs.typesafe.ai/models) foram consultadas novamente:

- Endpoint: `POST https://api.typesafe.ai/v1/systemone`.
- Modelo fixado: `jev-1.13.0`, sem alias mutável `jev-latest`.
- Entrada: `state` e mapa de `questions`; cada pergunta Choice tem
  `type`, `instructions` e `criteria`.
- Resposta: `model`, `answers` pelos mesmos IDs e `usage`; Choice inclui
  `choice`, `probabilities` e `confidence`.
- Preço publicado: US$ 0,042 por milhão de tokens de entrada; saída gratuita.
- Limites publicados: 64 mil tokens por requisição, 32 mil para o estado
  somado à pergunta mais longa. Bytes não substituem contagem de tokens.
- O SDK faz retry com backoff por padrão. O ensaio deve usar HTTP direto,
  sem retry nem redirecionamento, para não exceder as chamadas autorizadas.

Preço/limite são dados consultados nesta data, não autorização de consumo
nem garantia de disponibilidade futura. Antes de enviar, reconferir preço,
modelo, orçamento e identidade exata do pacote autorizado.

## Ordem do próximo trecho

1. Revisão independente recebe somente casos/gabarito/razões e rubrica,
   sem previsões ou métricas de classificadores. Registrar formato e
   veredito; o Manager audita os achados. Correção substantiva gera outra
   candidata, nunca alteração depois de medir.
2. Após aprovação, congelar separadamente textos, gabarito, rubrica,
   regra local, partições e payloads. Preparar quatro lotes de 12 casos.
   Revisão e inferências têm contadores e custos separados.
3. Construir payloads por **allowlist `id`/`text`**: nunca serializar o objeto
   completo e depois tentar remover `gold`, `reason`, `family` e `split`.
   Não transmitir resultados de outro classificador nem contexto pessoal.
4. Antes de cada chamada, conferir SHA-256 do payload autorizado, modelo,
   teto de tokens/custo e contador persistido. Ler a credencial apenas no
   processo de transporte, sem imprimir ou persistir seu valor.
5. Uma tentativa por lote. Timeout, HTTP 401/429/5xx, modelo divergente,
   resposta incompleta ou inválida são falhas registradas, não autorização
   para retry, login, upgrade ou modelo substituto.
6. Validar antes de pontuar: modelo exato; todos e somente os IDs esperados;
   Choice entre as seis classes; probabilidades finitas, no intervalo e
   normalizadas; confidence finita no intervalo; uso presente e válido.
   Preservar resposta original e custo reportado/calculado separadamente.
7. Só depois comparar risco crítico, abstenção, erro por classe/partição,
   tempo e custo por decisão. O teste B mede custo até entrega aceita;
   acerto de classificação ou preço baixo não prova economia de execução.

## Autoridade preservada

Na adoção inicial, JEV apenas recomenda em shadow mode. Não executa código,
escolhe modelo instalado, concede permissões ou reduz o piso de alto risco.
O Manager decide com regras locais e capacidade comprovada por via.
Decisions permanece alternativa sem contrato técnico verificado; não pode
virar fallback silencioso. T-131 trata elenco; T-139, especialização; T-141,
portabilidade ao Orca. Não misturar adoções nem alterar seus ensaios congelados.

Sem nova chamada, mudança de gabarito, congelamento final, egress, ativação,
bump, commit, push, publicação, instalação ou restart neste complemento.
