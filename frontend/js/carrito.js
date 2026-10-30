document.addEventListener('DOMContentLoaded', cargarCarrito);

let carritoActual;
let metodoEntrega = 'domicilio';

async function cargarCarrito() {
    try {
        carritoActual = await obtenerCarritoActivo();
        renderizarCarrito(carritoActual);
        activarFormularioPedido();
        activarMetodoEntrega();
    } catch (error) {
        mostrarError(`No se pudo cargar tu carrito: ${error.message}`);
    }
}

function renderizarCarrito(carrito) {
    carritoActual = carrito;
    const lista = document.querySelector('[data-items-carrito]');
    const plantilla = document.querySelector('#plantilla-item-carrito');
    const resumen = carrito.resumen;
    lista.replaceChildren();
    actualizarContadorCarrito(resumen.total_pizzas);
    document.querySelector('[data-total-pizzas]').textContent = resumen.total_pizzas;

    document.querySelector('[data-promocion]').hidden = !resumen.promocion_aplicada;
    document.querySelector('[data-promocion-texto]').textContent = resumen.promocion_aplicada || '';
    document.querySelector('[data-subtotal]').textContent = `${formatearDinero(resumen.subtotal)} MXN`;
    document.querySelector('[data-envio]').textContent = `${formatearDinero(resumen.costo_envio)} MXN`;
    document.querySelector('[data-total]').textContent = formatearDinero(resumen.total);

    const filaDescuento = document.querySelector('[data-fila-descuento]');
    filaDescuento.hidden = Number(resumen.descuento) <= 0;
    document.querySelector('[data-descuento]').textContent = `- ${formatearDinero(resumen.descuento)} MXN`;

    if (!carrito.items.length) {
        lista.innerHTML = '<p class="carrito-vacio">Tu carrito está vacío. <a href="menu.html">Explora el menú</a> y agrega tus pizzas favoritas.</p>';
    }

    carrito.items.forEach((item) => {
        const tarjeta = plantilla.content.firstElementChild.cloneNode(true);
        const imagenPizza = tarjeta.querySelector('[data-imagen-carrito]');
        imagenPizza.src = obtenerImagenPizza(item.sabor_pizza);
        imagenPizza.alt = `Pizza ${item.sabor_pizza}`;
        tarjeta.querySelector('[data-nombre]').textContent = item.sabor_pizza;
        tarjeta.querySelector('[data-tamano]').textContent = `Tamaño: ${item.nombre_tamano} (${formatearDinero(item.precio_base_pizza)} MXN)`;
        tarjeta.querySelector('[data-masa]').textContent = `Masa: ${item.nombre_masa} (+ ${formatearDinero(item.precio_extra_masa)} MXN)`;
        tarjeta.querySelector('[data-cantidad]').textContent = item.cantidad;

        const totalLinea = Number(item.importe_linea);
        const lineaGratis = item.es_gratis_promo && item.cantidad === 1;
        tarjeta.querySelector('[data-gratis]').hidden = !item.es_gratis_promo;
        const totalCobrado = Math.max(totalLinea - (lineaGratis ? Number(item.precio_base_pizza) : 0), 0);
        tarjeta.querySelector('[data-total-linea]').textContent = formatearDinero(totalCobrado);

        if (lineaGratis) {
            const anterior = tarjeta.querySelector('[data-precio-anterior]');
            anterior.textContent = formatearDinero(totalLinea);
            anterior.hidden = false;
        }

        tarjeta.querySelector('[data-sumar]').addEventListener('click', () => cambiarCantidad(item, item.cantidad + 1));
        tarjeta.querySelector('[data-restar]').addEventListener('click', () => cambiarCantidad(item, item.cantidad - 1));
        lista.append(tarjeta);
    });

    document.querySelector('[data-confirmar]').disabled = !carrito.items.length;
}

function obtenerImagenPizza(sabor) {
    const nombre = sabor.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const imagenes = [
        { palabra: 'pepperoni', archivo: 'pizza-pepperoni.png' },
        { palabra: 'hawaiana', archivo: 'pizza-hawaiana.png' },
        { palabra: 'mexicana', archivo: 'pizza-mexicana.png' },
        { palabra: 'carnes', archivo: 'pizza-carnes.png' },
        { palabra: 'vegetariana', archivo: 'pizza-vegetariana.png' }
    ];
    const pizza = imagenes.find((opcion) => nombre.includes(opcion.palabra));
    const archivo = pizza ? pizza.archivo : 'icono-pizza.svg';

    return new URL(`../imagenes/${archivo}`, document.baseURI).href;
}

async function cambiarCantidad(item, cantidad) {
    try {
        limpiarError();
        const ruta = `/carritos/${carritoActual.id_carrito}/items/${item.id_carrito_pizza}`;
        if (cantidad <= 0) {
            carritoActual = await solicitarAPI(ruta, { method: 'DELETE' });
        } else {
            carritoActual = await solicitarAPI(ruta, {
                method: 'PATCH',
                body: JSON.stringify({ cantidad })
            });
        }
        renderizarCarrito(carritoActual);
    } catch (error) {
        mostrarError(error.message || 'No se pudo actualizar la cantidad.');
    }
}

function activarMetodoEntrega() {
    document.querySelectorAll('[data-metodo]').forEach((boton) => {
        boton.addEventListener('click', () => {
            metodoEntrega = boton.dataset.metodo;
            document.querySelectorAll('[data-metodo]').forEach((opcion) => {
                const activo = opcion === boton;
                opcion.classList.toggle('activo', activo);
                opcion.setAttribute('aria-pressed', String(activo));
            });

            const campoDireccion = document.querySelector('[data-campo-direccion]');
            const direccion = document.querySelector('#direccion-cliente');
            const esDomicilio = metodoEntrega === 'domicilio';
            campoDireccion.hidden = !esDomicilio;
            direccion.required = esDomicilio;
        });
    });
}

function activarFormularioPedido() {
    document.querySelector('[data-confirmar]').addEventListener('click', confirmarPedido);
}

async function confirmarPedido() {
    const nombre = document.querySelector('#nombre-cliente');
    const telefono = document.querySelector('#telefono-cliente');
    const direccion = document.querySelector('#direccion-cliente');
    const boton = document.querySelector('[data-confirmar]');

    if (!nombre.reportValidity() || !telefono.reportValidity() || (metodoEntrega === 'domicilio' && !direccion.reportValidity())) return;

    try {
        boton.disabled = true;
        limpiarError();
        const ticket = await solicitarAPI('/tickets', {
            method: 'POST',
            body: JSON.stringify({
                id_carrito: carritoActual.id_carrito,
                nombre_cliente: nombre.value.trim(),
                telefono: telefono.value.trim(),
                metodo: metodoEntrega,
                direccion: metodoEntrega === 'domicilio' ? direccion.value.trim() : null,
                indicaciones: document.querySelector('#indicaciones').value.trim() || null
            })
        });

        localStorage.removeItem(CLAVE_CARRITO);
        window.location.href = `pedido.html?folio=${encodeURIComponent(ticket.folio)}`;
    } catch (error) {
        boton.disabled = false;
        mostrarError(error.message || 'No se pudo confirmar el pedido.');
    }
}
