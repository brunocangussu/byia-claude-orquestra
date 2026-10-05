## RECHECAGEM

**B1 da R8 (a evidência selada alegava cobrir o ramo symlink, mas o teste usava symlink para diretório): CORRIGIDO.**

Verifiquei só por inspeção do texto do pacote. Não executei nada.

**1. O teste novo é eficaz contra o ramo symlink**
- `test_v6_integrity.py:82-92` monta, dentro de `TemporaryDirectory`, a árvore `project/docs/experimentos/T-098-A2/candidata-r8-v6-local`.
  - Conferi a raiz: `_project_root` usa `parents[3]` e resolve exatamente para `project`.
  - O alvo `target.txt` é um arquivo regular.
- `test_v6_integrity.py:106` é o controle positivo: `_project_file(candidate, "target.txt")` devolve `self.target`.
  - Os dois lados são caminhos resolvidos, então o `/var`→`/private/var` do macOS não quebra a igualdade.
- `:107-110` cria `inside-link.txt` → `target` e afirma `is_file() == True` e `is_symlink() == True`.
  - Isso fecha exatamente o buraco da v5. O symlink para diretório tinha `is_file() == False`, então o ramo `not path.is_symlink()` nunca decidia nada.
  - Aqui o `is_file()` passa, e só `not is_symlink()` rejeita.
- `:111-113` rejeita os cinco casos: absoluto interno, `dir/../target.txt`, ausente, diretório e o link.

**2. Os três mutantes são mortos**
- **Sem `is_symlink`** (`:118-119`): o mutante aceita o link. O `relative_to` passa, porque o alvo está dentro do projeto.
- **Sem guarda relativa** (`:121-123`): o mutante aceita o absoluto interno e `dir/../target.txt`.
- **Sem `is_file`** (`:125-127`): o mutante aceita o caminho ausente.
- As strings substituídas aparecem uma vez cada em `_project_file`, e o `assertEqual(count, 1)` garante isso.
- Também conferi o efeito no próprio `preflight.py`: remover `and not path.is_symlink()` (`preflight.py` ≈76, em `_project_file` ≈69-81) derruba:
  - `test_v6_integrity.py:113`, com o link deixando de ser rejeitado;
  - o `count == 1` de `:100`;
  - `test_mutations.py` ≈101-117;
  - o selo, porque `preflight.py` é coberto pelo hash.

**3. O teste é descoberto e selado**
- O nome `test_v6_integrity.py` casa com `test_*.py`.
- O arquivo está em `manifesto.json:7-19` e em `selo-congelamento-r8-v6.json:5-31`.
- `validate_manifest` exige essa lista literal.
- `verify_v6_local_seal` roda dentro de `run_local_preflight`, que é chamado por `test_preflight.py`.

**4. A evidência foi retificada**
- `evidencias-bancada-local.md:27-31` descreve com precisão o que o teste faz:
  - o controle positivo;
  - os cinco casos rejeitados;
  - os três mutantes.
- A afirmação falsa da v5 (`:28`) não foi regravada, como pedido.

**5. O teste não muta mais o diretório congelado**
- A fixture fica toda em `TemporaryDirectory`, e o caminho específico de macOS (`/private/tmp`) sumiu.
- Isso resolve também o R8-risco 5.

**6. O metadata baseline está preservado integralmente**
- `validate_full_metadata_baseline` compara, para os 48 IDs, `gold`, `split`, `family`, `policy_code`, `facts` e `rationale` contra o manifesto v1 ancorado por hash.
- Compara também `policy_codes`, `taxonomy` e `batches` por JSON canônico.
- Conferi por amostragem o manifesto v6 contra o v1, incluindo Y007, Y011, Y028, Y041, Y042 e Y045, e os três blocos globais: são iguais.
- Os mutantes de `test_v6_integrity.py:35-61` cobrem cada campo e cada chave global.
- O oráculo de adjudicação dispara em `Y007` antes de `Y020`, que é o par da troca, na ordem `sorted`. A mensagem de `startswith` confere.

**7. Sobre a qualificação do Manager**
- Ficou demonstrado pelo texto:
  - o complemento externo da v5 tinha selo no inventário externo e exigência de comando separado, mas não entrava no selo da v5 nem na descoberta da suíte;
  - a v6 internaliza o teste;
  - por isso, "ausência histórica total" não se sustenta, e "correção dentro da candidata" se sustenta.
- Não aceito como provado:
  - as contagens (447/31) e os exit codes;
  - os 13/13 hashes;
  - o RED do oráculo contra a v4, porque o `preflight.py` da v4 não está no pacote.

## BLOQUEADORES

Nenhum.

## RISCOS

1. **O selo da v6 é autodeclarado.** Nada dentro da candidata ancora o hash de `selo-congelamento-r8-v6.json`. Quem editar `preflight.py` e regravar o selo passa no preflight. A mitigação depende da conferência externa de hashes pelo Manager. A limitação está declarada no recibo.
2. **Matar mutantes de `preflight.py` é em parte trivial por causa do selo.** Qualquer edição já quebra o hash. A discriminação real vem das asserções dirigidas de `test_v6_integrity.py:105-127`, que existem.
3. **A suíte exige `symlink_to`.** Em ambiente sem permissão para criar symlink, ela falha com erro, não passa em silêncio. Não afeta o macOS declarado.
4. **Continuam como limites, não como defeitos:**
   - o atalho lexical "Ainda não foi/há" em abster no dev;
   - a precisão de 3/3 do "?" em consulta;
   - a fronteira discutível do Y042;
   - o RED histórico da v4, que não é verificável aqui.

   Estão declarados em `politica-e-limites.md` e em `evidencias-bancada-local.md:35-43`.
5. **Nomes herdados enganosos:** `load_v5` em `test_mutations.py`/`test_preflight.py` e `r5_preflight_for_r7_v5_tests`. São só cosméticos.

## COBERTURA

Examinei somente o texto colado:
- o parecer R8, a auditoria Manager e o handoff v6;
- da candidata v6: `amostra`, `manifesto`, `preflight`, os dois oráculos, os três `test_*.py`, `evidencias`, `politica`, `recibo`, `regra` e `selo`;
- `amostra` e `manifesto` da R6 v1.

Ficaram fora do pacote, então não verifiquei:
- os arquivos v4/v5 e o complemento externo;
- o JSON de gates;
- a correspondência dos SHA-256 com os bytes reais.

A execução e os exit codes são declarados pelo Manager, não reproduzidos aqui. Não usei ferramentas nem plan file, conforme a instrução de revisão sem ferramentas. GO significa fechamento deste review delimitado. Não é autorização de campanha, Git, release ou adoção.

## VEREDITO

GO
