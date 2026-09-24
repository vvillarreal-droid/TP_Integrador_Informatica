# Guía · Pydantic + SQLite con una Pokédex

Informática (TDS05) · Universidad de Mendoza · Sede Río Cuarto

Esta guía muestra cómo combinar **Pydantic** (para validar datos) con **SQLite** (para guardarlos) en un ejemplo chico: una Pokédex con dos tablas relacionadas. Es el mismo patrón que necesitan para el Proyecto Integrador, solo que con 2 tablas en vez de 3.

El código completo está en la carpeta [pokedex/](pokedex/). Se puede correr directo con `python main.py`, no hace falta FastAPI para probarlo.

---

## 1. Quién hace qué

| Herramienta | Para qué sirve | Qué NO hace |
|---|---|---|
| **Pydantic** | Define la "forma" de los datos y **valida** que lo que llega sea correcto (tipos, rangos, campos obligatorios). | No guarda nada. Los datos viven en memoria y se pierden al cerrar el programa. |
| **SQLite** | **Guarda** los datos en un archivo `.db` con tablas, claves primarias y foráneas. | No valida reglas de negocio (ej. "nivel entre 1 y 100"). Solo tipos básicos y las restricciones que pongas en el `CREATE TABLE`. |

La idea es que cada dato pase primero por Pydantic (¿es válido?) y recién después por SQLite (guardalo). Así la base nunca recibe basura.

```
   dato de entrada  ──►  modelo Pydantic  ──►  función CRUD  ──►  SQLite
   (dict, JSON)          (valida)              (SQL)              (pokedex.db)
```

---

## 2. Estructura del proyecto

```
pokedex/
├── db.py        ← conexión y creación de tablas
├── modelos.py   ← modelos Pydantic
├── crud.py      ← funciones Create / Read / Update / Delete
├── main.py      ← programa de prueba
└── pokedex.db   ← se genera solo (no va al repo)
```

Separar en archivos no es obligatorio, pero ayuda a no mezclar SQL con validaciones. En el integrador, `main.py` sería la API de FastAPI y llamaría a las funciones de `crud.py`.

---

## 3. Las tablas — `db.py`

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
```

Tres detalles que importan:

- **`INTEGER PRIMARY KEY AUTOINCREMENT`**: el `id` lo asigna SQLite solo. Nunca lo mandás vos al insertar.
- **`PRAGMA foreign_keys = ON`**: por defecto SQLite **ignora** las claves foráneas. Sin esta línea podés cargar un pokémon con `tipo_id = 999` aunque ese tipo no exista, y no se queja. Hay que ejecutarla en **cada** conexión, por eso está dentro de `conectar()`.
- **`row_factory = sqlite3.Row`**: sin esto, cada fila es una tupla `(1, 'Charmander', 5, 1)` y tenés que acordarte qué posición es qué. Con esto, la fila se puede convertir con `dict(fila)` y pasar directo a Pydantic.
- **`with conectar() as con:`**: al salir del bloque hace `commit()` automáticamente si todo salió bien, y `rollback()` si hubo un error. Así no te olvidás de confirmar los cambios.

---

## 4. Los modelos — `modelos.py`

Un modelo Pydantic es una clase que hereda de `BaseModel` y declara sus campos con tipos. Cuando creás un objeto, Pydantic **verifica** que cada campo tenga el tipo correcto y cumpla las reglas. Si algo falla, lanza `ValidationError` y el objeto no se crea.

```python
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
```

### ¿Por qué tres modelos por tabla y no uno?

Porque los datos no tienen la misma forma en cada momento:

| Modelo | Cuándo se usa | ¿Tiene `id`? |
|---|---|---|
| `PokemonCrear` | Cuando llega un pokémon nuevo (un `POST`). | **No**, todavía no existe en la base. |
| `Pokemon` | Cuando lo leés de la base o lo devolvés. | **Sí**, lo asignó SQLite. |
| `PokemonActualizar` | Cuando modificás (un `PUT`). Todo opcional. | No, el id va en la URL. |

`Pokemon` hereda de `PokemonCrear`, así que tiene los mismos campos más el `id`. No hace falta repetirlos.

### `Field`: las reglas de cada campo

| Regla | Significa |
|---|---|
| `min_length=1` | el texto no puede estar vacío |
| `max_length=50` | como mucho 50 caracteres |
| `ge=1` | *greater or equal*: mayor o igual a 1 |
| `le=100` | *less or equal*: menor o igual a 100 |
| `default=None` | el campo es opcional |

Probalo en la consola:

```python
>>> from modelos import PokemonCrear
>>> PokemonCrear(nombre="Pikachu", nivel=25, tipo_id=1)
PokemonCrear(nombre='Pikachu', nivel=25, tipo_id=1)

