# T-131 — R1 executada e auditada

Destino: Anthropic, **Claude CLI/Opus 5.5**, pelo runner já instalado com `--model opus`,
conferindo `OPUS_MODEL=claude-opus-5-5` antes de aceitar parecer. Sem ferramentas, retry,
credenciais ou PII no briefing. A tentativa anterior foi bloqueada antes de iniciar processo.
Após autorização explícita do dono, em 23/09/2026, os **cinco lotes foram executados uma vez cada**,
todos exit0 e identidade 5.5. R1 concluída; nenhuma R2. Pareceres em `resultado-01.md` a
`resultado-05.md`; [auditoria do Manager](auditoria.md): quatro grupos de correção antes de integrar.

## Snapshot e cobertura

Fonte: worktree atualmente `.worktrees/t137-capacidade-modelos-runner`, branch
`codex/t137-capacidade-modelos-runner`, HEAD `a82a35f22f6c285aaa929da0e5b8a93c74685046`.
Era `t131-models-opus55-gpt6`; o reflog comprova renomeação concorrente às 22:44:42 de 22/09/2026.
Esta frente não a fez nem a reverteu. O board ainda nomeia o card T-131; conciliar a identificação
antes de nova escrita no produto, sem renumerar silenciosamente.

SHA256 do `git diff --no-ext-diff --no-color` congelado:
`479dce3e6cd0b370f20f70a232d7ceda29af9547bba39798ec3e9afc4efa7fda`.

Os lotes contêm os **51 hunks dos 10 arquivos** modificados, sem omitir hunk nem cortar bytes.
Arquivos grandes foram divididos por hunk, repetindo cabeçalho Git e critérios por lote.
O handoff não commitado é registro de execução, não produto, e não faz parte do diff de revisão.

| Lote | Bytes UTF-8 do arquivo | Hunks | SHA256 |
|---|---:|---:|---|
| lote-01.md | 14897 | 7 | 2be4638a914425dad8044278cf8717b9b2420bde72a103c690235553e7d78304 |
| lote-02.md | 15455 | 14 | 7d4edd3a6fdb9abdbc24b2ded54fe0da5d47714c75a73d0fd4f48c0f9c537407 |
| lote-03.md | 14264 | 12 | 84170e4a9d79d990835318524c53c58f738fb95e26f0f59a7186c509ac059dc2 |
| lote-04.md | 15483 | 10 | 6f08ba58449567b31c5e057890da3758bec7817d9f3d059ac316a69d5b7aa079 |
| lote-05.md | 9156 | 8 | eed9515eab55c388af71919e7a96d83736bfe86622cbfd07db2d324b4fe24d84 |

Todos abaixo de 16.384 bytes por lote. Não foi identificado conteúdo pessoal ou segredo nos hunks;
variáveis de autenticação/modelo mencionadas em testes são código, não valores de credenciais.
Não incluir arquivos adicionais na transmissão sem nova inspeção.

## Gates locais no caminho preservado

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'`:
  exit0, **421 testes**, 43,107s (execução única do Manager após a renomeação).
- `claude plugin validate ./orq --strict`: exit0.
- `git diff --check`: exit0.
- `PYTHONDONTWRITEBYTECODE=1 python3 orq/scripts/lint-coerencia.py .`: exit1 somente pela
  divergência fonte/cache 0.27.10 em `commands/elenco.md`. Sem bump/install, não declarar lint verde.
- SHA do diff conferido novamente após os testes: igual ao snapshot dos lotes.

## Gate pendente

É necessária autorização explícita do dono para enviar **estes cinco lotes sanitizados do diff e
instruções do T-131 à Anthropic por Claude CLI/Opus 5.5, em uma única R1 sem retry**. Isso não
autoriza bump, commit, push, integração, publicação, instalação ou restart.
Na retomada, conferir novamente o snapshot e o estado da frente antes do primeiro envio.
