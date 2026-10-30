const ORIGEN_API = window.CHEVERY_API_URL || (window.location.port === '5500' ? 'http://localhost:8000' : '');
const RUTA_API = `${ORIGEN_API}/api/v1`;
const CLAVE_CARRITO = 'chevery-id-carrito';

async function solicitarAPI(ruta, opciones = {}) {
    const respuesta = await fetch(`${RUTA_API}${ruta}`, {
        headers: { 'Content-Type': 'application/json', ...opciones.headers },
        ...opciones
    });

    if (!respuesta.ok) {
        let mensaje = `La solicitud falló (${respuesta.status}).`;

        try {
            const error = await respuesta.json();
            mensaje = typeof error.detail === 'string' ? error.detail : mensaje;
        } catch {
            // Algunas respuestas de error llegan sin JSON.
        }

        const problema = new Error(mensaje);
        problema.estado = respuesta.status;
        throw problema;
    }

    return respuesta.status === 204 ? null : respuesta.json();
}

async function obtenerCarritoActivo(crearNuevo = false) {
    const idGuardado = localStorage.getItem(CLAVE_CARRITO);

    if (idGuardado && !crearNuevo) {
        try {
            const carrito = await solicitarAPI(`/carritos/${idGuardado}`);
            if (carrito.estado === 'activo') return carrito;
        } catch (error) {
            if (error.estado !== 404) throw error;
        }
    }

    const carrito = await solicitarAPI('/carritos', { method: 'POST' });
    localStorage.setItem(CLAVE_CARRITO, carrito.id_carrito);
    return carrito;
}

function formatearDinero(valor) {
    return `$${Number(valor || 0).toFixed(2)}`;
}

function actualizarContadorCarrito(total = 0) {
    document.querySelectorAll('[data-cantidad-carrito]').forEach((contador) => {
        contador.textContent = total;
        contador.closest('.carrito-encabezado')?.setAttribute('aria-label', `Ver carrito, ${total} productos`);
    });
}

function mostrarError(mensaje) {
    const aviso = document.querySelector('[data-aviso]');
    if (!aviso) {
        window.alert(mensaje);
        return;
    }

    aviso.textContent = mensaje;
    aviso.hidden = false;
}

function limpiarError() {
    const aviso = document.querySelector('[data-aviso]');
    if (aviso) {
        aviso.textContent = '';
        aviso.hidden = true;
    }
}

function asignarImagen(imagen, producto) {
    const nombres = {
        1: 'pizza-pepperoni.png',
        2: 'pizza-hawaiana.png',
        3: 'pizza-mexicana.png',
        4: 'pizza-carnes.png',
        5: 'pizza-vegetariana.png'
    };
    const respaldo = `/imagenes/${nombres[producto.id_pizza] || 'icono-pizza.svg'}`;
    const origenImagenes = ORIGEN_API || window.location.origin;

    imagen.onerror = () => {
        imagen.onerror = null;
        imagen.src = new URL(respaldo, `${origenImagenes}/`).href;
    };
    imagen.src = new URL(producto.imagen_url || respaldo, `${origenImagenes}/`).href;
    imagen.alt = `Pizza ${producto.sabor}`;
}

async function agregarAlCarrito(idPizzaTamano, idMasa, boton) {
    try {
        boton.disabled = true;
        limpiarError();
        const carrito = await obtenerCarritoActivo();
        const actualizado = await solicitarAPI(`/carritos/${carrito.id_carrito}/items`, {
            method: 'POST',
            body: JSON.stringify({ id_pizza_tamano: idPizzaTamano, id_masa: idMasa, cantidad: 1 })
        });
        actualizarContadorCarrito(actualizado.resumen.total_pizzas);
        boton.textContent = 'Agregada';
        setTimeout(() => {
            boton.textContent = '+ Agregar';
            boton.disabled = false;
        }, 900);
    } catch (error) {
        boton.disabled = false;
        mostrarError(error.message || 'No se pudo agregar la pizza.');
    }
}
