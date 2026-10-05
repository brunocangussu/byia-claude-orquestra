# T-098 — candidata R4 local, não enviada

## Gate e recuperação — 2026-10-01

Correção local autorizada após a auditoria R3. Índice, board e thread relidos;
resolver instalado 0.27.11 comprovado. Sem nova chamada externa, commit, push,
integração, publicação, instalação, restart ou ativação. R3 fica byte-intacta.
Execução nesta sessão principal porque o gate proíbe novas chamadas externas;
não equivale a revisão independente de autoria/gabarito.

## Decisão metodológica delimitada

A rubrica v2 exige 48 casos fictícios, oito por classe e famílias indivisíveis.
Não exige quatro casos ou quatro classes diferentes por família. Essa exigência
artificial do plano R3 produziu espelhos de rótulos entre os domínios. A nova
candidata remove **esse** requisito local, não a rubrica: 18 famílias por mecanismo,
com duas ou três ações cada; classes repetidas são permitidas na mesma família.
24 casos em desenvolvimento e 24 reservados, quatro por classe por partição.

Família não significa domínio: autorização, transmissão, dependência, schema,
deploy e retenção não mudam de família só porque mudou o substantivo. Cada uma
fica em uma partição. A partição reservada usa outros mecanismos concretos.
Alguns conceitos de risco permanecem comuns porque são o objeto medido; isso
não autoriza uma paráfrase quase idêntica. A análise lexical é diagnóstico,
**não** certificado de independência semântica. O autor conhece as duas partições;
estudo exploratório, sem alegar cegamento ou validade estatística de segurança.

## Trabalho local

1. Propor 48 pedidos inequívocos, motivos por caso e IDs sem rótulo de classe.
2. Incluir controles de alto risco: leitura que expõe dados, patch mínimo,
   urgência, Markdown comportamental; contrastar texto inofensivo sobre segurança.
3. Validar por código: esquema, contagens, IDs, motivos, famílias/partições,
   repetição literal, ausência de distribuição espelhada e payload `id`/`text`.
4. RED/GREEN e mutações do preflight; diagnóstico de pares lexicais cruzados.
5. Auditar manualmente os mecanismos e rótulos; registrar limitações e digests.

Preflight é ferramenta local desta bancada, sem rede, CLI de LLM ou credenciais;
não é classificador nem componente do plugin. Não aprova o gabarito. A candidata
não está congelada para classificação, nem revisada de modo independente.
JEV/Luna A2 continuam 0/4 cada; B2 0/16. Pacote externo novo e cada campanha
continuam em gates próprios; nenhuma autorização anterior é reaproveitada.
