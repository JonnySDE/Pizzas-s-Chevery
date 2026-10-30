# Conectar y ejecutar Pizzería Chevery

La API FastAPI está en `api/` y sirve también los archivos estáticos de `../frontend`. La información del menú, existencias, carrito, promoción y pedidos confirmados se consulta en la API; el navegador solo guarda el identificador del carrito activo.

## Base de datos MySQL Workbench

El esquema de `api/schema.sql` coincide con los modelos SQLAlchemy de la API y con el diseño propuesto: `PIZZA`, `TAMANO`, `PIZZA_TAMANO`, `MASA`, `CARRITO`, `CARRITO_PIZZA` y `TICKET`. El archivo crea la base `pizzeria_chevery`, las tablas y los datos iniciales de pizzas, tamaños, precios y masas. Las imágenes iniciales apuntan a `frontend/imagenes/`.

En MySQL Workbench, abre `api/schema.sql` y ejecútalo contra tu servidor local. Si ya creaste tablas o tienes datos, conserva un respaldo antes de ejecutar cambios: `CREATE TABLE IF NOT EXISTS` no modifica tablas que ya existen.

## Configurar la conexión

1. Copia `api/.env.example` a `api/.env`.
2. Edita `DATABASE_URL` con el usuario, contraseña, host y puerto de tu servidor MySQL. Por ejemplo:

   ```text
   mysql+pymysql://root:TU_PASSWORD@127.0.0.1:3306/pizzeria_chevery?charset=utf8mb4
   ```

   MySQL Workbench es el cliente; la URL debe apuntar al servidor MySQL que Workbench administra.
3. Guarda `.env`. El archivo está excluido de Git para proteger las credenciales.

## Instalar y ejecutar

Desde PowerShell, partiendo de la carpeta raíz del proyecto:

```powershell
cd .\backend\api
Copy-Item .env.example .env
# Edita .env y escribe la contraseña real del servidor MySQL.
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Abre [http://localhost:8000](http://localhost:8000) para usar el sitio y [http://localhost:8000/docs](http://localhost:8000/docs) para consultar Swagger. El mismo servidor atiende `frontend/` y `/api/v1`, así no hace falta abrir los HTML con `file://` ni configurar CORS para el uso normal.

Si usas Live Server en el puerto 5500, ya está incluido en `FRONTEND_ORIGINS` de `.env.example`.

## Flujo conectado

- Inicio y Menú cargan pizzas, precios, stock y masas desde `GET /api/v1/catalogo/...`.
- Al comenzar, se crea o recupera el carrito activo. Su ID se guarda en `localStorage`.
- Agregar, quitar y cambiar cantidades usa los endpoints de carrito. El servidor calcula subtotal, descuento 2×1 y total.
- Confirmar pedido crea un ticket en la base de datos. La página Pedido busca ese ticket por su folio en la API.

No se incluye ninguna contraseña de MySQL ni datos de pedidos de demostración. El servicio requiere que configures `.env` y ejecutes `schema.sql` en tu servidor.
