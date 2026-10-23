import sqlite3

def cargar_base_de_datos():
    con = sqlite3.connect("productos.db")
    cur = con.cursor()

    # 1. Crear tabla productos (incluye columna stock)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL
    );
    """)

    # 2. Crear tabla pedidos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        estado TEXT NOT NULL,
        total REAL NOT NULL
    );
    """)

    # 3. Crear tabla items_pedido
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL
    );
    """)

    # Verificar e insertar productos iniciales
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        productos_iniciales = [
            (1, "Arroz Largo Fino 1kg", "Almacén", 1250.0, 50),
            (2, "Aceite de Girasol 1.5L", "Aceites y Aderezos", 2800.5, 30),
            (3, "Leche Entera 1L", "Lácteos", 1100.0, 40),
            (4, "Fideos Tallarines 500g", "Almacén", 950.0, 60),
            (5, "Yerba Mate 500g", "Infusiones", 1900.0, 25)
        ]
        cur.executemany("INSERT INTO productos VALUES (?, ?, ?, ?, ?)", productos_iniciales)

    # Verificar e insertar un pedido de prueba (para que GET /reporte_ventas funcione desde el primer momento)
    cur.execute("SELECT COUNT(*) FROM pedidos")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO pedidos (fecha, estado, total) VALUES ('2024-10-20T10:00:00', 'entregado', 4050.0);")
        pedido_id = cur.lastrowid
        cur.execute("INSERT INTO items_pedido (pedido_id, producto_id, cantidad) VALUES (?, 1, 1);", (pedido_id,))
        cur.execute("INSERT INTO items_pedido (pedido_id, producto_id, cantidad) VALUES (?, 2, 1);", (pedido_id,))

    con.commit()
    con.close()
    print("Base de datos 'productos.db' inicializada correctamente.")

if __name__ == "__main__":
    cargar_base_de_datos()
