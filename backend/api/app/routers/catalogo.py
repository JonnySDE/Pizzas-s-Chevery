from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Pizza, PizzaTamano, Masa
from app.schemas import PizzaCatalogoOut, TamanoPrecioOut, MasaOut

router = APIRouter(prefix="/api/v1/catalogo", tags=["Catálogo"])


@router.get("/pizzas", response_model=List[PizzaCatalogoOut])
def listar_pizzas(
    destacado: Optional[bool] = Query(None, description="Filtrar 'Pizzas Más Populares' para el Home"),
    etiqueta: Optional[str] = Query(None, description="Filtrar por etiqueta o promoción"),
    db: Session = Depends(get_db)
):
    query = (
        db.query(Pizza)
        .options(
            joinedload(Pizza.tamanos_disponibles).joinedload(PizzaTamano.tamano)
        )
        .filter(Pizza.activo.is_(True))
    )

    if destacado is not None:
        query = query.filter(Pizza.destacado.is_(destacado))
    if etiqueta:
        query = query.filter(Pizza.etiqueta.ilike(f"%{etiqueta}%"))

    pizzas = query.order_by(Pizza.id_pizza.asc()).all()

    resultado: List[PizzaCatalogoOut] = []
    for p in pizzas:
        tamanos_ordenados = sorted(
            p.tamanos_disponibles,
            key=lambda pt: pt.tamano.orden
        )
        tamanos_dto = [
            TamanoPrecioOut(
                id_pizza_tamano=pt.id_pizza_tamano,
                id_tamano=pt.id_tamano,
                nombre_tamano=pt.tamano.nombre,
                orden=pt.tamano.orden,
                precio=pt.precio,
                stock=pt.stock
            )
            for pt in tamanos_ordenados
        ]
        resultado.append(
            PizzaCatalogoOut(
                id_pizza=p.id_pizza,
                sabor=p.sabor,
                descripcion=p.descripcion,
                imagen_url=p.imagen_url,
                etiqueta=p.etiqueta,
                destacado=p.destacado,
                tamanos=tamanos_dto
            )
        )
    return resultado


@router.get("/masas", response_model=List[MasaOut])
def listar_masas(db: Session = Depends(get_db)):
    return (
        db.query(Masa)
        .filter(Masa.activo.is_(True))
        .order_by(Masa.precio_extra.asc(), Masa.id_masa.asc())
        .all()
    )


@router.delete("/pizzas/{id_pizza}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_pizza(id_pizza: int, db: Session = Depends(get_db)):
    """
    Soft-Delete: Usa la columna `activo = FALSE` de tu tabla PIZZA para no romper
    las llaves foráneas históricas en PIZZA_TAMANO y CARRITO_PIZZA.
    """
    pizza = db.query(Pizza).filter(Pizza.id_pizza == id_pizza).first()
    if not pizza:
        raise HTTPException(status_code=404, detail="Pizza no encontrada.")
    pizza.activo = False
    db.commit()
    return None