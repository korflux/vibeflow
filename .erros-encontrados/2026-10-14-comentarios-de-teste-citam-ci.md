# Comentários de teste citam o CI do GitHub removido

- Data: 2026-10-14.
- Local: docs/vibe-implement/tests/test-implement.py:1476 ("usada pelo CI") e docs/vibe-implement/tests/piloto-modo-a.py:19 ("Não entra no CI.").
- Problema: os dois comentários citam o CI do GitHub, removido na phase 20 por decisão do humano (custo). A referência ficou obsoleta.
- Impacto: apenas comentários, sem efeito em lógica ou asserts. Sugerem a quem lê uma execução em CI que não existe mais.
- Sugestão de correção: trocar a menção por "regressão completa local" numa T* que tenha esses arquivos no recorte de `Arquivos:`.
- Relação: encontrado na validação da phase 20, fora dos `Arquivos:` das T* dessa phase.
