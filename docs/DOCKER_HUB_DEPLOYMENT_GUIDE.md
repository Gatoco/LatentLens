# 🐳 Guía Completa: Docker Hub Registry

**Objetivo**: Subir la imagen de LatentLens a Docker Hub para distribución global  
**Fecha**: 21 de Agosto, 2025  

---

## 📋 Pasos Completos

### 1️⃣ **Crear Cuenta en Docker Hub**

1. **Ir a Docker Hub**: https://hub.docker.com/
2. **Registrarse**:
   - Click en "Sign Up"
   - Username: `gatoco` (o el que prefieras)
   - Email: tu email
   - Password: contraseña segura
3. **Verificar email** si es necesario
4. **Anotar tu username** para los siguientes pasos

### 2️⃣ **Login desde Terminal**

```bash
# Hacer login en Docker Hub
docker login

# Te pedirá:
# Username: gatoco
# Password: [tu contraseña]
```

### 3️⃣ **Construir la Imagen (si no existe)**

```bash
# Navegar al directorio del proyecto
cd C:\Users\Gat\Documents\GitHub\LatentLens

# Construir la imagen con un tag específico
docker build -t latentlens:latest .

# Verificar que se creó
docker images | grep latentlens
```

### 4️⃣ **Tagear la Imagen**

```bash
# Formato: docker tag imagen_local usuario/repositorio:tag
docker tag latentlens:latest gatoco/latentlens:latest

# También crear un tag con versión específica
docker tag latentlens:latest gatoco/latentlens:v1.0.0

# Verificar los tags
docker images | grep gatoco/latentlens
```

### 5️⃣ **Subir a Docker Hub**

```bash
# Subir la versión latest
docker push gatoco/latentlens:latest

# Subir la versión específica
docker push gatoco/latentlens:v1.0.0
```

---

## 🔧 Comandos Paso a Paso

### **Script Completo de Deployment**

```bash
# 1. Login en Docker Hub
echo "🔐 Haciendo login en Docker Hub..."
docker login

# 2. Construir imagen
echo "🏗️ Construyendo imagen LatentLens..."
docker build -t latentlens:latest .

# 3. Tagear para Docker Hub
echo "🏷️ Tageando imagen para Docker Hub..."
docker tag latentlens:latest gatoco/latentlens:latest
docker tag latentlens:latest gatoco/latentlens:v1.0.0

# 4. Subir a Docker Hub
echo "🚀 Subiendo a Docker Hub..."
docker push gatoco/latentlens:latest
docker push gatoco/latentlens:v1.0.0

echo "✅ ¡Imagen subida exitosamente!"
```

---

## 📊 Verificación

### **Comprobar en Docker Hub**
1. Ir a https://hub.docker.com/u/gatoco
2. Verificar que aparece `gatoco/latentlens`
3. Ver los tags disponibles (latest, v1.0.0)

### **Probar descarga**
```bash
# Eliminar imagen local (opcional)
docker rmi gatoco/latentlens:latest

# Descargar desde Docker Hub
docker pull gatoco/latentlens:latest

# Ejecutar contenedor
docker run -p 8000:8000 gatoco/latentlens:latest
```

---

## 🎯 Mejores Prácticas

### **1. Nomenclatura de Tags**
```bash
# Usar semantic versioning
gatoco/latentlens:v1.0.0    # Versión específica
gatoco/latentlens:v1.0      # Versión minor
gatoco/latentlens:latest    # Última versión
gatoco/latentlens:dev       # Desarrollo
```

### **2. Optimización de Imagen**
```dockerfile
# En tu Dockerfile, usar multi-stage builds
FROM python:3.10-slim AS builder
# ... build steps

FROM python:3.10-slim AS production
# ... production steps
```

### **3. Documentación en Docker Hub**
- Añadir README.md detallado
- Especificar variables de entorno
- Documentar puertos expuestos
- Incluir ejemplos de uso

---

## 🚀 Automatización con GitHub Actions

### **Workflow para Auto-Deploy**

```yaml
# .github/workflows/docker-deploy.yml
name: 🐳 Docker Hub Deploy

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          gatoco/latentlens:latest
          gatoco/latentlens:${{ github.ref_name }}
```

---

## 🔍 Troubleshooting

### **Error: "access denied"**
```bash
# Verificar que estás loggeado
docker info | grep Username

# Re-login si es necesario
docker logout
docker login
```

### **Error: "repository does not exist"**
```bash
# Verificar formato del tag
# Debe ser: usuario/repositorio:tag
docker tag imagen_local gatoco/latentlens:latest
```

### **Imagen muy grande**
```bash
# Optimizar Dockerfile
FROM python:3.10-slim  # En lugar de python:3.10

# Limpiar cache
RUN pip install --no-cache-dir -r requirements.txt

# Multi-stage build para reducir tamaño
```

---

## 📈 Uso Después del Deploy

### **Para otros usuarios**
```bash
# Descargar y ejecutar tu aplicación
docker pull gatoco/latentlens:latest
docker run -p 8000:8000 gatoco/latentlens:latest

# Acceder a la API
curl http://localhost:8000/docs
```

### **Para deployment en producción**
```bash
# Docker Compose con imagen de Docker Hub
version: '3.8'
services:
  latentlens:
    image: gatoco/latentlens:latest
    ports:
      - "8000:8000"
    environment:
      - ENV=production
```

---

## ✅ Checklist Final

- [ ] ✅ Cuenta Docker Hub creada
- [ ] ✅ Login exitoso desde terminal
- [ ] ✅ Imagen construida localmente
- [ ] ✅ Tags creados correctamente
- [ ] ✅ Push a Docker Hub exitoso
- [ ] ✅ Verificación en hub.docker.com
- [ ] ✅ Test de descarga funcional

---

**🎉 Resultado**: Tu aplicación LatentLens estará disponible globalmente como `docker pull gatoco/latentlens:latest` para cualquier persona en el mundo.
