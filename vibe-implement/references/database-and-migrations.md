# Banco de Dados, Migrations e Precisão Numérica (Guia de Referência)

Consulte este catálogo ao modelar schemas, especificar regras de dados, planejar migrations, implementar consultas/ORM ou auditar integridade e performance em bancos relacionais (Postgres, SQLite, MySQL).

---

## 1. Regra Inegociável dos Números e Dinheiro

O uso incorreto de tipos numéricos é uma das falhas mais destrutivas em sistemas de software, gerando distorções financeiras cumulativas silenciosas.

### A. O Perigo de `FLOAT` / `REAL` / `DOUBLE PRECISION`
- Ponto flutuante binário (IEEE 754) armazena números como frações em base 2. Decimais comuns como `0.10` ou `0.05` tornam-se dízimas periódicas que sofrem aproximação no hardware.
- Somas e agregações acumuladas geram desvios que corrompem relatórios e impedem igualdades exatas (`WHERE total = 108.80` retorna vazio).
- Arredondamento tardio (`toFixed`, `round`) atua sobre valores já corrompidos na memória e tende a truncar para baixo em casos de meio centavo.

### B. O Padrão Correto por Cenário
1. **No Banco de Dados:** Use sempre `DECIMAL(p, s)` ou `NUMERIC(p, s)` (ponto fixo exato).
   - Moedas e valores monetários comuns: `DECIMAL(12, 2)` ou `DECIMAL(14, 2)`.
   - Taxas, juros, câmbio, criptoativos ou rateios: `DECIMAL(16, 4)` até `DECIMAL(20, 8)`.
2. **Em APIs e Gateways de Pagamento (quando você controla as duas pontas):**
   - Centavos inteiros (`BIGINT` ou `INTEGER`). Exemplo: `1099` para `$10.99`.
   - Multiplicações e divisões exigem arredondamento explícito (`Math.round`) antes de truncar, evitando perda de centavo por conversão.
3. **No Tráfego e Serialização:**
   - Valores como `TEXT` em payloads JSON são seguros para transporte, mas no backend devem ser convertidos imediatamente para tipos de precisão arbitrária (`Decimal.js`, `BigDecimal`, `BigNumber`), **nunca** para `Number` ou `float` nativo.

---

## 2. Modelagem de Tabelas e Tipos de Dados

- **Chaves Primárias (PKs):**
  - `BIGINT GENERATED ALWAYS AS IDENTITY`: Padrão para performance máxima e menor ocupação de página em tabelas de alto volume.
  - `UUIDv7`: Padrão quando IDs precisam ser não enumeráveis e seguros para APIs públicas. O `UUIDv7` é ordenado no tempo, evitando a fragmentação severa de árvores B-Tree causada pelo `UUIDv4`.
- **Datas e Fusos Horários:**
  - Use sempre `TIMESTAMPTZ` (`TIMESTAMP WITH TIME ZONE`). O tipo `TIMESTAMP` sem fuso descarta a referência e quebra em mudanças de fuso ou horário de verão.
  - Armazene sempre em UTC e converta para o fuso do usuário na camada de apresentação.
- **Strings e Textos:**
  - Prefira `TEXT` com constraint `CHECK` em vez de `VARCHAR(255)` arbitrário. No Postgres, `TEXT` e `VARCHAR` têm desempenho idêntico; limites artificiais engessam o schema sem ganho de performance.
- **Constraints Declaradas no Banco (Defesa em Profundidade):**
  - `NOT NULL` explícito em todas as colunas que não devam aceitar nulo.
  - `CHECK` constraints para regras de negócio imutáveis (ex: `CHECK (price >= 0)`, `CHECK (status IN ('draft', 'published', 'archived'))`).
  - `FOREIGN KEY` sempre com regra de deleção explícita (`ON DELETE RESTRICT`, `CASCADE` ou `SET NULL`), nunca implícita.
  - **Índices em Foreign Keys:** O Postgres **não** cria índices automáticos em FKs. Toda coluna de FK deve ser explicitamente indexada para evitar Sequential Scans na tabela filha em deletes e joins.

