# Guía · SQLAlchemy (ORM) con una Pokédex

Informática (TDS05) · Universidad de Mendoza · Sede Río Cuarto

Esta guía muestra cómo guardar datos en **SQLite** usando **SQLAlchemy** como ORM: las tablas se definen como clases de Python y las consultas se hacen con métodos, **sin escribir SQL a mano**. Las validaciones de los datos se hacen **a mano**, con funciones de Python comunes. El ejemplo es una Pokédex con dos tablas relacionadas. Es el mismo patrón que necesitan para el Proyecto Integrador, solo que con 2 tablas en vez de 3.

El código completo está en la carpeta [pokedex/](pokedex/). Se puede correr directo con `python main.py`, no hace falta FastAPI para probarlo.

```
pip install sqlalchemy
```

> **Sobre los nombres.** Siguiendo el criterio del curso, las **variables, funciones y clases** del ejemplo están en inglés (`create_pokemon`, `get_session`, `PokemonType`). Los nombres de **tablas, columnas y rutas** (`pokemones`, `nombre`, `tipo_id`, `/pokemones`) quedan en español porque son el contrato de la API, igual que en el alcance de cada grupo. Los comentarios están en español para que se entiendan; en la entrega final los suyos van en inglés.

---

## 1. Qué es un ORM

ORM significa *Object-Relational Mapping*: una herramienta que **traduce** entre objetos de Python y filas de una tabla. Vos trabajás con clases, atributos y métodos; SQLAlchemy arma el SQL por atrás.

| Sin ORM (`sqlite3`) | Con ORM (SQLAlchemy) |
|---|---|
| `CREATE TABLE pokemones (...)` | `class Pokemon(Base): ...` |
| `INSERT INTO pokemones VALUES (?, ?, ?)` | `s.add(Pokemon(nombre=..., nivel=...))` |
| `SELECT * FROM pokemones WHERE tipo_id = ?` | `select(Pokemon).where(Pokemon.tipo_id == 1)` |
| `UPDATE pokemones SET nivel = ? WHERE id = ?` | `pokemon.nivel = 16` y `s.commit()` |
| `DELETE FROM pokemones WHERE id = ?` | `s.delete(pokemon)` |
| Fila = tupla `(1, 'Charmander', 5, 1)` | Fila = objeto `pokemon.nombre`, `pokemon.nivel` |

Lo que el ORM **no** hace: validar reglas de negocio. Que el nivel esté entre 1 y 100, que el nombre no venga vacío, eso lo tenemos que revisar nosotros antes de guardar.

```
   dato de entrada  ──►  validar (a mano)  ──►  función CRUD  ──►  SQLAlchemy  ──►  SQLite
   (dict, JSON)          (ValueError si                (métodos)       (arma el SQL)    (pokedex.db)
                          está mal)
```

---

## 2. Estructura del proyecto

```
pokedex/
├── db.py             ← conexión + las tablas como clases
├── validation.py     ← funciones que revisan los datos antes de guardar
├── crud.py           ← funciones Create / Read / Update / Delete
├── main.py           ← programa de prueba
└── pokedex.db        ← se genera solo (no va al repo)
```

Separar en archivos no es obligatorio, pero ayuda a no mezclar cosas. En el integrador, `main.py` sería la API de FastAPI y llamaría a las funciones de `crud.py`; `db.py` reemplaza la parte de "crear tablas" del `seed.py`.

---

## 3. Las tablas como clases — `db.py`

Dos tablas. `tipos` es la tabla "padre" y `pokemones` apunta a ella con una clave foránea (`tipo_id`).

