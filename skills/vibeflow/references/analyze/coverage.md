# Conferências do analyze (mapa interno)

Abrir só na etapa analyze. O revisor lê `spec.md`, `plan.md`, `AGENTS.md` e o código que os passos citam, com consumidores e testes. Ache a instância concreta, não o padrão genérico. Não copie esta tabela para o chat nem para o `plan.md`.

| Conferência | Sinal de achado | Ajuste no `plan.md` |
|---|---|---|
| Critério sem passo | Critério de aceite da spec fora de todo `Aceite:` | Acrescentar o critério ao passo que o entrega, ou um passo novo |
| Critério sem prova | `Prova:` que não testa o critério listado em `Aceite:`, ou que o observa num nível que não vê o resultado dele, como critério de tela provado só pela API ou só pelo E2E do checkpoint, sem o teste que renderiza a tela no passo (`references/testes.md`, Política de testes) | Trocar pelo teste que prova o critério no nível certo |
| Arquivo esquecido | Arquivo que o resultado do passo exige escrever fora de `Arquivos:` | Acrescentar o path ao passo; acima do teto, dividir o passo |
| Consumidor esquecido | Código que importa ou chama o que o passo muda, sem passo que o ajuste | Acrescentar o path ao passo, ou um passo dependente; acima do teto, dividir o passo |
| Teste quebrado fora do recorte | Teste existente que a mudança faz falhar, inclusive por snapshot, schema ou seletor, e que nenhum passo atualiza | Acrescentar o teste aos `Arquivos:` e à `Prova:` do passo que o quebra |
| Contradição com a spec | Passo que entrega comportamento fora do escopo, do Fora ou de uma decisão da spec | Alinhar o passo à spec; se a spec precisar mudar, parar e perguntar |
| Paralelo inseguro | Passos irmãos com `Arquivos:` sobrepostos ou path incomparável | Separar em números diferentes |
| Ordem quebrada | Passo que usa o resultado de outro posterior a ele | Reordenar |
| Risco no fim | Suposição mais arriscada ou caminho de ponta a ponta do critério central deixado para depois de passos que dependem dele (`references/plan.md`, Fatiar e ordenar) | Antecipar o passo |
| Formato fora do contrato | Linha de passo, `Arquivos:` ou checkpoint fora de `references/disco.md` (Plan) | Reescrever a linha na forma do contrato |
| Prova fora do contrato | Comando que o repo não tem, E2E ou suíte inteira no passo | Trocar pelos testes afetados do passo; em critério de tela, pelo teste que renderiza a tela (`references/testes.md`, Política de testes) |
| Passo acima do teto | Mais entradas de código em `Arquivos:` que o teto de `references/disco.md` (Plan > Arquivos) | Dividir pelo resultado verificável, sem engordar outro passo |
| Fato sem verificação | Fato da spec que só se prova implementando, sem passo de verificação antes dos passos de entrega | Acrescentar o passo de verificação (`references/plan.md`, Fatiar e ordenar) |
| Checkpoint fora da regra | Checkpoint sem motivo da tabela de `references/disco.md` (Plan > Checkpoint) ou cuja condição não vale: `tela` antes do passo que fecha o visual (acabamento incluído), critério de tela listado em checkpoint anterior ao passo que fecha o visual dele, `segundo grupo de risco` sem `# Risco:` ou sem um segundo grupo que toca a superfície de risco, `integração` em phase de até 10 passos, ou `caminho fino` e primeiro grupo de risco fora da posição da tabela; também checkpoint ausente na posição que a tabela pede, acima do máximo de 4 ou em phase de até 5 passos (a contagem, o motivo fora da tabela e a phase pequena o `plan.mjs` já acusa; o motivo ausente ele só avisa) | Acrescentar, mover ou remover a linha de checkpoint, ou registrar o motivo |
| Regressão completa | Seção ausente ou com comando que o repo não tem | Corrigir com os comandos reais |
| Isolamento do E2E | Critério com E2E (tela ou jornada) sem a escolha do isolamento registrada em `## Regressão completa` (`references/plan.md`, Ambiente de teste; opções em `references/verificador.md`, Desenho do E2E) | Registrar a escolha do líder; sem ela, parar e perguntar ao líder |
| `AGENTS.md` | Passo que viola regra mandatória do projeto | Ajustar o passo à regra |

Formato do passo, `Arquivos:` e checkpoint: `references/disco.md` (Plan). Prova do passo e Regressão completa: `references/plan.md`. Regras de teste: `references/testes.md`.
