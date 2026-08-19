# vibe-interview — análise do rascunho

Conteúdo de origem: `docs/vibe-interview/` (SKILL incompleto + 3 referências). Comparado com o contrato real da cadeia (`vibe-init`: fonte única em `.vibeflow/`, pasta `phases/` vazia no init, tabela xhigh/max = interview primeiro).

---

## O que o rascunho acerta

A mecânica de conversa é boa e entra na skill quase intacta:

- Gate antes de perguntar (não usar em typo / inequívoco; bloquear CI sem humano).
- HIPÓTESE + CONFIDENCE visíveis, número honesto.
- Uma pergunta por vez, com GUESS, disposto a estar errado.
- Distinção “quer” vs “deveria querer”.
- Probe visual curto e só quando a UI ainda está aberta. Interview não fecha CSS.
- Restate de ~10 segundos, Fora inegociável, sim explícito (não “beleza, bora”).
- Parada ~95%: prever as próximas 3 reações.
- Artefato = lógica (pedido → Q/GUESS/R → conclusão), não só o recap.
- Fase 2 é opcional: intenção ok, forma não. Lentes seletivas, não checklist.
- Calibração por ritmo (reframe, opinião, Not Doing), não por copiar exemplo.

Isso é o produto. O resto era embalagem quebrada.

---

## O que estava quebrado

### 1. Path de outro produto

O único destino em disco era:

```
docs/fluxline/interview/interview-fase-N-<slug>-<nome-curto>.md
```

Não existe `fluxline` neste repo. O init já reserva `.vibeflow/phases/` para a cadeia e **não escreve arquivo lá**. Interview gravar em `docs/` fura a fonte única e deixa spec/plan sem lugar comum.

### 2. SKILL.md truncado

O texto manda “ver **Artefato em disco**” e “template abaixo”. Nem a seção nem o template existem. Fase 2 não tem passo operacional no SKILL; só catalogs em `references/`. Um agente que seguir só o SKILL termina a Fase 1 sem arquivo válido e não sabe como refinar.

Também falta frontmatter (`name` / `description`). Sem isso a skill não dispara.

### 3. Nome do arquivo carrega metadado demais

`interview-fase-N-slug-nome-curto.md` mistura tipo, número, slug e título. Spec e plan, no mesmo esquema, viram uma pasta `docs/` com nomes longos e sem agrupamento por pedido.

O contrato novo separa:

| Dado | Onde |
|---|---|
| número da fase | pasta `phase-<n>-…` |
| frase curta | slug da pasta |
| tipo do artefato | nome do arquivo (`interview.md`, depois `spec.md`) |

### 4. Dois lares para a mesma regra

Gate, HIPÓTESE, probe visual e restate aparecem no SKILL e de novo no miolo da Fase 1. “Por que existe” é justificativa de produto, não instrução. Nas referências, SCAMPER/HMW/JTBD e os critérios de valor/viabilidade estão corretos como consulta, mas o SKILL precisa apontar para eles, não resumir as tabelas.

### 5. Handoff com nome morto

`fluxline-spec` não é skill deste repo. A cadeia chama `vibe-spec`. Interview **não** dispara a próxima skill; só grava `Handoff: vibe-spec` ou `precisa-forma`.

### 6. Disco sem dono

`vibe-init` acerta em dividir: script = fato de disco, IA = semântica. O rascunho deixa a IA inventar `N`, criar pasta e escolher path. Isso colide (dois `phase-1`), pisa fase existente e foge do padrão que você mandou copiar.

---

## Contrato que substitui o path fluxline

```
.vibeflow/phases/phase-<n>-<slug>/interview.md
```

- `n` crescente, calculado pelo script (max existente + 1).
- `slug` = frase curta da fase, sanitizada.
- Mesma pasta recebe `spec.md` / `plan.md` depois. Interview não os cria.
- Durante a sessão: `.vibeflow/interview-wip.md` (gitignored).
- Depois do sim: script promove wip → vivo e apaga o wip.

Continuar a mesma entrevista (já há `interview.md`, ainda não há `spec.md`) = editar o vivo. Pedido novo = próxima pasta.

---

## O que foi cortado (e por quê)

| Corte | Motivo |
|---|---|
| Texto “Por que existe” no SKILL | Não muda a ação. Uma linha no gate basta |
| Seção duplicada de HIPÓTESE | Fica só no passo de abrir |
| `docs/fluxline/…` e id `N-slug-nome` | Substituído pelo contrato acima |
| `fluxline-spec` | Handoff `vibe-spec`, sem executar |
| Inventar `refine.md` | Fase 2 atualiza o mesmo `interview.md` |
| Paleta, type pairing, manifesto visual | Já estava fora; permanece fora |
| Script copiar o template vazio no apply | Apply só promove wip preenchido pela IA |

## O que permanece nas referências

- `frameworks.md` — lentes de expansão (uma por vez).
- `refinement-criteria.md` — valor / viabilidade / diferenciação / Not Doing / MVP.
- `examples.md` — ritmo, não roteiro.

Consultadas só na Fase 2. Não são copiadas para o SKILL.

---

## Estrutura (igual vibe-init)

```
vibe-interview/
  SKILL.md
  scripts/interview.ps1 | interview.py | interview.sh
  templates/interview.md
  references/{frameworks,refinement-criteria,examples}.md
docs/vibe-interview/
  ANALISE.md          ← este arquivo
  ARQUITETURA.md      ← contrato de disco
  tests/test-interview.py
```

O rascunho `docs/vibe-interview/SKILL.md` não sobrevive: era o rascunho, agora duplicaria a skill real.

---

## Assunções (avisar, não perguntar)

- Init é pré-requisito. Sem `.vibeflow/` o script recusa; a IA manda rodar `/vibe-init`.
- Sem padding em `n` (`phase-1`, não `phase-01`). A lista é numérica.
- Não há backup em `old/` para interview: o vivo *é* a trilha. Wip só some após hash ok.
- v1 não commita, não chama spec, não escolhe stack na Fase 1.
