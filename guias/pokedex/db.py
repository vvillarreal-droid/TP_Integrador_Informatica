from sqlalchemy import create_engine, event, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

DB_FILE = "pokedex.db"

# El "engine" es la conexión a la base. sqlite:/// + nombre del archivo.
engine = create_engine(f"sqlite:///{DB_FILE}")


@event.listens_for(engine, "connect")
def enable_foreign_keys(con, _):
    """SQLite NO controla las FK si no le pedís esto. Se ejecuta en cada conexión nueva."""
    con.execute("PRAGMA foreign_keys = ON")


class Base(DeclarativeBase):
    """Clase base de la que heredan todas las tablas."""
    pass


# ---------- Tablas (una clase = una tabla, un atributo = una columna) ----------
# Las clases y funciones van en inglés (criterio del curso). Los nombres de las tablas
# y columnas quedan como en el alcance, porque son parte del contrato de la API.

class PokemonType(Base):
    __tablename__ = "tipos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)

    def to_dict(self) -> dict:
        """Para devolverlo desde la API: FastAPI sabe convertir un dict a JSON, un objeto no."""
        return {"id": self.id, "nombre": self.nombre}


class Pokemon(Base):
    __tablename__ = "pokemones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    nivel: Mapped[int]
    tipo_id: Mapped[int] = mapped_column(ForeignKey("tipos.id"))

    # No es una columna: es un "atajo" para llegar al objeto PokemonType desde el pokémon.
    pokemon_type: Mapped[PokemonType] = relationship()

    def to_dict(self) -> dict:
        return {"id": self.id, "nombre": self.nombre, "nivel": self.nivel, "tipo_id": self.tipo_id}


def create_tables():
    """Crea las tablas (si no existen) a partir de las clases de arriba."""
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Abre una sesión: la 'conversación' con la base donde se hacen las operaciones."""
    return Session(engine)
