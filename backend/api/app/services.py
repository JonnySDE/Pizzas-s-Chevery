from decimal import Decimal
from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models import Carrito, CarritoPizza, PizzaTamano, Ticket
from app.schemas import CarritoItemDetalleOut, ResumenCuentaOut


def construir_detalle_carrito(carrito: Carrito, aplicar_promo_2x1: bool = True) -> Tuple[List[CarritoItemDetalleOut], ResumenCuentaOut]:
    """
    Construye el desglose del carrito y calcula la promoción 2x1 en Pizzas Medianas
    exactamente como se muestra en Carrito.jpeg y Tiket.jpeg.
    """
    items_out: List[CarritoItemDetalleOut] = []
    subtotal = Decimal("0.00")
    total_pizzas = 0

    # Recolectar los precios de todas las unidades de tamaño "Mediana" para el 2x1
    precios_medianas: List[Decimal] = []

    for item in carrito.items:
        pt = item.pizza_tamano
        pizza = pt.pizza
        tamano = pt.tamano
        masa = item.masa

        importe_linea = item.precio_unitario * item.cantidad
        subtotal += importe_linea
        total_pizzas += item.cantidad

        if tamano.nombre.lower().startswith("med"):
            # Precio base de la especialidad mediana (en Carrito.jpeg se descuentan $170 de la Hawaiana Mediana)
            for _ in range(item.cantidad):
                precios_medianas.append(pt.precio)

        items_out.append(
            CarritoItemDetalleOut(
                id_carrito_pizza=item.id_carrito_pizza,
                id_pizza_tamano=pt.id_pizza_tamano,
                sabor_pizza=pizza.sabor,
                nombre_tamano=tamano.nombre,
                precio_base_pizza=pt.precio,
                id_masa=masa.id_masa,
                nombre_masa=masa.nombre,
                precio_extra_masa=masa.precio_extra,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                importe_linea=importe_linea,
                es_gratis_promo=False
            )
        )

    # Cálculo de Promo 2x1: Por cada 2 pizzas medianas, se descuenta la de menor valor
    descuento = Decimal("0.00")
    promocion_texto = None

    if aplicar_promo_2x1 and len(precios_medianas) >= 2:
        precios_medianas.sort()
        cantidad_gratis = len(precios_medianas) // 2
        descuento = sum(precios_medianas[:cantidad_gratis], Decimal("0.00"))
        promocion_texto = "¡Promoción Aplicada: Martes de Locura 2x1!"

        # Marcar visualmente el ítem bonificado para la UI
        restantes_por_marcar = cantidad_gratis
        for item_dto in sorted(items_out, key=lambda x: x.precio_base_pizza):
            if item_dto.nombre_tamano.lower().startswith("med") and restantes_por_marcar > 0:
                item_dto.es_gratis_promo = True
                restantes_por_marcar -= 1

    costo_envio = Decimal("0.00")  # Envío en Suchiapa $0.00 MXN según UI
    total = max(subtotal + costo_envio - descuento, Decimal("0.00"))

    resumen = ResumenCuentaOut(
        total_pizzas=total_pizzas,
        promocion_aplicada=promocion_texto,
        subtotal=subtotal,
        costo_envio=costo_envio,
        descuento=descuento,
        total=total
    )
    return items_out, resumen


def obtener_carrito_completo(db: Session, id_carrito: int) -> Carrito:
    carrito = (
        db.query(Carrito)
        .options(
            joinedload(Carrito.items)
            .joinedload(CarritoPizza.pizza_tamano)
            .joinedload(PizzaTamano.pizza),
            joinedload(Carrito.items)
            .joinedload(CarritoPizza.pizza_tamano)
            .joinedload(PizzaTamano.tamano),
            joinedload(Carrito.items)
            .joinedload(CarritoPizza.masa),
            joinedload(Carrito.ticket)
        )
        .filter(Carrito.id_carrito == id_carrito)
        .first()
    )
    if not carrito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El carrito con ID {id_carrito} no existe."
        )
    return carrito


def eliminar_carrito_sin_conflicto_fk(db: Session, id_carrito: int) -> None:
    """
    Elimina un carrito de forma 100% segura frente a restricciones de Foreign Key:
    1. TICKET referencia a CARRITO sin ON DELETE CASCADE. Si existe un ticket asociado,
       primero restauramos el stock (si no fue entregado/cancelado) y borramos el registro hijo en TICKET.
    2. Luego borramos CARRITO, lo cual dispara automáticamente el ON DELETE CASCADE hacia CARRITO_PIZZA.
    """
    carrito = obtener_carrito_completo(db, id_carrito)

    if carrito.ticket:
        if carrito.ticket.estado not in ("entregado", "cancelado"):
            for item in carrito.items:
                item.pizza_tamano.stock += item.cantidad
        db.delete(carrito.ticket)
        db.flush()  # Ejecuta el DELETE del hijo antes de borrar el padre

    db.delete(carrito)
    db.commit()