def SQLite3():
    con = sqlite3.connect()
    con.row_factory = sqlite3.Row
    return con

def listar_productos():
    #logica
    con = SQLite3()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos")
    filas = cur.fetchall()
    con.close()
    
    return [dict(fila) for fila in filas]
    pass

def listar_categorias():
    con = SQLite3()
    cur = con.cursor()
    cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria;")
    filas = cursor.fetchall()
    con.close

    return {"categorias": [fila["categoria"] for fila in filas]}

def listar_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria")
    producto: Optinal[str] = Query(None, description="Filtrar por producto")
):
    con = SQLite3()
    cursor = con.cursor()
    query = 

def funcion_crud_1():
    pass

def funcion_crud_2():
    pass

def funcion_crud_3():
    pass
