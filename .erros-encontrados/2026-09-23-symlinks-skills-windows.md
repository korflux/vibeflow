# Symlinks de skills não materializados no checkout Windows

- Data: 2026-09-23.
- Onde: `skills/vibe-*` no checkout `C:\projetos\vibeflow`.
- Problema: o Git materializou os symlinks versionados como arquivos de texto contendo `../vibe-*`. Os dois testes de distribuição que verificam os ponteiros e a descoberta das skills falham. As demais verificações de distribuição passaram.
- Correção futura: refazer ou reparar o checkout com suporte a symlinks no Windows e repetir `python docs/tests/test-distribuicao.py -v`.
