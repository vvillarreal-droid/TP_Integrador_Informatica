# Comentarios de la cátedra

Informática (TDS05) · Proyecto Integrador · UM Río Cuarto

Acá va la devolución de cada revisión semanal. Léanlo antes de seguir programando.
Primero está el alcance completo del proyecto; al final, la devolución de cada semana.

**Grupo:** Pablo Fernando Doblas, Ignacio Gabriel Carreño, Valentino Villarreal Ríos
**Tema:** Online Store — Clientes y pedidos (a confirmar)

---

# Alcances de este proyecto

Esto es lo que hay que entregar. Lo que no está acá, no se pide.

## Reglas comunes a todos los grupos

### Stack
- Python + **FastAPI** + Uvicorn.
- Datos en **SQLite**. Pueden usar **SQLAlchemy** (ORM, con la guía [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md)) o **`sqlite3` con SQL directo**: las dos formas valen. **Pydantic es opcional**: el cuerpo del `POST` se puede validar con un modelo de Pydantic (`class StudentIn(BaseModel)`) o a mano en `validation.py`. Las dos formas valen.
- Repositorio en GitHub con commits de **todos** los integrantes.
- **Demo local:** la API se corre en la notebook de cada grupo con `uvicorn`. No hace falta desplegarla en la web (ver *Demo local*, abajo).

### Nombres en el código (criterio acordado con la cátedra de Inglés)

> **Actualizado el 15/10:** los nombres de tablas, columnas y rutas en inglés pasan a ser una **recomendación**. Si quedan en español, no es un error.

- **Variables, funciones y clases en inglés**: `list_students`, `get_session`, `class Student(Base)`.
- **Tablas, columnas, rutas y query params:** se recomienda que también vayan en inglés (`__tablename__ = "students"`, columna `career_id`, ruta `GET /students`), pero pueden quedar en español, como figuran en el alcance.
- Lo que sí es obligatorio: usar **el mismo nombre en todos los archivos** (`models.py`, `seed.py`, `crud.py`, `main.py`, `validation.py`). Si la tabla se llama `estudiantes` en el seed, se llama `estudiantes` en todos lados.
- **Documentación en inglés**: `README.md`, docstrings y los mensajes que devuelve la API.
- **Comentarios**: pueden estar en español mientras desarrollan, pero para la **entrega final** tienen que estar en inglés.

### Demo local (sin despliegue)

> **Actualizado el 15/10:** no se despliega a producción. La defensa es **local**, en la notebook del grupo.

`requirements.txt` debe incluir:
```
fastapi
uvicorn
python-dotenv
```
y `sqlalchemy` si lo usan.

Para levantar el proyecto desde cero (lo mismo tiene que estar en el README):
```
python -m venv venv
venv\Scripts\activate          (en Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```
Y abrir http://127.0.0.1:8000/docs.

- El seed se corre **una vez, antes** de levantar el servidor. No va adentro de `main.py`.
- Antes de la defensa, prueben todo esto en la notebook con la que van a presentar.

### Base de datos
- **3 tablas**, cada una con clave primaria (`id`).
- Al menos **1 relación** entre tablas (clave foránea, ej. `equipo_id`).
- **Algunos datos de ejemplo** en cada tabla, los suficientes para ver funcionar los endpoints. No hay mínimo ni máximo. Siempre **datos ficticios**.
- Recomendación: que los datos permitan ver los filtros en acción, por ejemplo productos de varias categorías, para que `?category=` devuelva algo distinto de la lista completa.
- Un script de carga inicial `seed.py` que crea las tablas (con `create_all` o con `CREATE TABLE IF NOT EXISTS`) y carga los datos **solo si la base está vacía**. Se ejecuta antes de levantar el servidor y, si se corre dos veces, no duplica nada.
- El archivo `.db` **puede estar en el repo**. Si lo suben, que esté actualizado (el que genera el seed actual).

### Seguridad: TODOS los endpoints van protegidos

> **Actualizado el 15/10:** se **recomienda** guardar la clave en una variable de entorno en lugar de escribirla en el código. No es obligatorio; en la defensa se puede preguntar por qué conviene hacerlo.

