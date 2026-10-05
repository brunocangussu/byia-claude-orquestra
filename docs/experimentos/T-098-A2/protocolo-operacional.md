# T-098 A2 / T-138 — protocolo operacional e ledger

## Autoridade e escopo

O “prossiga” aprovou avançar o piloto seletivo, não a instalação de Agency Agents nem a adoção
do JEV. Esta preparação permanece fora de `orq/`, dos caches, das configurações e do elenco.
Sem bump, commit, push, integração, publicação ou restart. O snapshot v1 permanece intocado.

Após compactação, foram relidos índice, board canônico e threads T-098/T-138, com pacote
`/Users/brunocangucu/.codex/plugins/cache/orquestra/orq/0.27.10` existente e resolver `state=ok`.
Frente dona reafirmada: `@frente-jev-router @codex`. Não se assume trabalho do T-131/T-137.

## Orçamento explícito de chamadas

| Etapa | Modelo/via | Teto | Estado |
|---|---|---:|---|
| Autoria independente da amostra | Terra `gpt-5.6-terra@xhigh`, CLI Codex, read-only | 1 chamada | Autorizada e executada; estrutura válida, conteúdo reprovado depois |
| Revisão independente do gabarito | Opus, CLI Claude pelo runner canônico, read-only/sem ferramentas | 1 chamada | Autorizada e executada; Opus 5.5, BLOCKED, formato cercado por Markdown |
| Classificação | JEV `jev-1.13.0`, TypeSafe HTTPS | 4 chamadas; US$ 0,02 | Não executada; depende de amostra/gabarito válidos |
| Classificação | Luna `gpt-6-luna@low`, CLI Codex, sem ferramentas | 4 chamadas | Não executada; depende de amostra/gabarito válidos |
| Entregas 2×2 | Catálogo e via de escrita ainda por provar | 0 nesta etapa | Não despachar as 16 execuções propostas |

As duas chamadas de preparação **não estavam nas oito de classificação**. Foram apresentadas
ao dono separadamente e autorizadas; não serão escondidas no custo por decisão. Não haverá retry, substituição
de modelo nem divisão em chamadas extras se um resultado vier inválido. CLI usa a autenticação
existente, não token manual. Indisponibilidade não autoriza login, upgrade ou restart.

Se o dono preferir manter somente oito chamadas, registrar **estudo exploratório com gabarito
do autor**, não avaliação independente. Essa alternativa não pode ser adotada silenciosamente.

## Ordem e separação de informação

1. Congelar a rubrica v2, briefing do autor, critérios da revisão e formato dos dados.
2. Autor fresco recebe somente rubrica, restrições de ficção e esquema. Não recebe casos,
   resultados, erros ou prompts v1; não recebe conteúdo real de repositório.
3. Validar estrutura sem imprimir pedidos/gabaritos reservados na sessão principal. Persistir
   a resposta original, metadados de autoria e hashes antes de qualquer correção.
4. Revisão cross-vendor recebe casos e gabarito proposto, mas nenhum resultado de classificação.
   Avaliar aplicação da rubrica, ambiguidades, equilíbrio e vazamento entre famílias.
5. Achado substantivo ou formato inválido interrompe o despacho. Não chamar de “aprovado” um
   parecer incompleto nem fabricar consenso por revisão do próprio autor.
6. Congelar pedidos, gabarito, partições, prompts e regra local separadamente. Lotes 1/2 são
   desenvolvimento, 3/4 reservados. Cada lote contém 12 casos, sem identificadores de classe.
7. Enviar a cada classificador apenas `id` e `text`, a mesma rubrica e escolhas. Não enviar
   rótulos esperados, justificativas, split, famílias, resultados de concorrentes ou métricas.
8. Guardar respostas antes de pontuar. Abrir o reservado só após congelar os consumidores.
   Não ajustar prompts/regras após ver respostas reservadas. Caso isso aconteça, invalidar
   a alegação de validação reservada; preservar os números como exploratórios.

“Reservado” significa separado do ajuste. A autoria sintética por modelo não vira amostra real
de produção, e um parecer independente não prova que o conjunto representa o uso do dono.

## Preflight antes das oito chamadas

- Conferir preço/modelo/contexto na documentação oficial da TypeSafe; fechar estimativa abaixo
  de US$ 0,02 para o conjunto, incluindo todas as perguntas. Não inferir preço atual do recibo v1.
- Confirmar IDs e versions das CLIs sem executar outra inferência. Fixar `low` no Luna.
- Endpoint TypeSafe exclusivo, TLS validado, sem redirects, proxies herdados, SDK ou retries.
  Chave apenas em memória e no header autorizado; nunca em prompt, argumentos ou recibos.
- No Codex, sessão efêmera, configuração de usuário ignorada, read-only e entrada sem TTY;
  nenhum uso de ferramenta pelo classificador. Recusar recibo com chamada de ferramenta.
- Tempo máximo por lote: JEV 45 s; Luna 180 s. Uma tentativa por lote. Se houver falha de
  transporte/capacidade, parar a campanha e distinguir “tentado sem resultado” de “não enviado”.
- Status 200/exit0 não bastam: conferir modelo efetivo, conjunto exato de IDs, classes permitidas,
  ausência de duplicatas, resposta completa e campos numéricos válidos antes da pontuação.
- Probabilidades não são autoridade nem confiança calibrada. Primeira A2 sem limiar aprendido;
  reportar o rótulo `abster` e a distribuição. Qualquer limiar futuro requer novo protocolo.

## Métricas e decisões

Acerto por classe/partição, matriz de confusão, alto risco rebaixado, abstenções úteis/excessivas,
diferenças pareadas contra regra local, respostas inválidas e chamadas não concluídas. Sempre
informar os denominadores; não excluir exemplos ambíguos depois de medir sem identificar análise
pós-hoc. Intervalos binomiais acompanham taxas, sem alegação de poder estatístico com 24 reservados.

Registrar input/output/cache/raciocínio quando disponível, latência, chamadas preparatórias e
consumo total. Preço de tabela, cobrança da API e cota de assinatura são coisas distintas.
Ainda não mede economia **por entrega aceita** nem eficácia do perfil API Tester. Isso é a B2.

## Ledger de execução

- Recuperação: fontes canônicas verificadas; não houve perda nem limpeza de worktrees.
- Preparação: perfil local API Tester v1 e protocolo criados; nenhum perfil instalado.
- Desvio identificado antes do despacho: autoria/revisão consomem duas chamadas além das oito;
  solicitada decisão explícita, depois concedida pelo “autorizo”.
- Estado inicial: zero chamadas. Estado após autorização: autoria 1/1 e revisão 1/1 consumidas;
  JEV 0/4, Luna 0/4, B2 0. Amostra reprovada; não disparar inferências restantes.
- Verificação local: suíte por descoberta `414/414` em `51,225 s`, bytecode desativado;
  manifesto `--strict` e lint de coerência exit0. Links dos seis documentos de preparação válidos,
  `git diff --check` exit0 e fixture v1 com SHA original. Isso não mede a utilidade do perfil/JEV.
- Resultado posterior das duas chamadas e auditoria: [auditoria-revisao.md](auditoria-revisao.md).
  Não repetir nem corrigir silenciosamente o original. Revisão adicional exige novo limite do dono.
