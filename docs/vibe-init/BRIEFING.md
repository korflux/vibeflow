# Ao usar /vibe-init
1. Script cria a pasta .vibeflow
2. Dentro da pasta .vibeflow cria REGRAS.md
3. Na raiz do projeto, cria AGENTS.md e CLAUDE.md
4. Define symlink do REGRAS.md com AGENTS.md e CLAUDE.md para todos ficarem iguais o REGRAS.md
5. A IA preenche o REGRAS.md com:
- Um parágrafo curto que descreva o projeto (confirmar com usuário)
- Se está em homologação ou produção (confirmar com usuário)
- SE produção, deixar claro que deve tomar cuidado com migrations
- Regras de Major, Minor e Patch
- Regras do projeto (exemplo, é dashboard de dados, precisa ter cuidado para usar o devido padrão de número, para não term problema) (não usar co-author... etc...)
- Estrutura de pastas do projeto
- Questiona o usuário se falta alguma informação