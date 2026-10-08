# Guía · Estructura del proyecto

Informática (TDS05) · Universidad de Mendoza · Sede Río Cuarto

Todos los proyectos del integrador tienen la misma forma: una API que recibe un pedido, consulta una base y devuelve JSON. Por eso conviene que todos tengan **los mismos archivos, con las mismas responsabilidades**. Cada archivo hace una sola cosa, y cuando algo falla sabés dónde buscar.

```
my-project/
├── main.py            ← la app de FastAPI y los endpoints
├── crud.py            ← las funciones que hablan con la base
├── models.py          ← las tablas como clases + la conexión
├── validation.py      ← las funciones que revisan los datos del POST
├── security.py        ← la API key
├── seed.py            ← crea las tablas y carga los datos iniciales
├── requirements.txt   ← las librerías que hay que instalar
├── README.md          ← qué es, cómo se levanta, cómo se usa
└── .gitignore         ← lo que no se sube (*.db, __pycache__/, venv/, .env)
```

Los ejemplos son de la Pokédex, con los nombres en inglés como pide el criterio del curso.

---

## 1. Quién llama a quién

```
   pedido HTTP
        │
        ▼
    main.py  ──────►  security.py     (¿trae la clave?)
        │
        ▼
    crud.py  ──────►  validation.py   (¿los datos están bien?)
        │
        ▼
   models.py  ─────►  SQLite
```

La regla es que **las llamadas van siempre para abajo**:

- `main.py` llama a `crud.py`. No abre sesiones ni arma consultas.
- `crud.py` usa `models.py` y `validation.py`. No sabe nada de FastAPI ni de códigos HTTP.
- `models.py` no importa a ninguno de los otros.

Si en `main.py` aparece un `select(...)`, o en `crud.py` un `HTTPException`, está en el archivo equivocado.

---

## 2. `models.py` — las tablas

La conexión a la base y las tablas como clases de SQLAlchemy. Es lo que en la [guía de SQLAlchemy](sqlalchemy_orm.md) se llama `db.py`: si ya lo tenés con ese nombre, alcanza con renombrarlo.

```python
from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

engine = create_engine("sqlite:///pokedex.db")


class Base(DeclarativeBase):
    pass


class PokemonType(Base):
    __tablename__ = "types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class Pokemon(Base):
    __tablename__ = "pokemons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    level: Mapped[int]
    type_id: Mapped[int] = mapped_column(ForeignKey("types.id"))

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "level": self.level, "type_id": self.type_id}


def create_tables():
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
```

## 3. `crud.py` — las funciones de la base

Todo lo que lee o escribe en la base está acá, una función por operación. Reciben datos comunes de Python y devuelven `dict`, listas o `None`.

```python
from sqlalchemy import select

from models import get_session, Pokemon
from validation import validate_pokemon


def list_pokemons(type_id: int | None = None) -> list[dict]:
    with get_session() as s:
        query = select(Pokemon)
        if type_id is not None:
            query = query.where(Pokemon.type_id == type_id)
        return [p.to_dict() for p in s.scalars(query)]


def get_pokemon(pokemon_id: int) -> dict | None:
    with get_session() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        return pokemon.to_dict() if pokemon else None      # None = no existe


def create_pokemon(data: dict) -> dict:
    clean = validate_pokemon(data)                         # ValueError si está mal
    with get_session() as s:
        pokemon = Pokemon(**clean)
        s.add(pokemon)
        s.commit()
        return pokemon.to_dict()
```

## 4. `validation.py` — revisar los datos

Las funciones que revisan lo que llega en un `POST`. Si algo está mal lanzan `ValueError` con un mensaje claro; si está bien devuelven los datos limpios.

```python
def validate_pokemon(data: dict) -> dict:
    name = data.get("name")
    level = data.get("level")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("name is required")
    if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 100:
        raise ValueError("level must be an integer between 1 and 100")

    return {"name": name.strip(), "level": level, "type_id": data.get("type_id")}
```

