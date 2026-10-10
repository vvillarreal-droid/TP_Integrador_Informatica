import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from crud import funcion_crud_1, funcion_crud_2, funcion_crud_3

#Configuración de seguridad con API Key -> IRIA A SECURITY
CLAVE = "Almacen-Nosotros"
header = APIKeyHeader(name="X-API-Key")

def verificar(clave: str = Depends(header)): # -> IRIA A SECURITY
    if clave != CLAVE:
        raise HTTPException(status_code=401, detail="API key inválida")

#Inicialización de FastAPI con protección global en todos los endpoints
app = FastAPI(
    title="API Almacén",
    dependencies=[Depends(verificar)] #  ->  importar desde security
)

#Función para abrir la conexión a sqlite -> iria a db
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
listar_productos()


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


@app.get("/endpoint_1")
def endpoint_1(producto_id: int):
    data = funcion_crud_1()
    return data 

@app.get("/endpoint_2")
def endpoint_2(producto_id: int):
    data = funcion_crud_2()
    return data 

@app.get("/endpoint_3")
def endpoint_3(producto_id: int):
    data = funcion_crud_3()
    return data 
