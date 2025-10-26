# PRACT1-TCVD
# Steamdb-scraper

Repositorio para la práctica de creación de un dataset mediante web scraping sobre **Steamdb**: https://steamdb.info

## Integrantes del grupo
Jon Garrastatxu Fernandez<br>
Víctor Ruiz-Clavijo Jimeno

## Contenido del repositorio
- `/source` — Código del scraper.  
- `/dataset` — CSV resultante (`imdb_dataset.csv`).   
- `LICENSE`, `README.md`, `.gitignore`.

## Título del dataset
Steam Game Metadata with Review Scores Extracted from SteamDB

## Resumen rápido
Este proyecto extrae datos de juegos de Steam de la página no oficial steamdb.info para construir un dataset variables numéricas y categóricas ('title', app_id, app_type, developer, publisher, platforms, technologies,etc). El scraper realiza **descubrimiento de enlaces** y visita páginas `https://steamdb.info/app/href/charts` para extraer los metadatos usando selenium y evitando cloudfare simulando acciones del usuario ejecutor del código.

## Requisitos (ver `source/requirements.txt`)
- Python 3.12+
- Navegador Chrome

## Cómo reproducir (ejemplo)
```bash
# clonar repo
git clone https://github.com/JonGarrastatxu/PRACT1-TCVD.git
cd PRACT1-TCVD

# crear entorno (recomendado)
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r source/requirements.txt

# ejecutar (Overwrite!!!)
python source/main.py
# parameters
--skip # Skip hrefs scraping (Use steam_hrefs.csv)
--update # Update existing href list and dataset
```

## DOI de Zenodo del dataset generado
