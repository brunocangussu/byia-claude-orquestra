---
description: Cardápio por situação — o que dizer pra cada coisa acontecer. Existe pra ser a exceção que o dono digita, não a regra
---

Você pergunta, eu mostro. Apresente o **cardápio por situação** — frases naturais em primeiro
plano, comando entre parênteses só como referência. **Nunca** vire este comando um convite a
decorar sintaxe: quem chega aqui está perguntando "o que dá pra fazer", não "qual o comando".

## Formato

Uma tabela ou lista curta, **por situação**, não por comando:

| Se você diz algo como… | Acontece |
|---|---|
| "quero X" · "tem um problema em Y" · "não gostei de Z" · "não funciona" | Cria o card, planeja, **para pra você aprovar** (`/orq:plan-next`) |
| "pode implementar" · "manda ver" · "aprovado" | Implementa + revisa + documenta (`/orq:implement-next`) |
| "onde paramos" · "o que falta" · "o que preciso decidir" | Mostra o board, começando pelo que espera você (`/orq:quadro`) |
| "terminamos" · "salva aí" · "checkpoint" | Grava o estado durável; no Codex a conversa continua e a compactação fica disponível, no Claude libera o `/clear` (`/orq:checkpoint`) |
| "revisa isso" · "valida isso" | Revisão independente — um revisor do **vendor oposto** ao do host (`/orq:revisar`) |
| "audite a remoção de X" · "prove que X saiu" · "começamos pelo grafo?" | Produz ledger de remoção ou verifica um trace graph-first, offline e sem hooks (`/orq:auditar`) |
| "quem tá revisando" · "troca o modelo do planner" · "tô com pouco crédito, modo economia" | Mostra ou ajusta o elenco de LLMs — inclusive troca o **time inteiro** por contexto de crédito (`/orq:elenco`) |
| "anota isso" · "isso vira card" | Cria o card no backlog, sem tirar você do que está fazendo — planejamento fica pra quando você pedir (aí sim entra o `/orq:plan-next`) |
| "lembra quando a gente…" | Busca primeiro na wiki e depois só em memória confiável do host que não esteja marcada como Dispensada no projeto |
| "tá lento" · "o que falta instalar" | Detecta a stack que falta e instala só o que você aprovar (`/orq:stack`) |
| "o revisor sumiu" · "a statusline está muda" · "não conecta com X" · "parece que o plugin não pegou" | Diagnóstico do ferramental — plugin, escopo, PATH (`/orq:stack --verificar`) |
| "tem um comando pra instalar o Orquestra no Codex?" · "quero testar o Orquestra em outra LLM" | Instala o próprio Orquestra no host alternativo, escopo de usuário (`/orq:instalar`) |
| "vou abrir outra janela pra isso" · "deixa essa parte pra depois" | Registra a frente com nome, marca os cards em curso com `@frente` — pra não colidir com outra janela sua |
| "vou dormir, adianta o que der" | Modo noturno — só planejamento, com limites (`/orq:dormir`) |
| "bom dia" (depois do noturno) | Relatório do que rodou à noite (`/orq:acordar`) |
| Projeto sem `memory/` ainda | Oferece montar a disciplina adaptada ao projeto (`/orq:init`) |
| Você quer conferir a memória agora, sem esperar | Health-check da wiki (`/orq:wiki-lint`) — às vezes já roda sozinho por iniciativa do Manager (regra na skill `orq`); pedir na hora também funciona |
| "quais as possibilidades" · "o que dá pra fazer" | Este cardápio (`/orq:ajuda`) |

Adapte a lista ao que existir **neste** projeto — se `_elenco.md` não tiver a via cross-vendor
ativa, diga que a revisão sai degradada em vez de anunciar um revisor que não vai rodar.

## Regras

- **Frase antes de comando, sempre.** O comando entre parênteses é rodapé, não a resposta.
- A tabela acima, por situação, é o formato certo — cobrir as situações reais nela **não** é o
  que esta regra proíbe. O que não fazer é a versão *manual de referência*: uma lista
  comando-primeiro (nome do comando seguido de descrição), sem a frase que o dono diria, como se
  fosse uma cheat sheet de sintaxe. Frase na frente sempre; se sumir a frase, sumiu o ponto do
  comando.
- Se o dono descrever uma situação que não está no cardápio, responda com o que você faria e
  **não** invente um gatilho novo na hora — gatilho novo se propõe medindo falas reais, não
  adivinhando; se for recorrente, registre a lacuna e trate como card novo.
- Feche sempre com a mesma linha, adaptada ao contexto: **"você não precisa decorar nada — fale
  normal."**
