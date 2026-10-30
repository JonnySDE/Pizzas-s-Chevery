from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator


# --- CATÁLOGO ---
class TamanoPrecioOut(BaseModel):
    id_pizza_tamano: int
    id_tamano: int
    nombre_tamano: str
    orden: int
    precio: Decimal
    stock: int

    model_config = ConfigDict(from_attributes=True)


class PizzaCatalogoOut(BaseModel):
    id_pizza: int
    sabor: str
    descripcion: Optional[str]
    imagen_url: str
    etiqueta: Optional[str]
    destacado: bool
    tamanos: List[TamanoPrecioOut]

    model_config = ConfigDict(from_attributes=True)


class MasaOut(BaseModel):
    id_masa: int
    nombre: str
    precio_extra: Decimal

    model_config = ConfigDict(from_attributes=True)


# --- CARRITO ---
class CarritoItemCreate(BaseModel):
    id_pizza_tamano: int = Field(..., gt=0)
    id_masa: int = Field(..., gt=0)
    cantidad: int = Field(default=1, gt=0)


class CarritoItemUpdate(BaseModel):
    # Permite 0 para que si el usuario baja de 1 a 0 en el botón "-", se elimine automáticamente
    cantidad: int = Field(..., ge=0)


class CarritoItemDetalleOut(BaseModel):
    id_carrito_pizza: int
    id_pizza_tamano: int
    sabor_pizza: str
    nombre_tamano: str
    precio_base_pizza: Decimal
    id_masa: int
    nombre_masa: str
    precio_extra_masa: Decimal
    cantidad: int
    precio_unitario: Decimal
    importe_linea: Decimal
    es_gratis_promo: bool = False


class ResumenCuentaOut(BaseModel):
    total_pizzas: int
    promocion_aplicada: Optional[str] = None
    subtotal: Decimal
    costo_envio: Decimal
    descuento: Decimal
    total: Decimal


class CarritoDetalleOut(BaseModel):
    id_carrito: int
    estado: str
    items: List[CarritoItemDetalleOut]
    resumen: ResumenCuentaOut


# --- TICKET (CHECKOUT) ---
class TicketCreate(BaseModel):
    id_carrito: int = Field(..., gt=0)
    nombre_cliente: str = Field(..., min_length=2, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=20)
    metodo: Literal["domicilio", "recoger"]
    direccion: Optional[str] = Field(None, max_length=255)
    indicaciones: Optional[str] = Field(None, max_length=255)

    @model_validator(mode="after")
    def validar_direccion_domicilio(self):
        # Valida en API el CHECK (metodo = 'recoger' OR direccion IS NOT NULL)
        if self.metodo == "domicilio" and (not self.direccion or not self.direccion.strip()):
            raise ValueError("La dirección de entrega es obligatoria para pedidos a domicilio.")
        if self.metodo == "recoger":
            self.direccion = None
        return self


class TicketOut(BaseModel):
    id_ticket: int
    folio: str
    estado: str
    nombre_cliente: str
    telefono: str
    metodo: str
    direccion: Optional[str]
    indicaciones: Optional[str]
    subtotal: Decimal
    costo_envio: Decimal
    descuento: Decimal
    total: Decimal
    created_at: datetime
    items: List[CarritoItemDetalleOut]