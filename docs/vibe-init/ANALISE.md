## Visão geral

A vibe-init transforma as regras de agentes do repositório em uma fonte única:

```
.vibeflow/REGRAS.md       fonte real, editável
AGENTS.md                 symlink → .vibeflow/REGRAS.md
CLAUDE.md                 symlink → .vibeflow/REGRAS.md
```

A responsabilidade é dividida assim:

```
Skill decide o procedimento
    ↓
Script inventaria e prepara o disco
    ↓
IA lê o relatório e resolve conteúdo semântico
    ↓
Usuário responde dúvidas reais
    ↓
IA finaliza REGRAS.md
    ↓
Script converte os ponteiros restantes em symlinks
```

A implementação possui dois motores e um launcher Unix. A suíte principal é a Python, com 28 contratos, porque o
launcher Unix prefere Python 3. A suíte PowerShell cobre os mesmos cenários no motor gêmeo. O teste de paridade
entre os dois só roda quando existe PowerShell 7 de verdade: um `pwsh` que responde 5.1 é pulado, não aceito.

Os dois motores exigem PowerShell 7 e declaram isso com `#Requires`. Os arquivos `.ps1` são gravados com BOM
porque, sem ele, o PowerShell 5.1 lê o arquivo como ANSI e morre em erro de parser nos acentos, antes de chegar
ao `#Requires`. Com BOM, o humano vê a dependência que falta em vez de um muro de tokens inválidos.

## Papel de cada arquivo

- vibe-init/SKILL.md: orquestra todo o processo. Define quando executar o script, como
  interpretar o relatório, como fazer merge e quais perguntas fazer.

- vibe-init/scripts/init.ps1: implementação PowerShell do inventário, backups, reparos, scan,
  symlinks, protocolo de merge e relatório.

- vibe-init/scripts/init.py: implementação portátil em Python 3 com o mesmo contrato.

- vibe-init/scripts/init.sh: launcher Unix. Prefere Python 3 e usa PowerShell 7 como fallback.

- vibe-init/templates/REGRAS.md: template inicial da fonte viva de regras.
- docs/vibe-init/tests/test-init.ps1 e test-init.py: suítes de contrato externas ao pacote
  instalável. Não rodam durante a ativação normal da skill.

## Fluxo completo ao ativar a skill

### 1. A skill é selecionada

O description da skill declara os gatilhos. Ela deve ser ativada quando o usuário:

- Executa /vibe-init.
- Pede para preparar um repositório para agentes.
- Pede para unificar AGENTS.md, CLAUDE.md e REGRAS.md.
- Pede para criar ou reparar .vibeflow.
- Tem symlink quebrado.
- Está num checkout Windows em que o symlink virou um arquivo contendo somente .vibeflow/REGRAS.md.
- Ainda não possui regras de agentes.

Isso é importante na primeira execução: o roteador VIBEFLOW:CADEIA ainda não existe no repositório. Portanto, a
própria descrição da skill precisa disparar o init.

### 2. A IA localiza o diretório da skill

A IA resolve a pasta onde está o SKILL.md. Isso permite chamar os scripts e o template por caminhos absolutos,
independentemente do repositório atual.

### 3. A IA executa o script antes de interpretar o projeto

No diretório raiz do repositório do usuário:

pwsh "<skill>/scripts/init.ps1"

No Unix:

bash "<skill>/scripts/init.sh"

O init.sh seleciona, nesta ordem:

```
python3 scripts/init.py
python scripts/init.py, somente se for Python 3
pwsh -File scripts/init.ps1
```

Portanto, PowerShell 7 deixou de ser obrigatório no Unix. É necessário Python 3 ou PowerShell 7; não existe fallback
degradado com uma matriz parcial.

## O que o init.ps1 faz

### 4. Resolve o repositório e os caminhos

O script determina a raiz nesta ordem:

1. Usa -Root, se informado.
2. Tenta git rev-parse --show-toplevel.
3. Usa o diretório atual.

Depois define:

```
.vibeflow/
.vibeflow/REGRAS.md
.vibeflow/old/
.vibeflow/phases/
REGRAS.md
AGENTS.md
CLAUDE.md
```

### 5. Faz um inventário sem escrever nada

O script classifica o estado inicial de cada peça.

Para .vibeflow:

- ausente
- vazia
- sem_regras
- com_regras

Para as regras:

- ausente
- vazio
- template, ainda contém <!-- SLOT:... -->
- preenchido
- raiz_sozinho
- raiz_e_vibeflow

