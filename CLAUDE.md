
## Contexto

Você está trabalhando em uma API REST de frutas construída com FastAPI, SQLAlchemy 2, Alembic e PostgreSQL, rodando em Docker. O projeto já está funcional com um CRUD básico. Seu objetivo é evoluir essa API de forma estratégica, mantendo coerência arquitetural e boas práticas de backend Python.

---

## Estrutura atual do projeto

```
├── alembic/
│   ├── versions/
│   │   └── 79dee2c61eb6_create_fruits_table.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/v1/routers/
│   │   └── fruit.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── models/
│   │   └── fruit.py
│   ├── repositories/
│   │   └── fruit_repository.py
│   ├── schemas/
│   │   └── fruit.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_fruits.py
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── alembic.ini
└── requirements.txt
```

---

## Stack tecnológica

- Python 3.12
- FastAPI 0.115.x
- SQLAlchemy 2.0.x (estilo Mapped / mapped_column)
- Alembic 1.15.x
- Pydantic v2 com pydantic-settings
- PostgreSQL 16 via psycopg2-binary
- Docker + docker-compose

---

## O que deve ser implementado

Implemente as seguintes melhorias em ordem, garantindo que cada uma funcione antes de avançar para a próxima.

---

### 1. Camada `services` entre routers e repositories

**Objetivo:** Separar regras de negócio (services) de acesso ao banco (repositories).

**Fluxo obrigatório:** `router → service → repository → banco`

- Criar `app/services/fruit_service.py` contendo toda a lógica de negócio
- O `fruit_repository.py` deve conter apenas queries e operações de banco
- O `fruit.py` (router) deve chamar apenas o service, nunca o repository diretamente
- O service chama o repository
- Aplicar o mesmo padrão para todos os novos módulos criados nos itens seguintes

---

### 2. Model `Category` com vínculo em `Fruit`

**Objetivo:** Organizar frutas por categorias (tropical, cítrica, baga, etc.)

**Model `Category`:**
```python
id: str (UUID)
nome: str (único, max 80 chars)
descricao: str | None
data_cadastro: datetime (server_default)
```

**Alterações em `Fruit`:**
- Adicionar `category_id: str | None` como FK para `Category`

**Arquivos a criar:**
- `app/models/category.py`
- `app/schemas/category.py` — schemas: `CategoryCreate`, `CategoryUpdate`, `CategoryResponse`
- `app/repositories/category_repository.py`
- `app/services/category_service.py`
- `app/api/v1/routers/category.py`

**Endpoints:**
- `POST /api/v1/categories/` — criar categoria
- `GET /api/v1/categories/` — listar categorias (paginado)
- `GET /api/v1/categories/{id}` — buscar por id
- `PATCH /api/v1/categories/{id}` — atualizar parcial
- `DELETE /api/v1/categories/{id}` — remover (bloquear se houver frutas vinculadas → 409)
- `GET /api/v1/categories/{id}/fruits` — listar frutas de uma categoria

**Migration:** gerar migration para criar a tabela `categories` e adicionar a FK em `fruits`.

---

### 3. Soft delete em `Fruit`

**Objetivo:** Nunca apagar fisicamente uma fruta. Preservar histórico.

**Alterações em `Fruit`:**
- Adicionar campo `deleted_at: datetime | None = None`

**Regras:**
- `DELETE /fruits/{id}` apenas seta `deleted_at = now()`, nunca executa `DELETE` SQL
- Todas as queries de listagem e busca filtram `WHERE deleted_at IS NULL`
- Frutas deletadas não aparecem em nenhum endpoint, exceto no de restore

**Novos endpoints:**
- `POST /api/v1/fruits/{id}/restore` — recupera fruta removida (limpa `deleted_at`)
- `GET /api/v1/fruits/deleted` — lista frutas removidas (apenas para controle interno)

**Migration:** gerar migration adicionando coluna `deleted_at` em `fruits`.

---

### 4. Model `StockMovement` — histórico de movimentação de estoque

**Objetivo:** Registrar cada entrada ou saída de estoque de forma imutável.

**Model `StockMovement`:**
```python
id: str (UUID)
fruit_id: str (FK para fruits)
tipo: str  # "entrada" | "saida"
quantidade: int (> 0)
motivo: str | None
data_movimento: datetime (server_default)
```

**Regras de negócio no service:**
- `POST /fruits/{id}/stock/entrada` — incrementa `quantidade_estoque` na fruta e cria registro de movimento
- `POST /fruits/{id}/stock/saida` — valida se há saldo suficiente (422 se não houver), decrementa e cria registro
- O campo `quantidade_estoque` em `Fruit` continua existindo como cache do saldo atual

**Arquivos a criar:**
- `app/models/stock_movement.py`
- `app/schemas/stock.py` — schemas: `StockEntradaRequest`, `StockSaidaRequest`, `StockMovementResponse`, `StockSaldoResponse`
- `app/repositories/stock_repository.py`
- `app/services/stock_service.py`
- `app/api/v1/routers/stock.py`

**Endpoints:**
- `POST /api/v1/fruits/{id}/stock/entrada` — registrar entrada
- `POST /api/v1/fruits/{id}/stock/saida` — registrar saída (valida saldo)
- `GET /api/v1/fruits/{id}/stock/historico` — listar movimentações (paginado, ordenado por data desc)
- `GET /api/v1/fruits/{id}/stock/saldo` — retornar saldo atual com último movimento

