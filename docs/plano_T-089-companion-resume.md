# Plano — `T-089` reúso `card+papel` do Codex Companion

Planner·sistema: `gpt-6-astra@xhigh` via Codex Companion 1.0.5, read-only, 2026-09-28
(`jobId task-mum17vqn-x6dfia`, `threadId 01a0eae6-b7ed-72d2-9e6b-afee5f5485bb`). Evidência de base:
`memory/wiki/threads/T-089-companion-resume.md`. A auditoria do Manager está no fim.

## 1. Causa raiz — duas camadas, confirmadas

- **Ambiente:** o registro `user` do Claude aponta o Companion **1.0.5**; há quatro registros de
  escopo de projeto de outros projetos, a preservar. O cache **1.0.6** existe, está marcado
  `.orphaned_at` e não tem registro; os arquivos relevantes coincidem com o marketplace local.
- **1.0.5:** `handleTask` não declara `resume-thread`. O parser conserva a opção desconhecida e o
  valor como posicionais, e `readTaskPrompt()` os junta ao briefing. **1.0.6:** reconhece o ID e o
  encaminha até `thread/resume`.
- **Produto:** as instruções exigem IDs presentes, mas **não comparam o `threadId` devolvido com o
  pedido** — uma thread nova satisfaz a verificação. Os testes conferem presença de texto, não essa
  pós-condição.
- A CLI duplicada não explica o defeito: a opção se perde na entrada do Companion, antes do Codex.

### Grafias, pelo parser das duas versões

| Grafia | Companion 1.0.5 | Companion 1.0.6 |
|---|---|---|
| `-resume` / `--resume` | retoma a última task do repositório | igual |
| `--resume-last` | igual à linha acima | igual |
| `--resume ID` | retoma a última task; `ID` vira briefing | igual |
| `-resume-thread ID` / `--resume-thread ID` | opção e ID viram briefing | seleciona a thread pelo ID |
| `--wait` passado ao `task` | vira briefing | vira briefing |

Um e dois traços não são equivalentes em tudo: `--resume=false` é reconhecido, `-resume=false` vira
posicional. Documentar só a grafia canônica `--resume-thread <threadId>`.

## 2. Etapas

### Produto — executor Sonnet, worktree isolado

1. Checkout isolado; a raiz tem alterações preexistentes de outras frentes — não transportar nem
   limpar.
2. Testes e instruções da seção 3, com RED→GREEN.
3. Revisão pelo vendor oposto. Não implementar o adaptador do `T-087`.
4. Próxima versão livre nas quatro âncoras, só com autorização (`0.27.11` já pertence a outra frente).

### Ambiente — só com autorização específica

1. Registrar o estado anterior: entrada `user`, demais entradas, caminhos e conteúdo dos caches,
   marcador de órfão, sessões/jobs que os usam.
2. Backup recuperável fora dos diretórios administrados pelo instalador; preservar `1.0.5`, `1.0.2`
   e o `1.0.6` existente.
3. Esperar os trabalhos afetados terminarem; não encerrar brokers ou sessões de outros projetos.
4. `claude plugin update codex@openai-codex --scope user` — se não for possível garantir escopo e
   versão esperada, parar; nada de atualização global, reinstalação genérica ou edição improvisada
   do registro.
5. Atualizar só `codex@openai-codex`, escopo `user`, para **1.0.6**; não atualizar marketplaces em
   bloco.
6. Antes/depois: só a entrada autorizada mudou; registros de projeto idênticos; caches íntegros;
   destino registrado e sem marcador de órfão.
7. Registro atualizado não prova código carregado: a sessão só vale depois do restart.

### Ativação, restart e prova

1. Release do Orquestra só com autorização de versão, publicação e instalação; cache conferido
   contra checkout limpo do SHA remoto aprovado, com o verificador desse checkout.
2. Restart da sessão Claude afetada; `/reload-plugins` não prova agente nem hooks.
3. Conferir o caminho carregado do Companion e a procedência do broker — o código reaproveita broker
   existente, e janela nova não prova renovação.
4. Teste comportamental da seção 5.

## 3. Instruções ao executor (Sonnet)