```
tipos                      pokemones
┌────┬────────┐            ┌────┬────────────┬───────┬─────────┐
│ id │ nombre │            │ id │ nombre     │ nivel │ tipo_id │
├────┼────────┤            ├────┼────────────┼───────┼─────────┤
│ 1  │ Fuego  │◄───────────│ 1  │ Charmander │ 5     │ 1       │
│ 2  │ Agua   │◄──┐        │ 2  │ Squirtle   │ 7     │ 2       │
└────┴────────┘   └────────│ 3  │ Vulpix     │ 12    │ 1       │
                           └────┴────────────┴───────┴─────────┘
```

```python
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


class PokemonType(Base):
    __tablename__ = "tipos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)

    def to_dict(self) -> dict:
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
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
```

Lo que hay que entender de cada parte:

- **`engine`**: representa la base. Se crea una sola vez. Para SQLite la URL es `sqlite:///` más el nombre del archivo.
- **`class PokemonType(Base)`** con **`__tablename__`**: cada clase que hereda de `Base` es una tabla. El nombre de la tabla en la base es el de `__tablename__`, que puede ser distinto del nombre de la clase.
- **`Mapped[int]`** y **`mapped_column(...)`**: cada atributo con `Mapped[...]` es una columna. El tipo de Python (`int`, `str`) define el tipo de la columna. `mapped_column` es para agregar detalles: `primary_key=True`, `unique=True`, `ForeignKey("tipos.id")`, largo del texto. Si no hay detalles (`nivel: Mapped[int]`), no hace falta.
- **`primary_key=True`**: el `id` lo asigna la base solo. Nunca lo mandás vos al crear.
- **`ForeignKey("tipos.id")`**: `tipo_id` tiene que ser un `id` que exista en `tipos`. Es `"nombre_de_tabla.columna"`, no el nombre de la clase.
- **`relationship()`**: no crea una columna. Le dice a SQLAlchemy que desde un pokémon se puede llegar al objeto `PokemonType` con `pokemon.pokemon_type`. Lo usamos en la sección 5 para evitar escribir un JOIN.
- **`PRAGMA foreign_keys = ON`**: por defecto SQLite **ignora** las claves foráneas. Sin esto podés cargar un pokémon con `tipo_id = 999` y no se queja. Hay que ejecutarlo en cada conexión: `@event.listens_for(engine, "connect")` lo hace por nosotros.
- **`to_dict()`**: convierte el objeto en un diccionario. FastAPI sabe transformar un dict en JSON, pero no un objeto de SQLAlchemy. Es lo que devuelven todas las funciones de `crud.py`.
- **`Base.metadata.create_all(engine)`**: mira todas las clases que heredan de `Base` y crea las tablas que falten. Si ya existen no hace nada.
- **`Session(engine)`**: la sesión es la "conversación" con la base. Adentro se agregan, buscan, modifican y borran objetos. Nada se escribe hasta que hacés `s.commit()`.

---

## 4. Las validation — `validation.py`

La base solo controla tipos básicos y las restricciones de las columnas (`unique`, FK). Todo lo demás lo revisamos a mano **antes** de tocar la base. La idea es simple: una función que recibe un `dict` (lo que llegó del usuario), revisa campo por campo, y devuelve un dict clean. Si algo está mal, lanza `ValueError` con un mensaje claro.

```python
def validate_type(data: dict) -> dict:
    nombre = data.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("nombre es obligatorio y no puede estar vacío")
    if len(nombre) > 30:
        raise ValueError("nombre no puede superar los 30 caracteres")
    return {"nombre": nombre.strip()}


def validate_pokemon(data: dict, partial: bool = False) -> dict:
    """partial=False: para crear, todos los campos son obligatorios.
    partial=True: para actualizar, se revisan solo los campos que vinieron."""
    clean = {}

    if "nombre" in data or not partial:
        nombre = data.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("nombre es obligatorio y no puede estar vacío")
        if len(nombre) > 50:
            raise ValueError("nombre no puede superar los 50 caracteres")
        clean["nombre"] = nombre.strip()

    if "nivel" in data or not partial:
        nivel = data.get("nivel")
        if not isinstance(nivel, int) or isinstance(nivel, bool):
            raise ValueError("nivel es obligatorio y tiene que ser un número entero")
        if not 1 <= nivel <= 100:
            raise ValueError("nivel tiene que estar entre 1 y 100")
        clean["nivel"] = nivel

    if "tipo_id" in data or not partial:
        tipo_id = data.get("tipo_id")
        if not isinstance(tipo_id, int) or isinstance(tipo_id, bool):
            raise ValueError("tipo_id es obligatorio y tiene que ser un número entero")
        clean["tipo_id"] = tipo_id

    return clean
```

