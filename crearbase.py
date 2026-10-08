import sqlite3

def cargar_base_de_datos():
    con = sqlite3.connect("productos.bd")
    cur = con.cursor()

    #Crear la tabla indicando la y NOT NULL
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio REAL NOT NULL
    )
    """)

    #Verificar si la tabla ya tiene datos cargados
    cur.execute("SELECT COUNT(*) FROM productos")
    cantidad = cur.fetchone()[0]

    #Si la tabla está vacía, insertar los productos iniciales
    if cantidad == 0:
        productos_iniciales = [
            (1, "Arroz Largo Fino 1kg", "Almacén", 1250.0),
            (2, "Aceite de Girasol 1.5L", "Aceites y Aderezos", 2800.5),
            (3, "Leche Entera 1L", "Lácteos", 1100.0),
            (4, "Fideos Tallarines 500g", "Almacén", 950.0),
            (5, "Yerba Mate 500g", "Infusiones", 1900.0)
        ]
        cur.executemany("INSERT INTO productos VALUES (?, ?, ?, ?)", productos_iniciales)
        con.commit()
        print("Base de datos 'productos.bd' ")
    else:
        print("La base de datos ya contiene registros, no se duplicaron datos.")

    con.close()

if __name__ == "__main__":
    cargar_base_de_datos()
