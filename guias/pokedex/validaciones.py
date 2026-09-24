"""Validaciones hechas a mano. Cada función recibe un dict (lo que llega del usuario),
revisa que esté bien y devuelve un dict limpio. Si algo está mal, lanza ValueError
con un mensaje claro. Nada de acá toca la base."""


def validar_tipo(datos: dict) -> dict:
    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("nombre es obligatorio y no puede estar vacío")
    if len(nombre) > 30:
        raise ValueError("nombre no puede superar los 30 caracteres")
    return {"nombre": nombre.strip()}


def validar_pokemon(datos: dict, parcial: bool = False) -> dict:
    """parcial=False: para crear, todos los campos son obligatorios.
    parcial=True: para actualizar, se revisan solo los campos que vinieron."""
    limpio = {}

    if "nombre" in datos or not parcial:
        nombre = datos.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("nombre es obligatorio y no puede estar vacío")
        if len(nombre) > 50:
            raise ValueError("nombre no puede superar los 50 caracteres")
        limpio["nombre"] = nombre.strip()

    if "nivel" in datos or not parcial:
        nivel = datos.get("nivel")
        if not isinstance(nivel, int) or isinstance(nivel, bool):
            raise ValueError("nivel es obligatorio y tiene que ser un número entero")
        if not 1 <= nivel <= 100:
            raise ValueError("nivel tiene que estar entre 1 y 100")
        limpio["nivel"] = nivel

    if "tipo_id" in datos or not parcial:
        tipo_id = datos.get("tipo_id")
        if not isinstance(tipo_id, int) or isinstance(tipo_id, bool):
            raise ValueError("tipo_id es obligatorio y tiene que ser un número entero")
        limpio["tipo_id"] = tipo_id

    return limpio
