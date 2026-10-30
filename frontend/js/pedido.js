document.addEventListener('DOMContentLoaded', cargarPedido);

async function cargarPedido() {
    const folio = new URLSearchParams(window.location.search).get('folio');

    if (!folio) {
        mostrarError('No se indicó el folio del pedido. Vuelve al carrito para iniciar una orden.');
        document.querySelector('.confirmacion-card').hidden = true;
        return;
    }

    try {
        const ticket = await solicitarAPI(`/tickets/${encodeURIComponent(folio)}`);
        mostrarTicket(ticket);
    } catch (error) {
        mostrarError(`No se pudo recuperar el pedido: ${error.message}`);
        document.querySelector('.confirmacion-card').hidden = true;
    }
}

function mostrarTicket(ticket) {
    const nombresEstado = {
        recibido: 'Recibido',
        en_preparacion: 'En Preparación',
        en_camino: 'En Camino',
        listo_para_recoger: 'Listo para Recoger',
        entregado: 'Entregado',
        cancelado: 'Cancelado'
    };

    document.querySelector('[data-nombre-cliente]').textContent = ticket.nombre_cliente;
    document.querySelector('[data-folio]').textContent = ticket.folio;
    document.querySelector('[data-estado]').textContent = nombresEstado[ticket.estado] || ticket.estado;
    document.querySelector('[data-cliente]').textContent = ticket.nombre_cliente;
    document.querySelector('[data-telefono]').textContent = ticket.telefono;
    document.querySelector('[data-metodo]').textContent = ticket.metodo === 'recoger' ? 'Recoger en Tienda' : 'Envío a Domicilio';
    document.querySelector('[data-direccion]').textContent = ticket.direccion || 'Recoger en Tienda';
    document.querySelector('[data-subtotal]').textContent = `${formatearDinero(ticket.subtotal)} MXN`;
    document.querySelector('[data-envio]').textContent = `${formatearDinero(ticket.costo_envio)} MXN`;
    document.querySelector('[data-total]').textContent = formatearDinero(ticket.total);

    const filaDescuento = document.querySelector('[data-fila-descuento]');
    filaDescuento.hidden = Number(ticket.descuento) <= 0;
    document.querySelector('[data-descuento]').textContent = `- ${formatearDinero(ticket.descuento)} MXN`;

    const cantidadPizzas = ticket.items.reduce((total, item) => total + item.cantidad, 0);
    document.querySelector('[data-conteo]').textContent = `Subtotal (${cantidadPizzas} Especialidades):`;

    const lista = document.querySelector('[data-ticket-items]');
    const plantilla = document.querySelector('#plantilla-ticket-item');
    lista.replaceChildren();

    ticket.items.forEach((item) => {
        const fila = plantilla.content.firstElementChild.cloneNode(true);
        const promoGratis = item.es_gratis_promo && item.cantidad === 1;
        const promocion = promoGratis ? ' (Martes de Locura 2×1)' : '';
        fila.querySelector('[data-descripcion-item]').textContent = `${item.cantidad}x ${item.sabor_pizza} - ${item.nombre_tamano} (${item.nombre_masa})${promocion}`;
        const importeCobrado = Math.max(Number(item.importe_linea) - (promoGratis ? Number(item.precio_base_pizza) : 0), 0);
        fila.querySelector('[data-importe-item]').textContent = `${formatearDinero(importeCobrado)} MXN`;
        lista.append(fila);
    });
}
