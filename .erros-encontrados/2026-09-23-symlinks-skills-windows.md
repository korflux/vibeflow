# Symlinks de skills não materializados no checkout Windows

- Data: 2026-09-23.
- Onde: `skills/vibe-*` no checkout `C:\projetos\vibeflow`.
- Problema: o Git materializou os symlinks versionados como arquivos de texto contendo `../vibe-*`. Os dois testes de distribuição que verificam os ponteiros e a descoberta das skills falham. As demais verificações de distribuição passaram.
- Correção futura: refazer ou reparar o checkout com suporte a symlinks no Windows e repetir `python docs/tests/test-distribuicao.py -v`.

## Auditoria atual

Auditoria em 2026-10-10: o checkout citado C:/projetos/vibeflow não existe neste host. O checkout atual A:/Projetos/vibeflow possui os oito symlinks reais e core.symlinks=true; distribuição tem 9 testes verdes. Não há reparo aplicável aqui, nem certificação retroativa do checkout ausente.

## Auditoria 2026-10-13

Novo clone em C:/Projetos/vibeflow (phase 19) voltou a materializar `skills/vibe-*` como texto: `core.symlinks=false`. `test_skills_pointers` e `test_unique_names_under_skills` falham localmente pela mesma causa; o CI Linux cobre. Reparo exige habilitar symlinks no Windows (Modo de Desenvolvedor ou privilégio) e refazer o checkout, decisão do humano. Sem relação com o conteúdo da phase 19.
