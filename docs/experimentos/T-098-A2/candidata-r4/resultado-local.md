# T-098 — resultado da correção local, não aprovação independente

Data: 2026-10-01. Autor/implementação: Manager Codex, dentro do gate local.
Fonte de autoridade: `plano-local.md` e auditoria R3 preservada. Nenhum envio,
classificação, autenticação, alteração de produto ou adoção nesta correção.

## Amostra e cobertura

48 casos inteiramente fictícios; oito por classe. 24 desenvolvimento e 24
reservados, quatro de cada classe em cada partição. IDs `Y001` a `Y048`,
dispersos entre famílias/partições, sem nome de classe na identificação.
18 famílias indivisíveis por mecanismo, com dois/três casos; sem obrigação
artificial de quatro classes diferentes em cada família. Algumas assinaturas
de classes coincidem por acaso; os espectros globais não são espelhos.

| Mecanismos do desenvolvimento | Mecanismos reservados |
|---|---|
| controle de identidade, exposição de registros, dependências | evolução de schema, promoção de ambiente, retenção de histórico |
| redução de medidas, documentação executável, sequências | tratamento de arquivos, janelas temporais, composição de relatórios |
| roteamento de entrada, coordenação de tarefas, renderização | diagnóstico de processos, compatibilidade de protocolo, empacotamento |

Controles contrastivos: `Y012` pede exposição de PII apesar de “só leitura”;
`Y037` muda autenticação em uma linha de Markdown executável; `Y048` remove
proteção sob urgência. `Y027` é texto inofensivo sobre permissões; `Y009` é
Markdown com comportamento novo não sensível. Os normais pedem implementação
explicitamente; escolher algoritmo não se confunde com ausência de escopo.
Os pequenos variam entre reparo aritmético, redundância, limite, normalização,
string, comparação, chave e referência; não são oito constantes em configs.

Auditoria semântica do **mesmo autor**, não independente: rótulos e motivos
foram conferidos contra a precedência da rubrica v2. A família é definida pelo
mecanismo, não pelo substantivo. Não foram introduzidos nomes, identificadores
de pessoa ou credenciais reais; pedidos perigosos são dados fictícios a
classificar, nunca instruções de execução para o runner.

## Diagnóstico lexical, não prova semântica

Conjuntos de palavras minúsculas, regex `[a-zà-ÿ0-9]+`, Jaccard, retirando
somente as stopwords `a o as os de do da dos das em e no na um uma para por com
sem que ao não apenas só ou nem mas`. Todos os 576 pares cruzados foram medidos.
Os oito maiores: Y025/Y010 0,139; Y041/Y039 0,122; Y046/Y034 0,108;
Y025/Y026 0,108; Y016/Y035 0,097; Y041/Y013 0,095; Y004/Y035 0,094;
Y002/Y013 0,094. Não há repetição literal normalizada.

Os pares mais próximos compartilham vocabulário de simulação, leitura pública
ou correção de contrato. Coordenação de fila não é composição de relatório;
denominador, corte de sufixo e chave de serialização são mecanismos diferentes;
limite de enumerador e fronteira de janela temporal continuam próximos como
subtipos de correção. **Esta proximidade residual é uma limitação a reavaliar**,
não um certificado de independência. O índice lexical não detecta todas as
paráfrases, não testa assertividade nem permite baixar risco.

## RED/GREEN e mutações locais

O preflight fica apenas nesta bancada, fora de `orq/`. Não faz rede, inferência,
leitura de credenciais, escrita ou escolha de LLM. Valida estrutura, contagens,
famílias/partições e controles pontuais; não prova todos os rótulos semânticos.
`classifier_batches()` faz dry-run de quatro lotes de 12, copiando somente
`id`/`text`; famílias, split, gold e reason nunca entram no payload projetado.
Lotes 1/2 são desenvolvimento, 3/4 reservados; isso é metadado local, não campo
enviado. Os lotes não estão congelados ou autorizados para classificação.

Baseline RED deliberado do novo preflight: 13 testes, 11 falhas, zero erros.
GREEN final: **14 testes OK**, incluindo oito contrafactuais permanentes em
`test_mutations.py`: validação ausente, payload contaminado, campo extra,
IDs duplicados, família cruzada, pedido duplicado, controle ausente e motivo vazio.
Cada mutante produziu falha de asserção sem erro de bancada.

Na primeira bancada de mutações, remover somente a checagem imediata de ID
duplicado não permitiu o defeito: a guarda de conjunto e o controle de cobertura
o barraram. A bancada foi delimitada ao contrafactual de remover as duas guardas
de ID, usando IDs não pertencentes aos controles. Não contar remoção redundante
isolada como defeito sobrevivente, nem erro de bancada como mutante morto.

Reproduzir: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py'`
neste diretório. O teste do plugin continua separado, via `discover` de `orq/scripts`.

## Integridade e limites

| Arquivo candidato | Bytes | SHA-256 |
|---|---:|---|
| amostra.json | 17.314 | a69c8eac25ac8981ded509c9f1e4cb7df7aa796124357c945db5a4e8b53642ea |
| preflight.py | 4.178 | 90629815af66061a2299ea124944592e6c90acf75004a45372f0ff685db3f105 |
| test_preflight.py | 3.339 | e99868347e01ff07e9a7e5ea87a4f35a679c6d2b7488b128b5310d458d8bd3ed |
| test_mutations.py | 2.433 | 9dc0e391bf39cd7e9cb84857aeee9de38d8e593248c082b3acc7c992a145f533 |

R3 amostra/pacote conservam digests anteriores; não reaproveitar sua revisão.
O autor conhece as duas partições: **estudo exploratório, não cego**. A candidata
R4 é nova preparação, **R4 externa não executada**, gabarito não aprovado.
JEV/Luna A2 0/4 cada, B2 0/16. Economia/efetividade ainda não foram medidas.
Próximo gate: pacote sanitizado completo para revisão independente deste novo
snapshot; bytes/teto/destino/número de chamadas precisam de autorização própria.
Sem usar autorização histórica como retry, sem ativação ou promoção automática.
