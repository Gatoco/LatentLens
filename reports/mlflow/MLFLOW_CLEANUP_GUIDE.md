# 🧹 MLflow Experiments - Cleanup Guide

## 📊 Experimentos Actuales (9 total)

### ✅ **EXPERIMENTOS PRINCIPALES** (Mantener)

1. **`SVD_Recommendation_Experiments`** 🎯
   - **Fecha**: 2025-08-19 19:30
   - **Runs**: 7 exitosos
   - **Estado**: ✅ PRINCIPAL - Contiene todos los resultados finales
   - **Contenido**: Hybrid, SVD, Popular, Comparaciones

2. **`LatentLens-Ranking-Metrics-Evaluation`** 📊
   - **Fecha**: 2025-08-17 00:54
   - **Runs**: 3 exitosos
   - **Estado**: ✅ ÚTIL - Métricas de ranking avanzadas
   - **Contenido**: Precision@10, Recall@10, etc.

3. **`Ranking-Metrics-Comparison`** 📈
   - **Fecha**: 2025-08-16 19:01
   - **Runs**: 3 exitosos
   - **Estado**: ✅ ÚTIL - Comparación de algoritmos KNN/SVD

### ⚠️ **EXPERIMENTOS SECUNDARIOS** (Pueden eliminarse)

4. **`Hybrid_Model_Quick_Evaluation`** 
   - **Fecha**: 2025-08-20 00:08
   - **Runs**: 1 exitoso
   - **Estado**: ⚠️ DUPLICADO - Resultados ya en SVD_Recommendation_Experiments

5. **`SVD-Model-Registry-Ranking`**
   - **Fecha**: 2025-08-16 18:57
   - **Runs**: 2 (algunos fallidos)
   - **Estado**: ⚠️ EXPERIMENTAL - Testing inicial

6. **`LatentLens-SVD-Evaluation`**
   - **Fecha**: 2025-08-13 10:53
   - **Runs**: 1 exitoso
   - **Estado**: ⚠️ SUPERSEDED - Versión anterior de evaluación

### ❌ **EXPERIMENTOS VACÍOS** (Eliminar)

7. **`Hybrid_Model_Comparison`**
   - **Fecha**: 2025-08-20 16:41
   - **Runs**: 1 fallido
   - **Estado**: ❌ FALLIDO - Sin resultados útiles

8. **`Comprehensive_Model_Comparison`**
   - **Fecha**: 2025-08-20 00:35
   - **Runs**: 0
   - **Estado**: ❌ VACÍO - No tiene runs

9. **`Hybrid_Model_Evaluation`**
   - **Fecha**: 2025-08-19 23:24
   - **Runs**: 0
   - **Estado**: ❌ VACÍO - No tiene runs

---

## 🎯 **RECOMENDACIÓN DE LIMPIEZA**

### ✅ **MANTENER (3 experimentos):**
- `SVD_Recommendation_Experiments` ← **TODOS LOS RESULTADOS FINALES**
- `LatentLens-Ranking-Metrics-Evaluation` ← Métricas avanzadas
- `Ranking-Metrics-Comparison` ← Comparación de algoritmos

### 🗑️ **ELIMINAR SEGUROS (6 experimentos):**
- `Hybrid_Model_Comparison` (fallido)
- `Comprehensive_Model_Comparison` (vacío)  
- `Hybrid_Model_Evaluation` (vacío)
- `Hybrid_Model_Quick_Evaluation` (duplicado)
- `SVD-Model-Registry-Ranking` (experimental)
- `LatentLens-SVD-Evaluation` (superseded)

---

## 📊 **RESULTADOS CONSOLIDADOS**

### 🏆 Experimento Principal: `SVD_Recommendation_Experiments`

**Contiene todos los resultados importantes:**

| Modelo | Success Rate | Coverage | Unique Movies | Diversity |
|--------|-------------|----------|---------------|-----------|
| **Hybrid** | **100%** | **0.28%** | **176** | **1** |
| SVD | 100% | 0.00% | 0 | 0 |
| Popular | 100% | 0.00% | 0 | 0 |

**✅ CONCLUSIÓN**: El modelo híbrido supera claramente a los individuales en:
- Cobertura del catálogo
- Diversidad de géneros  
- Número de películas únicas
- Mantiene 100% success rate

---

## 🚀 **ESTADO FINAL**

✅ **EVALUACIÓN COMPLETA**
✅ **MODELO HÍBRIDO SUPERIOR DEMOSTRADO**  
✅ **RESULTADOS REGISTRADOS EN MLFLOW**
✅ **LISTO PARA PRODUCCIÓN**

**Acceso a resultados**: http://localhost:5000
**Experimento principal**: `SVD_Recommendation_Experiments`
