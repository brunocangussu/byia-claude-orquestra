# T-149 — Elenco padrão versionado 0.31.0

## Entregue na fonte

Commit `a81026f` integrado por fast-forward à main e confirmado em
origin/main. Quatro âncoras 0.31.0 no mesmo commit de fonte; sem tag,
release, instalação ou restart por esta frente.

O catálogo canônico distribuído está em
`orq/references/elenco-padrao.json`; a versão e o digest vêm do pacote,
não de uma segunda constante. Todos os consumidores consultam essa fonte.
O Manager continua usando a sessão escolhida pelo dono.

### Padrão da 0.31.0 (proposta, não prova de disponibilidade)

| Papel | Host Codex | Host Claude |
|---|---|---|
| planner·interface | Opus 5.5/high | Opus 5.5/high |
| planner·sistema | Sol 6.1/xhigh | Sol 6.1/xhigh |
| implementer·leve | Luna 6/medium | Sonnet 5.5/low |
| implementer·normal | Sol 6.1/high | Sonnet 5.5/medium |
| implementer·pesada | Sol 6.1/xhigh | Sonnet 5.5/high |
| reviewer | Opus 5.5/high | Sol 6.1/xhigh |
| docs | Luna 6/low | Sonnet 5.5/low |
| scout | Luna 6/medium | Sonnet 5.5/low |

Faixas expressam risco/incerteza de implementação, não volume de arquivos.
O Manager classifica e explica a escolha. Via e prova continuam contextuais.
Esta tabela é o snapshot histórico da entrega; o catálogo do pacote é
a fonte para futuras versões.

## Como adotar em outro projeto

Depois de atualizar/ativar o host sob autorização específica, diga:

> Siga o elenco padrão desta versão do Orquestra.

O Manager resolve a versão/digest carregados, mostra o diff dos oito
papéis e aplica a adoção explicitamente. Preserva o modelo da sessão,
papéis adicionais, overrides e presets locais. A projeção JSON não
substitui a seção Markdown inteira.

Instalar N+1 não migra um projeto adotado em N. Capacidade de modelo/effort,
conta, cliente, sandbox e via exige recibo contextual compatível.
Somente o despacho dependente espera prova ausente/inválida; trabalho
local independente já autorizado pode continuar.

## Evidências e limites

- R2 Opus 5.5 via Claude CLI: `APROVADO_COM_RESSALVAS`, sem bloqueadores;
  duas condições documentais encerradas. Uma chamada, sem retry.
- Modelo observado `claude-opus-5-5`; effort high solicitado/transmitido,
  não observado no servidor. Não houve dado de custo.
- Gates frescos no worktree e na main: 870 testes, manifesto estrito e
  lint exit 0. Dois ResourceWarnings registrados, origem não auditada.
- Dois mutation checks locais do snippet reprovaram corretamente.
- Whitespace literal de três evidências congeladas preservado para não
  falsificar hashes; check dos arquivos vivos/editáveis exit 0.
- `memory/wiki/_elenco.md` ativo e checkout Claude T-144 não alterados.
  Registros próprios da main mantidos em snapshot recuperável.

Parecer/auditoria/recibos em `docs/reviews/T-149-R2-*` e
`docs/reviews/T-149-gates-main-0.31.0.json`; histórico e autorizações em
`memory/wiki/threads/T-149-elenco-padrao-versionado.md`.

## Próximo gate

T-149 em `[?]` / VALIDATE. A entrega Git não comprova ativação em todos os
chats, nem autoriza instalação, restart ou migração em massa. Teste prático
e confirmação do dono são necessários antes de DONE. Não repetir R2,
reautenticar ou disparar inferência por causa deste handoff.
