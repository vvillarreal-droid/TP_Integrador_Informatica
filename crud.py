import sqlite3
from datetime import datetime
from fastapi import HTTPException

def obtener_conexion():
    #Función para activar cada función conectandola con SQLite3 y Cursor
    #sin la necesidad de conectarse en cada función
    con = sqlite3.connect("productos.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur

def tabla_productos():
    #Función para hacer las tablas de los productos
    con, cur = obtener_conexion()
    cur.execute("""CREATE TABLE IF NOT EXISTS productos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL); """)

    return 

def tabla_pedidos():
    #Función para hacer las tablas de los pedidos
    con, cur = obtener_conexion()
    cur.execute("""CREATE TABLE IF NOT EXISTS pedidos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL,
            total REAL NOT NULL); """)
    return

def tabla_items_pedidos():
    #Función para hacer las tablas con los productos que se van a comprar
    con, cur = obtener_conexion()
    cur.execute("""CREATE TABLE IF NOT EXISTS items_pedido
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL); """)
    return

def listar_productos():
    #logica para listar los productos en el stock
    con, cur = obtener_conexion()
    cur.execute("SELECT * FROM productos")
    filas = cur.fetchall()
    con.close()
    
    return [dict(fila) for fila in filas]

def listar_categorias():
    #Listar las categorias de los productos
    con, cur = obtener_conexion()
    cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria;")
    filas = cur.fetchall()
    con.close()

    return {"categorias": [fila["categoria"] for fila in filas]}

def pedido_compra(pedido_data=None):
    con, cur = obtener_conexion()
    try:
        cur.execute("BEGIN TRANSACTION;")
        items_procesados = []
        monto_total = 0.0
        
        # Si no se recibe pedido_data, procesa un ítem de prueba (1 unidad del producto 1)
        if pedido_data is None:
            items_a_procesar = [{"producto_id": 1, "cantidad": 1}]
        elif hasattr(pedido_data, "items"):
            items_a_procesar = [{"producto_id": i.producto_id, "cantidad": i.cantidad} for i in pedido_data.items]
        elif isinstance(pedido_data, dict) and "items" in pedido_data:
            items_a_procesar = pedido_data["items"]
        else:
            items_a_procesar = [{"producto_id": 1, "cantidad": 1}]

        for item in items_a_procesar:
            prod_id = item["producto_id"] if isinstance(item, dict) else item.producto_id
            cant = item["cantidad"] if isinstance(item, dict) else item.cantidad

            cur.execute("SELECT * FROM productos WHERE id = ?;", (prod_id,))
            prod = cur.fetchone()

            if not prod:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Producto con ID {prod_id} no existe en el catálogo."
                )

            if cant > prod["stock"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{prod['nombre']}' (ID {prod['id']}). Stock disponible: {prod['stock']}, Solicitado: {cant}."
                )

            subtotal = prod["precio"] * cant
            monto_total += subtotal

            nuevo_stock = prod["stock"] - cant
            cur.execute("UPDATE productos SET stock = ? WHERE id = ?;", (nuevo_stock, prod_id))

            items_procesados.append({
                "producto_id": prod["id"],
                "nombre": prod["nombre"],
                "categoria": prod["categoria"],
                "cantidad": cant,
                "subtotal": round(subtotal, 2)
            })

        fecha_registro = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO pedidos (fecha, estado, total) VALUES (?, 'completado', ?);",
            (fecha_registro, round(monto_total, 2))
        )
        pedido_id = cur.lastrowid

        for item_proc in items_procesados:
            cur.execute(
                "INSERT INTO items_pedido (pedido_id, producto_id, cantidad) VALUES (?, ?, ?);",
                (pedido_id, item_proc["producto_id"], item_proc["cantidad"])
            )
        con.commit()

        return {
            "mensaje": "Pedido registrado correctamente y stock actualizado.",
            "pedido": {
                "id": pedido_id,
                "fecha": fecha_registro,
                "total": round(monto_total, 2),
                "items": items_procesados
            }
        }
    except HTTPException as http_exc:
        con.rollback()
        raise http_exc
    except Exception as e:
        con.rollback()
        raise HTTPException(status_code=500, detail=f"Error inesperado al procesar el pedido: {str(e)}")
    finally:
        con.close()


def reporte_ventas():
    con, cur = obtener_conexion()
#"COALESCE" suma los valores de la columna total
    cur.execute("SELECT COUNT(id) as total_pedidos, COALESCE(SUM(total), 0.0) as total_facturado FROM pedidos;")
    resumen = cur.fetchone()
#Esto permite tener el total facturado y la cantidad de pedidios

#Ahora se debe determinar los productos más vendidos
#agrupando cuántas unidades se vendieron de cada producto
#y cuánto dinero se estima que generaron esas ventas,
#ejecutando una consulta a SQLite3 obteniendo la información
#para hacer un informe
    cur.execute("""SELECT p.id as producto_id, p.nombre,
            p.categoria, SUM(ip.cantidad) as unidades_vendidas,
            SUM(ip.cantidad * p.precio) as recaudacion_estimada
        FROM items_pedido ip JOIN productos p ON ip.producto_id = p.id
        GROUP BY p.id, p.nombre, p.categoria 
        ORDER BY unidades_vendidas DESC;""")
    mas_vendidos = [dict(fila) for fila in cur.fetchall()]
    con.close()

    return {"resumen_ventas":{
        "total_pedidos": resumen["total_pedidos"],
        "total_facturado": round(resumen["total_facturado"], 2)},
            "mas_vendidos": mas_vendidos
           }
