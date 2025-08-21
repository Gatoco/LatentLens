#!/usr/bin/env python3
"""
Análisis inteligente de archivos vacíos para determinar cuáles deben tener contenido
o cuáles se pueden eliminar
"""

import os
from pathlib import Path

def analyze_empty_files():
    """Analiza archivos vacíos y determina qué hacer con cada uno"""
    
    # Obtener archivos vacíos del proyecto (excluyendo venv)
    project_root = Path('.')
    empty_files = []
    
    for file_path in project_root.rglob('*'):
        if (file_path.is_file() and 
            file_path.stat().st_size == 0 and 
            'venv' not in file_path.parts):
            empty_files.append(file_path)
    
    # Categorizar archivos
    analysis = {
        'mantener_vacios': [],      # Archivos que deben estar vacíos intencionalmente
        'completar_contenido': [],  # Archivos que necesitan contenido
        'eliminar': [],             # Archivos que no son necesarios
        'revisar': []              # Archivos que necesitan revisión manual
    }
    
    for file_path in empty_files:
        file_str = str(file_path)
        file_name = file_path.name
        
        # Archivos que deben mantenerse vacíos
        if (file_name in ['.gitkeep', '__init__.py', 'py.typed'] or
            file_name.endswith('.typed')):
            analysis['mantener_vacios'].append(file_path)
            
        # Archivos de tests que necesitan contenido
        elif (file_path.parts[0] == 'tests' and 
              file_name.startswith('test_') and 
              file_name.endswith('.py')):
            analysis['completar_contenido'].append(file_path)
            
        # Scripts que necesitan contenido
        elif (file_path.parts[0] == 'scripts' and 
              file_name.endswith('.py')):
            analysis['completar_contenido'].append(file_path)
            
        # Archivos de documentación que necesitan contenido
        elif (file_name.endswith('.md') and 
              any(keyword in file_name.upper() for keyword in 
                  ['SUMMARY', 'REPORT', 'GUIDE', 'STATUS', 'PLAN'])):
            analysis['completar_contenido'].append(file_path)
            
        # Archivos temporales o duplicados que se pueden eliminar
        elif (file_name.startswith('test_') and file_path.parent == project_root):
            analysis['eliminar'].append(file_path)
            
        # Archivos Python en la raíz que parecen temporales
        elif (file_path.parent == project_root and 
              file_name.endswith('.py') and
              any(keyword in file_name for keyword in 
                  ['test_', 'quick_', 'validate_', 'mlflow_', 'comprehensive_'])):
            analysis['eliminar'].append(file_path)
            
        # Documentos de trabajo que se pueden eliminar
        elif (file_path.parent == project_root and 
              file_name.endswith('.md') and
              file_name not in ['README.md', 'FINAL_EXECUTIVE_SUMMARY.md']):
            analysis['eliminar'].append(file_path)
            
        # El resto necesita revisión
        else:
            analysis['revisar'].append(file_path)
    
    return analysis

def print_analysis(analysis):
    """Imprime el análisis de archivos vacíos"""
    
    print("🔍 ANÁLISIS DE ARCHIVOS VACÍOS")
    print("=" * 60)
    
    for category, files in analysis.items():
        if not files:
            continue
            
        if category == 'mantener_vacios':
            print(f"\n✅ MANTENER VACÍOS ({len(files)} archivos):")
            print("   (Archivos que deben estar vacíos intencionalmente)")
            
        elif category == 'completar_contenido':
            print(f"\n📝 COMPLETAR CONTENIDO ({len(files)} archivos):")
            print("   (Archivos que necesitan implementación)")
            
        elif category == 'eliminar':
            print(f"\n🗑️  ELIMINAR ({len(files)} archivos):")
            print("   (Archivos temporales o duplicados)")
            
        elif category == 'revisar':
            print(f"\n❓ REVISAR MANUALMENTE ({len(files)} archivos):")
            print("   (Requieren análisis específico)")
        
        for file_path in files:
            print(f"   - {file_path}")

def main():
    analysis = analyze_empty_files()
    print_analysis(analysis)
    
    # Preguntar sobre eliminación de archivos
    files_to_delete = analysis['eliminar']
    if files_to_delete:
        print(f"\n⚠️  ¿Eliminar los {len(files_to_delete)} archivos marcados para eliminación? (y/N): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes', 'sí', 's']:
            deleted = 0
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    print(f"✅ Eliminado: {file_path}")
                    deleted += 1
                except Exception as e:
                    print(f"❌ Error eliminando {file_path}: {e}")
            
            print(f"\n🎯 ELIMINADOS: {deleted} archivos")
        else:
            print("❌ Eliminación cancelada")
    
    # Mostrar resumen de acciones recomendadas
    print(f"\n📋 RESUMEN DE ACCIONES RECOMENDADAS:")
    print(f"✅ Mantener vacíos: {len(analysis['mantener_vacios'])}")
    print(f"📝 Completar contenido: {len(analysis['completar_contenido'])}")
    print(f"🗑️  Eliminar: {len(analysis['eliminar'])}")
    print(f"❓ Revisar: {len(analysis['revisar'])}")

if __name__ == "__main__":
    main()
