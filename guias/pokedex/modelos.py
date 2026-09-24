from pydantic import BaseModel, Field


# ---------- Tipos ----------

class TipoCrear(BaseModel):
    """Lo que hace falta para crear un tipo (todavía no tiene id)."""
    nombre: str = Field(min_length=1, max_length=30)


class Tipo(TipoCrear):
    """Un tipo tal como está guardado en la base (ya tiene id)."""
    id: int


# ---------- Pokemones ----------

class PokemonCrear(BaseModel):
    """Datos para dar de alta un pokémon."""
    nombre: str = Field(min_length=1, max_length=50)
    nivel: int = Field(ge=1, le=100)     # ge = mayor o igual, le = menor o igual
    tipo_id: int                          # FK: el id de un tipo que exista


class Pokemon(PokemonCrear):
    """Un pokémon tal como está guardado en la base."""
    id: int


class PokemonActualizar(BaseModel):
    """Para modificar: todos los campos son opcionales, mandás solo lo que cambia."""
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    nivel: int | None = Field(default=None, ge=1, le=100)
    tipo_id: int | None = None
