# Pizzería Chevery — Backend API (FastAPI)

API RESTful desarrollada en **FastAPI** y conectada a una base de datos relacional **MySQL 8 o MariaDB**, diseñada exclusivamente para soportar el flujo del frontend de Pizzería Chevery (Home, Menú, Carrito y Confirmación de Pedido con Ticket).

## Requisitos Previos

* Python 3.10 o superior.
* MySQL 8 o MariaDB instalado localmente.
* Gestor de paquetes `pip` o `uv`.

## Estructura del Proyecto

```
pizzeria_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada y configuración de CORS
│   ├── database.py          # Conexión SQLAlchemy con MySQL / MariaDB
│   ├── models.py            # Modelos ORM (Tablas DDL)
│   ├── schemas.py           # Esquemas Pydantic v2 (Request/Response)
│   ├── services.py          # Lógica de negocio (Promo 2x1 y manejo seguro de FKs)
│   └── routers/
│       ├── __init__.py
│       ├── catalogo.py      # Endpoints de Pizzas y Masas
│       ├── carritos.py      # Endpoints de Carrito y Carrito-Pizzas
│       └── tickets.py       # Endpoints de Checkout y Tickets
├── schema.sql               # Esquema y datos iniciales de catálogos
└── requirements.txt
```

## Configuración local

Para la configuración de MySQL Workbench, variables de entorno, ejecución conjunta del frontend y la API, consulta ../../README.md. El archivo .env.example muestra la URL de conexión; no guardes contraseñas en el código.

Las rutas implementadas son las descritas en el contrato API-first entregado con el proyecto: /api/v1/catalogo, /api/v1/carritos y /api/v1/tickets. El frontend se sirve desde FastAPI en el puerto 8000.

## Instalación y Ejecución

1. **Situarse en la carpeta del proyecto:**
   ```bash
   cd pizzeria_api
   ```

2. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar el servidor de desarrollo con Uvicorn:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Verificar la documentación interactiva:**
   Abre tu navegador en: `http://localhost:8000/docs`