Detalles que importan:

- **`data.get("nombre")`** en vez de `data["nombre"]`: si el campo no vino, devuelve `None` en vez de romper con `KeyError`. Así el mensaje de error lo damos nosotros.
- **`isinstance(nivel, int)`**: revisa el tipo. Un `"25"` como texto no pasa. Si querés aceptarlo, convertilo con `int(nivel)` dentro de un `try/except ValueError`.
- **`isinstance(nivel, bool)`**: en Python `True` es un `int` (vale 1). Sin esta línea, `nivel = True` pasaría como nivel 1.
- **Devolver un dict nuevo** (`clean`) y no el original: así solo llegan a la base los campos que conocemos, aunque el usuario mande basura extra.
- **`partial=True`**: para el `PUT` de Nivel B, donde el usuario manda solo lo que cambia. Con `partial=False` se exige todo.

Probalo en la consola:

```python
>>> from validation import validate_pokemon
>>> validate_pokemon({"nombre": "Pikachu", "nivel": 25, "tipo_id": 1})
{'nombre': 'Pikachu', 'nivel': 25, 'tipo_id': 1}

>>> validate_pokemon({"nombre": "Pikachu", "nivel": 999, "tipo_id": 1})
ValueError: nivel tiene que estar entre 1 y 100

>>> validate_pokemon({"nombre": "Pikachu", "tipo_id": 1})
ValueError: nivel es obligatorio y tiene que ser un número entero

>>> validate_pokemon({"nivel": 16}, partial=True)
{'nivel': 16}
```

---

## 5. Las operaciones CRUD — `crud.py`

Cada función valida (si hace falta), abre una sesión, trabaja con objetos y devuelve dicts. Fijate que el parámetro se llama `type_id` (inglés, es una variable de Python) pero la columna es `tipo_id` (como en el alcance). Quien llame a estas funciones no necesita saber nada de la base.

### Create

```python
def create_pokemon(data: dict) -> dict:
    clean = validate_pokemon(data)           # 1) validar (ValueError si está mal)
    with get_session() as s:
        pokemon = Pokemon(**clean)           # 2) objeto Python, todavía no está en la base
        s.add(pokemon)                        # 3) lo agrego a la sesión
        s.commit()                            # 4) recién acá se escribe (y se asigna el id)
        return pokemon.to_dict()               # ya tiene el id
```

- **`Pokemon(**clean)`**: el `**` desarma el dict en argumentos con nombre. Es lo mismo que `Pokemon(nombre="...", nivel=5, tipo_id=1)`.
- **`s.add()`** anota el objeto en la sesión; **`s.commit()`** ejecuta el `INSERT`. Después del commit, `pokemon.id` ya tiene el valor que asignó la base.
- **`with get_session() as s:`** cierra la sesión al salir del bloque, aunque haya un error.

### Read

```python
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
```

- **`select(Pokemon)`** arma la query (todavía no la ejecuta). Se le encadenan **`.where(...)`**, **`.order_by(...)`**, etc. Por eso se puede agregar el `where` solo si vino el filtro: es el patrón de **filtro opcional** que piden los endpoints de listado.
- **`Pokemon.tipo_id == type_id`** no es una comparación normal de Python: SQLAlchemy la convierte en `WHERE tipo_id = ?`. Otros que vas a usar: `Pokemon.nivel >= 10`, `Pokemon.nombre.like("%char%")`, `Pokemon.nombre.ilike(...)` (sin distinguir mayúsculas).
- **`s.scalars(query)`** ejecuta y devuelve los objetos uno por uno. Para traer todos en una lista: `s.scalars(query).all()`.
- **`s.get(Pokemon, id)`** busca por clave primaria. Devuelve `None` si no existe: en la API eso se traduce en un **404**.

