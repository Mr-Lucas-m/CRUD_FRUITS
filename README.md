# 🍎 Fruits API

API REST para gerenciamento de frutas com autenticação JWT, controle de estoque, categorias e soft delete — construída com **FastAPI**, **SQLAlchemy 2**, **Alembic** e **PostgreSQL**.

---

## Funcionalidades

- Autenticação JWT (register / login / refresh token)
- CRUD completo de frutas com soft delete (restauração incluída)
- Categorias de frutas com CRUD e listagem das frutas por categoria
- Controle de estoque com histórico imutável de movimentações (entrada/saída)
- Campos refinados: `unidade_medida`, `estoque_minimo`, `preco_custo`, flag `estoque_baixo`
- Listagem paginada com filtro por nome
- Validação de dados com Pydantic v2
- Migrations versionadas com Alembic
- Logging estruturado (JSON em produção, colorido em desenvolvimento)
- Rate limiting (200 req/min global, 30/min em escrita, 10/min no login)
- Testes com SQLite em memória (50 testes, isolamento total por função)
- Health check em `/health`
- Containerização com Docker + PostgreSQL

---

## Estrutura do Projeto

```
crud_fruits/
├── alembic/
│   └── versions/
│       ├── 79dee2c61eb6_create_fruits_table.py
│       ├── aaa111111111_category_and_fk.py
│       ├── bbb222222222_soft_delete.py
│       ├── ccc333333333_stock_movements.py
│       ├── ddd444444444_fruit_validations.py
│       └── eee555555555_users.py
├── app/
│   ├── api/v1/routers/
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── fruit.py
│   │   └── stock.py
│   ├── core/
│   │   ├── config.py       # Settings via pydantic-settings + .env
│   │   ├── database.py     # Engine, SessionLocal, Base, get_db
│   │   ├── exceptions.py   # HTTPExceptions de domínio
│   │   ├── limiter.py      # slowapi rate limiter
│   │   ├── logging.py      # structlog (JSON prod / colorido dev)
│   │   └── security.py     # JWT + bcrypt
│   ├── models/             # SQLAlchemy (Mapped / mapped_column)
│   ├── schemas/            # Pydantic v2
│   ├── repositories/       # Queries e operações de banco
│   ├── services/           # Regras de negócio
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_fruits.py
│   └── test_stock.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
└── requirements.txt
```

---

## Rodar com Docker (recomendado)

### Pré-requisito

