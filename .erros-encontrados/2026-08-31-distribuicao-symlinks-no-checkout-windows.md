# Distribuição não reconhece ponteiros no checkout Windows

- Data: 2026-08-31
- Onde: `docs/tests/test-distribuicao.py`, testes `test_skills_pointers` e `test_unique_names_under_skills`
- Problema: o repositório mantém `skills/vibe-*` como symlinks relativos no Git, mas este checkout está configurado com `core.symlinks=false` e materializa os sete ponteiros como arquivos regulares. A suíte falha antes de qualquer mudança desta phase.
- Evidência inicial: `python docs/tests/test-distribuicao.py -v` retornou 5 testes passando e 2 falhando; uma fixture isolada com symlinks reais retornou 7 testes passando.
- Correção: os sete arquivos-texto foram substituídos por symlinks relativos reais, após validação do conteúdo original e com backup temporário. A configuração local do Git foi ajustada para `core.symlinks=true`.
- Evidência atual: `python docs/tests/test-distribuicao.py -v` retornou 7 testes passando e 0 falhando no checkout principal.
- Estado: corrigido em 2026-08-31.
