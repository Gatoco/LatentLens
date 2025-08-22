# DVC (Data Version Control) en LatentLens

## ¿Qué es DVC?

DVC (Data Version Control) es una herramienta que permite versionar datasets y modelos de machine learning de manera eficiente. Similar a Git, pero optimizado para archivos grandes.

## Ventajas de DVC

- **Versionado de datos**: Track cambios en datasets sin almacenar archivos grandes en Git
- **Reproducibilidad**: Pipelines reproducibles para entrenamiento
- **Colaboración**: Compartir datasets y modelos entre equipos
- **Storage flexible**: Soporte para S3, GCS, Azure, SSH, etc.

## Configuración en este proyecto

### Inicialización
```bash
# Instalar DVC
pip install dvc[all]

# Inicializar en el proyecto
dvc init

# Configurar storage remoto (ejemplo local)
dvc remote add -d local_storage ./dvc_storage
```

### Tracking de datos
```bash
# Añadir dataset al tracking
dvc add data/ml-25m

# Añadir modelos entrenados
dvc add artifacts/models

# Commit archivos .dvc a Git
git add data/ml-25m.dvc artifacts/models.dvc
git commit -m "Add data and models to DVC tracking"
```

### Pipeline de entrenamiento
```bash
# Ejecutar pipeline completo
dvc repro

# Ver dependencias del pipeline
dvc dag

# Comparar métricas entre experiments
dvc metrics diff
```

## Flujo de trabajo con DVC

1. **Desarrollo**:
   ```bash
   # Obtener datos y modelos
   dvc pull
   
   # Hacer cambios al código
   git add .
   git commit -m "Update training script"
   
   # Re-entrenar modelo
   dvc repro
   
   # Subir nuevos artefactos
   dvc push
   ```

2. **Colaboración**:
   ```bash
   # Nuevo miembro del equipo
   git clone <repo>
   dvc pull  # Descarga datos y modelos
   
   # Reproducir experimento
   dvc repro
   ```

3. **Producción**:
   ```bash
   # Obtener modelo específico
   dvc get <repo> artifacts/models/model_v2.pkl
   
   # O clonar con datos
   git clone <repo>
   dvc pull
   ```

## Archivos importantes

- `.dvc/`: Configuración de DVC
- `*.dvc`: Metadatos de archivos trackeados
- `dvc.yaml`: Definición del pipeline
- `dvc.lock`: Lock file del pipeline
- `.dvcignore`: Archivos a ignorar por DVC

## Comandos útiles

```bash
# Estado de archivos DVC
dvc status

# Listar archivos trackeados
dvc list . --dvc-only

# Comparar métricas
dvc metrics show
dvc metrics diff

# Ver pipeline
dvc dag

# Limpiar cache
dvc cache clean

# Verificar integridad
dvc check-ignore <file>
```

## Integración con CI/CD

En GitHub Actions, puedes usar DVC para:

```yaml
- name: Setup DVC
  uses: iterative/setup-dvc@v1

- name: Pull data
  run: dvc pull

- name: Run training pipeline
  run: dvc repro

- name: Push new artifacts
  run: dvc push
```

## Mejores prácticas

1. **Versiona datos y modelos**, no código
2. **Usa .dvcignore** para archivos temporales
3. **Configura remote storage** desde el inicio
4. **Documenta tu pipeline** en dvc.yaml
5. **Usa tags de Git** para versiones importantes
6. **Automatiza con CI/CD** para reproducibilidad

## Troubleshooting

### Error: "file is not tracked by DVC"
```bash
dvc add <file>
git add <file>.dvc
```

### Error: "remote storage not accessible"
```bash
dvc remote list
dvc remote modify <remote> <property> <value>
```

### Error: "pipeline out of date"
```bash
dvc repro --force
```

## Más información

- [Documentación oficial](https://dvc.org/doc)
- [Tutorial interactivo](https://dvc.org/doc/tutorial)
- [Casos de uso](https://dvc.org/doc/use-cases)