### Read cruzando las dos tablas (la relationship)

Un `pokemon.to_dict()` te da `tipo_id = 1`, pero no te dice que el 1 es "Fuego". Sin ORM habría que escribir un `JOIN`. Con la `relationship()` que definimos en `db.py`, alcanza con `pokemon.pokemon_type`:

```python
def list_with_type() -> list[dict]:
    with get_session() as s:
        pokemons = s.scalars(select(Pokemon).order_by(Pokemon.id))
        return [p.to_dict() | {"tipo": p.pokemon_type.nombre} for p in pokemons]
```

`p.pokemon_type` es el objeto `PokemonType` completo, con `id` y `nombre`. El `|` une dos dicts. Ojo: `p.pokemon_type` solo funciona **adentro** del `with`, porque SQLAlchemy va a buscar el tipo a la base recién cuando lo pedís.

Para consultas más grandes (agrupar, contar, sumar) SQLAlchemy tiene `func.count()`, `func.sum()` y `.group_by()`. Pero para el integrador también vale traer los objetos y calcular en Python con un `for`.

### Update

```python
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
```

Acá se ve lo mejor del ORM: para modificar, **cambiás el atributo del objeto y hacés commit**. No hay que armar ningún `UPDATE ... SET`. `setattr(pokemon, "nivel", 16)` es lo mismo que `pokemon.nivel = 16`, pero con el nombre del campo en una variable, así sirve para cualquier campo que haya llegado.

### Delete

```python
def delete_pokemon(pokemon_id: int) -> bool:
    with get_session() as s:
        pokemon = s.get(Pokemon, pokemon_id)
        if pokemon is None:
            return False
        s.delete(pokemon)
        s.commit()
        return True
```

Primero se busca, después se borra. Devolver `True`/`False` le permite a la API responder 404 cuando no existía.

Las funciones de `tipos` (`create_type`, `list_types`, `get_type`, `delete_type`) son iguales pero más cortas. Están en [pokedex/crud.py](pokedex/crud.py).

---

## 6. Probarlo — `main.py`

```python
create_tables()

# CREATE: primero los tipos (tabla padre), después los pokemones
fire = crud.create_type({"nombre": "Fuego"})
water = crud.create_type({"nombre": "Agua"})
charmander = crud.create_pokemon({"nombre": "Charmander", "nivel": 5, "tipo_id": fire["id"]})
squirtle = crud.create_pokemon({"nombre": "Squirtle", "nivel": 7, "tipo_id": water["id"]})
crud.create_pokemon({"nombre": "Vulpix", "nivel": 12, "tipo_id": fire["id"]})

# READ
crud.list_pokemons()                       # todos
crud.list_pokemons(type_id=fire["id"])     # solo Fuego
crud.list_with_type()                        # con el nombre del tipo

# UPDATE
crud.update_pokemon(charmander["id"], {"nivel": 16})

# DELETE
crud.delete_pokemon(squirtle["id"])
```

El orden importa: **primero los tipos, después los pokemones**. Un pokémon necesita un `tipo_id` que ya exista. Lo mismo al borrar: no podés borrar un tipo mientras haya pokemones que lo usen.

Salida al correr `python main.py`:

