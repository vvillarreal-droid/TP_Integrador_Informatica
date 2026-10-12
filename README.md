# TP_Integrador_Integrador

# TiendaDB

REST API for an online store: product catalog, orders that update stock
automatically, and a sales report. Built with FastAPI and SQLite (sqlite3)
for the Informática course (TDS05) at Universidad de Mendoza, Río Cuarto.

## Authors

- Villarreal Ríos, Valentino
- Carreño, Ignacio
- Doblas, Pablo

## Requirements

- Python 3.11 or newer
- Git

## How to run it

1. Clone the repository and enter the folder:

  ```
   git clone https://github.com/vvillarreal-droid/TP_Integrador_Informatica
   cd TP_Integrador_Informatica
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

   The server also runs this automatically on startup if the database is
   empty, so the API always has data (this is needed on Render, where the
   disk is reset on every restart).

   5. Set the API key as an environment variable (Windows PowerShell):

   ```
   $env:API_KEY="tienda-test-2026"
   ```

   On Linux or Mac: `export API_KEY="tienda-test-2026"`

6. Start the server:

   ```
   uvicorn main:app --reload
   ```

7. Open http://127.0.0.1:8000/docs

## How to use it

The catalog is public. Orders, the sales report and the low-stock list are
protected: they require the API key in the `X-API-Key` header.
In `/docs`, click **Authorize** and paste the test key: `tienda-test-2026`.

| Method | Path                    | Auth | Description                                         |
|--------|-------------------------|------|-----------------------------------------------------|
| GET    | /                       | No   | Welcome message (checks the API is running)         |
| GET    | /productos              | No   | List products. Optional filters: `categoria`, `precio_min`, `precio_max`, `buscar` (partial text) |
| GET    | /productos/{id}         | No   | Get one product                                     |
| GET    | /categorias             | No   | List the product categories                         |
| GET    | /productos/bajo-stock   | Yes  | Products with low stock, to restock                 |
| POST   | /pedidos                | Yes  | Create an order: checks and updates stock, calculates the total |
| GET    | /ventas                 | Yes  | Sales report: total revenue and best-selling products |

Example (public):

```
curl http://127.0.0.1:8000/productos?categoria=electronica&precio_max=30000
```

```json
[{"id": 1, "nombre": "Auriculares inalambricos", "categoria": "electronica", "precio": 25000, "stock": 15}]
```

Example (protected, create an order):

```
curl -X POST http://127.0.0.1:8000/pedidos -H "X-API-Key: tienda-test-2026" -H "Content-Type: application/json" -d "{\"items\": [{\"producto_id\": 1, \"cantidad\": 2}]}"
```

```json
{"pedido_id": 1, "fecha": "2026-10-12", "total": 50000, "items": [{"producto_id": 1, "cantidad": 2, "subtotal": 50000}]}
```

Errors:

| Code | When                                                        |
|------|-------------------------------------------------------------|
| 401  | Missing or invalid API key                                  |
| 404  | The product does not exist                                  |
| 400  | Not enough stock for an order (the whole order is cancelled) |
| 422  | Invalid data (for example, a negative quantity)             |
| 500  | Unexpected database error                                   |

Every error is also saved with date and time in `errores.log`.

## Deploy

Live at https://tiendadb.onrender.com/docs

The free plan sleeps after 15 minutes without use, so the first request
can take about a minute. The database goes back to the sample data every
time the server restarts.

## Use of AI

We used an AI assistant (Claude) to plan the project structure, organize the
work between the team members and draft this README. All the code was
reviewed and tested by us, and every member can explain it.

   On Linux or Mac: `source venv/bin/activate`
