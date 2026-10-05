# T-143 — auditoria do Manager da R7

## Decisão

**GO independente com ressalvas não bloqueantes registrado.** Uma chamada
oficial Claude CLI/Anthropic, modelo cliente observado `claude-opus-5-5`,
178.436 bytes, exit 0 em 61,332 s, formato válido. Backend/modelo de servidor
não verificados independentemente. Parecer, log e recibo imutáveis:
`docs/reviews/T-143-R7-rechecagem-correcoes-2026-10-04/`.

B1 (inspeção integral do briefing do Planner) e B3 anterior
(schema/recuperação) foram classificados CORRIGIDO. Não houve bloqueador
novo nem edição do produto após o GO. A rechecagem está encerrada para
este snapshot, sem autorrevisão convertida em aprovação externa.

## Verificação do Manager

- `plan-next.md:43–49` exige inspeção de todo o briefing antes de
  preparação/despacho e explicita precedência sobre o gate de saldo;
  achado sensível para e avisa. Inspeção não autoriza egress.
- `_schema.md:208–211` distingue host e propriedade da frente e deixa
  transferência fora da recuperação; `:245–247` restringe retomada
  à frente dona com raiz/thread existentes. Nenhuma exceção no erro do
  resolver foi introduzida.
- `SKILL.md:394–399` é coerente com o schema. Os quatro mutantes
  estruturais discriminam a redução da inspeção, remoção, transferência
  durante recuperação e retomada universal.
- Treze fontes e o pacote conferidos após o parecer; hashes intactos.
  Dormir/arquitetura têm hashes iguais à R6 e omissão explicitada, não
  alegar nova revisão integral deles.
- Gates frescos do Manager: 465 testes em 51,155 s, manifesto estrito,
  lint e diff-check exit 0. Reviewer não executou esses comandos.

## Ressalvas auditadas, sem modificar o snapshot aprovado

1. **“não higienize por conta própria e envie” — ambiguidade textual
   residual reconhecida**, em `plan-next.md:48`. A frase imediatamente
   anterior manda parar/avisar, e §1b impõe a proibição; não foi demonstrado
   bypass no contrato coerente. A redação sugerida é manutenção futura,
   não correção realizada após o GO.
2. **Guardas de presença, sem negativas — confirmado na guarda R6.**
   `assert_contrato_r6` usa presença e ordem; não proíbe reintrodução
   concorrente de todas as frases ruins. Isso limita a prova dos testes,
   não transforma o snapshot atual em regressão demonstrada.
3. **Teste de ordem não cobre diretamente o gate — confirmado.**
   A comparação é inspeção versus despacho; a precedência sobre saldo
   está na prosa `plan-next.md:48–51`. Não alegar que foi testada
   diretamente ou fortalecida neste passe.
4. **Reenvio no §4 — ressalva anterior, não regressão R7.**
   `plan-next.md:126` não repete o gate; “qualquer briefing” em
   `:43` continua abrangendo reenvio. Registrado sem nova alteração
   ou autorização implícita de chamada adicional.
5. **Transferência “inoperável” — qualificada, não aceita como
   impossibilidade universal.** Não há protocolo runtime novo neste
   card. Na recuperação, trocar frente ou fabricar thread é proibido,
   inclusive entre worktrees. Execução de uma transferência separada
   depende de operação/autoridade humana própria e capacidade comprovada;
   isso não foi medido aqui. O GO não habilita essa capacidade.
6. **Autodeclaração em checkout compartilhado — limite conhecido.**
   Host não identifica sessão e duas janelas continuam podendo colidir;
   o worktree por tarefa/T-092 permanece a separação documentada.
7. **Riscos herdados da R6** (Dormir, timeout, telemetria, duplicação,
   teste autorreferente e ausência de prova LLM/runtime): preservados
   com seus limites, sem promovê-los em bloco a novos bugs. Dormir não
   foi reexaminado nesta R7; hashes iguais à fonte anterior conferidos
   pelo Manager. Não alegar resolução comportamental desses pontos.
8. **Conectores no parecer — descartados como orientação não pertinente.**
   Não há cenário/arquivo que os relacione ao card. Nenhum conector
   era necessário ou foi autorizado/ativado. A menção do modelo não
   prova uso de ferramenta nem exige conectar Gmail/Calendar/Zapier.

## Autenticação e limite de entrega

Uma única `claude auth login --claudeai` autorizada pelo dono terminou
exit 0; status oficial fresco confirmou login via assinatura Claude.
Nenhum logout, token manual, API key ou retry. O acesso foi recuperado;
a causa da indisponibilidade anterior permanece desconhecida e não há
garantia de permanência da autenticação.

T-143, T-131 e bancada T-098 possuem GO independente nos snapshots
registrados. Próximo gate é conciliação/entrega; não pedir revisão
genérica de novo desses mesmos snapshots. Não houve bump, commit, push,
integração, publicação, instalação ou restart. O contrato não está
aplicado em todos os chats/hosts só por estar revisado.
