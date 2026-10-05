# T-131 — disponibilidade Sol 6 / Luna 6 por via

## Estado verificado — 2026-09-24

Atualização autorizada concluída na instalação global existente (`/usr/local`): **0.153.4 →
0.156.1**, via pacote oficial npm. O prefixo foi explícito porque o `npm` atual usa `~/.local` por
padrão; instalar ali criaria outra CLI, em vez de atualizar a que os testes anteriores chamaram.

As duas sondas autorizadas, uma por modelo, terminaram **exit0**, sem retry e sem ferramentas:

| Modelo pedido | Effort pedido | Resposta | Task |
|---|---|---|---|
| `gpt-6-sol` | `low` | `SOL6_OK` | `01a0d444-f6ac-7583-bfd9-f0d3c68d8152` |
| `gpt-6-luna` | `low` | `LUNA6_OK` | `01a0d445-08c9-79b3-8772-48be9ba5e7c7` |

Recibos completos: `docs/T-131-sondas-cli-0.156.1.json`. Mesmo modo de login ChatGPT, sem API key
OpenAI, relogin, alteração de plugins ou restart. SHA256 de `config.toml`, `hooks.json` e elenco
vivo idênticos antes/depois. Nenhum papel foi migrado para Sol/Luna.

**Conclusão:** acesso via CLI comprovado nesta instalação/conta, após a atualização. O erro anterior
não sustenta falta de acesso global. Como os testes ocorreram em momentos diferentes durante um
rollout, não isolar a versão como causa única do HTTP400. A sonda comprova resposta à seleção
explícita do modelo; JSONL não oferece `modelUsage`. Não é benchmark, prova de escrita em worktree
nem validação de todos os efforts. Pendências documentais da R1 permanecem separadas.

## Evidência histórica — 2026-09-23, antes da atualização

- O comando `codex` do PATH resolve para `/usr/local/bin/codex`, link para o pacote npm global; versão **0.153.4**.
- O App instalado é `/Applications/ChatGPT.app`, versão **26.917.51856**. Seu binário embarcado `/Applications/ChatGPT.app/Contents/Resources/codex` anuncia **0.155.0-alpha.16**.
- O catálogo local, identificado como cliente 0.155.0, contém `gpt-6-sol` e `gpt-6-luna` com visibilidade `list`. Isso confirma oferta no catálogo, não prova execução por CLI.
- As duas sondas anteriores pela CLI 0.153.4 retornaram HTTP 400 com “not supported when using Codex with a ChatGPT account”. Essa evidência não autoriza dizer que a conta inteira, o App ou a API não têm acesso.
- Uma nova sonda sintética pelo binário do App, `gpt-6-luna@low`, iniciou a task `01a0d0fc-6169-7562-84f4-3db6058f5d10`, mas não devolveu resposta. Após mais de quatro minutos, somente esse subprocesso foi interrompido por SIGINT (exit1). Sem retry, sem ferramentas ou resultado de inferência observado; não contar como sucesso nem como nova recusa de modelo.

## Evidência do fornecedor

O [changelog oficial](https://learn.chatgpt.com/docs/changelog), em 23/09/2026, registra a CLI **0.156.1** com a adição de Sol 6/Luna 6 ao catálogo. A entrada de 22/09 registra o rollout nos planos elegíveis e a seleção pela CLI. O [guia de Work/Codex](https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex) distingue acesso por plano, workspace e rollout.

## Diagnóstico histórico e limite — 2026-09-23

Há um descompasso **comprovado** entre os runtimes do PATH e do App. A CLI global antecede a atualização de catálogo documentada. Esse é um pré-requisito a corrigir antes de concluir falta de acesso; ainda não está provado que ele, sozinho, causou o HTTP 400 anterior. A sonda do binário embarcado sem resposta não fecha essa causalidade. Não exigir API key OpenAI, relogin nem restart como tentativa sem evidência.

Teste então proposto: atualizar somente a CLI global para 0.156.1 e executar uma sonda por modelo.
Esse gate foi autorizado e cumprido em 24/09, conforme os recibos acima. Antes de ativação no
elenco, permanece a necessidade de validar os papéis e efforts realmente escolhidos.
