import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader


#Configuración de seguridad con API Key
CLAVE = "Almacen-Nosotros"
header = APIKeyHeader(name="X-API-Key")

def verificar(clave: str = Depends(header)):
    if clave != CLAVE:
        raise HTTPException(status_code=401, detail="API key inválida")

#Inicialización de FastAPI con protección global en todos los endpoints
app = FastAPI(
    title="API Almacén",
    dependencies=[Depends(verificar)]
)

#Función para abrir la conexión a sqlite
def obtener_conexion():
    con = sqlite3.connect("productos.bd")
    con.row_factory = sqlite3.Row  
    return con

#Endpoint de bienvenida
@app.get("/")
def bienvenido():
    return {"mensaje": "¡Bienvenido a la Api de nuestra Tienda Online!"}

#Endpoint para ver todos los productos que están en la base de datos
@app.get("/productos")
def listar_productos():
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos")
    filas = cur.fetchall()
    con.close()
    
    return [dict(fila) for fila in filas]

#Endpoint para buscar un producto específico por su ID
@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
    fila = cur.fetchone()
    con.close()
    
    if fila is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return dict(fila)