Para AGENTS.md e CLAUDE.md:

- ausente
- inesperado, por exemplo, é um diretório
- symlink_ok
- symlink_quebrado
- symlink_outro
- vazio
- ponteiro_texto
- arquivo_igual
- arquivo_legado

Esse inventário é preservado no relatório como o estado encontrado antes das alterações.

### 6. Decide entre novo e reparar

O fluxo será novo somente se não existir nenhuma destas peças:

- .vibeflow
- REGRAS.md na raiz
- AGENTS.md
- CLAUDE.md

Se qualquer uma existir, o fluxo será reparar.

### 7. Cria a infraestrutura mínima

O script cria, quando necessário:

```
.vibeflow/
.vibeflow/phases/
.vibeflow/phases/.gitkeep
.vibeflow/.gitignore
```

O .gitignore interno contém:

init-report.json
init-pending.json

Assim, o relatório operacional não deve entrar no Git.

### 8. Calcula se existe merge pendente

Antes de substituir arquivos, o script determina se há conteúdo legado que precisa ser interpretado pela IA.

A regra é uma só: toda fonte de texto que perde o papel de arquivo editável precisa aparecer em `merges[]`. O
critério não é o estado isolado do REGRAS, e sim quantos textos diferentes existem no disco. Enquanto houver
merge pendente, nenhuma fonte vira symlink.

Possíveis merges:

- duas_fontes: AGENTS.md e CLAUDE.md possuem conteúdos diferentes e ainda não existe uma fonte viva consolidada.
- legado_vs_regras: existe conteúdo legado em um ou ambos os ponteiros e também existe, ou passará a existir
  nesta run, um REGRAS.md com texto. O REGRAS que vem da raiz conta como fonte existente.
- regras_duplicado: existe REGRAS.md na raiz e .vibeflow/REGRAS.md, com conteúdos diferentes.

Os dois últimos podem sair juntos na mesma run, cada um com suas fontes. Quando AGENTS.md e CLAUDE.md são byte a
byte idênticos, os dois backups são gravados, mas o texto entra uma vez só como fonte: a IA não precisa ler o
mesmo conteúdo duas vezes para uni-lo a si mesmo.

O script não faz esse merge porque ele não consegue decidir semanticamente se duas regras são complementares ou
contraditórias.

### 9. Grava backups verificados

Toda peça que poderá ser substituída é copiada para .vibeflow/old/.

Exemplos:

```
.vibeflow/old/AGENTS.md
.vibeflow/old/CLAUDE.md
.vibeflow/old/REGRAS.md
.vibeflow/old/REGRAS-raiz.md
```

Se o nome já existir, usa timestamp:

AGENTS.md.20260818-143000

O backup é validado por:

1. Comparação de tamanho.
2. SHA-256 do original e da cópia.

Se a validação falhar:

OLD_HASH_MISMATCH

O script interrompe a operação e preserva o original. Essa é a principal garantia contra perda de regras durante uma
falha intermediária.

### 10. Resolve a localização de REGRAS.md

As principais possibilidades são:

- Se existe apenas REGRAS.md na raiz, faz backup e move para .vibeflow/REGRAS.md.
- Se existem os dois e são idênticos, faz backup e remove a cópia da raiz.
- Se existem os dois e são diferentes, preserva ambos e registra merge pendente.
- Se não existe conteúdo aproveitável, copia o template para .vibeflow/REGRAS.md.

### 11. Cria ou repara os symlinks seguros

O objetivo é:

```
AGENTS.md → .vibeflow/REGRAS.md
CLAUDE.md → .vibeflow/REGRAS.md
```

A criação normal é protegida:

1. Cria primeiro um symlink temporário.
2. Se o sistema recusar, lança SYMLINK_RECUSADO.
3. Somente depois de conseguir criar o temporário, remove o arquivo original.
4. Renomeia o temporário para AGENTS.md ou CLAUDE.md.

Se houver merge pendente e o arquivo legado for uma das fontes, ele permanece no lugar. A conversão só acontece depois
que a IA concluir o merge e chamar -ApplyPointers.

Casos especiais:

- symlink_ok: não faz nada.
- symlink_quebrado: recria.
- ponteiro_texto: guarda backup, avisa que aquilo não é uma regra e recria o symlink.
- arquivo_igual: guarda backup e converte em symlink.
- symlink_outro: não redireciona automaticamente.
- inesperado: não toca.

### 12. Faz um scan factual limitado

O script coleta:

- Nome do projeto a partir de package.json, pyproject.toml, go.mod ou nome da pasta.
- Primeiro parágrafo útil de README.md.
- Caso não exista, tenta description de package.json ou pyproject.toml.
- Estrutura de arquivos até dois níveis.
- Manifests de stack conhecidos.
- Evidências de migrations.

Ignora na listagem estrutural:

node_modules
.git
dist
build
.next
vendor
__pycache__

A detecção de migrations procura padrões como:

```
prisma/migrations
alembic
drizzle
knexfile.js
supabase/migrations
diretórios chamados migrations
```

### 13. Preenche somente SLOTs respaldados por evidência

O template possui:

SLOT:paragrafo
SLOT:ambiente
SLOT:estrutura
SLOT:regras

O script preenche automaticamente:

- estrutura, usando o scan do repositório.
- paragrafo, somente se encontrou evidência no README ou manifest.

Não preenche:

- ambiente, porque homologação versus produção exige informação humana.
- regras, porque regras específicas não podem ser inventadas.

### 14. Atualiza o roteador VIBEFLOW:CADEIA

O bloco delimitado por:

<!-- VIBEFLOW:CADEIA start -->
...
<!-- VIBEFLOW:CADEIA end -->

sempre vem do template atual.

Se o bloco:

- Não existe, é inserido depois do título.
- Existe e está antigo, é substituído.
- Já está atualizado, nada muda.

Somente esse bloco é controlado pela skill. O restante do conteúdo pertence ao usuário e não deve ser sobrescrito.

### 15. Produz .vibeflow/init-report.json

O relatório contém:

```
{
  "flow": "novo ou reparar",
  "root": "raiz do repo",
  "inventory": {},
  "olds": [],
  "actions": [],
  "merges": [],
  "conflicts": [],
  "filled": {},
  "slots_abertos": [],
  "migrations_detectadas": false,
  "symlink_ok": {},
  "scan": {},
  "avisos": [],
  "apply_token": "token quando houver merge ou null"
}
```

O script imprime o caminho desse relatório e termina.

## O que a IA faz depois do script

### 16. Lê apenas as fontes necessárias

A IA deve ler:

1. .vibeflow/init-report.json.
2. .vibeflow/REGRAS.md.
3. Cada arquivo listado em merges[].sources.
4. Arquivos dirigidos por evidência, SLOT ou indicação do usuário.

Ela não deve abrir indiscriminadamente toda a árvore.

Uma fonte contendo somente:

.vibeflow/REGRAS.md

é ignorada no merge. Isso representa um symlink degradado por checkout Windows, não uma regra.

### 17. Apresenta um resumo inicial curto

O contrato pede uma abertura em cinco dimensões:

fluxo · olds gravados · merges · conflitos · slots

Exemplo:

reparar · old: AGENTS.md · merge: legado_vs_regras · conflito: nenhum · slots: ambiente, regras

Mesmo se o repositório estiver saudável, a skill ainda precisa fazer a pergunta P4.

## Quando existe merge

### 18. A IA consolida semanticamente as fontes

A regra é de união, não de escolha de um arquivo vencedor:

- Trecho presente em qualquer fonte entra.
- Trecho idêntico nas duas entra uma vez.
- Trecho exclusivo de uma fonte entra sem ser reescrito.
- Contradições vão para ## Conflito a fechar, identificadas pela origem.

A IA encaixa cada regra nas seções existentes:

- Projeto
- Ambiente
- Versão
- Git
- Estrutura
- Regras deste repo

O bloco VIBEFLOW:CADEIA não é importado das fontes antigas. Ele sempre vem do template.

### 19. Trata políticas do template como oferta

As políticas do template, como semver e ausência de Co-Authored-By, não podem apagar silenciosamente uma política
legada diferente.

Se houver divergência, a IA mostra:

padrão: política do template
deles: política encontrada no repositório

Sem resposta humana, ambas permanecem em ## Conflito a fechar.

### 20. Grava o consolidado e mostra o mapa de origem

Depois do merge, a IA grava .vibeflow/REGRAS.md e mostra algo como:

de AGENTS: regra de dashboard
de CLAUDE: regra de deploy
das duas: descrição do projeto
contradição: homolog versus produção
política oferecida: semver

Antes de substituir os ponteiros, verifica:

- A política do usuário continua presente.
- Nenhum parágrafo é apenas o path do symlink.
- Somente SLOTs respondidos foram fechados.
- O mapa de origem foi mostrado.

### 21. Converte os arquivos legados em symlinks

Somente após o merge:

