# T-098 R4 — revisão integral executada; NO-GO auditado

Data: 2026-10-02. **1/1 consumida**, sem retry; CLI/runner 0, Opus 5.5 exato,
JSON/cobertura válidos, REPROVADO com três bloqueadores confirmados.
Recibos/parecer/auditoria em `../revisao-r4-execucao-2026-10-02/`.
Texto abaixo preserva o histórico pré-envio; não é nova autorização.

Atualização 2026-10-02: o gate isolado de autenticação foi concluído; CLI
reporta true/claude.ai/exit 0 em processos novos. Continua necessário autorizar
a retomada expressa da R4; esse status não comprova modelo ou corrige por si
a falha histórica da via. Ensaio em memória dos pacotes atuais foi registrado
na frente T-131, `docs/reviews/T-131-R4-integral-candidata/ensaio-offline-2026-10-02.json`:
entrada byte-exata com teto proposto, default 16 KiB e excesso bloqueados;
zero chamadas reais. Não é parecer ou prova de transporte/modo seguro.

`pacote.txt`: **51,176 bytes** (UTF-8), SHA-256
`0934fda33cdca92add01e4fb8f4dfbaaa8543d26470d08605e787900349e4281`. Contém sete arquivos integrais, 48 casos/18 famílias,
gabarito ainda não aprovado e rubrica v2; recomposição byte-idêntica verificada.
É bancada exploratória; não alegar cegamento ou aprovar efetividade/economia.

Proposta: uma chamada fresca ao Anthropic via **Claude CLI da assinatura**, modelo
desejado `claude-opus-5-5`, sem ferramentas, retry ou nova autenticação. Modo seguro
por chamada, pasta vazia; limite de supervisão 600 s. Exceção proposta **somente
para esta R4: até 64 KiB (65.536 bytes) de entrada**, incluindo o briefing.
Não altera runner, política geral de 16 KiB/lote ou modelos/papéis ativos.
Sem aceite explícito da exceção e dos bytes/destino/contagem, **não despachar**.

O runner requer override de limite por chamada, nunca modificação do default.
Antes de qualquer futuro envio: reconferir os hashes e o acesso existente,
montar o contrato local e validar o dry-run. Mudança no pacote exige novo gate.
Saída JSON pura, cobertura integral e identidade exata do modelo são requisitos;
formato inválido/timeout/falha não aprovam e não autorizam retry.
O inventário declara fontes e limites; scanner não substitui revisão de conteúdo.

R3 preservada. Esta autorização não inclui congelamento/classificação dos quatro
lotes JEV e quatro Luna, integração, bump, commit, push, release ou adoção.