[Docker Desktop](https://www.docker.com/products/docker-desktop) instalado e rodando.

### 1. Clone o repositório

```bash
git clone https://github.com/Mr-Lucas-m/CRUD_FRUITS.git
cd crud_fruits
```

### 2. Configure o .env

```bash
cp .env.example .env
```

Edite o `.env` e defina um `SECRET_KEY` seguro:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/fruits_db

APP_ENV=production
APP_TITLE=Fruits API
APP_VERSION=1.0.0
APP_DEBUG=false
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

SECRET_KEY=troque-por-uma-chave-secreta-forte-com-32-chars-minimo
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> O `DATABASE_URL` do `.env` é ignorado pelo container — o `docker-compose.yml` usa `db:5432` automaticamente.

### 3. Suba os containers

```bash
docker-compose up --build
```

O Docker vai:
1. Criar o container do PostgreSQL
2. Aguardar o banco estar saudável
3. Rodar `alembic upgrade head` (todas as migrations)
4. Subir a API

### 4. Acesse

| URL | Descrição |
|-----|-----------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/health | Health check |

### Comandos úteis

```bash
docker-compose up --build -d    # subir em background
docker-compose logs -f api      # ver logs da API
docker-compose logs -f db       # ver logs do banco
docker-compose down             # parar containers
docker-compose down -v          # parar e apagar volume do banco
```

---

## Rodar localmente (sem Docker)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
cp .env.example .env         # edite DATABASE_URL com localhost
```

Crie o banco e rode as migrations:

```bash
createdb -U seu_usuario fruits_db
alembic upgrade head
uvicorn app.main:app --reload
```

---

## Testes

Não precisa de banco rodando — usam SQLite em memória:

```bash
pytest -v                        # todos os testes
pytest tests/test_fruits.py -v   # módulo específico
pytest -v -k "test_create"       # filtrar por nome
```

---

## Como usar a API (fluxo completo)

### 1. Registrar usuário

```http
POST /api/v1/auth/register
{"email": "user@example.com", "password": "minimo8chars"}
```

### 2. Fazer login e obter token

```http
POST /api/v1/auth/login
{"email": "user@example.com", "password": "minimo8chars"}
```

Resposta:
```json
{"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}
```

### 3. Usar o token

No Swagger (`/docs`): clique em **Authorize** (cadeado) e cole o `access_token`.

Em requisições HTTP:
```
Authorization: Bearer eyJ...
```

### 4. Renovar o token

```http
POST /api/v1/auth/refresh
{"refresh_token": "eyJ..."}
```

---

## Endpoints

### Auth (públicos)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Registrar usuário |
| POST | `/api/v1/auth/login` | Login — retorna access + refresh token |
| POST | `/api/v1/auth/refresh` | Renovar access token |

### Frutas

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/api/v1/fruits/` | — | Listar (paginado, filtro por nome) |
| GET | `/api/v1/fruits/{id}` | — | Buscar por ID |
| GET | `/api/v1/fruits/deleted` | JWT | Listar frutas removidas |
| POST | `/api/v1/fruits/` | JWT | Cadastrar fruta |
| PATCH | `/api/v1/fruits/{id}` | JWT | Atualizar parcialmente |
| DELETE | `/api/v1/fruits/{id}` | JWT | Soft delete |
| POST | `/api/v1/fruits/{id}/restore` | JWT | Restaurar fruta removida |

### Categorias (todas requerem JWT)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/v1/categories/` | Listar categorias |
| GET | `/api/v1/categories/{id}` | Buscar por ID |
| GET | `/api/v1/categories/{id}/fruits` | Frutas da categoria |
| POST | `/api/v1/categories/` | Criar categoria |
| PATCH | `/api/v1/categories/{id}` | Atualizar parcialmente |
| DELETE | `/api/v1/categories/{id}` | Remover (bloqueia se houver frutas) |

### Estoque (todas requerem JWT)

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/fruits/{id}/stock/entrada` | Registrar entrada |
| POST | `/api/v1/fruits/{id}/stock/saida` | Registrar saída (valida saldo) |
| GET | `/api/v1/fruits/{id}/stock/historico` | Histórico paginado |
| GET | `/api/v1/fruits/{id}/stock/saldo` | Saldo atual + último movimento |

---

## Payload de exemplo — Fruta

```json
{
  "nome": "Manga",
  "preco": "4.99",
  "quantidade_estoque": 100,
  "unidade_medida": "unidade",
  "estoque_minimo": 10,
  "preco_custo": "2.50",
  "category_id": "uuid-da-categoria"
}
```

Campos de resposta adicionais:
- `estoque_baixo: bool` — `true` quando `quantidade_estoque <= estoque_minimo`
- `deleted_at` — preenchido em frutas soft-deleted

---

## Gerenciamento de Migrations

```bash
alembic upgrade head                              # aplicar todas
alembic revision --autogenerate -m "descricao"    # nova migration
alembic downgrade -1                              # reverter uma
alembic history --verbose                         # ver histórico
alembic current                                   # versão atual do banco
```

---

## Stack

| Lib | Versão | Função |
|-----|--------|--------|
| fastapi | 0.115.12 | Framework web |
| uvicorn | 0.34.0 | Servidor ASGI |
| sqlalchemy | 2.0.40 | ORM |
| alembic | 1.15.2 | Migrations |
| pydantic | 2.11.1 | Validação de dados |
| pydantic-settings | 2.8.1 | Configuração via .env |
| psycopg2-binary | 2.9.10 | Driver PostgreSQL |
| python-jose | 3.3.0 | JWT |
| bcrypt | 4.2.1 | Hash de senhas |
| structlog | 24.4.0 | Logging estruturado |
| slowapi | 0.1.9 | Rate limiting |
| email-validator | 2.2.0 | Validação de e-mail |
| pytest | 8.3.5 | Testes |
| httpx | 0.28.1 | Cliente HTTP para testes |
| ruff | 0.11.3 | Linter + formatter |
