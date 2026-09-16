# T-094 — Mini-revisor Luna nos dois hosts: plano de implementação

> **Status: aprovado para implementação e canários isolados em 2026-09-10. Em 2026-09-13, o dono
> escolheu estacionar T-062 em 6/6 e iniciar o canário Codex isolado. Sete chamadas de bancada
> foram feitas no total. No par final G/H, G passou e H achou a contradição com snapshot literal,
> mas o oráculo predeclarado reprovou uma referência O1 semanticamente pertinente. Não converter
> essa falha formal em aprovação retroativa. A configuração/guarda isolada B1 foi desenvolvida em
> worktree com fábrica desligada; nada foi integrado ao Loop A, publicado ou ativado.**
> Para agentes executores: usar a skill `superpowers:executing-plans`, respeitando a Matriz do
> Orquestra, o worker único por card e os gates do projeto. Este documento não autoriza release.

**Objetivo:** detectar contradições e lacunas no briefing antes de gastar com implementação,
usando uma única checagem auxiliar `gpt-5.6-luna@max`, disponível no Claude Code e no Codex.

**Arquitetura:** acrescentar B1 ao Loop A existente, depois da avaliação do Manager e antes da
aprovação do dono. Reusar as vias de execução do Orquestra, sem serviço, banco, fila ou novo loop.
O revisor formal continua único e cross-vendor; B1 não examina o produto implementado.

**Tecnologia:** instruções Markdown do plugin, executores existentes e testes Python `unittest`.
**Especificação:** seções 1–6 deste documento; evidência sintética em
[`avaliacao_T-094-mini-revisor.json`](avaliacao_T-094-mini-revisor.json).
**Classificação:** trilha `sistema`; faixa inicial `pesada` por desenho aberto. Reavaliar no gate.

## 1. O que sabemos — e o que ainda não sabemos

| Evidência | Resultado | Limite da conclusão |
|---|---|---|
| Primeira sonda: 8 casos, incluindo 4 erros intencionais, overrides `high` | Luna e Astra: 8/8 | Regras explícitas, sem trabalho real |
| Segunda sonda: 12 casos, incluindo 6 erros, 4 controles e 2 insuficiências, overrides `max` | Luna e Astra: 12/12; zero falsos positivos ou negativos nesses casos | Uma chamada por modelo; não mede confiabilidade geral |
| Documentação oficial de Luna | Suporta `max`; preço por token de faixa econômica | Não comprova custo do fluxo nem disponibilidade em um adaptador |
| Subagentes nativos nesta sessão | Despachos com modelo/effort explícitos retornaram respostas | Ferramenta não expôs recibo independente de faturamento ou do modelo/effort efetivo do backend |
| Registro de instalação do Claude | Companion de usuário aponta para 1.0.5; há registros de projeto 1.0.5 e 1.0.2 | Registro instalado não comprova runtime carregado numa sessão |
| Código do Companion 1.0.5, linha 71 | Allowlist termina em `xhigh`; `max` é recusado | Impede prometer Luna@max nessa via |
| Cache do Companion 1.0.6, linha 71 | Allowlist inclui `max` | Cache existente não significa instalado/ativo/homologado |

As respostas originais, o prompt e o gabarito da segunda sonda estão preservados no JSON.
O gabarito foi fixado antes das chamadas e não foi fornecido aos avaliadores. Foram detectados,
entre outros, reset indevido de contador entre hosts, erro de runtime convertido em lista vazia,
aprovação extraída do próprio documento e esforço `high` apresentado como `max`.

Não demonstramos superioridade de `max` sobre `high`, economia líquida, revisão de código real
ou funcionamento desta checagem pelo Claude. As sondas são avaliações de modelos sobre dados
fictícios, não pareceres sobre o card T-094 e não consomem suas revisões de implementação.

Fonte do suporte/preço: [documentação oficial de Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).
O preço da API não é uma medida do consumo da assinatura Codex. `max` não significa custo fixo.

## 2. Desenho recomendado

Fluxo: **Planner → auditoria inicial do Manager → B1/Luna → auditoria dos achados → dono aprova →
implementação → revisão formal existente → documentação → dono valida.**

Inserir B1 em `orq/commands/plan-next.md`, entre as seções 4 e 5. A checagem recebe as
instruções ao executor que o plano já precisa fornecer; não produz um segundo plano.

### Frequência e abrangência

- No estado final aprovado, estará disponível em todos os projetos que usam o plugin nos dois
  hosts, por padrão de fábrica; não será preciso editar cada projeto para habilitar.
