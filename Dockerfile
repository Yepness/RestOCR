# Defina a porta padrão
ARG PORT=443

# Use uma imagem base otimizada para Python
FROM python:3.11-slim

# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-por \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copie os requisitos para a imagem
COPY requirements.txt .

# Instale as dependências do Python
RUN python3 -m venv /app/venv \
    && . /app/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn==0.20.0

# Adicione o ambiente virtual ao PATH
ENV PATH="/app/venv/bin:$PATH"

# Copie o restante do código
COPY . .

# Comando para iniciar o servidor
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:443", "--timeout", "0"]
