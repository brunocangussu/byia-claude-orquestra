# Thread — T-025 · Comandos que nunca disparam sozinhos

**Frente:** cobertura de gatilho medida · superfície de descoberta · política de iniciativa do Manager.
**Aberta em** 2026-07-30 · **estado: PLANO PRONTO — aguarda gate do dono** · planner `fable`.
**Nada em `orq/` foi editado** — este arquivo é o único artefato.

## O pedido, verbatim (transcript de 2026-07-30, sessão `49b03dea`)

> "Eu também vi que o framework tem vários comandos, e às vezes nem eu lembro quais são os
> comandos. Depois eu queria revisar quais são as possibilidades. O ideal, na verdade, é que seja
> feito automaticamente. O próprio manage[r] e o próprio principal podem decidir o que fazer
> durante o desenvolvimento, o que é necessário fazer."

## A medição (método do T-014: falas reais, não imaginadas)

**Corpus:** 31 mensagens digitadas únicas do dono, extraídas dos transcripts das 4 sessões deste
projeto (`~/.claude/projects/-Users-…-byia-claude-orquestra/*.jsonl`, 26–30/jul). ~24 carregam
intenção (o resto é briefing colado ou resposta a pergunta numerada). As 10 frases do T-014 não
foram preservadas individualmente no log — este corpus foi re-extraído da fonte; os 3 fragmentos
que o log guarda ("queria acrescentar", "siga com suas recomendações", "vale a pena configurar")
batem com ele.

**Estrutural (SKILL.md hoje):** 11 dos 12 comandos têm gatilho na tabela (linhas 63–79).
`wiki-lint`: **zero menções** — confirmado por grep.

**Empírica, por intenção:**

| Intenção | Falas reais | Cobertura hoje |
|---|---|---|
| pedido de mudança | ≥8 ("queria melhorar o relatório…", "queria acrescentar…", "Seria interessante…", "precisa arrumar logo") | ✅ o T-014 consertou o grosso |
| prosseguir/aprovar | 6 ("sim pod eseguir", "pode comecar", "vamos seguir com suas recomendações", "aprova e faça…") | ✅ |
| elenco | 2 ("Quero que faça com o Fable o planejamento" ≈ gatilho listado) | ✅ |
| diagnóstico ferramental | 2 ("não consigo… conectar com o quinho [Kimi]" ≈ "não conecta com X") | ✅ |
| estado/board | 4 — **nenhuma bate literal**: "o que eu preciso fazer agora?", "o que preciso decidir??", "Eu não estou vendo card em lugar nenhum", "retomemos"/"continue de onde parou" | ⚠️ GAP — os gatilhos canônicos ("onde paramos", "cadê o board") **nunca foram digitados por ele** |
| revisar | 1 — "gostaria que validasse tambem com o plugin do codex" — stem "validar" ausente | ⚠️ GAP |
| feedback negativo pós-entrega | "Eu não gostei do formato do CheckPoint, não!" — "não gostei" ausente da description | ⚠️ GAP |
| checkpoint | 1 — "vamo fazer um checkpoint para depois eu dar um clear" — funcionou porque ele citou o nome; a palavra "checkpoint" **não está** na lista de gatilhos | ± |
| lembrar · dormir · acordar · init · **wiki-lint** | **zero falas no corpus** | sem evidência para propor gatilho — ver causa raiz |

**Amostra insuficiente, dito com todas as letras:** para `lembrar`, `dormir`, `acordar` e `init`
não há uma única fala real. **Não proponho gatilho novo para eles** — seria inventar frase, o
defeito que gerou o T-014. Ficam como estão.

## Causa raiz — são três, distintas

1. **`wiki-lint` foi desenhado com o invocador errado.** O dono nunca falou de saúde da wiki em 31
   mensagens ao longo de 4 sessões — e não vai falar: a regra global dele já diz "o Bruno só
   interage; VOCÊ organiza memória". O usuário natural do `wiki-lint` é o **Manager**, não o dono.
   Dar-lhe frase de gatilho repetiria o T-014 ao contrário. A correção é **condição** (parte 3) +
   entrada no cardápio (parte 2), não frase.
2. **Não existe superfície de descoberta.** O mapa intenção→ação vive na SKILL (para o modelo) e no
   README (para quem instala). "queria revisar quais são as possibilidades" foi dito verbatim e não
   casa com gatilho nenhum — virou este card porque foi tratado na mão.