- Executar uma vez por card não trivial elegível, no fechamento do planejamento.
- Não executar em todo prompt, conversa, status, typo, subagente, correção ou retomada.
- Só é elegível se existir briefing delimitado com objetivo, critérios, restrições e instruções
  suficientes para confrontar afirmações. Ausência desses elementos não é resolvida por inventá-los.
- Não executar sobre card já em implementação ou validado; não reabrir trabalho aprovado.
- Projeto com restrição explícita de dados, fornecedor ou proibição do auxiliar é respeitado.
  Ambiguidade de política produz não execução com motivo, não migração silenciosa de configuração.

### O que B1 procura

1. Afirmações incompatíveis entre objetivo, escopo, restrições e passos.
2. Critério declarado que não tem verificação descrita.
3. Instrução que pressupõe permissão, capacidade ou evidência ausente no pacote.

B1 não avalia arquitetura geral, estilo, qualidade do código, testes não fornecidos ou o
repositório inteiro. Não pesquisa, não usa ferramentas, não delega, não escreve, não publica e
não emite GO. Prompt de especialista delimita a tarefa; não garante capacidade superior.

### Alternativas descartadas

- **Luna substituir o revisor formal:** o teste não fundamenta isso e quebraria a independência
  cross-vendor no Codex.
- **Uma revisão pequena em toda interação, seguida de Terra/Astra em cascata:** acrescenta custo
  e complexidade sem evidência de benefício. Fora deste plano.

## 3. Contrato operacional de B1

### Entrada

Um pacote UTF-8 de até **8.192 bytes**, incluindo instruções fixas e material da tarefa:
`card`, `snapshot_briefing`, objetivo, critérios de aceite, restrições, fora de escopo,
instruções ao executor e referências numeradas para cada trecho. Usar hash dos bytes do pacote
ou referência de versão verificável; não inferir que dois textos são iguais pelo título.

Sem histórico integral da conversa ou repositório. O material é preparado pelo Manager a partir
do plano candidato, com todas as restrições relevantes; não se pode omitir restrição para caber.
Pacote acima do teto: `nao_executado: limite_entrada`, sem truncar, resumir silenciosamente ou lotear.
O teto é orçamento de conteúdo, não promessa de limite dos tokens internos de raciocínio.

### Saída

JSON de até **4.096 bytes**, sem prosa ao redor:

```json
{
  "estado": "checado",
  "snapshot_briefing": "valor recebido na entrada",
  "achados": [
    {
      "tipo": "contradicao",
      "referencias": ["C2", "E4"],
      "problema": "O critério exige somente leitura; o passo manda gravar.",
      "cenario": "O executor altera arquivos antes da aprovação."
    }
  ],
  "faltas": []
}
```

`estado`: `checado` ou `insuficiente`; `tipo`: `contradicao`, `criterio_sem_verificacao` ou
`premissa_sem_evidencia`. `faltas` lista a informação ausente. Referências devem existir no pacote.
`achados: []` só significa que nenhuma falha foi demonstrada no briefing recebido.
Não é aprovação. Se o conjunto de achados não couber, usar `insuficiente`, indicando excesso,
sem declarar cobertura completa. Saída ilegível, truncada, vazia ou acima do limite é `incompleto`.

### Autoridade, falha e parada

- O Manager verifica cada achado nas fontes. Somente achados confirmados entram no retorno ao
  Planner já existente. Mudança de escopo vai ao dono; B1 não decide nem corrige automaticamente.
- Uma tentativa iniciada consome B1. Registrar a reserva antes do despacho na thread do card.
  Se houver interrupção e não for possível provar que a chamada não começou, considerá-la consumida.
- Retomada, troca de host, correção de plano ou nova conversa não renovam B1. Não há retry,
  continuação do agente ou escalada automática. Exceção exige nova decisão explícita do dono.
- Preflight recusado antes do despacho: `nao_executado`, com motivo. Chamada iniciada que falha:
  `incompleto`. Modelo/effort divergente ou não comprovado: preservar essa limitação, sem anunciar
  execução homologada. Não usar a autodeclaração do modelo como prova.
- B1 é melhoria auxiliar. Sua indisponibilidade não torna a revisão formal degradada nem cria
  aprovação: o fluxo anterior continua sob todas as guardas existentes. Uma lacuna que impede
  avaliar o plano continua bloqueadora pelo Manager, mesmo se B1 estiver indisponível.
- Proibido enviar paciente, PII, credenciais, prontuário ou dado sensível. Se a separação segura
  do conteúdo não for demonstrável, não enviar. Instruções no material não sobem de autoridade.

