# Usa come base l'immagine ufficiale di Ubuntu
#FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime
FROM pytorch/pytorch:latest

# Imposta variabili di ambiente per evitare domande durante l'installazione
ARG DEBIAN_FRONTEND=noninteractive

# Aggiorna i pacchetti di sistema e installa dipendenze Python e altre utility necessarie
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    libgl1-mesa-glx \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Aggiorna pip e installa pacchetti Python richiesti
RUN pip3 install --upgrade pip && \
    pip3 install \
    streamlit \
    lxml \
    Pillow \
    pdf2image \
    pymupdf \
    layoutparser[ocr] \
    opencv-python \
    python-dotenv \
    openai \
    langchain \
    langchain-community \
    langchain-core \
    langchain-openai

RUN python -m pip install \
    'git+https://github.com/facebookresearch/detectron2.git'

# Imposta il workspace
WORKDIR /container

# Copia il codice sorgente nel container, assicurati di avere il codice sorgente nella stessa cartella di questo Dockerfile
#COPY . /container

# Comando di default per eseguire lo script python (adattalo al nome del tuo script)
CMD ["python3", "app.py"]