| Arquivo | Alteração |
|---|---|
| `orq/skills/orq/SKILL.md` (seção "Reúso durável do Codex Companion") | contrato canônico de identidade e degradação |
| `orq/commands/plan-next.md` (~l. 52) | aplicar o contrato antes de aceitar o plano |
| `orq/commands/revisar.md` (~l. 72) | aplicar o contrato antes de aceitar o parecer |
| `orq/commands/elenco.md` (~l. 177 e Matriz) | corrigir a promessa de capacidade e a Matriz |
| `memory/wiki/_elenco.md` (l. 67 e Matriz) | alinhar via e Matriz, conforme decisão do dono |
| `orq/scripts/test_companion_thread_reuse.py` | novas guardas |
| `orq/scripts/test_write_flag_guard.py` | preservar as mutações de escrita; só ajustar fixtures se as linhas-alvo mudarem |

**Contrato canônico (SKILL.md):**

> Uma continuação só pode ser aceita se a chamada terminar com sucesso, devolver JSON válido com
> `status: 0`, `jobId` e `threadId` não vazios, e o `threadId` devolvido for exatamente igual ao
> solicitado. IDs ausentes, falha ou divergência invalidam a continuação.

> Em caso de divergência, preservar o vínculo anterior, registrar IDs solicitado e devolvido,
> caminho/versão do runtime e motivo da degradação. Não aceitar o `rawOutput` como continuação; não
> repetir a chamada, iniciar outra fresca ou recorrer à última thread automaticamente. Não apagar a
> task criada por engano.

Não escrever "ID diferente prova que o runtime não reconheceu a flag": é a causa demonstrada no
1.0.5, mas o sintoma pode vir de encaminhamento incorreto. O diagnóstico geral é "continuação não
comprovada".

**Nos quatro consumidores, regra curta:**

> Continuação exige sucesso e `threadId` devolvido igual ao solicitado. Divergência ou recibo
> incompleto: registrar degradação, preservar o vínculo anterior e não repetir nem substituir a
> thread automaticamente. Aplicar o contrato "Reúso durável do Codex Companion".

Preservar literalmente a frase-âncora que proíbe escrita; não duplicar a opção proibida em novos
exemplos.

**Se o `T-090` for absorvido:**

> `--wait` pertence exclusivamente ao envelope enviado ao `codex:codex-rescue`, para exigir
> foreground. O intermediário deve removê-lo antes de invocar `task`; ele não integra os argumentos
> do runtime nem o briefing. `task` executa em foreground quando não recebe `--background`.

Retirar `--wait` do envelope inteiro deixaria o intermediário escolher background em tarefa longa.
As ocorrências estão em `plan-next.md` e `revisar.md`; `_elenco.md` não contém o token.

**Testes:**

| Nome | Asserção |
|---|---|
| `test_continuacao_exige_identidade_do_thread_id` | os pontos de instrução exigem igualdade entre ID pedido e devolvido |
| `test_recibo_exige_sucesso_e_ids_presentes` | o contrato exige `status: 0`, JSON válido e os dois IDs |
| `test_divergencia_preserva_vinculo_e_proibe_retry` | degradação, vínculo preservado, sem fallback automático |
| `test_wait_e_controle_do_envelope_nao_do_task` | distingue envelope e runtime; exemplos finais de `task` sem `--wait` |
| `test_via_codex_delega_modelo_ao_time_do_host` | a via não mantém `@ max` como segunda fonte |

Conferir as cláusulas **na seção relevante**, não no documento inteiro. Sensibilidade: mutar em
cópias temporárias a igualdade, a preservação do vínculo e a separação de `--wait` — cada mutação
reprova a guarda correspondente. Manter os testes de escrita nas cinco superfícies e o alias de
hífen único; nada de `skip` nem asserção enfraquecida. Rodar os três comandos obrigatórios do
`CLAUDE.md`. O Manager registra evidência na thread e move o card.

## 4. Riscos e rollback

- O `T-093` provou remoção de cache no **host Codex**; não garante que este update preserve todos os
  diretórios no Claude. O Companion tem hooks com caminho dentro do cache, e o `SessionEnd` encerra
  broker e limpa jobs — restart durante trabalho ativo pode interrompê-lo.
