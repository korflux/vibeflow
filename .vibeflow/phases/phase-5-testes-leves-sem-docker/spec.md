# Spec: testes locais leves, E2E paralelo e orçamento de duração
# Alvo: phase-5-testes-leves-sem-docker
# Status: aprovado
# Rota: high

## Objetivo

O líder e os analistas da skill passam a orientar, nos projetos consumidores, testes locais leves e rápidos: serviços nativos ou embutidos em vez de Docker, E2E desenhado para rodar em paralelo e sem trabalho repetido, e vigilância da duração da suíte. Sucesso é um projeto que siga a skill ter E2E restrito às jornadas com tela, sem cadeia serial de estado global, e a lentidão da regressão aparecer como registro antes de virar problema.

## Pontos do projeto

- `skills/vibeflow/references/implement.md`, seção Política de testes: é hoje a casa única de quando e o que testar, sem tratar de ambiente nem de desenho do E2E; a política sai daqui para a referência nova.
- `skills/vibeflow/references/plan.md` (Prova do passo, Regressão completa), `references/review.md` (passo 1, com regressão única em segundo plano e sem registro de duração), `references/delegation.md` (Níveis de prova) e os perfis em `templates/agents/`: citam provas e E2E e passam a apontar para a referência nova sem repetir a regra.
- `skills/vibeflow/templates/AGENTS.md`, SLOTs `comandos` e `ambiente`, e `references/init.md`, que preenche esses SLOTs com evidência: não há campo de orçamento de duração nem de decisão sobre Docker.
- `skills/vibeflow/references/chrome-devtools.md`: Playwright só quando o repo já o tem; a regra continua valendo.
- Evidência no aion: o Postgres de teste é embutido (`embedded-postgres`), sem Docker, e os testes unitários usam um banco por arquivo. O E2E, porém, faz build de produção a cada execução, usa banco único que põe 175 dos 211 testes (83%) em projetos seriais encadeados, faz login pela interface em quase todo teste (90 linhas) e tem 15 esperas fixas (`waitForTimeout`), com cerca de 25 minutos por execução.
- Evidência no kastir: o `AGENTS.md` do projeto prefere `docker compose up -d` e há `test:docker-build`. No atendimento, os testes só leem o texto de `Dockerfile` e `docker-compose.yml`.

## Decisões

1. Docker nos testes locais é preferência, sem bloqueio: a skill recomenda serviços nativos ou embutidos e Docker só no CI; quando o projeto já usa Docker nos testes, o líder pergunta ao humano uma vez, com recomendação, se prefere migrar para uma forma mais leve, e registra a resposta no `AGENTS.md` do projeto para não perguntar de novo. Pergunta: quão rígida a skill deve ser sobre Docker nos testes locais? Motivo: decisão do humano; o projeto mantém a escolha e a pergunta não se repete.
2. Duração com orçamento e alarme: o `AGENTS.md` do projeto declara o orçamento da regressão completa, com padrão de 10 minutos sem declaração; a review registra a duração medida por nível (lint e tipos, unitários, E2E); acima do orçamento, o revisor grava em `.erros-encontrados/` o tempo, o nível mais lento e a causa provável, sem bloquear. Pergunta: a skill deve vigiar a duração dos testes? Motivo: decisão do humano; a lentidão fica visível cedo sem travar a entrega.
3. As regras de teste ganham casa única em `skills/vibeflow/references/testes.md`, com a política que sai do `implement.md`, o ambiente local, o desenho do E2E e o orçamento; as demais referências e perfis apontam para ela. Pergunta: onde moram as regras de teste? Motivo: assumida; uma casa por fato.
4. Para isolar o E2E, a referência oferece duas saídas e o plan de cada projeto escolhe: isolamento por worker (banco por worker, ou a pilha inteira por worker quando o app tem estado global) ou descer a regra para teste de integração sem navegador. Pergunta: como o E2E deixa de depender de estado global serial? Motivo: assumida; o custo de cada saída depende do app.
5. A mudança é minor, versão 5.1.0. Pergunta: qual versão a mudança recebe? Motivo: assumida; acrescenta referência e campos sem quebrar contrato.

## Critérios de aceite

- A1: `references/testes.md` é a casa única da política de testes; `implement.md`, `plan.md`, `review.md`, `delegation.md` e os perfis apontam para ela sem repetir a regra.
- A2: a referência define o ambiente local: serviços nativos ou embutidos preferidos, Docker só no CI, e a pergunta única ao humano quando o projeto já usa Docker nos testes, com a decisão registrada no `AGENTS.md` do projeto.
- A3: a referência define o desenho do E2E: só jornadas de critério com tela; isolamento por worker ou regra descida para integração; nenhuma cadeia de estado global entre arquivos; autenticação reaproveitada por worker; nenhuma espera fixa; build feito uma vez e reaproveitado enquanto os inputs não mudam, com build de produção só na regressão completa.
- A4: a referência define que regra de negócio se prova em teste de integração sem navegador, e o E2E só confirma a jornada.
- A5: `templates/AGENTS.md` tem lugar para o orçamento da regressão e para a decisão sobre Docker; a review registra a duração por nível e, acima do orçamento (padrão de 10 minutos), o revisor grava o registro em `.erros-encontrados/` sem bloquear.
- A6: o init preenche o orçamento e detecta Docker nos comandos de teste ou no compose do projeto, levando a pergunta da decisão 1 ao humano.
- A7: o `AGENTS.md` deste repo e o `README.md` registram a versão 5.1.0 e o que mudou.

## Fora do escopo

- Corrigir o E2E do aion e migrar o kastir para serviços nativos: cada um é phase própria no respectivo projeto.
- Configuração de CI e novas ferramentas de teste: a skill usa o que o projeto já tem.
- Script que mede duração: a medição vem da saída dos comandos na review.

- [x] Aprovação humana (leu o arquivo e confirmou), 24/10/2026: "Aprovado a spec da phase-5. Pode seguir."
