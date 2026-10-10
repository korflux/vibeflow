# Symlinks de skills não materializados no checkout Windows

- Data: 2026-09-23.
- Onde: `skills/vibe-*` no checkout `C:\projetos\vibeflow`.
- Problema: o Git materializou os symlinks versionados como arquivos de texto contendo `../vibe-*`. Os dois testes de distribuição que verificam os ponteiros e a descoberta das skills falham. As demais verificações de distribuição passaram.
- Correção futura: refazer ou reparar o checkout com suporte a symlinks no Windows e repetir `python docs/tests/test-distribuicao.py -v`.

## Auditoria atual

Auditoria em 2026-10-10: o checkout citado C:/projetos/vibeflow não existe neste host. O checkout atual A:/Projetos/vibeflow possui os oito symlinks reais e core.symlinks=true; distribuição tem 9 testes verdes. Não há reparo aplicável aqui, nem certificação retroativa do checkout ausente.