>>> PokemonCrear(nombre="Pikachu", nivel="25", tipo_id=1)   # "25" como texto
PokemonCrear(nombre='Pikachu', nivel=25, tipo_id=1)         # lo convierte a int

>>> PokemonCrear(nombre="Pikachu", nivel=999, tipo_id=1)
ValidationError: nivel  Input should be less than or equal to 100

>>> PokemonCrear(nombre="Pikachu", tipo_id=1)
ValidationError: nivel  Field required
```

### Dos métodos que vas a usar todo el tiempo

- **`modelo.model_dump()`** → convierte el modelo en un `dict`. Sirve para sacarle los valores y mandarlos a SQL.
- **`Modelo(**dict(fila))`** → arma un modelo a partir de un diccionario. Sirve para convertir una fila de SQLite en un objeto Pydantic. El `**` desarma el dict en argumentos con nombre.

---

## 5. Las operaciones CRUD — `crud.py`

Cada función recibe o devuelve modelos Pydantic, y adentro habla SQL con la base. Quien llame a estas funciones no necesita saber SQL.

### Create

```python
def crear_pokemon(datos: PokemonCrear) -> Pokemon:
    with conectar() as con:
        cur = con.execute(
            "INSERT INTO pokemones (nombre, nivel, tipo_id) VALUES (?, ?, ?)",
            (datos.nombre, datos.nivel, datos.tipo_id),
        )
        # model_dump() convierte el modelo en dict -> le sumamos el id que asignó SQLite
        return Pokemon(id=cur.lastrowid, **datos.model_dump())
```

- Recibe un `PokemonCrear` (sin id) y devuelve un `Pokemon` (con id).
- **`cur.lastrowid`** es el `id` que SQLite le acaba de asignar a la fila insertada.
- Los **`?`** son marcadores de posición. Los valores van aparte en una tupla. **Nunca** armes el SQL con f-strings metiendo los datos adentro (`f"... VALUES ('{nombre}')"`): si alguien manda una comilla en el nombre, te rompe la consulta o peor.

### Read

```python
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
```

- **`fetchall()`** trae todas las filas (lista). **`fetchone()`** trae una sola, o `None` si no hay.
- `obtener_pokemon` devuelve `None` cuando no existe. En la API eso se traduce en un **404**.
- El filtro opcional (`tipo_id=None`) es el mismo patrón que piden los endpoints de listado del integrador: si no mandan el parámetro, devuelve todo.
- Ojo con la tupla de un solo valor: es `(tipo_id,)` con coma. Sin la coma, `(tipo_id)` es solo un número entre paréntesis.

### Read cruzando las dos tablas (JOIN)

Un `SELECT * FROM pokemones` te da `tipo_id = 1`, pero no te dice que el 1 es "Fuego". Para eso se cruzan las tablas:

```python
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
```

`JOIN tipos t ON t.id = p.tipo_id` dice: "por cada pokémon, buscá el tipo cuyo `id` coincida con su `tipo_id`". Como las dos tablas tienen una columna `nombre`, hay que renombrar una con `AS tipo` para que no se pisen.

### Update

```python
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
```

Esta es la más elaborada. Como `PokemonActualizar` tiene todo opcional, `model_dump(exclude_none=True)` devuelve **solo los campos que llegaron**. Si mandaron `{"nivel": 16}`, el SQL queda `UPDATE pokemones SET nivel = ? WHERE id = ?`. Si mandaron nombre y nivel, queda `SET nombre = ?, nivel = ?`.

Acá sí se usa un f-string, pero solo para los **nombres de columna**, que salen del modelo Pydantic y no del usuario. Los **valores** siguen yendo con `?`.

Si te resulta complicado, la versión simple es exigir todos los campos (usar `PokemonCrear` en vez de `PokemonActualizar`) y hacer siempre `SET nombre = ?, nivel = ?, tipo_id = ?`. Es válido, solo que el que actualiza tiene que mandar todo.

### Delete

```python
def borrar_pokemon(pokemon_id: int) -> bool:
    with conectar() as con:
        cur = con.execute("DELETE FROM pokemones WHERE id = ?", (pokemon_id,))
        return cur.rowcount > 0
