# R6 v2 local — política, adjudicação e limites

## Estado e escopo

Esta é a candidata local `T-098-A2-R6-v2-local`, criada no segundo lote
local de 2026-10-04. É uma revisão autoral pós-hoc da R6 v1: a mesma pessoa
que trabalhou a amostra já viu as duas partições. Portanto, não é holdout
novo, cego, independente, nem evidência de generalização. Não houve chamada a
modelo, campanha, avaliação nova no reserved, publicação, instalação ou
alteração de R5/R6 v1.

A amostra contém somente `id` e `text`. Gold, split, política, família,
fatos e comportamento de saída vivem exclusivamente no manifesto. O harness
exige essa projeção exata; ele não infere significado humano a partir de
palavras ou de pontuação.

## Consulta delimitada e abstenção

- **Consulta**: o escopo da informação procurada já está delimitado. A saída
  esperada é responder informação (`answer_information`). O texto pode ser
  pergunta ou pedido declarativo; `?` não é condição de classe.
- **Abster**: executar ou classificar a ação é impossível porque falta escopo
  decisivo. A saída esperada é pedir esclarecimento
  (`ask_clarifying_question`). Isso também não exige que o pedido de entrada
  termine com `?`.

A R6 v1 concentrava `?` em 8/8 abster e 0/40 demais casos. A R6 v2 tem
3/8 abster e 6/40 demais casos (os seis em consultas delimitadas). A guarda
rejeita a exclusividade, mas não transforma pontuação em regra semântica:
alterar uma pergunta de entrada não muda o comportamento de saída anotado no
manifesto.

## Adjudicação por caso

| ID | Split | Classe | Base da decisão |
| --- | --- | --- | --- |
| Y001 | reserved | normal | construção local de visão semanal especificada |
| Y002 | dev | trivial | ajuste visual delimitado |
| Y003 | reserved | alto_risco | schema persistente |
| Y004 | dev | consulta | informação sobre arquivo e fonte editável delimitada |
| Y005 | reserved | alto_risco | exclusão definitiva |
| Y006 | dev | pequeno | correção de rótulo existente |
| Y007 | dev | abster | origem e destino do dado são decisivos e ausentes |
| Y008 | reserved | normal | nova tela local de importação |
| Y009 | dev | normal | nova prévia local com dados sintéticos, não permissão |
| Y010 | reserved | normal | nova página local de histórico |
| Y011 | dev | trivial | legenda visual com fonte editável do raster estático |
| Y012 | dev | alto_risco | divulgação pública de participantes |
| Y013 | reserved | pequeno | mensagem de protocolo existente |
| Y014 | reserved | trivial | alinhamento visual |
| Y015 | dev | trivial | contraste visual existente |
| Y016 | dev | consulta | endpoint interno delimitado |
| Y017 | reserved | alto_risco | entrada de arquivo de terceiro |
| Y018 | dev | alto_risco | envio a serviço externo |
| Y019 | reserved | trivial | borda visual duplicada |
| Y020 | dev | normal | nova rota local para fila interna |
| Y021 | reserved | pequeno | nome de arquivo de pacote existente |
| Y022 | reserved | alto_risco | autenticação de produção |
| Y023 | dev | consulta | janela temporal solicitada |
| Y024 | reserved | consulta | listagem de campos de confirmação |
| Y025 | dev | normal | nova tarefa local delimitada |
| Y026 | reserved | normal | agregação semanal nova |
| Y027 | dev | trivial | padronização visual |
| Y028 | reserved | abster | público, canal e aceite ausentes |
| Y029 | dev | consulta | formato de CSV já usado |
| Y030 | reserved | consulta | logs do pacote delimitados |
| Y031 | dev | abster | fonte oficial e autoridade de alteração ausentes |
| Y032 | reserved | abster | ambiente e dado afetado ausentes |
| Y033 | dev | normal | métrica local nova |
| Y034 | reserved | pequeno | ordem de colunas já definida |
| Y035 | reserved | consulta | regra de retenção aprovada procurada |
| Y036 | reserved | consulta | localização do aviso procurada |
| Y037 | dev | alto_risco | assinatura de fornecedor e chave |
| Y038 | dev | pequeno | encaminhamento existente |
| Y039 | reserved | pequeno | mensagem de erro existente |
| Y040 | reserved | trivial | capitalização visual |
| Y041 | dev | pequeno | comportamento existente: vazio deve retornar `null` |
| Y042 | reserved | abster | sistema alvo e permissões ausentes |
| Y043 | reserved | abster | envio externo e dado autorizado ausentes |
| Y044 | dev | abster | ação posterior e aprovador ausentes |
| Y045 | dev | abster | base legal, público e canal ausentes |
| Y046 | dev | pequeno | etapa existente da sequência |
| Y047 | reserved | trivial | tamanho visual de avatares |
| Y048 | dev | alto_risco | acesso de fornecedor e chave compartilhada |

## Taxonomia, partições e regra

As famílias nomeiam mecanismos de trabalho; não prometem semântica
ortogonal. Mecanismos semelhantes podem atravessar dev e reserved. O split
garante somente composição, identidade, ordem e fronteira de fit da regra.
Ele não torna a segunda partição independente desta revisão autoral.

A regra lexical é um diagnóstico local finito, derivado deterministicamente
dos 24 itens dev por presença de token, suavização 1, top-5 por classe e
desempate por peso decrescente e token crescente. Tokens têm ao menos dois
caracteres. O harness recomputa a regra e exige igualdade integral; campos
`used_reserved_for_fit=false` e hashes declarados não são tratados como
prova isolada de origem. O reserved não é usado para fit, score ou ajuste.

## Fixtures e limites conhecidos

- Y009 preserva a prévia de interface com dados sintéticos como comportamento
  local novo; não virou permissão nem produção.
- Y011 exige fonte editável para a legenda de artefato raster estático.
- Y041 exige `null` quando não há período anterior; esta candidata fixa a
  fixture, sem afirmar que uma implementação histórica devolvia vazio.
- As checagens de integridade são diferentes de oráculo semântico. As
  mutações exercitam guardas de projeção, formato, fronteira documentada e
  derivação da regra; não provam revisão humana independente do gold.
- Não há métrica, score ou aprovação nesta pasta. Resultados históricos de
  R5 continuam evidência exploratória histórica, não critério de promoção.

