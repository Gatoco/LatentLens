#!/bin/bash
# Docker Hub Deployment Script para LatentLens
# ============================================
# 
# Uso: ./scripts/deploy_docker.sh [version]
# Ejemplo: ./scripts/deploy_docker.sh v1.0.0

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
DOCKER_USERNAME="gatoco"  # Cambiar por tu username
IMAGE_NAME="latentlens"
DOCKERFILE_PATH="."

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar argumentos
VERSION=${1:-"latest"}
if [[ $VERSION != "latest" && ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    warning "Versión '$VERSION' no sigue semantic versioning (vX.Y.Z)"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🐳 Docker Hub Deployment Script"
echo "================================"
echo "📦 Imagen: $DOCKER_USERNAME/$IMAGE_NAME"
echo "🏷️  Tag: $VERSION"
echo "📁 Dockerfile: $DOCKERFILE_PATH"
echo

# Paso 1: Verificar Docker
log "Verificando Docker..."
if ! docker --version &> /dev/null; then
    error "Docker no está instalado o no está en PATH"
fi
success "Docker disponible: $(docker --version)"

# Paso 2: Verificar login en Docker Hub
log "Verificando login en Docker Hub..."
if ! docker info | grep -q "Username"; then
    warning "No estás loggeado en Docker Hub"
    log "Ejecutando docker login..."
    docker login || error "Login fallido"
fi
success "Login verificado en Docker Hub"

# Paso 3: Construir imagen
log "Construyendo imagen Docker..."
LOCAL_TAG="$IMAGE_NAME:$VERSION"
docker build -t "$LOCAL_TAG" "$DOCKERFILE_PATH" || error "Build falló"
success "Imagen construida: $LOCAL_TAG"

# Paso 4: Tagear para Docker Hub
log "Tageando imagen para Docker Hub..."
REMOTE_TAG="$DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
docker tag "$LOCAL_TAG" "$REMOTE_TAG" || error "Tag falló"

# Si no es latest, también crear tag latest
if [[ $VERSION != "latest" ]]; then
    LATEST_TAG="$DOCKER_USERNAME/$IMAGE_NAME:latest"
    docker tag "$LOCAL_TAG" "$LATEST_TAG"
    log "También tageado como: $LATEST_TAG"
fi

success "Tags creados exitosamente"

# Paso 5: Mostrar información de la imagen
log "Información de la imagen:"
docker images | grep "$DOCKER_USERNAME/$IMAGE_NAME" || true

# Paso 6: Confirmar push
echo
echo "🚀 Listo para subir a Docker Hub:"
echo "   - $REMOTE_TAG"
if [[ $VERSION != "latest" ]]; then
    echo "   - $LATEST_TAG"
fi
echo
read -p "¿Proceder con el push? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    warning "Push cancelado por el usuario"
    exit 0
fi

# Paso 7: Push a Docker Hub
log "Subiendo imagen a Docker Hub..."
docker push "$REMOTE_TAG" || error "Push falló para $REMOTE_TAG"
success "Subida exitosa: $REMOTE_TAG"

if [[ $VERSION != "latest" ]]; then
    docker push "$LATEST_TAG" || error "Push falló para $LATEST_TAG"
    success "Subida exitosa: $LATEST_TAG"
fi

# Paso 8: Verificación
log "Verificando subida..."
sleep 2
echo
echo "✅ Deployment completado exitosamente!"
echo "🔗 Tu imagen está disponible en:"
echo "   https://hub.docker.com/r/$DOCKER_USERNAME/$IMAGE_NAME"
echo
echo "📥 Otros usuarios pueden usar tu imagen con:"
echo "   docker pull $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
echo "   docker run -p 8000:8000 $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
echo

# Paso 9: Cleanup opcional
read -p "¿Eliminar imágenes locales para ahorrar espacio? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Limpiando imágenes locales..."
    docker rmi "$LOCAL_TAG" 2>/dev/null || true
    docker rmi "$REMOTE_TAG" 2>/dev/null || true
    if [[ $VERSION != "latest" ]]; then
        docker rmi "$LATEST_TAG" 2>/dev/null || true
    fi
    success "Limpieza completada"
fi

echo "🎉 ¡Proceso completado!"
