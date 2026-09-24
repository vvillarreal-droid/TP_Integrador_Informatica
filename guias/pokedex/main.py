from sqlalchemy.exc import IntegrityError

from db import create_tables
import crud


def main():
    create_tables()

    # ---- CREATE: primero los tipos (la tabla "padre") ----
    fire = crud.create_type({"nombre": "Fuego"})
    water = crud.create_type({"nombre": "Agua"})
    print("Tipos creados:", fire, water)

    # ---- CREATE: después los pokemones (apuntan a un tipo por su id) ----
    charmander = crud.create_pokemon({"nombre": "Charmander", "nivel": 5, "tipo_id": fire["id"]})
    squirtle = crud.create_pokemon({"nombre": "Squirtle", "nivel": 7, "tipo_id": water["id"]})
    crud.create_pokemon({"nombre": "Vulpix", "nivel": 12, "tipo_id": fire["id"]})
    print("Pokémon creado:", charmander)

    # ---- READ ----
    print("\nTodos:")
    for p in crud.list_pokemons():
        print("  ", p)

    print("\nSolo de tipo Fuego:")
    for p in crud.list_pokemons(type_id=fire["id"]):
        print("  ", p["nombre"])

    print("\nCon el nombre del tipo (relationship):")
    for p in crud.list_with_type():
        print("  ", p)

    # ---- UPDATE: Charmander sube de nivel ----
    updated = crud.update_pokemon(charmander["id"], {"nivel": 16})
    print("\nActualizado:", updated)

    # ---- DELETE ----
    print("\n¿Se borró Squirtle?", crud.delete_pokemon(squirtle["id"]))
    print("¿Existe todavía?", crud.get_pokemon(squirtle["id"]))

    # ---- Errores que atrapan NUESTRAS validaciones, antes de tocar la base ----
    print("\nProbando un nivel inválido...")
    try:
        crud.create_pokemon({"nombre": "Mewtwo", "nivel": 999, "tipo_id": fire["id"]})
    except ValueError as e:
        print("Validación lo rechazó:", e)

    print("\nProbando sin nombre...")
    try:
        crud.create_pokemon({"nivel": 10, "tipo_id": fire["id"]})
    except ValueError as e:
        print("Validación lo rechazó:", e)

    # ---- Errores que atrapa la base (la FK) ----
    print("\nProbando un tipo_id que no existe...")
    try:
        crud.create_pokemon({"nombre": "Pikachu", "nivel": 10, "tipo_id": 999})
    except IntegrityError as e:
        print("La base lo rechazó:", e.orig)

    print("\nProbando borrar un tipo que tiene pokemones...")
    try:
        crud.delete_type(fire["id"])
    except IntegrityError as e:
        print("La base lo rechazó:", e.orig)


if __name__ == "__main__":
    main()
