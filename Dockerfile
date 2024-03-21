# Usa come base l'immagine ufficiale di Ubuntu
FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

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
    Pillow \
    pdf2image \
    layoutparser[ocr] \
    opencv-python \
    langchain

RUN pip install detectron2 -f \
  https://dl.fbaipublicfiles.com/detectron2/wheels/cu113/torch1.10/index.html

# Imposta il workspace
WORKDIR /container

# Copia il codice sorgente nel container, assicurati di avere il codice sorgente nella stessa cartella di questo Dockerfile
#COPY . /container

# Comando di default per eseguire lo script python (adattalo al nome del tuo script)
CMD ["python3", "app.py"]
