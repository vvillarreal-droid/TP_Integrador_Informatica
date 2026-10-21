import sqlite3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from datetime import datetime

def obtener_conexion():
    #Función para activar cada función conectandola con SQLite3 y Cursor
    #sin la necesidad de conectarse en cada función
    con = sqlite3.connect("productos.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur

def tabla_productos():
    #Función para hacer las tablas de los productos
    obtener_conexion()
    cur.execute("""CREATE TABLE IF NOT EXISTS productos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL); """)

def tabla_pedidos():
    #Función para hacer las tablas de los pedidos
    obtener_conexion()
    cur.execute("""CREATE TABLE IF NOT EXISTS pedidos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL,
            total REAL NOT NULL); """)

def tabla_items_pedidos():
    #Función para hacer las tablas con los productos que se van a comprar
    obtener_conexion()
    cur.execute("""CREATE TABLE IF NOT EXISTS items_pedido
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL); """)

def listar_productos():
    #logica para listar los productos en el stock
    obtener_conexion()
    cur.execute("SELECT * FROM productos")
    filas = cur.fetchall()
    con.close()
    
    return [dict(fila) for fila in filas]
    pass

def listar_categorias():
    #Listar las categorias de los productos
    obtener_conexion()
    cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria;")
    filas = cur.fetchall()
    con.close()

    return {"categorias": [fila["categoria"] for fila in filas]}

def pedido_compra():
    obtener_conexion()
    try:
#Primero hay que iniciar la transacción del pedido
        cur.execute("BEGIN ORDER;")
        items_procesados = []
        monto_total = 0.0
        
        for item in pedido_data.items:
            cur.execute("SELECT * FROM productos WHERE id = ?;", (item.producto_id,))
            prod = cur.fetchone() 
#cursor.fetchone es una función que ayuda a recuperar la siguiente
#fila de un conjunto de resultados de una consulta SQLite3
            if not prod:
                raise HTTPException(status_code=404, 
                detail=f"Producto con ID {item.producto_id} no existe en el catálogo."
                )
#Hay que agregar un condición para evitar
#vender más que el stock que haya disponible
            if item.cantidad > prod["stock"]:
                raise HTTPException(status_code=400,
                    detail=f"Stock insuficiente para '{prod['nombre']}' (ID {prod['id']}). Stock disponible: {prod['stock']}, Solicitado: {item.cantidad}."
                )
#Creo las nuevas variables resultantes de
#el stock y el precio para usar en el Reporte de Ventas
            subtotal = precio_unitario * item.cantidad
            monto_total += subtotal
#Para evitar que el stock figure de manera infinita
#hay que ir descontandolo a medida que se compra en
#relación a la cantidad comprada
            nuevo_stock = prod["stock"] - item.cantidad
            cur.execute("UPDATE productos SET stock = ? WHERE id = ?;", (nuevo_stock, item.producto_id)
            )
#Ahora cargo en la variable de la lista el resultado de
#los datos y montos obtenidos
            items_procesados.append({
                "producto_id": prod["id"],
                "nombre": prod["nombre"],
                "categoria": prod["categoria"],
                "cantidad": item.cantidad,
                "subtotal": round(subtotal, 2)
            })
#También hay que registrar la fecha y hora del pedido
#ChatGPT dice que "datetime.now().isoformat()" sirve para obtener
#la fecha y hora actuales y convertirlas en un texto
        fecha_registro = datetime.now().isoformat()
        cur.execute("INSERT INTO pedidos (fecha, total) VALUES (?, ?);",(fecha_registro, round(monto_total, 2)))
        pedido_id = cur.lastrowid
#"cursor.lastrowid"sirve para obtener el identificador (ID)
#de la última fila insertada en una tabla de una base de datos

#Se registran los ítems en una tabla
#para luego cargar los cambios
        for item_proc in items_procesados:
            cur.execute("INSERT INTO items_pedido (pedido_id, producto_id, cantidad) VALUES (?, ?, ?);",
                (pedido_id, item_proc["producto_id"], item_proc["cantidad"]))
        con.commit()
#Devolvemos un mensaje que marque cada dato/valor relevante
        return {
            "mensaje": "Pedido registrado correctamente y stock actualizado.",
            "pedido": {
                "id": pedido_id,
                "fecha": fecha_registro,
                "total": round(monto_total, 2),
                "items": items_procesados}}
#Al preguntar el progreso a la IA, se indicó que es
#recomendable generar Cancelaciones de los cambios realizados 
#por si se producen errores o fallos imprevistos
    except HTTPException as http_exc:
        con.rollback()
        raise http_exc
    except Exception as e:
        con.rollback()
        raise HTTPException(status_code=500, detail=f"Error inesperado al procesar el pedido: {str(e)}")
    finally:
        con.close()

def reporte_ventas():
    obtener_conexion()
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
            "mas_vendidos": productos_mas_vendidos}


def funcion_crud_1():
    pass

def funcion_crud_2():
    pass

def funcion_crud_3():
    pass
