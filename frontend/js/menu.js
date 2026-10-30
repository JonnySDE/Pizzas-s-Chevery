document.addEventListener('DOMContentLoaded', cargarMenu);

async function cargarMenu() {
    try {
        const [pizzas, masas, carrito] = await Promise.all([
            solicitarAPI('/catalogo/pizzas'),
            solicitarAPI('/catalogo/masas'),
            obtenerCarritoActivo()
        ]);

        actualizarContadorCarrito(carrito.resumen.total_pizzas);
        mostrarPizzasMenu(pizzas);
        mostrarMasasMenu(masas);
        activarFiltrosMenu();
    } catch (error) {
        mostrarError(`No se pudo conectar con el menú: ${error.message}`);
    }
}

function mostrarPizzasMenu(pizzas) {
    const lista = document.querySelector('[data-lista-menu]');
    const plantilla = document.querySelector('#plantilla-producto-menu');
    lista.replaceChildren();

    pizzas.forEach((pizza, indice) => {
        const tarjeta = plantilla.content.firstElementChild.cloneNode(true);
        tarjeta.dataset.destacado = String(pizza.destacado);
        tarjeta.dataset.pizza = pizza.id_pizza;
        tarjeta.querySelector('[data-etiqueta]').textContent = pizza.etiqueta || '';
        asignarImagen(tarjeta.querySelector('[data-imagen]'), pizza);
        tarjeta.querySelector('[data-nombre]').textContent = `${indice + 1}. ${pizza.sabor}`;
        tarjeta.querySelector('[data-descripcion]').textContent = pizza.descripcion || '';

        const precioActual = tarjeta.querySelector('[data-precio]');
        const botonAgregar = tarjeta.querySelector('[data-agregar]');
        const listaTamanos = tarjeta.querySelector('[data-tamanos]');
        let tamanoSeleccionado = pizza.tamanos.find((tamano) => tamano.orden === 2) || pizza.tamanos[0];

        function seleccionarTamano(tamano, boton) {
            tamanoSeleccionado = tamano;
            listaTamanos.querySelectorAll('button').forEach((opcion) => {
                opcion.classList.remove('activo');
                opcion.setAttribute('aria-pressed', 'false');
            });
            boton.classList.add('activo');
            boton.setAttribute('aria-pressed', 'true');
            precioActual.innerHTML = `${formatearDinero(tamano.precio)} <small>MXN</small>`;
            botonAgregar.disabled = tamano.stock < 1;
            botonAgregar.title = tamano.stock < 1 ? 'Sin existencia' : '';
        }

        pizza.tamanos.forEach((tamano) => {
            const boton = document.createElement('button');
            boton.type = 'button';
            boton.textContent = `${abreviarTamano(tamano.nombre_tamano)}: ${formatearDinero(tamano.precio)}`;
            boton.addEventListener('click', () => seleccionarTamano(tamano, boton));
            listaTamanos.append(boton);
            if (tamano === tamanoSeleccionado) seleccionarTamano(tamano, boton);
        });

        botonAgregar.addEventListener('click', () => {
            const masa = document.querySelector('[data-masa].seleccionada');
            agregarAlCarrito(tamanoSeleccionado.id_pizza_tamano, Number(masa?.dataset.idMasa), botonAgregar);
        });

        lista.append(tarjeta);
    });
}

async function mostrarMasasMenu(masas) {
    const lista = document.querySelector('[data-opciones-masa]');
    const plantilla = document.querySelector('#plantilla-opcion-masa');
    lista.replaceChildren();

    masas.forEach((masa, indice) => {
        const boton = plantilla.content.firstElementChild.cloneNode(true);
        boton.dataset.idMasa = masa.id_masa;
        boton.textContent = `${masa.nombre} (+ ${formatearDinero(masa.precio_extra)} MXN)`;
        boton.classList.toggle('seleccionada', indice === 0);
        boton.setAttribute('aria-pressed', String(indice === 0));
        boton.addEventListener('click', () => {
            lista.querySelectorAll('button').forEach((opcion) => {
                opcion.classList.remove('seleccionada');
                opcion.setAttribute('aria-pressed', 'false');
            });
            boton.classList.add('seleccionada');
            boton.setAttribute('aria-pressed', 'true');
        });
        lista.append(boton);
    });
}

function activarFiltrosMenu() {
    const filtros = document.querySelectorAll('.filtros button');
    filtros.forEach((filtro, indice) => {
        filtro.addEventListener('click', () => {
            filtros.forEach((opcion) => opcion.classList.remove('activo'));
            filtro.classList.add('activo');

            document.querySelectorAll('.producto-menu').forEach((tarjeta, posicion) => {
                tarjeta.hidden = indice === 1 && posicion > 1;
                if (!tarjeta.hidden) {
                    tarjeta.classList.remove('aparecer');
                    requestAnimationFrame(() => tarjeta.classList.add('aparecer'));
                }
            });
        });
    });
}

function abreviarTamano(nombre) {
    if (nombre.toLowerCase().startsWith('med')) return 'Med.';
    if (nombre.toLowerCase().startsWith('fam')) return 'Fam.';
    return nombre;
}
