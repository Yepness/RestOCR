# Usamos Ubuntu 22.04 como base
FROM ubuntu:22.04

# Define variáveis de ambiente
ENV PYTHON_VERSION=3.11
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV DEBIAN_FRONTEND=noninteractive
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata"

# Instala dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    ca-certificates \
    software-properties-common \
    build-essential \
    autoconf \
    automake \
    libtool \
    pkg-config \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Baixa e compila o Tesseract OCR 5.5.0
RUN wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.5.0.tar.gz \
    && tar -xzvf 5.5.0.tar.gz \
    && cd tesseract-5.5.0 \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && ldconfig

# Instala pacotes adicionais e baixa treinamentos de idioma
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    && wget -O /usr/share/tesseract-ocr/5/tessdata/por.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/por.traineddata \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Python 3.11 corretamente
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
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

# Verifica a instalação
RUN tesseract --version && \
    python3 --version && \
    pip list && \
    ls -l /usr/share/tesseract-ocr/5/tessdata/

# Comando para iniciar o servidor
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:443", "--timeout", "0"]