3. **A política de iniciativa não existe.** "Decisões que o Manager toma sozinho" (SKILL.md:181–188)
   só cobre decisões de board. Nenhuma **condição** não-linguística dispara nada — o que não tem
   frase do dono simplesmente nunca roda. Já existe UM precedente com borda certa: "contexto >50% →
   sugira checkpoint em UMA linha, não force" (SKILL.md:88). É esse padrão que falta generalizar.

## Solução

- **Parte 1:** acrescentar à SKILL **só os gatilhos atestados** no corpus (estado, revisar,
  feedback negativo, "checkpoint", "retomemos"). Nada inventado.
- **Parte 2:** gatilho "quais as possibilidades / o que dá pra fazer" → **cardápio por situação**
  ("você diz X → acontece Y"), frases naturais em primeiro plano, comando entre parênteses.
  Recomendo materializar como comando `/orq:ajuda` (custo zero permanente — só entra sob demanda).
  Recusadas: seção fixa no `/orq:quadro` (custo recorrente de tela; ele pediu "de vez em quando",
  não "sempre") e linha no relatório do checkpoint (momento errado + mexe num formato que ele
  aprovou por mockup na 0.13.0 depois de reprovar a 0.12.0 — não re-litigar).
- **Parte 3:** política de iniciativa em **3 níveis**, na seção que já existe:
  - **N1 — age sozinho e relata** (só leitura, nada de escrita): rodar `wiki-lint` quando (a)
    fechar release/marco ou (b) um checkpoint flagrar contradição página×trabalho; relatar achados
    em **uma linha no fim da resposta em curso** — nunca turno próprio, nunca corrigir sem ok (o
    próprio `wiki-lint.md:24` já proíbe).
  - **N2 — propõe em uma linha, uma vez**: `stack` ao flagrar o mesmo atrito 2×; checkpoint com
    contexto >50% (regra existente, vira exemplo do nível). **Teto: 1 proposta não solicitada por
    bloco de trabalho.** Recusou → registra (padrão "Dispensadas" do `_stack.md` / "não re-litigar"
    da thread) e **não repropõe**.
  - **N3 — sempre pergunta**: a lista atual (instalar, irreversível, rumo, aparência) intacta.
  - Transversal: **iniciativa nunca escreve** — mudança continua entrando pelo ciclo.

## Passos (após o gate — nenhum foi executado)

1. `orq/skills/orq/SKILL.md:3-19` (description): acrescentar "não gostei" (bloco pedido de
   mudança), "valida isso" (bloco revisar), "o que preciso decidir" (bloco estado), "checkpoint"
   (bloco fechar), "retomemos"/"continue de onde parou" (bloco retomar), "quais as possibilidades"/
   "o que dá pra fazer" (novo bloco descoberta). Verificar: grep de cada frase; `validate --strict`.
2. `orq/skills/orq/SKILL.md:63,65,66,70` (tabela): mesmas variantes nas linhas de ciclo, quadro,
   checkpoint e revisar. Verificar por leitura + lint.
3. `orq/skills/orq/SKILL.md` (tabela, linha nova): descoberta → cardápio (`/orq:ajuda`). E linha
   **situacional** (como a do init em :79): "fechou release · checkpoint flagrou contradição" →
   wiki-lint por iniciativa. Verificar: lint acusa se `/orq:ajuda` não existir.
4. Criar `orq/commands/ajuda.md` — cardápio por situação; fecho: "você não precisa decorar nada —
   fale normal". Verificar por leitura contra os 13 comandos reais.
5. `orq/skills/orq/SKILL.md:181-188`: expandir para os 3 níveis com as bordas (teto 1/bloco ·
   relato no fim de resposta · recusa registrada não volta · iniciativa nunca escreve).
6. `orq/commands/wiki-lint.md`: bloco curto "quando o Manager roda por iniciativa" **apontando** a
   política da SKILL — a política mora num lugar só. ⚠️ Vocabulário: os lugares que descrevem
   iniciativa passam a ser SKILL + wiki-lint.md + README — o lint não pega divergência entre eles;
   o implementer deve `grep -rn "iniciativa\|sozinho" orq/ README.md` antes e depois.
7. `README.md`: linha do `/orq:ajuda` na tabela (~:121-132) + seção curta da política de
   iniciativa + Status/versão. Conferir se há contagem literal de comandos ("12") a atualizar.
8. Bump **0.14.0 nos quatro lugares** (`orq/.claude-plugin/plugin.json` · README Status ·
   `memory/MEMORY.md` · `.claude-plugin/marketplace.json`).
9. Gates: `claude plugin validate ./orq --strict` + `python3 orq/scripts/lint-coerencia.py .`.
10. Release completo (`marketplace update` + `plugin update` + restart) e `diff -rq` do cache
    vazio; só então os testes do dono abaixo.
