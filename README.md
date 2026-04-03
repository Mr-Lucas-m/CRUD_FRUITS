# 🍎 Fruits API

API REST para gerenciamento de frutas, construída com **FastAPI**, **SQLAlchemy 2** e **Alembic**.

---

## 📋 Funcionalidades

- CRUD completo (POST, GET, PATCH, DELETE)
- Listagem paginada com filtro por nome
- Validação de dados com Pydantic v2
- Migrations versionadas com Alembic
- Tratamento de erros centralizado (409 duplicata, 404 não encontrado)
- Testes com banco SQLite em memória (isolamento total por teste)
- Health check em `/health`
- Containerização completa com Docker e PostgreSQL

---

## 🗂️ Estrutura do Projeto

```
crud_fruits/
├── alembic/
│   ├── versions/
│   │   └── 79dee2c61eb6_create_fruits_table.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │           ├── __init__.py
│   │           └── fruit.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings via pydantic-settings + .env
│   │   ├── database.py            # Engine, SessionLocal, Base, get_db
│   │   └── exceptions.py          # HTTPExceptions de domínio
│   ├── models/
│   │   ├── __init__.py
│   │   └── fruit.py               # Model SQLAlchemy (Mapped / mapped_column)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── fruit.py               # Pydantic v2: Create, Update, Response, List
│   ├── services/
│   │   ├── __init__.py
│   │   └── fruit_service.py       # Lógica de negócio e acesso ao banco
│   ├── __init__.py
│   └── main.py                    # Entry point, lifespan, middlewares
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures: client + banco em memória
│   └── test_fruits.py             # Testes de todos os endpoints
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── alembic.ini
├── docker-compose.yml
├── entrypoint.sh                  # Inicialização do container (migration + uvicorn)
├── pyproject.toml
└── requirements.txt
```

---

## 🐳 Rodar com Docker (recomendado)

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado e rodando

### 1. Clone o repositório

```bash
git clone https://github.com/Mr-Lucas-m/CRUD_FRUITS.git
cd crud_fruits
```

### 2. Configure o .env

```bash
cp .env.example .env
```

Edite o `.env` — **atenção ao host `db`**, que é o nome do serviço interno do Docker:

```env
DATABASE_URL=postgresql://fruits_user:fruits_pass@db:5432/fruits_db

APP_ENV=production
APP_TITLE=Fruits API
APP_VERSION=1.0.0
APP_DEBUG=false
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### 3. Suba os containers

```bash
docker-compose up --build
```

O Docker vai automaticamente:
1. Criar o container do PostgreSQL
2. Aguardar o banco estar saudável
3. Rodar `alembic upgrade head` (cria as tabelas)
4. Subir a API com uvicorn

### 4. Acesse

- Swagger UI → http://localhost:8000/docs
- Health check → http://localhost:8000/health

### Comandos úteis

```bash
# Subir em background (sem travar o terminal)
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Parar os containers
docker-compose down

# Parar e apagar o banco (volume)
docker-compose down -v

# Rebuild após mudanças no código
docker-compose up --build
```

---

## 🚀 Rodar localmente (sem Docker)

### 1. Clone e configure o ambiente

```bash
git clone <seu-repo>
cd crud_fruits

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure o .env

```bash
cp .env.example .env
```

Edite o `.env` com sua DATABASE_URL local — **host `localhost`**:

```env
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/fruits_db

APP_ENV=development
APP_TITLE=Fruits API
APP_VERSION=1.0.0
APP_DEBUG=true
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### 3. Crie o banco no PostgreSQL

```bash
createdb -U seu_usuario fruits_db
```

### 4. Execute as migrations

```bash
alembic upgrade head
```

### 5. Suba o servidor

```bash
uvicorn app.main:app --reload
```

---

## 🧪 Testes

Não precisa de banco rodando — usam SQLite em memória:

```bash
pytest -v
```

---

## 📡 Endpoints

| Método | Rota                  | Descrição                         |
|--------|-----------------------|-----------------------------------|
| POST   | /api/v1/fruits/       | Cadastrar fruta                   |
| GET    | /api/v1/fruits/       | Listar (paginado, filtrável)      |
| GET    | /api/v1/fruits/{id}   | Buscar por ID                     |
| PATCH  | /api/v1/fruits/{id}   | Atualizar campos (parcial)        |
| DELETE | /api/v1/fruits/{id}   | Remover fruta                     |

### Parâmetros de listagem

| Parâmetro   | Padrão | Descrição                        |
|-------------|--------|----------------------------------|
| page        | 1      | Página atual                     |
| page_size   | 20     | Itens por página (máx. 100)      |
| nome        | —      | Filtro parcial, case-insensitive |

### Exemplo de payload (POST / PATCH)

```json
{
  "nome": "Manga",
  "preco": "4.99",
  "quantidade_estoque": 100
}
```

---

## 🔄 Gerenciamento de migrations

```bash
# Aplicar todas as migrations pendentes
alembic upgrade head

# Gerar nova migration após alterar um model
alembic revision --autogenerate -m "descricao da mudanca"

# Reverter uma migration
alembic downgrade -1

# Reverter todas
alembic downgrade base

# Ver histórico
alembic history --verbose

# Ver versão atual do banco
alembic current
```

---

## 🧰 Tecnologias

| Lib               | Versão   | Função                     |
|-------------------|----------|----------------------------|
| fastapi           | 0.115.12 | Framework web              |
| uvicorn           | 0.34.0   | Servidor ASGI              |
| sqlalchemy        | 2.0.40   | ORM                        |
| alembic           | 1.15.2   | Migrations                 |
| pydantic          | 2.11.1   | Validação de dados         |
| pydantic-settings | 2.8.1    | Configuração via .env      |
| psycopg2-binary   | 2.9.10   | Driver PostgreSQL           |
| pytest            | 8.3.5    | Testes                     |
| httpx             | 0.28.1   | Cliente HTTP para testes   |
| ruff              | 0.11.3   | Linter + formatter         |