---

## 3. Estratégia de Índices e Performance de Consultas

- **Seleção de Índices:**
  - **B-Tree:** Padrão para igualdade (`=`) e intervalos (`<`, `>`, `BETWEEN`, `ORDER BY`).
  - **GIN:** Obrigatório para colunas `JSONB`, arrays e Full-Text Search.
  - **Índices Parciais (`Partial Indexes`):** Crie índices filtrados para subconjuntos ativos (ex: `CREATE INDEX ... WHERE deleted_at IS NULL` ou `WHERE status = 'pending'`). Reduzem tamanho em disco e aceleram queries focadas.
  - **BRIN:** Para tabelas gigantes ordenadas naturalmente por inserção cronológica (logs, telemetria, eventos).
- **Anti-Padrões de Query (Bloquear em Código e Review):**
  - **`SELECT *` em Produção:** Proibido. Liste explicitamente as colunas necessárias para reduzir I/O de rede e viabilizar Index-Only Scans.
  - **Funções em Colunas no `WHERE`:** `WHERE DATE(created_at) = '2026-08-25'` anula o índice. Reescreva para intervalo: `WHERE created_at >= '2026-08-25 00:00:00' AND created_at < '2026-08-26 00:00:00'`.
  - **Wildcards à Esquerda (`LIKE '%termo'`):** B-Tree não atende busca por sufixo/infixo. Exige extensão `pg_trgm` com índice GIN/GiST ou Full-Text Search.
  - **Paginação por `OFFSET` Alto:** `OFFSET 50000` lê e descarta 50 mil linhas. Use **Cursor / Keyset Pagination** (`WHERE id > last_id ORDER BY id LIMIT 20`).
  - **Queries N+1 em ORMs:** Proibido executar queries filhas em loop. Use `JOIN`, subqueries agregadas ou eager loading com `IN (...)`.

---

## 4. Migrations Seguras e Zero-Downtime

- **Padrão Expand/Contract (Migrações Não Destrutivas):**
  1. *Fase 1 (Expand):* Adicione a nova coluna como anulável (ou com `DEFAULT` constante).
  2. *Fase 2 (Dual-Write):* O código passa a escrever em ambas e ler da nova.
  3. *Fase 3 (Backfill):* Popule os dados legados em lotes pequenos.
  4. *Fase 4 (Contract):* Aplique `NOT NULL` usando `ADD CONSTRAINT ... NOT VALID` seguido de `VALIDATE CONSTRAINT` (evita locks longos de tabela).
  5. *Fase 5 (Cleanup):* Remova a coluna ou tabela legada somente após a versão antiga do código estar totalmente fora de circulação.
- **Criação Concorrente de Índices:** Em produção com tráfego, utilize sempre `CREATE INDEX CONCURRENTLY` para evitar lock de leitura e escrita.
- **Transações Curtas:** Blocos `BEGIN ... COMMIT` devem ser rápidos e conter apenas operações no banco. Proibido fazer requisições HTTP ou processamento pesado dentro da transação.
- **Proibido em Produção sem Autorização Humana:** `DROP TABLE`, `DROP COLUMN`, `TRUNCATE` ou alteração de tipo destrutiva sem plano de rollback explícito.

---

## 5. Segurança, RLS e Conexões

- **SQL Injection Zero:** Toda query dinâmica deve ser parametrizada (`$1, $2` ou parâmetros nomeados do ORM). Proibido `.raw` concatenado com inputs externos.
- **Row-Level Security (RLS):**
  - Em políticas RLS, utilize `(select auth.uid())` em vez de chamar funções diretamente na expressão para evitar reavaliação por linha.
  - Toda coluna usada como filtro de tenant/usuário em RLS (`user_id`, `org_id`, `tenant_id`) deve possuir índice.
- **Pool de Conexões em Serverless:**
  - Utilize poolers (PgBouncer, Supabase Pooler, Neon serverless driver) para prevenir exaustão de conexões em arquiteturas serverless/edge.
