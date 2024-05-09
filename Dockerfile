ARG PORT=443
FROM cypress/browsers:latest
RUN apt-get install python3 -y
RUN echo $(python3 -m site --user-base)
COPY requirements.txt .
ENV PATH /home/root/.local/bin:${PATH}
RUN apt-get update && apt-get install -y python3-pip && pip install -r requirements.txt
COPY . .
RUN pip install --ignore-installed uvicorn==0.20.0
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-por
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 0