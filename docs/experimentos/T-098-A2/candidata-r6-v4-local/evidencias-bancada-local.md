# Evidências locais — candidata R6 v4

## RED/GREEN reexecutável

`oraculo-red-green.py` é independente do módulo candidato. Ele lê somente
amostra e adjudicações, conta perfis e falha por `AssertionError` nomeado.

- RED histórico v1: `--oracle punctuation` retorna `1` com `atalho de
  pontuação exclusivo: 8/8 abster e 0/40 outras classes`.
- RED histórico v3: `--oracle phrase` retorna `1` com `atalho lexical de
  frase exclusivo: 8/8 abster e no máximo 1/40 outras classes`.
- GREEN v4: os dois oráculos retornam `0`. O perfil da frase é `0/8` em
  abster e `1/40` nas demais classes.

Esse RED caracteriza snapshots imutáveis; ele não entra como módulo
permanentemente vermelho na descoberta `test_*.py`.

## Guardas e mutações

A descoberta da v4 cobre e deve rejeitar, com erro nomeado:

- o atalho original de pontuação e o atalho de frase da v3;
- a volta do texto editorial de Y028 da v2;
- a troca de Y041 e de Y009 antes de qualquer selo novo;
- consulta marcada com lacuna decisiva;
- a fórmula/algoritmo float legado, campo de razão removido e ordem ASCII de
  um empate trocada;
- inventário R5 no caminho relativo antigo, escape de raiz e caminho absoluto;
- `rule.algorithm` ausente, `historical_r5.state` ausente, seis classes com
  tipo misto e `rule.sha256` inválido.

Também ficam cobertas a igualdade byte a byte da projeção, a verificação do
tipo antes de acessar campos, a derivação dev-only e os cenários Y009, Y011 e
Y041. As reproduções semânticas R5 continuam caracterizadas como históricas:
a projeção contaminada podia passar, item string lançava `AttributeError` e
regra com peso/contagem forjados podia ser aceita. A v4 recusa os equivalentes
com `ValueError` específico.

## Inventários

O manifesto v4 aponta o inventário R5 pelo caminho relativo conhecido a partir
da raiz do projeto, com SHA-256 próprio. O preflight exige 14 entradas
estruturadas, compara caminho e hash com o mapa histórico e não aceita caminho
absoluto, `..`, arquivo ausente ou symlink que escape da raiz. V1, v2 e v3
são verificados pelos respectivos mapas de 9, 10 e 10 fontes antes de a v4
ser aceita localmente.

Não há métrica de `reserved`, score, inferência ou revisão independente nesta
bancada.

