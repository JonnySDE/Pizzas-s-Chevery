from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from app.routers import catalogo, carritos, tickets

app = FastAPI(
    title="Pizzería Chevery API",
    description="API RESTful para el flujo de pedidos de Pizzería Chevery (Suchiapa, Chiapas)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000"
    ).split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(catalogo.router)
app.include_router(carritos.router)
app.include_router(tickets.router)

# El mismo servidor entrega el frontend y la API para evitar diferencias de origen.
CARPETA_FRONTEND = Path(__file__).resolve().parents[3] / "frontend"
app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
