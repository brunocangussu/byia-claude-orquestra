# Evidências locais — candidata R7 v5

## RED/GREEN

Dois oráculos independentes permanecem fora da descoberta `test_*.py`:

- v1 falha no oráculo de pontuação com `8/8` abster e `0/40` demais;
- v3 falha no oráculo da frase com `8/8` abster e no máximo `1/40` demais;
- v4 e v5 passam os dois oráculos. A v5 registra, sem promessa de
  generalização, `4/8` abster e `1/40` demais para a frase conhecida.

O oráculo de adjudicação cria, em memória, uma troca dev internamente coerente
de gold/policy/facts/rationale e refaz a regra dependente. A v4 aceita essa
mutação e falha com a mensagem nomeada de guarda ausente; a v5 a rejeita com
`metadados v1 divergentes: Y007`. Assim a prova não depende de hash antigo,
regra antiga, import ausente ou mero erro estrutural.

## Mutações e cobertura

A descoberta cobre e rejeita com `ValueError` nomeado:

- atalhos histórico de pontuação e frase;
- texto editorial Y028 da v2, Y041 e um dos 37 textos protegidos;
- consulta com lacuna decisiva;
- adjudicação alterada apesar de contrato interno coerente;
- fórmula/ranking float legado e ordem de empate trocada;
- inventário R5 antigo, caminho absoluto e escape `..`;
- ramos diretos de `_project_file`: absoluto, `..`, ausente e symlink;
- ausência de `rule.algorithm` ou `historical_r5.state`, classes mistas e
  SHA-256 inválido.

Y009, Y011 e Y041 permanecem fixtures concretas. Projeção byte a byte e tipo
antes de campo permanecem cobertos. As falhas R5 (projeção contaminada, item
string e regra forjada) são caracterização histórica; os equivalentes v5 são
rejeitados localmente.

Não há score, ajuste no reserved, nova inferência ou revisão independente.

