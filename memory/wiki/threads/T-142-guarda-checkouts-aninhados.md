# T-142 — guarda de OBSERVATION_TYPES inclui checkout histórico aninhado

Estado: BACKLOG, sem aprovação de implementação. Registro N0 do Manager
durante a verificação final das R4 T-098/T-131; não é alteração do T-081,
nem transferência da frente economia. Front dona deste registro:
prontidao-jev; host que diagnosticou: Codex. Não criou chat na interface.

## Reprodução e evidência

Em 2026-10-02, suíte discover da main: 447 testes, uma falha em
test_superficies_prescritivas_nao_prescrevem_chave_morta.
Manifesto estrito/lint/diff-check exit 0. A frente T-131 tem 484 testes OK.

achar_prescricoes_mortas(), em orq/scripts/test_observation_types_guard.py:93,
consome superfícies do checkout aninhado
.claude/worktrees/agent-a054e5c8dd838fcb5/ e retorna quatro arquivos históricos.
O teste :112 exige lista vazia. Reproduzido sem alteração, rede ou modelo.
A guarda é byte-idêntica ao HEAD, e as quatro testemunhas têm mtime de
2026-09-29, anterior às R4.

Recibo/diagnóstico: docs/experimentos/T-098-A2/revisao-r4-execucao-2026-10-02/
verificacao-local.json e verificacao-local.md. Não duplicar ou imprimir o
conteúdo bruto dos logs/testemunhas.

## Hipótese e requisito para o plano

A descoberta mistura o escopo prescritivo da fonte principal com cópias
de outras árvores de trabalho. Investigar descobrir_superficies_textuais
e a definição de fronteira do repositório antes de decidir o filtro.
Não resolver removendo o checkout, relaxando a proibição da chave morta,
ignorando indiscriminadamente toda documentação ou editando só a testemunha.

Plano/revisão futura devem provar: prescrição real na fonte principal
continua detectada; logs históricos já dispensados continuam fora;
checkout aninhado não é produto desta fonte; superfície normativa legítima
não é omitida. Cobrir cópia e worktree com .git arquivo/diretório, conforme
a causa realmente verificada, sem inventar plataformas não observadas.

## Escopo e gates

Só registro/reprodução foram feitos. Mudança no teste/descoberta precisa
de plano aprovado e RED/GREEN/mutações. Sem implementação, remoção de
checkout/branch, bump, commit, push, publicação, instalação ou restart.
Não contar esta falha como quarto bloqueador do parecer T-098.
