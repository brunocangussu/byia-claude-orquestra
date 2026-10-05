# T-141 — Orca como IDE principal, Orquestra portátil

**Estado:** PLANNING — desenho preparado, não implementado.
**Frente:** `@frente-orca-portabilidade` · **host:** `@codex`.
**Origem:** pedido do dono em 2026-09-29; sistema/pesada.

## Escopo

Preservar a arquitetura de agentes especializados usando Codex CLI e Claude
CLI nos terminais Orca, sem exigir as respectivas interfaces desktop.
Manager único, papéis/skills sob demanda, worktrees, revisão independente,
permissões e AI-Memory continuam parte do contrato.

Desenho em `docs/superpowers/specs/2026-09-29-t141-orca-portavel-design.md`.
Roteamento JEV/Decisions pertence ao T-098; especialização/experimentos ao
T-139; elenco ao T-131. Reusar T-085/T-087/T-089/T-090, sem tomar suas frentes.

## Evidência desta sessão

Guias locais versionados Orca lidos. `orca status --json` confirmou app
1.4.216 em execução, runtime pronto/alcançável e preferências de launch.
O repositório oficial confirma suporte a agentes CLI, incluindo Claude e
Codex. Isso comprova capacidade declarada, não equivalência comportamental.
Não iniciamos agentes nem alteramos configuração/permissões/autenticação.

## Aceite do piloto futuro

Despacho/recibo correlacionados, modelo/effort e permissões comprovados,
writer isolado, reviewer cruzado e eventos reais no banco AI-Memory para
os dois CLIs. Nenhuma dependência das interfaces desktop no caminho testado;
nenhuma perda de sessão, memória ou ownership existente.

## ⏭️ RETOMAR AQUI — recuperação e desenho, 2026-09-29

Índice, board e threads relacionadas relidos após compactação; resolver
do pacote absoluto 0.27.11 retornou `state=ok`, `exists=true`. Este card
foi criado nesta frente, sem renumerar os anteriores. Fonte ativa e trabalhos
paralelos preservados. Revisar o desenho antes do piloto; nenhuma chamada
de modelo, mudança de produto, bump, commit, push, publicação, instalação
ou restart nesta etapa.

### Verificação local do registro

Manifesto estrito, lint de coerência e `git diff --check` saíram 0.
A suíte por `discover` executou **447 testes em 47,968 s, com 1 falha**:
`test_superficies_prescritivas_nao_prescrevem_chave_morta`. Não declarar
all-clear. A descoberta recursiva atravessa o checkout ativo Claude
`.claude/worktrees/agent-a054e5c8dd838fcb5` e encontra quatro referências
em seu plano/históricos/teste como se pertencessem à fonte principal.

Diagnóstico sem escrita reproduziu os quatro achados, todos nesse checkout;
uma filtragem contrafactual somente em memória, limitada a
`.claude/worktrees/`, deixou zero achado na raiz. Isso **não é correção nem
suíte verde**. `git diff HEAD -- orq` está vazio; os novos documentos não
contêm essa chave. Não editei teste nem removi/alterei o worktree Claude.
O tratamento desse falso positivo deve ser separado da migração ao Orca.

Hashes de `memory/MEMORY.md`, `memory/fixes-history.md` e do elenco ativo
conferidos antes/depois, sem mudança nesta edição. Stash T-137 preservado.
Board editado somente nas linhas T-131/T-141; demais frentes intactas.
