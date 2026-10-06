# T-148 — main organizada e entrega de fonte 0.30.0

## Resultado

A main local e o GitHub receberam a conciliação do T-131, T-143,
T-089/T-090 e T-144/T-146. A bancada T-098 v6 e seu histórico congelado
também estão preservados. A versão única da fonte é **0.30.0**.

- Produto: `d760069`, com as quatro âncoras no mesmo commit.
- Evidências, baselines e handoffs: `d67cd99` (119 arquivos).
- Ancestralidade Claude: `0fc58ca` e `e4a85eb`. Os dois merges preservaram
  exatamente a árvore já conciliada; os commits originais não foram reescritos.
- Gates de entrega: 838 testes descobertos, manifesto estrito, lint e
  diff-check do produto verdes; bancada JEV: 31 testes e preflight verdes.

Checagem final também executada diretamente na main organizada: 838 testes
em 206,699 s, manifesto, lint e diff-check exit 0, com fingerprint de
`orq/` estável. Recibo: `docs/delivery/gates-T148-main-organizada-20261005.json`.

## O que foi entregue

| Frente | Entrega de fonte | O que ainda precisa ser validado |
|---|---|---|
| T-131 | Fábrica de modelos, faixas Luna 6/Sol 6.1 e Opus 5.5 explícito no runner | Escolha explícita no host carregado. Elencos/presets vivos foram preservados; candidato não vira fallback automático |
| T-143 | Continuidade do trabalho local já aprovado até o próximo gate específico | Uma tarefa aprovada continua sem renovar permissões já concedidas; egress e ações externas permanecem delimitados |
| T-089/T-090 | Identidade da retomada Companion, vínculo preservado na divergência e `--wait` somente no envelope | Continuação efetiva na mesma conversa após ativação do host, sem repetir os probes já consumidos |
| T-144/T-146 | Medidor portátil, ledger local, lembrete consultivo e statusline | Progresso representa o plano, não DONE automático; testar as vistas e o lembrete no host efetivo |
| T-098 | Bancada v6, oráculos, adjudicações e baselines imutáveis | Aceite da bancada. **Não houve campanha A2/B2, inferência avaliada ou adoção JEV** |

As revisões próprias das frentes e a revisão delimitada da fusão estão
preservadas com recibos. Na fusão, os dois pareceres brutos permanecem
intactos: ressalvas e reprovação condicional foram auditadas contra os arquivos
completos, e as correções receberam RED/GREEN, nove mutações e gates locais.
Não houve retry nem uma R2 externa disfarçada.

## Ambiente de desenvolvimento

De oito checkouts registrados, restam **dois**:

1. A main deste projeto, para continuar o desenvolvimento.
2. `../byia-claude-orquestra-worktrees/t144-medidor-progresso`, preservada
   porque havia 14 processos com cwd nela. Não foi encerrada ou reiniciada.

T-131, T-143, T-098, T-139 e a conciliação têm snapshots nativos
recuperáveis. O T-139 é preservação experimental, **não adoção** dos papéis.
Os 15 arquivos ignorados únicos foram antes preservados em
`.orq/progress/worktree-archives/ignored/`.

O checkout T-089 foi removido sem `--force`; a branch e os commits continuam
no repositório. Sua thread não rastreada está no handoff público
`docs/delivery/owner-handoffs/T-089-companion-resume.md` e em backup local
ignorado. As cópias conferem byte a byte. Nenhuma branch Claude foi apagada.

A chave de dono do medidor e o ledger T-146 permanecem locais e privados.
Nenhuma credencial foi publicada.

## Para a janela Claude

T-089/T-090 e T-144/T-146 já estão conciliados na main. **Não reaplique os
commits, não faça bump isolado e não repita probes ou revisões consumidas.**
A branch viva do medidor está no tip histórico `064e726`; não é a versão
final 0.30.0. Preserve seu ledger e sua sessão em andamento.

Depois de encerrar essa sessão, a continuação deve partir da main atual
ou de um novo worktree explicitamente delimitado. O checkpoint e os cards
em VALIDATE indicam os testes práticos pendentes, sem confundir entrega
Git com funcionamento de todos os chats.

## Limites da entrega

Esta frente não publicou release/tag, instalou cache ou reiniciou hosts.
A presença do cache 0.30.0 foi observada durante a recuperação de ferramentas,
mas não comprova sua origem nem que todos os chats abertos o carregaram.

O bug de retenção do cache antigo T-047 não foi declarado resolvido por
esta conciliação. Sessões antigas, campanha/adoção JEV e o piloto real dos
papéis especializados continuam com suas provas e gates específicos.

## Evidências e recuperação

- `docs/delivery/gates-T148-entrega-final-20261005.json`: gates frescos,
  fingerprint estável e diagnósticos, incluindo ResourceWarnings das fixtures.
- `docs/delivery/inventario-T148-evidencias-20261005.json`: 115 artefatos,
  1.543.720 bytes e SHA por arquivo; nenhum drift nos arquivos congelados.
- `docs/delivery/limpeza-T148-20261005.json`: snapshots, tips e backups.
- `docs/delivery/auditoria-T148-R1-fusao.md`: auditoria dos dois pareceres.
- `memory/wiki/threads/T-148-consolidacao-main.md`: checkpoint completo.

Os avisos de whitespace dos artefatos históricos foram registrados, não
apagados para produzir um diff verde: 109 trailing whitespace e 26 linhas
finais em branco. O gate de produto e documentação nova ficou separado.

Para recuperar um checkout nativo, use o root exato do recibo de limpeza
no mecanismo de restauração do Codex. Para T-089, recrie o checkout da branch
preservada e recupere a thread pelo handoff público/backup. Não há necessidade
de apagar ou reescrever uma branch para continuar.