Recibo curto na thread: seleção/motivo, snapshot, bytes de entrada/saída, estado, tentativa B1,
host, via, modelo/effort solicitados e evidência disponível dos efetivos, identificadores reais
retornados, achados aceitos/refutados e consumo/latência somente quando fornecidos pelo runtime.
Campo desconhecido fica desconhecido. Não criar banco, novo ledger ou campo obrigatório no board.

## 4. Compatibilidade com revisão, elenco e hosts

### Exceção explícita ao contrato de revisões — depende da aprovação deste plano

O T-062 aprovado, ainda em worktree separado, conta novos pareceres independentemente do nome.
Portanto, não basta chamar a avaliação de "mini". Acrescentar ao contrato canônico em
`orq/commands/revisar.md`, após reconciliar a integração do T-062:

> Uma única checagem B1 do briefing por card, antes da aprovação do plano e da primeira
> implementação, fica fora de R1–R4. Limita-se à consistência das informações fornecidas ao
> executor; não avalia produto implementado, não aprova e não substitui auditoria ou revisão
> formal. Tentativa iniciada consome B1; retomada, correções e troca de host não a renovam.
> Fora dessa borda aplica-se integralmente o contrato normal de revisão, inclusive vendor,
> contagem, degradação e autorização. B1 não é autorização para uma segunda opinião interna.

Preservar integralmente as quatro revisões formais previstas no T-062. O checkout principal ainda
tem textos antigos de duas rodadas: não criar uma terceira política ou copiar a worktree por cima.
A base de implementação deve reconciliar a frente responsável antes de alterar esse contrato.

### Fonte de configuração, sem reescrever todos os projetos

Definir em `orq/commands/elenco.md` uma seção canônica **Checagem auxiliar de briefing**, separada
dos papéis formais e dos presets. Campos por host: habilitado (`sim`/`nao`), modelo
(`gpt-5.6-luna`), effort (`max`). Alterar a frase absoluta "não existe outra tabela ativa" para
explicar essa única exceção e delimitar o uso cross-vendor read-only de B1.

Resolução: seção auxiliar explícita no `_elenco.md` do projeto vence integralmente para o host;
se ausente, usar exclusivamente o padrão do produto. Se presente mas duplicada, incompleta ou
inválida, não executar; não preencher lacunas misturando fontes. Presets de papéis formais não
modificam essa seção. `via OpenAI desligada` no Claude também impede B1.

Durante desenvolvimento e canários, padrão de fábrica **desligado**; chamadas experimentais têm
seleção explícita e não alteram instalações. Após evidência e autorização de adoção geral,
promover o padrão para habilitado nos dois hosts antes da release autorizada. Não é uma promoção
automática pelo sucesso dos testes. Projetos legados não são regravados em massa.

### Execução por host

| Host | Via prevista | Condição |
|---|---|---|
| Codex | Primitiva nativa com override e contexto fresco, documentada na Matriz após prova; alternativa oficial já prevista somente se necessária e homologada | Modelo/effort explícitos; separar pedido aceito de prova do executor |
| Claude Code | `codex:codex-rescue` → Companion pela via oficial homologada | Runtime carregado precisa aceitar Luna e `max`; nunca `--write` |

"Sem ferramentas" é uma restrição do papel; não declarar bloqueio técnico se a via não o expuser.
Verificar permissões e ações no canário. Prompt `read-only` não cria sandbox. Uma via sem prova
suficiente de identidade, esforço e ausência de efeitos não habilita B1 como homologada.

Não copiar as flags legadas conhecidamente problemáticas (`--wait` em `task`, reúso incompatível),
chamar `codex` diretamente no Claude ou construir outro adaptador. Coordenar com **T-087, T-089 e
T-090**, frente de coexistência. Atualização/ativação do Companion é ação separada, sujeita à
autorização do dono e à preservação das sessões/caches (T-047/T-093). Nenhum cache será editado.
Não alterar os modelos ou esforços dos papéis formais como efeito colateral desta homologação.

## 5. Implementação proposta, em uma entrega pequena

### Arquivos e responsabilidades

| Arquivo | Alteração autorizável por este plano |
|---|---|
| `orq/commands/plan-next.md` | Inserção única antes do gate, briefing B1, saída, falhas, registro e auditoria |
| `orq/commands/revisar.md` | Exceção delimitada B1; contrato formal e quatro revisões preservados |
| `orq/commands/elenco.md` | Configuração auxiliar, fallback de fábrica, resolução por host e referência às vias |
| `orq/scripts/lint-coerencia.py` | Guarda da coerência entre ponto de inserção, exceção e configuração auxiliar |
| `orq/scripts/test_briefing_check_contract.py` (novo) | Testes de contrato e mutações negativas, sem chamadas LLM na suíte |
| `memory/wiki/arquitetura.md` | Documentação da única checagem e seus limites |
| `memory/wiki/_elenco.md` | Só a exceção de resolução e procedência da via homologada; não alterar times/presets ou habilitar globalmente neste planejamento |

