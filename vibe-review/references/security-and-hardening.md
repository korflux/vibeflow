# Segurança e Hardening (Rubrica de Auditoria)

Abrir sempre que o diff tocar input, query, auth, sessão, permissão, segredo, upload, integração externa, banco de dados ou dados de usuário.

Julgar de forma implacável e cética. Toda vulnerabilidade real vira `R*` bloqueante (`Critical` ou `Required`). Remédio aponta para `vibe-implement`. Não altere código nesta skill.

---

## 1. Vulnerabilidades Críticas (Critical)

Bloqueio imediato. Falhas exploráveis ou perda de dados/segredos:

- **Injeção de Código e Dados:**
  - SQL Injection: consultas montadas com concatenação de string, interpolação ou `.raw` sem parametrização.
  - XSS (Cross-Site Scripting): inserção de HTML ou scripts controlados pelo usuário sem escape adequado no frontend ou backend.
  - Shell / Command Injection: execução de comandos de sistema (`exec`, `system`, subprocess) com strings concatenadas em vez de array de argumentos sem shell.
  - SSRF (Server-Side Request Forgery): requisições HTTP feitas pelo servidor usando URLs fornecidas pelo usuário sem allowlist estrita de domínios permitidos.
- **Autorização e Autenticação:**
  - IDOR (Insecure Direct Object Reference): manipulação de IDs para acessar ou modificar recursos de outros usuários sem validação de permissão no servidor.
  - Bypass de autorização: verificação de permissão feita apenas no client (browser) e ausente no endpoint do servidor.
  - Sessão insegura: tokens ou credenciais salvos em `localStorage` / `sessionStorage` em vez de cookies `HttpOnly` + `Secure` + `SameSite`.
  - Senhas em texto puro ou com hashes fracos (MD5, SHA1); ausência de Argon2id ou bcrypt.
- **Vazamento e Integridade:**
  - Segredos, chaves de API, credenciais ou tokens hardcoded no código, no git ou expostos no bundle do frontend.
  - Logs registrando senhas, tokens completos, dados de cartão ou dados pessoais sensíveis.
  - Caminhos de arquivo controlados pelo usuário sem `basename` ou validação contra diretório permitido (Path Traversal).

---

## 2. Robustez e Validação de Borda (Required)

- **Falta de limites de entrada:** Inputs sem restrição de tamanho máximo de caracteres, arquivos sem limite de bytes ou requests sem timeout (risco de DoS e travamento).
- **Validação frouxa:** Ausência de allowlist de campos no body das requisições (mass assignment).
- **Tratamento de erros inseguro na borda:** Exibição de stack traces, queries SQL, erros internos de banco ou infraestrutura para o usuário final. Ausência de envelope padronizado ({ error: { code, message, status } }) ou de middleware central para captura de exceções de domínio.
- **Rate Limit ausente:** Endpoints sensíveis de autenticação (login, cadastro, recuperação de senha, 2FA) sem limitação de taxa de requisições.

---

## 3. Classificação

| Gravidade | Critério | Bloqueia Approve? |
|---|---|---|
| **Critical** | Falha de injeção, bypass de auth/IDOR, vazamento de segredo ou perda de dados. | Sim |
| **Required** | Falta de limite de tamanho, ausência de validação de borda, CORS excessivo, log verboso de dados. | Sim |
| **Nit / FYI** | Sugestão de defense-in-depth adicional, ajuste cosmético de mensagem sem risco direto. | Não |
