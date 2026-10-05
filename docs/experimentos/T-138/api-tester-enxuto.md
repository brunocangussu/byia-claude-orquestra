# Suplemento experimental API Tester — v1

**Estado:** candidato de bancada, não instalado e não utilizado em resultado medido.
Inspiração: [API Tester do Agency Agents](https://github.com/msitarzewski/agency-agents/blob/053ddbbf392a1688fc7043d81529f47ef2cf86c8/testing/testing-api-tester.md),
SHA `053ddbbf392a1688fc7043d81529f47ef2cf86c8`, licença MIT, Copyright (c) 2025 AgentLand Contributors.
Redação própria em português; sem reprodução do código ou da persona do upstream.
Somente o trecho delimitado abaixo entra no prompt dos grupos C/D. Metadados e licença não são
instruções de execução. O teto de 600 tokens depende de medição no tokenizer da via antes do uso;
contagem de palavras ou bytes não será apresentada como contagem de tokens.

<!-- perfil:inicio -->
Dentro do escopo já aprovado, examine a mudança como um contrato de API:

- Identifique entradas, respostas, erros e comportamentos existentes que precisam permanecer.
- Derive casos positivos, negativos e de fronteira do contrato explícito. Diferencie campo
  ausente, nulo, vazio, zero, tipo inválido e limites inclusivos quando forem pertinentes.
- Confirme não só o valor final: confira também status, estrutura da resposta, ordem, duplicatas
  e ausência de efeitos colaterais quando o contrato os especificar.
- Teste compatibilidade com pelo menos um consumidor existente. Não invente requisitos quando
  o enunciado estiver em silêncio; registre a lacuna e seu efeito concreto.
- Para cada defeito corrigido, mostre um teste que falhava antes e passa depois. Asserções devem
  conferir valores esperados, não repetir a implementação para calcular o próprio gabarito.
- Use somente fixtures fictícias locais. Não faça chamadas de rede, carga, autenticação real,
  monitoramento em produção, instalação de dependências ou ampliação de escopo.
- Relate evidências executadas e limitações. Não deduza que passar testes prova segurança,
  prontidão de produção ou ausência de defeitos fora do contrato.

Este suplemento não altera permissões, modelo, papel, gates, política de retry ou revisão
independente. Se não houver mudança de API, aplique somente os itens pertinentes; não crie
trabalho extra para cumprir uma lista.
<!-- perfil:fim -->
