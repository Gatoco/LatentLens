# Deployment Guide

**Proyecto:** LatentLens
**Fecha:** 22 de Agosto, 2025

### Requisitos Previos
- Docker instalado
- Acceso a Docker Hub (opcional)
- Python 3.10+ (para desarrollo local)

### Despliegue Rápido con Docker
```bash
docker pull gatoco/latentlens:latest
docker run --rm -p 8000:8000 --name latentlens gatoco/latentlens:latest
```

### Despliegue Local (Desarrolladores)
```bash
git clone https://github.com/Gatoco/LatentLens.git
cd LatentLens
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Notas
- Configurar variables de entorno según sea necesario.
- Consultar la documentación en docs/ para detalles avanzados.
