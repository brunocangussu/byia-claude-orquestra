# T-098 A2 — desenho local da candidata R3

Estado: **plano de amostra, não gabarito aprovado**. Nenhum caso R3 foi enviado a modelo,
nenhuma classificação JEV/Luna foi executada e a R2 permanece congelada para auditoria.

## Por que a R2 não serve para medir

A auditoria confirmou famílias com uma única classe, prefixo quase exclusivo na classe
`pequeno`, subtipos de `alto_risco` separados por partição e dois gabaritos ambíguos.
Além disso, a partição `reserved` da R2 já foi aberta; reescrever só X015/X046 ou
embaralhar as frases não recuperaria uma validação cega. A candidata R3 precisa ter
textos novos para os 48 IDs e ser congelada antes de qualquer inferência.

## Matriz pré-declarada

São 12 famílias de domínio, quatro casos de classes distintas por família. Famílias
inteiras ficam em uma só partição. Os IDs continuam X001–X048, mas serão intercalados
entre famílias e classes antes do congelamento; o número não pode codificar `gold`,
família ou partição. `family`, `split`, `gold` e `reason` nunca entram no payload do
classificador.

| Partição | Família | Classes presentes |
|---|---|---|
| dev | interface de cadastro | normal, trivial, pequeno, abster |
| dev | API local | alto_risco, consulta, pequeno, abster |
| dev | exportação de dados fictícios | alto_risco, consulta, normal, trivial |
| dev | documentação e configuração | consulta, trivial, pequeno, abster |
| dev | migração de banco fictício | alto_risco, normal, trivial, abster |
| dev | entrega de versão fictícia | alto_risco, consulta, normal, pequeno |
| reserved | console administrativo fictício | normal, trivial, pequeno, abster |
| reserved | serviço de autenticação fictício | alto_risco, consulta, pequeno, abster |
| reserved | análise de eventos fictícios | alto_risco, consulta, normal, trivial |
| reserved | ferramenta de desenvolvimento | consulta, trivial, pequeno, abster |
| reserved | configuração de faturamento fictício | alto_risco, normal, trivial, abster |
| reserved | operação de implantação fictícia | alto_risco, consulta, normal, pequeno |

A matriz dá oito casos por classe e quatro por classe em cada partição. Em cada
partição, os quatro `alto_risco` cobrem, respectivamente, controle de acesso,
exposição de dado protegido, schema e produção/irreversibilidade. Os cenários são
inteiramente fictícios e não contêm projetos, pacientes, credenciais ou infraestrutura
do dono.

## Pré-auditoria obrigatória antes de pedir nova revisão

1. Conferir por código IDs únicos, 48 casos, matriz 8×6, 4 por classe/partição,
   quatro classes por família e família presente em uma partição só.
2. Verificar mistura lexical: nenhum prefixo curto ou molde sintático deve prever
   uma classe; comparar também comprimentos, verbos iniciais e termos de risco entre
   partições. Inspeção manual decide ambiguidades, não a contagem automática.
3. Para cada `pequeno`, citar no motivo o arquivo único, a reversibilidade e o
   resultado fechado. Para `trivial`, deixar explícito que não muda comportamento.
   Para `abster`, apontar exatamente qual fato impede classificar com segurança.
4. Conferir pares de risco equivalentes em `dev` e `reserved`, sem paráfrases
   quase idênticas; a distribuição de subtipos não pode identificar a partição.
5. Congelar separadamente textos, gabarito, rubrica, regra lexical e payloads.
   Uma revisão independente posterior recebe casos/gabarito, nunca resultados de
   classificadores. Achado substantivo bloqueia a A2; não corrigir após medir.

## Custo da revisão R2

Uma chamada R1 e uma R2 enviaram pacotes de tamanho próximo, mas o CLI reportou
criação de cache 7.731 → 193.823 tokens e custo **de tabela** US$ 0,1584622 →
US$ 1,636352. O recibo não prova a causa nem a cobrança efetiva. Antes de pedir
outra chamada, o wrapper de revisão deve registrar localmente apenas: versão do
CLI, ID de modelo solicitado/observado, flags, comprimento e digest do pacote,
diretório de trabalho de forma sanitizada, nomes (nunca valores) das variáveis
herdadas relevantes, contagem de mensagens quando disponível, uso e tempo.
Não repetir Opus só para investigar custo. O novo teto e o payload sanitizado
exigem autorização separada.

## Limite da evidência

Este desenho remove vieses conhecidos por construção, mas não comprova a qualidade
dos textos ainda não escritos, a independência do revisor, a utilidade do JEV ou
economia por entrega aceita. A banca T-138 continua em 0/16 até a A2 ter gabarito
aceito e orçamento próprio.
