def SQLite3():
    #Función para activar cada función conectandola con SQLite3 y Cursor
    con = sqlite3.connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur

def listar_productos():
    #logica para listar los productos
    con = SQLite3()
    cur.execute("SELECT * FROM productos")
    filas = cur.fetchall()
    con.close()
    
    return [dict(fila) for fila in filas]
    pass

def listar_categorias():
    #Listar las categorias de los productos
    con = SQLite3()
    cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria;")
    filas = cursor.fetchall()
    con.close

    return {"categorias": [fila["categoria"] for fila in filas]}

def listar_productos(
    #Logica para filtrar los elementos por productos y/o categorias
    categoria: Optional[str] = Query(None, description="Filtrar por categoria")
    producto: Optinal[str] = Query(None, description="Filtrar por producto")
):
    con = SQLite3()
    query = "SELECT * FROM productos WHERE 1=1"
    params = []
    
    if categoria:
        query += " AND LOWER(categoria) = LOWER(?)"
        params.append(categoria)
    if producto:
        query += " AND LOWER(producto) = LOWER(?)"
        params.append(producto)
        
    query += " ORDER BY id;"
    cursor.execute(query, params)
    productos = [dict(fila) for fila in cursor.fetchall()]
    con.close()

def funcion_crud_1():
    pass

def funcion_crud_2():
    pass

def funcion_crud_3():
    pass
