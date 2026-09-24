from sqlalchemy import create_engine, event, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

ARCHIVO_DB = "pokedex.db"

# El "engine" es la conexión a la base. sqlite:/// + nombre del archivo.
engine = create_engine(f"sqlite:///{ARCHIVO_DB}")


@event.listens_for(engine, "connect")
def activar_claves_foraneas(con, _):
    """SQLite NO controla las FK si no le pedís esto. Se ejecuta en cada conexión nueva."""
    con.execute("PRAGMA foreign_keys = ON")


class Base(DeclarativeBase):
    """Clase base de la que heredan todas las tablas."""
    pass


# ---------- Tablas (una clase = una tabla, un atributo = una columna) ----------

class Tipo(Base):
    __tablename__ = "tipos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)

    def a_dict(self) -> dict:
        """Para devolverlo desde la API: FastAPI sabe convertir un dict a JSON, un objeto no."""
        return {"id": self.id, "nombre": self.nombre}


class Pokemon(Base):
    __tablename__ = "pokemones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    nivel: Mapped[int]
    tipo_id: Mapped[int] = mapped_column(ForeignKey("tipos.id"))

    # No es una columna: es un "atajo" para llegar al objeto Tipo desde el pokémon.
    tipo: Mapped[Tipo] = relationship()

    def a_dict(self) -> dict:
        return {"id": self.id, "nombre": self.nombre, "nivel": self.nivel, "tipo_id": self.tipo_id}


def crear_tablas():
    """Crea las tablas (si no existen) a partir de las clases de arriba."""
    Base.metadata.create_all(engine)


def sesion() -> Session:
    """Abre una sesión: la 'conversación' con la base donde se hacen las operaciones."""
    return Session(engine)
