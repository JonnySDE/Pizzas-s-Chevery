/* Carrusel de promociones (index.html).
   El HTML ya trae las 3 promos; este script solo agrega
   flechas, puntos, autoplay y sincroniza con el deslizamiento táctil. */
(function () {
    var raiz = document.querySelector('[data-carrusel]');
    if (!raiz) return;

    var pista = raiz.querySelector('.carrusel-pista');
    var total = pista.children.length;
    var puntos = Array.prototype.slice.call(raiz.querySelectorAll('.carrusel-punto'));
    var anterior = raiz.querySelector('.anterior');
    var siguiente = raiz.querySelector('.siguiente');
    var sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var INTERVALO = 6000;
    var actual = 0;
    var temporizador = null;
    var pausado = false;

    function marcar(i) {
        actual = i;
        puntos.forEach(function (p, n) {
            if (n === i) p.setAttribute('aria-current', 'true');
            else p.removeAttribute('aria-current');
        });
    }

    function ir(i) {
        i = (i + total) % total;
        pista.scrollTo({ left: i * pista.clientWidth, behavior: sinMovimiento ? 'auto' : 'smooth' });
        marcar(i);
    }

    function iniciar() {
        detener();
        if (sinMovimiento || pausado || document.hidden) return;
        temporizador = setInterval(function () { ir(actual + 1); }, INTERVALO);
    }

    function detener() {
        if (temporizador) { clearInterval(temporizador); temporizador = null; }
    }

    function pausar(valor) {
        pausado = valor;
        valor ? detener() : iniciar();
    }

    anterior.addEventListener('click', function () { ir(actual - 1); iniciar(); });
    siguiente.addEventListener('click', function () { ir(actual + 1); iniciar(); });
    puntos.forEach(function (p, n) {
        p.addEventListener('click', function () { ir(n); iniciar(); });
    });

    // Mantiene los puntos al día cuando la persona desliza con el dedo o el trackpad.
    var esperando = false;
    pista.addEventListener('scroll', function () {
        if (esperando) return;
        esperando = true;
        requestAnimationFrame(function () {
            esperando = false;
            var i = Math.round(pista.scrollLeft / pista.clientWidth);
            if (i !== actual && i >= 0 && i < total) marcar(i);
        });
    }, { passive: true });

    window.addEventListener('resize', function () {
        pista.scrollTo({ left: actual * pista.clientWidth, behavior: 'auto' });
    });

    // El autoplay se detiene mientras se interactúa con el carrusel.
    raiz.addEventListener('mouseenter', function () { pausar(true); });
    raiz.addEventListener('mouseleave', function () { pausar(false); });
    raiz.addEventListener('focusin', function () { pausar(true); });
    raiz.addEventListener('focusout', function () { pausar(false); });
    raiz.addEventListener('touchstart', function () { pausar(true); }, { passive: true });
    raiz.addEventListener('touchend', function () { setTimeout(function () { pausar(false); }, INTERVALO); }, { passive: true });
    document.addEventListener('visibilitychange', iniciar);

    iniciar();
})();
