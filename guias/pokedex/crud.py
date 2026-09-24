from sqlalchemy import select

from db import sesion, Tipo, Pokemon
from validaciones import validar_tipo, validar_pokemon


# =====================================================
#  TIPOS
# =====================================================

def crear_tipo(datos: dict) -> dict:
    limpio = validar_tipo(datos)              # 1) validar (ValueError si está mal)
    with sesion() as s:
        tipo = Tipo(**limpio)                 # 2) objeto Python, todavía no está en la base
        s.add(tipo)                           # 3) lo agrego a la sesión
        s.commit()                            # 4) recién acá se escribe (y se asigna el id)
        return tipo.a_dict()


def listar_tipos() -> list[dict]:
    with sesion() as s:
        tipos = s.scalars(select(Tipo).order_by(Tipo.nombre))
        return [t.a_dict() for t in tipos]


def obtener_tipo(tipo_id: int) -> dict | None:
    with sesion() as s:
        tipo = s.get(Tipo, tipo_id)           # busca por clave primaria
        return tipo.a_dict() if tipo else None


def borrar_tipo(tipo_id: int) -> bool:
    """Devuelve True si borró algo. Falla si hay pokemones que usan ese tipo (FK)."""
    with sesion() as s:
        tipo = s.get(Tipo, tipo_id)
        if tipo is None:
            return False
        s.delete(tipo)
        s.commit()
        return True


# =====================================================
#  POKEMONES
# =====================================================

# ---- Create ----
def crear_pokemon(datos: dict) -> dict:
    limpio = validar_pokemon(datos)
    with sesion() as s:
        pokemon = Pokemon(**limpio)           # el dict validado se desarma en columnas
        s.add(pokemon)
        s.commit()
        return pokemon.a_dict()               # ya tiene el id que asignó la base


# ---- Read ----
def listar_pokemones(tipo_id: int | None = None) -> list[dict]:
    """Lista todos, o solo los de un tipo si se pasa tipo_id (filtro opcional)."""
    with sesion() as s:
        consulta = select(Pokemon).order_by(Pokemon.id)
        if tipo_id is not None:
            consulta = consulta.where(Pokemon.tipo_id == tipo_id)
        return [p.a_dict() for p in s.scalars(consulta)]


def obtener_pokemon(pokemon_id: int) -> dict | None:
    with sesion() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        return pokemon.a_dict() if pokemon else None


def listar_con_tipo() -> list[dict]:
    """Cada pokémon con el NOMBRE de su tipo. La relationship hace el JOIN por nosotros."""
    with sesion() as s:
        pokemones = s.scalars(select(Pokemon).order_by(Pokemon.id))
        return [p.a_dict() | {"tipo": p.tipo.nombre} for p in pokemones]


# ---- Update ----
def actualizar_pokemon(pokemon_id: int, cambios: dict) -> dict | None:
    limpio = validar_pokemon(cambios, parcial=True)   # solo revisa lo que vino
    with sesion() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        if pokemon is None:
            return None
        for campo, valor in limpio.items():
            setattr(pokemon, campo, valor)    # pokemon.nivel = 16, etc.
        s.commit()                            # SQLAlchemy detecta qué cambió y hace el UPDATE
        return pokemon.a_dict()


# ---- Delete ----
def borrar_pokemon(pokemon_id: int) -> bool:
    with sesion() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        if pokemon is None:
            return False
        s.delete(pokemon)
        s.commit()
        return True
