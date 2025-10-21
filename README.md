# PRACT1-TCVD
# imdb-scraper

Repositorio para la práctica de creación de un dataset mediante web scraping sobre **IMDb (es)**: https://www.imdb.com/es-es/

## Contenido del repositorio
- `/source` — Código del scraper.  
- `/dataset` — CSV resultante (`imdb_dataset.csv`).  
- `/docs` — Memoria en PDF (`memoria.pdf`) con todos los apartados requeridos.  
- `/figures` — Diagramas y esquemas.  
- `/video` — Enlace al vídeo explicativo (Drive).  
- `LICENSE`, `README.md`, `CITATION.cff`, `.gitignore`.

## Título del dataset
IMDb (es) — Metadata de películas (seed: es-es homepage)

## Resumen rápido
Este proyecto extrae de páginas públicas de IMDb para construir un dataset por película con variables numéricas y categóricas (rating, votos, duración, géneros, directores, reparto principal, sinopsis, países/idiomas cuando están disponibles). El crawler realiza **descubrimiento de enlaces** (p. ej. de listas y páginas seed) y visita páginas `/title/tt...` para extraer los metadatos.

> **IMPORTANTE (legal/ético):** Antes de ejecutar el scraper revisa `source/robots_check.py`, lee y respeta `robots.txt` de IMDb y su TOS.

## Requisitos (ver `source/requirements.txt`)
- Python 3.10+ recomendado
- Selenium (driver Chrome/Chromium ó geckodriver para Firefox)
- BeautifulSoup4, pandas, requests

## Cómo reproducir (ejemplo)
```bash
# clonar repo
git clone https://github.com/JonGarrastatxu/PRACT1-TCVD.git
cd PRACT1-TCVD

# crear entorno (recomendado)
python -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate     # Windows

pip install -r source/requirements.txt

# ejecutar (ejemplo: extraer 100 páginas empezando desde la homepage ES)
python source/scraper.py --out dataset/imdb_dataset.csv --max 100 --seed https://www.imdb.com/es-es/
