from db import conectar
from modelos import Tipo, TipoCrear, Pokemon, PokemonCrear, PokemonActualizar


# =====================================================
#  TIPOS
# =====================================================

def crear_tipo(datos: TipoCrear) -> Tipo:
    with conectar() as con:
        cur = con.execute("INSERT INTO tipos (nombre) VALUES (?)", (datos.nombre,))
        return Tipo(id=cur.lastrowid, nombre=datos.nombre)


def listar_tipos() -> list[Tipo]:
    with conectar() as con:
        filas = con.execute("SELECT * FROM tipos ORDER BY nombre").fetchall()
        return [Tipo(**dict(fila)) for fila in filas]


def obtener_tipo(tipo_id: int) -> Tipo | None:
    with conectar() as con:
        fila = con.execute("SELECT * FROM tipos WHERE id = ?", (tipo_id,)).fetchone()
        return Tipo(**dict(fila)) if fila else None


def borrar_tipo(tipo_id: int) -> bool:
    """Devuelve True si borró algo. Falla si hay pokemones que usan ese tipo (FK)."""
    with conectar() as con:
        cur = con.execute("DELETE FROM tipos WHERE id = ?", (tipo_id,))
        return cur.rowcount > 0


# =====================================================
#  POKEMONES
# =====================================================

# ---- Create ----
def crear_pokemon(datos: PokemonCrear) -> Pokemon:
    with conectar() as con:
        cur = con.execute(
            "INSERT INTO pokemones (nombre, nivel, tipo_id) VALUES (?, ?, ?)",
            (datos.nombre, datos.nivel, datos.tipo_id),
        )
        # model_dump() convierte el modelo en dict -> le sumamos el id que asignó SQLite
        return Pokemon(id=cur.lastrowid, **datos.model_dump())


# ---- Read ----
def listar_pokemones(tipo_id: int | None = None) -> list[Pokemon]:
    """Lista todos, o solo los de un tipo si se pasa tipo_id (filtro opcional)."""
    with conectar() as con:
        if tipo_id is None:
            filas = con.execute("SELECT * FROM pokemones ORDER BY id").fetchall()
        else:
            filas = con.execute(
                "SELECT * FROM pokemones WHERE tipo_id = ? ORDER BY id", (tipo_id,)
            ).fetchall()
        return [Pokemon(**dict(fila)) for fila in filas]


def obtener_pokemon(pokemon_id: int) -> Pokemon | None:
    with conectar() as con:
        fila = con.execute(
            "SELECT * FROM pokemones WHERE id = ?", (pokemon_id,)
        ).fetchone()
        return Pokemon(**dict(fila)) if fila else None


def listar_con_tipo() -> list[dict]:
    """JOIN: cada pokémon con el NOMBRE de su tipo, no solo el id."""
    with conectar() as con:
        filas = con.execute("""
            SELECT p.id, p.nombre, p.nivel, t.nombre AS tipo
            FROM pokemones p
            JOIN tipos t ON t.id = p.tipo_id
            ORDER BY p.id
        """).fetchall()
        return [dict(fila) for fila in filas]


# ---- Update ----
def actualizar_pokemon(pokemon_id: int, cambios: PokemonActualizar) -> Pokemon | None:
    # exclude_none=True -> solo los campos que el usuario mandó
    campos = cambios.model_dump(exclude_none=True)
    if not campos:
        return obtener_pokemon(pokemon_id)   # no había nada que cambiar

    # arma "nombre = ?, nivel = ?" según los campos que llegaron
    set_sql = ", ".join(f"{campo} = ?" for campo in campos)
    valores = list(campos.values()) + [pokemon_id]

    with conectar() as con:
        con.execute(f"UPDATE pokemones SET {set_sql} WHERE id = ?", valores)
    return obtener_pokemon(pokemon_id)


# ---- Delete ----
def borrar_pokemon(pokemon_id: int) -> bool:
    with conectar() as con:
        cur = con.execute("DELETE FROM pokemones WHERE id = ?", (pokemon_id,))
        return cur.rowcount > 0
