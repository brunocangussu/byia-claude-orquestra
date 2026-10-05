# T-148 — auditoria da R1 da fusão

## Escopo e recibos

Uma rodada independente, dois pacotes sanitizados, duas chamadas únicas ao
Opus 5.5 via CLI oficial. Sem retry e sem R2 externa. Os pareceres brutos,
logs, digests e contadores estão preservados nesta pasta. Nenhuma revisão
antiga foi contada como revisão desta fusão.

- Pacote 1: `APROVADO_COM_RESSALVAS`, exit 0.
- Pacote 2: `REPROVADO` com um bloqueador; o titular condicionou a aprovação
  à correção textual, com os demais itens como ressalvas.

O Manager verificou cada achado contra os arquivos completos, não só contra
os recortes recebidos pelo titular. As alterações pós-parecer são instruções
e guardas contratuais locais; não mudam o código de execução do runner nem
constituem um novo parecer independente sobre o snapshot final.

## Bloqueador do pacote 2 — PARCIAL, ambiguidade corrigida

`revisar.md` dizia "prefixo do alias legado", mas o código já usa
`re.fullmatch` em `run-opus-reviewer.py:129-134`. O texto agora especifica a
gramática completa `<base>(?:-\d+)*` e separa compatibilidade de alias da
prova do ID explícito `claude-opus-5-5` (`revisar.md:190-212`).

As sugestões de limitar aliases a datas de oito dígitos e rejeitar 5.5 via
alias legado foram **refutadas como mudança de contrato**, não aplicadas
silenciosamente: a suíte existente aceita explicitamente `claude-opus-5-6`
via `opus` (`test_run_opus_reviewer.py:729-730`). O alias conserva a
compatibilidade já revisada; ele não garante a adoção da fábrica 5.5.
O ID explícito continua rejeitando Opus 5, 5.50 e sufixo adicional.
O novo teste da fusão reproduz ambos os ramos sem rede e rejeita prefixo
arbitrário. Não estreitamos a compatibilidade para obter um verde artificial.

## Ressalvas confirmadas e corrigidas

1. **Custódia do medidor.** O worker recebia o ponteiro de uma thread que
   deveria conter a chave de dono. `implement-next.md`, `checkpoint.md`, a
   referência do medidor e a arquitetura passam a registrar publicamente
   só caminho, run_id e revisão. A chave fica no ledger ignorado da frente
   dona; não viaja para Git, briefing ou modelo externo. O Manager confere
   escopo antes de recuperá-la. O contrato explicita que ownership por
   instrução não é ACL contra outro processo do mesmo usuário.
2. **DONE não é permissão de validar.** `implement-next.md:169-176` separa
   entrada autorizada em `[?]` de validação positiva do dono para `[x]`.
   Com Git pendente, o medidor fica aberto em `docs`, sem pausa/fechamento
   por alcançar 100%; outras etapas locais aprovadas continuam.
3. **Isolamento e plano legado.** `plan-next.md:124-127` atribui ao Manager
   o isolamento já previsto no plano aprovado; worker não cria/remove refs
   ou worktrees. Plano antigo é o aprovado antes de adotar o medidor;
   mudança material ainda volta ao gate humano.
4. **Vínculo inicial de falha.** `SKILL.md:269-271` exige sucesso, JSON válido,
   status 0 e IDs não vazios também na chamada fresca. Falha terminal não
   cria vínculo. Continuação mantém a igualdade exata do threadId e o vínculo
   anterior em divergência, sem retry ou fallback.
5. **Pré-validação do envio.** `revisar.md:181-198` coloca `OPUS_STARTED`
   depois da validação de tamanho. `BRIEFING_TOO_LARGE` sem início é preparo
   local, não chamada consumida; a exceção precede o tratamento genérico de
   exit não zero. Redivisão continua exigindo cobertura humana dos digests.
6. **Remissões.** O elenco consultado é nomeado explicitamente. A arquitetura
   distingue o default legado `opus` do modelo resolvido passado pelo host.

## Alegações refutadas ou já cobertas

- Loop B está definido na skill completa (`## Os dois loops`); a ausência
  no recorte não é ausência do produto.
- `card` e `papel` estão no contrato canônico de vínculo, consultado pelos
  consumidores; o recibo não se reduz aos IDs isolados.
- `--wait` permanece exclusivamente no envelope do `codex:codex-rescue`,
  nunca no `task`; a frase literal que proíbe `--write` permanece nas cinco
  superfícies. A ausência em um pacote não permite concluir remoção.
- Observações do titular sobre conectores externos não têm relação com
  estes pacotes e não são prova de acesso a qualquer conector.

## RED/GREEN e mutações

O novo `test_t148_fusion_contract.py` foi executado antes das correções:
6 testes, 6 falhas. Depois: 6 testes verdes; nove mutações de instrução
rejeitadas nas superfícies de chave, prefixo, DONE, 100%, recibo inicial,
worktree e plano legado. O teste também chama o matcher real localmente,
sem CLI/modelo. As guardas existentes de medidor, Companion e continuidade
passaram: 10 + 9 + 18 testes focados. A atualização da fixture do medidor
reflete a custódia nova, não remove o teste das duas chaves.

## Destino

Auditoria fecha a ambiguidade real e preserva a compatibilidade já testada.
Entrega de fonte fica condicionada à suíte descoberta integral, manifesto,
lint e diff-check finais. Não atesta instalação, versão carregada em chats
vivos, campanha JEV ou validação prática do dono.
