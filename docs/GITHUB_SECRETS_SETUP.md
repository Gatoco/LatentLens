# 🔐 GitHub Secrets Configuration Guide

## Required Secrets for LatentLens CI/CD Pipeline

Para configurar el despliegue automático a Docker Hub, necesitas añadir los siguientes secrets en tu repositorio de GitHub:

### 1. Navegación a GitHub Secrets
```
GitHub Repository → Settings → Secrets and variables → Actions → New repository secret
```

### 2. Secrets Requeridos

#### `DOCKER_USERNAME`
- **Valor**: `gatoco` (tu nombre de usuario de Docker Hub)
- **Descripción**: Nombre de usuario para autenticación en Docker Hub

#### `DOCKER_PASSWORD`
- **Valor**: `[TU_DOCKER_HUB_TOKEN]`
- **Descripción**: Token de acceso personal de Docker Hub (recomendado) o contraseña
- **⚠️ Importante**: Usa Access Token en lugar de contraseña por seguridad

### 3. Cómo crear Docker Hub Access Token

```bash
# 1. Ve a Docker Hub → Account Settings → Security
# 2. Click "New Access Token"
# 3. Nombre: "LatentLens-GitHub-Actions"
# 4. Permisos: Read, Write, Delete
# 5. Copia el token generado
```

### 4. Variables de Entorno Adicionales (Opcionales)

#### Para MLflow Tracking:
```
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=latentlens-production
```

#### Para Base de Datos:
```
DATABASE_URL=postgresql://user:password@localhost:5432/latentlens
REDIS_URL=redis://localhost:6379
```

### 5. Verificación de Secrets

Una vez configurados los secrets, el workflow automáticamente:
- ✅ Construirá la imagen Docker
- ✅ Ejecutará tests y linting
- ✅ Subirá la imagen a Docker Hub con tags automáticos
- ✅ Generará tags semánticos (latest, v1.0.0, etc.)

### 6. Comando para Deploy Manual (Backup)

Si necesitas hacer deploy manual:
```bash
# Usando los scripts de deploy
./scripts/deploy_docker.ps1

# O comando directo
docker build -t gatoco/latentlens:latest .
docker push gatoco/latentlens:latest
```

### 7. Tags Automáticos Generados

El workflow generará automáticamente estos tags:
- `gatoco/latentlens:latest` (rama main)
- `gatoco/latentlens:main` (rama main)  
- `gatoco/latentlens:v1.0.0` (releases)
- `gatoco/latentlens:1.0` (versión mayor.menor)

### 8. Monitoreo del Deploy

Verifica el estado del deploy en:
- GitHub Actions: `https://github.com/[TU_USUARIO]/LatentLens/actions`
- Docker Hub: `https://hub.docker.com/r/gatoco/latentlens`

### 9. Uso de la Imagen Desplegada

```bash
# Pull desde Docker Hub
docker pull gatoco/latentlens:latest

# Run la aplicación
docker run -p 8000:8000 gatoco/latentlens:latest

# Acceder a la API
curl http://localhost:8000/docs
```

---

## 🔄 Workflow Trigger Events

El pipeline se ejecuta automáticamente en:
- ✅ Push a rama `main` o `master`
- ✅ Pull Request a rama `main` o `master`  
- ✅ Creación de Release/Tag
- ✅ Trigger manual desde GitHub Actions

---

## 🎯 Estado Actual

- [x] Docker Hub account configurado (gatoco)
- [x] Imagen local construida y taggeada
- [x] Workflow de CI/CD creado
- [ ] GitHub Secrets configurados ← **PRÓXIMO PASO**
- [ ] Primer deploy automático ejecutado
