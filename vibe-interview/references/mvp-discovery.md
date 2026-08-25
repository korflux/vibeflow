# Descoberta adaptativa de MVP

Use somente quando a IA classificar o pedido como projeto novo ou MVP completo. Esta referência é um mapa interno de cobertura, não um questionário para copiar no chat.

## Ritmo

- Investigue em blocos pequenos, normalmente uma a três perguntas relacionadas.
- Comece pelo que muda o produto: dor, público, resultado e jornada principal.
- Aceite respostas incompletas. Recomende e assuma lacunas reversíveis de baixo risco.
- Pergunte diretamente o que for caro, irreversível, sensível ou capaz de alterar a lógica central.
- Não repita uma pergunta respondida indiretamente. Registre a evidência e siga.
- Não encerre enquanto houver `PENDENTE CRÍTICO`.

## Formato de recomendação

1. **Recomendação:** uma escolha clara.
2. **Por quê:** relação com a realidade informada pelo usuário.
3. **Impacto:** o que essa escolha determina no MVP.
4. **Contra crítico:** somente quando puder mudar a decisão ou a arquitetura.

Não apresente opções equivalentes sem preferência. Quando houver duas opções plausíveis, recomende uma e explique em que condição a outra passa a ser melhor.

## Mapa de cobertura

| Domínio | Descobrir | Pode assumir quando | Exige decisão explícita quando |
|---|---|---|---|
| Produto | nome, problema, público, proposta, objetivo e critério de sucesso | nome provisório e métrica inicial reversível | proposta ou público continuam conflitantes |
| Escopo | aposta central, entregas, cortes, riscos e definição de pronto | cortes que preservam a aposta central | corte elimina o valor ou introduz obrigação externa |
| Jornadas | entrada, ação principal, conclusão, erros e estados vazios | estados auxiliares convencionais | usuário não sabe qual resultado principal deve obter |
| Telas | telas conhecidas, dinâmica, responsividade e estados | navegação simples derivada das jornadas | arquitetura de navegação altera permissões ou operação |
| Acesso | login, cadastro, convite, recuperação e primeiro usuário | e-mail e senha segura para sistema fechado simples | SSO, domínio restrito, login social, app interno ou acesso público |
| Usuários | criação, aprovação, desativação, perfis e tenancy | cadastro por convite em operação controlada | autorregistro, multiempresa, menores ou dados sensíveis |
| Permissões | papéis, capacidades e auditoria | admin e membro quando realmente bastam | ação sensível ou segregação de responsabilidades |
| Dados | entidades, relações, retenção, importação, exportação e busca | modelo relacional e retenção mínima documentada | migração, obrigação legal, exclusão irreversível ou dado sensível |
| Arquivos | formatos, tamanho, armazenamento e acesso | limites conservadores e storage gerenciado | conteúdo privado, grande volume ou processamento especial |
| Integrações | sistemas, APIs, webhooks, credenciais e falhas | nenhuma integração sem necessidade concreta | integração é parte da jornada central |
| Notificações | evento, canal, destinatário e opt-out | e-mail transacional essencial | marketing, WhatsApp, SMS ou custo por envio |
| Visual | logo, marca, referências, tom, temas, tokens e acessibilidade | UI clean e minimalista, fonte moderna, tema principal com light e dark desde o início | identidade existente, exigência de marca ou público com necessidade específica |
| Repositório | dono, hospedagem, visibilidade, branches e CI | GitHub privado e branch principal protegida | organização ou política do cliente já existe |
| Stack | tipo do produto, experiência, hospedagem e operação | baseline contextual abaixo | restrição de plataforma, equipe ou integração determina tecnologia |
| Infraestrutura | domínio, hospedagem, VPS, painel, runtime, banco e deploy | serviço gerenciado compatível com orçamento | infraestrutura existente limita runtime, acesso ou banco |
| Ambientes | local, homologação, produção, segredos e promoção | local mais produção para MVP simples, com preview quando nativo | compliance ou operação exige homologação separada |
| Segurança | ameaça, sessão, validação, rate limit, auditoria e recuperação | padrões seguros das regras do repo | auth, pagamento, segredo, produção ou dado pessoal |
| Privacidade | dados pessoais, base legal, consentimento e exclusão | coleta mínima | dado sensível, criança, saúde, financeiro ou obrigação contratual |
| Operação | responsável, suporte, observabilidade, backup, restore e custo | logs seguros, monitoramento básico e backup gerenciado testável | SLA, 24x7, alto custo de indisponibilidade ou operação manual crítica |
| Métricas | evento de sucesso, funil e ferramenta | métricas mínimas sem dado pessoal desnecessário | decisão comercial depende de atribuição ou experimento |
| Comercial | plano, cobrança, teste e entitlement | N/A sem monetização no MVP | pagamento ou limitação por plano faz parte da aposta |
| Conteúdo | autoria, revisão, mídia e administração | conteúdo versionado no repo para volume pequeno | cliente precisa editar frequentemente |
| SEO e localização | indexação, idiomas, regiões e URLs | N/A em ferramenta interna | aquisição orgânica ou múltiplos mercados importam |
| Legal | termos, privacidade, licenças e responsabilidades | sinalizar para validação humana | setor regulado, pagamento ou tratamento relevante de dados pessoais |

## Baselines técnicos contextuais

| Contexto | Recomendação inicial | Quando mudar |
|---|---|---|
| Aplicação web dinâmica | Next.js, Auth.js quando houver autenticação própria, Zod e PostgreSQL | framework imposto, equipe já padronizada ou requisitos fora do modelo web |
| Site predominantemente estático | Astro | área logada, mutações frequentes ou lógica de servidor dominar o produto |
| Usuário não opera PostgreSQL, não tem infraestrutura ou precisa visualizar tabelas facilmente | Supabase | há DBA/infra adequada, exigência de portabilidade estrita ou recursos específicos fora do serviço |
| Sem infraestrutura aproveitável | GitHub, Vercel e Supabase gerenciados | custo, região, compliance ou runtime exigir outro provedor |
| Cache ou fila | não incluir Redis por padrão | existe necessidade concreta de cache compartilhado, rate limit distribuído, fila ou coordenação |

Antes de recomendar hospedagem, pergunte o que já existe: Hostinger, HostGator, VPS, cloud, painel, domínio, banco disponível e nível de acesso. Hospedagem compartilhada pode não executar runtime Node persistente; esse é um contra crítico quando a stack depende disso.

## Direção visual padrão

- Priorize interface clean, minimalista e moderna.
- Escolha um tema principal conforme contexto, mas planeje light e dark desde o início.
- Use uma cor primária clara, tokens semânticos e contraste acessível.
- Prefira fonte moderna e legível. Não invente logo se já houver identidade.
- Pergunte por logo, nome, brand book, referências e restrições antes de fechar tokens.

## Acesso administrativo e break-glass

- Defina como o primeiro usuário é criado e como acesso administrativo é recuperado.
- Padrão recomendado: bootstrap único por segredo de ambiente, invalidado após uso, ou ação administrativa temporária equivalente.
- Break-glass deve ser temporário, auditado, protegido por segredo forte e removido ou desabilitado após recuperação.
- Nunca criar senha master permanente, conta invisível ou credencial compartilhada.

## Registro

Na Cobertura, use `DECIDIDO`, `ASSUMIDO`, `N/A` ou `PENDENTE CRÍTICO` e cite a evidência.
Na tabela de Decisões críticas, use IDs estáveis por domínio. Uma decisão crítica muda arquitetura, acesso, dados, operação, custo, segurança ou escopo central. Detalhes cosméticos reversíveis não recebem ID.
