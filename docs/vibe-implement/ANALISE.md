# vibe-implement, análise

## Problema e decisão

O coordenador acumulava seleção, implementação delegada, reconferência técnica, execução de provas, manutenção de snapshots e Git. Cada handoff era seguido de nova inspeção pelo coordenador, mesmo quando um responsável já tinha evidência suficiente. O plan também reunia planejamento, estado e histórico operacional, aumentando contexto e risco de duplicação.

O protocolo explícito coordenacao-v1 transforma coordenação em encaminhamento por resultado. Implementador investiga o fluxo e entrega código/testes juntos; verificador responde por conferir diff, ownership, cobertura e integração; corretor responde por falhas; revisor julga independentemente. Finalizador genérico/default apto recebe handoff operacional delimitado para registros/Git. Perfis específicos atuais continuam sem Git; não há instalação nova obrigatória nem renomeação de perfil para remover proibição.

Coordenador escolhe resultado, dependências, responsáveis e colaboração; recebe cobertura, exceções e próximo passo. Reconferência só entra diante de contradição ou decisão estratégica. Inventário e transições mecânicas ficam com os responsáveis, evitando que trocar o arquivo de estado preserve o mesmo operador central.

## Fluxo de ponta a ponta

```text
plan aprovado + modo → finalizador obtém resumo do motor
  → coordenador seleciona entrega e colaboração útil
  → implementador entrega código + testes + checagem local
  → finalizador registra local; dependentes podem avançar
  → verificador confere entrega/aceite/cobertura e prova integração
  → falha concreta → corretor → verificador renova provas afetadas
  → finalizador registra integração e commit real
  → revisor independente julga origem, código e riscos
  → correção bloqueante → corretor/verificador/finalizador → nova review
  → coordenador apresenta resultado e pede confirmação humana única
  → finalizador fecha review/decisões autorizadas/Git/push
```

Não existe passagem obrigatória de complementar testes. O implementador cobre seu resultado; verificador identifica lacunas concretas de integração. Não se elimina teste necessário nem se executa matriz completa por task. Seleção considera diff, consumidores, risco e aceite; provas verdes de inputs inalterados são reaproveitadas. UI exige inspeção renderizada quando o aceite depender dela.

## Colaboração e independência

Colaboração depende de uma incerteza ou dependência que possa ser destravada. Exploração e preparação de recortes independentes podem ocorrer juntas, com interlocutores e comunicação técnica direta. Coordenador escolhe o arranjo e evita intermediar cada detalhe. Contexto relacionado é reutilizado; certificação/review continuam independentes dos escritores.

Um recurso compartilhado tem um dono por vez, inclusive arquivos operacionais e índice. Código paralelo conserva autorização aplicável e isolamento; a mudança não cria escritores concorrentes nem framework de orquestração. Grupo registrado ajuda a decisão e não autoriza sozinho paralelizar.

## Estado e retomada

Plan define trabalho e mostra resumo curto. execution.json versionado ao lado guarda somente estado atual por task, integração, origem e commit; Git/review guardam histórico. O motor captura hashes/HEAD, valida formato/paths/ancestralidade e troca arquivo atomicamente sem executar comandos informados como evidência. stdout é compacto; detalhes são consultados por quem precisa diagnosticar.

Isso evita JSON e logs em Markdown e duas fontes concorrentes de conclusão. Checkbox resume estado comprovado pelo motor. Ausência do sidecar significa pendente; corrupção bloqueia. Inputs alterados invalidam somente evidência afetada, sem refazer código válido. Cobertura semântica ainda pertence ao verificador, pois integridade do hash não prova completude do teste.

Registro do hash depois do commit pode deixar residual operacional; ele entra no fechamento final autorizado. Não se cria ciclo de commits para guardar o próprio hash.

## Compatibilidade e limites

Etapas-v1 conserva etapas de código/testes/validação e snapshots no plan. Legado conserva commit por task. B conserva ciclo individual, inclusive com marcador novo, sem sidecar. Runs existentes não migram implicitamente. O manual histórico é carregado somente quando o marcador/modo exigir; o fluxo principal permanece curto.

Express/texto avulso conserva a entrada proporcional e não cria phase/init para ajuste localizado. Falhas de prova exigem correção pela causa, enquanto decisões materiais e impedimentos reais chegam ao humano. Review tem no máximo duas rodadas de correção; aprovação/push continuam dependentes da confirmação final. O motor não interpreta intenção, certifica cobertura semântica nem opera Git de escrita.
