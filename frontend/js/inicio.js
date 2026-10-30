document.addEventListener('DOMContentLoaded', cargarInicio);

async function cargarInicio() {
    try {
        const [pizzas, masas, carrito] = await Promise.all([
            solicitarAPI('/catalogo/pizzas?destacado=true'),
            solicitarAPI('/catalogo/masas'),
            obtenerCarritoActivo()
        ]);

        actualizarContadorCarrito(carrito.resumen.total_pizzas);
        mostrarPizzasInicio(pizzas);
        mostrarMasas(masas, 'inicio');
    } catch (error) {
        mostrarError(`No se pudo conectar con el menú: ${error.message}`);
    }
}

function mostrarPizzasInicio(pizzas) {
    const lista = document.querySelector('[data-productos-inicio]');
    const plantilla = document.querySelector('#plantilla-producto-inicio');
    lista.replaceChildren();

    pizzas.slice(0, 3).forEach((pizza, indice) => {
        const tarjeta = plantilla.content.firstElementChild.cloneNode(true);
        const tamano = pizza.tamanos[0];

        tarjeta.querySelector('[data-etiqueta]').textContent = pizza.etiqueta || '';
        asignarImagen(tarjeta.querySelector('[data-imagen]'), pizza);
        tarjeta.querySelector('[data-nombre]').textContent = `${indice + 1}. ${pizza.sabor}`;
        tarjeta.querySelector('[data-descripcion]').textContent = pizza.descripcion || '';
        tarjeta.querySelector('[data-precios]').textContent = pizza.tamanos
            .map((opcion) => `${opcion.nombre_tamano}: ${formatearDinero(opcion.precio)}`)
            .join(' | ');
        tarjeta.querySelector('[data-precio]').innerHTML = `${formatearDinero(tamano?.precio)} <small>MXN</small>`;

        const agregar = tarjeta.querySelector('[data-agregar]');
        agregar.disabled = !tamano || tamano.stock < 1;
        agregar.addEventListener('click', () => {
            const masa = document.querySelector('[data-masa].seleccionada');
            agregarAlCarrito(tamano.id_pizza_tamano, Number(masa?.dataset.idMasa), agregar);
        });

        lista.append(tarjeta);
    });
}

function mostrarMasas(masas, pagina) {
    const lista = document.querySelector('[data-opciones-masa]');
    const plantilla = document.querySelector('#plantilla-opcion-masa');
    lista.replaceChildren();

    masas.forEach((masa, indice) => {
        const opcion = plantilla.content.firstElementChild.cloneNode(true);
        opcion.dataset.idMasa = masa.id_masa;
        opcion.textContent = `${masa.nombre} (+ ${formatearDinero(masa.precio_extra)})`;
        opcion.classList.toggle('seleccionada', indice === 0);
        opcion.setAttribute('aria-pressed', String(indice === 0));
        opcion.addEventListener('click', () => {
            lista.querySelectorAll('button').forEach((boton) => {
                boton.classList.remove('seleccionada');
                boton.setAttribute('aria-pressed', 'false');
            });
            opcion.classList.add('seleccionada');
            opcion.setAttribute('aria-pressed', 'true');
        });
        lista.append(opcion);
    });
}