```
Tipos creados: {'id': 1, 'nombre': 'Fuego'} {'id': 2, 'nombre': 'Agua'}
Pokémon creado: {'id': 1, 'nombre': 'Charmander', 'nivel': 5, 'tipo_id': 1}

Todos:
   {'id': 1, 'nombre': 'Charmander', 'nivel': 5, 'tipo_id': 1}
   {'id': 2, 'nombre': 'Squirtle', 'nivel': 7, 'tipo_id': 2}
   {'id': 3, 'nombre': 'Vulpix', 'nivel': 12, 'tipo_id': 1}

Solo de tipo Fuego:
   Charmander
   Vulpix

Con el nombre del tipo (relationship):
   {'id': 1, 'nombre': 'Charmander', 'nivel': 5, 'tipo_id': 1, 'tipo': 'Fuego'}
   {'id': 2, 'nombre': 'Squirtle', 'nivel': 7, 'tipo_id': 2, 'tipo': 'Agua'}
   {'id': 3, 'nombre': 'Vulpix', 'nivel': 12, 'tipo_id': 1, 'tipo': 'Fuego'}

Actualizado: {'id': 1, 'nombre': 'Charmander', 'nivel': 16, 'tipo_id': 1}

¿Se borró Squirtle? True
¿Existe todavía? None

Probando un nivel inválido...
Validación lo rechazó: nivel tiene que estar entre 1 y 100

Probando sin nombre...
Validación lo rechazó: nombre es obligatorio y no puede estar vacío

Probando un tipo_id que no existe...
La base lo rechazó: FOREIGN KEY constraint failed

Probando borrar un tipo que tiene pokemones...
La base lo rechazó: FOREIGN KEY constraint failed
```

Si lo corrés dos veces, la segunda va a fallar en `create_type({"nombre": "Fuego"})` porque el nombre es `unique` y ya está cargado. Borrá `pokedex.db` para empezar de cero. En el integrador, el `seed.py` resuelve esto cargando datos solo si la base está vacía.

---

## 7. Quién atrapa cada error

Los últimos bloques de la salida muestran algo importante: hay errores que atrapan **nuestras validaciones** y otros que atrapa **la base**. Conviene saber cuál es cuál para poner el `try/except` correcto.

| Error | Lo detecta | Excepción | Cuándo |
|---|---|---|---|
| Nivel 999, nombre vacío, falta un campo, `"abc"` donde va un número | `validation.py` | `ValueError` | Antes de tocar la base |
| `tipo_id` que no existe en `tipos` | La base (por la FK) | `sqlalchemy.exc.IntegrityError` | En el `commit()` del alta |
| Borrar un tipo que tiene pokemones | La base (por la FK) | `sqlalchemy.exc.IntegrityError` | En el `commit()` del borrado |
| Dos tipos con el mismo nombre | La base (por el `unique`) | `sqlalchemy.exc.IntegrityError` | En el `commit()` del alta |
| La base no existe, la tabla no existe | La base | `sqlalchemy.exc.OperationalError` | En cualquier query |

Nuestras validaciones no pueden saber si el tipo 999 existe porque no miran la base. La base no puede saber que el nivel máximo es 100 porque nadie se lo dijo. Cada uno controla lo suyo. Si querés, también podés chequear en `create_pokemon` que el tipo exista con `s.get(PokemonType, tipo_id)` antes del `add`, y dar un mensaje más lindo que el de la FK.

---

## 8. Cómo encaja en FastAPI

Cuando lo lleven al integrador, las funciones de `crud.py` quedan **igual**. Lo único que cambia es quién las llama: en vez de `main.py` con prints, las llama un endpoint.

Como no usamos modelos de Pydantic, el cuerpo del `POST` se recibe como un **`dict`** y lo validamos nosotros. Fijate cómo cada excepción o `None` de `crud.py` se convierte en un código HTTP:

```python
from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError

from db import create_tables
import crud

app = FastAPI()
create_tables()


@app.get("/pokemones")
def list_all(tipo_id: int | None = None):      # el nombre del parámetro ES el query param: ?tipo_id=1
    try:
        return crud.list_pokemons(type_id=tipo_id)
    except OperationalError:
        raise HTTPException(status_code=500, detail="Error al consultar la base")


@app.get("/pokemones/{pokemon_id}")
def detail(pokemon_id: int):
    pokemon = crud.get_pokemon(pokemon_id)
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return pokemon


@app.post("/pokemones", status_code=201)
def create(data: dict):
    try:
        return crud.create_pokemon(data)
    except ValueError as e:                       # falló una validación nuestra
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:                        # falló la FK o el unique
        raise HTTPException(status_code=400, detail="El tipo_id no existe")
```

| Lo que pasó en `crud.py` | Código HTTP |
|---|---|
| Devolvió `None` | **404** |
| Lanzó `ValueError` (validación) | **400** con el mensaje de la validación |
| Lanzó `IntegrityError` (FK, unique) | **400** |
| Lanzó `OperationalError` (la base no está) | **500**, pero la API sigue viva |
| Todo bien | **200** (o **201** en el alta) |

En `/docs`, el `POST` va a mostrar un cuerpo genérico (`{}`) porque FastAPI no sabe qué campos esperamos. Es normal: escribí el JSON a mano, por ejemplo `{"nombre": "Pikachu", "nivel": 25, "tipo_id": 1}`. Conviene documentar los campos esperados en el README.

> FastAPI trae Pydantic instalado por dentro, pero en este proyecto **no lo usamos**: las validaciones van a mano en `validation.py`.

---

## 9. Cómo queda el `seed.py`

Con el ORM, el seed es crear las tablas y agregar objetos si la base está vacía:

```python
from sqlalchemy import select
from db import create_tables, get_session, PokemonType, Pokemon

create_tables()

with get_session() as s:
    if s.scalars(select(PokemonType)).first() is None:   # ¿está vacía?
        fire = PokemonType(nombre="Fuego")
        water = PokemonType(nombre="Agua")
        s.add_all([fire, water])
        s.commit()                                        # ahora fire.id y water.id existen
        s.add_all([
            Pokemon(nombre="Charmander", nivel=5, tipo_id=fire.id),
            Pokemon(nombre="Squirtle", nivel=7, tipo_id=water.id),
            Pokemon(nombre="Vulpix", nivel=12, tipo_id=fire.id),
        ])
        s.commit()
        print("Datos cargados.")
    else:
        print("La base ya tenía datos.")
```

`s.add_all([...])` es `s.add()` para varios objetos a la vez. Primero los padres con su commit (para tener los `id`), después los hijos.

---

## 10. Errores comunes

- **Olvidarse el `commit()`.** Hacés `s.add()` y no aparece nada en la base. Sin `commit()` no se escribe.
- **Usar el objeto fuera del `with`.** `pokemon.pokemon_type` afuera de la sesión da `DetachedInstanceError`. Convertí a dict adentro del bloque.
- **Devolver el objeto de SQLAlchemy en FastAPI.** No es JSON. Devolvé `objeto.to_dict()`.
- **`ForeignKey("PokemonType.id")`.** Va el nombre de la **tabla** (`"tipos.id"`), no el de la clase.
- **Mandar el `id` al crear.** El id lo pone la base. Por eso `validate_pokemon` no lo acepta.
- **Confiar en que el tipo de la columna valida.** `Mapped[int]` no rechaza un `"25"` en texto ni un nivel 999. Lo hace `validation.py`.
- **`data["nombre"]` en vez de `data.get("nombre")`.** Si el campo no vino, rompe con `KeyError` en vez de dar un mensaje claro.
- **Cargar hijos antes que padres.** Primero `tipos`, después `pokemones`. Y en el seed, en ese orden.
- **Olvidarse el `PRAGMA foreign_keys = ON`.** La FK queda de adorno y podés cargar cualquier `tipo_id`.
- **Olvidarse `sqlalchemy` en `requirements.txt`.** Localmente anda porque lo instalaste, pero en Render falla el deploy.
