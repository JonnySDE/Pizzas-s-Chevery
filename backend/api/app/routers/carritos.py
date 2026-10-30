from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Carrito, CarritoPizza, PizzaTamano, Masa
from app.schemas import CarritoDetalleOut, CarritoItemCreate, CarritoItemUpdate
from app.services import (
    obtener_carrito_completo,
    construir_detalle_carrito,
    eliminar_carrito_sin_conflicto_fk
)

router = APIRouter(prefix="/api/v1/carritos", tags=["Carrito"])


@router.post("", response_model=CarritoDetalleOut, status_code=status.HTTP_201_CREATED)
def crear_carrito(db: Session = Depends(get_db)):
    nuevo_carrito = Carrito(
        estado="activo",
        expira_en=datetime.now(timezone.utc) + timedelta(hours=2)
    )
    db.add(nuevo_carrito)
    db.commit()
    db.refresh(nuevo_carrito)

    items_out, resumen = construir_detalle_carrito(nuevo_carrito)
    return CarritoDetalleOut(
        id_carrito=nuevo_carrito.id_carrito,
        estado=nuevo_carrito.estado,
        items=items_out,
        resumen=resumen
    )


@router.get("/{id_carrito}", response_model=CarritoDetalleOut)
def obtener_carrito(id_carrito: int, db: Session = Depends(get_db)):
    carrito = obtener_carrito_completo(db, id_carrito)
    items_out, resumen = construir_detalle_carrito(carrito)
    return CarritoDetalleOut(
        id_carrito=carrito.id_carrito,
        estado=carrito.estado,
        items=items_out,
        resumen=resumen
    )


@router.post("/{id_carrito}/items", response_model=CarritoDetalleOut, status_code=status.HTTP_201_CREATED)
def agregar_pizza_al_carrito(
    id_carrito: int,
    payload: CarritoItemCreate,
    db: Session = Depends(get_db)
):
    carrito = obtener_carrito_completo(db, id_carrito)
    if carrito.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pueden agregar productos a un carrito en estado '{carrito.estado}'."
        )

    pizza_tamano = (
        db.query(PizzaTamano)
        .filter(PizzaTamano.id_pizza_tamano == payload.id_pizza_tamano)
        .first()
    )
    if not pizza_tamano or not pizza_tamano.pizza.activo:
        raise HTTPException(status_code=404, detail="El tamaño o especialidad de pizza no está disponible.")

    masa = (
        db.query(Masa)
        .filter(Masa.id_masa == payload.id_masa, Masa.activo.is_(True))
        .first()
    )
    if not masa:
        raise HTTPException(status_code=404, detail="El tipo de masa seleccionado no está disponible.")

    # Verificar si ya existe la combinación (id_carrito, id_pizza_tamano, id_masa) por la restricción UNIQUE
    item_existente = (
        db.query(CarritoPizza)
        .filter(
            CarritoPizza.id_carrito == id_carrito,
            CarritoPizza.id_pizza_tamano == payload.id_pizza_tamano,
            CarritoPizza.id_masa == payload.id_masa
        )
        .first()
    )

    nueva_cantidad = payload.cantidad + (item_existente.cantidad if item_existente else 0)
    if pizza_tamano.stock < nueva_cantidad:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stock insuficiente. Disponible: {pizza_tamano.stock}."
        )

    precio_unitario_calculado = pizza_tamano.precio + masa.precio_extra

    if item_existente:
        item_existente.cantidad = nueva_cantidad
        item_existente.precio_unitario = precio_unitario_calculado
    else:
        nuevo_item = CarritoPizza(
            id_carrito=id_carrito,
            id_pizza_tamano=payload.id_pizza_tamano,
            id_masa=payload.id_masa,
            cantidad=payload.cantidad,
            precio_unitario=precio_unitario_calculado
        )
        db.add(nuevo_item)

    db.commit()
    carrito_actualizado = obtener_carrito_completo(db, id_carrito)
    items_out, resumen = construir_detalle_carrito(carrito_actualizado)
    return CarritoDetalleOut(
        id_carrito=carrito_actualizado.id_carrito,
        estado=carrito_actualizado.estado,
        items=items_out,
        resumen=resumen
    )


@router.patch("/{id_carrito}/items/{id_carrito_pizza}", response_model=CarritoDetalleOut)
def actualizar_cantidad_item(
    id_carrito: int,
    id_carrito_pizza: int,
    payload: CarritoItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Soporta los botones '-' y '+' en la vista Tu Carrito y Confirmación (Carrito.jpeg).
    Si cantidad == 0, elimina la fila automáticamente para no violar CHECK (cantidad > 0).
    """
    carrito = obtener_carrito_completo(db, id_carrito)
    if carrito.estado != "activo":
        raise HTTPException(status_code=400, detail="El carrito ya no está activo.")

    item = (
        db.query(CarritoPizza)
        .filter(
            CarritoPizza.id_carrito_pizza == id_carrito_pizza,
            CarritoPizza.id_carrito == id_carrito
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="El producto no se encuentra en este carrito.")

    if payload.cantidad == 0:
        db.delete(item)
    else:
        if item.pizza_tamano.stock < payload.cantidad:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock insuficiente. Disponible: {item.pizza_tamano.stock}."
            )
        item.cantidad = payload.cantidad

    db.commit()
    carrito_actualizado = obtener_carrito_completo(db, id_carrito)
    items_out, resumen = construir_detalle_carrito(carrito_actualizado)
    return CarritoDetalleOut(
        id_carrito=carrito_actualizado.id_carrito,
        estado=carrito_actualizado.estado,
        items=items_out,
        resumen=resumen
    )


@router.delete("/{id_carrito}/items/{id_carrito_pizza}", response_model=CarritoDetalleOut)
def eliminar_item_carrito(
    id_carrito: int,
    id_carrito_pizza: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una línea específica de CARRITO_PIZZA (cuando el usuario baja de 1 a 0 con '-').
    """
    carrito = obtener_carrito_completo(db, id_carrito)
    if carrito.estado != "activo":
        raise HTTPException(status_code=400, detail="No se puede modificar un carrito finalizado o expirado.")

    item = (
        db.query(CarritoPizza)
        .filter(
            CarritoPizza.id_carrito_pizza == id_carrito_pizza,
            CarritoPizza.id_carrito == id_carrito
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="El ítem no existe en el carrito.")

    db.delete(item)
    db.commit()

    carrito_actualizado = obtener_carrito_completo(db, id_carrito)
    items_out, resumen = construir_detalle_carrito(carrito_actualizado)
    return CarritoDetalleOut(
        id_carrito=carrito_actualizado.id_carrito,
        estado=carrito_actualizado.estado,
        items=items_out,
        resumen=resumen
    )


@router.delete("/{id_carrito}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_carrito(id_carrito: int, db: Session = Depends(get_db)):
    """
    Borra el carrito completo resolviendo primero la dependencia con TICKET
    y delegando CARRITO_PIZZA al ON DELETE CASCADE de la base de datos.
    """
    eliminar_carrito_sin_conflicto_fk(db, id_carrito)
    return None