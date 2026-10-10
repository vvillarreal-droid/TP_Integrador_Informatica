from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

# Configuración de seguridad con API Key
CLAVE = "Almacen-Nosotros"
header = APIKeyHeader(name="X-API-Key")

def verificar_clave(clave: str = Depends(header)):
    if clave != CLAVE:
        raise HTTPException(status_code=401, detail="API key inválida")
