# Verificação local final — 2026-10-02

Esta verificação não faz novas chamadas a modelos e não corrige os cinco
bloqueadores dos pareceres. Resultado estruturado em verificacao-local.json.

- Frente T-131: **484 testes OK**, manifesto estrito exit 0, lint exit 0,
  git diff --check exit 0.
- Main: **447 testes, uma falha**; manifesto estrito exit 0, lint exit 0,
  git diff --check exit 0. Não reportar a suíte da main como verde.
- Falha: test_superficies_prescritivas_nao_prescrevem_chave_morta.
  A descoberta da guarda inclui o checkout aninhado
  .claude/worktrees/agent-a054e5c8dd838fcb5/; encontrou quatro superfícies
  históricas desse checkout, não os pacotes/recibos novos.
  orq/scripts/test_observation_types_guard.py:93 percorre essas superfícies,
  e :112 exige zero resultados. Reprodução read-only devolveu os mesmos
  quatro caminhos. A guarda é byte-idêntica ao HEAD; os quatro arquivos têm
  mtime de 2026-09-29, anterior às R4 atuais.
- Nenhuma exclusão, mudança de escopo da guarda, alteração ou remoção do
  checkout aninhado. A correção dessa varredura exige escopo próprio; não
  substituímos a falha por verde nem apagamos evidência para a suíte passar.
- Hashes dos dois pacotes e dos dezoito arquivos fonte intactos; pareceres
  persistidos byte-exatos e JSON válido; autorizações/contadores consumidos
  1/1 cada; uma chamada do processo por pacote e modelo 5.5 exato.
- HEAD main/frente 4e58e7f…; branch Claude T-089 2a879d9…; índices vazios,
  três arquivos protegidos e demais linhas do board byte-preservados.
  Zero Git writes, release, instalação ou restart.

As afirmações anteriores sobre não repetir gates históricos descrevem o momento
do envio; estes são **gates locais novos**, posteriores às duas revisões.
Não são release, prova comportamental pós-restart nem aprovação do gabarito.
