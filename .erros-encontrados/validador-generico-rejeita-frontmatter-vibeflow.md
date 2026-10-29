# Validador genérico rejeita campo obrigatório do VibeFlow

Data: 2026-10-29.

Local: `C:/Users/marco/.codex/skills/.system/skill-creator/scripts/quick_validate.py`, ao validar `skills/vibeflow/SKILL.md`.

Descrição: o validador retorna código 1 porque sua lista de campos permitidos não inclui `disable-model-invocation`. O contrato do VibeFlow exige esse campo no frontmatter para impedir invocação implícita no Claude Code.

Impacto: a validação genérica não certifica o pacote, mesmo sem alteração no frontmatter. A configuração dos perfis TOML pode ser validada separadamente.

Sugestão: ajustar o validador externo para reconhecer o campo antes de usá-lo como critério de aprovação deste pacote. Preservar o campo obrigatório no VibeFlow.

Relação com a tarefa: incompatibilidade preexistente encontrada na verificação da troca de modelos e esforços dos perfis Codex; nenhum ajuste no validador ou no frontmatter faz parte do pedido.
