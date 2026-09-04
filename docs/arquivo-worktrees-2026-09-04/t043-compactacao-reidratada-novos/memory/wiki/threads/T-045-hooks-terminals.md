# T-045 — Compatibilidade do `hooks.json` do Terminals com Codex 0.147

**Classificação:** arquitetural, alto risco. A solução cruza a fronteira entre um produtor externo
(Terminals), uma configuração global do usuário, o carregamento de hooks do Codex e os hooks
empacotados do Orquestra.

**Estado do planejamento:** investigação fechada; solução local desenhada; **AWAITING_OWNER
recomendado** para escolher o contrato de corrida da primeira sessão. Somente o Manager pode mover o
card no board.

**Decisão irrevogável do dono — 2026-08-14:** não enviar relatório, pedido ou implementação ao
Terminals/Alison. A mitigação deve ser planejada e, após novo gate explícito, implementada neste
projeto.

## Resultado executivo

O warning não é cosmético. O Codex 0.147 rejeita o arquivo global inteiro porque `_managedBy` não
faz parte do schema; nessa sessão, os hooks globais do Terminals não são registrados. Os hooks do
plugin Orquestra são descobertos por outra fonte e continuam ativos, como já foi provado em processo
novo.

O Terminals 1.11.0 regrava o arquivo incompatível quando abre. Portanto:

- uma edição manual é comprovadamente efêmera;
- nenhuma configuração de precedência do Codex consegue ocultar somente essa fonte;
- `[features] hooks=false` desliga também o Orquestra e não é solução;
- um reparo executado por `SessionStart` chega depois da descoberta e só beneficia a próxima sessão;
- tornar o arquivo imutável apenas põe dois donos em conflito e deve ser rejeitado.

A recomendação local é um **helper de compatibilidade atômico e idempotente**, instalado somente por
opt-in, acionado por um LaunchAgent com `WatchPaths`. O runtime normal do Orquestra **não deve editar
silenciosamente** o arquivo gerenciado. A única exceção proposta é esse componente separado,
explicitamente instalado e reversível, com contrato estreito, backup, auditoria e falha fechada.

Há uma limitação que nenhuma implementação local baseada em `WatchPaths` remove: o LaunchAgent é
assíncrono. Se o Terminals regravar o JSON e iniciar o Codex imediatamente, o Codex pode ler o
arquivo antes do reparo. Nesse caso, a primeira sessão ainda avisa e precisa ser reiniciada uma vez.
Zero warning determinístico na primeira sessão exigiria corrigir o produtor ou interceptar o
launcher do Terminals; as duas opções estão fora da decisão atual.

## Evidências fechadas

### Regeneração e ausência de controle no Terminals

Em 2026-08-14, abrir o Terminals 1.11.0 regravou `~/.codex/hooks.json` no launch:

- `mtime`: `2026-08-14T13:31:05`;
- SHA-256 permaneceu `781655a0ec6315a88ac645cd02c37d9da055d380f3528437eb5fa97d306a82c2`;
- chaves de topo permaneceram exatamente `_managedBy` e `hooks`;
- `_managedBy` permaneceu `terminals.app`.

Isso prova que remover `_managedBy` manualmente não é uma correção durável. A inspeção de
`defaults great.terminals`, de `Application Support/terminals/settings.json`, de Contas e de
Preferências não encontrou toggle para hook/configuração global do Codex. O checkbox
“Sincronizar arquivos de configuração” do workspace estava desligado e controla `CLAUDE.md` e
`AGENTS.md` na raiz; ele não desativa esse hook global.

O binário do Terminals já havia revelado as referências a
`terminals/AgentConfigFilesSection.swift`, `.codex/hooks.json` e ao aviso de arquivo gerenciado. A
fonte do produto é privada, logo não existe linha pública que este projeto possa corrigir ou testar.

### Contrato do Codex

Na tag `rust-v0.147.0`, o tipo `HooksFile` usa `deny_unknown_fields` e aceita somente
`description` e `hooks` no topo:
<https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/config/src/hook_config.rs>.

A documentação oficial confirma:

- todas as fontes de hooks encontradas são aditivas;
- maior precedência não substitui fontes inferiores;
- não existe ignore por fonte;
- `[features] hooks=false` desliga todos os hooks;
- um `hooks.json` válido usa `description` e `hooks` no topo.

Referência operacional: <https://developers.openai.com/codex/hooks>, especialmente “Where Codex
looks for hooks” e “Turn hooks off”.

