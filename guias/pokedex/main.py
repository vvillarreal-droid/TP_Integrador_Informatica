from sqlalchemy.exc import IntegrityError

from db import crear_tablas
import crud


def main():
    crear_tablas()

    # ---- CREATE: primero los tipos (la tabla "padre") ----
    fuego = crud.crear_tipo({"nombre": "Fuego"})
    agua = crud.crear_tipo({"nombre": "Agua"})
    print("Tipos creados:", fuego, agua)

    # ---- CREATE: después los pokemones (apuntan a un tipo por su id) ----
    charmander = crud.crear_pokemon({"nombre": "Charmander", "nivel": 5, "tipo_id": fuego["id"]})
    squirtle = crud.crear_pokemon({"nombre": "Squirtle", "nivel": 7, "tipo_id": agua["id"]})
    crud.crear_pokemon({"nombre": "Vulpix", "nivel": 12, "tipo_id": fuego["id"]})
    print("Pokémon creado:", charmander)

    # ---- READ ----
    print("\nTodos:")
    for p in crud.listar_pokemones():
        print("  ", p)

    print("\nSolo de tipo Fuego:")
    for p in crud.listar_pokemones(tipo_id=fuego["id"]):
        print("  ", p["nombre"])

    print("\nCon el nombre del tipo (relationship):")
    for p in crud.listar_con_tipo():
        print("  ", p)

    # ---- UPDATE: Charmander sube de nivel ----
    actualizado = crud.actualizar_pokemon(charmander["id"], {"nivel": 16})
    print("\nActualizado:", actualizado)

    # ---- DELETE ----
    print("\n¿Se borró Squirtle?", crud.borrar_pokemon(squirtle["id"]))
    print("¿Existe todavía?", crud.obtener_pokemon(squirtle["id"]))

    # ---- Errores que atrapan NUESTRAS validaciones, antes de tocar la base ----
    print("\nProbando un nivel inválido...")
    try:
        crud.crear_pokemon({"nombre": "Mewtwo", "nivel": 999, "tipo_id": fuego["id"]})
    except ValueError as e:
        print("Validación lo rechazó:", e)

    print("\nProbando sin nombre...")
    try:
        crud.crear_pokemon({"nivel": 10, "tipo_id": fuego["id"]})
    except ValueError as e:
        print("Validación lo rechazó:", e)

    # ---- Errores que atrapa la base (la FK) ----
    print("\nProbando un tipo_id que no existe...")
    try:
        crud.crear_pokemon({"nombre": "Pikachu", "nivel": 10, "tipo_id": 999})
    except IntegrityError as e:
        print("La base lo rechazó:", e.orig)

    print("\nProbando borrar un tipo que tiene pokemones...")
    try:
        crud.borrar_tipo(fuego["id"])
    except IntegrityError as e:
        print("La base lo rechazó:", e.orig)


if __name__ == "__main__":
    main()
