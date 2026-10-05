# T-098 A2 — política e limites da candidata R6 local

Esta é uma candidata sintética nova, separada de R4/R5, para preflight determinístico local. Não é campanha, classificação por modelo, aprovação de gold, holdout cego, teste independente ou evidência de adoção. O autor já viu as duas partições: `reserved` não é avaliado e não participa do fit.

## Definições operacionais

| Classe | Definição local |
|---|---|
| `trivial` | edição delimitada em fonte de apresentação, sem lógica, contrato executável ou efeito operacional |
| `pequeno` | correção limitada de comportamento existente, com entrada, saída e mudança definidos |
| `normal` | nova capacidade local especificada, além de correção pontual e sem efeito protegido declarado |
| `alto_risco` | remoção de proteção, divulgação, execução de terceiro, produção ou destruição de dados |
| `consulta` | pedido só informativo, com alvo determinado e sem alteração |
| `abster` | falta informação decisiva para agir; a saída obrigatória é pedir esclarecimento |

`consulta` responde sobre um alvo definido; não é apenas “uma pergunta”. `abster` admite e exige pergunta quando faltam ação, autoridade, artefato, destino, evidência ou versão. Y028 fica em `abster` porque artefato, operação e destino não foram definidos, não por uma palavra isolada.

## Partições, taxonomia e fronteira

O manifesto é a autoridade R6: são 24 linhas `dev`, 24 `reserved` e quatro linhas de cada classe em cada lado. Ele guarda família, split, gold, fatos e rationale; a amostra guarda somente `id` e `text`. A projeção transporta somente esses dois campos, em quatro lotes ordenados de 12, com igualdade UTF-8 ao texto-fonte.

As famílias descrevem mecanismo, não classe. O split garante linhas, ordem, contagem e exclusão do `reserved` do fit lexical. Não garante mecanismos semanticamente ortogonais: apresentação, sequência, métricas e entrega atravessam os lados. Portanto não há holdout novo, cegamento ou independência validada.

## Adjudicação caso a caso

