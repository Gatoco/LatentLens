#!/usr/bin/env python3
"""
DVC Setup and Investigation Script
=================================

Script para investigar e implementar Data Version Control (DVC)
en el proyecto LatentLens.

DVC permite versionar datasets y modelos de manera eficiente,
tracking solo los metadatos en Git y almacenando los archivos
grandes en storage externo.

Uso:
    python scripts/setup_dvc.py [--init] [--add-data] [--add-models]

Autor: Gatoco
Fecha: 21 de Agosto, 2025
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def run_command(cmd: List[str], cwd: str = None) -> Dict[str, Any]:
    """
    Ejecuta un comando y retorna el resultado.
    
    Args:
        cmd: Lista con el comando a ejecutar
        cwd: Directorio de trabajo
        
    Returns:
        Diccionario con resultado del comando
    """
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            check=True
        )
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'stdout': e.stdout,
            'stderr': e.stderr,
            'returncode': e.returncode
        }
    except FileNotFoundError:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command not found',
            'returncode': -1
        }

def check_dvc_installation() -> bool:
    """Verifica si DVC está instalado."""
    print("🔍 Verificando instalación de DVC...")
    
    result = run_command(['dvc', '--version'])
    if result['success']:
        print(f"✅ DVC instalado: {result['stdout'].strip()}")
        return True
    else:
        print("❌ DVC no está instalado")
        return False

def install_dvc():
    """Instala DVC usando pip."""
    print("📦 Instalando DVC...")
    
    result = run_command(['pip', 'install', 'dvc[all]'])
    if result['success']:
        print("✅ DVC instalado exitosamente")
        return True
    else:
        print(f"❌ Error instalando DVC: {result['stderr']}")
        return False

def init_dvc_project():
    """Inicializa DVC en el proyecto."""
    print("🚀 Inicializando DVC en el proyecto...")
    
    # Verificar si ya está inicializado
    if Path('.dvc').exists():
        print("⚠️  DVC ya está inicializado en este proyecto")
        return True
    
    result = run_command(['dvc', 'init'])
    if result['success']:
        print("✅ DVC inicializado exitosamente")
        print("📝 Archivos .dvc/ y .dvcignore creados")
        return True
    else:
        print(f"❌ Error inicializando DVC: {result['stderr']}")
        return False

def setup_remote_storage():
    """Configura almacenamiento remoto para DVC."""
    print("☁️  Configurando almacenamiento remoto...")
    
    # Por defecto, usar almacenamiento local
    remote_path = Path.cwd() / 'dvc_storage'
    remote_path.mkdir(exist_ok=True)
    
    print(f"📂 Usando almacenamiento local: {remote_path}")
    
    # Configurar remote
    result = run_command(['dvc', 'remote', 'add', '-d', 'local_storage', str(remote_path)])
    if result['success']:
        print("✅ Almacenamiento remoto configurado")
        
        # Información sobre otras opciones
        print("\n💡 Opciones de almacenamiento remoto:")
        print("   - AWS S3: dvc remote add -d myremote s3://mybucket/path")
        print("   - Google Cloud: dvc remote add -d myremote gs://mybucket/path")
        print("   - Azure: dvc remote add -d myremote azure://container/path")
        print("   - SSH: dvc remote add -d myremote ssh://example.com/path")
        
        return True
    else:
        print(f"❌ Error configurando almacenamiento: {result['stderr']}")
        return False

def add_data_to_dvc():
    """Añade datasets al tracking de DVC."""
    print("📊 Añadiendo datos a DVC...")
    
    data_paths = [
        'data/ml-25m',
        'data/*.csv'
    ]
    
    added_files = []
    for path in data_paths:
        if Path(path.split('*')[0]).exists():  # Check if base path exists
            print(f"📂 Añadiendo {path} a DVC...")
            result = run_command(['dvc', 'add', path])
            if result['success']:
                print(f"✅ {path} añadido a DVC")
                added_files.append(path)
                
                # Añadir .dvc file a Git
                dvc_file = f"{path}.dvc"
                if Path(dvc_file).exists():
                    git_result = run_command(['git', 'add', dvc_file])
                    if git_result['success']:
                        print(f"📝 {dvc_file} añadido a Git")
            else:
                print(f"❌ Error añadiendo {path}: {result['stderr']}")
    
    if added_files:
        print(f"\n✅ {len(added_files)} archivos/directorios añadidos a DVC")
        print("📝 Recuerda hacer commit de los archivos .dvc:")
        print("   git commit -m 'Add data files to DVC tracking'")
    
    return added_files

def add_models_to_dvc():
    """Añade modelos entrenados al tracking de DVC."""
    print("🤖 Añadiendo modelos a DVC...")
    
    model_paths = [
        'artifacts/models',
        'mlruns/models'
    ]
    
    added_models = []
    for path in model_paths:
        if Path(path).exists():
            print(f"🎯 Añadiendo {path} a DVC...")
            result = run_command(['dvc', 'add', path])
            if result['success']:
                print(f"✅ {path} añadido a DVC")
                added_models.append(path)
                
                # Añadir .dvc file a Git
                dvc_file = f"{path}.dvc"
                if Path(dvc_file).exists():
                    git_result = run_command(['git', 'add', dvc_file])
                    if git_result['success']:
                        print(f"📝 {dvc_file} añadido a Git")
            else:
                print(f"❌ Error añadiendo {path}: {result['stderr']}")
    
    return added_models

def create_dvc_pipeline():
    """Crea un pipeline DVC para reproducibilidad."""
    print("🔄 Creando pipeline DVC...")
    
    pipeline_config = {
        'stages': {
            'prepare_data': {
                'cmd': 'python src/data_loader.py',
                'deps': ['src/data_loader.py', 'data/ml-25m'],
                'outs': ['data/processed']
            },
            'train_model': {
                'cmd': 'python src/train.py --experiment-name dvc_pipeline',
                'deps': ['src/train.py', 'src/models/', 'data/processed'],
                'outs': ['artifacts/models'],
                'metrics': ['artifacts/metrics.json'],
                'params': ['config.yaml']
            },
            'evaluate': {
                'cmd': 'python src/evaluate.py',
                'deps': ['src/evaluate.py', 'artifacts/models'],
                'metrics': ['metrics/evaluation.json']
            }
        }
    }
    
    # Crear archivo dvc.yaml
    try:
        import yaml
        with open('dvc.yaml', 'w') as f:
            yaml.dump(pipeline_config, f, default_flow_style=False)
        print("✅ Pipeline DVC creado en dvc.yaml")
        
        print("\n🔄 Para ejecutar el pipeline completo:")
        print("   dvc repro")
        print("\n📊 Para ver el pipeline:")
        print("   dvc dag")
        
        return True
    except ImportError:
        print("❌ PyYAML no instalado. Instala con: pip install pyyaml")
        return False

def show_dvc_status():
    """Muestra el estado actual de DVC."""
    print("📊 Estado de DVC:")
    
    # Verificar status
    result = run_command(['dvc', 'status'])
    if result['success']:
        if result['stdout'].strip():
            print("📝 Cambios pendientes:")
            print(result['stdout'])
        else:
            print("✅ Todos los archivos están sincronizados")
    
    # Mostrar archivos trackeados
    tracked_files = []
    for dvc_file in Path('.').glob('*.dvc'):
        tracked_files.append(str(dvc_file))
    
    if tracked_files:
        print(f"\n📂 Archivos trackeados por DVC: {len(tracked_files)}")
        for file in tracked_files:
            print(f"   - {file}")
    
    # Mostrar remotes
    result = run_command(['dvc', 'remote', 'list'])
    if result['success'] and result['stdout'].strip():
        print("\n☁️  Almacenamiento remoto configurado:")
        print(result['stdout'])

def create_dvc_documentation():
    """Crea documentación sobre el uso de DVC en el proyecto."""
    doc_content = """# DVC (Data Version Control) en LatentLens

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
"""
    
    with open('docs/DVC_GUIDE.md', 'w') as f:
        f.write(doc_content)
    
    print("✅ Documentación DVC creada en docs/DVC_GUIDE.md")

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="DVC Setup and Investigation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--init', action='store_true', help='Inicializar DVC en el proyecto')
    parser.add_argument('--add-data', action='store_true', help='Añadir datos a DVC tracking')
    parser.add_argument('--add-models', action='store_true', help='Añadir modelos a DVC tracking')
    parser.add_argument('--create-pipeline', action='store_true', help='Crear pipeline DVC')
    parser.add_argument('--status', action='store_true', help='Mostrar estado de DVC')
    parser.add_argument('--docs', action='store_true', help='Crear documentación DVC')
    
    args = parser.parse_args()
    
    print("🔍 DVC Investigation Script para LatentLens")
    print("=" * 50)
    
    # Verificar instalación
    if not check_dvc_installation():
        install_choice = input("¿Instalar DVC? (y/n): ").lower()
        if install_choice == 'y':
            if not install_dvc():
                sys.exit(1)
        else:
            print("❌ DVC es necesario para continuar")
            sys.exit(1)
    
    # Ejecutar acciones según argumentos
    if args.init or not any([args.add_data, args.add_models, args.create_pipeline, args.status, args.docs]):
        init_dvc_project()
        setup_remote_storage()
    
    if args.add_data:
        add_data_to_dvc()
    
    if args.add_models:
        add_models_to_dvc()
    
    if args.create_pipeline:
        create_dvc_pipeline()
    
    if args.status:
        show_dvc_status()
    
    if args.docs:
        Path('docs').mkdir(exist_ok=True)
        create_dvc_documentation()
    
    # Si no se especificaron argumentos, ejecutar flujo completo
    if not any([args.init, args.add_data, args.add_models, args.create_pipeline, args.status, args.docs]):
        print("\n🚀 Ejecutando configuración completa de DVC...")
        
        # Crear documentación
        Path('docs').mkdir(exist_ok=True)
        create_dvc_documentation()
        
        # Mostrar status final
        show_dvc_status()
        
        print("\n✅ DVC configurado exitosamente!")
        print("\n🔄 Próximos pasos:")
        print("1. Añadir datos: python scripts/setup_dvc.py --add-data")
        print("2. Entrenar modelo: python src/train.py")
        print("3. Añadir modelos: python scripts/setup_dvc.py --add-models")
        print("4. Crear pipeline: python scripts/setup_dvc.py --create-pipeline")
        print("5. Ver estado: python scripts/setup_dvc.py --status")

if __name__ == "__main__":
    main()
