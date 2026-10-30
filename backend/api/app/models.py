from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import (
    String, Integer, Boolean, Numeric, Enum, DateTime, TIMESTAMP, ForeignKey, UniqueConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Pizza(Base):
    __tablename__ = "PIZZA"

    id_pizza: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sabor: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    imagen_url: Mapped[str] = mapped_column(String(255), nullable=False)
    etiqueta: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    destacado: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    tamanos_disponibles: Mapped[List["PizzaTamano"]] = relationship(
        "PizzaTamano", back_populates="pizza"
    )


class Tamano(Base):
    __tablename__ = "TAMANO"

    id_tamano: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0)


class PizzaTamano(Base):
    __tablename__ = "PIZZA_TAMANO"
    __table_args__ = (UniqueConstraint("id_pizza", "id_tamano"),)

    id_pizza_tamano: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_pizza: Mapped[int] = mapped_column(ForeignKey("PIZZA.id_pizza"), nullable=False)
    id_tamano: Mapped[int] = mapped_column(ForeignKey("TAMANO.id_tamano"), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    pizza: Mapped["Pizza"] = relationship("Pizza", back_populates="tamanos_disponibles")
    tamano: Mapped["Tamano"] = relationship("Tamano")


class Masa(Base):
    __tablename__ = "MASA"

    id_masa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    precio_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Carrito(Base):
    __tablename__ = "CARRITO"

    id_carrito: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estado: Mapped[str] = mapped_column(
        Enum("activo", "finalizado", "expirado"), default="activo", nullable=False
    )
    expira_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    items: Mapped[List["CarritoPizza"]] = relationship(
        "CarritoPizza", back_populates="carrito", cascade="all, delete-orphan"
    )
    ticket: Mapped[Optional["Ticket"]] = relationship(
        "Ticket", back_populates="carrito", uselist=False
    )


class CarritoPizza(Base):
    __tablename__ = "CARRITO_PIZZA"
    __table_args__ = (UniqueConstraint("id_carrito", "id_pizza_tamano", "id_masa"),)

    id_carrito_pizza: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_carrito: Mapped[int] = mapped_column(
        ForeignKey("CARRITO.id_carrito", ondelete="CASCADE"), nullable=False
    )
    id_pizza_tamano: Mapped[int] = mapped_column(
        ForeignKey("PIZZA_TAMANO.id_pizza_tamano"), nullable=False
    )
    id_masa: Mapped[int] = mapped_column(ForeignKey("MASA.id_masa"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    carrito: Mapped["Carrito"] = relationship("Carrito", back_populates="items")
    pizza_tamano: Mapped["PizzaTamano"] = relationship("PizzaTamano")
    masa: Mapped["Masa"] = relationship("Masa")


class Ticket(Base):
    __tablename__ = "TICKET"

    id_ticket: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_carrito: Mapped[int] = mapped_column(
        ForeignKey("CARRITO.id_carrito"), unique=True, nullable=False
    )
    folio: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre_cliente: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    metodo: Mapped[str] = mapped_column(Enum("domicilio", "recoger"), nullable=False)
    direccion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    indicaciones: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    costo_envio: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    descuento: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[str] = mapped_column(
        Enum("recibido", "en_preparacion", "en_camino", "listo_para_recoger", "entregado", "cancelado"),
        default="recibido",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    carrito: Mapped["Carrito"] = relationship("Carrito", back_populates="ticket")