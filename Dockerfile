# Usamos Ubuntu 22.04 como base para ter acesso ao PPA do Tesseract mais recente
FROM ubuntu:22.04

# Define variáveis de ambiente
ENV PYTHON_VERSION=3.11
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Instala dependências do sistema e configura Python 3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    wget \
    && add-apt-repository ppa:alex-p/tesseract-ocr -y \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --set python3 /usr/bin/python3.11

# Cria e ativa o ambiente virtual
RUN python3 -m venv $VIRTUAL_ENV

# Copia os requisitos primeiro para aproveitar o cache de camadas
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uvicorn==0.20.0

# Copia o restante da aplicação
COPY . .

# Verifica a versão do Tesseract (opcional, para debug)
RUN tesseract --version

# Comando para iniciar o servidor
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:443", "--timeout", "0"]