# Spec: IA como piloto e scripts como auxiliares
# Pasta: phase-5-ia-piloto-scripts-auxiliares
# Status: aprovado

## Objetivo

Atualizar `.vibeflow/REGRAS.md` para tornar explícito que a IA conduz cada run, interpreta o contexto e responde pelas decisões semânticas. Scripts continuam sendo ferramentas determinísticas para tarefas mecânicas e evidências de disco, mas seus resultados não substituem a leitura, a auditoria nem o julgamento da IA. Sucesso significa remover das regras o modelo em que o relatório ou o script dita o fluxo sem eliminar garantias mecânicas úteis.

## Inventário

1. A diff local de `vibe-init/` já desloca inventário, leitura do projeto e consolidação para a IA.
2. `.vibeflow/REGRAS.md` ainda determina “Inventário antes de interpretar”, define o relatório como contrato `script → IA`, limita a leitura aos paths fornecidos pelo script e exige “Script primeiro” em toda skill.
3. As regras ainda atribuem ao script fatos determinísticos legítimos, como `next_n`, sanitização de slug, promoção byte a byte e validação por tamanho e SHA-256.

## Suposições e decisões

1. A IA é o piloto operacional e semântico da run, o script é auxiliar auditável. (processo)
2. Antes de executar ou contornar um script relevante, a IA deve entender seu objetivo, entradas, saídas, mutações e proteções aplicáveis. (confiabilidade)
3. Resultado de script e relatório são evidência operacional, não autoridade semântica nem limite automático para investigar paths relevantes. (processo)
4. Operações determinísticas de disco permanecem preferencialmente nos scripts quando centralizam invariantes e reduzem risco. A IA não inventa fatos que o disco ou o humano não sustentam. (segurança)
5. Falha do script exige diagnóstico da causa. A IA pode corrigir o script durante a run quando o defeito estiver no código e a correção respeitar o contrato; limitação de ambiente pode usar motor alternativo ou execução manual equivalente, preservando as mesmas garantias. (confiabilidade)

## Escopo e comportamento

### 1. Papel da IA, do script e do relatório

- Reescrever a seção `Papéis na run` para colocar a IA como condutora do fluxo, dona da interpretação e responsável por auditar o resultado.
- Definir scripts como implementação auxiliar de operações mecânicas, nunca como piloto da investigação ou da decisão semântica.
- Definir relatórios como evidência estruturada opcional conforme a arquitetura de cada skill, não como verdade suficiente nem como fronteira obrigatória de leitura.
- Permitir leitura dirigida de qualquer path necessário para entender ou verificar a tarefa, sem varredura cega de árvore nem dump de listagem.

### 2. Contrato de scripts e escrita de skills

- Substituir a regra universal “Script primeiro” por uma etapa de entendimento e uso consciente do script.
- Exigir que a skill oriente a IA a localizar e compreender o script relevante antes da mutação, incluindo entradas, saídas, efeitos e invariantes de segurança.
- Manter paridade de motores, flags públicas, mensagens de erro previstas, comentários semânticos, preservação verificada de arquivos e testes de contrato.
- Manter `next_n`, sanitização de slug, promoção de wip e verificações mecânicas no script quando esses mecanismos existirem.

### 3. Diagnóstico e correção durante o uso

- Registrar que falha ou saída incoerente não deve ser obedecida nem contornada cegamente.
- A IA diferencia defeito do script, limitação do ambiente e violação deliberada de contrato.
- Defeito do script dentro do escopo pode ser corrigido e verificado na própria run.
- Execução manual ou por motor alternativo deve reproduzir as proteções relevantes, principalmente preservação, hash, path permitido e ausência de perda de dados.

### Fora

- Reescrever agora todas as sete skills `vibe-*` para o novo formato. Esta entrega fixa primeiro a regra canônica que orientará as migrações seguintes.
- Revisar ou concluir os scripts e o `SKILL.md` modificados localmente em `vibe-init/`. As mudanças pertencem ao usuário e exigem uma entrega própria de implementação e testes.
- Remover relatórios operacionais de skills que ainda dependem deles. Cada contrato deve ser migrado conscientemente, sem quebra incidental.

## Checklist de entrega

### Aceite

- [x] A1: `.vibeflow/REGRAS.md` declara sem ambiguidade que a IA pilota a run e o script auxilia operações determinísticas.
- [x] A2: as regras exigem que a IA entenda e audite o script relevante antes de confiar em sua execução ou corrigi-lo.
- [x] A3: relatórios deixam de ser autoridade semântica e deixam de limitar automaticamente os paths que a IA pode ler.
- [x] A4: garantias de path, numeração, promoção verificada, backup, hash e paridade de motores permanecem preservadas.
- [x] A5: as regras autorizam diagnóstico, correção do script e fallback equivalente sem permitir contorno de invariantes de segurança.

### Critérios de sucesso

- [x] C1: não resta em `.vibeflow/REGRAS.md` nenhuma regra universal que obrigue execução cega do script antes de entendê-lo.
- [x] C2: a nova redação separa decisão semântica, evidência operacional e mutação mecânica em responsabilidades verificáveis.
- [x] C3: a diff da entrega toca somente `.vibeflow/REGRAS.md` e os artefatos vivos desta fase.

## Implementação

### Estrutura tocada

```text
.vibeflow/REGRAS.md                                      # contrato canônico atualizado
.vibeflow/phases/phase-5-ia-piloto-scripts-auxiliares/  # spec, plan, implement e review da mudança
```

### Estilo e padrões

- Reutilizar a estrutura e o vocabulário atuais das seções `Papéis na run`, `Scripts`, `Escrita da skill` e `Tom`.
- Alterar o menor número possível de trechos, removendo contradições em vez de criar uma política paralela.

### Contratos e módulos

- limites: a IA conduz sem inventar fatos; o script automatiza sem decidir semântica; o humano decide apenas o que muda materialmente o resultado.
- contrato público preservado: paths de artefato, schema existente durante a migração, flags públicas e mecanismos de segurança não mudam nesta entrega.

## Como provar

### Seams

- Conferir a coerência entre as seções de disco, papéis, scripts, escrita de skill, tom e testes de contrato.
- Comparar a redação nova com a intenção observável na diff local de `vibe-init/` sem incorporar regressões específicas daquela implementação.

### Estratégia

- Inspeção de diff: confirmar que somente as regras e os artefatos da fase foram adicionados nesta entrega.
- Busca textual: localizar termos antigos como `Script primeiro`, `contrato script → IA` e restrição universal de paths.
- Revisão semântica: confirmar preservação explícita das garantias determinísticas e de segurança.

### Comandos

```bash
git diff -- .vibeflow/REGRAS.md .vibeflow/phases/phase-5-ia-piloto-scripts-auxiliares
rg -n "Script primeiro|contrato script|Inventário antes|piloto|auxiliar|auditar" .vibeflow/REGRAS.md
```

## Boundaries

### Always

- Preservar integralmente as mudanças locais existentes em `vibe-init/`.
- Basear a redação no comportamento pretendido pelo usuário e nas garantias já consolidadas do repositório.

### Ask first

- Remover uma garantia mecânica existente ou mudar um contrato público de script.

### Never

- Tratar script ou relatório como substituto do entendimento da IA.
- Permitir fallback manual que reduza proteção contra perda de dados.
- Disparar a próxima skill sem confirmação humana.

## Handoff

vibe-plan

- [x] Aprovação humana (leu o arquivo e confirmou)
