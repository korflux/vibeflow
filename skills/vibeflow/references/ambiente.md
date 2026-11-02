# Ambiente local

Leia quando o teste depende de banco ou serviço, ou quando o init ou o plan procuram Docker nos testes.

- Testes locais preferem serviços nativos (instalação oficial do sistema) ou embutidos no processo de teste (binário como dependência de desenvolvimento, como `embedded-postgres`) a containers. Docker fica para o CI.
- Banco limpo vem de banco por arquivo, por worker ou por template, de reset de schema ou de transação com rollback, nunca de recriar container.
- Sinais de Docker nos testes: comando de teste que chama `docker`, `docker compose` no setup de teste, arquivo de compose do projeto (`docker-compose.yml`, `compose.yaml` e variantes) ou documentação que o prefere.
- Com Docker nos testes e sem decisão registrada na seção Ambiente do `AGENTS.md` do projeto, o líder pergunta ao humano uma vez, com recomendação, se prefere migrar para uma forma mais leve, e a resposta e a data são gravadas em Ambiente. Com a decisão registrada, não pergunte de novo.
- A pergunta acontece no init (`references/init.md`, passo 2), com o registro no commit de governança, e no plan, onde vira o primeiro passo (`references/plan.md`, passo 2).