### Impacto real

O loader falha somente para a fonte global inválida. Resultado observado:

1. os quatro grupos do Terminals no arquivo global não são registrados (`PermissionRequest`,
   `PreToolUse`, `Stop` e `UserPromptSubmit`);
2. perdem-se os sinais que esses handlers forneceriam ao Terminals, incluindo os estados OSC e o
   comando `terminals hook codex`;
3. o runtime de hooks não é desligado como um todo;
4. os seis hooks funcionais empacotados do Orquestra permanecem ativos apesar do warning global.

O comportamento interno de `terminals hook codex` não é auditável sem a fonte privada. Não se deve
ampliar o impacto além do fato comprovado de que o comando não é registrado nessa sessão.

## Causa raiz e fronteira de propriedade

O produtor Terminals grava um campo proprietário em um documento cujo consumidor Codex aplica
schema fechado. O ponto tecnicamente ideal de correção seria o produtor, substituindo `_managedBy`
por `description`; a decisão do dono excluiu essa via. Dentro da superfície controlável, a correção
mais segura é um adaptador explícito na fronteira, não uma mutação embutida no `context-guard.py`.

Regras de propriedade:

- o Orquestra instalado normalmente não ganha autoridade implícita sobre `~/.codex/hooks.json`;
- nenhum hook `SessionStart` pode reparar o arquivo em silêncio;
- somente o helper opt-in pode transformar a forma legada exata;
- qualquer forma desconhecida, customização ou disputa de escrita interrompe o reparo;
- o helper preserva o objeto `hooks` integralmente e troca somente o metadado de topo incompatível.

## Alternativas arquiteturais

| Abordagem | Vantagens | Limites e riscos | Veredito |
|---|---|---|---|
| Helper atômico/idempotente + LaunchAgent `WatchPaths` | Local, automatiza regenerações futuras, reversível, testável e mantém Terminals e Orquestra ativos | Escreve configuração global mediante opt-in; `WatchPaths` é assíncrono e não garante vencer o primeiro startup do Codex | **Recomendada**, com gate sobre a corrida |
| Reparo mutante no `SessionStart` do Orquestra | Não exige LaunchAgent e reutiliza o ciclo do plugin | A descoberta já ocorreu; os hooks do Terminals continuam ausentes na sessão atual. Cria autorreparo tardio e silencioso dentro do runtime | **Rejeitada como reparo**; usar no máximo diagnóstico read-only |
| Arquivo imutável (`chflags uchg` ou permissões) | Impediria a regeneração após uma correção inicial | Combate o dono declarado, pode quebrar o launch/sync do Terminals, tem falhas pouco observáveis, rollback frágil e ainda exige mutação inicial | **Rejeitada** |

Interceptar ou substituir o launcher do Terminals poderia serializar “gerar → reparar → abrir Codex”
e eliminar a corrida, mas passaria a controlar uma rota privada do aplicativo. Não entra no plano
sem nova decisão de escopo.

## Arquitetura recomendada

### Componentes futuros

Arquivos propostos para uma implementação posterior; nenhum é alterado por este planejamento:

- `orq/scripts/terminals-hooks-compat.py`: classificador, normalizador, I/O atômico e comandos de
  ciclo de vida;
- `orq/scripts/test_terminals_hooks_compat.py`: testes unitários, concorrência e instalação;
- `orq/commands/stack.md`: diagnóstico, opt-in, status, desinstalação e avisos;
- `orq/hooks/hooks.json`: somente se o dono aprovar um diagnóstico read-only no `SessionStart`;
- teste do bundle de hooks correspondente, caso o diagnóstico seja adicionado.

Manter o helper separado do `context-guard.py` reduz acoplamento com a máquina de estado de contexto
e permite desinstalá-lo sem alterar o comportamento normal dos seis hooks funcionais existentes.

### Estado instalado

Usar um diretório estável, resolvido no install, por exemplo
`$CODEX_HOME/plugins/data/orq-orquestra/terminals-hooks-compat/` (com fallback documentado para
`$HOME/.codex/plugins/data/...`). Copiar para ele o helper versionado e manter ali:

- backup com modo `0600`;
- lock do helper;
- recibo de reparo com timestamps e hashes, nunca conteúdo de comandos;
- stdout/stderr de baixo volume, sem PII, credenciais ou conteúdo do JSON.

O plist fica em
`~/Library/LaunchAgents/com.byia.orq.terminals-hooks-compat.plist`, com:

