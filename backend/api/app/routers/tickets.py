from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ticket, PizzaTamano
from app.schemas import TicketCreate, TicketOut
from app.services import obtener_carrito_completo, construir_detalle_carrito

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def confirmar_pedido(payload: TicketCreate, db: Session = Depends(get_db)):
    carrito = obtener_carrito_completo(db, payload.id_carrito)

    if carrito.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este carrito ya fue procesado o expiró."
        )
    if not carrito.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes confirmar un pedido con el carrito vacío."
        )

    # 1. Bloquear y validar stock en PIZZA_TAMANO
    for item in carrito.items:
        pt = (
            db.query(PizzaTamano)
            .filter(PizzaTamano.id_pizza_tamano == item.id_pizza_tamano)
            .with_for_update()
            .first()
        )
        if not pt or pt.stock < item.cantidad:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock insuficiente para {item.pizza_tamano.pizza.sabor} ({item.pizza_tamano.tamano.nombre})."
            )
        pt.stock -= item.cantidad

    # 2. Calcular importes finales (Subtotal, Promo 2x1, Envío, Total)
    items_out, resumen = construir_detalle_carrito(carrito)

    # 3. Generar folio temporal y crear registro en TICKET
    anio_actual = datetime.now().year
    folio_temp = f"TEMP-{carrito.id_carrito}"

    nuevo_ticket = Ticket(
        id_carrito=carrito.id_carrito,
        folio=folio_temp,
        nombre_cliente=payload.nombre_cliente.strip(),
        telefono=payload.telefono.strip(),
        metodo=payload.metodo,
        direccion=payload.direccion.strip() if payload.direccion else None,
        indicaciones=payload.indicaciones.strip() if payload.indicaciones else None,
        subtotal=resumen.subtotal,
        costo_envio=resumen.costo_envio,
        descuento=resumen.descuento,
        total=resumen.total,
        estado="en_preparacion"  # Coincide con "En Preparación" en Tiket.jpeg
    )

    carrito.estado = "finalizado"
    db.add(nuevo_ticket)
    db.flush()  # Obtiene id_ticket autogenerado sin cerrar la transacción

    # Formato exacto de Tiket.jpeg: #CHV-2026-084
    nuevo_ticket.folio = f"#CHV-{anio_actual}-{nuevo_ticket.id_ticket:03d}"

    db.commit()
    db.refresh(nuevo_ticket)

    return TicketOut(
        id_ticket=nuevo_ticket.id_ticket,
        folio=nuevo_ticket.folio,
        estado=nuevo_ticket.estado,
        nombre_cliente=nuevo_ticket.nombre_cliente,
        telefono=nuevo_ticket.telefono,
        metodo=nuevo_ticket.metodo,
        direccion=nuevo_ticket.direccion,
        indicaciones=nuevo_ticket.indicaciones,
        subtotal=nuevo_ticket.subtotal,
        costo_envio=nuevo_ticket.costo_envio,
        descuento=nuevo_ticket.descuento,
        total=nuevo_ticket.total,
        created_at=nuevo_ticket.created_at,
        items=items_out
    )


@router.get("/{folio}", response_model=TicketOut)
def obtener_ticket_por_folio(folio: str, db: Session = Depends(get_db)):
    """
    Permite consultar el ticket por su folio (ej. #CHV-2026-084 o CHV-2026-084)
    para renderizar la vista Tiket.jpeg.
    """
    folio_normalizado = folio if folio.startswith("#") else f"#{folio}"
    ticket = (
        db.query(Ticket)
        .filter((Ticket.folio == folio_normalizado) | (Ticket.folio == folio))
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="No se encontró ningún ticket con ese folio.")

    carrito = obtener_carrito_completo(db, ticket.id_carrito)
    items_out, _ = construir_detalle_carrito(carrito)

    return TicketOut(
        id_ticket=ticket.id_ticket,
        folio=ticket.folio,
        estado=ticket.estado,
        nombre_cliente=ticket.nombre_cliente,
        telefono=ticket.telefono,
        metodo=ticket.metodo,
        direccion=ticket.direccion,
        indicaciones=ticket.indicaciones,
        subtotal=ticket.subtotal,
        costo_envio=ticket.costo_envio,
        descuento=ticket.descuento,
        total=ticket.total,
        created_at=ticket.created_at,
        items=items_out
    )