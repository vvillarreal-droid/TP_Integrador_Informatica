import sqlite3
from pydantic import ValidationError

from db import crear_tablas
from modelos import TipoCrear, PokemonCrear, PokemonActualizar
import crud


def main():
    crear_tablas()

    # ---- CREATE: primero los tipos (la tabla "padre") ----
    fuego = crud.crear_tipo(TipoCrear(nombre="Fuego"))
    agua = crud.crear_tipo(TipoCrear(nombre="Agua"))
    print("Tipos creados:", fuego, agua)

    # ---- CREATE: después los pokemones (apuntan a un tipo por su id) ----
    charmander = crud.crear_pokemon(PokemonCrear(nombre="Charmander", nivel=5, tipo_id=fuego.id))
    squirtle = crud.crear_pokemon(PokemonCrear(nombre="Squirtle", nivel=7, tipo_id=agua.id))
    crud.crear_pokemon(PokemonCrear(nombre="Vulpix", nivel=12, tipo_id=fuego.id))
    print("Pokémon creado:", charmander)

    # ---- READ ----
    print("\nTodos:")
    for p in crud.listar_pokemones():
        print("  ", p)

    print("\nSolo de tipo Fuego:")
    for p in crud.listar_pokemones(tipo_id=fuego.id):
        print("  ", p.nombre)

    print("\nCon el nombre del tipo (JOIN):")
    for fila in crud.listar_con_tipo():
        print("  ", fila)

    # ---- UPDATE: Charmander sube de nivel ----
    actualizado = crud.actualizar_pokemon(charmander.id, PokemonActualizar(nivel=16))
    print("\nActualizado:", actualizado)

    # ---- DELETE ----
    print("\n¿Se borró Squirtle?", crud.borrar_pokemon(squirtle.id))
    print("¿Existe todavía?", crud.obtener_pokemon(squirtle.id))

    # ---- Errores que Pydantic atrapa ANTES de tocar la base ----
    print("\nProbando un nivel inválido...")
    try:
        PokemonCrear(nombre="Mewtwo", nivel=999, tipo_id=fuego.id)
    except ValidationError as e:
        print("Pydantic lo rechazó:", e.errors()[0]["msg"])

    # ---- Errores que atrapa SQLite (la FK) ----
    print("\nProbando un tipo_id que no existe...")
    try:
        crud.crear_pokemon(PokemonCrear(nombre="Pikachu", nivel=10, tipo_id=999))
    except sqlite3.IntegrityError as e:
        print("SQLite lo rechazó:", e)

    print("\nProbando borrar un tipo que tiene pokemones...")
    try:
        crud.borrar_tipo(fuego.id)
    except sqlite3.IntegrityError as e:
        print("SQLite lo rechazó:", e)


if __name__ == "__main__":
    main()