- `Label = com.byia.orq.terminals-hooks-compat`;
- `ProgramArguments` absolutos para Python, helper estável, alvo e diretório de suporte;
- `WatchPaths` contendo o caminho absoluto de `~/.codex/hooks.json`;
- `RunAtLoad = true` para normalizar o estado já existente depois do opt-in;
- `KeepAlive` ausente ou `false`;
- `ThrottleInterval` curto e explícito para conter rajadas;
- geração via `plistlib`, não interpolação de shell.

Comandos previstos: `inspect`, `repair-once`, `install-agent`, `uninstall-agent`, `status` e
`restore`. `install-agent` exige confirmação inequívoca e usa `launchctl bootstrap gui/$UID`;
`uninstall-agent` usa `launchctl bootout gui/$UID/<label>`.

### Classificador fail-closed

O helper só pode escrever quando todas estas condições forem verdadeiras:

1. JSON válido e objeto no topo;
2. chaves de topo exatamente `_managedBy` e `hooks`;
3. `_managedBy == "terminals.app"`;
4. `hooks` é objeto e seus eventos, matchers e handlers satisfazem o schema Codex esperado;
5. nenhuma chave extra ou estrutura desconhecida existe;
6. o arquivo ainda tem o mesmo SHA imediatamente antes do replace.

Estados distintos e observáveis:

- `legacy_supported`: pode normalizar;
- `already_normalized`: no-op, sem alterar `mtime`;
- `absent`: no-op;
- `foreign_or_customized`, `invalid_json` ou `unexpected_structure`: falha fechada, sem escrita;
- `changed_during_repair`: retry limitado somente se a nova leitura ainda for legado suportado;
  caso contrário, aborta.

A saída válida tem somente:

```json
{
  "description": "Generated by terminals.app; normalized for Codex compatibility by the Orquestra opt-in helper.",
  "hooks": {}
}
```

O `{}` é apenas abreviação documental. A implementação deve reutilizar o objeto `hooks` lido sem
alterar qualquer evento, matcher, handler, comando, argumento ou valor. O aceite compara igualdade
profunda e SHA canônico do subtree antes/depois; uma mudança de formatação do documento externo não
pode mascarar mudança semântica interna.

### Escrita, concorrência e prevenção de loop

Fluxo de uma execução:

1. adquirir `flock` com timeout curto no diretório de suporte;
2. ler bytes, `stat` e SHA do alvo;
3. classificar e validar; qualquer surpresa encerra sem escrita;
4. criar backup byte-idêntico, exclusivo e `0600`; `fsync` do backup e diretório;
5. construir a saída em memória e provar que `before["hooks"] == after["hooks"]` e que o SHA
   canônico do subtree é idêntico;
6. gravar temporário no mesmo diretório do alvo, preservar o modo do alvo, `flush` e `fsync`;
7. reler o alvo e comparar SHA/stat; em divergência, descartar o temporário e fazer no máximo duas
   tentativas classificadas;
8. `os.replace`, seguido de `fsync` do diretório;
9. gravar recibo com SHA de origem, SHA final, resultado e tempo; nunca registrar o JSON.

O lock serializa instâncias do helper; a comparação antes do replace protege contra o produtor
Terminals, que não usa esse lock. A primeira execução muda o arquivo e pode acionar novamente
`WatchPaths`; a segunda encontra `already_normalized`, não escreve e termina. Sem `KeepAlive`, isso
evita loop de autorreparo.

Reparos automáticos nunca são silenciosos no sentido operacional: dependem de instalação opt-in,
deixam recibo consultável e falhas aparecem em `status`. Estrutura inesperada não é “consertada”.

### Diagnóstico de corrida no SessionStart

Não usar `SessionStart` para escrever. Se aprovado, adicionar apenas uma checagem read-only:

- se o arquivo ainda está inválido, avisar que os hooks globais não entraram e pedir reinício depois
  de `status` confirmar o reparo;
- se o recibo de reparo for muito recente, emitir aviso conservador de que esta sessão pode ter
  descoberto o arquivo antes do LaunchAgent e recomendar um único reinício;
- se o arquivo está normalizado e estável, permanecer silencioso.

Essa janela temporal pode produzir falso positivo e não prova a ordem exata entre discovery e
reparo. Ela é contenção observável, não garantia. O teste de aceitação deve medir a corrida real.

## Plano executável TDD

