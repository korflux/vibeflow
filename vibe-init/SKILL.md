---
name: vibe-init
description: >
  Inicializa ou repara as regras de um projeto de software em AGENTS.md na raiz, sem criar CLAUDE.md nem REGRAS.md. Use when the user runs /vibe-init, pede governança para agentes, unificar regras, preparar um repositório VibeFlow ou encontra uma instalação antiga com REGRAS.md ou CLAUDE.md, mesmo sem citar vibe-init.
---

# vibe-init

`AGENTS.md` na raiz é a única fonte editável de regras. Preserve toda fonte existente em backup verificado antes de substituí-la. Não crie `CLAUDE.md`, `REGRAS.md` ou cópias das regras em outros paths. A execução do init também migra instalações antigas.

## 0. Entender e usar o motor

Leia `scripts/init.py` no Unix ou `scripts/init.ps1` no Windows antes de executar. O motor aceita `--root`/`-Root`, cria `.vibeflow/phases/`, prepara `AGENTS.md` com `templates/AGENTS.md`, atualiza a ponte `.agents/rules/vibeflow.md` para `@../../AGENTS.md` e emite `.vibeflow/init-report.json`. Um `AGENTS.md` existente mantém suas regras; o motor atualiza só a regra de escopo e o bloco `VIBEFLOW:CADEIA`. Fontes legadas recebem backup verificado em `.vibeflow/old/`; o motor remove automaticamente apenas as que forem idênticas ao conteúdo materializado em `AGENTS.md` antes da atualização do cabeçalho.

Execute na raiz do projeto:

```text
Windows: pwsh "<skill>/scripts/init.ps1"
Unix:    bash "<skill>/scripts/init.sh"
```

Se faltar runtime, tente o outro motor. Se ambos falharem por limitação de ambiente, reproduza as mesmas validações e backups manualmente. Erro de proteção de path, link externo ou hash nunca é contornado.

## 1. Investigar e consolidar

Confira `agent_profiles` no relatório: os cinco papéis são distribuídos em `.codex/agents/*.toml` e `.claude/agents/*.md`. O motor pré-valida fontes de até 1 MiB e todos os destinos antes de mutações, recusa links/reparse points e tipos não regulares, instala ausentes e preserva bytes dos idênticos ou conflitantes. Relate conflitos por host, papel e path; não substitua personalizações sem decisão humana. Não altere configurações globais, permissões gerais nem modelos pessoais.

Distinga disco de sessão: `agent_session.status: nao_verificada` não certifica carregamento. Perfis de projeto podem prevalecer sobre perfis pessoais. Antes da primeira delegação, confira explorador, implementador, verificador, corretor e revisor nas ferramentas disponíveis do host. Se faltarem, oriente recarregar/reabrir o host e conferir novamente; relate host indisponível sem afirmar ativação. Não substitua um modelo indisponível silenciosamente.

Leia o relatório, o `AGENTS.md` e apenas as fontes listadas em `merges`. Use `rg --files` e `rg -n` para localizar manifestos, comandos, entradas e dependências relevantes; não leia a árvore inteira. Preserve diferenças materiais dos legados no `AGENTS.md`. Depois de confirmar que o conteúdo foi incorporado e está salvo em `old/`, remova os arquivos legados restantes apenas quando forem do antigo VibeFlow; outros arquivos do usuário permanecem até a decisão humana sobre sua função.

Preencha os SLOTs do template somente com evidência do projeto. Em arquivos de referência, aproveite a forma, não os fatos: comandos reais de setup/teste, mapa curto da estrutura, fluxos de ponta a ponta, invariantes, validações e caminhos de alteração frequentes. Não copie stack, paths, nomes de funções ou regras do projeto de origem. O bloco de proibição a documentos fica no topo de `AGENTS.md`, antes da cadeia.

## 2. Fechar

Confira que `AGENTS.md` é arquivo regular na raiz, o bloco da cadeia está atualizado, a ponte Antigravity aponta para ele, e nenhuma regra legada se perdeu. Confira os dez perfis e seus estados no relatório. Não crie `CLAUDE.md`, `.vibeflow/REGRAS.md` nem `GEMINI.md`. Faça staging explícito dos paths produzidos e backups necessários, incluindo somente perfis com status `instalado`; exclua perfis conflitantes, trabalho alheio e relatório transitório. Confira o diff e crie commit local sem push. Informe o hash, paths, conflitos, fontes legadas que ainda exigem consolidação e disponibilidade efetivamente verificada em cada host. Handoff: `vibe-interview` quando houver ambiguidade de software; para documento avulso, só a entrevista é aplicável e as demais skills VibeFlow não entram.
