# Guía · Cómo escribir un `README.md`

Informática (TDS05) · Universidad de Mendoza · Sede Río Cuarto

El `README.md` es lo primero que ve alguien que entra a tu repo. Tiene que responder tres preguntas: **qué es esto, cómo lo levanto y cómo lo uso**. Si una persona que no te conoce puede hacer andar el proyecto leyendo solo el README, está bien escrito.

Según el criterio del curso, el README va **en inglés**.

---

## 1. Qué tiene que tener

| Sección | Qué responde |
|---|---|
| Título y descripción | Qué hace el proyecto, en dos o tres líneas |
| Autores | Quiénes lo hicieron |
| Requisitos | Qué hay que tener instalado antes |
| Cómo levantarlo | Los comandos, en orden, para que ande en una compu nueva |
| Cómo usarlo | La clave, los endpoints y un ejemplo |
| Deploy | La URL pública |
| Uso de IA | Si usaron IA, para qué |

No hace falta más. Un README corto y que funciona es mejor que uno largo.

## 2. Markdown en un minuto

El archivo es texto común con algunas marcas:

```
# Título            ## Subtítulo
**negrita**         `código en la línea`
- ítem de lista     1. ítem numerado
[texto](https://link.com)
```

Los comandos van en un **bloque de código**, entre tres acentos graves, para que se puedan copiar:

````
```
pip install -r requirements.txt
```
````

Una tabla se arma con barras:

```
| Method | Path           | Description      |
|--------|----------------|------------------|
| GET    | /pokemons      | List all pokemon |
```

En VS Code, `Ctrl + Shift + V` muestra cómo queda.

## 3. Plantilla

Copiala, pegala en tu `README.md` y cambiá los datos por los de tu proyecto.

````markdown
# Pokedex API

REST API to look up pokemon and their types. Built with FastAPI and SQLite
for the Informática course (TDS05) at Universidad de Mendoza.

## Authors

- Ash Ketchum
- Misty Waterflower

## Requirements

- Python 3.11 or newer
- Git

## How to run it

1. Clone the repository and enter the folder:

   ```
   git clone https://github.com/user/pokedex-api.git
   cd pokedex-api
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   On Linux or Mac: `source venv/bin/activate`

3. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create the database and load the sample data:

   ```
   python seed.py
   ```

5. Start the server:

   ```
   uvicorn main:app --reload
   ```

6. Open http://127.0.0.1:8000/docs

## How to use it

Every endpoint requires the API key in the `X-API-Key` header.
In `/docs`, click **Authorize** and paste the key: `test-key-2026`.

| Method | Path                   | Description                      |
|--------|------------------------|----------------------------------|
| GET    | /pokemons?type_id=1    | List pokemon, optionally by type |
| GET    | /pokemons/{id}         | Get one pokemon                  |
| GET    | /types/{id}/pokemons   | List the pokemon of a type       |
| POST   | /pokemons              | Create a pokemon                 |

Example:

```
curl -H "X-API-Key: test-key-2026" http://127.0.0.1:8000/pokemons/1
```

```json
{"id": 1, "name": "Charmander", "level": 5, "type_id": 1}
```

Errors: `401` without a valid key, `404` if the id does not exist,
`400` if the data sent is invalid.

## Deploy

Live at https://pokedex-api.onrender.com/docs

The free plan sleeps after 15 minutes without use, so the first request
can take about a minute.

## Use of AI

We used an AI assistant to understand SQLAlchemy relationships and to
review error messages. All the code was written and tested by us.
````

## 4. Antes de subirlo, probalo

Cloná tu repo en **otra carpeta** y seguí tu propio README paso a paso, sin saltearte nada. Si algo falla o tuviste que hacer un paso que no estaba escrito, falta en el README.

---

## Errores comunes

- **"Instalar las dependencias y correr."** No sirve. Hay que escribir el comando exacto.
- **Pasos que faltan.** Lo más olvidado: activar el entorno virtual y correr el `seed.py`.
- **Comandos fuera de un bloque de código.** Se copian mal, con espacios o comillas cambiadas.
- **Endpoints que ya no existen.** Si cambiás una ruta, cambiala también en el README.
- **Poner la clave real.** En el integrador la clave es de prueba y puede ir. En un proyecto real, nunca: va en un `.env` (ver [variables_de_entorno.md](variables_de_entorno.md)).
- **No declarar el uso de IA.** Es parte de lo que se pide. Decir para qué la usaron no resta.
- **Dejarlo para el final.** Escribilo apenas el proyecto levanta y actualizalo cuando agregás un endpoint.
