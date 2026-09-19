# vibe-design, arquitetura

`/vibe-design` desenha a apresentação de fluxos aprovados na spec e grava um único `design.md` entre spec e plan. A IA decide o desenho a partir da spec e das referências de leitura; o motor resolve o alvo e prepara o arquivo vivo.

```text
.vibeflow/phases/phase-<n>-<slug>/design.md
.vibeflow/mvp/design.md
```

## 1. Papéis e ownership

| Peça | Responsabilidade |
|---|---|
| `SKILL.md` | Validar spec aprovada, escolher modo de entrada, aplicar os três usos, redigir telas, kit, tokens e handoff para plan. |
| `scripts/design.py`, `design.ps1`, `design.sh` | Inventário, seleção do alvo, gates mecânicos, preparação do vivo e relatório. |
| `templates/design.md` | Forma de entrada, inventário de telas, kit, disposição por tela, tokens, responsivo, estados e prova. |
| `references/modos-entrada.md` | Catálogo dos dois modos de entrada, consultado conforme a origem do desenho. |
| `references/kit-e-tokens.md` | Catálogo de kit mínimo, tokens, iconografia, responsivo, estados e prova visual. |
| `.vibeflow/design-report.json` | Evidência operacional, fora do Git. |
| `design.md` | Restrição executável para plan, implement e review. Texto versionado, sem código e sem imagem final. |

O motor não desenha tela, não escolhe tokens, não escreve prosa e não edita source ou teste.

## 2. Dependências e seleção

Sem `.vibeflow/`, `INIT_AUSENTE`. O modo phase exige `spec.md` aprovada e reusa a maior phase com spec sem design. `--dir` força uma phase existente. A skill não cria phase por conta própria sem spec, e `plan.md` existente bloqueia nova escrita semântica no mesmo alvo. Pedido novo exige outra phase.

No modo MVP, `--mvp` fixa `.vibeflow/mvp/`, exige `spec.md`, recusa `--slug` e `--dir`, e nunca cria phase. A flag representa uma decisão semântica da IA.

Flags públicas:

```text
python design.py [--root PATH] [--apply] [--slug TEXTO] [--dir phase-N-slug] [--mvp]
pwsh design.ps1 [-Root PATH] [-Apply] [-Slug TEXTO] [-Dir phase-N-slug] [-Mvp]
bash design.sh [--root PATH] [--apply] [--slug TEXTO] [--dir phase-N-slug] [--mvp]
```

## 3. Modos de entrada e usos

Dois modos de entrada. Com referência, DS, DESIGN.md ou Figma entram como leitura, e o vivo registra o reusado e o adaptado com motivo, sem copiar a fonte para dentro do repo como verdade. Greenfield cria o kit mínimo primeiro com cores, tipografia, espaçamento, raio, botão, input, modal, toast, tabela e empty state, e depois mapeia cada tela da spec sobre o kit.

Três usos no mesmo contrato. Criar páginas novas, corrigir UI com R da review, e analisar UI existente contra o contrato. Os três gravam disposição técnica e decisão no vivo, sem gerar imagem final e sem editar código.

## 4. Relatório

O relatório mantém `vibeflow`, `phases`, `next_n`, `existing`, `spec_pendente`, `rascunho`, `alvo`, `mvp`, `modo_sugerido`, `created`, `modo`, `actions` e `avisos`. Não existe estado de arquivo temporário no contrato.

`actions` registra criação de `phases/.gitkeep`, de phase ou do arquivo vivo. `files` lista os sete artefatos da cadeia, incluindo `design.md`. O relatório não descreve conteúdo semântico.

## 5. Apply e escrita direta

1. Reexecuta o inventário.
2. Valida predecessor com `spec.md`, `--dir`, slug e ausência de `plan.md`.
3. Prepara `design.md` vazio quando ausente.
4. Preserva byte a byte o vivo existente.
5. Grava o relatório.
6. A IA escreve ou atualiza diretamente `design.md`, mantendo `# Status: rascunho` até aprovação.

O script não escolhe modo, não preenche markdown e não dispara plan. Ajuste ou aprovação posterior é patch no arquivo vivo. Em falha de gate, pasta nova vazia é removida para não deixar fase vazia no disco.

## 6. Contrato do artefato

Seções: Entrada, Inventário de telas, Kit mínimo quando greenfield, Disposição por tela, Tokens e iconografia, Responsivo e estados, Prova visual esperada, Decisões e Handoff.

Cada tela contém hierarquia de cima para baixo, layout e grid, ordem de leitura, componente por zona, tokens, regra de ícone com texto obrigatório em ação ambígua, responsivo com viewport estreita, overflow e truncamento, e estados por tela. Primitivo novo na página com DS existente é defeito. Design não cria comportamento novo.

## 7. Erros e testes

Falhas previstas usam `CODIGO: descricao`, incluindo `INIT_AUSENTE`, `PHASES_INESPERADO`, `MVP_INESPERADO`, `DESIGN_SEM_SPEC`, `DESIGN_SEM_ALVO`, `DESIGN_JA_PLANEJADO`, `FASE_AUSENTE`, `FASE_EXISTE`, `SLUG_INVALIDO` e `MODO_INVALIDO`.

Suítes: `docs/vibe-design/tests/test-design.py` e `docs/vibe-design/tests/test-design.sh`. Elas cobrem criação, reuse, MVP, `--dir`, colisões, gates de plan, paridade e preservação do vivo.

O handoff normal é `vibe-plan`. Recomenda-se novo chat para a porta seguinte. O `design.md` vivo carrega a restrição verificável.

## 8. Limites

- Design não contém código e não edita source, teste ou lockfile.
- Design não gera imagem final e não sincroniza Figma automaticamente.
- Design não inventa comportamento, rota, regra de negócio ou token fora do modo declarado.
- O inventário não autoriza ler a árvore inteira. A IA localiza evidências com `rg --files` e `rg -n`.
- O relatório fica fora do Git; `design.md` entra no Git.
- Design não commita; o commit começa somente quando a implement fecha uma task verde. Não há disparo automático da próxima skill.
