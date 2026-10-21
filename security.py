import os
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

# Configuración de seguridad con API Key
CLAVE = os.environ.get("API_KEY")

# auto_error=False: si falta el header, no corta solo; lo manejamos nosotros
# para devolver siempre 401 (como pide la consigna).
header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verificar_clave(clave: str = Depends(header)):
    # Si la variable de entorno no está cargada, CLAVE es None.
    # Sin este chequeo, un pedido SIN header (clave=None) pasaría,
    # porque None == None.
    if CLAVE is None or clave != CLAVE:
        raise HTTPException(status_code=401, detail="API key inválida")
    return clave