- Todos los endpoints piden la API key en el encabezado `X-API-Key`.
- Sin clave o con clave incorrecta → **401**. Con la clave correcta → **200** y los datos.
- **Recomendado:** guardar la clave en un archivo **`.env`** que **no se sube** (va en el `.gitignore`) y leerla con `python-dotenv`. Al repo se sube un **`.env.example`** con el nombre de la variable y sin el valor. Paso a paso en [guias/variables_de_entorno.md](guias/variables_de_entorno.md). Si la dejan como constante en `security.py`, también vale.
- Los datos son todos **ficticios**: esta API no se usa para nada real.

`security.py` con la clave en el `.env` (la forma recomendada):

```python
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

load_dotenv()
API_KEY = os.getenv("API_KEY")
header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Depends(header)):
    if API_KEY is None or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

Y en `main.py` se protege toda la app de una vez:

```python
app = FastAPI(dependencies=[Depends(verify_api_key)])
```

En `/docs` usá el botón **Authorize** para cargar la clave y probar.
---

## Nivel A — obligatorio (igual para todos)

Cada grupo implementa **exactamente estos 6 endpoints**, adaptados a su tema (ver *Alcance de este grupo*):

| # | Tipo | Ejemplo genérico | Qué practica |
|---|---|---|---|
| 1 | Listado con filtro | `GET /cosas?campo=valor` | Query param y filtro en la consulta |
| 2 | Detalle | `GET /cosas/{id}` | Path param, **404** si no existe |
| 3 | Relación | `GET /cosas/{id}/otras` | Cruzar dos tablas por la clave foránea |
| 4 | Segundo listado con filtro | `GET /otras?campo=valor` | Query param sobre otra tabla |
| 5 | Calculado | `GET /resumen` | Contar, sumar o agrupar (en Python o en la consulta) |
| 6 | Alta | `POST /cosas` | Recibir el cuerpo (con un modelo de Pydantic o como `dict` validado a mano), rechazar los datos inválidos con **400** o **422**, e insertar en la base |

Además, en Nivel A:
- **Errores:** 401 (sin clave), 404 (no existe), y la API no se cae si la base no está o falla una consulta (`try/except`).
- **Filtros opcionales:** si no se manda el query param, devuelve todo.
- **Seguridad (recomendado):** API key en variable de entorno (`.env`) en lugar de escrita en el código.
- **README:** qué hace la API, lista de endpoints, cómo usar la API key, cómo correrla localmente, y declaración de uso de IA si la usaron.

## Nivel B — opcional

Existe un Nivel B que suma hasta 1 punto sobre la nota final. **No se preocupen por eso todavía:** lo vemos en clase más adelante, cuando el Nivel A esté andando.

---

## Alcance de este grupo

### Grupo 6 · Online Store — Clientes y pedidos
**Integrantes:** Pablo Fernando Doblas, Ignacio Gabriel Carreño, Valentino Villarreal Ríos

**Tablas**
- `clientes`: id, nombre, email, ciudad
- `productos`: id, nombre, categoria, precio
- `pedidos`: id, fecha, estado (pendiente / enviado / entregado), total, cliente_id (FK)

**Endpoints Nivel A**
1. `GET /productos?categoria=electronica`
2. `GET /clientes/{id}`
3. `GET /clientes/{id}/pedidos`
4. `GET /pedidos?estado=pendiente`
5. `GET /clientes/ranking` → clientes ordenados por total gastado
6. `POST /clientes`


---

## Fuera de alcance (para todos)

No se pide y **no suma**:
- Frontend o páginas web.
- Login de usuarios, registro, JWT.
- Bases de datos externas (PostgreSQL, MySQL, etc.).
- Docker.
- Integración con IA o con el chatbot (eso corresponde a Análisis de Sistemas).
- Pagos, facturación, envío de mails, hardware real.

## Entregables

1. Repositorio GitHub: `main.py`, script de seed, `requirements.txt`, `README.md`, commits de todos.
2. Video demo (máx. 5 min): endpoints funcionando con clave, y un pedido **sin** clave mostrando el 401.
3. Defensa oral el **miércoles 28/10**: demo en vivo desde `/docs`, en local, y preguntas sobre el código. El repositorio tiene que estar al día el **miércoles 21/10**.

---

# Devolución semanal

## 23/09

**📌 Novedad:** la base se maneja con **SQLAlchemy** (ORM) y **sin Pydantic**; las validaciones del `POST` van a mano. Hay una guía con ejemplo completo en [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md) y el código en `guias/pokedex/`. Agreguen `sqlalchemy` a `requirements.txt`.

**Lo que hay:** 19 commits, pero sin código que funcione: `archivito.py` es un `print("Hola")`, `Online_Store.py` tiene solo un comentario y el README dice "hola".

**Hoy (23/09):** renombraron `archivito.py` a `principal.py`, pero el archivo quedó **vacío**. Además el archivo principal tiene que llamarse `main.py`, porque el arranque en producción es `gunicorn main:app`.

**A corregir**
- Confirmen el tema. Se los asigné como Online Store orientada a clientes por el nombre del archivo y el commit de la base de clientes.
- Los commits tienen que decir qué se hizo. "Prueba" y "lalalalla" no sirven para mostrar el avance.
- El README tiene que explicar qué hace la API, no decir "hola".

**Próximos pasos**
1. `main.py` con FastAPI levantando y `/docs` abriendo.
2. `seed.py` con las 3 tablas: `clientes`, `productos`, `pedidos` (con `cliente_id`).
3. Son tres: repártanse una tabla y dos endpoints cada uno.

## 24/09

**📌 Criterio de nombres.** Variables, funciones y clases en **inglés**; tablas, columnas y rutas como en el alcance; comentarios en inglés para la entrega final. Está detallado arriba en *Reglas comunes* y la guía ya lo aplica.

**Lo que hay:** README nuevo que describe bien el proyecto, y `Online_Store.py` con una tabla `Clients` en SQLite. `main.py` y `seed.py` siguen **vacíos**. Ahora hay commits de Pablo y Valentino; **faltan los de Ignacio**.

**A corregir**
- `Online_Store.py` es un programa de consola: pide nombre y DNI con `input()` y los guarda. Eso no sirve para la API, que no tiene consola. Los datos se cargan desde `seed.py` y se consultan desde los endpoints.
- La tabla `Clients` tiene solo `name_costumer` y `dni`. El alcance pide `clientes`: id, nombre, email, ciudad. Y faltan `productos` y `pedidos` (con `cliente_id`).
- El nombre de la base es `Base_of_Date.db`. Un nombre corto y sin mayúsculas: `tienda.db`.
- **La base va con SQLAlchemy** (ver [guias/sqlalchemy_orm.md](guias/sqlalchemy_orm.md)): tablas como clases, sin `cursor.execute` ni SQL a mano.
- El README dice "at least six endpoints": son **exactamente** los 6 del alcance (arriba en este archivo). Falta también `requirements.txt`.

**Próximos pasos**
1. Borrar `Online_Store.py` y escribir `seed.py` con SQLAlchemy: `clientes`, `productos`, `pedidos` con `cliente_id`, ~10 registros cada una, carga solo si está vacía.
2. `main.py` con `app = FastAPI()` y `GET /productos?categoria=` andando en `/docs`.
3. `requirements.txt` con `fastapi`, `uvicorn`, `uvicorn-worker`, `gunicorn`, `sqlalchemy`.
4. Ignacio: tu primer commit tiene que aparecer esta semana.

## 08/10

**📌 Cambio de criterio: todo en inglés.** Ahora también las **tablas, columnas, rutas y query params** van en inglés, igual que el README, los docstrings y los mensajes de la API. Reemplaza lo dicho el 24/09; está detallado arriba en *Nombres en el código*. El alcance sigue listando los nombres en español solo como referencia.

**📌 Guía nueva (opcional):** [guias/variables_de_entorno.md](guias/variables_de_entorno.md), para sacar la clave del código con un `.env`.

**Lo que hay:** primera versión que funciona. 👍 Probé la API: la clave anda (401 sin clave o con clave mala), `GET /productos` lista y `GET /productos/{producto_id}` devuelve el producto o un 404. `crearbase.py` crea la tabla con clave primaria y no duplica si se corre dos veces. Ignacio: ya aparecieron tus commits.

**⚠️ Desde el 24/09 solo hay commits de Ignacio.** Pablo y Valentino: los commits tienen que mostrar el aporte de los tres.

**⚠️ La base va con SQLAlchemy.** Es la tercera devolución en que lo marco. `main.py` y `crearbase.py` usan `sqlite3` con `cursor.execute` y SQL a mano. Tienen que ser clases en `db.py` y consultas con `select(...)`, como en la [guía](guias/sqlalchemy_orm.md). El ejemplo de `guias/pokedex/` se puede copiar y adaptar.

**⚠️ Falta casi todo el alcance.** Hay 1 tabla de 3 y, de los 6 endpoints, ninguno completo:

| # | Alcance | Estado |
|---|---|---|
| 1 | `GET /productos?categoria=` | Está el listado, **falta el filtro**: `?categoria=Lácteos` devuelve todo |
| 2 | `GET /clientes/{id}` | Falta (no existe la tabla `clientes`) |
| 3 | `GET /clientes/{id}/pedidos` | Falta (no existe la tabla `pedidos`) |
| 4 | `GET /pedidos?estado=pendiente` | Falta |
| 5 | `GET /clientes/ranking` | Falta |
| 6 | `POST /clientes` | Falta |

El tema del grupo son **clientes y pedidos**: cinco de los seis endpoints salen de esas dos tablas. `GET /productos/{id}` no está en el alcance; pueden dejarlo, pero no cuenta.

**A corregir**
- **Nombres en inglés** (criterio nuevo). Hoy está todo en español: funciones (`listar_productos`, `obtener_conexion`), variables (`CLAVE`, `fila`), tabla, columnas, rutas, comentarios y mensajes. Tiene que ser `list_products`, `API_KEY`, tablas `customers`, `products`, `orders`, columnas `name`, `email`, `city`, `category`, `price`, `date`, `status`, `total`, `customer_id`, y rutas `/products`, `/customers/{id}`, `/customers/{id}/orders`, `/orders?status=`, `/customers/ranking`.
- Si no se corrió `crearbase.py` antes, la API devuelve **500** en vez de un mensaje claro. Falta el `try/except`.
- `seed.py` está vacío y la carga está en `crearbase.py`. Tiene que llamarse `seed.py`: el arranque en Render es `python seed.py && gunicorn ...`.
- La base se llama `productos.bd`. La extensión es `.db`, y el nombre conviene que sea el del proyecto: `store.db`. Agreguen `*.db` al `.gitignore`, que hoy no la cubre.
- `Online_Store.py` sigue en el repo (pedí borrarlo el 24/09). Es un programa de consola con `input()` y no forma parte de la API.
- Sigue faltando `requirements.txt`. Sin eso no se puede desplegar.
- Hay 5 productos. Se piden unos 10 registros por tabla.
- Los commits se llaman "Create crearbase.py" y "Update main.py", que son los nombres que pone GitHub cuando se sube un archivo desde la web. Trabajen con `git` desde la compu (`add`, `commit`, `push`) y con un mensaje que diga qué cambiaron.

**Próximos pasos**
1. `db.py` con las tres clases (`Customer`, `Product`, `Order` con `customer_id` como `ForeignKey`).
2. `seed.py` con SQLAlchemy: ~10 registros por tabla, carga solo si está vacía. Borrar `crearbase.py` y `Online_Store.py`.
3. Pasar los dos endpoints que ya tienen a SQLAlchemy y agregar el filtro por categoría.
4. `requirements.txt` con `fastapi`, `uvicorn`, `uvicorn-worker`, `gunicorn`, `sqlalchemy`.
5. Repártanse: uno la tabla y los endpoints de clientes (2 y 6), otro los de pedidos (3 y 4), otro productos y el ranking (1 y 5).

## 10/10

**Lo que hay:** 20 commits en una tarde, de Valentino e Ignacio. 👍 Siguieron la estructura que armamos en clase: la lógica de la base pasó a `crud.py` y la clave a `security.py`. `security.py` está bien: lo probé y responde 401 sin clave o con clave mala. Valentino: bien por los mensajes de commit que dicen qué se hizo, por los comentarios que explican el código y por dejar escrito dónde usaste IA.

**⚠️ La API dejó de arrancar.** El 08/10 levantaba y respondía dos endpoints. Hoy `uvicorn main:app` falla antes de empezar, porque `main.py` y `crud.py` tienen errores de sintaxis. Ninguno de los 20 commits se probó antes de subirlo.

**⚠️ Prueben antes de cada commit.** Ignacio: tus diez commits se llaman "Update main.py" o "Update crud.py", que es el nombre que pone GitHub cuando se edita desde la web. Desde el navegador no se puede ejecutar nada, y por eso se subió código que no corre. Hay que trabajar en la compu: clonar, editar, levantar con `uvicorn main:app --reload`, probar en `/docs` y recién ahí hacer `commit` y `push`.

**Sobre los commits de Pablo.** No hay commits suyos desde el 24/09. Si están trabajando juntos en una misma compu (*pair coding*), está perfecto, pero **aclárenlo en el mensaje del commit**, así queda registrado quién participó:
```
git commit -m "Add product filter by category (pair coding with Pablo)"
```

**A corregir en `main.py`**
- Después de `@app.get(...)` va la **definición** de una función, no una llamada. Esto es un error de sintaxis:
  ```python
  @app.get("/productos")
  listar_productos()
  ```
  El endpoint es una función propia, que adentro llama a la de `crud.py`. Abajo va el ejemplo completo.
- `main.py` no importa las funciones que usa. Importa `funcion_crud_1`, `funcion_crud_2` y `funcion_crud_3`, que eran solo el ejemplo de clase. Borren esas tres y los `/endpoint_1`, `/endpoint_2` y `/endpoint_3`.
- `obtener_producto` sigue usando `obtener_conexion()`, que ya no está en `main.py`. Esa consulta va en `crud.py`.
- Crear un pedido no puede ser un `GET`: las altas van con `POST`.

**A corregir en `crud.py`**
- **No tiene ningún `import`.** Usa `sqlite3`, `datetime`, `Optional`, `Query` y `HTTPException` sin importarlos.
- **La conexión se llama de tres formas distintas.** `obtener_conexion()` devuelve dos cosas (`con, cur`), pero después se usa como `con = obtener_conexion()`, en otras funciones se llama `SQLite3()` (que no existe), y el cursor aparece como `cur` y como `cursor`. Elijan una sola forma y úsenla en todas las funciones.
- `sqlite3.connect(productos.bd)` va entre comillas: `"productos.bd"`.
- `listar_productos` está definida dos veces.
- `filtrar_productos`: falta una coma entre los dos parámetros, `Optinal` está mal escrito, filtra por una columna `producto` que no existe (es `nombre`) y **no devuelve nada** (falta el `return`). `Query(...)` es de FastAPI y va en `main.py`, no acá.
- `con.close` sin paréntesis no cierra nada: es `con.close()`.
- `pedido_compra`: `OrderCreate` no está definido en ningún lado (y es un modelo de Pydantic, que no usamos: el cuerpo llega como `dict` y se valida a mano), `BEGIN ORDER;` no es SQL válido, y `precio_unitario` nunca se define.
- `reporte_ventas` devuelve `productos_mas_vendidos`, pero la variable se llama `mas_vendidos`.
- Las dos últimas usan las tablas `pedidos` e `items_pedido` y la columna `stock`, que el seed no crea.
- `crud.py` no lanza `HTTPException`: devuelve `None` o lanza `ValueError`, y el que decide el código HTTP es `main.py`. Está en [guias/estructura_del_proyecto.md](guias/estructura_del_proyecto.md).

**Cómo tiene que quedar un endpoint.** Este ejemplo está probado. Arranquen de acá y agreguen de a uno:

```python
# crud.py
import sqlite3

