---
name: vibe-init
description: >
  Inicializa ou repara a governança e o Documento Vivo de regras (.vibeflow/REGRAS.md)
  com AGENTS.md e CLAUDE.md como ponteiros. Use when the user runs /vibe-init,
  pede para preparar o repo para agentes, unificar regras, consertar symlinks ou
  quando o projeto não possui .vibeflow/REGRAS.md.
---

# vibe-init

Inicializa a infraestrutura de governança do Vibeflow e cria a fonte única e viva da verdade de arquitetura e regras (`.vibeflow/REGRAS.md`).

A investigação começa pela pergunta do bootstrap e pelas evidências do disco. Use `rg --files` para localizar README, manifestos, regras, ponteiros e entradas; use `rg -n` para localizar símbolos, comandos e referências. Abra somente os paths que sustentam a decisão e expanda a leitura quando uma lacuna bloquear a prova. O inventário é mapa de seleção, não autorização para ler a árvore inteira.

---

## 1. O que o Utilitário de Setup Faz

O script (`scripts/init.ps1`, `scripts/init.py`, `scripts/init.sh`) foi desenhado para automatizar tarefas mecânicas de sistema operacional:
1. **Estrutura de Diretórios:** Cria `.vibeflow/` e `.vibeflow/phases/` com um arquivo `.gitkeep` vazio.
2. **Preservação de Legado:** Se encontrar arquivos `AGENTS.md` ou `CLAUDE.md` com conteúdo prévio na raiz (que não sejam links para `.vibeflow/REGRAS.md`), ele não apaga: copia com segurança para `.vibeflow/old/AGENTS.md` e `.vibeflow/old/CLAUDE.md`.
3. **Template Base:** Se `.vibeflow/REGRAS.md` não existir, copia o modelo inicial de `templates/REGRAS.md`.
4. **Ponteiros Unificados:** Cria symlinks relativos `AGENTS.md` e `CLAUDE.md` apontando para `.vibeflow/REGRAS.md`. Caso o sistema operacional recuse a criação de links simbólicos (ex: Windows sem Developer Mode ativo), o script cria arquivos ponteiro de texto contendo `.vibeflow/REGRAS.md` como fallback seguro.

---

## 2. Execução e Resiliência de Ambiente

### Como executar:
Execute o script correspondente ao sistema operacional no repositório:
* **Windows:** `pwsh "<skill>/scripts/init.ps1"` (ou `python "<skill>/scripts/init.py"`)
* **Unix/macOS:** `bash "<skill>/scripts/init.sh"` (ou `python3 "<skill>/scripts/init.py"`)

### Dever de Diagnóstico e Autocorreção:
Se o script falhar por limitações da máquina do usuário (ex: versão incompatível de shell, restrição de política de execução `ExecutionPolicy`, ausência de runtime ou bloqueio de permissão de arquivo):
* **Não trave nem transfira o trabalho mecânico para o usuário.**
* Analise o erro retornado no terminal, tente ajustar o comando (ex: usar `python` em vez de `pwsh` ou vice-versa).
* Se a execução via terminal continuar bloqueada, **execute a infraestrutura manualmente** através das suas ferramentas de escrita e manipulação de arquivos: crie as pastas `.vibeflow/` e `.vibeflow/phases/`, faça os backups necessários em `.vibeflow/old/` e crie o `.vibeflow/REGRAS.md` e os arquivos ponteiro na raiz.

---

## 3. Auditoria Factual e Leitura de Contexto

Audite o disco antes de consolidar as regras. Comece pela pergunta que motivou o bootstrap, por exemplo ausência, conflito ou ponteiro inválido, e formule as evidências necessárias para respondê-la.

1. **Localizar as entradas:**
   * Use `rg --files -g 'README*' -g 'package.json' -g 'Cargo.toml' -g 'pyproject.toml' -g 'go.mod' -g 'pom.xml' -g 'AGENTS.md' -g 'CLAUDE.md' -g 'REGRAS.md'` para encontrar candidatos.
   * Use `rg -n 'entrada|rota|stack|migra|AGENTS|CLAUDE|REGRAS'` somente nos paths relevantes para localizar referências e símbolos.
   * Abra o `README.md`, os manifestos encontrados, os ponteiros e os entrypoints necessários, não todos os arquivos listados.

2. **Auditoria de Disco:**
   * Verifique se `.vibeflow/REGRAS.md` existe e está acessível.
   * Inspecione `.vibeflow/old/` somente para confirmar regras legadas que precisam ser resgatadas e mescladas.
   * Confirme se `AGENTS.md` e `CLAUDE.md` estão presentes na raiz como links ou ponteiros válidos.

3. **Mapeamento Semântico de Arquitetura:**
   * Leia apenas as pastas e arquivos necessários para explicar o fluxo real do projeto.
   * Mapeie o papel arquitetural de cada pasta relevante, como rotas, regras de negócio, componentes visuais e configs.
   * Destaque somente arquivos-chave ou pontos de entrada essenciais.
   * O inventário não é uma ordem para ler a árvore inteira. Não faça dump cego de listagem de arquivos; registre o mapa de responsabilidades.

---

## 4. Alinhamento Objetivo com o Usuário

Faça apenas perguntas pontuais para fechar definições que o disco não respondeu por completo:
* **Ambiente Principal:**
  * **MVP:** Foco em velocidade e validação do núcleo essencial sem complexidade prematura, mantendo integridade básica.
  * **Homologação:** Ambiente intermediário com testes de integração e validações completas.
  * **Produção:** Rigor máximo, plano de rollback em migrations, zero tolerância a regressões e segurança estrita.
* **Regras Específicas:** Pergunte se há restrições, decisões técnicas ou regras de negócio que não estejam explícitas nos arquivos de código.

---

## 5. Consolidação no Documento Vivo (`.vibeflow/REGRAS.md`)

Edite e preencha diretamente o arquivo `.vibeflow/REGRAS.md`:
* Propósito do sistema e stack técnica identificada.
* Perfil do ambiente selecionado (`MVP`, `Homologação` ou `Produção`).
* Tabela de cadeia do Vibeflow preservada.
* Mapa semântico de arquitetura das pastas.
* Regras e convenções específicas consolidadas.

### Princípio da Manutenção Contínua:
O `.vibeflow/REGRAS.md` é um **Documento Vivo**. Sempre que novas fases adicionarem novos módulos, serviços ou convenções de código, a IA e o desenvolvedor devem atualizar este arquivo para que o repositório nunca fique com governança defasada.

---

## 6. Fechar

Não commite no git. A fonte viva e o caminho do handoff são a ponte para a etapa seguinte. `init → interview` pode continuar no mesmo chat; abrir outro chat é opcional quando o humano quiser separar o bootstrap da definição do pedido.

Handoff: `vibe-interview`.
