FROM python:3.12-slim

WORKDIR /app

# Dependências de sistema (gcc para compilar bcrypt, libpq para psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python antes de copiar o código (cache de layers)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Garante que o entrypoint não tenha CRLF (problema de linha no Windows)
RUN sed -i 's/\r//' entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
