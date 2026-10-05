# Correção local pós-R4 — T-131 e T-098

2026-10-02. **Aprovado pelo dono ("aprovo..."); ainda não implementado.**
O pedido simultâneo de resolver as interrupções virou prioridade máxima T-143;
T-131/T-098 permanecem aprovados para o escopo local abaixo, atrás dessa prioridade.
Preparação dentro da meta persistente. R4 do T-131 e R4 do T-098 foram
executadas uma vez cada e estão consumidas. Nenhuma nova chamada será feita
por este documento. A aprovação local abaixo não inclui revisão R5/egress,
classificação JEV/Luna, adoção, autenticação, bump, Git, release ou restart.

## Autoridade e isolamento

- T-131 permanece na branch/worktree codex/t131-elenco-sol61-luna6.
  Não tocar claude/t089-companion-identidade, o elenco ativo na main,
  MEMORY.md ou fixes-history.md protegidos.
- T-098 permanece na frente dona; nova candidata pós-R4 fica em diretório
  novo, candidata-r5-local. R3/R4, seus pacotes, inventários, amostras e
  pareceres históricos não são reescritos.
- Só o Manager move os dois cards após aprovação explícita. Preservar
  @frente e @codex; não ativar modelos por aprovação de código.
- Esta é proposta técnica do Manager baseada no parecer externo auditado,
  não um novo planner/reviewer independente ou uma nova revisão.
- Ler o estado de disco antes de cada patch. Nenhum git add ., restauração
  de dirty tree, amend, reserva de versão ou instalação.

## T-131 — dois bloqueadores e três riscos técnicos confirmados

1. **Separar candidato de ativo no template copiável.**
   Em orq/commands/elenco.md, preservar os gates e o status de fábrica na
   prosa externa ao bloco canônico. Dentro do bloco que init copia, usar
   linguagem neutra de configuração e recibo, sem “Proposta de fábrica,
   não elenco ativo”, “candidato” como status ativo ou “requer prova” de
   mecanismo já exercitado. Isso não deve afirmar saúde automática nem
   dispensar a verificação de sessão/modelo/via.
   Guardas: extrair o bloco real pela função _bloco_canonico_elenco;
   reprovar reintrodução de status transitório na seção de host copiada.
   Preservar tabelas e snapshots dos papéis que a operação não altera.

2. **Defaults sem ambiguidade.**
   Corrigir a passagem README.md:301: fábrica do elenco usa ID explícito
   5.5, mas o runner sem --model mantém opus legado. Não mudar o default
   nem o mapa de aliases por esta correção.
   Estender as guardas aos trechos correspondentes de README.md, stack.md
   e revisar.md; normalização de case/espaço não pode esconder contradição.
   Mutações: reintroduzir default candidato como default do runner em
   cada consumidor deve falhar no teste certo, não por erro de bancada.

3. **Privacidade — fortalecer o oráculo, sem alegar vazamento real.**
   Em test_opus_diagnostics.py, validar os recibos JSON decodificados,
   inclusive escapes Unicode, além da saída literal. O payload sintético,
   os marcadores fictícios de segredo/PII e campos livres de erro não
   devem reaparecer no diagnóstico. Saída de parecer legítimo é distinta
   da telemetria: não banir conteúdo autorizado do próprio parecer.
   Mutação offline: introduzir briefing em campo de diagnóstico com
   json.dumps/ensure_ascii=True deve reprovar. Sem segredo/PII real.

4. **Init — cláusulas delimitadas, completas e na etapa correta.**
   Em test_elenco_perfis.py, extrair a etapa 2b real de init.md; não basta
   achar termos em outro parágrafo. Guardar validação de todos os papéis
   novos, escopo limitado em elenco existente, preservação integral,
   proibição de semear presets/headings/fallback e ausência de autorização
   implícita para prova. Remoção e deslocamento de cada cláusula relevante
   devem ser detectados por contrafactuais focais e pela suíte completa.

5. **Subtipo futuro — política fail-closed explícita.**
   Em run-opus-reviewer.py e testes, manter aliases e identidade exata 5.5.
   Proposta: aceitar success ou ausência legada de subtype somente quando
   o restante do envelope satisfizer os contratos; subtipo presente não
   reconhecido não vira parecer, mesmo com is_error=false e modelo/result.
   Definir saída sanitizada/exit usando os contratos OPUS_ existentes, sem
   expor mensagem bruta, sem retry e sem inventar request/custo.
   Essa alteração de aceitação de schema exige a aprovação deste plano:
   ainda não foi aplicada. Testar ausência legada, success, erro conhecido,
   subtipo desconhecido e tipo de campo inválido; tudo com CLI falsa.

