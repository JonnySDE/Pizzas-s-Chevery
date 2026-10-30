-- Esquema compatible con backend/api/app/models.py (MySQL 8 / MariaDB).
-- Ejecuta este archivo una vez en MySQL Workbench sobre una base nueva.

CREATE DATABASE IF NOT EXISTS pizzeria_chevery
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE pizzeria_chevery;

CREATE TABLE IF NOT EXISTS PIZZA (
    id_pizza INT AUTO_INCREMENT PRIMARY KEY,
    sabor VARCHAR(60) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    imagen_url VARCHAR(255) NOT NULL,
    etiqueta VARCHAR(30),
    destacado BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS TAMANO (
    id_tamano INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE,
    orden INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS PIZZA_TAMANO (
    id_pizza_tamano INT AUTO_INCREMENT PRIMARY KEY,
    id_pizza INT NOT NULL,
    id_tamano INT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    UNIQUE (id_pizza, id_tamano),
    CHECK (precio > 0),
    CHECK (stock >= 0),
    FOREIGN KEY (id_pizza) REFERENCES PIZZA(id_pizza),
    FOREIGN KEY (id_tamano) REFERENCES TAMANO(id_tamano)
);

CREATE TABLE IF NOT EXISTS MASA (
    id_masa INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    precio_extra DECIMAL(10, 2) NOT NULL DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    CHECK (precio_extra >= 0)
);

CREATE TABLE IF NOT EXISTS CARRITO (
    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
    estado ENUM('activo', 'finalizado', 'expirado') NOT NULL DEFAULT 'activo',
    expira_en DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CARRITO_PIZZA (
    id_carrito_pizza INT AUTO_INCREMENT PRIMARY KEY,
    id_carrito INT NOT NULL,
    id_pizza_tamano INT NOT NULL,
    id_masa INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    UNIQUE (id_carrito, id_pizza_tamano, id_masa),
    CHECK (cantidad > 0),
    CHECK (precio_unitario > 0),
    FOREIGN KEY (id_carrito) REFERENCES CARRITO(id_carrito) ON DELETE CASCADE,
    FOREIGN KEY (id_pizza_tamano) REFERENCES PIZZA_TAMANO(id_pizza_tamano),
    FOREIGN KEY (id_masa) REFERENCES MASA(id_masa)
);

CREATE TABLE IF NOT EXISTS TICKET (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    id_carrito INT NOT NULL UNIQUE,
    folio VARCHAR(20) NOT NULL UNIQUE,
    nombre_cliente VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    metodo ENUM('domicilio', 'recoger') NOT NULL,
    direccion VARCHAR(255) NULL,
    indicaciones VARCHAR(255) NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    costo_envio DECIMAL(10, 2) NOT NULL DEFAULT 0,
    descuento DECIMAL(10, 2) NOT NULL DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,
    estado ENUM(
        'recibido', 'en_preparacion', 'en_camino',
        'listo_para_recoger', 'entregado', 'cancelado'
    ) NOT NULL DEFAULT 'recibido',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (subtotal >= 0),
    CHECK (costo_envio >= 0),
    CHECK (descuento >= 0),
    CHECK (total >= 0),
    CHECK (metodo = 'recoger' OR direccion IS NOT NULL),
    FOREIGN KEY (id_carrito) REFERENCES CARRITO(id_carrito)
);

-- Datos iniciales de menú y stock. Los precios viven en la base de datos.
START TRANSACTION;

INSERT INTO TAMANO (id_tamano, nombre, orden) VALUES
    (1, 'Chica', 1),
    (2, 'Mediana', 2),
    (3, 'Familiar', 3)
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), orden = VALUES(orden);

INSERT INTO MASA (id_masa, nombre, precio_extra, activo) VALUES
    (1, 'Tradicional', 0.00, TRUE),
    (2, 'Fina y Crujiente', 0.00, TRUE),
    (3, 'Orilla Rellena de Queso', 30.00, TRUE),
    (4, 'Orilla Queso + Pepperoni', 45.00, TRUE)
ON DUPLICATE KEY UPDATE
    nombre = VALUES(nombre), precio_extra = VALUES(precio_extra), activo = VALUES(activo);

INSERT INTO PIZZA (id_pizza, sabor, descripcion, imagen_url, etiqueta, destacado, activo) VALUES
    (1, 'La Clásica (Pepperoni)', 'Queso mozzarella derretido y generosas rodajas de pepperoni tradicional.', '/imagenes/pizza-pepperoni.png', 'MÁS VENDIDA', TRUE, TRUE),
    (2, 'Hawaiana', 'Jamón selecto, piña dulce en trozos y extra queso mozzarella fundido.', '/imagenes/pizza-hawaiana.png', 'TROPICAL', TRUE, TRUE),
    (3, 'La Mexicana', 'Chorizo, jalapeño en rodajas, cebolla morada y deliciosa base de frijoles.', '/imagenes/pizza-mexicana.png', 'LOCAL', TRUE, TRUE),
    (4, 'Carnes Frías', 'Salami, pepperoni, jamón, salchicha y crujiente tocino ahumado.', '/imagenes/pizza-carnes.png', 'ESPECIAL', FALSE, TRUE),
    (5, 'Vegetariana', 'Champiñones, pimiento verde, cebolla, aceitunas negras y jitomate fresco.', '/imagenes/pizza-vegetariana.png', 'VEGETARIANA', FALSE, TRUE)
ON DUPLICATE KEY UPDATE
    descripcion = VALUES(descripcion), imagen_url = VALUES(imagen_url),
    etiqueta = VALUES(etiqueta), destacado = VALUES(destacado), activo = VALUES(activo);

INSERT INTO PIZZA_TAMANO (id_pizza_tamano, id_pizza, id_tamano, precio, stock) VALUES
    (1, 1, 1, 110.00, 25), (2, 1, 2, 160.00, 30), (3, 1, 3, 220.00, 15),
    (4, 2, 1, 120.00, 25), (5, 2, 2, 170.00, 30), (6, 2, 3, 230.00, 15),
    (7, 3, 1, 135.00, 20), (8, 3, 2, 185.00, 25), (9, 3, 3, 250.00, 10),
    (10, 4, 1, 145.00, 20), (11, 4, 2, 195.00, 25), (12, 4, 3, 270.00, 10),
    (13, 5, 1, 130.00, 20), (14, 5, 2, 180.00, 25), (15, 5, 3, 240.00, 10)
ON DUPLICATE KEY UPDATE
    precio = VALUES(precio);

COMMIT;