DB_FILE = "store.db"


def get_connection():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con


def list_products(category=None):
    con = get_connection()
    if category is not None:
        rows = con.execute("SELECT * FROM products WHERE category = ?", (category,)).fetchall()
    else:
        rows = con.execute("SELECT * FROM products").fetchall()
    con.close()
    return [dict(row) for row in rows]
```

```python
# main.py
from fastapi import FastAPI, Depends

import crud
from security import verify_api_key

app = FastAPI(title="Online Store API", dependencies=[Depends(verify_api_key)])


@app.get("/products")
def list_products(category: str = None):
    return crud.list_products(category)
```

**A corregir en el resto**
- `seed.py` no cambió: crea solo la tabla de productos, con 5 registros y sin la columna `stock`. Tiene que crear **todas las tablas que usan sus funciones** (hoy faltan las de pedidos e items) y cargar unos 10 registros por tabla.
- `db.py` todavía tiene el programa de consola viejo, con `input()`. Bórrenle todo: ahí va solamente `get_connection()`.
- **Nombres en inglés.** Sigue todo en español: funciones, variables, tablas, columnas, rutas y mensajes. Como hay que reescribir casi todo, es el momento de hacerlo.
- Sigue faltando `requirements.txt`. Es la cuarta devolución en que lo marco, y sin eso no se puede desplegar.
- La base se sigue llamando `productos.bd`. Es `.db`; agreguen `*.db` al `.gitignore`.
- Sigue pendiente pasar la base a SQLAlchemy (`models.py` está vacío). Primero hagan que arranque.

**Próximos pasos**
1. Que `uvicorn main:app --reload` levante. Dejen en `main.py` y `crud.py` solo lo que funciona (el ejemplo de arriba) y saquen el resto.
2. `seed.py` con todas las tablas que usan sus funciones, en inglés y con ~10 registros cada una.
3. Agregar los endpoints **de a uno**, probando cada uno en `/docs` antes de pasar al siguiente. Empiecen por los más simples: el listado con filtro y el detalle por id con 404.
4. `requirements.txt` con `fastapi`, `uvicorn`, `uvicorn-worker`, `gunicorn`, `sqlalchemy`.
5. Repártanse los endpoints entre los tres. Si trabajan de a dos en una compu, pónganlo en el mensaje del commit.

## 15/10

**📌 Cambios en las reglas** (están arriba, en *Reglas comunes*):
- **SQLAlchemy es opcional:** también vale `sqlite3` con SQL directo.
- **No hay que desplegar.** La defensa es **local**, en su notebook, el **miércoles 28/10**. El repo tiene que estar al día el **miércoles 21/10**.
- **Recomendado:** la API key en una variable de entorno (`.env`) en lugar de escrita en el código. No es obligatorio, pero en la defensa se puede preguntar dónde está la clave y por qué conviene sacarla del código.

**Lo que hay:** se corrigieron los errores de sintaxis del 10/10: ahora `uvicorn main:app` arranca. 👍 Pablo reescribió el README en inglés (con declaración de IA), creó `requirements.txt` y arregló el `.gitignore`. La clave se lee de una variable de entorno y da 401 sin clave o con clave mala. El seed no duplica. Bien también por avisar del *pair coding* en un commit.

**⚠️ El único endpoint que responde es `GET /`.** Todos los que consultan la base dan **500**, porque `crud.py` sigue con los problemas del 10/10:
- No tiene **ningún `import`**: usa `sqlite3`, `datetime` y `HTTPException` sin importarlos.
- Llama a `obtener_conexion()` sin guardar el resultado, y después usa `con` y `cur`, que no existen.
- Usa las tablas `pedidos` e `items_pedido` y la columna `stock`, que el seed no crea (el seed crea solo `productos`, con 5 filas).

Siguen además los `/endpoint_1`, `/endpoint_2` y `/endpoint_3`, que llaman a funciones que no existen.

**La clave:** `security.py` usa `os.environ.get("API_KEY")` pero no carga el `.env`, así que si no la exportan a mano en la terminal, todo da 401, incluso con la clave correcta. Agreguen `from dotenv import load_dotenv` y `load_dotenv()` (ver *Seguridad*, arriba). El `.env.example` tiene un espacio y comillas de más (`API_KEY= "Almacen-Nosotros"`): tiene que ser `API_KEY=` sin valor. Y el README da dos claves distintas.

**El README describe una API que no existe.** Lista `/categorias`, `/productos/bajo-stock`, `POST /pedidos` y `/ventas`, filtros por precio y un archivo de log, y dice que el seed corre solo. Tiene que describir lo que realmente hay.

**Lo mínimo para tener algo que defender el 28/10**, en este orden:
1. Arreglar `crud.py` con el ejemplo probado del 10/10: un `import sqlite3` arriba y `con = get_connection()` en cada función. Con eso andan `GET /productos` y `GET /productos/{id}` con su 404.
2. Borrar `/endpoint_1..3` y las `funcion_crud_1..3`.
3. Agregar al seed las tablas que usan (`pedidos` con su clave foránea, y la columna `stock`), con algunos datos en cada una.
4. Un endpoint que **calcule** algo (el reporte de ventas, por ejemplo) y un **filtro** con query param.
5. `try/except` en las consultas, para que un error de base no dé 500 sin control.
6. README que describa solo lo que funciona.

Prueben **cada** endpoint en `/docs` antes de hacer commit. La defensa es una demo en vivo: va a contar lo que funcione, no lo que esté escrito.