11. Pós-validação (dever de checkpoint): atualizar `arquitetura.md` (política de iniciativa é
    desenho novo), log e esta thread.

## Critérios de aceite — o dono usando o produto, pós-release + restart

1. Dizer **"queria revisar quais são as possibilidades"** (a frase real dele) → cardápio por
   situação aparece, sem comando digitado, sem despejar nomes de comando como interface.
2. Dizer **"o que preciso decidir?"** → board com a seção "esperando você" primeiro.
3. Fechar um release → o Manager roda o `wiki-lint` **sozinho**, relata em uma linha e **não
   corrige nada** sem ok.
4. **Contra-teste de intromissão:** num bloco normal sem condição disparada, **nenhuma** proposta
   não solicitada; recusar uma proposta 1× e conferir que ela não volta nos 2 blocos seguintes.
5. `/orq:wiki-lint` digitado continua funcionando (sem regressão).

## Decisões do dono (numeradas — responda "1a, 2…" que destrava tudo)

1. **Forma da descoberta:** (a) comando `/orq:ajuda` + gatilho de frase — **recomendo**: custo só
   sob demanda; (b) seção fixa no quadro — custo em toda visualização; (c) linha no checkpoint —
   re-litiga formato aprovado na 0.13.0.
2. **Nome** (se 1a): `ajuda` — **recomendo** (óbvio ao listar) — ou `possibilidades` (a palavra
   dele, porém longa).
3. **Condição do wiki-lint autônomo:** (a) a cada release fechado + contradição flagrada —
   **recomendo** (sem número mágico); (b) a cada N cards DONE (defina N).
4. **Teto de iniciativa:** 1 proposta não solicitada por bloco — **recomendo**; diga se quer mais
   frouxo ou mais apertado.
5. **Onde o achado do lint autônomo aparece:** (a) uma linha no fim da resposta corrente —
   **recomendo**; (b) seção no relatório do checkpoint — só com seu ok explícito (formato 0.13.0
   foi aprovado por mockup).
6. **Gatilhos atestados extras** (passo 1–2): aplicar? **Recomendo sim** — risco único é a
   `description` crescer (1447 chars hoje; ver Riscos).

## Riscos

- **Tamanho da `description`:** 1447 chars hoje, funciona; o limite formal não está documentado
  localmente. Mitigação: acréscimo mínimo, `validate --strict` e teste comportamental decidem.
- **Ironia do 13º comando:** `/orq:ajuda` só se justifica se a interface for a frase — o cardápio
  nunca deve ensinar o dono a digitar comando.
- **Assistente intrometido:** é o risco nomeado do card — as bordas do N2 (teto, fim de resposta,
  recusa não volta) existem exatamente para isso; o contra-teste 4 verifica.
- **Vocabulário espalhado:** a política ficará descrita em 3 arquivos; erro já aconteceu 4× numa
  sessão — por isso o grep obrigatório do passo 6.

## O que NÃO investiguei (e por quê)

- **Transcripts de outros projetos** onde o orq roda — o corpus é só deste repo; a fala dele em
  projeto-alvo pode ter padrões diferentes. Fora do alcance combinado das fontes.
- **Limite formal da description de skill** — sem documentação local; coberto por gate + teste.
- **Contexto turno-a-turno de cada fala** — classifiquei intenção pelo texto extraído por script,
  sem reler as sessões inteiras (2,5–3,8 MB cada).
- **Custo de rodar wiki-lint em wiki grande** — aqui são ~10 páginas; num projeto-alvo maior pode
  valer delegar a subagente. Se aparecer, é card novo, não escopo deste.

## Escopo — fica de fora

- Enforcement por hook (é `T-001`/`T-002`); perfis de elenco (`T-020`); host alternativo (`T-026`);
  gatilhos para `lembrar`/`dormir`/`acordar`/`init` (zero evidência); qualquer mudança no formato
  do relatório do checkpoint sem decisão 5b explícita; mover cards; editar `memory/` além desta
  thread.

## ⏭️ RETOMAR AQUI

**O plano está pronto e nada foi implementado.** Próxima ação: o **Manager leva as 6 decisões
acima ao dono**. Com as respostas, o card vai a READY e o implementer executa os passos 1–11 na
ordem — os passos 4, 6 e 7 dependem das decisões 1–2; o 3 e o 5 dependem das 3–5. Sem resposta,
o card vira `[!]` com a pergunta exata: "responda as decisões 1–6 da thread T-025-gatilhos".