Não adicionar um novo agente de framework, serviço, runner, schema do board ou lista de revisores.
O prompt delimitado no comando é suficiente para o subagente efêmero. Se a execução real revelar
necessidade de mudar outra interface, parar e ampliar o plano explicitamente; não crescer em silêncio.

### Passos ao executor

- [ ] Confirmar a base integrada do T-062 e a interface homologada da frente T-087/T-089/T-090.
  Sem isso, desenvolver/testar o contrato isoladamente e manter a ativação Claude bloqueada.
- [ ] Trabalhar em worktree próprio, preservando as alterações alheias. Não começar sem aprovação.
- [ ] Criar testes negativos antes da alteração: remover a exceção B1 deve reprovar; introduzir
  a checagem depois do gate deve reprovar; configuração `high` ou dupla fonte deve reprovar.
- [ ] Acrescentar a guarda `validate_briefing_check_contract(raiz: Path, plugin: Path) -> list`,
  seguindo o retorno `(Path, linha, mensagem)` de `validate_elenco_perfis`. Integrá-la ao lint.
  Guardar âncoras de B1, posição entre auditoria e gate, referência à exceção canônica e gramática
  da seção auxiliar; não alegar que busca textual comprova obediência de um LLM.
- [ ] Implementar as três alterações de instrução e o fallback com fábrica desligada. Não alterar
  os presets nem a regra de independência do reviewer.
- [ ] Confirmar que as mutações negativas falham e os documentos coerentes passam; testar projeto
  legado sem seção, seção válida, duplicada, incompleta, host ausente, desligada e effort incorreto.
- [ ] Rodar os três verificadores do projeto e os canários descritos abaixo. Registrar limites.
- [ ] Passar a implementação por revisão formal cross-vendor, com auditoria do Manager, seguindo
  o contrato de rodadas aplicável. Luna não revisa a própria implementação como substituto.
- [ ] Atualizar documentação sobre o resultado final. Levar os resultados ao dono antes de
  promover o padrão de fábrica, publicar, atualizar hosts ou fazer a validação final.

Exemplo autocontido de teste negativo, isolando uma cópia das instruções candidatas:

```python
import importlib.util
from pathlib import Path
import re
import shutil
import tempfile
import unittest


class BriefingCheckContractTest(unittest.TestCase):
    def test_effort_incorreto_reprova(self):
        fonte = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "lint_b1", fonte / "scripts" / "lint-coerencia.py")
        lint = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lint)
        with tempfile.TemporaryDirectory(prefix="orq-b1-") as pasta:
            raiz = Path(pasta)
            plugin = raiz / "orq"
            shutil.copytree(fonte / "commands", plugin / "commands")
            self.assertEqual([], lint.validate_briefing_check_contract(raiz, plugin))
            p = plugin / "commands" / "elenco.md"
            original = p.read_text(encoding="utf-8")
            alterado, n = re.subn(
                r"(\|\s*Codex\s*\|\s*(?:sim|nao)\s*\|\s*gpt-5\.6-luna\s*\|)\s*max\s*\|",
                r"\1 high |", original, count=1)
            self.assertEqual(1, n)
            p.write_text(alterado, encoding="utf-8")
            self.assertTrue(lint.validate_briefing_check_contract(raiz, plugin))
```

O controle positivo valida a fixture antes da mutação, que independe de habilitação `sim`/`nao`.
A tabela auxiliar tem colunas `Host | Habilitado | Modelo | Effort` e linhas `Claude` e `Codex`;
essa gramática integra o contrato da seção 4. Esse teste valida instrução/configuração, não a
capacidade do modelo. Antes da implementação, a função ausente também faz o teste falhar.

## 6. Testes de aceite e adoção

