# Prova visual no browser

Abrir **só** se a fatia muda o que o usuário vê no browser. Não carregar no boot de T* sem UI.

## Default

MCP `chrome-devtools` do host.

1. Subir (ou achar) a URL do fluxo da fatia. Sem servidor/URL → para e pergunta.
2. `navigate_page` até o estado a provar.
3. `take_snapshot` (árvore de a11y) para achar o controle. Interagir pelo uid do snapshot fresco.
4. `take_screenshot` do alvo (página, dialog ou trecho).
5. **Ler** a imagem: layout, copy, vazio/erro, elemento coberto, contraste óbvio. Print sem leitura não conta.
6. No fechamento: URL, o que clicou, path do print se gravou, ok/falhas visuais.

Pixel baseline não é default.

## Playwright / E2E do repo

Usar quando:

- a verificação da T* já é esse comando, ou
- o humano pediu, ou
- o DevTools não está ligado e o humano escolheu essa opção na Q.

Rode o comando do repo. Leia o artefato visual se houver (screenshot do teste). Não instale Playwright (nem outra lib de browser) sem o humano pedir.

Se a T* manda E2E **e** o DevTools está disponível: rode o comando da T*; o DevTools cobre a leitura visual se o E2E não gerar evidência inspecionável.

## Sem prova de browser

Não feche a T* com “unit passou”. Q:

```
Q: sem MCP chrome-devtools e sem E2E no repo para esta tela
RECOMENDO: ligar o MCP / rodar o E2E que já existe / você valida e reporta
(ok / outra?)
```
