# Guía · Variables de entorno con `.env`

Informática (TDS05) · Universidad de Mendoza · Sede Río Cuarto

Una **variable de entorno** es un valor que vive **fuera del código**: lo define el sistema donde corre el programa, y el programa lo lee al arrancar. Sirve para todo lo que no querés dejar escrito en el repo (claves, contraseñas) o que cambia según dónde corra (tu compu, Render).

El archivo `.env` es la forma cómoda de definirlas en tu compu: un archivo de texto con una variable por línea, que **no se sube a GitHub**.

> **¿Es obligatorio en el integrador?** No. El alcance permite dejar la API key como constante en `main.py`. Esto es el paso siguiente, para quien quiera hacerlo bien.

---

## 1. Instalar

```
pip install python-dotenv
```

Y agregá `python-dotenv` a `requirements.txt`. Si no, en Render falla el deploy.

## 2. Crear el `.env`

En la raíz del proyecto (al lado de `main.py`), un archivo que se llama exactamente `.env`:

```
API_KEY=clave-de-prueba-2026
DB_FILE=pokedex.db
```

Sin espacios alrededor del `=` y sin comillas.

## 3. Sacarlo del repo

En `.gitignore`:

```
.env
```

Hacelo **antes** del primer commit. Si el `.env` ya se subió, la clave quedó en el historial: sacalo con `git rm --cached .env` y **cambiá la clave**.

## 4. Leerlo desde Python

```python
import os
from dotenv import load_dotenv

load_dotenv()                       # lee el .env y carga las variables

API_KEY = os.getenv("API_KEY")
DB_FILE = os.getenv("DB_FILE", "pokedex.db")   # el segundo valor es el default

if API_KEY is None:
    raise RuntimeError("Falta la variable API_KEY")
```

`load_dotenv()` va una sola vez, arriba de todo, antes de usar las variables. El resto del código no cambia: donde antes comparabas contra la constante, ahora comparás contra `API_KEY`.

## 5. Dejar un `.env.example`

Como el `.env` no se sube, tu compañero no sabe qué variables hacen falta. Para eso se sube un `.env.example` con los nombres y **sin los valores reales**:

```
API_KEY=
DB_FILE=pokedex.db
```

Cada uno lo copia como `.env` y completa lo suyo. Explicalo en el README.

## 6. En Render

En Render no hay `.env`. Las variables se cargan desde el panel: tu servicio → **Environment** → **Add Environment Variable**, con el mismo nombre (`API_KEY`) y su valor.

No hay que tocar el código: si no encuentra el archivo, `load_dotenv()` no hace nada y `os.getenv` lee lo que cargaste en el panel.

---

## Errores comunes

- **Subir el `.env`.** Es el error que la guía entera busca evitar. Revisá con `git status` que no aparezca.
- **No controlar que la variable exista.** Si falta, `os.getenv` devuelve `None` sin avisar. Por eso el `raise` del paso 4: mejor que no arranque a que arranque sin clave.
- **Esperar un número.** Todo lo que viene del entorno es **texto**. Para un número: `int(os.getenv("PORT", "8000"))`.
- **Llamar a `load_dotenv()` tarde.** Si leés la variable antes de cargarla, da `None`.
- **Cambiar el `.env` y no reiniciar.** Se lee al arrancar. Con `uvicorn --reload` tampoco alcanza: cortá y volvé a levantar.
- **Olvidarse de cargarla en Render.** Local anda, en producción no.
