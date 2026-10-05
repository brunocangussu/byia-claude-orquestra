# T-098 — recuperação e baseline pós-R4

2026-10-02. Registro local do Manager dentro do plano de correção aprovado.
A candidata nova ainda não contém amostra/gabarito corrigidos; este registro
não é R5, revisão independente, aprovação do gold ou classificação por LLM.

## Fontes preservadas

- Pacote R4: 51.176 bytes, SHA-256
  `0934fda33cdca92add01e4fb8f4dfbaaa8543d26470d08605e787900349e4281`.
- Amostra R4: 17.314 bytes, SHA-256
  `a69c8eac25ac8981ded509c9f1e4cb7df7aa796124357c945db5a4e8b53642ea`.
- Auditoria: `../revisao-r4-execucao-2026-10-02/auditoria-manager.md`.
- Plano aprovado: `docs/plano-correcao-local-pos-R4-T-098-T-131.md`.

## Verificações executadas nesta retomada

Baseline com descoberta, sem gerar bytecode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s docs/experimentos/T-098-A2/candidata-r4 -p 'test_*.py'
```

Resultado: exit 0, **14 testes OK**. Não houve edição da R4.

A cascata descrita no parecer também foi executada em memória sobre os
textos congelados, nesta ordem e com case normalizado:

1. `não sei|não tenho|não consigo informar|não foram informados|não está decidido|ainda não defini` → abster.
2. `explique|entender|diga apenas|mostre a conta` → consulta.
3. Apóstrofo ou `pontos finais` → trivial.
4. `.py|.json` → pequeno.
5. `implemente|construa|acrescente|instrucoes.md` → normal.
6. Restante → alto_risco.

Resultado: **24/24 dev e 24/24 reserved**, sem divergências. Diagnóstico
pós-hoc com gabarito conhecido, não regra derivada somente do dev, não
medição cega e não benchmark de modelo. Ele reproduz o bloqueador lexical;
o baseline estrutural verde não o invalida.

## Borda da próxima execução

Preservar os IDs, gold, partições e as 18 famílias; produzir textos novos
com ações/escopos explícitos, sem marcadores exclusivos por classe. Y006
precisa ser reparo observável conforme contrato fechado. Os pares de
esqueleto repetido exigem análise por mecanismo, não só Jaccard.

Não existe checkout dedicado T-098 no inventário atual de worktrees.
Este registro não autoriza criar checkout/branch, escrever código na main
ou reutilizar o worktree T-131 como se fosse a frente T-098. A documentação
preparatória está isolada neste diretório novo, sem modificar a R4.

Ainda pendentes: amostra corrigida, RED/GREEN e mutações da nova bancada,
regra derivada apenas do dev e congelada antes de pontuar reservado,
gates locais e handoff. Revisão externa e aprovação do gold seguem
separadas. A2: JEV 0/4 e Luna 0/4; B2 0/16. Sem nova inferência,
autenticação, bump, commit, push, merge, instalação ou restart.
