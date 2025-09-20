FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala todas as dependências de uma vez
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte e configs
COPY ./src /app/src
COPY alembic.ini /app/alembic.ini
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Configura variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OPENAI_API_KEY=${OPENAI_API_KEY}


# Usa o entrypoint para iniciar o container
ENTRYPOINT ["/entrypoint.sh"]