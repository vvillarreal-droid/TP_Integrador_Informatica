# Comentarios de la cátedra

Informática (TDS05) · Proyecto Integrador · UM Río Cuarto

Acá va la devolución de cada revisión semanal. Léanlo antes de seguir programando.
El alcance completo del grupo está en el documento de alcances.

**Grupo:** Pablo Fernando Doblas, Ignacio Gabriel Carreño, Valentino Villarreal Ríos
**Tema:** Online Store — Clientes y pedidos (a confirmar)

---

## 23/09

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

**Endpoints a entregar (Nivel A)**
- [ ] `GET /productos?categoria=electronica`
- [ ] `GET /clientes/{id}` (404 si no existe)
- [ ] `GET /clientes/{id}/pedidos`
- [ ] `GET /pedidos?estado=pendiente`
- [ ] `GET /clientes/ranking` (total gastado)
- [ ] `POST /clientes`
- [ ] Todos protegidos con `X-API-Key` (clave como constante en `main.py`)
