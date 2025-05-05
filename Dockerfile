# Usamos a imagem base slim do Python 3.11
FROM python:3.11-slim

# Instala dependências necessárias para rodar AppImage
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1-mesa-glx \
    wget \
    ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Baixa e configura Tesseract OCR 5.5.0 AppImage
RUN wget -O /usr/local/bin/tesseract https://github.com/AlexanderP/tesseract-appimage/releases/download/v5.5.0/tesseract-5.5.0-x86_64.AppImage \
    && chmod +x /usr/local/bin/tesseract

# Verifica se Tesseract foi instalado corretamente
RUN tesseract -v

# Cria e ativa o ambiente virtual
RUN python3 -m venv /app/venv

# Adiciona o ambiente virtual ao PATH
ENV PATH="/app/venv/bin:$PATH"

# Copia os requisitos primeiro para otimizar cache
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn==0.20.0

# Copia o restante da aplicação
COPY . .

# Comando para iniciar o servidor
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:443", "--timeout", "0"]
