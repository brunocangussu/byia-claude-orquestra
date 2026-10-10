# T-151 — candidata local concluída, não ativada

## Resultado

O dono corrigiu T-180 para **T-151** e aprovou desenvolvimento local. O plano
aprovado foi executado em `codex/t151-autonomia-meta`, worktree gerenciado
`t151-autonomia-meta`, base `6c8482a8b3deca31ecdc330c38d675c39f14058c`.

Um acordo inicial por meta permite ao Manager aceitar complementos técnicos
necessários e cobertos sem nova pergunta humana. Escritores com ownership
disjunto e interfaces fechadas e análises independentes podem avançar juntos.
Dependências, sobreposição e falhas estacionam somente o trecho afetado.
Manager integra/verifica; worker não entrega Git, move board/ledger ou delega
recursivamente. Retomadas preservam handles, saldo e o mesmo medidor.

Isso não transforma Manager ou JEV em fonte de consentimento: novo escopo,
gasto, egress, credenciais, produção e Git continuam limites humanos explícitos.
Modelos, efforts e presets não mudaram. Não foi criado um novo runtime.

## Candidata e prova

Dez arquivos do produto/testes estão congelados. Lista e hashes em
`docs/T-151-implementacao-local-2026-10-09-recibo.json`. Worker real
Sol 6.1/xhigh e consumidor disjunto pelo Manager, CLI 0.160.1; thread
`01a122f4-3836-7702-b798-752033f64751`, terminal exit 0. Modelo/effort
observados no cliente, não identidade garantida no servidor.

- Descoberta completa final: **936 testes, OK**, 272.039 s.
- Manager: **66 testes frescos** com Python 3.14.7 e 10 mutações detectadas.
- Total: **41 mutações contratuais**, 31 worker + 10 Manager.
- Manifesto estrito, coerência, Ruff, diff-check e formato da skill: exit 0.
- Sonda final 8/8, mas baseline também 8/8; sem economia ou ganho causal
  demonstrados. C01 tem uma citação de arquivo imprecisa. Sem efeitos reais.

A descoberta final usou PATH restrito a CommandLineTools (incluindo Python
3.9), pois Git do macOS criava `systmp/xcrun_db` em testes de isolamento.
Nenhum ambiente global alterado; guardas preservadas. Falhas anteriores e
seus reparos, runtimes e originais dos logs estão discriminados no recibo.

## Próximo limite real

R1 independente **não iniciada**. Pacote sanitizado preparado no worktree:
`docs/reviews/T-151-R1-sanitizado.md`, **187.361 bytes**, teto proposto 192 KiB,
SHA-256 `5d8d15f974f53826966f01db1c7aef65ea19183c929f62cdf3678eed42a0c70a`.
Fontes candidatas completas + plano + referência + mapa de trechos alterados;
não contém diff completo, logs privados, PII, credenciais ou chaves de ledger.
AGENTS/CLAUDE idênticos são reproduzidos uma vez. Recibo público:
`docs/T-151-R1-pacote-preparado-2026-10-09.json`.

O futuro envio ao Opus 5.5/high via Claude CLI/Anthropic precisa de gate humano
de snapshot, bytes e orçamento. Preparação local não consome nem cria esse
gate. Não fazer retry/revisão externa, bump, Git ou ativação por inferência.

## Retomada sem repetir trabalho

Leia o índice, board canônico e `threads/T-151-autonomia-por-meta.md` da
frente de origem. Continue o run `05118f07-4c9e-4e92-8c2a-eda7ea7b478f`;
P01–P04 locais concluídos, P05 ainda exige revisão independente. Os handles
de implementação e sondas são terminais; não relançar.

Não pedir novamente aprovação de etapas locais já cobertas. Não declarar
100%, VALIDATE/DONE ou funcionamento em todos os projetos. A main ainda tem
fonte 0.32.0; T-151 não está nos caches. Sem commit, push, publicação,
instalação ou restart. T-098 e sua campanha/JEV e a validação prática T-150
foram preservados, sem serem fechados por esta implementação.