pwsh "<skill>/scripts/init.ps1" -ApplyPointers -MergeToken "<apply_token>"

No Unix:

init.sh --apply-pointers --merge-token "<apply_token>"

A primeira execução grava init-pending.json com hashes das fontes, hash inicial do alvo e token. A segunda valida o
token, confirma que as fontes não mudaram e exige que o consolidado tenha mudado. Só então substitui arquivos legados
pelos symlinks e remove REGRAS.md duplicado da raiz, quando aplicável.

## Tratamento de conflitos

### Contradição de regras

```
A IA mostra as duas regras e pergunta qual deve permanecer. A perdedora é removida somente de .vibeflow/REGRAS.md. Os
backups continuam em .vibeflow/old/.
```

### ponteiro_alheio

Exemplo:

AGENTS.md → docs/agents.md

O padrão é preservar esse symlink. Para redirecioná-lo explicitamente:

init.ps1 -RedirectPointer AGENTS

O alvo antigo é registrado em .vibeflow/old/AGENTS.target.txt.

### tipo_inesperado

Se AGENTS.md ou CLAUDE.md for um diretório ou outro tipo inesperado, o script não toca. O usuário precisa resolver
essa estrutura fora da skill.

### SYMLINK_RECUSADO

No Windows, a IA deve orientar:

- Ativar Developer Mode.
- Ou executar com privilégios administrativos.

A skill proíbe usar uma cópia física de REGRAS.md na raiz como fallback, porque isso criaria duas fontes divergentes.

## Perguntas ao usuário

São feitas uma por vez.

1. P1, confirmar ou fornecer o parágrafo do projeto, somente se o SLOT ainda estiver aberto.
2. P2, informar se o ambiente é homologação ou produção.
3. P3, informar alguma regra específica que o scan e o merge não capturaram. “Nenhuma” é resposta válida.
4. P4, perguntar se falta alguma informação ou se existe algo ambíguo a registrar.

No fluxo reparar saudável:

- P1 a P3 só aparecem se houver SLOT ou merge aberto.
- P4 sempre aparece.

A resposta humana deve ser aplicada literalmente ao SLOT correspondente, sem a IA “melhorar” o conteúdo.

Se o usuário informar produção e migrations forem detectadas, entra exatamente este bloco:

## Produção / migrations
Migration em produção é irreversível no sentido prático. Não gerar, não aplicar, não “aproveitar o gancho”. Se a
tarefa exigir schema, parar e perguntar.

## Encerramento

A skill não faz commit.

Ela orienta commitar:

```
.vibeflow/REGRAS.md
AGENTS.md
CLAUDE.md
.vibeflow/old/, se existir
.vibeflow/phases/.gitkeep
```

E não commitar:

```
.vibeflow/init-report.json
.vibeflow/init-pending.json
```

No Windows, core.symlinks=true é apenas verificado. O script emite aviso, mas não altera a configuração do Git.

## Resumo linear

```
Usuário ativa vibe-init
→ IA lê SKILL.md
→ IA chama init.ps1 no Windows ou init.sh no Unix
→ script identifica raiz do repo
→ script inventaria .vibeflow, REGRAS, AGENTS e CLAUDE
→ script classifica o fluxo como novo ou reparar
→ script cria .vibeflow/phases e .gitignore
→ script calcula merges e conflitos
→ script cria backups e valida SHA-256
→ script move, cria ou preserva REGRAS.md
→ script cria symlinks que já são seguros
→ script preserva arquivos usados por merge
→ script escaneia nome, descrição, estrutura, stack e migrations
→ script preenche somente SLOTs comprováveis
→ script atualiza VIBEFLOW:CADEIA
→ script grava init-report.json
→ IA lê relatório, REGRAS atual e fontes de merge
→ IA apresenta resumo inicial
→ IA une regras sem descartar fontes
→ IA pergunta contradições e SLOTs ainda abertos
→ IA grava .vibeflow/REGRAS.md consolidado
→ IA chama o motor com ApplyPointers + apply_token
→ script substitui os legados por symlinks
→ IA faz P4
→ IA informa os arquivos que devem ser commitados
```

A suíte comprova os principais cenários: repositório vazio, reparo, backup versionado, falha de hash, merge com uma
ou duas fontes, REGRAS.md da raiz somado a legado, migração de REGRAS.md da raiz, checkout Windows sem symlinks,
reparo do bloco da cadeia, restauração de `phases/.gitkeep`, relatório parcial em falha tardia, teto da estrutura e
idempotência do estado saudável.
