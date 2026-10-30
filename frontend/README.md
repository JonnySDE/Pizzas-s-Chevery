# Frontend Pizzería Chevery

## Vistas

- `index.html`: inicio.
- `paginas/menu.html`: menú.
- `paginas/carrito.html`: carrito y datos de envío.
- `paginas/pedido.html`: confirmación del pedido.

Cada archivo HTML define la estructura de su pantalla. Los estilos compartidos están en `css/base.css` y cada pantalla enlaza su hoja correspondiente. JavaScript carga los datos de la API en plantillas HTML y atiende interacciones; no genera las páginas completas.

Para ejecutar la página conectada, sigue las instrucciones de [backend/README.md](../backend/README.md). FastAPI sirve los HTML y expone la API en el mismo origen.

Las imágenes de las pizzas y los iconos están en `imagenes/`. El catálogo de la API entrega la ruta de cada foto.
