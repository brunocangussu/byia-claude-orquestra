# T-098 — verificação e handoff da preparação documental

2026-10-02. Plano local aprovado; candidata nova **não enviada**, gabarito
**não aprovado**, código de bancada novo **ainda não implementado**.

## Artefatos novos e estado

- `amostra.json`: 48 pedidos/razões reformulados, 27.883 bytes, SHA-256
  `fba8c8a5f07375540369cb471c6cd8a21959564259edc7a823f2d897096ca4fb`.
- `mecanismos-e-limites.md`: mapa dos 18 mecanismos e auditoria dos pares
  Y044/Y042, Y002/Y040, Y007/Y027/Y014 e Y046/Y034, com limites explícitos.
- `regra-lexical-congelada.json` e `recibo-congelamento-lexical.md`:
  parâmetros derivados só de dev; regra gravada/hasheada antes do reservado.
- `resultado-diagnostico-local.json`: pontuação, matriz e contrafactuais
  analíticos. Contém gold local; **não é payload de classificação**.

## RED e GREEN analíticos

Antes da reformulação, a cascata auditada acertou 24/24 dev e 24/24 reservado;
a asserção de que ela não separava perfeitamente cada partição falhou em
ambas. O cenário antigo Y006 também reprovou a exigência de entrada/saídas
observáveis do reparo. Esses REDs são analíticos, não uma suíte nova persistente.

Depois da reformulação, a mesma cascata acertou 10/24 em cada partição;
as guardas analíticas correspondentes passaram. Y006 agora compara
[2,4,6] e [2,2,2] num contrato de avanço fechado. A edição não foi relabelada.

O preflight original R4 foi importado read-only e executado sobre os dados
novos, com `PYTHONDONTWRITEBYTECODE=1`: exit 0. Conferiu 48 IDs, campos,
contagens, famílias/partições e controles; projeção de quatro lotes de doze
casos, **somente id/text**. Metadados por ID iguais à amostra R4.

Baseline R4 por descoberta: 14 testes OK em 0,024 s, exit 0. Esse resultado
é da bancada histórica intacta; **não chamar de suíte descoberta da candidata
nova nem de correção completa do T-098**.

## Diagnóstico lexical congelado

Regra de cinco tokens por classe, presença e peso log-odds com suavização;
parâmetros e receita no recibo. Sem ajuste após ler a pontuação reservada.

| Partição | Regra ajustada no dev | Cascata histórica pós-hoc |
|---|---:|---:|
| dev | 23/24 | 10/24 |
| reserved | 16/24 | 10/24 |

16/24 (66,7%) com uma regra simples é informação para auditar novos atalhos,
não evidência de assertividade/economia do JEV. Autor conhece as duas
partições: não houve cegamento ou validação estatística de generalização.

Marcadores de arquivo e implementação aparecem nas seis classes do dev;
no reservado, em quatro e três classes, respectivamente. Explicação também
aparece em diferentes classes. Isso quebra a exclusividade antiga desses
marcadores, não demonstra que todo atalho lexical foi eliminado.

## Contrafactuais analíticos, sem mutação da fonte

Oito alterações em cópias de memória foram detectadas pela asserção esperada,
nenhuma por erro da bancada: volta dos textos antigos no dev; volta no reservado;
Y006 sem cenário observável; troca de gold por ID preservando contagens;
Y038 preservando rejeições atuais; Y047 sem isolamento da prosa; projeção com
gold; mudança do arquivo da regra após o selo. Nenhum sobrevivente nesses
oito checks. São guardas estruturais delimitadas, não oráculo semântico.

## Preservação e pendências honestas

R4 pacote 51.176 bytes/SHA `0934fda33cdca92add01e4fb8f4dfbaaa8543d26470d08605e787900349e4281`
e amostra SHA `a69c8eac25ac8981ded509c9f1e4cb7df7aa796124357c945db5a4e8b53642ea`
permanecem intactos. Main/Claude/T-089 protegidos conferidos; nenhuma escrita
em código de produto, elenco ativo, credenciais, caches ou âncoras.

Falta checkout dedicado compatível com o gate sem Git writes. Não criar
silenciosamente branch, reutilizar T-131 ou escrever código da bancada na main.
Na frente isolada, ainda portar as guardas, descobrir toda a suíte nova e
rodar mutações/gates persistentes. Não preparar despacho integral de R5 antes
dessas etapas. Depois vêm revisão independente válida, aprovação do gold,
selos e campanha autorizada, custo/efetividade e adoção em shadow mode.

A2: JEV 0/4, Luna 0/4; B2 0/16. R4 externa consumida 1/1; nenhuma R5,
classificação ou nova chamada. Sem autenticação, bump, commit, push, merge,
publicação, instalação ou restart. Não fechar o card pelo preflight verde.
