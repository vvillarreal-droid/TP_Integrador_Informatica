import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from crud import obtener_conexion, tabla_productos, tabla_pedidos, tabla_items_pedidos, listar_productos, listar_categorias, pedido_compra, reporte_ventas
from security import verificar_clave



#Inicialización de FastAPI con protección global en todos los endpoints
app = FastAPI(
    title="API Almacén",
    dependencies=[Depends(verificar_clave)]
)


#Endpoint de bienvenida
@app.get("/")
def bienvenido():
    return {"mensaje": "¡Bienvenido a la Api de nuestra Tienda Online!"}

#Endpoint para ver todos los productos que están en la base de datos
@app.get("/productos")
def list_products():
    products = listar_productos()
    return products

#Endpoint para hacer las compras
@app.get("/pedido")
def purchase_order():
    order = pedido_compra()
    return order

#Endpoint para hacer el informe de ventas
@app.get("/reporte_ventas")
def report_sells():
    report = reporte_ventas()
    return report

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
