# Hospedagem e dados

Descubra onde o produto vai rodar: computador local, rede interna, hospedagem compartilhada, VPS, serviço gerenciado, lojas de aplicativos ou outro destino. Para aplicativo distribuído por loja, separe distribuição do app e hospedagem do backend, quando houver.

Pergunte o que já existe antes de recomendar stack ou provedor: domínio, plano/VPS e provedor, sistema operacional, painel, acesso e permissões, runtime, banco disponível, e-mail, DNS/SSL, rotina de deploy, backup e responsável pela operação. Detalhe apenas o ramo escolhido. Informação que o usuário não sabe vira dependência verificável, nunca especificação inventada.

Descubra o que precisa persistir, quem cria/edita/exclui, relações, busca, volume, retenção, exportação e recuperação. Decida se precisa de banco, arquivos ou conteúdo versionado. Site estático sem dados dinâmicos pode ter banco N/A. Hospedagem compartilhada pode restringir runtime persistente; valide isso antes de escolher a stack.