```

**`cur.rowcount`** es la cantidad de filas afectadas. Si es 0, no existía ese id. Devolver `True`/`False` le permite a la API responder 404 cuando corresponde.

Las funciones de `tipos` (`crear_tipo`, `listar_tipos`, `obtener_tipo`, `borrar_tipo`) son iguales pero más cortas. Están en [pokedex/crud.py](pokedex/crud.py).

---

## 6. Probarlo — `main.py`

```python
crear_tablas()

# CREATE: primero los tipos (tabla padre), después los pokemones
fuego = crud.crear_tipo(TipoCrear(nombre="Fuego"))
agua = crud.crear_tipo(TipoCrear(nombre="Agua"))
charmander = crud.crear_pokemon(PokemonCrear(nombre="Charmander", nivel=5, tipo_id=fuego.id))
squirtle = crud.crear_pokemon(PokemonCrear(nombre="Squirtle", nivel=7, tipo_id=agua.id))
crud.crear_pokemon(PokemonCrear(nombre="Vulpix", nivel=12, tipo_id=fuego.id))

# READ
crud.listar_pokemones()                  # todos
crud.listar_pokemones(tipo_id=fuego.id)  # solo Fuego
crud.listar_con_tipo()                   # con el nombre del tipo

# UPDATE
crud.actualizar_pokemon(charmander.id, PokemonActualizar(nivel=16))

# DELETE
crud.borrar_pokemon(squirtle.id)
```

El orden importa: **primero los tipos, después los pokemones**. Un pokémon necesita un `tipo_id` que ya exista. Lo mismo al borrar: no podés borrar un tipo mientras haya pokemones que lo usen.

Salida al correr `python main.py`:

```
Tipos creados: nombre='Fuego' id=1 nombre='Agua' id=2
Pokémon creado: nombre='Charmander' nivel=5 tipo_id=1 id=1

Todos:
   nombre='Charmander' nivel=5 tipo_id=1 id=1
   nombre='Squirtle' nivel=7 tipo_id=2 id=2
   nombre='Vulpix' nivel=12 tipo_id=1 id=3

Solo de tipo Fuego:
   Charmander
   Vulpix

Con el nombre del tipo (JOIN):
   {'id': 1, 'nombre': 'Charmander', 'nivel': 5, 'tipo': 'Fuego'}
   {'id': 2, 'nombre': 'Squirtle', 'nivel': 7, 'tipo': 'Agua'}
   {'id': 3, 'nombre': 'Vulpix', 'nivel': 12, 'tipo': 'Fuego'}

Actualizado: nombre='Charmander' nivel=16 tipo_id=1 id=1

¿Se borró Squirtle? True
¿Existe todavía? None

Probando un nivel inválido...
Pydantic lo rechazó: Input should be less than or equal to 100

Probando un tipo_id que no existe...
SQLite lo rechazó: FOREIGN KEY constraint failed

