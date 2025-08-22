# Quickstart for Windows PowerShell
Write-Host "1) Pulling Docker image..."
docker pull gatoco/latentlens:latest

Write-Host "2) Running container on http://localhost:8000"
docker run --rm -p 8000:8000 --name latentlens gatoco/latentlens:latest | Out-Null

Write-Host "Waiting 10s for initialization..."
Start-Sleep -Seconds 10

Write-Host "Health:"
try {
    curl.exe http://localhost:8000/health
}
catch {
    Write-Host "Health check failed (the app may still be initializing)."
}

Write-Host "Open docs at http://localhost:8000/docs"
Write-Host "To stop the container: docker rm -f latentlens"
