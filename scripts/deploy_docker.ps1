# Docker Hub Deployment Script para LatentLens (PowerShell)
# =========================================================
# 
# Uso: .\scripts\deploy_docker.ps1 [-Version "v1.0.0"]
# Ejemplo: .\scripts\deploy_docker.ps1 -Version "v1.0.0"

param(
    [string]$Version = "latest",
    [string]$Username = "gatoco",
    [string]$ImageName = "latentlens",
    [string]$DockerfilePath = "."
)

# Función para logging con colores
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    switch ($Level) {
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "SUCCESS" { Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green }
        "WARNING" { Write-Host "[$timestamp] [WARNING] $Message" -ForegroundColor Yellow }
        default { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor Blue }
    }
}

function Write-Error-Exit {
    param([string]$Message)
    Write-Log $Message "ERROR"
    exit 1
}

# Validar versión
if ($Version -ne "latest" -and $Version -notmatch "^v\d+\.\d+\.\d+$") {
    Write-Log "Versión '$Version' no sigue semantic versioning (vX.Y.Z)" "WARNING"
    $continue = Read-Host "¿Continuar? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

Write-Host "🐳 Docker Hub Deployment Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📦 Imagen: $Username/$ImageName" -ForegroundColor White
Write-Host "🏷️  Tag: $Version" -ForegroundColor White
Write-Host "📁 Dockerfile: $DockerfilePath" -ForegroundColor White
Write-Host ""

# Paso 1: Verificar Docker
Write-Log "Verificando Docker..."
try {
    $dockerVersion = docker --version
    Write-Log "Docker disponible: $dockerVersion" "SUCCESS"
}
catch {
    Write-Error-Exit "Docker no está instalado o no está en PATH"
}

# Paso 2: Verificar login en Docker Hub
Write-Log "Verificando login en Docker Hub..."
$dockerInfo = docker info 2>$null | Select-String "Username"
if (-not $dockerInfo) {
    Write-Log "No estás loggeado en Docker Hub" "WARNING"
    Write-Log "Ejecutando docker login..."
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Exit "Login falló"
    }
}
Write-Log "Login verificado en Docker Hub" "SUCCESS"

# Paso 3: Construir imagen
Write-Log "Construyendo imagen Docker..."
$localTag = "$ImageName`:$Version"
docker build -t $localTag $DockerfilePath
if ($LASTEXITCODE -ne 0) {
    Write-Error-Exit "Build falló"
}
Write-Log "Imagen construida: $localTag" "SUCCESS"

# Paso 4: Tagear para Docker Hub
Write-Log "Tageando imagen para Docker Hub..."
$remoteTag = "$Username/$ImageName`:$Version"
docker tag $localTag $remoteTag
if ($LASTEXITCODE -ne 0) {
    Write-Error-Exit "Tag falló"
}

# Si no es latest, también crear tag latest
if ($Version -ne "latest") {
    $latestTag = "$Username/$ImageName`:latest"
    docker tag $localTag $latestTag
    Write-Log "También tageado como: $latestTag"
}

Write-Log "Tags creados exitosamente" "SUCCESS"

# Paso 5: Mostrar información de la imagen
Write-Log "Información de la imagen:"
docker images | Where-Object { $_ -match "$Username/$ImageName" }

# Paso 6: Confirmar push
Write-Host ""
Write-Host "🚀 Listo para subir a Docker Hub:" -ForegroundColor Green
Write-Host "   - $remoteTag" -ForegroundColor White
if ($Version -ne "latest") {
    Write-Host "   - $latestTag" -ForegroundColor White
}
Write-Host ""

$proceed = Read-Host "¿Proceder con el push? (y/N)"
if ($proceed -ne "y" -and $proceed -ne "Y") {
    Write-Log "Push cancelado por el usuario" "WARNING"
    exit 0
}

# Paso 7: Push a Docker Hub
Write-Log "Subiendo imagen a Docker Hub..."
docker push $remoteTag
if ($LASTEXITCODE -ne 0) {
    Write-Error-Exit "Push falló para $remoteTag"
}
Write-Log "Subida exitosa: $remoteTag" "SUCCESS"

if ($Version -ne "latest") {
    docker push $latestTag
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Exit "Push falló para $latestTag"
    }
    Write-Log "Subida exitosa: $latestTag" "SUCCESS"
}

# Paso 8: Verificación
Write-Log "Verificando subida..."
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Deployment completado exitosamente!" -ForegroundColor Green
Write-Host "🔗 Tu imagen está disponible en:" -ForegroundColor Cyan
Write-Host "   https://hub.docker.com/r/$Username/$ImageName" -ForegroundColor White
Write-Host ""
Write-Host "📥 Otros usuarios pueden usar tu imagen con:" -ForegroundColor Cyan
Write-Host "   docker pull $Username/$ImageName`:$Version" -ForegroundColor White
Write-Host "   docker run -p 8000:8000 $Username/$ImageName`:$Version" -ForegroundColor White
Write-Host ""

# Paso 9: Cleanup opcional
$cleanup = Read-Host "¿Eliminar imágenes locales para ahorrar espacio? (y/N)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Write-Log "Limpiando imágenes locales..."
    try {
        docker rmi $localTag 2>$null
        docker rmi $remoteTag 2>$null
        if ($Version -ne "latest") {
            docker rmi $latestTag 2>$null
        }
        Write-Log "Limpieza completada" "SUCCESS"
    }
    catch {
        Write-Log "Algunas imágenes no pudieron eliminarse (pueden estar en uso)" "WARNING"
    }
}

Write-Host "🎉 ¡Proceso completado!" -ForegroundColor Green