Probando borrar un tipo que tiene pokemones...
SQLite lo rechazó: FOREIGN KEY constraint failed
```

Si lo corrés dos veces, la segunda va a fallar en `crear_tipo("Fuego")` porque el nombre es `UNIQUE` y ya está cargado. Borrá `pokedex.db` para empezar de cero. En el integrador, el `seed.py` resuelve esto cargando datos solo si la base está vacía.

---

## 7. Quién atrapa cada error

Los tres últimos bloques de la salida muestran algo importante: hay errores que atrapa **Pydantic** y otros que atrapa **SQLite**. Conviene saber cuál es cuál para poner el `try/except` correcto.

| Error | Lo detecta | Excepción | Cuándo |
|---|---|---|---|
| Nivel 999, nombre vacío, falta un campo, `"abc"` donde va un número | Pydantic | `ValidationError` | Al crear el modelo, **antes** de tocar la base |
| `tipo_id` que no existe en `tipos` | SQLite (por la FK) | `sqlite3.IntegrityError` | Al hacer el `INSERT` |
| Borrar un tipo que tiene pokemones | SQLite (por la FK) | `sqlite3.IntegrityError` | Al hacer el `DELETE` |
| Dos tipos con el mismo nombre | SQLite (por el `UNIQUE`) | `sqlite3.IntegrityError` | Al hacer el `INSERT` |
| La base no existe, la tabla no existe | SQLite | `sqlite3.OperationalError` | En cualquier consulta |

Pydantic no puede saber si el tipo 999 existe porque no mira la base. SQLite no puede saber que el nivel máximo es 100 porque nadie se lo dijo. Cada uno controla lo suyo.

---

## 8. Cómo encaja en FastAPI

Cuando lo lleven al integrador, las funciones de `crud.py` quedan **igual**. Lo único que cambia es quién las llama: en vez de `main.py` con prints, las llama un endpoint. FastAPI ya usa Pydantic por debajo, así que el modelo `PokemonCrear` sirve directo como cuerpo del `POST`, y la validación la hace solo (un nivel 999 responde **422** sin que escribas nada).

```python
import sqlite3
from fastapi import FastAPI, HTTPException
from modelos import Pokemon, PokemonCrear
import crud

app = FastAPI()


@app.get("/pokemones")
def listar(tipo_id: int | None = None) -> list[Pokemon]:
    return crud.listar_pokemones(tipo_id)


@app.get("/pokemones/{pokemon_id}")
def detalle(pokemon_id: int) -> Pokemon:
    pokemon = crud.obtener_pokemon(pokemon_id)
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return pokemon


@app.post("/pokemones", status_code=201)
def crear(datos: PokemonCrear) -> Pokemon:
    try:
        return crud.crear_pokemon(datos)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El tipo_id no existe")
```

Fijate cómo cada `None` o `False` de `crud.py` se convierte en un código HTTP: `None` → 404, `IntegrityError` → 400, `ValidationError` → 422 (automático).

---

## 9. Errores comunes

- **Olvidarse el `PRAGMA foreign_keys = ON`.** La FK queda de adorno y podés cargar cualquier `tipo_id`. Si lo probás y no falla con un id inexistente, es esto.
- **Mandar el `id` al insertar.** El id lo pone SQLite. Por eso el modelo `PokemonCrear` no lo tiene.
- **Armar SQL con f-strings o `+`.** Usá `?` y la tupla de valores. Siempre.
- **`(valor)` en vez de `(valor,)`.** Una tupla de un elemento lleva coma.
- **Cargar hijos antes que padres.** Primero `tipos`, después `pokemones`. Y en el seed, en ese orden.
- **Devolver el `sqlite3.Row` directo en FastAPI.** No es un dict ni un modelo. Convertilo: `Pokemon(**dict(fila))`.
- **Un solo modelo para todo.** Si `Pokemon` tiene `id: int` obligatorio, no podés usarlo para el `POST`, porque el que crea no conoce el id todavía. Por eso `PokemonCrear` va aparte.