### Guardas automatizadas obrigatórias

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orq/scripts -p 'test_*.py'
claude plugin validate ./orq --strict
python3 orq/scripts/lint-coerencia.py .
```

Os três devem sair `0`. Falhas de base ficam registradas separadamente, nunca renomeadas como
sucesso. Não substituir descoberta da suíte por uma lista fixa de módulos.

### Canários, sem mudar configuração global

1. Usar prompts e dados fictícios em chamadas explicitamente selecionadas. Não instalar outra
   versão global para fazer a comparação. Simulação é evidência preliminar, não fechamento.
2. Verificar uma execução pequena em cada host, com a via oficial e o mesmo pacote, identidade,
   effort, ausência de ferramentas/escrita e vínculo de chamada. No Claude, somente após a
   autorização e homologação da dependência. Metadados ausentes não viram prova positiva.
3. Exercitar comportamento: contradição inserida, controle correto, dado insuficiente, injeção
   no material, pedido de GO, pacote excessivo, corpo ilegível, tentativa B1 repetida, mudança de
   host, via desligada e effort incompatível. Exigir zero falhas críticas perdidas e zero falsos
   alarmes nos controles fixados; preservar gates, escopo e o saldo de revisões formais.
4. Comparar duas tarefas pequenas e autocontidas: uma com briefing consistente e outra com uma
   contradição intencional. Para cada uma, fluxo vigente versus fluxo com B1, mesmo escritor,
   esforço, contexto inicial e critério de aceite. Contextos novos, sem resposta do outro braço.
   Manter o revisor formal e sua cobertura; não dar uma vantagem diferente a cada braço.
5. Registrar achados realmente confirmados, mudanças aceitas, resultado final, chamadas, latência
   e tokens/custo completos disponíveis. Preparação do Manager e auditoria contam. Não chamar
   correção hipotética de "retrabalho evitado" nem converter preço por token em economia observada.

**Regra de decisão:** se B1 não melhorar o resultado do par defeituoso, prejudicar o controle ou
introduzir bypass, não promover o padrão. Se o custo total mensurável aumentar, apresentar o
trade-off qualidade/custo ao dono; não promover como economia. Sem consumo verificável, custo
permanece indeterminado: eventual adoção por qualidade exige decisão consciente, não promessa.
Um canário favorável autoriza discutir adoção, não prova benefício em todos os projetos.

### Release e reversão

- Publicação, bump, commit/push e atualização de hosts mantêm seus gates próprios. Mexeu em `orq/`,
  a release autorizada inclui os quatro arquivos de versão: `orq/.claude-plugin/plugin.json`,
  Status do `README.md`, `memory/MEMORY.md` e `.claude-plugin/marketplace.json`.
- Depois da release completa, conferir caches de cada host contra fonte limpa aprovada com
  `verify_installed_cache.py`, reiniciar/carregar e realizar teste conversacional nos dois hosts,
  conforme `AGENTS.md` e distribuição. Só isso mais validação do dono permite fechar o card.
- Reversão funcional: desligar a seção auxiliar do host/projeto afetado por solicitação do dono;
  papéis formais e fluxo anterior permanecem. Reversão global é nova alteração autorizada do
  padrão de fábrica/release; nunca apagar caches para "voltar".

## 7. Aprovações e handoff

O pedido "entao vamos prosseguir - o que precisa?" foi tratado como aprovação dos itens 1–2,
mantendo o item 3 separado. O preflight confirmou que o T-062 tem correções e R3 ainda dependentes
de autorização própria; não é somente uma integração mecânica pendente.

1. **Aprovar o desenho B1:** Luna@max uma vez por card elegível, antes do gate do plano, como auxiliar.
   Recomendação: sim, com a exceção explícita de contagem acima e sem substituir revisão formal.
2. **Aprovar implementação e canários isolados:** padrão de fábrica desligado durante validação.
   Recomendação: sim; nenhuma ativação geral ou atualização do Companion fica implícita.
3. **Adoção geral e Claude:** decidir depois dos resultados e da homologação da via instalada.
   Recomendação: manter como gate separado; não rebaixar para `xhigh` silenciosamente.

**Próxima ação:** revisar a implementação isolada B1, reconciliar T-062 antes de inserir a exceção
em `revisar.md` e provar a via Claude antes de qualquer adoção. A sonda G/H consumiu 2/2 chamadas
autorizadas; a referência extra O1 não pode ser apagada do resultado formal. Bump, commit/push,
publicação, instalação, restart e ativação geral mantêm gates próprios.
**Pendência externa:** capacidade Luna@max pelo Companion efetivamente carregado no Claude.
**Fora do escopo:** Kimi/outros hosts, nuvem remota, mudança dos modelos principais, revisão de
produto pelo Luna, alteração de políticas de dados, automação noturna, atualização global agora.

Planejamento por Astra; consolidação e auditoria pelo Manager. Artefatos criados nesta etapa:
este plano, a avaliação sintética e a thread do T-094. O board registra apenas o gate do plano.