### Fase 0 — gate e preflight

1. Registrar a resposta do dono à pergunta final deste documento.
2. Confirmar que a base integrada não mudou o contrato do Codex nem adicionou uma solução nativa.
3. Verificar qual é o próximo patch livre; se T-044 consumir `0.22.2`, T-045 não pode reutilizá-lo.
4. Confirmar concordância das quatro fontes de versão antes de editar `orq/`.
5. Não instalar agente nem tocar no global durante desenvolvimento; usar diretórios temporários.

### Fase 1 — testes do classificador, inicialmente vermelhos

Criar fixtures sintéticas e cobrir:

- legado exato → `description` + `hooks`;
- igualdade profunda e SHA canônico de `hooks` antes/depois;
- já normalizado, ausente e segunda execução → no-op, sem mudança de `mtime`;
- dono diferente, chave extra, JSON inválido, evento/matcher/handler malformado → falha fechada;
- logs e recibos contêm somente estado, tempo e hashes;
- mensagens nunca imprimem comandos nem o conteúdo do arquivo.

Só então implementar as funções puras de classificação e transformação até os testes passarem.

### Fase 2 — testes de I/O atômico e concorrência

Antes do código de escrita, testar:

- backup byte-idêntico, exclusivo, `0600` e sincronizado antes do replace;
- falha em cada etapa deixa o alvo original íntegro;
- temporário no mesmo diretório, `os.replace` e `fsync` do pai;
- duas instâncias concorrentes produzem um reparo efetivo e nenhum arquivo parcial;
- regravação do produtor entre leitura e replace é detectada pelo CAS;
- retry é limitado e nunca sobrescreve uma forma inesperada mais nova;
- segunda ativação causada pelo próprio replace é no-op e não cria loop.

Implementar lock, backup e replace somente após os testes falharem pelo motivo esperado.

### Fase 3 — ciclo de vida do LaunchAgent em ambiente falso

Com HOME, alvo e `launchctl` falsos, testar:

- plist com label, argumentos absolutos, `WatchPaths`, `RunAtLoad`, `ThrottleInterval` e sem
  `KeepAlive`;
- instalação exige confirmação explícita;
- reinstalação da mesma versão é idempotente;
- plist existente de outro dono ou conteúdo divergente causa abort, nunca overwrite;
- `status` distingue instalado, carregado, reparado, falha fechada e corrida possível;
- uninstall remove somente plist/helper com assinatura esperada e preserva backups;
- fora do macOS, instalação falha com instrução clara e sem escrita.

### Fase 4 — integração macOS isolada

Usar arquivo temporário e label exclusivo de teste, nunca o global real:

1. `bootstrap` do plist de teste;
2. simular uma gravação atômica do legado pelo produtor;
3. aguardar por prazo máximo definido e observar normalização + recibo;
4. comparar `hooks` integralmente;
5. provar que o segundo acionamento é no-op e que o processo não fica reiniciando;
6. `bootout` e remover somente os artefatos temporários.

### Fase 5 — integração com Orquestra e release

- Documentar em `stack.md` instalação, `status`, limite de corrida, uninstall e restore explícito.
- Se aprovado, registrar o diagnóstico read-only como handler separado de `SessionStart` e atualizar
  testes que enumeram eventos/handlers; os seis hooks funcionais preexistentes devem continuar
  idênticos.
- Rodar os testes do helper, a suíte do context guard se o bundle mudar,
  `claude plugin validate ./orq --strict` e `python3 orq/scripts/lint-coerencia.py .`.
- Fazer o bump coordenado para o próximo patch livre somente após aprovação: manifest do plugin,
  marketplace, README e memória de versão devem concordar.
- Não publicar, instalar release nem alterar config global sem gate separado do dono.

### Fase 6 — aceite real autorizado

Somente após aprovação específica para mutar a máquina:

1. capturar SHA/stat do global e criar backup byte-idêntico sem expor conteúdo;
2. instalar e carregar o LaunchAgent opt-in;
3. fechar e abrir Terminals; provar a regeneração legada e o recibo de normalização;
4. confirmar chaves finais `description` + `hooks` e igualdade integral de `hooks` com o backup;
5. abrir um processo Codex novo e confirmar ausência do warning;
6. em `/hooks`, confirmar Terminals e Orquestra como fontes distintas, sem bypass de confiança;
7. disparar eventos sintéticos inócuos dos quatro grupos do Terminals e dos seis hooks funcionais do
   Orquestra;
