# MLflow Cleanup Guide

**Proyecto:** LatentLens
**Fecha:** 22 de Agosto, 2025

### Objetivo
Mantener el entorno de MLflow limpio y eficiente, eliminando runs, modelos y artefactos obsoletos.

### Pasos para Limpieza
1. Acceder a la UI de MLflow (`localhost:5000`)
2. Identificar runs y modelos antiguos o fallidos
3. Eliminar desde la interfaz o usando scripts:
	```bash
	mlflow gc --backend-store-uri ./mlruns
	```
4. Limpiar artefactos manualmente si es necesario (`mlruns/`)

### Recomendaciones
- Realizar limpieza periódica
- Respaldar antes de eliminar runs importantes
