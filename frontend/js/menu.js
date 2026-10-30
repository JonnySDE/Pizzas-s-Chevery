document.addEventListener('DOMContentLoaded', () => {
    const tarjetas = document.querySelectorAll('.producto-menu');

    document.querySelectorAll('.producto-menu .tamanos button').forEach((boton) => {
        boton.addEventListener('click', () => {
            const tarjeta = boton.closest('.producto-menu');
            const precio = boton.textContent.match(/\$(\d+)/)?.[1];

            tarjeta.querySelectorAll('.tamanos button').forEach((opcion) => {
                opcion.classList.remove('activo');
                opcion.setAttribute('aria-pressed', 'false');
            });

            boton.classList.add('activo');
            boton.setAttribute('aria-pressed', 'true');

            if (precio) {
                tarjeta.querySelector('.precio-grande').innerHTML = `$${precio}.00 <small>MXN</small>`;
            }
        });
    });

    document.querySelectorAll('.filtros button').forEach((boton, indice) => {
        boton.addEventListener('click', () => {
            document.querySelectorAll('.filtros button').forEach((filtro) => {
                filtro.classList.remove('activo');
                filtro.setAttribute('aria-pressed', 'false');
            });

            boton.classList.add('activo');
            boton.setAttribute('aria-pressed', 'true');

            tarjetas.forEach((tarjeta, posicion) => {
                const mostrar = indice === 0 || posicion < 2;
                tarjeta.hidden = !mostrar;

                if (mostrar) {
                    tarjeta.classList.remove('aparecer');
                    requestAnimationFrame(() => tarjeta.classList.add('aparecer'));
                }
            });
        });
    });

    document.querySelectorAll('.opciones-masa button').forEach((boton) => {
        boton.addEventListener('click', () => {
            document.querySelectorAll('.opciones-masa button').forEach((opcion) => {
                opcion.classList.remove('seleccionada');
                opcion.setAttribute('aria-pressed', 'false');
            });

            boton.classList.add('seleccionada');
            boton.setAttribute('aria-pressed', 'true');
        });
    });
});
