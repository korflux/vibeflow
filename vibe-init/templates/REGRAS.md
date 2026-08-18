# Regras do projeto

<!-- VIBEFLOW:CADEIA start -->
| esforço | fluxo | quando |
|---|---|---|
| — | init | primeira vez no repo, ou disco quebrado — de novo só para reparar |
| low | implement | pedido claro, direto, simples (cor, texto…) |
| medium | implement → review | pedido claro e direto, sem possibilidade de regressão |
| high | spec → plan → implement → review | pedido claro, execução difícil, ou possibilidade de regressão |
| xhigh | interview → spec → plan → implement → review | pedido ambíguo, confiança baixa, intenção ou sucesso em aberto |
| max | interview → spec → plan → analyze → implement → review | pedido toca auth, pagamento, segredo, perda de dados, produção ou alto blast radius |
<!-- VIBEFLOW:CADEIA end -->

## Projeto
<!-- SLOT:paragrafo -->
<!-- evidência: <path ou vazio> -->

## Ambiente
<!-- SLOT:ambiente -->
<!-- homolog | producao -->

## Versão (semver)
- **Major:** quebra contrato (API, schema, comportamento que caller já usa).
- **Minor:** adiciona sem quebrar.
- **Patch:** correção sem mudança de contrato.
- Produção: migration só com plano de rollback; não rodar migration destrutiva sem o humano pedir.

## Git
- Sem `Co-Authored-By` de ferramenta em commit/push.

## Estrutura
<!-- SLOT:estrutura -->

## Regras deste repo
<!-- SLOT:regras -->
