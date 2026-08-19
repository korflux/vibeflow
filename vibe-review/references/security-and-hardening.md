# Security (review)

Abrir **só** se o diff toca input, auth, autorização, segredo, upload, pagamento, LLM ou dados pessoais. Uma ref. Sem pasta de classes.

Julgar. Remédio = `R*` + `vibe-implement`. Não patche aqui.

## O que vira Critical (confiança alta)

Padrão explorável + input do atacante, ou perda de dado/segredo.

- Input na borda sem allowlist / limite; SQL concatenado; HTML/URL sem escape
- Segredo em código, log ou client
- Ação privilegiada sem checagem no servidor; IDOR (id do recurso sem dono)
- Mass assignment / body sem allowlist
- Sessão em `localStorage`; senha sem Argon2id/bcrypt; crypto caseira
- SSRF / URL do usuário sem allowlist de destino

## O que não inventar

Teórico, defense-in-depth, “e se um dia” → Nit ou FYI. Sem CVE de dep sem evidência no diff.

## Checklist rápido no diff

- Validação na borda, não só no client
- Query parametrizada; sem `.raw` / `exec` com string montada
- Authz no handler, não só no login
- `.env` / secret manager; nada no bundle do browser
- Erro ao usuário sem stack; log sem senha/token
- Rate limit em login/reset se a fatia cria esse path