**Migration:** gerar migration para criar tabela `stock_movements`.

---

### 5. Validações de negócio mais refinadas nos schemas

**Objetivo:** Tornar os dados mais ricos e com integridade garantida desde a entrada.

**Adicionar em `Fruit`:**
- `unidade_medida: str` — enum: `"kg"`, `"unidade"`, `"caixa"`, `"duzia"` (default: `"unidade"`)
- `estoque_minimo: int` — padrão 0, >= 0. Quando `quantidade_estoque <= estoque_minimo`, retornar campo `estoque_baixo: bool = True` na response
- `preco_custo: Decimal | None` — opcional, mas se informado deve ser < `preco` (preço de venda)

**Regra cruzada no service:** se `preco_custo` for informado, validar que `preco > preco_custo`. Caso contrário retornar 422 com mensagem clara.

**Atualizar schemas** `FruitCreate`, `FruitUpdate` e `FruitResponse` com esses campos.

**Migration:** gerar migration adicionando as novas colunas em `fruits`.

---

### 6. Logging estruturado com `structlog`

**Objetivo:** Observabilidade em produção com logs em JSON.

**Instalar:** `structlog==24.x`

**Criar `app/core/logging.py`:**
- Configurar `structlog` para emitir JSON em produção (`APP_ENV=production`) e texto colorido em desenvolvimento
- Cada request deve logar: `method`, `path`, `status_code`, `duration_ms` e um `request_id` (UUID gerado por request)
- Adicionar middleware no `main.py` para injetar o `request_id` em cada request

**Uso nos services:** nos pontos importantes (criação, deleção, movimentação de estoque), logar a operação com os dados relevantes usando `structlog.get_logger()`.

---

### 7. Autenticação JWT

**Objetivo:** Proteger os endpoints da API.

**Instalar:** `python-jose[cryptography]` e `passlib[bcrypt]`

**Adicionar em `.env.example`:**
```
SECRET_KEY=sua-chave-secreta-aqui-minimo-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Criar `app/core/security.py`:**
- Funções: `create_access_token`, `create_refresh_token`, `verify_token`, `hash_password`, `verify_password`

**Model `User` mínimo:**
```python
id: str (UUID)
email: str (único)
hashed_password: str
is_active: bool (default True)
data_cadastro: datetime
```

**Arquivos a criar:**
- `app/models/user.py`
- `app/schemas/auth.py` — `UserCreate`, `UserResponse`, `TokenResponse`, `LoginRequest`
- `app/repositories/user_repository.py`
- `app/services/auth_service.py`
- `app/api/v1/routers/auth.py`

**Endpoints públicos (sem autenticação):**
- `POST /api/v1/auth/register` — criar usuário
- `POST /api/v1/auth/login` — retorna `access_token` e `refresh_token`
- `POST /api/v1/auth/refresh` — renova access token usando refresh token

**Proteger com `Depends(get_current_user)`:**
- Todos os endpoints de frutas (exceto GET de listagem e busca, que podem ser públicos)
- Todos os endpoints de categorias
- Todos os endpoints de estoque

**Migration:** gerar migration para criar tabela `users`.

---

### 8. Rate limiting com `slowapi`

**Objetivo:** Proteger a API contra abuso.

**Instalar:** `slowapi==0.1.x`

**Configuração em `main.py`:**
- Limitar globalmente: 200 requisições/minuto por IP
- Endpoints de escrita (POST, PATCH, DELETE): 30/minuto por IP
- Endpoint de login: 10/minuto por IP (proteção contra brute force)

**Tratar o erro 429** com uma response JSON padronizada igual ao padrão de erros da API.

---

## Estrutura de pastas esperada ao final

```
app/
├── api/v1/routers/
│   ├── fruit.py
│   ├── category.py
│   ├── stock.py
│   └── auth.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   ├── security.py
│   └── logging.py
├── models/
│   ├── fruit.py
│   ├── category.py
│   ├── stock_movement.py
│   └── user.py
├── schemas/
│   ├── fruit.py
│   ├── category.py
│   ├── stock.py
│   └── auth.py
├── services/
│   ├── fruit_service.py
│   ├── category_service.py
│   ├── stock_service.py
│   └── auth_service.py
└── repositories/
    ├── fruit_repository.py
    ├── category_repository.py
    ├── stock_repository.py
    └── user_repository.py
```

---

## Regras gerais obrigatórias

- Usar sempre `Mapped` e `mapped_column` do SQLAlchemy 2 nos models
- Usar Pydantic v2 com `model_dump()`, `model_validate()` e `ConfigDict`
- Nunca chamar o repository diretamente no router — sempre passar pelo service
- Manter o padrão de exceções HTTP em `app/core/exceptions.py`
- Gerar uma migration separada para cada conjunto de alterações (uma por item implementado)
- Atualizar o `requirements.txt` com todas as novas dependências e versões fixas
- atualizar todas os scripts de testes com as novas atualizações.
- Manter os testes existentes funcionando — adaptar `conftest.py` se necessário
- Ao final de cada item, confirmar que `pytest -v` passa sem erros