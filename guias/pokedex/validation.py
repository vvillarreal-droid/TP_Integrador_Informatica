"""Validaciones hechas a mano. Cada función recibe un dict (lo que llega del usuario),
revisa que esté bien y devuelve un dict limpio. Si algo está mal, lanza ValueError
con un mensaje claro. Nada de acá toca la base."""


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
