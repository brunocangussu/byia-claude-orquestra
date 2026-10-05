# R1 / lote 1 — Opus 5.5

Recibo: exit 0; `OPUS_MODEL=claude-opus-5-5`; 72,0s; 14897 bytes.
Payload: `lote-01.md`, SHA256 `2be4638a914425dad8044278cf8717b9b2420bde72a103c690235553e7d78304`.
Uma chamada; sem retry. A seguir, transcrição do parecer recebido.

## BLOQUEADORES

1. **`orq/commands/elenco.md:271` e `:191-193`: a guarda de capacidade não tem escopo e não define o que conta como "prova".**
   - **Entrada:** host Claude, `/orq:elenco perfil economia`. O perfil troca `opus` por `sonnet`. O mesmo vale para `/orq:elenco implementer·normal haiku`.
   - **Erro:** o passo 2 exige "prova válida de capacidade para modelo + via + conta/host de cada valor que o perfil alteraria". O texto também proíbe sonda automática e não diz de onde vem a prova. Para `sonnet` ou `haiku` nunca há prova registrada, então a leitura literal recusa toda troca, e a guarda do ajuste (`:191-193`) faz o mesmo. A guarda foi escrita para os modelos que as sondas recusaram (Sol6/Luna6), mas o texto a aplica a qualquer modelo. Isso é uma regressão introduzida pelo lote: o perfil de economia deixa de funcionar.
   - **Correção mínima:** limitar a guarda aos valores marcados como **candidato pendente** (hoje `gpt-6-sol` e `gpt-6-luna`) e dizer onde a prova fica, por exemplo "prova registrada no `_elenco.md`". Valores já presentes no elenco ativo ou nos presets continuam passando sem prova nova.

2. **`orq/commands/elenco.md:191-195`: o lote apagou a única instrução de criar o arquivo de elenco.**
   - **Entrada:** projeto novo sem `_elenco.md`, e o dono faz um ajuste com um valor comprovado.
   - **Erro:** o trecho removido "(crie o arquivo a partir do modelo abaixo se não existir)" não foi substituído. O texto novo só diz "não crie arquivo nem elenco inoperante". Resta a proibição sem o caminho feliz, então o comando não tem como inicializar um elenco. Isso contradiz `:337-338`, que diz que a tabela de fábrica serve para "inicializar um elenco novo".
   - **Correção mínima:** reintroduzir o caminho com prova: "Com prova válida e sem arquivo, crie-o a partir do modelo abaixo; sem prova, pare e peça ao dono…".

## RISCOS

1. **`:316` (Host Claude, `planner·interface`): "capacidade confirmada no uso" contradiz a regra de prova antes da troca de `:271` e `:192`.**
   - **Entrada:** perfil ou inicialização que grava `claude-opus-5-5`.
   - **Erro:** uma leitura trata o valor como isento da guarda; outra bloqueia porque não existe prova anterior ao uso.
   - **Correção:** "ID explícito; exigir identidade exata `claude-opus-5-5` no spawn, divergência reprova" ou citar a prova já obtida.

2. **`:352`: a linha `implementer·leve` ainda diz "(sem effort declarado — ver nota)", mas a nota foi removida (antiga `:340-343`).**
   - **Erro:** a referência aponta para um texto que não existe mais.
   - **Correção:** trocar por "(sem effort declarado — candidato pendente)" ou manter a frase sobre effort em `:357`.

3. **`:85`: o texto ainda diz "só entra **alias** presente no mapa de prova", enquanto `:173`, `:181` e `:353` usam "opção" e passam `--model claude-opus-5-5`, que é um ID e não um alias.**
   - **Entrada:** registrar o reviewer `claude-opus-5-5` no host Codex.
   - **Erro:** uma leitura literal de `:85` recusa o registro.
   - **Correção:** "só entra opção (ID explícito ou alias) presente no mapa".

4. **`:172-181`: o exemplo "pedir `fable` e receber Opus reprova" foi removido.**
   - **Erro:** o objetivo aprovado "fable não vira Opus" deixa de estar dito explicitamente. Sobra apenas "prova por prefixo", sem dizer qual é o prefixo de cada alias.
   - **Correção:** manter uma frase: "pedir `fable` e receber `claude-opus-*` continua reprovando".
   - Observação: a veracidade da afirmação sobre o runner depende de outro lote; não atribuo essa cobertura a este.

5. **`:350`, `:352`, `:354`, `:355`: a proposta de fábrica do host Codex agora tem quatro linhas com modelos que as sondas recusaram.**
   - **Erro:** toda inicialização do host Codex a partir da fábrica cai hoje no ramo "pare e peça ao dono". O comportamento está coerente com a guarda, mas a proposta ficou inoperante na prática.
   - **Correção (opcional):** dizer explicitamente em `:337` que, nesta conta/host, a proposta atual exige escolha do dono.

6. **`:160`: `opus` aparece duas vezes ("`opus` · … · `inherit`, o alias legado `opus`").**
   - **Erro:** fica ambíguo se `opus` puro deve resolver para 5.5, que exige igualdade, ou é legado com prova por prefixo.
   - **Correção:** remover a primeira ocorrência ou dizer "`opus` (alias legado, prova por prefixo)".

## VEREDITO

**REPROVADO.** Os bloqueadores 1 e 2 são regressões introduzidas por este lote: a guarda sem escopo trava perfis e ajustes do host Claude, e não há mais caminho para inicializar o elenco. As correções são pontuais; depois delas e dos riscos 1 e 2, o lote fica em condição de **APROVADO_COM_RESSALVAS**.

*(Revisão feita só sobre o texto do diff. Não usei nenhuma ferramenta, conforme pedido.)*