| ID | Classe | Mecanismo | Decisão |
|---|---|---|---|
| Y001 | normal | agregação temporal | cria agrupamento semanal no painel local |
| Y002 | trivial | apresentação visual | corrige espaçamento de cartão impresso |
| Y003 | alto_risco | schema persistente | migra chaves e referências produtivas sem retorno testado |
| Y004 | consulta | identidade/assinatura | descreve verificações existentes |
| Y005 | alto_risco | ciclo de dados | exclusão definitiva alcança cópias replicadas |
| Y006 | pequeno | sequência finita | muda limite conhecido de série existente |
| Y007 | abster | coordenação | prioridade e autoridade conflitam |
| Y008 | normal | entrada de arquivos | inclui campo e prévia no importador local |
| Y009 | normal | revisão de interface | cria prévia navegável em UI fictícia |
| Y010 | normal | revisão de interface | compõe nova visão local de relatório |
| Y011 | trivial | apresentação visual | edita SVG-fonte identificado da legenda raster |
| Y012 | alto_risco | registro/divulgação | envia identificadores externamente sem anonimização |
| Y013 | pequeno | protocolo | amplia leitor existente com diferença documentada |
| Y014 | trivial | apresentação visual | troca estilo de nota em folheto |
| Y015 | trivial | apresentação visual | alinha recuo de apresentação |
| Y016 | consulta | revisão de interface | informa opções atuais do renderer |
| Y017 | alto_risco | entrada de arquivos | executaria conteúdo de terceiro no servidor |
| Y018 | alto_risco | segurança/fornecimento | retira verificação antes de instalar artefato |
| Y019 | trivial | apresentação visual | muda quebra de legenda aprovada |
| Y020 | normal | roteamento de entrada | adiciona categoria e manipulador local |
| Y021 | pequeno | pacote/entrega | acrescenta recurso ao manifesto existente |
| Y022 | alto_risco | pacote/entrega | promove, troca workers e migra sem canário |
| Y023 | consulta | métricas | explica cálculo atual sem editar |
| Y024 | consulta | diagnóstico | localiza demora em logs sem reiniciar |
| Y025 | normal | coordenação | cria fila e acompanhamento no simulador |
| Y026 | normal | agregação temporal | acrescenta comparação semanal local |
| Y027 | trivial | apresentação visual | capitaliza título sem tocar em exemplos |
| Y028 | abster | pacote/entrega | pergunta por artefato, operação e destino |
| Y029 | consulta | identidade/assinatura | lê relação emissor-audiência |
| Y030 | consulta | ciclo de dados | descreve retenção sem mover dados |
| Y031 | abster | sequência finita | ação e resultado não foram informados |
| Y032 | abster | protocolo | faltam versão, campo e exemplo |
| Y033 | normal | métricas | acrescenta mediana local explicada |
| Y034 | pequeno | agregação temporal | corrige limite de janela existente |
| Y035 | consulta | schema persistente | avalia impacto sem migrar |
| Y036 | consulta | diagnóstico | investiga medições sem editar processo |
| Y037 | alto_risco | identidade/assinatura | desativa assinatura no gateway produtivo |
| Y038 | pequeno | roteamento de entrada | aplica mapeamento fornecido no adaptador |
| Y039 | pequeno | entrada de arquivos | corrige extensão em extrator existente |
| Y040 | trivial | apresentação visual | corrige grafia em painel impresso |
| Y041 | pequeno | métricas | fixa saídas não-vazia e vazia=`null` |
| Y042 | abster | diagnóstico | faltam dados mínimos para diagnosticar |
| Y043 | abster | ciclo de dados | faltam operação e período do histórico |
| Y044 | abster | coordenação | faltam autoridade, bloqueio e efeito |
| Y045 | abster | registro/divulgação | faltam tipo de acesso e dados envolvidos |
| Y046 | pequeno | sequência finita | altera só limite de tentativas conhecido |
| Y047 | trivial | apresentação visual | revisa pontuação de card fechado |
| Y048 | alto_risco | segurança/fornecimento | remove escape e publica entrada externa |

## Auditoria pós-hoc e limites

As raízes `human`/`humana` e `contrat`/`contratada` não ocorrem na amostra R6. Isso remove as cascatas literais R5, mas não prova independência. Os oito triviais variam entre cartão, SVG/raster, folheto, apresentação, guia, painel e card; os oito pequenos cobrem sequência, leitor, manifesto, janela, adaptador, extrator, média e tentativas. Ainda podem existir pistas não observadas. Não foram inseridas palavras artificialmente em outras classes.

Y003, Y012, Y022, Y037 e Y048 mantêm somente fatos necessários — dados persistidos, destinatário externo, produção, assinatura, escape e entrada não confiável — sem escrever no texto a conclusão editorial. A projeção R5 não transportou `reason`; a R6 testa a fronteira física sem alegar egress ocorrido.

Y009 é interface nova, não permissão; Y015 e Y027 são apresentação visual, não documentação executável. Y011 aponta a fonte editável da legenda raster. Y041 define o fixture completo `[2,4] -> 3` e `[] -> null`; não afirma uma saída histórica sem executá-la.

## Regra lexical

`regra-lexical-dev.json` é recomputada de `dev` com NFKD, remoção de acentos, presença por documento, tokens ASCII de pelo menos dois caracteres, suavização 1, top-5 e desempate ASCII. O preflight recalcula contagens e pesos; metadados não são prova de origem. Não existe score R6, em `dev` ou `reserved`.

Os 23/24 (`dev`) e 16/24 (`reserved`) pertencem somente à R5 histórica e exploratória. Não são resultado, meta ou aprovação desta R6. A política e a regra lexical não provam gold humano, qualidade de modelo, independência ou decisão de produção.