8. repetir várias vezes “regravação legada + startup imediato do Codex” e registrar quantas vezes o
   Codex venceu o watcher;
9. se houver corrida, confirmar aviso/reinício único e que o processo seguinte carrega as duas
   fontes.

Não definir “zero warning na primeira sessão” como critério oculto: esse resultado não é garantível
pela arquitetura recomendada. Se o dono exigir zero, retornar a AWAITING_OWNER com a necessidade de
ampliar o escopo.

## Gates de aceite

- **G0 — contrato arquitetural:** dono aceita ou rejeita explicitamente a possível reinicialização
  única.
- **G1 — implementação isolada:** todos os testes sintéticos passam sem tocar em HOME real.
- **G2 — segurança:** revisão prova fail-closed, backup, CAS, idempotência, logs sem conteúdo e
  uninstall restrito aos artefatos próprios.
- **G3 — mutação local:** autorização separada para instalar LaunchAgent e normalizar o global.
- **G4 — runtime:** processo Codex novo sem warning; quatro grupos do Terminals e seis hooks
  funcionais do Orquestra registrados e exercitados separadamente.
- **G5 — corrida:** resultado do stress documentado. Qualquer corrida deve ser detectável e resolvida
  com um único restart; zero determinístico exige nova arquitetura.
- **G6 — release:** validação/lint/versionamento coordenados; publish/install somente após aprovação.

## Riscos e contenções

- **Perda ou alteração de handlers:** deep equality + SHA canônico do subtree antes do replace;
  abortar em divergência.
- **Dois escritores:** lock local + CAS contra o Terminals + retry curto e limitado.
- **Loop do WatchPaths:** transformação idempotente, no-op sem `mtime`, sem `KeepAlive`,
  `ThrottleInterval` e teste de estabilidade.
- **Reparo invisível:** opt-in, recibo/status e diagnóstico conservador; nenhuma mutação no
  `SessionStart`.
- **Falsa sensação de sucesso:** ausência do warning não basta; exigir `/hooks` e eventos vivos das
  duas fontes.
- **Arquivo customizado:** sentinela e topologia exatas; qualquer campo adicional falha fechado.
- **Atualização futura do Codex/Terminals:** `inspect` deve reconhecer quando o workaround deixa de
  ser necessário e nunca reescrever schema desconhecido.
- **Colisão de release com T-044:** escolher o próximo patch livre a partir da base integrada.

## Rollback

1. `bootout` do label exato;
2. remover somente plist e cópia estável cuja assinatura/conteúdo esperado pertença a este helper;
3. preservar backups e recibos por padrão;
4. não restaurar silenciosamente o JSON inválido: com o agente desligado, o próximo launch do
   Terminals já volta a gerar sua forma original;
5. se o dono pedir restore de um backup específico, exigir `--backup`, SHA atual esperado e
   confirmação; usar o mesmo fluxo atômico/CAS;
6. em qualquer divergência, parar e instruir revisão manual, sem force e sem `chflags`.

## Pergunta exata ao dono

> Você aprova implementar o helper atômico/idempotente + LaunchAgent `WatchPaths` opt-in e
> reversível, aceitando o limite explícito de que uma abertura imediata do Codex pode vencer o
> watcher e exigir uma única reinicialização — detectada e avisada —, ou exige zero warnings já na
> primeira sessão? Zero determinístico não é garantível sem modificar o Terminals ou interceptar o
> launcher dele, ambos fora da decisão atual.

**Recomendação do Planner:** aprovar a primeira opção, incluindo o diagnóstico read-only de corrida,
e manter instalação/mutação global sob um segundo gate após testes isolados.

## Handoff ao Manager e checkpoint de recuperação

- Solicitar ao Manager que registre **AWAITING_OWNER** e leve somente a pergunta acima; este Planner
  não altera o board.
- Não enviar nada ao Terminals/Alison.
- Não editar manualmente `~/.codex/hooks.json`; o Terminals provou que a edição é efêmera.
- Não iniciar implementação, instalar plist, executar `launchctl`, alterar produto/configuração ou
  fazer Git antes dos gates.
- Ao retomar, reler esta thread, obter a resposta do dono ao G0 e começar pela Fase 0. Se a resposta
  aceitar a corrida, escrever primeiro os testes da Fase 1; se exigir zero warning, não codificar e
  devolver a decisão de ampliação de escopo.

⏭️ RETOMAR AQUI