- **Rollback de ambiente:** interromper chamadas; restaurar caches afetados do backup, conferindo
  conteúdo; restaurar **só a entrada `user`** anterior (1.0.5, campos originais), sem sobrescrever o
  registro inteiro se houver mudança concorrente; preservar registros de projeto e o cache 1.0.6;
  reiniciar só a sessão afetada e verificar. Voltar ao 1.0.5 deixa o reúso degradado, nunca
  silencioso.
- **Rollback de produto:** reversão em Git e release corretivo autorizado; nunca reusar versão
  publicada com bytes diferentes.

## 5. Critérios de aceite

- Registro `user` do Companion aprovado; demais registros preservados; caches anteriores íntegros.
- Caminho carregado e broker conferidos após restart.
- RED→GREEN demonstrado; os três comandos obrigatórios com exit 0.
- Release autorizado e cache do Orquestra validado contra fonte remota limpa.
- Teste pela rota real `Claude → codex-rescue → task`, com vínculo sintético separado dos reais,
  duas chamadas, sem retry, foreground e sem escrita:

| Chamada | Pedido | Exigido |
|---|---|---|
| 1 | `--fresh --json`, modelo/effort normativos, read-only; memorizar marcador sintético | exit 0, `status: 0`, IDs presentes; `threadId=A` |
| 2 | `--resume-thread A --json`; pedir o marcador sem reenviá-lo | exit 0, `status: 0`, `jobId` novo, **`threadId=A`**, marcador correto |

IDs conferidos no JSON do runtime, não em texto do modelo. Ausência de arquivos alterados, sozinha,
não prova o sandbox efetivo.

## 6. Decisões sugeridas pelo planner

1. Absorver `T-090` — sim, limitado a envelope/runtime e seus testes.
2. Atualizar o Companion `user` para 1.0.6 — sim, com backup, janela e rollback. Escopo `user` afeta
   os projetos que herdam essa instalação.
3. CLI duplicada — não neste card.
4. `_elenco.md:67` — sim, "conforme `## Times por host`", preservando `gpt-6-astra@xhigh`.
5. Bump/release/restart — decidir depois da revisão do diff; não atualizar o host Codex de carona.

## 7. Sem prova

Continuação real no 1.0.6 após restart; comportamento do instalador sobre caches, marcadores e
escopo nesta máquina; caminhos carregados pelas sessões e brokers vivos; modelo/effort/sandbox
efetivos; aplicação infalível da pós-condição pelo Manager (enforcement determinístico é do
`T-087`); testes e release não executados.

## Auditoria do Manager (2026-09-28)

- **Aceito:** causa raiz, pós-condição de identidade, diagnóstico "continuação não comprovada",
  separação envelope/runtime do `--wait`, preservação dos escopos de projeto, rollback só da entrada
  `user`.
- **Ajuste 1 — pré-checagem de capacidade removida deste card.** O planner propôs "confirmar o
  caminho da instalação efetivamente carregada" antes de continuar, sem procedimento executável: o
  Manager não enxerga o `CLAUDE_PLUGIN_ROOT` do Companion, e uma regra sem como verificar é
  ambígua. A pós-condição de identidade já impede aceitar continuação falsa; homologar instalação
  por caminho e capacidade é o escopo do `T-087`. O teste `test_capacidade_de_resume_deve_ser_comprovada`
  sai.
- **Ajuste 2 — checar a versão do upstream antes do update.** `claude plugin update` leva à "latest
  version" e pode atualizar o catálogo. Antes de rodar, conferir, sem escrever nada, a versão que o
  upstream `openai/codex-plugin-cc` publica; diferente de 1.0.6 → parar e perguntar, porque seria
  código não auditado.
- **Ajuste 3 — ordem.** Recomendo ambiente **antes** do produto, divergindo do planner: com o 1.0.6
  carregado, a segunda rodada do reviewer deste próprio card já consegue continuar pelo `threadId`.
  Custo: dois restarts ao longo do card em vez de um.
- **Degradação declarada:** o plano não voltou ao planner para esses ajustes porque a continuação do
  mesmo `card+papel` é justamente o que está quebrado no 1.0.5; uma chamada fresca criaria outro
  vínculo. Os ajustes são do Manager e ficam sujeitos à revisão cross-vendor da implementação.
