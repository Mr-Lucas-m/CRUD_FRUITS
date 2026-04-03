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

---

## 🗂️ Estrutura do Projeto

```
├── alembic
│   ├── versions
│   │   └── 79dee2c61eb6_create_fruits_table.py
│   ├── env.py
│   └── script.py.mako
├── app
│   ├── api
│   │   ├── v1
│   │   │   ├── routers
│   │   │   │   ├── __init__.py
│   │   │   │   └── fruit.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── models
│   │   ├── __init__.py
│   │   └── fruit.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── fruit.py
│   ├── services
│   │   ├── __init__.py
│   │   └── fruit_service.py
│   ├── __init__.py
│   └── main.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_fruits.py
├── .env.example
├── .gitignore
├── README.md
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

---

## 🚀 Como rodar

### 1. Clone e configure o ambiente

```bash
git clone <seu-repo>
cd crud_fruits

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com sua DATABASE_URL
```

Exemplo com PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/fruits_db
```

Exemplo com SQLite (dev rápido):
```
DATABASE_URL=sqlite:///./fruits.db
```

### 3. Execute as migrations

```bash
alembic revision --autogenerate -m "create fruits table"
alembic upgrade head
```

### 4. Suba o servidor

```bash
uvicorn app.main:app --reload
```

Acesse:
- Swagger UI → http://localhost:8000/docs
- Health    → http://localhost:8000/health

---

## 🧪 Testes

```bash
  pytest -v
```

Os testes usam SQLite em memória — nenhuma configuração de banco necessária.

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
# Gerar nova migration após alterar um model
alembic revision --autogenerate -m "descricao da mudanca"

# Aplicar
alembic upgrade head

# Reverter uma migration
alembic downgrade -1

# Ver histórico
alembic history --verbose
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
