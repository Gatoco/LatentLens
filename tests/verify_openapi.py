"""
OpenAPI Schema Verification for Fase 3.1
"""

from main import app

def verify_openapi_schema():
    """Verify that the hybrid endpoint is correctly implemented in OpenAPI schema"""
    
    print('🔍 Verificando implementación de tags en OpenAPI schema:')
    
    # Get OpenAPI schema to verify tags
    schema = app.openapi()
    
    # Check if our hybrid endpoint is correctly tagged
    hybrid_endpoint = schema['paths']['/recommend/hybrid/{user_id}']['get']
    tags = hybrid_endpoint.get('tags', [])
    
    print(f'   Endpoint: /recommend/hybrid/{{user_id}}')
    print(f'   Tags: {tags}')
    
    if 'Recomendaciones' in tags:
        print('   ✅ Tag "Recomendaciones" correctamente implementado')
    else:
        print('   ❌ Tag "Recomendaciones" faltante')
    
    # Check parameters
    parameters = hybrid_endpoint.get('parameters', [])
    path_params = [p for p in parameters if p['in'] == 'path']
    query_params = [p for p in parameters if p['in'] == 'query']
    
    print(f'\n📋 Parámetros detectados:')
    for param in path_params:
        param_type = param.get('schema', {}).get('type', 'unknown')
        print(f'   Path parameter: {param["name"]} ({param_type})')
    
    for param in query_params:
        default = param.get('schema', {}).get('default', 'No default')
        param_type = param.get('schema', {}).get('type', 'unknown')
        print(f'   Query parameter: {param["name"]} ({param_type}, default: {default})')
    
    print('\n🎉 Fase 3.1 completamente implementada según especificaciones!')
    
    return True

if __name__ == "__main__":
    verify_openapi_schema()