Não alterar por conveniência: aliases legados, identidade exata, estado do
elenco ativo, fallback, gate de capacidade ou comportamento do Companion.
Os demais riscos R1/R2/R6/R7/R8/R10/R11 permanecem separados: documentar
limites confirmados, sem transformar hipóteses/estilo em implementação extra.

## T-098 — nova candidata, três bloqueadores e ambiguidades confirmadas

1. Manter 48 casos fictícios, seis classes, oito por classe, 24 dev/24
   reserved e quatro por classe em cada partição. Famílias indivisíveis:
   o manifesto de 18 mecanismos não deve ser alterado silenciosamente.
2. Reescrever exemplos em nova candidata para quebrar exclusividade de
   marcadores lexicais em cada classe e partição. Não resolver trocando
   regex por sinônimos igualmente exclusivos; usar os mesmos marcadores
   em classes diferentes com ação/escopo explícitos.
3. Eliminar esqueletos quase idênticos Y044/Y042 e Y002/Y040 entre
   partições, e auditar os demais pares apontados. Registrar mecanismo
   de cada exemplo e a comparação cruzada; substantivo/domínio e Jaccard
   baixo não são prova de independência.
4. Substituir Y006 por reparo de comportamento observável e contrato
   existente fechado, preservando classe/contagem/família. Alternativa de
   relabel exige rebalanceamento documentado, nunca só ajustar o gold
   para favorecer um modelo.
5. Clarificar Y038 (rejeições previstas no contrato, não bugs atuais),
   delimitar a prosa estática de Y047 e listar corretamente o controle
   Y026. Preservar distinção entre interface/preview e controle de
   autorização; não promover Y009 a alto risco sem cenário real.
6. Acrescentar diagnóstico lexical local antes de qualquer despacho:
   regra definida somente com dev, recibo do congelamento da regra e
   pontuação reservada posterior. Como o autor conhece o conjunto,
   continuar chamando o estudo de exploratório. Não alegar cegamento,
   segurança estatística ou efetividade geral.
7. Descoberta de testes completa e mutações sintéticas locais. Guardas
   estruturais não aprovam o gabarito nem substituem revisão semântica.
   Projeção continua apenas id/text; nenhum transporte HTTP, Keychain,
   SDK/CLI de LLM ou autorização de execução é acrescentado.

Os selos finais separados de pedidos/gold, payloads de classificação,
preflight das vias e campanhas só vêm depois do gabarito aprovado e de seus
gates. JEV/Luna A2 permanece 0/4 por modelo; B2 permanece 0/16.

## Sequência e evidência exigida

1. Aprovação local única com este escopo, mantendo os gates externos fora.
2. Registrar RED focal antes de alterar cada causa; GREEN depois.
3. Mutações aplicáveis devem falhar por asserção contratual, não por erro
   de harness; guardar contrafactuais que sobrevivam em vez de descartá-los.
4. T-131: suíte discover de orq/scripts com PYTHONDONTWRITEBYTECODE=1,
   manifesto estrito, lint e diff-check. T-098: discover da candidata nova,
   mutações/cobertura/contagens e checks de projeção/hash.
5. Preservar a falha conhecida da main por checkout histórico; T-142
   registra esse problema em card próprio. Não editar/apagar o checkout
   nem mascarar a suíte para reportar tudo verde.
6. Gravar handoff/digests novos, confirmar fontes e protegidos. Só então
   preparar pacotes sanitizados integrais para a decisão de R5, com
   bytes/destino/modelo/teto/cobertura/contador atualizados.
7. R5 exige autorização própria e extensão quando aplicável. Qualquer
   reprovação/erro conta no orçamento autorizado; nenhum retry/fallback.

## Próximas fases do objetivo completo

Estas correções NÃO deixam JEV adotado. Ainda faltam revisão independente
válida do snapshot/gabarito, prova de capacidade das vias reais, aprovação e
congelamento da campanha, JEV/Luna contados, métricas de custo/efetividade,
gate de shadow mode e, se aprovado, avaliação de entrega com perfis B2.
Nenhuma etapa é substituída por testes locais ou status loggedIn.

## Aprovação recebida

O dono aprovou em 2026-10-02 as correções locais acima no T-131/T-098 com
RED/GREEN, mutações e gates, sem nova chamada externa, bump, commit, push,
integração, publicação, instalação ou restart. O T-143 é a prioridade máxima
antes desta execução. Não pedir de novo essa aprovação local. O gate de
envio das R4 continua consumido; revisão/classificação não foram autorizadas.
