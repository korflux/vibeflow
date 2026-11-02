# Conferências do analyze (mapa interno)

Abrir só na etapa analyze. Ache a instância concreta, não o padrão genérico. Não copie esta tabela para o chat nem para o `plan.md`.

| Conferência | Sinal de achado | Ajuste no `plan.md` |
|---|---|---|
| Critério sem passo | Critério de aceite da spec fora de todo `Aceite:` | Acrescentar o critério ao passo que o entrega, ou um passo novo |
| Critério sem prova | `Prova:` que não exercita o critério listado em `Aceite:` | Trocar pelo teste que prova o critério |
| Arquivo esquecido | Arquivo que o resultado do passo exige escrever fora de `Arquivos:` | Acrescentar o path ao passo; acima do teto, dividir o passo |
| Consumidor esquecido | Código que importa ou chama o que o passo muda, sem passo que o ajuste | Acrescentar o path ao passo, ou um passo dependente; acima do teto, dividir o passo |
| Teste quebrado fora do recorte | Teste existente que a mudança faz falhar, inclusive por snapshot, schema ou seletor, e que nenhum passo atualiza | Acrescentar o teste aos `Arquivos:` e à `Prova:` do passo que o quebra |
| Contradição com a spec | Passo que entrega comportamento fora do escopo, do Fora ou de uma decisão da spec | Alinhar o passo à spec; se a spec precisar mudar, parar e perguntar |
| Paralelo inseguro | Passos irmãos com `Arquivos:` sobrepostos ou path incomparável | Separar em números diferentes |
| Ordem quebrada | Passo que usa o resultado de outro posterior a ele | Reordenar |
| Risco no fim | Suposição mais arriscada ou caminho de ponta a ponta do critério central deixado para depois de passos que dependem dele (`references/plan.md`, Fatiar e ordenar) | Antecipar o passo |
| Prova fora do contrato | Comando que o repo não tem, E2E ou suíte inteira no passo | Trocar pelos testes afetados do passo |
| Passo acima do teto | Mais entradas de código em `Arquivos:` que o teto de `references/disco.md` (Plan > Arquivos) | Dividir pelo resultado verificável, sem engordar outro passo |
| Fato sem verificação | Fato da spec que só se prova implementando, sem passo de verificação antes dos passos de entrega | Acrescentar o passo de verificação (`references/plan.md`, Fatiar e ordenar) |
| Checkpoint fora da regra | Checkpoint ausente numa posição de `references/disco.md` (Plan > Checkpoint), em outra posição, acima do máximo ou em phase sem checkpoint | Acrescentar, mover ou remover a linha de checkpoint |
| Regressão completa | Seção ausente ou com comando que o repo não tem | Corrigir com os comandos reais |
| Isolamento do E2E | Critério de tela sem a escolha do isolamento registrada em `## Regressão completa` (`references/plan.md`, Ambiente de teste; opções em `references/verificador.md`, Desenho do E2E) | Registrar a escolha do líder; sem ela, parar e perguntar ao líder |
| `AGENTS.md` | Passo que viola regra mandatória do projeto | Ajustar o passo à regra |

Formato do passo, `Arquivos:` e checkpoint: `references/disco.md` (Plan). Prova do passo e Regressão completa: `references/plan.md`. Regras de teste: `references/testes.md`.
