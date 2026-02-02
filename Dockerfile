# Bruk en offisiell Python-image som base
FROM python:3.12-slim

# Sett arbeidskatalog
WORKDIR /app

# Installer systemavhengigheter (LaTeX og verktøy for PDF-generering)
# Vi bruker texlive-latex-extra og texlive-fonts-recommended for å holde størrelsen nede, 
# men nok til å dekke de fleste behov.
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-lang-norwegian \
    texlive-pictures \
    texlive-science \
    ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopier requirements først for å utnytte Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopier resten av applikasjonen
COPY . .

# Opprett output-mappe og sett rettigheter
RUN mkdir -p output && chmod 777 output

# Eksponer porten Streamlit bruker
EXPOSE 8501

# Start-kommando
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
