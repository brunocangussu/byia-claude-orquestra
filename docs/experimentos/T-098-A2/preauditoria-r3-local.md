# T-098 A2 — pré-auditoria local da candidata R3

Data: 2026-09-29. Esta auditoria verifica a **candidata**, não aprova seu
gabarito nem abre o gate de classificação. Nenhum modelo foi chamado para
criar, revisar ou classificar a R3.

## Identidade do snapshot candidato

- Arquivo: `amostra-r3-candidata.json`.
- SHA-256 do arquivo nesta passagem:
  `8cc2e3b5225cb59fa869de66b466912fb607781d6ba587761e874492f7f987e1`.
- A R2, seus pareceres, recibos e hashes não foram alterados.
- O digest identifica somente este estado local; qualquer correção posterior
  exige digest novo e outra pré-auditoria. Ainda **não** é o selo de um
  benchmark cego ou a autorização de egress.

## Controles verificados

| Controle | Resultado |
|---|---|
| JSON válido, IDs X001–X048 únicos | 48/48 |
| Classes | 8 por classe, 4 por classe em `dev` e 4 em `reserved` |
| Famílias | 12; 4 classes distintas por família; nenhuma atravessa partições |
| Alto risco | Acesso, exposição protegida, schema e produção/irreversibilidade presentes em cada partição |
| Textos reutilizados da R2 | 0 |
| Semelhança lexical máxima com a R2 (Jaccard de tokens) | 0,333, em uma consulta genérica a documentação; não prova independência semântica |
| Prefixo normalizado de duas palavras que se repete só em uma classe | 0 |
| Caminhos pessoais, e-mail, URL e sequência longa de dígitos nos textos | 0 na varredura local |

O maior texto tem 139 bytes UTF-8. Médias de comprimento por classe, em
caracteres: `alto_risco` 125, `consulta` 103, `normal` 120, `trivial` 101,
`pequeno` 115 e `abster` 104. Há sobreposição das faixas, mas a diferença
de comprimento ainda pode oferecer atalho estatístico. Este diagnóstico não
substitui teste de separabilidade lexical nem revisão humana independente.

## Auditoria semântica do Manager

- Os oito `pequeno` declaram um único arquivo, uma constante/limite/duração
  específica e reversibilidade; nenhum depende apenas de cor, espaçamento ou
  ortografia, ambiguidade que bloqueou X015 na R2.
- `trivial` limita-se a grafia ou pontuação, com exclusão explícita de
  comandos, regras ou cálculo quando o contexto poderia gerar dúvida.
- `abster` indica no `reason` qual alvo, sintoma, ambiente ou resultado
  necessário não está especificado. Os textos não entregam o rótulo por uma
  fórmula repetida como “não informei”.
- Há pares de risco por subtipo entre as partições sem reutilizar uma mesma
  frase. Eles são **exemplos fictícios**, não dados operacionais do dono.

## Bloqueio restante

O autor desta amostra conhece a R2 e os rótulos da R3, inclusive o reservado.
Portanto, a checagem acima é **pré-auditoria interna**, não validação cega.
Antes de qualquer chamada JEV/Luna, um revisor independente deve receber
somente textos, gabarito, razões e rubrica (sem resultados de classificadores),
avaliar ambiguidades e decidir se aprova o snapshot. Se apontar correção,
criar nova candidata e repetir os controles; não ajustar após medir.

O orçamento, os payloads sem `gold`/`family`/`split`, os hashes separados e
o limite de chamadas ainda não foram congelados. Nova revisão externa e as
oito inferências requerem aprovação específica do dono; JEV/Luna permanecem
em 0/4 cada nesta A2, e a B2 em 0/16.
