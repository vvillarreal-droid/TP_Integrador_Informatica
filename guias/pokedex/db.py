import sqlite3

ARCHIVO_DB = "pokedex.db"


def conectar():
    """Abre la conexión a la base y la deja lista para usar."""
    con = sqlite3.connect(ARCHIVO_DB)
    con.row_factory = sqlite3.Row          # las filas se leen como diccionarios
    con.execute("PRAGMA foreign_keys = ON")  # SQLite NO controla las FK si no le pedís esto
    return con


def crear_tablas():
    """Crea las dos tablas si todavía no existen."""
    with conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS tipos (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS pokemones (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre  TEXT    NOT NULL,
                nivel   INTEGER NOT NULL,
                tipo_id INTEGER NOT NULL,
                FOREIGN KEY (tipo_id) REFERENCES tipos(id)
            )
        """)
