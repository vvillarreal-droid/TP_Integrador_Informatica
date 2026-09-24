from sqlalchemy import select

from db import get_session, PokemonType, Pokemon
from validation import validate_type, validate_pokemon


# =====================================================
#  TIPOS
# =====================================================

def create_type(data: dict) -> dict:
    clean = validate_type(data)               # 1) validar (ValueError si está mal)
    with get_session() as s:
        pokemon_type = PokemonType(**clean)   # 2) objeto Python, todavía no está en la base
        s.add(pokemon_type)                   # 3) lo agrego a la sesión
        s.commit()                            # 4) recién acá se escribe (y se asigna el id)
        return pokemon_type.to_dict()


def list_types() -> list[dict]:
    with get_session() as s:
        types = s.scalars(select(PokemonType).order_by(PokemonType.nombre))
        return [t.to_dict() for t in types]


def get_type(type_id: int) -> dict | None:
    with get_session() as s:
        pokemon_type = s.get(PokemonType, type_id)   # busca por clave primaria
        return pokemon_type.to_dict() if pokemon_type else None


def delete_type(type_id: int) -> bool:
    """Devuelve True si borró algo. Falla si hay pokemones que usan ese tipo (FK)."""
    with get_session() as s:
        pokemon_type = s.get(PokemonType, type_id)
        if pokemon_type is None:
            return False
        s.delete(pokemon_type)
        s.commit()
        return True


# =====================================================
#  POKEMONES
# =====================================================

# ---- Create ----
def create_pokemon(data: dict) -> dict:
    clean = validate_pokemon(data)
    with get_session() as s:
        pokemon = Pokemon(**clean)            # el dict validado se desarma en columnas
        s.add(pokemon)
        s.commit()
        return pokemon.to_dict()              # ya tiene el id que asignó la base


# ---- Read ----
def list_pokemons(type_id: int | None = None) -> list[dict]:
    """Lista todos, o solo los de un tipo si se pasa type_id (filtro opcional)."""
    with get_session() as s:
        query = select(Pokemon).order_by(Pokemon.id)
        if type_id is not None:
            query = query.where(Pokemon.tipo_id == type_id)
        return [p.to_dict() for p in s.scalars(query)]


def get_pokemon(pokemon_id: int) -> dict | None:
    with get_session() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        return pokemon.to_dict() if pokemon else None


def list_with_type() -> list[dict]:
    """Cada pokémon con el NOMBRE de su tipo. La relationship hace el JOIN por nosotros."""
    with get_session() as s:
        pokemons = s.scalars(select(Pokemon).order_by(Pokemon.id))
        return [p.to_dict() | {"tipo": p.pokemon_type.nombre} for p in pokemons]


# ---- Update ----
def update_pokemon(pokemon_id: int, changes: dict) -> dict | None:
    clean = validate_pokemon(changes, partial=True)   # solo revisa lo que vino
    with get_session() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        if pokemon is None:
            return None
        for field, value in clean.items():
            setattr(pokemon, field, value)    # pokemon.nivel = 16, etc.
        s.commit()                            # SQLAlchemy detecta qué cambió y hace el UPDATE
        return pokemon.to_dict()


# ---- Delete ----
def delete_pokemon(pokemon_id: int) -> bool:
    with get_session() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        if pokemon is None:
            return False
        s.delete(pokemon)
        s.commit()
        return True
