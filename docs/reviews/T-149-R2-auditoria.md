# T-149 — Auditoria da R2 Opus 5.5

## Recibo e autorização

Uma chamada autorizada e consumida, sem retry: R2 via Claude CLI/Anthropic,
de 2026-10-06T17:36:02.741Z a 2026-10-06T17:40:34.744Z (272,003 s).
Runner e CLI terminaram com exit 0; o parecer tem formato válido e veredito
literal `APROVADO_COM_RESSALVAS`, sem bloqueadores. Identidade conferida pelo
runner em `modelUsage`: `OPUS_MODEL_USAGE=claude-opus-5-5`.

O effort `high` foi solicitado e transmitido, não observado no servidor;
custo não informado. Não inferimos esforço efetivo nem cobrança. O recibo
original do processo foi preservado, incluindo seu campo de modelo ainda
nulo, anterior à validação de identidade do runner. A evidência final fica
em campo separado no recibo da rodada.

Pacote congelado: 126.107 bytes, SHA-256
`ee6a468b00bc93a090ed5087b454d607c60ca2bb5a710ee62ca9ae8ba39675bf`.
Tetos de 128 KiB e 600 s; nenhum byte adicional de prompt. Nenhuma chamada
externa depois da R2. Publicação, instalação e restart continuam proibidos.

## Ressalvas exigidas antes do commit — encerradas

1. **Legado sem effort:** o cabeçalho de `revisar.md` agora segue o contrato
   de `elenco.md`: dois parâmetros no perfil explícito `@effort`; apenas
   modelo comprovado no legado sem effort. Recusa explícita não permite
   omissão nem downgrade. A instrução antiga sobre sempre dois overrides
   deixou de contradizer o snippet executável.
2. **Critério de legado e retorno ao preset:** `elenco.md` distingue a
   combinação autorizada/comprovada no papel/contexto da data de escrita da
   linha. Retorno ao preset reaproveita somente recibo compatível; uma nova
   combinação só com modelo não herda essa exceção. Não é gravada nem
   despachada: é apresentada com effort explícito para decisão/gate do dono.

## Outros riscos auditados

- **Projeção dos oito papéis:** probe puro confirmou que o helper não mantém
  papéis extras dentro de `hosts[host]`. Não é um reescritor de arquivo.
  Contrato agora explícito na API e no comando: Manager, papéis adicionais e
  overrides locais ficam fora da projeção; o chamador aplica só o diff das
  oito linhas nomeadas, nunca substitui a seção inteira pelo JSON. Aceitamos
  esse limite documentado, não alegamos preservação automática de chaves
  extras pelo helper. Nenhum algoritmo foi alterado após a R2.
- **Claude nativo:** os seis papéis pela via nativa ainda exigem prova
  contextual antes de adoção/despacho. O catálogo é uma proposta, não prova
  de disponibilidade. A base 0.30.0 já tinha o gate contextual; não se trata
  de proibição nova. Não houve smoke externo nem ativação de host nesta etapa.
- **Cliente autoatualizado:** mudança de versão invalida somente a prova
  dependente. A regra foi explicitada; não bloqueia trabalho local
  independente nem encerra workers já iniciados. Não inventamos equivalência
  entre versões ou nova prova automática.
- **Notas na célula do reviewer:** o placeholder agora pede só o token
  `modelo[@effort]`, usando o primeiro par de crases se houver, sem notas.
  O teste Bash exercita aliases, IDs completos e presença/ausência de effort
  sem substituir artificialmente a extração de `MODEL_ALIAS`/`EFFORT`.
- **Herança acidental de modelo:** frontmatter neutro e gate pré-despacho
  reduzem o risco, mas não comprovam execução nem custo. Não restauramos
  fallback silencioso nem declaramos a configuração carregada em todos os
  chats. A prova prática permanece um gate separado.

Os apontamentos teóricos não viraram bloqueadores sem cenário demonstrado:
ausência histórica de effort não é prova efetiva; preset de um host não
adota o outro; o template demonstra formato sem comprovar adoção; o helper
de intenção é puro e não um dispatcher instalado. A fixture histórica não
substitui o diff/digest atual. O snippet declara Bash, não POSIX sh.

## Verificação local das clarificações

- Foco do runner: 29/29 testes verdes, incluindo cinco casos reais do
  snippet Bash com CLI falsa, sem rede.
- Duas mutações locais reprovaram pelo oráculo correto: forçar alias `opus`
  no lugar do ID completo e apagar o effort declarado. Cada uma produziu
  duas falhas de asserção, sem erro de execução.
- A tentativa inicial com classe de teste incorreta gerou `AttributeError`;
  não conta como RED nem como evidência de mutação. O seletor correto foi
  executado depois.
- `git diff --check`: exit 0 após as clarificações. Gates frescos com as
  quatro âncoras 0.31.0: 870/870 testes, manifesto estrito e lint exit 0.
  Recibo em `T-149-gates-pos-R2-0.31.0.json`. Dois ResourceWarnings de
  arquivo não fechado foram preservados, origem não auditada; não houve
  falha. A fonte integrada será verificada novamente.

## Delta posterior à revisão

O pacote e o parecer originais ficam imutáveis. Encerramento local limitado
a `elenco.md`, `revisar.md`, docstring de `elenco_padrao.py` e reforço do
teste executável de `test_run_opus_reviewer.py`; sem alteração algorítmica
do helper e sem nova rodada externa. O bump e os registros de entrega são
posteriores à revisão e serão comprovados pelos gates locais frescos.

**Conclusão do Manager:** GO para a entrega Git condicional já autorizada,
com as duas ressalvas documentais encerradas. Não é aprovação de ativação,
instalação nem de funcionamento de todos os projetos/chats. O T-149 segue
para validação prática do dono, não para DONE por causa de um commit.

## Conferência do staged — evidências congeladas

`git diff --cached --check` global devolveu exit 2: somente whitespace
literal em `T-149-R1-opus55.md` (1 ocorrência),
`T-149-R1-pacote-sanitizado.md` (70) e
`T-149-R2-pacote-sanitizado.md` (75). Os pacotes contêm diffs literais;
remover seus espaços mudaria os bytes/hashes enviados e autorizados.
O parecer recebido também não foi reescrito.

A checagem foi repetida excluindo **só esses três arquivos imutáveis**:
exit 0 em todo o código, instruções vivas e registros editáveis.
Não houve mudança global de configuração, .gitattributes, exclusão de
produto do lint ou ocultação do exit 2 original. Digest da saída global:
`6460ed3f85b462a8e3b1142b15e1e0fc0450a9d0ef208962defc478524a1021a`.
Essa exceção documental não equivale a declarar o check global verde.