## 5. `security.py` — la API key

La clave y la función que la controla. Nada más.

```python
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "test-key-2026"
header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Depends(header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

## 6. `main.py` — la app y los endpoints

Crea la app y define los endpoints. Cada endpoint es **corto** y hace tres cosas: recibe el pedido, llama a una función de `crud.py` y devuelve la respuesta o el error.

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError

import crud
from security import verify_api_key

app = FastAPI(title="Pokedex API", dependencies=[Depends(verify_api_key)])


@app.get("/pokemons")
def list_pokemons(type_id: int | None = None):
    try:
        return crud.list_pokemons(type_id)
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/pokemons/{pokemon_id}")
def get_pokemon(pokemon_id: int):
    pokemon = crud.get_pokemon(pokemon_id)
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return pokemon


@app.post("/pokemons", status_code=201)
def create_pokemon(data: dict):
    try:
        return crud.create_pokemon(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="type_id does not exist")
```

`main.py` es el único que traduce a HTTP lo que pasó en `crud.py`:

| Lo que pasó en `crud.py` | Respuesta |
|---|---|
| Devolvió datos | **200** (o **201** en el alta) |
| Devolvió `None` | **404** |
| Lanzó `ValueError` | **400** con el mensaje |
| Lanzó `IntegrityError` | **400** |
| Lanzó `OperationalError` | **500** |

## 7. `seed.py` — crear la base y cargar los datos

Crea las tablas y carga los datos iniciales **solo si la base está vacía**. Se corre a mano, antes de levantar el servidor: `python seed.py`.

```python
from sqlalchemy import select

from models import create_tables, get_session, PokemonType, Pokemon


def seed():
    create_tables()
    with get_session() as s:
        if s.scalars(select(PokemonType)).first() is not None:
            print("The database already has data.")
            return
        fire = PokemonType(name="Fire")
        s.add(fire)
        s.commit()                       # ahora fire.id existe
        s.add_all([
            Pokemon(name="Charmander", level=5, type_id=fire.id),
            Pokemon(name="Vulpix", level=12, type_id=fire.id),
        ])
        s.commit()
        print("Data loaded.")


if __name__ == "__main__":
    seed()
```

`main.py` **no** llama al seed. En Render el arranque es `python seed.py && gunicorn main:app ...`: primero el seed, una sola vez, y después el servidor.

---

## ¿Dónde va cada cosa?

| Quiero... | Va en |
|---|---|
| Agregar un endpoint | `main.py` (y su función en `crud.py`) |
| Cambiar una consulta o un filtro | `crud.py` |
| Agregar una columna o una tabla | `models.py` (y borrar el `.db` para regenerarlo) |
| Cambiar una regla de validación | `validation.py` |
| Cambiar la clave | `security.py` |
| Cambiar los datos de ejemplo | `seed.py` |
| Agregar una librería | `requirements.txt` |

## Errores comunes

- **Todo en `main.py`.** Funciona, pero con seis endpoints ya no se encuentra nada. Separá apenas tengas el segundo.
- **Consultas adentro de los endpoints.** El `select(...)` va en `crud.py`; el endpoint solo llama a la función.
- **`HTTPException` adentro de `crud.py`.** `crud.py` devuelve `None` o lanza `ValueError`; el que decide el código HTTP es `main.py`.
- **Llamar al seed desde `main.py`.** Con dos workers se ejecuta dos veces.
- **Imports en círculo.** Si `models.py` importa `crud.py` y `crud.py` importa `models.py`, Python falla al arrancar. Las llamadas van siempre para abajo.
- **Nombres de archivo distintos.** `segurity.py`, `Crud.py` o `modelos.py` rompen los `import`. Minúsculas, en inglés y tal cual figuran acá.
- **Carpetas.** No hacen falta: todos los archivos van en la raíz del repo, al lado de `main.py`.
