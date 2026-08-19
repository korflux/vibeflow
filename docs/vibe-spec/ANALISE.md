# vibe-spec — mapeamento e fluxo

Fontes:

- [fluxline-spec](https://github.com/korflux/fluxline/blob/main/skills/fluxline-spec/SKILL.md)
- [spec-kit specify](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md) + [spec-template.md](https://github.com/github/spec-kit/blob/main/templates/spec-template.md)
- [spec-kit plan-template.md](https://github.com/github/spec-kit/blob/main/templates/plan-template.md) (link que você mandou; é **plan**, não spec)

Comparado com `.vibeflow/REGRAS.md` e com `vibe-interview`.

---

## O que cada fonte é

| | Fluxline spec | Spec-kit specify | Spec-kit plan-template |
|---|---|---|---|
| Papel | Registrar o **decidido** para o plan não chutar | Requisitos *what/why* para stakeholder | Desenho técnico da feature |
| Disco | `docs/fluxline/spec/spec-fase-N-….md` | `specs/NNN-slug/spec.md` + checklist extra | `specs/…/plan.md` + research/data-model/contracts |
| N | **Reusa** o da interview | Número novo (ou timestamp) + branch opcional | Lê a spec já existente |
| Chat | Path + resumo. Proibido dump | Completion report + até 3 perguntas em lote | Preenchido pelo comando plan |
| Buraco | Q+RECOMENDO no chat. **Proibido** Open Questions no arquivo | Até 3 `[NEEDS CLARIFICATION]` **dentro** do spec.md | `NEEDS CLARIFICATION` no contexto técnico |
| How | Delta de stack, paths da fatia, comandos reais | **Proibido** how (sem stack, API, estrutura) | How completo (tech context, constitution, árvore) |
| Qualidade | Spec operacional (A*/C*, seams, boundaries) | User stories P1–P3 + FR-00N + SC-00N | Constitution gate + complexity table |

As duas “skills de spec” não descrevem o mesmo artefato. Spec-kit parte o trabalho em specify (negócio) e plan (técnica). Fluxline junta o que o **agente** precisa para executar, e empurra fatia/todo para a porta seguinte. O link `plan-template.md` é insumo da **vibe-plan**, não da spec.

---

## O que entra na vibe-spec (de cada um)

### De fluxline (espinha)

- Gate ~80%. Abaixo: mandar `vibe-interview`. Intenção quebrada no meio: voltar. Não reabrir interview por seam técnico.
- Só o decidido. Omitir o que não se aplica. Não omitir o que plan/implement precisariam inventar.
- Grava **já** como rascunho. Humano lê o **arquivo**. Chat = path + resumo curto.
- “Pode ir pro plan” / pedido da próxima porta = aprovação. “Parece bom” sem isso não basta.
- Q+RECOMENDO no chat, uma por vez. “Tanto faz” crava a rec.
- Mesmo `n` da interview. `next_n` só se não houver fase alvo (rota `high` sem interview).
- Seções: Objetivo, Suposições, Escopo+Fora, Direção visual se UI, Checklist A*/C*, Implementação delta, Como provar, Boundaries.
- Não dispara a próxima skill. Handoff é linha no arquivo.
- UI: ref curta, não CSS.

### De spec-kit specify (o que sobrevive traduzido)

- Sucesso **observável** (vira `C*`, não SC-00N).
- Assunções explícitas (vira Suposições). Defaults razoáveis no chat, não mural de FR-00N.
- Entidades de dado, se houver, **dentro** de Escopo. Sem seção obrigatória vazia.
- Critério de qualidade: testável, sem adjetivo. Sem arquivo extra `checklists/requirements.md`.
- Foco what/why no Objetivo e no aceite. How só como **delta** (fluxline), nunca dump de stack.

### De spec-kit plan-template (o que a spec **não** absorve)

| Peça | Destino |
|---|---|
| Summary técnico + approach | vibe-plan |
| Technical Context completo | vibe-plan; spec só tabela delta se houver decisão |
| Constitution Check | `.vibeflow/REGRAS.md` já é a constituição. Spec não duplica |
| Árvore Option 1/2/3 | Fora. Spec: paths reais da fatia, se âncora |
| research.md, data-model.md, contracts/, quickstart.md | vibe-plan / analyze, se um dia existirem |
| Complexity Tracking | vibe-plan |
| Branch `###-feature-name` | Fora. Pasta da cadeia já é `phase-N-slug` |

---

## O que foi cortado (e por quê)

| Corte | Motivo |
|---|---|
| `docs/fluxline/spec/…` e id `N-slug-nome` no filename | Contrato `.vibeflow/phases/phase-N-slug/spec.md` |
| Mural de user stories P1–P3 | Fluxline: comportamento observável por área. Story wall inchou spec sem ajudar o agente |
| FR-001, SC-001, NEEDS CLARIFICATION no `.md` | Pendência no arquivo vira chute no plan. Fecha no chat |
| Checklist file separado | Uma casa: verificação curta no próprio `spec.md` |
| Hooks, extensions.yml, feature.json, specs/ | Outro produto |
| Constitution + três layouts de repo | Ruído. Disco real + REGRAS |
| “Spec para stakeholder, zero how” | Nesta cadeia o leitor é o agente da próxima porta. Spec magra fez o plan inventar (lição do fluxline) |
| Colar spec no chat “pra validar” | Arquivo é a fonte |
| Esperar sim **antes** de gravar | Spec grava rascunho na hora; interview é que espera sim |
| Disparar `vibe-plan` | REGRAS: handoff é linha |

---

## Fluxo de uma run

```
[1] Script inventário → spec-report.json
[2] IA lê relatório + interview.md da alvo (se houver) + spec.md se rascunho
    + REGRAS.md; paths só se citados
[3] CONFIDENCE. <80% e buraco de intenção → pare, mande interview
[4] Seams/buracos: Q+RECOMENDO no chat, uma a uma
[5] Escreve spec-wip.md no molde do template (Status: rascunho)
[6] Script apply → phase-N-slug/spec.md
    reuse se já há pasta alvo; criar só sem alvo + slug
[7] Chat: path + resumo 4 linhas + “leia o arquivo”
[8] Ajuste = patch no vivo. Aprovado ou “pode ir pro plan” = Status aprovado
[9] Fecha. Não commita. Não dispara plan
```

---

## Assumido

- Rota `high` pode chegar aqui sem interview. Aí a spec **cria** `phase-N-slug` (slug da frase curta). Com interview, **reusa** a pasta.
- A*/C* ficam na spec para a build marcar depois. Plan aponta, não copia.
- `plan.md` na mesma pasta trava overwrite: spec daquele pedido já foi fatiada. Pedido novo = pasta nova.
- v1 não cria `research.md` nem contratos OpenAPI. Isso, se existir, é outra skill.
